#!/usr/bin/env python3
"""Clean duplicate labels from label files."""

import os
import glob

def clean_label_file(label_path):
    """Remove duplicate labels from a file."""
    if not os.path.exists(label_path):
        return
    
    with open(label_path, 'r') as f:
        lines = f.readlines()
    
    # Keep unique labels (based on class and approximate position)
    seen = set()
    cleaned = []
    
    for line in lines:
        parts = line.strip().split()
        if len(parts) >= 5:
            cls_id = parts[0]
            x = float(parts[1])
            y = float(parts[2])
            # Round to 3 decimals for comparison
            key = (cls_id, round(x, 3), round(y, 3))
            if key not in seen:
                seen.add(key)
                cleaned.append(line)
    
    # Write cleaned labels
    with open(label_path, 'w') as f:
        f.writelines(cleaned)

def clean_all_labels():
    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
    train_lbl_dir = os.path.join(CURRENT_DIR, "training", "dataset", "labels", "train")
    val_lbl_dir = os.path.join(CURRENT_DIR, "training", "dataset", "labels", "val")
    
    print("🧹 Cleaning label files...")
    
    for label_file in glob.glob(os.path.join(train_lbl_dir, "*.txt")):
        clean_label_file(label_file)
        print(f"  Cleaned: {os.path.basename(label_file)}")
    
    for label_file in glob.glob(os.path.join(val_lbl_dir, "*.txt")):
        clean_label_file(label_file)
        print(f"  Cleaned: {os.path.basename(label_file)}")
    
    print("✅ Done!")

if __name__ == "__main__":
    clean_all_labels()
