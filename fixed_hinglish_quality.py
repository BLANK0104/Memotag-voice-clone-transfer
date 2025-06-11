#!/usr/bin/env python3
"""
FIXED: Simple, high-quality Hinglish voice cloning
This script fixes the major audio quality issues by simplifying the approach
"""

import os
import sys
import numpy as np
import soundfile as sf
import librosa
import re
from app.voice_cloner_multilingual import MultilingualVoiceCloner

def create_fixed_quality_optimizer():
    """Create a FIXED voice cloner that produces natural, high-quality audio"""
    
    class FixedHinglishCloner(MultilingualVoiceCloner):
        """FIXED: Simple but effective Hinglish optimization"""
        
        def __init__(self):
            super().__init__()
            
        def optimize_text_for_voice_cloning(self, text: str) -> str:
            """SIMPLIFIED text optimization - minimal changes for natural flow"""
            original_text = text
            
            # Basic cleanup only
            text = re.sub(r'\s+', ' ', text.strip())
            
            # Only fix obvious splitting issues - NO aggressive punctuation replacement
            # Replace sentence-ending punctuation with periods for consistency
            text = re.sub(r'[।]+', '.', text)  # Hindi sentence endings
            text = re.sub(r'[!?]+', '.', text)  # Exclamations/questions
            
            # Remove multiple consecutive periods
            text = re.sub(r'\.+', '.', text)
            
            # Don't mess with language transitions - XTTS handles this well
            
            if text != original_text:
                print(f"📝 Minimal optimization applied:")
                print(f"   Before: '{original_text}'")
                print(f"   After:  '{text}'")
            
            return text
        
        def clone_voice_multilingual(self, text: str, voice_features: dict, 
                                   output_path: str, enhance_quality: bool = True) -> str:
            """FIXED: Simple, natural voice generation"""
            try:
                self._ensure_model_loaded()
                
                print(f"🎯 FIXED Hinglish generation: '{text}'")
                
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
                temp_speaker_path = "temp_speaker_fixed.wav"
                sf.write(temp_speaker_path, reference_audio, self.sample_rate)
                
                try:
                    # FIXED: Use SIMPLE, NATURAL parameters
                    print(f"🎵 Generating with NATURAL parameters...")
                    print(f"   Language: {primary_language}")
                    print(f"   Text: '{optimized_text}'")
                    
                    # SIMPLE parameters that work
                    generated_audio = self.tts.tts(
                        text=optimized_text,
                        speaker_wav=temp_speaker_path,
                        language=primary_language,
                        # NO exotic parameters that cause distortion
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
                print(f"📊 Duration: {duration:.2f}s (expected: 2-4s for normal sentences)")
                print(f"🔊 RMS level: {rms:.3f}")
                
                if duration > 10:
                    print("⚠️  WARNING: Duration unusually long - check TTS parameters")
                
                return output_path
                
            except Exception as e:
                print(f"❌ Generation failed: {e}")
                raise
        
        def _minimal_audio_cleanup(self, audio: np.ndarray) -> np.ndarray:
            """MINIMAL cleanup - just remove obvious artifacts"""
            try:
                print("🧹 Minimal cleanup...")
                
                # Convert to float32
                if audio.dtype != np.float32:
                    audio = audio.astype(np.float32)
                
                # Remove DC offset
                audio = audio - np.mean(audio)
                
                # Basic trimming (remove long silences)
                audio, _ = librosa.effects.trim(audio, top_db=20)
                
                # Gentle normalization
                peak = np.max(np.abs(audio))
                if peak > 0:
                    audio = audio / peak * 0.8
                
                # Very gentle fade in/out to remove clicks
                fade_samples = min(int(0.01 * self.sample_rate), len(audio) // 40)
                if fade_samples > 0:
                    fade_in = np.linspace(0, 1, fade_samples)
                    fade_out = np.linspace(1, 0, fade_samples)
                    audio[:fade_samples] *= fade_in
                    audio[-fade_samples:] *= fade_out
                
                print("✅ Minimal cleanup completed")
                return audio
                
            except Exception as e:
                print(f"⚠️ Cleanup failed: {e}")
                return audio

    return FixedHinglishCloner()

def test_fixed_quality():
    """Test the FIXED quality system"""
    print("🚀 Testing FIXED Hinglish Quality System")
    print("=" * 50)
    
    # Initialize fixed cloner
    cloner = create_fixed_quality_optimizer()
    
    # Load reference voice
    voice_features = cloner.load_voice_features("sample_voice.wav")
    if not voice_features:
        print("❌ Could not load voice features")
        return
    
    # Test sentences (same as before for comparison)
    test_texts = [
        "Dinner bahut tasty tha and I really enjoyed it",
        "Aaj ka weather बहुत अच्छा है, let's go for a walk",
        "मैं very excited हूँ for the party tonight",
        "This movie था really boring, मुझे नहीं लगा अच्छा",
        "क्या आप coffee पीना चाहते हैं? It's fresh और hot"
    ]
    
    print(f"📂 Creating test files...")
    
    for i, text in enumerate(test_texts, 1):
        try:
            output_path = f"fixed_quality_{i}.wav"
            print(f"\n🎤 Test {i}: '{text}'")
            
            result_path = cloner.clone_voice_multilingual(
                text=text,
                voice_features=voice_features,
                output_path=output_path,
                enhance_quality=True
            )
            
            # Quick validation
            if os.path.exists(result_path):
                audio, sr = sf.read(result_path)
                duration = len(audio) / sr
                print(f"✅ Generated: {result_path} ({duration:.2f}s)")
                
                if duration > 8:
                    print(f"⚠️  WARNING: Duration {duration:.2f}s seems too long!")
                else:
                    print(f"✅ Duration {duration:.2f}s looks normal")
            else:
                print(f"❌ Failed to create {result_path}")
                
        except Exception as e:
            print(f"❌ Test {i} failed: {e}")
    
    print(f"\n✅ FIXED quality testing completed!")
    print("🎧 Compare the 'fixed_quality_*.wav' files with previous versions")

if __name__ == "__main__":
    test_fixed_quality()
