#!/usr/bin/env python3
"""
Voice Cloning WebSocket Server
Main server startup script for the Hinglish Voice Cloning application
"""

import os
import sys
import uvicorn
from pathlib import Path

def start_voice_cloning_server():
    """Start the Voice Cloning WebSocket server with all features"""
    print("🚀 Starting Hinglish Voice Cloning Server")
    print("=" * 60)
    print("🎤 Voice Cloning with Hinglish Support")
    print("🤖 AI Chatbots: OpenAI GPT-3.5-turbo & Google Gemini")
    print("🔄 Hinglish to Hindi TTS conversion")
    print("✅ Natural TTS parameters")
    print("✅ Minimal audio processing")
    print("✅ Ultra-minimal text optimization")
    print("✅ Fixed realtime streaming")
    print("✅ WebSocket real-time communication")
    print("=" * 60)
      # Set environment variables
    os.environ["PYTHONPATH"] = os.getcwd()
    
    # Get port from environment variable (for Render deployment) or default to 8000
    port = int(os.environ.get("PORT", 8000))
    
    # Ensure required directories exist
    required_dirs = ["generated", "temp", "voices", "logs"]
    for dir_name in required_dirs:
        os.makedirs(dir_name, exist_ok=True)
      # Check if static files exist
    static_path = Path("static")
    if not static_path.exists():
        print("⚠️  Warning: static directory not found!")
    elif not (static_path / "index.html").exists():
        print("⚠️  Warning: static/index.html not found!")
    
    # Start server
    try:
        print("\n🌐 Server Configuration:")
        print(f"   URL: http://localhost:{port}")
        print(f"   WebSocket: ws://localhost:{port}/ws")
        print(f"   API Docs: http://localhost:{port}/docs")
        print("\n🎯 Features Available:")
        print("   • Voice Upload & Cloning")
        print("   • Hinglish AI Chatbot")
        print("   • Real-time Speech Generation")
        print("   • Speech-to-Text")
        print("   • Conversation Management")
        print("\n⚡ Starting server...")
        uvicorn.run(
            "app.websocket_server:app",
            host="0.0.0.0",
            port=port,  # Use dynamic port
            log_level="info",
            reload=False,  # Disable auto-reload for production Docker deployment
            access_log=True
        )
        
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Server failed to start: {e}")
        print("\n🔍 Troubleshooting:")
        print(f"   1. Check if port {port} is available")
        print("   2. Ensure all dependencies are installed: pip install -r requirements.txt")
        print("   3. Check environment variables (API keys)")
        print("   4. Verify app/websocket_server.py exists")
        import traceback
        traceback.print_exc()

def check_dependencies():
    """Check if required dependencies are available"""
    required_modules = [
        "fastapi", "uvicorn", "websockets", "python-multipart",
        "numpy", "scipy", "librosa", "soundfile", "torch"
    ]
    
    missing_modules = []
    for module in required_modules:
        try:
            __import__(module.replace("-", "_"))
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        print(f"⚠️  Missing dependencies: {', '.join(missing_modules)}")
        print("   Run: pip install -r requirements.txt")
        return False
    return True

if __name__ == "__main__":
    print("🔧 Checking dependencies...")
    if check_dependencies():
        print("✅ All dependencies available")
        start_voice_cloning_server()
    else:
        print("❌ Please install missing dependencies first")
        sys.exit(1)
