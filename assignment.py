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

# 3. Simulation Logic
def simulate_website_traffic(url):
    try:
        host = url.replace("https://", "").replace("http://", "").split("/")[0]
        dst_ip = socket.gethostbyname(host)
        response = requests.get(url, timeout=5)
        duration = response.elapsed.total_seconds()

        data = {
            'src_port': random.randint(49152, 65535),
            'dst_port': 443 if "https" in url else 80,
            'proto': 6,
            'src_bytes': len(url),
            'dst_bytes': len(response.content),
            'duration': duration,
            'src_pkts': random.randint(1, 10),
            'dst_pkts': random.randint(1, 15),
            'missed_bytes': 0,
            'conn_state': 1
        }
        return data, dst_ip
    except Exception as e:
        return None, str(e)

# ---- UI ----
st.set_page_config(page_title="Sunny Traffic Sentinel", layout="wide")

st.markdown("""
<style>
/* Background */
.stApp,
[data-testid="stAppViewContainer"] {
    background-color: #fff6b0;
}

/* Slightly larger UI + black text */
html, body, [class*="st-"] {
    font-size: 17px;
    color: #000000;
}

/* Text input + number input field */
div[data-testid="stTextInput"] input,
div[data-testid="stNumberInput"] input {
    background-color: #ffffff !important;
    color: #000000 !important;
    border: 1px solid #cfcfcf !important;
}

/* + / - buttons in number input */
div[data-testid="stNumberInput"] button {
    background-color: #ffffff !important;
    color: #000000 !important;
    border: 1px solid #cfcfcf !important;
}
            
/* Run Simulation button */
div[data-testid="stButton"] button {
    background-color: #ffffff !important;
    color: #000000 !important;
    border: 1px solid #cfcfcf !important;
}

/* Header */
.app-header {
    background: linear-gradient(90deg, #ff8a00, #ffd000);
    padding: 20px;
    border-radius: 14px;
    color: #000000;
    margin-bottom: 18px;
}

/* KPI cards */
.kpi {
    background: #fffbe0;   # <-- change this
    border: 1px solid #f5c542;
    padding: 14px;
    border-radius: 12px;
    color: #000000;
    text-align: center;
    box-shadow: 0 6px 12px rgba(255, 170, 0, 0.25);
}

/* Panels */
.panel {
    background: #fffdf0;
    border: 1px solid #f5c542;
    padding: 18px;
    border-radius: 14px;
    box-shadow: 0 8px 16px rgba(255, 170, 0, 0.2);
}

/* Recolor Streamlit default white boxes */
div[data-testid="stMetric"],
div[data-testid="stAlert"],
div[data-testid="stDataFrame"],
div[data-testid="stTable"],
div[data-testid="stContainer"] {
    background-color: #fff3a6 !important;
    border: 1px solid #f5c542 !important;
    box-shadow: 0 6px 12px rgba(255, 170, 0, 0.18) !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="app-header">
    <h1>☀️ Sunny Traffic Sentinel</h1>
    <p>Bright UI for real‑time anomaly detection</p>
</div>
""", unsafe_allow_html=True)

# ---- INPUT ROW ----
c1, c2, c3, c4 = st.columns([3, 2, 2, 2])
with c1:
    target_url = st.text_input("Website URL", "https://google.com")
with c2:
    request_count = st.number_input("Requests", min_value=1, max_value=500, value=10)
with c3:
    delay = st.number_input("Delay (s)", min_value=0.1, max_value=2.0, value=0.5, step=0.1)
with c4:
    start = st.button("🚀 Run Simulation")

# ---- PLACEHOLDERS ----
status_box = st.empty()
kpi_row = st.empty()
chart_box = st.empty()
table_box = st.empty()

if start:
    status_box.info(f"Simulating traffic to {target_url}...")

    history = []

    for i in range(request_count):
        traffic_data, ip_info = simulate_website_traffic(target_url)

        if traffic_data:
            input_df = pd.DataFrame([traffic_data])
            for col in features:
                if col not in input_df.columns:
                    input_df[col] = 0

            prediction = model.predict(input_df[features])[0]
            label = "⚠️ ANOMALY" if prediction == 1 else "✅ NORMAL"

            traffic_data["Result"] = label
            traffic_data["IP"] = ip_info
            history.append(traffic_data)

            hist_df = pd.DataFrame(history)

            # Update KPI row
            with kpi_row.container():
                k1, k2, k3, k4 = st.columns(4)
                k1.markdown('<div class="kpi">📡<br><b>Status</b><br>Running</div>', unsafe_allow_html=True)
                k2.markdown(f'<div class="kpi">🔁<br><b>Requests</b><br>{request_count}</div>', unsafe_allow_html=True)
                k3.markdown(f'<div class="kpi">⏱️<br><b>Delay</b><br>{delay}s</div>', unsafe_allow_html=True)
                k4.markdown(f'<div class="kpi">🌐<br><b>Target</b><br>{target_url}</div>', unsafe_allow_html=True)

            # Update chart (big line-only, darker bg)
            with chart_box.container():
                st.markdown('<div class="panel">', unsafe_allow_html=True)
                fig = px.line(
                hist_df, y="duration", color="Result",
                title="Latency Over Time",
                color_discrete_map={"✅ NORMAL": "#1f4ed8", "⚠️ ANOMALY": "#b91c1c"}  # blue + red
                )
                fig.update_traces(line=dict(width=4))
                fig.update_layout(
                height=520,
                paper_bgcolor="#f2d35f",
                plot_bgcolor="#f2d35f",
                template="plotly_white",
                font_color="black",
                title_font_color="black",
                legend_font_color="black",
                xaxis=dict(
                    color="black",
                    tickfont=dict(color="black"),
                    title_font=dict(color="black")
                    ),
                yaxis=dict(
                    color="black",
                    tickfont=dict(color="black"),
                    title_font=dict(color="black")
                    )
                )
                st.plotly_chart(fig, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            
            # Update table
            with table_box.container():
                st.markdown('<div class="panel">', unsafe_allow_html=True)
                st.subheader("Latest Packets")
                st.dataframe(hist_df.tail(6), use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

            if prediction == 1:
                st.toast(f"Anomaly detected from {ip_info}!", icon="⚠️")

        time.sleep(delay)