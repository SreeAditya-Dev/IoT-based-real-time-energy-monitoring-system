# Energy Monitoring and Theft Detection System

A comprehensive IoT-based real-time energy monitoring system with AI-powered theft detection capabilities.

## System Overview

This project consists of four main components:

1. **Real-time Energy Monitoring**
   - ESP32 microcontroller with current and gyro sensors
   - RGB LED status indicators (green/yellow/red)
   - Live data displayed on dashboard

2. **Energy Theft Detection**
   - Create the load using DC motor and Vibrating sensor
   - Triggers buzzer and sends alerts on detection
   - Visual alerts in dashboard

3. **AI-powered Anomaly Detection**
   - Uses Isolation Forest algorithm
   - Identifies abnormal energy consumption patterns
   - Provides visual indicators for potential theft

4. **Streamlit Dashboard**
   - Real-time graphs showing voltage/current/power
   - Historical logs and trend analysis
   - Anomaly insights and alert controls

## Project Structure

- `app.py` - Main Streamlit dashboard application
- `api_server.py` - FastAPI backend for receiving ESP32 data
- `dashboard_components.py` - UI components for the dashboard
- `anomaly_detection.py` - AI model for detecting anomalies
- `data_simulator.py` - Data generation for testing
- `utils.py` - Utility functions
- `api_client.py` - Functions to communicate with API
- `esp32_example.ino` - Arduino code for ESP32 devices
- `simulate_esp32.py` - Script to simulate ESP32 data

## Getting Started

### Running the System

1. Start the API server:
   ```
   python api_server.py
   ```

2. Start the Streamlit dashboard:
   ```
   streamlit run app.py --server.port 5000
   ```

3. (Optional) Run the ESP32 simulator for testing:
   ```
   python simulate_esp32.py
   ```

### Setting Up Real ESP32 Devices

1. Install required Arduino libraries:
   - WiFi
   - HTTPClient
   - ArduinoJson

2. Update the following in the ESP32 code:
   - WiFi credentials (SSID and password)
   - API endpoint URL (your server address)
   - Pin configurations based on your hardware setup

3. Calibrate sensors as needed for your specific hardware

4. Upload the code to your ESP32 device

## Hardware Components

- ESP32 microcontroller
- vibrating sensor for load
- DC motor for load
- RGB LEDs for status indication
- Buzzer for alerts


## Dashboard Features

- **Live Monitoring** - Real-time energy consumption graphs
- **Historical Data** - Past consumption patterns with filtering
- **Anomaly Detection** - AI-powered theft identification
- **Alert Settings** - Customize threshold controls
- **Status Indicators** - Visual RGB LED status display

## API Endpoints

- `GET /` - API health check
- `POST /api/readings` - Submit new reading from ESP32
- `GET /api/readings/latest` - Get latest readings
- `GET /api/readings/history` - Get historical data

## Customization

### Threshold Settings

Adjust the alert thresholds in the dashboard sidebar:
- Low threshold: Triggers yellow indicator (moderate alert)
- High threshold: Triggers red indicator and alerts (high alert/potential theft)

### Email Notifications

Enable email notifications for high alerts in the dashboard settings.

## Troubleshooting

- **ESP32 not connecting** - Check WiFi credentials and network
- **API connection error** - Verify server IP address and port
- **Sensor readings incorrect** - Calibrate sensors and check wiring

## Team Members
 - **V SREE ADITYA**
 - **Sathyam**
 - **R Sunil**
 - **Shrihari**

