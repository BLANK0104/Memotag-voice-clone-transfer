"""
Simplified Voice Cloner with Lazy Loading
Provides the same functionality as VoiceCloner but with lazy initialization
"""

import os
import sys
import torch
import librosa
import soundfile as sf
import numpy as np
from typing import Optional, Dict, Any
import hashlib
from datetime import datetime

class VoiceClonerSimple:
    """Simplified Voice Cloner with lazy loading"""
    
    def __init__(self):
        """Initialize with lazy loading"""
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model_name = "tts_models/multilingual/multi-dataset/xtts_v2"
        self.tts = None  # Will be loaded when needed
        self.sample_rate = 22050
        self.model_loaded = False
        
        print(f"[*] VoiceClonerSimple initialized on device: {self.device}")
        print("[*] TTS model will be loaded on first use")
    
    def _ensure_model_loaded(self):
        """Load the TTS model if not already loaded"""
        if not self.model_loaded:
            try:
                print("📥 Loading XTTS-v2 model...")
                
                # Import matplotlib workaround
                try:
                    import matplotlib
                    matplotlib.use('Agg')  # Use non-GUI backend
                except ImportError:
                    pass
                
                from TTS.api import TTS
                self.tts = TTS(self.model_name).to(self.device)
                self.model_loaded = True
                print("✅ Model loaded successfully!")
                
            except Exception as e:
                print(f"❌ Error loading model: {e}")
                raise
    
    def extract_voice_features(self, audio_path: str) -> Dict[str, Any]:
        """Extract voice features from audio sample"""
        try:
            print(f"🎵 Extracting voice features from: {audio_path}")
            
            # Load and preprocess audio
            audio, sr = librosa.load(audio_path, sr=self.sample_rate)
            
            # Ensure audio is at least 3 seconds and at most 30 seconds
            min_length = 3 * self.sample_rate
            max_length = 30 * self.sample_rate
            
            if len(audio) < min_length:
                # Repeat audio if too short
                repeats = int(np.ceil(min_length / len(audio)))
                audio = np.tile(audio, repeats)[:min_length]
            elif len(audio) > max_length:
                # Trim if too long
                audio = audio[:max_length]
            
            # Normalize audio
            audio = librosa.util.normalize(audio)
            
            # Extract basic features for voice cloning
            features = {
                "audio_data": audio.tolist(),
                "sample_rate": self.sample_rate,
                "duration": len(audio) / self.sample_rate,
                "rms_energy": float(np.sqrt(np.mean(audio**2))),
                "spectral_centroid": float(np.mean(librosa.feature.spectral_centroid(y=audio, sr=sr)[0])),
                "zero_crossing_rate": float(np.mean(librosa.feature.zero_crossing_rate(audio)[0])),
                "mfcc": librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=13).mean(axis=1).tolist(),
                "created_at": datetime.now().isoformat()
            }
            
            print("✅ Voice features extracted successfully!")
            return features
            
        except Exception as e:
            print(f"❌ Error extracting voice features: {e}")
            raise
    
    def clone_voice(self, text: str, voice_features: Dict[str, Any], output_path: str) -> str:
        """Generate speech using cloned voice with XTTS-v2"""
        try:
            print(f"🗣️ Generating speech with voice cloning: '{text[:50]}...'")
            
            # Ensure model is loaded
            self._ensure_model_loaded()
            
            # Create temporary speaker audio file from voice features
            temp_speaker_path = "temp_speaker.wav"
            audio_data = np.array(voice_features["audio_data"])
            sf.write(temp_speaker_path, audio_data, voice_features["sample_rate"])
            
            # Generate speech using XTTS-v2 with the uploaded voice characteristics
            self.tts.tts_to_file(
                text=text,
                speaker_wav=temp_speaker_path,
                language="hi",  # Hindi language code
                file_path=output_path
            )
            
            # Clean up temporary file
            if os.path.exists(temp_speaker_path):
                os.remove(temp_speaker_path)
            
            print(f"✅ Voice cloned speech generated successfully: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"❌ Error generating cloned voice speech: {e}")
            # If voice cloning fails, fall back to alternative method
            try:
                print("🔄 Falling back to alternative TTS...")
                from .voice_cloner_alternative import VoiceClonerAlternative
                fallback = VoiceClonerAlternative()
                return fallback.clone_voice(text, voice_features, output_path)
            except Exception as e2:
                print(f"❌ Fallback also failed: {e2}")
                raise e
    
    def preprocess_audio(self, audio_path: str, output_path: str) -> str:
        """Preprocess audio for voice cloning"""
        try:
            from pydub import AudioSegment
            
            # Load audio with pydub for format conversion
            audio = AudioSegment.from_file(audio_path)
            
            # Convert to mono if stereo
            if audio.channels > 1:
                audio = audio.set_channels(1)
            
            # Set sample rate
            audio = audio.set_frame_rate(self.sample_rate)
            
            # Normalize audio
            audio = audio.normalize()
            
            # Export as WAV
            audio.export(output_path, format="wav")
            
            print(f"✅ Audio preprocessed and saved to: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"❌ Error preprocessing audio: {e}")
            raise
    
    def validate_audio_quality(self, audio_path: str) -> Dict[str, Any]:
        """Validate audio quality for voice cloning"""
        try:
            audio, sr = librosa.load(audio_path, sr=None)
            
            validation = {
                "is_valid": True,
                "issues": [],
                "recommendations": [],
                "duration": len(audio) / sr,
                "sample_rate": sr,
                "channels": 1 if len(audio.shape) == 1 else audio.shape[1]
            }
            
            # Check duration
            if validation["duration"] < 3:
                validation["issues"].append("Audio too short (minimum 3 seconds)")
                validation["is_valid"] = False
            elif validation["duration"] > 30:
                validation["issues"].append("Audio too long (maximum 30 seconds)")
                validation["recommendations"].append("Consider trimming to 10-15 seconds")
            
            # Check sample rate
            if sr < 16000:
                validation["issues"].append("Low sample rate (minimum 16kHz recommended)")
                validation["recommendations"].append("Use higher quality audio")
            
            # Check audio levels
            rms = np.sqrt(np.mean(audio**2))
            if rms < 0.01:
                validation["issues"].append("Audio level too low")
                validation["recommendations"].append("Increase recording volume")
            elif rms > 0.8:
                validation["issues"].append("Audio level too high (may be clipped)")
                validation["recommendations"].append("Reduce recording volume")
            
            # Check for silence
            silence_threshold = 0.001
            silence_ratio = np.sum(np.abs(audio) < silence_threshold) / len(audio)
            if silence_ratio > 0.3:
                validation["issues"].append("Too much silence in audio")
                validation["recommendations"].append("Remove silent portions")
            
            return validation
            
        except Exception as e:
            return {
                "is_valid": False,
                "issues": [f"Error validating audio: {e}"],
                "recommendations": ["Please check audio file format"],
                "duration": 0,
                "sample_rate": 0,
                "channels": 0
            }

# Create a global instance getter function
def get_voice_cloner():
    """Get voice cloner instance"""
    return VoiceClonerSimple()