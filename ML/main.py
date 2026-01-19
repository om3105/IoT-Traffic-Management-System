import cv2
import json
import sys
import numpy as np
from ultralytics import YOLO

class TrafficAnalyzer:
    def __init__(self, model_path='yolov8m.pt'):
        self.model = YOLO(model_path)
        # COCO classes: 2=car, 3=motorcycle, 5=bus, 7=truck
        self.vehicle_classes = [2, 3, 5, 7] 

    def get_density_percentage(self, count):
        # Heuristic: Assuming the visible road segment is "full" with 4 vehicles
        # (based on the toy car size vs road length in images)
        MAX_CAPACITY = 4
        percentage = (count / MAX_CAPACITY) * 100
        return min(percentage, 100.0) # Cap at 100%

    def calculate_signal_time(self, density_percentage):
        """
        Calculates Green Signal Time based on traffic density.
        Logic: Linear scaling from MIN_TIME to MAX_TIME.
        """
        MIN_TIME = 30
        MAX_TIME = 60
        
        # Formula: Scale linearly between 30s and 60s based on density
        # 0% density -> 30s
        # 100% density -> 60s
        added_time = (density_percentage / 100) * (MAX_TIME - MIN_TIME)
        return int(MIN_TIME + added_time)

    def analyze_road_image(self, image_path):

        """
        Analyzes a single image representing ONE road.
        Returns count and density percentage.
        """
        img = cv2.imread(image_path)
        if img is None:
            return 0, 0.0
        
        # Run inference on the whole image
        results = self.model(img, verbose=False)
        result = results[0]
        
        vehicle_count = 0
        
        for box in result.boxes:
            cls_id = int(box.cls[0])
            if cls_id in self.vehicle_classes:
                vehicle_count += 1
                
        density = self.get_density_percentage(vehicle_count)
        return vehicle_count, density

def main():
    # Mapping specific images to directions as requested
    # Image 0 -> North
    # Image 1 -> East
    # Image 2 -> South
    # Image 3 -> West
    road_images = {
        "North": "/Users/omchandrakantdeo/.gemini/antigravity/brain/8d6f22ed-f158-4775-aa94-b34c31bc9d46/uploaded_image_0_1768580120607.jpg",
        "East": "/Users/omchandrakantdeo/.gemini/antigravity/brain/8d6f22ed-f158-4775-aa94-b34c31bc9d46/uploaded_image_1_1768580120607.jpg",
        "South": "/Users/omchandrakantdeo/.gemini/antigravity/brain/8d6f22ed-f158-4775-aa94-b34c31bc9d46/uploaded_image_2_1768580120607.jpg",
        "West": "/Users/omchandrakantdeo/.gemini/antigravity/brain/8d6f22ed-f158-4775-aa94-b34c31bc9d46/uploaded_image_3_1768580120607.jpg"
    }

    analyzer = TrafficAnalyzer()
    
    final_counts = {}
    final_densities = {}
    final_signal_times = {}
    
    print("Processing traffic feeds...")
    for direction, img_path in road_images.items():
        count, density = analyzer.analyze_road_image(img_path)
        signal_time = analyzer.calculate_signal_time(density)
        
        final_counts[direction] = count
        final_densities[direction] = f"{density:.1f}%"
        final_signal_times[direction] = f"{signal_time}s"
        
        print(f"{direction} Road ({img_path.split('/')[-1]}): {count} vehicles -> {density:.1f}% -> Green Light: {signal_time}s")

    result = {
        "vehicle_counts": final_counts,
        "traffic_density": final_densities,
        "signal_times": final_signal_times
    }
    
    print("\nFinal Output:")
    print(json.dumps(result, indent=4))

if __name__ == "__main__":
    main()
