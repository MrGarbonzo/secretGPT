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
    walletAddress: null,
    lastScrollTime: 0  // For throttling scroll updates
};

// Chat interface management
const ChatInterface = {
    // Initialize chat interface
    init() {
        console.log('🔮 Initializing SecretGPTee chat interface...');

        this.setupEventListeners();
        this.loadConversationHistory();
        this.initializeUI();

        // Sync wallet state on initialization
        this.syncWalletState();

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
        this.scrollToBottom(true); // Force scroll during initialization
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

        // Sync wallet state before sending message
        this.syncWalletState();
        
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
            const requestData = {
                message: message,
                temperature: ChatState.temperature,
                enable_tools: ChatState.enableTools,
                wallet_connected: ChatState.walletConnected,
                wallet_address: ChatState.walletAddress,
                system_prompt: this.getSystemPrompt()
            };

            // Detect SNIP token queries and add viewing keys
            await this.addViewingKeysToRequest(requestData, message);
            
            console.log('📤 Sending streaming chat request with wallet info:', {
                wallet_connected: requestData.wallet_connected,
                wallet_address: requestData.wallet_address,
                message: requestData.message
            });
            
            const response = await fetch('/secret_gptee/api/v1/chat/stream', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestData)
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            await this.handleStreamingResponse(response, message);
            
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
            const requestData = {
                message: message,
                temperature: ChatState.temperature,
                enable_tools: ChatState.enableTools,
                wallet_connected: ChatState.walletConnected,
                wallet_address: ChatState.walletAddress,
                system_prompt: this.getSystemPrompt()
            };

            // Detect SNIP token queries and add viewing keys
            await this.addViewingKeysToRequest(requestData, message);
            
            console.log('📤 Sending chat request with wallet info:', {
                wallet_connected: requestData.wallet_connected,
                wallet_address: requestData.wallet_address,
                message: requestData.message
            });
            
            const response = await fetch('/secret_gptee/api/v1/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestData)
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

                // Check for transaction in non-streaming response
                const lastMessage = ChatState.messages[ChatState.messages.length - 1];
                if (lastMessage && lastMessage.role === 'assistant') {
                    await this.checkForTransactionRequest(lastMessage.content);
                }
            } else {
                // Check if it's a viewing key error for SNIP tokens
                if (data.error_type === 'viewing_key_required' && data.requires_user_action && window.SNIPTokenManager) {
                    // Auto-trigger viewing key creation
                    await this.autoCreateViewingKey(data, requestData.message);
                } else if (data.error_type === 'viewing_key_required' && data.token && window.SNIPTokenManager) {
                    // Fallback to old behavior if no action flag
                    await this.handleViewingKeyRequired(data, requestData.message);
                } else {
                    this.addMessage('assistant', '❌ ' + (data.error || 'Unknown error occurred'));
                    SecretGPTee.showToast('Chat error: ' + data.error, 'error');
                }
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
    async handleStreamingResponse(response, originalMessage = '') {
        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        this.hideTypingIndicator();
        let assistantMessageId = this.addMessage('assistant', '', { streaming: true });

        let buffer = '';  // Buffer to handle partial SSE events
        let fullMessage = '';  // Track the full message for viewing key detection
        
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
                                    console.log('🔍 Processing chunk type:', data.chunk.type);
                                    if (data.chunk.type === 'content' ||
                                        data.chunk.type === 'mcp_response' ||
                                        data.chunk.type === 'keplr_response' ||
                                        data.chunk.type === 'text_chunk') {
                                        console.log('✅ Appending chunk data:', data.chunk.data.substring(0, 100) + '...');

                                        // Accumulate the full message
                                        fullMessage += data.chunk.data;

                                        // Check if this is a viewing key required response
                                        console.log('🔍 Checking for viewing key error in full message so far');
                                        if (fullMessage.includes('Viewing Key Required') ||
                                            fullMessage.includes('Viewing key required')) {
                                            console.log('🔑 VIEWING KEY REQUIRED DETECTED!');
                                            console.log('🔍 Full message so far:', fullMessage);

                                            // Parse token from the full message - look for SSCRT, SHD, etc
                                            const tokenMatch = fullMessage.match(/query\s+(\w+)\s+balance/i) ||
                                                             fullMessage.match(/to\s+query\s+(\w+)/i) ||
                                                             fullMessage.match(/(\w+)\s+balance/i) ||
                                                             fullMessage.match(/for\s+(\w+)/i);
                                            console.log('🔍 Token match result:', tokenMatch);

                                            if (tokenMatch && tokenMatch[1]) {
                                                const tokenSymbol = tokenMatch[1].toLowerCase();
                                                console.log(`🔑 Detected viewing key required for ${tokenSymbol}`);

                                                // Clear the error message
                                                this.finalizeMessage(assistantMessageId);

                                                // Trigger viewing key creation
                                                this.handleMissingViewingKey(tokenSymbol, originalMessage);
                                                return; // Stop processing this stream
                                            } else {
                                                console.log('⚠️ Waiting for more chunks to parse token...');
                                            }
                                        }

                                        this.appendToMessage(assistantMessageId, data.chunk.data);
                                    } else if (data.chunk.type === 'stream_complete') {
                                        console.log('🏁 Stream completed');
                                    } else {
                                        console.warn('⚠️ Unknown chunk type:', data.chunk.type);
                                    }
                                } else if (!data.success) {
                                    // Check if this is a viewing key required error with action flag
                                    if (data.error_type === 'viewing_key_required' && data.requires_user_action && window.SNIPTokenManager) {
                                        console.log('🔑 Viewing key required with action flag detected in stream');
                                        // Clear any partial error message
                                        this.finalizeMessage(assistantMessageId);
                                        // Auto-trigger viewing key creation
                                        await this.autoCreateViewingKey(data, originalMessage);
                                        return; // Stop processing this stream
                                    } else {
                                        this.appendToMessage(assistantMessageId, '\n\n❌ Error: ' + (data.error || 'Unknown error'));
                                    }
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
        this.scrollToBottom(true); // Force scroll for new messages
        this.saveConversation();
        
        return messageId;
    },
    
    // Append content to existing message
    appendToMessage(messageId, content) {
        const message = ChatState.messages.find(m => m.id === messageId);
        if (message) {
            message.content += content;
            this.updateMessageElement(messageId, message.content);
            // Note: scrollToBottom is called in updateMessageElement
        }
    },
    
    // Finalize streaming message
    finalizeMessage(messageId) {
        const message = ChatState.messages.find(m => m.id === messageId);
        if (message && message.metadata) {
            message.metadata.streaming = false;
            this.updateMessageElement(messageId, message.content, false);

            // Force scroll to ensure completed assistant message is visible
            if (message.role === 'assistant') {
                setTimeout(() => this.scrollToBottom(true), 100);
                this.checkForTransactionRequest(message.content);
            }
        }
    },
    
    // Check if AI response contains transaction request
    async checkForTransactionRequest(content, messageId = null) {
        console.log('🔍 Checking for transaction request in AI response');
        console.log('Content to check:', content);
        
        // Pattern to match transaction prepared messages (multiple formats)
        // Updated to handle formats like "Amount: .1 SCRT (100000 uscrt)" and markdown bold text
        const txPattern = /Transaction prepared:[\s\S]*?From:\s*(secret[a-z0-9]+)[\s\S]*?To:\s*(secret[a-z0-9]+)[\s\S]*?Amount:\s*([\d.]+)\s*SCRT/i;
        const mcpPattern = /secret_send_tokens[:\*\s]*Transaction prepared:[\s\S]*?From:\s*(secret[a-z0-9]+)[\s\S]*?To:\s*(secret[a-z0-9]+)[\s\S]*?Amount:\s*([\d.]+)\s*SCRT/i;
        // Also try a simpler pattern that just looks for the key information
        const simplePattern = /From:\s*(secret[a-z0-9]+)[\s\S]*?To:\s*(secret[a-z0-9]+)[\s\S]*?Amount:\s*([\d.]+)\s*SCRT/i;
        
        console.log('Trying txPattern:', txPattern.test(content));
        console.log('Trying mcpPattern:', mcpPattern.test(content));
        console.log('Trying simplePattern:', simplePattern.test(content));
        
        const match = content.match(txPattern) || content.match(mcpPattern) || content.match(simplePattern);
        
        if (match) {
            const [, fromAddress, toAddress, amount] = match;
            console.log('💰 Transaction detected in AI response:', {
                from: fromAddress,
                to: toAddress,
                amount: amount
            });
            
            // Auto-trigger the transaction if wallet is connected
            if (window.WalletInterface && window.WalletState && window.WalletState.connected) {
                console.log('🚀 Auto-triggering transaction from AI response - calling Keplr directly');
                
                try {
                    // Directly call the wallet's sendTransaction method (like the Send button does)
                    // This will trigger Keplr popup automatically
                    const result = await window.WalletInterface.sendTransaction(toAddress, amount);
                    
                    if (result.success) {
                        console.log('✅ Transaction sent successfully!', result);
                        // Show success message in chat if we have a messageId
                        const successMsg = `\n\n✅ **Transaction sent!**\n**Hash:** ${result.txHash}\n[View on Zonescan](https://zonescan.io/blockchain/secret/explorer/transactions/${result.txHash})`;
                        
                        // Find the latest assistant message to append to
                        const messages = ChatState.messages.filter(m => m.role === 'assistant');
                        const lastAssistantMsg = messages[messages.length - 1];
                        if (lastAssistantMsg) {
                            this.appendToMessage(lastAssistantMsg.id, successMsg);
                        }
                        
                        // Show toast notification
                        if (window.SecretGPTee && window.SecretGPTee.showToast) {
                            window.SecretGPTee.showToast('Transaction sent successfully!', 'success');
                        }
                    }
                } catch (error) {
                    console.error('Transaction failed:', error);
                    const errorMsg = `\n\n❌ **Transaction failed:** ${error.message}`;
                    
                    // Find the latest assistant message to append to
                    const messages = ChatState.messages.filter(m => m.role === 'assistant');
                    const lastAssistantMsg = messages[messages.length - 1];
                    if (lastAssistantMsg) {
                        this.appendToMessage(lastAssistantMsg.id, errorMsg);
                    }
                    
                    // Show toast notification
                    if (window.SecretGPTee && window.SecretGPTee.showToast) {
                        window.SecretGPTee.showToast(`Transaction failed: ${error.message}`, 'error');
                    }
                }
            } else {
                console.log('⚠️ Wallet not connected, cannot auto-trigger transaction');
            }
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
        setTimeout(() => this.scrollToBottom(true), 50); // Force scroll for new messages
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
            
            // Auto-scroll to bottom to keep up with content updates
            console.log('📝 Message updated, calling scrollToBottom()');
            // Force scroll during streaming to ensure content is visible
            this.scrollToBottom(streaming);
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
            this.scrollToBottom(true); // Force scroll when showing typing indicator
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

    // Handle missing viewing key for SNIP tokens
    async handleMissingViewingKey(tokenSymbol, originalMessage) {
        try {
            console.log(`🔐 Handling missing viewing key for ${tokenSymbol}`);

            // Show user that we're creating a viewing key
            this.addMessage('assistant', `🔐 Creating viewing key for ${tokenSymbol.toUpperCase()}...\n\nPlease approve the transaction in Keplr.`);

            // Try to create the viewing key
            if (window.SNIPTokenManager) {
                try {
                    const viewingKey = await window.SNIPTokenManager.createViewingKey(tokenSymbol);

                    // Success! Now query the balance directly
                    this.addMessage('assistant', `✅ Viewing key created successfully! Fetching your ${tokenSymbol.toUpperCase()} balance...`);

                    // Query the balance directly using the new viewing key
                    try {
                        const balanceResult = await window.SNIPTokenManager.querySnip20Balance(tokenSymbol);

                        if (balanceResult.success) {
                            // Show the balance result
                            this.addMessage('assistant', `💎 **${tokenSymbol.toUpperCase()} Token Balance**\n\n${balanceResult.formatted}\n\nAddress: \`${WalletState.address}\``);
                        } else {
                            // If balance query fails, retry the original message
                            this.addMessage('assistant', `⚠️ Couldn't fetch balance directly. Retrying...`);
                            setTimeout(() => {
                                this.sendMessage(originalMessage);
                            }, 1000);
                        }
                    } catch (balanceError) {
                        console.error('Error querying balance after key creation:', balanceError);
                        // Fallback to resending the original query
                        setTimeout(() => {
                            this.sendMessage(originalMessage);
                        }, 1000);
                    }

                } catch (error) {
                    console.error('Failed to create viewing key:', error);

                    if (error.message.includes('User denied') || error.message.includes('Request rejected')) {
                        this.addMessage('assistant', `❌ Transaction cancelled. You need to approve the viewing key creation in Keplr to check your ${tokenSymbol.toUpperCase()} balance.`);
                    } else if (!error.message.includes('createSecret20ViewingKey')) {
                        // Only show error if it's not the old API error
                        this.addMessage('assistant', `❌ Failed to create viewing key: ${error.message}`);
                    }
                }
            } else {
                this.addMessage('assistant', `❌ SNIP token manager not available. Please refresh the page.`);
            }
        } catch (error) {
            console.error('Error in handleMissingViewingKey:', error);
            this.addMessage('assistant', `❌ Error handling viewing key: ${error.message}`);
        }
    },

    // Automatically create viewing key when backend requests it
    async autoCreateViewingKey(errorData, originalMessage) {
        try {
            const tokenSymbol = errorData.token_symbol || errorData.token;
            const contractAddress = errorData.contract_address;

            console.log(`🔑 Auto-triggering viewing key creation for ${tokenSymbol}`);

            // Show user that we're automatically creating the viewing key
            this.addMessage('assistant', `🔐 **Creating Viewing Key for ${tokenSymbol.toUpperCase()}**\n\nI need to create a viewing key to check your balance. Please approve the transaction in your Keplr wallet popup.`);

            // Automatically trigger the viewing key creation
            try {
                const viewingKey = await window.SNIPTokenManager.createViewingKey(tokenSymbol);

                if (viewingKey) {
                    // Success! Show success message
                    this.addMessage('assistant', `✅ Viewing key created successfully! Now fetching your ${tokenSymbol.toUpperCase()} balance...`);

                    // Retry the balance query with the new viewing key
                    setTimeout(async () => {
                        try {
                            console.log(`🔄 Auto-retrying balance query for ${tokenSymbol} with new viewing key`);

                            // Build a fresh request with the new viewing key directly
                            const retryRequestData = {
                                message: originalMessage,
                                temperature: 0.7,
                                enable_tools: true,
                                wallet_connected: ChatState.walletConnected,
                                wallet_address: ChatState.walletAddress,
                                system_prompt: this.getSystemPrompt(),
                                viewing_keys: {},
                                snip_balances: {}
                            };

                            // Add the newly created viewing key directly
                            retryRequestData.viewing_keys[tokenSymbol.toLowerCase()] = viewingKey;

                            // Try to pre-fetch the balance for immediate response
                            if (window.SNIPTokenManager) {
                                try {
                                    const balanceResult = await window.SNIPTokenManager.querySnip20Balance(tokenSymbol);
                                    if (balanceResult && balanceResult.success) {
                                        retryRequestData.snip_balances[tokenSymbol.toLowerCase()] = balanceResult;
                                        console.log(`💎 Pre-fetched ${tokenSymbol} balance for retry:`, balanceResult.formatted);
                                    }
                                } catch (balanceError) {
                                    console.log(`⚠️ Could not pre-fetch balance for ${tokenSymbol}:`, balanceError.message);
                                }
                            }

                            // Send the retry request with the pre-built data
                            const response = await fetch('/secret_gptee/api/v1/chat/stream', {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json',
                                },
                                body: JSON.stringify(retryRequestData)
                            });

                            if (!response.ok) {
                                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                            }

                            // Process the streaming response
                            await this.processStreamingResponse(response, originalMessage);
                        } catch (retryError) {
                            console.error('Auto-retry failed:', retryError);
                            this.addMessage('assistant', `⚠️ Viewing key was created successfully, but the automatic balance query failed. Please ask about your ${tokenSymbol.toUpperCase()} balance again.`);
                        }
                    }, 1500); // Slightly longer delay to ensure viewing key is stored
                }
            } catch (error) {
                console.error('Failed to create viewing key:', error);

                if (error.message.includes('User denied') || error.message.includes('Request rejected')) {
                    this.addMessage('assistant', `❌ **Transaction Cancelled**\n\nYou cancelled the viewing key creation. I need your approval to create a viewing key to check your ${tokenSymbol.toUpperCase()} balance.\n\nWould you like to try again?`);
                } else if (error.message.includes('Insufficient')) {
                    this.addMessage('assistant', `❌ **Insufficient Gas**\n\nYou need some SCRT in your wallet to pay for the transaction fee. Please add SCRT to your wallet and try again.`);
                } else {
                    this.addMessage('assistant', `❌ **Failed to Create Viewing Key**\n\n${error.message}\n\nPlease try again or check your wallet connection.`);
                }
            }
        } catch (error) {
            console.error('Error in autoCreateViewingKey:', error);
            this.addMessage('assistant', `❌ Error creating viewing key: ${error.message}`);
        }
    },

    // Handle viewing key required error for SNIP tokens (old behavior)
    async handleViewingKeyRequired(errorData, originalMessage) {
        try {
            const tokenSymbol = errorData.token;
            const contractAddress = errorData.contract_address;

            console.log(`🔑 Handling viewing key required for ${tokenSymbol}`);

            // Show user that viewing key is needed
            this.addMessage('assistant', `🔑 **Viewing Key Required**\n\nTo query your ${tokenSymbol.toUpperCase()} balance, you need a viewing key. Would you like me to help you create one?`);

            // Try to handle the viewing key creation
            const viewingKey = await window.SNIPTokenManager.handleViewingKeyError(tokenSymbol, contractAddress);

            if (viewingKey) {
                // Viewing key created successfully, retry the original query
                this.addMessage('assistant', `✅ Viewing key created! Let me retry your ${tokenSymbol.toUpperCase()} balance query...`);

                // Re-send the original message to get the balance
                setTimeout(async () => {
                    try {
                        const requestData = this.buildRequestData(originalMessage);

                        const response = await fetch('/secret_gptee/api/v1/chat', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify({
                                ...requestData,
                                viewing_key: viewingKey,
                                token_symbol: tokenSymbol
                            })
                        });

                        if (!response.ok) {
                            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                        }

                        const retryData = await response.json();

                        if (retryData.success) {
                            this.addMessage('assistant', retryData.response, {
                                model: retryData.model,
                                tools_used: retryData.tools_used
                            });
                        } else {
                            this.addMessage('assistant', `❌ Still unable to query ${tokenSymbol.toUpperCase()} balance: ${retryData.error || 'Unknown error'}`);
                        }

                    } catch (error) {
                        console.error('Retry query failed:', error);
                        this.addMessage('assistant', `❌ Failed to retry ${tokenSymbol.toUpperCase()} balance query. Please try again.`);
                    }
                }, 1000); // Small delay to let viewing key propagate

            } else {
                // User cancelled or viewing key creation failed
                this.addMessage('assistant', `⚠️ Unable to create viewing key for ${tokenSymbol.toUpperCase()}. You can try again later or create one manually in your Keplr wallet.`);
            }

        } catch (error) {
            console.error('Error handling viewing key requirement:', error);
            this.addMessage('assistant', `❌ Error handling viewing key: ${error.message}`);
        }
    },

    // Build request data for API calls
    buildRequestData(message) {
        return {
            message: message,
            wallet_connected: ChatState.walletConnected,
            wallet_address: ChatState.walletAddress,
            temperature: ChatState.temperature,
            streaming: ChatState.streaming
        };
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
        this.scrollToBottom(true); // Force scroll to welcome message
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
    
    // Scroll to bottom of chat (simplified and more reliable)
    scrollToBottom(force = false) {
        const messagesContainer = document.getElementById('messages');
        console.log('🔍 scrollToBottom called:', { force, containerFound: !!messagesContainer });
        
        if (messagesContainer) {
            const scrollHeight = messagesContainer.scrollHeight;
            const scrollTop = messagesContainer.scrollTop;
            const clientHeight = messagesContainer.clientHeight;
            const distanceFromBottom = scrollHeight - scrollTop - clientHeight;
            
            console.log('📏 Scroll metrics:', {
                scrollHeight,
                scrollTop,
                clientHeight,
                distanceFromBottom,
                isAtBottom: distanceFromBottom < 5
            });
            
            // Always scroll if forced, or if we're close to bottom (within 150px for better UX)
            const shouldScroll = force || distanceFromBottom < 150;
            
            if (shouldScroll) {
                console.log('⬇️ Scrolling to bottom');

                // Enhanced scrolling with multiple fallbacks
                messagesContainer.scrollTop = messagesContainer.scrollHeight;

                // Use requestAnimationFrame for better timing
                requestAnimationFrame(() => {
                    messagesContainer.scrollTo({
                        top: messagesContainer.scrollHeight,
                        behavior: 'smooth'
                    });

                    // Final fallback to ensure visibility
                    setTimeout(() => {
                        messagesContainer.scrollTop = messagesContainer.scrollHeight;
                        console.log('🔄 Final scroll applied');
                    }, 200);
                });
                setTimeout(() => {
                    messagesContainer.scrollTop = messagesContainer.scrollHeight;
                }, 50);
            } else {
                console.log('⏸️ Not scrolling - user scrolled up (distance:', distanceFromBottom, ')');
            }
        } else {
            console.warn('❌ Messages container #messages not found');
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
                this.scrollToBottom(true); // Force scroll when loading history
            }
        } catch (error) {
            console.error('Failed to load conversation history:', error);
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
    },

    // Sync wallet state from localStorage and WalletState
    syncWalletState() {
        // Check localStorage for wallet connection
        const savedAddress = localStorage.getItem('secretgptee-wallet-address');
        const savedConnected = localStorage.getItem('secretgptee-wallet-connected') === 'true';

        // Update ChatState if wallet is connected
        if (savedConnected && savedAddress) {
            ChatState.walletConnected = true;
            ChatState.walletAddress = savedAddress;
            console.log('📱 Wallet state synced:', {
                connected: ChatState.walletConnected,
                address: ChatState.walletAddress
            });
        } else {
            ChatState.walletConnected = false;
            ChatState.walletAddress = null;
            console.log('📱 No wallet connected');
        }

        // Also check if WalletState is available and use it
        if (window.WalletState && window.WalletState.connected) {
            ChatState.walletConnected = true;
            ChatState.walletAddress = window.WalletState.address;
            console.log('📱 Synced from WalletState:', {
                connected: ChatState.walletConnected,
                address: ChatState.walletAddress
            });
        }
    },

    // Detect SNIP token queries and add viewing keys from Keplr
    async addViewingKeysToRequest(requestData, message) {
        console.log('🔍 CACHE TEST: addViewingKeysToRequest function updated v2025081414');

        if (!ChatState.walletConnected) {
            console.log('❌ Wallet not connected, skipping viewing key detection');
            return;
        }

        if (!window.SNIPTokenManager) {
            console.log('❌ SNIPTokenManager not available, skipping viewing key detection');
            return;
        }

        console.log('✅ Wallet connected and SNIPTokenManager available');

        try {
            // Detect if message contains SNIP token queries
            const messageLower = message.toLowerCase();
            console.log(`🔍 Analyzing message: "${messageLower}"`);

            // All supported SNIP tokens from backend registry
            const snipTokens = [
                'sscrt', 'silk', 'shd', 'stkd-scrt', 'sstjuno', 'sstatom', 'sstluna', 'sstosmo',
                'sinj', 'swbtc', 'susdt', 'snobleusdc', 'sdydx', 'sarch', 'sakt', 'stia',
                'butt', 'alter', 'amber'
            ];

            // Token aliases for natural language queries
            const tokenAliases = {
                'eth': ['seth', 'steth'],
                'ethereum': ['seth', 'steth'],
                'btc': ['sbtc', 'swbtc'],
                'bitcoin': ['sbtc', 'swbtc'],
                'wbtc': ['swbtc'],
                'usdt': ['susdt'],
                'tether': ['susdt'],
                'usdc': ['snobleusdc'],
                'dydx': ['sdydx'],
                'injective': ['sinj'],
                'inj': ['sinj'],
                'arch': ['sarch'],
                'akash': ['sakt'],
                'akt': ['sakt'],
                'celestia': ['stia'],
                'tia': ['stia'],
                'juno': ['sstjuno'],
                'atom': ['sstatom'],
                'luna': ['sstluna'],
                'osmo': ['sstosmo'],
                'osmosis': ['sstosmo'],
                'scrt': ['sscrt', 'stkd-scrt']
            };

            // Check for token aliases first, then direct matches
            let requestedTokens = [];

            // Check aliases
            for (const [alias, actualTokens] of Object.entries(tokenAliases)) {
                if (messageLower.includes(alias) &&
                    (messageLower.includes('balance') || messageLower.includes('how much'))) {
                    requestedTokens.push(...actualTokens);
                }
            }

            // Check direct token matches
            const directMatches = snipTokens.filter(token =>
                messageLower.includes(token) &&
                (messageLower.includes('balance') || messageLower.includes('how much'))
            );

            requestedTokens.push(...directMatches);

            // Remove duplicates
            requestedTokens = [...new Set(requestedTokens)];

            if (requestedTokens.length > 0) {
                console.log(`🔍 Detected SNIP token query for: ${requestedTokens.join(', ')}`);

                // Get viewing keys and query balances directly for detected tokens
                const viewingKeys = {};
                const snipBalances = {};

                for (const token of requestedTokens) {
                    try {
                        console.log(`🔑 Attempting to get viewing key for ${token}...`);
                        const viewingKey = await window.SNIPTokenManager.getViewingKey(token);

                        if (viewingKey) {
                            viewingKeys[token] = viewingKey;
                            console.log(`✅ Retrieved viewing key for ${token}: KEY_EXISTS`);

                            // Query balance directly using SecretJS in browser
                            console.log(`💰 Querying ${token} balance directly in browser...`);
                            try {
                                const balanceResult = await window.SNIPTokenManager.querySnip20Balance(token);

                                if (balanceResult.success) {
                                    console.log(`✅ Got ${token} balance: ${balanceResult.formatted}`);
                                    snipBalances[token] = balanceResult;
                                } else {
                                    console.log(`⚠️ Failed to query ${token} balance:`, balanceResult.error);
                                }
                            } catch (balanceError) {
                                console.error(`❌ Error querying ${token} balance:`, balanceError);
                            }
                        } else {
                            console.log(`❌ No viewing key found for ${token}`);
                        }
                    } catch (error) {
                        console.log(`⚠️ No viewing key found for ${token}:`, error.message);
                        // Continue with other tokens - backend will handle missing keys
                    }
                }

                // Add viewing keys to request if any were found
                if (Object.keys(viewingKeys).length > 0) {
                    requestData.viewing_keys = viewingKeys;
                    console.log(`📤 Added ${Object.keys(viewingKeys).length} viewing keys to request:`, Object.keys(viewingKeys));
                }

                // Add SNIP balances to request if any were found
                if (Object.keys(snipBalances).length > 0) {
                    requestData.snip_balances = snipBalances;
                    console.log(`💎 Added ${Object.keys(snipBalances).length} SNIP balances to request:`, snipBalances);
                }

                if (Object.keys(viewingKeys).length === 0 && Object.keys(snipBalances).length === 0) {
                    console.log('❌ No viewing keys or balances retrieved, backend will handle viewing key requirement');
                }
            } else {
                console.log(`❌ No SNIP token queries detected in: "${messageLower}"`);
            }
        } catch (error) {
            console.error('Error detecting SNIP tokens or getting viewing keys:', error);
            // Continue without viewing keys - backend will handle the error
        }
    }
};

// Export for global access
window.ChatInterface = ChatInterface;
window.ChatState = ChatState;  // Make ChatState globally accessible

// Global initialization function for HTML
window.initializeChat = function() {
    ChatInterface.init();
};

// Global sync function for wallet integration
window.syncWalletWithChat = function() {
    console.log('🔄 Syncing wallet with chat...');
    if (window.ChatInterface) {
        window.ChatInterface.syncWalletState();
    }
};

// Global function to clear chat history (for testing)
window.clearChatHistory = function() {
    ChatInterface.clearConversationHistory();
};