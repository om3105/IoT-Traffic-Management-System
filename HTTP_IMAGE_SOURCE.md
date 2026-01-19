# HTTP Image Source Integration - Update Guide

## ✅ What's New

Your Smart Traffic System now supports **HTTP-based image sources** like web servers!

Previously configured for: Webcam or IP camera streams  
**Now also supports:** HTTP URLs returning JPEG images

### Example
```
http://10.52.250.215/capture
```

---

## 🎯 Configuration

### Default Setting (Already Configured)
```python
# Project/config.py
CAMERA_SOURCE = "http://10.52.250.215/capture"
CAPTURE_INTERVAL = 5  # seconds
REQUEST_TIMEOUT = 10  # seconds for HTTP requests
```

### To Switch Camera Source

**HTTP Web Server:**
```python
CAMERA_SOURCE = "http://10.52.250.215/capture"
```

**Webcam (Local):**
```python
CAMERA_SOURCE = 0
```

**IP Camera/ESP32-CAM Stream:**
```python
CAMERA_SOURCE = "http://192.168.1.100:81/stream"
```

---

## 🚀 Run the System

```bash
cd /Users/omchandrakantdeo/Developer/C2W/IoT
source venv/bin/activate
python Project/smart_traffic_system.py
```

---

## 📊 System Flow with HTTP Source

```
HTTP Web Server (http://10.52.250.215/capture)
    ↓ (GET request every 5s)
Receive JPEG image data
    ↓ (Decode to OpenCV format)
Image Processing
    ↓ (YOLO vehicle detection)
Traffic Density Analysis
    ↓ (4-road breakdown)
ThingSpeak Upload
    ↓ (Real-time data)
Cloud Dashboard
```

---

## ✨ Features

- ✅ **HTTP JPEG Support** - Directly fetch images from web server
- ✅ **Automatic Retry** - Handles connection errors gracefully
- ✅ **Timeout Protection** - 10-second timeout for each request
- ✅ **Multi-Source** - Works with HTTP, Webcam, and IP cameras
- ✅ **No Manual Interaction** - Fully automatic continuous operation

---

## 🔧 Technical Details

### Supported Sources

| Source Type | Example | Config |
|-------------|---------|--------|
| HTTP JPEG | http://10.52.250.215/capture | Direct URL |
| Webcam | Built-in camera | `0` |
| IP Camera | ESP32-CAM | `"http://IP:81/stream"` |
| RTSP Stream | IP camera stream | `"rtsp://IP/stream"` |

### HTTP Image Capture Flow

1. **Connect:** GET request to HTTP URL
2. **Receive:** JPEG image data (typically 15-20 KB)
3. **Decode:** Convert bytes to OpenCV image
4. **Process:** Run YOLO detection
5. **Save:** Store image locally
6. **Transmit:** Send to ThingSpeak

### Configuration Options

```python
# Project/config.py
CAMERA_SOURCE = "http://10.52.250.215/capture"  # Image URL
CAPTURE_INTERVAL = 5        # Seconds between captures
REQUEST_TIMEOUT = 10        # HTTP timeout in seconds
IMAGE_WIDTH = 640           # Target image width
IMAGE_HEIGHT = 480          # Target image height
```

---

## 📈 Output Example

```
[SETUP] ✓ System initialization complete
[CAPTURE] Testing HTTP image source: http://10.52.250.215/capture...
[CAPTURE] ✓ HTTP image source connected successfully

[START] Launching parallel capture and detection threads...

[2026-01-19 12:01:45] Processing: capture_20260119_120126_090.jpg
----------------------------------------------------------------------
  Road 1: 4 vehicles (3 cars, 1 ambulance) - MEDIUM
  Road 2: 2 vehicles (2 cars, 0 ambulances) - LOW
  Road 3: 3 vehicles (3 cars, 0 ambulances) - LOW
  Road 4: 5 vehicles (4 cars, 1 ambulance) - MEDIUM

  TOTAL: 14 vehicles (12 cars, 2 ambulances)
[THINGSPEAK] ✓ Data sent successfully at 12:01:45
  Road 1: 4 | Road 2: 2 | Road 3: 3 | Road 4: 5
----------------------------------------------------------------------
```

---

## 🐛 Troubleshooting

### "HTTP server returned status 404"
- Check URL is correct
- Verify server is running and accessible
- Test URL in browser first

### "HTTP request timeout"
- Server might be slow
- Increase `REQUEST_TIMEOUT` in config.py
- Check network connectivity

### "Failed to decode image from HTTP response"
- Server might not be returning JPEG
- Verify URL returns valid image data
- Try URL in browser to confirm

### "Connection error to http://..."
- Check if server is reachable
- Verify IP address/hostname
- Check firewall settings

---

## ✅ Verification

### Test HTTP Connection

```bash
python -c "
import requests
url = 'http://10.52.250.215/capture'
response = requests.get(url, timeout=5)
print(f'Status: {response.status_code}')
print(f'Content-Length: {len(response.content)} bytes')
print(f'Content-Type: {response.headers.get(\"content-type\")}')
"
```

### Test Image Capture

```bash
python -c "
from Project.image_capture import ImageCapture
capturer = ImageCapture()
if capturer.connect_camera():
    capturer.capture_and_save()
    print('✓ Image captured successfully')
"
```

---

## 🔄 System Capabilities

- **Parallel Processing:** Capture and detection run simultaneously
- **Continuous Operation:** 24/7 automatic without user interaction
- **Vehicle-Only Detection:** Ignores non-vehicle objects
- **4-Road Analysis:** Per-road traffic density
- **Cloud Integration:** Real-time ThingSpeak data
- **Error Resilience:** Graceful handling of connection issues

---

## 📝 Files Modified

- `config.py` - Updated to use HTTP source
- `image_capture.py` - Added HTTP support with requests library
- Git commit: `7fec2fe`

---

## 🎓 Next Steps

1. **Run the system:**
   ```bash
   python Project/smart_traffic_system.py
   ```

2. **Monitor output** - Watch for vehicle detections and ThingSpeak updates

3. **Check captures folder** - Images are saved to `captures/`

4. **View on ThingSpeak** - Monitor real-time traffic data on your channel

---

## 📞 Support

- **Setup:** See `SYSTEM_SETUP.md`
- **Quick Start:** See `QUICK_START.md`
- **Full Docs:** See `README_UPDATED.md`
- **Project Summary:** See `PROJECT_COMPLETE.md`

---

**Status:** ✅ HTTP Support Added and Tested  
**Current Source:** http://10.52.250.215/capture  
**Last Updated:** January 19, 2026
