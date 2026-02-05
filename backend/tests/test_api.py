"""
Tests for FastAPI endpoints
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path
import base64
import numpy as np
import cv2

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.main import app

client = TestClient(app)


class TestHealthCheck:
    """Test basic health endpoints"""
    
    def test_root(self):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "online"
    
    def test_get_classes(self):
        """Test get classes endpoint"""
        response = client.get("/api/classes")
        assert response.status_code == 200
        data = response.json()
        assert "classes" in data
        assert len(data["classes"]) == 6


class TestUpload:
    """Test file upload functionality"""
    
    def test_upload_stl(self):
        """Test uploading an STL file"""
        # Create fake STL content
        fake_stl = b"solid test\nendsolid test"
        
        response = client.post(
            "/api/upload",
            files={"file": ("test.stl", fake_stl, "application/octet-stream")}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "piece_id" in data
        assert data["filename"] == "test.stl"
    
    def test_upload_invalid_extension(self):
        """Test uploading invalid file type"""
        fake_content = b"test content"
        
        response = client.post(
            "/api/upload",
            files={"file": ("test.txt", fake_content, "text/plain")}
        )
        
        assert response.status_code == 400


class TestAnalysis:
    """Test analysis functionality"""
    
    def test_analyze_with_valid_images(self):
        """Test analysis with valid base64 images"""
        # First upload a piece
        fake_stl = b"solid test\nendsolid test"
        upload_response = client.post(
            "/api/upload",
            files={"file": ("test.stl", fake_stl, "application/octet-stream")}
        )
        piece_id = upload_response.json()["piece_id"]
        
        # Create fake grayscale image
        img = np.random.randint(0, 256, (200, 200), dtype=np.uint8)
        _, buffer = cv2.imencode('.png', img)
        img_b64 = base64.b64encode(buffer).decode('utf-8')
        
        # Analyze
        analyze_response = client.post(
            "/api/analyze",
            json={
                "piece_id": piece_id,
                "images": [img_b64, img_b64]  # Two views
            }
        )
        
        assert analyze_response.status_code == 200
        data = analyze_response.json()
        assert "results" in data
        assert "predicted_class" in data["results"]
        assert "class_probs" in data["results"]
        assert "anomaly_score" in data["results"]
    
    def test_analyze_nonexistent_piece(self):
        """Test analyzing non-existent piece"""
        response = client.post(
            "/api/analyze",
            json={
                "piece_id": "NONEXISTENT",
                "images": ["fake_base64"]
            }
        )
        
        assert response.status_code == 404


class TestReport:
    """Test report generation"""
    
    def test_generate_report(self):
        """Test report generation for analyzed piece"""
        # Upload and analyze
        fake_stl = b"solid test\nendsolid test"
        upload_response = client.post(
            "/api/upload",
            files={"file": ("test.stl", fake_stl, "application/octet-stream")}
        )
        piece_id = upload_response.json()["piece_id"]
        
        # Create and analyze
        img = np.random.randint(0, 256, (200, 200), dtype=np.uint8)
        _, buffer = cv2.imencode('.png', img)
        img_b64 = base64.b64encode(buffer).decode('utf-8')
        
        client.post(
            "/api/analyze",
            json={"piece_id": piece_id, "images": [img_b64]}
        )
        
        # Generate report
        report_response = client.post(
            "/api/report",
            json={
                "piece_id": piece_id,
                "notes": "Test notes"
            }
        )
        
        assert report_response.status_code == 200
        data = report_response.json()
        assert "report_path" in data


class TestValidation:
    """Test validation/rejection endpoints"""
    
    def test_validate_piece(self):
        """Test validating a piece"""
        # Upload first
        fake_stl = b"solid test\nendsolid test"
        upload_response = client.post(
            "/api/upload",
            files={"file": ("test.stl", fake_stl, "application/octet-stream")}
        )
        piece_id = upload_response.json()["piece_id"]
        
        # Validate
        validate_response = client.post(
            "/api/validate",
            json={
                "piece_id": piece_id,
                "status": "validated",
                "notes": "Looks good"
            }
        )
        
        assert validate_response.status_code == 200
        data = validate_response.json()
        assert data["status"] == "validated"
    
    def test_reject_piece(self):
        """Test rejecting a piece"""
        # Upload first
        fake_stl = b"solid test\nendsolid test"
        upload_response = client.post(
            "/api/upload",
            files={"file": ("test.stl", fake_stl, "application/octet-stream")}
        )
        piece_id = upload_response.json()["piece_id"]
        
        # Reject
        reject_response = client.post(
            "/api/reject",
            json={
                "piece_id": piece_id,
                "status": "rejected",
                "notes": "Defect found"
            }
        )
        
        assert reject_response.status_code == 200
        data = reject_response.json()
        assert data["status"] == "rejected"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
