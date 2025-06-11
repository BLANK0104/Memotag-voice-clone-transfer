"""
Simple HTML interface for voice cloning demonstration
"""

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎤 Voice Cloning Studio</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }

        .header {
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            padding: 30px;
            text-align: center;
        }

        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 10px;
        }

        .header p {
            font-size: 1.1rem;
            opacity: 0.9;
        }

        .main-content {
            padding: 40px;
        }

        .section {
            margin-bottom: 40px;
            padding: 30px;
            border-radius: 15px;
            background: #f8f9fa;
            border: 2px solid #e9ecef;
        }

        .section h2 {
            color: #495057;
            margin-bottom: 20px;
            font-size: 1.8rem;
        }

        .form-group {
            margin-bottom: 20px;
        }

        .form-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #495057;
        }

        .form-group input,
        .form-group select,
        .form-group textarea {
            width: 100%;
            padding: 12px;
            border: 2px solid #dee2e6;
            border-radius: 8px;
            font-size: 16px;
            transition: border-color 0.3s;
        }

        .form-group input:focus,
        .form-group select:focus,
        .form-group textarea:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }

        .btn {
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s;
            margin-right: 10px;
            margin-bottom: 10px;
        }

        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
        }

        .btn:active {
            transform: translateY(0);
        }

        .btn-secondary {
            background: linear-gradient(45deg, #6c757d, #495057);
        }

        .btn-success {
            background: linear-gradient(45deg, #28a745, #20c997);
        }

        .btn-danger {
            background: linear-gradient(45deg, #dc3545, #c82333);
        }

        .progress {
            width: 100%;
            height: 20px;
            background: #e9ecef;
            border-radius: 10px;
            overflow: hidden;
            margin: 20px 0;
        }

        .progress-bar {
            height: 100%;
            background: linear-gradient(45deg, #28a745, #20c997);
            width: 0%;
            transition: width 0.3s;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: 600;
        }

        .status {
            padding: 15px;
            border-radius: 8px;
            margin: 15px 0;
            font-weight: 600;
        }

        .status.success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }

        .status.error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }

        .status.info {
            background: #d1ecf1;
            color: #0c5460;
            border: 1px solid #bee5eb;
        }

        .voice-card {
            background: white;
            border: 2px solid #dee2e6;
            border-radius: 15px;
            padding: 20px;
            margin: 15px 0;
            transition: transform 0.2s;
        }

        .voice-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }

        .voice-card h3 {
            color: #495057;
            margin-bottom: 10px;
        }

        .voice-card p {
            color: #6c757d;
            margin-bottom: 15px;
        }

        .audio-player {
            width: 100%;
            margin: 15px 0;
        }

        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }

        .hidden {
            display: none;
        }

        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .connections {
            position: fixed;
            top: 20px;
            right: 20px;
            background: rgba(255,255,255,0.9);
            padding: 10px;
            border-radius: 8px;
            font-weight: 600;
        }

        .connection-status {
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            margin-right: 5px;
        }

        .connected {
            background: #28a745;
        }        .disconnected {
            background: #dc3545;
        }

        /* Chatbot Styles */
        .chat-message {
            margin-bottom: 15px;
            padding: 12px;
            border-radius: 8px;
            max-width: 80%;
        }

        .chat-message.user {
            background: #e3f2fd;
            margin-left: auto;
            text-align: right;
        }

        .chat-message.assistant {
            background: #f1f8e9;
            margin-right: auto;
        }

        .message-content {
            word-wrap: break-word;
        }

        .message-audio {
            margin-top: 8px;
        }

        .message-audio audio {
            width: 100%;
            max-width: 300px;
        }

        .conversation-item {
            background: white;
            border: 2px solid #dee2e6;
            border-radius: 8px;
            padding: 15px;
            margin: 10px 0;
            cursor: pointer;
            transition: transform 0.2s;
        }

        .conversation-item:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }

        .conversation-item h4 {
            margin-bottom: 5px;
            color: #495057;
        }

        .conversation-item p {
            color: #6c757d;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="connections">
        <span class="connection-status disconnected" id="connectionStatus"></span>
        <span id="connectionText">Connecting...</span>
    </div>

    <div class="container">
        <div class="header">
            <h1>🎤 Voice Cloning Studio</h1>
            <p>Clone voices from 10-second samples and generate Hindi text-to-speech</p>
        </div>

        <div class="main-content">
            <!-- Upload Voice Section -->
            <div class="section" id="uploadSection">
                <h2>📤 Upload Voice Sample</h2>
                <form id="uploadForm">
                    <div class="grid">
                        <div>
                            <div class="form-group">
                                <label for="voiceName">Voice Name *</label>
                                <input type="text" id="voiceName" required placeholder="Enter unique voice name">
                            </div>
                            <div class="form-group">
                                <label for="description">Description</label>
                                <textarea id="description" rows="3" placeholder="Describe this voice..."></textarea>
                            </div>
                            <div class="form-group">
                                <label for="language">Language</label>
                                <select id="language">
                                    <option value="hi">Hindi</option>
                                    <option value="en">English</option>
                                    <option value="other">Other</option>
                                </select>
                            </div>
                        </div>
                        <div>
                            <div class="form-group">
                                <label for="audioFile">Audio File *</label>
                                <input type="file" id="audioFile" accept=".wav,.mp3,.m4a,.flac,.ogg" required>
                            </div>
                            <div id="audioPreview" class="hidden">
                                <audio id="previewPlayer" class="audio-player" controls></audio>
                            </div>
                        </div>
                    </div>
                    <button type="submit" class="btn">🚀 Upload and Process Voice</button>
                </form>
                <div class="progress hidden" id="uploadProgress">
                    <div class="progress-bar" id="uploadProgressBar">0%</div>
                </div>
                <div id="uploadStatus"></div>
            </div>

            <!-- Generate Speech Section -->
            <div class="section" id="generateSection">
                <h2>🎵 Generate Speech</h2>
                <form id="generateForm">
                    <div class="grid">
                        <div>
                            <div class="form-group">
                                <label for="selectedVoice">Select Voice</label>
                                <select id="selectedVoice">
                                    <option value="">Select a voice...</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label for="textInput">Hindi Text to Convert *</label>
                                <textarea id="textInput" rows="4" required placeholder="यहाँ अपना हिंदी टेक्स्ट लिखें..."></textarea>
                            </div>
                        </div>
                        <div>
                            <div class="form-group">
                                <label>Voice Details</label>
                                <div id="voiceDetails" class="voice-card">
                                    <p>Select a voice to see details</p>
                                </div>
                            </div>
                        </div>
                    </div>
                    <button type="submit" class="btn">🎤 Generate Speech</button>
                </form>
                <div class="progress hidden" id="generateProgress">
                    <div class="progress-bar" id="generateProgressBar">0%</div>
                </div>
                <div id="generateStatus"></div>
                <div id="generatedAudio" class="hidden">
                    <h3>Generated Audio:</h3>
                    <audio id="generatedPlayer" class="audio-player" controls></audio>
                    <br>
                    <a id="downloadLink" class="btn btn-success" download>📥 Download Audio</a>
                </div>
            </div>            <!-- Voice Library Section -->
            <div class="section" id="librarySection">
                <h2>📊 Voice Library</h2>
                <button id="refreshVoices" class="btn btn-secondary">🔄 Refresh</button>
                <div id="voicesList"></div>
            </div>

            <!-- Hinglish Chatbot Section -->
            <div class="section" id="chatbotSection">
                <h2>🤖 Hinglish Chatbot</h2>
                <p>Chat with AI in mixed Hindi-English and get voice responses using your cloned voices!</p>
                
                <!-- Conversation Controls -->
                <div class="grid">
                    <div>
                        <div class="form-group">
                            <label for="chatVoice">Select Voice for AI Responses</label>
                            <select id="chatVoice">
                                <option value="">No voice (text only)</option>
                            </select>
                        </div>
                    </div>
                    <div>
                        <div class="form-group">
                            <label>Conversation</label>
                            <div style="display: flex; gap: 10px;">
                                <button id="newConversation" class="btn">🆕 New Chat</button>
                                <button id="loadConversations" class="btn btn-secondary">📂 Load Chats</button>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Chat Container -->
                <div id="chatContainer" class="hidden">
                    <div id="chatHeader" style="padding: 15px; background: #f8f9fa; border-radius: 8px; margin-bottom: 20px;">
                        <h3 id="chatTitle">New Conversation</h3>
                        <p><span id="chatLanguage">Hinglish</span> • <span id="chatMessageCount">0 messages</span></p>
                    </div>

                    <!-- Chat Messages -->
                    <div id="chatMessages" style="max-height: 400px; overflow-y: auto; border: 2px solid #dee2e6; border-radius: 8px; padding: 15px; margin-bottom: 20px; background: white;">
                        <div id="welcomeMessage" class="chat-message assistant">
                            <div class="message-content">
                                <strong>AI Assistant:</strong> नमस्ते! I'm ready to chat with you in Hinglish. आप कैसे हैं? How can I help you today?
                            </div>
                        </div>
                    </div>

                    <!-- Message Input -->
                    <div class="form-group">
                        <div style="display: flex; gap: 10px;">
                            <textarea id="chatInput" rows="2" placeholder="Type your message in Hinglish... हिंदी और English दोनों में लिख सकते हैं!" style="flex: 1;"></textarea>
                            <div style="display: flex; flex-direction: column; gap: 5px;">
                                <button id="sendMessage" class="btn">📤 Send</button>
                                <button id="voiceInput" class="btn btn-secondary">🎤 Voice</button>
                            </div>
                        </div>
                    </div>

                    <!-- Example Hinglish Messages -->
                    <div style="margin-top: 15px;">
                        <label>Quick Examples:</label>
                        <div style="display: flex; flex-wrap: wrap; gap: 5px; margin-top: 8px;">
                            <button class="btn" style="font-size: 12px; padding: 5px 10px;" onclick="app.setExample('नमस्ते! आज कैसा दिन है?')">नमस्ते! आज कैसा दिन है?</button>
                            <button class="btn" style="font-size: 12px; padding: 5px 10px;" onclick="app.setExample('Weather kaisa hai today?')">Weather kaisa hai today?</button>
                            <button class="btn" style="font-size: 12px; padding: 5px 10px;" onclick="app.setExample('Mujhe Hindi aur English दोनों पसंद हैं')">Mixed language</button>
                            <button class="btn" style="font-size: 12px; padding: 5px 10px;" onclick="app.setExample('Tell me a joke yaar!')">Tell me a joke yaar!</button>
                        </div>
                    </div>

                    <div id="chatStatus"></div>
                    <div class="progress hidden" id="chatProgress">
                        <div class="progress-bar" id="chatProgressBar">0%</div>
                    </div>
                </div>

                <!-- Conversations List -->
                <div id="conversationsList" class="hidden">
                    <h3>Your Conversations</h3>
                    <div id="conversationsContainer"></div>
                </div>
            </div>
        </div>
    </div>

    <script>
        class VoiceCloningApp {
            constructor() {
                this.ws = null;
                this.voices = [];
                this.isConnected = false;
                this.init();
            }            init() {
                this.connectWebSocket();
                this.setupEventListeners();
                this.loadVoices();
                this.initChatbot();
            }

            connectWebSocket() {
                const clientId = 'web_client_' + Math.random().toString(36).substr(2, 9);
                this.ws = new WebSocket(`ws://localhost:8000/ws/${clientId}`);

                this.ws.onopen = () => {
                    this.isConnected = true;
                    this.updateConnectionStatus();
                    console.log('WebSocket connected');
                    this.sendMessage({ type: 'list_voices' });
                };

                this.ws.onmessage = (event) => {
                    const message = JSON.parse(event.data);
                    this.handleWebSocketMessage(message);
                };

                this.ws.onclose = () => {
                    this.isConnected = false;
                    this.updateConnectionStatus();
                    console.log('WebSocket disconnected');
                    setTimeout(() => this.connectWebSocket(), 3000);
                };

                this.ws.onerror = (error) => {
                    console.error('WebSocket error:', error);
                };
            }

            updateConnectionStatus() {
                const statusElement = document.getElementById('connectionStatus');
                const textElement = document.getElementById('connectionText');
                
                if (this.isConnected) {
                    statusElement.className = 'connection-status connected';
                    textElement.textContent = 'Connected';
                } else {
                    statusElement.className = 'connection-status disconnected';
                    textElement.textContent = 'Disconnected';
                }
            }

            sendMessage(message) {
                if (this.ws && this.ws.readyState === WebSocket.OPEN) {
                    this.ws.send(JSON.stringify(message));
                }
            }            handleWebSocketMessage(message) {
                switch (message.type) {
                    case 'voice_list':
                        this.voices = message.voices;
                        this.updateVoicesList();
                        this.updateVoiceSelect();
                        this.updateChatVoiceSelect();
                        break;
                    case 'voice_added':
                        this.showStatus('uploadStatus', `Voice '${message.voice_name}' added successfully!`, 'success');
                        this.loadVoices();
                        break;
                    case 'voice_deleted':
                        this.showStatus('librarySection', `Voice '${message.voice_name}' deleted successfully!`, 'success');
                        this.loadVoices();
                        break;
                    case 'progress':
                        this.updateProgress('generateProgress', 'generateProgressBar', message.progress, message.message);
                        break;
                    case 'speech_generated':
                        this.handleSpeechGenerated(message);
                        break;
                    case 'error':
                        this.showStatus('generateStatus', `Error: ${message.message}`, 'error');
                        this.showStatus('chatStatus', `Error: ${message.message}`, 'error');
                        this.hideProgress('chatProgress');
                        break;
                    // Chatbot message types
                    case 'conversation_started':
                        this.handleConversationStarted(message);
                        break;
                    case 'chat_response':
                        this.handleChatResponse(message);
                        break;
                    case 'chat_progress':
                        this.updateProgress('chatProgress', 'chatProgressBar', message.progress, message.message);
                        break;
                    case 'conversations_list':
                        this.handleConversationsList(message);
                        break;
                    case 'conversation_details':
                        this.handleConversationDetails(message);
                        break;
                }
            }

            setupEventListeners() {
                // Upload form
                document.getElementById('uploadForm').addEventListener('submit', (e) => {
                    e.preventDefault();
                    this.uploadVoice();
                });

                // Generate form
                document.getElementById('generateForm').addEventListener('submit', (e) => {
                    e.preventDefault();
                    this.generateSpeech();
                });

                // Audio file preview
                document.getElementById('audioFile').addEventListener('change', (e) => {
                    this.previewAudio(e.target.files[0]);
                });

                // Voice selection
                document.getElementById('selectedVoice').addEventListener('change', (e) => {
                    this.showVoiceDetails(e.target.value);
                });

                // Refresh voices
                document.getElementById('refreshVoices').addEventListener('click', () => {
                    this.loadVoices();
                });
            }

            previewAudio(file) {
                if (file) {
                    const url = URL.createObjectURL(file);
                    const preview = document.getElementById('audioPreview');
                    const player = document.getElementById('previewPlayer');
                    
                    player.src = url;
                    preview.classList.remove('hidden');
                }
            }

            async uploadVoice() {
                const form = document.getElementById('uploadForm');
                const formData = new FormData();
                
                formData.append('voice_name', document.getElementById('voiceName').value);
                formData.append('description', document.getElementById('description').value);
                formData.append('language', document.getElementById('language').value);
                formData.append('audio_file', document.getElementById('audioFile').files[0]);

                try {
                    this.showProgress('uploadProgress', 'uploadProgressBar', 0, 'Uploading...');
                    
                    const response = await fetch('/upload_voice', {
                        method: 'POST',
                        body: formData
                    });

                    const result = await response.json();
                    
                    if (result.success) {
                        this.showStatus('uploadStatus', 'Voice uploaded successfully!', 'success');
                        form.reset();
                        document.getElementById('audioPreview').classList.add('hidden');
                        this.hideProgress('uploadProgress');
                        this.loadVoices();
                    } else {
                        this.showStatus('uploadStatus', `Upload failed: ${result.message}`, 'error');
                        this.hideProgress('uploadProgress');
                    }
                } catch (error) {
                    this.showStatus('uploadStatus', `Upload error: ${error.message}`, 'error');
                    this.hideProgress('uploadProgress');
                }
            }

            generateSpeech() {
                const voiceName = document.getElementById('selectedVoice').value;
                const text = document.getElementById('textInput').value;

                if (!voiceName || !text) {
                    this.showStatus('generateStatus', 'Please select a voice and enter text', 'error');
                    return;
                }

                this.sendMessage({
                    type: 'generate_speech',
                    voice_name: voiceName,
                    text: text
                });

                this.showProgress('generateProgress', 'generateProgressBar', 20, 'Starting generation...');
            }

            handleSpeechGenerated(message) {
                this.hideProgress('generateProgress');
                this.showStatus('generateStatus', 'Speech generated successfully!', 'success');
                
                const audioContainer = document.getElementById('generatedAudio');
                const player = document.getElementById('generatedPlayer');
                const downloadLink = document.getElementById('downloadLink');
                
                const audioUrl = `http://localhost:8000${message.audio_file}`;
                player.src = audioUrl;
                downloadLink.href = audioUrl;
                downloadLink.download = `generated_${message.voice_name}.wav`;
                
                audioContainer.classList.remove('hidden');
            }

            async loadVoices() {
                try {
                    const response = await fetch('/voices');
                    const data = await response.json();
                    
                    if (data.success) {
                        this.voices = data.voices;
                        this.updateVoicesList();
                        this.updateVoiceSelect();
                    }
                } catch (error) {
                    console.error('Error loading voices:', error);
                }
            }

            updateVoiceSelect() {
                const select = document.getElementById('selectedVoice');
                select.innerHTML = '<option value="">Select a voice...</option>';
                
                this.voices.forEach(voice => {
                    const option = document.createElement('option');
                    option.value = voice.voice_name;
                    option.textContent = voice.voice_name;
                    select.appendChild(option);
                });
            }

            updateVoicesList() {
                const container = document.getElementById('voicesList');
                
                if (this.voices.length === 0) {
                    container.innerHTML = '<p>No voices available. Upload your first voice sample!</p>';
                    return;
                }

                container.innerHTML = this.voices.map(voice => `
                    <div class="voice-card">
                        <h3>${voice.voice_name}</h3>
                        <p>${voice.metadata?.description || 'No description'}</p>
                        <p><strong>Language:</strong> ${voice.metadata?.language || 'Unknown'}</p>
                        <p><strong>Created:</strong> ${new Date(voice.created_at).toLocaleDateString()}</p>
                        <button class="btn" onclick="app.selectVoiceForGeneration('${voice.voice_name}')">🎤 Use for Generation</button>
                        <button class="btn btn-danger" onclick="app.deleteVoice('${voice.voice_name}')">🗑️ Delete</button>
                    </div>
                `).join('');
            }

            selectVoiceForGeneration(voiceName) {
                document.getElementById('selectedVoice').value = voiceName;
                this.showVoiceDetails(voiceName);
                document.getElementById('generateSection').scrollIntoView({ behavior: 'smooth' });
            }

            async showVoiceDetails(voiceName) {
                const container = document.getElementById('voiceDetails');
                
                if (!voiceName) {
                    container.innerHTML = '<p>Select a voice to see details</p>';
                    return;
                }

                try {
                    const response = await fetch(`/voice/${voiceName}`);
                    const data = await response.json();
                    
                    if (data.success) {
                        const profile = data.voice_profile;
                        const metadata = profile.metadata || {};
                        
                        container.innerHTML = `
                            <h3>${voiceName}</h3>
                            <p><strong>Description:</strong> ${metadata.description || 'No description'}</p>
                            <p><strong>Language:</strong> ${metadata.language || 'Unknown'}</p>
                            <p><strong>Created:</strong> ${new Date(profile.created_at).toLocaleDateString()}</p>
                            <p><strong>File:</strong> ${metadata.original_filename || 'Unknown'}</p>
                        `;
                    }
                } catch (error) {
                    container.innerHTML = '<p>Error loading voice details</p>';
                }
            }

            async deleteVoice(voiceName) {
                if (!confirm(`Are you sure you want to delete voice '${voiceName}'?`)) {
                    return;
                }

                try {
                    const response = await fetch(`/voice/${voiceName}`, {
                        method: 'DELETE'
                    });

                    const result = await response.json();
                    
                    if (result.success) {
                        this.loadVoices();
                    } else {
                        alert(`Failed to delete voice: ${result.message}`);
                    }
                } catch (error) {
                    alert(`Error deleting voice: ${error.message}`);
                }
            }

            showStatus(containerId, message, type) {
                const container = document.getElementById(containerId);
                const statusDiv = document.createElement('div');
                statusDiv.className = `status ${type}`;
                statusDiv.textContent = message;
                
                // Remove existing status
                const existing = container.querySelector('.status');
                if (existing) {
                    existing.remove();
                }
                
                container.appendChild(statusDiv);
                
                // Auto-remove after 5 seconds
                setTimeout(() => {
                    if (statusDiv.parentNode) {
                        statusDiv.remove();
                    }
                }, 5000);
            }

            showProgress(containerId, barId, progress, message) {
                const container = document.getElementById(containerId);
                const bar = document.getElementById(barId);
                
                container.classList.remove('hidden');
                bar.style.width = `${progress}%`;
                bar.textContent = message || `${progress}%`;
            }

            updateProgress(containerId, barId, progress, message) {
                const bar = document.getElementById(barId);
                bar.style.width = `${progress}%`;
                bar.textContent = message || `${progress}%`;
            }            hideProgress(containerId) {
                const container = document.getElementById(containerId);
                container.classList.add('hidden');
            }

            // === CHATBOT METHODS ===
            initChatbot() {
                this.currentConversationId = null;
                this.setupChatEventListeners();
                this.updateChatVoiceSelect();
            }

            setupChatEventListeners() {
                // New conversation button
                document.getElementById('newConversation').addEventListener('click', () => {
                    this.startNewConversation();
                });

                // Load conversations button
                document.getElementById('loadConversations').addEventListener('click', () => {
                    this.toggleConversationsList();
                });

                // Send message button
                document.getElementById('sendMessage').addEventListener('click', () => {
                    this.sendChatMessage();
                });

                // Voice input button
                document.getElementById('voiceInput').addEventListener('click', () => {
                    this.startVoiceInput();
                });

                // Enter key in chat input
                document.getElementById('chatInput').addEventListener('keypress', (e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        this.sendChatMessage();
                    }
                });
            }

            updateChatVoiceSelect() {
                const select = document.getElementById('chatVoice');
                select.innerHTML = '<option value="">No voice (text only)</option>';
                
                this.voices.forEach(voice => {
                    const option = document.createElement('option');
                    option.value = voice.voice_name;
                    option.textContent = voice.voice_name;
                    select.appendChild(option);
                });
            }

            startNewConversation() {
                this.sendMessage({
                    type: 'start_conversation',
                    title: 'New Hinglish Chat',
                    language: 'hinglish',
                    metadata: { created_from: 'web_interface' }
                });
            }

            sendChatMessage() {
                const input = document.getElementById('chatInput');
                const message = input.value.trim();
                const voiceName = document.getElementById('chatVoice').value;

                if (!message) return;
                if (!this.currentConversationId) {
                    this.showStatus('chatStatus', 'Please start a new conversation first', 'error');
                    return;
                }

                // Clear input
                input.value = '';

                // Add user message to chat
                this.addChatMessage('user', message);

                // Send to server
                this.sendMessage({
                    type: 'chat_message',
                    conversation_id: this.currentConversationId,
                    message: message,
                    voice_name: voiceName
                });

                this.showProgress('chatProgress', 'chatProgressBar', 20, 'Sending message...');
            }

            addChatMessage(role, content, audioFile = null) {
                const messagesContainer = document.getElementById('chatMessages');
                const messageDiv = document.createElement('div');
                messageDiv.className = `chat-message ${role}`;

                let audioHtml = '';
                if (audioFile) {
                    audioHtml = `
                        <div class="message-audio">
                            <audio controls>
                                <source src="${audioFile}" type="audio/wav">
                                Your browser does not support the audio element.
                            </audio>
                        </div>
                    `;
                }

                messageDiv.innerHTML = `
                    <div class="message-content">
                        <strong>${role === 'user' ? 'You' : 'AI Assistant'}:</strong> ${content}
                        ${audioHtml}
                    </div>
                `;

                messagesContainer.appendChild(messageDiv);
                messagesContainer.scrollTop = messagesContainer.scrollHeight;

                // Update message count
                const messageCount = messagesContainer.children.length - 1; // Exclude welcome message
                document.getElementById('chatMessageCount').textContent = `${messageCount} messages`;
            }

            toggleConversationsList() {
                const listContainer = document.getElementById('conversationsList');
                const chatContainer = document.getElementById('chatContainer');

                if (listContainer.classList.contains('hidden')) {
                    // Show conversations list
                    this.loadConversations();
                    listContainer.classList.remove('hidden');
                    chatContainer.classList.add('hidden');
                } else {
                    // Hide conversations list
                    listContainer.classList.add('hidden');
                    if (this.currentConversationId) {
                        chatContainer.classList.remove('hidden');
                    }
                }
            }

            loadConversations() {
                this.sendMessage({
                    type: 'list_conversations',
                    limit: 20
                });
            }

            setExample(text) {
                document.getElementById('chatInput').value = text;
            }

            startVoiceInput() {
                // This would integrate with speech-to-text
                this.showStatus('chatStatus', 'Voice input not implemented yet', 'info');
            }

            handleChatResponse(message) {
                this.hideProgress('chatProgress');
                
                // Add assistant response to chat
                this.addChatMessage('assistant', message.assistant_message, message.audio_file);
                
                this.showStatus('chatStatus', 'Response received!', 'success');
            }

            handleConversationStarted(message) {
                this.currentConversationId = message.conversation_id;
                document.getElementById('chatTitle').textContent = message.title;
                document.getElementById('chatLanguage').textContent = message.language;
                
                // Show chat container
                document.getElementById('chatContainer').classList.remove('hidden');
                document.getElementById('conversationsList').classList.add('hidden');
                
                // Clear previous messages except welcome
                const messagesContainer = document.getElementById('chatMessages');
                const welcomeMessage = document.getElementById('welcomeMessage');
                messagesContainer.innerHTML = '';
                messagesContainer.appendChild(welcomeMessage);
                
                this.showStatus('chatStatus', 'New conversation started!', 'success');
            }

            handleConversationsList(message) {
                const container = document.getElementById('conversationsContainer');
                
                if (message.conversations.length === 0) {
                    container.innerHTML = '<p>No conversations yet. Start your first chat!</p>';
                    return;
                }

                container.innerHTML = message.conversations.map(conv => `
                    <div class="conversation-item" onclick="app.loadConversation('${conv.id}')">
                        <h4>${conv.title}</h4>
                        <p>Language: ${conv.language} • Created: ${new Date(conv.created_at).toLocaleDateString()}</p>
                        <p>Last updated: ${new Date(conv.updated_at).toLocaleString()}</p>
                    </div>
                `).join('');
            }

            loadConversation(conversationId) {
                this.sendMessage({
                    type: 'get_conversation',
                    conversation_id: conversationId
                });
            }

            handleConversationDetails(message) {
                this.currentConversationId = message.conversation.id;
                document.getElementById('chatTitle').textContent = message.conversation.title;
                document.getElementById('chatLanguage').textContent = message.conversation.language;
                
                // Load messages
                const messagesContainer = document.getElementById('chatMessages');
                const welcomeMessage = document.getElementById('welcomeMessage');
                messagesContainer.innerHTML = '';
                messagesContainer.appendChild(welcomeMessage);
                
                message.messages.forEach(msg => {
                    this.addChatMessage(msg.role, msg.content, msg.audio_path);
                });
                
                // Show chat container
                document.getElementById('chatContainer').classList.remove('hidden');
                document.getElementById('conversationsList').classList.add('hidden');
            }
        }

        // Initialize app
        const app = new VoiceCloningApp();
    </script>
</body>
</html>
"""

def create_html_interface():
    """Create HTML interface file"""
    with open("static/index.html", "w", encoding="utf-8") as f:
        f.write(HTML_TEMPLATE)
    print("HTML interface created at static/index.html")

if __name__ == "__main__":
    import os
    os.makedirs("static", exist_ok=True)
    create_html_interface()
