#!/usr/bin/env python3
"""
Start WebSocket Server with FIXED Hinglish Quality
"""

import os
import sys
import uvicorn

def start_fixed_websocket_server():
    """Start the WebSocket server with our fixed quality improvements"""
    print("🚀 Starting FIXED Hinglish WebSocket Server with OpenAI")
    print("=" * 60)
    print("✅ Natural TTS parameters")
    print("✅ Minimal audio processing")
    print("✅ Ultra-minimal text optimization")
    print("✅ Fixed realtime streaming")
    print("🤖 OpenAI GPT-3.5-turbo for Hinglish conversations")
    print("=" * 60)
      # Set environment
    os.environ["PYTHONPATH"] = os.getcwd()
    
    # Import and start server
    try:
        print("🌐 Server starting on http://localhost:8000")
        print("📱 WebSocket endpoint: ws://localhost:8000/ws")
        print("🎤 Voice cloning API ready with FIXED quality!")
        print("🤖 OpenAI GPT-3.5-turbo chatbot integrated!")
        
        uvicorn.run(
            "app.websocket_server:app",
            host="0.0.0.0",
            port=8000,
            log_level="info",
            reload=True  # Enable auto-reload for development
        )
        
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Server failed to start: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    start_fixed_websocket_server()
