# Vue.js Implementation Guide - SecretGPTee.com

## Project Setup & Architecture

### Initial Setup Commands
```bash
# Create Vue.js project with Vite
npm create vue@latest secretgptee
cd secretgptee

# Select options:
# ✅ TypeScript: No (keep it simple for demo)
# ✅ JSX: No
# ✅ Vue Router: Yes
# ✅ Pinia: Yes (state management)
# ✅ Vitest: No (skip for MVP)
# ✅ ESLint: Yes
# ✅ Prettier: Yes

# Install additional dependencies
npm install @tailwindcss/ui
npm install @headlessui/vue
npm install @heroicons/vue
npm install axios
npm install @keplr-wallet/cosmos
```

### Project Structure
```
secretgptee/
├── public/
│   ├── favicon.ico
│   └── index.html
├── src/
│   ├── assets/
│   │   ├── css/
│   │   │   ├── tailwind.css
│   │   │   └── variables.css
│   │   └── icons/
│   ├── components/
│   │   ├── layout/
│   │   │   ├── HeaderBar.vue          # Top navigation
│   │   │   ├── Sidebar.vue            # Left sidebar
│   │   │   ├── MainLayout.vue         # Overall layout wrapper
│   │   │   └── MobileMenu.vue         # Mobile navigation
│   │   ├── wallet/
│   │   │   ├── WalletConnection.vue   # Connect/disconnect UI
│   │   │   ├── WalletStatus.vue       # Connection indicator
│   │   │   ├── BalanceDisplay.vue     # Token balances
│   │   │   └── WalletModal.vue        # Full wallet details
│   │   ├── chat/
│   │   │   ├── ChatInterface.vue      # Main chat container
│   │   │   ├── MessageBubble.vue      # Individual messages
│   │   │   ├── MessageInput.vue       # Input field + send
│   │   │   ├── ChatHistory.vue        # Conversation list
│   │   │   └── TypingIndicator.vue    # AI typing animation
│   │   ├── attestations/
│   │   │   ├── AttestationPanel.vue   # Status overview
│   │   │   ├── VMStatus.vue           # Individual VM status
│   │   │   ├── BridgeStatus.vue       # Bridge health
│   │   │   └── StatusIndicator.vue    # Reusable status icon
│   │   └── common/
│   │       ├── LoadingSpinner.vue
│   │       ├── ErrorMessage.vue
│   │       ├── Modal.vue
│   │       └── Button.vue
│   ├── stores/
│   │   ├── wallet.js                  # Wallet state (Pinia)
│   │   ├── chat.js                    # Chat state
│   │   ├── attestations.js            # VM status state
│   │   └── ui.js                      # UI state (sidebar, modals)
│   ├── services/
│   │   ├── walletService.js           # Keplr integration
│   │   ├── apiService.js              # Cross-VM API calls
│   │   ├── chatService.js             # SecretAI communication
│   │   └── attestationService.js      # VM health monitoring
│   ├── composables/
│   │   ├── useWallet.js               # Wallet composable
│   │   ├── useChat.js                 # Chat composable
│   │   └── useAttestations.js         # Status monitoring
│   ├── utils/
│   │   ├── formatters.js              # Currency, date formatting
│   │   ├── constants.js               # App constants
│   │   └── validators.js              # Input validation
│   ├── views/
│   │   ├── HomeView.vue               # Main chat interface
│   │   ├── WalletView.vue             # Wallet management (optional)
│   │   └── SettingsView.vue           # App settings (optional)
│   ├── router/
│   │   └── index.js                   # Vue Router config
│   ├── App.vue                        # Root component
│   └── main.js                        # App entry point
├── tailwind.config.js
├── vite.config.js
└── package.json
```

## Core Component Implementation

### 1. Main Layout Structure

#### `src/App.vue`
```vue
<template>
  <div id="app" class="min-h-screen bg-gray-900 text-white">
    <MainLayout />
  </div>
</template>

<script setup>
import MainLayout from '@/components/layout/MainLayout.vue'
import { onMounted } from 'vue'
import { useWalletStore } from '@/stores/wallet'
import { useAttestationStore } from '@/stores/attestations'

const walletStore = useWalletStore()
const attestationStore = useAttestationStore()

onMounted(() => {
  // Initialize app state
  walletStore.checkWalletConnection()
  attestationStore.startHealthMonitoring()
})
</script>
```

#### `src/components/layout/MainLayout.vue`
```vue
<template>
  <div class="flex h-screen overflow-hidden">
    <!-- Sidebar -->
    <Sidebar 
      :isOpen="uiStore.sidebarOpen" 
      @close="uiStore.toggleSidebar()"
      class="hidden md:block"
    />
    
    <!-- Mobile sidebar overlay -->
    <div 
      v-if="uiStore.sidebarOpen" 
      class="fixed inset-0 z-40 md:hidden"
      @click="uiStore.toggleSidebar()"
    >
      <Sidebar :isOpen="true" @close="uiStore.toggleSidebar()" />
    </div>

    <!-- Main content -->
    <div class="flex-1 flex flex-col overflow-hidden">
      <!-- Header -->
      <HeaderBar @toggle-sidebar="uiStore.toggleSidebar()" />
      
      <!-- Chat area -->
      <main class="flex-1 overflow-hidden">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup>
import HeaderBar from './HeaderBar.vue'
import Sidebar from './Sidebar.vue'
import { useUIStore } from '@/stores/ui'

const uiStore = useUIStore()
</script>
```

### 2. State Management (Pinia Stores)

#### `src/stores/wallet.js`
```javascript
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { walletService } from '@/services/walletService'

export const useWalletStore = defineStore('wallet', () => {
  // State
  const isConnected = ref(false)
  const isConnecting = ref(false)
  const address = ref('')
  const balances = ref({})
  const error = ref('')

  // Getters
  const formattedAddress = computed(() => {
    if (!address.value) return ''
    return `${address.value.slice(0, 6)}...${address.value.slice(-4)}`
  })

  const totalBalance = computed(() => {
    return balances.value.scrt || '0'
  })

  // Actions
  async function connectWallet() {
    try {
      isConnecting.value = true
      error.value = ''
      
      const result = await walletService.connect()
      if (result.success) {
        isConnected.value = true
        address.value = result.address
        await fetchBalances()
      } else {
        error.value = result.error
      }
    } catch (err) {
      error.value = err.message
    } finally {
      isConnecting.value = false
    }
  }

  async function disconnectWallet() {
    isConnected.value = false
    address.value = ''
    balances.value = {}
    error.value = ''
  }

  async function fetchBalances() {
    if (!address.value) return
    
    try {
      const result = await walletService.getBalances(address.value)
      balances.value = result
    } catch (err) {
      console.error('Failed to fetch balances:', err)
    }
  }

  function checkWalletConnection() {
    // Check if wallet was previously connected
    walletService.checkConnection().then(result => {
      if (result.connected) {
        isConnected.value = true
        address.value = result.address
        fetchBalances()
      }
    })
  }

  return {
    // State
    isConnected,
    isConnecting,
    address,
    balances,
    error,
    // Getters
    formattedAddress,
    totalBalance,
    // Actions
    connectWallet,
    disconnectWallet,
    fetchBalances,
    checkWalletConnection
  }
})
```

#### `src/stores/chat.js`
```javascript
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { chatService } from '@/services/chatService'

export const useChatStore = defineStore('chat', () => {
  // State
  const messages = ref([])
  const isTyping = ref(false)
  const currentConversation = ref(null)
  const conversationHistory = ref([])

  // Actions
  async function sendMessage(content) {
    if (!content.trim()) return

    // Add user message
    const userMessage = {
      id: Date.now(),
      content,
      sender: 'user',
      timestamp: new Date()
    }
    messages.value.push(userMessage)

    try {
      isTyping.value = true
      
      // Send to SecretAI
      const response = await chatService.sendMessage(content)
      
      // Add AI response
      const aiMessage = {
        id: Date.now() + 1,
        content: response.content,
        sender: 'ai',
        timestamp: new Date()
      }
      messages.value.push(aiMessage)
      
    } catch (error) {
      // Add error message
      const errorMessage = {
        id: Date.now() + 1,
        content: 'Sorry, I encountered an error. Please try again.',
        sender: 'system',
        type: 'error',
        timestamp: new Date()
      }
      messages.value.push(errorMessage)
    } finally {
      isTyping.value = false
    }
  }

  function startNewConversation() {
    if (messages.value.length > 0) {
      // Save current conversation
      conversationHistory.value.unshift({
        id: Date.now(),
        title: messages.value[0]?.content.slice(0, 50) + '...',
        messages: [...messages.value],
        timestamp: new Date()
      })
    }
    
    // Clear current conversation
    messages.value = []
    currentConversation.value = null
  }

  function loadConversation(conversationId) {
    const conversation = conversationHistory.value.find(c => c.id === conversationId)
    if (conversation) {
      messages.value = [...conversation.messages]
      currentConversation.value = conversation.id
    }
  }

  return {
    // State
    messages,
    isTyping,
    currentConversation,
    conversationHistory,
    // Actions
    sendMessage,
    startNewConversation,
    loadConversation
  }
})
```

### 3. Service Layer

#### `src/services/walletService.js`
```javascript
class WalletService {
  constructor() {
    this.chainId = 'secret-4'
    this.currency = {
      coinDenom: 'SCRT',
      coinMinimalDenom: 'uscrt',
      coinDecimals: 6,
    }
  }

  async connect() {
    try {
      if (!window.keplr) {
        throw new Error('Keplr wallet not found. Please install Keplr extension.')
      }

      // Enable chain
      await window.keplr.enable(this.chainId)
      
      // Get account
      const key = await window.keplr.getKey(this.chainId)
      
      return {
        success: true,
        address: key.bech32Address,
        name: key.name
      }
    } catch (error) {
      return {
        success: false,
        error: error.message
      }
    }
  }

  async getBalances(address) {
    try {
      // Call to secret_network_mcp VM
      const response = await apiService.get(`/api/balances/${address}`)
      return response.data
    } catch (error) {
      console.error('Failed to fetch balances:', error)
      return {}
    }
  }

  async checkConnection() {
    try {
      if (!window.keplr) return { connected: false }
      
      const key = await window.keplr.getKey(this.chainId)
      return {
        connected: true,
        address: key.bech32Address
      }
    } catch (error) {
      return { connected: false }
    }
  }

  async signTransaction(transaction) {
    try {
      // Implementation for transaction signing
      const response = await window.keplr.signAmino(
        this.chainId,
        transaction.signerAddress,
        transaction.signDoc
      )
      return response
    } catch (error) {
      throw new Error(`Failed to sign transaction: ${error.message}`)
    }
  }
}

export const walletService = new WalletService()
```

#### `src/services/apiService.js`
```javascript
import axios from 'axios'

class ApiService {
  constructor() {
    // Configure base URLs for different VMs
    this.secretMcpUrl = process.env.VUE_APP_SECRET_MCP_URL || 'http://localhost:3002'
    this.secretAiUrl = process.env.VUE_APP_SECRET_AI_URL || 'http://localhost:3003'
    
    // Create axios instances
    this.mcpApi = axios.create({
      baseURL: this.secretMcpUrl,
      timeout: 10000
    })
    
    this.aiApi = axios.create({
      baseURL: this.secretAiUrl,
      timeout: 30000
    })

    // Add message signing interceptors
    this.setupMessageSigning()
  }

  setupMessageSigning() {
    // Add request interceptor for message signing
    this.mcpApi.interceptors.request.use(async (config) => {
      // Add timestamp and nonce
      const timestamp = new Date().toISOString()
      const nonce = this.generateNonce()
      
      // Create signature (implement based on your signing protocol)
      const signature = await this.signMessage({
        method: config.method,
        url: config.url,
        data: config.data,
        timestamp,
        nonce
      })

      // Add headers
      config.headers['X-Timestamp'] = timestamp
      config.headers['X-Nonce'] = nonce
      config.headers['X-Signature'] = signature
      
      return config
    })
  }

  generateNonce() {
    return Math.random().toString(36).substring(2) + Date.now().toString(36)
  }

  async signMessage(payload) {
    // Implement your message signing logic here
    // This would use your cryptographic keys
    return 'signature-placeholder'
  }

  // Wallet-related API calls
  async getBalances(address) {
    return this.mcpApi.get(`/api/balances/${address}`)
  }

  async getWalletStatus() {
    return this.mcpApi.get('/api/wallet/status')
  }

  async signTransaction(transaction) {
    return this.mcpApi.post('/api/wallet/sign', transaction)
  }

  // Chat-related API calls
  async sendChatMessage(message) {
    return this.aiApi.post('/api/chat/message', { message })
  }

  async getChatHistory() {
    return this.aiApi.get('/api/chat/history')
  }

  // Attestation API calls
  async getVMStatus(vmName) {
    return this.mcpApi.get(`/api/attestations/${vmName}`)
  }

  async getBridgeStatus() {
    return this.mcpApi.get('/api/attestations/bridge')
  }
}

export const apiService = new ApiService()
```

## Development Workflow

### 1. Setup Development Environment
```bash
# Clone and setup
git clone <repository>
cd secretgptee
npm install

# Setup environment variables
cp .env.example .env
# Edit .env with your VM URLs and configurations

# Start development server
npm run dev
```

### 2. Component Development Order
1. **Layout Components** (MainLayout, HeaderBar, Sidebar)
2. **Basic UI Components** (Button, Modal, LoadingSpinner)
3. **Wallet Components** (WalletConnection, WalletStatus)
4. **Chat Components** (ChatInterface, MessageBubble)
5. **Attestation Components** (AttestationPanel, VMStatus)

### 3. Testing Strategy
```bash
# Component testing (manual)
npm run dev

# Build testing
npm run build
npm run preview

# Linting
npm run lint
npm run format
```

### 4. Environment Configuration

#### `.env.development`
```bash
VUE_APP_SECRET_MCP_URL=http://localhost:3002
VUE_APP_SECRET_AI_URL=http://localhost:3003
VUE_APP_CHAIN_ID=secret-4
VUE_APP_ENV=development
```

#### `.env.production`
```bash
VUE_APP_SECRET_MCP_URL=https://secret-mcp-vm.your-domain.com
VUE_APP_SECRET_AI_URL=https://secret-ai.your-domain.com
VUE_APP_CHAIN_ID=secret-4
VUE_APP_ENV=production
```

### 5. Build Configuration

#### `vite.config.js`
```javascript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  },
  server: {
    port: 3001,
    proxy: {
      '/api': {
        target: 'http://localhost:3002',
        changeOrigin: true
      }
    }
  },
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['vue', 'vue-router', 'pinia'],
          wallet: ['@keplr-wallet/cosmos']
        }
      }
    }
  }
})
```

This Vue.js implementation provides a solid foundation for the ChatGPT-like interface with all the required Secret Network features integrated through a clean, maintainable architecture.
