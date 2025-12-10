import redis
import json
import random
import time
from datetime import datetime, timezone
import threading

# --- Configuration ---
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
RAW_DATA_KEY = 'raw_data_stream' # Redis List where raw messages go
LOCATIONS = ["DowsLake", "FifthAvenue", "NAC"]
SEND_INTERVAL_SECONDS = 10

# Initialize Redis client
try:
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    r.ping()
    print("Successfully connected to Redis.")
except redis.exceptions.ConnectionError:
    print("FATAL ERROR: Cannot connect to Redis. Ensure it is running on localhost:6379.")
    exit(1)


def generate_telemetry(location_name: str) -> dict:
    """Generates a realistic set of sensor readings for a given location."""
    
    # Simulate realistic ranges, slightly varying them for demonstration
    ice_thickness = round(random.uniform(20.0, 35.0), 2)
    surface_temp = round(random.normalvariate(-6.0, 2.5), 2)
    external_temp = round(surface_temp + random.uniform(0.5, 3.0), 2)
    snow_accumulation = round(random.uniform(0.0, 5.0), 2)

    timestamp = datetime.now(timezone.utc).isoformat()
    
    data = {
        "deviceId": f"Device_{location_name}",
        "location": location_name,
        "timestamp": timestamp,
        "IceThickness": ice_thickness,
        "SurfaceTemperature": surface_temp,
        "SnowAccumulation": snow_accumulation,
        "ExternalTemperature": external_temp
    }
    return data

def sensor_thread(location_name: str):
    """Function run by each sensor thread to send data."""
    print(f"[{location_name}] Sensor thread started.")
    
    while True:
        try:
            # 1. Generate sensor data
            telemetry_data = generate_telemetry(location_name)
            
            # 2. Serialize data to JSON
            message_body = json.dumps(telemetry_data)
            
            # 3. Push to Redis List
            r.rpush(RAW_DATA_KEY, message_body)
            print(f"[{location_name}] Pushed to Redis: {message_body}")

            # Wait for the next interval
            time.sleep(SEND_INTERVAL_SECONDS)

        except Exception as e:
            print(f"[{location_name}] An error occurred: {e}")
            time.sleep(5) # Wait before retrying

def main():
    """Starts the simulation for all three locations concurrently using threads."""
    print("Starting Rideau Canal Sensor Simulation...")
    
    # Create and start a thread for each location
    threads = []
    for loc in LOCATIONS:
        thread = threading.Thread(target=sensor_thread, args=(loc,))
        thread.daemon = True # Allows the main program to exit even if threads are running
        threads.append(thread)
        thread.start()

    # Keep the main thread alive so the sensor threads can continue sending data
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nSimulation process interrupted. Shutting down all sensors.")
        
if __name__ == "__main__":
    main()