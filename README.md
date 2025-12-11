#  Rideau Canal Sensor Simulation Repository

This repository contains the code for the IoT sensor simulator component of the Rideau Canal Ice Monitoring System, designed for the CST8916 Final Project.

---

##  Overview

The `sensor_simulator.py` script mimics the behavior of three independent IoT sensors deployed at key locations along the Rideau Canal Skateway. It generates continuous, realistic environmental telemetry (ice thickness, temperature, snow accumulation) and sends this data in real-time to **Azure IoT Hub**.

### Technologies Used

* **Language:** Python
* **IoT SDK:** Azure IoT Device SDK for Python

##  Prerequisites

To run the simulator, you must have the following software installed and configured:

1.  **Python 3.x**
2.  **Azure IoT Hub:** You must have an IoT Hub instance created in Azure.
3.  **IoT Hub Devices:** Three devices must be registered in your IoT Hub, one for each location, to obtain the necessary connection strings.

##  Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/anil0015/rideau-canal-sensor-simulation.git](https://github.com/anil0015/rideau-canal-sensor-simulation.git)
    cd rideau-canal-sensor-simulation
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    *(Assuming `requirements.txt` includes `azure-iot-device`)*

##  Configuration

The simulator requires the connection strings for the three registered IoT Hub devices to authenticate and send data. These must be set as environment variables.

1.  **Create a `.env` file** (or export variables directly):

    *Example `.env.example` content:*
    ```
    # Replace the placeholders with the actual device connection strings from Azure IoT Hub
    DOWS_LAKE_CONNECTION_STRING="HostName=...;DeviceId=DowsLake;SharedAccessKey=..."
    FIFTH_AVE_CONNECTION_STRING="HostName=...;DeviceId=FifthAvenue;SharedAccessKey=..."
    NAC_CONNECTION_STRING="HostName=...;DeviceId=NAC;SharedAccessKey=..."
    ```
2.  **Load the environment variables** before running the script (e.g., using a library like `python-dotenv` or using `source .env` if your shell supports it).

##  Usage

Execute the main Python script. The simulator will start generating data and printing the output before sending it to Azure.

```bash
python sensor_simulator.py

```
The script will run continuously, sending a new message for each of the three locations every **10 seconds**.

##  Code Structure

### `sensor_simulator.py`

This is the main simulation script. Its key functions are:

| Component / Function | Description |
| :--- | :--- |
| `generate_telemetry(location)` | Generates randomized, yet realistic, readings for ice thickness, temperatures, and snow accumulation for a given location. |
| `send_telemetry_async(device_client, message)` | Handles asynchronous connection and transmission of the JSON payload to Azure IoT Hub. |
| `main()` | The core loop that initializes the three device clients, loads the connection strings, and schedules the data generation and sending tasks every 10 seconds. |

##  Sensor Data Format

All data is sent to Azure IoT Hub as a JSON payload, adhering to the following schema:

| Field | Data Type | Example Value | Description |
| :--- | :--- | :--- | :--- |
| **`Location`** | string | `"DowsLake"` | The canal section where the sensor is located. |
| **`Timestamp`** | string | `"2025-12-10T13:30:00Z"` | UTC timestamp of the reading (ISO 8601 format). |
| **`IceThicknessCm`** | float | `32.5` | Measured ice thickness in centimeters. |
| **`SurfaceTemperatureC`** | float | `-5.2` | Temperature of the ice surface in Celsius. |
| **`SnowAccumulationCm`** | float | `1.0` | Depth of snow on the ice in centimeters. |
| **`AirTemperatureC`** | float | `-8.1` | Ambient external air temperature in Celsius. |

### Example Output Message

```json
{
    "Location": "FifthAvenue",
    "Timestamp": "2025-12-10T13:30:10.000Z",
    "IceThicknessCm": 31.8,
    "SurfaceTemperatureC": -4.5,
    "SnowAccumulationCm": 0.5,
    "AirTemperatureC": -7.0
}

```
## Troubleshooting

| Common Issue | Solution |
|--------------|----------|
| **Authentication Error** | Double-check that all three connection strings in your `.env` file are copied correctly and belong to the correct device ID. |
| **ModuleNotFoundError** | Make sure you ran `pip install -r requirements.txt` to install the Azure IoT Device SDK. |
| **IoT Hub shows 0 messages** | Verify that your firewall is not blocking the connection and that the script is running without throwing exceptions. Also check IoT Hub metrics after a few minutes. |
