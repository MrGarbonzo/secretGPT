// secretGPT Web UI - Chat-specific JavaScript

class ChatManager {
    constructor() {
        this.conversationHistory = [];
        this.isStreaming = false;
        this.streamingEnabled = true;
        this.activeStreams = new Map();
        this.currentStreamId = null;
    }

    formatMessage(content) {
        // Format message content for display
        // Handle code blocks, links, etc.
        
        // Basic markdown-like formatting
        content = content.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        content = content.replace(/\*(.*?)\*/g, '<em>$1</em>');
        content = content.replace(/`(.*?)`/g, '<code>$1</code>');
        
        // Handle code blocks
        content = content.replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>');
        
        // Handle URLs
        content = content.replace(/(https?:\/\/[^\s]+)/g, '<a href="$1" target="_blank">$1</a>');
        
        return content;
    }

    addToHistory(role, content) {
        this.conversationHistory.push({
            role: role,
            content: content,
            timestamp: new Date().toISOString()
        });
        
        // Keep only last 20 messages to avoid memory issues
        if (this.conversationHistory.length > 20) {
            this.conversationHistory = this.conversationHistory.slice(-20);
        }
    }

    exportConversation() {
        const exportData = {
            export_timestamp: new Date().toISOString(),
            application: 'secretGPT',
            version: '2.0.0',
            conversation: this.conversationHistory
        };
        
        const blob = new Blob([JSON.stringify(exportData, null, 2)], {
            type: 'application/json'
        });
        
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `secretgpt_conversation_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.json`;
        document.body.appendChild(a);
        a.click();
        URL.revokeObjectURL(url);
        document.body.removeChild(a);
    }

    clearHistory() {
        this.conversationHistory = [];
    }

    async sendStreamingMessage(message, options = {}) {
        // Send a streaming message using EventSource (Server-Sent Events)
        // Args:
        //   message: The message to send
        //   options: Optional parameters (temperature, system_prompt)
        if (this.isStreaming) {
            console.warn('Already streaming, ignoring new request');
            return;
        }

        this.isStreaming = true;
        const streamId = this.generateStreamId();
        this.currentStreamId = streamId;

        try {
            // Create the request body
            const requestBody = {
                message: message,
                temperature: options.temperature || 0.7,
                system_prompt: options.system_prompt || "You are a helpful assistant."
            };

            // Use fetch with streaming response
            const response = await fetch('/api/v1/chat/stream', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'text/event-stream',
                    'Cache-Control': 'no-cache'
                },
                body: JSON.stringify(requestBody)
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            // Create a streaming reader
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = '';
            let messageElement = null;

            // Process the streaming response
            while (true) {
                const { value, done } = await reader.read();
                
                if (done) break;

                // Decode the chunk
                const chunk = decoder.decode(value, { stream: true });
                buffer += chunk;

                // Process complete SSE events
                const lines = buffer.split('\n');
                buffer = lines.pop(); // Keep incomplete line in buffer

                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        try {
                            const eventData = JSON.parse(line.slice(6));
                            messageElement = this.handleStreamChunk(eventData, messageElement);
                        } catch (e) {
                            console.error('Error parsing stream chunk:', e);
                        }
                    }
                }
            }

        } catch (error) {
            console.error('Streaming error:', error);
            this.handleStreamError(error);
        } finally {
            this.isStreaming = false;
            this.currentStreamId = null;
            this.updateStreamControls(false);
        }
    }

    handleStreamChunk(eventData, messageElement) {
        // Handle individual streaming chunks from the server
        // Args:
        //   eventData: The parsed JSON data from the SSE event
        //   messageElement: The current message DOM element being updated
        // Returns:
        //   The message element (created if needed)
        const chunk = eventData.chunk;
        
        if (!chunk) return messageElement;

        switch (chunk.type) {
            case 'stream_start':
                messageElement = this.createStreamingMessage();
                this.updateStreamControls(true);
                break;

            case 'text_chunk':
                if (messageElement) {
                    this.appendToStreamingMessage(messageElement, chunk);
                }
                break;

            case 'think_start':
                if (messageElement) {
                    this.startThinkingSection(messageElement, chunk);
                }
                break;

            case 'think_end':
                if (messageElement) {
                    this.endThinkingSection(messageElement, chunk);
                }
                break;

            case 'stream_complete':
                this.completeStreamingMessage(messageElement, eventData);
                this.updateStreamControls(false);
                break;

            case 'mcp_response':
                // Handle MCP command responses (debug commands, tool results)
                console.log('mcp_response case triggered with chunk:', chunk);
                if (!messageElement) {
                    messageElement = this.createStreamingMessage();
                    console.log('Created new message element:', messageElement);
                }
                this.displayMcpResponse(messageElement, chunk);
                this.completeStreamingMessage(messageElement, eventData);
                this.updateStreamControls(false);
                break;

            case 'stream_error':
                console.error('Stream error:', chunk.data);
                this.handleStreamError(new Error(chunk.data));
                break;
        }

        return messageElement;
    }

    createStreamingMessage() {
        // Create a new streaming message element
        const chatContainer = document.getElementById('chat-messages');
        if (!chatContainer) return null;

        const messageDiv = document.createElement('div');
        messageDiv.className = 'message assistant-message streaming';
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content streaming-content';
        
        messageDiv.appendChild(contentDiv);
        chatContainer.appendChild(messageDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;

        return messageDiv;
    }

    appendToStreamingMessage(messageElement, chunk) {
        // Append text chunk to streaming message
        const contentDiv = messageElement.querySelector('.message-content');
        if (!contentDiv) return;

        const text = chunk.data;
        
        if (chunk.content_type === 'thinking') {
            // Append to thinking section with cyan color
            let thinkingDiv = contentDiv.querySelector('.thinking-section:last-child');
            if (thinkingDiv) {
                const span = document.createElement('span');
                span.textContent = text;
                span.className = 'thinking-text';
                thinkingDiv.appendChild(span);
            }
        } else {
            // Append normal text
            const span = document.createElement('span');
            span.textContent = text;
            contentDiv.appendChild(span);
        }

        // Scroll to bottom
        const chatContainer = document.getElementById('chat-messages');
        if (chatContainer) {
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
    }

    startThinkingSection(messageElement, chunk) {
        // Start a new thinking section with brain emoji
        const contentDiv = messageElement.querySelector('.message-content');
        if (!contentDiv) return;

        const thinkingDiv = document.createElement('div');
        thinkingDiv.className = 'thinking-section';
        
        const brainEmoji = document.createElement('span');
        brainEmoji.textContent = chunk.data; // Should be 🧠
        brainEmoji.className = 'brain-emoji';
        
        thinkingDiv.appendChild(brainEmoji);
        contentDiv.appendChild(thinkingDiv);
    }

    endThinkingSection(messageElement, chunk) {
        // End the current thinking section
        const contentDiv = messageElement.querySelector('.message-content');
        if (!contentDiv) return;

        const brainEmoji = document.createElement('span');
        brainEmoji.textContent = chunk.data; // Should be 🧠
        brainEmoji.className = 'brain-emoji';
        contentDiv.appendChild(brainEmoji);
    }

    displayMcpResponse(messageElement, chunk) {
        // Display MCP command response with special formatting
        console.log('displayMcpResponse called with:', chunk);
        const contentDiv = messageElement.querySelector('.message-content');
        if (!contentDiv) {
            console.error('No content div found in message element');
            return;
        }

        // Clear any existing content
        contentDiv.innerHTML = '';

        // Create MCP response container
        const mcpDiv = document.createElement('div');
        mcpDiv.className = 'mcp-response';
        
        // Add MCP badge
        const badge = document.createElement('div');
        badge.className = 'mcp-badge';
        badge.innerHTML = '<i class="fas fa-cogs"></i> MCP Response';
        mcpDiv.appendChild(badge);

        // Add the response content with formatting
        const responseDiv = document.createElement('div');
        responseDiv.className = 'mcp-content';
        responseDiv.innerHTML = this.formatMessage(chunk.data);
        mcpDiv.appendChild(responseDiv);

        contentDiv.appendChild(mcpDiv);

        // Scroll to bottom
        const chatContainer = document.getElementById('chat-messages');
        if (chatContainer) {
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
    }

    completeStreamingMessage(messageElement, eventData) {
        // Complete the streaming message and add metadata
        if (!messageElement) return;

        // Remove streaming class
        messageElement.classList.remove('streaming');

        // Add metadata if available
        if (eventData.model) {
            const metaDiv = document.createElement('div');
            metaDiv.className = 'message-meta';
            metaDiv.innerHTML = `<i class="fas fa-robot"></i> Model: ${eventData.model} | Interface: ${eventData.interface || 'web_ui'} | Streamed`;
            messageElement.appendChild(metaDiv);
        }

        // Store in conversation history
        const content = messageElement.querySelector('.message-content').textContent;
        this.addToHistory('assistant', content);

        // Store for proof generation
        if (window.attestAIApp) {
            window.attestAIApp.lastAnswer = content;
        }
    }

    handleStreamError(error) {
        // Handle streaming errors
        console.error('Stream error:', error);
        
        // Show error message in chat
        const chatContainer = document.getElementById('chat-messages');
        if (chatContainer) {
            const errorDiv = document.createElement('div');
            errorDiv.className = 'message error-message';
            errorDiv.innerHTML = `<div class="message-content">Streaming error: ${error.message}</div>`;
            chatContainer.appendChild(errorDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }

        // Update UI
        this.updateStreamControls(false);
    }

    updateStreamControls(isStreaming) {
        // Update streaming control buttons
        const streamControls = document.getElementById('stream-controls');
        if (streamControls) {
            if (isStreaming) {
                streamControls.classList.remove('d-none');
            } else {
                streamControls.classList.add('d-none');
            }
        }

        // Update send button
        const sendButton = document.getElementById('send-button');
        if (sendButton) {
            if (isStreaming) {
                sendButton.disabled = true;
                sendButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Streaming...';
            } else {
                sendButton.disabled = false;
                sendButton.innerHTML = '<i class="fas fa-paper-plane"></i> Send';
            }
        }
    }

    generateStreamId() {
        // Generate a unique stream ID
        return 'stream_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    stopCurrentStream() {
        // Stop the current streaming session
        if (this.currentStreamId && this.activeStreams.has(this.currentStreamId)) {
            const eventSource = this.activeStreams.get(this.currentStreamId);
            eventSource.close();
            this.activeStreams.delete(this.currentStreamId);
        }
        
        this.isStreaming = false;
        this.currentStreamId = null;
        this.updateStreamControls(false);
    }

    setStreamingEnabled(enabled) {
        // Enable or disable streaming mode
        this.streamingEnabled = enabled;
        
        // Update UI toggle if it exists
        const streamingToggle = document.getElementById('streaming-toggle');
        if (streamingToggle) {
            streamingToggle.checked = enabled;
        }
    }
}

// Additional chat functionality
document.addEventListener('DOMContentLoaded', () => {
    window.chatManager = new ChatManager();
    
    // Export conversation functionality
    const exportButton = document.getElementById('export-conversation');
    if (exportButton) {
        exportButton.addEventListener('click', () => {
            window.chatManager.exportConversation();
        });
    }
});