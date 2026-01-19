import os
import shutil
import glob
from ultralytics import YOLO
import cv2

# Define paths
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
# Updating source to the user's Dataset folder in the parent IoT directory
SOURCE_IMG_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..", "Dataset"))
DATASET_DIR = os.path.join(CURRENT_DIR, "training", "dataset")

IMG_DIR_TRAIN = os.path.join(DATASET_DIR, "images", "train")
IMG_DIR_VAL = os.path.join(DATASET_DIR, "images", "val")
LBL_DIR_TRAIN = os.path.join(DATASET_DIR, "labels", "train")
LBL_DIR_VAL = os.path.join(DATASET_DIR, "labels", "val")

# COCO to Custom Class Mapping
# We are training for 2 classes: vehicle and ambulance
# Class 0: Regular vehicles (car, bus, truck, motorcycle)
# Class 1: Ambulance (emergency vehicle)
# Note: COCO doesn't have ambulance class, so we'll need manual labeling or use a different approach
# For now, we'll map vehicles to class 0, and ambulances will need manual labeling
CLASS_MAP = {2: 0, 3: 0, 5: 0, 7: 0}  # car, motorcycle, bus, truck -> vehicle (class 0)
# Ambulance (class 1) will need to be manually labeled in the dataset

def setup():
    print(f"Scanning for images in {SOURCE_IMG_DIR}...")
    images = glob.glob(os.path.join(SOURCE_IMG_DIR, "*.*"))
    images = [x for x in images if x.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    if not images:
        print("No images found! Please add .jpg or .png files to Project/training/images/")
        return

    print(f"Found {len(images)} images.")

    # 1. Clean and Create Directories
    if os.path.exists(DATASET_DIR):
        shutil.rmtree(DATASET_DIR)
    
    for d in [IMG_DIR_TRAIN, IMG_DIR_VAL, LBL_DIR_TRAIN, LBL_DIR_VAL]:
        os.makedirs(d, exist_ok=True)

    # 2. Load Model for Auto-labeling
    print("Loading model for auto-labeling...")
    model = YOLO("yolov8m.pt")

    # 3. Process Images
    # Simple split: 80% train, 20% val
    split_idx = int(len(images) * 0.8)
    if split_idx == 0 and len(images) > 0: split_idx = 1 # at least 1 for train if very few

    for i, img_path in enumerate(images):
        filename = os.path.basename(img_path)
        
        if i < split_idx:
            dest_img_dir = IMG_DIR_TRAIN
            dest_lbl_dir = LBL_DIR_TRAIN
        else:
            dest_img_dir = IMG_DIR_VAL
            dest_lbl_dir = LBL_DIR_VAL
            
        # Copy Image
        dest_img_path = os.path.join(dest_img_dir, filename)
        shutil.copy(img_path, dest_img_path)
        
        # Auto-Label with low confidence to pick up toy cars
        # Using 0.15 to filter noise but catch the buses/trucks (which we map to car)
        results = model(dest_img_path, verbose=False, conf=0.15)
        result = results[0]
        
        # We need to save labels in YOLO format
        label_filename = os.path.splitext(filename)[0] + ".txt"
        label_path = os.path.join(dest_lbl_dir, label_filename)
        
        with open(label_path, "w") as f:
            for box in result.boxes:
                cls_id = int(box.cls[0])
                if cls_id in CLASS_MAP:
                    x, y, w, h = box.xywhn[0].tolist()
                    new_cls = CLASS_MAP[cls_id]
                    f.write(f"{new_cls} {x} {y} {w} {h}\n")
        
        print(f"Processed {filename}")

    # 4. Create data.yaml
    yaml_content = f"""
path: {DATASET_DIR}
train: images/train
val: images/val

nc: 2
names:
  0: vehicle
  1: ambulance
"""
    with open(os.path.join(DATASET_DIR, "data.yaml"), "w") as f:
        f.write(yaml_content.strip())
        
    print("Dataset setup complete.")

if __name__ == "__main__":
    setup()
