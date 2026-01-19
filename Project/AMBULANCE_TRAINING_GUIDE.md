# Ambulance Detection Training Guide

## 🚨 Overview

This guide explains how to train the YOLOv8 model to detect **ambulances** as a separate class from regular vehicles. This enables automatic emergency vehicle detection in the traffic management system.

---

## 📋 Dataset Requirements

### **Classes:**
1. **Class 0: Vehicle** - Regular vehicles (cars, buses, trucks, motorcycles)
2. **Class 1: Ambulance** - Emergency vehicles (ambulances)

### **Dataset Structure:**

```
Dataset/                          # Source images folder
├── regular_traffic_1.jpg        # Regular vehicles
├── regular_traffic_2.jpg
├── ambulance_1.jpg              # Images with ambulances
├── ambulance_2.jpg
└── ...
```

---

## 🎯 Training Steps

### **Step 1: Prepare Your Dataset**

1. **Collect Images:**
   - Regular traffic scenes (cars, buses, trucks)
   - Ambulance images (real ambulances in traffic scenes)
   - Mix of different angles, lighting, backgrounds

2. **Place Images:**
   - Put all images in the `Dataset/` folder (parent directory)
   - Supported formats: `.jpg`, `.jpeg`, `.png`

### **Step 2: Setup Dataset (Auto-labeling)**

Run the setup script to auto-label regular vehicles:

```bash
cd Project
python3 setup_training.py
```

**What this does:**
- Auto-labels regular vehicles (class 0) using pre-trained YOLOv8
- Creates train/val split (80/20)
- Generates YOLO-format label files

### **Step 3: Manual Ambulance Labeling** ⚠️ **IMPORTANT**

Since COCO dataset doesn't have ambulance class, you **MUST manually label ambulances**:

1. **Open label files** in `training/dataset/labels/train/` and `val/`

2. **For images with ambulances**, add ambulance labels:
   - Format: `1 x_center y_center width height` (all normalized 0-1)
   - Class ID `1` = Ambulance
   - Class ID `0` = Vehicle

3. **Example label file** (`image_with_ambulance.txt`):
   ```
   0 0.5 0.3 0.2 0.15    # Vehicle at center
   1 0.7 0.6 0.15 0.2    # Ambulance on right
   0 0.2 0.8 0.1 0.12    # Another vehicle
   ```

4. **Labeling Tools:**
   - **LabelImg**: https://github.com/tzutalin/labelImg
   - **Roboflow**: https://roboflow.com/
   - **CVAT**: https://cvat.org/

### **Step 4: Train the Model**

```bash
cd Project
python3 train.py
```

**Training Parameters:**
- **Epochs:** 100
- **Classes:** 2 (vehicle, ambulance)
- **Output:** `custom_model.pt`

### **Step 5: Verify Ambulance Detection**

The trained model will:
- Detect regular vehicles (class 0)
- Detect ambulances (class 1)
- Automatically trigger emergency mode when ambulance is detected

---

## 🔧 Manual Labeling Instructions

### **Using LabelImg (Recommended)**

1. **Install LabelImg:**
   ```bash
   pip install labelImg
   labelImg
   ```

2. **Configure:**
   - Format: YOLO
   - Classes: `vehicle`, `ambulance`
   - Open image directory: `Project/training/dataset/images/train/`
   - Save labels to: `Project/training/dataset/labels/train/`

3. **Labeling:**
   - Draw bounding boxes around vehicles → Class: `vehicle` (0)
   - Draw bounding boxes around ambulances → Class: `ambulance` (1)
   - Save labels (creates `.txt` files)

### **Label Format (YOLO):**

```
class_id x_center y_center width height
```

All values normalized (0-1):
- `x_center`: X coordinate of box center / image width
- `y_center`: Y coordinate of box center / image height
- `width`: Box width / image width
- `height`: Box height / image height

**Example:**
```
0 0.5 0.5 0.2 0.3    # Vehicle at center, 20% width, 30% height
1 0.8 0.6 0.15 0.25 # Ambulance on right, 15% width, 25% height
```

---

## 📊 Dataset Recommendations

### **Minimum Requirements:**
- **Training:** 50+ images with vehicles, 20+ images with ambulances
- **Validation:** 10+ images with vehicles, 5+ images with ambulances

### **Optimal Dataset:**
- **Training:** 200+ images with vehicles, 50+ images with ambulances
- **Validation:** 50+ images with vehicles, 15+ images with ambulances

### **Image Quality:**
- Clear, well-lit images
- Various angles (front, side, back)
- Different backgrounds
- Mix of close-up and wide shots
- Real-world traffic scenarios

---

## 🎯 Training Tips

### **1. Balanced Dataset**
- Ensure both classes have similar number of examples
- If ambulances are rare, use data augmentation

### **2. Data Augmentation**
- Already enabled in training script:
  - Horizontal flip
  - Mosaic (combines 4 images)
  - Color variations (HSV)
  - Translation and scaling

### **3. Class Imbalance**
If you have many vehicles but few ambulances:
- Use class weights (modify train.py)
- Oversample ambulance images
- Use focal loss

### **4. Validation**
- Monitor validation mAP for both classes
- Check confusion matrix
- Ensure ambulance detection doesn't degrade vehicle detection

---

## 🚀 Quick Start Checklist

- [ ] Collect images with vehicles and ambulances
- [ ] Place images in `Dataset/` folder
- [ ] Run `python3 setup_training.py` (auto-labels vehicles)
- [ ] **Manually label ambulances** in label files
- [ ] Verify label files are correct
- [ ] Run `python3 train.py`
- [ ] Check training results
- [ ] Test model in dashboard

---

## 🔍 Verification

After training, verify the model:

1. **Check Training Metrics:**
   - mAP50 for class 0 (vehicle) > 0.7
   - mAP50 for class 1 (ambulance) > 0.6
   - Overall mAP50 > 0.7

2. **Test in Dashboard:**
   - Upload image with ambulance
   - Should detect ambulance
   - Should trigger emergency mode
   - Emergency indicator should show "DETECTED"

3. **Check Annotated Images:**
   - View `training/runs/custom_traffic_model/val_batch0_pred.jpg`
   - Verify ambulances are correctly labeled

---

## ⚠️ Important Notes

1. **COCO Limitation:**
   - COCO dataset doesn't include ambulance class
   - You MUST manually label ambulances
   - Auto-labeling only works for regular vehicles

2. **Model Compatibility:**
   - Custom model (2 classes) replaces `custom_model.pt`
   - Dashboard automatically uses custom model if available
   - Falls back to default model if custom model not found

3. **Emergency Detection:**
   - Ambulance detection triggers `Emg = 1` in dashboard
   - Emergency mode: Forces North lane, 99s timer
   - Visual indicator shows "DETECTED" in red

---

## 🛠️ Troubleshooting

### **Issue: Ambulances not detected**
- **Solution:** Ensure ambulances are properly labeled in training data
- Check label files have class `1` for ambulances
- Verify ambulance images are in training set

### **Issue: False positives (vehicles detected as ambulances)**
- **Solution:** Add more diverse vehicle images
- Review and correct mislabeled training data
- Increase training epochs

### **Issue: Low ambulance detection accuracy**
- **Solution:** 
  - Add more ambulance training images
  - Ensure balanced dataset
  - Use data augmentation
  - Check label quality

---

## 📈 Expected Results

After proper training:
- **Vehicle Detection:** > 85% accuracy
- **Ambulance Detection:** > 70% accuracy
- **False Positive Rate:** < 5%
- **Emergency Trigger:** Automatic when ambulance detected

---

## 🎓 Next Steps

1. Train the model with your dataset
2. Test ambulance detection
3. Fine-tune if needed
4. Deploy to production

**Ready to train?** Follow the steps above! 🚀

---

**Need Help?** Check the main `TRAINING_GUIDE.md` for general training instructions.
