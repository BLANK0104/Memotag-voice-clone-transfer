"""
Audio Utilities for Voice Cloning
"""

import os
import librosa
import soundfile as sf
import numpy as np
from pydub import AudioSegment
from typing import Tuple, Optional
import matplotlib.pyplot as plt
from scipy import signal

class AudioProcessor:
    """Audio processing utilities"""
    
    def __init__(self, sample_rate: int = 22050):
        self.sample_rate = sample_rate
    
    def load_audio(self, file_path: str, target_sr: Optional[int] = None) -> Tuple[np.ndarray, int]:
        """Load audio file with optional resampling"""
        try:
            sr = target_sr or self.sample_rate
            audio, _ = librosa.load(file_path, sr=sr)
            return audio, sr
        except Exception as e:
            raise ValueError(f"Error loading audio file: {e}")
    
    def save_audio(self, audio: np.ndarray, file_path: str, sample_rate: int):
        """Save audio to file"""
        try:
            sf.write(file_path, audio, sample_rate)
            return True
        except Exception as e:
            print(f"Error saving audio: {e}")
            return False
    
    def normalize_audio(self, audio: np.ndarray) -> np.ndarray:
        """Normalize audio to [-1, 1] range"""
        max_val = np.max(np.abs(audio))
        if max_val > 0:
            return audio / max_val
        return audio
    
    def trim_silence(self, audio: np.ndarray, threshold: float = 0.01) -> np.ndarray:
        """Remove silence from beginning and end of audio"""
        # Find first and last non-silent samples
        non_silent = np.where(np.abs(audio) > threshold)[0]
        
        if len(non_silent) == 0:
            return audio
        
        start_idx = non_silent[0]
        end_idx = non_silent[-1] + 1
        
        return audio[start_idx:end_idx]
    
    def apply_noise_reduction(self, audio: np.ndarray, noise_factor: float = 0.1) -> np.ndarray:
        """Simple noise reduction using spectral subtraction"""
        # Compute STFT
        stft = librosa.stft(audio)
        magnitude = np.abs(stft)
        phase = np.angle(stft)
        
        # Estimate noise from first few frames
        noise_frames = magnitude[:, :5]
        noise_spectrum = np.mean(noise_frames, axis=1, keepdims=True)
        
        # Spectral subtraction
        clean_magnitude = magnitude - noise_factor * noise_spectrum
        clean_magnitude = np.maximum(clean_magnitude, 0.1 * magnitude)
        
        # Reconstruct audio
        clean_stft = clean_magnitude * np.exp(1j * phase)
        clean_audio = librosa.istft(clean_stft)
        
        return clean_audio
    
    def enhance_voice(self, audio: np.ndarray, sample_rate: int) -> np.ndarray:
        """Enhance voice quality"""
        # Apply pre-emphasis filter
        pre_emphasis = 0.97
        emphasized = np.append(audio[0], audio[1:] - pre_emphasis * audio[:-1])
        
        # Apply bandpass filter for voice frequencies (80-8000 Hz)
        nyquist = sample_rate / 2
        low_freq = 80 / nyquist
        high_freq = 8000 / nyquist
        
        b, a = signal.butter(4, [low_freq, high_freq], btype='band')
        filtered = signal.filtfilt(b, a, emphasized)
        
        return self.normalize_audio(filtered)
    
    def detect_voice_activity(self, audio: np.ndarray, sample_rate: int, 
                            frame_length: int = 2048, hop_length: int = 512) -> np.ndarray:
        """Detect voice activity in audio"""
        # Compute energy
        energy = librosa.feature.rms(y=audio, frame_length=frame_length, hop_length=hop_length)[0]
        
        # Compute spectral centroid
        spectral_centroid = librosa.feature.spectral_centroid(y=audio, sr=sample_rate)[0]
        
        # Compute zero crossing rate
        zcr = librosa.feature.zero_crossing_rate(audio, frame_length=frame_length, hop_length=hop_length)[0]
        
        # Simple VAD based on energy and spectral features
        energy_threshold = np.mean(energy) * 0.3
        spectral_threshold = np.mean(spectral_centroid) * 0.5
        zcr_threshold = np.mean(zcr) * 2
        
        voice_activity = (energy > energy_threshold) & \
                        (spectral_centroid > spectral_threshold) & \
                        (zcr < zcr_threshold)
        
        return voice_activity
    
    def convert_format(self, input_path: str, output_path: str, output_format: str = "wav") -> bool:
        """Convert audio file format using pydub"""
        try:
            audio = AudioSegment.from_file(input_path)
            
            # Convert to mono if stereo
            if audio.channels > 1:
                audio = audio.set_channels(1)
            
            # Set sample rate
            audio = audio.set_frame_rate(self.sample_rate)
            
            # Export in desired format
            audio.export(output_path, format=output_format)
            return True
            
        except Exception as e:
            print(f"Error converting audio format: {e}")
            return False
    
    def split_audio(self, audio: np.ndarray, sample_rate: int, 
                   chunk_duration: float = 10.0) -> list:
        """Split audio into chunks of specified duration"""
        chunk_samples = int(chunk_duration * sample_rate)
        chunks = []
        
        for i in range(0, len(audio), chunk_samples):
            chunk = audio[i:i + chunk_samples]
            if len(chunk) >= chunk_samples * 0.5:  # Keep chunks that are at least 50% of target size
                chunks.append(chunk)
        
        return chunks
    
    def create_spectrogram(self, audio: np.ndarray, sample_rate: int, 
                          output_path: Optional[str] = None) -> np.ndarray:
        """Create and optionally save spectrogram"""
        # Compute spectrogram
        stft = librosa.stft(audio)
        spectrogram = np.abs(stft)
        
        # Convert to dB scale
        spectrogram_db = librosa.amplitude_to_db(spectrogram, ref=np.max)
        
        if output_path:
            plt.figure(figsize=(12, 6))
            librosa.display.specshow(spectrogram_db, sr=sample_rate, x_axis='time', y_axis='hz')
            plt.colorbar(format='%+2.0f dB')
            plt.title('Spectrogram')
            plt.tight_layout()
            plt.savefig(output_path)
            plt.close()
        
        return spectrogram_db
    
    def analyze_audio_quality(self, audio: np.ndarray, sample_rate: int) -> dict:
        """Analyze audio quality metrics"""
        try:
            # Basic metrics
            duration = len(audio) / sample_rate
            rms_energy = np.sqrt(np.mean(audio**2))
            peak_amplitude = np.max(np.abs(audio))
            
            # Dynamic range
            dynamic_range = 20 * np.log10(peak_amplitude / (rms_energy + 1e-8))
            
            # Signal-to-noise ratio estimate
            # Assume noise is in the quietest 10% of the signal
            sorted_audio = np.sort(np.abs(audio))
            noise_floor = np.mean(sorted_audio[:int(0.1 * len(sorted_audio))])
            signal_power = rms_energy
            snr = 20 * np.log10(signal_power / (noise_floor + 1e-8))
            
            # Spectral features
            spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=audio, sr=sample_rate))
            spectral_bandwidth = np.mean(librosa.feature.spectral_bandwidth(y=audio, sr=sample_rate))
            spectral_rolloff = np.mean(librosa.feature.spectral_rolloff(y=audio, sr=sample_rate))
            
            # Zero crossing rate
            zcr = np.mean(librosa.feature.zero_crossing_rate(audio))
            
            # MFCC features
            mfccs = librosa.feature.mfcc(y=audio, sr=sample_rate, n_mfcc=13)
            mfcc_mean = np.mean(mfccs, axis=1)
            mfcc_std = np.std(mfccs, axis=1)
            
            return {
                'duration': duration,
                'sample_rate': sample_rate,
                'rms_energy': float(rms_energy),
                'peak_amplitude': float(peak_amplitude),
                'dynamic_range_db': float(dynamic_range),
                'snr_estimate_db': float(snr),
                'spectral_centroid': float(spectral_centroid),
                'spectral_bandwidth': float(spectral_bandwidth),
                'spectral_rolloff': float(spectral_rolloff),
                'zero_crossing_rate': float(zcr),
                'mfcc_mean': mfcc_mean.tolist(),
                'mfcc_std': mfcc_std.tolist()
            }
            
        except Exception as e:
            print(f"Error analyzing audio quality: {e}")
            return {}

class VoiceMetrics:
    """Voice-specific audio analysis"""
    
    @staticmethod
    def extract_pitch_contour(audio: np.ndarray, sample_rate: int) -> dict:
        """Extract detailed pitch contour"""
        try:
            # Use librosa's piptrack for pitch detection
            pitches, magnitudes = librosa.core.piptrack(y=audio, sr=sample_rate, threshold=0.1)
            
            # Extract pitch values over time
            pitch_contour = []
            for t in range(pitches.shape[1]):
                index = magnitudes[:, t].argmax()
                pitch = pitches[index, t]
                pitch_contour.append(pitch if pitch > 0 else 0)
            
            pitch_contour = np.array(pitch_contour)
            valid_pitches = pitch_contour[pitch_contour > 0]
            
            if len(valid_pitches) > 0:
                return {
                    'mean_pitch': float(np.mean(valid_pitches)),
                    'std_pitch': float(np.std(valid_pitches)),
                    'min_pitch': float(np.min(valid_pitches)),
                    'max_pitch': float(np.max(valid_pitches)),
                    'pitch_range': float(np.max(valid_pitches) - np.min(valid_pitches)),
                    'pitch_contour': pitch_contour.tolist()
                }
            else:
                return {'error': 'No pitch detected'}
                
        except Exception as e:
            return {'error': f'Pitch extraction failed: {e}'}
    
    @staticmethod
    def extract_formants(audio: np.ndarray, sample_rate: int, n_formants: int = 4) -> dict:
        """Extract formant frequencies"""
        try:
            # Pre-emphasis
            pre_emphasis = 0.97
            emphasized = np.append(audio[0], audio[1:] - pre_emphasis * audio[:-1])
            
            # Window the signal
            windowed = emphasized * np.hanning(len(emphasized))
            
            # Apply FFT
            fft = np.fft.fft(windowed)
            magnitude = np.abs(fft)
            freqs = np.fft.fftfreq(len(fft), 1/sample_rate)
            
            # Keep only positive frequencies
            half_len = len(magnitude) // 2
            magnitude = magnitude[:half_len]
            freqs = freqs[:half_len]
            
            # Find peaks (potential formants)
            from scipy.signal import find_peaks
            peaks, properties = find_peaks(magnitude, height=np.max(magnitude) * 0.1, distance=20)
            
            # Get formant frequencies
            formant_freqs = freqs[peaks]
            formant_amps = magnitude[peaks]
            
            # Sort by amplitude and take top n_formants
            sorted_indices = np.argsort(formant_amps)[::-1]
            top_formants = formant_freqs[sorted_indices[:n_formants]]
            top_formants = np.sort(top_formants)  # Sort by frequency
            
            formants = {}
            for i, freq in enumerate(top_formants):
                formants[f'F{i+1}'] = float(freq)
            
            # Fill missing formants
            for i in range(len(top_formants), n_formants):
                formants[f'F{i+1}'] = 0.0
            
            return formants
            
        except Exception as e:
            return {'error': f'Formant extraction failed: {e}'}
    
    @staticmethod
    def extract_voice_quality(audio: np.ndarray, sample_rate: int) -> dict:
        """Extract voice quality measures"""
        try:
            # Jitter (pitch period variation)
            pitches, _ = librosa.core.piptrack(y=audio, sr=sample_rate)
            pitch_periods = []
            
            for t in range(pitches.shape[1]):
                pitch = np.max(pitches[:, t])
                if pitch > 0:
                    period = sample_rate / pitch
                    pitch_periods.append(period)
            
            if len(pitch_periods) > 1:
                pitch_periods = np.array(pitch_periods)
                jitter = np.std(pitch_periods) / np.mean(pitch_periods) * 100
            else:
                jitter = 0.0
            
            # Shimmer (amplitude variation)
            rms = librosa.feature.rms(y=audio, frame_length=2048, hop_length=512)[0]
            if len(rms) > 1:
                shimmer = np.std(rms) / np.mean(rms) * 100
            else:
                shimmer = 0.0
            
            # Harmonics-to-noise ratio (HNR)
            # Simplified estimation using spectral features
            stft = librosa.stft(audio)
            magnitude = np.abs(stft)
            
            # Estimate harmonic and noise components
            harmonic_strength = np.mean(np.max(magnitude, axis=0))
            noise_level = np.mean(np.std(magnitude, axis=0))
            hnr = 20 * np.log10(harmonic_strength / (noise_level + 1e-8))
            
            return {
                'jitter_percent': float(jitter),
                'shimmer_percent': float(shimmer),
                'hnr_db': float(hnr),
                'voice_quality_score': float(max(0, min(100, 100 - jitter - shimmer + hnr/10)))
            }
            
        except Exception as e:
            return {'error': f'Voice quality extraction failed: {e}'}
