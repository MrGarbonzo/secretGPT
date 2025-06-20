// secretGPT Web UI - Chat-specific JavaScript

class ChatManager {
    constructor() {
        this.conversationHistory = [];
        this.isStreaming = false;
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