#!/bin/bash
# Training script for YOLOv8 custom traffic model

cd "$(dirname "$0")"

echo "🚀 Starting YOLOv8 Training for Traffic Detection"
echo "=================================================="
echo ""

# Check if dataset exists
if [ ! -f "training/dataset/data.yaml" ]; then
    echo "❌ Dataset not found! Running setup first..."
    python3 setup_training.py
    if [ $? -ne 0 ]; then
        echo "❌ Setup failed!"
        exit 1
    fi
fi

# Check dataset counts
TRAIN_COUNT=$(find training/dataset/images/train -type f \( -name "*.jpg" -o -name "*.jpeg" -o -name "*.png" \) | wc -l | tr -d ' ')
VAL_COUNT=$(find training/dataset/images/val -type f \( -name "*.jpg" -o -name "*.jpeg" -o -name "*.png" \) | wc -l | tr -d ' ')

echo "📊 Dataset Summary:"
echo "   Training images: $TRAIN_COUNT"
echo "   Validation images: $VAL_COUNT"
echo ""

if [ "$TRAIN_COUNT" -eq 0 ]; then
    echo "❌ No training images found!"
    exit 1
fi

# Run training
echo "🚀 Starting training..."
echo ""
python3 train.py

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Training completed successfully!"
    echo "📁 Check training/runs/custom_traffic_model/ for results"
    echo "💾 Model saved to: custom_model.pt"
else
    echo ""
    echo "❌ Training failed!"
    exit 1
fi
