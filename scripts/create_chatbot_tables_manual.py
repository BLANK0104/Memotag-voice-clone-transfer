"""
Create chatbot tables using direct SQL execution
"""

import os
import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.append(str(Path(__file__).parent / "app"))

try:
    from database import VoiceDatabase
except ImportError:
    sys.path.append("app")
    from database import VoiceDatabase
from dotenv import load_dotenv

load_dotenv()

def create_chatbot_tables():
    """Create the chatbot tables using the database connection"""
    
    try:
        # Initialize database connection
        db = VoiceDatabase()
        print("✅ Connected to Supabase database")
        
        print("\n🎯 MANUAL TABLE CREATION REQUIRED")
        print("=" * 60)
        print("Please create these tables manually in your Supabase dashboard:")
        print("1. Go to your Supabase dashboard")
        print("2. Navigate to SQL Editor")
        print("3. Copy and execute the following SQL:")
        print()
        
        full_sql = """
-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create conversations table
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id TEXT NOT NULL,
    title TEXT NOT NULL DEFAULT 'New Conversation',
    language TEXT DEFAULT 'hinglish',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT TRUE
);

-- Create messages table
CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    audio_path TEXT,
    voice_used TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

-- Create audio_transcripts table
CREATE TABLE IF NOT EXISTS audio_transcripts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    message_id UUID NOT NULL REFERENCES messages(id) ON DELETE CASCADE,
    transcript TEXT NOT NULL,
    confidence FLOAT DEFAULT 0.0,
    language_detected TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations(user_id);
CREATE INDEX IF NOT EXISTS idx_conversations_created_at ON conversations(created_at);
CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at);
CREATE INDEX IF NOT EXISTS idx_audio_transcripts_message_id ON audio_transcripts(message_id);

-- Enable Row Level Security (optional)
-- ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE audio_transcripts ENABLE ROW LEVEL SECURITY;
"""
        
        print(full_sql)
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = create_chatbot_tables()
    if success:
        print("\n✅ Table creation SQL provided! Please execute manually in Supabase.")
    else:
        print("\n❌ Failed to generate table creation SQL")
        sys.exit(1)