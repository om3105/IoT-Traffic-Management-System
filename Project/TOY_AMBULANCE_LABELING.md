# Toy Ambulance Labeling Guide

## 🚑 Your Ambulance Type

Based on your dataset, you're working with **toy ambulances** that have:
- White body
- Blue and red lights on roof
- Red "Star of Life" emblem
- Red cross symbol on front
- Simplified toy design

---

## 📝 Labeling Instructions

### **Step 1: Identify Ambulances in Images**

Look for these features:
- ✅ White toy ambulance
- ✅ Emergency lights (blue/red)
- ✅ Star of Life symbol
- ✅ Red cross on front
- ✅ Distinctive ambulance shape

### **Step 2: Label Format**

For each ambulance in an image, add a line to the label file:

```
1 x_center y_center width height
```

**Where:**
- `1` = Ambulance class ID
- All coordinates are normalized (0.0 to 1.0)

### **Step 3: Calculate Coordinates**

**Example:** If ambulance is at:
- Center X: 400 pixels (image width: 800px) → `400/800 = 0.5`
- Center Y: 300 pixels (image height: 600px) → `300/600 = 0.5`
- Width: 200 pixels → `200/800 = 0.25`
- Height: 150 pixels → `150/600 = 0.25`

**Label line:**
```
1 0.5 0.5 0.25 0.25
```

---

## 🎯 Labeling Tips for Toy Ambulances

### **1. Include Full Vehicle**
- Draw bounding box around entire ambulance
- Include lights, emblems, and body
- Don't cut off edges

### **2. Multiple Ambulances**
If image has multiple ambulances, add one line per ambulance:
```
0 0.3 0.4 0.15 0.2    # Regular vehicle
1 0.6 0.5 0.2 0.25   # Ambulance 1
1 0.8 0.7 0.18 0.22  # Ambulance 2
```

### **3. Partial Visibility**
- If ambulance is partially visible, still label it
- Include visible parts in bounding box
- Model will learn partial detections

### **4. Different Angles**
- Label ambulances from all angles (front, side, back)
- Helps model recognize ambulances in various positions

---

## 🔧 Quick Labeling Workflow

### **Using LabelImg:**

1. **Open LabelImg:**
   ```bash
   labelImg
   ```

2. **Configure:**
   - Format: **YOLO**
   - Open Dir: `Project/training/dataset/images/train/`
   - Save Dir: `Project/training/dataset/labels/train/`

3. **Create Classes:**
   - Class 0: `vehicle`
   - Class 1: `ambulance`

4. **Label Process:**
   - Open each image
   - Draw box around vehicles → Select "vehicle" (0)
   - Draw box around ambulances → Select "ambulance" (1)
   - Save (Ctrl+S)
   - Next image (D key)

---

## 📊 Example Label File

**Image:** `ambulance_traffic_1.jpg` (800x600 pixels)

**Label file:** `ambulance_traffic_1.txt`
```
0 0.25 0.4 0.15 0.2    # Car on left
0 0.75 0.5 0.12 0.18   # Car on right
1 0.5 0.3 0.2 0.25     # Ambulance in center
```

**Visualization:**
```
[Car]        [Ambulance]        [Car]
  (0.25)        (0.5)          (0.75)
```

---

## ✅ Verification Checklist

After labeling, verify:

- [ ] All ambulances are labeled (class 1)
- [ ] All regular vehicles are labeled (class 0)
- [ ] Bounding boxes are tight around vehicles
- [ ] Coordinates are normalized (0-1)
- [ ] Label files match image files (same name, .txt extension)
- [ ] Both train and val sets have ambulance labels

---

## 🚀 After Labeling

1. **Verify dataset:**
   ```bash
   python3 check_dataset.py
   ```

2. **Check ambulance count:**
   - Should show ambulance labels in output
   - Minimum: 10+ ambulance labels for training

3. **Train model:**
   ```bash
   python3 train.py
   ```

---

## 🎓 Training Tips for Toy Ambulances

### **1. Distinctive Features**
Toy ambulances have clear features:
- White color (distinct from other vehicles)
- Emergency lights (blue/red)
- Star of Life symbol
- Red cross emblem

### **2. Size Variations**
- Toy ambulances may be smaller than real vehicles
- Label accurately regardless of size
- Model will learn size variations

### **3. Lighting Conditions**
- Label ambulances in various lighting
- Bright, dim, and shadow conditions
- Helps model generalize

### **4. Occlusion**
- If ambulance is partially hidden, still label visible parts
- Model learns to detect partial ambulances

---

## 📈 Expected Results

After training with properly labeled toy ambulances:

- **Detection Accuracy:** > 75% for toy ambulances
- **False Positives:** < 10% (other white vehicles)
- **Emergency Trigger:** Automatic when ambulance detected

---

## ⚠️ Common Mistakes

1. **Wrong Class ID:**
   - ❌ Using `0` for ambulance
   - ✅ Use `1` for ambulance

2. **Incorrect Coordinates:**
   - ❌ Using pixel values
   - ✅ Use normalized values (0-1)

3. **Missing Labels:**
   - ❌ Not labeling all ambulances
   - ✅ Label every ambulance in every image

4. **Loose Bounding Boxes:**
   - ❌ Box too large (includes background)
   - ✅ Tight box around vehicle only

---

## 🎯 Quick Reference

**Class IDs:**
- `0` = Vehicle (car, bus, truck, motorcycle)
- `1` = Ambulance

**Label Format:**
```
class_id x_center y_center width height
```

**All values normalized 0-1**

---

**Ready to label?** Use LabelImg and follow the steps above! 🚀
