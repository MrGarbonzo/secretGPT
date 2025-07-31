# SecretGPTee UI - Secret Network Branded Interface Plan

## Overview
SecretGPTee is the consumer-focused web interface for secretGPT, featuring Secret Network branding, Keplr wallet integration, and comprehensive attestation monitoring. This UI runs alongside the existing attestAI interface on the same VM and backend infrastructure with **dual-domain support** (attestai.io + secretgptee.com).

## Dual-Domain Architecture Plan

### **Domain Strategy**
- **attestai.io** - Existing technical/educational interface
- **secretgptee.com** - New consumer-focused interface with wallet features
- **Shared Backend** - Single FastAPI app serves both domains
- **Domain-Based Routing** - Middleware routes requests based on Host header

### **Infrastructure Architecture**
```
DNS Layer:
attestai.io ────────┐
www.attestai.io ────┤
                    ├──→ Nginx Reverse Proxy ──→ FastAPI App (Port 8000)
secretgptee.com ────┤                            └──→ Hub Router & Services
www.secretgptee.com ┘

Backend Services (Shared):
├── SecretGPT Hub Router
├── Secret AI Service  
├── MCP Service
├── Wallet Proxy Service (New)
└── Attestation Service
```

### **Implementation Approach: INTEGRATED BUILD**
**Recommendation: Build dual-domain support as part of SecretGPTee implementation**

#### **Why Integrated Approach:**
✅ **Single codebase** - Easier to maintain and deploy
✅ **Shared infrastructure** - Nginx, SSL, monitoring
✅ **Atomic deployment** - Both UIs update together
✅ **Consistent backend** - No API version drift between UIs
✅ **Simpler development** - One server to run and debug
✅ **Resource efficiency** - Single process, shared connections

#### **File Structure Integration:**
```
F:\coding\secretGPT\
├── main.py                           # Updated for dual-domain support
├── interfaces/
│   ├── multi_ui_service.py          # NEW: Domain routing service
│   ├── web_ui/                      # Existing attestAI (unchanged)
│   │   ├── app.py
│   │   ├── service.py
│   │   ├── static/
│   │   └── templates/
│   └── secretgptee_ui/              # NEW: SecretGPTee interface
│       ├── app.py                   # SecretGPTee FastAPI routes
│       ├── service.py               # Hub integration
│       ├── static/
│       │   ├── css/secretgptee.css  # Secret Network styling
│       │   └── js/
│       │       ├── wallet.js        # Keplr integration
│       │       ├── chat.js          # Chat interface
│       │       └── attestation.js   # Status monitoring
│       └── templates/
│           ├── base.html            # Secret Network branding
│           ├── index.html           # Main chat interface
│           └── components/
├── services/
│   └── wallet_service/              # NEW: Wallet proxy service
│       ├── proxy.py                 # Bridge to secret_network_mcp
│       └── __init__.py
├── deployment/                      # NEW: Infrastructure as code
│   ├── nginx/
│   │   └── dual-domain.conf        # Nginx configuration
│   ├── ssl/
│   │   └── setup-ssl.sh            # SSL certificate automation
│   └── docker/
│       └── docker-compose.dual.yml # Dual-domain deployment
└── docs/
    └── dual-domain-setup.md        # Deployment guide
```

## Secret Network Branding & Design System

### **Primary Colors**
```css
:root {
    /* Secret Network Official Brand Colors */
    --secret-blue: #1B1F3A;           /* Dark navy blue - primary */
    --secret-purple: #6C5CE7;         /* Vibrant purple - secondary */
    --secret-cyan: #00D4FF;           /* Bright cyan - accent */
    --secret-pink: #FF6B9D;           /* Accent pink - highlights */
    
    /* UI Background Colors */
    --bg-primary: #0F1419;            /* Almost black background */
    --bg-secondary: #1E2328;          /* Dark gray cards */
    --bg-card: #252A2F;               /* Elevated surfaces */
    --bg-glass: rgba(255, 255, 255, 0.05); /* Glassmorphism */
    
    /* Text Colors */
    --text-primary: #FFFFFF;          /* Primary text */
    --text-secondary: #8B949E;        /* Secondary text */
    --text-muted: #6E7681;            /* Muted text */
    
    /* Status Colors */
    --status-ok: #00D4FF;             /* Connected/Success */
    --status-warning: #FFB800;        /* Checking/Warning */
    --status-error: #FF4757;          /* Error/Disconnected */
    
    /* Gradients */
    --gradient-primary: linear-gradient(135deg, var(--secret-blue) 0%, var(--secret-purple) 100%);
    --gradient-accent: linear-gradient(135deg, var(--secret-cyan) 0%, var(--secret-pink) 100%);
    --gradient-card: linear-gradient(145deg, #1E2328 0%, #252A2F 100%);
}
```

### **Typography & Spacing**
- **Font Family**: Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui
- **Font Weights**: 400 (regular), 500 (medium), 600 (semibold), 700 (bold)
- **Border Radius**: 8px (standard), 12px (cards), 50% (circles)
- **Shadows**: Subtle with Secret Network color tints
- **Spacing Scale**: 0.25rem, 0.5rem, 0.75rem, 1rem, 1.5rem, 2rem, 3rem

## Dual-Domain Implementation Details

### **1. Multi-UI Service (Core Infrastructure)**
```python
# interfaces/multi_ui_service.py
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
import os

class MultiWebUIService:
    def __init__(self, hub_router):
        self.hub = hub_router
        self.app = FastAPI(
            title="SecretGPT Dual-Domain Service",
            description="Serves both AttestAI and SecretGPTee interfaces"
        )
        self._setup_middleware()
        self._setup_domain_routing()
    
    def _setup_middleware(self):
        # CORS for both domains
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=[
                "https://attestai.io",
                "https://www.attestai.io", 
                "https://secretgptee.com",
                "https://www.secretgptee.com",
                "http://localhost:8000",  # Development
                "http://local.attestai.io:8000",
                "http://local.secretgptee.com:8000"
            ],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Domain routing middleware
        @self.app.middleware("http")
        async def domain_router(request: Request, call_next):
            host = request.headers.get("host", "").lower()
            original_path = request.url.path
            
            # Route based on domain
            if any(domain in host for domain in ["attestai.io", "local.attestai.io"]):
                # AttestAI domain - route to /attestai
                if not original_path.startswith("/attestai"):
                    request.scope["path"] = f"/attestai{original_path}"
            elif any(domain in host for domain in ["secretgptee.com", "local.secretgptee.com"]):
                # SecretGPTee domain - route to /secretgptee  
                if not original_path.startswith("/secretgptee"):
                    request.scope["path"] = f"/secretgptee{original_path}"
            
            response = await call_next(request)
            
            # Add domain-specific headers
            if "attestai" in host:
                response.headers["X-Service"] = "AttestAI"
            elif "secretgptee" in host:
                response.headers["X-Service"] = "SecretGPTee"
            
            return response
    
    def _setup_domain_routing(self):
        # Import and create sub-applications
        from .web_ui.app import create_attestai_app
        from .secretgptee_ui.app import create_secretgptee_app
        
        # Create sub-applications with hub integration
        attestai_app = create_attestai_app(self.hub)
        secretgptee_app = create_secretgptee_app(self.hub)
        
        # Mount sub-applications
        self.app.mount("/attestai", attestai_app)
        self.app.mount("/secretgptee", secretgptee_app)
        
        # Shared API endpoints (both domains can access)
        self._setup_shared_api()
        
        # Health check endpoint
        @self.app.get("/api/system/status")
        async def system_status():
            return {
                "success": True,
                "service": "SecretGPT Dual-Domain",
                "domains": ["attestai.io", "secretgptee.com"],
                "interfaces": ["attestai", "secretgptee"],
                "backend_services": ["secret_ai", "mcp_service", "wallet_proxy", "attestation"]
            }
        
        # Domain detection endpoint (for debugging)
        @self.app.get("/api/system/domain-info")
        async def domain_info(request: Request):
            host = request.headers.get("host", "unknown")
            return {
                "detected_host": host,
                "original_path": str(request.url.path),
                "routed_path": request.scope.get("path", "not_modified"),
                "timestamp": "2025-07-30T12:00:00Z"
            }
    
    def _setup_shared_api(self):
        """API endpoints shared between both UIs"""
        
        # Chat endpoint (both UIs use this)
        @self.app.post("/api/chat/message")
        async def chat_message(request: Request):
            # Determine source UI from domain
            host = request.headers.get("host", "")
            source_ui = "attestai" if "attestai" in host else "secretgptee"
            
            # Route through hub with UI context
            body = await request.json()
            response = await self.hub.route_message(
                interface=source_ui,
                message=body.get("message", ""),
                options=body.get("options", {})
            )
            return response
        
        # Attestation endpoints (both UIs show status)
        @self.app.get("/api/attestation/status")
        async def attestation_status():
            return await self.hub.get_attestation_status()
        
        # Wallet endpoints (primarily for SecretGPTee, but AttestAI can show read-only)
        @self.app.post("/api/wallet/connect")
        async def wallet_connect(request: Request):
            body = await request.json()
            return await self.hub.connect_wallet(
                address=body.get("address"),
                name=body.get("name"),
                is_hardware=body.get("isHardwareWallet", False)
            )
    
    def get_fastapi_app(self):
        return self.app
```

### **2. Updated Main Application**
```python
# main.py - Updated for dual-domain support
import os
from enum import Enum

# Add new component types
class ComponentType(Enum):
    SECRET_AI = "secret_ai"
    MCP_SERVICE = "mcp_service"
    WEB_UI = "web_ui"                    # Legacy - keep for compatibility
    MULTI_WEB_UI = "multi_web_ui"        # NEW: Dual-domain service
    WALLET_PROXY = "wallet_proxy"        # NEW: Wallet integration
    ATTESTATION_SERVICE = "attestation_service"

async def run_with_dual_domains():
    """Run secretGPT with dual-domain support (attestai.io + secretgptee.com)"""
    hub = None
    multi_ui_service = None
    
    def signal_handler(sig, frame):
        logger.info(f"Received signal {sig}, shutting down...")
        if hub:
            asyncio.create_task(hub.shutdown())
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Initialize hub router
        hub = HubRouter()
        
        # Initialize core services
        logger.info("Initializing Secret AI service...")
        secret_ai = SecretAIService()
        hub.register_component(ComponentType.SECRET_AI, secret_ai)
        
        logger.info("Initializing MCP service...")
        mcp_service = HTTPMCPService()
        hub.register_component(ComponentType.MCP_SERVICE, mcp_service)
        
        # Initialize wallet proxy service (for SecretGPTee)
        logger.info("Initializing Wallet Proxy service...")
        from services.wallet_service.proxy import WalletProxyService
        wallet_proxy = WalletProxyService()
        hub.register_component(ComponentType.WALLET_PROXY, wallet_proxy)
        
        # Initialize the hub
        await hub.initialize()
        
        # Initialize multi-UI service (handles both domains)
        logger.info("Initializing Multi-UI service...")
        from interfaces.multi_ui_service import MultiWebUIService
        multi_ui_service = MultiWebUIService(hub)
        hub.register_component(ComponentType.MULTI_WEB_UI, multi_ui_service)
        
        # Get the FastAPI app
        app = multi_ui_service.get_fastapi_app()
        
        # Start server
        import uvicorn
        config = uvicorn.Config(
            app=app,
            host=os.getenv("SECRETGPT_HUB_HOST", "0.0.0.0"),
            port=int(os.getenv("SECRETGPT_HUB_PORT", "8000")),
            log_level=settings.log_level.lower(),
            access_log=True
        )
        server = uvicorn.Server(config)
        
        # System status
        status = await hub.get_system_status()
        logger.info(f"System status: {status}")
        
        logger.info("SecretGPT Dual-Domain Service started successfully")
        logger.info(f"AttestAI available at: https://attestai.io")
        logger.info(f"SecretGPTee available at: https://secretgptee.com")
        logger.info(f"Local development: http://localhost:{config.port}")
        
        # Run the server
        await server.serve()
        
    except Exception as e:
        logger.error(f"Service error: {e}")
        raise
    finally:
        if multi_ui_service:
            logger.info("Shutting down Multi-UI service...")
        if hub:
            logger.info("Shutting down hub...")
            await hub.shutdown()
            logger.info("Hub shutdown complete")

async def main():
    """Main entry point - now supports dual domains"""
    logger.info("Starting secretGPT Hub - Dual Domain Edition")
    
    if not validate_settings():
        logger.error("Invalid settings configuration")
        return
    
    run_mode = os.getenv("SECRETGPT_RUN_MODE", "service").lower()
    enable_dual_domains = os.getenv("SECRETGPT_ENABLE_DUAL_DOMAINS", "true").lower() == "true"
    
    if run_mode == "service":
        if enable_dual_domains:
            await run_with_dual_domains()  # NEW: Dual-domain mode
        else:
            await run_with_web_ui()        # Legacy single UI mode
    else:
        logger.error(f"Unknown run mode: {run_mode}")
```

### **3. Wallet Proxy Service**
```python
# services/wallet_service/proxy.py
import aiohttp
import os
from typing import Dict, Any, Optional

class WalletProxyService:
    """Proxy service to communicate with secret_network_mcp on VM2"""
    
    def __init__(self):
        self.mcp_base_url = os.getenv("SECRET_NETWORK_MCP_URL", "http://secret-network-mcp:8002")
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def initialize(self):
        """Initialize the proxy service"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30)
        )
        
        # Test connection to secret_network_mcp
        try:
            await self._health_check()
            return {"success": True, "message": "Wallet proxy initialized"}
        except Exception as e:
            return {"success": False, "error": f"Failed to connect to MCP service: {e}"}
    
    async def _health_check(self) -> Dict[str, Any]:
        """Check if secret_network_mcp is accessible"""
        async with self.session.get(f"{self.mcp_base_url}/api/health") as response:
            return await response.json()
    
    async def connect_wallet(self, address: str, name: str = None, is_hardware: bool = False) -> Dict[str, Any]:
        """Forward wallet connection to secret_network_mcp"""
        try:
            payload = {
                "address": address,
                "name": name or "Keplr Wallet",
                "isHardwareWallet": is_hardware
            }
            
            async with self.session.post(
                f"{self.mcp_base_url}/api/wallet/connect",
                json=payload
            ) as response:
                result = await response.json()
                return result
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Wallet connection failed: {str(e)}"
            }
    
    async def get_wallet_balance(self, address: str) -> Dict[str, Any]:
        """Get wallet balance from secret_network_mcp"""
        try:
            async with self.session.get(
                f"{self.mcp_base_url}/api/wallet/balance/{address}"
            ) as response:
                result = await response.json()
                return result
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Balance query failed: {str(e)}"
            }
    
    async def get_transaction_status(self, tx_hash: str) -> Dict[str, Any]:
        """Check transaction status via secret_network_mcp"""
        try:
            async with self.session.get(
                f"{self.mcp_base_url}/api/wallet/transaction/{tx_hash}"
            ) as response:
                result = await response.json()
                return result
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Transaction status query failed: {str(e)}"
            }
    
    async def get_status(self) -> Dict[str, Any]:
        """Get wallet service status"""
        try:
            mcp_status = await self._health_check()
            return {
                "success": True,
                "service": "Wallet Proxy",
                "mcp_connection": mcp_status.get("success", False),
                "mcp_url": self.mcp_base_url
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Status check failed: {str(e)}"
            }
    
    async def cleanup(self):
        """Clean shutdown"""
        if self.session:
            await self.session.close()
```

## Infrastructure Deployment Plan

### **1. Nginx Configuration**
```nginx
# deployment/nginx/dual-domain.conf
# Dual-domain Nginx configuration for attestai.io + secretgptee.com

# Rate limiting
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
limit_req_zone $binary_remote_addr zone=chat:10m rate=5r/s;

# Upstream backend
upstream secretgpt_backend {
    server 127.0.0.1:8000;
    keepalive 32;
}

# Main server block - handles both domains
server {
    listen 443 ssl http2;
    server_name attestai.io www.attestai.io secretgptee.com www.secretgptee.com;
    
    # SSL Configuration (multi-domain certificate)
    ssl_certificate /etc/letsencrypt/live/attestai.io/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/attestai.io/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin";
    
    # Content Security Policy (domain-specific)
    set $csp_default "default-src 'self'";
    set $csp_script "script-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com";
    set $csp_style "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com";
    set $csp_font "font-src 'self' https://fonts.gstatic.com";
    set $csp_connect "connect-src 'self'";
    
    # Add Keplr CSP for SecretGPTee domain
    if ($host ~* "secretgptee") {
        set $csp_script "${csp_script} chrome-extension:// moz-extension://";
        set $csp_connect "${csp_connect} https://api.secret.network wss://api.secret.network";
    }
    
    add_header Content-Security-Policy "${csp_default}; ${csp_script}; ${csp_style}; ${csp_font}; ${csp_connect}";
    
    # Logging with domain identification
    access_log /var/log/nginx/secretgpt_access.log combined;
    error_log /var/log/nginx/secretgpt_error.log;
    
    # Main application proxy
    location / {
        # Rate limiting for general requests
        limit_req zone=api burst=20 nodelay;
        
        proxy_pass http://secretgpt_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Chat API with stricter rate limiting
    location /api/chat/ {
        limit_req zone=chat burst=10 nodelay;
        
        proxy_pass http://secretgpt_backend;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Longer timeout for AI responses
        proxy_read_timeout 120s;
    }
    
    # WebSocket support for real-time features
    location /ws/ {
        proxy_pass http://secretgpt_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket timeouts
        proxy_read_timeout 3600s;
        proxy_send_timeout 3600s;
    }
    
    # Static files with caching
    location /static/ {
        proxy_pass http://secretgpt_backend;
        proxy_cache_valid 200 1h;
        add_header Cache-Control "public, max-age=3600";
        expires 1h;
    }
    
    # Health check endpoint
    location /api/system/status {
        proxy_pass http://secretgpt_backend;
        access_log off;
    }
}

# HTTP to HTTPS redirect for both domains
server {
    listen 80;
    server_name attestai.io www.attestai.io secretgptee.com www.secretgptee.com;
    return 301 https://$server_name$request_uri;
}

# Redirect www to non-www (optional - choose one)
server {
    listen 443 ssl http2;
    server_name www.attestai.io www.secretgptee.com;
    
    ssl_certificate /etc/letsencrypt/live/attestai.io/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/attestai.io/privkey.pem;
    
    return 301 https://$server_name$request_uri;
}
```

### **2. SSL Certificate Setup**
```bash
#!/bin/bash
# deployment/ssl/setup-ssl.sh
# Automated SSL certificate setup for both domains

set -e

echo "Setting up SSL certificates for dual domains..."

# Install certbot if not already installed
if ! command -v certbot &> /dev/null; then
    echo "Installing certbot..."
    sudo apt update
    sudo apt install -y certbot python3-certbot-nginx
fi

# Stop nginx temporarily for certificate generation
sudo systemctl stop nginx

# Generate multi-domain certificate
echo "Generating SSL certificate for both domains..."
sudo certbot certonly --standalone \
    -d attestai.io \
    -d www.attestai.io \
    -d secretgptee.com \
    -d www.secretgptee.com \
    --email your-email@example.com \
    --agree-tos \
    --no-eff-email

# Copy nginx configuration
echo "Installing nginx configuration..."
sudo cp deployment/nginx/dual-domain.conf /etc/nginx/sites-available/secretgpt-dual
sudo ln -sf /etc/nginx/sites-available/secretgpt-dual /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test nginx configuration
echo "Testing nginx configuration..."
sudo nginx -t

# Start nginx
sudo systemctl start nginx
sudo systemctl enable nginx

# Setup auto-renewal
echo "Setting up SSL auto-renewal..."
sudo crontab -l | grep -v certbot | sudo crontab -
(sudo crontab -l 2>/dev/null; echo "0 12 * * * /usr/bin/certbot renew --quiet --nginx") | sudo crontab -

echo "SSL setup complete!"
echo "AttestAI: https://attestai.io"
echo "SecretGPTee: https://secretgptee.com"
```

### **3. Docker Deployment**
```yaml
# deployment/docker/docker-compose.dual.yml
version: '3.8'

services:
  secretgpt-dual:
    build:
      context: ../..
      dockerfile: Dockerfile
    container_name: secretgpt-dual-domain
    ports:
      - "8000:8000"
    environment:
      - SECRETGPT_RUN_MODE=service
      - SECRETGPT_ENABLE_DUAL_DOMAINS=true
      - SECRETGPT_HUB_HOST=0.0.0.0
      - SECRETGPT_HUB_PORT=8000
      - SECRET_NETWORK_MCP_URL=http://secret-network-mcp:8002
      - ATTESTAI_DOMAIN=attestai.io
      - SECRETGPTEE_DOMAIN=secretgptee.com
    volumes:
      - ./logs:/app/logs
      - ./data:/app/data
    networks:
      - secretgpt-network
    depends_on:
      - secret-network-mcp
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/system/status"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  secret-network-mcp:
    image: secret-network-mcp:latest
    container_name: secret-network-mcp
    ports:
      - "8002:8002"
    environment:
      - PORT=8002
      - SECRET_NODE_URL=https://rpc.ankr.com/http/scrt_cosmos
      - SECRET_CHAIN_ID=secret-4
    networks:
      - secretgpt-network
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    container_name: secretgpt-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/dual-domain.conf:/etc/nginx/conf.d/default.conf
      - /etc/letsencrypt:/etc/letsencrypt:ro
      - ./logs/nginx:/var/log/nginx
    depends_on:
      - secretgpt-dual
    networks:
      - secretgpt-network
    restart: unless-stopped

networks:
  secretgpt-network:
    driver: bridge

volumes:
  logs:
  data:
```

## SecretGPTee UI Components

### **1. Base Template with Secret Network Branding**
```html
<!-- interfaces/secretgptee_ui/templates/base.html -->
<!DOCTYPE html>
<html lang="en" data-theme="secret-dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}SecretGPTee - Private AI powered by Secret Network{% endblock %}</title>
    
    <!-- Meta tags for SEO and social -->
    <meta name="description" content="Private AI conversations powered by Secret Network. Chat with AI while maintaining complete privacy and control over your data.">
    <meta name="keywords" content="AI, Secret Network, Privacy, Blockchain, Keplr, Wallet, Chat">
    <meta property="og:title" content="SecretGPTee - Private AI">
    <meta property="og:description" content="Private AI powered by Secret Network">
    <meta property="og:type" content="website">
    <meta property="og:url" content="https://secretgptee.com">
    
    <!-- Favicon -->
    <link rel="icon" type="image/svg+xml" href="/static/assets/secretgptee-favicon.svg">
    <link rel="alternate icon" href="/static/assets/secretgptee-favicon.ico">
    
    <!-- Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    
    <!-- Font Awesome for icons -->
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    
    <!-- SecretGPTee CSS -->
    <link href="/static/css/secretgptee.css" rel="stylesheet">
    
    <!-- Keplr wallet detection -->
    <script>
        window.keplrReady = new Promise((resolve) => {
            if (window.keplr) {
                resolve(true);
            } else {
                window.addEventListener('keplr_keystorechange', () => resolve(true));
                // Timeout after 3 seconds if Keplr not detected
                setTimeout(() => resolve(false), 3000);
            }
        });
    </script>
    
    {% block extra_head %}{% endblock %}
</head>
<body>
    <!-- Navigation Header -->
    <nav class="navbar">
        <div class="nav-container">
            <!-- Logo and Brand -->
            <div class="nav-brand">
                <div class="brand-logo">
                    <img src="/static/assets/secret-logo.svg" alt="Secret Network" class="secret-logo">
                    <span class="brand-text">SecretGPTee</span>
                </div>
                <div class="brand-tagline">Private AI</div>
            </div>
            
            <!-- Navigation Items -->
            <div class="nav-items">
                <!-- Attestation Status (Compact) -->
                <div class="nav-status" id="nav-attestation-status">
                    <div class="status-indicators">
                        <div class="status-dot status-ok" id="status-hub"></div>
                        <div class="status-dot status-ok" id="status-ai"></div>
                        <div class="status-dot status-ok" id="status-mcp"></div>
                        <div class="status-dot status-ok" id="status-bridge"></div>
                    </div>
                    <span class="status-text">All Systems</span>
                </div>
                
                <!-- Wallet Connection -->
                <div class="nav-wallet" id="wallet-container">
                    <button class="wallet-connect-btn" id="connect-wallet-btn" style="display: none;">
                        <i class="fab fa-ethereum"></i>
                        <span>Connect Wallet</span>
                    </button>
                    <div class="wallet-connected" id="wallet-connected" style="display: none;">
                        <div class="wallet-balance" id="wallet-balance">0 SCRT</div>
                        <div class="wallet-address" id="wallet-address">secret1...</div>
                    </div>
                </div>
                
                <!-- Settings -->
                <button class="nav-btn" id="settings-btn" title="Settings">
                    <i class="fas fa-cog"></i>
                </button>
                
                <!-- Menu Toggle (Mobile) -->
                <button class="nav-toggle" id="nav-toggle">
                    <span></span>
                    <span></span>
                    <span></span>
                </button>
            </div>
        </div>
    </nav>

    <!-- Main Content Area -->
    <main class="main-content">
        {% block content %}{% endblock %}
    </main>

    <!-- Footer -->
    <footer class="footer">
        <div class="footer-content">
            <div class="footer-section">
                <h4>SecretGPTee</h4>
                <p>Private AI powered by Secret Network</p>
            </div>
            <div class="footer-section">
                <h4>Privacy</h4>
                <ul>
                    <li><a href="/privacy">Privacy Policy</a></li>
                    <li><a href="/security">Security</a></li>
                    <li><a href="/attestation">Attestation</a></li>
                </ul>
            </div>
            <div class="footer-section">
                <h4>Resources</h4>
                <ul>
                    <li><a href="https://docs.secret.network" target="_blank">Secret Network Docs</a></li>
                    <li><a href="https://wallet.keplr.app" target="_blank">Keplr Wallet</a></li>
                    <li><a href="/api/docs" target="_blank">API Documentation</a></li>
                </ul>
            </div>
            <div class="footer-section">
                <div class="footer-logo">
                    <img src="/static/assets/secret-logo.svg" alt="Secret Network">
                </div>
                <p class="footer-tagline">Built on Secret Network</p>
            </div>
        </div>
        <div class="footer-bottom">
            <p>&copy; 2025 SecretGPTee. Powered by Secret Network.</p>
        </div>
    </footer>

    <!-- Settings Panel Overlay -->
    <div class="settings-overlay" id="settings-overlay" style="display: none;">
        <div class="settings-panel" id="settings-panel">
            <!-- Settings content will be loaded here -->
        </div>
    </div>

    <!-- Attestation Detail Panel -->
    <div class="attestation-overlay" id="attestation-overlay" style="display: none;">
        <div class="attestation-panel" id="attestation-panel">
            <!-- Attestation details will be loaded here -->
        </div>
    </div>

    <!-- Transaction Confirmation Modal -->
    <div class="modal-overlay" id="transaction-modal" style="display: none;">
        <div class="modal-content">
            <div class="modal-header">
                <h3>Confirm Transaction</h3>
                <button class="modal-close" onclick="closeTransactionModal()">×</button>
            </div>
            <div class="modal-body">
                <div class="transaction-details">
                    <div class="tx-detail">
                        <label>Amount:</label>
                        <span id="tx-amount">0 SCRT</span>
                    </div>
                    <div class="tx-detail">
                        <label>Recipient:</label>
                        <span id="tx-recipient">secret1...</span>
                    </div>
                    <div class="tx-detail">
                        <label>Gas Fee:</label>
                        <span id="tx-gas">~0.025 SCRT</span>
                    </div>
                </div>
            </div>
            <div class="modal-footer">
                <button class="btn-secondary" onclick="closeTransactionModal()">Cancel</button>
                <button class="btn-primary" id="confirm-transaction-btn">Confirm Transaction</button>
            </div>
        </div>
    </div>

    <!-- Core JavaScript Libraries -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/axios/1.6.0/axios.min.js"></script>
    
    <!-- SecretJS for wallet integration -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/secretjs/1.12.0/index.min.js"></script>
    
    <!-- SecretGPTee Application Scripts -->
    <script src="/static/js/app.js"></script>
    <script src="/static/js/wallet.js"></script>
    <script src="/static/js/attestation.js"></script>
    <script src="/static/js/chat.js"></script>
    <script src="/static/js/settings.js"></script>
    
    {% block extra_scripts %}{% endblock %}
    
    <!-- Initialize Application -->
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            // Initialize SecretGPTee application
            SecretGPTeeApp.init();
            
            // Start attestation monitoring
            AttestationMonitor.startMonitoring();
            
            // Initialize wallet detection
            WalletIntegration.detectWallet();
        });
    </script>
</body>
</html>
```

### **2. Main Chat Interface**
```html
<!-- interfaces/secretgptee_ui/templates/index.html -->
{% extends "base.html" %}

{% block title %}SecretGPTee - Private AI Chat{% endblock %}

{% block content %}
<div class="chat-app">
    <!-- Sidebar (Collapsible) -->
    <aside class="sidebar" id="sidebar">
        <div class="sidebar-header">
            <h3>Conversations</h3>
            <button class="sidebar-toggle" id="sidebar-toggle">
                <i class="fas fa-times"></i>
            </button>
        </div>
        
        <div class="sidebar-content">
            <!-- New Chat Button -->
            <button class="new-chat-btn" id="new-chat-btn">
                <i class="fas fa-plus"></i>
                <span>New Chat</span>
            </button>
            
            <!-- Conversation History -->
            <div class="conversation-list" id="conversation-list">
                <div class="conversation-group">
                    <div class="group-header">Today</div>
                    <div class="conversation-item active">
                        <div class="conversation-preview">
                            <div class="conversation-title">Secret Network Overview</div>
                            <div class="conversation-snippet">What is Secret Network...</div>
                        </div>
                        <div class="conversation-actions">
                            <button class="action-btn" title="Delete">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </div>
                    <div class="conversation-item">
                        <div class="conversation-preview">
                            <div class="conversation-title">SCRT Token Staking</div>
                            <div class="conversation-snippet">How to stake SCRT tokens...</div>
                        </div>
                        <div class="conversation-actions">
                            <button class="action-btn" title="Delete">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </div>
                </div>
                
                <div class="conversation-group">
                    <div class="group-header">Yesterday</div>
                    <div class="conversation-item">
                        <div class="conversation-preview">
                            <div class="conversation-title">Keplr Wallet Setup</div>
                            <div class="conversation-snippet">Setting up Keplr wallet...</div>
                        </div>
                        <div class="conversation-actions">
                            <button class="action-btn" title="Delete">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="sidebar-footer">
            <!-- Quick Stats -->
            <div class="quick-stats">
                <div class="stat-item">
                    <span class="stat-label">Conversations</span>
                    <span class="stat-value">12</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">This Month</span>
                    <span class="stat-value">48</span>
                </div>
            </div>
        </div>
    </aside>

    <!-- Main Chat Area -->
    <div class="chat-main">
        <!-- Chat Header -->
        <div class="chat-header">
            <div class="chat-title">
                <button class="sidebar-open-btn" id="sidebar-open-btn">
                    <i class="fas fa-bars"></i>
                </button>
                <h2>Private AI Chat</h2>
            </div>
            
            <!-- Chat Controls -->
            <div class="chat-controls">
                <div class="temperature-control">
                    <label for="temperature-slider">Creativity</label>
                    <input type="range" id="temperature-slider" min="0" max="1" step="0.1" value="0.7">
                    <span id="temperature-value">0.7</span>
                </div>
                
                <button class="control-btn" id="export-chat-btn" title="Export Chat">
                    <i class="fas fa-download"></i>
                </button>
                
                <button class="control-btn" id="clear-chat-btn" title="Clear Chat">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        </div>

        <!-- Messages Container -->
        <div class="messages-container" id="messages-container">
            <!-- Welcome Message -->
            <div class="message-wrapper">
                <div class="message assistant-message welcome-message">
                    <div class="message-avatar">
                        <img src="/static/assets/secret-logo.svg" alt="SecretGPTee">
                    </div>
                    <div class="message-content">
                        <div class="message-header">
                            <span class="message-sender">SecretGPTee</span>
                            <div class="trust-indicators">
                                <span class="trust-badge verified" title="Fully Attested">
                                    <i class="fas fa-shield-alt"></i>
                                    Verified
                                </span>
                                <span class="privacy-badge" title="Private & Encrypted">
                                    <i class="fas fa-lock"></i>
                                    Private
                                </span>
                            </div>
                        </div>
                        <div class="message-text">
                            <h3>Welcome to SecretGPTee! 🔮</h3>
                            <p>Your private AI assistant powered by Secret Network. Your conversations are:</p>
                            <ul>
                                <li><strong>🔒 Private</strong> - End-to-end encrypted</li>
                                <li><strong>🛡️ Secure</strong> - Running in trusted execution environment</li>
                                <li><strong>🔑 Yours</strong> - You control your data</li>
                            </ul>
                            <p>Connect your Keplr wallet to unlock blockchain features like sending SCRT, checking balances, and interacting with Secret contracts!</p>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Chat messages will be dynamically added here -->
        </div>

        <!-- Typing Indicators -->
        <div class="typing-indicator" id="typing-indicator" style="display: none;">
            <div class="message-wrapper">
                <div class="message assistant-message">
                    <div class="message-avatar">
                        <img src="/static/assets/secret-logo.svg" alt="SecretGPTee">
                    </div>
                    <div class="message-content">
                        <div class="typing-animation">
                            <div class="typing-dot"></div>
                            <div class="typing-dot"></div>
                            <div class="typing-dot"></div>
                        </div>
                        <span class="typing-text">SecretGPTee is thinking...</span>
                    </div>
                </div>
            </div>
        </div>

        <!-- Input Area -->
        <div class="input-area">
            <div class="input-container">
                <!-- Attachment Button -->
                <button class="input-btn" id="attachment-btn" title="Attach File">
                    <i class="fas fa-paperclip"></i>
                </button>
                
                <!-- Message Input -->
                <div class="input-wrapper">
                    <textarea 
                        id="message-input" 
                        placeholder="Ask me anything... Try 'What's my SCRT balance?' or 'Send 10 SCRT to secret1...'"
                        rows="1"></textarea>
                    <div class="input-suggestions" id="input-suggestions" style="display: none;">
                        <!-- Dynamic suggestions will appear here -->
                    </div>
                </div>
                
                <!-- Voice Input Button -->
                <button class="input-btn" id="voice-btn" title="Voice Input">
                    <i class="fas fa-microphone"></i>
                </button>
                
                <!-- Send Button -->
                <button class="send-btn" id="send-btn" disabled>
                    <i class="fas fa-paper-plane"></i>
                </button>
            </div>
            
            <!-- Input Footer -->
            <div class="input-footer">
                <div class="input-status">
                    <span class="char-count" id="char-count">0</span>
                    <span class="model-info">DeepSeek R1 70B</span>
                </div>
                <div class="input-shortcuts">
                    <kbd>Enter</kbd> to send • <kbd>Shift + Enter</kbd> for new line
                </div>
            </div>
        </div>
    </div>
</div>

<!-- Quick Actions Floating Menu -->
<div class="quick-actions" id="quick-actions">
    <button class="quick-action-btn" id="wallet-quick-btn" title="Wallet Actions">
        <i class="fas fa-wallet"></i>
    </button>
    <button class="quick-action-btn" id="attestation-quick-btn" title="Security Status">
        <i class="fas fa-shield-alt"></i>
    </button>
    <button class="quick-action-btn" id="export-quick-btn" title="Export Chat">
        <i class="fas fa-download"></i>
    </button>
</div>
{% endblock %}

{% block extra_scripts %}
<script>
// Initialize chat interface
document.addEventListener('DOMContentLoaded', function() {
    ChatInterface.init();
    
    // Auto-resize textarea
    const messageInput = document.getElementById('message-input');
    messageInput.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = Math.min(this.scrollHeight, 120) + 'px';
        
        // Update character count
        document.getElementById('char-count').textContent = this.value.length;
        
        // Enable/disable send button
        document.getElementById('send-btn').disabled = this.value.trim().length === 0;
    });
    
    // Handle Enter key
    messageInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            if (this.value.trim()) {
                ChatInterface.sendMessage(this.value.trim());
            }
        }
    });
    
    // Send button click
    document.getElementById('send-btn').addEventListener('click', function() {
        const input = document.getElementById('message-input');
        if (input.value.trim()) {
            ChatInterface.sendMessage(input.value.trim());
        }
    });
    
    // Temperature slider
    document.getElementById('temperature-slider').addEventListener('input', function() {
        document.getElementById('temperature-value').textContent = this.value;
        ChatInterface.updateTemperature(parseFloat(this.value));
    });
});
</script>
{% endblock %}
```

## Implementation Phases with Dual-Domain Support

### **Phase 1: Dual-Domain Infrastructure (Week 1-2)**
- [ ] **Day 1-2**: Purchase secretgptee.com domain and configure DNS
- [ ] **Day 3-4**: Create multi_ui_service.py with domain routing
- [ ] **Day 5-6**: Update main.py for dual-domain support
- [ ] **Day 7-8**: Setup SSL certificates and Nginx configuration
- [ ] **Day 9-10**: Create wallet proxy service structure
- [ ] **Day 11-14**: Test domain routing and basic infrastructure

### **Phase 2: SecretGPTee UI Foundation (Week 3-4)**  
- [ ] **Day 15-18**: Create secretgptee_ui directory structure
- [ ] **Day 19-22**: Build base templates with Secret Network branding
- [ ] **Day 23-26**: Implement core chat interface with Secret styling
- [ ] **Day 27-28**: Integrate with hub router and test basic functionality

### **Phase 3: Wallet Integration (Week 5-6)**
- [ ] **Day 29-32**: Implement Keplr wallet connection UI components
- [ ] **Day 33-36**: Build wallet proxy service for secret_network_mcp bridge
- [ ] **Day 37-40**: Add wallet balance display and management features
- [ ] **Day 41-42**: Test end-to-end wallet connectivity

### **Phase 4: Attestation & Advanced Features (Week 7-8)**
- [ ] **Day 43-46**: Build four-component attestation monitoring system
- [ ] **Day 47-50**: Create comprehensive settings panel
- [ ] **Day 51-54**: Add natural language transaction processing
- [ ] **Day 55-56**: Final testing and performance optimization

## Success Metrics & Monitoring

### **User Experience Metrics**
- **Time to first chat**: < 3 seconds for both domains
- **Wallet connection success rate**: > 95% on secretgptee.com
- **Domain routing accuracy**: 100% correct UI served
- **Cross-domain API latency**: < 200ms average
- **SSL/TLS performance**: A+ grade on both domains

### **Technical Performance**
- **Page load time**: < 2 seconds for both UIs
- **JavaScript bundle size**: < 500KB per UI
- **Shared backend efficiency**: < 50MB memory per session
- **Attestation status updates**: < 5 seconds latency
- **Dual-domain overhead**: < 10% additional resource usage

### **Infrastructure Reliability**
- **Domain availability**: 99.9% uptime for both domains
- **SSL certificate auto-renewal**: 100% success rate
- **Backend service health**: 99.9% availability
- **Cross-VM communication**: < 1% packet loss to secret_network_mcp
- **Security posture**: Zero SSL/TLS vulnerabilities

### **Security & Trust**
- **Attestation verification success**: > 99%
- **Wallet connection security**: Zero private key exposure
- **Transaction confirmation accuracy**: 100%
- **SSL/TLS grade**: A+ for both domains
- **Security audit compliance**: Complete

## Final Recommendations

### **Build Strategy: INTEGRATED APPROACH**

**✅ Include dual-domain infrastructure as part of the SecretGPTee build** because:

1. **Core Infrastructure** - Domain routing is fundamental to serving both UIs
2. **Single Deployment** - Everything updates together, no version mismatches
3. **Shared Resources** - Nginx, SSL, monitoring, logging all unified
4. **Development Efficiency** - One codebase, one server, one deployment process
5. **Future Scalability** - Easy to add more domains/UIs later

### **Implementation Timeline**
- **Total Duration**: 8 weeks
- **Dual-Domain Setup**: Week 1-2 (foundation)
- **SecretGPTee UI**: Week 3-8 (incremental build)
- **Testing & Optimization**: Continuous throughout

### **Resource Requirements**
- **Additional Domain**: ~$15/year for secretgptee.com
- **SSL Certificate**: FREE (Let's Encrypt multi-domain)
- **Server Resources**: Same (shared backend)
- **Development Time**: +2 weeks for dual-domain infrastructure

This comprehensive plan provides everything needed to build SecretGPTee with dual-domain support as an integrated solution. The approach minimizes complexity while maximizing functionality and future flexibility.
