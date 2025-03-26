"""
ESP32 Simulator Script

This script simulates an ESP32 device sending energy monitoring data to the API.
Use this for testing the API integration without actual hardware.
"""

import requests
import json
import time
import random
import math
from datetime import datetime

# API endpoint
API_URL = "http://localhost:8000/api/readings"

# Device ID
DEVICE_ID = "ESP32_SIMULATOR_001"

# Thresholds for alerts
LOW_THRESHOLD = 2.0
HIGH_THRESHOLD = 4.0

def generate_reading(include_anomaly=False):
    """
    Generate a simulated energy reading.
    
    Args:
        include_anomaly (bool): Whether to include an anomaly in the reading
        
    Returns:
        dict: Simulated energy reading
    """
    # Base values
    voltage = 220.0 + random.uniform(-5.0, 5.0)  # 220V ± 5V
    
    # Normal current pattern: sinusoidal with some variation
    time_of_day = datetime.now().hour + datetime.now().minute / 60.0
    # Higher usage during morning and evening
    base_current = 1.5 + 0.5 * math.sin(((time_of_day - 6) / 24) * 2 * math.pi)
    
    # Add some random variation
    current = base_current + random.uniform(-0.3, 0.3)
    
    # Introduce anomaly occasionally if requested
    if include_anomaly and random.random() < 0.3:  # 30% chance of anomaly
        anomaly_type = random.choice(["spike", "drop", "gradual"])
        
        if anomaly_type == "spike":
            # Sudden large spike
            current += random.uniform(HIGH_THRESHOLD, HIGH_THRESHOLD + 3.0)
        elif anomaly_type == "drop":
            # Sudden drop (possible power theft)
            current *= 0.3  # Drop to 30% of expected value
        else:  # gradual
            # Gradual increase (possible circuit issue)
            current *= 1.5  # 150% of expected value
    
    # Ensure current is positive
    current = max(0.1, current)
    
    # Calculate power
    power = voltage * current
    
    # Create reading
    reading = {
        "current": round(current, 2),
        "voltage": round(voltage, 1),
        "power": round(power, 2),
        "device_id": DEVICE_ID
    }
    
    return reading

def send_reading_to_api(reading):
    """
    Send the reading to the API server.
    
    Args:
        reading (dict): Energy reading to send
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        response = requests.post(API_URL, json=reading, timeout=5)
        response.raise_for_status()
        
        print(f"Sent: {reading}")
        print(f"Response: {response.status_code} - {response.json()}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error sending data to API: {e}")
        return False

def main():
    """Main simulation loop"""
    print("Starting ESP32 simulator...")
    print(f"Sending data to: {API_URL}")
    
    # Counter for anomalies
    anomaly_counter = 0
    
    while True:
        # Introduce anomalies occasionally
        include_anomaly = False
        anomaly_counter += 1
        
        # Generate anomaly every 10th reading
        if anomaly_counter >= 10:
            include_anomaly = True
            anomaly_counter = 0
            print("Generating anomaly in this reading...")
        
        # Generate and send reading
        reading = generate_reading(include_anomaly)
        success = send_reading_to_api(reading)
        
        # Status based on current value
        if reading["current"] < LOW_THRESHOLD:
            status = "Normal (Green LED)"
        elif reading["current"] < HIGH_THRESHOLD:
            status = "Moderate (Yellow LED)"
        else:
            status = "High Alert (Red LED)"
        
        print(f"Status: {status}")
        print("-" * 50)
        
        # Wait before next reading
        time.sleep(5)  # Send data every 5 seconds

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nSimulation terminated by user")