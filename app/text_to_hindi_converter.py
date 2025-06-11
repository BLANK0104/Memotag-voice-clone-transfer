"""
Text to Hindi Converter using Google Gemini AI
Converts any input text (English, Hinglish, mixed) to pure Hindi
"""

import os
import logging
from typing import Optional
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

logger = logging.getLogger(__name__)

class TextToHindiConverter:
    """
    Converts any text to pure Hindi using Google Gemini AI
    """
    
    def __init__(self, api_key: str = None):
        """Initialize the text converter"""
        self.api_key = api_key or os.getenv('API_KEY_GEMINI')
        if not self.api_key:
            raise ValueError("Gemini API key is required. Set API_KEY_GEMINI environment variable.")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        
        # Initialize model with safety settings
        self.model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            safety_settings={
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            }
        )
          # System prompt for Hinglish to pure Hindi conversion
        self.conversion_prompt = """You are an expert Hinglish to Hindi converter. Your task is to convert Hinglish text (Hindi-English mix in Roman script) to pure Hindi using Devanagari script for voice generation.

CONVERSION RULES:
1. Convert ALL English words to their Hindi Devanagari equivalents
2. Convert Romanized Hindi words to proper Devanagari script
3. Keep the exact meaning and context
4. Use proper Hindi grammar and sentence structure
5. Convert English names/brands to Hindi phonetic equivalents
6. Use commonly understood Hindi words for better TTS pronunciation
7. Maintain the tone and emotion of the original text

HINGLISH TO HINDI EXAMPLES:
- "Good morning aap kaise hain?" → "सुप्रभात आप कैसे हैं?"
- "Computer programming bahut interesting hai" → "कंप्यूटर प्रोग्रामिंग बहुत दिलचस्प है"
- "Screen ko clear kar do" → "स्क्रीन को साफ़ कर दो"
- "Haan yaar bilkul right" → "हाँ यार बिल्कुल सही"
- "Main theek hun thanks" → "मैं ठीक हूँ धन्यवाद"
- "Kya baat hai!" → "क्या बात है!"
- "Phone pe call kar do" → "फोन पे कॉल कर दो"
- "Internet connection slow hai" → "इंटरनेट कनेक्शन धीमा है"
- "Very good achha laga" → "बहुत अच्छा अच्छा लगा"
- "Please help karo" → "कृपया मदद करो"

TECHNICAL WORD CONVERSIONS:
- "Computer" → "कंप्यूटर"
- "Mobile/Phone" → "मोबाइल/फोन"
- "Internet" → "इंटरनेट"
- "Clear" → "साफ़"
- "Screen" → "स्क्रीन"
- "Programming" → "प्रोग्रामिंग"
- "Connection" → "कनेक्शन"
- "Software" → "सॉफ्टवेयर"
- "Application/App" → "एप्लिकेशन/ऐप"

IMPORTANT:
- Output ONLY the Hindi text in Devanagari script, nothing else
- No explanations, no additional text
- Ensure proper Hindi pronunciation for TTS
- Maintain natural flow and readability
- Convert ALL Roman script to Devanagari"""
        
        logger.info("TextToHindiConverter initialized successfully")
    
    async def convert_to_hindi(self, text: str) -> str:
        """
        Convert any text to pure Hindi
        
        Args:
            text: Input text in any language/script
            
        Returns:
            str: Pure Hindi text in Devanagari script
        """
        try:
            if not text or not text.strip():
                return ""
            
            # Prepare the conversion prompt
            conversion_request = f"{self.conversion_prompt}\n\nText to convert: {text}\n\nHindi output:"
            
            logger.info(f"Converting to Hindi: {text[:50]}...")
            
            # Generate Hindi conversion
            response = await self.model.generate_content_async(conversion_request)
            hindi_text = response.text.strip()
            
            logger.info(f"Converted to Hindi: {hindi_text[:50]}...")
            return hindi_text
            
        except Exception as e:
            logger.error(f"Error converting text to Hindi: {str(e)}")
            # Fallback: if conversion fails, return original text
            return text
    
    def convert_to_hindi_sync(self, text: str) -> str:
        """
        Synchronous version of convert_to_hindi
        
        Args:
            text: Input text in any language/script
            
        Returns:
            str: Pure Hindi text in Devanagari script
        """
        try:
            if not text or not text.strip():
                return ""
            
            # Prepare the conversion prompt
            conversion_request = f"{self.conversion_prompt}\n\nText to convert: {text}\n\nHindi output:"
            
            logger.info(f"Converting to Hindi (sync): {text[:50]}...")
            
            # Generate Hindi conversion
            response = self.model.generate_content(conversion_request)
            hindi_text = response.text.strip()
            
            logger.info(f"Converted to Hindi (sync): {hindi_text[:50]}...")
            return hindi_text
            
        except Exception as e:
            logger.error(f"Error converting text to Hindi (sync): {str(e)}")
            # Fallback: if conversion fails, return original text
            return text

# Example usage and testing
if __name__ == "__main__":
    import asyncio
    
    async def test_converter():
        """Test the Hindi converter"""
        print("Testing Text to Hindi Converter...")
        
        try:
            converter = TextToHindiConverter()
            
            # Test texts
            test_texts = [
                "Clear the screen",
                "Good morning! How are you?",
                "Thank you very much",
                "I love coding in Python",
                "The weather is nice today",
                "Happy birthday to you",
                "Please call me later",
                "Computer programming is fun",
                "Mobile phone is ringing"
            ]
            
            for text in test_texts:
                print(f"\nOriginal: {text}")
                hindi_text = await converter.convert_to_hindi(text)
                print(f"Hindi: {hindi_text}")
                
        except Exception as e:
            print(f"Error testing converter: {e}")
    
    # Run test
    asyncio.run(test_converter())
