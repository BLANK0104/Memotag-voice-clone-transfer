"""
Hinglish Chatbot using OpenAI GPT-3.5-turbo
Supports mixed Hindi-English conversations with context awareness
"""

import os
import json
import logging
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime
from dotenv import load_dotenv

import openai
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionMessageParam

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)

class HinglishOpenAIChatbot:
    """
    A sophisticated Hinglish chatbot powered by OpenAI GPT-3.5-turbo
    Supports mixed Hindi-English conversations with cultural context
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the Hinglish OpenAI chatbot"""
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable.")
        
        # Initialize OpenAI client
        self.client = AsyncOpenAI(api_key=self.api_key)          # System prompt for Hinglish conversation
        self.system_prompt = """You are a friendly and knowledgeable AI assistant who speaks in natural Hinglish (Hindi + English mix). You understand all languages but respond in conversational Hinglish using Roman script.

PERSONALITY & STYLE:
- Speak naturally in Hinglish like a modern Indian person
- Mix Hindi and English words naturally as Indians do in daily conversation
- Be warm, helpful, and culturally aware
- Maintain respectful and polite tone

LANGUAGE GUIDELINES:
- Respond in natural Hinglish using Roman script (not Devanagari)
- Mix English and Hindi words naturally: "Good morning! Aap kaise hain?"
- Use common Hindi words: hai, hain, hun, kya, kaise, aap, main, bahut, theek, achha
- Use English words for: technical terms, modern concepts, common expressions
- Examples: "Computer programming bahut interesting hai", "Screen ko clear kar do"
- Keep it conversational: "Haan yaar, bilkul right kaha tumne!"

CULTURAL CONTEXT:
- Understand Indian cultural references, festivals, food, traditions
- Be aware of regional variations in language and culture
- Use appropriate respectful terms (ji, sahab, etc.) when suitable
- Understand context of Indian family relationships and social structures

RESPONSE STYLE:
- Keep responses conversational and friendly in Hinglish
- Ask follow-up questions to engage the user
- Use emotions and expressions common in Indian conversations: "Arre wah!", "Kya baat hai!", "Bilkul sahi"
- Be helpful with both local Indian and international topics
- Make it sound like a natural Indian conversation

IMPORTANT: Always respond in natural Hinglish using Roman script. This makes it sound more conversational and relatable to Indian users.

Remember: You're having a casual conversation with an Indian friend. Mix Hindi and English naturally like Indians do every day!"""
        
        # Conversation context
        self.conversation_history: List[Dict[str, str]] = []
        self.max_history_length = 20  # Keep last 20 exchanges for context
        
        logger.info("HinglishOpenAIChatbot initialized successfully")
    
    def add_to_history(self, role: str, content: str):
        """Add message to conversation history"""
        self.conversation_history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
          # Keep history manageable
        if len(self.conversation_history) > self.max_history_length * 2:
            # Remove oldest messages but keep pairs
            self.conversation_history = self.conversation_history[-self.max_history_length:]
    
    def get_context_messages(self) -> List[ChatCompletionMessageParam]:
        """Format conversation history for OpenAI API"""
        messages: List[ChatCompletionMessageParam] = []
        
        # Add system prompt as the first message
        messages.append({
            "role": "system",
            "content": self.system_prompt
        })
        
        # Add conversation history
        for msg in self.conversation_history[-10:]:  # Last 10 messages for context
            if msg["role"] in ["user", "assistant"]:
                messages.append({
                    "role": msg["role"],  # type: ignore
                    "content": msg["content"]
                })
        
        return messages
    
    async def get_response(self, user_message: str, context: Optional[Dict] = None) -> Tuple[str, Dict]:
        """
        Get response from OpenAI GPT-3.5-turbo for user message
        
        Args:
            user_message: User's input message in Hinglish
            context: Additional context (conversation_id, user_info, etc.)
            
        Returns:
            Tuple of (response_text, metadata)
        """
        try:
            # Add user message to history
            self.add_to_history("user", user_message)
            
            # Prepare context with conversation history
            messages = self.get_context_messages()
            
            # Add current user message with context if provided
            current_message = user_message
            if context:
                context_info = self._format_context(context)
                if context_info:
                    current_message += f"\n\nContext: {context_info}"
            
            messages.append({
                "role": "user",
                "content": current_message
            })
            
            logger.info(f"Sending message to OpenAI: {user_message[:100]}...")
              # Generate response using OpenAI
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=1000,
                temperature=0.7,
                top_p=0.9
            )
            
            # Handle response with proper None checking
            response_content = response.choices[0].message.content
            response_text = response_content.strip() if response_content else "Sorry, I couldn't generate a response."
            
            # Add assistant response to history
            self.add_to_history("assistant", response_text)
            
            # Prepare metadata with safe access to usage
            usage_info = {}
            if response.usage:
                usage_info = {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            
            metadata = {
                "model": "gpt-3.5-turbo",
                "timestamp": datetime.now().isoformat(),
                "usage": usage_info,
                "language_detected": self._detect_language_mix(user_message),
                "response_language": self._detect_language_mix(response_text),
                "context_used": bool(context)
            }
            
            logger.info(f"Generated response: {response_text[:100]}...")
            return response_text, metadata
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            error_response = "Sorry, मुझे कुछ problem हो रही है। कृपया थोड़ी देर बाद try करें।"
            metadata = {
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "model": "gpt-3.5-turbo"
            }
            return error_response, metadata
    
    def _format_context(self, context: Dict) -> str:
        """Format additional context for the conversation"""
        context_parts = []
        
        if context.get('user_name'):
            context_parts.append(f"User name: {context['user_name']}")
        
        if context.get('time_of_day'):
            context_parts.append(f"Time: {context['time_of_day']}")
        
        if context.get('conversation_topic'):
            context_parts.append(f"Topic: {context['conversation_topic']}")
        
        if context.get('user_preferences'):
            prefs = context['user_preferences']
            if isinstance(prefs, dict):
                pref_items = [f"{k}: {v}" for k, v in prefs.items()]
                context_parts.append(f"User preferences: {', '.join(pref_items)}")
        
        return "; ".join(context_parts) if context_parts else ""
    
    def _detect_language_mix(self, text: str) -> Dict[str, float]:
        """
        Simple language detection for Hinglish text
        Returns estimated percentages of Hindi and English
        """
        if not text:
            return {"hindi": 0.0, "english": 0.0}
        
        # Simple heuristic based on character sets and common words
        total_chars = len(text)
        if total_chars == 0:
            return {"hindi": 0.0, "english": 0.0}
        
        # Count Devanagari characters
        hindi_chars = sum(1 for char in text if '\u0900' <= char <= '\u097F')
        
        # Count common Hindi words in Roman script
        hindi_words = [
            'hai', 'hain', 'hun', 'ho', 'ke', 'ki', 'ka', 'main', 'mein', 
            'aap', 'tum', 'kya', 'kaise', 'kaun', 'kab', 'kahan', 'kyun',
            'nahi', 'nahin', 'haan', 'ji', 'acha', 'theek', 'sab', 'kuch',
            'bahut', 'thoda', 'zyada', 'kam', 'bhi', 'to', 'se', 'me', 'par'
        ]
        
        text_lower = text.lower()
        roman_hindi_count = sum(1 for word in hindi_words if word in text_lower)
        
        # Estimate Hindi percentage
        hindi_score = (hindi_chars + roman_hindi_count * 3) / total_chars
        hindi_percentage = min(hindi_score * 100, 100.0)
        english_percentage = max(100.0 - hindi_percentage, 0.0)
        
        return {
            "hindi": round(hindi_percentage, 2),
            "english": round(english_percentage, 2)
        }
    
    def clear_conversation(self):
        """Clear conversation history"""
        self.conversation_history.clear()
        logger.info("Conversation history cleared")
    
    def get_conversation_summary(self) -> Dict:
        """Get summary of current conversation"""
        if not self.conversation_history:
            return {"message_count": 0, "language_mix": {"hindi": 0, "english": 0}}
        
        total_messages = len(self.conversation_history)
        user_messages = [msg for msg in self.conversation_history if msg["role"] == "user"]
        assistant_messages = [msg for msg in self.conversation_history if msg["role"] == "assistant"]
        
        # Calculate average language mix
        all_text = " ".join([msg["content"] for msg in self.conversation_history])
        language_mix = self._detect_language_mix(all_text)
        
        return {
            "message_count": total_messages,
            "user_messages": len(user_messages),
            "assistant_messages": len(assistant_messages),
            "language_mix": language_mix,
            "start_time": self.conversation_history[0]["timestamp"] if self.conversation_history else None,
            "last_message_time": self.conversation_history[-1]["timestamp"] if self.conversation_history else None
        }
    
    def set_conversation_context(self, conversation_history: List[Dict]):
        """Load existing conversation history"""
        self.conversation_history = conversation_history
        logger.info(f"Loaded {len(conversation_history)} messages into context")

# Example usage and testing
if __name__ == "__main__":
    import asyncio
    
    async def test_chatbot():
        """Test the Hinglish OpenAI chatbot"""
        print("Testing Hinglish OpenAI Chatbot...")
        
        try:
            chatbot = HinglishOpenAIChatbot()
            
            # Test messages
            test_messages = [
                "Namaste! Kaise ho aap?",
                "मैं ठीक हूँ। आप कैसे हैं?",
                "Main ek Hindi-English chatbot के बारे में जानना चाहता हूँ।",
                "Can you tell me about Indian festivals in Hinglish?",
                "Diwali के बारे में बताइए।"
            ]
            
            for message in test_messages:
                print(f"\nUser: {message}")
                response, metadata = await chatbot.get_response(message)
                print(f"Bot: {response}")
                print(f"Language Mix: {metadata.get('language_detected', {})}")
                
            # Test conversation summary
            summary = chatbot.get_conversation_summary()
            print(f"\nConversation Summary: {summary}")
            
        except Exception as e:
            print(f"Error testing chatbot: {e}")
    
    # Run test
    asyncio.run(test_chatbot())
