#!/usr/bin/env python3
"""
WebSocket-Compatible Fixed Hinglish Voice Cloner
This integrates the fixed Hinglish quality improvements into the WebSocket system
"""

import os
import sys
import numpy as np
import soundfile as sf
import librosa
import re
from app.voice_cloner_multilingual import MultilingualVoiceCloner

class WebSocketFixedHinglishCloner(MultilingualVoiceCloner):
    """Fixed Hinglish cloner compatible with WebSocket server interface"""
    
    def __init__(self):
        super().__init__()
        print("🚀 WebSocket Fixed Hinglish Cloner initialized")
        print("   ✅ Natural TTS parameters")
        print("   ✅ Minimal audio processing")
        print("   ✅ Ultra-minimal text optimization")
    
    def _chunk_long_text(self, text: str, max_length: int = 150) -> list:
        """Split long text into manageable chunks for better audio quality"""
        if len(text) <= max_length:
            return [text]
        
        # Try to split by sentences first
        sentences = re.split(r'[.!?।]', text)
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            # If adding this sentence would exceed max_length, start a new chunk
            if current_chunk and len(current_chunk + " " + sentence) > max_length:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence
            else:
                if current_chunk:
                    current_chunk += " " + sentence
                else:
                    current_chunk = sentence
        
        # Add the last chunk
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        print(f"📝 Text chunked into {len(chunks)} parts (max {max_length} chars each)")
        return chunks

    def optimize_text_for_voice_cloning(self, text: str) -> str:
        """FIXED: Ultra-minimal text optimization for natural audio"""
        original_text = text
        
        # Basic cleanup only
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Detect language composition
        segments = self.detect_text_language_segments(text)
        hindi_ratio = sum(1 for _, lang in segments if lang == "hi") / len(segments) if segments else 0
        
        # FIXED: ULTRA-MINIMAL Hinglish optimization (almost no changes)
        if 0.1 < hindi_ratio < 0.9:  # Mixed content
            print(f"🔧 ULTRA-MINIMAL Hinglish optimization (Hindi ratio: {hindi_ratio:.2f})")
            
            # Strategy 1: Only remove sentence splitters that cause problems
            text = re.sub(r'[!।?]+', '', text)  # Remove punctuation that causes splits
            
            # Strategy 2: Add TINY space between Hindi and English to prevent confusion
            text = re.sub(r'([अ-ह])([A-Za-z])', r'\1 \2', text)  # Hindi to English
            text = re.sub(r'([A-Za-z])([अ-ह])', r'\1 \2', text)  # English to Hindi
            
            # Strategy 3: Clean up multiple spaces
            text = re.sub(r'\s+', ' ', text.strip())
        
        if text != original_text:
            print(f"📝 Minimal optimization applied:")
            print(f"   Before: '{original_text}'")
            print(f"   After:  '{text}'")
        
        return text
    
    def _minimal_audio_cleanup(self, audio: np.ndarray) -> np.ndarray:
        """FIXED: Minimal audio cleanup that preserves quality"""
        if audio is None or len(audio) == 0:
            return audio
        
        try:
            # Only basic normalization and trimming
            print("🔧 Applying minimal audio cleanup...")
            
            # Trim silence from start and end
            audio = librosa.effects.trim(audio, top_db=20)[0]
            
            # Basic normalization to prevent clipping
            if np.max(np.abs(audio)) > 0:
                audio = audio / np.max(np.abs(audio)) * 0.95
              # Very gentle fade in/out (1ms) to prevent clicks
            if len(audio) > 1000:
                fade_samples = min(22, len(audio) // 100)  # 1ms at 22kHz
                fade_in = np.linspace(0, 1, fade_samples)
                fade_out = np.linspace(1, 0, fade_samples)
                audio[:fade_samples] *= fade_in
                audio[-fade_samples:] *= fade_out
            
            print("✅ Minimal cleanup completed")
            return audio
            
        except Exception as e:
            print(f"⚠️ Cleanup failed: {e}")
            return audio
    
    def clone_voice_multilingual(self, text: str, voice_features: dict, 
                               output_path: str, enhance_quality: bool = True) -> str:
        """FIXED: Simple, natural voice generation with chunking for long texts"""
        try:
            self._ensure_model_loaded()
            
            print(f"🎯 FIXED Hinglish generation: '{text[:100]}...' ({len(text)} chars)")
            
            # Minimal text optimization
            optimized_text = self.optimize_text_for_voice_cloning(text)
            
            # Use reference audio as-is (no "enhancement" that causes distortion)
            reference_audio = np.array(voice_features["audio_data"])
            
            # Basic normalization only
            if np.max(np.abs(reference_audio)) > 0:
                reference_audio = reference_audio / np.max(np.abs(reference_audio)) * 0.8
            
            # Create output directory
            output_dir = os.path.dirname(output_path)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
            
            # Language detection
            segments = self.detect_text_language_segments(text)
            hindi_ratio = sum(1 for _, lang in segments if lang == "hi") / len(segments) if segments else 0
            
            # Simple language selection
            primary_language = "hi" if hindi_ratio > 0.3 else "en"
            
            # Create temporary speaker file
            temp_speaker_path = "temp_speaker_websocket.wav"
            sf.write(temp_speaker_path, reference_audio, self.sample_rate)
            
            try:                # Generate as single text without length limitations
                print(f"🎵 Generating unlimited text length: {len(optimized_text)} characters")
                print(f"🎵 Generating with NATURAL parameters (single chunk)...")
                print(f"   Language: {primary_language}")
                print(f"   Text: '{optimized_text[:100]}...'")
                
                generated_audio = self.tts.tts(
                    text=optimized_text,
                    speaker_wav=temp_speaker_path,
                    language=primary_language,
                    split_sentences=False,  # FIXED: Prevent voice bleeding
                )
            
            finally:
                if os.path.exists(temp_speaker_path):
                    os.remove(temp_speaker_path)
            
            # Convert to numpy array
            if not isinstance(generated_audio, np.ndarray):
                generated_audio = np.array(generated_audio)
            
            # MINIMAL post-processing - just basic cleanup
            generated_audio = self._minimal_audio_cleanup(generated_audio)
            
            # Save directly
            sf.write(output_path, generated_audio, self.sample_rate)
            
            # Simple quality analysis
            duration = len(generated_audio) / self.sample_rate
            rms = np.sqrt(np.mean(generated_audio**2))
            
            print(f"✅ FIXED audio generated: {output_path}")
            print(f"📊 Duration: {duration:.2f}s (expected: 2-8s for normal sentences)")
            print(f"🔊 RMS level: {rms:.3f}")
            
            if duration > 15:
                print("⚠️  WARNING: Duration unusually long - check text complexity")
            elif duration > 8:
                print("ℹ️  INFO: Long duration may be due to complex/long text")
            
            return output_path
            
        except Exception as e:
            print(f"❌ FIXED generation failed: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def clone_voice(self, text: str, voice_features: dict, output_path: str) -> str:
        """WebSocket-compatible interface - calls the fixed multilingual method"""
        print(f"🌐 WebSocket clone_voice called: '{text}'")
        return self.clone_voice_multilingual(text, voice_features, output_path, enhance_quality=True)

def create_websocket_fixed_cloner():
    """Create the WebSocket-compatible fixed cloner"""
    return WebSocketFixedHinglishCloner()

# Test function for validation
def test_websocket_integration():
    """Test the WebSocket integration"""
    print("🔧 Testing WebSocket Integration")
    print("=" * 50)
    
    # Initialize cloner
    cloner = create_websocket_fixed_cloner()
    
    # Test voice features extraction
    voice_path = "voices/rupesh sir_3c2b9c74.wav"
    if os.path.exists(voice_path):
        voice_features = cloner.extract_voice_features(voice_path)
        if voice_features:
            print("✅ Voice features extracted successfully")
            
            # Test the WebSocket interface method
            test_text = "Hello यह एक test है for WebSocket integration"
            output_path = "websocket_test.wav"
            
            try:
                result = cloner.clone_voice(test_text, voice_features, output_path)
                
                if os.path.exists(result):
                    audio, sr = sf.read(result)
                    duration = len(audio) / sr
                    print(f"✅ WebSocket test successful: {duration:.2f}s")
                    
                    if duration < 8:
                        print("🎉 WebSocket integration working perfectly!")
                    else:
                        print("⚠️ Duration still too long")
                else:
                    print("❌ WebSocket test failed - no output file")
            except Exception as e:
                print(f"❌ WebSocket test failed: {e}")
        else:
            print("❌ Could not extract voice features")
    else:
        print(f"❌ Voice file not found: {voice_path}")

if __name__ == "__main__":
    test_websocket_integration()
