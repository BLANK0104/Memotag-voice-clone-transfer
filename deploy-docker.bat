@echo off
echo 🐳 Hinglish Voice Cloning - Docker Deployment Script
echo =====================================================

echo.
echo ⚠️  Checking Docker Desktop status...

REM Check if Docker is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Desktop is not running!
    echo.
    echo 🚀 Please start Docker Desktop manually:
    echo    1. Press Win + R
    echo    2. Type: "Docker Desktop"
    echo    3. Press Enter
    echo    4. Wait for Docker to start (green icon in system tray)
    echo    5. Run this script again
    echo.
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist ".env" (
    echo 📝 Creating .env file from template...
    copy .env.example .env
    echo ⚠️  Please edit .env file with your API keys before continuing!
    echo    Required: OPENAI_API_KEY, GEMINI_API_KEY, SUPABASE_URL, SUPABASE_KEY
    pause
)

REM Create necessary directories
echo 📁 Creating directories...
if not exist "generated" mkdir generated
if not exist "temp" mkdir temp
if not exist "logs" mkdir logs
if not exist "voices" mkdir voices
if not exist "models" mkdir models

REM Build Docker image
echo 🔨 Building Docker image...
docker build -t hinglish-voice-cloning:latest .

if %errorlevel% neq 0 (
    echo ❌ Docker build failed!
    exit /b 1
)

REM Stop existing container if running
echo 🛑 Stopping existing container...
docker stop hinglish-voice-app 2>nul
docker rm hinglish-voice-app 2>nul

REM Start new container
echo 🚀 Starting container...
docker-compose up -d

REM Wait for container to be ready
echo ⏳ Waiting for container to start...
timeout /t 15 /nobreak >nul

REM Health check
echo 🏥 Checking health...
curl -f http://localhost:8000/health >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Container is healthy!
    echo.
    echo 🌐 Application URLs:
    echo    Web Interface: http://localhost:8000
    echo    API Docs: http://localhost:8000/docs
    echo    Health Check: http://localhost:8000/health
    echo.
    echo 📊 Monitor with:
    echo    docker-compose logs -f
    echo    docker stats hinglish-voice-cloning
) else (
    echo ❌ Health check failed!
    echo 📋 Check logs with: docker-compose logs
    exit /b 1
)

echo 🎉 Deployment completed successfully!
pause
