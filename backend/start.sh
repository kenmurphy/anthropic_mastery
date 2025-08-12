#!/bin/bash

# Claude Backend Quick Start Script

echo "🚀 Starting Claude Backend..."
echo "================================"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Start MongoDB
echo "📦 Starting MongoDB container..."
docker-compose up -d

# Wait for MongoDB to be ready
echo "⏳ Waiting for MongoDB to be ready..."
sleep 10

# Check if MongoDB is running
if ! docker ps | grep -q claude_mongodb; then
    echo "❌ Failed to start MongoDB container"
    exit 1
fi

echo "✅ MongoDB is running"

# Check if Python dependencies are installed
if [ ! -d "venv" ]; then
    echo "🐍 Creating Python virtual environment..."
    python3 -m venv venv
fi

echo "📦 Activating virtual environment and installing dependencies..."
source venv/bin/activate
pip install -r requirements.txt

# Start the Flask application
echo "🌐 Starting Flask application..."
echo "   Access the API at: http://localhost:10000"
echo "   Press Ctrl+C to stop the server"
echo ""

python app.py
