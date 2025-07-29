# API Specification - SecretGPTee Cross-VM Communication

## Overview

This document defines the API contracts between:
- **secretgptee.com** (Vue.js frontend on secretGPT VM)
- **secret_network_mcp VM** (Keplr wallet backend)
- **SecretAI** (Chat AI service)

## Authentication: Verified Message Signing

### Message Format
All cross-VM API calls use signed messages instead of SSL/TLS:

```json
{
  "timestamp": "2025-07-28T10:30:00.000Z",
  "nonce": "abc123def456",
  "method": "POST",
  "endpoint": "/api/wallet/connect",
  "payload": "base64-encoded-request-body",
  "signature": "cryptographic-signature-here"
}
```

### Signature Verification Process
1. **Timestamp Validation:** Must be within 5 minutes of current time
2. **Nonce Tracking:** Prevent replay attacks
3. **Signature Verification:** Ed25519 or ECDSA verification
4. **Payload Integrity:** Verify payload hasn't been tampered with

---

## Wallet APIs (secret_network_mcp VM)

### Base URL: `https://secret-mcp-vm.domain.com/api`

### 1. Wallet Connection

#### `POST /wallet/connect`
**Purpose:** Establish wallet connection and verify Keplr access

**Request:**
```json
{
  "chainId": "secret-4",
  "walletType": "keplr"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "address": "secret1abc123...",
    "publicKey": "base64-encoded-public-key",
    "algorithm": "secp256k1"
  },
  "error": null
}
```

**Error Response:**
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "WALLET_NOT_FOUND",
    "message": "Keplr wallet not detected",
    "details": "Please install Keplr browser extension"
  }
}
```

### 2. Wallet Status

#### `GET /wallet/status/:address`
**Purpose:** Check wallet connection and basic info

**Response:**
```json
{
  "success": true,
  "data": {
    "connected": true,
    "address": "secret1abc123...",
    "network": "secret-4",
    "lastActivity": "2025-07-28T10:30:00.000Z"
  }
}
```

### 3. Balance Queries

#### `GET /balances/:address`
**Purpose:** Retrieve all token balances for address

**Response:**
```json
{
  "success": true,
  "data": {
    "native": {
      "scrt": {
        "amount": "1234567890",
        "denom": "uscrt",
        "formatted": "1,234.567890",
        "usdValue": "2,469.14"
      }
    },
    "tokens": {
      "sscrt": {
        "amount": "987654321",
        "contractAddress": "secret1...",
        "formatted": "987.654321",
        "usdValue": "1,975.31"
      }
    },
    "total": {
      "usdValue": "4,444.45"
    },
    "lastUpdated": "2025-07-28T10:30:00.000Z"
  }
}
```

### 4. Transaction Signing

#### `POST /wallet/sign`
**Purpose:** Sign transactions using Keplr

**Request:**
```json
{
  "transaction": {
    "chainId": "secret-4",
    "accountNumber": "12345",
    "sequence": "67",
    "fee": {
      "amount": [{"denom": "uscrt", "amount": "25000"}],
      "gas": "200000"
    },
    "msgs": [
      {
        "type": "cosmos-sdk/MsgSend",
        "value": {
          "from_address": "secret1abc123...",
          "to_address": "secret1def456...",
          "amount": [{"denom": "uscrt", "amount": "1000000"}]
        }
      }
    ],
    "memo": "Test transaction"
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "signature": "base64-encoded-signature",
    "publicKey": "base64-encoded-public-key",
    "txHash": "ABC123DEF456...",
    "broadcastMode": "sync"
  }
}
```

### 5. Transaction Broadcasting

#### `POST /wallet/broadcast`
**Purpose:** Broadcast signed transaction to Secret Network

**Request:**
```json
{
  "signedTx": "base64-encoded-signed-transaction"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "txHash": "ABC123DEF456...",
    "height": "8123456",
    "gasUsed": "185423",
    "gasWanted": "200000",
    "events": [...]
  }
}
```

---

## Chat APIs (SecretAI Service)

### Base URL: `https://secret-ai.domain.com/api`

### 1. Send Message

#### `POST /chat/message`
**Purpose:** Send message to SecretAI and get response

**Request:**
```json
{
  "message": "What is my SCRT balance?",
  "context": {
    "walletAddress": "secret1abc123...",
    "conversationId": "conv-123",
    "sessionId": "sess-456"
  },
  "options": {
    "includeBalance": true,
    "includeAttestations": false,
    "maxTokens": 500
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "response": "Your current SCRT balance is 1,234.56 SCRT (worth approximately $2,469.14 USD).",
    "messageId": "msg-789",
    "timestamp": "2025-07-28T10:30:00.000Z",
    "context": {
      "balanceChecked": true,
      "dataUsed": ["wallet_balance"]
    },
    "suggestions": [
      "Would you like to see your transaction history?",
      "Should I help you send some SCRT to another address?"
    ]
  }
}
```

### 2. Chat History

#### `GET /chat/history/:sessionId`
**Purpose:** Retrieve conversation history

**Response:**
```json
{
  "success": true,
  "data": {
    "sessionId": "sess-456",
    "messages": [
      {
        "id": "msg-001",
        "content": "Hello! How can I help you today?",
        "sender": "ai",
        "timestamp": "2025-07-28T10:25:00.000Z"
      },
      {
        "id": "msg-002",
        "content": "What is my balance?",
        "sender": "user",
        "timestamp": "2025-07-28T10:25:30.000Z"
      }
    ],
    "totalMessages": 2,
    "lastActivity": "2025-07-28T10:30:00.000Z"
  }
}
```

### 3. New Conversation

#### `POST /chat/new`
**Purpose:** Start a new conversation session

**Request:**
```json
{
  "walletAddress": "secret1abc123...",
  "initialContext": {
    "userPreferences": {
      "language": "en",
      "verbosity": "normal"
    }
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "sessionId": "sess-789",
    "conversationId": "conv-456",
    "welcomeMessage": "Welcome back! I can help you with your Secret Network wallet and transactions. What would you like to know?",
    "availableFeatures": [
      "balance_queries",
      "transaction_help",
      "network_status",
      "attestation_info"
    ]
  }
}
```

---

## Attestation APIs (VM Health Monitoring)

### Base URL: `https://secret-mcp-vm.domain.com/api`

### 1. VM Status Check

#### `GET /attestations/vm/:vmName`
**Purpose:** Get health status of specific VM

**Supported VMs:** `secretgpt`, `secretai`, `secret-mcp`

**Response:**
```json
{
  "success": true,
  "data": {
    "vmName": "secretgpt",
    "status": "healthy",
    "uptime": "72:15:30",
    "lastChecked": "2025-07-28T10:30:00.000Z",
    "metrics": {
      "cpu": {
        "usage": "23%",
        "cores": 2
      },
      "memory": {
        "used": "2.1GB",
        "total": "4.0GB",
        "percentage": "52%"
      },
      "storage": {
        "used": "15.2GB",
        "total": "40.0GB",
        "percentage": "38%"
      }
    },
    "services": {
      "nginx": "running",
      "secretgptee": "running",
      "attestai": "running"
    },
    "connectivity": {
      "internet": true,
      "secret_network": true,
      "bridge_to_mcp": true
    }
  }
}
```

### 2. Bridge Status

#### `GET /attestations/bridge`
**Purpose:** Check communication bridge health between VMs

**Response:**
```json
{
  "success": true,
  "data": {
    "bridgeStatus": "operational",
    "lastCommunication": "2025-07-28T10:29:45.000Z",
    "messagesSigned": 1247,
    "messagesVerified": 1247,
    "failureRate": "0%",
    "averageLatency": "45ms",
    "endpoints": {
      "secretgpt_to_mcp": {
        "status": "healthy",
        "lastTest": "2025-07-28T10:29:45.000Z",
        "responseTime": "42ms"
      },
      "mcp_to_secretgpt": {
        "status": "healthy",
        "lastTest": "2025-07-28T10:29:50.000Z",
        "responseTime": "38ms"
      }
    },
    "signingKeys": {
      "secretgpt_key": {
        "status": "valid",
        "expiresAt": "2025-08-28T00:00:00.000Z"
      },
      "mcp_key": {
        "status": "valid",
        "expiresAt": "2025-08-28T00:00:00.000Z"
      }
    }
  }
}
```

### 3. All Attestations

#### `GET /attestations/all`
**Purpose:** Get comprehensive status of entire system

**Response:**
```json
{
  "success": true,
  "data": {
    "overallStatus": "healthy",
    "timestamp": "2025-07-28T10:30:00.000Z",
    "vms": {
      "secretgpt": {
        "status": "healthy",
        "uptime": "99.8%",
        "services": 3,
        "issues": 0
      },
      "secretai": {
        "status": "healthy",
        "uptime": "99.9%",
        "services": 2,
        "issues": 0
      },
      "secret_mcp": {
        "status": "healthy",
        "uptime": "99.7%",
        "services": 4,
        "issues": 0
      }
    },
    "bridge": {
      "status": "operational",
      "messagesSigned": 1247,
      "successRate": "100%"
    },
    "network": {
      "secretNetwork": "connected",
      "blockHeight": 8123456,
      "latency": "150ms"
    }
  }
}
```

---

## Error Handling

### Standard Error Response Format
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable error message",
    "details": "Additional context or debugging information",
    "timestamp": "2025-07-28T10:30:00.000Z",
    "requestId": "req-123456"
  }
}
```

### Common Error Codes

#### Wallet Errors
- `WALLET_NOT_FOUND` - Keplr wallet not installed
- `WALLET_LOCKED` - Wallet is locked by user
- `INSUFFICIENT_FUNDS` - Not enough balance for transaction
- `TRANSACTION_FAILED` - Transaction broadcasting failed
- `INVALID_ADDRESS` - Malformed wallet address

#### Authentication Errors
- `INVALID_SIGNATURE` - Message signature verification failed
- `EXPIRED_TIMESTAMP` - Request timestamp too old
- `REPLAY_ATTACK` - Nonce already used
- `UNAUTHORIZED` - Invalid or missing credentials

#### System Errors
- `VM_UNREACHABLE` - Target VM not responding
- `SERVICE_UNAVAILABLE` - Specific service is down
- `RATE_LIMITED` - Too many requests
- `INTERNAL_ERROR` - Unexpected server error

#### Chat Errors
- `AI_UNAVAILABLE` - SecretAI service not responding
- `CONTEXT_INVALID` - Invalid conversation context
- `MESSAGE_TOO_LONG` - Message exceeds maximum length
- `CONTENT_FILTERED` - Message blocked by content filter

---

## Rate Limiting

### Default Limits
- **Wallet APIs:** 100 requests/minute per wallet address
- **Chat APIs:** 30 messages/minute per session
- **Attestation APIs:** 120 requests/minute per client
- **Bridge Communication:** No limit (internal traffic)

### Rate Limit Headers
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 87
X-RateLimit-Reset: 1690545600
```

---

## WebSocket Events (Optional Future Enhancement)

### Real-time Updates
```javascript
// Balance updates
{
  "event": "balance_updated",
  "data": {
    "address": "secret1abc123...",
    "newBalance": "1235.567890",
    "change": "+1.000000"
  }
}

// VM status changes
{
  "event": "vm_status_changed",
  "data": {
    "vmName": "secretgpt",
    "status": "warning",
    "reason": "High CPU usage detected"
  }
}

// Chat typing indicators
{
  "event": "ai_typing",
  "data": {
    "sessionId": "sess-456",
    "typing": true
  }
}
```

This API specification provides a complete contract for all cross-VM communications needed for the SecretGPTee.com MVP, with proper error handling, security through message signing, and comprehensive documentation for implementation.
