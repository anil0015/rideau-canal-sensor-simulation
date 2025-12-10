import redis
import json
import time
from datetime import datetime, timezone
import sys

# --- Configuration ---
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
RAW_DATA_KEY = 'raw_data_stream'
AGGREGATION_KEY_PREFIX = 'AGGREGATION:'
TUMBLING_WINDOW_SECONDS = 20 # New window size: 20 seconds
#TUMBLING_WINDOW_MINUTES = 5 # Simulates the 5-minute ASA window

# Connect to Redis
try:
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    r.ping()
    print(" Successfully connected to Redis.")
except redis.exceptions.ConnectionError:
    print(" ERROR: Could not connect to Redis.")
    print("Please ensure your local Redis server is running on localhost:6379.")
    sys.exit(1)


# Dictionary to hold raw data for the current window (Location -> List of Readings)
current_window_readings = {
    "DowsLake": [], 
    "FifthAvenue": [], 
    "NAC": []
}

last_window_end_time = time.time() # Timestamp when the last window completed

# --- Aggregation and Safety Logic Function ---
def process_window(location, readings):
    """Calculates all required aggregations and safety status for a location."""
    if not readings:
        return None

    # 1. Prepare data (ensure numbers are used for calculation)
    try:
        # NOTE: Readings are stored as strings from the simulator, so convert back to float
        ice_thicknesses = [float(d.get('IceThickness', 0)) for d in readings]
        surface_temps = [float(d.get('SurfaceTemperature', 0)) for d in readings]
        snow_accumulations = [float(d.get('SnowAccumulation', 0)) for d in readings]
        external_temps = [float(d.get('ExternalTemperature', 0)) for d in readings]
    except ValueError as e:
        print(f"Error converting sensor data to float for {location}: {e}")
        return None

    # 2. Calculate Aggregations
    avg_ice = sum(ice_thicknesses) / len(ice_thicknesses)
    max_ice = max(ice_thicknesses)
    min_ice = min(ice_thicknesses)
    
    avg_surface_temp = sum(surface_temps) / len(surface_temps)
    max_surface_temp = max(surface_temps)
    min_surface_temp = min(surface_temps)

    max_snow = max(snow_accumulations)
    
    avg_external_temp = sum(external_temps) / len(external_temps)
    reading_count = len(readings)

    # 3. Safety Status Logic (MUST use MAX values for safety assessment)
    # The lowest MAX IceThickness and highest MAX Surface Temperature determine safety
    max_ice_condition = max_ice
    max_surface_temp_condition = max_surface_temp 

    safety_status = 'Unsafe'
    if max_ice_condition >= 30 and max_surface_temp_condition <= -2:
        safety_status = 'Safe'
    elif max_ice_condition >= 25 and max_surface_temp_condition <= 0:
        safety_status = 'Caution'
        
    # 4. Prepare the final aggregated document (Cosmos DB equivalent)
    agg_data = {
        "location": location,
        "WindowEndTime": datetime.now(timezone.utc).isoformat(),
        "AvgIceThickness_cm": round(avg_ice, 2),
        "MinIceThickness_cm": round(min_ice, 2),
        "MaxIceThickness_cm": round(max_ice, 2),
        "AvgSurfaceTemperature_C": round(avg_surface_temp, 2),
        "MinSurfaceTemperature_C": round(min_surface_temp, 2),
        "MaxSurfaceTemperature_C": round(max_surface_temp, 2),
        "MaxSnowAccumulation_cm": round(max_snow, 2),
        "AvgExternalTemperature_C": round(avg_external_temp, 2),
        "ReadingCount": reading_count,
        "SafetyStatus": safety_status
    }
    return agg_data

# --- Main Processor Loop ---
def stream_processor():
    global last_window_end_time
    global current_window_readings
    
    print("Rideau Canal Stream Processor Started.")
    print(f"   Window size: {TUMBLING_WINDOW_SECONDS} seconds.")
    print("--------------------------------------------------")

    while True:
        current_time = time.time()
        
        # 1. --- Consume Raw Data from Redis List (LPOP is non-blocking) ---
        raw_message = r.lpop(RAW_DATA_KEY)
        
        if raw_message:
            try:
                data = json.loads(raw_message)
                location = data.get('location')
                
                if location in current_window_readings:
                    current_window_readings[location].append(data)
                
            except json.JSONDecodeError:
                print(f"Error decoding raw JSON message: {raw_message}")
            
        # 2. --- Tumbling Window Logic (Process & Store) ---
        if current_time - last_window_end_time >= (TUMBLING_WINDOW_SECONDS * 60):
            print(f"\n--- {TUMBLING_WINDOW_SECONDS}-Seconds Window Closed at {datetime.now().strftime('%H:%M:%S')} ---")
            
            # Process and store aggregated data for each location
            for location, readings in current_window_readings.items():
                if readings:
                    aggregated_data = process_window(location, readings)
                    
                    if aggregated_data:
                        # Store in Redis Hash (Cosmos DB replacement)
                        key = f"{AGGREGATION_KEY_PREFIX}{location}"
                        r.hset(key, mapping=aggregated_data)

                        print(f"  AGGREGATED: {location}. Status: {aggregated_data['SafetyStatus']}. Readings: {len(readings)}")
                else:
                    print(f"  SKIPPED: {location}. No readings in this window.")
            
            # Reset the window and timer
            current_window_readings = {k: [] for k in current_window_readings.keys()}
            last_window_end_time = current_time
            print("--------------------------------------------------")
            print("--- New Window Started ---\n")

        # Small sleep to prevent excessive CPU usage while polling Redis
        time.sleep(0.1) 

if __name__ == "__main__":
    try:
        stream_processor()
    except KeyboardInterrupt:
        print("\nStream Processor stopped by user.")