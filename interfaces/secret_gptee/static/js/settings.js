// SecretGPTee Settings Interface JavaScript
// Advanced settings panel functionality, user preferences, and configuration management

// Settings interface state
const SettingsState = {
    isOpen: false,
    activeTab: 'general',
    isDirty: false,
    backupSettings: null
};

// Default settings configuration
const DEFAULT_SETTINGS = {
    general: {
        theme: 'dark',
        language: 'en',
        enableNotifications: true,
        enableSounds: false,
        confirmBeforeExit: true
    },
    chat: {
        temperature: 0.7,
        maxTokens: 2048,
        enableStreaming: true,
        enableTools: true,
        autoSave: true,
        showTimestamps: true,
        messageFormat: 'markdown'
    },
    wallet: {
        autoConnect: false,
        showBalanceInUSD: false,
        defaultGasLimit: 200000,
        gasPrice: 0.25,
        networkTimeout: 30000,
        confirmTransactions: true
    },
    privacy: {
        privacyMode: false,
        localStorageOnly: true,
        clearOnExit: false,
        anonymizeRequests: false,
        encryptStorage: false
    },
    advanced: {
        debugMode: false,
        verboseLogging: false,
        experimentalFeatures: false,
        customAPIEndpoint: '',
        requestTimeout: 30000,
        retryAttempts: 3
    }
};

// Settings interface management
const SettingsInterface = {
    // Initialize settings interface
    init() {
        console.log('⚙️ Initializing settings interface...');
        
        this.setupEventListeners();
        this.loadSettings();
        this.updateUI();
        
        console.log('✅ Settings interface initialized');
    },
    
    // Setup event listeners
    setupEventListeners() {
        // Settings panel toggle
        const settingsBtn = document.getElementById('settings-btn');
        if (settingsBtn) {
            settingsBtn.addEventListener('click', this.togglePanel.bind(this));
        }
        
        // Close settings panel
        const closeSettingsBtn = document.getElementById('close-settings');
        if (closeSettingsBtn) {
            closeSettingsBtn.addEventListener('click', this.closePanel.bind(this));
        }
        
        // Tab navigation
        const settingsTabs = document.querySelectorAll('.settings-tab');
        settingsTabs.forEach(tab => {
            tab.addEventListener('click', (e) => {
                this.switchTab(e.target.dataset.tab);
            });
        });
        
        // Settings form elements
        this.setupFormListeners();
        
        // Action buttons
        const saveBtn = document.getElementById('save-settings');
        const resetBtn = document.getElementById('reset-settings');
        const exportBtn = document.getElementById('export-settings');
        const importBtn = document.getElementById('import-settings');
        
        if (saveBtn) saveBtn.addEventListener('click', this.saveSettings.bind(this));
        if (resetBtn) resetBtn.addEventListener('click', this.resetSettings.bind(this));
        if (exportBtn) exportBtn.addEventListener('click', this.exportSettings.bind(this));
        if (importBtn) importBtn.addEventListener('click', this.importSettings.bind(this));
        
        // Import file handler
        const importFile = document.getElementById('settings-import-file');
        if (importFile) {
            importFile.addEventListener('change', this.handleImportFile.bind(this));
        }
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (SettingsState.isOpen) {
                if (e.key === 'Escape') {
                    e.preventDefault();
                    this.closePanel();
                }
                
                // Ctrl/Cmd + S to save
                if ((e.ctrlKey || e.metaKey) && e.key === 's') {
                    e.preventDefault();
                    this.saveSettings();
                }
            }
        });
    },
    
    // Setup form input listeners
    setupFormListeners() {
        // Monitor all settings inputs for changes
        const settingsInputs = document.querySelectorAll('.settings-panel input, .settings-panel select, .settings-panel textarea');
        settingsInputs.forEach(input => {
            input.addEventListener('change', this.markDirty.bind(this));
            
            // Special handlers for specific inputs
            if (input.type === 'range') {
                input.addEventListener('input', (e) => {
                    this.updateRangeDisplay(e.target);
                    this.markDirty();
                });
            }
        });
        
        // Theme change handler
        const themeSelect = document.getElementById('theme-select');
        if (themeSelect) {
            themeSelect.addEventListener('change', (e) => {
                if (window.SecretGPTee && window.SecretGPTee.setTheme) {
                    window.SecretGPTee.setTheme(e.target.value);
                }
            });
        }
        
        // Language change handler
        const languageSelect = document.getElementById('language-select');
        if (languageSelect) {
            languageSelect.addEventListener('change', (e) => {
                this.applyLanguage(e.target.value);
            });
        }
        
        // Privacy mode toggle
        const privacyToggle = document.getElementById('privacy-mode');
        if (privacyToggle) {
            privacyToggle.addEventListener('change', (e) => {
                this.togglePrivacyMode(e.target.checked);
            });
        }
        
        // Debug mode toggle
        const debugToggle = document.getElementById('debug-mode');
        if (debugToggle) {
            debugToggle.addEventListener('change', (e) => {
                this.toggleDebugMode(e.target.checked);
            });
        }
    },
    
    // Toggle settings panel
    togglePanel() {
        if (SettingsState.isOpen) {
            this.closePanel();
        } else {
            this.openPanel();
        }
    },
    
    // Open settings panel
    openPanel() {
        const settingsPanel = document.getElementById('settings-panel');
        if (settingsPanel) {
            // Backup current settings
            SettingsState.backupSettings = this.getCurrentSettings();
            
            settingsPanel.classList.remove('hidden');
            SettingsState.isOpen = true;
            SettingsState.isDirty = false;
            
            // Focus first input
            const firstInput = settingsPanel.querySelector('input, select, textarea');
            if (firstInput) {
                setTimeout(() => firstInput.focus(), 100);
            }
            
            // Add backdrop
            this.addBackdrop();
            
            console.log('Settings panel opened');
        }
    },
    
    // Close settings panel
    closePanel() {
        if (SettingsState.isDirty) {
            if (!confirm('You have unsaved changes. Are you sure you want to close without saving?')) {
                return;
            }
            
            // Restore backup settings
            if (SettingsState.backupSettings) {
                this.applySettings(SettingsState.backupSettings);
            }
        }
        
        const settingsPanel = document.getElementById('settings-panel');
        if (settingsPanel) {
            settingsPanel.classList.add('hidden');
            SettingsState.isOpen = false;
            SettingsState.isDirty = false;
            SettingsState.backupSettings = null;
            
            this.removeBackdrop();
            
            console.log('Settings panel closed');
        }
    },
    
    // Add backdrop
    addBackdrop() {
        let backdrop = document.getElementById('settings-backdrop');
        if (!backdrop) {
            backdrop = document.createElement('div');
            backdrop.id = 'settings-backdrop';
            backdrop.className = 'settings-backdrop';
            backdrop.addEventListener('click', this.closePanel.bind(this));
            document.body.appendChild(backdrop);
        }
    },
    
    // Remove backdrop
    removeBackdrop() {
        const backdrop = document.getElementById('settings-backdrop');
        if (backdrop) {
            backdrop.remove();
        }
    },
    
    // Switch settings tab
    switchTab(tabName) {
        SettingsState.activeTab = tabName;
        
        // Update tab buttons
        const tabs = document.querySelectorAll('.settings-tab');
        tabs.forEach(tab => {
            if (tab.dataset.tab === tabName) {
                tab.classList.add('active');
            } else {
                tab.classList.remove('active');
            }
        });
        
        // Update content panels
        const panels = document.querySelectorAll('.settings-content');
        panels.forEach(panel => {
            if (panel.dataset.tab === tabName) {
                panel.classList.add('active');
            } else {
                panel.classList.remove('active');
            }
        });
        
        console.log(`Switched to ${tabName} settings tab`);
    },
    
    // Mark settings as dirty (changed)
    markDirty() {
        SettingsState.isDirty = true;
        this.updateSaveButton();
    },
    
    // Update save button state
    updateSaveButton() {
        const saveBtn = document.getElementById('save-settings');
        if (saveBtn) {
            if (SettingsState.isDirty) {
                saveBtn.disabled = false;
                saveBtn.textContent = 'Save Changes';
                saveBtn.classList.add('has-changes');
            } else {
                saveBtn.disabled = true;
                saveBtn.textContent = 'Saved';
                saveBtn.classList.remove('has-changes');
            }
        }
    },
    
    // Update range input display
    updateRangeDisplay(rangeInput) {
        const displayElement = document.getElementById(rangeInput.id + '-value');
        if (displayElement) {
            let value = parseFloat(rangeInput.value);
            
            // Format based on input type
            if (rangeInput.id === 'temperature-slider') {
                displayElement.textContent = value.toFixed(1);
            } else if (rangeInput.id === 'gas-price-slider') {
                displayElement.textContent = value.toFixed(2) + ' uscrt';
            } else {
                displayElement.textContent = value.toString();
            }
        }
    },
    
    // Load settings from storage
    loadSettings() {
        try {
            const savedSettings = localStorage.getItem('secretgptee-settings');
            if (savedSettings) {
                const settings = JSON.parse(savedSettings);
                this.applySettings(this.mergeSettings(DEFAULT_SETTINGS, settings));
            } else {
                this.applySettings(DEFAULT_SETTINGS);
            }
        } catch (error) {
            console.error('Failed to load settings:', error);
            this.applySettings(DEFAULT_SETTINGS);
        }
    },
    
    // Save settings to storage
    saveSettings() {
        try {
            const currentSettings = this.getCurrentSettings();
            localStorage.setItem('secretgptee-settings', JSON.stringify(currentSettings));
            
            // Apply settings to app state
            this.applySettingsToApp(currentSettings);
            
            SettingsState.isDirty = false;
            this.updateSaveButton();
            
            if (window.SecretGPTee && window.SecretGPTee.showToast) {
                window.SecretGPTee.showToast('Settings saved successfully', 'success');
            }
            
            console.log('Settings saved successfully');
            
        } catch (error) {
            console.error('Failed to save settings:', error);
            if (window.SecretGPTee && window.SecretGPTee.showToast) {
                window.SecretGPTee.showToast('Failed to save settings', 'error');
            }
        }
    },
    
    // Reset settings to defaults
    resetSettings() {
        if (confirm('Are you sure you want to reset all settings to their defaults? This cannot be undone.')) {
            this.applySettings(DEFAULT_SETTINGS);
            this.markDirty();
            
            if (window.SecretGPTee && window.SecretGPTee.showToast) {
                window.SecretGPTee.showToast('Settings reset to defaults', 'info');
            }
        }
    },
    
    // Export settings to file
    exportSettings() {
        try {
            const settings = this.getCurrentSettings();
            const exportData = {
                version: '1.0',
                timestamp: new Date().toISOString(),
                settings: settings
            };
            
            const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            
            const a = document.createElement('a');
            a.href = url;
            a.download = `secretgptee-settings-${Date.now()}.json`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            
            if (window.SecretGPTee && window.SecretGPTee.showToast) {
                window.SecretGPTee.showToast('Settings exported successfully', 'success');
            }
            
        } catch (error) {
            console.error('Failed to export settings:', error);
            if (window.SecretGPTee && window.SecretGPTee.showToast) {
                window.SecretGPTee.showToast('Failed to export settings', 'error');
            }
        }
    },
    
    // Import settings
    importSettings() {
        const fileInput = document.getElementById('settings-import-file');
        if (fileInput) {
            fileInput.click();
        }
    },
    
    // Handle import file selection
    handleImportFile(event) {
        const file = event.target.files[0];
        if (!file) return;
        
        const reader = new FileReader();
        reader.onload = (e) => {
            try {
                const importData = JSON.parse(e.target.result);
                
                if (importData.settings) {
                    this.applySettings(this.mergeSettings(DEFAULT_SETTINGS, importData.settings));
                    this.markDirty();
                    
                    if (window.SecretGPTee && window.SecretGPTee.showToast) {
                        window.SecretGPTee.showToast('Settings imported successfully', 'success');
                    }
                } else {
                    throw new Error('Invalid settings file format');
                }
                
            } catch (error) {
                console.error('Failed to import settings:', error);
                if (window.SecretGPTee && window.SecretGPTee.showToast) {
                    window.SecretGPTee.showToast('Failed to import settings: Invalid file format', 'error');
                }
            }
        };
        
        reader.readAsText(file);
        
        // Clear file input
        event.target.value = '';
    },
    
    // Get current settings from UI
    getCurrentSettings() {
        return {
            general: {
                theme: this.getInputValue('theme-select', 'dark'),
                language: this.getInputValue('language-select', 'en'),
                enableNotifications: this.getInputValue('enable-notifications', true),
                enableSounds: this.getInputValue('enable-sounds', false),
                confirmBeforeExit: this.getInputValue('confirm-exit', true)
            },
            chat: {
                temperature: parseFloat(this.getInputValue('temperature-slider', 0.7)),
                maxTokens: parseInt(this.getInputValue('max-tokens', 2048)),
                enableStreaming: this.getInputValue('enable-streaming', true),
                enableTools: this.getInputValue('enable-tools', true),
                autoSave: this.getInputValue('auto-save-chat', true),
                showTimestamps: this.getInputValue('show-timestamps', true),
                messageFormat: this.getInputValue('message-format', 'markdown')
            },
            wallet: {
                autoConnect: this.getInputValue('auto-connect-wallet', false),
                showBalanceInUSD: this.getInputValue('show-balance-usd', false),
                defaultGasLimit: parseInt(this.getInputValue('default-gas-limit', 200000)),
                gasPrice: parseFloat(this.getInputValue('gas-price-slider', 0.25)),
                networkTimeout: parseInt(this.getInputValue('network-timeout', 30000)),
                confirmTransactions: this.getInputValue('confirm-transactions', true)
            },
            privacy: {
                privacyMode: this.getInputValue('privacy-mode', false),
                localStorageOnly: this.getInputValue('local-storage-only', true),
                clearOnExit: this.getInputValue('clear-on-exit', false),
                anonymizeRequests: this.getInputValue('anonymize-requests', false),
                encryptStorage: this.getInputValue('encrypt-storage', false)
            },
            advanced: {
                debugMode: this.getInputValue('debug-mode', false),
                verboseLogging: this.getInputValue('verbose-logging', false),
                experimentalFeatures: this.getInputValue('experimental-features', false),
                customAPIEndpoint: this.getInputValue('custom-api-endpoint', ''),
                requestTimeout: parseInt(this.getInputValue('request-timeout', 30000)),
                retryAttempts: parseInt(this.getInputValue('retry-attempts', 3))
            }
        };
    },
    
    // Apply settings to UI
    applySettings(settings) {
        // General settings
        this.setInputValue('theme-select', settings.general.theme);
        this.setInputValue('language-select', settings.general.language);
        this.setInputValue('enable-notifications', settings.general.enableNotifications);
        this.setInputValue('enable-sounds', settings.general.enableSounds);
        this.setInputValue('confirm-exit', settings.general.confirmBeforeExit);
        
        // Chat settings
        this.setInputValue('temperature-slider', settings.chat.temperature);
        this.setInputValue('max-tokens', settings.chat.maxTokens);
        this.setInputValue('enable-streaming', settings.chat.enableStreaming);
        this.setInputValue('enable-tools', settings.chat.enableTools);
        this.setInputValue('auto-save-chat', settings.chat.autoSave);
        this.setInputValue('show-timestamps', settings.chat.showTimestamps);
        this.setInputValue('message-format', settings.chat.messageFormat);
        
        // Wallet settings
        this.setInputValue('auto-connect-wallet', settings.wallet.autoConnect);
        this.setInputValue('show-balance-usd', settings.wallet.showBalanceInUSD);
        this.setInputValue('default-gas-limit', settings.wallet.defaultGasLimit);
        this.setInputValue('gas-price-slider', settings.wallet.gasPrice);
        this.setInputValue('network-timeout', settings.wallet.networkTimeout);
        this.setInputValue('confirm-transactions', settings.wallet.confirmTransactions);
        
        // Privacy settings
        this.setInputValue('privacy-mode', settings.privacy.privacyMode);
        this.setInputValue('local-storage-only', settings.privacy.localStorageOnly);
        this.setInputValue('clear-on-exit', settings.privacy.clearOnExit);
        this.setInputValue('anonymize-requests', settings.privacy.anonymizeRequests);
        this.setInputValue('encrypt-storage', settings.privacy.encryptStorage);
        
        // Advanced settings
        this.setInputValue('debug-mode', settings.advanced.debugMode);
        this.setInputValue('verbose-logging', settings.advanced.verboseLogging);
        this.setInputValue('experimental-features', settings.advanced.experimentalFeatures);
        this.setInputValue('custom-api-endpoint', settings.advanced.customAPIEndpoint);
        this.setInputValue('request-timeout', settings.advanced.requestTimeout);
        this.setInputValue('retry-attempts', settings.advanced.retryAttempts);
        
        // Update range displays
        const rangeInputs = document.querySelectorAll('input[type="range"]');
        rangeInputs.forEach(input => this.updateRangeDisplay(input));
        
        // Apply to app
        this.applySettingsToApp(settings);
    },
    
    // Apply settings to app state
    applySettingsToApp(settings) {
        // Update global app state
        if (window.SecretGPTee && window.SecretGPTee.AppState) {
            window.SecretGPTee.AppState.temperature = settings.chat.temperature;
            window.SecretGPTee.AppState.streaming = settings.chat.enableStreaming;
            window.SecretGPTee.AppState.settings = settings;
        }
        
        // Update chat state
        if (window.ChatState) {
            window.ChatState.temperature = settings.chat.temperature;
            window.ChatState.enableTools = settings.chat.enableTools;
        }
        
        // Apply theme
        if (window.SecretGPTee && window.SecretGPTee.setTheme) {
            window.SecretGPTee.setTheme(settings.general.theme);
        }
    },
    
    // Helper function to get input value
    getInputValue(id, defaultValue) {
        const element = document.getElementById(id);
        if (!element) return defaultValue;
        
        switch (element.type) {
            case 'checkbox':
                return element.checked;
            case 'number':
            case 'range':
                return parseFloat(element.value) || defaultValue;
            default:
                return element.value || defaultValue;
        }
    },
    
    // Helper function to set input value
    setInputValue(id, value) {
        const element = document.getElementById(id);
        if (!element) return;
        
        switch (element.type) {
            case 'checkbox':
                element.checked = Boolean(value);
                break;
            case 'number':
            case 'range':
                element.value = value;
                break;
            default:
                element.value = value;
        }
    },
    
    // Merge settings objects
    mergeSettings(defaults, overrides) {
        const result = JSON.parse(JSON.stringify(defaults));
        
        for (const category in overrides) {
            if (result[category]) {
                Object.assign(result[category], overrides[category]);
            }
        }
        
        return result;
    },
    
    // Update UI components
    updateUI() {
        this.updateSaveButton();
        
        // Update active tab
        this.switchTab(SettingsState.activeTab);
    },
    
    // Toggle privacy mode
    togglePrivacyMode(enabled) {
        if (enabled) {
            // Enable privacy mode features
            console.log('Privacy mode enabled');
            if (window.SecretGPTee && window.SecretGPTee.showToast) {
                window.SecretGPTee.showToast('Privacy mode enabled', 'info');
            }
        } else {
            console.log('Privacy mode disabled');
        }
    },
    
    // Toggle debug mode
    toggleDebugMode(enabled) {
        if (enabled) {
            console.log('Debug mode enabled');
            if (window.SecretGPTee && window.SecretGPTee.showToast) {
                window.SecretGPTee.showToast('Debug mode enabled', 'info');
            }
        } else {
            console.log('Debug mode disabled');
        }
    },
    
    // Apply language settings
    applyLanguage(languageCode) {
        // Language implementation would go here
        console.log(`Language changed to: ${languageCode}`);
        if (window.SecretGPTee && window.SecretGPTee.showToast) {
            window.SecretGPTee.showToast(`Language changed to ${languageCode}`, 'info');
        }
    }
};

// Export for global access
window.SettingsInterface = SettingsInterface;
window.SettingsState = SettingsState;
window.DEFAULT_SETTINGS = DEFAULT_SETTINGS;