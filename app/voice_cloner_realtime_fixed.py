#!/usr/bin/env python3
"""
FIXED Real-time Hinglish Voice Cloning with Streaming Audio
This applies our quality fixes to the realtime streaming system
"""

import os
import sys
import torch
import librosa
import soundfile as sf
import numpy as np
import re
import asyncio
import threading
import queue
from typing import Optional, Dict, Any, List, Tuple, AsyncGenerator
import hashlib
from datetime import datetime
import tempfile

class FixedRealTimeHinglishVoiceCloner:
    """FIXED Real-time streaming voice cloner for Hinglish text"""
    
    def __init__(self, chunk_duration: float = 2.0):
        """Initialize with FIXED real-time streaming support"""
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model_name = "tts_models/multilingual/multi-dataset/xtts_v2"
        self.tts = None
        self.sample_rate = 22050
        self.model_loaded = False
        self.chunk_duration = chunk_duration  # Duration of each audio chunk in seconds
        
        # Enhanced language detection patterns
        self.hindi_pattern = re.compile(r'[\u0900-\u097F]+')
        self.english_pattern = re.compile(r'[a-zA-Z]+')
        
        # Real-time processing queue
        self.processing_queue = queue.Queue()
        self.audio_queue = queue.Queue()
        
        print(f"[*] 🚀 FIXED RealTimeHinglishVoiceCloner initialized on device: {self.device}")
        print(f"[*] Chunk duration: {chunk_duration}s for real-time streaming")
        print("    ✅ Natural TTS parameters")
        print("    ✅ Minimal audio processing")
        print("    ✅ Ultra-minimal text optimization")
    
    def _ensure_model_loaded(self):
        """Load the TTS model if not already loaded"""
        if not self.model_loaded:
            try:
                print("📥 Loading XTTS-v2 model for FIXED real-time synthesis...")
                
                # Import matplotlib workaround
                try:
                    import matplotlib
                    matplotlib.use('Agg')  # Use non-GUI backend
                except ImportError:
                    pass
                
                from TTS.api import TTS
                self.tts = TTS(self.model_name).to(self.device)
                self.model_loaded = True
                print("✅ XTTS-v2 model loaded successfully for real-time streaming")
                
            except Exception as e:
                print(f"❌ Failed to load XTTS-v2 model: {e}")
                raise
    
    def detect_text_language_segments(self, text: str) -> List[Tuple[str, str]]:
        """Detect language segments in mixed text"""
        segments = []
        words = text.split()
        
        for word in words:
            if self.hindi_pattern.search(word):
                segments.append((word, "hi"))
            elif self.english_pattern.search(word):
                segments.append((word, "en"))
            else:
                segments.append((word, "unknown"))
        
        return segments
    
    def optimize_text_for_voice_cloning(self, text: str) -> str:
        """FIXED: Ultra-minimal text optimization for natural realtime audio"""
        original_text = text
        
        # Basic cleanup only
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Detect language composition
        segments = self.detect_text_language_segments(text)
        hindi_ratio = sum(1 for _, lang in segments if lang == "hi") / len(segments) if segments else 0
        
        # FIXED: ULTRA-MINIMAL Hinglish optimization (almost no changes)
        if 0.1 < hindi_ratio < 0.9:  # Mixed content
            print(f"🔧 ULTRA-MINIMAL realtime optimization (Hindi ratio: {hindi_ratio:.2f})")
            
            # Strategy 1: Only remove sentence splitters that cause problems
            text = re.sub(r'[!।?]+', '', text)  # Remove punctuation that causes splits
            
            # Strategy 2: Add TINY space between Hindi and English to prevent confusion
            text = re.sub(r'([अ-ह])([A-Za-z])', r'\1 \2', text)  # Hindi to English
            text = re.sub(r'([A-Za-z])([अ-ह])', r'\1 \2', text)  # English to Hindi
            
            # Strategy 3: Clean up multiple spaces
            text = re.sub(r'\s+', ' ', text.strip())
        
        if text != original_text:
            print(f"📝 Realtime optimization applied:")
            print(f"   Before: '{original_text}'")
            print(f"   After:  '{text}'")
        
        return text
    
    def _minimal_audio_cleanup(self, audio: np.ndarray) -> np.ndarray:
        """FIXED: Minimal audio cleanup for realtime processing"""
        if audio is None or len(audio) == 0:
            return audio
        
        try:
            # Only basic normalization and trimming for realtime
            audio = librosa.effects.trim(audio, top_db=20)[0]
            
            # Basic normalization to prevent clipping
            if np.max(np.abs(audio)) > 0:
                audio = audio / np.max(np.abs(audio)) * 0.95
            
            # Very gentle fade in/out to prevent clicks            if len(audio) > 1000:
                fade_samples = min(22, len(audio) // 100)  # 1ms at 22kHz
                fade_in = np.linspace(0, 1, fade_samples)
                fade_out = np.linspace(1, 0, fade_samples)
                audio[:fade_samples] *= fade_in
                audio[-fade_samples:] *= fade_out
            
            return audio
            
        except Exception as e:
            print(f"⚠️ Realtime cleanup failed: {e}")
            return audio
    
    def _split_text_into_chunks(self, text: str) -> List[str]:
        """Split text into manageable chunks for streaming (no length limitations)"""
        # Split by sentences for natural streaming
        sentences = re.split(r'[.!?।]+', text)
        chunks = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            # Add sentence as-is without length restrictions
            chunks.append(sentence)
        
        return chunks
    
    async def clone_voice_realtime(self, text: str, voice_features: dict, 
                                 progress_callback=None) -> AsyncGenerator[bytes, None]:
        """FIXED: Real-time voice cloning with streaming output"""
        try:
            self._ensure_model_loaded()
            
            print(f"🎯 FIXED Realtime generation: '{text}'")
            
            # Minimal text optimization
            optimized_text = self.optimize_text_for_voice_cloning(text)
            
            # Use reference audio as-is
            reference_audio = np.array(voice_features["audio_data"])
            
            # Basic normalization only
            if np.max(np.abs(reference_audio)) > 0:
                reference_audio = reference_audio / np.max(np.abs(reference_audio)) * 0.8
            
            # Language detection
            segments = self.detect_text_language_segments(text)
            hindi_ratio = sum(1 for _, lang in segments if lang == "hi") / len(segments) if segments else 0
            primary_language = "hi" if hindi_ratio > 0.3 else "en"
            
            # Split text into chunks for streaming
            text_chunks = self._split_text_into_chunks(optimized_text)
            total_chunks = len(text_chunks)
            
            print(f"📝 Split into {total_chunks} chunks for streaming")
            
            # Create temporary speaker file
            temp_speaker_path = f"temp_speaker_realtime_{hash(text) % 10000}.wav"
            sf.write(temp_speaker_path, reference_audio, self.sample_rate)
            
            try:
                for i, chunk in enumerate(text_chunks):
                    if not chunk.strip():
                        continue
                    
                    print(f"🎵 Processing chunk {i+1}/{total_chunks}: '{chunk[:50]}...'")
                    
                    # Progress callback
                    if progress_callback:
                        await progress_callback(f"Processing chunk {i+1}/{total_chunks}")
                      # FIXED: Use SIMPLE, NATURAL parameters for realtime
                    generated_audio = self.tts.tts(
                        text=chunk,
                        speaker_wav=temp_speaker_path,
                        language=primary_language,
                        split_sentences=False,  # FIXED: Prevent voice bleeding
                        # NO exotic parameters that cause distortion
                    )
                    
                    # Convert to numpy array
                    if not isinstance(generated_audio, np.ndarray):
                        generated_audio = np.array(generated_audio)
                    
                    # MINIMAL post-processing
                    generated_audio = self._minimal_audio_cleanup(generated_audio)
                    
                    # Convert to bytes for streaming
                    audio_bytes = (generated_audio * 32767).astype(np.int16).tobytes()
                      # Yield audio chunk
                    yield audio_bytes
                    
                    # Very small delay to prevent overwhelming the client
                    await asyncio.sleep(0.02)
            
            finally:
                if os.path.exists(temp_speaker_path):
                    os.remove(temp_speaker_path)
            
            print("✅ FIXED realtime generation completed")
            
        except Exception as e:
            print(f"❌ FIXED realtime generation failed: {e}")
            import traceback
            traceback.print_exc()
            raise

# For backward compatibility
class RealTimeHinglishVoiceCloner(FixedRealTimeHinglishVoiceCloner):
    """Backward compatibility wrapper"""
    pass

def create_fixed_realtime_cloner(chunk_duration: float = 2.0):
    """Create the fixed realtime cloner"""
    return FixedRealTimeHinglishVoiceCloner(chunk_duration)

# Test function
async def test_realtime_integration():
    """Test the realtime integration"""
    print("🔧 Testing FIXED Realtime Integration")
    print("=" * 50)
    
    # Initialize cloner
    cloner = create_fixed_realtime_cloner()
    
    # Test text
    test_text = "Hello यह एक realtime test है. आज का weather बहुत अच्छा है!"
    
    # Mock voice features (would normally come from actual voice)
    mock_voice_features = {
        "audio_data": np.random.randn(22050) * 0.1  # 1 second of mock audio
    }
    
    print(f"🎤 Testing realtime: '{test_text}'")
    
    try:
        chunk_count = 0
        async for audio_chunk in cloner.clone_voice_realtime(test_text, mock_voice_features):
            chunk_count += 1
            print(f"📦 Received chunk {chunk_count}: {len(audio_chunk)} bytes")
            
            # In real usage, you'd stream this to the client
            if chunk_count >= 3:  # Limit for testing
                break
        
        print(f"✅ Realtime test successful: {chunk_count} chunks generated")
        
    except Exception as e:
        print(f"❌ Realtime test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_realtime_integration())
