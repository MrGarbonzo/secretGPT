# Secret Panthers NFT Chat - Phase 1 Technical Build Guide

## Overview
This guide provides complete technical instructions for building Phase 1 of the Secret Panthers NFT chat interface. Phase 1 implements NFT-gated access to an LLM chat with blockchain integration capabilities.

## Architecture Summary
- **Domain**: secretpanthers.com
- **Integration**: Extends existing secretGPT hub multi-domain routing
- **Reuse Strategy**: 90%+ code reuse from SecretGPTee interface
- **New Development**: NFT verification layer + Panther theming

## Prerequisites
- Working secretGPT hub deployment
- NFT contract for testing (Jack Robbins Collection provided)
- Keplr wallet for testing
- Test wallet with/without NFTs from test collection

---

## Section 1: Infrastructure Setup

### 1.1 Component Registration

**File to modify**: `hub/core/router.py`

Add new component type to enum (line ~17):
```python
class ComponentType(Enum):
    SECRET_AI = "secret_ai"
    WEB_UI = "web_ui"
    MCP_SERVICE = "mcp_service"
    MULTI_UI_SERVICE = "multi_ui_service"
    SECRET_GPTEE_UI = "secret_gptee_ui"
    WALLET_PROXY = "wallet_proxy"
    PANTHER_NFT_UI = "panther_nft_ui"  # NEW
```

### 1.2 Directory Structure Creation

Create the following directory structure by copying from SecretGPTee:
```
interfaces/
├── panther_nft/           [NEW - Copy from secret_gptee]
│   ├── app.py            [Copy & modify]
│   ├── service.py        [Copy & modify]
│   ├── templates/        [Copy all]
│   │   └── index.html    [Modify branding]
│   └── static/           [Copy all]
│       ├── css/
│       │   ├── main.css  [Copy from secret_gptee]
│       │   └── panther-theme.css [NEW]
│       └── js/
│           ├── wallet.js [Copy - no changes needed]
│           ├── chat.js   [Copy - no changes needed]
│           ├── app.js    [Copy & add NFT check]
│           └── *.js      [Copy all other files]
```

### 1.3 Domain Routing Configuration

**File to modify**: `interfaces/multi_ui_service.py`

Add domain mappings (around line 44):
```python
self.domain_mappings = {
    "attestai.io": "attest_ai",
    "www.attestai.io": "attest_ai",
    "secretgptee.com": "secret_gptee",
    "www.secretgptee.com": "secret_gptee",
    "secretpanthers.com": "panther_nft",      # NEW
    "www.secretpanthers.com": "panther_nft",  # NEW
    # Development domains
    "localhost": "attest_ai",
    "127.0.0.1": "attest_ai",
    "0.0.0.0": "attest_ai"
}
```

Add service initialization (around line 66):
```python
# Initialize Panther NFT service
logger.info("Initializing Panther NFT service...")
try:
    from interfaces.panther_nft.service import PantherNFTService
    self.panther_nft_service = PantherNFTService(self.hub_router)
except ImportError as e:
    logger.warning(f"Panther NFT service not available: {e}")
    self.panther_nft_service = None
```

Add mounting configuration (around line 101):
```python
# Mount Panther NFT interface  
if self.panther_nft_service:
    panther_nft_app = self.panther_nft_service.get_fastapi_app()
    self.app.mount("/panther_nft", panther_nft_app, name="panther_nft")
    logger.info("Panther NFT interface mounted at /panther_nft")
```

---

## Section 2: Interface Implementation

### 2.1 Service Layer

**Create file**: `interfaces/panther_nft/service.py`

Copy from: `interfaces/secret_gptee/service.py`

Key modifications:
1. Change all "SecretGPTee" references to "PantherNFT"
2. Update component type to `ComponentType.PANTHER_NFT_UI`
3. Add NFT verification status to get_status() method

### 2.2 Application Layer

**Create file**: `interfaces/panther_nft/app.py`

Copy from: `interfaces/secret_gptee/app.py`

Key modifications:
1. Update class name to `PantherNFTInterface`
2. Change title/description strings
3. Add NFT verification endpoint
4. Modify chat endpoint to check NFT ownership
5. Pass contract address to templates:

```python
# In the home route
@self.app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Panther NFT main page - NFT gated chat interface"""
    import os
    return self.templates.TemplateResponse(
        "index.html", 
        {
            "request": request, 
            "title": "Secret Panthers - NFT Gated AI Chat",
            "interface_type": "panther_nft",
            "panther_nft_contract": os.getenv('PANTHER_NFT_CONTRACT', 'secret10xgnqk9rfggdemk9qlfsvw4lkc4ph2sjhr7eav'),
            "panther_contract_hash": os.getenv('PANTHER_CONTRACT_HASH', '')
        }
    )
```
5. Pass contract address to templates:

```python
# In the home route
@self.app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Panther NFT main page - NFT gated chat interface"""
    import os
    return self.templates.TemplateResponse(
        "index.html", 
        {
            "request": request, 
            "title": "Secret Panthers - NFT Gated AI Chat",
            "interface_type": "panther_nft",
            "panther_nft_contract": os.getenv('PANTHER_NFT_CONTRACT', 'secret10xgnqk9rfggdemk9qlfsvw4lkc4ph2sjhr7eav'),
            "panther_contract_hash": os.getenv('PANTHER_CONTRACT_HASH', '')
        }
    )
```

Add NFT verification route (after line 95):
```python
@self.app.post("/api/v1/verify_nft")
async def verify_nft_ownership(request: Request):
    """
    Verify Panthers NFT ownership for the connected wallet
    Uses MCP service to query the blockchain
    """
    try:
        data = await request.json()
        wallet_address = data.get("wallet_address")
        
        if not wallet_address:
            raise HTTPException(status_code=400, detail="Wallet address required")
        
        # Use MCP service to query NFT ownership
        mcp_service = self.hub_router.get_component(ComponentType.MCP_SERVICE)
        if not mcp_service:
            raise HTTPException(status_code=503, detail="Blockchain service unavailable")
        
        # Get contract from environment (set in Dockerfile)
        import os
        PANTHERS_NFT_CONTRACT = os.getenv('PANTHER_NFT_CONTRACT', 'secret10xgnqk9rfggdemk9qlfsvw4lkc4ph2sjhr7eav')
        
        # Query Panthers NFT contract
        query_result = await mcp_service.execute_tool(
            "query_contract",
            {
                "contract_address": PANTHERS_NFT_CONTRACT,
                "query": {
                    "tokens": {
                        "owner": wallet_address,
                        "limit": 1
                    }
                }
            }
        )
        
        # Check if user owns any Panthers
        has_nft = len(query_result.get("tokens", [])) > 0
        
        return {
            "success": True,
            "has_nft": has_nft,
            "token_count": len(query_result.get("tokens", [])),
            "wallet_address": wallet_address
        }
        
    except Exception as e:
        logger.error(f"NFT verification error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

---

## Section 3: Frontend Implementation

### 3.1 HTML Template

**Copy and modify**: `interfaces/panther_nft/templates/index.html`

Source: `interfaces/secret_gptee/templates/index.html`

Key changes:
1. Update title to "Secret Panthers - NFT Gated AI Chat"
2. Add Panther branding elements
3. Include NFT verification UI component
4. Add access denied message for non-holders
5. Pass contract address from backend to frontend:

```html
<!-- Add this script tag before other JS files -->
<script>
    // Pass environment variables from backend to frontend
    window.PANTHER_NFT_CONTRACT = '{{ panther_nft_contract }}';
    window.PANTHER_CONTRACT_HASH = '{{ panther_contract_hash }}';
</script>
```
5. Pass contract address from backend to frontend:

```html
<!-- Add this script tag before other JS files -->
<script>
    // Pass environment variables from backend to frontend
    window.PANTHER_NFT_CONTRACT = '{{ panther_nft_contract }}';
    window.PANTHER_CONTRACT_HASH = '{{ panther_contract_hash }}';
</script>
```

### 3.2 Wallet Integration (No Changes Needed)

**Copy file**: `interfaces/panther_nft/static/js/wallet.js`

Source: `interfaces/secret_gptee/static/js/wallet.js`

This file already contains complete Keplr integration:
- Wallet connection flow
- SecretJS initialization
- Balance queries
- Transaction capabilities

### 3.3 NFT Verification Logic with Permit

**Modify file**: `interfaces/panther_nft/static/js/app.js`

Add NFT verification after wallet connection (around line 150):
```javascript
// Configuration - Get from environment (set in Dockerfile)
const NFT_CONTRACT = window.PANTHER_NFT_CONTRACT || 'secret10xgnqk9rfggdemk9qlfsvw4lkc4ph2sjhr7eav';
const CONTRACT_CODE_HASH = window.PANTHER_CONTRACT_HASH || '';  // Optional

// After successful wallet connection
async function onWalletConnected(address) {
    console.log('Wallet connected:', address);
    
    // Verify NFT ownership using permit
    try {
        // Check if we have secretjs instance from wallet.js
        if (!WalletState.secretjs) {
            throw new Error('SecretJS not initialized');
        }
        
        // Generate permit for NFT query
        const permit = await WalletState.secretjs.utils.accessControl.permit.sign(
            address,
            "secret-4",
            "NFTAccess",  // Generic name for testing
            [NFT_CONTRACT],
            ["owner"],
            false
        );
        
        // Store permit for later use
        sessionStorage.setItem('panther_permit', JSON.stringify(permit));
        
        // Send permit to backend for verification
        const response = await fetch('/api/v1/verify_nft', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                wallet_address: address,
                permit: permit,
                contract_address: NFT_CONTRACT,
                code_hash: CONTRACT_CODE_HASH
            })
        });
        
        const result = await response.json();
        
        if (result.has_nft) {
            // Store NFT tokens for Phase 2 (personality traits)
            sessionStorage.setItem('owned_panthers', JSON.stringify(result.tokens));
            
            // Enable chat interface
            document.getElementById('chat-container').style.display = 'block';
            document.getElementById('access-denied').style.display = 'none';
            showNotification(`Panthers NFT verified! You own ${result.token_count} Panther(s).`);
        } else {
            // Show access denied message
            document.getElementById('chat-container').style.display = 'none';
            document.getElementById('access-denied').style.display = 'block';
            showNotification('No Panthers NFT found. Access denied.', 'error');
        }
    } catch (error) {
        console.error('NFT verification failed:', error);
        showNotification('Failed to verify NFT ownership: ' + error.message, 'error');
    }
}
```

### 3.4 Panther Theme CSS (Placeholder - Awaiting Branding)

**Create file**: `interfaces/panther_nft/static/css/panther-theme.css`

**NOTE**: These are placeholder colors. Final branding/artwork pending.

```css
/* Panther Theme Overlay - PLACEHOLDER STYLING */
/* TODO: Update with final branding once available */
:root {
    /* Override SecretGPTee color variables */
    --primary-color: #4B0082;      /* Deep Purple */
    --primary-dark: #310055;       /* Darker Purple */
    --primary-light: #6B46C1;      /* Light Purple */
    --accent-color: #FFD700;       /* Gold accents */
    --bg-primary: #0A0A0A;         /* Near black */
    --bg-secondary: #1A1A2E;       /* Dark blue-purple */
    --text-primary: #E0E0E0;       /* Light gray text */
    --text-secondary: #B0B0B0;     /* Medium gray text */
}

/* Panther-specific styling */
.panther-header {
    background: linear-gradient(135deg, var(--primary-dark) 0%, var(--primary-color) 100%);
    border-bottom: 2px solid var(--accent-color);
}

.panther-logo {
    width: 48px;
    height: 48px;
    filter: drop-shadow(0 0 10px var(--accent-color));
}

/* NFT verification UI */
.nft-gate-container {
    text-align: center;
    padding: 3rem;
    background: var(--bg-secondary);
    border-radius: 12px;
    border: 1px solid var(--primary-light);
}

.access-denied-message {
    color: var(--accent-color);
    font-size: 1.2rem;
    margin: 2rem 0;
}

/* Chat bubbles with Panther style */
.message-bubble {
    background: var(--bg-secondary);
    border-left: 3px solid var(--primary-light);
    box-shadow: 0 2px 10px rgba(75, 0, 130, 0.3);
}

.message-bubble.ai-message {
    background: linear-gradient(90deg, var(--bg-secondary) 0%, rgba(75, 0, 130, 0.1) 100%);
    border-left-color: var(--accent-color);
}
```

---

## Section 4: MCP Integration

### 4.1 MCP Service Configuration

The MCP service is already fully integrated in SecretGPTee. No changes needed.

**Available MCP tools** (from `services/mcp_service/http_mcp_service.py`):
- `query_balance` - Check SCRT balance
- `query_contract` - Query any Secret Network contract
- `send_tokens` - Send SCRT tokens
- `execute_contract` - Execute contract methods

### 4.2 NFT Contract Queries (SNIP-721 with Permits)

**Test Contract (Jack Robbins Collection)**: `secret10xgnqk9rfggdemk9qlfsvw4lkc4ph2sjhr7eav`
**Panthers NFT Contract**: PENDING DEPLOYMENT
**Code Hash**: Can be queried from chain or hardcoded once known

#### Query Tokens with Permit (Preferred Method)

Using permits for privacy-preserving queries:

```javascript
// Generate permit for NFT queries
const permit = await secretjs.utils.accessControl.permit.sign(
    walletAddress,           // User's address
    "secret-4",             // Chain ID (mainnet)
    "NFTAccess",            // Permission name (generic for testing)
    [NFT_CONTRACT],          // Contract address array
    ["owner"],              // Permissions array
    false                    // Allow hash lookup
);

// Query owned tokens using permit
const ownedTokens = await secretjs.query.snip721.GetOwnedTokens({
    contract: { 
        address: NFT_CONTRACT,  // Jack Robbins for testing, Panthers later
        codeHash: CONTRACT_CODE_HASH 
    },
    owner: walletAddress,
    auth: { permit: permit }
});

// Check ownership
const hasNFT = ownedTokens.token_list && ownedTokens.token_list.length > 0;
```

#### Alternative: Query with Viewing Key (Fallback)

```javascript
// If permit fails, fall back to viewing key
const query = {
    tokens: {
        owner: wallet_address,
        viewing_key: viewing_key,
        limit: 100
    }
};
```

#### Query NFT Metadata

```javascript
// Query specific NFT info
const nftInfo = await secretjs.query.snip721.NftInfo({
    contract: { 
        address: PANTHERS_CONTRACT, 
        codeHash: CONTRACT_CODE_HASH 
    },
    token_id: "panther_001"
});

// Query private metadata (requires permit or viewing key)
const privateMetadata = await secretjs.query.snip721.PrivateMetadata({
    contract: { 
        address: PANTHERS_CONTRACT, 
        codeHash: CONTRACT_CODE_HASH 
    },
    token_id: "panther_001",
    auth: { permit: permit }
});
```

---

## Section 5: Environment Configuration

### 5.1 Docker Configuration with Hardcoded Contract

**Update Dockerfile** to include NFT contract directly:
```dockerfile
# After existing ENV statements (around line 30-35)
# Panther NFT Configuration - Hardcoded for secretVM
ENV PANTHER_NFT_ENABLED=true
ENV PANTHER_NFT_CONTRACT=secret10xgnqk9rfggdemk9qlfsvw4lkc4ph2sjhr7eav  # Jack Robbins (TEST)
# TODO: Replace with Panthers contract when deployed
# ENV PANTHER_NFT_CONTRACT=secret1xxxxx  # Future Panthers contract
ENV PANTHER_DOMAIN=secretpanthers.com
ENV PANTHER_CACHE_TTL=300
```

**Only dynamic configuration needs to be in .env**:
```bash
# Existing required variables
SECRET_AI_API_KEY=xxx
SECRET_MCP_URL=http://xxx:8002
SECRETGPT_ENABLE_WEB_UI=true
SECRETGPT_DUAL_DOMAIN=true
```

### 5.2 Docker Configuration

Update `docker-compose.yml` to include new domain:
```yaml
environment:
  - TRUSTED_HOSTS=attestai.io,secretgptee.com,secretpanthers.com
  - CORS_ORIGINS=https://attestai.io,https://secretgptee.com,https://secretpanthers.com
```

---

## Section 6: Testing Checklist

### 6.1 Component Testing
- [ ] Domain routing: secretpanthers.com routes to Panther interface
- [ ] Wallet connection: Keplr connects successfully
- [ ] NFT verification: Contract query returns ownership status
- [ ] Access control: Non-holders see access denied
- [ ] Chat functionality: Holders can send/receive messages
- [ ] MCP tools: Blockchain queries work in chat

### 6.2 Integration Testing
- [ ] Hub router accepts PANTHER_NFT_UI component
- [ ] Messages route through hub to Secret AI
- [ ] Streaming responses display correctly
- [ ] Session persistence maintains NFT verification

### 6.3 User Flow Testing
1. Visit secretpanthers.com
2. See Panther-themed interface
3. Click "Connect Wallet"
4. Keplr popup appears
5. Approve connection
6. NFT verification runs automatically
7. If owner: Chat interface appears
8. If not owner: Access denied message
9. Send test message
10. Receive AI response
11. Test MCP command (e.g., "Check my SCRT balance")

---

## Section 7: Deployment Steps

### 7.1 File Deployment
1. Copy entire `interfaces/secret_gptee` to `interfaces/panther_nft`
2. Apply modifications as outlined above
3. Add panther-theme.css
4. Update multi_ui_service.py
5. Update hub/core/router.py

### 7.2 Configuration Deployment
1. Dockerfile already contains contract address (no .env update needed)
2. Update docker-compose.yml for domain routing only
3. Add SSL certificates for secretpanthers.com
4. Configure DNS to point to server

### 7.3 Launch Sequence
```bash
# Pull latest changes
git pull

# Rebuild container with new interface
docker-compose build

# Start services
docker-compose up -d

# Check logs
docker-compose logs -f secretgpt

# Verify health
curl http://localhost/health
```

---

## Section 8: Code References

### 8.1 Key Files to Reference

**Wallet Integration**:
- `interfaces/secret_gptee/static/js/wallet.js` - Complete Keplr implementation
- `interfaces/secret_gptee/static/js/secretjs-wrapper.js` - SecretJS helpers

**MCP Integration**:
- `services/mcp_service/http_mcp_service.py` - MCP client
- Lines 95-150: Tool execution methods

**Multi-Domain Routing**:
- `interfaces/multi_ui_service.py` - Domain routing logic
- Lines 30-50: Domain mappings
- Lines 120-150: Routing middleware

**Hub Integration**:
- `hub/core/router.py` - Component registration
- Lines 200-300: Message routing logic

### 8.2 Reusable Components

**From SecretGPTee (100% reuse)**:
- Wallet connection flow
- SecretJS initialization
- MCP tool calling
- Chat streaming
- Message handling
- Error handling
- Loading states
- Notification system

**New Development Required**:
- NFT verification endpoint (~50 lines)
- Panther theme CSS (~200 lines)
- Access control logic (~30 lines)
- Domain routing entry (~10 lines)

---

## Section 9: External Requirements

### 9.1 Information Status

#### ✅ Confirmed:
- **Query Method**: SNIP-721 with Permits (code provided)
- **Authentication**: Permit-based queries preferred over viewing keys

#### ✅ Available for Testing:
- **Test NFT Contract**: Jack Robbins Collection (`secret10xgnqk9rfggdemk9qlfsvw4lkc4ph2sjhr7eav`)
- **Purpose**: Gate chat access only (no metadata/traits for Phase 1)

#### ⏳ Pending:
1. **Panthers NFT Contract Address** - Not yet deployed (using Jack Robbins for testing)
2. **Contract Code Hash** - Can query from chain or hardcode
3. **Panther Logo/Assets** - No branding yet (using placeholder theme)
4. **Brand Colors** - TBD (currently using purple/gold placeholder)

#### 🚀 Development Approach:
- Contract address hardcoded in Dockerfile for secretVM deployment
- When Panthers contract deploys, update Dockerfile and rebuild
- Theme can be updated independently once branding is ready

### 9.2 Testing Resources
1. Wallet with Jack Robbins NFT (for positive test)
2. Wallet without Jack Robbins NFT (for negative test)
3. Test contract: `secret10xgnqk9rfggdemk9qlfsvw4lkc4ph2sjhr7eav`
4. Multiple NFT test case (user with >1 NFT from collection)

---

## Section 10: Troubleshooting Guide

### Common Issues and Solutions

**Domain not routing correctly**:
- Check multi_ui_service.py domain mappings
- Verify DNS configuration
- Check nginx/proxy configuration

**Wallet connection failing**:
- Ensure secretjs libraries are loaded
- Check browser console for errors
- Verify Keplr is installed

**NFT verification failing**:
- Confirm contract address is correct
- Check MCP service is running
- Verify query message format
- Check network (mainnet vs testnet)

**Chat not working after verification**:
- Check hub router connection
- Verify Secret AI service is running
- Check browser console for WebSocket errors

---

## Appendix A: File Structure Summary

```
secretGPT/
├── hub/core/router.py                    [Add PANTHER_NFT_UI enum]
├── interfaces/
│   ├── multi_ui_service.py              [Add domain routing]
│   └── panther_nft/                     [NEW - Copy from secret_gptee]
│       ├── service.py                   [Minimal changes]
│       ├── app.py                       [Add NFT verification]
│       ├── templates/index.html         [Update branding]
│       └── static/
│           ├── css/panther-theme.css    [NEW theme file]
│           └── js/                      [Copy all, modify app.js]
└── .env                                 [Add Panther variables]
```

---

## Appendix B: Quick Start Commands

```bash
# 1. Copy SecretGPTee interface
cp -r interfaces/secret_gptee interfaces/panther_nft

# 2. Apply modifications (use this guide)

# 3. Test locally
python main.py

# 4. Build and deploy
docker-compose build && docker-compose up -d

# 5. Monitor logs
docker-compose logs -f secretgpt | grep panther
```

---

## Next Steps for Phase 2

Phase 2 will add personality traits from encrypted NFT metadata:
1. Query and decrypt NFT metadata
2. Extract personality traits array
3. Build dynamic system prompts
4. Inject personality into chat responses
5. UI indicators for active traits
6. Multi-NFT trait switching

This will be documented in `panther-nft-phase2-build-guide.md` after Phase 1 completion.
