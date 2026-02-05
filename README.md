# NEU Surface Defect Detection - Quality Control Application

A full-stack web application for automated surface defect detection on 3D models using deep learning, exactly matching the NEU Surface Defect Detection Colab notebook preprocessing.

![Application Screenshot](screenshot.png)

## 🎯 Features

- **3D Model Viewer**: Support for STL, OBJ, GLTF, GLB formats
- **Multi-View Capture**: Automatic capture from 5 camera angles (iso, front, left, right, top)
- **AI-Powered Analysis**: CNN model trained on NEU Surface Defect Database
- **6 Defect Classes**: crazing, inclusion, patches, pitted_surface, rolled-in_scale, scratches
- **French UI**: Complete CONTRÔLE QUALITÉ VISUEL interface
- **Report Generation**: Save analysis results
- **Piece Validation/Rejection**: Quality control workflow

## 🏗️ Architecture

```
neu-quality-control-app/
├── frontend/          # React + TypeScript + Three.js
├── backend/           # FastAPI + TensorFlow
│   ├── app/           # API endpoints
│   ├── inference/     # ML inference module
│   └── tests/         # Pytest tests
├── models/            # Trained model storage
├── docker/            # Docker configurations
└── data/              # Upload and report storage
```

## 📋 Prerequisites

- **Python 3.11+**
- **Node.js 18+**
- **Docker & Docker Compose** (for containerized deployment)

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
# Clone or extract the project
cd neu-quality-control-app

# Start all services
docker-compose up --build

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Option 2: Local Development

**Backend:**

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run backend
cd ..
python -m uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend:**

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

## 🤖 Model Integration

### CRITICAL: Preprocessing Requirements

The application uses **EXACT** preprocessing from the NEU notebook:

```python
IMG_SIZE = 200
# Images are:
# 1. Loaded as GRAYSCALE (cv2.IMREAD_GRAYSCALE)
# 2. Resized to (200, 200)
# 3. Normalized: float32 / 255.0
# 4. Channel dimension added: (200, 200, 1)
```

### Using the Real Model

1. **Train your model** using the provided `NEU_Surface_Defect_Detection_v1.ipynb`

2. **Save the model**:
   ```python
   model.save('neu_cnn_model.h5')
   # or
   model.save('neu_cnn_model.keras')
   ```

3. **Place the model file**:
   ```bash
   cp neu_cnn_model.h5 models/
   ```

4. **Set environment variable** (optional):
   ```bash
   export MODEL_PATH=models/neu_cnn_model.h5
   ```

5. **Restart the backend**:
   ```bash
   docker-compose restart backend
   # or if running locally
   # restart the uvicorn process
   ```

### Model Requirements

- **Input Shape**: `(None, 200, 200, 1)` - Grayscale images
- **Output Shape**: `(None, 6)` - 6 class probabilities
- **Format**: Keras `.h5` or `.keras` file
- **Classes (in order)**:
  1. crazing
  2. inclusion
  3. patches
  4. pitted_surface
  5. rolled-in_scale
  6. scratches

### Mock vs Real Mode

**Without Model (Mock Mode)**:
- Uses deterministic hash-based predictions
- Returns valid probability distributions
- Perfect for testing and development

**With Model (Real Mode)**:
- Loads TensorFlow model automatically
- Runs actual inference on captured views
- Averages predictions across multiple views

## 🧪 Testing

### Backend Tests

```bash
cd backend

# Run all tests
pytest -v

# Run specific test file
pytest tests/test_inference.py -v

# Run with coverage
pytest --cov=inference --cov=app tests/
```

### Test Coverage

- ✅ Preprocessing validation (shape, dtype, normalization)
- ✅ Mock inference determinism
- ✅ Multi-view inference
- ✅ API endpoints (upload, analyze, report, validate, reject)
- ✅ Constants match notebook exactly

## 📊 API Endpoints

### Upload File
```http
POST /api/upload
Content-Type: multipart/form-data

file: <3D model file>
```

### Analyze Piece
```http
POST /api/analyze
Content-Type: application/json

{
  "piece_id": "PIECE_20240205_123456_ABC",
  "images": ["data:image/png;base64,iVBOR...", ...]
}
```

### Generate Report
```http
POST /api/report
Content-Type: application/json

{
  "piece_id": "PIECE_20240205_123456_ABC",
  "notes": "Optional notes"
}
```

### Validate Piece
```http
POST /api/validate
Content-Type: application/json

{
  "piece_id": "PIECE_20240205_123456_ABC",
  "status": "validated",
  "notes": "Approved"
}
```

### Reject Piece
```http
POST /api/reject
Content-Type: application/json

{
  "piece_id": "PIECE_20240205_123456_ABC",
  "status": "rejected",
  "notes": "Defect found"
}
```

## 🎨 UI Components

### Left Panel
- Import 3D model button
- Model selector (placeholder)
- Piece ID display
- Preview thumbnail
- Inspection summary

### Center Panel
- 3D viewer with Three.js
- Camera view controls (iso, front, left, right, top, reset)
- Multi-view capture for analysis
- Real-time rendering status

### Right Panel
- Analysis results display
- Predicted defect class
- Anomaly probability score
- Per-class probability breakdown
- Visual probability bars

### Footer
- Save report button
- Reject piece button
- Validate piece button

## 🔧 Configuration

### Environment Variables

**Backend:**
- `MODEL_PATH`: Path to the trained model (default: `models/neu_cnn_model.h5`)

**Frontend:**
- `VITE_API_URL`: Backend API URL (default: `http://localhost:8000`)

### Model Path Options

1. Environment variable: `MODEL_PATH=custom/path/model.h5`
2. Docker volume: Mount your models directory
3. Default location: `models/neu_cnn_model.h5`

## 📦 Deliverables

This project includes:

- ✅ Complete React + TypeScript frontend
- ✅ FastAPI backend with TensorFlow inference
- ✅ Exact NEU notebook preprocessing implementation
- ✅ Multi-view grayscale capture system
- ✅ Comprehensive test suite
- ✅ Docker deployment configuration
- ✅ Drop-in model support
- ✅ Mock inference for testing

## ⚠️ Important Notes

### Preprocessing Compatibility

**DO NOT MODIFY** the preprocessing in `backend/inference/neu_inference.py` unless you also retrain the model with the same changes. The preprocessing is **exact** and matches:

```python
# From notebook:
img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)  # Grayscale
img = cv2.resize(img, (200, 200))              # Resize
img = img.astype('float32') / 255.0            # Normalize
img = np.expand_dims(img, axis=-1)             # Add channel
```

### Common Mistakes to Avoid

❌ **Don't** convert to RGB (model expects grayscale)  
❌ **Don't** resize to 224×224 (model expects 200×200)  
❌ **Don't** use different normalization  
❌ **Don't** change channel order  

✅ **Do** use exact preprocessing  
✅ **Do** verify with tests  
✅ **Do** check model input shape matches  

## 🐛 Troubleshooting

### Model Loading Issues

**Error**: "Model not found"
- Check `MODEL_PATH` environment variable
- Verify model file exists in `models/` directory
- Ensure file permissions are correct

**Error**: "Cannot load model"
- Verify TensorFlow version compatibility
- Check model file isn't corrupted
- Try loading model manually in Python shell

### Inference Issues

**Error**: "Shape mismatch"
- Run preprocessing validation: `python backend/inference/neu_inference.py`
- Verify model input shape is `(None, 200, 200, 1)`
- Check you didn't modify preprocessing

### Frontend Issues

**Error**: "Cannot capture views"
- Check WebGL support in browser
- Verify 3D model loaded successfully
- Check browser console for errors

## 📚 References

- [NEU Surface Defect Database](https://www.kaggle.com/datasets/kaustubhdikshit/neu-surface-defect-database)
- [Original Colab Notebook](NEU_Surface_Defect_Detection_v1.ipynb)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Three.js Documentation](https://threejs.org/docs/)

## 📄 License

This project is for educational and research purposes.

## 🤝 Contributing

1. Ensure preprocessing remains unchanged
2. Add tests for new features
3. Update documentation
4. Follow existing code style

## 📧 Support

For issues related to:
- **Model training**: See the Colab notebook
- **Preprocessing**: Check `backend/inference/neu_inference.py`
- **API**: See `/docs` endpoint for interactive documentation
- **UI**: Check browser console and network tab

---

**Built with ❤️ for Industrial Quality Control**
