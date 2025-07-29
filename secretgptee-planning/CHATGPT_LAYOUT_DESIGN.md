# ChatGPT-Like Layout Design - SecretGPTee.com

## Visual Layout Reference

### Desktop Layout (1200px+)
```
┌─────────────────────────────────────────────────────────────────────────────┐
│ [🔒 SecretGPTee]                           [💰 Balance] [🛡️ Status] [👤 Wallet] │ ← Header (60px)
├─────────────────────────────────────────────────────────────────────────────┤
│ ┌─────────────────┐                                                         │
│ │ 💬 Chat History │                    Main Chat Area                       │
│ │ ┌─────────────┐ │                                                         │
│ │ │ Conv 1      │ │  ┌─────────────────────────────────────────────────┐   │
│ │ │ Conv 2      │ │  │ 🤖 Welcome to SecretGPTee! How can I help?    │   │
│ │ │ + New Chat  │ │  └─────────────────────────────────────────────────┘   │
│ │ └─────────────┘ │                                                         │
│ │                 │  ┌─────────────────────────────────────────────────┐   │
│ │ 💰 Balances     │  │ 👤 Show me my wallet balance                   │   │
│ │ SCRT: 1,234.56  │  └─────────────────────────────────────────────────┘   │
│ │ sSCRT: 789.12   │                                                         │
│ │                 │  ┌─────────────────────────────────────────────────┐   │
│ │ 🛡️ VM Status    │  │ 🤖 Your SCRT balance is 1,234.56 tokens       │   │
│ │ ✅ SecretGPT    │  └─────────────────────────────────────────────────┘   │
│ │ ✅ SecretAI     │                                                         │
│ │ ✅ NetworkMCP   │                                                         │
│ │ ✅ Bridge       │                                                         │
│ └─────────────────┘  ┌─────────────────────────────┐ ┌─────┐               │
│                      │ Type your message here...   │ │Send │               │ ← Input (80px)
│                      └─────────────────────────────┘ └─────┘               │
└─────────────────────────────────────────────────────────────────────────────┘
     ↑ 280px                                    ↑ Flexible width
   Sidebar                                   Main content area
```

### Mobile Layout (< 768px)
```
┌─────────────────────────────────────┐
│ ☰ [SecretGPTee]      [💰] [🛡️] [👤] │ ← Collapsed header
├─────────────────────────────────────┤
│                                     │
│  ┌─────────────────────────────┐    │
│  │ 🤖 Welcome message          │    │
│  └─────────────────────────────┘    │
│                                     │
│  ┌─────────────────────────────┐    │
│  │ 👤 User message             │    │
│  └─────────────────────────────┘    │
│                                     │
│                                     │
├─────────────────────────────────────┤
│ [Message input...]        [Send]    │ ← Fixed bottom input
└─────────────────────────────────────┘
```

## Component Breakdown

### 1. Header Bar Component (`HeaderBar.vue`)
**Features:**
- Logo/brand on the left
- Balance indicator (clickable to expand)
- Attestation status indicator
- Wallet connection status/button
- Responsive collapse on mobile

**Styling:**
- Fixed height: 60px
- Dark background with subtle border
- Icons with hover effects
- Notification badges for status updates

### 2. Sidebar Component (`Sidebar.vue`) 
**Sections:**
- **Chat History** (top priority)
  - Previous conversations
  - "New Chat" button
  - Search conversations
- **Balance Panel** (expandable)
  - SCRT balance
  - Other Secret Network tokens
  - Quick refresh button
- **VM Status Panel**
  - Real-time health indicators
  - Click to expand details
  - Color-coded status

**Responsive Behavior:**
- Desktop: Always visible (280px width)
- Tablet: Collapsible overlay
- Mobile: Hidden, accessible via hamburger menu

### 3. Main Chat Area (`ChatInterface.vue`)
**Structure:**
- **Message Container:** Scrollable area for conversation
- **Message Bubbles:** User vs AI styling
- **Input Area:** Fixed bottom positioning
- **Loading States:** Typing indicators, connection status

**Message Types:**
- User messages (right-aligned, blue)
- AI responses (left-aligned, gray) 
- System messages (centered, muted)
- Error messages (red accent)

### 4. Wallet Integration (`WalletConnection.vue`)
**Connection States:**
- **Disconnected:** "Connect Wallet" button
- **Connecting:** Loading spinner
- **Connected:** Address + balance preview
- **Error:** Clear error message with retry

**Wallet Actions:**
- Connect/disconnect
- View full balance details
- Quick transaction signing
- Network switching (if needed)

### 5. Attestation System (`AttestationPanel.vue`)
**VM Status Display:**
- **SecretGPT VM:** Current hosting VM
- **SecretAI:** AI service availability  
- **Secret Network MCP:** Wallet service
- **Signing Bridge:** Inter-VM communication

**Status Indicators:**
- ✅ Green: Healthy/operational
- ⚠️ Yellow: Warning/degraded
- ❌ Red: Error/offline
- 🔄 Blue: Updating/syncing

## Design System

### Color Palette
```css
/* Dark Mode (Primary) */
--bg-primary: #1a1a1a;      /* Main background */
--bg-secondary: #2d2d2d;    /* Sidebar, cards */
--bg-tertiary: #3d3d3d;     /* Hover states */
--text-primary: #ffffff;    /* Main text */
--text-secondary: #b3b3b3;  /* Secondary text */
--text-muted: #666666;      /* Muted text */

/* Accent Colors */
--accent-primary: #00d4ff;  /* Secret Network blue */
--accent-success: #00ff88;  /* Success/connected */
--accent-warning: #ffb800;  /* Warning states */
--accent-error: #ff4757;    /* Error states */
--accent-user: #007bff;     /* User messages */

/* Light Mode (Optional) */
--bg-primary-light: #ffffff;
--bg-secondary-light: #f8f9fa;
--text-primary-light: #1a1a1a;
```

### Typography Scale
```css
/* Font Sizes */
--text-xs: 0.75rem;    /* 12px - Small labels */
--text-sm: 0.875rem;   /* 14px - Secondary text */
--text-base: 1rem;     /* 16px - Body text */
--text-lg: 1.125rem;   /* 18px - Large text */
--text-xl: 1.25rem;    /* 20px - Headings */
--text-2xl: 1.5rem;    /* 24px - Large headings */

/* Font Weights */
--font-normal: 400;
--font-medium: 500;
--font-semibold: 600;
--font-bold: 700;
```

### Spacing System
```css
/* Spacing Scale */
--space-1: 0.25rem;  /* 4px */
--space-2: 0.5rem;   /* 8px */
--space-3: 0.75rem;  /* 12px */
--space-4: 1rem;     /* 16px */
--space-6: 1.5rem;   /* 24px */
--space-8: 2rem;     /* 32px */
--space-12: 3rem;    /* 48px */
```

## Animation Guidelines

### Micro-interactions
- **Button Hover:** Subtle scale (1.02x) + color transition
- **Message Send:** Slide-in from right with fade
- **Status Changes:** Color pulse + icon animation
- **Loading States:** Skeleton screens + spinners

### Page Transitions
- **Sidebar Toggle:** Slide left/right (300ms ease)
- **Modal Dialogs:** Fade + scale from center
- **Chat Scroll:** Smooth auto-scroll to new messages
- **Connection States:** Fade between states

### Performance Considerations
- Use CSS transforms for animations
- Limit to 60fps animations
- Reduce motion for accessibility preferences
- Hardware acceleration for smooth interactions

## Accessibility Features

### Keyboard Navigation
- Tab order: Header → Sidebar → Main → Input
- Arrow keys for message history
- Enter to send messages
- Escape to close modals

### Screen Reader Support
- Semantic HTML structure
- ARIA labels for interactive elements
- Live regions for status updates
- Alt text for all icons/images

### Visual Accessibility
- High contrast mode support
- Focus indicators for all interactive elements
- Consistent heading hierarchy
- Readable font sizes (minimum 16px)

## Responsive Breakpoints

```css
/* Mobile First Approach */
.container {
  /* Mobile: < 768px */
  padding: 1rem;
}

@media (min-width: 768px) {
  /* Tablet */
  .sidebar { width: 280px; }
}

@media (min-width: 1024px) {
  /* Desktop */
  .container { max-width: 1200px; }
}

@media (min-width: 1440px) {
  /* Large Desktop */
  .container { max-width: 1400px; }
}
```

---

## Implementation Priority

### Phase 1: Core Layout
1. Header bar with basic navigation
2. Sidebar structure (collapsible)
3. Main chat area layout
4. Responsive grid system

### Phase 2: Interactive Elements  
1. Wallet connection button/modal
2. Chat input and send functionality
3. Message bubble components
4. Basic state management

### Phase 3: Advanced Features
1. Real-time status indicators
2. Balance display and updates
3. Chat history management
4. Advanced animations

### Phase 4: Polish & Optimization
1. Performance optimization
2. Accessibility improvements
3. Error state handling
4. Final design refinements

This layout provides a familiar ChatGPT-like experience while showcasing the unique Secret Network features through the wallet integration and multi-VM attestation system.
