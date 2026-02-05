#!/bin/bash
# Quick start script

echo "================================"
echo "NEU Quality Control Application"
echo "================================"
echo ""

# Check if Docker is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose not found!"
    echo "Please install Docker and Docker Compose first."
    exit 1
fi

echo "✅ Docker Compose found"
echo ""

# Create necessary directories
mkdir -p models data/uploads data/reports

echo "📦 Starting services..."
echo ""

# Start with Docker Compose
docker-compose up --build

echo ""
echo "================================"
echo "Services Started!"
echo "Frontend: http://localhost:3000"
echo "Backend:  http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo "================================"
