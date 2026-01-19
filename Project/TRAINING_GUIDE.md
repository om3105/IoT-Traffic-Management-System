# YOLOv8 Training Guide - Traffic Detection Model

## 📋 Overview

This guide explains how to train a custom YOLOv8 model for traffic vehicle detection using your dataset.

---

## 🗂️ Dataset Structure

Your dataset should be organized as follows:

```
Dataset/                          # Source images folder (parent directory)
├── image1.jpg
├── image2.jpg
└── ...

Project/training/dataset/         # Processed dataset (auto-generated)
├── data.yaml                    # Dataset configuration
├── images/
│   ├── train/                   # Training images (80%)
│   └── val/                     # Validation images (20%)
└── labels/
    ├── train/                   # Training labels (YOLO format)
    └── val/                     # Validation labels (YOLO format)
```

---

## 🚀 Training Steps

### Step 1: Prepare Dataset

1. **Place your images** in the `Dataset/` folder (parent directory of Project)
   - Supported formats: `.jpg`, `.jpeg`, `.png`
   - Images should contain vehicles/traffic scenes

2. **Run dataset setup** (auto-labels images using pre-trained model):
   ```bash
   cd Project
   python3 setup_training.py
   ```

   This will:
   - Copy images to training/validation folders (80/20 split)
   - Auto-label using YOLOv8m pre-trained model
   - Create YOLO-format label files
   - Generate `data.yaml` configuration

3. **Review labels** (optional but recommended):
   - Check `training/dataset/labels/train/` and `val/`
   - Manually correct any incorrect labels if needed
   - Label format: `class_id x_center y_center width height` (normalized 0-1)

### Step 2: Train the Model

**Option A: Using the training script**
```bash
cd Project
python3 train.py
```

**Option B: Using the shell script**
```bash
cd Project
./run_training.sh
```

**Training Parameters:**
- **Epochs:** 100 (full training cycle)
- **Image Size:** 640x640 pixels
- **Batch Size:** 8 (auto-adjusted based on GPU memory)
- **Learning Rate:** 0.01 (initial), decays to 0.001
- **Base Model:** YOLOv8m (medium)
- **Output:** `custom_model.pt` in Project root

### Step 3: Monitor Training

Training progress is displayed in real-time:
- Loss curves (box, class, DFL)
- mAP metrics (mAP50, mAP50-95)
- Validation results

**Output Location:**
```
training/runs/custom_traffic_model/
├── weights/
│   ├── best.pt      # Best model (highest mAP)
│   └── last.pt      # Last checkpoint
├── results.png      # Training curves
├── confusion_matrix.png
└── ...
```

### Step 4: Use Trained Model

The best model is automatically copied to:
```
Project/custom_model.pt
```

The dashboard (`dashboard.py`) will automatically use this model if it exists, otherwise falls back to `yolov8m.pt`.

---

## ⚙️ Training Configuration

### Current Settings (Optimized for Small Dataset)

```python
epochs=100           # Training iterations
imgsz=640            # Input image size
batch=8              # Batch size
lr0=0.01            # Initial learning rate
lrf=0.1             # Final learning rate factor
momentum=0.937      # SGD momentum
weight_decay=0.0005 # L2 regularization
warmup_epochs=3     # Learning rate warmup
```

### Augmentation Settings

- **Mosaic:** Enabled (1.0) - Combines 4 images
- **Horizontal Flip:** 50% probability
- **HSV Augmentation:** Color variations
- **Translation/Scale:** Geometric augmentations
- **Mosaic Disabled:** Last 10 epochs (for better convergence)

---

## 📊 Expected Results

### Metrics to Monitor

1. **mAP50 (mean Average Precision at IoU=0.5)**
   - Target: > 0.7 (70%) for good performance
   - Excellent: > 0.85 (85%)

2. **mAP50-95 (mean Average Precision at IoU=0.5:0.95)**
   - Target: > 0.5 (50%)
   - Excellent: > 0.65 (65%)

3. **Loss Values**
   - Box Loss: Should decrease steadily
   - Class Loss: Should decrease steadily
   - DFL Loss: Should decrease steadily

### Training Time Estimates

- **CPU:** ~2-4 hours for 100 epochs (small dataset)
- **GPU (CUDA):** ~15-30 minutes for 100 epochs
- **GPU (M1/M2 Mac):** ~30-60 minutes for 100 epochs

---

## 🔧 Troubleshooting

### Issue: "Dataset not found"
**Solution:** Run `setup_training.py` first to prepare the dataset.

### Issue: "Out of memory" error
**Solution:** Reduce batch size in `train.py`:
```python
batch=4  # or batch=2 for very limited memory
```

### Issue: Poor validation results
**Solutions:**
1. Add more training images
2. Check label quality (manually review labels)
3. Increase epochs (150-200)
4. Adjust learning rate (try 0.005 or 0.02)

### Issue: Overfitting (high train mAP, low val mAP)
**Solutions:**
1. Add more validation images
2. Increase augmentation
3. Reduce epochs
4. Add dropout (if supported)

### Issue: Model not improving
**Solutions:**
1. Check if labels are correct
2. Verify dataset split (enough validation images)
3. Try different learning rate
4. Use data augmentation more aggressively

---

## 📈 Improving Model Performance

### 1. **Increase Dataset Size**
   - More images = better generalization
   - Aim for 100+ training images minimum
   - Diverse lighting, angles, backgrounds

### 2. **Improve Label Quality**
   - Manually review auto-generated labels
   - Ensure accurate bounding boxes
   - Remove false positives

### 3. **Data Augmentation**
   - Current: Mosaic, flip, HSV, translation, scale
   - Can add: Rotation, shear, perspective (if needed)

### 4. **Hyperparameter Tuning**
   - Learning rate: Try 0.005, 0.01, 0.02
   - Batch size: Adjust based on GPU memory
   - Epochs: Increase for larger datasets

### 5. **Model Architecture**
   - Current: YOLOv8m (medium)
   - Can try: YOLOv8s (smaller, faster) or YOLOv8l (larger, more accurate)

---

## 🎯 Best Practices

1. **Dataset Split:**
   - 80% training, 20% validation (current)
   - Ensure validation set is representative

2. **Label Review:**
   - Always review auto-generated labels
   - Correct mislabeled objects
   - Remove incorrect detections

3. **Training Monitoring:**
   - Watch for overfitting (val loss > train loss)
   - Stop early if validation metrics plateau
   - Save best model (automatic)

4. **Model Evaluation:**
   - Test on unseen images
   - Check false positives/negatives
   - Adjust confidence threshold if needed

---

## 📝 Notes

- **Model Format:** PyTorch (.pt)
- **Classes:** 1 class (vehicle)
- **Input:** RGB images, 640x640
- **Output:** Bounding boxes with confidence scores

---

## 🔗 References

- [YOLOv8 Documentation](https://docs.ultralytics.com/)
- [YOLOv8 Training Guide](https://docs.ultralytics.com/modes/train/)
- [Dataset Format](https://docs.ultralytics.com/datasets/)

---

**Ready to train?** Run:
```bash
cd Project
python3 train.py
```

Good luck! 🚀
