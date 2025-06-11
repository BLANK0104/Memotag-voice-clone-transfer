-- Chatbot Tables for Hinglish Voice Chatbot
-- Created for Supabase PostgreSQL database

-- Enable Row Level Security (RLS) and UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Table 1: Conversations
-- Stores conversation sessions between users and the chatbot
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

-- Table 2: Messages
-- Stores individual messages within conversations
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

-- Table 3: Audio Transcripts
-- Stores speech-to-text transcription results
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
CREATE INDEX IF NOT EXISTS idx_conversations_active ON conversations(is_active);

CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_messages_role ON messages(role);
CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at);

CREATE INDEX IF NOT EXISTS idx_audio_transcripts_message_id ON audio_transcripts(message_id);
CREATE INDEX IF NOT EXISTS idx_audio_transcripts_confidence ON audio_transcripts(confidence);

-- Enable Row Level Security
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE audio_transcripts ENABLE ROW LEVEL SECURITY;

-- RLS Policies for conversations table
DROP POLICY IF EXISTS "Users can view their own conversations" ON conversations;
CREATE POLICY "Users can view their own conversations" 
ON conversations FOR SELECT 
USING (auth.uid()::text = user_id OR user_id = 'anonymous');

DROP POLICY IF EXISTS "Users can insert their own conversations" ON conversations;
CREATE POLICY "Users can insert their own conversations" 
ON conversations FOR INSERT 
WITH CHECK (auth.uid()::text = user_id OR user_id = 'anonymous');

DROP POLICY IF EXISTS "Users can update their own conversations" ON conversations;
CREATE POLICY "Users can update their own conversations" 
ON conversations FOR UPDATE 
USING (auth.uid()::text = user_id OR user_id = 'anonymous');

DROP POLICY IF EXISTS "Users can delete their own conversations" ON conversations;
CREATE POLICY "Users can delete their own conversations" 
ON conversations FOR DELETE 
USING (auth.uid()::text = user_id OR user_id = 'anonymous');

-- RLS Policies for messages table
DROP POLICY IF EXISTS "Users can view messages from their conversations" ON messages;
CREATE POLICY "Users can view messages from their conversations" 
ON messages FOR SELECT 
USING (
    conversation_id IN (
        SELECT id FROM conversations 
        WHERE auth.uid()::text = user_id OR user_id = 'anonymous'
    )
);

DROP POLICY IF EXISTS "Users can insert messages to their conversations" ON messages;
CREATE POLICY "Users can insert messages to their conversations" 
ON messages FOR INSERT 
WITH CHECK (
    conversation_id IN (
        SELECT id FROM conversations 
        WHERE auth.uid()::text = user_id OR user_id = 'anonymous'
    )
);

DROP POLICY IF EXISTS "Users can update messages in their conversations" ON messages;
CREATE POLICY "Users can update messages in their conversations" 
ON messages FOR UPDATE 
USING (
    conversation_id IN (
        SELECT id FROM conversations 
        WHERE auth.uid()::text = user_id OR user_id = 'anonymous'
    )
);

DROP POLICY IF EXISTS "Users can delete messages from their conversations" ON messages;
CREATE POLICY "Users can delete messages from their conversations" 
ON messages FOR DELETE 
USING (
    conversation_id IN (
        SELECT id FROM conversations 
        WHERE auth.uid()::text = user_id OR user_id = 'anonymous'
    )
);

-- RLS Policies for audio_transcripts table
DROP POLICY IF EXISTS "Users can view transcripts from their messages" ON audio_transcripts;
CREATE POLICY "Users can view transcripts from their messages" 
ON audio_transcripts FOR SELECT 
USING (
    message_id IN (
        SELECT m.id FROM messages m
        JOIN conversations c ON m.conversation_id = c.id
        WHERE auth.uid()::text = c.user_id OR c.user_id = 'anonymous'
    )
);

DROP POLICY IF EXISTS "Users can insert transcripts for their messages" ON audio_transcripts;
CREATE POLICY "Users can insert transcripts for their messages" 
ON audio_transcripts FOR INSERT 
WITH CHECK (
    message_id IN (
        SELECT m.id FROM messages m
        JOIN conversations c ON m.conversation_id = c.id
        WHERE auth.uid()::text = c.user_id OR c.user_id = 'anonymous'
    )
);

DROP POLICY IF EXISTS "Users can update transcripts for their messages" ON audio_transcripts;
CREATE POLICY "Users can update transcripts for their messages" 
ON audio_transcripts FOR UPDATE 
USING (
    message_id IN (
        SELECT m.id FROM messages m
        JOIN conversations c ON m.conversation_id = c.id
        WHERE auth.uid()::text = c.user_id OR c.user_id = 'anonymous'
    )
);

DROP POLICY IF EXISTS "Users can delete transcripts from their messages" ON audio_transcripts;
CREATE POLICY "Users can delete transcripts from their messages" 
ON audio_transcripts FOR DELETE 
USING (
    message_id IN (
        SELECT m.id FROM messages m
        JOIN conversations c ON m.conversation_id = c.id
        WHERE auth.uid()::text = c.user_id OR c.user_id = 'anonymous'
    )
);

-- Create function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger for conversations table
DROP TRIGGER IF EXISTS update_conversations_updated_at ON conversations;
CREATE TRIGGER update_conversations_updated_at
    BEFORE UPDATE ON conversations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();