import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# --- CONFIGURATION & PAGE SETUP ---
st.set_page_config(
    page_title="SatCom Resource Allocator",
    page_icon="📡",
    layout="wide"
)

st.title("📡 Satellite Radio Resource Management (RRM) Allocator")
st.markdown("""
*Based on the Dynamic Spectrum Allocation challenges outlined in **'Artificial Intelligence for Satellite Communication: A Survey'***
***
""")

# --- SIDEBAR CONTROLS (THE ENVIRONMENT) ---
st.sidebar.header("🕹️ Satellite Environment Controls")

# Select Scenario Profile
scenario = st.sidebar.selectbox(
    "Select Network Scenario Profile",
    ["Normal Operations", "Natural Disaster Spike", "Monsoon Heavy Rain Fading"]
)

st.sidebar.markdown("---")
st.sidebar.subheader("Adjust Spot Beam Traffic Loads")

# Set up initial slider positions based on profiles for quick demo transitions
if scenario == "Natural Disaster Spike":
    b1_init, b2_init, b3_init, b4_init = 95, 20, 15, 10
    weather_init = "Clear Sky"
elif scenario == "Monsoon Heavy Rain Fading":
    b1_init, b2_init, b3_init, b4_init = 40, 35, 30, 25
    weather_init = "Heavy Monsoon Rain"
else:  # Normal Operations
    b1_init, b2_init, b3_init, b4_init = 45, 50, 35, 20
    weather_init = "Clear Sky"

# Render interactive traffic sliders
beam1_traffic = st.sidebar.slider("Beam 1 Traffic (Mbps)", 0, 100, b1_init)
beam2_traffic = st.sidebar.slider("Beam 2 Traffic (Mbps)", 0, 100, b2_init)
beam3_traffic = st.sidebar.slider("Beam 3 Traffic (Mbps)", 0, 100, b3_init)
beam4_traffic = st.sidebar.slider("Beam 4 Traffic (Mbps)", 0, 100, b4_init)

weather_cond = st.sidebar.selectbox(
    "Atmospheric Weather Condition",
    ["Clear Sky", "Light Rain", "Heavy Monsoon Rain"],
    index=["Clear Sky", "Light Rain", "Heavy Monsoon Rain"].index(weather_init)
)

# --- THE RESOURCE ALLOCATION CORE ENGINE ---
# Total bandwidth capacity pool available to allocate = 100 MHz
total_bandwidth_pool = 100

# Compile demands vector
demands = np.array([beam1_traffic, beam2_traffic, beam3_traffic, beam4_traffic])
total_demand = np.sum(demands) if np.sum(demands) > 0 else 1

# Proportional dynamic spectrum mapping algorithm
raw_allocations = (demands / total_demand) * total_bandwidth_pool

# Simulate Rain Attenuation signal degradation factor
attenuation_factor = 1.0
if weather_cond == "Light Rain":
    attenuation_factor = 0.85
elif weather_cond == "Heavy Monsoon Rain":
    attenuation_factor = 0.60

effective_capacity = raw_allocations * attenuation_factor

# --- MAIN DASHBOARD INTERFACE LAYOUT ---
st.subheader("📊 Real-Time Spectrum & Resource Optimization")

# Key Performance Indicators (KPIs)
kpi1, kpi2, kpi3 = st.columns(3)
kpi1.metric(label="Network Context Profile", value=scenario)
kpi2.metric(label="Total Network Traffic Demand", value=f"{np.sum(demands)} Mbps")
kpi3.metric(label="Global Spectrum Utilization Ratio", value=f"{min(100, int((np.sum(demands)/200)*100))}%")

st.markdown("---")

# Layout columns for data visualizations and system outputs
col1, col2 = st.columns([2, 1])

with col1:
    st.write("#### Dynamic Frequency Allocations Matrix")

    # Bundle calculations into a structured dataframe
    df_allocs = pd.DataFrame({
        "Satellite Beams": ["Beam 1", "Beam 2", "Beam 3", "Beam 4"],
        "Allocated Bandwidth (MHz)": np.round(raw_allocations, 2),
        "Effective Link Throughput (Mbps)": np.round(effective_capacity, 2)
    })

    # Plot allocations using a clear, clean horizontal bar chart
    fig = px.bar(
        df_allocs,
        x="Allocated Bandwidth (MHz)",
        y="Satellite Beams",
        orientation='h',
        color="Effective Link Throughput (Mbps)",
        color_continuous_scale="Viridis",
        text="Allocated Bandwidth (MHz)"
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.write("#### 📡 System Status Warnings")
    for idx, row in df_allocs.iterrows():
        if row["Allocated Bandwidth (MHz)"] > 40:
            st.error(f"⚠️ {row['Satellite Beams']}: Severe Interference/Congestion Risk!")
        elif row["Effective Link Throughput (Mbps)"] < 20:
            st.warning(f"📉 {row['Satellite Beams']}: Rain Attenuation Drop Danger.")
        else:
            st.success(f"✅ {row['Satellite Beams']}: Link Budget Balanced.")