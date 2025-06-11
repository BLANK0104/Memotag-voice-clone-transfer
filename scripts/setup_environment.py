#!/usr/bin/env python3
"""
Environment setup script for Hinglish Voice Cloning Server
Creates a .env file with the required environment variables
"""

import os
from pathlib import Path

def create_env_file():
    """Create a .env file template"""
    env_content = """# Hinglish Voice Cloning Server Environment Variables
# Copy this file to .env and fill in your actual values

# Required: Supabase Database Configuration
SUPABASE_URL=your_supabase_project_url_here
SUPABASE_KEY=your_supabase_anon_key_here

# Optional: Gemini AI API Key (for chatbot functionality)
# Get this from: https://makersuite.google.com/app/apikey
API_KEY_GEMINI=your_gemini_api_key_here

# Optional: Additional Configuration
# CORS_ORIGINS=http://localhost:3000,http://localhost:8080
# MAX_FILE_SIZE=50000000
# VOICE_STORAGE_PATH=voices
"""
    
    env_file = Path(".env.example")
    with open(env_file, "w", encoding="utf-8") as f:
        f.write(env_content)
    
    print(f"✅ Created {env_file}")
    print("💡 Copy this to .env and fill in your actual values")

def check_existing_env():
    """Check if .env file exists and what's configured"""
    env_file = Path(".env")
    
    if not env_file.exists():
        print("❌ No .env file found")
        return False
    
    print("✅ Found .env file")
    
    # Check what's configured
    configured = []
    with open(env_file, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    for line in lines:
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key = line.split("=")[0]
            value = line.split("=", 1)[1]
            if value and value != "your_" + key.lower() + "_here":
                configured.append(key)
    
    if configured:
        print(f"📝 Configured variables: {', '.join(configured)}")
    else:
        print("⚠️  No variables are configured in .env file")
    
    return True

def main():
    """Main setup function"""
    print("🔧 Hinglish Voice Cloning Server - Environment Setup")
    print("=" * 55)
    
    # Check current environment
    print("🔍 Checking current environment...")
    
    has_env = check_existing_env()
    
    if not has_env:
        print("\n📝 Creating environment template...")
        create_env_file()
    
    print(f"\n🌐 Current environment variables:")
    env_vars = ['SUPABASE_URL', 'SUPABASE_KEY', 'API_KEY_GEMINI']
    
    for var in env_vars:
        value = os.getenv(var)
        if value:
            # Show only first/last few characters for security
            if len(value) > 10:
                masked = value[:4] + "..." + value[-4:]
            else:
                masked = "***"
            print(f"   ✅ {var}: {masked}")
        else:
            print(f"   ❌ {var}: Not set")
    
    print(f"\n📋 Setup Instructions:")
    print(f"1. Create a Supabase project at https://supabase.com")
    print(f"2. Get your project URL and anon key from the dashboard")
    print(f"3. (Optional) Get a Gemini API key from https://makersuite.google.com/app/apikey")
    print(f"4. Copy .env.example to .env and fill in your values")
    print(f"5. Run: python start_server.py")
    
    print(f"\n" + "=" * 55)

if __name__ == "__main__":
    main()
