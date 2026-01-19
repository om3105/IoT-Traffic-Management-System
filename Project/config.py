"""
Configuration for Smart Traffic Management System
"""

# ThingSpeak Configuration
THINGSPEAK_API_KEY = "YOUR_THINGSPEAK_API_KEY"  # Replace with your API key
THINGSPEAK_CHANNEL_ID = "YOUR_CHANNEL_ID"  # Replace with your channel ID
THINGSPEAK_BASE_URL = "https://api.thingspeak.com/update"

# Camera Configuration
CAMERA_SOURCE = "http://10.52.250.215/capture"  # 0 for webcam, HTTP URL for web server, or ESP32-CAM IP
CAPTURE_INTERVAL = 5  # Seconds between captures
IMAGE_WIDTH = 640
IMAGE_HEIGHT = 480
REQUEST_TIMEOUT = 10  # Timeout for HTTP requests in seconds

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
