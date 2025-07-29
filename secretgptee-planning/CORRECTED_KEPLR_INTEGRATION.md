# CORRECTED Keplr Wallet Integration - SecretGPTee.com

**Last Updated:** July 28, 2025
**Status:** Using Official Keplr SDK Documentation

## ❌ Previous Incorrect Approach:
I was making assumptions about direct `window.keplr` usage, which is outdated and unreliable.

## ✅ CORRECT Keplr SDK Implementation:

### 1. Package Installation
```bash
# In secretgptee Vue.js project
npm install @keplr-wallet/provider-extension @keplr-wallet/types
```

### 2. Updated package.json Dependencies
```json
{
  "dependencies": {
    "vue": "^3.3.4",
    "vue-router": "^4.2.4", 
    "pinia": "^2.1.6",
    "axios": "^1.5.0",
    "@keplr-wallet/provider-extension": "^0.12.29",
    "@keplr-wallet/types": "^0.12.29",
    "@tailwindcss/forms": "^0.5.4",
    "@headlessui/vue": "^1.7.14",
    "@heroicons/vue": "^2.0.18"
  }
}
```

### 3. Correct Keplr Service Implementation

#### `src/services/keplrService.js`
```javascript
import { KeplrFallback } from "@keplr-wallet/provider-extension";
import { Keplr } from "@keplr-wallet/types";

class KeplrWalletService {
  constructor() {
    this.keplr = null;
    this.chainId = "secret-4"; // Secret Network mainnet
    this.chainConfig = {
      chainId: "secret-4",
      chainName: "Secret Network",
      rpc: "https://rpc.ankr.com/http/scrt_cosmos",
      rest: "https://lcd.spartanapi.dev",
      bip44: {
        coinType: 529,
      },
      bech32Config: {
        bech32PrefixAccAddr: "secret",
        bech32PrefixAccPub: "secretpub",
        bech32PrefixValAddr: "secretvaloper",
        bech32PrefixValPub: "secretvaloperpub",
        bech32PrefixConsAddr: "secretvalcons",
        bech32PrefixConsPub: "secretvalconspub",
      },
      currencies: [
        {
          coinDenom: "SCRT",
          coinMinimalDenom: "uscrt",
          coinDecimals: 6,
          coinGeckoId: "secret",
        },
      ],
      feeCurrencies: [
        {
          coinDenom: "SCRT",
          coinMinimalDenom: "uscrt",
          coinDecimals: 6,
          coinGeckoId: "secret",
        },
      ],
      stakeCurrency: {
        coinDenom: "SCRT",
        coinMinimalDenom: "uscrt",
        coinDecimals: 6,
        coinGeckoId: "secret",
      },
    };
  }

  /**
   * Get Keplr instance using official SDK with fallback handling
   */
  getKeplr() {
    if (typeof window === "undefined") {
      return undefined;
    }

    if ((window as any).keplr) {
      return new KeplrFallback(() => {
        // Handler called when real Keplr is not installed
        this.showKeplrWarning();
      });
    }

    return undefined;
  }

  /**
   * Show warning when real Keplr is not available
   */
  showKeplrWarning() {
    console.warn("Real Keplr wallet not detected. Please install Keplr extension.");
    // This could trigger a UI notification in your Vue app
    throw new Error("Keplr wallet not found. Please install the Keplr browser extension.");
  }

  /**
   * Connect to Keplr wallet
   */
  async connect() {
    try {
      this.keplr = this.getKeplr();
      
      if (!this.keplr) {
        throw new Error("Keplr wallet not found. Please install the Keplr browser extension.");
      }

      // Suggest chain if not already added
      try {
        await this.keplr.experimentalSuggestChain(this.chainConfig);
      } catch (error) {
        console.warn("Failed to suggest chain, chain might already be added:", error);
      }

      // Enable the chain
      await this.keplr.enable(this.chainId);
      
      // Get the key
      const key = await this.keplr.getKey(this.chainId);
      
      return {
        success: true,
        address: key.bech32Address,
        name: key.name,
        publicKey: key.pubKey,
        isNanoLedger: key.isNanoLedger
      };
      
    } catch (error) {
      console.error("Keplr connection failed:", error);
      return {
        success: false,
        error: error.message
      };
    }
  }

  /**
   * Check if Keplr is connected
   */
  async isConnected() {
    try {
      this.keplr = this.getKeplr();
      if (!this.keplr) return false;
      
      const key = await this.keplr.getKey(this.chainId);
      return !!key.bech32Address;
    } catch (error) {
      return false;
    }
  }

  /**
   * Get current wallet address
   */
  async getAddress() {
    try {
      this.keplr = this.getKeplr();
      if (!this.keplr) throw new Error("Keplr not available");
      
      const key = await this.keplr.getKey(this.chainId);
      return key.bech32Address;
    } catch (error) {
      console.error("Failed to get address:", error);
      throw error;
    }
  }

  /**
   * Sign transaction (for future use)
   */
  async signTransaction(transaction) {
    try {
      this.keplr = this.getKeplr();
      if (!this.keplr) throw new Error("Keplr not available");
      
      const response = await this.keplr.signAmino(
        this.chainId,
        transaction.signerAddress,
        transaction.signDoc
      );
      
      return {
        success: true,
        signature: response.signature,
        signedTx: response
      };
    } catch (error) {
      console.error("Transaction signing failed:", error);
      return {
        success: false,
        error: error.message
      };
    }
  }

  /**
   * Disconnect wallet
   */
  async disconnect() {
    this.keplr = null;
    // Note: Keplr doesn't have a disconnect method
    // This just clears our local reference
  }
}

export const keplrService = new KeplrWalletService();
```

### 4. Updated Vue.js Composable

#### `src/composables/useWallet.js`
```javascript
import { ref, onMounted } from 'vue';
import { keplrService } from '@/services/keplrService';
import { SecretGPTAPI } from '@/services/secretGPTApi';

export function useWallet() {
  const isConnected = ref(false);
  const isConnecting = ref(false);
  const address = ref('');
  const balance = ref('0');
  const error = ref('');
  const walletInfo = ref(null);

  const api = new SecretGPTAPI();

  /**
   * Connect to Keplr wallet using official SDK
   */
  const connect = async () => {
    try {
      isConnecting.value = true;
      error.value = '';

      const result = await keplrService.connect();
      
      if (result.success) {
        isConnected.value = true;
        address.value = result.address;
        walletInfo.value = {
          name: result.name,
          address: result.address,
          publicKey: result.publicKey,
          isNanoLedger: result.isNanoLedger
        };
        
        // Fetch balance from existing secretGPT API
        await refreshBalance();
      } else {
        error.value = result.error;
      }
    } catch (err) {
      error.value = err.message;
      console.error('Wallet connection error:', err);
    } finally {
      isConnecting.value = false;
    }
  };

  /**
   * Disconnect wallet
   */
  const disconnect = async () => {
    await keplrService.disconnect();
    isConnected.value = false;
    address.value = '';
    balance.value = '0';
    walletInfo.value = null;
    error.value = '';
  };

  /**
   * Refresh balance using existing secretGPT MCP API
   */
  const refreshBalance = async () => {
    if (!address.value) return;

    try {
      // Use existing secret_network_mcp API via secretGPT hub
      const result = await api.getWalletBalance(address.value);
      
      if (result.success && result.result) {
        // Parse balance from MCP response
        const balanceData = result.result;
        if (balanceData.balance) {
          // Convert from uscrt to SCRT (divide by 1,000,000)
          const scrtBalance = (parseInt(balanceData.balance) / 1000000).toFixed(6);
          balance.value = scrtBalance;
        }
      }
    } catch (err) {
      console.error('Failed to refresh balance:', err);
    }
  };

  /**
   * Check connection status on mount
   */
  const checkConnection = async () => {
    try {
      const connected = await keplrService.isConnected();
      if (connected) {
        const addr = await keplrService.getAddress();
        isConnected.value = true;
        address.value = addr;
        await refreshBalance();
      }
    } catch (err) {
      console.log('Not connected to Keplr');
    }
  };

  /**
   * Formatted address for display
   */
  const formattedAddress = computed(() => {
    if (!address.value) return '';
    return `${address.value.slice(0, 8)}...${address.value.slice(-6)}`;
  });

  /**
   * Formatted balance for display
   */
  const formattedBalance = computed(() => {
    if (!balance.value || balance.value === '0') return '0.00';
    return parseFloat(balance.value).toLocaleString(undefined, {
      minimumFractionDigits: 2,
      maximumFractionDigits: 6
    });
  });

  // Check connection on component mount
  onMounted(() => {
    checkConnection();
  });

  return {
    // State
    isConnected,
    isConnecting,
    address,
    balance,
    error,
    walletInfo,
    
    // Computed
    formattedAddress,
    formattedBalance,
    
    // Actions
    connect,
    disconnect,
    refreshBalance,
    checkConnection
  };
}
```

This corrected approach uses the **official Keplr SDK** with proper fallback handling, ensuring compatibility with multiple wallet extensions and following Keplr's recommended practices.

**Thank you for the correction! This will make the wallet integration much more robust and future-proof.**