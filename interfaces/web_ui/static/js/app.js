// Attest AI Web UI - Main JavaScript

class AttestAIApp {
    constructor() {
        this.API_BASE = '/api/v1';
        this.isLoading = false;
        this.currentConversation = [];
        
        this.init();
    }

    async init() {
        await this.loadSystemStatus();
        await this.loadModels();
        this.setupEventListeners();
    }

    async loadSystemStatus() {
        try {
            const response = await fetch(`${this.API_BASE}/status`);
            const status = await response.json();
            
            this.updateStatusIndicators(status);
        } catch (error) {
            console.error('Failed to load system status:', error);
            this.showError('Failed to connect to system');
        }
    }

    async loadModels() {
        try {
            const response = await fetch(`${this.API_BASE}/models`);
            const data = await response.json();
            
            const currentModelDisplay = document.getElementById('current-model-display');
            
            if (data.models && data.models.length > 0) {
                const currentModel = data.models[0];
                
                if (currentModelDisplay) {
                    currentModelDisplay.textContent = currentModel;
                }
            }
        } catch (error) {
            console.error('Failed to load models:', error);
            const currentModelDisplay = document.getElementById('current-model-display');
            
            if (currentModelDisplay) {
                currentModelDisplay.textContent = 'Error loading model';
            }
        }
    }

    updateStatusIndicators(status) {
        // Update ChaTEE Attestation status (self VM)
        const chateeAttestationStatus = document.getElementById('chatee-attestation-status');
        if (chateeAttestationStatus) {
            const circle = chateeAttestationStatus.querySelector('.status-circle');
            const text = chateeAttestationStatus.querySelector('span:last-child');
            
            // Set initial checking state
            circle.className = 'status-circle status-checking';
            text.textContent = 'Checking...';
            
            // Check self attestation
            this.checkSelfAttestation(circle, text);
        }

        // Update Secret AI Attestation status
        const secretaiAttestationStatus = document.getElementById('secretai-attestation-status');
        if (secretaiAttestationStatus) {
            const circle = secretaiAttestationStatus.querySelector('.status-circle');
            const text = secretaiAttestationStatus.querySelector('span:last-child');
            
            if (status.components && status.components.secret_ai === 'operational') {
                circle.className = 'status-circle status-connected';
                text.textContent = 'Connected';
            } else {
                circle.className = 'status-circle status-error';
                text.textContent = 'Error';
            }
        }
    }

    async checkSelfAttestation(circle, text) {
        try {
            const response = await fetch(`${this.API_BASE}/attestation/self`);
            const data = await response.json();
            
            if (data.success) {
                circle.className = 'status-circle status-connected';
                text.textContent = 'Connected';
            } else {
                circle.className = 'status-circle status-error';
                text.textContent = 'Error';
            }
        } catch (error) {
            console.log('Self attestation check failed (expected outside SecretVM):', error);
            circle.className = 'status-circle status-unknown';
            text.textContent = 'Unknown';
        }
    }

    setupEventListeners() {
        // Send button
        const sendButton = document.getElementById('send-button');
        if (sendButton) {
            sendButton.addEventListener('click', () => this.sendMessage());
        }

        // Message input - Enter to send
        const messageInput = document.getElementById('message-input');
        if (messageInput) {
            messageInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendMessage();
                }
            });
        }

        // Clear chat button
        const clearButton = document.getElementById('clear-chat');
        if (clearButton) {
            clearButton.addEventListener('click', () => this.clearChat());
        }

        // Generate proof buttons (both sidebar and header)
        const generateProofButton = document.getElementById('generate-proof');
        const generateProofHeaderButton = document.getElementById('generate-proof-header');
        
        if (generateProofButton) {
            generateProofButton.addEventListener('click', () => this.showProofModal());
        }
        
        if (generateProofHeaderButton) {
            generateProofHeaderButton.addEventListener('click', () => this.showProofModal());
        }

        // Proof modal submit
        const proofSubmitButton = document.getElementById('generate-proof-submit');
        if (proofSubmitButton) {
            proofSubmitButton.addEventListener('click', () => this.generateProof());
        }

        // Streaming toggle
        const streamingToggle = document.getElementById('streaming-toggle');
        if (streamingToggle) {
            streamingToggle.addEventListener('change', (e) => {
                if (window.chatManager) {
                    window.chatManager.setStreamingEnabled(e.target.checked);
                }
            });
        }

        // Stream control buttons
        const stopStreamButton = document.getElementById('stop-stream');
        if (stopStreamButton) {
            stopStreamButton.addEventListener('click', () => {
                if (window.chatManager) {
                    window.chatManager.stopCurrentStream();
                }
            });
        }

        // PROOF VERIFICATION FORM - MOVED FROM ATTESTATION PAGE
        const proofVerifyForm = document.getElementById('proof-verify-form');
        if (proofVerifyForm) {
            proofVerifyForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.verifyProof();
            });
        }
    }

    async sendMessage() {
        if (this.isLoading) return;

        const messageInput = document.getElementById('message-input');
        const message = messageInput.value.trim();
        
        if (!message) return;

        // Add user message to chat
        this.addMessage('user', message);
        messageInput.value = '';

        // Store question for proof generation
        this.lastQuestion = message;
        
        // Add user message to conversation history
        if (window.chatManager) {
            window.chatManager.addToHistory('user', message);
        }

        // Check if streaming is enabled
        const streamingToggle = document.getElementById('streaming-toggle');
        const useStreaming = streamingToggle ? streamingToggle.checked : true;

        if (useStreaming && window.chatManager && window.chatManager.streamingEnabled) {
            // Use streaming mode
            try {
                await window.chatManager.sendStreamingMessage(message, {
                    temperature: 0.7,
                    system_prompt: "You are a helpful assistant."
                });
            } catch (error) {
                console.error('Streaming failed, falling back to regular chat:', error);
                this.sendRegularMessage(message);
            }
        } else {
            // Use regular non-streaming mode
            this.sendRegularMessage(message);
        }
    }

    async sendRegularMessage(message) {
        // Show loading
        this.setLoading(true);
        const loadingMessage = this.addMessage('assistant', 'Thinking...');

        try {
            const response = await fetch(`${this.API_BASE}/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    temperature: 0.7,  // Fixed temperature
                    system_prompt: "You are a helpful assistant."  // Fixed system prompt
                })
            });

            const data = await response.json();

            // Remove loading message
            loadingMessage.remove();

            if (data.success) {
                this.addMessage('assistant', data.response, {
                    model: data.model,
                    interface: data.interface
                });
                
                // Store last Q&A for proof generation
                this.lastAnswer = data.response;
        
        // Add to conversation history
        if (window.chatManager) {
            window.chatManager.addToHistory('assistant', data.response);
        }
            } else {
                this.addMessage('error', `Error: ${data.error || 'Unknown error'}`);
            }
        } catch (error) {
            loadingMessage.remove();
            console.error('Chat error:', error);
            this.addMessage('error', 'Failed to send message. Please try again.');
        } finally {
            this.setLoading(false);
        }
    }

    addMessage(type, content, meta = null) {
        const chatContainer = document.getElementById('chat-messages');
        if (!chatContainer) return null;

        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}-message`;

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.textContent = content;

        messageDiv.appendChild(contentDiv);

        if (meta) {
            const metaDiv = document.createElement('div');
            metaDiv.className = 'message-meta';
            metaDiv.innerHTML = `<i class="fas fa-robot"></i> Model: ${meta.model} | Interface: ${meta.interface}`;
            messageDiv.appendChild(metaDiv);
        }

        chatContainer.appendChild(messageDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;

        return messageDiv;
    }

    clearChat() {
        const chatContainer = document.getElementById('chat-messages');
        if (chatContainer) {
            chatContainer.innerHTML = '';
        }
        this.currentConversation = [];
        this.lastQuestion = null;
        this.lastAnswer = null;
        
        // Clear conversation history in chat manager
        if (window.chatManager) {
            window.chatManager.clearHistory();
        }
    }

    setLoading(loading) {
        this.isLoading = loading;
        const sendButton = document.getElementById('send-button');
        
        if (sendButton) {
            if (loading) {
                sendButton.disabled = true;
                sendButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Sending...';
            } else {
                sendButton.disabled = false;
                sendButton.innerHTML = '<i class="fas fa-paper-plane"></i> Send';
            }
        }
    }

    showProofModal() {
        if (!this.lastQuestion || !this.lastAnswer) {
            this.showError('No conversation to generate proof for. Please have a conversation first.');
            return;
        }

        // Check if password is provided in sidebar or header
        const sidebarPassword = document.getElementById('proof-password-sidebar')?.value;
        const headerPassword = document.getElementById('proof-password-header')?.value;
        
        if (sidebarPassword) {
            // Generate proof directly from sidebar
            this.generateProof(sidebarPassword);
        } else if (headerPassword) {
            // Generate proof directly from header
            this.generateProof(headerPassword);
        } else {
            // Show modal for password input
            document.getElementById('proof-question').value = this.lastQuestion;
            document.getElementById('proof-answer').value = this.lastAnswer;
            
            const modal = new bootstrap.Modal(document.getElementById('proofModal'));
            modal.show();
        }
    }

    async generateProof(password = null) {
        // Get password from parameter or modal
        if (!password) {
            password = document.getElementById('proof-password').value;
        }
        
        if (!password) {
            this.showError('Please enter a password for proof encryption.');
            return;
        }

        // Hide modal if it's open
        const modal = bootstrap.Modal.getInstance(document.getElementById('proofModal'));
        if (modal) {
            modal.hide();
        }

        const loadingModal = new bootstrap.Modal(document.getElementById('loadingModal'));
        loadingModal.show();

        try {
            const formData = new FormData();
            formData.append('question', this.lastQuestion);
            formData.append('answer', this.lastAnswer);
            formData.append('password', password);
            
            // Include full conversation history if available
            if (window.chatManager && window.chatManager.conversationHistory) {
                formData.append('conversation_history', JSON.stringify(window.chatManager.conversationHistory));
            }

            const response = await fetch(`${this.API_BASE}/proof/generate`, {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `attest-ai_proof_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.attestproof`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
                
                this.showSuccess('Proof file generated and downloaded successfully!');
            } else {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to generate proof');
            }
        } catch (error) {
            console.error('Proof generation error:', error);
            this.showError(`Failed to generate proof: ${error.message}`);
        } finally {
            loadingModal.hide();
            document.getElementById('proof-password').value = '';
        }
    }

    // PROOF VERIFICATION METHODS - MOVED FROM ATTESTATION.JS
    async verifyProof() {
        const fileInput = document.getElementById('proof-file');
        const passwordInput = document.getElementById('proof-verify-password');
        const resultsDiv = document.getElementById('proof-results');
        const contentDiv = document.getElementById('proof-content');
        
        if (!fileInput.files[0] || !passwordInput.value) {
            this.showError('Please select a proof file and enter the password.');
            return;
        }

        const formData = new FormData();
        formData.append('file', fileInput.files[0]);
        formData.append('password', passwordInput.value);

        try {
            const response = await fetch(`${this.API_BASE}/proof/verify`, {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (data.success && data.verified) {
                this.displayProofResults(data.proof_data, contentDiv);
                resultsDiv.style.display = 'block';
                this.showSuccess('Proof verified successfully!');
            } else {
                throw new Error(data.error || 'Proof verification failed');
            }
        } catch (error) {
            console.error('Proof verification error:', error);
            this.showError(`Proof verification failed: ${error.message}`);
        }

        // Clear form
        fileInput.value = '';
        passwordInput.value = '';
    }

    displayProofResults(proofData, container) {
        // Check if full conversation is included
        const hasFullConversation = proofData.conversation && proofData.conversation.full_history && proofData.conversation.full_history.length > 0;
        
        let conversationHtml = '';
        if (hasFullConversation) {
            conversationHtml = `
                <div class="col-12 mt-3">
                    <h6>Full Conversation History (${proofData.conversation.total_messages} messages)</h6>
                    <div class="conversation-history" style="max-height: 400px; overflow-y: auto; border: 1px solid #ddd; padding: 10px; background-color: #f8f9fa;">
                        ${proofData.conversation.full_history.map(msg => `
                            <div class="conversation-message mb-2">
                                <strong class="${msg.role === 'user' ? 'text-primary' : 'text-success'}">${msg.role === 'user' ? 'User' : 'Assistant'}:</strong>
                                <div class="message-content">${this.escapeHtml(msg.content)}</div>
                                <small class="text-muted">${new Date(msg.timestamp).toLocaleString()}</small>
                            </div>
                        `).join('')}
                    </div>
                    <div class="mt-2">
                        <small class="text-muted">
                            <strong>Conversation Hash:</strong> <code>${proofData.conversation.conversation_hash}</code>
                        </small>
                    </div>
                </div>
            `;
        }
        
        const html = `
            <div class="card">
                <div class="card-header">
                    <h6><i class="fas fa-check-circle text-success"></i> Verified Proof</h6>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-6">
                            <h6>Latest Interaction</h6>
                            <div class="mb-2">
                                <strong>Question:</strong>
                                <div class="border p-2 bg-light">${this.escapeHtml(proofData.interaction.question)}</div>
                            </div>
                            <div class="mb-2">
                                <strong>Answer:</strong>
                                <div class="border p-2 bg-light">${this.escapeHtml(proofData.interaction.answer)}</div>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <h6>Attestation Verification</h6>
                            <div class="mb-2">
                                <strong>Dual VM:</strong>
                                <span class="badge bg-success">${proofData.attestation.dual_attestation ? 'Verified' : 'Failed'}</span>
                            </div>
                            <div class="mb-2">
                                <strong>Timestamp:</strong>
                                <code>${new Date(proofData.timestamp).toLocaleString()}</code>
                            </div>
                            <div class="mb-2">
                                <strong>Generator:</strong>
                                <code>${proofData.metadata.generator}</code>
                            </div>
                            <div class="mb-2">
                                <strong>Version:</strong>
                                <code>${proofData.version}</code>
                            </div>
                            <div class="mb-2">
                                <strong>Full Conversation:</strong>
                                <span class="badge ${hasFullConversation ? 'bg-success' : 'bg-warning'}">
                                    ${hasFullConversation ? 'Included' : 'Not Included'}
                                </span>
                            </div>
                        </div>
                        ${conversationHtml}
                    </div>
                </div>
            </div>
        `;
        
        container.innerHTML = html;
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    showError(message) {
        this.showAlert(message, 'danger');
    }

    showSuccess(message) {
        this.showAlert(message, 'success');
    }

    showAlert(message, type) {
        // Create alert element
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; max-width: 400px;';
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        document.body.appendChild(alertDiv);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.attestAIApp = new AttestAIApp();
});