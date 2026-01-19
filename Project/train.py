from ultralytics import YOLO
import os
import shutil

def train_model():
    """
    Train YOLOv8 model on custom traffic dataset.
    Uses proper hyperparameters for small dataset fine-tuning.
    """
    # Define paths
    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
    DATASET_YAML = os.path.join(CURRENT_DIR, "training", "dataset", "data.yaml")
    
    if not os.path.exists(DATASET_YAML):
        print("❌ Dataset not found! Please run setup_training.py first.")
        return

    # Verify dataset structure
    train_dir = os.path.join(CURRENT_DIR, "training", "dataset", "images", "train")
    val_dir = os.path.join(CURRENT_DIR, "training", "dataset", "images", "val")
    
    if not os.path.exists(train_dir) or not os.path.exists(val_dir):
        print("❌ Dataset directories not found! Please run setup_training.py first.")
        return
    
    train_count = len([f for f in os.listdir(train_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
    val_count = len([f for f in os.listdir(val_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
    
    print(f"📊 Dataset Summary:")
    print(f"   Training images: {train_count}")
    print(f"   Validation images: {val_count}")
    
    if train_count == 0:
        print("❌ No training images found!")
        return

    # Load model
    print("\n🔄 Loading base model (yolov8m.pt)...")
    model = YOLO("yolov8m.pt")
    
    print("\n🚀 Starting training with optimized hyperparameters...")
    print("   Epochs: 100")
    print("   Image size: 640")
    print("   Batch size: 8 (auto-adjusted if needed)")
    print("   Learning rate: 0.01 (initial)")
    
    # Train with optimized hyperparameters for small dataset
    # Using conservative settings for small dataset to prevent overfitting
    results = model.train(
        data=DATASET_YAML,
        epochs=100,              # More epochs for better convergence
        imgsz=640,               # Standard YOLO input size
        batch=8,                 # Batch size (auto-adjusted if GPU memory is limited)
        lr0=0.01,               # Initial learning rate
        lrf=0.1,                # Final learning rate (lr0 * lrf)
        momentum=0.937,         # SGD momentum
        weight_decay=0.0005,    # Weight decay
        warmup_epochs=3,        # Warmup epochs
        warmup_momentum=0.8,    # Warmup momentum
        warmup_bias_lr=0.1,     # Warmup bias learning rate
        box=7.5,                # Box loss gain
        cls=0.5,                # Class loss gain
        dfl=1.5,                # DFL loss gain
        hsv_h=0.015,            # HSV-Hue augmentation
        hsv_s=0.7,              # HSV-Saturation augmentation
        hsv_v=0.4,              # HSV-Value augmentation
        degrees=0.0,            # Rotation augmentation
        translate=0.1,          # Translation augmentation
        scale=0.5,              # Scale augmentation
        fliplr=0.5,             # Horizontal flip augmentation
        mosaic=1.0,             # Mosaic augmentation probability
        close_mosaic=10,        # Disable mosaic augmentation for last N epochs
        project=os.path.join(CURRENT_DIR, "training", "runs"),
        name="custom_traffic_model",
        exist_ok=True,
        pretrained=True,        # Use pretrained weights
        optimizer='auto',       # Auto-select optimizer (SGD/Adam)
        verbose=True,           # Verbose output
        seed=42,                # Random seed for reproducibility
        deterministic=True,    # Deterministic mode
        amp=True,              # Automatic Mixed Precision (AMP) training
        device=None,           # Auto-detect device (cuda/cpu)
    )
    
    print("\n✅ Training complete!")
    
    # Display results summary
    if hasattr(results, 'results_dict'):
        print("\n📈 Training Results:")
        print(f"   mAP50: {results.results_dict.get('metrics/mAP50(B)', 'N/A')}")
        print(f"   mAP50-95: {results.results_dict.get('metrics/mAP50-95(B)', 'N/A')}")
    
    # Copy best model to Project root
    best_weight_path = os.path.join(CURRENT_DIR, "training", "runs", "custom_traffic_model", "weights", "best.pt")
    target_path = os.path.join(CURRENT_DIR, "custom_model.pt")
    
    if os.path.exists(best_weight_path):
        shutil.copy(best_weight_path, target_path)
        print(f"\n💾 Best model saved to: {target_path}")
        print(f"   Model size: {os.path.getsize(target_path) / (1024*1024):.2f} MB")
    else:
        print("\n⚠️  Could not find best weights file.")
        print(f"   Expected path: {best_weight_path}")
        
        # Try to find last.pt as fallback
        last_weight_path = os.path.join(CURRENT_DIR, "training", "runs", "custom_traffic_model", "weights", "last.pt")
        if os.path.exists(last_weight_path):
            shutil.copy(last_weight_path, target_path)
            print(f"   Using last checkpoint instead: {target_path}")

if __name__ == "__main__":
    train_model()
