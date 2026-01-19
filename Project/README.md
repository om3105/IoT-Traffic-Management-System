# Smart Traffic Management System

A Streamlit-based dashboard for monitoring real-time traffic data from ThingSpeak, powered by ESP32 and ESP32-CAM.

## 🚀 Features
- **Real-time Traffic Density**: Visualized with live interactive charts.
- **Smart Parking Status**: View available/full status instantly.
- **AQI Monitoring**: Air Quality Index with safety indicators.
- **Emergency Alerts**: Instant visual warning for emergency vehicles.

## 📦 Installation

1.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Configure API Keys:**
    Open `dashboard.py` and replace the placeholders with your ThingSpeak credentials:
    ```python
    THINGSPEAK_CHANNEL_ID = "YOUR_CHANNEL_ID"
    THINGSPEAK_READ_KEY = "YOUR_READ_KEY"
    ```

3.  **Run the Dashboard:**
    ```bash
    streamlit run dashboard.py
    ```

## 🛠 Tech Stack
- **Frontend**: Streamlit (Python)
- **Data Store**: ThingSpeak Cloud
- **Hardware**: ESP32, ESP32-CAM
- **ML**: Python (on Laptop)
