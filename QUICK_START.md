# 🚀 QUICK START REFERENCE

## 5-Minute Setup

### Step 1: ThingSpeak Configuration (2 min)
```
1. Go to https://thingspeak.com
2. Sign up → Create new channel
3. Add 8 fields (any names work)
4. Copy your API Key
```

### Step 2: Update Config (1 min)
```bash
# Edit Project/config.py
THINGSPEAK_API_KEY = "paste_your_key_here"
THINGSPEAK_CHANNEL_ID = "paste_your_channel_id"
CAMERA_SOURCE = 0  # 0 for webcam, or "http://IP:81/stream" for ESP32
```

### Step 3: Run System (2 min)
```bash
cd /Users/omchandrakantdeo/Developer/C2W/IoT
source venv/bin/activate
python Project/smart_traffic_system.py
```

---

## 🎯 What Happens

✅ Camera starts capturing every 5 seconds  
✅ Images saved to `captures/` folder  
✅ YOLO detects only cars + ambulances  
✅ Counts per road calculated  
✅ Data sent to ThingSpeak  
✅ View real-time dashboard on ThingSpeak  

---

## 📊 Output You'll See

```
[SETUP] ✓ System initialization complete

[START] Launching parallel capture and detection threads...

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

## 🎛 Important Settings

| Setting | Location | Default | Options |
|---------|----------|---------|---------|
| API Key | `config.py` | `YOUR_KEY` | Your ThingSpeak API key |
| Camera | `config.py` | `0` | `0` (webcam) or `"http://IP:81/stream"` (ESP32) |
| Capture Interval | `config.py` | `5` | 1-60 seconds |
| Model | `config.py` | `custom_model.pt` | Your trained YOLO model |
| Roads | `config.py` | `4` | 1-8 roads |

---

## 🐛 Troubleshoot

**Camera not working?**
```bash
# Test camera
python Project/image_capture.py
# Should save test images to captures/
```

**ThingSpeak not receiving data?**
```bash
# Check connection
python -c "from Project.thingspeak_client import ThingSpeakClient; ThingSpeakClient().verify_connection()"
```

**Model not loading?**
- Check if `Project/custom_model.pt` exists
- Falls back to `yolov8m.pt` automatically

---

## 📁 File Locations

```
Local Project:
/Users/omchandrakantdeo/Developer/C2W/IoT/

GitHub:
https://github.com/om3105/IoT-Traffic-Management-System

Main System:
Project/smart_traffic_system.py

Config:
Project/config.py
```

---

## 🔄 Workflow

1. **Setup** → Configure config.py
2. **Run** → `python Project/smart_traffic_system.py`
3. **Monitor** → Check ThingSpeak dashboard
4. **Stop** → Press Ctrl+C

---

## 📞 Support Files

| File | Purpose |
|------|---------|
| `PROJECT_COMPLETE.md` | Full project summary |
| `README_UPDATED.md` | Complete documentation |
| `SYSTEM_SETUP.md` | Detailed setup guide |
| `config.py` | All configuration options |

---

## ✅ Pre-Flight Checklist

- [ ] ThingSpeak account created
- [ ] API key copied to config.py
- [ ] Camera source set (0 or IP)
- [ ] `custom_model.pt` exists
- [ ] Virtual environment ready
- [ ] Dependencies installed

**If all checked → Ready to fly! 🚀**

---

## 🎓 Key Concepts

- **Vehicles-Only:** Model detects ONLY cars & ambulances (no overfitting)
- **4 Roads:** Image divided into 4 vertical lanes for per-road analysis
- **Auto Pipeline:** Continuous automatic operation with no user input
- **Cloud Ready:** Real-time ThingSpeak integration for IoT monitoring
- **Multi-Threaded:** Capture and detection run in parallel

---

## 💡 Advanced Tips

**Speed up processing:**
```python
CAPTURE_INTERVAL = 2  # More frequent captures
CONFIDENCE_THRESHOLD = 0.6  # Stricter detection
```

**Better accuracy:**
```bash
# Retrain model on your data
python Project/train.py
```

**View real-time logs:**
```bash
python Project/smart_traffic_system.py | tee traffic.log
```

---

## 🎉 You're All Set!

Your Smart Traffic Management System is ready to detect traffic in real-time!

**Next:** Run it and watch your ThingSpeak dashboard update live! 📊

---

**Repository:** https://github.com/om3105/IoT-Traffic-Management-System  
**Status:** ✅ Production Ready
