"""
Speech-to-Text module for Hinglish (Hindi-English) audio transcription
Supports multiple speech recognition engines with fallback options
"""

import os
import io
import json
import logging
import tempfile
from typing import Dict, Optional, Tuple, List
from pathlib import Path

import speech_recognition as sr
import numpy as np
from pydub import AudioSegment

logger = logging.getLogger(__name__)

class HinglishSpeechToText:
    """
    Speech-to-text conversion for Hinglish (Hindi-English mixed) audio
    Supports multiple recognition engines with automatic fallback
    """
    
    def __init__(self):
        """Initialize the speech recognition system"""
        self.recognizer = sr.Recognizer()
        
        # Configure recognition settings
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
        self.recognizer.operation_timeout = None
        self.recognizer.phrase_threshold = 0.3
        self.recognizer.non_speaking_duration = 0.5
        
        # Supported languages for recognition
        self.languages = {
            'hinglish': 'hi-IN',  # Hindi (India) - best for Hinglish
            'english': 'en-IN',   # English (India)
            'hindi': 'hi-IN',     # Pure Hindi
            'auto': 'hi-IN'       # Default to Hindi for mixed content
        }
        
        logger.info("HinglishSpeechToText initialized")
    
    def transcribe_audio_file(self, audio_path: str, language: str = 'hinglish') -> Dict:
        """
        Transcribe audio file to text
        
        Args:
            audio_path: Path to audio file
            language: Language hint ('hinglish', 'english', 'hindi', 'auto')
            
        Returns:
            Dict with transcript, confidence, and metadata
        """
        try:            # Convert audio to the required format if needed
            audio_path = self._prepare_audio_file(audio_path)
            
            # Load audio file
            with sr.AudioFile(audio_path) as source:
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                
                # Record the audio
                audio_data = self.recognizer.record(source)
            
            # Try multiple recognition methods
            results = self._try_multiple_recognizers(audio_data, language)
            
            # Clean up temporary files
            if audio_path != audio_path and Path(audio_path).exists():
                Path(audio_path).unlink()
            
            return results
            
        except Exception as e:
            logger.error(f"Error transcribing audio file: {str(e)}")
            return {
                "transcript": "",
                "confidence": 0.0,
                "language_detected": "unknown",
                "error": str(e),
                "success": False
            }
    
    def transcribe_audio_data(self, audio_data: bytes, language: str = 'hinglish') -> Dict:
        """
        Transcribe raw audio data to text
        
        Args:
            audio_data: Raw audio bytes
            language: Language hint for recognition
            
        Returns:
            Dict with transcript, confidence, and metadata
        """
        try:
            # Save audio data to temporary file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_path = temp_file.name
            
            # Transcribe the temporary file
            result = self.transcribe_audio_file(temp_path, language)
            
            # Clean up
            Path(temp_path).unlink()
            
            return result
            
        except Exception as e:
            logger.error(f"Error transcribing audio data: {str(e)}")
            return {
                "transcript": "",
                "confidence": 0.0,
                "language_detected": "unknown",
                "error": str(e),
                "success": False
            }
    
    def transcribe_microphone(self, duration: Optional[float] = None, language: str = 'hinglish') -> Dict:
        """
        Transcribe audio from microphone
        
        Args:
            duration: Recording duration in seconds (None for automatic)
            language: Language hint for recognition
            
        Returns:
            Dict with transcript, confidence, and metadata
        """
        try:
            with sr.Microphone() as source:
                logger.info("Listening from microphone...")
                
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                
                # Record audio
                if duration:
                    audio_data = self.recognizer.record(source, duration=duration)
                else:
                    audio_data = self.recognizer.listen(source, timeout=10, phrase_time_limit=30)
            
            # Try multiple recognition methods
            results = self._try_multiple_recognizers(audio_data, language)
            
            return results
            
        except sr.WaitTimeoutError:
            logger.warning("Microphone listening timeout")
            return {
                "transcript": "",
                "confidence": 0.0,
                "language_detected": "unknown",
                "error": "Listening timeout",
                "success": False
            }
        except Exception as e:
            logger.error(f"Error transcribing microphone: {str(e)}")
            return {
                "transcript": "",
                "confidence": 0.0,
                "language_detected": "unknown",
                "error": str(e),
                "success": False
            }
    
    def _try_multiple_recognizers(self, audio_data, language: str) -> Dict:
        """Try multiple speech recognition engines with fallback"""
        
        lang_code = self.languages.get(language, 'hi-IN')
        results = {"transcript": "", "confidence": 0.0, "success": False}
          # Method 1: Google Speech Recognition (Primary)
        try:
            transcript = self.recognizer.recognize_google(
                audio_data, 
                language=lang_code,
                show_all=False
            )
            
            if transcript and isinstance(transcript, str):
                confidence = 0.85  # Google doesn't provide confidence, estimate high
                detected_lang = self._detect_language(transcript)
                
                return {
                    "transcript": transcript.strip(),
                    "confidence": confidence,
                    "language_detected": detected_lang,
                    "method": "google",
                    "success": True
                }
        except sr.UnknownValueError:
            logger.debug("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            logger.warning(f"Google Speech Recognition error: {e}")
        except Exception as e:
            logger.warning(f"Google Speech Recognition unexpected error: {e}")
          # Method 2: Google Speech Recognition with all results
        try:
            all_results = self.recognizer.recognize_google(
                audio_data, 
                language=lang_code,
                show_all=True
            )
            
            if all_results and isinstance(all_results, dict) and 'alternative' in all_results:
                alternatives = all_results['alternative']
                if alternatives and len(alternatives) > 0:
                    best_result = alternatives[0]
                    transcript = best_result.get('transcript', '')
                    confidence = best_result.get('confidence', 0.7)
                    
                    if transcript and isinstance(transcript, str):
                        detected_lang = self._detect_language(transcript)
                        return {
                            "transcript": transcript.strip(),
                            "confidence": confidence,
                            "language_detected": detected_lang,
                            "method": "google_detailed",
                            "success": True
                        }
        except Exception as e:
            logger.debug(f"Google detailed recognition failed: {e}")
        
        # Method 3: Try different language codes
        fallback_languages = ['en-IN', 'hi-IN', 'en-US']
        for fallback_lang in fallback_languages:
            if fallback_lang == lang_code:
                continue
                
            try:
                transcript = self.recognizer.recognize_google(
                    audio_data,
                    language=fallback_lang
                )
                
                if transcript and isinstance(transcript, str):
                    confidence = 0.7  # Lower confidence for fallback
                    detected_lang = self._detect_language(transcript)
                    
                    return {
                        "transcript": transcript.strip(),
                        "confidence": confidence,
                        "language_detected": detected_lang,
                        "method": f"google_fallback_{fallback_lang}",
                        "success": True
                    }
            except Exception:
                continue
          # Method 4: Sphinx (offline fallback)
        try:
            transcript = self.recognizer.recognize_sphinx(audio_data)
            
            if transcript and isinstance(transcript, str):
                confidence = 0.5  # Lower confidence for offline recognition
                detected_lang = self._detect_language(transcript)
                
                return {
                    "transcript": transcript.strip(),
                    "confidence": confidence,
                    "language_detected": detected_lang,
                    "method": "sphinx_offline",
                    "success": True
                }
        except Exception as e:
            logger.debug(f"Sphinx recognition failed: {e}")
        
        # If all methods fail
        return {
            "transcript": "",
            "confidence": 0.0,
            "language_detected": "unknown",
            "method": "none",
            "error": "All recognition methods failed",
            "success": False
        }
    
    def _prepare_audio_file(self, audio_path: str) -> str:
        """Convert audio file to supported format if needed"""
        try:
            file_path = Path(audio_path)
            
            # Check if file exists
            if not file_path.exists():
                raise FileNotFoundError(f"Audio file not found: {audio_path}")
            
            # If already WAV, return as-is
            if file_path.suffix.lower() == '.wav':
                return str(file_path)
            
            # Convert to WAV format
            logger.info(f"Converting {file_path.suffix} to WAV format")
            
            # Load audio with pydub
            audio = AudioSegment.from_file(str(file_path))
            
            # Convert to mono, 16kHz, 16-bit (optimal for speech recognition)
            audio = audio.set_channels(1).set_frame_rate(16000).set_sample_width(2)
            
            # Create temporary WAV file
            temp_path = tempfile.mktemp(suffix='.wav')
            audio.export(temp_path, format='wav')
            
            return temp_path
            
        except Exception as e:
            logger.error(f"Error preparing audio file: {str(e)}")
            return str(audio_path)  # Return original path as fallback
    
    def _detect_language(self, text: str) -> str:
        """Simple language detection for transcript"""
        if not text:
            return "unknown"
        
        # Count Devanagari characters
        hindi_chars = sum(1 for char in text if '\u0900' <= char <= '\u097F')
        
        # Count English characters
        english_chars = sum(1 for char in text if char.isascii() and char.isalpha())
        
        # Count common Hindi words in Roman script
        hindi_words = ['hai', 'hain', 'hun', 'ho', 'main', 'mein', 'aap', 'kya', 'kaise']
        text_lower = text.lower()
        roman_hindi_count = sum(1 for word in hindi_words if word in text_lower)
        
        # Determine language
        if hindi_chars > 0:
            if english_chars > hindi_chars:
                return "hinglish"
            else:
                return "hindi"
        elif roman_hindi_count > 0:
            return "hinglish"
        elif english_chars > 0:
            return "english"
        else:
            return "unknown"
    
    def get_available_microphones(self) -> List[Dict]:
        """Get list of available microphone devices"""
        try:
            microphones = []
            for index, name in enumerate(sr.Microphone.list_microphone_names()):
                microphones.append({
                    "index": index,
                    "name": name
                })
            return microphones
        except Exception as e:
            logger.error(f"Error getting microphones: {str(e)}")
            return []
    
    def test_microphone(self, device_index: Optional[int] = None) -> Dict:
        """Test microphone functionality"""
        try:
            with sr.Microphone(device_index=device_index) as source:
                logger.info("Testing microphone... Say something!")
                
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                
                # Record a short test
                audio_data = self.recognizer.listen(source, timeout=5, phrase_time_limit=3)
            
            # Try to recognize the test audio
            result = self._try_multiple_recognizers(audio_data, 'hinglish')
            
            return {
                "success": True,
                "test_result": result,
                "message": "Microphone test completed"
            }
            
        except Exception as e:
            logger.error(f"Microphone test failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "Microphone test failed"
            }

# Example usage and testing
if __name__ == "__main__":
    import asyncio
    
    def test_speech_to_text():
        """Test the speech-to-text functionality"""
        print("Testing Hinglish Speech-to-Text...")
        
        try:
            stt = HinglishSpeechToText()
            
            # Test microphone list
            mics = stt.get_available_microphones()
            print(f"Available microphones: {len(mics)}")
            for mic in mics[:3]:  # Show first 3
                print(f"  {mic['index']}: {mic['name']}")
            
            # Test microphone (uncomment to test)
            # print("\nTesting microphone (speak something in Hinglish)...")
            # result = stt.transcribe_microphone(duration=5, language='hinglish')
            # print(f"Transcript: {result.get('transcript', 'No speech detected')}")
            # print(f"Confidence: {result.get('confidence', 0):.2f}")
            # print(f"Language: {result.get('language_detected', 'unknown')}")
            
            print("Speech-to-Text module ready!")
            
        except Exception as e:
            print(f"Error testing speech-to-text: {e}")
    
    # Run test
    test_speech_to_text()