-- SQL code to create the voice_profiles table in Supabase
-- Run this in your Supabase SQL editor

-- Create the voice_profiles table (matches the database.py code)
CREATE TABLE IF NOT EXISTS public.voice_profiles (
    id BIGSERIAL PRIMARY KEY,
    voice_name VARCHAR(255) NOT NULL UNIQUE,
    voice_features JSONB NOT NULL,
    audio_path VARCHAR(500),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_voice_profiles_voice_name ON public.voice_profiles(voice_name);
CREATE INDEX IF NOT EXISTS idx_voice_profiles_created_at ON public.voice_profiles(created_at);
CREATE INDEX IF NOT EXISTS idx_voice_profiles_updated_at ON public.voice_profiles(updated_at);

-- Create trigger function to automatically update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to automatically update updated_at on row updates
CREATE TRIGGER update_voice_profiles_updated_at 
    BEFORE UPDATE ON public.voice_profiles 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Enable Row Level Security (RLS)
ALTER TABLE public.voice_profiles ENABLE ROW LEVEL SECURITY;

-- Create policy to allow all operations (adjust as needed for your security requirements)
CREATE POLICY "Allow all operations on voice_profiles" ON public.voice_profiles
    FOR ALL USING (true);

-- Grant permissions to authenticated users and anonymous users
GRANT ALL ON public.voice_profiles TO authenticated;
GRANT ALL ON public.voice_profiles TO anon;
GRANT USAGE, SELECT ON SEQUENCE voice_profiles_id_seq TO authenticated;
GRANT USAGE, SELECT ON SEQUENCE voice_profiles_id_seq TO anon;

-- Add comments for documentation
COMMENT ON TABLE public.voice_profiles IS 'Stores voice profiles for voice cloning application';
COMMENT ON COLUMN public.voice_profiles.voice_name IS 'Unique name identifier for the voice';
COMMENT ON COLUMN public.voice_profiles.voice_features IS 'JSON data containing extracted voice features';
COMMENT ON COLUMN public.voice_profiles.audio_path IS 'Path to the audio file used for voice cloning';
COMMENT ON COLUMN public.voice_profiles.metadata IS 'Additional metadata like description, language, file info';

-- Verify table creation
SELECT 'voice_profiles table created successfully' as status;