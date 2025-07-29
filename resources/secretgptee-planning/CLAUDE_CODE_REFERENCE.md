# Claude Code Build Reference - SecretGPTee.com

## Quick Start for Claude Code Build

### Project Context
**What we're building:** secretgptee.com - User-focused website with Keplr wallet integration for Secret Network tech demo

**Current Status:** Planning phase complete, ready for development

**Key Requirements:**
- Host alongside existing attestAI.io on same VM
- Integrate with Keplr wallet via secret_network_mcp VM
- Implement verified message signing between VMs
- Low traffic tech demo (not production scale)

### Essential Information for Claude Code

#### VM Specifications
```
Target VM: secretGPT VM
- vCPUs: 2
- RAM: 4 GB  
- Storage: 40 GB
- Currently hosting: attestAI.io
- Expected load: Tech demo traffic only
```

#### Architecture Overview
```
secretGPT VM (2 vCPU, 4GB RAM)
├── attestAI.io (existing, education-focused)
└── secretgptee.com (new, user-focused)
    └── Connects to → secret_network_mcp VM (Keplr wallet)
```

#### Key Constraints
1. **No code changes to attestAI.io** - Keep existing site unchanged
2. **Wallet features only on secretgptee.com** - Clean separation
3. **Resource sharing** - Both sites on same VM
4. **Security** - Verified message signing instead of SSL between VMs

### Technology Stack Recommendations

#### Frontend (Choose One)
- **React + Vite** - Good for component reuse, fast dev
- **Vue.js** - Lightweight, good for demos  
- **Vanilla JS** - Minimal overhead, simple

#### Styling
- **Tailwind CSS** - Rapid development, consistent design
- **Custom CSS** - Full control for unique branding

#### Domain Routing
- **Nginx reverse proxy** - Route by domain name
- **SSL certificates** - Let's Encrypt for both domains

### Critical Files & Directories

#### Planning Documents Location
```
F:\coding\secretgptee-planning\
├── BUILD_REQUIREMENTS.md
├── TECHNICAL_SPECS.md
├── TIMELINE_CHECKLIST.md
└── CLAUDE_CODE_REFERENCE.md (this file)
```

#### Existing Project Structure
```
F:\coding\secretGPT\ (existing attestAI.io)
F:\coding\secret_network_mcp\ (Keplr wallet backend)
```

### Development Priorities

#### Phase 1: Basic Website (START HERE)
1. Set up secretgptee.com basic structure
2. Configure reverse proxy for domain routing
3. Create user-focused landing page
4. Ensure both sites work simultaneously

#### Phase 2: Wallet Integration
1. Add Keplr connection button UI
2. Implement API calls to secret_network_mcp VM
3. Create wallet status/balance display
4. Test end-to-end wallet flow

#### Phase 3: Message Signing Security
1. Generate cryptographic key pairs
2. Implement signed message protocol
3. Replace API authentication with signatures
4. Test security implementation

### Environment Setup Commands

#### For Domain Configuration
```bash
# Test domain resolution
nslookup secretgptee.com

# Check current nginx config
nginx -t

# Reload nginx after changes
systemctl reload nginx
```

#### For SSL Certificates
```bash
# Generate Let's Encrypt certificates
certbot --nginx -d secretgptee.com
```

### API Endpoints to Implement

#### Wallet Integration APIs (secretgptee.com → secret_network_mcp)
```
POST /api/wallet/connect
GET  /api/wallet/status
POST /api/wallet/sign
GET  /api/wallet/balance
```

#### Message Signing Format
```json
{
  "timestamp": "2025-07-28T10:30:00Z",
  "nonce": "unique-request-id",
  "payload": "base64-encoded-request-data", 
  "signature": "cryptographic-signature"
}
```

### Testing Checklist

#### Basic Functionality
- [ ] secretgptee.com loads correctly
- [ ] attestAI.io still works unchanged  
- [ ] SSL certificates valid for both domains
- [ ] Responsive design on mobile/desktop

#### Wallet Integration  
- [ ] Keplr wallet connection works
- [ ] Wallet status displays correctly
- [ ] Transaction signing functional
- [ ] Error handling for connection failures

#### Cross-VM Communication
- [ ] API calls reach secret_network_mcp VM
- [ ] Message signing/verification works
- [ ] Proper error handling for network issues
- [ ] Performance meets <1 second target

### Common Issues & Solutions

#### Domain Routing Issues
- Check nginx configuration syntax
- Verify DNS propagation 
- Test with curl/postman before browser

#### Wallet Connection Problems
- Ensure Keplr extension installed
- Check browser console for errors
- Verify API endpoints reachable

#### Resource Constraints
- Monitor VM memory/CPU usage
- Optimize bundle sizes
- Implement caching where appropriate

### Demo Script Outline

1. **Landing Page** - Show user-focused design vs education site
2. **Wallet Connection** - Demonstrate Keplr integration  
3. **Secret Network Features** - Show specific capabilities
4. **Security** - Explain message signing vs traditional SSL
5. **Architecture** - Highlight VM separation and communication

### Deployment Notes

#### Pre-deployment Checklist
- [ ] Test on staging/local environment
- [ ] Backup existing attestAI.io configuration
- [ ] Have rollback plan ready
- [ ] Monitor resource usage during deployment

#### Post-deployment Verification
- [ ] Both domains accessible
- [ ] SSL certificates working
- [ ] Wallet integration functional
- [ ] No impact on existing attestAI.io users

---

## Quick Commands Reference

```bash
# Check VM resources
htop
df -h

# Test domains
curl -I https://attestai.io
curl -I https://secretgptee.com

# Check nginx
nginx -t
systemctl status nginx

# View logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

## Emergency Contacts & Resources

- **Domain Registrar:** [To be documented]
- **VM Provider:** [To be documented]  
- **SSL Certificate Authority:** Let's Encrypt
- **Keplr Documentation:** https://docs.keplr.app/
- **Secret Network Docs:** https://docs.scrt.network/

---
*This document should be the primary reference when starting the Claude Code build phase.*
