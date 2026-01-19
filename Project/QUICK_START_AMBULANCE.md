# 🚑 Quick Start: Train Model to Detect Your Toy Ambulance

## Current Status ✅

Your dataset is ready with:
- ✅ 11 training images
- ✅ 3 validation images  
- ✅ 36 vehicles already labeled (class 0)
- ⚠️ **0 ambulances labeled** - You need to add these!

---

## 🎯 What You Need to Do

### **Step 1: Label the Toy Ambulances** (15-30 minutes)

Your images contain toy ambulances like the one shown. You need to manually label them.

**Option A: Using LabelImg (Recommended)**

1. **Install LabelImg:**
   ```bash
   pip install labelImg
   ```

2. **Open LabelImg:**
   ```bash
   labelImg
   ```

3. **Configure:**
   - Click "Open Dir" → Select: `Project/training/dataset/images/train/`
   - Click "Change Save Dir" → Select: `Project/training/dataset/labels/train/`
   - Format: **YOLO** (top right)
   - Create classes: `vehicle` and `ambulance`

4. **Label Process:**
   - Open each image
   - **For regular vehicles:** Draw box → Select "vehicle" (class 0)
   - **For toy ambulances:** Draw box → Select "ambulance" (class 1)
   - Press `Ctrl+S` to save
   - Press `D` for next image
   - Repeat for all 11 training images

5. **Do the same for validation:**
   - Open: `Project/training/dataset/images/val/`
   - Save to: `Project/training/dataset/labels/val/`
   - Label all 3 validation images

**Option B: Manual Text Editing**

1. Open label files in: `Project/training/dataset/labels/train/`
2. For images with ambulances, add lines like:
   ```
   1 0.5 0.5 0.2 0.25  # Ambulance at center
   ```
   (See TOY_AMBULANCE_LABELING.md for coordinate calculation)

---

### **Step 2: Verify Labels** (2 minutes)

```bash
cd Project
python3 check_dataset.py
```

**Expected output:**
- Should show ambulance labels > 0
- Both train and val should have ambulances

---

### **Step 3: Train the Model** (30-60 minutes)

```bash
python3 train.py
```

**What happens:**
- Trains for 100 epochs
- Saves best model to `custom_model.pt`
- Shows training progress and metrics

---

### **Step 4: Test in Dashboard** (5 minutes)

1. **Start dashboard:**
   ```bash
   streamlit run dashboard.py
   ```

2. **Test ambulance detection:**
   - Go to sidebar → Select "AI Analysis"
   - Upload an image with toy ambulance
   - Click "🤖 RUN ANALYSIS"
   - Should show: "🚨 AMBULANCE DETECTED! Emergency mode activated."

---

## 🎯 Identifying Your Toy Ambulance

Look for these features in your images:
- ✅ White toy vehicle
- ✅ Blue and red lights on roof
- ✅ Red "Star of Life" symbol
- ✅ Red cross on front
- ✅ Distinctive ambulance shape

**Label ALL ambulances you see**, even if:
- Partially visible
- Different angles
- Different sizes

---

## ⏱️ Time Estimate

- **Labeling:** 15-30 minutes (11 train + 3 val images)
- **Training:** 30-60 minutes (depending on hardware)
- **Testing:** 5 minutes
- **Total:** ~1-2 hours

---

## 🚀 Quick Command Summary

```bash
# 1. Label ambulances (use LabelImg)
labelImg

# 2. Verify dataset
cd Project
python3 check_dataset.py

# 3. Train model
python3 train.py

# 4. Test in dashboard
streamlit run dashboard.py
```

---

## 📚 Need Help?

- **Labeling guide:** `TOY_AMBULANCE_LABELING.md`
- **Full training guide:** `AMBULANCE_TRAINING_GUIDE.md`
- **General training:** `TRAINING_GUIDE.md`

---

## ✅ Success Checklist

After training, you should have:
- [ ] Ambulance labels in dataset (> 10 labels)
- [ ] Trained model: `custom_model.pt`
- [ ] Dashboard detects ambulances
- [ ] Emergency mode triggers automatically

**Ready? Start with Step 1 - Label those ambulances!** 🚑🚀
