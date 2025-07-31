// SecretGPTee Main Application JavaScript

// Global app state
const AppState = {
    theme: 'dark',
    walletConnected: false,
    walletAddress: null,
    streaming: true,
    temperature: 0.7,
    settings: {},
    isLoading: false
};

// Initialize the application
function initializeApp() {
    console.log('🚀 Initializing SecretGPTee...');
    
    // Load theme from localStorage
    const savedTheme = localStorage.getItem('secretgptee-theme') || 'dark';
    setTheme(savedTheme);
    
    // Load settings
    loadUserSettings();
    
    // Initialize UI components
    initializeThemeToggle();
    initializeToastSystem();
    initializeEventListeners();
    
    // Initialize chat interface if available
    if (window.ChatInterface) {
        window.ChatInterface.init();
    }
    
    // Initialize wallet interface if available  
    if (window.WalletInterface) {
        window.WalletInterface.init();
    }
    
    // Initialize settings interface if available
    if (window.SettingsInterface) {
        window.SettingsInterface.init();
    }
    
    // Setup keyboard shortcuts
    setupKeyboardShortcuts();
    
    // Setup responsive handlers
    setupResponsiveHandlers();
    
    console.log('✅ SecretGPTee initialized successfully');
}

// Theme Management
function setTheme(theme) {
    AppState.theme = theme;
    document.documentElement.setAttribute('data-theme', theme);
    
    const themeIcon = document.getElementById('theme-icon');
    if (themeIcon) {
        themeIcon.className = theme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
    }
    
    localStorage.setItem('secretgptee-theme', theme);
}

function toggleTheme() {
    const newTheme = AppState.theme === 'dark' ? 'light' : 'dark';
    setTheme(newTheme);
    
    showToast('Theme changed to ' + newTheme + ' mode', 'info');
}

function initializeThemeToggle() {
    const themeBtn = document.querySelector('.theme-btn');
    if (themeBtn) {
        themeBtn.addEventListener('click', toggleTheme);
    }
}

// Settings Management
function loadUserSettings() {
    try {
        const savedSettings = localStorage.getItem('secretgptee-settings');
        if (savedSettings) {
            AppState.settings = JSON.parse(savedSettings);
            applySettings(AppState.settings);
        } else {
            // Default settings
            AppState.settings = {
                temperature: 0.7,
                enableTools: true,
                enableStreaming: true,
                autoConnectWallet: false,
                localStorageOnly: true,
                privacyMode: false,
                defaultGas: 200000
            };
            saveUserSettings();
        }
    } catch (error) {
        console.error('Failed to load user settings:', error);
        // Use default settings
        AppState.settings = {
            temperature: 0.7,
            enableTools: true,
            enableStreaming: true,
            autoConnectWallet: false,
            localStorageOnly: true,
            privacyMode: false,
            defaultGas: 200000
        };
    }
}

function saveUserSettings() {
    try {
        localStorage.setItem('secretgptee-settings', JSON.stringify(AppState.settings));
        console.log('Settings saved successfully');
    } catch (error) {
        console.error('Failed to save settings:', error);
        showToast('Failed to save settings', 'error');
    }
}

function applySettings(settings) {
    // Apply temperature
    AppState.temperature = settings.temperature || 0.7;
    updateTemperatureDisplay(AppState.temperature);
    
    // Apply streaming
    AppState.streaming = settings.enableStreaming !== false;
    updateStreamingDisplay(AppState.streaming);
    
    // Apply other settings
    const temperatureSlider = document.getElementById('temperature-slider');
    if (temperatureSlider) {
        temperatureSlider.value = AppState.temperature;
    }
    
    const enableToolsCheckbox = document.getElementById('enable-tools');
    if (enableToolsCheckbox) {
        enableToolsCheckbox.checked = settings.enableTools !== false;
    }
    
    const enableStreamingCheckbox = document.getElementById('enable-streaming');
    if (enableStreamingCheckbox) {
        enableStreamingCheckbox.checked = settings.enableStreaming !== false;
    }
    
    const autoConnectCheckbox = document.getElementById('auto-connect-wallet');
    if (autoConnectCheckbox) {
        autoConnectCheckbox.checked = settings.autoConnectWallet === true;
    }
    
    const localStorageCheckbox = document.getElementById('local-storage-only');
    if (localStorageCheckbox) {
        localStorageCheckbox.checked = settings.localStorageOnly !== false;
    }
    
    const privacyModeCheckbox = document.getElementById('privacy-mode');
    if (privacyModeCheckbox) {
        privacyModeCheckbox.checked = settings.privacyMode === true;
    }
    
    const defaultGasInput = document.getElementById('default-gas');
    if (defaultGasInput) {
        defaultGasInput.value = settings.defaultGas || 200000;
    }
}

function updateTemperatureDisplay(temperature) {
    const tempValue = document.getElementById('temp-value');
    if (tempValue) {
        tempValue.textContent = temperature.toFixed(1);
    }
}

function updateStreamingDisplay(streaming) {
    const streamingIcon = document.getElementById('streaming-icon');
    const streamingText = document.getElementById('streaming-text');
    
    if (streamingIcon && streamingText) {
        streamingIcon.className = streaming ? 'fas fa-stream' : 'fas fa-pause';
        streamingText.textContent = streaming ? 'Streaming' : 'Non-streaming';
    }
}

// Settings Panel
function toggleSettings() {
    const settingsPanel = document.getElementById('settings-panel');
    if (settingsPanel) {
        settingsPanel.classList.toggle('hidden');
        
        if (!settingsPanel.classList.contains('hidden')) {
            // Refresh settings display
            applySettings(AppState.settings);
        }
    }
}

function resetSettings() {
    if (confirm('Are you sure you want to reset all settings to defaults?')) {
        AppState.settings = {
            temperature: 0.7,
            enableTools: true,
            enableStreaming: true,
            autoConnectWallet: false,
            localStorageOnly: true,
            privacyMode: false,
            defaultGas: 200000
        };
        
        applySettings(AppState.settings);
        saveUserSettings();
        showToast('Settings reset to defaults', 'success');
    }
}

function saveSettings() {
    try {
        // Collect settings from UI
        const temperatureSlider = document.getElementById('temperature-slider');
        const enableToolsCheckbox = document.getElementById('enable-tools');
        const enableStreamingCheckbox = document.getElementById('enable-streaming');
        const autoConnectCheckbox = document.getElementById('auto-connect-wallet');
        const localStorageCheckbox = document.getElementById('local-storage-only');
        const privacyModeCheckbox = document.getElementById('privacy-mode');
        const defaultGasInput = document.getElementById('default-gas');
        
        AppState.settings = {
            temperature: parseFloat(temperatureSlider?.value || 0.7),
            enableTools: enableToolsCheckbox?.checked !== false,
            enableStreaming: enableStreamingCheckbox?.checked !== false,
            autoConnectWallet: autoConnectCheckbox?.checked === true,
            localStorageOnly: localStorageCheckbox?.checked !== false,
            privacyMode: privacyModeCheckbox?.checked === true,
            defaultGas: parseInt(defaultGasInput?.value || 200000)
        };
        
        // Apply new settings
        applySettings(AppState.settings);
        saveUserSettings();
        
        // Close settings panel
        toggleSettings();
        
        showToast('Settings saved successfully', 'success');
        
    } catch (error) {
        console.error('Failed to save settings:', error);
        showToast('Failed to save settings', 'error');
    }
}

// Streaming toggle
function toggleStreaming() {
    AppState.streaming = !AppState.streaming;
    AppState.settings.enableStreaming = AppState.streaming;
    updateStreamingDisplay(AppState.streaming);
    saveUserSettings();
    
    showToast(`Streaming ${AppState.streaming ? 'enabled' : 'disabled'}`, 'info');
}

// Character counter for textarea
function updateCharCount() {
    const textarea = document.getElementById('message-input');
    const charCount = document.querySelector('.char-count');
    
    if (textarea && charCount) {
        const currentLength = textarea.value.length;
        const maxLength = textarea.getAttribute('maxlength') || 4000;
        charCount.textContent = `${currentLength} / ${maxLength}`;
        
        // Visual feedback for approaching limit
        if (currentLength > maxLength * 0.9) {
            charCount.style.color = 'var(--warning-color)';
        } else if (currentLength > maxLength * 0.8) {
            charCount.style.color = 'var(--accent-color)';
        } else {
            charCount.style.color = 'var(--text-muted)';
        }
    }
}

// Auto-resize textarea
function autoResize() {
    const textarea = document.getElementById('message-input');
    if (textarea) {
        textarea.style.height = 'auto';
        textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
    }
}

// Loading states
function showLoading(message = 'Loading...') {
    AppState.isLoading = true;
    const overlay = document.getElementById('loading-overlay');
    const spinner = overlay?.querySelector('.loading-spinner span');
    
    if (overlay) {
        overlay.classList.remove('hidden');
    }
    
    if (spinner) {
        spinner.textContent = message;
    }
}

function hideLoading() {
    AppState.isLoading = false;
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
        overlay.classList.add('hidden');
    }
}

// Toast notification system
function initializeToastSystem() {
    // Create toast container if it doesn't exist
    if (!document.getElementById('toast-container')) {
        const toastContainer = document.createElement('div');
        toastContainer.id = 'toast-container';
        toastContainer.className = 'toast-container';
        document.body.appendChild(toastContainer);
    }
}

function showToast(message, type = 'info', duration = 5000) {
    const toastContainer = document.getElementById('toast-container');
    if (!toastContainer) return;
    
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const icons = {
        success: 'fas fa-check-circle',
        error: 'fas fa-exclamation-circle',
        warning: 'fas fa-exclamation-triangle',
        info: 'fas fa-info-circle'
    };
    
    toast.innerHTML = `
        <div class="toast-content">
            <i class="toast-icon ${icons[type] || icons.info}"></i>
            <div class="toast-message">
                <div class="toast-description">${message}</div>
            </div>
            <button class="toast-close" onclick="removeToast(this.parentElement.parentElement)">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    // Auto-remove after duration
    if (duration > 0) {
        setTimeout(() => {
            removeToast(toast);
        }, duration);
    }
}

function removeToast(toast) {
    if (toast && toast.parentNode) {
        toast.style.animation = 'slideOutRight 0.3s ease-out';
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 300);
    }
}

// Utility functions
function formatTimestamp(date = new Date()) {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function copyToClipboard(text) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(() => {
            showToast('Copied to clipboard', 'success');
        }).catch(err => {
            console.error('Failed to copy:', err);
            showToast('Failed to copy to clipboard', 'error');
        });
    } else {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        try {
            document.execCommand('copy');
            showToast('Copied to clipboard', 'success');
        } catch (err) {
            console.error('Failed to copy:', err);
            showToast('Failed to copy to clipboard', 'error');
        }
        document.body.removeChild(textArea);
    }
}

// Error handling
window.addEventListener('error', function(event) {
    console.error('JavaScript error:', event.error);
    showToast('An unexpected error occurred', 'error');
});

window.addEventListener('unhandledrejection', function(event) {
    console.error('Unhandled promise rejection:', event.reason);
    showToast('An unexpected error occurred', 'error');
});

// Additional initialization functions
function initializeEventListeners() {
    // Global event listeners
    document.addEventListener('DOMContentLoaded', () => {
        // Auto-resize textarea
        const messageInput = document.getElementById('message-input');
        if (messageInput) {
            messageInput.addEventListener('input', (e) => {
                autoResize();
                updateCharCount();
            });
        }
        
        // Settings panel toggle
        const settingsBtn = document.getElementById('settings-btn');
        if (settingsBtn) {
            settingsBtn.addEventListener('click', toggleSettings);
        }
        
        // Streaming toggle
        const streamingToggle = document.getElementById('streaming-toggle');
        if (streamingToggle) {
            streamingToggle.addEventListener('click', toggleStreaming);
        }
        
        // Settings form handlers
        const saveSettingsBtn = document.getElementById('save-settings-btn');
        if (saveSettingsBtn) {
            saveSettingsBtn.addEventListener('click', saveSettings);
        }
        
        const resetSettingsBtn = document.getElementById('reset-settings-btn');
        if (resetSettingsBtn) {
            resetSettingsBtn.addEventListener('click', resetSettings);
        }
        
        // Temperature slider
        const temperatureSlider = document.getElementById('temperature-slider');
        if (temperatureSlider) {
            temperatureSlider.addEventListener('input', (e) => {
                updateTemperatureDisplay(parseFloat(e.target.value));
            });
        }
    });
}

function setupKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
        // Ctrl/Cmd + Enter to send message
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            e.preventDefault();
            if (window.ChatInterface && typeof window.ChatInterface.sendMessage === 'function') {
                window.ChatInterface.sendMessage();
            }
        }
        
        // Ctrl/Cmd + K to focus message input
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            const messageInput = document.getElementById('message-input');
            if (messageInput) {
                messageInput.focus();
            }
        }
        
        // Ctrl/Cmd + Shift + T to toggle theme
        if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'T') {
            e.preventDefault();
            toggleTheme();
        }
        
        // Ctrl/Cmd + Shift + S to toggle settings
        if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'S') {
            e.preventDefault();
            toggleSettings();
        }
        
        // Escape to close modals and panels
        if (e.key === 'Escape') {
            // Close settings panel
            const settingsPanel = document.getElementById('settings-panel');
            if (settingsPanel && !settingsPanel.classList.contains('hidden')) {
                toggleSettings();
            }
            
            // Close any open modals
            const modals = document.querySelectorAll('.install-modal-overlay, .transaction-modal-overlay');
            modals.forEach(modal => modal.remove());
        }
    });
}

function setupResponsiveHandlers() {
    // Handle window resize
    window.addEventListener('resize', () => {
        // Adjust chat container height if needed
        const messagesContainer = document.getElementById('messages-container');
        if (messagesContainer) {
            // Recalculate container height on resize
            messagesContainer.style.height = 'calc(100vh - 200px)';
        }
    });
    
    // Handle visibility change (tab focus/blur)
    document.addEventListener('visibilitychange', () => {
        if (!document.hidden) {
            // Page became visible, refresh wallet connection if needed
            if (window.WalletInterface && window.WalletState && window.WalletState.connected) {
                window.WalletInterface.refreshConnection();
            }
        }
    });
    
    // Handle online/offline status
    window.addEventListener('online', () => {
        showToast('Connection restored', 'success');
    });
    
    window.addEventListener('offline', () => {
        showToast('Connection lost - working offline', 'warning');
    });
}

// Animation helpers
function fadeIn(element, duration = 300) {
    element.style.opacity = '0';
    element.style.display = 'block';
    
    let start = null;
    function animate(timestamp) {
        if (!start) start = timestamp;
        const progress = timestamp - start;
        const opacity = Math.min(progress / duration, 1);
        
        element.style.opacity = opacity;
        
        if (progress < duration) {
            requestAnimationFrame(animate);
        }
    }
    
    requestAnimationFrame(animate);
}

function fadeOut(element, duration = 300) {
    let start = null;
    const initialOpacity = parseFloat(element.style.opacity) || 1;
    
    function animate(timestamp) {
        if (!start) start = timestamp;
        const progress = timestamp - start;
        const opacity = Math.max(initialOpacity - (progress / duration), 0);
        
        element.style.opacity = opacity;
        
        if (progress < duration) {
            requestAnimationFrame(animate);
        } else {
            element.style.display = 'none';
        }
    }
    
    requestAnimationFrame(animate);
}

function slideDown(element, duration = 300) {
    element.style.height = '0';
    element.style.display = 'block';
    const targetHeight = element.scrollHeight + 'px';
    
    let start = null;
    function animate(timestamp) {
        if (!start) start = timestamp;
        const progress = timestamp - start;
        const heightProgress = Math.min(progress / duration, 1);
        
        element.style.height = (parseInt(targetHeight) * heightProgress) + 'px';
        
        if (progress < duration) {
            requestAnimationFrame(animate);
        } else {
            element.style.height = 'auto';
        }
    }
    
    requestAnimationFrame(animate);
}

// Enhanced error handling
function handleError(error, context = 'Unknown') {
    console.error(`Error in ${context}:`, error);
    
    let userMessage = 'An unexpected error occurred';
    
    if (error.message) {
        if (error.message.includes('network') || error.message.includes('fetch')) {
            userMessage = 'Network error - please check your connection';
        } else if (error.message.includes('wallet')) {
            userMessage = 'Wallet error - please check your wallet connection';
        } else if (error.message.includes('unauthorized') || error.message.includes('401')) {
            userMessage = 'Authentication error - please refresh the page';
        }
    }
    
    showToast(userMessage, 'error');
}

// Performance monitoring
function measurePerformance(name, fn) {
    return async function(...args) {
        const start = performance.now();
        try {
            const result = await fn.apply(this, args);
            const end = performance.now();
            console.log(`⏱️ ${name} took ${(end - start).toFixed(2)}ms`);
            return result;
        } catch (error) {
            const end = performance.now();
            console.error(`❌ ${name} failed after ${(end - start).toFixed(2)}ms:`, error);
            throw error;
        }
    };
}

// DOM ready handler
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeApp);
} else {
    // DOM is already ready
    initializeApp();
}

// Export for use in other scripts
window.SecretGPTee = {
    AppState,
    showToast,
    showLoading,
    hideLoading,
    setTheme,
    toggleTheme,
    loadUserSettings,
    saveUserSettings,
    copyToClipboard,
    formatTimestamp,
    escapeHtml,
    handleError,
    measurePerformance,
    fadeIn,
    fadeOut,
    slideDown
};