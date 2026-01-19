# Smart Traffic Management System

**A production-ready ML pipeline for automatic traffic density detection with real-time IoT data transmission.**

## 🎯 Overview

This system automatically:
- 📷 **Captures images** from ESP32-CAM or webcam every 5 seconds
- 🚗 **Detects vehicles** (cars & ambulances only) using YOLO
- 📊 **Analyzes traffic density** across 4 roads in real-time
- ☁️ **Sends data to ThingSpeak** for cloud visualization
- 🚨 **Alerts on ambulances** for priority detection

**Key Feature:** Focuses ONLY on vehicles in the dataset - no overfitting to irrelevant objects.

---

## 📂 Project Structure

```
Project/
├── smart_traffic_system.py        # Main integrated system
├── config.py                       # Configuration (API keys, camera settings)
├── image_capture.py                # Camera capture module
├── thingspeak_client.py            # IoT data transmission
├── traffic_density_detector_yolo.py # Alternative detection (manual mode)
├── custom_model.pt                 # Your trained YOLO model
├── SYSTEM_SETUP.md                 # Setup guide
└── captures/                       # Auto-captured images (created at runtime)
```

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
cd /Users/omchandrakantdeo/Developer/C2W/IoT
source venv/bin/activate
pip install requests opencv-python ultralytics
```

### 2. Configure ThingSpeak
1. Go to https://thingspeak.com
2. Create a new channel with 8 fields:
   - **Field 1-4:** Road 1-4 Vehicles
   - **Field 5:** Total Cars
   - **Field 6:** Total Ambulances
   - **Field 7:** Overall Density (1=LOW, 2=MEDIUM, 3=HIGH)
   - **Field 8:** Ambulance Alert

3. Copy your **API Key** and update `Project/config.py`:
```python
THINGSPEAK_API_KEY = "your_actual_key_here"
THINGSPEAK_CHANNEL_ID = "your_channel_id"
```

### 3. Configure Camera
Edit `Project/config.py`:

**Webcam:**
```python
CAMERA_SOURCE = 0
```

**ESP32-CAM (replace IP):**
```python
CAMERA_SOURCE = "http://192.168.1.100:81/stream"
```

### 4. Run System
```bash
source venv/bin/activate
python Project/smart_traffic_system.py
```

---

## 📊 Output Example

```
[2026-01-19 10:30:45] Processing: capture_20260119_103045_123.jpg
----------------------------------------------------------------------
  Road 1: 5 vehicles (4 cars, 1 ambulance) - MEDIUM
  Road 2: 3 vehicles (3 cars, 0 ambulances) - LOW
  Road 3: 2 vehicles (2 cars, 0 ambulances) - LOW
  Road 4: 6 vehicles (5 cars, 1 ambulance) - MEDIUM

  TOTAL: 16 vehicles (14 cars, 2 ambulances)
[THINGSPEAK] ✓ Data sent successfully at 10:30:45
  Road 1: 5 | Road 2: 3 | Road 3: 2 | Road 4: 6
----------------------------------------------------------------------
```

---

## ⚙️ Configuration Options

### `Project/config.py`

```python
# ThingSpeak
THINGSPEAK_API_KEY = "your_key"
THINGSPEAK_CHANNEL_ID = "your_channel"

# Camera (0=webcam, or "http://IP:port" for ESP32-CAM)
CAMERA_SOURCE = 0
CAPTURE_INTERVAL = 5  # seconds

# Model
MODEL_PATH = "Project/custom_model.pt"
CONFIDENCE_THRESHOLD = 0.5

# Detection
VEHICLE_CLASSES = [0, 1]  # 0=car, 1=ambulance only
NUM_ROADS = 4

# Density thresholds (per road)
DENSITY_THRESHOLDS = {
    "LOW": 3,
    "MEDIUM": 8,
    "HIGH": 8
}
```

---

## 🧠 How It Works

```
┌─────────────────┐
│  Camera Stream  │ (Webcam / ESP32-CAM)
└────────┬────────┘
         │
┌────────▼────────────┐
│  Image Capture      │ (Every 5 seconds)
│  Saves to captures/ │
└────────┬────────────┘
         │
┌────────▼──────────────────┐
│  YOLO Inference            │
│  Detects: Cars + Ambulances│
│  (Vehicles Only!)          │
└────────┬──────────────────┘
         │
┌────────▼───────────────┐
│  4-Road Analysis       │
│  - Count per road      │
│  - Classify density    │
│  - Flag ambulances     │
└────────┬───────────────┘
         │
┌────────▼──────────────┐
│  ThingSpeak Upload    │
│  Real-time dashboard  │
│  Mobile alerts        │
└───────────────────────┘
```

---

## 🔧 Troubleshooting

### Camera Connection Failed
- Check ESP32 IP: http://192.168.1.100
- Ensure webcam not in use by other apps
- Check system permissions

### ThingSpeak Not Updating
- Verify API key in config.py
- Check internet connection
- Confirm channel has 8+ fields

### Model Not Loading
- Ensure `custom_model.pt` exists in Project/
- Falls back to `yolov8m.pt` if missing
- Train model on vehicles only (no trucks, bikes, etc.)

---

## 📈 Performance Tips

**Faster Processing:**
```python
CAPTURE_INTERVAL = 2  # More frequent
CONFIDENCE_THRESHOLD = 0.6  # Stricter filtering
```

**Better Accuracy:**
```python
# Retrain model with only vehicle classes
python Project/train.py
```

**Monitor Logs:**
```bash
python Project/smart_traffic_system.py | tee traffic.log
```

---

## 🎓 Model Details

- **Base:** YOLOv8m
- **Training Data:** Annotated vehicle images
- **Classes:** 
  - 0: Car
  - 1: Ambulance
- **No Overfitting:** Ignores trucks, bikes, and non-vehicle objects

---

## 🔗 Integration Points

### Inputs
- ESP32-CAM video stream
- Webcam feed

### Outputs
- Console logs
- ThingSpeak cloud data
- Real-time traffic dashboard

### Extended Features (Future)
- Database storage (InfluxDB)
- Traffic light control
- Ambulance routing optimization

---

## 📝 Files Overview

| File | Purpose |
|------|---------|
| `smart_traffic_system.py` | Main integrated pipeline |
| `config.py` | Centralized settings |
| `image_capture.py` | Camera control |
| `thingspeak_client.py` | Cloud transmission |
| `traffic_density_detector_yolo.py` | Manual detection mode |
| `SYSTEM_SETUP.md` | Detailed setup guide |

---

## ✅ Feature Checklist

- ✅ Automatic image capture
- ✅ Vehicles-only detection (no overfitting)
- ✅ 4-road traffic analysis
- ✅ Real-time ThingSpeak transmission
- ✅ Ambulance priority detection
- ✅ Configurable thresholds
- ✅ Multi-threaded processing
- ✅ Production-ready code

---

## 📊 GitHub Repository

https://github.com/om3105/IoT-Traffic-Management-System

---

## 👤 Developer

**om3105** | deo.omchandrakant31@gmail.com

---

## 📄 License

This project is part of a final-year engineering initiative.

---

**Status:** ✅ Production Ready | Auto Capture & ThingSpeak Integrated | Vehicles Only Focus
