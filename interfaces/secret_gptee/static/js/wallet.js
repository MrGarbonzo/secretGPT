// SecretGPTee Wallet Integration JavaScript
// Keplr wallet detection, connection, balance queries, and transaction handling

// Wallet interface state
const WalletState = {
    connected: false,
    address: null,
    balance: null,
    network: 'secret-4', // Secret Network mainnet
    keplrInstalled: false,
    isConnecting: false
};

// Keplr wallet configuration for Secret Network
const KEPLR_CHAIN_CONFIG = {
    chainId: 'secret-4',
    chainName: 'Secret Network',
    rpc: 'https://scrt-rpc.whispernode.com:443',
    rest: 'https://scrt-lcd.whispernode.com:443',
    bip44: {
        coinType: 529,
    },
    bech32Config: {
        bech32PrefixAccAddr: 'secret',
        bech32PrefixAccPub: 'secretpub',
        bech32PrefixValAddr: 'secretvaloper',
        bech32PrefixValPub: 'secretvaloperpub',
        bech32PrefixConsAddr: 'secretvalcons',
        bech32PrefixConsPub: 'secretvalconspub',
    },
    currencies: [{
        coinDenom: 'SCRT',
        coinMinimalDenom: 'uscrt',
        coinDecimals: 6,
        coinGeckoId: 'secret',
    }],
    feeCurrencies: [{
        coinDenom: 'SCRT',
        coinMinimalDenom: 'uscrt',
        coinDecimals: 6,
        coinGeckoId: 'secret',
    }],
    stakeCurrency: {
        coinDenom: 'SCRT',
        coinMinimalDenom: 'uscrt',
        coinDecimals: 6,
        coinGeckoId: 'secret',
    },
    coinType: 529,
    gasPriceStep: {
        low: 0.1,
        average: 0.25,
        high: 0.4,
    },
    features: ['secretwasm'],
};

// Wallet interface management
const WalletInterface = {
    // Initialize wallet interface
    init() {
        console.log('🔮 Initializing SecretGPTee wallet interface...');
        
        this.checkKeplrInstallation();
        this.setupEventListeners();
        this.updateUI();
        
        console.log('✅ Wallet interface initialized');
    },
    
    // Check if Keplr wallet is installed
    checkKeplrInstallation() {
        if (window.keplr) {
            WalletState.keplrInstalled = true;
            console.log('✅ Keplr wallet detected');
        } else {
            WalletState.keplrInstalled = false;
            console.log('❌ Keplr wallet not found');
        }
        
        // Listen for Keplr installation
        window.addEventListener('keplr_keystorechange', () => {
            console.log('🔄 Keplr keystore changed, refreshing connection...');
            this.refreshConnection();
        });
    },
    
    // Setup event listeners
    setupEventListeners() {
        const connectBtn = document.getElementById('connect-wallet-btn');
        const disconnectBtn = document.getElementById('disconnect-wallet-btn');
        const refreshBalanceBtn = document.getElementById('refresh-balance-btn');
        
        if (connectBtn) {
            connectBtn.addEventListener('click', this.connectWallet.bind(this));
        }
        
        if (disconnectBtn) {
            disconnectBtn.addEventListener('click', this.disconnectWallet.bind(this));
        }
        
        if (refreshBalanceBtn) {
            refreshBalanceBtn.addEventListener('click', this.refreshBalance.bind(this));
        }
        
        // Auto-connect if previously connected
        this.tryAutoConnect();
    },
    
    // Try to auto-connect wallet if previously connected
    async tryAutoConnect() {
        try {
            const savedAddress = localStorage.getItem('secretgptee-wallet-address');
            if (savedAddress && WalletState.keplrInstalled) {
                console.log('🔄 Attempting auto-connect to wallet...');
                await this.connectWallet(false); // Silent connection
            }
        } catch (error) {
            console.log('Auto-connect failed:', error);
        }
    },
    
    // Connect to Keplr wallet
    async connectWallet(showMessages = true) {
        if (!WalletState.keplrInstalled) {
            if (showMessages) {
                SecretGPTee.showToast('Please install Keplr wallet extension', 'error');
                this.showInstallModal();
            }
            return false;
        }
        
        if (WalletState.isConnecting) {
            return false;
        }
        
        WalletState.isConnecting = true;
        this.updateConnectButton();
        
        try {
            // Add Secret Network to Keplr
            await this.addSecretNetworkToKeplr();
            
            // Enable Secret Network in Keplr
            await window.keplr.enable(KEPLR_CHAIN_CONFIG.chainId);
            
            // Get the offline signer
            const offlineSigner = window.getOfflineSigner(KEPLR_CHAIN_CONFIG.chainId);
            const accounts = await offlineSigner.getAccounts();
            
            if (accounts.length === 0) {
                throw new Error('No accounts found in Keplr wallet');
            }
            
            const account = accounts[0];
            WalletState.connected = true;
            WalletState.address = account.address;
            
            // Save connection state
            localStorage.setItem('secretgptee-wallet-address', account.address);
            localStorage.setItem('secretgptee-wallet-connected', 'true');
            
            // Update chat state
            if (window.ChatState) {
                window.ChatState.walletConnected = true;
                window.ChatState.walletAddress = account.address;
            }
            
            console.log('✅ Wallet connected:', account.address);
            if (showMessages) {
                SecretGPTee.showToast('Wallet connected successfully', 'success');
            }
            
            // Get balance
            await this.refreshBalance();
            
            this.updateUI();
            return true;
            
        } catch (error) {
            console.error('Wallet connection failed:', error);
            if (showMessages) {
                SecretGPTee.showToast('Failed to connect wallet: ' + error.message, 'error');
            }
            WalletState.connected = false;
            WalletState.address = null;
            return false;
        } finally {
            WalletState.isConnecting = false;
            this.updateConnectButton();
        }
    },
    
    // Add Secret Network to Keplr
    async addSecretNetworkToKeplr() {
        try {
            await window.keplr.experimentalSuggestChain(KEPLR_CHAIN_CONFIG);
            console.log('✅ Secret Network added to Keplr');
        } catch (error) {
            if (error.message !== 'Request rejected') {
                console.error('Failed to add Secret Network to Keplr:', error);
                throw error;
            }
        }
    },
    
    // Disconnect wallet
    disconnectWallet() {
        WalletState.connected = false;
        WalletState.address = null;
        WalletState.balance = null;
        
        // Clear saved state
        localStorage.removeItem('secretgptee-wallet-address');
        localStorage.removeItem('secretgptee-wallet-connected');
        
        // Update chat state
        if (window.ChatState) {
            window.ChatState.walletConnected = false;
            window.ChatState.walletAddress = null;
        }
        
        console.log('🔌 Wallet disconnected');
        SecretGPTee.showToast('Wallet disconnected', 'info');
        
        this.updateUI();
    },
    
    // Refresh wallet balance
    async refreshBalance() {
        if (!WalletState.connected || !WalletState.address) {
            return;
        }
        
        try {
            const refreshBtn = document.getElementById('refresh-balance-btn');
            if (refreshBtn) {
                refreshBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
                refreshBtn.disabled = true;
            }
            
            const response = await fetch('/secret_gptee/api/v1/wallet/balance', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    address: WalletState.address
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            if (data.success) {
                WalletState.balance = data.balance;
                console.log('💰 Balance updated:', data.balance);
                this.updateBalanceDisplay();
            } else {
                throw new Error('Failed to fetch balance');
            }
            
        } catch (error) {
            console.error('Balance refresh failed:', error);
            SecretGPTee.showToast('Failed to refresh balance', 'error');
        } finally {
            const refreshBtn = document.getElementById('refresh-balance-btn');
            if (refreshBtn) {
                refreshBtn.innerHTML = '<i class="fas fa-sync-alt"></i>';
                refreshBtn.disabled = false;
            }
        }
    },
    
    // Refresh connection status
    async refreshConnection() {
        if (WalletState.connected) {
            await this.connectWallet(false);
        }
    },
    
    // Update UI elements
    updateUI() {
        this.updateWalletStatus();
        this.updateConnectButton();
        this.updateWalletInfo();
        this.updateBalanceDisplay();
    },
    
    // Update wallet status indicator
    updateWalletStatus() {
        const statusElement = document.getElementById('wallet-status');
        if (statusElement) {
            if (WalletState.connected) {
                statusElement.innerHTML = `
                    <span class="status-dot connected"></span>
                    <span>Connected</span>
                `;
                statusElement.className = 'wallet-status connected';
            } else if (!WalletState.keplrInstalled) {
                statusElement.innerHTML = `
                    <span class="status-dot error"></span>
                    <span>Keplr Not Installed</span>
                `;
                statusElement.className = 'wallet-status error';
            } else {
                statusElement.innerHTML = `
                    <span class="status-dot disconnected"></span>
                    <span>Disconnected</span>
                `;
                statusElement.className = 'wallet-status disconnected';
            }
        }
    },
    
    // Update connect button  
    updateConnectButton() {
        const connectBtn = document.getElementById('wallet-connect-btn');
        const statusSpan = document.getElementById('wallet-status');
        
        if (connectBtn && statusSpan) {
            if (WalletState.isConnecting) {
                statusSpan.textContent = 'Connecting...';
                connectBtn.disabled = true;
                connectBtn.querySelector('i').className = 'fas fa-spinner fa-spin';
            } else if (WalletState.connected) {
                statusSpan.textContent = 'Connected';
                connectBtn.disabled = false;
                connectBtn.querySelector('i').className = 'fas fa-wallet';
            } else if (!WalletState.keplrInstalled) {
                statusSpan.textContent = 'Install Keplr';
                connectBtn.disabled = false;
                connectBtn.querySelector('i').className = 'fas fa-download';
            } else {
                statusSpan.textContent = 'Connect Wallet';
                connectBtn.disabled = false;
                connectBtn.querySelector('i').className = 'fas fa-wallet';
            }
        }
        
        const disconnectBtn = document.getElementById('disconnect-wallet-btn');
        if (disconnectBtn) {
            disconnectBtn.style.display = WalletState.connected ? 'block' : 'none';
        }
    },
    
    // Update wallet info display
    updateWalletInfo() {
        const walletInfo = document.getElementById('wallet-info');
        if (walletInfo) {
            if (WalletState.connected && WalletState.address) {
                walletInfo.innerHTML = `
                    <div class="wallet-address">
                        <label>Address:</label>
                        <span class="address" title="${WalletState.address}">
                            ${this.formatAddress(WalletState.address)}
                        </span>
                        <button class="copy-btn" onclick="WalletInterface.copyAddress()" title="Copy Address">
                            <i class="fas fa-copy"></i>
                        </button>
                    </div>
                `;
                walletInfo.style.display = 'block';
            } else {
                walletInfo.style.display = 'none';
            }
        }
    },
    
    // Update balance display
    updateBalanceDisplay() {
        const balanceElement = document.getElementById('wallet-balance');
        if (balanceElement) {
            if (WalletState.connected && WalletState.balance !== null) {
                const scrtBalance = this.formatBalance(WalletState.balance);
                balanceElement.innerHTML = `
                    <div class="balance-info">
                        <label>Balance:</label>
                        <span class="balance-amount">${scrtBalance} SCRT</span>
                        <button id="refresh-balance-btn" class="refresh-btn" title="Refresh Balance">
                            <i class="fas fa-sync-alt"></i>
                        </button>
                    </div>
                `;
                balanceElement.style.display = 'block';
                
                // Re-attach event listener
                const refreshBtn = document.getElementById('refresh-balance-btn');
                if (refreshBtn) {
                    refreshBtn.addEventListener('click', this.refreshBalance.bind(this));
                }
            } else {
                balanceElement.style.display = 'none';
            }
        }
    },
    
    // Format wallet address for display
    formatAddress(address) {
        if (!address) return '';
        return `${address.slice(0, 10)}...${address.slice(-8)}`;
    },
    
    // Format balance for display
    formatBalance(balance) {
        if (!balance || typeof balance !== 'object') return '0.00';
        
        // Handle different balance response formats
        if (balance.amount) {
            // Convert from uscrt to SCRT (divide by 1,000,000)
            const scrtAmount = parseFloat(balance.amount) / 1000000;
            return scrtAmount.toFixed(6);
        } else if (typeof balance === 'string') {
            const scrtAmount = parseFloat(balance) / 1000000;
            return scrtAmount.toFixed(6);
        }
        
        return '0.000000';
    },
    
    // Copy address to clipboard
    async copyAddress() {
        if (!WalletState.address) return;
        
        try {
            await navigator.clipboard.writeText(WalletState.address);
            SecretGPTee.showToast('Address copied to clipboard', 'success');
        } catch (error) {
            console.error('Failed to copy address:', error);
            SecretGPTee.showToast('Failed to copy address', 'error');
        }
    },
    
    // Show Keplr installation modal
    showInstallModal() {
        const modal = document.createElement('div');
        modal.className = 'install-modal-overlay';
        modal.innerHTML = `
            <div class="install-modal">
                <div class="modal-header">
                    <h3>Install Keplr Wallet</h3>
                    <button class="close-btn" onclick="this.closest('.install-modal-overlay').remove()">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="modal-body">
                    <p>To use SecretGPTee's wallet features, you need to install the Keplr wallet extension.</p>
                    <div class="install-options">
                        <a href="https://chrome.google.com/webstore/detail/keplr/dmkamcknogkgcdfhhbddcghachkejeap" 
                           target="_blank" class="install-btn chrome">
                            <i class="fab fa-chrome"></i>
                            Install for Chrome
                        </a>
                        <a href="https://addons.mozilla.org/en-US/firefox/addon/keplr/" 
                           target="_blank" class="install-btn firefox">
                            <i class="fab fa-firefox"></i>
                            Install for Firefox
                        </a>
                    </div>
                    <div class="install-note">
                        <i class="fas fa-info-circle"></i>
                        After installing, refresh this page and click "Connect Wallet" again.
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Close modal when clicking outside
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });
    },
    
    // Send SCRT transaction
    async sendTransaction(recipientAddress, amount, memo = '') {
        if (!WalletState.connected || !window.keplr) {
            throw new Error('Wallet not connected');
        }
        
        try {
            // Get the offline signer
            const offlineSigner = window.getOfflineSigner(KEPLR_CHAIN_CONFIG.chainId);
            
            // Import CosmJS
            const { SigningCosmWasmClient } = window.cosmjs;
            
            // Create signing client
            const client = await SigningCosmWasmClient.connectWithSigner(
                KEPLR_CHAIN_CONFIG.rpc,
                offlineSigner
            );
            
            // Convert SCRT to uscrt (multiply by 1,000,000)
            const amountInUscrt = Math.floor(parseFloat(amount) * 1000000);
            
            // Create send message
            const sendMsg = {
                typeUrl: '/cosmos.bank.v1beta1.MsgSend',
                value: {
                    fromAddress: WalletState.address,
                    toAddress: recipientAddress,
                    amount: [{
                        denom: 'uscrt',
                        amount: amountInUscrt.toString()
                    }]
                }
            };
            
            // Calculate fee
            const fee = {
                amount: [{
                    denom: 'uscrt',
                    amount: '25000' // 0.025 SCRT
                }],
                gas: '100000'
            };
            
            // Sign and broadcast transaction
            const result = await client.signAndBroadcast(
                WalletState.address,
                [sendMsg],
                fee,
                memo
            );
            
            return result;
            
        } catch (error) {
            console.error('Transaction failed:', error);
            throw error;
        }
    },
    
    // Get transaction status
    async getTransactionStatus(txHash) {
        try {
            const response = await fetch(`${KEPLR_CHAIN_CONFIG.rest}/cosmos/tx/v1beta1/txs/${txHash}`);
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Failed to get transaction status:', error);
            throw error;
        }
    },
    
    // Utility function to check if address is valid Secret Network address
    isValidSecretAddress(address) {
        return address && address.startsWith('secret1') && address.length === 45;
    }
};

// Transaction helper functions
const TransactionHelpers = {
    // Show send transaction modal
    showSendModal() {
        if (!WalletState.connected) {
            SecretGPTee.showToast('Please connect wallet first', 'warning');
            return;
        }
        
        const modal = document.createElement('div');
        modal.className = 'transaction-modal-overlay';
        modal.innerHTML = `
            <div class="transaction-modal">
                <div class="modal-header">
                    <h3>Send SCRT</h3>
                    <button class="close-btn" onclick="this.closest('.transaction-modal-overlay').remove()">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="modal-body">
                    <form id="send-transaction-form">
                        <div class="form-group">
                            <label for="recipient-address">Recipient Address</label>
                            <input type="text" id="recipient-address" placeholder="secret1..." required>
                        </div>
                        <div class="form-group">
                            <label for="send-amount">Amount (SCRT)</label>
                            <input type="number" id="send-amount" step="0.000001" min="0.000001" required>
                            <div class="balance-hint">
                                Available: ${WalletInterface.formatBalance(WalletState.balance)} SCRT
                            </div>
                        </div>
                        <div class="form-group">
                            <label for="transaction-memo">Memo (Optional)</label>
                            <input type="text" id="transaction-memo" placeholder="Transaction memo">
                        </div>
                        <div class="form-actions">
                            <button type="button" class="cancel-btn" onclick="this.closest('.transaction-modal-overlay').remove()">
                                Cancel
                            </button>
                            <button type="submit" class="send-btn">
                                <i class="fas fa-paper-plane"></i> Send SCRT
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Handle form submission
        const form = modal.querySelector('#send-transaction-form');
        form.addEventListener('submit', this.handleSendTransaction.bind(this));
        
        // Close modal when clicking outside
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });
    },
    
    // Handle send transaction form submission
    async handleSendTransaction(event) {
        event.preventDefault();
        
        const recipientAddress = document.getElementById('recipient-address').value.trim();
        const amount = document.getElementById('send-amount').value.trim();
        const memo = document.getElementById('transaction-memo').value.trim();
        
        // Validate inputs
        if (!WalletInterface.isValidSecretAddress(recipientAddress)) {
            SecretGPTee.showToast('Invalid recipient address', 'error');
            return;
        }
        
        if (!amount || parseFloat(amount) <= 0) {
            SecretGPTee.showToast('Invalid amount', 'error');
            return;
        }
        
        try {
            const sendBtn = document.querySelector('.send-btn');
            sendBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Sending...';
            sendBtn.disabled = true;
            
            const result = await WalletInterface.sendTransaction(recipientAddress, amount, memo);
            
            if (result.code === 0) {
                SecretGPTee.showToast('Transaction sent successfully!', 'success');
                console.log('Transaction hash:', result.transactionHash);
                
                // Close modal
                document.querySelector('.transaction-modal-overlay').remove();
                
                // Refresh balance
                setTimeout(() => {
                    WalletInterface.refreshBalance();
                }, 2000);
            } else {
                throw new Error(result.rawLog || 'Transaction failed');
            }
            
        } catch (error) {
            console.error('Send transaction failed:', error);
            SecretGPTee.showToast('Transaction failed: ' + error.message, 'error');
        } finally {
            const sendBtn = document.querySelector('.send-btn');
            if (sendBtn) {
                sendBtn.innerHTML = '<i class="fas fa-paper-plane"></i> Send SCRT';
                sendBtn.disabled = false;
            }
        }
    }
};

// Export for global access
window.WalletInterface = WalletInterface;
window.WalletState = WalletState;
window.TransactionHelpers = TransactionHelpers;

// Global functions for HTML onclick handlers
window.toggleWallet = function() {
    if (WalletState.connected) {
        WalletInterface.disconnect();
    } else {
        WalletInterface.connect();
    }
};

window.refreshBalance = function() {
    if (WalletState.connected && WalletState.address) {
        WalletInterface.refreshBalance();
    }
};

window.copyWalletAddress = function() {
    WalletInterface.copyAddress();
};