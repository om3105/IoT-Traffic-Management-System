# Traffic Junction Vehicle Counter

This project detects and counts vehicles (cars, buses, trucks, motorcycles) on 4 roads (mapped to 4 vertical lanes) from a top-down traffic junction image.

## Setup

1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
    Note: This will install `ultralytics` (YOLOv8) and `opencv-python-headless`.

2.  **Run the Script**:
    ```bash
    python main.py
    ```

## Lane Mapping
The script assumes the image contains 4 vertical lane regions corresponding to the 4 roads:
-   **North**: Leftmost Lane (0-25% width)
-   **East**: Mid-Left Lane (25-50% width)
-   **South**: Mid-Right Lane (50-75% width)
-   **West**: Rightmost Lane (75-100% width)

You can adjust this mapping in `main.py` -> `detect_vehicles` method.

## Features
-   Uses YOLOv8m (Medium) for high accuracy.
-   Filters for valid road vehicles (Car, Bus, Truck, Motorcycle).
-   Ignores Pedestrians/Animals.
-   Outputs structured JSON.

## Training (Improve the Model)

To improve the model's accuracy on your specific traffic scene (toy cars), you can fine-tune it using the provided scripts.

1.  **Setup Dataset**:
    This script copies your uploaded images, creates a dataset structure, and uses the pre-trained model to generate initial labels (Auto-Labeling).
    ```bash
    python setup_training.py
    ```
    *Note: Check `dataset/labels` after running this to manually correct any wrong detections if needed.*

2.  **Train**:
    Run this script to fine-tune YOLOv8 on your dataset.
    ```bash
    python train.py
    ```
    This will save the best model to `traffic_analysis/custom_yolov8m/weights/best.pt`.

3.  **Run Custom Model**:
    To use your trained model for detection:
    ```bash
    python predict_custom.py
    ```
