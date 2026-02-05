# 🚀 Quick Start Guide

Get the NEU Quality Control application running in under 5 minutes!

## Prerequisites

Choose ONE option:

**Option A: Docker (Easiest)**
- Docker Desktop installed
- That's it!

**Option B: Local Development**
- Python 3.11+
- Node.js 18+
- pip and npm

## 🏃 Quick Start (Docker)

```bash
# 1. Navigate to project
cd neu-quality-control-app

# 2. Start everything
docker-compose up --build

# 3. Open browser
# Frontend: http://localhost:3000
# API Docs: http://localhost:8000/docs
```

That's it! The application is now running in mock mode.

## 🔧 Quick Start (Local)

### Terminal 1 - Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run backend
cd ..
python -m uvicorn backend.app.main:app --reload
```

### Terminal 2 - Frontend

```bash
cd frontend

# Install dependencies
npm install

# Run frontend
npm run dev
```

Open http://localhost:3000

## 🧪 Test the Application

### 1. Upload a 3D Model

Click "Importer une pièce" and select a file:
- Supported: `.stl`, `.obj`, `.gltf`, `.glb`
- The 3D viewer will display your model

### 2. Run Analysis

Click "🔍 Analyser automatiquement"
- Captures 5 views (iso, front, left, right, top)
- Converts to grayscale
- Runs inference (mock or real)
- Displays results in right panel

### 3. Review Results

Check the right panel for:
- Predicted defect class
- Anomaly probability score
- Per-class probabilities

### 4. Take Action

Use footer buttons:
- 📄 **Enregistrer rapport** - Save analysis report
- ❌ **Rejeter la pièce** - Reject the piece
- ✅ **Valider la pièce** - Validate the piece

## 🤖 Add Real Model (Optional)

Currently running in mock mode. To use a real trained model:

```bash
# 1. Train model using the Colab notebook
# 2. Download model file (neu_cnn_model.h5)
# 3. Place in models directory
cp neu_cnn_model.h5 models/

# 4. Restart backend
docker-compose restart backend
# or Ctrl+C and restart uvicorn
```

See `MODEL_INTEGRATION.md` for details.

## ✅ Verify Installation

### Check Backend

```bash
curl http://localhost:8000/
# Should return: {"status":"online",...}

curl http://localhost:8000/api/classes
# Should return: {"classes":["crazing","inclusion",...]}
```

### Check Frontend

Open http://localhost:3000
- Should see "CONTRÔLE QUALITÉ VISUEL" header
- Left panel with "Importer une pièce" button
- Center panel with 3D viewer space
- Right panel with "MESURE 3D / IA"
- Footer with action buttons

## 🧪 Run Tests

```bash
cd backend
pytest -v
```

All tests should pass ✅

## 📊 API Documentation

Visit http://localhost:8000/docs for interactive API documentation.

Try the endpoints:
- `POST /api/upload` - Upload a 3D file
- `POST /api/analyze` - Analyze a piece
- `GET /api/classes` - List defect classes

## 🐛 Troubleshooting

### Port Already in Use

**Backend (8000):**
```bash
# Kill process on port 8000
kill $(lsof -t -i:8000)
```

**Frontend (3000):**
```bash
# Kill process on port 3000
kill $(lsof -t -i:3000)
```

### Docker Issues

```bash
# Stop all containers
docker-compose down

# Remove volumes
docker-compose down -v

# Rebuild from scratch
docker-compose up --build --force-recreate
```

### Module Not Found

**Backend:**
```bash
# Reinstall dependencies
pip install -r backend/requirements.txt
```

**Frontend:**
```bash
# Clear cache and reinstall
rm -rf frontend/node_modules
cd frontend && npm install
```

## 📁 Project Structure

```
neu-quality-control-app/
├── frontend/              # React app
│   ├── src/
│   │   ├── components/   # UI components
│   │   ├── utils/        # API client
│   │   └── types/        # TypeScript types
│   └── package.json
├── backend/              # FastAPI app
│   ├── app/             # API endpoints
│   ├── inference/       # ML module
│   └── tests/           # Tests
├── models/              # Place trained model here
├── docker/              # Docker configs
└── docker-compose.yml
```

## 🎯 Next Steps

1. ✅ **Application running** - You're here!
2. 📖 **Read README.md** - Full documentation
3. 🤖 **Add real model** - See MODEL_INTEGRATION.md
4. 🧪 **Run tests** - `./run_tests.sh`
5. 🚀 **Deploy** - Docker Compose for production

## 💡 Tips

- **Mock Mode**: Works without a trained model - perfect for testing
- **3D Files**: Try with sample STL files first
- **API Docs**: Explore at http://localhost:8000/docs
- **Console**: Check browser console (F12) for debug info
- **Logs**: Watch Docker logs: `docker-compose logs -f`

## 📞 Need Help?

1. Check `README.md` for full documentation
2. Check `MODEL_INTEGRATION.md` for model setup
3. Run tests: `pytest -v`
4. Check logs: `docker-compose logs backend`
5. Verify preprocessing: `python backend/inference/neu_inference.py`

---

**Happy Quality Controlling! 🏭✨**
