import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def simulate_energy_data(n_points=1440, include_anomalies=False):
    """
    Generate simulated energy consumption data.
    
    Args:
        n_points (int): Number of data points to generate
        include_anomalies (bool): Whether to include anomalies in the data
    
    Returns:
        pd.DataFrame: DataFrame containing simulated energy data
    """
    # Generate timestamps (one per minute)
    end_time = datetime.now()
    start_time = end_time - timedelta(minutes=n_points)
    timestamps = [start_time + timedelta(minutes=i) for i in range(n_points)]
    
    # Base patterns for normal consumption
    # Daily pattern with two peaks (morning and evening)
    hour_of_day = np.array([t.hour + t.minute/60 for t in timestamps])
    
    # Morning peak (around 7-9 AM)
    morning_peak = 2.5 * np.exp(-0.5 * ((hour_of_day - 8) / 1.5) ** 2)
    
    # Evening peak (around 6-9 PM)
    evening_peak = 3 * np.exp(-0.5 * ((hour_of_day - 19) / 2) ** 2)
    
    # Base load (always present)
    base_load = 0.8 + 0.2 * np.sin(2 * np.pi * hour_of_day / 24)
    
    # Combine patterns with some noise
    current = base_load + morning_peak + evening_peak + np.random.normal(0, 0.1, n_points)
    
    # Ensure positive values
    current = np.maximum(0.1, current)
    
    # Generate voltage with small variations around 220V
    voltage = 220 + np.random.normal(0, 2, n_points)
    
    # Calculate power
    power = current * voltage
    
    # Create DataFrame
    df = pd.DataFrame({
        'timestamp': timestamps,
        'current': current,
        'voltage': voltage,
        'power': power
    })
    
    # Add anomalies if requested
    if include_anomalies:
        # Randomly select indices for anomalies (approximately 1% of data)
        anomaly_count = int(n_points * 0.01)
        anomaly_indices = np.random.choice(n_points, size=anomaly_count, replace=False)
        
        for idx in anomaly_indices:
            # Different types of anomalies
            anomaly_type = np.random.choice(['spike', 'drop', 'fluctuation'])
            
            if anomaly_type == 'spike':
                # Sudden spike in current (potential theft)
                df.loc[idx, 'current'] = df.loc[idx, 'current'] * np.random.uniform(2.5, 4.0)
            
            elif anomaly_type == 'drop':
                # Sudden drop in current (potential outage)
                df.loc[idx, 'current'] = df.loc[idx, 'current'] * np.random.uniform(0.1, 0.4)
            
            elif anomaly_type == 'fluctuation':
                # Unusual fluctuation pattern
                if idx < n_points - 5:
                    fluctuation = np.random.uniform(0.6, 1.8, 5)
                    df.loc[idx:idx+4, 'current'] = df.loc[idx:idx+4, 'current'] * fluctuation
            
            # Recalculate power after modifying current
            df.loc[idx, 'power'] = df.loc[idx, 'current'] * df.loc[idx, 'voltage']
    
    return df

def get_live_data_point(last_point, include_anomalies=False, anomaly_probability=0.02):
    """
    Generate a single new data point based on the last data point.
    
    Args:
        last_point (pd.Series): The last data point
        include_anomalies (bool): Whether to include potential anomalies
        anomaly_probability (float): Probability of generating an anomaly
    
    Returns:
        dict: New data point
    """
    # Get hour of day for pattern calculation
    now = datetime.now()
    hour_of_day = now.hour + now.minute/60
    
    # Morning peak (around 7-9 AM)
    morning_factor = 2.5 * np.exp(-0.5 * ((hour_of_day - 8) / 1.5) ** 2)
    
    # Evening peak (around 6-9 PM)
    evening_factor = 3 * np.exp(-0.5 * ((hour_of_day - 19) / 2) ** 2)
    
    # Base load (always present)
    base_load = 0.8 + 0.2 * np.sin(2 * np.pi * hour_of_day / 24)
    
    # Start with previous value and adjust based on time patterns
    target_current = base_load + morning_factor + evening_factor
    
    # Gradually move toward the target with some noise
    new_current = last_point['current'] * 0.9 + target_current * 0.1 + np.random.normal(0, 0.05)
    new_current = max(0.1, new_current)  # Ensure positive value
    
    # Generate voltage with small variations around 220V
    new_voltage = 220 + np.random.normal(0, 0.5)
    
    # Introduce anomaly with specified probability
    if include_anomalies and np.random.random() < anomaly_probability:
        anomaly_type = np.random.choice(['spike', 'drop'])
        
        if anomaly_type == 'spike':
            # Sudden spike in current (potential theft)
            new_current = new_current * np.random.uniform(2.5, 4.0)
        
        elif anomaly_type == 'drop':
            # Sudden drop in current (potential outage)
            new_current = new_current * np.random.uniform(0.1, 0.4)
    
    # Calculate power
    new_power = new_current * new_voltage
    
    return {
        'current': new_current,
        'voltage': new_voltage,
        'power': new_power
    }
