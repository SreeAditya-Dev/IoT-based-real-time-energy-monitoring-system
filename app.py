import streamlit as st
import time
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests

# Import custom modules
from data_simulator import simulate_energy_data, get_live_data_point
from anomaly_detection import detect_anomalies, train_isolation_forest_model
from dashboard_components import (
    render_sidebar, 
    render_metrics_section, 
    render_live_monitoring_section,
    render_historical_data_section,
    render_anomaly_detection_section,
    render_alert_settings_section
)
from utils import load_data, save_data, check_threshold_breach
from api_client import get_latest_readings, get_historical_data as get_api_historical_data, check_api_status

# Page configuration
st.set_page_config(
    page_title="Energy Monitoring & Theft Detection Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state variables if they don't exist
if 'alert_threshold_low' not in st.session_state:
    st.session_state.alert_threshold_low = 2.0  # Low alert threshold (Yellow)
    
if 'alert_threshold_high' not in st.session_state:
    st.session_state.alert_threshold_high = 4.0  # High alert threshold (Red)
    
if 'historical_data' not in st.session_state:
    # Generate initial historical data for past 24 hours
    st.session_state.historical_data = simulate_energy_data(
        n_points=1440,  # 24 hours of minute-by-minute data
        include_anomalies=True
    )
    
if 'live_data' not in st.session_state:
    # Initialize with last 60 points from historical data for continuity
    st.session_state.live_data = st.session_state.historical_data[-60:].copy()
    
if 'alert_history' not in st.session_state:
    st.session_state.alert_history = []
    
if 'model' not in st.session_state:
    # Train the anomaly detection model with historical data
    st.session_state.model = train_isolation_forest_model(
        st.session_state.historical_data[['current', 'voltage', 'power']]
    )

# Main dashboard title
st.title("⚡ Real-Time Energy Monitoring & Theft Detection")
st.markdown("#### Smart monitoring system with AI-powered anomaly detection")

# Display sidebar with controls
render_sidebar()

# Create a layout with two columns
col1, col2 = st.columns([2, 1])

with col1:
    # Real-time monitoring section with live graph
    render_live_monitoring_section()

with col2:
    # Metrics and KPIs section
    render_metrics_section()

# Historical data visualization section
render_historical_data_section()

# Anomaly detection section
render_anomaly_detection_section()

# Alert settings section
render_alert_settings_section()

# Function to update data and refresh the dashboard
def update_data():
    # Check if API is accessible
    api_available = check_api_status()
    
    if api_available:
        # Try to get data from API
        latest_readings = get_latest_readings(limit=60)
        
        if latest_readings and len(latest_readings) > 0:
            # Convert to DataFrame
            df_readings = pd.DataFrame(latest_readings)
            
            # Convert timestamp strings to datetime
            df_readings['timestamp'] = pd.to_datetime(df_readings['timestamp'])
            
            # Update live data with readings from API
            st.session_state.live_data = df_readings
            
            # Use the latest reading for threshold checks
            new_point = latest_readings[-1]
            
            # Update historical data if needed
            api_historical = get_api_historical_data(days=1)
            if not api_historical.empty:
                st.session_state.historical_data = api_historical
            
            # Check if there's anomaly information already in the reading
            is_anomaly = new_point.get('is_anomaly', False)
            
            # Check threshold breach
            status, color = check_threshold_breach(
                new_point['current'],
                st.session_state.alert_threshold_low,
                st.session_state.alert_threshold_high
            )
            
            # If it's a high threshold breach or anomaly, add to alert history
            if status == "High" or is_anomaly:
                alert_type = "Anomaly Detected" if is_anomaly else "Threshold Breach"
                st.session_state.alert_history.append({
                    'timestamp': pd.to_datetime(new_point['timestamp']),
                    'current': new_point['current'],
                    'power': new_point['power'],
                    'type': alert_type,
                    'status': status
                })
                
            return True
    
    # Fallback to simulated data if API is not available or no data returned
    # Get new data point
    new_point = get_live_data_point(
        last_point=st.session_state.live_data.iloc[-1],
        include_anomalies=True,
        anomaly_probability=0.02
    )
    
    # Add timestamp
    new_point['timestamp'] = datetime.now()
    
    # Add to live data
    st.session_state.live_data = pd.concat([
        st.session_state.live_data.iloc[1:],  # Remove oldest point
        pd.DataFrame([new_point])  # Add new point
    ]).reset_index(drop=True)
    
    # Add to historical data every minute
    if datetime.now().second < 1:
        st.session_state.historical_data = pd.concat([
            st.session_state.historical_data,
            pd.DataFrame([new_point])
        ]).reset_index(drop=True)
    
    # Check for anomalies
    features_df = pd.DataFrame([[new_point['current'], new_point['voltage'], new_point['power']]], 
                              columns=['current', 'voltage', 'power'])
    is_anomaly = detect_anomalies(
        st.session_state.model,
        features_df
    )[0]
    
    # Check threshold breach
    status, color = check_threshold_breach(
        new_point['current'],
        st.session_state.alert_threshold_low,
        st.session_state.alert_threshold_high
    )
    
    # If it's a high threshold breach or anomaly, add to alert history
    if status == "High" or is_anomaly:
        alert_type = "Anomaly Detected" if is_anomaly else "Threshold Breach"
        st.session_state.alert_history.append({
            'timestamp': new_point['timestamp'],
            'current': new_point['current'],
            'power': new_point['power'],
            'type': alert_type,
            'status': status
        })
    
    return False

# Add a placeholder for status messages
status_placeholder = st.empty()

# Auto refresh data if the toggle is on
if st.session_state.get('auto_refresh', True):
    using_api = update_data()
    
    if using_api:
        status_placeholder.success("✅ Using real-time data from ESP32 via API - Dashboard refreshes automatically")
    else:
        status_placeholder.info("ℹ️ Using simulated data (API not available) - Dashboard refreshes automatically")
    
    # Use st.rerun() for automatic refresh
    st.rerun()
