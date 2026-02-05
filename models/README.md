# Models Directory

Place your trained NEU Surface Defect Detection model here.

## Quick Start

1. Train model using `NEU_Surface_Defect_Detection_v1.ipynb`
2. Save model as `neu_cnn_model.h5` or `neu_cnn_model.keras`
3. Copy to this directory:
   ```bash
   cp /path/to/neu_cnn_model.h5 ./models/
   ```
4. Restart backend

## Model Requirements

- **Input**: (None, 200, 200, 1) - Grayscale images
- **Output**: (None, 6) - 6 class probabilities
- **Format**: Keras .h5 or .keras
- **Classes**:
  1. crazing
  2. inclusion
  3. patches
  4. pitted_surface
  5. rolled-in_scale
  6. scratches

## Without a Model

The application works in mock mode without a real model:
- Uses deterministic hash-based predictions
- Perfect for testing and development
- Returns valid probability distributions

See `MODEL_INTEGRATION.md` for complete integration guide.
