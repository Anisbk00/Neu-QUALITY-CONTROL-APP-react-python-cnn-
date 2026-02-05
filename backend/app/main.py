"""
FastAPI Backend for NEU Surface Defect Detection
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from typing import List, Optional, Dict
import numpy as np
import cv2
import os
import json
import uuid
from datetime import datetime
from pathlib import Path
import base64

# Import inference module
from backend.inference.neu_inference import run_inference, CLASS_NAMES


app = FastAPI(title="NEU Quality Control API", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data directories
DATA_DIR = Path("data")
UPLOADS_DIR = DATA_DIR / "uploads"
REPORTS_DIR = DATA_DIR / "reports"

UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# In-memory storage for pieces (in production, use a database)
pieces_db: Dict[str, Dict] = {}


class AnalyzeRequest(BaseModel):
    """Request body for analyze endpoint"""
    piece_id: str
    images: List[str]  # Base64 encoded PNG images


class ReportRequest(BaseModel):
    """Request body for report generation"""
    piece_id: str
    notes: Optional[str] = ""


class ValidationRequest(BaseModel):
    """Request body for validation/rejection"""
    piece_id: str
    status: str  # 'validated' or 'rejected'
    notes: Optional[str] = ""


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "NEU Quality Control API",
        "version": "1.0.0"
    }


@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a 3D model file (.stl, .obj, .gltf, .glb)
    """
    # Validate file extension
    allowed_extensions = ['.stl', '.obj', '.gltf', '.glb']
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
        )
    
    # Generate unique piece ID
    piece_id = f"PIECE_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8].upper()}"
    
    # Save file
    file_path = UPLOADS_DIR / f"{piece_id}{file_ext}"
    
    try:
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
        
        # Store piece metadata
        pieces_db[piece_id] = {
            "id": piece_id,
            "filename": file.filename,
            "file_path": str(file_path),
            "uploaded_at": datetime.now().isoformat(),
            "status": "uploaded",
            "analysis_results": None
        }
        
        return {
            "piece_id": piece_id,
            "filename": file.filename,
            "message": "File uploaded successfully"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@app.post("/api/analyze")
async def analyze(request: AnalyzeRequest):
    piece_id = request.piece_id
    if piece_id not in pieces_db:
        raise HTTPException(status_code=404, detail="Piece not found")
    
    try:
        images = []
        for i, img_b64 in enumerate(request.images):
            if ',' in img_b64:
                img_b64 = img_b64.split(',')[1]
            img_data = base64.b64decode(img_b64)
            nparr = np.frombuffer(img_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
            if img is None:
                raise ValueError(f"Failed to decode image {i}")
            images.append(img)
        
        results = run_inference(images, piece_id=piece_id)
        
        pieces_db[piece_id]["analysis_results"] = results
        pieces_db[piece_id]["analyzed_at"] = datetime.now().isoformat()
        pieces_db[piece_id]["status"] = "analyzed"
        
        return {"piece_id": piece_id, "results": results}
    
    except Exception as e:
        import traceback
        print("❌ Analysis error traceback:\n", traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/api/report")
async def generate_report(request: ReportRequest):
    """
    Generate a PDF report for the analyzed piece.
    """
    piece_id = request.piece_id
    
    if piece_id not in pieces_db:
        raise HTTPException(status_code=404, detail="Piece not found")
    
    piece = pieces_db[piece_id]
    
    if not piece.get("analysis_results"):
        raise HTTPException(status_code=400, detail="Piece has not been analyzed yet")
    
    # Generate report content
    report_data = {
        "piece_id": piece_id,
        "filename": piece["filename"],
        "uploaded_at": piece["uploaded_at"],
        "analyzed_at": piece.get("analyzed_at"),
        "results": piece["analysis_results"],
        "notes": request.notes,
        "status": piece.get("status", "analyzed")
    }
    
    # Save report as JSON (in production, generate PDF)
    report_path = REPORTS_DIR / f"{piece_id}_report.json"
    with open(report_path, "w") as f:
        json.dump(report_data, f, indent=2)
    
    piece["report_path"] = str(report_path)
    
    return {
        "piece_id": piece_id,
        "report_path": str(report_path),
        "message": "Report generated successfully"
    }


@app.post("/api/validate")
async def validate_piece(request: ValidationRequest):
    """
    Mark a piece as validated.
    """
    piece_id = request.piece_id
    
    if piece_id not in pieces_db:
        raise HTTPException(status_code=404, detail="Piece not found")
    
    pieces_db[piece_id]["status"] = "validated"
    pieces_db[piece_id]["validated_at"] = datetime.now().isoformat()
    pieces_db[piece_id]["validation_notes"] = request.notes
    
    return {
        "piece_id": piece_id,
        "status": "validated",
        "message": "Pièce validée avec succès"
    }


@app.post("/api/reject")
async def reject_piece(request: ValidationRequest):
    """
    Mark a piece as rejected.
    """
    piece_id = request.piece_id
    
    if piece_id not in pieces_db:
        raise HTTPException(status_code=404, detail="Piece not found")
    
    pieces_db[piece_id]["status"] = "rejected"
    pieces_db[piece_id]["rejected_at"] = datetime.now().isoformat()
    pieces_db[piece_id]["rejection_notes"] = request.notes
    
    return {
        "piece_id": piece_id,
        "status": "rejected",
        "message": "Pièce rejetée"
    }


@app.get("/api/pieces/{piece_id}")
async def get_piece(piece_id: str):
    """
    Get piece information by ID.
    """
    if piece_id not in pieces_db:
        raise HTTPException(status_code=404, detail="Piece not found")
    
    return pieces_db[piece_id]


@app.get("/api/pieces")
async def list_pieces():
    """
    List all pieces.
    """
    return {"pieces": list(pieces_db.values())}


@app.get("/api/classes")
async def get_classes():
    """
    Get list of defect classes.
    """
    return {
        "classes": CLASS_NAMES,
        "count": len(CLASS_NAMES)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
