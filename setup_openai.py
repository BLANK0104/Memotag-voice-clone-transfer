"""
Configuration script to set up OpenAI API key for the Hinglish Voice Cloning System
"""

import os
from pathlib import Path

def setup_openai_key():
    """Set up OpenAI API key in environment"""
    
    # The OpenAI API key provided by the user
    api_key = "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"
    
    # Set environment variable for current session
    os.environ['OPENAI_API_KEY'] = api_key
    
    # Create/update .env file
    env_file = Path('.env')
    
    # Read existing .env content
    env_content = ""
    if env_file.exists():
        with open(env_file, 'r') as f:
            lines = f.readlines()
        
        # Remove existing OPENAI_API_KEY if present
        lines = [line for line in lines if not line.startswith('OPENAI_API_KEY=')]
        env_content = ''.join(lines)
    
    # Add OpenAI API key
    with open(env_file, 'w') as f:
        f.write(env_content)
        if env_content and not env_content.endswith('\n'):
            f.write('\n')
        f.write(f'OPENAI_API_KEY={api_key}\n')
    
    print("✅ OpenAI API key configured successfully!")
    print("✅ Environment variable OPENAI_API_KEY set")
    print("✅ .env file updated")
    print("\n🤖 Your Hinglish chatbot is now ready to use OpenAI GPT-3.5-turbo!")
    
    return True

if __name__ == "__main__":
    setup_openai_key()
