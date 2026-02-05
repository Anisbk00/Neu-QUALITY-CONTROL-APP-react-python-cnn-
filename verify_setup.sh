#!/bin/bash
# Verification script to check project setup

echo "========================================"
echo "NEU Quality Control - Setup Verification"
echo "========================================"
echo ""

ERRORS=0

# Check directories
echo "📁 Checking directory structure..."
REQUIRED_DIRS=(
    "frontend/src/components"
    "frontend/src/utils"
    "frontend/src/types"
    "backend/app"
    "backend/inference"
    "backend/tests"
    "models"
    "data/uploads"
    "data/reports"
    "docker"
)

for dir in "${REQUIRED_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        echo "  ✅ $dir"
    else
        echo "  ❌ $dir - MISSING!"
        ERRORS=$((ERRORS + 1))
    fi
done

echo ""
echo "📄 Checking critical files..."

REQUIRED_FILES=(
    "backend/inference/neu_inference.py"
    "backend/app/main.py"
    "backend/requirements.txt"
    "frontend/package.json"
    "frontend/src/App.tsx"
    "frontend/src/components/Viewer3D.tsx"
    "docker-compose.yml"
    "README.md"
    "MODEL_INTEGRATION.md"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file - MISSING!"
        ERRORS=$((ERRORS + 1))
    fi
done

echo ""
echo "🔍 Checking preprocessing implementation..."

if grep -q "IMG_SIZE = 200" backend/inference/neu_inference.py; then
    echo "  ✅ IMG_SIZE = 200"
else
    echo "  ❌ IMG_SIZE not set correctly!"
    ERRORS=$((ERRORS + 1))
fi

if grep -q "COLOR_RGB2GRAY\|IMREAD_GRAYSCALE" backend/inference/neu_inference.py; then
    echo "  ✅ Grayscale conversion"
else
    echo "  ❌ Grayscale conversion not implemented!"
    ERRORS=$((ERRORS + 1))
fi

if grep -q "astype.*float32.*/ 255" backend/inference/neu_inference.py; then
    echo "  ✅ Normalization: float32 / 255.0"
else
    echo "  ❌ Normalization incorrect!"
    ERRORS=$((ERRORS + 1))
fi

if grep -q "np.expand_dims.*axis=-1" backend/inference/neu_inference.py; then
    echo "  ✅ Channel dimension: np.expand_dims"
else
    echo "  ❌ Channel dimension not added!"
    ERRORS=$((ERRORS + 1))
fi

echo ""
echo "🎯 Checking class names..."

CLASSES=("crazing" "inclusion" "patches" "pitted_surface" "rolled-in_scale" "scratches")
CLASS_CHECK=0

for cls in "${CLASSES[@]}"; do
    if grep -q "\"$cls\"" backend/inference/neu_inference.py; then
        CLASS_CHECK=$((CLASS_CHECK + 1))
    fi
done

if [ $CLASS_CHECK -eq 6 ]; then
    echo "  ✅ All 6 classes present"
else
    echo "  ❌ Missing classes (found $CLASS_CHECK/6)!"
    ERRORS=$((ERRORS + 1))
fi

echo ""
echo "🧪 Checking test files..."

if [ -f "backend/tests/test_inference.py" ]; then
    TEST_COUNT=$(grep -c "def test_" backend/tests/test_inference.py)
    echo "  ✅ test_inference.py ($TEST_COUNT tests)"
else
    echo "  ❌ test_inference.py missing!"
    ERRORS=$((ERRORS + 1))
fi

if [ -f "backend/tests/test_api.py" ]; then
    TEST_COUNT=$(grep -c "def test_" backend/tests/test_api.py)
    echo "  ✅ test_api.py ($TEST_COUNT tests)"
else
    echo "  ❌ test_api.py missing!"
    ERRORS=$((ERRORS + 1))
fi

echo ""
echo "🐳 Checking Docker configuration..."

if [ -f "docker-compose.yml" ]; then
    if grep -q "backend:" docker-compose.yml && grep -q "frontend:" docker-compose.yml; then
        echo "  ✅ Docker Compose configured"
    else
        echo "  ❌ Docker Compose incomplete!"
        ERRORS=$((ERRORS + 1))
    fi
else
    echo "  ❌ docker-compose.yml missing!"
    ERRORS=$((ERRORS + 1))
fi

echo ""
echo "📚 Checking documentation..."

DOC_FILES=("README.md" "MODEL_INTEGRATION.md" "QUICKSTART.md")
for doc in "${DOC_FILES[@]}"; do
    if [ -f "$doc" ]; then
        LINES=$(wc -l < "$doc")
        echo "  ✅ $doc ($LINES lines)"
    else
        echo "  ❌ $doc missing!"
        ERRORS=$((ERRORS + 1))
    fi
done

echo ""
echo "========================================"
if [ $ERRORS -eq 0 ]; then
    echo "✅ ALL CHECKS PASSED!"
    echo "========================================"
    echo ""
    echo "Next steps:"
    echo "  1. docker-compose up --build"
    echo "  2. Open http://localhost:3000"
    echo "  3. See QUICKSTART.md for usage"
    exit 0
else
    echo "❌ FOUND $ERRORS ERROR(S)"
    echo "========================================"
    echo ""
    echo "Please fix the errors above before proceeding."
    exit 1
fi
