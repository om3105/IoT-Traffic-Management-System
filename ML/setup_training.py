import os
import shutil
from ultralytics import YOLO
import cv2

# Hardcoded paths of the new images
SOURCE_IMAGES = [
    "/Users/omchandrakantdeo/.gemini/antigravity/brain/8d6f22ed-f158-4775-aa94-b34c31bc9d46/uploaded_image_0_1768579623135.jpg",
    "/Users/omchandrakantdeo/.gemini/antigravity/brain/8d6f22ed-f158-4775-aa94-b34c31bc9d46/uploaded_image_1_1768579623135.jpg",
    "/Users/omchandrakantdeo/.gemini/antigravity/brain/8d6f22ed-f158-4775-aa94-b34c31bc9d46/uploaded_image_2_1768579623135.jpg",
    "/Users/omchandrakantdeo/.gemini/antigravity/brain/8d6f22ed-f158-4775-aa94-b34c31bc9d46/uploaded_image_3_1768579623135.jpg",
    "/Users/omchandrakantdeo/.gemini/antigravity/brain/8d6f22ed-f158-4775-aa94-b34c31bc9d46/uploaded_image_4_1768579623135.jpg"
]

BASE_DIR = os.path.abspath("dataset")
IMG_DIR_TRAIN = os.path.join(BASE_DIR, "images", "train")
IMG_DIR_VAL = os.path.join(BASE_DIR, "images", "val")
LBL_DIR_TRAIN = os.path.join(BASE_DIR, "labels", "train")
LBL_DIR_VAL = os.path.join(BASE_DIR, "labels", "val")

# COCO to Custom Class Mapping
# 2: car -> 0
# 3: motorcycle -> 1
# 5: bus -> 2
# 7: truck -> 3
CLASS_MAP = {2: 0, 3: 1, 5: 2, 7: 3}

def setup():
    # 1. Clean and Create Directories
    if os.path.exists(BASE_DIR):
        shutil.rmtree(BASE_DIR)
    
    for d in [IMG_DIR_TRAIN, IMG_DIR_VAL, LBL_DIR_TRAIN, LBL_DIR_VAL]:
        os.makedirs(d, exist_ok=True)
        
    print("Directories created.")

    # 2. Load Model for Auto-labeling
    print("Loading model for auto-labeling...")
    model = YOLO("yolov8m.pt")

    # 3. Process Images
    # We will use the first 4 for train, and the last 1 for val
    split_idx = 4
    
    for i, img_path in enumerate(SOURCE_IMAGES):
        filename = f"image_{i}.jpg"
        
        # Decide split
        if i < split_idx:
            dest_img_dir = IMG_DIR_TRAIN
            dest_lbl_dir = LBL_DIR_TRAIN
        else:
            dest_img_dir = IMG_DIR_VAL
            dest_lbl_dir = LBL_DIR_VAL
            
        # Copy Image
        dest_img_path = os.path.join(dest_img_dir, filename)
        shutil.copy(img_path, dest_img_path)
        
        # Auto-Label
        results = model(dest_img_path, verbose=False)
        result = results[0]
        
        label_path = os.path.join(dest_lbl_dir, filename.replace(".jpg", ".txt"))
        
        with open(label_path, "w") as f:
            for box in result.boxes:
                cls_id = int(box.cls[0])
                if cls_id in CLASS_MAP:
                    # YOLO format: class x_center y_center width height (normalized)
                    # box.xywhn returns [x, y, w, h] normalized
                    x, y, w, h = box.xywhn[0].tolist()
                    new_cls = CLASS_MAP[cls_id]
                    f.write(f"{new_cls} {x} {y} {w} {h}\n")
        
        print(f"Processed {filename} -> {dest_lbl_dir}")

    # 4. Create data.yaml
    yaml_content = f"""
path: {BASE_DIR}
train: images/train
val: images/val

nc: 4
names:
  0: car
  1: motorcycle
  2: bus
  3: truck
"""
    with open(os.path.join(BASE_DIR, "data.yaml"), "w") as f:
        f.write(yaml_content.strip())
        
    print("Dataset setup complete. Please inspect 'dataset/labels' to correct any errors before training.")

if __name__ == "__main__":
    setup()
