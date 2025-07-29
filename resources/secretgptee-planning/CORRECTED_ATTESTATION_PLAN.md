# CORRECTED Attestation Plan - SecretGPTee.com

**Last Updated:** July 28, 2025  
**Status:** Accurate VM Architecture

## ✅ **CORRECTED VM Understanding:**

### **Our VMs (We Control):**
1. **secretGPT VM** - Runs attestAI.io, secretGPT hub, will run secretgptee.com
2. **secret_network_mcp VM** - Runs Secret Network MCP service

### **External Service (We Don't Control):**
- **secretAI** - Public Secret Network AI service (not our VM)

### **MVP Attestation Scope:**
- ✅ **secretGPT VM** - Show our main VM attestation  
- ✅ **secret_network_mcp VM** - Show our MCP VM attestation
- ❌ **NOT secretAI** - It's external, not our VM to attest
- ❌ **NOT bridge attestation** - That's for later phase

## **Simple MVP Attestation Plan:**

### **Current Working (attestAI.io):**
```javascript
fetch('/api/v1/attestation/self')  // ✅ secretGPT VM attestation
```

### **What secretgptee.com Needs:**
```javascript
fetch('/api/v1/attestation/self')        // ✅ secretGPT VM  
fetch('/api/v1/attestation/secret-mcp')  // ➕ Add secret_network_mcp VM
```

### **Updated Vue.js Implementation:**

#### **Simple Attestation Service:**
```javascript
// src/services/attestationService.js
class AttestationService {
  constructor() {
    this.API_BASE = '/api/v1'
  }

  async getSecretGPTAttestation() {
    const response = await fetch(`${this.API_BASE}/attestation/self`)
    return await response.json()
  }

  async getSecretMCPAttestation() {
    const response = await fetch(`${this.API_BASE}/attestation/secret-mcp`)
    return await response.json()
  }

  // Simple 2-VM status for MVP
  async getAllAttestations() {
    const [secretGPT, secretMCP] = await Promise.all([
      this.getSecretGPTAttestation(),
      this.getSecretMCPAttestation()
    ])

    return {
      secretGPT: {
        name: "SecretGPT VM",
        status: secretGPT.success ? 'healthy' : 'error',
        details: secretGPT
      },
      secret_network_mcp: {
        name: "Secret Network MCP VM", 
        status: secretMCP.success ? 'healthy' : 'error',
        details: secretMCP
      }
    }
  }
}
```

#### **Simple Vue.js Component:**
```vue
<!-- src/components/attestations/AttestationPanel.vue -->
<template>
  <div class="bg-gray-800 border border-gray-700 rounded-lg p-4">
    <h3 class="text-lg font-semibold text-white mb-4">
      <ShieldCheckIcon class="w-5 h-5 inline mr-2" />
      VM Status
    </h3>
    
    <!-- 2 VM Status -->
    <div class="space-y-3">
      <VMStatusCard 
        name="SecretGPT VM"
        description="Main hub and web interface"
        :status="attestations.secretGPT.status"
        :details="attestations.secretGPT.details"
      />
      <VMStatusCard 
        name="Secret Network MCP VM" 
        description="Secret Network tools and wallet services"
        :status="attestations.secret_network_mcp.status"
        :details="attestations.secret_network_mcp.details"
      />
    </div>

    <button 
      @click="refreshAttestations"
      class="mt-4 w-full btn-primary text-sm"
      :disabled="isLoading"
    >
      <ArrowPathIcon class="w-4 h-4 mr-2" />
      {{ isLoading ? 'Refreshing...' : 'Refresh Status' }}
    </button>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ShieldCheckIcon, ArrowPathIcon } from '@heroicons/vue/24/outline'
import { AttestationService } from '@/services/attestationService'
import VMStatusCard from './VMStatusCard.vue'

const attestations = ref({
  secretGPT: { status: 'unknown' },
  secret_network_mcp: { status: 'unknown' }
})

const isLoading = ref(false)
const attestationService = new AttestationService()

const refreshAttestations = async () => {
  isLoading.value = true
  try {
    attestations.value = await attestationService.getAllAttestations()
  } catch (error) {
    console.error('Failed to refresh attestations:', error)
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  refreshAttestations()
  setInterval(refreshAttestations, 30000)
})
</script>
```

#### **Simple Status Card Component:**
```vue
<!-- src/components/attestations/VMStatusCard.vue -->
<template>
  <div class="flex items-center justify-between p-3 bg-gray-700 rounded-lg">
    <div>
      <h4 class="font-medium text-white">{{ name }}</h4>
      <p class="text-sm text-gray-400">{{ description }}</p>
    </div>
    
    <div class="flex items-center space-x-2">
      <div class="flex items-center space-x-1">
        <div 
          class="w-2 h-2 rounded-full"
          :class="{
            'bg-green-400': status === 'healthy',
            'bg-red-400': status === 'error', 
            'bg-gray-400': status === 'unknown'
          }"
        ></div>
        <span 
          class="text-sm font-medium"
          :class="{
            'text-green-400': status === 'healthy',
            'text-red-400': status === 'error',
            'text-gray-400': status === 'unknown'
          }"
        >
          {{ statusText }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  name: String,
  description: String, 
  status: String,
  details: Object
})

const statusText = computed(() => {
  switch (props.status) {
    case 'healthy': return 'Healthy'
    case 'error': return 'Error'
    default: return 'Unknown'
  }
})
</script>
```

## **Implementation Steps:**

### **Step 1: Add secret_network_mcp to Attestation Hub (1 day)**
- Add endpoint `/api/v1/attestation/secret-mcp` to secretGPT hub
- Configure attestation hub to monitor secret_network_mcp VM

### **Step 2: Create Vue.js Components (1 day)** 
- Copy pattern from attestAI.io 
- Create 2-VM status display
- Show secretGPT VM + secret_network_mcp VM status

## **Future Phase (Later Project):**
- ✅ **Verified message signing** between secretGPT ↔ secret_network_mcp
- ✅ **Bridge attestation** showing communication security
- ✅ **Cryptographic proof** of message integrity

## **MVP Result:**
Simple, clean 2-VM status display showing the health of our actual infrastructure without overcomplicating with external services or future features.

**Much cleaner scope - thanks for the correction!**