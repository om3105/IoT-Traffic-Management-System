"""
Image Capture Module - HTTP/Webcam/IP Camera Support
Handles automatic image capture from multiple sources:
- HTTP URLs (e.g., http://10.52.250.215/capture)
- Webcam (local)
- IP Camera streams (ESP32-CAM, RTSP, etc.)
"""

import cv2
import os
import sys
import requests
import numpy as np
from datetime import datetime
from pathlib import Path

# Add project directory to path
sys.path.insert(0, str(Path(__file__).parent))
from config import CAPTURES_FOLDER, CAMERA_SOURCE, IMAGE_WIDTH, IMAGE_HEIGHT, VERBOSE, REQUEST_TIMEOUT


class ImageCapture:
    """Handles automatic image capture from multiple sources."""
    
    def __init__(self, camera_source=CAMERA_SOURCE):
        self.camera_source = camera_source
        self.captures_folder = CAPTURES_FOLDER
        self.image_count = 0
        self.camera = None
        self.is_http = isinstance(camera_source, str) and (
            camera_source.startswith("http://") or camera_source.startswith("https://")
        )
        self.is_webcam = isinstance(camera_source, int)
        
        self.create_captures_folder()
    
    def create_captures_folder(self):
        """Ensure captures folder exists."""
        Path(self.captures_folder).mkdir(exist_ok=True)
        if VERBOSE:
            print(f"[CAPTURE] Folder ready: {os.path.abspath(self.captures_folder)}")
    
    def connect_camera(self):
        """Connect to camera source."""
        try:
            if self.is_http:
                # HTTP URL - test connection with GET request
                if VERBOSE:
                    print(f"[CAPTURE] Testing HTTP image source: {self.camera_source}...")
                response = requests.get(self.camera_source, timeout=REQUEST_TIMEOUT)
                if response.status_code == 200:
                    if VERBOSE:
                        print("[CAPTURE] ✓ HTTP image source connected successfully")
                    return True
                else:
                    print(f"[CAPTURE] ✗ HTTP server returned status {response.status_code}")
                    return False
            
            elif self.is_webcam:
                # Webcam
                if VERBOSE:
                    print(f"[CAPTURE] Connecting to webcam (index {self.camera_source})...")
                self.camera = cv2.VideoCapture(self.camera_source)
                
                if self.camera.isOpened():
                    self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, IMAGE_WIDTH)
                    self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, IMAGE_HEIGHT)
                    self.camera.set(cv2.CAP_PROP_FPS, 30)
                    if VERBOSE:
                        print("[CAPTURE] ✓ Webcam connected successfully")
                    return True
                else:
                    print("[CAPTURE] ✗ Failed to open webcam")
                    return False
            
            else:
                # Assume it's an IP camera stream
                if VERBOSE:
                    print(f"[CAPTURE] Connecting to IP camera at {self.camera_source}...")
                self.camera = cv2.VideoCapture(self.camera_source)
                if self.camera.isOpened():
                    if VERBOSE:
                        print("[CAPTURE] ✓ IP camera connected successfully")
                    return True
                else:
                    print("[CAPTURE] ✗ Failed to connect to IP camera")
                    return False
        
        except Exception as e:
            print(f"[CAPTURE] ✗ Error connecting camera: {e}")
            return False
    
    def capture_frame_from_http(self):
        """Capture frame from HTTP URL."""
        try:
            response = requests.get(self.camera_source, timeout=REQUEST_TIMEOUT)
            
            if response.status_code == 200:
                # Convert response to numpy array
                image_array = np.frombuffer(response.content, np.uint8)
                # Decode image
                frame = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
                if frame is not None:
                    return frame
                else:
                    print("[CAPTURE] ✗ Failed to decode image from HTTP response")
                    return None
            else:
                print(f"[CAPTURE] ✗ HTTP request failed with status {response.status_code}")
                return None
        
        except requests.exceptions.Timeout:
            print(f"[CAPTURE] ✗ HTTP request timeout ({REQUEST_TIMEOUT}s)")
            return None
        except requests.exceptions.ConnectionError:
            print(f"[CAPTURE] ✗ Connection error to {self.camera_source}")
            return None
        except Exception as e:
            print(f"[CAPTURE] ✗ Error capturing from HTTP: {e}")
            return None
    
    def capture_frame_from_camera(self):
        """Capture frame from webcam or IP camera."""
        try:
            if self.camera is None or not self.camera.isOpened():
                if not self.connect_camera():
                    return None
            
            ret, frame = self.camera.read()
            
            if ret:
                return frame
            else:
                print("[CAPTURE] ✗ Failed to read frame from camera")
                return None
        
        except Exception as e:
            print(f"[CAPTURE] ✗ Error capturing frame: {e}")
            return None
    
    def capture_frame(self):
        """Capture a single frame from the camera/HTTP source."""
        try:
            if self.is_http:
                return self.capture_frame_from_http()
            else:
                return self.capture_frame_from_camera()
        
        except Exception as e:
            print(f"[CAPTURE] ✗ Error in capture_frame: {e}")
            return None
    
    def save_image(self, frame, filename=None):
        """Save captured frame to file."""
        try:
            if frame is None:
                return None
            
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
                filename = f"capture_{timestamp}.jpg"
            
            filepath = os.path.join(self.captures_folder, filename)
            
            success = cv2.imwrite(filepath, frame)
            
            if success:
                self.image_count += 1
                if VERBOSE:
                    print(f"[CAPTURE] ✓ Saved: {filename}")
                return filepath
            else:
                print(f"[CAPTURE] ✗ Failed to save {filename}")
                return None
        
        except Exception as e:
            print(f"[CAPTURE] ✗ Error saving image: {e}")
            return None
    
    def capture_and_save(self):
        """Capture one frame and save it."""
        frame = self.capture_frame()
        if frame is not None:
            return self.save_image(frame)
        return None
    
    def disconnect(self):
        """Disconnect camera."""
        if self.camera is not None:
            self.camera.release()
            if VERBOSE:
                print("[CAPTURE] Camera disconnected")


if __name__ == "__main__":
    # Test capture system
    capturer = ImageCapture()
    
    if capturer.connect_camera():
        # Capture a few test images
        for i in range(3):
            capturer.capture_and_save()
        
        capturer.disconnect()
