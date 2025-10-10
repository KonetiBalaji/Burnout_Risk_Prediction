@echo off
REM Development startup script for Burnout Risk Prediction System
REM Created by Balaji Koneti

echo 🚀 Starting Burnout Risk Prediction System in Development Mode
echo ==============================================================

REM Check if Docker is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not running. Please start Docker Desktop first.
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist "backend\.env" (
    echo ⚠️  No .env file found. Creating from example...
    copy "backend\env.example" "backend\.env"
    echo 📝 Please edit backend\.env with your configuration
)

REM Start services
echo 🐳 Starting Docker services...
docker-compose up --build

echo ✅ Development environment started!
echo 🌐 Frontend: http://localhost:5173
echo 🔧 Backend API: http://localhost:3000
echo 📊 ML Service: http://localhost:8000
echo 🗄️  MongoDB: mongodb://localhost:27017
pause
