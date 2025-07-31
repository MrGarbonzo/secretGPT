# SecretGPTee UI - Secret Network Branded Interface Plan

## Overview
SecretGPTee is the consumer-focused web interface for secretGPT, featuring Secret Network branding, Keplr wallet integration, and comprehensive attestation monitoring. This UI runs alongside the existing attestAI interface on the same VM and backend infrastructure.

## Secret Network Branding & Design System

### **Primary Colors**
```css
:root {
    /* Secret Network Official Brand Colors */
    --secret-blue: #1B1F3A;           /* Dark navy blue - primary */
    --secret-purple: #6C5CE7;         /* Vibrant purple - secondary */
    --secret-cyan: #00D4FF;           /* Bright cyan - accent */
    --secret-pink: #FF6B9D;           /* Accent pink - highlights */
    
    /* UI Background Colors */
    --bg-primary: #0F1419;            /* Almost black background */
    --bg-secondary: #1E2328;          /* Dark gray cards */
    --bg-card: #252A2F;               /* Elevated surfaces */
    --bg-glass: rgba(255, 255, 255, 0.05); /* Glassmorphism */
    
    /* Text Colors */
    --text-primary: #FFFFFF;          /* Primary text */
    --text-secondary: #8B949E;        /* Secondary text */
    --text-muted: #6E7681;            /* Muted text */
    
    /* Status Colors */
    --status-ok: #00D4FF;             /* Connected/Success */
    --status-warning: #FFB800;        /* Checking/Warning */
    --status-error: #FF4757;          /* Error/Disconnected */
    
    /* Gradients */
    --gradient-primary: linear-gradient(135deg, var(--secret-blue) 0%, var(--secret-purple) 100%);
    --gradient-accent: linear-gradient(135deg, var(--secret-cyan) 0%, var(--secret-pink) 100%);
    --gradient-card: linear-gradient(145deg, #1E2328 0%, #252A2F 100%);
}
```

### **Typography & Spacing**
- **Font Family**: Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui
- **Font Weights**: 400 (regular), 500 (medium), 600 (semibold), 700 (bold)
- **Border Radius**: 8px (standard), 12px (cards), 50% (circles)
- **Shadows**: Subtle with Secret Network color tints
- **Spacing Scale**: 0.25rem, 0.5rem, 0.75rem, 1rem, 1.5rem, 2rem, 3rem

## Architecture & File Structure

### **Directory Structure**
```
interfaces/secretgptee_ui/
├── app.py                          # FastAPI application
├── service.py                      # Hub service integration
├── static/
│   ├── css/
│   │   └── secretgptee.css        # Secret Network branded styles
│   ├── js/
│   │   ├── app.js                 # Main application logic  
│   │   ├── wallet.js              # Keplr wallet integration
│   │   ├── chat.js                # Chat interface management
│   │   ├── attestation.js         # Attestation status monitoring
│   │   └── settings.js            # Settings panel management
│   └── assets/
│       ├── secret-logo.svg        # Secret Network branding
│       └── icons/                 # Custom icon set
├── templates/
│   ├── base.html                  # Base template with Secret branding
│   ├── index.html                 # Main chat interface
│   ├── components/
│   │   ├── attestation_panel.html # Detailed attestation view
│   │   ├── wallet_panel.html      # Wallet connection UI
│   │   └── settings_panel.html    # Settings interface
│   └── partials/
│       ├── status_bar.html        # Compact attestation status
│       └── chat_message.html      # Message templates
└── __init__.py
```

### **Backend Integration Points**
- **Hub Router**: Reuse existing secretGPT hub for AI responses
- **Secret AI Service**: Direct integration for LLM processing
- **MCP Service**: Blockchain tools and Secret Network integration
- **Wallet Proxy**: Bridge to secret_network_mcp on VM2
- **Attestation Service**: Four-component status monitoring

## UI Layout & Components

### **1. Main Interface Layout**
```
┌─────────────────────────────────────────────────────────────┐
│ 🔮 SecretGPTee                  [💰 Wallet] [⚙️] [☰]      │
├─────────────────────────────────────────────────────────────┤
│ 🟢 SecretGPT  🟢 SecretAI  🟢 SecretMCP  🟢 MCP Bridge     │ ← Status Bar
├─────────────────────────────────────────────────────────────┤
│                                                             │
│                   Chat Messages Area                        │
│                     (Scrollable)                           │
│                                                             │
│  [User Message Bubble]                                     │
│                                   [AI Response Bubble]     │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│ Type your message... [🎤] [📎] [Send] [⚡ Temp: 0.7]       │
└─────────────────────────────────────────────────────────────┘
```

### **2. Collapsible Sidebar**
```
┌─────────────────┐
│ 💰 Wallet       │
│ ├ 🟢 Connected   │
│ ├ 1,250 SCRT    │
│ └ secret1abc... │
│                 │
│ 🛡️ Security      │
│ ├ All Systems ✓ │
│ ├ Last Check: 1m│
│ └ View Details  │
│                 │
│ 📝 Conversations│
│ ├ Today (3)     │
│ ├ Yesterday (5) │
│ └ This Week (12)│
│                 │
│ ⚙️ Settings      │
│ ├ Temperature   │
│ ├ Model Select  │
│ └ Privacy       │
└─────────────────┘
```

## Four-Component Attestation System

### **Components to Monitor**
1. **SecretGPT Hub** - Main router and orchestration service
2. **SecretAI Service** - LLM processing and AI responses  
3. **SecretMCP Service** - Blockchain tools and Secret Network integration
4. **MCP Bridge** - Secure communication bridge to VM2

### **Status Display Levels**

#### **Compact Status Bar (Always Visible)**
```html
<div class="attestation-status-bar">
    <div class="service-status" id="secretgpt-status">
        <div class="status-dot status-ok"></div>
        <span>SecretGPT</span>
    </div>
    <div class="service-status" id="secretai-status">
        <div class="status-dot status-ok"></div>
        <span>SecretAI</span>
    </div>
    <div class="service-status" id="secretmcp-status">
        <div class="status-dot status-ok"></div>
        <span>SecretMCP</span>
    </div>
    <div class="service-status" id="bridge-status">
        <div class="status-dot status-ok"></div>
        <span>Bridge</span>
    </div>
    <button class="expand-attestation" onclick="toggleAttestationPanel()">
        <i class="fas fa-chevron-down"></i>
    </button>
</div>
```

#### **Detailed Attestation Panel (Expandable)**
```html
<div class="attestation-panel" id="attestation-details" style="display: none;">
    <div class="panel-header">
        <h3>🛡️ Security Attestation Details</h3>
        <button class="close-panel" onclick="toggleAttestationPanel()">×</button>
    </div>
    
    <div class="attestation-grid">
        <div class="attestation-card">
            <div class="card-header">
                <h4>🔮 SecretGPT Hub</h4>
                <span class="status-badge status-ok">OK</span>
            </div>
            <div class="card-content">
                <div class="attestation-detail">
                    <label>Status:</label>
                    <span>Fully Attested</span>
                </div>
                <div class="attestation-detail">
                    <label>MRTD:</label>
                    <code class="hash-display">a1b2c3d4e5f6...</code>
                </div>
                <div class="attestation-detail">
                    <label>Last Verified:</label>
                    <span>2 minutes ago</span>
                </div>
            </div>
        </div>
        
        <div class="attestation-card">
            <div class="card-header">
                <h4>🤖 SecretAI Service</h4>
                <span class="status-badge status-ok">OK</span>
            </div>
            <div class="card-content">
                <div class="attestation-detail">
                    <label>Status:</label>
                    <span>Fully Attested</span>
                </div>
                <div class="attestation-detail">
                    <label>MRTD:</label>
                    <code class="hash-display">e5f6g7h8i9j0...</code>
                </div>
                <div class="attestation-detail">
                    <label>Last Verified:</label>
                    <span>1 minute ago</span>
                </div>
            </div>
        </div>
        
        <div class="attestation-card">
            <div class="card-header">
                <h4>⚡ SecretMCP Service</h4>
                <span class="status-badge status-ok">OK</span>
            </div>
            <div class="card-content">
                <div class="attestation-detail">
                    <label>Status:</label>
                    <span>Connected & Verified</span>
                </div>
                <div class="attestation-detail">
                    <label>Endpoint:</label>
                    <span>secret-network-mcp:8002</span>
                </div>
                <div class="attestation-detail">
                    <label>Last Ping:</label>
                    <span>30 seconds ago</span>
                </div>
            </div>
        </div>
        
        <div class="attestation-card">
            <div class="card-header">
                <h4>🌉 MCP Bridge</h4>
                <span class="status-badge status-ok">OK</span>
            </div>
            <div class="card-content">
                <div class="attestation-detail">
                    <label>Status:</label>
                    <span>Secure Channel Active</span>
                </div>
                <div class="attestation-detail">
                    <label>Encryption:</label>
                    <span>AES-256-GCM</span>
                </div>
                <div class="attestation-detail">
                    <label>Last Handshake:</label>
                    <span>5 minutes ago</span>
                </div>
            </div>
        </div>
    </div>
</div>
```

### **Real-time Status Monitoring**
```javascript
// attestation.js - Status monitoring system
const AttestationMonitor = {
    components: {
        secretgpt: {
            name: 'SecretGPT Hub',
            endpoint: '/api/hub/status',
            element: 'secretgpt-status'
        },
        secretai: {
            name: 'SecretAI Service', 
            endpoint: '/api/secretai/status',
            element: 'secretai-status'
        },
        secretmcp: {
            name: 'SecretMCP Service',
            endpoint: '/api/mcp/status', 
            element: 'secretmcp-status'
        },
        bridge: {
            name: 'MCP Bridge',
            endpoint: '/api/bridge/status',
            element: 'bridge-status'
        }
    },
    
    async checkStatus(componentKey) {
        const component = this.components[componentKey];
        try {
            const response = await fetch(component.endpoint);
            const status = await response.json();
            this.updateStatusIndicator(component.element, status);
            return status;
        } catch (error) {
            this.updateStatusIndicator(component.element, { success: false, error: error.message });
            return { success: false, error: error.message };
        }
    },
    
    updateStatusIndicator(elementId, status) {
        const element = document.getElementById(elementId);
        const statusDot = element.querySelector('.status-dot');
        
        if (status.success) {
            statusDot.className = 'status-dot status-ok';
        } else if (status.checking) {
            statusDot.className = 'status-dot status-warning';
        } else {
            statusDot.className = 'status-dot status-error';
        }
    },
    
    startMonitoring() {
        // Check all components every 30 seconds
        setInterval(() => {
            Object.keys(this.components).forEach(key => {
                this.checkStatus(key);
            });
        }, 30000);
        
        // Initial check
        Object.keys(this.components).forEach(key => {
            this.checkStatus(key);
        });
    }
};
```

## Keplr Wallet Integration

### **Wallet Connection Flow**
1. User clicks "Connect Wallet" button
2. Check if Keplr extension is installed
3. Request connection to Secret Network (secret-4)
4. Get wallet key and address information
5. Send wallet details to secretGPT hub
6. Hub forwards to wallet proxy service
7. Proxy communicates with secret_network_mcp on VM2
8. Connection confirmed and UI updates

### **Wallet UI Components**

#### **Wallet Connection Button**
```html
<button class="wallet-connect-btn" onclick="connectWallet()">
    <div class="wallet-icon">
        <img src="/static/assets/keplr-logo.svg" alt="Keplr">
    </div>
    <div class="wallet-text">
        <span class="wallet-label">Connect Wallet</span>
        <span class="wallet-network">Secret Network</span>
    </div>
</button>
```

#### **Connected Wallet Display**
```html
<div class="wallet-connected">
    <div class="wallet-info">
        <div class="wallet-balance">1,250.42 SCRT</div>
        <div class="wallet-address">secret1abc...xyz</div>
    </div>
    <div class="wallet-actions">
        <button class="btn-wallet-action" onclick="showTransactionDialog()">
            Send
        </button>
        <button class="btn-wallet-action" onclick="showWalletDetails()">
            Details
        </button>
    </div>
</div>
```

### **Natural Language Transaction Processing**
```javascript
// wallet.js - Transaction processing
const WalletIntegration = {
    async processTransactionRequest(message) {
        // Parse natural language for transaction intent
        const transactionPattern = /send\s+(\d+(?:\.\d+)?)\s+scrt\s+to\s+(secret1[a-z0-9]+)/i;
        const match = message.match(transactionPattern);
        
        if (match) {
            const [, amount, recipient] = match;
            return this.showTransactionConfirmation(amount, recipient);
        }
        
        return null;
    },
    
    async showTransactionConfirmation(amount, recipient) {
        const modal = document.getElementById('transaction-modal');
        document.getElementById('tx-amount').textContent = amount;
        document.getElementById('tx-recipient').textContent = recipient;
        modal.style.display = 'block';
    },
    
    async executeTransaction(amount, recipient) {
        try {
            // Get Keplr signer
            const offlineSigner = window.keplr.getOfflineSigner('secret-4');
            const accounts = await offlineSigner.getAccounts();
            
            // Initialize SecretJS with Keplr
            const secretjs = new SecretNetworkClient({
                url: "https://api.secret.network",
                chainId: 'secret-4',
                wallet: offlineSigner,
                walletAddress: accounts[0].address,
                encryptionUtils: window.keplr.getEnigmaUtils('secret-4')
            });
            
            // Execute transaction
            const tx = await secretjs.tx.bank.send({
                from_address: accounts[0].address,
                to_address: recipient,
                amount: [{ denom: "uscrt", amount: String(amount * 1000000) }]
            }, {
                gasLimit: 200000
            });
            
            // Show success and update chat
            this.showTransactionSuccess(tx.transactionHash);
            return tx.transactionHash;
            
        } catch (error) {
            this.showTransactionError(error.message);
            throw error;
        }
    }
};
```

## Settings Panel Design

### **Comprehensive Settings Interface**
```html
<div class="settings-panel" id="settings-panel">
    <div class="settings-header">
        <h2>⚙️ Settings</h2>
        <button class="close-settings" onclick="closeSettings()">×</button>
    </div>
    
    <div class="settings-content">
        <!-- AI Behavior Settings -->
        <div class="settings-section">
            <h3>🎯 AI Behavior</h3>
            <div class="setting-item">
                <label>Temperature (Creativity)</label>
                <div class="temperature-control">
                    <input type="range" id="temperature-slider" min="0" max="1" step="0.1" value="0.7">
                    <div class="temperature-labels">
                        <span>Focused</span>
                        <span id="temperature-value">0.7</span>
                        <span>Creative</span>
                    </div>
                </div>
            </div>
            <div class="setting-item">
                <label>Model Selection</label>
                <select id="model-select">
                    <option value="deepseek-r1:70b">DeepSeek R1 70B (Default)</option>
                    <option value="coming-soon" disabled>More models coming soon</option>
                </select>
            </div>
            <div class="setting-item">
                <label>System Prompt</label>
                <select id="system-prompt-select">
                    <option value="default">Default Assistant</option>
                    <option value="helpful">Helpful & Concise</option>
                    <option value="creative">Creative & Detailed</option>
                    <option value="technical">Technical Expert</option>
                    <option value="custom">Custom...</option>
                </select>
            </div>
        </div>
        
        <!-- Wallet Settings -->
        <div class="settings-section">
            <h3>💰 Wallet Settings</h3>
            <div class="setting-item">
                <label>Auto-connect Keplr</label>
                <input type="checkbox" id="auto-connect-wallet" class="toggle-switch">
            </div>
            <div class="setting-item">
                <label>Transaction Confirmations</label>
                <select id="tx-confirmations">
                    <option value="always">Always require confirmation</option>
                    <option value="smart">Smart confirmations (high amounts only)</option>
                    <option value="minimal">Minimal confirmations</option>
                </select>
            </div>
            <div class="setting-item">
                <label>Gas Fee Settings</label>
                <select id="gas-settings">
                    <option value="auto">Auto (Recommended)</option>
                    <option value="low">Low (Slow but cheap)</option>
                    <option value="high">High (Fast but expensive)</option>
                    <option value="custom">Custom...</option>
                </select>
            </div>
        </div>
        
        <!-- Interface Settings -->
        <div class="settings-section">
            <h3>🎨 Interface</h3>
            <div class="setting-item">
                <label>Theme</label>
                <select id="theme-select">
                    <option value="secret-dark">Secret Dark (Default)</option>
                    <option value="secret-light">Secret Light</option>
                    <option value="midnight">Midnight Blue</option>
                    <option value="purple-haze">Purple Haze</option>
                </select>
            </div>
            <div class="setting-item">
                <label>Chat Message Density</label>
                <select id="chat-density">
                    <option value="comfortable">Comfortable</option>
                    <option value="compact">Compact</option>
                    <option value="spacious">Spacious</option>
                </select>
            </div>
            <div class="setting-item">
                <label>Animations</label>
                <input type="checkbox" id="enable-animations" class="toggle-switch" checked>
            </div>
            <div class="setting-item">
                <label>Sound Effects</label>
                <input type="checkbox" id="enable-sounds" class="toggle-switch">
            </div>
        </div>
        
        <!-- Privacy & Security Settings -->
        <div class="settings-section">
            <h3>🔒 Privacy & Security</h3>
            <div class="setting-item">
                <label>Store Conversations Locally Only</label>
                <input type="checkbox" id="local-storage-only" class="toggle-switch" checked>
            </div>
            <div class="setting-item">
                <label>Auto-delete Conversations</label>
                <select id="auto-delete">
                    <option value="never">Never</option>
                    <option value="1h">After 1 hour</option>
                    <option value="24h">After 24 hours</option>
                    <option value="7d">After 7 days</option>
                    <option value="30d">After 30 days</option>
                </select>
            </div>
            <div class="setting-item">
                <label>Show Attestation Details</label>
                <input type="checkbox" id="show-attestation" class="toggle-switch" checked>
            </div>
            <div class="setting-item">
                <label>Enable Analytics</label>
                <input type="checkbox" id="enable-analytics" class="toggle-switch">
            </div>
        </div>
    </div>
    
    <div class="settings-footer">
        <button class="btn-secondary" onclick="resetSettings()">Reset to Defaults</button>
        <button class="btn-primary" onclick="saveSettings()">Save Settings</button>
    </div>
</div>
```

## CSS Styling Framework

### **Core Styles with Secret Network Branding**
```css
/* Base Styles */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
    background: var(--bg-primary);
    color: var(--text-primary);
    line-height: 1.6;
    overflow-x: hidden;
}

/* Glassmorphism Effects */
.glass-card {
    background: var(--bg-glass);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 12px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}

.glass-panel {
    background: rgba(27, 31, 58, 0.8);
    backdrop-filter: blur(15px);
    border: 1px solid rgba(108, 92, 231, 0.2);
    border-radius: 16px;
}

/* Secret Network Styled Buttons */
.btn-primary {
    background: var(--gradient-primary);
    border: none;
    color: white;
    padding: 0.75rem 1.5rem;
    border-radius: 8px;
    font-weight: 600;
    font-size: 0.875rem;
    cursor: pointer;
    transition: all 0.3s ease;
    text-decoration: none;
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
}

.btn-primary:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(108, 92, 231, 0.4);
}

.btn-primary:active {
    transform: translateY(0);
}

.btn-secondary {
    background: var(--bg-secondary);
    border: 1px solid rgba(255, 255, 255, 0.2);
    color: var(--text-primary);
    padding: 0.75rem 1.5rem;
    border-radius: 8px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.3s ease;
}

.btn-secondary:hover {
    background: var(--bg-card);
    border-color: var(--secret-cyan);
}

/* Status Indicators */
.status-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    display: inline-block;
    margin-right: 0.5rem;
    transition: all 0.3s ease;
}

.status-ok {
    background: var(--status-ok);
    box-shadow: 0 0 8px rgba(0, 212, 255, 0.6);
}

.status-warning {
    background: var(--status-warning);
    box-shadow: 0 0 8px rgba(255, 184, 0, 0.6);
    animation: pulse-warning 2s infinite;
}

.status-error {
    background: var(--status-error);
    box-shadow: 0 0 8px rgba(255, 71, 87, 0.6);
}

@keyframes pulse-warning {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}

/* Chat Interface Styles */
.chat-container {
    flex: 1;
    display: flex;
    flex-direction: column;
    max-height: calc(100vh - 200px);
    overflow-y: auto;
    padding: 1rem;
    gap: 1rem;
}

.message-bubble {
    max-width: 70%;
    padding: 1rem 1.25rem;
    border-radius: 18px;
    word-wrap: break-word;
    animation: slideIn 0.3s ease-out;
}

.message-user {
    background: var(--gradient-primary);
    color: white;
    align-self: flex-end;
    border-bottom-right-radius: 4px;
}

.message-assistant {
    background: var(--bg-card);
    color: var(--text-primary);
    align-self: flex-start;
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-bottom-left-radius: 4px;
}

@keyframes slideIn {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* Wallet Integration Styles */
.wallet-connect-btn {
    background: var(--gradient-accent);
    border: none;
    color: white;
    padding: 1rem 1.5rem;
    border-radius: 12px;
    cursor: pointer;
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
    gap: 0.75rem;
    font-weight: 600;
}

.wallet-connect-btn:hover {
    transform: translateY(-3px);
    box-shadow: 0 12px 35px rgba(0, 212, 255, 0.4);
}

.wallet-connected {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: var(--glass-card);
    padding: 1rem;
    border-radius: 12px;
    border: 1px solid rgba(0, 212, 255, 0.3);
}

.wallet-balance {
    font-size: 1.25rem;
    font-weight: 700;
    color: var(--secret-cyan);
}

.wallet-address {
    font-family: 'SF Mono', 'Monaco', monospace;
    font-size: 0.875rem;
    color: var(--text-secondary);
}

/* Form Controls */
.form-control {
    background: var(--bg-secondary);
    border: 1px solid rgba(255, 255, 255, 0.2);
    color: var(--text-primary);
    padding: 0.75rem 1rem;
    border-radius: 8px;
    font-size: 0.875rem;
    transition: all 0.3s ease;
}

.form-control:focus {
    outline: none;
    border-color: var(--secret-cyan);
    box-shadow: 0 0 0 3px rgba(0, 212, 255, 0.1);
    background: var(--bg-card);
}

/* Toggle Switches */
.toggle-switch {
    appearance: none;
    width: 50px;
    height: 24px;
    background: var(--bg-secondary);
    border-radius: 12px;
    position: relative;
    cursor: pointer;
    transition: all 0.3s ease;
}

.toggle-switch:checked {
    background: var(--secret-cyan);
}

.toggle-switch::before {
    content: '';
    position: absolute;
    width: 20px;
    height: 20px;
    border-radius: 50%;
    background: white;
    top: 2px;
    left: 2px;
    transition: all 0.3s ease;
}

.toggle-switch:checked::before {
    transform: translateX(26px);
}

/* Responsive Design */
@media (max-width: 768px) {
    .chat-container {
        max-height: calc(100vh - 150px);
        padding: 0.5rem;
    }
    
    .message-bubble {
        max-width: 85%;
        padding: 0.75rem 1rem;
    }
    
    .settings-panel {
        width: 100%;
        height: 100%;
        border-radius: 0;
    }
    
    .wallet-connected {
        flex-direction: column;
        gap: 1rem;
        text-align: center;
    }
}

/* Loading States */
.loading-spinner {
    width: 20px;
    height: 20px;
    border: 2px solid rgba(255, 255, 255, 0.3);
    border-top: 2px solid var(--secret-cyan);
    border-radius: 50%;
    animation: spin 1s linear infinite;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

/* Scrollbar Styling */
::-webkit-scrollbar {
    width: 6px;
}

::-webkit-scrollbar-track {
    background: var(--bg-secondary);
}

::-webkit-scrollbar-thumb {
    background: var(--secret-purple);
    border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
    background: var(--secret-cyan);
}
```

## Implementation Phases

### **Phase 1: Foundation (Week 1-2)**
- [ ] Create basic file structure and FastAPI app
- [ ] Implement Secret Network branded base template
- [ ] Build core chat interface with Secret styling
- [ ] Integrate with existing secretGPT hub router
- [ ] Add four-component attestation status bar

### **Phase 2: Wallet Integration (Week 3-4)**  
- [ ] Implement Keplr wallet connection UI
- [ ] Create wallet proxy service for secret_network_mcp
- [ ] Add wallet balance display and management
- [ ] Build natural language transaction processing
- [ ] Implement transaction confirmation dialogs

### **Phase 3: Advanced Features (Week 5-6)**
- [ ] Build comprehensive settings panel
- [ ] Add detailed attestation monitoring panel
- [ ] Implement conversation history and search
- [ ] Create export functionality for chats
- [ ] Add temperature control with real-time preview

### **Phase 4: Polish & Optimization (Week 7-8)**
- [ ] Implement responsive design for mobile
- [ ] Add smooth animations and micro-interactions
- [ ] Optimize performance and bundle size
- [ ] Comprehensive testing across devices
- [ ] Documentation and deployment guides

## Integration with Existing Infrastructure

### **Hub Router Integration**
```python
# Add to hub/core/router.py
class ComponentType(Enum):
    SECRET_AI = "secret_ai"
    MCP_SERVICE = "mcp_service"
    WEB_UI = "web_ui"
    SECRETGPTEE_UI = "secretgptee_ui"  # New component
    WALLET_PROXY = "wallet_proxy"      # New component
```

### **Main Application Updates**
```python
# Add to main.py
async def run_with_dual_web_ui():
    """Run hub with both attestAI and secretGPTee interfaces"""
    # Initialize existing services
    hub = HubRouter()
    secret_ai = SecretAIService()
    mcp_service = HTTPMCPService()
    
    # Initialize wallet proxy service
    wallet_proxy = WalletProxyService()
    
    # Initialize both UIs
    attestai_service = WebUIService(hub)
    secretgptee_service = SecretGPTeeService(hub)
    
    # Register all components
    hub.register_component(ComponentType.SECRET_AI, secret_ai)
    hub.register_component(ComponentType.MCP_SERVICE, mcp_service)
    hub.register_component(ComponentType.WALLET_PROXY, wallet_proxy)
    hub.register_component(ComponentType.WEB_UI, attestai_service)
    hub.register_component(ComponentType.SECRETGPTEE_UI, secretgptee_service)
```

### **URL Routing Strategy**
- **AttestAI**: `https://attestai.io/` (existing)
- **SecretGPTee**: `https://attestai.io/secretgptee/` or `https://secretgptee.attestai.io/`
- **API Endpoints**: Shared backend at `https://attestai.io/api/`

## Success Metrics & Monitoring

### **User Experience Metrics**
- Time to first chat: < 3 seconds
- Wallet connection success rate: > 95%
- Transaction completion rate: > 90%
- Mobile responsiveness score: > 90
- Attestation status update latency: < 5 seconds

### **Technical Performance**
- Page load time: < 2 seconds
- JavaScript bundle size: < 500KB
- CSS bundle size: < 100KB
- Real-time status updates: < 1 second latency
- Memory usage: < 50MB per session

### **Security & Trust**
- Attestation verification success: > 99%
- Wallet connection security: Zero private key exposure
- Transaction confirmation accuracy: 100%
- SSL/TLS grade: A+
- Security audit compliance: Complete

This comprehensive plan provides a complete roadmap for building the SecretGPTee UI with Secret Network branding, Keplr wallet integration, and robust attestation monitoring. The interface will be modern, secure, and user-friendly while maintaining the technical excellence of the underlying secretGPT infrastructure.
