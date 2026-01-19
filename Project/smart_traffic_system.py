"""
Smart Traffic Management System - Complete Auto Pipeline
Auto-captures images, detects vehicles, and sends data to ThingSpeak
Focuses only on vehicles present in dataset (cars + ambulances)
"""

import os
import cv2
import time
import threading
import sys
from datetime import datetime
from pathlib import Path
from ultralytics import YOLO

# Add project directory to path
sys.path.insert(0, str(Path(__file__).parent))
from config import (
    MODEL_PATH, CAPTURES_FOLDER, CAPTURE_INTERVAL, NUM_ROADS,
    VEHICLE_CLASSES, CONFIDENCE_THRESHOLD, VERBOSE
)
from image_capture import ImageCapture
from thingspeak_client import ThingSpeakClient


class SmartTrafficSystem:
    """Complete automatic traffic management system."""
    
    def __init__(self):
        self.processed_files = set()
        self.model = None
        self.capturer = None
        self.thingspeak = None
        self.running = False
        
        # Initialize components
        self.setup_system()
    
    def setup_system(self):
        """Initialize all system components."""
        print("\n" + "="*70)
        print("SMART TRAFFIC MANAGEMENT SYSTEM - AUTO PIPELINE")
        print("="*70)
        
        # Load YOLO model (vehicles only)
        print("\n[SETUP] Loading YOLO model (vehicles only)...")
        try:
            if os.path.exists(MODEL_PATH):
                self.model = YOLO(MODEL_PATH)
                print(f"[SETUP] ✓ Custom model loaded: {MODEL_PATH}")
            else:
                print(f"[SETUP] ⚠ Custom model not found. Using yolov8m.pt")
                self.model = YOLO("yolov8m.pt")
        except Exception as e:
            print(f"[SETUP] ✗ Error loading model: {e}")
            return False
        
        # Initialize image capture
        print("\n[SETUP] Initializing camera system...")
        self.capturer = ImageCapture()
        if not self.capturer.connect_camera():
            print("[SETUP] ⚠ Camera connection failed. Will use manual captures only.")
        
        # Initialize ThingSpeak
        print("\n[SETUP] Initializing ThingSpeak connection...")
        self.thingspeak = ThingSpeakClient()
        if not self.thingspeak.verify_connection():
            print("[SETUP] ⚠ ThingSpeak not configured. Update API key in config.py")
        
        print("\n[SETUP] ✓ System initialization complete")
        print("="*70 + "\n")
        return True
    
    def get_road_region(self, image_height, image_width, road_id):
        """Divide image into 4 vertical lanes."""
        lane_width = image_width // NUM_ROADS
        x_min = road_id * lane_width
        x_max = (road_id + 1) * lane_width if road_id < NUM_ROADS - 1 else image_width
        return (0, image_height, x_min, x_max)
    
    def detect_vehicles(self, image_path):
        """
        Detect ONLY vehicles (cars + ambulances) using YOLO.
        Focuses on dataset classes only, no overfitting.
        """
        try:
            image = cv2.imread(image_path)
            if image is None:
                return None
            
            image_height, image_width = image.shape[:2]
            
            # Run YOLO inference
            results = self.model(image, verbose=False, conf=CONFIDENCE_THRESHOLD)
            
            # Initialize road data
            road_data = {}
            for road_id in range(NUM_ROADS):
                road_data[road_id] = {
                    "cars": 0,
                    "ambulances": 0,
                    "total": 0,
                    "density": "LOW"
                }
            
            # Process detections (vehicles only)
            if results and len(results) > 0:
                result = results[0]
                
                if result.boxes is not None:
                    boxes = result.boxes.xyxy.cpu().numpy()
                    classes = result.boxes.cls.cpu().numpy().astype(int)
                    
                    for box, cls_id in zip(boxes, classes):
                        # Only process vehicle classes (0=car, 1=ambulance)
                        if cls_id not in VEHICLE_CLASSES:
                            continue
                        
                        x_min, y_min, x_max, y_max = box
                        center_x = (x_min + x_max) / 2
                        
                        # Determine road
                        road_id = int(center_x // (image_width // NUM_ROADS))
                        road_id = min(road_id, NUM_ROADS - 1)
                        
                        # Count by type
                        if cls_id == 0:
                            road_data[road_id]["cars"] += 1
                        elif cls_id == 1:
                            road_data[road_id]["ambulances"] += 1
                        
                        road_data[road_id]["total"] += 1
            
            # Classify density
            for road_id in road_data:
                total = road_data[road_id]["total"]
                if total < 3:
                    road_data[road_id]["density"] = "LOW"
                elif total < 8:
                    road_data[road_id]["density"] = "MEDIUM"
                else:
                    road_data[road_id]["density"] = "HIGH"
            
            return road_data
        
        except Exception as e:
            print(f"[DETECTION] ✗ Error: {e}")
            return None
    
    def process_image(self, image_path):
        """Process single image and send to ThingSpeak."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        filename = os.path.basename(image_path)
        
        print(f"\n[{timestamp}] Processing: {filename}")
        print("-" * 70)
        
        # Detect vehicles
        road_data = self.detect_vehicles(image_path)
        if road_data is None:
            print("  [SKIP] Detection failed")
            return
        
        # Display results
        total_cars = 0
        total_ambulances = 0
        
        for road_id in range(NUM_ROADS):
            data = road_data[road_id]
            cars = data["cars"]
            ambulances = data["ambulances"]
            total = data["total"]
            density = data["density"]
            
            total_cars += cars
            total_ambulances += ambulances
            
            print(f"  Road {road_id + 1}: {total} vehicles ({cars} cars, {ambulances} ambulances) - {density}")
        
        # Send to ThingSpeak
        print(f"\n  TOTAL: {total_cars + total_ambulances} vehicles "
              f"({total_cars} cars, {total_ambulances} ambulances)")
        
        if self.thingspeak:
            self.thingspeak.send_traffic_data(road_data)
        
        print("-" * 70)
    
    def capture_loop(self):
        """Continuously capture images and add to queue."""
        print(f"\n[CAPTURE] Starting auto-capture loop (interval: {CAPTURE_INTERVAL}s)")
        
        while self.running:
            try:
                if self.capturer:
                    filepath = self.capturer.capture_and_save()
                    if filepath:
                        self.processed_files.add(filepath)
                
                time.sleep(CAPTURE_INTERVAL)
            
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"[CAPTURE] ✗ Error: {e}")
                time.sleep(CAPTURE_INTERVAL)
    
    def detection_loop(self):
        """Continuously process new images."""
        print(f"\n[DETECTION] Starting detection loop")
        
        while self.running:
            try:
                if not os.path.exists(CAPTURES_FOLDER):
                    time.sleep(2)
                    continue
                
                # Check for new images
                for filename in sorted(os.listdir(CAPTURES_FOLDER)):
                    if filename.lower().endswith(('.jpg', '.png', '.jpeg', '.bmp')):
                        filepath = os.path.join(CAPTURES_FOLDER, filename)
                        
                        if filepath not in self.processed_files and os.path.isfile(filepath):
                            time.sleep(0.5)  # Wait for write to complete
                            self.process_image(filepath)
                            self.processed_files.add(filepath)
                
                time.sleep(2)
            
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"[DETECTION] ✗ Error: {e}")
                time.sleep(2)
    
    def run(self):
        """Start the complete pipeline."""
        if not self.setup_system():
            print("[ERROR] Failed to initialize system")
            return
        
        self.running = True
        
        print("[START] Launching parallel capture and detection threads...")
        print("[INFO] Press Ctrl+C to stop\n")
        
        # Start capture thread
        capture_thread = threading.Thread(target=self.capture_loop, daemon=True)
        capture_thread.start()
        
        # Start detection thread
        detection_thread = threading.Thread(target=self.detection_loop, daemon=True)
        detection_thread.start()
        
        try:
            while self.running:
                time.sleep(1)
        
        except KeyboardInterrupt:
            print("\n\n[STOP] Shutting down system...")
            self.running = False
            
            # Cleanup
            if self.capturer:
                self.capturer.disconnect()
            
            print(f"[INFO] Processed {len(self.processed_files)} images total")
            print("="*70 + "\n")


def main():
    """Entry point."""
    system = SmartTrafficSystem()
    system.run()


if __name__ == "__main__":
    main()
