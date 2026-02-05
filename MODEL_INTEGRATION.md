# Model Integration Guide

This document explains how to integrate your trained NEU Surface Defect Detection model into the application.

## Overview

The application is designed for **drop-in replacement** of the ML model. When you train a model using the provided Colab notebook and save it, you can simply place it in the correct location and the application will use it automatically.

## Step-by-Step Integration

### 1. Train Your Model

Use the provided `NEU_Surface_Defect_Detection_v1.ipynb` notebook:

```python
# After training in the notebook...
# Save the best model
model.save('neu_cnn_model.keras')

# Or as HDF5
model.save('neu_cnn_model.h5')

# Also save class information
import json
class_info = {
    "classes": CLASS_NAMES,
    "img_size": IMG_SIZE
}
with open('class_info.json', 'w') as f:
    json.dump(class_info, f)
```

### 2. Download Model Files

From Google Colab or Kaggle:

```python
# In the notebook
from google.colab import files
files.download('neu_cnn_model.keras')
files.download('class_info.json')
```

### 3. Place Model in Application

```bash
# Copy model to the models directory
cp /path/to/neu_cnn_model.keras neu-quality-control-app/models/
cp /path/to/neu_cnn_model.h5 neu-quality-control-app/models/  # if using .h5

# Verify placement
ls -lh neu-quality-control-app/models/
```

### 4. Configure Model Path (Optional)

**Option A: Use default location**
```bash
# Just place the file at models/neu_cnn_model.h5
# Application will find it automatically
```

**Option B: Custom path via environment variable**
```bash
export MODEL_PATH=/custom/path/to/model.h5
```

**Option C: Docker Compose**
```yaml
# In docker-compose.yml
services:
  backend:
    environment:
      - MODEL_PATH=/app/models/my_model.keras
    volumes:
      - ./my_models:/app/models
```

### 5. Verify Integration

**Run the validation script:**

```bash
cd backend
python inference/neu_inference.py
```

You should see:
```
============================================================
PREPROCESSING VALIDATION
============================================================
✅ Shape: (200, 200, 1)
✅ Dtype: float32
✅ Value range: [0.0000, 1.0000]

✅ All preprocessing checks PASSED!
============================================================
```

**Test with real model:**

```python
from inference.neu_inference import load_model, run_inference
import numpy as np

# Load model
model = load_model()
print(f"Model loaded: {model is not None}")

# Test inference
test_img = np.random.randint(0, 256, (200, 200), dtype=np.uint8)
result = run_inference([test_img], piece_id="TEST")
print(f"Predicted class: {result['predicted_class']}")
print(f"Anomaly score: {result['anomaly_score']:.2f}%")
```

### 6. Restart Application

**Docker:**
```bash
docker-compose restart backend
```

**Local:**
```bash
# Stop the uvicorn process (Ctrl+C)
# Restart it
cd neu-quality-control-app
python -m uvicorn backend.app.main:app --reload
```

### 7. Test in UI

1. Open http://localhost:3000
2. Import a 3D model (STL/OBJ/GLTF/GLB)
3. Click "Analyser automatiquement"
4. Check that results use the real model (not mock)

## Model Requirements Checklist

Before integrating, verify your model meets these requirements:

### ✅ Architecture Requirements

- [ ] Input shape: `(None, 200, 200, 1)` - GRAYSCALE images
- [ ] Output shape: `(None, 6)` - 6 class probabilities
- [ ] Output activation: Softmax (probabilities sum to 1)
- [ ] File format: Keras `.h5` or `.keras`

### ✅ Class Order

The model MUST output classes in this exact order:

```python
CLASS_NAMES = [
    "crazing",         # Index 0
    "inclusion",       # Index 1
    "patches",         # Index 2
    "pitted_surface",  # Index 3
    "rolled-in_scale", # Index 4
    "scratches"        # Index 5
]
```

### ✅ Preprocessing Compatibility

The model was trained with:

```python
# 1. Grayscale loading
img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)

# 2. Resize to 200x200
img = cv2.resize(img, (200, 200))

# 3. Normalize to [0, 1]
img = img.astype('float32') / 255.0

# 4. Add channel dimension
img = np.expand_dims(img, axis=-1)  # (200, 200, 1)
```

## Verify Model Structure

```python
import tensorflow as tf

model = tf.keras.models.load_model('models/neu_cnn_model.h5')

# Check input shape
print("Input shape:", model.input_shape)
# Expected: (None, 200, 200, 1)

# Check output shape
print("Output shape:", model.output_shape)
# Expected: (None, 6)

# Check output layer
print("Output activation:", model.layers[-1].activation.__name__)
# Expected: softmax

# Test with dummy data
import numpy as np
dummy_input = np.random.rand(1, 200, 200, 1).astype('float32')
output = model.predict(dummy_input)
print("Output shape:", output.shape)  # (1, 6)
print("Sum of probabilities:", output.sum())  # ~1.0
```

## Common Integration Issues

### Issue 1: Model File Not Found

**Symptoms:**
```
⚠️  Model not found at models/neu_cnn_model.h5. Using mock inference.
```

**Solutions:**
- Check file exists: `ls -lh models/`
- Check file permissions: `chmod 644 models/neu_cnn_model.h5`
- Verify `MODEL_PATH` environment variable
- Check Docker volume mounts

### Issue 2: Wrong Input Shape

**Symptoms:**
```
ValueError: Input 0 of layer "model" is incompatible with the layer
```

**Solutions:**
- Verify model input shape matches `(None, 200, 200, 1)`
- Check you didn't modify preprocessing
- Ensure model was trained with grayscale images
- Run: `python backend/inference/neu_inference.py`

### Issue 3: Wrong Number of Classes

**Symptoms:**
```
IndexError: list index out of range
```

**Solutions:**
- Verify model outputs 6 classes
- Check class names list matches training
- Ensure softmax activation on output layer

### Issue 4: TensorFlow Version Mismatch

**Symptoms:**
```
Unable to load model due to version incompatibility
```

**Solutions:**
- Check TensorFlow version: `pip show tensorflow`
- Required: TensorFlow 2.15.x
- Reinstall if needed: `pip install tensorflow-cpu==2.15.0`
- Consider saving model in compatible format

## Performance Optimization

### For CPU Inference

The default configuration uses `tensorflow-cpu`:

```txt
# requirements.txt
tensorflow-cpu==2.15.0
```

### For GPU Inference

1. **Update requirements.txt:**
```txt
tensorflow==2.15.0  # GPU version
```

2. **Ensure CUDA compatibility:**
- CUDA 12.2
- cuDNN 8.9

3. **Verify GPU detection:**
```python
import tensorflow as tf
print("GPUs Available:", tf.config.list_physical_devices('GPU'))
```

### Model Optimization Options

For production deployment, consider:

1. **TensorFlow Lite** (for edge devices):
```python
converter = tf.lite.TFLiteConverter.from_keras_model(model)
tflite_model = converter.convert()
with open('model.tflite', 'wb') as f:
    f.write(tflite_model)
```

2. **ONNX** (for cross-platform):
```python
import tf2onnx
onnx_model, _ = tf2onnx.convert.from_keras(model)
```

3. **TensorRT** (for NVIDIA GPUs):
```python
# Requires TensorRT installed
# Converts model to optimized format
```

## Testing Your Integration

### Unit Test

```bash
cd backend
pytest tests/test_inference.py::TestRunInference -v
```

### API Test

```bash
# Test analyze endpoint
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "piece_id": "TEST_PIECE",
    "images": ["<base64_image_data>"]
  }'
```

### Full Integration Test

```bash
# Run all tests
cd backend
pytest -v
```

## Rollback Plan

If the real model causes issues:

1. **Remove model file:**
```bash
rm models/neu_cnn_model.h5
```

2. **Application automatically falls back to mock inference**

3. **Or set environment variable:**
```bash
export USE_MOCK_INFERENCE=true
```

## Production Checklist

Before deploying to production:

- [ ] Model validated on test dataset
- [ ] Preprocessing verified identical to training
- [ ] Integration tests pass
- [ ] Performance acceptable (inference time < 1s)
- [ ] Error handling tested
- [ ] Monitoring/logging configured
- [ ] Backup/rollback plan ready
- [ ] Documentation updated

## Support

For model integration issues:

1. Check logs: `docker-compose logs backend`
2. Run validation: `python backend/inference/neu_inference.py`
3. Test preprocessing manually
4. Verify model file integrity
5. Check TensorFlow version compatibility

---

**Remember:** The preprocessing pipeline is the most critical aspect. Any mismatch between training and inference preprocessing will cause poor predictions, even with a perfectly trained model.
