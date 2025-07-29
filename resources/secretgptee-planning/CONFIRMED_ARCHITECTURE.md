# CONFIRMED Architecture - SecretGPTee.com Build Plan

**Last Updated:** July 28, 2025
**Status:** Based on Working Infrastructure

## ✅ CONFIRMED Working Architecture

### Current Setup:
```
secretGPT VM (2 vCPU, 4GB RAM)
├── attestAI.io (running - education focused)
├── secretGPT hub (Python/FastAPI)
└── [Future] secretgptee.com (Vue.js)

secretVM (separate VM)  
├── secret_network_mcp (running)
└── Connected to secretGPT hub

Communication Flow:
attestAI.io → secretGPT hub → secret_network_mcp (on secretVM)
```

### ✅ TESTED Working Features:
- **attestAI.io** can query Secret Network status ✅
- **attestAI.io** can get current block height ✅  
- **secret_network_mcp** is running on secretVM ✅
- **secretGPT hub** successfully routes to secret_network_mcp ✅

## secretgptee.com Implementation Strategy

### Architecture Decision:
Since attestAI.io already successfully connects to secret_network_mcp, we can:
1. **Reuse the existing communication path** (secretGPT hub → secretVM)
2. **Build Vue.js frontend** that talks to the same secretGPT hub
3. **Add new endpoints** to secretGPT hub specifically for secretgptee.com features

### Updated Communication Flow:
```
secretgptee.com (Vue.js) → secretGPT hub → secret_network_mcp (secretVM)
attestAI.io (existing) → secretGPT hub → secret_network_mcp (secretVM)
```

## Implementation Plan - REALISTIC

### Phase 1: Vue.js Frontend + Domain Setup
**Goal:** Get secretgptee.com running alongside attestAI.io

#### 1.1 Vue.js Project Structure
```
secretgptee/ (on secretGPT VM)
├── src/
│   ├── components/
│   │   ├── layout/ (ChatGPT-like layout)
│   │   ├── wallet/ (Keplr integration)
│   │   ├── chat/ (SecretAI interface)
│   │   └── attestations/ (VM status)
│   ├── services/
│   │   └── secretGPTHub.js  # → localhost:XXXX (secretGPT hub)
│   └── stores/
```

#### 1.2 Reverse Proxy Configuration
```nginx
# Existing (keep unchanged)
server {
    server_name attestai.io;
    location / {
        proxy_pass http://localhost:XXXX;  # Current secretGPT hub port
    }
}

# New
server {
    server_name secretgptee.com;
    location / {
        proxy_pass http://localhost:3001;  # Vue.js app
    }
    location /api/ {
        proxy_pass http://localhost:XXXX/api/;  # Same secretGPT hub
    }
}
```

### Phase 2: secretGPT Hub API Extensions
**Goal:** Add secretgptee.com specific endpoints to existing hub

#### 2.1 New Endpoints to Add to secretGPT Hub:
```python
# New endpoints for secretgptee.com
@app.get("/api/secretgptee/wallet/balance/{address}")
async def get_wallet_balance(address: str):
    # Use existing secret_network_mcp connection
    return await secret_mcp.query_balance(address)

@app.post("/api/secretgptee/chat/message")  
async def chat_with_secretai(message: dict):
    # Use existing Secret AI integration
    return await secret_ai.process_message(message)

@app.get("/api/secretgptee/attestations/status")
async def get_vm_attestations():
    # Use existing attestation hub
    return await attestation_hub.get_all_status()
```

#### 2.2 Vue.js Service Layer:
```javascript
class SecretGPTHubService {
  constructor() {
    this.baseURL = '/api/secretgptee'  # Proxied to secretGPT hub
  }
  
  async getWalletBalance(address) {
    return await fetch(`${this.baseURL}/wallet/balance/${address}`)
  }
  
  async sendChatMessage(message) {
    return await fetch(`${this.baseURL}/chat/message`, {
      method: 'POST',
      body: JSON.stringify({message})
    })
  }
  
  async getAttestations() {
    return await fetch(`${this.baseURL}/attestations/status`)
  }
}
```

### Phase 3: Message Signing Between VMs
**Goal:** Implement verified signing between secretGPT VM ↔ secretVM

#### Current: HTTP between secretGPT hub ↔ secret_network_mcp
#### Target: Signed messages between secretGPT hub ↔ secret_network_mcp

## Questions for You:

### 1. secretGPT Hub Details:
- **What port** is the secretGPT hub running on?
- **What's the current API structure?** Can you show me a few endpoints?
- **How does attestAI.io** currently call "what is the status of secret network"?

### 2. Current Communication Path:
- When you ask attestAI.io "what is the current block height", what's the **exact flow**?
- Does attestAI.io → secretGPT hub → secret_network_mcp work via HTTP?
- Are there existing API endpoints we can examine?

### 3. Domain/Deployment:
- **How is attestAI.io currently deployed?** (nginx config, ports, etc.)
- **What's the VM setup?** Are both running on cloud providers?

## Next Steps:

1. **Examine secretGPT hub code** to understand current API structure
2. **Test the exact endpoints** that attestAI.io uses for Secret Network queries  
3. **Set up Vue.js project** that calls the same endpoints
4. **Add domain routing** for secretgptee.com

This approach leverages your **working infrastructure** instead of building from scratch. We just need to:
- Add a Vue.js frontend
- Extend the secretGPT hub with secretgptee.com specific endpoints  
- Reuse the existing secret_network_mcp connection

**Can you help me understand the current secretGPT hub API structure?**
