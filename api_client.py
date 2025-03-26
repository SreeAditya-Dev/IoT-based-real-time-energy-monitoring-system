"""
API Client Module for Energy Monitoring Dashboard

This module provides functions to communicate with the FastAPI backend server.
It fetches data from ESP32 devices via the API server.
"""

import requests
import pandas as pd
from datetime import datetime
import json
import streamlit as st
from typing import List, Dict, Any, Optional

# API server URL
API_BASE_URL = "http://localhost:8000"

def get_latest_readings(limit: int = 60) -> List[Dict[str, Any]]:
    """
    Fetch the latest readings from the API.
    
    Args:
        limit (int): Maximum number of readings to fetch
        
    Returns:
        List[Dict[str, Any]]: List of latest readings
    """
    try:
        response = requests.get(f"{API_BASE_URL}/api/readings/latest?limit={limit}", timeout=5)
        response.raise_for_status()  # Raise exception for HTTP errors
        data = response.json()
        return data["readings"]
    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to API server: {e}")
        return []

def get_historical_data(days: int = 1) -> pd.DataFrame:
    """
    Fetch historical data from the API.
    
    Args:
        days (int): Number of days of data to fetch
        
    Returns:
        pd.DataFrame: DataFrame containing historical data
    """
    try:
        response = requests.get(f"{API_BASE_URL}/api/readings/history?days={days}", timeout=5)
        response.raise_for_status()
        data = response.json()
        
        if not data["readings"]:
            return pd.DataFrame()
        
        # Convert to DataFrame
        df = pd.DataFrame(data["readings"])
        
        # Convert timestamp strings to datetime objects
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        return df
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching historical data: {e}")
        return pd.DataFrame()

def check_api_status() -> bool:
    """
    Check if the API server is running and accessible.
    
    Returns:
        bool: True if API is accessible, False otherwise
    """
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=2)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def post_test_reading() -> Optional[Dict[str, Any]]:
    """
    Post a test reading to the API (for testing purposes).
    
    Returns:
        Optional[Dict[str, Any]]: API response or None if request failed
    """
    test_reading = {
        "current": 2.5,
        "voltage": 220.0,
        "device_id": "TEST_DEVICE"
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/readings", 
            json=test_reading,
            timeout=5
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error posting test reading: {e}")
        return None