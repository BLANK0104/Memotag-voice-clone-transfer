"""
Configuration management for Voice Cloning Application
"""

import os
from dotenv import load_dotenv
from typing import Dict, Any

# Load environment variables
load_dotenv()

class Config:
    """Application configuration"""
    
    # API Settings
    API_HOST = os.getenv("APP_HOST", "localhost")
    API_PORT = int(os.getenv("APP_PORT", 8000))
    
    # Model Settings
    MODEL_NAME = os.getenv("MODEL_NAME", "tts_models/multilingual/multi-dataset/xtts_v2")
    DEVICE = "cuda" if os.getenv("USE_GPU", "true").lower() == "true" else "cpu"
    
    # Audio Settings
    SAMPLE_RATE = int(os.getenv("SAMPLE_RATE", 22050))
    MAX_AUDIO_LENGTH = int(os.getenv("MAX_AUDIO_LENGTH", 300))  # seconds
    MIN_AUDIO_LENGTH = 3  # seconds
    SUPPORTED_FORMATS = ['wav', 'mp3', 'm4a', 'flac', 'ogg']
    
    # Directory Settings
    VOICE_SAMPLES_DIR = os.getenv("VOICE_SAMPLES_DIR", "./voices")
    GENERATED_DIR = os.getenv("GENERATED_DIR", "./generated")
    MODELS_DIR = "./models"
    TEMP_DIR = "./temp"
    
    # Database Settings
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    USE_LOCAL_DB = not bool(SUPABASE_URL and SUPABASE_KEY)
    LOCAL_DB_PATH = "local_voice_db.json"
    
    # WebSocket Settings
    WS_PORT = int(os.getenv("WS_PORT", 8001))
    MAX_CONNECTIONS = 100
    
    # Security Settings
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    ALLOWED_ORIGINS = ["*"]  # In production, specify actual origins
    
    # Voice Processing Settings
    VOICE_VALIDATION = {
        "min_duration": 3,
        "max_duration": 30,
        "min_sample_rate": 16000,
        "max_file_size": MAX_FILE_SIZE,
        "required_rms_min": 0.01,
        "required_rms_max": 0.8,
        "max_silence_ratio": 0.3
    }
    
    # TTS Generation Settings
    TTS_CONFIG = {
        "temperature": 0.75,
        "length_penalty": 1.0,
        "repetition_penalty": 5.0,
        "top_k": 50,
        "top_p": 0.85,
        "speed": 1.0
    }
    
    # Supported Languages
    SUPPORTED_LANGUAGES = {
        "hi": "Hindi",
        "en": "English",
        "es": "Spanish",
        "fr": "French",
        "de": "German",
        "it": "Italian",
        "pt": "Portuguese",
        "pl": "Polish",
        "tr": "Turkish",
        "ru": "Russian",
        "nl": "Dutch",
        "cs": "Czech",
        "ar": "Arabic",
        "zh": "Chinese",
        "ja": "Japanese",
        "hu": "Hungarian",
        "ko": "Korean"
    }
    
    @classmethod
    def ensure_directories(cls):
        """Create necessary directories"""
        directories = [
            cls.VOICE_SAMPLES_DIR,
            cls.GENERATED_DIR,
            cls.MODELS_DIR,
            cls.TEMP_DIR
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    @classmethod
    def get_config_dict(cls) -> Dict[str, Any]:
        """Get configuration as dictionary"""
        return {
            "api": {
                "host": cls.API_HOST,
                "port": cls.API_PORT
            },
            "model": {
                "name": cls.MODEL_NAME,
                "device": cls.DEVICE
            },
            "audio": {
                "sample_rate": cls.SAMPLE_RATE,
                "max_length": cls.MAX_AUDIO_LENGTH,
                "supported_formats": cls.SUPPORTED_FORMATS
            },
            "directories": {
                "voices": cls.VOICE_SAMPLES_DIR,
                "generated": cls.GENERATED_DIR,
                "models": cls.MODELS_DIR,
                "temp": cls.TEMP_DIR
            },
            "database": {
                "use_local": cls.USE_LOCAL_DB,
                "local_path": cls.LOCAL_DB_PATH
            },
            "websocket": {
                "port": cls.WS_PORT,
                "max_connections": cls.MAX_CONNECTIONS
            },
            "validation": cls.VOICE_VALIDATION,
            "tts": cls.TTS_CONFIG,
            "languages": cls.SUPPORTED_LANGUAGES
        }

# Create directories on import
Config.ensure_directories()
