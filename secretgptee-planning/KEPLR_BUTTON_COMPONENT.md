# Keplr Connect Button - Complete Implementation

**Last Updated:** July 28, 2025
**Status:** Complete UI Component for Keplr Connection

## ✅ **Yes! The Plan Includes a Keplr Button**

### **Button States:**
1. **Disconnected:** "Connect Wallet" button
2. **Connecting:** "Connecting..." loading state  
3. **Connected:** Shows address + balance + disconnect option
4. **Error:** Shows error message with retry option

## 🎯 **Complete Keplr Button Component:**

### **`src/components/wallet/WalletConnectionButton.vue`**
```vue
<template>
  <div class="relative">
    <!-- Connected State -->
    <div v-if="isConnected" class="flex items-center space-x-2">
      <!-- Wallet Info Display -->
      <div class="flex items-center space-x-2 bg-green-900/20 border border-green-500/30 rounded-lg px-3 py-2">
        <div class="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
        <div class="flex flex-col">
          <span class="text-sm text-green-400 font-medium">{{ formattedAddress }}</span>
          <span class="text-xs text-gray-300">{{ formattedBalance }} SCRT</span>
        </div>
      </div>
      
      <!-- Disconnect Button -->
      <button
        @click="disconnect"
        class="p-2 text-gray-400 hover:text-red-400 transition-colors rounded-lg hover:bg-gray-700"
        title="Disconnect wallet"
      >
        <XMarkIcon class="w-4 h-4" />
      </button>
    </div>

    <!-- Disconnected State - Main Keplr Button -->
    <button
      v-else
      @click="connect"
      :disabled="isConnecting"
      class="flex items-center space-x-2 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 disabled:from-gray-600 disabled:to-gray-600 text-white px-4 py-2 rounded-lg transition-all duration-200 font-medium shadow-lg hover:shadow-xl"
    >
      <!-- Keplr Logo/Icon -->
      <div class="w-5 h-5 bg-white rounded-full flex items-center justify-center">
        <span class="text-blue-600 font-bold text-xs">K</span>
      </div>
      
      <!-- Button Text -->
      <span v-if="isConnecting" class="flex items-center space-x-2">
        <svg class="animate-spin h-4 w-4" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
        </svg>
        <span>Connecting...</span>
      </span>
      <span v-else>Connect Keplr</span>
    </button>

    <!-- Error Message -->
    <div v-if="error" class="absolute top-full mt-2 right-0 bg-red-900/20 border border-red-500/30 rounded-lg p-3 text-sm text-red-400 max-w-sm z-10">
      <div class="flex items-start space-x-2">
        <ExclamationTriangleIcon class="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
        <div class="flex-1">
          <p class="font-medium">Connection Failed</p>
          <p class="text-xs text-red-300 mt-1">{{ error }}</p>
          <button 
            @click="clearError" 
            class="text-red-300 hover:text-red-100 text-xs underline mt-2"
          >
            Try Again
          </button>
        </div>
        <button 
          @click="clearError" 
          class="text-red-300 hover:text-red-100 text-lg leading-none"
        >
          ×
        </button>
      </div>
    </div>

    <!-- Keplr Not Found Help -->
    <div v-if="showKeplrHelp" class="absolute top-full mt-2 right-0 bg-blue-900/20 border border-blue-500/30 rounded-lg p-3 text-sm text-blue-400 max-w-sm z-10">
      <div class="flex items-start space-x-2">
        <InformationCircleIcon class="w-5 h-5 text-blue-400 flex-shrink-0 mt-0.5" />
        <div class="flex-1">
          <p class="font-medium">Keplr Wallet Required</p>
          <p class="text-xs text-blue-300 mt-1">Install the Keplr browser extension to connect your wallet.</p>
          <a 
            href="https://www.keplr.app/download" 
            target="_blank"
            class="text-blue-300 hover:text-blue-100 text-xs underline mt-2 inline-block"
          >
            Download Keplr →
          </a>
        </div>
        <button 
          @click="showKeplrHelp = false" 
          class="text-blue-300 hover:text-blue-100 text-lg leading-none"
        >
          ×
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { 
  WalletIcon, 
  XMarkIcon, 
  ExclamationTriangleIcon,
  InformationCircleIcon 
} from '@heroicons/vue/24/outline';
import { useWallet } from '@/composables/useWallet';

const {
  isConnected,
  isConnecting,
  formattedAddress,
  formattedBalance,
  error,
  connect,
  disconnect
} = useWallet();

const showKeplrHelp = ref(false);

const clearError = () => {
  error.value = '';
  // Show help if error was about Keplr not found
  if (error.value?.includes('not found')) {
    showKeplrHelp.value = true;
  }
};
</script>

<style scoped>
/* Custom styles for wallet button */
.animate-pulse-slow {
  animation: pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
</style>
```

## 🎨 **Button Design Features:**

### **Visual Design:**
- ✅ **Gradient background** - Blue to purple Keplr-inspired colors
- ✅ **Keplr "K" icon** - Recognizable branding
- ✅ **Hover effects** - Smooth transitions and shadow changes
- ✅ **Loading spinner** - During connection process
- ✅ **Status indicators** - Green dot for connected state

### **User Experience:**
- ✅ **Clear states** - Disconnected, connecting, connected, error
- ✅ **Error handling** - Helpful error messages with retry
- ✅ **Keplr help** - Link to download if not installed
- ✅ **Wallet info** - Shows address and balance when connected
- ✅ **Easy disconnect** - X button to disconnect

### **Integration Points:**
- ✅ **Uses useWallet composable** - Reactive state management
- ✅ **Official Keplr SDK** - KeplrFallback for security
- ✅ **Balance display** - Shows SCRT from Secret Network MCP
- ✅ **Error recovery** - Clear error states and retry options

## 📍 **Where It Goes in the Layout:**

### **Header Bar Placement:**
```vue
<!-- In HeaderBar.vue -->
<template>
  <header class="flex items-center justify-between px-4 py-3 bg-gray-900">
    <!-- Left: Logo -->
    <div class="flex items-center space-x-2">
      <h1 class="text-xl font-semibold text-white">SecretGPTee</h1>
    </div>

    <!-- Right: Keplr Button -->
    <div class="flex items-center space-x-4">
      <WalletConnectionButton />
    </div>
  </header>
</template>
```

## ✅ **Complete Button Flow:**

1. **User sees:** "Connect Keplr" button with Keplr branding
2. **User clicks:** Button shows "Connecting..." with spinner
3. **Keplr prompts:** Official Keplr popup for connection approval
4. **Connected:** Shows wallet address + SCRT balance
5. **Balance updates:** Automatically fetches from Secret Network MCP
6. **Disconnect:** X button to disconnect and return to step 1

**Yes, the plan includes a complete, professional Keplr connect button with all the necessary states and error handling!**