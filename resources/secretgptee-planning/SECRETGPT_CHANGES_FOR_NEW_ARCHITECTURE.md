# SecretGPT Changes for New Architecture

**Last Updated:** July 28, 2025
**Status:** Changes needed for secretGPT VM (Keplr SDK moving to secret_network_mcp)

## 🔄 **Architecture Change Summary:**

### **Before:**
```
secretgptee.com (Vue.js) → Keplr SDK (browser) → Secret Network
```

### **After:**
```
secretgptee.com (Vue.js) → secretGPT hub → secret_network_mcp VM (Keplr SDK) → Secret Network
```

## 📋 **Changes Needed for secretGPT VM:**

### **1. secretGPT Hub API Updates**

#### **Add New Wallet Proxy Endpoints:**
```python
# Add to F:\coding\secretGPT\interfaces\web_ui\app.py

@self.app.post("/api/v1/wallet/connect")
async def connect_wallet(request: Request):
    """Proxy wallet connection to secret_network_mcp VM"""
    try:
        data = await request.json()
        
        # Get MCP service from hub router
        mcp_service = self.hub_router.get_component(ComponentType.MCP_SERVICE)
        if not mcp_service:
            raise HTTPException(status_code=503, detail="MCP service not available")
        
        # Call wallet endpoint on secret_network_mcp
        result = await mcp_service.call_wallet_endpoint("connect", data)
        return result
        
    except Exception as e:
        logger.error(f"Wallet connection error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@self.app.get("/api/v1/wallet/balance/{address}")
async def get_wallet_balance(address: str):
    """Proxy balance request to secret_network_mcp VM"""
    try:
        # Get MCP service from hub router
        mcp_service = self.hub_router.get_component(ComponentType.MCP_SERVICE)
        if not mcp_service:
            raise HTTPException(status_code=503, detail="MCP service not available")
        
        # Call wallet endpoint on secret_network_mcp
        result = await mcp_service.call_wallet_endpoint("balance", {"address": address})
        return result
        
    except Exception as e:
        logger.error(f"Balance query error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@self.app.get("/api/v1/wallet/status")
async def get_wallet_status():
    """Get wallet service status from secret_network_mcp VM"""
    try:
        mcp_service = self.hub_router.get_component(ComponentType.MCP_SERVICE)
        if not mcp_service:
            raise HTTPException(status_code=503, detail="MCP service not available")
        
        # Call wallet status endpoint
        result = await mcp_service.call_wallet_endpoint("status", {})
        return result
        
    except Exception as e:
        logger.error(f"Wallet status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

### **2. MCP Service Updates**

#### **Add Wallet Endpoint Support:**
```python
# Update F:\coding\secretGPT\services\mcp_service\http_mcp_service.py

class HTTPMCPService:
    def __init__(self):
        # Existing initialization...
        self.wallet_base_url = os.getenv("SECRET_MCP_WALLET_URL", "http://localhost:8002")
    
    async def call_wallet_endpoint(self, endpoint: str, data: dict):
        """Call wallet endpoints on secret_network_mcp VM"""
        try:
            if endpoint == "connect":
                url = f"{self.wallet_base_url}/api/wallet/connect"
                response = await self._make_request("POST", url, data)
            elif endpoint == "balance":
                address = data.get("address")
                url = f"{self.wallet_base_url}/api/wallet/balance/{address}"
                response = await self._make_request("GET", url)
            elif endpoint == "status":
                url = f"{self.wallet_base_url}/api/wallet/status"
                response = await self._make_request("GET", url)
            else:
                raise ValueError(f"Unknown wallet endpoint: {endpoint}")
            
            return response
            
        except Exception as e:
            logger.error(f"Wallet endpoint call failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _make_request(self, method: str, url: str, data: dict = None):
        """Make HTTP request to secret_network_mcp VM"""
        import aiohttp
        
        async with aiohttp.ClientSession() as session:
            if method == "POST":
                async with session.post(url, json=data) as response:
                    return await response.json()
            elif method == "GET":
                async with session.get(url) as response:
                    return await response.json()
```

### **3. Environment Configuration**

#### **Update Environment Variables:**
```bash
# Add to F:\coding\secretGPT\.env.example

# Wallet Service Configuration
SECRET_MCP_WALLET_URL=http://localhost:8002
WALLET_SERVICE_ENABLED=true
WALLET_TIMEOUT=10000
```

### **4. secretgptee.com Vue.js Updates**

#### **Simplified Wallet Service (No Keplr SDK):**
```javascript
// src/services/walletService.js - SIMPLIFIED for proxy approach

class WalletService {
  constructor() {
    this.baseURL = '/api/v1/wallet'  // Calls secretGPT hub
    this.isConnected = false
    this.currentAddress = null
  }

  async connect(address) {
    try {
      const response = await fetch(`${this.baseURL}/connect`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ 
          address: address,
          chainId: "secret-4"
        })
      })
      
      const result = await response.json()
      
      if (result.success) {
        this.isConnected = true
        this.currentAddress = result.address
      }
      
      return result
    } catch (error) {
      return {
        success: false,
        error: error.message
      }
    }
  }

  async getBalance(address) {
    try {
      const response = await fetch(`${this.baseURL}/balance/${address}`)
      return await response.json()
    } catch (error) {
      return {
        success: false,
        error: error.message
      }
    }
  }

  async getStatus() {
    try {
      const response = await fetch(`${this.baseURL}/status`)
      return await response.json()
    } catch (error) {
      return {
        success: false,
        error: error.message
      }
    }
  }

  disconnect() {
    this.isConnected = false
    this.currentAddress = null
  }
}

export const walletService = new WalletService()
```

#### **Updated Vue.js Composable:**
```javascript
// src/composables/useWallet.js - SIMPLIFIED

import { ref, computed } from 'vue'
import { walletService } from '@/services/walletService'

export function useWallet() {
  const isConnected = ref(false)
  const isConnecting = ref(false)
  const address = ref('')
  const balance = ref('0')
  const error = ref('')

  const connect = async (userAddress) => {
    try {
      isConnecting.value = true
      error.value = ''

      // User manually provides address (demo approach)
      const result = await walletService.connect(userAddress)
      
      if (result.success) {
        isConnected.value = true
        address.value = result.address
        await refreshBalance()
      } else {
        error.value = result.error
      }
    } catch (err) {
      error.value = err.message
    } finally {
      isConnecting.value = false
    }
  }

  const refreshBalance = async () => {
    if (!address.value) return

    try {
      const result = await walletService.getBalance(address.value)
      if (result.success) {
        // Convert uscrt to SCRT
        const scrtBalance = (parseInt(result.balance) / 1000000).toFixed(6)
        balance.value = scrtBalance
      }
    } catch (err) {
      console.error('Failed to refresh balance:', err)
    }
  }

  const disconnect = () => {
    walletService.disconnect()
    isConnected.value = false
    address.value = ''
    balance.value = '0'
    error.value = ''
  }

  const formattedAddress = computed(() => {
    if (!address.value) return ''
    return `${address.value.slice(0, 8)}...${address.value.slice(-6)}`
  })

  const formattedBalance = computed(() => {
    return parseFloat(balance.value).toLocaleString(undefined, {
      minimumFractionDigits: 2,
      maximumFractionDigits: 6
    })
  })

  return {
    isConnected,
    isConnecting,
    address,
    balance,
    error,
    formattedAddress,
    formattedBalance,
    connect,
    disconnect,
    refreshBalance
  }
}
```

### **5. Updated Package Dependencies**

#### **Remove Keplr SDK from Vue.js:**
```json
// secretgptee package.json - REMOVE Keplr dependencies
{
  "dependencies": {
    "vue": "^3.3.4",
    "vue-router": "^4.2.4",
    "pinia": "^2.1.6",
    "axios": "^1.5.0",
    // REMOVED: "@keplr-wallet/provider-extension": "^0.12.29",
    // REMOVED: "@keplr-wallet/types": "^0.12.29",
    "@tailwindcss/forms": "^0.5.4",
    "@headlessui/vue": "^1.7.14",
    "@heroicons/vue": "^2.0.18"
  }
}
```

### **6. Updated User Experience**

#### **Demo Wallet Connection Flow:**
```vue
<!-- Simple address input for tech demo -->
<template>
  <div v-if="!isConnected" class="space-y-4">
    <div>
      <label class="block text-sm font-medium text-gray-300 mb-2">
        Enter Secret Network Address:
      </label>
      <input
        v-model="addressInput"
        type="text"
        placeholder="secret1..."
        class="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white"
      >
    </div>
    <button
      @click="connect(addressInput)"
      :disabled="!addressInput || isConnecting"
      class="w-full btn-primary"
    >
      {{ isConnecting ? 'Connecting...' : 'Connect Wallet' }}
    </button>
  </div>
  
  <!-- Connected state shows balance -->
  <div v-else class="space-y-2">
    <div class="text-green-400">
      ✅ Connected: {{ formattedAddress }}
    </div>
    <div class="text-gray-300">
      Balance: {{ formattedBalance }} SCRT
    </div>
    <button @click="disconnect" class="text-red-400 hover:text-red-300">
      Disconnect
    </button>
  </div>
</template>
```

## 🎯 **Summary of secretGPT Changes:**

1. ✅ **Add wallet proxy endpoints** to secretGPT hub
2. ✅ **Update MCP service** to call wallet endpoints
3. ✅ **Simplify Vue.js** - remove Keplr SDK, use proxy calls
4. ✅ **Update environment** configuration
5. ✅ **Demo UX** - manual address input for tech demo

**These changes prepare secretGPT to proxy wallet requests to secret_network_mcp VM where the actual Keplr SDK will live.**

Next step: Implement the Keplr SDK and wallet endpoints on secret_network_mcp VM.