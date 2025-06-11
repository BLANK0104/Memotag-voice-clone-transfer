# filepath: e:\Projects\VOice self\app\voice_cloner_multilingual.py
"""
Enhanced Multilingual Voice Cloner for Hindi-English Mixed Text
Optimized for perfect voice characteristic preservation in code-mixed scenarios
"""

import os
import sys
import torch
import librosa
import soundfile as sf
import numpy as np
import re
from typing import Optional, Dict, Any, List, Tuple
import hashlib
from datetime import datetime
from scipy import signal

class MultilingualVoiceCloner:
    """Enhanced Voice Cloner for multilingual and code-mixed text"""
    
    # Class-level model cache to persist across instances
    _model_cache = None
    _model_loaded = False
    
    def __init__(self):
        """Initialize with enhanced multilingual support"""
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model_name = "tts_models/multilingual/multi-dataset/xtts_v2"
        self.sample_rate = 22050
        
        # Enhanced language detection patterns
        self.hindi_pattern = re.compile(r'[\u0900-\u097F]+')  # Devanagari script
        self.english_pattern = re.compile(r'[a-zA-Z]+')
        
        print(f"[*] MultilingualVoiceCloner initialized on device: {self.device}")
        print("[*] Enhanced for Hindi-English code-mixed text")
        
        # Load model immediately for better performance
        self._ensure_model_loaded()
    
    def _ensure_model_loaded(self):
        """Load the TTS model if not already loaded (class-level caching)"""
        if not MultilingualVoiceCloner._model_loaded:
            try:
                print("📥 Loading XTTS-v2 model for multilingual synthesis...")
                
                # Import matplotlib workaround
                try:
                    import matplotlib
                    matplotlib.use('Agg')  # Use non-GUI backend
                except ImportError:
                    pass
                
                from TTS.api import TTS
                MultilingualVoiceCloner._model_cache = TTS(self.model_name).to(self.device)
                MultilingualVoiceCloner._model_loaded = True
                print("✅ Multilingual model loaded successfully and cached!")
                
            except Exception as e:
                print(f"❌ Error loading model: {e}")
                raise
        else:
            print("⚡ Using cached model - no loading needed!")
    
    @property
    def tts(self):
        """Get the cached TTS model"""
        self._ensure_model_loaded()
        return MultilingualVoiceCloner._model_cache
    def detect_text_language_segments(self, text: str) -> List[Tuple[str, str]]:
        """
        Detect language segments in mixed Hindi-English text
        Returns list of (segment, language) tuples
        """
        segments = []
        words = text.split()
        
        for word in words:
            # Remove punctuation for detection
            clean_word = re.sub(r'[^\w\u0900-\u097F]', '', word)
            
            if self.hindi_pattern.search(clean_word):
                segments.append((word, "hi"))
            elif self.english_pattern.search(clean_word):
                segments.append((word, "en"))
            else:  # Default to Hindi for mixed/unknown
                segments.append((word, "hi"))
        
        return segments
    
    def optimize_text_for_voice_cloning(self, text: str) -> str:
        """
        Optimize text for better voice characteristic preservation in Hinglish content
        Enhanced to prevent XTTS internal sentence splitting and improve speed
        """
        # Store original text for debugging
        original_text = text
        
        # Quick return for very short text
        if len(text) <= 20:
            return text.strip()
          # Normalize whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Detect if this is Hinglish content to apply special preprocessing
        segments = self.detect_text_language_segments(text)
        hindi_ratio = sum(1 for _, lang in segments if lang == "hi") / len(segments) if segments else 0
        is_hinglish = 0.2 < hindi_ratio < 0.8  # Mixed content
        
        # FIXED: Apply punctuation removal to ALL text to prevent XTTS splitting
        # Whether it's pure Hindi, pure English, or mixed - all need this fix
        print(f"🚨 REMOVING ALL SPLITTING PUNCTUATION to prevent voice bleeding")
        print(f"   Hindi ratio: {hindi_ratio:.2f} ({'Hinglish' if is_hinglish else 'Pure language'})")
        
        # Remove ALL punctuation that causes XTTS internal splitting
        text = re.sub(r'[!।?]', ' ', text)  # Remove ! । ? completely
        text = re.sub(r'[,;:]', ' ', text)  # Remove commas, semicolons, colons
        text = re.sub(r'\.(?=\s)', ' ', text)  # Replace periods followed by space
        text = re.sub(r'\.$', '', text)  # Remove period at end
          # Remove any quotation marks and other splitting characters
        text = re.sub(r'["""''`]', '', text)  # Remove quotes
        text = re.sub(r'[-–—]', ' ', text)  # Replace dashes with space
        
        if is_hinglish:
            print(f"🔧 Applying additional Hinglish-specific optimizations...")
            # Additional Hinglish-specific processing only
            
            # Remove excessive punctuation that might cause splitting
            text = re.sub(r'[,]{2,}', ',', text)  # Multiple commas
            text = re.sub(r'[.]{2,}', '.', text)  # Multiple periods
            
            # Ensure smooth transitions between languages  
            # Add minimal pause markers only when necessary
            text = re.sub(r'([a-zA-Z])(\s{2,})([अ-ह])', r'\1 \3', text)  # English to Hindi (remove multiple spaces)
            text = re.sub(r'([अ-ह])(\s{2,})([a-zA-Z])', r'\1 \3', text)  # Hindi to English (remove multiple spaces)
            
        else:
            # For non-Hinglish content, apply minimal changes
            # Remove excessive punctuation that might cause splitting
            text = re.sub(r'[।]{2,}', '।', text)  # Multiple devanagari periods
            text = re.sub(r'[.]{2,}', '.', text)  # Multiple periods
            
            # Gentle pause optimization - don't add too many pauses
            text = re.sub(r'([।.!?])\s*([^\s])', r'\1 \2', text)
        
        # Final cleanup
        # Ensure proper spacing around remaining punctuation
        text = re.sub(r'([,.])([^\s])', r'\1 \2', text)
        
        # Remove any double spaces
        text = re.sub(r'\s+', ' ', text)
        
        # Log the optimization for debugging
        if len(text) != len(original_text) or text != original_text:
            print(f"📝 Text optimized for voice consistency and speed:")
            print(f"   Original: '{original_text[:100]}...' ({len(original_text)} chars)")
            print(f"   Optimized: '{text[:100]}...' ({len(text)} chars)")
        
        return text
    def extract_voice_features(self, audio_path: str) -> Dict[str, Any]:
        """
        Extract comprehensive voice features for multilingual cloning
        Enhanced for better characteristic preservation
        """
        try:
            print(f"🎤 Extracting voice features from: {audio_path}")
            
            # Load audio with high quality
            audio, sr = librosa.load(audio_path, sr=None)
            
            # Resample to model's expected sample rate if needed
            if sr != self.sample_rate:
                audio = librosa.resample(audio, orig_sr=sr, target_sr=self.sample_rate)
            
            # Extract pitch characteristics safely
            pitches, magnitudes = librosa.piptrack(y=audio, sr=self.sample_rate, threshold=0.1)
            pitch_values = []
            for t in range(pitches.shape[1]):
                index = magnitudes[:, t].argmax()
                pitch = pitches[index, t]
                if pitch > 0:
                    pitch_values.append(pitch)
            
            if len(pitch_values) > 0:
                pitch_mean = float(np.mean(pitch_values))
                pitch_std = float(np.std(pitch_values))
            else:
                pitch_mean = 150.0  # Default pitch
                pitch_std = 25.0
            
            # Enhanced feature extraction for voice characteristics
            features = {
                "audio_data": audio.tolist(),  # Raw audio for voice cloning
                "sample_rate": self.sample_rate,
                "duration": len(audio) / self.sample_rate,
                
                # Pitch characteristics
                "pitch_mean": pitch_mean,
                "pitch_std": pitch_std,
                
                # Spectral characteristics for voice timbre
                "spectral_centroid": float(np.mean(librosa.feature.spectral_centroid(y=audio, sr=self.sample_rate))),
                "spectral_rolloff": float(np.mean(librosa.feature.spectral_rolloff(y=audio, sr=self.sample_rate))),
                "spectral_bandwidth": float(np.mean(librosa.feature.spectral_bandwidth(y=audio, sr=self.sample_rate))),
                
                # Voice quality indicators
                "zero_crossing_rate": float(np.mean(librosa.feature.zero_crossing_rate(audio))),
                "rms_energy": float(np.mean(librosa.feature.rms(y=audio))),
                
                # MFCC features for voice characteristics
                "mfcc_features": librosa.feature.mfcc(y=audio, sr=self.sample_rate, n_mfcc=13).tolist(),
                
                # Metadata
                "extraction_timestamp": datetime.now().isoformat(),
                "audio_hash": hashlib.md5(audio.tobytes()).hexdigest()
            }
            
            print(f"✅ Voice features extracted (duration: {features['duration']:.2f}s)")
            return features
            
        except Exception as e:
            print(f"❌ Error extracting voice features: {e}")
            raise
    
    def clone_voice_multilingual(self, text: str, voice_features: Dict[str, Any], 
                                output_path: str, enhance_quality: bool = True) -> str:
        """
        Generate speech with multilingual support and enhanced voice preservation
        """
        try:
            self._ensure_model_loaded()
            print(f"🎯 Generating multilingual speech: '{text[:50]}...'")
            print(f"💾 Voice features loaded (duration: {voice_features.get('duration', 0):.2f}s)")
            
            # Optimize text for multilingual synthesis
            optimized_text = self.optimize_text_for_voice_cloning(text)
            print(f"📝 Optimized text: '{optimized_text[:50]}...'")
            
            # Detect language composition
            segments = self.detect_text_language_segments(text)
            hindi_ratio = sum(1 for _, lang in segments if lang == "hi") / len(segments)
            print(f"🌐 Language composition: {hindi_ratio*100:.1f}% Hindi, {(1-hindi_ratio)*100:.1f}% English")
            
            # Reconstruct audio from features
            reference_audio = np.array(voice_features["audio_data"])
              # Use primary language based on content
            primary_language = "hi" if hindi_ratio > 0.3 else "en"
            
            # Generate speech with enhanced settings for voice preservation
            print(f"🎵 Synthesizing with primary language: {primary_language}")
            
            # Create output directory if needed
            output_dir = os.path.dirname(output_path)
            if output_dir:  # Only create directory if output_path contains a directory
                os.makedirs(output_dir, exist_ok=True)
              # Create temporary speaker file for TTS
            temp_speaker_path = "temp_speaker_multilingual.wav"
            sf.write(temp_speaker_path, reference_audio, self.sample_rate)
            
            try:
                # Generate speech with optimized parameters for voice characteristic preservation
                # FIXED: Force split_sentences=False to prevent voice bleeding and inconsistency
                print(f"🔧 FIXED: Using split_sentences=False to prevent voice language bleeding")
                print(f"🌐 Text length: {len(optimized_text)} chars, Hindi ratio: {hindi_ratio:.2f}")
                  # Enhanced TTS parameters to prevent internal splitting and optimize speed
                tts_params = {
                    "text": optimized_text,
                    "speaker_wav": temp_speaker_path,
                    "language": primary_language,
                    "split_sentences": False,  # FIXED: Always False to prevent voice bleeding
                    "speed": 1.0,  # Normal speed for better quality
                    # CRITICAL: Additional parameters to force single-pass generation
                    "do_trim": False,  # Don't trim audio (can cause splitting)
                    "use_microphone": False,  # Ensure consistent processing
                }
                  # Add speed optimization parameters for faster generation
                if hasattr(self.tts, 'tts') and hasattr(self.tts.tts, 'model'):
                    # Try to access speed optimization parameters
                    try:
                        print(f"🎵 Generating with NATURAL parameters (single chunk)...")
                        print(f"   Language: {primary_language}")
                        print(f"   Text: '{optimized_text}'")
                        
                        # FAST generation parameters - optimized for speed without quality loss
                        generated_audio = self.tts.tts(
                            **tts_params,
                            # Speed optimization parameters
                            temperature=0.75,  # Slightly higher for faster generation
                            length_penalty=1.0,  # Neutral
                            repetition_penalty=1.0,  # Neutral
                            # These help reduce generation time
                            use_deepspeed=False,  # Disable if available for consistency
                        )
                    except (TypeError, AttributeError):
                        # Fallback to basic fast parameters
                        print("⚡ Using optimized basic parameters for speed")
                        generated_audio = self.tts.tts(**tts_params)
                else:
                    generated_audio = self.tts.tts(**tts_params)
                    
            finally:
                # Clean up temporary file
                if os.path.exists(temp_speaker_path):
                    os.remove(temp_speaker_path)
            
            # Ensure we have a numpy array
            if not isinstance(generated_audio, np.ndarray):
                generated_audio = np.array(generated_audio)
            
            # SPEED OPTIMIZATION: Minimal audio processing for faster results
            print("🔧 Applying minimal audio cleanup...")
            
            # Only essential cleanup for speed
            generated_audio = self._clean_audio_artifacts(generated_audio)
            
            # Skip heavy processing if not requested or for speed
            if enhance_quality and len(optimized_text) < 100:  # Only for short text
                print("🎨 Applying quality enhancement...")
                generated_audio = self._enhance_audio_quality(generated_audio, voice_features)
            else:
                print("⚡ Skipping heavy processing for speed")
            
            # Minimal final cleanup
            generated_audio = self._minimal_final_cleanup(generated_audio)
            
            # Save generated audio
            sf.write(output_path, generated_audio, self.sample_rate)
            
            # Performance analysis
            duration = len(generated_audio) / self.sample_rate
            rms = np.sqrt(np.mean(generated_audio**2))
            
            print(f"✅ FIXED audio generated: {output_path}")
            print(f"📊 Duration: {duration:.2f}s (expected: 2-8s for normal sentences)")
            print(f"🔊 RMS level: {rms:.3f}")
            
            if duration > 12:
                print("⚠️  WARNING: Duration unusually long - check text complexity")
            
            return output_path
            
        except Exception as e:
            print(f"❌ Error generating multilingual speech: {e}")
            raise
    
    def _enhance_audio_quality(self, audio: np.ndarray, voice_features: Dict[str, Any]) -> np.ndarray:
        """
        Post-process audio to better match original voice characteristics
        """
        try:
            # Normalize audio level to match reference
            target_rms = voice_features.get("rms_energy", 0.1)
            current_rms = np.sqrt(np.mean(audio**2))
            
            if current_rms > 0:
                audio = audio * (target_rms / current_rms)
            
            # Apply gentle filtering to match spectral characteristics
            target_centroid = voice_features.get("spectral_centroid", 2000)
            
            # Simple high-pass/low-pass adjustment based on spectral centroid
            if target_centroid < 1500:  # Lower voice
                # Emphasize lower frequencies slightly
                audio = audio * 0.95  # Gentle adjustment
            elif target_centroid > 3000:  # Higher voice
                # Emphasize higher frequencies slightly
                audio = audio * 1.05  # Gentle adjustment
            
            # Ensure audio is in valid range
            audio = np.clip(audio, -1.0, 1.0)
            
            return audio
            
        except Exception as e:
            print(f"⚠️ Warning: Audio enhancement failed: {e}")
            return audio
    
    def validate_audio_quality(self, audio_path: str) -> Dict[str, Any]:
        """
        Validate audio quality for multilingual voice cloning
        """
        try:
            audio, sr = librosa.load(audio_path, sr=None)
            duration = len(audio) / sr
            
            # Enhanced validation for multilingual content
            issues = []
            recommendations = []
            
            # Duration check - more lenient for multilingual samples
            if duration < 3:
                issues.append("Audio too short for reliable multilingual cloning")
                recommendations.append("Use audio samples of at least 5-10 seconds for better results")
            elif duration > 60:
                issues.append("Audio very long - may contain too much variation")
                recommendations.append("Consider using a 10-30 second clear segment")
            
            # Quality checks
            rms = np.sqrt(np.mean(audio**2))
            if rms < 0.01:
                issues.append("Audio level too low")
                recommendations.append("Increase audio volume or use a better recording")
            
            # Silence detection
            silence_thresh = 0.01
            silence_ratio = np.sum(np.abs(audio) < silence_thresh) / len(audio)
            if silence_ratio > 0.7:
                issues.append("Too much silence in audio")
                recommendations.append("Use audio with more continuous speech")
            
            return {
                "is_valid": len(issues) == 0,
                "duration": duration,
                "issues": issues,
                "recommendations": recommendations,
                "quality_score": max(0, 100 - len(issues) * 25),
                "sample_rate": sr,
                "rms_level": float(rms),
                "silence_ratio": float(silence_ratio)
            }
            
        except Exception as e:
            return {
                "is_valid": False,
                "issues": [f"Audio validation failed: {str(e)}"],
                "recommendations": ["Check if the audio file is valid and accessible"]
            }
    
    def preprocess_audio(self, input_path: str, output_path: str):
        """
        Preprocess audio for optimal multilingual voice cloning
        """
        try:
            print(f"🔧 Preprocessing audio for multilingual cloning: {input_path}")
            
            # Load audio
            audio, sr = librosa.load(input_path, sr=None)
            
            # Normalize sample rate
            if sr != self.sample_rate:
                audio = librosa.resample(audio, orig_sr=sr, target_sr=self.sample_rate)
            
            # Normalize volume (gentle normalization to preserve voice characteristics)
            peak = np.max(np.abs(audio))
            if peak > 0:
                audio = audio / peak * 0.8  # Normalize to 80% to avoid clipping
              # Remove very short silence gaps that might affect voice characteristic extraction
            audio = librosa.effects.trim(audio, top_db=30)[0]
            
            # Create output directory if needed
            output_dir = os.path.dirname(output_path)
            if output_dir:  # Only create directory if output_path contains a directory
                os.makedirs(output_dir, exist_ok=True)
            
            # Save preprocessed audio
            sf.write(output_path, audio, self.sample_rate)
            
            print(f"✅ Audio preprocessed and saved: {output_path}")
        except Exception as e:
            print(f"❌ Error preprocessing audio: {e}")
            raise
    
    def clone_voice(self, text: str, voice_features: Dict[str, Any], output_path: str) -> str:
        """
        Compatibility method for existing code - calls the multilingual cloning method
        """
        return self.clone_voice_multilingual(text, voice_features, output_path)
    
    def _clean_audio_artifacts(self, audio: np.ndarray) -> np.ndarray:
        """
        Clean up artifacts, weird sounds, and noise at the beginning and end of generated audio
        Enhanced for Hinglish content with better artifact detection
        """
        try:
            print("🧹 Cleaning audio artifacts (Hinglish optimized)...")
            
            # Convert to float32 for processing
            if audio.dtype != np.float32:
                audio = audio.astype(np.float32)
              # Remove DC offset
            audio = audio - np.mean(audio)
            
            # Apply high-pass filter to remove low-frequency artifacts that are common in Hinglish TTS
            nyquist = self.sample_rate * 0.5
            high_cutoff = 85 / nyquist  # Remove frequencies below 85Hz (common TTS artifacts)
            b, a = signal.butter(2, high_cutoff, btype='high')
            audio = signal.filtfilt(b, a, audio)
            
            # Enhanced trimming for Hinglish content
            # Use energy-based detection to find actual speech content
            window_size = int(0.02 * self.sample_rate)  # 20ms windows
            energy = np.array([
                np.sum(audio[i:i+window_size]**2) 
                for i in range(0, len(audio)-window_size, window_size//2)
            ])
            
            # Find the start and end of actual speech content
            energy_threshold = np.max(energy) * 0.01  # 1% of max energy
            valid_frames = np.where(energy > energy_threshold)[0]
            
            if len(valid_frames) > 0:
                start_idx = valid_frames[0] * window_size // 2
                end_idx = min((valid_frames[-1] + 2) * window_size // 2, len(audio))
                audio = audio[start_idx:end_idx]
            
            # Additional artifact removal for TTS-generated content
            # Remove outliers that don't fit the voice profile
            audio_abs = np.abs(audio)
            q99 = np.percentile(audio_abs, 99)
            audio = np.clip(audio, -q99, q99)
            
            # Apply fade-in/fade-out to prevent clicks and pops
            fade_samples = min(int(0.03 * self.sample_rate), len(audio) // 15)  # 30ms or 6.7% of audio
            
            if fade_samples > 0:
                # Smooth fade in
                fade_in = np.power(np.linspace(0, 1, fade_samples), 2)  # Quadratic fade for smoother transition
                audio[:fade_samples] *= fade_in
                
                # Smooth fade out
                fade_out = np.power(np.linspace(1, 0, fade_samples), 2)
                audio[-fade_samples:] *= fade_out
            
            print(f"✅ Hinglish audio cleaned and optimized")
            return audio
            
        except Exception as e:
            print(f"⚠️ Warning: Audio cleanup failed: {e}")
            return audio
    
    def _precise_silence_removal(self, audio: np.ndarray) -> np.ndarray:
        """
        Remove silence and artifacts more precisely from start and end
        """
        try:
            # Calculate RMS in small windows to find speech boundaries
            window_size = int(0.025 * self.sample_rate)  # 25ms windows
            hop_size = int(0.010 * self.sample_rate)     # 10ms hop
            
            # Calculate RMS for each window
            rms_values = []
            for i in range(0, len(audio) - window_size, hop_size):
                window = audio[i:i + window_size]
                rms = np.sqrt(np.mean(window**2))
                rms_values.append(rms)
            
            if len(rms_values) == 0:
                return audio
            
            rms_values = np.array(rms_values)
            
            # Find noise floor (lowest 10% of RMS values)
            noise_floor = np.percentile(rms_values, 10)
            
            # Speech threshold (3x noise floor, but with minimum threshold)
            speech_threshold = max(noise_floor * 3, 0.01)
            
            # Find first and last speech regions
            speech_frames = rms_values > speech_threshold
            
            if not np.any(speech_frames):
                # If no speech detected, return trimmed version
                return librosa.effects.trim(audio, top_db=30)[0]
            
            # Find speech boundaries
            first_speech = np.argmax(speech_frames)
            last_speech = len(speech_frames) - 1 - np.argmax(speech_frames[::-1])
            
            # Convert frame indices to sample indices
            start_sample = max(0, first_speech * hop_size - window_size)
            end_sample = min(len(audio), (last_speech + 1) * hop_size + window_size)
            
            return audio[start_sample:end_sample]
            
        except Exception as e:
            print(f"⚠️ Warning: Precise silence removal failed: {e}")
            return librosa.effects.trim(audio, top_db=30)[0]
    
    def _final_audio_cleanup(self, audio: np.ndarray) -> np.ndarray:
        """
        Final cleanup pass to remove any remaining artifacts
        """       
        try:
            print("🔧 Final audio cleanup...")
            
            # Remove any remaining outliers (extreme values that might be artifacts)
            # Clip extreme values that are likely artifacts
            audio_std = np.std(audio)
            audio_mean = np.mean(audio)
            clip_threshold = audio_std * 4  # 4 standard deviations
            
            audio = np.clip(audio, 
                          audio_mean - clip_threshold, 
                          audio_mean + clip_threshold)
            
            # Apply gentle high-pass filter to remove very low frequency artifacts
            # These often cause the "weird" sounds at the beginning/end
            try:
                # High-pass filter at 80Hz to remove low-frequency artifacts
                nyquist = self.sample_rate / 2
                high_cutoff = 80 / nyquist
                
                if high_cutoff < 0.99:  # Make sure filter is valid
                    b, a = signal.butter(2, high_cutoff, btype='high')
                    audio = signal.filtfilt(b, a, audio)
            except Exception as filter_error:
                print(f"⚠️ Warning: High-pass filtering failed: {filter_error}")
                # Continue without filtering
            
            # Normalize to prevent clipping while preserving dynamics
            peak = np.max(np.abs(audio))
            if peak > 0.95:
                audio = audio * (0.95 / peak)
            
            # Ensure audio is finite and valid
            audio = np.nan_to_num(audio, nan=0.0, posinf=0.0, neginf=0.0)
            
            print("✅ Final cleanup completed")
            return audio
            
        except Exception as e:
            print(f"⚠️ Warning: Final cleanup failed: {e}")
            # Fallback: just normalize and clip
            audio = np.clip(audio, -1.0, 1.0)
            return audio
        
    def _minimal_final_cleanup(self, audio: np.ndarray) -> np.ndarray:
        """
        Minimal final cleanup for speed - only essential processing
        """
        try:
            print("✅ Minimal cleanup completed")
            
            # Only basic normalization and clipping for speed
            if len(audio) == 0:
                return audio
            
            # Remove DC offset
            audio = audio - np.mean(audio)
            
            # Basic normalization to prevent clipping
            peak = np.max(np.abs(audio))
            if peak > 0:
                audio = audio / peak * 0.95
            
            # Very basic trimming (remove long silences only)
            audio, _ = librosa.effects.trim(audio, top_db=25)
            
            # Minimal fade to prevent clicks
            if len(audio) > 220:  # 10ms at 22kHz
                fade_samples = 110  # 5ms fade
                fade_in = np.linspace(0, 1, fade_samples)
                fade_out = np.linspace(1, 0, fade_samples)
                audio[:fade_samples] *= fade_in
                audio[-fade_samples:] *= fade_out
            
            return audio
            
        except Exception as e:
            print(f"⚠️ Minimal cleanup failed: {e}")
            # Return basic normalized audio
            if len(audio) > 0:
                peak = np.max(np.abs(audio))
                if peak > 0:
                    return audio / peak * 0.95
            return audio

# Compatibility function for existing code
def clone_voice(text: str, voice_features: Dict[str, Any], output_path: str) -> str:
    """Compatibility function for existing code"""
    cloner = MultilingualVoiceCloner()
    return cloner.clone_voice_multilingual(text, voice_features, output_path)
