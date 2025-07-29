# FINAL ACCURATE Build Plan - SecretGPTee.com

**Last Updated:** July 28, 2025
**Status:** Based on Complete Code Review

## ✅ CONFIRMED Current Working Setup

### Architecture:
```
secretGPT VM (2 vCPU, 4GB RAM) - Port 8000
├── attestAI.io → FastAPI Web UI → secretGPT Hub Router
├── secretGPT Hub Router (Python/FastAPI)
│   ├── Secret AI Service  
│   ├── MCP Service → HTTP calls to secretVM
│   └── Attestation Service
└── [NEW] secretgptee.com (Vue.js) → Same Hub Router

secretVM (separate VM) - Port 8002  
└── secret_network_mcp HTTP Server (TypeScript/Express)
    ├── Secret Network mainnet (secret-4)
    ├── Available Tools: secret_query_balance, secret_network_status
    └── API: POST /api/mcp/tools/call
```

### ✅ TESTED Working API Endpoints on Port 8000:

#### Chat APIs (Ready to Use):
- `POST /api/v1/chat` - Send message to Secret AI
- `POST /api/v1/chat/stream` - Streaming chat with Server-Sent Events
- `GET /api/v1/models` - Get available AI models

#### Secret Network APIs (via MCP):  
- `GET /api/v1/mcp/tools` - List available Secret Network tools
- `POST /api/v1/mcp/tools/{tool_name}/execute` - Execute Secret Network tools
- `GET /api/v1/mcp/status` - Secret Network MCP status

#### Attestation APIs (Ready to Use):
- `GET /api/v1/attestation/self` - secretGPT VM attestation 
- `GET /api/v1/attestation/secret-ai` - Secret AI VM attestation
- `GET /api/v1/status` - Overall system status with attestation

#### System APIs:
- `GET /health` - Health check with hub status
- `GET /api/v1/debug/version` - Debug and feature info

## secretgptee.com Implementation - REALISTIC

### Phase 1: Vue.js Frontend (2 days)
**Goal:** Create ChatGPT-like interface using existing APIs

#### 1.1 Vue.js Project Setup
```bash
# On secretGPT VM
cd /var/www/
npm create vue@latest secretgptee
cd secretgptee
npm install axios @headlessui/vue @heroicons/vue tailwindcss
```

#### 1.2 Domain Configuration (nginx)
```nginx
# Existing - Keep unchanged
server {
    listen 80;
    server_name attestai.io;
    location / {
        proxy_pass http://localhost:8000;  # secretGPT hub
    }
}

# New - Add this
server {
    listen 80; 
    server_name secretgptee.com;
    
    # Vue.js frontend
    location / {
        proxy_pass http://localhost:3001;  # Vue dev server
    }
    
    # API calls to same secretGPT hub
    location /api/ {
        proxy_pass http://localhost:8000/api/;  
    }
}
```

#### 1.3 Vue.js Service Layer (Use Existing APIs)
```javascript
// src/services/secretGPTApi.js
class SecretGPTAPI {
  constructor() {
    this.baseURL = '/api/v1'  // Proxied to port 8000
  }
  
  // Chat with Secret AI (EXISTING ENDPOINT)
  async sendMessage(message, options = {}) {
    return await fetch(`${this.baseURL}/chat`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        message,
        temperature: options.temperature || 0.7,
        system_prompt: options.system_prompt || "You are a helpful assistant."
      })
    })
  }
  
  // Get wallet balance via Secret Network MCP (EXISTING)
  async getWalletBalance(address) {
    return await fetch(`${this.baseURL}/mcp/tools/secret_query_balance/execute`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        arguments: { address }
      })
    })
  }
  
  // Get Secret Network status (EXISTING)
  async getSecretNetworkStatus() {
    return await fetch(`${this.baseURL}/mcp/tools/secret_network_status/execute`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        arguments: {}
      })
    })
  }
  
  // Get VM attestations (EXISTING) 
  async getAttestations() {
    const [selfAttest, secretAiAttest, systemStatus] = await Promise.all([
      fetch(`${this.baseURL}/attestation/self`),
      fetch(`${this.baseURL}/attestation/secret-ai`),
      fetch(`${this.baseURL}/status`)
    ])
    
    return {
      secretGPT: await selfAttest.json(),
      secretAI: await secretAiAttest.json(), 
      system: await systemStatus.json()
    }
  }
}
```

### Phase 2: MVP Features Implementation (2-3 days)

#### 2.1 Keplr Wallet Integration
```javascript
// src/composables/useWallet.js
export function useWallet() {
  const isConnected = ref(false)
  const address = ref('')
  const balance = ref('')
  
  const connect = async () => {
    if (!window.keplr) throw new Error('Keplr not found')
    
    await window.keplr.enable('secret-4')
    const key = await window.keplr.getKey('secret-4')
    
    isConnected.value = true
    address.value = key.bech32Address
    
    // Get balance from existing API
    await refreshBalance()
  }
  
  const refreshBalance = async () => {
    if (!address.value) return
    
    const api = new SecretGPTAPI()
    const result = await api.getWalletBalance(address.value)
    
    if (result.success) {
      balance.value = result.result.balance
    }
  }
  
  return { isConnected, address, balance, connect, refreshBalance }
}
```

#### 2.2 Chat Interface (Using Existing Stream API)
```javascript
// src/composables/useChat.js
export function useChat() {
  const messages = ref([])
  const isTyping = ref(false)
  
  const sendMessage = async (content) => {
    // Add user message
    messages.value.push({
      role: 'user',
      content,
      timestamp: new Date()
    })
    
    isTyping.value = true
    
    try {
      // Use existing streaming API
      const response = await fetch('/api/v1/chat/stream', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ message: content })
      })
      
      const reader = response.body.getReader()
      let aiMessage = { role: 'ai', content: '', timestamp: new Date() }
      messages.value.push(aiMessage)
      
      while (true) {
        const {done, value} = await reader.read()
        if (done) break
        
        const chunk = new TextDecoder().decode(value)
        const lines = chunk.split('\n')
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = JSON.parse(line.slice(6))
            if (data.chunk?.data) {
              aiMessage.content += data.chunk.data
            }
          }
        }
      }
    } finally {
      isTyping.value = false
    }
  }
  
  return { messages, isTyping, sendMessage }
}
```

#### 2.3 Attestation Monitoring
```javascript
// src/composables/useAttestations.js 
export function useAttestations() {
  const status = ref({
    secretGPT: { status: 'unknown' },
    secretAI: { status: 'unknown' },
    secret_network_mcp: { status: 'unknown' },
    bridge: { status: 'unknown' }
  })
  
  const refresh = async () => {
    const api = new SecretGPTAPI()
    const attestations = await api.getAttestations()
    
    status.value = {
      secretGPT: { 
        status: attestations.secretGPT.success ? 'healthy' : 'error',
        details: attestations.secretGPT
      },
      secretAI: {
        status: attestations.secretAI.success ? 'healthy' : 'error', 
        details: attestations.secretAI
      },
      secret_network_mcp: {
        status: attestations.system.mcp_service ? 'healthy' : 'error',
        details: attestations.system
      },
      bridge: {
        status: attestations.system.hub_status?.components?.mcp_service ? 'healthy' : 'error'
      }
    }
  }
  
  // Auto-refresh every 30 seconds
  onMounted(() => {
    refresh()
    setInterval(refresh, 30000)
  })
  
  return { status, refresh }
}
```

### Phase 3: Message Signing Implementation (3-4 days)

#### Current State: HTTP between secretGPT Hub ↔ secret_network_mcp
#### Goal: Add signed message verification

#### 3.1 Add Signing to secretGPT Hub (Python)
```python
# In secretGPT hub - add message signing to MCP calls
import hmac
import hashlib
import time
import json

class MessageSigner:
    def __init__(self, private_key):
        self.private_key = private_key
    
    def sign_message(self, payload):
        timestamp = str(int(time.time()))
        nonce = os.urandom(16).hex()
        
        message = f"{timestamp}.{nonce}.{json.dumps(payload)}"
        signature = hmac.new(
            self.private_key.encode(),
            message.encode(), 
            hashlib.sha256
        ).hexdigest()
        
        return {
            "timestamp": timestamp,
            "nonce": nonce, 
            "payload": payload,
            "signature": signature
        }
```

#### 3.2 Add Verification to secret_network_mcp (TypeScript)
```typescript
// In secret_network_mcp - add verification middleware
class MessageVerifier {
  constructor(private publicKey: string) {}
  
  verifyMessage(signedMessage: any): boolean {
    const { timestamp, nonce, payload, signature } = signedMessage
    
    // Check timestamp (within 5 minutes)
    const now = Math.floor(Date.now() / 1000)
    if (Math.abs(now - parseInt(timestamp)) > 300) {
      return false
    }
    
    // Verify signature
    const message = `${timestamp}.${nonce}.${JSON.stringify(payload)}`
    const expectedSig = crypto
      .createHmac('sha256', this.publicKey)
      .update(message)
      .digest('hex')
    
    return expectedSig === signature
  }
}
```

## Development Timeline

### Week 1: Frontend Foundation
- **Day 1-2:** Vue.js setup + ChatGPT layout + domain routing
- **Day 3:** Connect to existing chat APIs
- **Day 4:** Keplr wallet integration  
- **Day 5:** Attestation monitoring UI

### Week 2: Integration & Security
- **Day 1-2:** Secret Network balance integration
- **Day 3-4:** Message signing implementation
- **Day 5:** Testing and bug fixes

## Ready to Start?

This plan uses your **existing, working APIs** without making assumptions. All the endpoints I've referenced are already implemented in your secretGPT hub.

**Next steps:**
1. Set up Vue.js project on secretGPT VM
2. Configure nginx for secretgptee.com domain
3. Build components that call existing `/api/v1/*` endpoints
4. Test against your working attestAI.io → secretGPT hub → secret_network_mcp flow

**Should we start with the Vue.js setup and domain configuration?**
