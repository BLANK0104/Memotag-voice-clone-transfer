# filepath: e:\Projects\VOice self\app\database.py
"""
Supabase Database Integration for Voice Cloning App
"""

import os
import json
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
from dotenv import load_dotenv

# Import Supabase
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    print("⚠️ Supabase not installed. Install with: pip install supabase")

load_dotenv()

class VoiceDatabase:

    """Database for voice storage using Supabase only"""
    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        
        # Check Supabase availability
        if not SUPABASE_AVAILABLE:
            raise Exception("Supabase client not available. Install with: pip install supabase")
        
        if not self.supabase_url or not self.supabase_key:
            raise Exception("Supabase credentials not found. Check your .env file for SUPABASE_URL and SUPABASE_KEY")
        
        try:
            self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
            print("✅ Connected to Supabase database")
            self._ensure_tables_exist()
        except Exception as e:
            raise Exception(f"Failed to connect to Supabase: {e}")
    
    def _ensure_tables_exist(self):
        """Ensure necessary tables exist in Supabase"""
        try:
            # Test table access
            result = self.supabase.table('voice_profiles').select("id").limit(1).execute()
            print("✅ Supabase tables verified")
        except Exception as e:
            print(f"⚠️ Could not verify Supabase tables: {e}")
            print("📝 Make sure to run the SQL script: create_supabase_table.sql")

    async def save_voice_profile(self, voice_name: str, voice_features: Dict[str, Any], 
                                 audio_path: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Save voice profile to Supabase database"""
        try:
            # Prepare data for Supabase
            voice_data = {
                "voice_name": voice_name,
                "voice_features": json.dumps(voice_features),  # Store as JSON string
                "audio_path": audio_path,
                "metadata": json.dumps(metadata or {}),  # Store as JSON string
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            # Check if voice already exists
            existing = self.supabase.table('voice_profiles').select("*").eq('voice_name', voice_name).execute()
            
            if existing.data:
                # Update existing voice
                result = self.supabase.table('voice_profiles').update({
                    "voice_features": voice_data["voice_features"],
                    "audio_path": voice_data["audio_path"],
                    "metadata": voice_data["metadata"],
                    "updated_at": voice_data["updated_at"]
                }).eq('voice_name', voice_name).execute()
                print(f"💾 Voice profile '{voice_name}' updated in Supabase")
            else:
                # Insert new voice
                result = self.supabase.table('voice_profiles').insert(voice_data).execute()
                print(f"💾 Voice profile '{voice_name}' saved to Supabase")
            
            return True
            
        except Exception as e:
            print(f"❌ Error saving to Supabase: {e}")
            return False

    async def get_voice_profile(self, voice_name: str) -> Optional[Dict[str, Any]]:
        """Retrieve voice profile from Supabase database"""
        try:
            result = self.supabase.table('voice_profiles').select("*").eq('voice_name', voice_name).execute()
            
            if result.data:
                voice_data = result.data[0]
                # Parse JSON strings back to objects
                voice_data['voice_features'] = json.loads(voice_data['voice_features'])
                voice_data['metadata'] = json.loads(voice_data['metadata'])
                print(f"📖 Voice profile '{voice_name}' retrieved from Supabase")
                return voice_data
            else:
                print(f"❌ Voice profile '{voice_name}' not found in Supabase")
                return None
            
        except Exception as e:
            print(f"❌ Error reading voice profile from Supabase: {e}")
            return None
    
    async def list_voice_profiles(self) -> List[Dict[str, Any]]:
        """List all voice profiles from Supabase database"""
        try:
            result = self.supabase.table('voice_profiles').select("*").execute()
            
            voices = []
            for voice_data in result.data:
                # Create summary with parsed metadata
                summary = {
                    "id": voice_data.get("id"),
                    "voice_name": voice_data.get("voice_name"),
                    "audio_path": voice_data.get("audio_path"),
                    "created_at": voice_data.get("created_at"),
                    "updated_at": voice_data.get("updated_at"),
                    "metadata": json.loads(voice_data.get("metadata", "{}"))
                }
                voices.append(summary)
            
            print(f"📋 Found {len(voices)} voice profiles in Supabase")
            return voices
            
        except Exception as e:
            print(f"❌ Error listing voices from Supabase: {e}")
            return []
    
    async def delete_voice_profile(self, voice_name: str) -> bool:
        """Delete voice profile from Supabase database"""
        try:
            result = self.supabase.table('voice_profiles').delete().eq('voice_name', voice_name).execute()
            
            if result.data:
                print(f"🗑️ Voice profile '{voice_name}' deleted from Supabase")
                return True
            else:
                print(f"❌ Voice profile '{voice_name}' not found in Supabase")
                return False
                
        except Exception as e:
            print(f"❌ Error deleting voice profile from Supabase: {e}")
            return False
    
    async def get_voice_features(self, voice_name: str) -> Optional[Dict[str, Any]]:
        """Get just the voice features for a specific voice"""
        try:
            result = self.supabase.table('voice_profiles').select("voice_features").eq('voice_name', voice_name).execute()
            
            if result.data:
                features_json = result.data[0]['voice_features']
                return json.loads(features_json)
            else:
                print(f"❌ Voice features for '{voice_name}' not found in Supabase")
                return None
                
        except Exception as e:
            print(f"❌ Error getting voice features from Supabase: {e}")
            return None
    
    async def update_voice_metadata(self, voice_name: str, metadata: Dict[str, Any]) -> bool:
        """Update just the metadata for a voice profile"""
        try:
            result = self.supabase.table('voice_profiles').update({
                "metadata": json.dumps(metadata),
                "updated_at": datetime.now().isoformat()
            }).eq('voice_name', voice_name).execute()
            
            if result.data:
                print(f"📝 Metadata updated for voice '{voice_name}' in Supabase")
                return True
            else:
                print(f"❌ Voice profile '{voice_name}' not found in Supabase")
                return False
                
        except Exception as e:
            print(f"❌ Error updating metadata in Supabase: {e}")
            return False
    
    async def search_voices(self, query: str) -> List[Dict[str, Any]]:
        """Search voice profiles by name or metadata"""
        try:
            all_voices = await self.list_voice_profiles()
            
            matching_voices = []
            query_lower = query.lower()
            
            for voice in all_voices:
                # Search in voice name
                if query_lower in voice["voice_name"].lower():
                    matching_voices.append(voice)
                    continue
                  # Search in metadata
                metadata = voice.get("metadata", {})
                metadata_str = json.dumps(metadata).lower()
                if query_lower in metadata_str:
                    matching_voices.append(voice)
            
            print(f"🔍 Found {len(matching_voices)} voices matching '{query}'")
            return matching_voices
        except Exception as e:
            print(f"❌ Error searching voices: {e}")
            return []
    
    # === CHATBOT METHODS ===
    
    async def create_conversation(self, user_id: str = "anonymous", title: str = "New Conversation",
                                language: str = "hinglish", metadata: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """Create a new conversation and return conversation ID"""
        try:
            # Use 'anonymous' for web interface users to comply with RLS policies
            if not user_id or user_id.startswith('web_client_'):
                user_id = 'anonymous'
                
            conversation_data = {
                "user_id": user_id,
                "title": title,
                "language": language,
                "metadata": json.dumps(metadata or {}),
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "is_active": True
            }
            
            result = self.supabase.table('conversations').insert(conversation_data).execute()
            
            if result.data:
                conversation_id = result.data[0]['id']
                print(f"✅ Conversation '{title}' created with ID: {conversation_id}")
                return conversation_id
            else:
                print("❌ Failed to create conversation")
                return None
                
        except Exception as e:
            print(f"❌ Error creating conversation: {e}")
            return None
    
    async def get_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Get conversation details by ID"""
        try:
            result = self.supabase.table('conversations').select("*").eq('id', conversation_id).execute()
            if result.data:
                conversation = result.data[0]
                conversation['metadata'] = json.loads(conversation.get('metadata', '{}'))
                return conversation
            else:
                print(f"❌ Conversation '{conversation_id}' not found")
                return None
                
        except Exception as e:
            print(f"❌ Error getting conversation: {e}")
            return None

    async def list_conversations(self, user_id: str = "anonymous", limit: int = 50) -> List[Dict[str, Any]]:
        """List user's conversations with message counts"""
        try:
            # Use 'anonymous' for web interface users to comply with RLS policies
            if not user_id or user_id.startswith('web_client_'):
                user_id = 'anonymous'
                
            # Get conversations first
            result = self.supabase.table('conversations').select("*").eq('user_id', user_id)\
                .eq('is_active', True).order('updated_at', desc=True).limit(limit).execute()
            
            conversations = []
            for conv in result.data:
                conv['metadata'] = json.loads(conv.get('metadata', '{}'))
                
                # Get message count for this conversation
                try:
                    msg_result = self.supabase.table('messages')\
                        .select("id")\
                        .eq('conversation_id', conv['id']).execute()
                    
                    conv['message_count'] = len(msg_result.data) if msg_result.data else 0
                except:
                    conv['message_count'] = 0
                
                # Get last message for preview
                try:
                    last_msg_result = self.supabase.table('messages').select("content")\
                        .eq('conversation_id', conv['id']).order('created_at', desc=True).limit(1).execute()
                    
                    conv['last_message'] = last_msg_result.data[0]['content'] if last_msg_result.data else "No messages yet"
                except:
                    conv['last_message'] = "No messages yet"
                
                conversations.append(conv)
            
            print(f"📋 Found {len(conversations)} conversations for user {user_id}")
            return conversations
            
        except Exception as e:
            print(f"❌ Error listing conversations: {e}")
            return []
    
    async def update_conversation(self, conversation_id: str, title: Optional[str] = None, 
                                metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Update conversation details"""
        try:
            update_data = {"updated_at": datetime.now().isoformat()}
            
            if title:
                update_data["title"] = title
            if metadata:
                update_data["metadata"] = json.dumps(metadata)
            
            result = self.supabase.table('conversations').update(update_data).eq('id', conversation_id).execute()
            
            if result.data:
                print(f"✅ Conversation '{conversation_id}' updated")
                return True
            else:
                print(f"❌ Conversation '{conversation_id}' not found")
                return False
                
        except Exception as e:
            print(f"❌ Error updating conversation: {e}")
            return False
    
    async def delete_conversation(self, conversation_id: str) -> bool:
        """Soft delete conversation by marking as inactive"""
        try:
            result = self.supabase.table('conversations').update({
                "is_active": False,
                "updated_at": datetime.now().isoformat()
            }).eq('id', conversation_id).execute()
            
            if result.data:
                print(f"🗑️ Conversation '{conversation_id}' deleted (marked inactive)")
                return True
            else:
                print(f"❌ Conversation '{conversation_id}' not found")
                return False
                
        except Exception as e:
            print(f"❌ Error deleting conversation: {e}")
            return False
    
    async def add_message(self, conversation_id: str, role: str, content: str, 
                         audio_path: Optional[str] = None, voice_used: Optional[str] = None,
                         metadata: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """Add a message to a conversation"""
        try:
            message_data = {
                "conversation_id": conversation_id,
                "role": role,
                "content": content,
                "audio_path": audio_path,
                "voice_used": voice_used,
                "metadata": json.dumps(metadata or {}),
                "created_at": datetime.now().isoformat()
            }
            
            result = self.supabase.table('messages').insert(message_data).execute()
            
            if result.data:
                message_id = result.data[0]['id']
                print(f"✅ Message added with ID: {message_id}")
                
                # Update conversation timestamp
                await self.update_conversation(conversation_id)
                
                return message_id
            else:
                print("❌ Failed to add message")
                return None
                
        except Exception as e:
            print(f"❌ Error adding message: {e}")
            return None
    
    async def get_conversation_messages(self, conversation_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all messages for a conversation"""
        try:
            result = self.supabase.table('messages').select("*").eq('conversation_id', conversation_id)\
                .order('created_at', desc=False).limit(limit).execute()
            
            messages = []
            for msg in result.data:
                msg['metadata'] = json.loads(msg.get('metadata', '{}'))
                messages.append(msg)
            
            print(f"📋 Found {len(messages)} messages for conversation {conversation_id}")
            return messages
            
        except Exception as e:
            print(f"❌ Error getting conversation messages: {e}")
            return []
    
    async def save_audio_transcript(self, message_id: str, transcript: str, 
                                  confidence: float = 0.0, language_detected: Optional[str] = None,
                                  metadata: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """Save audio transcript for a message"""
        try:
            transcript_data = {
                "message_id": message_id,
                "transcript": transcript,
                "confidence": confidence,
                "language_detected": language_detected,
                "metadata": json.dumps(metadata or {}),
                "created_at": datetime.now().isoformat()
            }
            
            result = self.supabase.table('audio_transcripts').insert(transcript_data).execute()
            
            if result.data:
                transcript_id = result.data[0]['id']
                print(f"✅ Audio transcript saved with ID: {transcript_id}")
                return transcript_id
            else:
                print("❌ Failed to save audio transcript")
                return None
                
        except Exception as e:
            print(f"❌ Error saving audio transcript: {e}")
            return None
    
    async def get_message_transcripts(self, message_id: str) -> List[Dict[str, Any]]:
        """Get all transcripts for a message"""
        try:
            result = self.supabase.table('audio_transcripts').select("*").eq('message_id', message_id)\
                .order('created_at', desc=False).execute()
            
            transcripts = []
            for transcript in result.data:
                transcript['metadata'] = json.loads(transcript.get('metadata', '{}'))
                transcripts.append(transcript)
            
            return transcripts
            
        except Exception as e:
            print(f"❌ Error getting message transcripts: {e}")
            return []

    # ... existing voice profile methods ...
