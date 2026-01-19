from ultralytics import YOLO
import os

def train_model():
    # 1. Load a model
    # Load a pretrained model (recommended for training)
    model = YOLO("yolov8m.pt") 
    
    # 2. Train the model
    # We use the dataset created by setup_training.py
    # epochs=10 is for demonstration. For real results, use 50-100+
    # device='cpu' or 0 (gpu). Auto-selects usually.
    
    print("Starting training...")
    results = model.train(
        data=os.path.abspath("dataset/data.yaml"),
        epochs=10,
        imgsz=640,
        project="traffic_analysis",
        name="custom_yolov8m",
        exist_ok=True
    )
    
    print("Training complete.")
    print(f"Best model saved to: {results.save_dir}/weights/best.pt")
    
    # 3. Validation
    metrics = model.val()
    print(f"Validation mAP50-95: {metrics.box.map}")

if __name__ == "__main__":
    train_model()
