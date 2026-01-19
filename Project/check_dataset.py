#!/usr/bin/env python3
"""
Dataset verification script for ambulance detection training.
Checks dataset structure, label files, and class distribution.
"""

import os
import glob

def check_dataset():
    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
    DATASET_DIR = os.path.join(CURRENT_DIR, "training", "dataset")
    
    print("🔍 Dataset Verification for Ambulance Detection")
    print("=" * 50)
    print()
    
    # Check dataset structure
    train_img_dir = os.path.join(DATASET_DIR, "images", "train")
    val_img_dir = os.path.join(DATASET_DIR, "images", "val")
    train_lbl_dir = os.path.join(DATASET_DIR, "labels", "train")
    val_lbl_dir = os.path.join(DATASET_DIR, "labels", "val")
    
    # Count images
    train_images = [f for f in os.listdir(train_img_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))] if os.path.exists(train_img_dir) else []
    val_images = [f for f in os.listdir(val_img_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))] if os.path.exists(val_img_dir) else []
    
    print(f"📊 Dataset Summary:")
    print(f"   Training images: {len(train_images)}")
    print(f"   Validation images: {len(val_images)}")
    print()
    
    # Check labels
    train_labels = [f for f in os.listdir(train_lbl_dir) if f.endswith('.txt')] if os.path.exists(train_lbl_dir) else []
    val_labels = [f for f in os.listdir(val_lbl_dir) if f.endswith('.txt')] if os.path.exists(val_lbl_dir) else []
    
    print(f"📝 Label Files:")
    print(f"   Training labels: {len(train_labels)}")
    print(f"   Validation labels: {len(val_labels)}")
    print()
    
    # Check class distribution
    def count_classes(label_dir):
        class_counts = {0: 0, 1: 0}  # vehicle, ambulance
        if not os.path.exists(label_dir):
            return class_counts
        
        for label_file in glob.glob(os.path.join(label_dir, "*.txt")):
            try:
                with open(label_file, 'r') as f:
                    for line in f:
                        parts = line.strip().split()
                        if len(parts) >= 5:
                            cls_id = int(parts[0])
                            if cls_id in class_counts:
                                class_counts[cls_id] += 1
            except Exception as e:
                print(f"   ⚠️  Error reading {label_file}: {e}")
        
        return class_counts
    
    train_classes = count_classes(train_lbl_dir)
    val_classes = count_classes(val_lbl_dir)
    
    print(f"🚗 Class Distribution (Training):")
    print(f"   Vehicles (class 0): {train_classes[0]}")
    print(f"   Ambulances (class 1): {train_classes[1]}")
    print()
    
    print(f"🚑 Class Distribution (Validation):")
    print(f"   Vehicles (class 0): {val_classes[0]}")
    print(f"   Ambulances (class 1): {val_classes[1]}")
    print()
    
    # Check for ambulance labels
    total_ambulances = train_classes[1] + val_classes[1]
    
    if total_ambulances == 0:
        print("⚠️  WARNING: No ambulance labels found!")
        print("   You need to manually label ambulances in the dataset.")
        print("   See AMBULANCE_TRAINING_GUIDE.md for instructions.")
        print()
    else:
        print(f"✅ Found {total_ambulances} ambulance labels")
        print()
    
    # Check data.yaml
    yaml_path = os.path.join(DATASET_DIR, "data.yaml")
    if os.path.exists(yaml_path):
        print(f"✅ Dataset config found: {yaml_path}")
        with open(yaml_path, 'r') as f:
            content = f.read()
            if 'ambulance' in content.lower():
                print("   ✅ Ambulance class configured")
            else:
                print("   ⚠️  Ambulance class not found in config")
    else:
        print(f"❌ Dataset config not found: {yaml_path}")
        print("   Run setup_training.py first!")
    
    print()
    print("=" * 50)
    
    # Recommendations
    if total_ambulances == 0:
        print()
        print("📋 Next Steps:")
        print("   1. Manually label ambulances in label files")
        print("   2. Use LabelImg or similar tool")
        print("   3. See AMBULANCE_TRAINING_GUIDE.md for details")
    elif total_ambulances < 20:
        print()
        print("💡 Recommendation:")
        print(f"   You have {total_ambulances} ambulance labels.")
        print("   Consider adding more ambulance images for better accuracy.")
    else:
        print()
        print("✅ Dataset looks good! Ready for training.")
        print("   Run: python3 train.py")

if __name__ == "__main__":
    check_dataset()
