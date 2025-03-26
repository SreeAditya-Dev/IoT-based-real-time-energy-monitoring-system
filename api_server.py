from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from contextlib import asynccontextmanager
import json
import os
import uvicorn
import pandas as pd
import numpy as np
from typing import Optional  # Add this import at the top

# Import from our existing modules
from utils import save_data, load_data
from anomaly_detection import detect_anomalies, get_anomaly_score

# Data model for incoming sensor readings
class SensorReading(BaseModel):
    current: float
    voltage: float
    power: Optional[float] = None  # Changed from float | None
    device_id: str = "ESP32_001"  # Default device ID if not provided
    timestamp: Optional[str] = None  # Changed from str | None

# Global variables for data storage
latest_readings = []
MAX_LATEST_READINGS = 60  # Keep last 60 readings in memory
anomaly_model = None
DATA_FILE = "energy_data.json"

# Define lifespan context manager for startup/shutdown events
@asynccontextmanager
async def lifespan(app):
    # Startup: Load the model and data
    global anomaly_model, latest_readings
    
    # Load existing data if available
    existing_data = load_data(DATA_FILE)
    if existing_data is not None and len(existing_data) > 0:
        print(f"Loaded {len(existing_data)} existing data points")
        
        # Import here to avoid circular imports
        from anomaly_detection import train_isolation_forest_model
        
        # Train anomaly detection model with historical data
        features = existing_data[['current', 'voltage', 'power']]
        anomaly_model = train_isolation_forest_model(features)
        
        # Fill latest_readings with the most recent data
        latest_readings = existing_data.tail(MAX_LATEST_READINGS).to_dict('records')
    else:
        print("No existing data found")
        
    yield  # This is where the app runs
    
    # Shutdown: Clean up resources if needed
    print("Shutting down API server")

# Create FastAPI app with lifespan
app = FastAPI(
    title="Energy Monitoring API",
    lifespan=lifespan
)

# Add CORS middleware to allow requests from ESP32 and frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Energy Monitoring API is running"}

# Endpoint to receive data from ESP32
@app.post("/api/readings")
async def add_reading(reading: SensorReading):
    global latest_readings, anomaly_model
    
    # Process the incoming data
    now = datetime.now()
    
    # Create a new reading dict
    new_reading = {
        "current": reading.current,
        "voltage": reading.voltage,
        "power": reading.power if reading.power is not None else reading.current * reading.voltage,
        "device_id": reading.device_id,
        "timestamp": reading.timestamp if reading.timestamp else now.isoformat()
    }
    
    # Add to latest readings
    latest_readings.append(new_reading)
    if len(latest_readings) > MAX_LATEST_READINGS:
        latest_readings = latest_readings[-MAX_LATEST_READINGS:]
    
    # Check for anomalies if model exists
    is_anomaly = False
    anomaly_score = 0
    
    if anomaly_model is not None:
        # Import here to avoid circular imports
        from anomaly_detection import detect_anomalies, get_anomaly_score
        
        # Create a DataFrame for the new reading
        features_df = pd.DataFrame([[new_reading['current'], new_reading['voltage'], new_reading['power']]], 
                                  columns=['current', 'voltage', 'power'])
        
        # Detect anomalies
        is_anomaly = detect_anomalies(anomaly_model, features_df)[0]
        anomaly_score = float(get_anomaly_score(anomaly_model, features_df)[0])
        
        # Add anomaly information to the reading
        new_reading["is_anomaly"] = is_anomaly
        new_reading["anomaly_score"] = anomaly_score
    
    # Every 5 minutes, save all data to disk
    if now.minute % 5 == 0 and now.second < 10:
        # Load existing data
        existing_data = load_data(DATA_FILE)
        
        if existing_data is not None:
            # Append new data
            updated_data = pd.concat([
                existing_data,
                pd.DataFrame([new_reading])
            ]).reset_index(drop=True)
        else:
            # Create new DataFrame if no existing data
            updated_data = pd.DataFrame([new_reading])
        
        # Save updated data
        save_data(updated_data, DATA_FILE)
        print(f"Saved {len(updated_data)} data points to {DATA_FILE}")
    
    # Return the processed reading with anomaly information
    return {
        "success": True,
        "reading": new_reading,
        "is_anomaly": is_anomaly,
        "anomaly_score": anomaly_score
    }

# Endpoint to get latest readings
@app.get("/api/readings/latest")
async def get_latest_readings(limit: int = 60):
    """Get the latest readings"""
    limit = min(limit, len(latest_readings))  # Don't try to return more than we have
    return {"readings": latest_readings[-limit:]}

# Endpoint to get historical data
@app.get("/api/readings/history")
async def get_historical_data(days: int = 1):
    """Get historical data for specified number of days"""
    # Load existing data
    data = load_data(DATA_FILE)
    
    if data is None or len(data) == 0:
        return {"readings": []}
    
    # Filter to requested time period
    start_date = datetime.now() - pd.Timedelta(days=days)
    filtered_data = data[data['timestamp'] >= start_date]
    
    return {"readings": filtered_data.to_dict('records')}

# Run the server if this file is executed directly
if __name__ == "__main__":
    uvicorn.run("api_server:app", host="0.0.0.0", port=8000, reload=True)