import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Import your custom modular backend engine
from engine.telemetry import fetch_live_link_budget
from engine.ml_predictor import train_satcom_ai, predict_allocation

st.set_page_config(page_title="AI-Driven RRM Allocator", page_icon="🛰️", layout="wide")

st.title("🛰️ AI-Driven Cognitive Radio Resource Management")
st.markdown(f"**System State:** Live Machine Learning Inference | **Timestamp:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
st.markdown("---")

# --- EXECUTE MODULAR BACKEND ---
with st.spinner("Booting Machine Learning Model & Fetching Live Telemetry..."):
    # 1. Train the ML model
    model = train_satcom_ai()
    # 2. Fetch the live Earth data
    live_data = fetch_live_link_budget()
    # 3. Feed the live data into the ML model for predictions
    ai_allocations = predict_allocation(model, live_data)

# --- UI DASHBOARD ---
c1, c2, c3 = st.columns(3)
c1.metric("ML Core", "Random Forest Regressor (Online)")
c2.metric("Tracked Ground Nodes", "4 Active")
c3.metric("Total System Bandwidth Predicted", f"{sum(d['predicted_bw_mhz'] for d in ai_allocations.values()):.1f} MHz")

st.markdown("---")

col1, col2 = st.columns([2, 1])

with col1:
    st.write("#### 📡 AI Predicted Resource Allocation Map")

    # Format data for Plotly
    df = pd.DataFrame([
        {
            "Satellite Spot Beams": name,
            "Predicted Bandwidth (MHz)": round(metrics["predicted_bw_mhz"], 2),
            "Operational MODCOD": metrics["modcod"],
            "Priority Tier": f"Tier {metrics['priority']}"
        }
        for name, metrics in ai_allocations.items()
    ])

    fig = px.bar(
        df, x="Predicted Bandwidth (MHz)", y="Satellite Spot Beams",
        color="Priority Tier", orientation="h", text="Operational MODCOD",
        color_discrete_sequence=["#ef553b", "#00cc96", "#ab63fa"]
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.write("#### 🤖 ML Inference Decision Logs")
    for name, metrics in ai_allocations.items():
        st.markdown(f"**{name}** (Priority {metrics['priority']})")
        st.write(f"• Rain Fade Input: `-{metrics['fade_db']} dB`")

        if metrics["priority"] == 1 and metrics["fade_db"] > 0:
            st.error(f"⚡ **AI Action:** Weather anomaly detected. AI aggressively scaled bandwidth up to **{metrics['predicted_bw_mhz']:.1f} MHz** to protect Tier-1 SLA.")
        elif metrics["priority"] == 3 and metrics["fade_db"] > 0:
            st.warning(f"⚠️ **AI Action:** Tier-3 link fading. AI actively throttled bandwidth to **{metrics['predicted_bw_mhz']:.1f} MHz** to preserve system power.")
        else:
            st.success(f"✅ **AI Action:** Clear skies. Routine bandwidth assigned: **{metrics['predicted_bw_mhz']:.1f} MHz**.")
        st.markdown("---")