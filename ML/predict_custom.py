import cv2
import json
import sys
import os
from ultralytics import YOLO

class CustomTrafficAnalyzer:
    def __init__(self, model_path):
        print(f"Loading custom model from: {model_path}")
        self.model = YOLO(model_path)
        # Our custom model maps: 0:car, 1:motorcycle, 2:bus, 3:truck
        self.vehicle_classes = [0, 1, 2, 3] 
        self.class_names = {0: 'car', 1: 'motorcycle', 2: 'bus', 3: 'truck'}
        
    def detect_vehicles(self, image_path):
        img = cv2.imread(image_path)
        if img is None:
            return None
        
        height, width, _ = img.shape
        col_width = width // 4
        
        counts = {
            "North": 0,
            "East": 0,
            "South": 0,
            "West": 0
        }
        
        results = self.model(img, verbose=False)
        result = results[0]
        
        for box in result.boxes:
            cls_id = int(box.cls[0])
            if cls_id in self.vehicle_classes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                cx = (x1 + x2) / 2
                
                # Lane Logic
                if 0 <= cx < col_width:
                    counts["North"] += 1
                elif col_width <= cx < 2 * col_width:
                    counts["East"] += 1
                elif 2 * col_width <= cx < 3 * col_width:
                    counts["South"] += 1
                elif 3 * col_width <= cx <= width:
                    counts["West"] += 1
                    
        return counts

def main():
    # Path to the best model after training
    model_path = "traffic_analysis/custom_yolov8m/weights/best.pt"
    
    if not os.path.exists(model_path):
        print(f"Error: Model not found at {model_path}")
        print("Please run 'python train.py' first.")
        sys.exit(1)

    image_paths = []
    if len(sys.argv) > 1:
        image_paths = sys.argv[1:]
    else:
        # Default to the uploaded images for demo
        image_paths = [
            "/Users/omchandrakantdeo/.gemini/antigravity/brain/8d6f22ed-f158-4775-aa94-b34c31bc9d46/uploaded_image_0_1768579623135.jpg",
            "/Users/omchandrakantdeo/.gemini/antigravity/brain/8d6f22ed-f158-4775-aa94-b34c31bc9d46/uploaded_image_1_1768579623135.jpg",
            "/Users/omchandrakantdeo/.gemini/antigravity/brain/8d6f22ed-f158-4775-aa94-b34c31bc9d46/uploaded_image_2_1768579623135.jpg",
            "/Users/omchandrakantdeo/.gemini/antigravity/brain/8d6f22ed-f158-4775-aa94-b34c31bc9d46/uploaded_image_3_1768579623135.jpg",
            "/Users/omchandrakantdeo/.gemini/antigravity/brain/8d6f22ed-f158-4775-aa94-b34c31bc9d46/uploaded_image_4_1768579623135.jpg"
        ]
        
    analyzer = CustomTrafficAnalyzer(model_path)
    
    for img_path in image_paths:
        counts = analyzer.detect_vehicles(img_path)
        if counts:
            print(f"Custom Model Results for {img_path}:")
            print(json.dumps(counts, indent=4))
        else:
            print(f"Failed to load {img_path}")

if __name__ == "__main__":
    main()
