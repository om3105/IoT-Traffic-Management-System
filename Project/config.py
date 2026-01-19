"""
Configuration for Smart Traffic Management System
"""

# ThingSpeak Configuration
THINGSPEAK_API_KEY = "YOUR_THINGSPEAK_API_KEY"  # Replace with your API key
THINGSPEAK_CHANNEL_ID = "YOUR_CHANNEL_ID"  # Replace with your channel ID
THINGSPEAK_BASE_URL = "https://api.thingspeak.com/update"

# Camera Configuration
CAMERA_SOURCE = 0  # 0 for webcam, or IP address for ESP32-CAM (e.g., "http://192.168.1.100:81/stream")
CAPTURE_INTERVAL = 5  # Seconds between captures
IMAGE_WIDTH = 640
IMAGE_HEIGHT = 480

# Model Configuration
MODEL_PATH = "Project/custom_model.pt"  # Your YOLO model
CONFIDENCE_THRESHOLD = 0.5
VEHICLE_CLASSES = [0, 1]  # Car (0) and Ambulance (1) only

# Traffic Density Thresholds
DENSITY_THRESHOLDS = {
    "LOW": 3,      # < 3 vehicles per road
    "MEDIUM": 8,   # 3-7 vehicles per road
    "HIGH": 8      # >= 8 vehicles per road
}

# Folder Configuration
CAPTURES_FOLDER = "captures"
OUTPUT_FOLDER = "output"
NUM_ROADS = 4

# Logging
LOG_FILE = "traffic_system.log"
VERBOSE = True
