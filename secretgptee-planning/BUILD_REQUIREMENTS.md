# SecretGPTee.com Build Requirements & Planning Document

**Last Updated:** July 28, 2025
**Status:** Planning Phase
**Target Domain:** secretgptee.com

## Project Overview
Tech demo for Secret Network showcasing:
- User-focused website (complementing education-focused attestAI.io)
- Keplr wallet integration
- Verified message signing communication between VMs
- Demonstration of Secret Network capabilities

## Current Architecture
- **attestAI.io** - Education focused (F:\coding\secretGPT)
- **secret_network_mcp** - Working separately (F:\coding\secret_network_mcp)
- **Target VM specs:** 2 vCPUs, 4 GB RAM, 40 GB Storage

## Build Phases

### Phase 1: New Website Foundation ⭐ CURRENT PRIORITY
**Goal:** Create secretgptee.com on same VM as attestAI.io

#### Technical Requirements:
- [ ] Domain routing setup (secretgptee.com)
- [ ] Reverse proxy configuration for multi-site hosting
- [ ] SSL certificate management for both domains
- [ ] User-focused UI/UX design
- [ ] Base website framework/stack decision

#### Key Decisions: 
- ✅ Web framework: Vue.js
- ✅ Build tool: Vite 
- ✅ UI Design: ChatGPT-like layout
- [ ] Styling approach: Tailwind CSS (recommended)
- [ ] Component structure planning

### Phase 2: Keplr Wallet Integration
**Goal:** Connect Keplr wallet functionality from secret_network_mcp VM

#### Technical Requirements:
- [ ] Keplr wallet SDK integration
- [ ] Wallet connection button UI
- [ ] User authentication flow
- [ ] Cross-VM API communication design
- [ ] Error handling for wallet connection failures

#### Constraints:
- ✅ Only on secretgptee.com (NOT on attestAI.io)
- ✅ Wallet logic hosted on secret_network_mcp VM
- ✅ Clean separation between education site and user site

### Phase 3: Verified Message Signing Communication
**Goal:** Replace SSL with verified message signing between VMs

#### Technical Requirements:
- [ ] Asymmetric key pair generation and management
- [ ] Message signing protocol design
- [ ] Key distribution strategy
- [ ] Key rotation mechanism
- [ ] API endpoint security implementation

#### Security Considerations:
- [ ] Key storage location and security
- [ ] Message replay attack prevention
- [ ] Timestamp validation
- [ ] Signature verification performance

## Infrastructure Decisions

### Hosting Strategy: ✅ DECIDED - Same VM
**Rationale:** 
- Low expected traffic (tech demo)
- Cost efficiency
- Simplified management
- Adequate resources for demo purposes

### Routing Strategy: TBD
**Options:**
1. **Reverse Proxy (nginx/Apache)** - Route by domain name
2. **Different Ports** - Requires port in URL
3. **Subdomain Routing** - Complicates SSL management

**Recommendation:** Reverse proxy for clean domain routing

## Resource Planning

### Current VM Utilization: TBD
- [ ] Assess current attestAI.io resource usage
- [ ] Monitor CPU/RAM patterns
- [ ] Determine headroom available

### Performance Requirements:
- [ ] Expected concurrent users
- [ ] Response time targets
- [ ] Wallet connection speed requirements

## Development Environment Setup

### For Claude Code Build:
- [ ] Target VM specifications
- [ ] Development environment requirements
- [ ] Deployment pipeline design
- [ ] Testing strategy

### Prerequisites:
- [ ] Domain DNS configuration
- [ ] SSL certificate acquisition
- [ ] VM access credentials
- [ ] Development dependencies list

## Documentation Needs

### Technical Docs:
- [ ] API specification for VM communication
- [ ] Keplr integration guide
- [ ] Message signing protocol documentation
- [ ] Deployment procedures

### User Docs:
- [ ] Wallet connection instructions
- [ ] Troubleshooting guide
- [ ] Demo walkthrough scripts

## Risk Assessment

### Technical Risks:
- [ ] VM resource constraints under load
- [ ] Cross-VM communication reliability
- [ ] Keplr wallet compatibility issues
- [ ] SSL/domain configuration complexity

### Mitigation Strategies:
- [ ] Resource monitoring setup
- [ ] Fallback communication methods
- [ ] Wallet connection error handling
- [ ] Backup domain configuration

## Next Steps

### Immediate Actions:
1. [ ] Finalize web framework choice
2. [ ] Create basic website structure
3. [ ] Set up domain routing architecture
4. [ ] Design user-focused content strategy

### Questions to Resolve:
1. What specific Secret Network features should the demo highlight?
2. What user journey should the demo follow?
3. What's the primary call-to-action for secretgptee.com?
4. How technical should the user interface be?

---

## Notes & Ideas
*Use this section for brainstorming and capturing ideas during planning*

- Consider progressive web app features for mobile demo
- Potential integration with Secret Network testnet vs mainnet
- Demo script for presentations
- Analytics tracking for demo engagement
