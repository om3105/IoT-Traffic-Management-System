"""
Smart Traffic Management System - YOLO-based ML Pipeline with Multi-Road Detection
Monitors "captures/" folder and detects cars/ambulances across 4 roads.
Categorizes traffic density per road.
"""

import os
import cv2
import numpy as np
from datetime import datetime
from pathlib import Path
import time
from ultralytics import YOLO

# Configuration
CAPTURES_FOLDER = "captures"
MODEL_PATH = "Project/custom_model.pt"  # Your trained YOLO model
POLLING_INTERVAL = 2  # seconds between folder checks

# Road/Lane division (4 vertical lanes)
NUM_ROADS = 4

# Class names for detection
CLASS_NAMES = {
    0: "car",
    1: "ambulance"
}


class MultiRoadTrafficDetector:
    """Detects vehicles across 4 roads and classifies traffic density."""
    
    def __init__(self, model_path=MODEL_PATH):
        self.processed_files = set()
        self.create_captures_folder()
        self.load_model(model_path)
    
    def create_captures_folder(self):
        """Ensure captures folder exists."""
        Path(CAPTURES_FOLDER).mkdir(exist_ok=True)
        print(f"[INIT] Monitoring folder: {os.path.abspath(CAPTURES_FOLDER)}")
    
    def load_model(self, model_path):
        """Load YOLO model."""
        if not os.path.exists(model_path):
            print(f"[ERROR] Model not found at {model_path}")
            print(f"[INFO] Using default yolov8m.pt instead")
            self.model = YOLO("yolov8m.pt")
        else:
            print(f"[LOAD] Loading custom model: {model_path}")
            self.model = YOLO(model_path)
            print(f"[SUCCESS] Model loaded successfully")
    
    def get_road_region(self, image_height, image_width, road_id):
        """
        Define region of interest for each road.
        Divides image into 4 vertical lanes.
        
        road_id: 0, 1, 2, 3 (left to right)
        Returns: (y_min, y_max, x_min, x_max)
        """
        lane_width = image_width // NUM_ROADS
        x_min = road_id * lane_width
        x_max = (road_id + 1) * lane_width if road_id < NUM_ROADS - 1 else image_width
        y_min = 0
        y_max = image_height
        
        return (y_min, y_max, x_min, x_max)
    
    def detect_vehicles(self, image_path):
        """
        Detect cars and ambulances using YOLO.
        Returns: detections for each road
        """
        try:
            # Read image
            image = cv2.imread(image_path)
            if image is None:
                print(f"[ERROR] Failed to read image: {image_path}")
                return None
            
            image_height, image_width = image.shape[:2]
            
            # Run YOLO inference
            results = self.model(image, verbose=False)
            
            # Initialize road data
            road_data = {}
            for road_id in range(NUM_ROADS):
                road_data[road_id] = {
                    "cars": 0,
                    "ambulances": 0,
                    "total": 0,
                    "region": self.get_road_region(image_height, image_width, road_id)
                }
            
            # Process detections
            if results and len(results) > 0:
                result = results[0]
                
                if result.boxes is not None:
                    boxes = result.boxes.xyxy.cpu().numpy()  # Bounding boxes
                    classes = result.boxes.cls.cpu().numpy().astype(int)  # Class IDs
                    confidences = result.boxes.conf.cpu().numpy()  # Confidence scores
                    
                    # Process each detection
                    for box, cls_id, conf in zip(boxes, classes, confidences):
                        x_min, y_min, x_max, y_max = box
                        center_x = (x_min + x_max) / 2
                        
                        # Determine which road this detection belongs to
                        road_id = int(center_x // (image_width // NUM_ROADS))
                        road_id = min(road_id, NUM_ROADS - 1)
                        
                        # Count by type
                        if cls_id == 0:  # Car
                            road_data[road_id]["cars"] += 1
                        elif cls_id == 1:  # Ambulance
                            road_data[road_id]["ambulances"] += 1
                        
                        road_data[road_id]["total"] += 1
            
            return road_data
        
        except Exception as e:
            print(f"[ERROR] Exception in vehicle detection: {e}")
            return None
    
    def classify_density(self, vehicle_count):
        """
        Classify traffic density based on vehicle count.
        Adjusted thresholds for per-road detection.
        """
        if vehicle_count < 3:
            return "LOW"
        elif vehicle_count < 8:
            return "MEDIUM"
        else:
            return "HIGH"
    
    def get_road_name(self, road_id):
        """Return friendly name for road/lane."""
        names = ["Road 1 (Lane 1)", "Road 2 (Lane 2)", "Road 3 (Lane 3)", "Road 4 (Lane 4)"]
        return names[road_id]
    
    def process_image(self, image_path):
        """
        Process a single image: detect vehicles per road and classify density.
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        filename = os.path.basename(image_path)
        
        print(f"\n[{timestamp}] Processing: {filename}")
        print("=" * 70)
        
        # Detect vehicles across all roads
        road_data = self.detect_vehicles(image_path)
        
        if road_data is None:
            print("  [SKIP] Detection failed")
            return None
        
        # Display results per road
        total_cars = 0
        total_ambulances = 0
        
        for road_id in range(NUM_ROADS):
            data = road_data[road_id]
            cars = data["cars"]
            ambulances = data["ambulances"]
            total = data["total"]
            density = self.classify_density(total)
            
            total_cars += cars
            total_ambulances += ambulances
            
            road_name = self.get_road_name(road_id)
            print(f"  {road_name}:")
            print(f"    ├─ Cars: {cars}")
            print(f"    ├─ Ambulances: {ambulances}")
            print(f"    ├─ Total Vehicles: {total}")
            print(f"    └─ Density: {density}")
        
        # Summary
        print("-" * 70)
        print(f"  TOTAL SUMMARY:")
        print(f"    ├─ Total Cars: {total_cars}")
        print(f"    ├─ Total Ambulances: {total_ambulances}")
        print(f"    └─ Total Vehicles: {total_cars + total_ambulances}")
        print("=" * 70)
        
        return {
            "filename": filename,
            "timestamp": timestamp,
            "road_data": road_data,
            "total_cars": total_cars,
            "total_ambulances": total_ambulances,
            "total_vehicles": total_cars + total_ambulances
        }
    
    def get_new_images(self):
        """
        Get list of unprocessed images in captures folder.
        Returns: list of image paths
        """
        if not os.path.exists(CAPTURES_FOLDER):
            return []
        
        image_files = []
        for filename in os.listdir(CAPTURES_FOLDER):
            # Check if it's an image file
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
                filepath = os.path.join(CAPTURES_FOLDER, filename)
                if filepath not in self.processed_files and os.path.isfile(filepath):
                    image_files.append(filepath)
        
        return sorted(image_files)
    
    def run(self):
        """
        Main loop: continuously monitor captures folder and process new images.
        """
        print("\n" + "="*70)
        print("SMART TRAFFIC MANAGEMENT SYSTEM - MULTI-ROAD ML PIPELINE")
        print("="*70)
        print("[START] Monitoring for new images...")
        print(f"[INFO] Check interval: {POLLING_INTERVAL} seconds")
        print(f"[INFO] Detection mode: YOLO (Cars + Ambulances)")
        print(f"[INFO] Roads: {NUM_ROADS} lanes")
        print("="*70 + "\n")
        
        try:
            while True:
                # Get new images
                new_images = self.get_new_images()
                
                if new_images:
                    for image_path in new_images:
                        # Process image
                        result = self.process_image(image_path)
                        
                        # Mark as processed
                        self.processed_files.add(image_path)
                
                # Wait before checking again
                time.sleep(POLLING_INTERVAL)
        
        except KeyboardInterrupt:
            print("\n\n[STOP] Pipeline interrupted by user.")
            print(f"[INFO] Processed {len(self.processed_files)} images in total.")
            print("="*70 + "\n")


def main():
    """Entry point for the multi-road traffic density detection pipeline."""
    detector = MultiRoadTrafficDetector()
    detector.run()


if __name__ == "__main__":
    main()
