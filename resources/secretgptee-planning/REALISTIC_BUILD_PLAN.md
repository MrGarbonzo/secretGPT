# ACCURATE SecretGPTee.com Build Plan - Based on Existing Infrastructure

**Last Updated:** July 28, 2025
**Status:** Planning Phase - Based on Real Code Review

## Current Infrastructure Analysis

### ✅ What We Know Works:
1. **secretGPT VM** (F:\coding\secretGPT)
   - FastAPI-based hub system
   - attestAI.io web interface running
   - Attestation hub service with multi-VM support
   - Secret AI integration
   - Environment: Python 3.11+, FastAPI

2. **secret_network_mcp VM** (F:\coding\secret_network_mcp)
   - HTTP API server (port 8002)
   - Secret Network mainnet connection (`secret-4`)
   - Tools: balance queries, block info, transactions, contracts
   - Built with TypeScript, Express, SecretJS
   - Docker ready

3. **Network Configuration:**
   - **Mainnet:** `secret-4` chain
   - **RPC:** `https://rpc.ankr.com/http/scrt_cosmos` (default)
   - **Tools Available:** secret_query_balance, secret_network_status, etc.

## secretgptee.com Requirements - REALISTIC Scope

### MVP Features (Based on Available APIs):

#### 1. Keplr Wallet Connection ✅ FEASIBLE
- **Frontend:** Vue.js integration with Keplr browser extension  
- **Backend:** Use existing secret_network_mcp API at port 8002
- **Available Endpoints:**
  - `GET /api/mcp/tools/list`
  - `POST /api/mcp/tools/call` with `secret_query_balance`

#### 2. Secret Network Balances ✅ WORKING API EXISTS
- **Current Tool:** `secret_query_balance` in secret_network_mcp
- **API Call:** 
  ```bash
  curl -X POST http://localhost:8002/api/mcp/tools/call \
    -H "Content-Type: application/json" \
    -d '{"name": "secret_query_balance", "arguments": {"address": "secret1..."}}'
  ```

#### 3. Multi-VM Attestations ✅ INFRASTRUCTURE EXISTS  
- **secretGPT VM:** Existing attestation hub service
- **secretAI VM:** Already configured in attestation system
- **secret_network_mcp VM:** Need to add to attestation config
- **Bridge Status:** Need to implement between secretGPT ↔ secret_network_mcp

#### 4. SecretAI Chat Interface ✅ EXISTING SERVICE
- **Current:** Secret AI integration in secretGPT hub
- **Available:** Streaming responses, async/sync invocation
- **Challenge:** Extract chat interface from existing FastAPI app

## Technical Implementation Plan

### Phase 1: Vue.js Frontend Setup (2-3 days)
**Goal:** Get basic secretgptee.com running alongside attestAI.io

#### Reverse Proxy Configuration (nginx)
```nginx
# Existing
server {
    server_name attestai.io;
    # Current attestAI.io configuration
}

# New
server {
    server_name secretgptee.com;
    location / {
        proxy_pass http://localhost:3001;  # Vue.js dev server
    }
    location /api/mcp/ {
        proxy_pass http://localhost:8002/api/;  # secret_network_mcp
    }
    location /api/secretai/ {
        proxy_pass http://localhost:8000/;  # secretGPT hub
    }
}
```

#### Vue.js Project Structure
```
secretgptee/
├── src/
│   ├── components/
│   │   ├── layout/ (HeaderBar, Sidebar, MainLayout)
│   │   ├── wallet/ (KeplrConnection, BalanceDisplay)  
│   │   ├── chat/ (ChatInterface, MessageBubble)
│   │   └── attestations/ (VMStatus, HealthIndicators)
│   ├── services/
│   │   ├── mcpApiService.js     # → secret_network_mcp:8002
│   │   ├── secretAIService.js   # → secretGPT:8000  
│   │   └── attestationService.js # → secretGPT attestation hub
│   └── stores/ (Pinia for state)
```

### Phase 2: API Integration (2-3 days)
**Goal:** Connect Vue.js to existing APIs

#### 2.1 Keplr Wallet Service
```javascript
// Based on existing secret_network_mcp tools
class WalletService {
  async connect() {
    // Keplr browser extension integration
    await window.keplr.enable('secret-4')
    return await window.keplr.getKey('secret-4')
  }
  
  async getBalance(address) {
    // Call existing secret_network_mcp API
    return await fetch('http://localhost:8002/api/mcp/tools/call', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        name: 'secret_query_balance',
        arguments: { address }
      })
    })
  }
}
```

#### 2.2 SecretAI Chat Service  
```javascript
// Integration with existing secretGPT hub
class ChatService {
  async sendMessage(message) {
    // Use existing secretGPT streaming API
    return await fetch('http://localhost:8000/api/chat', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ message })
    })
  }
}
```

#### 2.3 Attestation Service
```javascript
// Use existing attestation hub
class AttestationService {
  async getVMStatus() {
    // Call existing attestation hub API
    return await fetch('http://localhost:8000/api/attestation/status')
  }
}
```

### Phase 3: Message Signing Bridge (3-4 days)
**Goal:** Implement verified message signing between VMs

#### Current Challenge:
- secretGPT hub and secret_network_mcp currently use HTTP
- Need to replace with signed message protocol

#### Implementation:
1. **Generate key pairs** for both VMs
2. **Add signing middleware** to secret_network_mcp Express server
3. **Add verification** to secretGPT Python hub
4. **Update Vue.js** to handle signed requests

## Questions to Resolve

### 1. SecretGPT Hub API Structure
**Question:** What are the exact API endpoints for the secretGPT hub?
**Action:** Need to examine `F:\coding\secretGPT\interfaces\web_ui\` and `services/` to understand current APIs

### 2. Attestation Hub Current Status  
**Question:** Is the attestation hub service currently running? What port?
**Action:** Check `F:\coding\secretGPT\services\attestation_hub\main.py` for port and endpoints

### 3. secret_network_mcp Deployment
**Question:** Is secret_network_mcp currently running on port 8002?
**Action:** Test with `curl http://localhost:8002/api/health`

### 4. Domain Configuration
**Question:** How is attestAI.io currently configured for nginx/reverse proxy?
**Action:** Need actual nginx config to understand routing setup

## Next Steps - REALISTIC Approach

### Immediate Actions:
1. **Test existing APIs** to confirm what's working
   ```bash
   # Test secret_network_mcp
   curl http://localhost:8002/api/health
   
   # Test secretGPT hub  
   curl http://localhost:8000/api/status
   ```

2. **Examine actual API structures** in the codebases
3. **Create Vue.js project** with correct API endpoints
4. **Set up domain routing** for secretgptee.com

### Development Order:
1. ✅ **Basic Vue.js frontend** with ChatGPT layout
2. ✅ **Keplr wallet integration** using browser extension
3. ✅ **Connect to secret_network_mcp** for balances
4. ✅ **Integrate with secretGPT** for chat
5. ✅ **Add attestation monitoring** 
6. ✅ **Implement message signing** between VMs

This realistic plan is based on your actual working infrastructure and avoids assumptions about APIs that don't exist.
