import streamlit as st
import pandas as pd
import joblib
import requests
import time
import socket
import random
import plotly.express as px

# 1. Load your Model Assets
model = joblib.load('iot_model.pkl')
features = joblib.load('selected_features.pkl')

st.set_page_config(page_title="Website Traffic Simulator", layout="wide")
st.title("🌐 Website Traffic & Anomaly Detection")

# 2. Sidebar Input
st.sidebar.header("Traffic Controls")
target_url = st.sidebar.text_input("Enter Website URL", "https://google.com")
request_count = st.sidebar.slider("Number of Requests", 1, 500, 10)
delay = st.sidebar.slider("Delay between requests (s)", 0.1, 2.0, 0.5)

# 3. Simulation Logic
def simulate_website_traffic(url):
    try:
        # Get Destination IP
        host = url.replace("https://", "").replace("http://", "").split("/")[0]
        dst_ip = socket.gethostbyname(host)
        
        # Perform the actual request
        start_time = time.time()
        response = requests.get(url, timeout=5)
        duration = response.elapsed.total_seconds()
        
        # Map to TON_IoT format
        data = {
            'src_port': random.randint(49152, 65535),
            'dst_port': 443 if "https" in url else 80,
            'proto': 6, # TCP
            'src_bytes': len(url), 
            'dst_bytes': len(response.content),
            'duration': duration,
            'src_pkts': random.randint(1, 10),
            'dst_pkts': random.randint(1, 15),
            'missed_bytes': 0,
            'conn_state': 1 # S1 (Connection established)
        }
        return data, dst_ip
    except Exception as e:
        return None, str(e)

# 4. Dashboard Interface
if st.button("🚀 Start Traffic Simulation"):
    st.info(f"Simulating traffic to {target_url}...")
    
    # Placeholders for live updates
    col1, col2 = st.columns(2)
    chart_place = col1.empty()
    table_place = col2.empty()
    
    history = []
    
    for i in range(request_count):
        traffic_data, ip_info = simulate_website_traffic(target_url)
        
        if traffic_data:
            # Convert to DataFrame
            input_df = pd.DataFrame([traffic_data])
            
            # Ensure all model features are present
            for col in features:
                if col not in input_df.columns: input_df[col] = 0
            
            # PREDICTION
            prediction = model.predict(input_df[features])[0]
            label = "⚠️ ANOMALY" if prediction == 1 else "✅ NORMAL"
            
            # Update Dashboard
            traffic_data['Result'] = label
            traffic_data['IP'] = ip_info
            history.append(traffic_data)
            
            hist_df = pd.DataFrame(history)
            
            # Visual 1: Live Line Chart (Duration)
            fig = px.line(hist_df, y="duration", title="Request Response Latency (Duration)", color="Result", color_discrete_map={"✅ NORMAL": "green", "⚠️ ANOMALY": "red"})
            chart_place.plotly_chart(fig, use_container_width=True)
            
            # Visual 2: Data Table
            table_place.write("### Latest Traffic Metadata")
            table_place.dataframe(hist_df.tail(5))
            
            if prediction == 1:
                st.toast(f"Anomaly detected from {ip_info}!", icon="⚠️")
        
        time.sleep(delay)

st.sidebar.markdown("""
### 💡 How this works:
1. **Real Request:** Python sends a real HTTP GET to the website.
2. **Metadata Extraction:** We measure response time and payload size.
3. **ML Check:** We feed those real numbers into your IoT model.
4. **No PCAP:** We analyze traffic in memory without saving bulky files.
""")