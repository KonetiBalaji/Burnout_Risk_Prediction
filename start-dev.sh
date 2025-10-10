#!/bin/bash

# Development startup script for Burnout Risk Prediction System
# Created by Balaji Koneti

echo "🚀 Starting Burnout Risk Prediction System in Development Mode"
echo "=============================================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop first."
    exit 1
fi

# Check if .env file exists
if [ ! -f "backend/.env" ]; then
    echo "⚠️  No .env file found. Creating from example..."
    cp backend/env.example backend/.env
    echo "📝 Please edit backend/.env with your configuration"
fi

# Start services
echo "🐳 Starting Docker services..."
docker-compose up --build

echo "✅ Development environment started!"
echo "🌐 Frontend: http://localhost:5173"
echo "🔧 Backend API: http://localhost:3000"
echo "📊 ML Service: http://localhost:8000"
echo "🗄️  MongoDB: mongodb://localhost:27017"
