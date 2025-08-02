/**
 * Debug utilities for wallet integration testing
 */

window.WalletDebug = {
    
    // Test if secretGPT service is running
    async testServiceConnection() {
        console.log('🔍 Testing secretGPT service connection...');
        
        try {
            const response = await fetch('/api/system/status', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                console.log('✅ secretGPT service is running:', data);
                return true;
            } else {
                console.error('❌ secretGPT service not responding:', response.status, response.statusText);
                return false;
            }
        } catch (error) {
            console.error('❌ Cannot connect to secretGPT service:', error);
            return false;
        }
    },
    
    // Test wallet service status
    async testWalletService() {
        console.log('🔍 Testing wallet service...');
        
        try {
            const response = await fetch('/api/wallet/status', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                console.log('✅ Wallet service status:', data);
                return data;
            } else {
                console.error('❌ Wallet service not available:', response.status, response.statusText);
                return null;
            }
        } catch (error) {
            console.error('❌ Wallet service error:', error);
            return null;
        }
    },
    
    // Test full wallet integration
    async runFullTest() {
        console.log('🧪 Running full wallet integration test...');
        console.log('=' .repeat(50));
        
        // Test 1: Service connection
        const serviceRunning = await this.testServiceConnection();
        if (!serviceRunning) {
            console.log('❌ Test failed: secretGPT service not running');
            return false;
        }
        
        // Test 2: Wallet service
        const walletStatus = await this.testWalletService();
        if (!walletStatus) {
            console.log('❌ Test failed: Wallet service not available');
            return false;
        }
        
        // Test 3: Keplr detection
        if (!window.keplr) {
            console.log('❌ Test failed: Keplr wallet not installed');
            return false;
        }
        console.log('✅ Keplr wallet detected');
        
        // Test 4: MCP connection
        if (walletStatus.mcp_connection) {
            console.log('✅ secret_network_mcp connection working');
        } else {
            console.log('⚠️  secret_network_mcp not connected - blockchain queries may fail');
        }
        
        console.log('✅ All tests passed! Wallet integration should work');
        return true;
    },
    
    // Show connection instructions
    showConnectionInstructions() {
        console.log('🔗 Wallet Connection Instructions:');
        console.log('1. Make sure Keplr wallet extension is installed');
        console.log('2. Make sure secretGPT Hub service is running');
        console.log('3. Make sure secret_network_mcp service is running');
        console.log('4. Try connecting your wallet');
        console.log('');
        console.log('Debug commands:');
        console.log('- WalletDebug.testServiceConnection()');
        console.log('- WalletDebug.testWalletService()');
        console.log('- WalletDebug.runFullTest()');
    }
};

// Auto-run test on page load
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(() => {
        console.log('🔮 SecretGPTee Wallet Debug Tools Loaded');
        console.log('Run WalletDebug.runFullTest() to test wallet integration');
        console.log('Run WalletDebug.showConnectionInstructions() for help');
    }, 1000);
});