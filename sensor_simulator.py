import os
import json
import time
import random
from datetime import datetime
from dotenv import load_dotenv
from azure.iot.device import IoTHubDeviceClient, Message

# Load .env file values
load_dotenv()

# Debug print - optional
print("Loaded env vars:")
print("DOWS =", os.getenv("DOWS_LAKE_CS"))
print("FIFTH =", os.getenv("FIFTH_AVENUE_CS"))
print("NAC =", os.getenv("NAC_CS"))
print("-------------------------------------")

def get_env(name):
    value = os.getenv(name)
    if not value:
        raise ValueError(f" Missing environment variable: {name}")
    return value

# Create IoT Hub clients
clients = {
    "dows-lake": IoTHubDeviceClient.create_from_connection_string(get_env("DOWS_LAKE_CS")),
    "fifth-ave": IoTHubDeviceClient.create_from_connection_string(get_env("FIFTH_AVENUE_CS")),
    "nac": IoTHubDeviceClient.create_from_connection_string(get_env("NAC_CS"))
}

def generate_sensor_data(location):
    return {
        "location": location,
        "timestamp": datetime.utcnow().isoformat(),
        "ice_thickness": round(random.uniform(20, 40), 2),
        "surface_temp": round(random.uniform(-15, 2), 2),
        "snow_accumulation": round(random.uniform(0, 10), 2),
        "external_temp": round(random.uniform(-20, 5), 2)
    }

print(" Starting Rideau Canal Sensor Simulation...")
print("Sending new data every 10 seconds...\n")

while True:
    for location, client in clients.items():
        data = generate_sensor_data(location)
        message = Message(json.dumps(data))
        message.content_type = "application/json"

        try:
            client.send_message(message)
            print(f"✔ Sent from {location}: {data}")
        except Exception as e:
            print(f"ERROR sending from {location}: {e}")

    print("\n--- Waiting 10 seconds ---\n")
    time.sleep(10)
