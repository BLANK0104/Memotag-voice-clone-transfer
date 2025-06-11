#!/bin/bash
# Docker deployment script for Windows (Git Bash/WSL)

echo "🐳 Starting Hinglish Voice Cloning Docker Deployment"
echo "=================================================="

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop."
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your API keys before continuing!"
    echo "   Required: OPENAI_API_KEY, GEMINI_API_KEY, SUPABASE_URL, SUPABASE_KEY"
    read -p "Press Enter after updating .env file..."
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p generated temp logs voices models

# Build Docker image
echo "🔨 Building Docker image..."
docker build -t hinglish-voice-cloning:latest .

if [ $? -ne 0 ]; then
    echo "❌ Docker build failed!"
    exit 1
fi

# Stop existing container if running
echo "🛑 Stopping existing container..."
docker stop hinglish-voice-app 2>/dev/null || true
docker rm hinglish-voice-app 2>/dev/null || true

# Start new container
echo "🚀 Starting container..."
docker-compose up -d

# Wait for container to be ready
echo "⏳ Waiting for container to start..."
sleep 10

# Health check
echo "🏥 Checking health..."
if curl -f http://localhost:8000/health >/dev/null 2>&1; then
    echo "✅ Container is healthy!"
    echo ""
    echo "🌐 Application URLs:"
    echo "   Web Interface: http://localhost:8000"
    echo "   API Docs: http://localhost:8000/docs"
    echo "   Health Check: http://localhost:8000/health"
    echo ""
    echo "📊 Monitor with:"
    echo "   docker-compose logs -f"
    echo "   docker stats hinglish-voice-cloning"
else
    echo "❌ Health check failed!"
    echo "📋 Check logs with: docker-compose logs"
    exit 1
fi

echo "🎉 Deployment completed successfully!"
