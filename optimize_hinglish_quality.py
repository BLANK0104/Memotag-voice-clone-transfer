#!/usr/bin/env python3
"""
Advanced quality optimization for Hinglish voice cloning
This script implements sophisticated techniques to improve voice quality and consistency
"""

import os
import sys
import numpy as np
import soundfile as sf
import librosa
from scipy import signal
import re
from app.voice_cloner_multilingual import MultilingualVoiceCloner
import tempfile

def create_advanced_quality_optimizer():
    """Create an enhanced voice cloner with optimized parameters for Hinglish"""
    
    class OptimizedHinglishCloner(MultilingualVoiceCloner):
        """Enhanced cloner with advanced Hinglish optimization"""
        
        def __init__(self):
            super().__init__()
            # Advanced optimization parameters
            self.quality_enhanced = True
            
        def optimize_text_for_voice_cloning(self, text: str) -> str:
            """Advanced text optimization for superior voice consistency"""
            original_text = text
            
            # Normalize whitespace
            text = re.sub(r'\s+', ' ', text.strip())
            
            # Detect language composition
            segments = self.detect_text_language_segments(text)
            hindi_ratio = sum(1 for _, lang in segments if lang == "hi") / len(segments) if segments else 0            # FIXED: ULTRA-MINIMAL Hinglish optimization (almost no changes)
            if 0.1 < hindi_ratio < 0.9:  # Mixed content
                print(f"🔧 ULTRA-MINIMAL Hinglish optimization (Hindi ratio: {hindi_ratio:.2f})")
                
                # Strategy 1: Only remove sentence splitters that cause problems
                text = re.sub(r'[!।?]+', '', text)  # Remove all punctuation that causes splits
                
                # Strategy 2: Add TINY space between Hindi and English to prevent confusion
                # This fixes the issue where "आज It's" becomes problematic
                text = re.sub(r'([अ-ह])([A-Za-z])', r'\1 \2', text)  # Hindi to English
                text = re.sub(r'([A-Za-z])([अ-ह])', r'\1 \2', text)  # English to Hindi
                
                # Strategy 3: Clean up multiple spaces
                text = re.sub(r'\s+', ' ', text.strip())
            
            # Final cleanup
            text = re.sub(r'\s+', ' ', text.strip())
            
            if text != original_text:
                print(f"📝 ULTRA-MINIMAL optimization applied:")
                print(f"   Before: '{original_text[:80]}...'")
                print(f"   After:  '{text[:80]}...'")
            else:
                print(f"📝 No optimization needed - text is completely natural")
            
            return text
        
        def clone_voice_multilingual(self, text: str, voice_features: dict, 
                                   output_path: str, enhance_quality: bool = True) -> str:
            """Enhanced multilingual cloning with advanced quality optimization"""
            try:
                self._ensure_model_loaded()
                
                print(f"🎯 Advanced Hinglish voice generation: '{text[:50]}...'")
                
                # Advanced text optimization
                optimized_text = self.optimize_text_for_voice_cloning(text)
                
                # Enhanced voice preparation
                reference_audio = np.array(voice_features["audio_data"])
                reference_audio = self._enhance_reference_audio(reference_audio)
                
                # Create output directory
                output_dir = os.path.dirname(output_path)
                if output_dir:
                    os.makedirs(output_dir, exist_ok=True)
                
                # Language detection for parameter optimization
                segments = self.detect_text_language_segments(text)
                hindi_ratio = sum(1 for _, lang in segments if lang == "hi") / len(segments)
                
                # Determine optimal TTS parameters
                primary_language = "hi" if hindi_ratio > 0.3 else "en"
                
                # Create enhanced temporary speaker file
                temp_speaker_path = "temp_speaker_advanced.wav"
                sf.write(temp_speaker_path, reference_audio, self.sample_rate)
                
                try:                    # FIXED TTS parameters - natural and simple
                    tts_params = {
                        "text": optimized_text,
                        "speaker_wav": temp_speaker_path,
                        "language": primary_language,
                        "split_sentences": False,  # Keep voices consistent
                        # NO speed manipulation - use natural speed
                    }
                    
                    print(f"🎵 Generating with advanced parameters...")
                    print(f"   Language: {primary_language}")
                    print(f"   Split sentences: False")
                    print(f"   Text length: {len(optimized_text)} chars")
                      # Generate with FIXED parameters (no exotic settings)
                    print("🔧 FIXED: Using natural TTS parameters (no speed/length manipulation)")
                    generated_audio = self.tts.tts(**tts_params)
                
                finally:
                    if os.path.exists(temp_speaker_path):
                        os.remove(temp_speaker_path)
                
                # Convert to numpy array
                if not isinstance(generated_audio, np.ndarray):
                    generated_audio = np.array(generated_audio)
                  # MINIMAL post-processing to avoid distortion
                print("🧹 Applying minimal cleanup only...")
                
                # Basic cleanup only
                generated_audio = generated_audio.astype(np.float32)
                generated_audio = generated_audio - np.mean(generated_audio)  # Remove DC offset
                
                # Gentle normalization
                peak = np.max(np.abs(generated_audio))
                if peak > 0:
                    generated_audio = generated_audio / peak * 0.8
                
                # Save with natural format
                sf.write(output_path, generated_audio, self.sample_rate)
                
                # Simple analysis
                duration = len(generated_audio) / self.sample_rate
                rms = np.sqrt(np.mean(generated_audio**2))
                
                print(f"✅ FIXED Hinglish audio generated: {output_path}")
                print(f"📊 Duration: {duration:.2f}s (should be 2-5s for normal sentences)")
                print(f"🔊 RMS level: {rms:.3f}")
                
                if duration > 8:
                    print("⚠️  WARNING: Duration too long - TTS parameters may need adjustment")
                
                return output_path
                
            except Exception as e:
                print(f"❌ Advanced generation failed: {e}")
                raise
        
        def _enhance_reference_audio(self, audio: np.ndarray) -> np.ndarray:
            """Enhance reference audio for better voice characteristic extraction"""
            try:
                # Normalize
                audio = audio / np.max(np.abs(audio)) * 0.8
                
                # Apply gentle high-pass filter to remove low-frequency noise
                nyquist = self.sample_rate * 0.5
                high_cutoff = 80 / nyquist
                if high_cutoff < 0.99:
                    b, a = signal.butter(2, high_cutoff, btype='high')
                    audio = signal.filtfilt(b, a, audio)
                
                # Apply gentle low-pass filter to remove high-frequency artifacts
                low_cutoff = 8000 / nyquist
                if low_cutoff < 0.99:
                    b, a = signal.butter(2, low_cutoff, btype='low')
                    audio = signal.filtfilt(b, a, audio)
                
                return audio
                
            except Exception as e:
                print(f"⚠️ Reference audio enhancement failed: {e}")
                return audio
        
        def _advanced_audio_cleanup(self, audio: np.ndarray) -> np.ndarray:
            """Advanced audio cleanup for superior quality"""
            try:
                print("🧹 Advanced audio cleanup...")
                
                # Convert to float32
                if audio.dtype != np.float32:
                    audio = audio.astype(np.float32)
                
                # Remove DC offset
                audio = audio - np.mean(audio)
                
                # Advanced artifact removal
                # 1. Remove extreme outliers
                audio_std = np.std(audio)
                audio_mean = np.mean(audio)
                clip_threshold = audio_std * 3.5
                audio = np.clip(audio, audio_mean - clip_threshold, audio_mean + clip_threshold)
                
                # 2. Apply advanced filtering
                nyquist = self.sample_rate * 0.5
                
                # High-pass filter (remove rumble and TTS artifacts)
                high_cutoff = 90 / nyquist
                if high_cutoff < 0.99:
                    b, a = signal.butter(3, high_cutoff, btype='high')
                    audio = signal.filtfilt(b, a, audio)
                
                # 3. Intelligent silence trimming
                audio = self._intelligent_silence_removal(audio)
                
                # 4. Apply advanced fade-in/fade-out
                fade_samples = min(int(0.02 * self.sample_rate), len(audio) // 20)
                if fade_samples > 0:
                    # Smooth cubic fade
                    fade_in = np.power(np.linspace(0, 1, fade_samples), 3)
                    fade_out = np.power(np.linspace(1, 0, fade_samples), 3)
                    audio[:fade_samples] *= fade_in
                    audio[-fade_samples:] *= fade_out
                
                print("✅ Advanced cleanup completed")
                return audio
                
            except Exception as e:
                print(f"⚠️ Advanced cleanup failed: {e}")
                return audio
        
        def _intelligent_silence_removal(self, audio: np.ndarray) -> np.ndarray:
            """Intelligent silence removal using energy-based detection"""
            try:
                # Use smaller windows for precise detection
                window_size = int(0.02 * self.sample_rate)  # 20ms
                hop_size = int(0.01 * self.sample_rate)     # 10ms
                
                # Calculate energy for each window
                energy_values = []
                for i in range(0, len(audio) - window_size, hop_size):
                    window = audio[i:i + window_size]
                    energy = np.sum(window**2)
                    energy_values.append(energy)
                
                if len(energy_values) == 0:
                    return audio
                
                energy_values = np.array(energy_values)
                
                # Adaptive threshold based on energy distribution
                energy_sorted = np.sort(energy_values)
                noise_floor = np.mean(energy_sorted[:len(energy_sorted)//10])  # Bottom 10%
                speech_threshold = max(noise_floor * 5, np.max(energy_values) * 0.01)
                
                # Find speech regions
                speech_frames = energy_values > speech_threshold
                
                if not np.any(speech_frames):
                    return librosa.effects.trim(audio, top_db=25)[0]
                
                # Find boundaries with padding
                first_speech = max(0, np.argmax(speech_frames) - 2)  # 2 frames padding
                last_speech = min(len(speech_frames) - 1, 
                                len(speech_frames) - 1 - np.argmax(speech_frames[::-1]) + 2)
                
                # Convert to sample indices
                start_sample = first_speech * hop_size
                end_sample = min(len(audio), (last_speech + 1) * hop_size + window_size)
                
                return audio[start_sample:end_sample]
                
            except Exception as e:
                print(f"⚠️ Intelligent silence removal failed: {e}")
                return librosa.effects.trim(audio, top_db=25)[0]
        
        def _advanced_quality_enhancement(self, audio: np.ndarray, voice_features: dict) -> np.ndarray:
            """Advanced quality enhancement based on voice characteristics"""
            try:
                print("🎨 Advanced quality enhancement...")
                
                # Target characteristics
                target_rms = voice_features.get("rms_energy", 0.1)
                current_rms = np.sqrt(np.mean(audio**2))
                
                # Intelligent volume matching
                if current_rms > 0:
                    volume_ratio = target_rms / current_rms
                    # Apply gentle volume adjustment
                    volume_ratio = np.clip(volume_ratio, 0.5, 2.0)  # Limit adjustment
                    audio = audio * volume_ratio
                
                # Spectral enhancement
                target_centroid = voice_features.get("spectral_centroid", 2000)
                
                # Apply spectral shaping
                if target_centroid < 1800:  # Lower voice
                    # Enhance lower frequencies slightly
                    audio = self._apply_spectral_tilt(audio, tilt=-0.5)
                elif target_centroid > 2500:  # Higher voice
                    # Enhance higher frequencies slightly
                    audio = self._apply_spectral_tilt(audio, tilt=0.5)
                
                # Dynamic range optimization
                audio = self._optimize_dynamic_range(audio)
                
                return audio
                
            except Exception as e:
                print(f"⚠️ Quality enhancement failed: {e}")
                return audio
        
        def _apply_spectral_tilt(self, audio: np.ndarray, tilt: float) -> np.ndarray:
            """Apply subtle spectral tilt for voice matching"""
            try:
                # Simple spectral tilt using first-order emphasis
                if abs(tilt) < 0.1:
                    return audio
                
                # Pre-emphasis or de-emphasis
                if tilt > 0:
                    # High-frequency emphasis
                    emphasis_coeff = min(0.97, 0.95 + tilt * 0.02)
                    emphasized = np.append(audio[0], audio[1:] - emphasis_coeff * audio[:-1])
                    return emphasized
                else:
                    # Low-frequency emphasis (de-emphasis)
                    deemphasis_coeff = min(0.97, 0.95 - tilt * 0.02)
                    deemphasized = signal.lfilter([1], [1, -deemphasis_coeff], audio)
                    return deemphasized
                    
            except Exception as e:
                print(f"⚠️ Spectral tilt failed: {e}")
                return audio
        
        def _optimize_dynamic_range(self, audio: np.ndarray) -> np.ndarray:
            """Optimize dynamic range for natural sound"""
            try:
                # Gentle compression to even out volume variations
                # Calculate envelope
                window_size = int(0.05 * self.sample_rate)  # 50ms
                envelope = np.maximum.reduce([np.abs(audio[i:i+window_size]) 
                                           for i in range(0, len(audio)-window_size, window_size//4)])
                
                # Interpolate envelope to audio length
                envelope_interp = np.interp(np.linspace(0, len(envelope)-1, len(audio)), 
                                          np.arange(len(envelope)), envelope)
                
                # Gentle compression
                compressed_envelope = np.power(envelope_interp, 0.8)  # Mild compression
                
                # Apply compression
                safe_envelope = np.maximum(envelope_interp, 0.001)  # Prevent division by zero
                gain = compressed_envelope / safe_envelope
                gain = np.clip(gain, 0.3, 3.0)  # Limit gain
                
                return audio * gain
                
            except Exception as e:
                print(f"⚠️ Dynamic range optimization failed: {e}")
                return audio
        
        def _final_quality_optimization(self, audio: np.ndarray) -> np.ndarray:
            """Final quality optimization pass"""
            try:
                # Ensure finite values
                audio = np.nan_to_num(audio, nan=0.0, posinf=0.0, neginf=0.0)
                
                # Final normalization
                peak = np.max(np.abs(audio))
                if peak > 0.95:
                    audio = audio * (0.95 / peak)
                
                # Final filtering to remove any remaining artifacts
                try:
                    nyquist = self.sample_rate * 0.5
                    low_cutoff = 7500 / nyquist  # Remove very high frequencies
                    if low_cutoff < 0.99:
                        b, a = signal.butter(2, low_cutoff, btype='low')
                        audio = signal.filtfilt(b, a, audio)
                except:
                    pass  # Skip if filtering fails
                
                return audio
                
            except Exception as e:
                print(f"⚠️ Final optimization failed: {e}")
                return np.clip(audio, -1.0, 1.0)
        
        def _analyze_audio_quality(self, audio: np.ndarray) -> float:
            """Analyze and score audio quality"""
            try:
                # Basic quality metrics
                rms = np.sqrt(np.mean(audio**2))
                peak = np.max(np.abs(audio))
                
                # Dynamic range
                dynamic_range = peak / (rms + 1e-8)
                
                # Spectral analysis
                fft = np.fft.fft(audio[:min(len(audio), 22050)])  # 1 second max
                magnitude = np.abs(fft)
                freqs = np.fft.fftfreq(len(fft), 1/self.sample_rate)
                
                # Spectral centroid
                positive_freqs = freqs[:len(freqs)//2]
                positive_magnitude = magnitude[:len(magnitude)//2]
                if np.sum(positive_magnitude) > 0:
                    spectral_centroid = np.sum(positive_freqs * positive_magnitude) / np.sum(positive_magnitude)
                else:
                    spectral_centroid = 1000
                
                # Quality score calculation
                quality_score = 50  # Base score
                
                # RMS level (optimal around 0.1-0.3)
                if 0.05 <= rms <= 0.4:
                    quality_score += 20
                elif 0.01 <= rms <= 0.6:
                    quality_score += 10
                
                # Dynamic range (optimal around 3-8)
                if 2 <= dynamic_range <= 10:
                    quality_score += 15
                elif 1.5 <= dynamic_range <= 15:
                    quality_score += 8
                
                # Spectral characteristics
                if 800 <= spectral_centroid <= 3500:
                    quality_score += 15
                elif 500 <= spectral_centroid <= 5000:
                    quality_score += 8
                
                return min(100, max(0, quality_score))
                
            except Exception as e:
                print(f"⚠️ Quality analysis failed: {e}")
                return 50.0
    
    return OptimizedHinglishCloner()

def test_advanced_optimization():
    """Test the advanced optimization system"""
    print("🚀 Testing Advanced Hinglish Quality Optimization")
    print("=" * 70)
    
    # Test texts designed to challenge voice consistency
    test_texts = [
        "नमस्ते! How are you doing today?",  # Original issue
        "मैं बहुत खुश हूँ! This is working great.",  # Mixed emotions
        "Weather kaisa hai आज? It's really nice outside!",  # Weather talk
        "Hi दोस्त! कैसे हो तुम? I hope सब कुछ ठीक चल रहा है।",  # Casual conversation
        "आज का dinner बहुत tasty था and I really enjoyed it।",  # Food discussion
    ]
    
    try:
        # Create optimized cloner
        cloner = create_advanced_quality_optimizer()
        
        # Create enhanced reference audio (more realistic)
        duration = 8  # 8 seconds
        sample_rate = 22050
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        
        # Create more sophisticated voice-like signal
        fundamental = 160  # 160Hz fundamental
        signal_components = (
            0.4 * np.sin(2 * np.pi * fundamental * t) +      # Fundamental
            0.25 * np.sin(2 * np.pi * fundamental * 2 * t) +  # 2nd harmonic
            0.15 * np.sin(2 * np.pi * fundamental * 3 * t) +  # 3rd harmonic
            0.1 * np.sin(2 * np.pi * fundamental * 4 * t) +   # 4th harmonic
            0.05 * np.random.randn(len(t))  # Realistic noise
        )
        
        # Add natural voice modulation
        modulation = 1 + 0.08 * np.sin(2 * np.pi * 3 * t)  # 3Hz modulation
        formant_simulation = np.sin(2 * np.pi * 800 * t) * 0.1  # Formant
        
        enhanced_audio = signal_components * modulation + formant_simulation
        
        # Apply realistic envelope
        envelope = np.exp(-np.abs(t - duration/2) / (duration/3))
        enhanced_audio = enhanced_audio * envelope
        
        # Normalize
        enhanced_audio = enhanced_audio / np.max(np.abs(enhanced_audio)) * 0.7
        
        # Enhanced voice features
        voice_features = {
            'audio_data': enhanced_audio.tolist(),
            'sample_rate': sample_rate,
            'duration': duration,
            'pitch_mean': 160.0,
            'pitch_std': 20.0,
            'rms_energy': float(np.sqrt(np.mean(enhanced_audio**2))),
            'spectral_centroid': 2200.0,
            'spectral_rolloff': 4200.0,
            'zero_crossing_rate': 0.08
        }
        
        print(f"🎤 Enhanced voice reference created: {duration}s, RMS: {voice_features['rms_energy']:.4f}")
        
        results = []
        
        for i, text in enumerate(test_texts):
            print(f"\n📝 Advanced Test {i+1}: '{text}'")
            print("-" * 50)
            
            # Test optimization
            optimized = cloner.optimize_text_for_voice_cloning(text)
            print(f"📝 Optimized: '{optimized}'")
            
            # Generate with advanced parameters
            try:
                output_path = f"advanced_hinglish_{i+1}.wav"
                
                print(f"🎵 Generating with advanced optimization...")
                result_path = cloner.clone_voice_multilingual(
                    text=text,
                    voice_features=voice_features,
                    output_path=output_path,
                    enhance_quality=True
                )
                
                # Analyze result
                if os.path.exists(result_path):
                    audio, sr = librosa.load(result_path, sr=None)
                    duration = len(audio) / sr
                    rms = np.sqrt(np.mean(audio**2))
                    
                    # Advanced consistency analysis
                    quality_metrics = analyze_advanced_quality(audio, sr)
                    
                    print(f"✅ Generated: {duration:.2f}s")
                    print(f"📊 RMS: {rms:.4f}")
                    print(f"🎯 Consistency: {quality_metrics['consistency_score']:.1f}/100")
                    print(f"🎵 Voice quality: {quality_metrics['voice_quality']:.1f}/100")
                    
                    results.append({
                        'text': text,
                        'file': output_path,
                        'duration': duration,
                        'rms': rms,
                        'consistency': quality_metrics['consistency_score'],
                        'quality': quality_metrics['voice_quality']
                    })
                    
                else:
                    print("❌ File not generated")
                    
            except Exception as e:
                print(f"❌ Generation failed: {e}")
                continue
        
        # Summary
        print(f"\n🎉 Advanced Optimization Results:")
        print("=" * 50)
        
        if results:
            avg_consistency = np.mean([r['consistency'] for r in results])
            avg_quality = np.mean([r['quality'] for r in results])
            
            print(f"📊 Average Consistency: {avg_consistency:.1f}/100")
            print(f"🎵 Average Quality: {avg_quality:.1f}/100")
            
            print(f"\n📁 Generated files:")
            for result in results:
                print(f"   ✅ {result['file']} - Quality: {result['quality']:.1f}/100")
        else:
            print("❌ No files generated successfully")
            
    except Exception as e:
        print(f"❌ Advanced optimization test failed: {e}")
        import traceback
        traceback.print_exc()

def analyze_advanced_quality(audio: np.ndarray, sr: int) -> dict:
    """Analyze audio quality with advanced metrics"""
    try:
        # Consistency analysis (RMS variation)
        window_size = int(0.1 * sr)  # 100ms windows
        rms_windows = []
        for i in range(0, len(audio) - window_size, window_size//2):
            window_rms = np.sqrt(np.mean(audio[i:i+window_size]**2))
            rms_windows.append(window_rms)
        
        rms_std = np.std(rms_windows) if rms_windows else 0
        consistency_score = max(0, 100 - (rms_std * 2000))  # Lower variation = higher score
        
        # Voice quality analysis
        overall_rms = np.sqrt(np.mean(audio**2))
        peak = np.max(np.abs(audio))
        dynamic_range = peak / (overall_rms + 1e-8)
        
        # Spectral quality
        fft = np.fft.fft(audio[:min(len(audio), sr)])
        magnitude = np.abs(fft)
        freqs = np.fft.fftfreq(len(fft), 1/sr)
        
        # Quality score based on multiple factors
        voice_quality = 50  # Base score
        
        # RMS level
        if 0.05 <= overall_rms <= 0.3:
            voice_quality += 25
        elif 0.02 <= overall_rms <= 0.5:
            voice_quality += 15
        
        # Dynamic range
        if 2 <= dynamic_range <= 8:
            voice_quality += 25
        elif 1.5 <= dynamic_range <= 12:
            voice_quality += 15
        
        return {
            'consistency_score': consistency_score,
            'voice_quality': voice_quality,
            'rms_variation': rms_std,
            'dynamic_range': dynamic_range,
            'overall_rms': overall_rms
        }
        
    except Exception as e:
        print(f"⚠️ Quality analysis failed: {e}")
        return {
            'consistency_score': 50.0,
            'voice_quality': 50.0,
            'rms_variation': 0.0,
            'dynamic_range': 1.0,
            'overall_rms': 0.1
        }

if __name__ == "__main__":
    test_advanced_optimization()
