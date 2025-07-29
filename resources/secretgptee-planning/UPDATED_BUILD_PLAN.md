# UPDATED Build Plan - SecretGPTee.com

**Last Updated:** July 28, 2025
**Status:** Reflecting Latest Decisions and Corrections

## 🔄 **Key Changes Since Original Plan:**

### **1. Keplr Integration Corrected:**
- ❌ **Old:** Direct `window.keplr` usage
- ✅ **New:** Official Keplr SDK with `@keplr-wallet/provider-extension` and `KeplrFallback`

### **2. Attestation Scope Corrected:**
- ❌ **Old:** 4 VMs (secretGPT, secretAI, secret_network_mcp, bridge)
- ✅ **New:** 2 VMs only (secretGPT, secret_network_mcp) - secretAI is external service

### **3. VM Architecture Clarified:**
- ✅ **Our VMs:** secretGPT VM + secret_network_mcp VM
- ✅ **External:** secretAI (public Secret Network service)
- ✅ **Bridge attestation:** Future phase, not MVP

## ✅ **UPDATED MVP Features:**

1. **Keplr Wallet Connection** - Using official SDK with KeplrFallback
2. **Secret Network Balances** - Via existing MCP API
3. **SecretAI Chat Interface** - Via existing chat API  
4. **2-VM Attestation Status** - secretGPT + secret_network_mcp only

## 📋 **CORRECTED Implementation Plan:**

### **Phase 1: Vue.js Setup (2 days)**

#### **Updated Dependencies:**
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

#### **Correct Keplr Service:**
```javascript
// src/services/keplrService.js - CORRECTED
import { KeplrFallback } from "@keplr-wallet/provider-extension";

class KeplrWalletService {
  getKeplr() {
    if (typeof window === "undefined") return undefined;
    
    if ((window as any).keplr) {
      return new KeplrFallback(() => {
        this.showKeplrWarning();
      });
    }
    return undefined;
  }

  async connect() {
    this.keplr = this.getKeplr();
    if (!this.keplr) {
      throw new Error("Keplr wallet not found");
    }
    
    await this.keplr.enable("secret-4");
    const key = await this.keplr.getKey("secret-4");
    
    return {
      success: true,
      address: key.bech32Address,
      name: key.name
    };
  }
}
```

### **Phase 2: API Integration (2 days)**

#### **Unchanged - Using Existing APIs:**
- ✅ `POST /api/v1/chat` - SecretAI chat
- ✅ `POST /api/v1/mcp/tools/secret_query_balance/execute` - Balance queries
- ✅ `GET /api/v1/attestation/self` - secretGPT VM attestation

#### **Need to Add:**
- ➕ `GET /api/v1/attestation/secret-mcp` - secret_network_mcp VM attestation

### **Phase 3: Corrected Attestation (1 day)**

#### **Simple 2-VM Status:**
```javascript
// src/services/attestationService.js - CORRECTED
class AttestationService {
  async getAllAttestations() {
    const [secretGPT, secretMCP] = await Promise.all([
      fetch('/api/v1/attestation/self'),
      fetch('/api/v1/attestation/secret-mcp')
    ])

    return {
      secretGPT: {
        name: "SecretGPT VM",
        status: secretGPT.success ? 'healthy' : 'error'
      },
      secret_network_mcp: {
        name: "Secret Network MCP VM", 
        status: secretMCP.success ? 'healthy' : 'error'
      }
    }
  }
}
```

### **Phase 4: Future (Not MVP):**
- ✅ Verified message signing between secretGPT ↔ secret_network_mcp  
- ✅ Bridge attestation display
- ✅ Advanced transaction features

## 🎯 **Updated Success Criteria:**

### **When MVP Complete:**
1. ✅ **secretgptee.com loads** with ChatGPT-like interface
2. ✅ **Keplr connects** using official SDK (secure, reliable)
3. ✅ **Shows SCRT balance** from user's wallet
4. ✅ **Chat with SecretAI** about wallet/blockchain questions
5. ✅ **2-VM status display** showing our actual infrastructure health
6. ✅ **Demo ready** - complete Secret Network showcase

### **Not in MVP (Future Phase):**
- ❌ Bridge attestation verification
- ❌ Verified message signing
- ❌ Transaction signing
- ❌ Advanced wallet features

## 📊 **Timeline Updated:**

- **Days 1-2:** Vue.js setup + correct Keplr SDK integration
- **Days 3-4:** Chat interface + balance integration  
- **Day 5:** Simple 2-VM attestation display
- **Day 6:** Testing, polish, demo preparation

## 🚨 **Critical Corrections Made:**

1. **Keplr SDK:** Now uses proper `@keplr-wallet/provider-extension` approach
2. **Attestation Scope:** Reduced to 2 VMs we actually control
3. **Architecture Clarity:** secretAI is external service, not our VM
4. **Future Features:** Bridge attestation moved to future phase

**This plan now accurately reflects our decisions and uses correct implementations!**