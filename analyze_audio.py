#!/usr/bin/env python3
"""
Analyze the generated audio to understand distortion patterns
"""

import soundfile as sf
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend
import matplotlib.pyplot as plt

def analyze_audio_distortion():
    """Analyze the test audio for distortion patterns"""
    try:
        # Load the generated audio
        audio, sr = sf.read('test_split_fix.wav')
        print(f"📊 Audio Analysis:")
        print(f"   Length: {len(audio)} samples")
        print(f"   Duration: {len(audio)/sr:.2f}s")
        print(f"   Sample rate: {sr}")
        print("")
        
        # Check the first few seconds for distortion
        first_2_seconds = audio[:int(2*sr)]
        middle_2_seconds = audio[int(2*sr):int(4*sr)] if len(audio) > int(4*sr) else audio[int(2*sr):]
        last_2_seconds = audio[-int(2*sr):] if len(audio) > int(2*sr) else audio
        
        print("🔍 Segment Analysis:")
        print(f"   First 2s RMS: {np.sqrt(np.mean(first_2_seconds**2)):.4f}")
        print(f"   Middle 2s RMS: {np.sqrt(np.mean(middle_2_seconds**2)):.4f}")
        print(f"   Last 2s RMS: {np.sqrt(np.mean(last_2_seconds**2)):.4f}")
        print("")
        
        print("📈 Amplitude Analysis:")
        print(f"   First 2s max: {np.max(np.abs(first_2_seconds)):.4f}")
        print(f"   Middle 2s max: {np.max(np.abs(middle_2_seconds)):.4f}")
        print(f"   Last 2s max: {np.max(np.abs(last_2_seconds)):.4f}")
        print("")
        
        # Check for sudden jumps or artifacts
        extreme_first = np.sum(np.abs(first_2_seconds) > 0.8)
        extreme_middle = np.sum(np.abs(middle_2_seconds) > 0.8)
        extreme_last = np.sum(np.abs(last_2_seconds) > 0.8)
        
        print("⚠️ Extreme Values (>0.8):")
        print(f"   First 2s: {extreme_first}")
        print(f"   Middle 2s: {extreme_middle}")
        print(f"   Last 2s: {extreme_last}")
        print("")
        
        # Check for silence at the beginning (common TTS artifact)
        silence_threshold = 0.01
        silence_samples = np.sum(np.abs(first_2_seconds) < silence_threshold)
        silence_ratio = silence_samples / len(first_2_seconds)
        
        print("🔇 Silence Analysis (first 2s):")
        print(f"   Silence samples: {silence_samples}")
        print(f"   Silence ratio: {silence_ratio:.2%}")
        print("")
        
        # Check for sudden onset (common cause of distortion)
        onset_samples = first_2_seconds[:int(0.1*sr)]  # First 100ms
        onset_rms = np.sqrt(np.mean(onset_samples**2))
        
        print("🎬 Onset Analysis (first 100ms):")
        print(f"   Onset RMS: {onset_rms:.4f}")
        print(f"   Sudden onset: {'YES' if onset_rms > 0.1 else 'NO'}")
        print("")
        
        # Detect if there are multiple segments (sign of sentence splitting)
        # Look for silent gaps that indicate sentence boundaries
        window_size = int(0.05 * sr)  # 50ms windows
        rms_windows = []
        for i in range(0, len(audio) - window_size, window_size):
            window = audio[i:i+window_size]
            rms = np.sqrt(np.mean(window**2))
            rms_windows.append(rms)
        
        # Find silent gaps (potential sentence boundaries)
        silence_threshold = 0.01
        silent_windows = np.array(rms_windows) < silence_threshold
        
        # Count segments separated by silence
        segments = 0
        in_silence = True
        for is_silent in silent_windows:
            if not is_silent and in_silence:
                segments += 1
                in_silence = False
            elif is_silent:
                in_silence = True
        
        print("🔄 Sentence Splitting Detection:")
        print(f"   Audio segments detected: {segments}")
        print(f"   Silent windows: {np.sum(silent_windows)}/{len(silent_windows)}")
        
        if segments > 1:
            print("   ⚠️ MULTIPLE SEGMENTS DETECTED - XTTS may still be splitting internally!")
        else:
            print("   ✅ Single continuous segment - no internal splitting detected")
        
        return {
            'duration': len(audio)/sr,
            'segments': segments,
            'first_2s_rms': np.sqrt(np.mean(first_2_seconds**2)),
            'onset_rms': onset_rms,
            'extreme_values_first': extreme_first
        }
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        return None

if __name__ == "__main__":
    print("🔧 Starting audio analysis...")
    result = analyze_audio_distortion()
    if result:
        print("\n✅ Analysis completed successfully!")
    else:
        print("\n❌ Analysis failed!")
