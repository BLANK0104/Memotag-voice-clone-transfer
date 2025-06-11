"""
WebSocket Server for Real-time Voice Cloning
"""

import os
import json
import asyncio
import uuid
import traceback
import base64
from typing import Dict, Any, Set
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
import uvicorn

try:
    from .database import VoiceDatabase
except ImportError:
    from database import VoiceDatabase

# Initialize FastAPI app
app = FastAPI(title="Voice Cloning API", version="1.0.0")

# Global voice cloner instance (will be initialized later)
voice_cloner = None

def get_voice_cloner():
    """Get or initialize FIXED voice cloner instance"""
    global voice_cloner
    if voice_cloner is None:
        try:
            # PRIORITY 1: Use the FIXED Hinglish cloner for best quality
            try:
                from .websocket_fixed_cloner import create_websocket_fixed_cloner
            except ImportError:
                from websocket_fixed_cloner import create_websocket_fixed_cloner
            voice_cloner = create_websocket_fixed_cloner()
            print("[+] 🚀 Using FIXED Hinglish voice cloner with optimized quality!")
            print("    ✅ Natural TTS parameters")
            print("    ✅ Minimal audio processing") 
            print("    ✅ Ultra-minimal text optimization")
        except Exception as e:
            print(f"[!] Cannot import FIXED cloner: {e}")
            print("[!] Falling back to basic multilingual cloner...")
            try:
                try:
                    from .voice_cloner_multilingual import MultilingualVoiceCloner
                except ImportError:
                    from voice_cloner_multilingual import MultilingualVoiceCloner
                voice_cloner = MultilingualVoiceCloner()
                print("[+] Using enhanced multilingual voice cloner")
            except Exception as e2:
                print(f"[!] Cannot import full voice cloner: {e2}")
                try:
                    try:
                        from .voice_cloner_simple import VoiceClonerSimple
                    except ImportError:
                        from voice_cloner_simple import VoiceClonerSimple
                    voice_cloner = VoiceClonerSimple()
                    print("[+] Using simplified voice cloner")
                except Exception as e3:
                    print(f"[!] Cannot import simplified voice cloner: {e3}")
                    raise ImportError("No voice cloner could be imported")
    return voice_cloner

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize components - database can be initialized immediately
voice_db = VoiceDatabase()

# Add startup event to preload the model
@app.on_event("startup")
async def startup_event():
    """Preload voice cloning model at startup for better performance"""
    try:
        print("🚀 Preloading voice cloning model for optimal performance...")
        # This will initialize and cache the model
        cloner = get_voice_cloner()
        print("✅ Voice cloning model preloaded successfully!")
    except Exception as e:
        print(f"⚠️ Could not preload model: {e}")
        print("Model will be loaded on first use.")

# Active WebSocket connections
active_connections: Set[WebSocket] = set()

class ConnectionManager:
    """Manage WebSocket connections"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        print(f"🔗 Client {client_id} connected")
    
    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            print(f"❌ Client {client_id} disconnected")
    
    async def send_personal_message(self, message: Dict[str, Any], client_id: str):
        if client_id in self.active_connections:
            websocket = self.active_connections[client_id]
            try:
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                print(f"❌ Error sending message to {client_id}: {e}")
                self.disconnect(client_id)
    
    async def broadcast(self, message: Dict[str, Any]):
        disconnected_clients = []
        for client_id, websocket in self.active_connections.items():
            try:
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                print(f"❌ Error broadcasting to {client_id}: {e}")
                disconnected_clients.append(client_id)
        
        # Clean up disconnected clients
        for client_id in disconnected_clients:
            self.disconnect(client_id)

manager = ConnectionManager()

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket endpoint for real-time communication"""
    await manager.connect(websocket, client_id)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Process different message types
            await handle_websocket_message(message, client_id)
            
    except WebSocketDisconnect:
        manager.disconnect(client_id)
    except Exception as e:
        print(f"❌ WebSocket error for client {client_id}: {e}")
        manager.disconnect(client_id)

async def handle_websocket_message(message: Dict[str, Any], client_id: str):
    """Handle incoming WebSocket messages"""
    try:
        message_type = message.get("type")
        
        if message_type == "ping":
            await manager.send_personal_message({"type": "pong"}, client_id)
        
        elif message_type == "list_voices":
            voices = await voice_db.list_voice_profiles()
            await manager.send_personal_message({
                "type": "voice_list",
                "voices": voices
            }, client_id)
        
        elif message_type == "generate_speech":
            await handle_speech_generation(message, client_id)
        
        elif message_type == "generate_speech_realtime":
            await handle_realtime_speech_generation(message, client_id)
        
        elif message_type == "get_voice_profile":
            voice_name = message.get("voice_name")
            if voice_name:
                profile = await voice_db.get_voice_profile(voice_name)
                await manager.send_personal_message({
                    "type": "voice_profile",
                    "voice_name": voice_name,
                    "profile": profile
                }, client_id)
        
        # Chatbot handlers
        elif message_type == "start_conversation":
            await handle_start_conversation(message, client_id)
        
        elif message_type == "chat_message":
            await handle_chat_message(message, client_id)
        
        elif message_type == "speech_to_text":
            await handle_speech_to_text(message, client_id)
        
        elif message_type == "list_conversations":
            await handle_list_conversations(message, client_id)
        
        elif message_type == "get_conversation":
            await handle_get_conversation(message, client_id)
        
        elif message_type == "delete_conversation":
            await handle_delete_conversation(message, client_id)
        
        else:
            await manager.send_personal_message({
                "type": "error",
                "message": f"Unknown message type: {message_type}"
            }, client_id)
    
    except Exception as e:
        await manager.send_personal_message({
            "type": "error",
            "message": f"Error processing message: {str(e)}"
        }, client_id)

async def handle_speech_generation(message: Dict[str, Any], client_id: str):
    """Handle speech generation request"""
    try:
        voice_name = message.get("voice_name")
        text = message.get("text")
        
        if not voice_name or not text:
            await manager.send_personal_message({
                "type": "error",
                "message": "Missing voice_name or text"
            }, client_id)
            return
        
        # Send progress update
        await manager.send_personal_message({
            "type": "progress",
            "message": "Retrieving voice profile...",
            "progress": 20
        }, client_id)
        
        # Get voice profile
        voice_profile = await voice_db.get_voice_profile(voice_name)
        if not voice_profile:
            await manager.send_personal_message({
                "type": "error",
                "message": f"Voice profile '{voice_name}' not found"
            }, client_id)
            return
        
        # Send progress update
        await manager.send_personal_message({
            "type": "progress",
            "message": "Generating speech...",
            "progress": 50
        }, client_id)
        
        # Generate output filename
        output_filename = f"generated_{voice_name}_{uuid.uuid4().hex[:8]}.wav"
        output_path = os.path.join("generated", output_filename)
          # Generate speech
        voice_features = voice_profile["voice_features"]
        generated_path = get_voice_cloner().clone_voice(text, voice_features, output_path)
        
        # Send completion message
        await manager.send_personal_message({
            "type": "speech_generated",
            "message": "Speech generated successfully!",
            "progress": 100,
            "audio_file": f"/download/{output_filename}",
            "voice_name": voice_name,
            "text": text
        }, client_id)
        
    except Exception as e:
        await manager.send_personal_message({
            "type": "error",
            "message": f"Error generating speech: {str(e)}"
        }, client_id)

async def handle_realtime_speech_generation(message: Dict[str, Any], client_id: str):
    """Handle real-time streaming speech generation request"""
    try:
        voice_name = message.get("voice_name")
        text = message.get("text")
        
        if not voice_name or not text:
            await manager.send_personal_message({
                "type": "error", 
                "message": "Missing voice_name or text"
            }, client_id)
            return
        
        # Send initial progress
        await manager.send_personal_message({
            "type": "realtime_started",
            "message": "Starting real-time generation...",
            "progress": 0
        }, client_id)
        
        # Get voice profile
        voice_profile = await voice_db.get_voice_profile(voice_name)
        if not voice_profile:
            await manager.send_personal_message({
                "type": "error",
                "message": f"Voice profile '{voice_name}' not found"
            }, client_id)        # Import FIXED real-time cloner
        try:
            try:
                from .voice_cloner_realtime_fixed import FixedRealTimeHinglishVoiceCloner
            except ImportError:
                from voice_cloner_realtime_fixed import FixedRealTimeHinglishVoiceCloner
            realtime_cloner = FixedRealTimeHinglishVoiceCloner()
            print("[+] 🚀 Using FIXED real-time cloner for optimal streaming quality!")
        except ImportError:
            print("[!] FIXED realtime cloner not available!")
            await manager.send_personal_message({
                "type": "error",
                "message": "Real-time cloner not available"
            }, client_id)
            return
        
        # Progress callback for streaming updates
        async def progress_callback(progress, message_text):
            await manager.send_personal_message({
                "type": "realtime_progress",
                "progress": progress,
                "message": message_text
            }, client_id)
        
        voice_features = voice_profile["voice_features"]
        chunk_count = 0
        
        # Stream audio chunks
        async for audio_chunk in realtime_cloner.clone_voice_realtime(text, voice_features, progress_callback):
            chunk_count += 1
            
            # Save chunk temporarily
            chunk_filename = f"realtime_{voice_name}_{client_id}_{chunk_count}.wav"
            chunk_path = os.path.join("temp", chunk_filename)
            
            # Ensure temp directory exists
            os.makedirs("temp", exist_ok=True)
            
            # Write chunk to file
            with open(chunk_path, 'wb') as f:
                f.write(audio_chunk)
            
            # Send chunk notification
            await manager.send_personal_message({
                "type": "audio_chunk",
                "chunk_id": chunk_count,
                "audio_file": f"/download/{chunk_filename}",
                "voice_name": voice_name,
                "is_final": False
            }, client_id)
        
        # Send completion message
        await manager.send_personal_message({
            "type": "realtime_complete",
            "message": f"Real-time generation completed! Generated {chunk_count} audio chunks.",
            "total_chunks": chunk_count,
            "voice_name": voice_name,
            "text": text        }, client_id)
        
    except Exception as e:
        await manager.send_personal_message({
            "type": "error",
            "message": f"Error in real-time generation: {str(e)}"
        }, client_id)

# Chatbot WebSocket Handlers

async def handle_start_conversation(message: Dict[str, Any], client_id: str):
    """Handle starting a new conversation"""
    try:
        user_id = message.get("user_id", client_id)  # Use client_id as fallback
        title = message.get("title", "New Hinglish Conversation")
        language = message.get("language", "hinglish")
        metadata = message.get("metadata", {})
        
        conversation_id = await voice_db.create_conversation(user_id, title, language, metadata)
        
        if conversation_id:
            await manager.send_personal_message({
                "type": "conversation_started",
                "conversation_id": conversation_id,
                "title": title,
                "language": language,
                "message": "New conversation started successfully"
            }, client_id)
        else:
            await manager.send_personal_message({
                "type": "error",
                "message": "Failed to create conversation"
            }, client_id)
            
    except Exception as e:
        await manager.send_personal_message({
            "type": "error",
            "message": f"Error starting conversation: {str(e)}"
        }, client_id)

async def handle_chat_message(message: Dict[str, Any], client_id: str):
    """Handle sending a chat message with AI response (OpenAI or Gemini)"""
    try:
        conversation_id = message.get("conversation_id")
        user_message = message.get("message")
        voice_name = message.get("voice_name")  # Voice to use for TTS
        audio_data = message.get("audio_data")  # Base64 encoded audio if from speech
        chatbot_provider = message.get("chatbot_provider", "openai")  # Default to OpenAI
        
        if not conversation_id or not user_message:
            await manager.send_personal_message({
                "type": "error",
                "message": "Missing conversation_id or message"
            }, client_id)
            return
        
        # Send progress update
        await manager.send_personal_message({
            "type": "chat_progress",
            "message": "Processing your message...",
            "progress": 20
        }, client_id)
        
        # Save user message to database
        user_message_id = await voice_db.add_message(
            conversation_id, "user", user_message, 
            metadata={"audio_provided": bool(audio_data), "chatbot_provider": chatbot_provider}
        )
        
        # If audio was provided, save transcript
        if audio_data and user_message_id:
            await voice_db.save_audio_transcript(
                user_message_id, user_message, 
                language_detected="hinglish"
            )
        
        # Send progress update based on provider
        provider_name = "OpenAI GPT-3.5-turbo" if chatbot_provider == "openai" else "Google Gemini"
        await manager.send_personal_message({
            "type": "chat_progress",
            "message": f"Getting {provider_name} response...",
            "progress": 50
        }, client_id)
        
        # Get AI response based on selected provider
        try:
            if chatbot_provider == "openai":
                # Use OpenAI ChatGPT
                try:
                    from .openai_chatbot import HinglishOpenAIChatbot
                except ImportError:
                    from openai_chatbot import HinglishOpenAIChatbot
                
                chatbot = HinglishOpenAIChatbot()
                  # Get conversation context for better responses
                messages = await voice_db.get_conversation_messages(conversation_id, limit=10)
                context = []
                for msg in messages[-5:]:  # Last 5 messages for context
                    context.append(f"{msg['role']}: {msg['content']}")
                
                context_str = "\n".join(context) if context else ""
                context_dict = {"previous_context": context_str} if context_str else {}
                response_data = await chatbot.get_response(user_message, context_dict)
                ai_response = response_data[0] if isinstance(response_data, tuple) else response_data
                
            else:  # gemini
                # Use Google Gemini
                try:
                    from .gemini_chatbot import HinglishChatbot
                except ImportError:
                    from gemini_chatbot import HinglishChatbot
                
                gemini_chatbot = HinglishChatbot()
                
                # Get conversation context for better responses
                messages = await voice_db.get_conversation_messages(conversation_id, limit=10)
                context = []
                for msg in messages[-5:]:  # Last 5 messages for context
                    context.append(f"{msg['role']}: {msg['content']}")
                
                context_str = "\n".join(context) if context else ""
                context_dict = {"previous_context": context_str} if context_str else {}
                ai_response = await gemini_chatbot.get_response(user_message, context_dict)
            
        except Exception as e:
            print(f"❌ {provider_name} API error: {e}")
            ai_response = "मुझे खुशी होगी आपकी मदद करने में! Sorry, मैं अभी available नहीं हूं। Please try again later."
        
        # Normalize AI response to string (handle both OpenAI tuple and Gemini string responses)
        if isinstance(ai_response, tuple):
            ai_response = ai_response[0]  # Extract text from OpenAI tuple response
        
        # Send progress update
        await manager.send_personal_message({
            "type": "chat_progress",
            "message": "Generating voice response...",
            "progress": 75
        }, client_id)
          # Save AI response to database
        assistant_message_id = await voice_db.add_message(
            conversation_id, "assistant", ai_response,
            voice_used=voice_name,
            metadata={"chatbot_provider": chatbot_provider}
        )

        # Generate TTS if voice is selected
        audio_file = None
        if voice_name:
            try:
                # Convert AI response to pure Hindi before TTS generation
                try:
                    from .text_to_hindi_converter import TextToHindiConverter
                except ImportError:
                    from text_to_hindi_converter import TextToHindiConverter
                
                print(f"🔄 Converting to Hindi: {ai_response[:50]}...")
                hindi_converter = TextToHindiConverter()
                hindi_text = await hindi_converter.convert_to_hindi(ai_response)
                print(f"✅ Hindi conversion: {hindi_text[:50]}...")
                
                # Get voice profile
                voice_profile = await voice_db.get_voice_profile(voice_name)
                if voice_profile:
                    # Generate output filename with safe ID
                    safe_id = assistant_message_id[:8] if assistant_message_id else uuid.uuid4().hex[:8]
                    output_filename = f"chatbot_{voice_name}_{safe_id}.wav"
                    output_path = os.path.join("generated", output_filename)
                    
                    # Ensure generated directory exists
                    os.makedirs("generated", exist_ok=True)
                    
                    print(f"🎵 Generating audio for Hindi text: {hindi_text[:50]}...")
                      # Generate speech using FIXED cloner with converted Hindi text
                    voice_features = voice_profile["voice_features"]
                    generated_path = get_voice_cloner().clone_voice(hindi_text, voice_features, output_path)
                    
                    if generated_path and os.path.exists(generated_path):
                        audio_file = f"/download/{output_filename}"
                        print(f"✅ Audio generated successfully: {output_filename}")
                        
                        # Update message with audio path (store original AI response but use Hindi for audio)
                        if assistant_message_id:
                            await voice_db.add_message(
                                conversation_id, "assistant", ai_response,
                                audio_path=generated_path, voice_used=voice_name,
                                metadata={
                                    "chatbot_provider": chatbot_provider,
                                    "original_text": ai_response,
                                    "hindi_text_for_tts": hindi_text
                                }
                            )
                    else:
                        print(f"❌ Audio generation failed - no file created")
                        
            except Exception as e:
                print(f"❌ TTS generation failed: {e}")
                import traceback
                traceback.print_exc()
          # Send complete response
        response_data = {
            "type": "chat_response",
            "conversation_id": conversation_id,
            "user_message": user_message,
            "assistant_message": ai_response,
            "audio_file": audio_file,
            "voice_used": voice_name,
            "message_id": assistant_message_id,
            "progress": 100
        }
        
        print(f"📤 Sending chat response with audio_file: {audio_file}")
        await manager.send_personal_message(response_data, client_id)
        
    except Exception as e:
        await manager.send_personal_message({
            "type": "error",
            "message": f"Error processing chat message: {str(e)}"
        }, client_id)

async def handle_speech_to_text(message: Dict[str, Any], client_id: str):
    """Handle speech-to-text conversion"""
    try:
        audio_data = message.get("audio_data")  # Base64 encoded audio
        audio_format = message.get("format", "wav")
        
        if not audio_data:
            await manager.send_personal_message({
                "type": "error",
                "message": "No audio data provided"
            }, client_id)
            return
        
        # Send progress update
        await manager.send_personal_message({
            "type": "stt_progress",
            "message": "Processing audio...",
            "progress": 30
        }, client_id)
          # Import speech-to-text module
        try:
            from .speech_to_text import HinglishSpeechToText
        except ImportError:
            from speech_to_text import HinglishSpeechToText
        
        stt = HinglishSpeechToText()
        
        # Decode base64 audio
        import base64
        audio_bytes = base64.b64decode(audio_data)
        
        # Save to temporary file
        temp_filename = f"stt_temp_{client_id}_{uuid.uuid4().hex[:8]}.{audio_format}"
        temp_path = os.path.join("temp", temp_filename)
        
        os.makedirs("temp", exist_ok=True)
        with open(temp_path, "wb") as f:
            f.write(audio_bytes)
        
        # Send progress update
        await manager.send_personal_message({
            "type": "stt_progress",
            "message": "Converting speech to text...",
            "progress": 70
        }, client_id)        # Perform speech-to-text
        result = stt.transcribe_audio_file(temp_path)
        
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        # Send result
        await manager.send_personal_message({
            "type": "stt_result",
            "transcript": result.get("transcript", ""),
            "confidence": result.get("confidence", 0.0),
            "language": result.get("language", "unknown"),
            "processing_time": result.get("processing_time", 0.0),
            "progress": 100
        }, client_id)
        
    except Exception as e:
        await manager.send_personal_message({
            "type": "error",
            "message": f"Error in speech-to-text: {str(e)}"
        }, client_id)

async def handle_list_conversations(message: Dict[str, Any], client_id: str):
    """Handle listing user conversations"""
    try:
        user_id = message.get("user_id", client_id)
        limit = message.get("limit", 50)
        
        conversations = await voice_db.list_conversations(user_id, limit)
        
        await manager.send_personal_message({
            "type": "conversations_list",
            "conversations": conversations,
            "count": len(conversations)
        }, client_id)
        
    except Exception as e:
        await manager.send_personal_message({
            "type": "error",
            "message": f"Error listing conversations: {str(e)}"
        }, client_id)

async def handle_get_conversation(message: Dict[str, Any], client_id: str):
    """Handle getting conversation details with messages"""
    try:
        conversation_id = message.get("conversation_id")
        
        if not conversation_id:
            await manager.send_personal_message({
                "type": "error",
                "message": "Missing conversation_id"
            }, client_id)
            return
        
        # Get conversation details
        conversation = await voice_db.get_conversation(conversation_id)
        if not conversation:
            await manager.send_personal_message({
                "type": "error",
                "message": "Conversation not found"
            }, client_id)
            return
        
        # Get conversation messages
        messages = await voice_db.get_conversation_messages(conversation_id)
        
        await manager.send_personal_message({
            "type": "conversation_details",
            "conversation": conversation,
            "messages": messages,
            "message_count": len(messages)
        }, client_id)
        
    except Exception as e:
        await manager.send_personal_message({
            "type": "error",
            "message": f"Error getting conversation: {str(e)}"
        }, client_id)

async def handle_delete_conversation(message: Dict[str, Any], client_id: str):
    """Handle deleting a conversation"""
    try:
        conversation_id = message.get("conversation_id")
        
        if not conversation_id:
            await manager.send_personal_message({
                "type": "error",
                "message": "Missing conversation_id"
            }, client_id)
            return
        
        success = await voice_db.delete_conversation(conversation_id)
        
        if success:
            await manager.send_personal_message({
                "type": "conversation_deleted",
                "conversation_id": conversation_id,
                "message": "Conversation deleted successfully"
            }, client_id)
        else:
            await manager.send_personal_message({
                "type": "error",
                "message": "Failed to delete conversation"
            }, client_id)
        
    except Exception as e:
        await manager.send_personal_message({
            "type": "error",
            "message": f"Error deleting conversation: {str(e)}"
        }, client_id)

@app.post("/upload_voice")
async def upload_voice(
    voice_name: str = Form(...),
    audio_file: UploadFile = File(...),
    description: str = Form(""),
    language: str = Form("hi")
):
    """Upload and process voice sample"""
    try:
        print(f"[DEBUG] Upload request received:")
        print(f"  - voice_name: {voice_name}")
        print(f"  - audio_file: {audio_file.filename if audio_file else 'None'}")
        print(f"  - description: {description}")
        print(f"  - language: {language}")
        
        # Validate required fields
        if not voice_name or voice_name.strip() == "":
            print("[DEBUG] Error: voice_name is empty")
            return JSONResponse(
                status_code=400,
                content={"success": False, "message": "Voice name is required"}
            )
            
        if not audio_file or not audio_file.filename:
            print("[DEBUG] Error: no audio file provided")
            return JSONResponse(
                status_code=400,
                content={"success": False, "message": "Audio file is required"}
            )
        
        # Validate file type
        filename = audio_file.filename or "unknown.wav"
        print(f"[DEBUG] Checking file type: {filename}")
        if not filename.lower().endswith(('.wav', '.mp3', '.m4a', '.flac', '.ogg')):
            print(f"[DEBUG] Error: unsupported file type: {filename}")
            return JSONResponse(
                status_code=400,
                content={"success": False, "message": f"Unsupported audio format: {filename}"}
            )
        
        print(f"[DEBUG] File validation passed, proceeding with upload...")
        
        # Save uploaded file
        upload_dir = "voices"
        os.makedirs(upload_dir, exist_ok=True)
        
        file_extension = os.path.splitext(filename)[1]
        temp_filename = f"temp_{uuid.uuid4().hex[:8]}{file_extension}"
        temp_path = os.path.join(upload_dir, temp_filename)
        with open(temp_path, "wb") as buffer:
            content = await audio_file.read()
            buffer.write(content)
        
        print(f"[DEBUG] Audio file saved to: {temp_path}")
        print(f"[DEBUG] Starting audio quality validation...")
        
        # Validate audio quality
        validation = get_voice_cloner().validate_audio_quality(temp_path)
        
        print(f"[DEBUG] Validation result: {validation}")
        
        if not validation["is_valid"]:
            print(f"[DEBUG] Validation failed: {validation['issues']}")
            os.remove(temp_path)
            return JSONResponse(
                status_code=400,
                content={"success": False,
                    "message": "Audio quality validation failed",
                    "issues": validation["issues"],
                    "recommendations": validation["recommendations"]
                }
            )
        
        # Preprocess audio
        processed_filename = f"{voice_name}_{uuid.uuid4().hex[:8]}.wav"
        processed_path = os.path.join(upload_dir, processed_filename)
        get_voice_cloner().preprocess_audio(temp_path, processed_path)
        
        # Extract voice features
        voice_features = get_voice_cloner().extract_voice_features(processed_path)
        
        # Save to database
        metadata = {
            "description": description,
            "language": language,
            "original_filename": audio_file.filename,
            "file_size": len(content),
            "validation": validation
        }
        
        success = await voice_db.save_voice_profile(
            voice_name, voice_features, processed_path, metadata
        )
        
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        if success:
            # Broadcast update to all connected clients
            await manager.broadcast({
                "type": "voice_added",
                "voice_name": voice_name,
                "message": f"Voice '{voice_name}' added successfully"
            })
            
            return JSONResponse(content={
                "success": True,
                "message": f"Voice '{voice_name}' uploaded and processed successfully",
                "voice_name": voice_name,
                "features_extracted": True,
                "validation": validation
            })
        else:
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "message": "Failed to save voice profile"
                }
            )
    
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": f"Error processing voice upload: {str(e)}"
            }
        )

@app.post("/generate_speech")
async def generate_speech_api(
    voice_name: str = Form(...),
    text: str = Form(...),
    output_format: str = Form("wav")
):
    """Generate speech using stored voice profile"""
    try:
        # Get voice profile
        voice_profile = await voice_db.get_voice_profile(voice_name)
        if not voice_profile:
            raise HTTPException(status_code=404, detail=f"Voice '{voice_name}' not found")
        
        # Generate output filename
        output_filename = f"generated_{voice_name}_{uuid.uuid4().hex[:8]}.{output_format}"
        output_path = os.path.join("generated", output_filename)
          # Generate speech
        voice_features = voice_profile["voice_features"]
        generated_path = get_voice_cloner().clone_voice(text, voice_features, output_path)
        
        return JSONResponse(content={
            "success": True,
            "message": "Speech generated successfully",
            "audio_file": f"/download/{output_filename}",
            "voice_name": voice_name,
            "text": text
        })
    
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": f"Error generating speech: {str(e)}"
            }
        )

@app.get("/voices")
async def list_voices():
    """List all available voice profiles"""
    try:
        voices = await voice_db.list_voice_profiles()
        return JSONResponse(content={
            "success": True,
            "voices": voices,
            "count": len(voices)
        })
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": f"Error listing voices: {str(e)}"
            }
        )

@app.get("/voice/{voice_name}")
async def get_voice_profile(voice_name: str):
    """Get detailed voice profile"""
    try:
        profile = await voice_db.get_voice_profile(voice_name)
        if not profile:
            raise HTTPException(status_code=404, detail=f"Voice '{voice_name}' not found")
        
        # Remove large audio data from response
        profile_copy = profile.copy()
        if "voice_features" in profile_copy and "audio_data" in profile_copy["voice_features"]:
            profile_copy["voice_features"] = profile_copy["voice_features"].copy()
            del profile_copy["voice_features"]["audio_data"]
        
        return JSONResponse(content={
            "success": True,
            "voice_profile": profile_copy
        })
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": f"Error retrieving voice profile: {str(e)}"
            }
        )

@app.delete("/voice/{voice_name}")
async def delete_voice(voice_name: str):
    """Delete voice profile"""
    try:
        success = await voice_db.delete_voice_profile(voice_name)
        if success:
            # Broadcast update to all connected clients
            await manager.broadcast({
                "type": "voice_deleted",
                "voice_name": voice_name,
                "message": f"Voice '{voice_name}' deleted successfully"
            })
            
            return JSONResponse(content={
                "success": True,
                "message": f"Voice '{voice_name}' deleted successfully"
            })
        else:
            raise HTTPException(status_code=404, detail=f"Voice '{voice_name}' not found")
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": f"Error deleting voice: {str(e)}"
            }
        )

@app.get("/download/{filename}")
async def download_file(filename: str):
    """Download generated audio file"""
    try:
        file_path = os.path.join("generated", filename)
        if os.path.exists(file_path):
            return FileResponse(
                file_path,
                media_type="audio/wav",
                filename=filename
            )
        else:
            raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error downloading file: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return JSONResponse(content={
        "status": "healthy",
        "service": "Voice Cloning API",
        "version": "1.0.0"
    })

@app.get("/")
async def root():
    """Serve the main HTML interface"""
    return FileResponse("static/index.html")

@app.get("/api")
async def api_info():
    """API information endpoint"""
    return JSONResponse(content={
        "message": "Voice Cloning API",
        "version": "1.0.0",
        "endpoints": {
            "upload_voice": "POST /upload_voice",
            "generate_speech": "POST /generate_speech",
            "list_voices": "GET /voices",
            "get_voice": "GET /voice/{voice_name}",
            "delete_voice": "DELETE /voice/{voice_name}",
            "websocket": "WS /ws/{client_id}",
            "download": "GET /download/{filename}"
        }
    })

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
