"""
Smart Traffic Management System - Automatic ML Pipeline
Monitors "captures/" folder and detects traffic density in real-time.
Uses OpenCV-based image processing for vehicle detection.
"""

import os
import cv2
import numpy as np
from datetime import datetime
from pathlib import Path
import time

# Configuration
CAPTURES_FOLDER = "captures"
PROCESSED_FILES = set()
MIN_CONTOUR_AREA = 200  # Minimum area to consider as a vehicle
MAX_CONTOUR_AREA = 50000  # Maximum area to filter noise
POLLING_INTERVAL = 2  # seconds between folder checks


class TrafficDensityDetector:
    """Detects vehicles and classifies traffic density from images."""
    
    def __init__(self):
        self.processed_files = set()
        self.create_captures_folder()
    
    def create_captures_folder(self):
        """Ensure captures folder exists."""
        Path(CAPTURES_FOLDER).mkdir(exist_ok=True)
        print(f"[INIT] Monitoring folder: {os.path.abspath(CAPTURES_FOLDER)}")
    
    def detect_vehicles(self, image_path):
        """
        Detect vehicles in an image using edge detection and contour analysis.
        Returns: vehicle_count (int)
        """
        try:
            # Read image
            image = cv2.imread(image_path)
            if image is None:
                print(f"[ERROR] Failed to read image: {image_path}")
                return 0
            
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply Gaussian blur to reduce noise
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # Edge detection using Canny
            edges = cv2.Canny(blurred, 50, 150)
            
            # Dilate edges to connect nearby contours
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
            dilated = cv2.dilate(edges, kernel, iterations=2)
            
            # Find contours
            contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            
            # Filter contours by area (potential vehicles)
            vehicle_contours = []
            for contour in contours:
                area = cv2.contourArea(contour)
                if MIN_CONTOUR_AREA < area < MAX_CONTOUR_AREA:
                    # Additional filter: aspect ratio (vehicles are not too square)
                    x, y, w, h = cv2.boundingRect(contour)
                    if w > 0 and h > 0:
                        aspect_ratio = float(w) / h
                        # Accept contours with reasonable aspect ratios
                        if 0.3 < aspect_ratio < 3.0:
                            vehicle_contours.append(contour)
            
            vehicle_count = len(vehicle_contours)
            return vehicle_count
        
        except Exception as e:
            print(f"[ERROR] Exception in vehicle detection: {e}")
            return 0
    
    def classify_density(self, vehicle_count):
        """
        Classify traffic density based on vehicle count.
        Returns: density_category (str)
        """
        if vehicle_count < 5:
            return "LOW"
        elif vehicle_count < 15:
            return "MEDIUM"
        else:
            return "HIGH"
    
    def process_image(self, image_path):
        """
        Process a single image: detect vehicles and classify density.
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        filename = os.path.basename(image_path)
        
        print(f"\n[{timestamp}] Processing: {filename}")
        
        # Detect vehicles
        vehicle_count = self.detect_vehicles(image_path)
        
        # Classify density
        density = self.classify_density(vehicle_count)
        
        # Output results
        print(f"  ├─ Vehicles Detected: {vehicle_count}")
        print(f"  └─ Traffic Density: {density}")
        
        return {
            "filename": filename,
            "vehicle_count": vehicle_count,
            "density": density,
            "timestamp": timestamp
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
        print("\n" + "="*60)
        print("SMART TRAFFIC MANAGEMENT SYSTEM - ML PIPELINE")
        print("="*60)
        print("[START] Monitoring for new images...")
        print(f"[INFO] Check interval: {POLLING_INTERVAL} seconds")
        print("="*60 + "\n")
        
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
            print("="*60 + "\n")


def main():
    """Entry point for the traffic density detection pipeline."""
    detector = TrafficDensityDetector()
    detector.run()


if __name__ == "__main__":
    main()
