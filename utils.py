import json
import os
import pandas as pd
from datetime import datetime

def load_data(filename='energy_data.json'):
    """
    Load data from JSON file.
    
    Args:
        filename (str): Name of the file to load
        
    Returns:
        pd.DataFrame or None: Loaded data or None if file doesn't exist
    """
    try:
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                data = json.load(f)
            
            # Convert to DataFrame
            df = pd.DataFrame(data)
            
            # Convert timestamp strings to datetime objects
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            return df
        else:
            return None
    except Exception as e:
        print(f"Error loading data: {e}")
        return None

def save_data(data, filename='energy_data.json'):
    """
    Save data to JSON file.
    
    Args:
        data (pd.DataFrame): Data to save
        filename (str): Name of the file to save to
    """
    try:
        # Convert DataFrame to list of dictionaries
        data_dict = data.copy()
        
        # Convert datetime objects to strings
        if 'timestamp' in data_dict.columns:
            data_dict['timestamp'] = data_dict['timestamp'].astype(str)
        
        # Save to file
        with open(filename, 'w') as f:
            json.dump(data_dict.to_dict('records'), f)
    except Exception as e:
        print(f"Error saving data: {e}")

def check_threshold_breach(current_value, low_threshold, high_threshold):
    """
    Check if the current value breaches the thresholds.
    
    Args:
        current_value (float): Current value to check
        low_threshold (float): Low threshold value
        high_threshold (float): High threshold value
        
    Returns:
        tuple: (status, color) indicating the status and color for visualization
    """
    if current_value >= high_threshold:
        return "High", "red"
    elif current_value >= low_threshold:
        return "Moderate", "orange"
    else:
        return "Normal", "green"
