# Technical Specifications - SecretGPTee.com

## System Architecture

### VM Configuration
```
Current secretGPT VM:
- vCPUs: 2
- RAM: 4 GB
- Storage: 40 GB
- OS: [To be documented]
- Current load: [To be measured]
```

### Multi-Site Hosting Architecture
```
Single VM hosting both:
├── attestAI.io (existing)
│   ├── Education-focused content
│   ├── Current tech stack: [To be documented]
│   └── No wallet features
└── secretgptee.com (new)
    ├── User-focused interface
    ├── Keplr wallet integration UI
    └── Message signing communication
```

### Inter-VM Communication
```
secretGPT VM ←→ secret_network_mcp VM
Protocol: Verified Message Signing (replacing SSL)
```

## Technical Stack Decisions

### Frontend Framework Options
| Option | Pros | Cons | Recommendation |
|--------|------|------|----------------|
| React | Rich ecosystem, component reuse | Larger bundle size | ⭐ Good for demo |
| Vue.js | Gentler learning curve | Smaller ecosystem | ✅ Lightweight option |
| Vanilla JS | Minimal overhead | More manual work | ✅ For simple demos |
| Svelte | Excellent performance | Newer ecosystem | Consider for production |

### Styling Framework Options
| Option | Pros | Cons | Use Case |
|--------|------|------|---------|
| Tailwind CSS | Rapid development | Learning curve | ⭐ Recommended |
| Bootstrap | Familiar, comprehensive | Generic look | Quick prototyping |
| Custom CSS | Full control | More time investment | Unique branding |

### Build Tools
- **Vite** - Fast development, good for demos
- **Webpack** - Mature, comprehensive
- **Parcel** - Zero config, simple setup

## API Design

### Wallet Integration Endpoints
```
secretgptee.com → secret_network_mcp VM

Endpoints needed:
- POST /wallet/connect
- GET /wallet/status
- POST /wallet/sign
- GET /wallet/balance
- POST /wallet/transaction
```

### Message Signing Protocol
```
Request Format:
{
  "timestamp": "ISO-8601",
  "nonce": "unique-identifier",
  "payload": "base64-encoded-data",
  "signature": "signed-hash"
}

Verification Process:
1. Verify timestamp (prevent replay)
2. Check nonce uniqueness
3. Verify signature against public key
4. Process payload if valid
```

## Security Considerations

### Key Management
- **Key Generation:** Ed25519 or ECDSA
- **Storage:** Secure key storage on each VM
- **Rotation:** Monthly or on-demand
- **Distribution:** Initial secure exchange

### Message Security
- **Replay Protection:** Timestamp + nonce tracking
- **Integrity:** Full message signing
- **Non-repudiation:** Asymmetric signatures
- **Forward Secrecy:** Consider key rotation

## Performance Requirements

### Response Time Targets
- **Page Load:** < 2 seconds
- **Wallet Connection:** < 5 seconds
- **Cross-VM API:** < 1 second
- **Message Signing:** < 100ms

### Scalability Considerations
- **Current:** Tech demo traffic
- **Future:** Production readiness
- **Monitoring:** Resource usage tracking

## Deployment Architecture

### Domain Configuration
```
secretgptee.com → secretGPT VM
attestAI.io → secretGPT VM (existing)

Reverse Proxy Setup:
nginx/Apache routing by Host header
SSL termination at proxy level
```

### SSL Certificate Management
- **Option 1:** Wildcard certificate
- **Option 2:** Individual domain certificates
- **Renewal:** Automated (Let's Encrypt)

## Development Workflow

### Local Development
1. Clone from existing secretGPT structure
2. Set up local development server
3. Mock cross-VM communication for testing
4. Hot reload for rapid iteration

### Testing Strategy
- **Unit Tests:** Core functionality
- **Integration Tests:** Cross-VM communication
- **E2E Tests:** Wallet connection flow
- **Performance Tests:** Load testing

### Deployment Process
1. Build production assets
2. Deploy to VM
3. Update reverse proxy configuration
4. Test both domains
5. Monitor performance

## Browser Compatibility

### Target Browsers
- **Chrome/Chromium:** Latest 2 versions
- **Firefox:** Latest 2 versions
- **Safari:** Latest 2 versions
- **Edge:** Latest 2 versions

### Keplr Wallet Requirements
- **Desktop:** Browser extension support
- **Mobile:** WalletConnect integration
- **Fallback:** Manual connection instructions

## Monitoring & Analytics

### Performance Monitoring
- **VM Resources:** CPU, RAM, disk usage
- **Response Times:** API endpoint performance
- **Error Rates:** Failed requests/connections

### User Analytics
- **Page Views:** Traffic patterns
- **Wallet Connections:** Success/failure rates
- **Demo Completion:** User journey tracking

---

## Configuration Templates

### Nginx Reverse Proxy Example
```nginx
server {
    listen 80;
    server_name attestai.io;
    # Existing configuration
}

server {
    listen 80;
    server_name secretgptee.com;
    location / {
        proxy_pass http://localhost:3001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Environment Variables Template
```bash
# Domain configuration
ATTESTAI_DOMAIN=attestAI.io
SECRETGPTEE_DOMAIN=secretgptee.com

# Cross-VM communication
SECRET_MCP_URL=http://secret-network-mcp-vm:port
SIGNING_PRIVATE_KEY=path/to/private/key
VERIFICATION_PUBLIC_KEY=path/to/public/key

# Development settings
NODE_ENV=production
PORT=3001
```
