import cv2
import numpy as np
from ultralytics import YOLO

class TrafficAnalyzer:
    def __init__(self, model_path='yolov8m.pt'):
        self.model = YOLO(model_path)
        # Check if custom model (2 classes: vehicle, ambulance) or default (COCO classes)
        # Custom model: 0=vehicle, 1=ambulance
        # Default model: 2=car, 3=motorcycle, 5=bus, 7=truck
        self.is_custom_model = model_path.endswith('custom_model.pt')
        if self.is_custom_model:
            self.vehicle_classes = [0]  # Only regular vehicles for density
            self.ambulance_class = 1    # Ambulance class
        else:
            self.vehicle_classes = [2, 3, 5, 7]  # COCO vehicle classes
            self.ambulance_class = None  # No ambulance in COCO

    def get_density_percentage(self, vehicle_count):
        """
        Calculate traffic density percentage based on vehicle count.
        
        Density Scale:
        - 0-2 vehicles: 0-25% (Light)
        - 2-4 vehicles: 25-50% (Moderate)
        - 4-6 vehicles: 50-75% (Heavy)
        - 6+ vehicles: 75-100% (Very Heavy)
        
        MAX_CAPACITY is set to 8 vehicles per road segment.
        """
        MAX_CAPACITY = 8.0
        percentage = (vehicle_count / MAX_CAPACITY) * 100
        return min(percentage, 100.0)

    def calculate_signal_time(self, density_percentage):
        """
        Calculates Green Signal Time based on traffic density.
        Logic: Linear scaling from MIN_TIME to MAX_TIME.
        """
        MIN_TIME = 0  # Changed to 0 as base, but logic below sets 30-60
        # Wait, the original logic was 30-60.
        # Let's stick to the user's logic: 30s to 60s.
        
        MIN_TIME_BASE = 5 # User objective in history said 5s to 60s
        # But code said 30 to 60.
        # History: "defined minimum (5s) and maximum (60s) durations."
        # Code: MIN_TIME = 30.
        
        # I will start with what was in the code to minimize friction, 
        # but the user prompt mentioned combining. 
        # I'll stick to the file I read (ML/main.py) which had 30-60 logic.
        # But looking at conversation history "minimum (5s)".
        # I'll try to honor the code I saw which works, or maybe make it configurable.
        # Let's stick to the ml/main.py logic for now to ensure consistency with what they just ran.
        
        BASE_MIN = 5
        BASE_MAX = 60
        
        # Original code logic:
        # added_time = (density_percentage / 100) * (MAX_TIME - MIN_TIME)
        # return int(MIN_TIME + added_time)
        
        # Let's update to use 5s as min if density is very low?
        # Actually, let's just copy the logic from ML/main.py effectively, 
        # but maybe adjust constants if needed. 
        # ML/main.py lines 25-32:
        # MIN_TIME = 30
        # MAX_TIME = 60
        # This seems to be what they wrote most recently. I will use that.
        
        MIN_TIME = 5
        MAX_TIME = 60
        
        added_time = (density_percentage / 100) * (MAX_TIME - MIN_TIME)
        return int(MIN_TIME + added_time)

    def analyze_road_image(self, image_input):
        """
        Analyzes a single image representing ONE road.
        Accepts: image_path (str) OR image (numpy array)

        Returns: (vehicle_count, density_percentage, annotated_image, has_ambulance)
        """
        if isinstance(image_input, str):
            img = cv2.imread(image_input)
        else:
            img = image_input

        if img is None:
            return 0, 0.0, None, False
        
        # Run inference - detect all classes (vehicles + ambulance if custom model)
        if self.is_custom_model:
            # Custom model: detect both vehicles and ambulances
            results = self.model(img, verbose=False, conf=0.25)
        else:
            # Default model: only detect vehicles
            results = self.model(img, verbose=False, classes=self.vehicle_classes, conf=0.25)
        
        result = results[0]
        
        vehicle_count = 0
        ambulance_detected = False
        
        for box in result.boxes:
            cls_id = int(box.cls[0])
            
            # Check for ambulance (class 1 in custom model)
            if self.is_custom_model and cls_id == self.ambulance_class:
                ambulance_detected = True
                # Ambulance doesn't count toward traffic density
                continue
            
            # Count regular vehicles
            if self.is_custom_model:
                if cls_id in self.vehicle_classes:
                    vehicle_count += 1
            else:
                # Default COCO model
                if cls_id in self.vehicle_classes:
                    vehicle_count += 1
        
        # Generate annotated image
        annotated_img = result.plot()
                
        density = self.get_density_percentage(vehicle_count)
        return vehicle_count, density, annotated_img, ambulance_detected
