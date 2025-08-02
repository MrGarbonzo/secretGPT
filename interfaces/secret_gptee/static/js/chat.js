// SecretGPTee Chat Interface JavaScript

// Chat interface state
const ChatState = {
    messages: [],
    isStreaming: false,
    currentStreamId: null,
    conversationId: null,
    temperature: 0.7,
    enableTools: true,
    walletConnected: false,
    walletAddress: null
};

// Chat interface management
const ChatInterface = {
    // Initialize chat interface
    init() {
        console.log('🔮 Initializing SecretGPTee chat interface...');
        
        this.setupEventListeners();
        this.loadConversationHistory();
        this.initializeUI();
        
        console.log('✅ Chat interface initialized');
    },
    
    // Setup event listeners
    setupEventListeners() {
        const messageInput = document.getElementById('message-input');
        const sendBtn = document.getElementById('send-btn');
        const newChatBtn = document.getElementById('new-chat-btn');
        const clearChatBtn = document.getElementById('clear-chat-btn');
        const exportChatBtn = document.getElementById('export-chat-btn');
        
        // Message input handlers
        if (messageInput) {
            messageInput.addEventListener('input', this.handleInputChange.bind(this));
            messageInput.addEventListener('keydown', this.handleKeyDown.bind(this));
            messageInput.addEventListener('paste', this.handlePaste.bind(this));
        }
        
        // Button handlers
        if (sendBtn) {
            sendBtn.addEventListener('click', this.handleSendClick.bind(this));
        }
        
        if (newChatBtn) {
            newChatBtn.addEventListener('click', this.startNewChat.bind(this));
        }
        
        if (clearChatBtn) {
            clearChatBtn.addEventListener('click', this.clearChat.bind(this));
        }
        
        if (exportChatBtn) {
            exportChatBtn.addEventListener('click', this.exportChat.bind(this));
        }
        
        // Temperature slider
        const tempSlider = document.getElementById('temperature-slider');
        if (tempSlider) {
            tempSlider.addEventListener('input', this.handleTemperatureChange.bind(this));
        }
    },
    
    // Initialize UI elements
    initializeUI() {
        this.updateSendButton();
        this.updateTemperatureDisplay();
        this.scrollToBottom();
    },
    
    // Handle input change
    handleInputChange(event) {
        const input = event.target;
        
        // Auto-resize textarea
        input.style.height = 'auto';
        input.style.height = Math.min(input.scrollHeight, 120) + 'px';
        
        // Update character count
        this.updateCharCount(input.value.length);
        
        // Update send button state
        this.updateSendButton();
        
        // Show/hide input suggestions
        this.updateInputSuggestions(input.value);
    },
    
    // Handle keydown events
    handleKeyDown(event) {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            if (!ChatState.isStreaming) {
                this.sendMessage();
            }
        }
    },
    
    // Handle paste events
    handlePaste(event) {
        // Future: Handle file attachments, images, etc.
        console.log('Paste event detected');
    },
    
    // Handle send button click  
    handleSendClick() {
        if (!ChatState.isStreaming) {
            this.sendMessage();
        }
    },
    
    // Handle temperature change
    handleTemperatureChange(event) {
        ChatState.temperature = parseFloat(event.target.value);
        this.updateTemperatureDisplay();
        
        // Save to local storage
        this.saveSettings();
    },
    
    // Send message
    async sendMessage(message = null) {
        const messageInput = document.getElementById('message-input');
        const messageText = message || messageInput?.value?.trim();
        
        if (!messageText || ChatState.isStreaming) {
            return;
        }
        
        try {
            // Add user message to chat
            this.addMessage('user', messageText);
            
            // Clear input
            if (messageInput) {
                messageInput.value = '';
                messageInput.style.height = 'auto';
                this.updateCharCount(0);
                this.updateSendButton();
            }
            
            // Show typing indicator
            this.showTypingIndicator();
            
            // Send message to API
            if (AppState.streaming) {
                await this.sendStreamingMessage(messageText);
            } else {
                await this.sendDirectMessage(messageText);
            }
            
        } catch (error) {
            console.error('Error sending message:', error);
            this.hideTypingIndicator();
            this.addMessage('assistant', '❌ Sorry, there was an error sending your message. Please try again.');
            SecretGPTee.showToast('Failed to send message', 'error');
        }
    },
    
    // Send streaming message
    async sendStreamingMessage(message) {
        ChatState.isStreaming = true;
        this.updateSendButton();
        
        try {
            const response = await fetch('/api/v1/chat/stream', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    temperature: ChatState.temperature,
                    enable_tools: ChatState.enableTools,
                    wallet_connected: ChatState.walletConnected,
                    wallet_address: ChatState.walletAddress,
                    system_prompt: this.getSystemPrompt()
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            await this.handleStreamingResponse(response);
            
        } catch (error) {
            console.error('Streaming error:', error);
            this.hideTypingIndicator();
            this.addMessage('assistant', '❌ Connection error. Please check your network and try again.');
            SecretGPTee.showToast('Connection error', 'error');
        } finally {
            ChatState.isStreaming = false;
            this.updateSendButton();
        }
    },
    
    // Send direct message (non-streaming)
    async sendDirectMessage(message) {
        ChatState.isStreaming = true;
        this.updateSendButton();
        
        try {
            const response = await fetch('/api/v1/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    temperature: ChatState.temperature,
                    enable_tools: ChatState.enableTools,
                    wallet_connected: ChatState.walletConnected,
                    wallet_address: ChatState.walletAddress,
                    system_prompt: this.getSystemPrompt()
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            this.hideTypingIndicator();
            
            if (data.success) {
                this.addMessage('assistant', data.response, {
                    model: data.model,
                    tools_used: data.tools_used
                });
            } else {
                this.addMessage('assistant', '❌ ' + (data.error || 'Unknown error occurred'));
                SecretGPTee.showToast('Chat error: ' + data.error, 'error');
            }
            
        } catch (error) {
            console.error('Direct message error:', error);
            this.hideTypingIndicator();
            this.addMessage('assistant', '❌ Connection error. Please check your network and try again.');
            SecretGPTee.showToast('Connection error', 'error');
        } finally {
            ChatState.isStreaming = false;
            this.updateSendButton();
        }
    },
    
    // Handle streaming response
    async handleStreamingResponse(response) {
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        
        this.hideTypingIndicator();
        let assistantMessageId = this.addMessage('assistant', '', { streaming: true });
        
        let buffer = '';  // Buffer to handle partial SSE events
        
        try {
            while (true) {
                const { done, value } = await reader.read();
                
                if (done) break;
                
                // Decode chunk and add to buffer
                buffer += decoder.decode(value, { stream: true });
                
                // Process complete SSE events (separated by \n\n)
                let eventEndIndex;
                while ((eventEndIndex = buffer.indexOf('\n\n')) !== -1) {
                    const eventData = buffer.slice(0, eventEndIndex);
                    buffer = buffer.slice(eventEndIndex + 2);  // Remove processed event
                    
                    // Parse SSE event
                    const lines = eventData.split('\n');
                    for (const line of lines) {
                        if (line.startsWith('data: ')) {
                            try {
                                const jsonStr = line.slice(6);  // Remove 'data: ' prefix
                                const data = JSON.parse(jsonStr);
                                
                                console.log('SSE Event received:', data);
                                
                                if (data.success && data.chunk) {
                                    if (data.chunk.type === 'content' || 
                                        data.chunk.type === 'mcp_response' || 
                                        data.chunk.type === 'text_chunk') {
                                        this.appendToMessage(assistantMessageId, data.chunk.data);
                                    } else if (data.chunk.type === 'stream_complete') {
                                        console.log('Stream completed');
                                    }
                                } else if (!data.success) {
                                    this.appendToMessage(assistantMessageId, '\n\n❌ Error: ' + (data.error || 'Unknown error'));
                                    break;
                                }
                            } catch (e) {
                                console.warn('Failed to parse SSE data:', line, 'Error:', e);
                            }
                            break;  // Only process first data line per event
                        }
                    }
                }
            }
        } catch (error) {
            console.error('Stream reading error:', error);
            this.appendToMessage(assistantMessageId, '\n\n❌ Stream interrupted: ' + error.message);
        } finally {
            this.finalizeMessage(assistantMessageId);
        }
    },
    
    // Add message to chat
    addMessage(role, content, metadata = {}) {
        const messageId = 'msg_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        
        const message = {
            id: messageId,
            role: role,
            content: content,
            timestamp: new Date(),
            metadata: metadata
        };
        
        ChatState.messages.push(message);
        this.renderMessage(message);
        this.scrollToBottom();
        this.saveConversation();
        
        return messageId;
    },
    
    // Append content to existing message
    appendToMessage(messageId, content) {
        const message = ChatState.messages.find(m => m.id === messageId);
        if (message) {
            message.content += content;
            this.updateMessageElement(messageId, message.content);
        }
    },
    
    // Finalize streaming message
    finalizeMessage(messageId) {
        const message = ChatState.messages.find(m => m.id === messageId);
        if (message && message.metadata) {
            message.metadata.streaming = false;
            this.updateMessageElement(messageId, message.content, false);
        }
    },
    
    // Render message in chat
    renderMessage(message) {
        const messagesContainer = document.getElementById('messages');
        if (!messagesContainer) return;
        
        const messageWrapper = document.createElement('div');
        messageWrapper.className = 'message-wrapper';
        messageWrapper.id = `wrapper-${message.id}`;
        
        const messageElement = document.createElement('div');
        messageElement.className = `message ${message.role}-message`;
        messageElement.id = message.id;
        
        // Message avatar
        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        
        if (message.role === 'user') {
            avatar.innerHTML = '<i class="fas fa-user"></i>';
        } else {
            avatar.innerHTML = '<i class="fas fa-robot"></i>';
        }
        
        // Message content
        const content = document.createElement('div');
        content.className = 'message-content';
        
        // Message header (for assistant messages)
        if (message.role === 'assistant') {
            const header = document.createElement('div');
            header.className = 'message-header';
            header.innerHTML = `
                <span class="message-sender">SecretGPTee</span>
                <div class="trust-indicators">
                    <span class="trust-badge verified" title="Fully Attested">
                        <i class="fas fa-shield-alt"></i>
                        Verified
                    </span>
                    <span class="privacy-badge" title="Private & Encrypted">
                        <i class="fas fa-lock"></i>
                        Private
                    </span>
                </div>
            `;
            content.appendChild(header);
        }
        
        // Message text
        const textElement = document.createElement('div');
        textElement.className = 'message-text';
        textElement.innerHTML = this.formatMessageContent(message.content);
        content.appendChild(textElement);
        
        // Message metadata (timestamp, tools used, etc.)
        const metaElement = document.createElement('div');
        metaElement.className = 'message-meta';
        metaElement.innerHTML = this.formatMessageMeta(message);
        content.appendChild(metaElement);
        
        messageElement.appendChild(avatar);
        messageElement.appendChild(content);
        messageWrapper.appendChild(messageElement);
        
        messagesContainer.appendChild(messageWrapper);
        
        // Auto-scroll to bottom after adding message
        setTimeout(() => this.scrollToBottom(), 100);
    },
    
    // Update existing message element
    updateMessageElement(messageId, content, streaming = true) {
        const messageElement = document.getElementById(messageId);
        if (!messageElement) return;
        
        const textElement = messageElement.querySelector('.message-text');
        if (textElement) {
            textElement.innerHTML = this.formatMessageContent(content);
            
            // Add streaming indicator
            if (streaming) {
                textElement.classList.add('streaming');
            } else {
                textElement.classList.remove('streaming');
            }
        }
    },
    
    // Format message content (markdown, links, etc.)
    formatMessageContent(content) {
        if (!content) return '';
        
        // Basic markdown formatting
        let formatted = content
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/`(.*?)`/g, '<code>$1</code>')
            .replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>')
            .replace(/\n/g, '<br>');
        
        // Convert URLs to links
        formatted = formatted.replace(
            /(https?:\/\/[^\s]+)/g,
            '<a href="$1" target="_blank" rel="noopener">$1</a>'
        );
        
        return formatted;
    },
    
    // Format message metadata
    formatMessageMeta(message) {
        const parts = [];
        
        // Timestamp with fallback
        let timestampStr = 'now';
        try {
            if (message.timestamp) {
                timestampStr = SecretGPTee.formatTimestamp(message.timestamp);
            }
        } catch (error) {
            console.warn('Error formatting timestamp:', error, message.timestamp);
            timestampStr = 'now';
        }
        parts.push(`<span class="timestamp">${timestampStr}</span>`);
        
        // Model info (for assistant messages)
        if (message.role === 'assistant' && message.metadata.model) {
            parts.push(`<span class="model-info">${message.metadata.model}</span>`);
        }
        
        // Tools used
        if (message.metadata.tools_used && message.metadata.tools_used.length > 0) {
            parts.push(`<span class="tools-used">🛠️ ${message.metadata.tools_used.join(', ')}</span>`);
        }
        
        return parts.join(' • ');
    },
    
    // Show typing indicator
    showTypingIndicator() {
        const indicator = document.getElementById('typing-indicator');
        if (indicator) {
            indicator.style.display = 'block';
            this.scrollToBottom();
        }
    },
    
    // Hide typing indicator
    hideTypingIndicator() {
        const indicator = document.getElementById('typing-indicator');
        if (indicator) {
            indicator.style.display = 'none';
        }
    },
    
    // Update character count
    updateCharCount(count) {
        const charCount = document.querySelector('.char-count');
        if (charCount) {
            const maxLength = 4000;
            charCount.textContent = `${count} / ${maxLength}`;
            
            // Visual feedback for approaching limit
            if (count > maxLength * 0.9) {
                charCount.style.color = 'var(--warning-color)';
            } else if (count > maxLength * 0.8) {
                charCount.style.color = 'var(--accent-color)';
            } else {
                charCount.style.color = 'var(--text-muted)';
            }
        }
    },
    
    // Update send button state
    updateSendButton() {
        const sendBtn = document.getElementById('send-btn');
        const messageInput = document.getElementById('message-input');
        
        if (sendBtn) {
            const hasText = messageInput && messageInput.value.trim().length > 0;
            const canSend = hasText && !ChatState.isStreaming;
            
            sendBtn.disabled = !canSend;
            sendBtn.innerHTML = ChatState.isStreaming 
                ? '<i class="fas fa-spinner fa-spin"></i>' 
                : '<i class="fas fa-paper-plane"></i>';
        }
    },
    
    // Update temperature display
    updateTemperatureDisplay() {
        const tempValue = document.getElementById('temp-value');
        if (tempValue) {
            tempValue.textContent = ChatState.temperature.toFixed(1);
        }
        
        const tempSlider = document.getElementById('temperature-slider');
        if (tempSlider) {
            tempSlider.value = ChatState.temperature;
        }
    },
    
    // Update input suggestions
    updateInputSuggestions(input) {
        const suggestions = document.getElementById('input-suggestions');
        if (!suggestions) return;
        
        // Smart suggestions based on input
        const suggestionsData = this.generateSuggestions(input);
        
        if (suggestionsData.length > 0) {
            suggestions.innerHTML = suggestionsData.map(s => 
                `<div class="suggestion-item" onclick="ChatInterface.applySuggestion('${s}')">${s}</div>`
            ).join('');
            suggestions.style.display = 'block';
        } else {
            suggestions.style.display = 'none';
        }
    },
    
    // Generate smart suggestions
    generateSuggestions(input) {
        const suggestions = [];
        const inputLower = input.toLowerCase();
        
        // Wallet-related suggestions
        if (inputLower.includes('balance') || inputLower.includes('scrt')) {
            suggestions.push("What's my SCRT balance?");
            suggestions.push("Show my Secret Network balance");
        }
        
        if (inputLower.includes('send') && ChatState.walletConnected) {
            suggestions.push("Send 10 SCRT to secret1...");
            suggestions.push("Send tokens to another address");
        }
        
        // Blockchain suggestions
        if (inputLower.includes('secret network') || inputLower.includes('network')) {
            suggestions.push("What is Secret Network?");
            suggestions.push("Secret Network status");
            suggestions.push("Latest Secret Network block");
        }
        
        // General suggestions when empty
        if (!input.trim()) {
            suggestions.push("What is Secret Network?");
            suggestions.push("How does privacy work here?");
            suggestions.push("Show me Secret Network status");
            if (ChatState.walletConnected) {
                suggestions.push("What's my balance?");
            }
        }
        
        return suggestions.slice(0, 4); // Max 4 suggestions
    },
    
    // Apply suggestion
    applySuggestion(suggestion) {
        const messageInput = document.getElementById('message-input');
        if (messageInput) {
            messageInput.value = suggestion;
            messageInput.focus();
            this.handleInputChange({ target: messageInput });
        }
        
        // Hide suggestions
        const suggestions = document.getElementById('input-suggestions');
        if (suggestions) {
            suggestions.style.display = 'none';
        }
    },
    
    // Get system prompt
    getSystemPrompt() {
        let prompt = "You are SecretGPTee, a helpful AI assistant integrated with the Secret Network blockchain. You can help with both general questions and blockchain-specific queries.";
        
        if (ChatState.walletConnected && ChatState.walletAddress) {
            prompt += `\n\nThe user has connected their Keplr wallet with address: ${ChatState.walletAddress}. You can help them with Secret Network transactions, balance queries, and other blockchain operations.`;
        }
        
        return prompt;
    },
    
    // Start new chat
    startNewChat() {
        if (ChatState.messages.length > 0) {
            if (confirm('Are you sure you want to start a new chat? Current conversation will be saved.')) {
                this.saveConversation();
                this.clearMessages();
                this.showWelcomeMessage();
            }
        }
    },
    
    // Clear chat
    clearChat() {
        if (confirm('Are you sure you want to clear this conversation? This action cannot be undone.')) {
            this.clearMessages();
            this.showWelcomeMessage();
        }
    },
    
    // Clear all messages
    clearMessages() {
        ChatState.messages = [];
        const messagesContainer = document.getElementById('messages');
        if (messagesContainer) {
            // Keep welcome message, remove others
            const messages = messagesContainer.querySelectorAll('.message-wrapper:not(.welcome-message)');
            messages.forEach(msg => msg.remove());
        }
    },
    
    // Show welcome message
    showWelcomeMessage() {
        // Welcome message is in the HTML template
        this.scrollToBottom();
    },
    
    // Export chat
    exportChat() {
        const format = prompt('Export format:\n1. JSON\n2. Markdown\n3. Plain Text\n\nEnter 1, 2, or 3:', '2');
        
        switch (format) {
            case '1':
                this.exportAsJSON();
                break;
            case '2':
                this.exportAsMarkdown();
                break;
            case '3':
                this.exportAsText();
                break;
            default:
                SecretGPTee.showToast('Export cancelled', 'info');
        }
    },
    
    // Export as JSON
    exportAsJSON() {
        const data = {
            conversation_id: ChatState.conversationId,
            timestamp: new Date().toISOString(),
            messages: ChatState.messages,
            settings: {
                temperature: ChatState.temperature,
                enableTools: ChatState.enableTools
            }
        };
        
        this.downloadFile(
            JSON.stringify(data, null, 2),
            `secretgptee-chat-${Date.now()}.json`,
            'application/json'
        );
    },
    
    // Export as Markdown
    exportAsMarkdown() {
        let markdown = `# SecretGPTee Conversation\n\n`;
        markdown += `**Date:** ${new Date().toLocaleDateString()}\n`;
        markdown += `**Messages:** ${ChatState.messages.length}\n\n---\n\n`;
        
        ChatState.messages.forEach(msg => {
            const role = msg.role === 'user' ? '**You**' : '**SecretGPTee**';
            const time = msg.timestamp.toLocaleTimeString();
            markdown += `### ${role} (${time})\n\n${msg.content}\n\n---\n\n`;
        });
        
        this.downloadFile(
            markdown,
            `secretgptee-chat-${Date.now()}.md`,
            'text/markdown'
        );
    },
    
    // Export as plain text
    exportAsText() {
        let text = `SecretGPTee Conversation - ${new Date().toLocaleDateString()}\n`;
        text += `Messages: ${ChatState.messages.length}\n\n`;
        text += '=' .repeat(50) + '\n\n';
        
        ChatState.messages.forEach(msg => {
            const role = msg.role === 'user' ? 'You' : 'SecretGPTee';
            const time = msg.timestamp.toLocaleTimeString();
            text += `${role} (${time}):\n${msg.content}\n\n`;
        });
        
        this.downloadFile(
            text,
            `secretgptee-chat-${Date.now()}.txt`,
            'text/plain'
        );
    },
    
    // Download file helper
    downloadFile(content, filename, mimeType) {
        const blob = new Blob([content], { type: mimeType });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        SecretGPTee.showToast(`Chat exported as ${filename}`, 'success');
    },
    
    // Scroll to bottom of chat
    scrollToBottom() {
        const messagesContainer = document.getElementById('messages');
        if (messagesContainer) {
            setTimeout(() => {
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
            }, 100);
        }
    },
    
    // Load conversation history
    loadConversationHistory() {
        try {
            const saved = localStorage.getItem('secretgptee-current-conversation');
            if (saved) {
                const data = JSON.parse(saved);
                ChatState.messages = (data.messages || []).map(msg => {
                    // Convert timestamp back to Date object if it's a string
                    if (msg.timestamp && typeof msg.timestamp === 'string') {
                        msg.timestamp = new Date(msg.timestamp);
                    }
                    // Ensure metadata exists
                    if (!msg.metadata) {
                        msg.metadata = {};
                    }
                    return msg;
                });
                ChatState.conversationId = data.conversation_id;
                
                // Re-render messages
                ChatState.messages.forEach(msg => this.renderMessage(msg));
                this.scrollToBottom();
            }
        } catch (error) {
            console.error('Failed to load conversation history:', error);
        }
    },
    
    // Scroll to bottom of messages area
    scrollToBottom(smooth = true) {
        try {
            const messagesArea = document.getElementById('messages');
            if (messagesArea) {
                const scrollOptions = {
                    top: messagesArea.scrollHeight,
                    behavior: smooth ? 'smooth' : 'auto'
                };
                messagesArea.scrollTo(scrollOptions);
                
                // Also try scrolling the main container if needed
                const chatContainer = document.querySelector('.chat-container');
                if (chatContainer) {
                    chatContainer.scrollTo({
                        top: chatContainer.scrollHeight,
                        behavior: smooth ? 'smooth' : 'auto'
                    });
                }
            }
        } catch (error) {
            console.error('Error scrolling to bottom:', error);
        }
    },
    
    // Save conversation
    saveConversation() {
        try {
            if (!ChatState.conversationId) {
                ChatState.conversationId = 'conv_' + Date.now();
            }
            
            const data = {
                conversation_id: ChatState.conversationId,
                timestamp: new Date().toISOString(),
                messages: ChatState.messages
            };
            
            localStorage.setItem('secretgptee-current-conversation', JSON.stringify(data));
        } catch (error) {
            console.error('Failed to save conversation:', error);
        }
    },
    
    // Clear conversation history
    clearConversationHistory() {
        try {
            // Clear from memory
            ChatState.messages = [];
            ChatState.conversationId = null;
            
            // Clear from localStorage
            localStorage.removeItem('secretgptee-current-conversation');
            
            // Clear messages from UI
            const messagesContainer = document.getElementById('messages');
            if (messagesContainer) {
                // Keep the welcome message, remove others
                const welcomeMessage = messagesContainer.querySelector('.welcome-message');
                messagesContainer.innerHTML = '';
                if (welcomeMessage) {
                    messagesContainer.appendChild(welcomeMessage);
                }
            }
            
            console.log('Conversation history cleared');
        } catch (error) {
            console.error('Failed to clear conversation history:', error);
        }
    },
    
    // Save settings
    saveSettings() {
        try {
            const settings = {
                temperature: ChatState.temperature,
                enableTools: ChatState.enableTools
            };
            
            localStorage.setItem('secretgptee-chat-settings', JSON.stringify(settings));
        } catch (error) {
            console.error('Failed to save chat settings:', error);
        }
    },
    
    // Load settings
    loadSettings() {
        try {
            const saved = localStorage.getItem('secretgptee-chat-settings');
            if (saved) {
                const settings = JSON.parse(saved);
                ChatState.temperature = settings.temperature || 0.7;
                ChatState.enableTools = settings.enableTools !== false;
                
                this.updateTemperatureDisplay();
            }
        } catch (error) {
            console.error('Failed to load chat settings:', error);
        }
    },
    
    // Update temperature
    updateTemperature(temperature) {
        ChatState.temperature = temperature;
        this.updateTemperatureDisplay();
        this.saveSettings();
    }
};

// Export for global access
window.ChatInterface = ChatInterface;

// Global initialization function for HTML
window.initializeChat = function() {
    ChatInterface.init();
};

// Global function to clear chat history (for testing)
window.clearChatHistory = function() {
    ChatInterface.clearConversationHistory();
};