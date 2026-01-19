
import streamlit as st
import time
import numpy as np
import requests
import cv2
import os
import importlib
import traffic_engine
from traffic_engine import TrafficAnalyzer

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="VYBE Crew | Traffic AI",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# AI MODEL LOADER
# ==========================================
@st.cache_resource
def get_analyzer():
    # Force reload of the module to pick up changes
    # Updated to TrafficAnalyzer v2 (returns 4 values)
    importlib.reload(traffic_engine)
    from traffic_engine import TrafficAnalyzer
    
    custom_model_path = os.path.join(os.path.dirname(__file__), 'custom_model.pt')
    default_model_path = os.path.join(os.path.dirname(__file__), 'yolov8m.pt')
    
    if os.path.exists(custom_model_path):
        return TrafficAnalyzer(custom_model_path)
    return TrafficAnalyzer(default_model_path)

# ==========================================
# CSS LOADING
# ==========================================
def load_css(file_name, theme):
    base_dir = os.path.dirname(__file__)
    css_path = os.path.join(base_dir, file_name)
    
    with open(css_path) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    
    if theme == "Light Mode":
        try:
            light_css_path = os.path.join(base_dir, "style_light.css")
            with open(light_css_path) as f:
                st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
        except FileNotFoundError:
            pass

# ==========================================
# STATE & LOGIC
# ==========================================

if 'mode' not in st.session_state: st.session_state.mode = 'Simulation'
if 'override' not in st.session_state: st.session_state.override = None
if 'ai_data' not in st.session_state: st.session_state.ai_data = None
if 'ai_images' not in st.session_state: st.session_state.ai_images = {}
if 'run_analysis' not in st.session_state: st.session_state.run_analysis = False
# Timer State
if 'time_left' not in st.session_state: st.session_state.time_left = 0
if 'active_lane' not in st.session_state: st.session_state.active_lane = "N"
if 'is_emg' not in st.session_state: st.session_state.is_emg = False

def get_simulated_data():
    t = time.time()
    return {
        "N": int(50 + 40 * np.sin(t/5)) + np.random.randint(-5, 5),
        "E": int(50 + 40 * np.sin(t/5 + 2)) + np.random.randint(-5, 5),
        "S": int(50 + 40 * np.sin(t/5 + 4)) + np.random.randint(-5, 5),
        "W": int(50 + 40 * np.sin(t/5 + 5)) + np.random.randint(-5, 5),
        "Emg": 1 if np.random.random() > 0.98 else 0,
        "AQI": np.random.randint(20, 150),
        "Latency": np.random.randint(10, 40)
    }

def get_live_data(channel, key):
    try:
        url = f"https://api.thingspeak.com/channels/{channel}/feeds/last.json?api_key={key}"
        r = requests.get(url).json()
        return {
            "N": float(r.get("field1") or 0),
            "E": float(r.get("field2") or 0),
            "S": float(r.get("field3") or 0),
            "W": float(r.get("field4") or 0),
            "Emg": int(r.get("field5") or 0),
            "AQI": float(r.get("field7") or 0),
            "Latency": 120
        }
    except:
        return get_simulated_data()

def logic_engine(data):
    if st.session_state.override:
        return st.session_state.override, 999, False
    if data["Emg"] == 1:
        return "N", 99, True
    d = {k: max(0, min(100, v)) for k,v in data.items() if k in ["N","E","S","W"]}
    active = max(d, key=d.get)
    val = d[active]
    timer = 30 + int((val / 100) * 60)
    return active, timer, False

# ==========================================
# COMPONENTS (HTML)
# ==========================================
def card_html(direction, density, is_active, is_yellow=False):
    if is_active:
        state_cls, r, y, g, status_txt, col = "status-go", "", "", "active", "GO", "#00ff9d"
    elif is_yellow:
        state_cls, r, y, g, status_txt, col = "status-slow", "", "active", "", "SLOW", "#ffcc00"
    else:
        state_cls, r, y, g, status_txt, col = "status-stop", "active", "", "", "STOP", "#ff0055"
        
    names = {"N":"NORTH", "E":"EAST", "S":"SOUTH", "W":"WEST"}
    return f"""<div class="glass-card {state_cls}">
<div class="card-header">{names[direction]} AVE ({direction})</div>
<div class="density-value">{int(density)}<span style="font-size:1rem">%</span></div>
<div class="density-label">TRAFFIC DENSITY</div>
<div class="pole">
<div class="bulb red {r}"></div>
<div class="bulb yellow {y}"></div>
<div class="bulb green {g}"></div>
</div>
<div style="font-family:'Orbitron'; font-weight:bold; color:{col}; margin-top:15px; letter-spacing:2px;">
{status_txt}
</div>
</div>"""

def timer_html(timer, active_lane, is_emg):
    names = {"N":"NORTH", "E":"EAST", "S":"SOUTH", "W":"WEST"}
    lane_txt = "EMERGENCY" if is_emg else f"{names.get(active_lane, active_lane)} OPEN"
    badge_cls = "emergency" if is_emg else ""
    return f"""<div class="ring-container">
<div class="time-label">TIME REMAINING</div>
<div class="time-val">{timer}</div>
<div class="time-label">SECONDS</div>
<div class="lane-badge {badge_cls}">{lane_txt}</div>
</div>"""

def metric_html(label, value, color="#00ff9d"):
    return f"""<div class="metric-box">
<div class="metric-val" style="color:{color}">{value}</div>
<div class="metric-lbl">{label}</div>
</div>"""

# ==========================================
# LAYOUT EXECUTION
# ==========================================
# Header & Theme Control
head_c1, head_c2 = st.columns([5, 1])
with head_c1:
    st.markdown("# 🚦 VYBE CREW | SMART TRAFFIC AI")
    st.markdown("### AUTOMATED NEURAL CONTROL GRID")
with head_c2:
    st.write("") 
    st.write("")
    is_dark = st.toggle("DARK MODE", value=True)
    theme_choice = "Dark Mode" if is_dark else "Light Mode"

load_css("style.css", theme_choice)
st.divider()


# Wrapper Logic
if st.session_state.mode == "Simulation":
    data = get_simulated_data()
elif st.session_state.mode == "AI Analysis":
    if st.session_state.ai_data is None:
        st.session_state.ai_data = get_simulated_data() # Default/Fallback
    data = st.session_state.ai_data
else:
    data = get_simulated_data() # Placeholder for Live Data

# Logic and Timer Management
target_active, target_time, target_emg = logic_engine(data)

if st.session_state.override:
    # Override Mode
    active = st.session_state.override
    timer = 999
    is_emg = False
    st.session_state.active_lane = active # Sync state
elif target_emg and not st.session_state.is_emg:
    # Emergency Interrupt
    st.session_state.active_lane = target_active
    st.session_state.time_left = target_time
    st.session_state.is_emg = True
    active, timer, is_emg = target_active, target_time, True
else:
    # Standard Countdown
    if st.session_state.time_left > 0:
        st.session_state.time_left -= 1
    else:
        # Time expired, switch phase
        st.session_state.active_lane = target_active
        st.session_state.time_left = target_time
        st.session_state.is_emg = target_emg
    
    active = st.session_state.active_lane
    timer = st.session_state.time_left
    is_emg = st.session_state.is_emg

# --- MAIN GRID (Cross Layout) ---
# Row 1: North (Center)
r1_c1, r1_c2, r1_c3 = st.columns(3)
with r1_c2:
    st.markdown(card_html("N", data["N"], active=="N"), unsafe_allow_html=True)
    if st.button("FORCE NORTH", key="btn_n", use_container_width=True):
        st.session_state.override = "N"
        st.rerun()

# Row 2: West (Left) - Timer (Center) - East (Right)
r2_c1, r2_c2, r2_c3 = st.columns(3)
with r2_c1:
    st.markdown(card_html("W", data["W"], active=="W"), unsafe_allow_html=True)
    if st.button("FORCE WEST", key="btn_w", use_container_width=True):
        st.session_state.override = "W"
        st.rerun()
with r2_c2:
    st.write("") # Spacer
    st.markdown(timer_html(timer, active, is_emg), unsafe_allow_html=True)
    if st.button("RESET", key="reset_center", use_container_width=True):
        st.session_state.override = None
        st.rerun()
with r2_c3:
    st.markdown(card_html("E", data["E"], active=="E"), unsafe_allow_html=True)
    if st.button("FORCE EAST", key="btn_e", use_container_width=True):
        st.session_state.override = "E"
        st.rerun()

# Row 3: South (Center)
r3_c1, r3_c2, r3_c3 = st.columns(3)
with r3_c2:
    st.markdown(card_html("S", data["S"], active=="S"), unsafe_allow_html=True)
    if st.button("FORCE SOUTH", key="btn_s", use_container_width=True):
        st.session_state.override = "S"
        st.rerun()

st.write("")
st.write("")
# CONTROLS BAR (Top Priority)
ctrl_c1, ctrl_c2, ctrl_c3, ctrl_c4 = st.columns(4)
with ctrl_c1:
    mode_options = ["Simulation", "AI Analysis", "Live Data"]
    st.session_state.mode = st.selectbox("📊 SOURCE", mode_options, index=mode_options.index(st.session_state.mode) if st.session_state.mode in mode_options else 0)

with ctrl_c2:
    if st.button("🤖 RUN ANALYSIS", type="primary", use_container_width=True):
        st.session_state.run_analysis = True

with ctrl_c3:
    if st.button("⚠️ EMERGENCY MODE", type="secondary", use_container_width=True):
        st.session_state.is_emg = True
        st.session_state.active_lane = "N"

with ctrl_c4:
    if st.button("🔄 RESET", use_container_width=True):
        st.session_state.override = None
        st.session_state.run_analysis = False

st.divider()
# BOTTOM BAR (Metrics)
m1, m2, m3 = st.columns(3)
with m1:
    aqi_col = "#00ff9d" if data["AQI"] < 100 else "#ffcc00"
    st.markdown(metric_html("AIR QUALITY INDEX", data["AQI"], aqi_col), unsafe_allow_html=True)
with m2:
    st.markdown(metric_html("SYSTEM LATENCY", f"{data['Latency']}ms", "#00d4ff"), unsafe_allow_html=True)
with m3:
    emg_txt = "DETECTED" if is_emg else "NONE"
    emg_col = "#ff0055" if is_emg else "#444" 
    st.markdown(metric_html("EMERGENCY SCAN", emg_txt, emg_col), unsafe_allow_html=True)

if st.session_state.mode == "AI Analysis" and st.session_state.ai_images:
    st.write("")
    st.write("")
    st.divider()
    st.markdown("### 📷 LIVE TRAFFIC VISUAL ANALYSIS")
    
    img_cols = st.columns(4)
    directions = ["N", "E", "S", "W"]
    labels = {"N": "NORTH AVE", "E": "EAST AVE", "S": "SOUTH AVE", "W": "WEST AVE"}
    
    for idx, d in enumerate(directions):
        with img_cols[idx]:
            img = st.session_state.ai_images.get(d)
            density = st.session_state.ai_data.get(d, 0)
            
            st.markdown(f"**{labels[d]}**")
            if img is not None:
                st.image(img, use_container_width=True, channels="RGB")
            else:
                st.info("No Feed")
            
            # Density Bar
            st.progress(int(density) / 100)
            st.markdown(f"Density: **{density:.1f}%**")

# Sidebar for AI Analysis Feed Upload
with st.sidebar:
    st.header("📷 CAMERA FEEDS")
    
    if st.session_state.mode == "AI Analysis":
        st.write("📸 **Upload Traffic Feeds**")
        img_n = st.file_uploader("North Feed", type=['jpg','png','jpeg'], key='u_n')
        img_e = st.file_uploader("East Feed", type=['jpg','png','jpeg'], key='u_e')
        img_s = st.file_uploader("South Feed", type=['jpg','png','jpeg'], key='u_s')
        img_w = st.file_uploader("West Feed", type=['jpg','png','jpeg'], key='u_w')
        
        if st.session_state.run_analysis:
            with st.spinner("Analyzing Traffic Patterns..."):
                analyzer = get_analyzer()
                new_data = {}
                new_images = {}
                ambulance_detected = False
                
                # Process each direction
                files = {'N': img_n, 'E': img_e, 'S': img_s, 'W': img_w}
                for direction, img_file in files.items():
                    if img_file:
                        file_bytes = np.asarray(bytearray(img_file.read()), dtype=np.uint8)
                        img = cv2.imdecode(file_bytes, 1)
                        # Analyzer now returns (count, density, annotated_bgr_img, has_ambulance)
                        count, density, annotated_bgr, has_ambulance = analyzer.analyze_road_image(img)
                        
                        # Check for ambulance in any direction
                        if has_ambulance:
                            ambulance_detected = True
                        
                        # Convert Annotated BGR to RGB for Streamlit
                        if annotated_bgr is not None:
                            annotated_rgb = cv2.cvtColor(annotated_bgr, cv2.COLOR_BGR2RGB)
                            new_images[direction] = annotated_rgb
                        new_data[direction] = density
                    else:
                        new_images[direction] = None
                        new_data[direction] = 0.0

                # Set emergency flag if ambulance detected
                new_data["Emg"] = 1 if ambulance_detected else 0
                new_data["AQI"] = np.random.randint(40, 80)
                new_data["Latency"] = np.random.randint(100, 300)
                
                if ambulance_detected:
                    st.success("🚨 AMBULANCE DETECTED! Emergency mode activated.")
                
                st.session_state.ai_data = new_data
                st.session_state.ai_images = new_images
                st.session_state.run_analysis = False
                st.rerun()
    else:
        st.info("Switch to 'AI Analysis' mode to upload feeds")

# Auto Refresh Loop
# time.sleep(1)
# st.rerun()
