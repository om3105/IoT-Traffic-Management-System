"""
Image Capture Module
Handles automatic image capture from webcam or ESP32-CAM
"""

import cv2
import os
import sys
from datetime import datetime
from pathlib import Path

# Add project directory to path
sys.path.insert(0, str(Path(__file__).parent))
from config import CAPTURES_FOLDER, CAMERA_SOURCE, IMAGE_WIDTH, IMAGE_HEIGHT, VERBOSE


class ImageCapture:
    """Handles automatic image capture from camera sources."""
    
    def __init__(self, camera_source=CAMERA_SOURCE):
        self.camera_source = camera_source
        self.captures_folder = CAPTURES_FOLDER
        self.image_count = 0
        self.create_captures_folder()
        self.camera = None
    
    def create_captures_folder(self):
        """Ensure captures folder exists."""
        Path(self.captures_folder).mkdir(exist_ok=True)
        if VERBOSE:
            print(f"[CAPTURE] Folder ready: {os.path.abspath(self.captures_folder)}")
    
    def connect_camera(self):
        """Connect to camera (webcam or ESP32-CAM)."""
        try:
            if isinstance(self.camera_source, str):
                # ESP32-CAM or IP camera
                if VERBOSE:
                    print(f"[CAPTURE] Connecting to ESP32-CAM at {self.camera_source}...")
                self.camera = cv2.VideoCapture(self.camera_source)
            else:
                # Webcam
                if VERBOSE:
                    print(f"[CAPTURE] Connecting to webcam (index {self.camera_source})...")
                self.camera = cv2.VideoCapture(self.camera_source)
            
            # Set camera properties
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, IMAGE_WIDTH)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, IMAGE_HEIGHT)
            self.camera.set(cv2.CAP_PROP_FPS, 30)
            
            if self.camera.isOpened():
                if VERBOSE:
                    print("[CAPTURE] ✓ Camera connected successfully")
                return True
            else:
                print("[CAPTURE] ✗ Failed to open camera")
                return False
        
        except Exception as e:
            print(f"[CAPTURE] ✗ Error connecting camera: {e}")
            return False
    
    def capture_frame(self):
        """Capture a single frame from the camera."""
        try:
            if self.camera is None or not self.camera.isOpened():
                if not self.connect_camera():
                    return None
            
            ret, frame = self.camera.read()
            
            if ret:
                return frame
            else:
                print("[CAPTURE] ✗ Failed to read frame")
                return None
        
        except Exception as e:
            print(f"[CAPTURE] ✗ Error capturing frame: {e}")
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
