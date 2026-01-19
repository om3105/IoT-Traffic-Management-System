# Smart Traffic Management System - Setup Guide

## Quick Start

### 1. Install Dependencies
```bash
cd /Users/omchandrakantdeo/Developer/C2W/IoT
source venv/bin/activate
pip install requests opencv-python ultralytics
```

### 2. Configure ThingSpeak
1. Go to https://thingspeak.com
2. Create a new channel with 8 fields:
   - Field 1: Road 1 Vehicles
   - Field 2: Road 2 Vehicles
   - Field 3: Road 3 Vehicles
   - Field 4: Road 4 Vehicles
   - Field 5: Total Cars
   - Field 6: Total Ambulances
   - Field 7: Overall Density (1=LOW, 2=MEDIUM, 3=HIGH)
   - Field 8: Ambulance Alert (1=Present, 0=Absent)

3. Copy your **API Key** and **Channel ID**

### 3. Update Configuration
Edit `Project/config.py`:
```python
THINGSPEAK_API_KEY = "YOUR_ACTUAL_API_KEY"
THINGSPEAK_CHANNEL_ID = "YOUR_ACTUAL_CHANNEL_ID"
```

### 4. Configure Camera Source
Edit `Project/config.py`:

**For Webcam (Local):**
```python
CAMERA_SOURCE = 0  # Default webcam
```

**For ESP32-CAM (Remote):**
```python
CAMERA_SOURCE = "http://192.168.1.100:81/stream"  # Replace with your ESP32 IP
```

### 5. Run the System
```bash
source venv/bin/activate
python Project/smart_traffic_system.py
```

## System Features

### ✅ Automatic Image Capture
- Captures images every 5 seconds (configurable)
- Supports webcam or ESP32-CAM
- Saves to `captures/` folder

### ✅ Vehicle Detection (Vehicles Only)
- Detects only classes present in dataset:
  - **Cars** (class 0)
  - **Ambulances** (class 1)
- Ignores trucks, bikes, etc. (no overfitting)
- Divides road into 4 lanes

### ✅ Real-Time Processing
- Processes images as they're captured
- Parallel capture and detection threads
- Low latency response

### ✅ ThingSpeak Integration
- Sends traffic data every capture
- Real-time dashboard visualization
- Mobile app alerts available

## Output Example

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

## File Structure

```
Project/
├── smart_traffic_system.py       # Main integrated system
├── config.py                      # Configuration file
├── image_capture.py               # Camera capture module
├── thingspeak_client.py           # ThingSpeak integration
├── traffic_density_detector_yolo.py # Alternative manual detection
├── custom_model.pt                # Your trained YOLO model
└── captures/                      # Auto-captured images (created at runtime)
```

## Troubleshooting

### Camera Connection Failed
- Check ESP32 IP address: http://192.168.1.100 (adjust IP)
- For webcam, ensure no other app is using it
- Check camera permissions in System Settings

### ThingSpeak Not Receiving Data
- Verify API key is correct
- Check internet connection
- Ensure channel has 8+ fields
- Check ThingSpeak dashboard for updates

### Model Not Loading
- Ensure `custom_model.pt` exists in Project folder
- Falls back to `yolov8m.pt` if custom model missing
- Models should only detect vehicles (cars + ambulances)

## Performance Tips

1. **Reduce capture interval** for more frequent updates:
   ```python
   CAPTURE_INTERVAL = 2  # 2 seconds
   ```

2. **Adjust vehicle thresholds**:
   ```python
   DENSITY_THRESHOLDS = {"LOW": 2, "MEDIUM": 5, "HIGH": 5}
   ```

3. **Monitor logs**:
   ```bash
   python Project/smart_traffic_system.py | tee traffic_system.log
   ```

## Model Training (For Future Improvements)

Only train on vehicles in your dataset:
```bash
python Project/train.py
```

This ensures the model focuses on accurate vehicle detection without overfitting to irrelevant classes.

---

**Status:** ✅ Production Ready | Vehicles Only | Auto Capture & ThingSpeak Ready
