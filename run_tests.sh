#!/bin/bash
# Run all tests

echo "================================"
echo "Running Backend Tests"
echo "================================"

cd backend

# Run preprocessing tests
echo ""
echo "→ Testing Preprocessing..."
pytest tests/test_inference.py::TestPreprocessing -v

# Run mock inference tests
echo ""
echo "→ Testing Mock Inference..."
pytest tests/test_inference.py::TestMockInference -v

# Run real inference tests
echo ""
echo "→ Testing Run Inference..."
pytest tests/test_inference.py::TestRunInference -v

# Run constants tests
echo ""
echo "→ Testing Constants..."
pytest tests/test_inference.py::TestConstants -v

# Run API tests
echo ""
echo "→ Testing API Endpoints..."
pytest tests/test_api.py -v

echo ""
echo "================================"
echo "All Tests Complete!"
echo "================================"
