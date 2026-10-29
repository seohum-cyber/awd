import streamlit as st
import pandas as pd

# Page configuration - Aviation Cockpit Theme
st.set_page_config(
    page_title="Cockpit Flight Fuel Calculator",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Cockpit UI Theme
st.markdown("""
<style>
    /* Dark Cockpit Theme Styling */
    .main {
        background-color: #0b132b;
        color: #e0e6ed;
    }
    .stApp {
        background: linear-gradient(135deg, #0a1128 0%, #1c2541 100%);
    }
    
    /* Custom Headers */
    h1, h2, h3 {
        font-family: 'Courier New', monospace;
        letter-spacing: 1px;
        color: #4cc9f0 !important;
    }
    
    /* Metric Cards */
    .metric-card {
        background-color: #1c2541;
        border: 1px solid #3a506b;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .metric-value {
        font-size: 26px;
        font-weight: bold;
        font-family: 'Courier New', monospace;
    }
    .metric-label {
        font-size: 13px;
        color: #a0aec0;
        text-transform: uppercase;
    }
    
    /* Clearance Banners */
    .status-approved {
        background: rgba(16, 185, 129, 0.15);
        border: 2px solid #10b981;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        color: #10b981;
        font-family: 'Courier New', monospace;
        font-size: 28px;
        font-weight: bold;
        margin-bottom: 20px;
    }
    .status-denied {
        background: rgba(239, 68, 68, 0.15);
        border: 2px solid #ef4444;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        color: #ef4444;
        font-family: 'Courier New', monospace;
        font-size: 28px;
        font-weight: bold;
        margin-bottom: 20px;
    }
    
    /* Progress / Fuel Bar styling */
    .stProgress > div > div > div > div {
        background-color: #4cc9f0;
    }
</style>
""", unsafe_allow_html=True)

# Application Header
st.title("✈️ PILOT FLIGHT FUEL & DISPATCH CALCULATOR")
st.caption("Flight Planning & Legal Fuel Reserve Diagnostics for Pilots")
st.markdown("---")

# Sidebar - Flight Configuration Inputs
st.sidebar.header("🕹️ FLIGHT CONFIGURATION")

# Aircraft Specs Presets
AIRCRAFT_SPECS = {
    "Cessna 172 (C172)": {"speed": 120, "gph": 10.0, "unit": "Gal", "desc": "Single Engine Piston"},
    "Piper Archer (PA28)": {"speed": 128, "gph": 10.5, "unit": "Gal", "desc": "Single Engine Piston"},
    "Boeing 737-800 (B737)": {"speed": 450, "gph": 850.0, "unit": "Gal (x10)", "desc": "Commercial Jet Transport"}
}

aircraft_choice = st.sidebar.selectbox("Aircraft Model", list(AIRCRAFT_SPECS.keys()))
selected_spec = AIRCRAFT_SPECS[aircraft_choice]

st.sidebar.info(f"**Specs:** {selected_spec['desc']}\n* Cruise Speed: **{selected_spec['speed']} Kts**\n* Fuel Flow: **{selected_spec['gph']} {selected_spec['unit']}/hr**")

st.sidebar.subheader("📍 Route Parameters")
dist_dest = st.sidebar.number_input("Destination Distance (NM)", min_value=1.0, value=180.0, step=10.0)
dist_alt = st.sidebar.number_input("Alternate Airport Distance (NM)", min_value=0.0, value=45.0, step=5.0)

st.sidebar.subheader("💨 Enroute Weather")
wind_component = st.sidebar.slider(
    "Wind Component (Knots)",
    min_value=-50,
    max_value=50,
    value=-10,
    help="Negative = Headwind (Slows down), Positive = Tailwind (Speeds up)"
)

if wind_component < 0:
    st.sidebar.caption(f"⚠️ **Headwind:** -{abs(wind_component)} Kts")
elif wind_component > 0:
    st.sidebar.caption(f"🟢 **Tailwind:** +{wind_component} Kts")
else:
    st.sidebar.caption("⚪ **Calm Wind / Crosswind**")

st.sidebar.subheader("⛽ Fuel Load")
fuel_loaded = st.sidebar.number_input(
    f"Loaded Fuel ({selected_spec['unit']})",
    min_value=0.0,
    value=45.0 if "B737" not in aircraft_choice else 3500.0,
    step=5.0
)

# Core Calculations
cruise_speed = selected_spec["speed"]
fuel_flow = selected_spec["gph"]
unit = selected_spec["unit"]

ground_speed = cruise_speed + wind_component

if ground_speed <= 0:
    st.error("🚨 CRITICAL ERROR: Extreme headwind exceeds aircraft cruise speed! Ground speed is 0 or negative.")
else:
    # Flight Times (hours)
    time_dest_hr = dist_dest / ground_speed
    time_alt_hr = dist_alt / ground_speed
    time_reserve_hr = 0.75  # FAA Legal Reserve: 45 Minutes VFR/IFR (0.75 Hours)

    # Fuel Required (Gallons)
    fuel_dest = time_dest_hr * fuel_flow
    fuel_alt = time_alt_hr * fuel_flow
    fuel_reserve = time_reserve_hr * fuel_flow

    total_required = fuel_dest + fuel_alt + fuel_reserve
    fuel_margin = fuel_loaded - total_required

    # -------------------------------------------------------------
    # Clearance Status Banner
    # -------------------------------------------------------------
    if fuel_loaded >= total_required:
        st.markdown(
            f"""
            <div class="status-approved">
                ✅ FLIGHT CLEARANCE: APPROVED<br>
                <span style="font-size:16px; font-weight:normal;">SUFFICIENT FUEL ONBOARD (MARGIN: +{fuel_margin:.1f} {unit})</span>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        shortage = abs(fuel_margin)
        st.markdown(
            f"""
            <div class="status-denied">
                🚨 FLIGHT CLEARANCE: DENIED<br>
                <span style="font-size:16px; font-weight:normal;">INSUFFICIENT FUEL! MINIMUM REQUIRED EXTRA: +{shortage:.1f} {unit}</span>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Key Metrics Display (4 Columns)
    m1, m2, m3, m4 = st.columns(4)

    with m1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Ground Speed (GS)</div>
            <div class="metric-value" style="color:#4cc9f0;">{ground_speed} Kts</div>
        </div>
        """, unsafe_allow_html=True)

    with m2:
        dest_min = int(time_dest_hr * 60)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Destination ETE</div>
            <div class="metric-value" style="color:#e0e6ed;">{dest_min // 60}h {dest_min % 60}m</div>
        </div>
        """, unsafe_allow_html=True)

    with m3:
        alt_min = int(time_alt_hr * 60)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Alternate ETE</div>
            <div class="metric-value" style="color:#e0e6ed;">{alt_min // 60}h {alt_min % 60}m</div>
        </div>
        """, unsafe_allow_html=True)

    with m4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total Required Fuel</div>
            <div class="metric-value" style="color:#f72585;">{total_required:.1f} {unit}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("###")

    # Detailed Fuel Breakdown & Visual Chart
    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.subheader("📊 Fuel Requirement Breakdown")
        
        fuel_data = {
            "Segment": ["1. Destination Flight", "2. Alternate Airport", "3. Legal Reserve (45 min)", "TOTAL REQUIRED"],
            "Flight Time": [f"{time_dest_hr*60:.0f} min", f"{time_alt_hr*60:.0f} min", "45 min", f"{(time_dest_hr+time_alt_hr+0.75)*60:.0f} min"],
            f"Fuel ({unit})": [f"{fuel_dest:.1f}", f"{fuel_alt:.1f}", f"{fuel_reserve:.1f}", f"{total_required:.1f}"]
        }
        st.table(pd.DataFrame(fuel_data))

    with col_right:
        st.subheader("⛽ Fuel Onboard Diagnostic")
        
        # Streamlit Bar Chart comparing segments
        df_chart = pd.DataFrame({
            "Fuel Segment": ["Destination", "Alternate", "Reserve (45m)", "Loaded Fuel"],
            f"Fuel Amount ({unit})": [fuel_dest, fuel_alt, fuel_reserve, fuel_loaded]
        })
        
        st.bar_chart(df_chart.set_index("Fuel Segment"))

    # Aviation Notice Footer
    st.markdown("---")
    st.caption("ℹ️ **FAA Safety Standard**: Legal reserve reflects 45 minutes of reserve fuel. Always verify calculations with the official Aircraft Flight Manual (AFM) or Pilot's Operating Handbook (POH).")
