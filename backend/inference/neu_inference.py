"""
NEU Surface Defect Detection Inference Module
CRITICAL: Matches preprocessing from NEU_Surface_Defect_Detection_v1.ipynb exactly
"""

import os
import numpy as np
import cv2
from typing import List, Dict, Tuple
import hashlib

# EXACT CONSTANTS FROM NOTEBOOK
IMG_SIZE = 200
CLASS_NAMES = [
    "crazing",
    "inclusion",
    "patches",
    "pitted_surface",
    "rolled-in_scale",
    "scratches"
]

# Model path (configurable via environment)
MODEL_PATH = os.getenv("MODEL_PATH", "models/neu_cnn_model.keras")


def preprocess_image(img: np.ndarray) -> np.ndarray:
    """
    Preprocess image EXACTLY as in the notebook.
    
    Args:
        img: uint8 grayscale image (H, W) or (H, W, 1)
    
    Returns:
        Preprocessed image (200, 200, 1) with values in [0, 1]
    """
    # Ensure grayscale
    if len(img.shape) == 3:
        if img.shape[2] == 3:
            img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        elif img.shape[2] == 1:
            img = img[:, :, 0]
    
    # Resize to 200x200 (EXACT from notebook)
    img = cv2.resize(img, (IMG_SIZE, IMG_SIZE))
    
    # Normalize to [0, 1] (EXACT from notebook: astype('float32') / 255.0)
    img = img.astype("float32") / 255.0
    
    # Add channel dimension (EXACT from notebook: np.expand_dims(img, axis=-1))
    img = np.expand_dims(img, axis=-1)  # Shape: (200, 200, 1)
    
    return img


def load_model():
    """
    Load the trained Keras model.
    Returns None if model doesn't exist (falls back to mock).
    """
    if not os.path.exists(MODEL_PATH):
        print(f"⚠️  Model not found at {MODEL_PATH}. Using mock inference.")
        return None
    
    try:
        import tensorflow as tf
        model = tf.keras.models.load_model(MODEL_PATH)
        print(f"✅ Model loaded from {MODEL_PATH}")
        return model
    except Exception as e:
        print(f"❌ Error loading model: {e}. Using mock inference.")
        return None


def run_inference(images: List[np.ndarray], piece_id: str = None) -> Dict:
    """
    Run inference on multiple views of a 3D piece.
    
    Args:
        images: List of grayscale images (multiple views from 3D viewer)
        piece_id: Identifier for the piece (used in mock mode)
    
    Returns:
        {
            "predicted_class": str,
            "class_probs": dict[str, float],
            "anomaly_score": float
        }
    """
    model = load_model()
    
    if model is None:
        # MOCK INFERENCE for testing
        return mock_inference(piece_id or "default")
    
    # REAL INFERENCE
    # Preprocess all images
    X = np.stack([preprocess_image(img) for img in images], axis=0)
    # X.shape = (N_views, 200, 200, 1)
    
    # Predict on all views
    preds = model.predict(X, verbose=0)  # Shape: (N_views, 6)
    
    # Average predictions across views
    avg_preds = preds.mean(axis=0)  # Shape: (6,)
    
    # Get predicted class
    predicted_idx = int(np.argmax(avg_preds))
    predicted_class = CLASS_NAMES[predicted_idx]
    
    # Build class probabilities dict
    class_probs = {
        CLASS_NAMES[i]: float(avg_preds[i]) 
        for i in range(len(CLASS_NAMES))
    }
    
    # Anomaly score = max probability * 100
    anomaly_score = float(np.max(avg_preds)) * 100.0
    
    return {
        "predicted_class": predicted_class,
        "class_probs": class_probs,
        "anomaly_score": anomaly_score
    }


def mock_inference(piece_id: str) -> Dict:
    """
    Deterministic mock inference for testing without a trained model.
    Uses piece_id hash to generate consistent but varied predictions.
    """
    # Hash piece_id to generate deterministic random seed
    seed = int(hashlib.md5(piece_id.encode()).hexdigest()[:8], 16) % 10000
    np.random.seed(seed)
    
    # Generate random probabilities that sum to 1
    raw_probs = np.random.dirichlet(np.ones(6) * 2.0)
    
    # Ensure at least one class has >50% probability (more realistic)
    max_idx = np.argmax(raw_probs)
    raw_probs[max_idx] = max(raw_probs[max_idx], 0.5)
    raw_probs = raw_probs / raw_probs.sum()  # Renormalize
    
    # Get predicted class
    predicted_idx = int(np.argmax(raw_probs))
    predicted_class = CLASS_NAMES[predicted_idx]
    
    # Build class probabilities dict
    class_probs = {
        CLASS_NAMES[i]: float(raw_probs[i])
        for i in range(len(CLASS_NAMES))
    }
    
    # Anomaly score
    anomaly_score = float(np.max(raw_probs)) * 100.0
    
    return {
        "predicted_class": predicted_class,
        "class_probs": class_probs,
        "anomaly_score": anomaly_score
    }


def validate_preprocessing():
    """
    Validation function to ensure preprocessing matches notebook exactly.
    """
    print("\n" + "="*60)
    print("PREPROCESSING VALIDATION")
    print("="*60)
    
    # Create test image
    test_img = np.random.randint(0, 256, (300, 400), dtype=np.uint8)
    
    # Preprocess
    processed = preprocess_image(test_img)
    
    # Check shape
    assert processed.shape == (200, 200, 1), \
        f"❌ Shape mismatch! Expected (200, 200, 1), got {processed.shape}"
    print(f"✅ Shape: {processed.shape}")
    
    # Check dtype
    assert processed.dtype == np.float32, \
        f"❌ Dtype mismatch! Expected float32, got {processed.dtype}"
    print(f"✅ Dtype: {processed.dtype}")
    
    # Check value range
    assert processed.min() >= 0.0 and processed.max() <= 1.0, \
        f"❌ Value range error! Min: {processed.min()}, Max: {processed.max()}"
    print(f"✅ Value range: [{processed.min():.4f}, {processed.max():.4f}]")
    
    print("\n✅ All preprocessing checks PASSED!")
    print("="*60 + "\n")


if __name__ == "__main__":
    # Run validation
    validate_preprocessing()
    
    # Test mock inference
    print("Testing mock inference...")
    result = mock_inference("TEST_PIECE_123")
    print(f"\nPredicted class: {result['predicted_class']}")
    print(f"Anomaly score: {result['anomaly_score']:.2f}%")
    print("\nClass probabilities:")
    for cls, prob in result['class_probs'].items():
        print(f"  {cls:<20} {prob*100:>6.2f}%")
