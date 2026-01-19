#!/usr/bin/env python3
"""
Automated ambulance labeling script.
Uses computer vision to detect toy ambulances based on:
- White color detection
- Red/blue light detection (emergency lights)
- Shape and size characteristics
"""

import cv2
import numpy as np
import os
import glob
from ultralytics import YOLO

def detect_white_vehicles(image):
    """Detect white vehicles in the image using color thresholding."""
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
    # White color range in HSV
    lower_white = np.array([0, 0, 200])
    upper_white = np.array([180, 30, 255])
    
    mask = cv2.inRange(hsv, lower_white, upper_white)
    
    # Find contours
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    white_regions = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > 500:  # Filter small noise
            x, y, w, h = cv2.boundingRect(contour)
            white_regions.append((x, y, w, h))
    
    return white_regions

def detect_emergency_lights(image, x, y, w, h):
    """Check if a region has red/blue emergency lights."""
    try:
        # Ensure coordinates are within image bounds
        x = max(0, min(x, image.shape[1] - 1))
        y = max(0, min(y, image.shape[0] - 1))
        w = min(w, image.shape[1] - x)
        h = min(h, image.shape[0] - y)
        
        if w <= 0 or h <= 0:
            return False
        
        roi = image[y:y+h, x:x+w]
        if roi.size == 0 or roi.shape[0] == 0 or roi.shape[1] == 0:
            return False
        
        hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        
        # Red color range
        lower_red1 = np.array([0, 50, 50])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([170, 50, 50])
        upper_red2 = np.array([180, 255, 255])
        
        # Blue color range
        lower_blue = np.array([100, 50, 50])
        upper_blue = np.array([130, 255, 255])
        
        mask_red1 = cv2.inRange(hsv_roi, lower_red1, upper_red1)
        mask_red2 = cv2.inRange(hsv_roi, lower_red2, upper_red2)
        mask_red = cv2.bitwise_or(mask_red1, mask_red2)
        mask_blue = cv2.inRange(hsv_roi, lower_blue, upper_blue)
        
        # Check if red or blue pixels exist (emergency lights)
        red_pixels = np.sum(mask_red > 0)
        blue_pixels = np.sum(mask_blue > 0)
        total_pixels = roi.shape[0] * roi.shape[1]
        
        if total_pixels == 0:
            return False
        
        # If significant red or blue pixels, likely has emergency lights
        return (red_pixels / total_pixels > 0.01) or (blue_pixels / total_pixels > 0.01)
    except Exception as e:
        return False

def is_ambulance_candidate(image, x, y, w, h):
    """Determine if a detected vehicle is likely an ambulance."""
    try:
        # Ensure coordinates are valid
        if w <= 0 or h <= 0:
            return False
        
        # Check 1: Has emergency lights (red/blue) - most important
        has_lights = detect_emergency_lights(image, x, y, w, h)
        
        # Check 2: Aspect ratio (ambulances are typically rectangular)
        aspect_ratio = w / h if h > 0 else 0
        reasonable_aspect = 1.0 < aspect_ratio < 4.0
        
        # Check 3: Size (not too small)
        area = w * h
        reasonable_size = area > 500
        
        # Primary indicator: has emergency lights
        # Secondary: reasonable shape and size
        return has_lights and reasonable_aspect and reasonable_size
    except Exception as e:
        return False

def convert_to_yolo_format(x, y, w, h, img_width, img_height):
    """Convert bounding box to YOLO format (normalized center coordinates)."""
    x_center = (x + w / 2) / img_width
    y_center = (y + h / 2) / img_height
    width = w / img_width
    height = h / img_height
    
    return x_center, y_center, width, height

def auto_label_ambulances():
    """Automatically label ambulances in the dataset."""
    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
    
    # Paths
    train_img_dir = os.path.join(CURRENT_DIR, "training", "dataset", "images", "train")
    train_lbl_dir = os.path.join(CURRENT_DIR, "training", "dataset", "labels", "train")
    val_img_dir = os.path.join(CURRENT_DIR, "training", "dataset", "images", "val")
    val_lbl_dir = os.path.join(CURRENT_DIR, "training", "dataset", "labels", "val")
    
    print("🚑 Automated Ambulance Labeling")
    print("=" * 50)
    print()
    
    # Load YOLO model to detect vehicles first
    print("Loading YOLO model for vehicle detection...")
    model = YOLO("yolov8m.pt")
    
    total_ambulances = 0
    
    # Process training images
    print("\n📁 Processing training images...")
    train_images = glob.glob(os.path.join(train_img_dir, "*.*"))
    train_images = [f for f in train_images if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    
    for img_path in train_images:
        filename = os.path.basename(img_path)
        label_path = os.path.join(train_lbl_dir, os.path.splitext(filename)[0] + ".txt")
        
        # Read image
        img = cv2.imread(img_path)
        if img is None:
            continue
        
        img_height, img_width = img.shape[:2]
        
        # Read existing labels
        existing_labels = []
        if os.path.exists(label_path):
            with open(label_path, 'r') as f:
                existing_labels = f.readlines()
        
        # Detect vehicles using YOLO
        results = model(img, verbose=False, conf=0.25)
        result = results[0]
        
        # Find potential ambulances
        ambulance_labels = []
        vehicle_labels = []
        
        for box in result.boxes:
            try:
                cls_id = int(box.cls[0])
                # Only check vehicle classes (car, bus, truck)
                if cls_id in [2, 5, 7]:  # car, bus, truck
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    x, y, w, h = int(x1), int(y1), int(x2 - x1), int(y2 - y1)
                    
                    # Ensure valid coordinates
                    if w > 0 and h > 0 and x >= 0 and y >= 0:
                        # Check if this vehicle is likely an ambulance
                        if is_ambulance_candidate(img, x, y, w, h):
                            # Convert to YOLO format
                            x_center, y_center, width, height = convert_to_yolo_format(
                                x, y, w, h, img_width, img_height
                            )
                            # Ensure normalized values are valid
                            if 0 <= x_center <= 1 and 0 <= y_center <= 1 and 0 < width <= 1 and 0 < height <= 1:
                                ambulance_labels.append(f"1 {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n")
                                total_ambulances += 1
                                print(f"  ✅ Found ambulance in {filename}")
                        else:
                            # Regular vehicle
                            x_center, y_center, width, height = convert_to_yolo_format(
                                x, y, w, h, img_width, img_height
                            )
                            if 0 <= x_center <= 1 and 0 <= y_center <= 1 and 0 < width <= 1 and 0 < height <= 1:
                                vehicle_labels.append(f"0 {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n")
            except Exception as e:
                continue
        
        # Write labels (ambulances + vehicles)
        all_labels = ambulance_labels + vehicle_labels
        
        # Also keep existing labels that might be manually added
        for line in existing_labels:
            parts = line.strip().split()
            if len(parts) >= 5:
                cls_id = int(parts[0])
                if cls_id == 1:  # Keep existing ambulance labels
                    if line not in ambulance_labels:
                        all_labels.append(line)
                elif cls_id == 0:  # Keep existing vehicle labels if not already detected
                    if line not in vehicle_labels:
                        all_labels.append(line)
        
        # Write updated labels
        with open(label_path, 'w') as f:
            f.writelines(all_labels)
    
    # Process validation images
    print("\n📁 Processing validation images...")
    val_images = glob.glob(os.path.join(val_img_dir, "*.*"))
    val_images = [f for f in val_images if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    
    for img_path in val_images:
        filename = os.path.basename(img_path)
        label_path = os.path.join(val_lbl_dir, os.path.splitext(filename)[0] + ".txt")
        
        # Read image
        img = cv2.imread(img_path)
        if img is None:
            continue
        
        img_height, img_width = img.shape[:2]
        
        # Read existing labels
        existing_labels = []
        if os.path.exists(label_path):
            with open(label_path, 'r') as f:
                existing_labels = f.readlines()
        
        # Detect vehicles using YOLO
        results = model(img, verbose=False, conf=0.25)
        result = results[0]
        
        # Find potential ambulances
        ambulance_labels = []
        vehicle_labels = []
        
        for box in result.boxes:
            try:
                cls_id = int(box.cls[0])
                if cls_id in [2, 5, 7]:  # car, bus, truck
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    x, y, w, h = int(x1), int(y1), int(x2 - x1), int(y2 - y1)
                    
                    if w > 0 and h > 0 and x >= 0 and y >= 0:
                        if is_ambulance_candidate(img, x, y, w, h):
                            x_center, y_center, width, height = convert_to_yolo_format(
                                x, y, w, h, img_width, img_height
                            )
                            if 0 <= x_center <= 1 and 0 <= y_center <= 1 and 0 < width <= 1 and 0 < height <= 1:
                                ambulance_labels.append(f"1 {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n")
                                total_ambulances += 1
                                print(f"  ✅ Found ambulance in {filename}")
                        else:
                            x_center, y_center, width, height = convert_to_yolo_format(
                                x, y, w, h, img_width, img_height
                            )
                            if 0 <= x_center <= 1 and 0 <= y_center <= 1 and 0 < width <= 1 and 0 < height <= 1:
                                vehicle_labels.append(f"0 {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n")
            except Exception as e:
                continue
        
        # Write labels
        all_labels = ambulance_labels + vehicle_labels
        
        # Keep existing labels
        for line in existing_labels:
            parts = line.strip().split()
            if len(parts) >= 5:
                cls_id = int(parts[0])
                if cls_id == 1:
                    if line not in ambulance_labels:
                        all_labels.append(line)
                elif cls_id == 0:
                    if line not in vehicle_labels:
                        all_labels.append(line)
        
        with open(label_path, 'w') as f:
            f.writelines(all_labels)
    
    print()
    print("=" * 50)
    print(f"✅ Labeling complete!")
    print(f"   Total ambulances labeled: {total_ambulances}")
    print()
    print("📋 Next steps:")
    print("   1. Review labels: python3 check_dataset.py")
    print("   2. Train model: python3 train.py")

if __name__ == "__main__":
    auto_label_ambulances()
