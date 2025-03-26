import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

def train_isolation_forest_model(data):
    """
    Train an Isolation Forest model for anomaly detection.
    
    Args:
        data (pd.DataFrame): DataFrame containing features for training
        
    Returns:
        IsolationForest: Trained model
    """
    # Normalize the data
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(data)
    
    # Initialize and train the model
    model = IsolationForest(
        n_estimators=100,
        max_samples='auto',
        contamination=0.01,  # Expected proportion of anomalies
        random_state=42
    )
    
    model.fit(scaled_data)
    
    # Store the scaler in the model object for later use
    model.scaler_ = scaler
    
    return model

def detect_anomalies(model, data):
    """
    Detect anomalies in the data using the trained model.
    
    Args:
        model (IsolationForest): Trained anomaly detection model
        data (pd.DataFrame): Data to check for anomalies
        
    Returns:
        list: Boolean indicators for anomalies (True for anomaly)
    """
    # Scale the data using the stored scaler
    scaled_data = model.scaler_.transform(data)
    
    # Get predictions (-1 for anomalies, 1 for normal)
    predictions = model.predict(scaled_data)
    
    # Convert to boolean (True for anomalies)
    return [p == -1 for p in predictions]

def get_anomaly_score(model, data):
    """
    Get anomaly scores for the data points.
    
    Args:
        model (IsolationForest): Trained anomaly detection model
        data (pd.DataFrame): Data to score
        
    Returns:
        np.array: Anomaly scores (higher is more anomalous)
    """
    # Scale the data using the stored scaler
    scaled_data = model.scaler_.transform(data)
    
    # Get decision function scores
    # Lower (more negative) scores = more anomalous
    scores = model.decision_function(scaled_data)
    
    # Invert and scale for easier interpretation (higher = more anomalous)
    return -scores
