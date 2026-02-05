"""
Tests for NEU inference module
"""

import pytest
import numpy as np
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from inference.neu_inference import (
    preprocess_image,
    run_inference,
    mock_inference,
    CLASS_NAMES,
    IMG_SIZE
)


class TestPreprocessing:
    """Test preprocessing matches notebook exactly"""
    
    def test_output_shape(self):
        """Test that output shape is exactly (200, 200, 1)"""
        # Test with various input sizes
        test_sizes = [(100, 100), (300, 400), (200, 200)]
        
        for size in test_sizes:
            img = np.random.randint(0, 256, size, dtype=np.uint8)
            processed = preprocess_image(img)
            
            assert processed.shape == (IMG_SIZE, IMG_SIZE, 1), \
                f"Expected shape (200, 200, 1), got {processed.shape}"
    
    def test_dtype(self):
        """Test output dtype is float32"""
        img = np.random.randint(0, 256, (100, 100), dtype=np.uint8)
        processed = preprocess_image(img)
        
        assert processed.dtype == np.float32, \
            f"Expected dtype float32, got {processed.dtype}"
    
    def test_value_range(self):
        """Test values are normalized to [0, 1]"""
        img = np.random.randint(0, 256, (100, 100), dtype=np.uint8)
        processed = preprocess_image(img)
        
        assert processed.min() >= 0.0, f"Min value {processed.min()} < 0"
        assert processed.max() <= 1.0, f"Max value {processed.max()} > 1"
    
    def test_grayscale_conversion(self):
        """Test RGB to grayscale conversion"""
        # Create RGB image
        img_rgb = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
        processed = preprocess_image(img_rgb)
        
        # Should still produce (200, 200, 1)
        assert processed.shape == (IMG_SIZE, IMG_SIZE, 1)
    
    def test_normalization(self):
        """Test that normalization is /255.0"""
        # Create image with known values
        img = np.full((100, 100), 255, dtype=np.uint8)
        processed = preprocess_image(img)
        
        # Should be approximately 1.0
        assert np.allclose(processed, 1.0, atol=0.01)
        
        # Test with 0
        img = np.zeros((100, 100), dtype=np.uint8)
        processed = preprocess_image(img)
        assert np.allclose(processed, 0.0, atol=0.01)


class TestMockInference:
    """Test mock inference behavior"""
    
    def test_returns_valid_structure(self):
        """Test mock inference returns correct structure"""
        result = mock_inference("TEST_PIECE")
        
        assert "predicted_class" in result
        assert "class_probs" in result
        assert "anomaly_score" in result
    
    def test_predicted_class_valid(self):
        """Test predicted class is one of CLASS_NAMES"""
        result = mock_inference("TEST_PIECE")
        
        assert result["predicted_class"] in CLASS_NAMES
    
    def test_probabilities_sum_to_one(self):
        """Test class probabilities sum to approximately 1.0"""
        result = mock_inference("TEST_PIECE")
        
        prob_sum = sum(result["class_probs"].values())
        assert np.isclose(prob_sum, 1.0, atol=0.01)
    
    def test_all_classes_present(self):
        """Test all classes have probabilities"""
        result = mock_inference("TEST_PIECE")
        
        assert len(result["class_probs"]) == len(CLASS_NAMES)
        for cls in CLASS_NAMES:
            assert cls in result["class_probs"]
    
    def test_deterministic(self):
        """Test same piece_id gives same results"""
        result1 = mock_inference("TEST_PIECE_123")
        result2 = mock_inference("TEST_PIECE_123")
        
        assert result1["predicted_class"] == result2["predicted_class"]
        assert result1["anomaly_score"] == result2["anomaly_score"]
    
    def test_anomaly_score_range(self):
        """Test anomaly score is in [0, 100]"""
        result = mock_inference("TEST_PIECE")
        
        assert 0 <= result["anomaly_score"] <= 100


class TestRunInference:
    """Test run_inference with multiple views"""
    
    def test_single_view(self):
        """Test inference with single view"""
        img = np.random.randint(0, 256, (200, 200), dtype=np.uint8)
        result = run_inference([img], piece_id="TEST")
        
        assert "predicted_class" in result
        assert result["predicted_class"] in CLASS_NAMES
    
    def test_multiple_views(self):
        """Test inference with multiple views"""
        images = [
            np.random.randint(0, 256, (200, 200), dtype=np.uint8)
            for _ in range(5)
        ]
        result = run_inference(images, piece_id="TEST")
        
        assert "predicted_class" in result
        assert len(result["class_probs"]) == len(CLASS_NAMES)
    
    def test_different_sizes(self):
        """Test inference with different image sizes"""
        images = [
            np.random.randint(0, 256, (100, 150), dtype=np.uint8),
            np.random.randint(0, 256, (300, 400), dtype=np.uint8),
            np.random.randint(0, 256, (200, 200), dtype=np.uint8),
        ]
        result = run_inference(images, piece_id="TEST")
        
        assert "predicted_class" in result


class TestConstants:
    """Test that constants match notebook"""
    
    def test_img_size(self):
        """Test IMG_SIZE is 200"""
        assert IMG_SIZE == 200
    
    def test_class_names(self):
        """Test CLASS_NAMES match notebook"""
        expected = [
            "crazing",
            "inclusion",
            "patches",
            "pitted_surface",
            "rolled-in_scale",
            "scratches"
        ]
        assert CLASS_NAMES == expected
    
    def test_num_classes(self):
        """Test we have 6 classes"""
        assert len(CLASS_NAMES) == 6


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
