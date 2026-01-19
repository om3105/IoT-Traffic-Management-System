# IoT Smart Traffic Management System - Project Analysis

## 📋 Project Overview

This is an **IoT-based Smart Traffic Management System** that combines:
- **Machine Learning** (YOLOv8) for vehicle detection and traffic density analysis
- **Real-time Dashboard** (Streamlit) for traffic monitoring and signal control
- **Hardware Integration** (ESP32/ESP32-CAM) via ThingSpeak cloud platform

---

## 🏗️ Project Structure

```
IoT/
├── ML/                          # Machine Learning Module
│   ├── main.py                  # Main vehicle detection script
│   ├── predict_custom.py        # Custom trained model inference
│   ├── train.py                 # Model training script
│   ├── setup_training.py        # Dataset preparation & auto-labeling
│   ├── yolov8m.pt              # Pre-trained YOLOv8 medium model
│   ├── requirements.txt         # ML dependencies
│   └── README.md               # ML module documentation
│
└── Project/                     # Dashboard & Control System
    ├── dashboard.py             # Streamlit web dashboard
    ├── traffic_engine.py        # Traffic analysis engine
    ├── style.css                # Dark theme styles
    ├── style_light.css          # Light theme styles
    ├── yolov8m.pt              # Model copy for dashboard
    ├── requirements.txt         # Dashboard dependencies
    └── README.md               # Dashboard documentation
```

---

## 🔍 Component Analysis

### 1. ML Module (`/ML/`)

#### **main.py**
- **Purpose**: Standalone vehicle detection for 4-directional traffic analysis
- **Key Features**:
  - Uses YOLOv8m for vehicle detection
  - Detects: Car, Motorcycle, Bus, Truck (COCO classes: 2, 3, 5, 7)
  - Calculates traffic density percentage (0-100%)
  - Computes signal timing (30-60 seconds based on density)
- **Output**: JSON with vehicle counts, densities, and signal times
- **Issues**:
  - ❌ Hardcoded image paths pointing to temporary Gemini upload directories
  - ❌ No command-line argument support for image paths

#### **traffic_engine.py** (in Project/)
- **Purpose**: TrafficAnalyzer class used by dashboard
- **Key Differences from ML/main.py**:
  - Returns annotated images (BGR format)
  - Uses MIN_TIME=5, MAX_TIME=60 (vs 30-60 in ML/main.py)
  - Filters classes during inference (more efficient)
- **Issues**:
  - ⚠️ Code duplication with ML/main.py
  - ⚠️ Inconsistent timing logic

#### **train.py**
- **Purpose**: Fine-tune YOLOv8 on custom dataset
- **Configuration**: 10 epochs (recommended: 50-100+ for production)
- **Output**: `traffic_analysis/custom_yolov8m/weights/best.pt`

#### **setup_training.py**
- **Purpose**: Dataset preparation with auto-labeling
- **Process**:
  1. Copies images to YOLO dataset structure
  2. Auto-labels using pre-trained model
  3. Maps COCO classes to custom classes (0-3)
  4. Creates train/val split (4:1)
- **Issues**:
  - ❌ Hardcoded source image paths

#### **predict_custom.py**
- **Purpose**: Inference using custom trained model
- **Features**: Lane-based detection (4 vertical lanes)
- **Issues**:
  - ❌ Hardcoded default image paths

---

### 2. Dashboard Module (`/Project/`)

#### **dashboard.py**
- **Purpose**: Real-time traffic monitoring and control dashboard
- **Features**:
  - 🎨 Dark/Light theme support
  - 📊 Real-time traffic density visualization
  - 🚦 Interactive traffic signal control
  - 🤖 AI Analysis mode (image upload & processing)
  - 📡 Live Data mode (ThingSpeak integration - placeholder)
  - ⏱️ Auto-refresh (1-second interval)
  - 🚨 Emergency vehicle detection
  - 📈 AQI monitoring
- **Modes**:
  1. **Simulation**: Synthetic data with sine wave patterns
  2. **AI Analysis**: Upload images for ML-based analysis
  3. **Live Data**: ThingSpeak API integration (needs configuration)
- **Logic Engine**:
  - Determines active lane based on highest density
  - Calculates timer: 30-60s (base 30s + density-based extension)
  - Emergency override: 99s timer, forces North lane
  - Manual override support

#### **traffic_engine.py**
- **Purpose**: Core ML engine for dashboard
- **Class**: `TrafficAnalyzer`
- **Methods**:
  - `analyze_road_image()`: Returns (count, density%, annotated_image)
  - `get_density_percentage()`: Converts count to 0-100% (MAX_CAPACITY=4)
  - `calculate_signal_time()`: Maps density to 5-60s signal time

---

## 🔧 Technical Stack

### Dependencies

**ML Module:**
- `ultralytics` (YOLOv8)
- `opencv-python-headless`
- `numpy<2.0` (compatibility constraint)

**Dashboard Module:**
- `streamlit`
- `streamlit-autorefresh`
- `requests` (ThingSpeak API)
- `pandas`, `plotly` (data visualization)
- `ultralytics`, `opencv-python-headless` (ML integration)

---

## ⚠️ Issues & Recommendations

### Critical Issues

1. **Code Duplication**
   - `TrafficAnalyzer` exists in both `ML/main.py` and `Project/traffic_engine.py`
   - **Recommendation**: Create shared module or consolidate

2. **Inconsistent Signal Timing Logic**
   - `ML/main.py`: MIN_TIME=30, MAX_TIME=60
   - `Project/traffic_engine.py`: MIN_TIME=5, MAX_TIME=60
   - **Recommendation**: Standardize to single configuration

3. **Hardcoded Paths**
   - Multiple files contain hardcoded Gemini upload paths
   - **Recommendation**: Use command-line arguments or config files

### Improvements

1. **Configuration Management**
   - Create `config.yaml` for:
     - Signal timing parameters
     - Model paths
     - ThingSpeak credentials
     - Lane mappings

2. **Code Organization**
   - Extract `TrafficAnalyzer` to shared module
   - Create utility functions for common operations

3. **Error Handling**
   - Add try-catch blocks for API calls
   - Validate image inputs
   - Handle missing model files gracefully

4. **Documentation**
   - Add docstrings to all functions
   - Document API endpoints
   - Create deployment guide

---

## 🚀 Usage Workflows

### ML Analysis Workflow
```bash
cd ML/
python main.py                    # Analyze with pre-trained model
python setup_training.py          # Prepare custom dataset
python train.py                   # Train custom model
python predict_custom.py          # Use custom model
```

### Dashboard Workflow
```bash
cd Project/
pip install -r requirements.txt
streamlit run dashboard.py        # Launch dashboard
```

---

## 📊 Data Flow

1. **Image Input** → YOLOv8 Model → Vehicle Detection
2. **Vehicle Count** → Density Calculation (0-100%)
3. **Density** → Signal Timing (5-60s or 30-60s)
4. **Dashboard** → Visual Display + Control Logic
5. **Control Logic** → Determines Active Lane & Timer

---

## 🎯 Key Metrics

- **Vehicle Detection**: YOLOv8m (medium model)
- **Supported Classes**: Car, Motorcycle, Bus, Truck
- **Density Calculation**: Based on MAX_CAPACITY=4 vehicles
- **Signal Timing Range**: 5-60s or 30-60s (inconsistent)
- **Dashboard Refresh**: 1 second interval
- **Lane Mapping**: 4 vertical lanes (N, E, S, W)

---

## 📝 Next Steps

1. ✅ Consolidate `TrafficAnalyzer` into shared module
2. ✅ Standardize signal timing configuration
3. ✅ Replace hardcoded paths with config/CLI args
4. ✅ Add comprehensive error handling
5. ✅ Implement proper logging
6. ✅ Create deployment documentation
7. ✅ Add unit tests for core functions

---

**Generated**: Project Analysis Document
**Status**: Ready for refactoring and improvements

