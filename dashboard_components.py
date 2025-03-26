import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta

from anomaly_detection import get_anomaly_score
from utils import check_threshold_breach

def render_sidebar():
    """Render the sidebar with controls and settings"""
    with st.sidebar:
        st.header("🔧 Dashboard Controls")
        
        # Auto-refresh toggle
        st.session_state.auto_refresh = st.toggle(
            "Auto-refresh data",
            value=st.session_state.get('auto_refresh', True)
        )
        
        # Time window selection for live graph
        st.session_state.live_window = st.select_slider(
            "Live graph time window",
            options=[1, 5, 15, 30, 60],
            value=st.session_state.get('live_window', 15),
            format_func=lambda x: f"{x} minutes"
        )
        
        # Alert thresholds with color indicators
        st.subheader("🚨 Alert Thresholds")
        
        st.markdown("##### RGB LED Status Indicators")
        st.markdown("""
        <div style="display: flex; margin-bottom: 10px;">
            <div style="width: 15px; height: 15px; border-radius: 50%; background-color: #4CAF50; margin-right: 10px;"></div>
            <span>Green: Normal power usage</span>
        </div>
        <div style="display: flex; margin-bottom: 10px;">
            <div style="width: 15px; height: 15px; border-radius: 50%; background-color: #FFA500; margin-right: 10px;"></div>
            <span>Yellow: Moderate spikes</span>
        </div>
        <div style="display: flex; margin-bottom: 15px;">
            <div style="width: 15px; height: 15px; border-radius: 50%; background-color: #F44336; margin-right: 10px;"></div>
            <span>Red: High consumption / Suspicious</span>
        </div>
        """, unsafe_allow_html=True)
        
        st.session_state.alert_threshold_low = st.slider(
            "Low alert threshold (A)",
            min_value=0.5,
            max_value=5.0,
            value=st.session_state.get('alert_threshold_low', 2.0),
            step=0.1,
            help="Current value that triggers yellow LED and moderate alert status"
        )
        
        st.session_state.alert_threshold_high = st.slider(
            "High alert threshold (A)",
            min_value=1.0,
            max_value=10.0,
            value=st.session_state.get('alert_threshold_high', 4.0),
            step=0.1,
            help="Current value that triggers red LED, buzzer, and potential theft alert"
        )
        
        # Add email notification controls
        st.subheader("📧 Email Notifications")
        st.checkbox("Send email on high alerts", value=True, 
                   help="When enabled, an email notification will be sent for potential theft events")
        
        st.markdown("---")
        st.caption("⚡ Energy Monitoring and Detection System")
        st.caption("By team IOT noob's")

def render_metrics_section():
    """Render the metrics and KPIs section"""
    # Get most recent data
    latest_data = st.session_state.live_data.iloc[-1]
    
    # Calculate average values for the day
    daily_avg = st.session_state.historical_data[
        st.session_state.historical_data['timestamp'] >= (datetime.now() - timedelta(days=1))
    ].mean()
    
    # Status based on current reading
    status, color = check_threshold_breach(
        latest_data['current'],
        st.session_state.alert_threshold_low,
        st.session_state.alert_threshold_high
    )
    
    # Display current status with RGB LED indicator
    st.markdown("### Current System Status")
    
    # RGB LED status indicators
    led_cols = st.columns(3)
    with led_cols[0]:
        if color == "green":
            st.markdown("""
            <div style="display: flex; align-items: center;">
                <div style="width: 20px; height: 20px; border-radius: 50%; background-color: #4CAF50; margin-right: 10px;"></div>
                <span style="color: #4CAF50; font-weight: bold;">Normal power usage</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="display: flex; align-items: center;">
                <div style="width: 20px; height: 20px; border-radius: 50%; background-color: #ccc; margin-right: 10px;"></div>
                <span style="color: #777;">Normal power usage</span>
            </div>
            """, unsafe_allow_html=True)
            
    with led_cols[1]:
        if color == "orange":
            st.markdown("""
            <div style="display: flex; align-items: center;">
                <div style="width: 20px; height: 20px; border-radius: 50%; background-color: #FFA500; margin-right: 10px;"></div>
                <span style="color: #FFA500; font-weight: bold;">Moderate spikes</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="display: flex; align-items: center;">
                <div style="width: 20px; height: 20px; border-radius: 50%; background-color: #ccc; margin-right: 10px;"></div>
                <span style="color: #777;">Moderate spikes</span>
            </div>
            """, unsafe_allow_html=True)
            
    with led_cols[2]:
        if color == "red":
            st.markdown("""
            <div style="display: flex; align-items: center;">
                <div style="width: 20px; height: 20px; border-radius: 50%; background-color: #F44336; margin-right: 10px;"></div>
                <span style="color: #F44336; font-weight: bold;">High consumption / Suspicious activity</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="display: flex; align-items: center;">
                <div style="width: 20px; height: 20px; border-radius: 50%; background-color: #ccc; margin-right: 10px;"></div>
                <span style="color: #777;">High consumption / Suspicious activity</span>
            </div>
            """, unsafe_allow_html=True)
    
    # Metrics
    st.metric(
        label="Current (A)",
        value=f"{latest_data['current']:.2f}",
        delta=f"{latest_data['current'] - daily_avg['current']:.2f}"
    )
    
    st.metric(
        label="Voltage (V)",
        value=f"{latest_data['voltage']:.1f}",
        delta=f"{latest_data['voltage'] - daily_avg['voltage']:.1f}"
    )
    
    st.metric(
        label="Power (W)",
        value=f"{latest_data['power']:.1f}",
        delta=f"{latest_data['power'] - daily_avg['power']:.1f}"
    )
    
    # Alert history section
    st.subheader("Recent Alerts")
    
    if not st.session_state.alert_history:
        st.info("No alerts recorded yet.")
    else:
        # Display last 5 alerts, most recent first
        alert_df = pd.DataFrame(st.session_state.alert_history[-5:])
        for _, alert in alert_df.iloc[::-1].iterrows():
            alert_color = "red" if alert['status'] == "High" else "orange"
            # Add a buzzer icon for high alerts (simulating buzzer activation)
            buzzer_icon = "🔔 " if alert['status'] == "High" else ""
            st.markdown(
                f"""
                <div style="padding: 10px; border-left: 5px solid {alert_color}; background-color: #f5f5f5; margin-bottom: 10px;">
                    <strong>{buzzer_icon}{alert['type']}</strong> at {alert['timestamp'].strftime('%H:%M:%S')}<br>
                    Current: {alert['current']:.2f} A | Power: {alert['power']:.2f} W
                </div>
                """, 
                unsafe_allow_html=True
            )

def render_live_monitoring_section():
    """Render the real-time monitoring section with live graph"""
    st.subheader("Real-Time Energy Monitoring")
    
    # Filter data for the selected time window
    window_start = datetime.now() - timedelta(minutes=st.session_state.live_window)
    
    # Create the real-time graph
    fig = go.Figure()
    
    # Add current line
    fig.add_trace(go.Scatter(
        x=st.session_state.live_data['timestamp'],
        y=st.session_state.live_data['current'],
        mode='lines',
        name='Current (A)',
        line=dict(color='#1f77b4', width=2)
    ))
    
    # Add threshold lines
    fig.add_shape(
        type="line",
        x0=st.session_state.live_data['timestamp'].min(),
        x1=st.session_state.live_data['timestamp'].max(),
        y0=st.session_state.alert_threshold_low,
        y1=st.session_state.alert_threshold_low,
        line=dict(color="orange", width=1, dash="dash"),
    )
    
    fig.add_shape(
        type="line",
        x0=st.session_state.live_data['timestamp'].min(),
        x1=st.session_state.live_data['timestamp'].max(),
        y0=st.session_state.alert_threshold_high,
        y1=st.session_state.alert_threshold_high,
        line=dict(color="red", width=1, dash="dash"),
    )
    
    # Customize layout
    fig.update_layout(
        title='Live Current Monitoring',
        xaxis_title='Time',
        yaxis_title='Current (A)',
        height=400,
        margin=dict(l=0, r=0, t=40, b=0),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode="x unified"
    )
    
    # Add range selector
    fig.update_xaxes(
        rangeslider_visible=False,
        rangeselector=dict(
            buttons=list([
                dict(count=5, label="5m", step="minute", stepmode="backward"),
                dict(count=15, label="15m", step="minute", stepmode="backward"),
                dict(count=30, label="30m", step="minute", stepmode="backward"),
                dict(step="all")
            ])
        )
    )
    
    # Highlight threshold zones
    fig.update_layout(
        shapes=[
            # Low alert zone (yellow)
            dict(
                type="rect",
                xref="paper",
                yref="y",
                x0=0,
                y0=st.session_state.alert_threshold_low,
                x1=1,
                y1=st.session_state.alert_threshold_high,
                fillcolor="yellow",
                opacity=0.1,
                layer="below",
                line_width=0,
            ),
            # High alert zone (red)
            dict(
                type="rect",
                xref="paper",
                yref="y",
                x0=0,
                y0=st.session_state.alert_threshold_high,
                x1=1,
                y1=max(st.session_state.live_data['current']) * 1.1,
                fillcolor="red",
                opacity=0.1,
                layer="below",
                line_width=0,
            ),
        ]
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Get latest reading for status indicators
    latest_reading = st.session_state.live_data.iloc[-1]
    status, color = check_threshold_breach(
        latest_reading['current'],
        st.session_state.alert_threshold_low,
        st.session_state.alert_threshold_high
    )
    
    # Status indicators
    cols = st.columns(3)
    with cols[0]:
        if color == "green":
            st.success("Normal")
    with cols[1]:
        if color == "orange":
            st.warning("Moderate")
    with cols[2]:
        if color == "red":
            st.error("High Alert")

def render_historical_data_section():
    """Render the historical data visualization section"""
    st.subheader("Historical Energy Consumption")
    
    # Time period selector for historical data
    col1, col2 = st.columns(2)
    with col1:
        period = st.selectbox(
            "Select time period",
            options=["Last 24 Hours", "Last Week", "Last Month"],
            index=0
        )
    
    with col2:
        aggregation = st.selectbox(
            "Aggregation",
            options=["Minute", "Hour", "Day"],
            index=1
        )
    
    # Filter historical data based on selected period
    if period == "Last 24 Hours":
        start_date = datetime.now() - timedelta(days=1)
    elif period == "Last Week":
        start_date = datetime.now() - timedelta(weeks=1)
    else:  # Last Month
        start_date = datetime.now() - timedelta(days=30)
    
    filtered_data = st.session_state.historical_data[
        st.session_state.historical_data['timestamp'] >= start_date
    ]
    
    # Aggregate data if needed
    if aggregation == "Hour":
        # Resample to hourly data
        resampled_data = filtered_data.set_index('timestamp').resample('h').mean().reset_index()
    elif aggregation == "Day":
        # Resample to daily data
        resampled_data = filtered_data.set_index('timestamp').resample('D').mean().reset_index()
    else:
        # Minute data (no resampling needed)
        resampled_data = filtered_data
    
    # Create visualization tabs
    tab1, tab2, tab3 = st.tabs(["Current", "Power", "Voltage"])
    
    with tab1:
        # Current over time
        fig = px.line(
            resampled_data,
            x='timestamp',
            y='current',
            title='Current Consumption Over Time',
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        # Power over time
        fig = px.line(
            resampled_data,
            x='timestamp',
            y='power',
            title='Power Consumption Over Time',
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        # Voltage over time
        fig = px.line(
            resampled_data,
            x='timestamp',
            y='voltage',
            title='Voltage Over Time',
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

def render_anomaly_detection_section():
    """Render the AI-powered anomaly detection section"""
    st.subheader("🔍 AI-Powered Anomaly Detection")
    
    # Add model information
    st.markdown("""
    <div style="background-color: #f0f2f6; padding: 15px; border-radius: 5px; margin-bottom: 20px;">
        <h4 style="margin-top: 0;">Model Information</h4>
        <p><strong>Algorithm:</strong> Isolation Forest</p>
        <p><strong>Training Data:</strong> Historical power consumption patterns</p>
        <p><strong>Detection Focus:</strong> Unusual consumption patterns indicating possible energy theft</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Calculate anomaly scores
    historical_data = st.session_state.historical_data.copy()
    features = historical_data[['current', 'voltage', 'power']]
    anomaly_scores = get_anomaly_score(st.session_state.model, features)
    
    # Add anomaly score to the dataframe
    historical_data['anomaly_score'] = anomaly_scores
    
    # Filter to last 24 hours
    start_date = datetime.now() - timedelta(days=1)
    filtered_data = historical_data[historical_data['timestamp'] >= start_date]
    
    # Create scatter plot with color based on anomaly score
    fig = px.scatter(
        filtered_data,
        x='timestamp',
        y='current',
        color='anomaly_score',
        color_continuous_scale='Viridis',
        title='AI Model Anomaly Detection Results (Last 24 Hours)',
        labels={'anomaly_score': 'Anomaly Score'}
    )
    
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    # Highest anomalies
    st.markdown("### 🚨 Predictive Alerts - Potential Energy Theft")
    
    # Get top 5 anomalies
    top_anomalies = historical_data.sort_values(
        by='anomaly_score', 
        ascending=False
    ).head(5)
    
    if len(top_anomalies) > 0:
        for _, anomaly in top_anomalies.iterrows():
            st.markdown(
                f"""
                <div style="padding: 15px; border-left: 5px solid red; background-color: #f5f5f5; margin-bottom: 15px;">
                    <strong>🚨 Potential Energy Theft Detected</strong> at {anomaly['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}<br>
                    Current: {anomaly['current']:.2f} A | Power: {anomaly['power']:.2f} W<br>
                    <strong>AI Confidence:</strong> {min(anomaly['anomaly_score'] * 20, 99):.1f}% | <span style="color: red;">Email notification sent</span>
                </div>
                """, 
                unsafe_allow_html=True
            )
    else:
        st.info("No anomalies detected.")
        
    # Add explanation of how the model works
    with st.expander("How AI Detection Works"):
        st.markdown("""
        The dashboard uses an **Isolation Forest** algorithm to detect unusual patterns in energy consumption:
        
        1. **Training:** The model learns normal consumption patterns from historical data
        2. **Detection:** It identifies abnormal patterns that deviate from expected behavior
        3. **Scoring:** Each data point receives an anomaly score based on how unusual it appears
        4. **Alerting:** High-scoring anomalies trigger alerts and email notifications
        
        Potential signs of energy theft include:
        - Sudden unexplained drops in consumption
        - Brief high-consumption spikes
        - Irregular patterns compared to historical usage
        """)

def render_alert_settings_section():
    """Render the alert settings section"""
    st.subheader("🔍 Threshold Controls & Alert Settings")
    
    # Create columns for the threshold visualization
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Create a simple visualization of the thresholds
        fig = go.Figure()
        
        # Create sample data for visualization
        x = np.linspace(0, 10, 100)
        y = np.zeros_like(x)
        
        # Add area for zones
        fig.add_trace(go.Scatter(
            x=np.concatenate([x, x[::-1]]),
            y=np.concatenate([np.zeros_like(x), np.ones_like(x) * st.session_state.alert_threshold_low]),
            fill='toself',
            fillcolor='rgba(0, 255, 0, 0.2)',
            line=dict(color='rgba(0, 255, 0, 0)'),
            name='Normal Zone (Green LED)',
            showlegend=True
        ))
        
        fig.add_trace(go.Scatter(
            x=np.concatenate([x, x[::-1]]),
            y=np.concatenate([np.ones_like(x) * st.session_state.alert_threshold_low, 
                              np.ones_like(x) * st.session_state.alert_threshold_high]),
            fill='toself',
            fillcolor='rgba(255, 165, 0, 0.2)',
            line=dict(color='rgba(255, 165, 0, 0)'),
            name='Moderate Alert Zone (Yellow LED)',
            showlegend=True
        ))
        
        fig.add_trace(go.Scatter(
            x=np.concatenate([x, x[::-1]]),
            y=np.concatenate([np.ones_like(x) * st.session_state.alert_threshold_high,
                              np.ones_like(x) * 10]),
            fill='toself',
            fillcolor='rgba(255, 0, 0, 0.2)',
            line=dict(color='rgba(255, 0, 0, 0)'),
            name='High Alert Zone (Red LED + Buzzer)',
            showlegend=True
        ))
        
        # Add threshold lines
        fig.add_shape(
            type="line",
            x0=0,
            x1=10,
            y0=st.session_state.alert_threshold_low,
            y1=st.session_state.alert_threshold_low,
            line=dict(color="orange", width=2),
        )
        
        fig.add_shape(
            type="line",
            x0=0,
            x1=10,
            y0=st.session_state.alert_threshold_high,
            y1=st.session_state.alert_threshold_high,
            line=dict(color="red", width=2),
        )
        
        # Customize layout
        fig.update_layout(
            title='Alert Threshold Configuration',
            xaxis_title='Time',
            yaxis_title='Current (A)',
            height=300,
            margin=dict(l=0, r=0, t=40, b=0),
            showlegend=True,
            yaxis=dict(range=[0, 10]),
            xaxis=dict(showticklabels=False)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("### Alert Indicators")
        st.markdown(f"""
        <div style="margin-bottom: 10px;">
            <div style="display: flex; align-items: center; margin-bottom: 5px;">
                <div style="width: 15px; height: 15px; border-radius: 50%; background-color: #4CAF50; margin-right: 10px;"></div>
                <span><strong>Normal:</strong> < {st.session_state.alert_threshold_low} A</span>
            </div>
            <small>Green LED indicates normal power usage</small>
        </div>
        
        <div style="margin-bottom: 10px;">
            <div style="display: flex; align-items: center; margin-bottom: 5px;">
                <div style="width: 15px; height: 15px; border-radius: 50%; background-color: #FFA500; margin-right: 10px;"></div>
                <span><strong>Moderate:</strong> {st.session_state.alert_threshold_low} - {st.session_state.alert_threshold_high} A</span>
            </div>
            <small>Yellow LED indicates moderate consumption spikes</small>
        </div>
        
        <div style="margin-bottom: 10px;">
            <div style="display: flex; align-items: center; margin-bottom: 5px;">
                <div style="width: 15px; height: 15px; border-radius: 50%; background-color: #F44336; margin-right: 10px;"></div>
                <span><strong>High Alert:</strong> > {st.session_state.alert_threshold_high} A</span>
            </div>
            <small>Red LED + Buzzer indicates potential energy theft</small>
        </div>
        """, unsafe_allow_html=True)
        
    # Add MQ3 current sensor info
    st.info("""
    **Sensor Information:**  
    The system uses an DC Motor and Vibrating sensor to create the load. When current exceeds the high threshold, 
    the system activates the buzzer alarm and logs the event as potential energy theft.
    """)
    
    # Allow user to test the alert system
    if st.button("Test Alert System"):
        st.session_state.alert_history.append({
            'timestamp': datetime.now(),
            'current': st.session_state.alert_threshold_high + 1.0,
            'power': (st.session_state.alert_threshold_high + 1.0) * 220,
            'type': "Test Alert",
            'status': "High"
        })
        st.success("Test alert generated! Check the Recent Alerts section to view it.")
