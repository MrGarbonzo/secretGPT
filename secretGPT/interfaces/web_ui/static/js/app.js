// secretGPT Web UI - Main JavaScript

class SecretGPTApp {
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
            
            const modelDisplay = document.getElementById('model-display');
            const headerModelDisplay = document.getElementById('header-model-display');
            
            if (data.models && data.models.length > 0) {
                const currentModel = data.models[0];
                
                // Update both displays
                if (modelDisplay) {
                    modelDisplay.value = currentModel;
                }
                if (headerModelDisplay) {
                    headerModelDisplay.textContent = currentModel;
                }
            }
        } catch (error) {
            console.error('Failed to load models:', error);
            const modelDisplay = document.getElementById('model-display');
            const headerModelDisplay = document.getElementById('header-model-display');
            
            if (modelDisplay) {
                modelDisplay.value = 'Error loading model';
            }
            if (headerModelDisplay) {
                headerModelDisplay.textContent = 'Error loading model';
            }
        }
    }

    updateStatusIndicators(status) {
        // Update Secret AI status
        const secretAIStatus = document.getElementById('secretai-status');
        if (secretAIStatus) {
            const icon = secretAIStatus.querySelector('i');
            if (status.components && status.components.secret_ai === 'operational') {
                icon.className = 'fas fa-circle text-success';
            } else {
                icon.className = 'fas fa-circle text-danger';
            }
        }

        // Update Hub status
        const hubStatus = document.getElementById('hub-status');
        if (hubStatus) {
            const icon = hubStatus.querySelector('i');
            if (status.hub === 'operational') {
                icon.className = 'fas fa-circle text-success';
            } else {
                icon.className = 'fas fa-circle text-danger';
            }
        }

        // Update Attestation status
        const attestationStatus = document.getElementById('attestation-status');
        if (attestationStatus) {
            const icon = attestationStatus.querySelector('i');
            if (status.attestation && status.attestation.status === 'operational') {
                icon.className = 'fas fa-circle text-success';
            } else {
                icon.className = 'fas fa-circle text-warning';
            }
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

        // Generate proof button
        const generateProofButton = document.getElementById('generate-proof');
        if (generateProofButton) {
            generateProofButton.addEventListener('click', () => this.showProofModal());
        }

        // Proof modal submit
        const proofSubmitButton = document.getElementById('generate-proof-submit');
        if (proofSubmitButton) {
            proofSubmitButton.addEventListener('click', () => this.generateProof());
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
                this.lastQuestion = message;
                this.lastAnswer = data.response;
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

        document.getElementById('proof-question').value = this.lastQuestion;
        document.getElementById('proof-answer').value = this.lastAnswer;
        
        const modal = new bootstrap.Modal(document.getElementById('proofModal'));
        modal.show();
    }

    async generateProof() {
        const password = document.getElementById('proof-password').value;
        
        if (!password) {
            this.showError('Please enter a password for proof encryption.');
            return;
        }

        const modal = bootstrap.Modal.getInstance(document.getElementById('proofModal'));
        modal.hide();

        const loadingModal = new bootstrap.Modal(document.getElementById('loadingModal'));
        loadingModal.show();

        try {
            const formData = new FormData();
            formData.append('question', this.lastQuestion);
            formData.append('answer', this.lastAnswer);
            formData.append('password', password);

            const response = await fetch(`${this.API_BASE}/proof/generate`, {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `secretgpt_proof_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.attestproof`;
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
    window.secretGPTApp = new SecretGPTApp();
});