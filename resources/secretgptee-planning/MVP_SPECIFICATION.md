# SecretGPTee.com MVP Specification

**Last Updated:** July 28, 2025
**Framework Decision:** ✅ Vue.js + Vite
**UI Design:** ChatGPT-like layout
**Domain:** secretgptee.com

## MVP Feature Set

### 1. Keplr Wallet Connection 🔗
**Functionality:**
- Connect/disconnect Keplr wallet button
- Display wallet connection status
- Show connected wallet address
- Handle connection errors gracefully

**UI Location:** Top-right corner (like ChatGPT profile menu)

### 2. Secret Network Balances 💰
**Functionality:**
- Display SCRT token balance
- Show other Secret Network token balances
- Real-time balance updates
- Formatted currency display

**UI Location:** Sidebar panel (expandable)

### 3. Multi-VM Attestations 🛡️
**Display attestations for:**
- **secretGPT VM** - Current VM status and health
- **secretAI** - AI service status and capabilities  
- **secret_network_mcp VM** - Wallet service status
- **Verified Signing Bridge** - Communication channel health between secretGPT ↔ secret_network_mcp

**UI Location:** Status bar or dedicated attestations panel

### 4. SecretAI Chat Interface 💬
**Functionality:**
- ChatGPT-like conversation interface
- Message history
- Typing indicators
- Send/receive messages to secretAI
- Message formatting (markdown support)

**UI Location:** Main content area (primary focus)

## ChatGPT-Like Layout Structure

```
┌─────────────────────────────────────────────────────────────┐
│ [SecretGPTee Logo]                    [Wallet] [Attestations] │ ← Header
├─────────────────────────────────────────────────────────────┤
│ [Sidebar]     │                                             │
│ - Chat History│              Main Chat Area                 │
│ - Balances    │                                             │
│ - Quick Links │         [Message Bubbles]                   │
│               │                                             │
│               │         ┌─────────────────────────┐         │
│               │         │ Type your message...   │[Send]   │ ← Input
└───────────────┴─────────┴─────────────────────────┴─────────┘
```

### Header Bar Components
- **Logo/Brand:** "SecretGPTee" 
- **Wallet Connection:** Button showing connection status
- **Attestations Indicator:** Health status of all VMs
- **Settings/Profile:** Optional dropdown menu

### Sidebar Components  
- **Chat History:** Previous conversations (if implementing)
- **Balance Panel:** Expandable SCRT/token balances
- **Quick Actions:** Common wallet operations
- **VM Status:** Mini health indicators

### Main Chat Area
- **Message Thread:** SecretAI conversation
- **Message Input:** Text area with send button
- **Typing Indicators:** Show when AI is responding
- **Message Actions:** Copy, regenerate, etc.

## Technical Architecture

### Vue.js Component Structure
```
src/
├── components/
│   ├── layout/
│   │   ├── HeaderBar.vue
│   │   ├── Sidebar.vue
│   │   └── MainLayout.vue
│   ├── wallet/
│   │   ├── WalletConnection.vue
│   │   ├── BalanceDisplay.vue
│   │   └── WalletStatus.vue
│   ├── chat/
│   │   ├── ChatInterface.vue
│   │   ├── MessageBubble.vue
│   │   ├── MessageInput.vue
│   │   └── TypingIndicator.vue
│   ├── attestations/
│   │   ├── AttestationPanel.vue
│   │   ├── VMStatus.vue
│   │   └── BridgeStatus.vue
│   └── common/
│       ├── LoadingSpinner.vue
│       └── ErrorMessage.vue
├── stores/
│   ├── wallet.js (Pinia store)
│   ├── chat.js
│   └── attestations.js
├── services/
│   ├── walletService.js
│   ├── chatService.js
│   └── attestationService.js
└── assets/
    ├── styles/
    └── icons/
```

### State Management (Pinia)
- **Wallet Store:** Connection status, balances, transactions
- **Chat Store:** Message history, current conversation
- **Attestations Store:** VM health status, bridge status

### API Integration Points

#### 1. Keplr Wallet APIs
```javascript
// Direct browser integration
window.keplr.enable("secret-4")
window.keplr.getKey("secret-4")
```

#### 2. Secret Network MCP VM APIs
```javascript
// Cross-VM calls to secret_network_mcp
GET  /api/balances/:address
POST /api/transactions/sign
GET  /api/status
```

#### 3. SecretAI Chat APIs  
```javascript
// Local or remote SecretAI endpoints
POST /api/chat/message
GET  /api/chat/history
POST /api/chat/new
```

#### 4. Attestation APIs
```javascript
// VM health and bridge status
GET /api/attestations/secretgpt
GET /api/attestations/secretai  
GET /api/attestations/secret-mcp
GET /api/attestations/bridge
```

## UI/UX Design Specifications

### Color Scheme (ChatGPT-inspired)
- **Primary Background:** Dark mode (#1a1a1a) / Light mode (#ffffff)
- **Sidebar:** Slightly darker/lighter than main
- **Message Bubbles:** User vs AI differentiation
- **Accent Colors:** Secret Network brand colors
- **Status Colors:** Green (healthy), Yellow (warning), Red (error)

### Typography
- **Primary Font:** System fonts (similar to ChatGPT)
- **Code/Monospace:** For addresses, hashes, technical data
- **Font Sizes:** Responsive, accessible

### Responsive Design Breakpoints
- **Desktop:** Full sidebar + main area
- **Tablet:** Collapsible sidebar
- **Mobile:** Hidden sidebar, focus on chat

### Animation & Interactions
- **Smooth transitions** between states
- **Loading animations** for wallet operations
- **Typing indicators** for AI responses
- **Hover effects** on interactive elements
- **Slide-in animations** for notifications

## Development Phases

### Phase 1: Core Layout & Navigation (2-3 days)
- [ ] Set up Vue.js + Vite project
- [ ] Create ChatGPT-like layout structure
- [ ] Implement responsive design
- [ ] Add basic navigation and routing
- [ ] Style with Tailwind CSS

### Phase 2: Wallet Integration (3-4 days)
- [ ] Implement Keplr connection UI
- [ ] Add wallet status indicators
- [ ] Create balance display components
- [ ] Test wallet connection flow
- [ ] Handle error states

### Phase 3: Chat Interface (2-3 days)
- [ ] Build chat message components
- [ ] Implement message input/send
- [ ] Add conversation state management
- [ ] Connect to SecretAI APIs
- [ ] Add typing indicators and loading states

### Phase 4: Attestations System (2-3 days)
- [ ] Create VM status components
- [ ] Implement bridge health monitoring
- [ ] Add attestation data visualization
- [ ] Real-time status updates
- [ ] Alert system for issues

### Phase 5: Integration & Polish (2-3 days)
- [ ] Connect all systems together
- [ ] Add error handling and edge cases
- [ ] Performance optimization
- [ ] Accessibility improvements
- [ ] Final testing and bug fixes

## Success Metrics

### Technical Metrics
- [ ] Page load time < 2 seconds
- [ ] Wallet connection < 5 seconds
- [ ] Chat response time < 3 seconds
- [ ] 99%+ uptime for attestations

### User Experience Metrics
- [ ] Intuitive wallet connection flow
- [ ] Clear status indicators
- [ ] Responsive design on all devices
- [ ] Smooth chat interaction

### Demo Metrics
- [ ] Reliable demonstration script
- [ ] Professional appearance
- [ ] Clear value proposition
- [ ] Engaging user journey

---

## Notes & Considerations

### Security Considerations
- Never store private keys in browser
- Validate all cross-VM communications
- Implement proper error handling for wallet failures
- Secure message signing for bridge communications

### Performance Optimizations  
- Lazy load non-critical components
- Implement efficient state management
- Optimize bundle size with code splitting
- Cache attestation data appropriately

### Accessibility Features
- Keyboard navigation support
- Screen reader compatibility
- High contrast mode support
- Focus management for modal dialogs
