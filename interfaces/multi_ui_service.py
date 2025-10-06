"""
Multi-UI Service Infrastructure for Dual-Domain Routing
Supports both AttestAI (attestai.io) and SecretGPTee (secretgptee.com) interfaces
"""
import logging
from typing import Dict, Any, Optional
from urllib.parse import urlparse

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from hub.core.router import HubRouter, ComponentType
from interfaces.web_ui.service import WebUIService

logger = logging.getLogger(__name__)


class MultiUIService:
    """
    Multi-UI service that routes requests to appropriate interfaces based on domain
    - attestai.io -> AttestAI interface (existing Web UI)
    - secretgptee.com -> SecretGPTee interface (new consumer UI)
    """
    
    def __init__(self, hub_router: HubRouter):
        """Initialize multi-UI service with hub router integration"""
        self.hub_router = hub_router
        self.app = FastAPI(
            title="SecretGPT Multi-UI Service",
            description="Dual-domain routing for AttestAI and SecretGPTee interfaces",
            version="1.0.0"
        )
        
        # UI service instances
        self.attest_ai_service = None
        self.secret_gptee_service = None
        
        # Domain mappings
        self.domain_mappings = {
            "attestai.io": "attest_ai",  # AttestAI interface
            "www.attestai.io": "attest_ai",  # AttestAI interface
            "secretgptee.com": "secret_gptee",  # SecretGPTee interface
            "www.secretgptee.com": "secret_gptee",  # SecretGPTee interface
            # Development domains
            "localhost": "attest_ai",  # Default to AttestAI for localhost
            "127.0.0.1": "attest_ai",
            "0.0.0.0": "attest_ai"
        }
        
        # Initialize services
        self._initialize_services()
        
        # Setup middleware and routing
        self._setup_middleware()
        self._setup_domain_routing()
        
        logger.info("Multi-UI service initialized")
    
    def _initialize_services(self):
        """Initialize both UI services"""
        try:
            # Initialize AttestAI service (existing Web UI)
            logger.info("Initializing AttestAI service...")
            self.attest_ai_service = WebUIService(self.hub_router)
            
            # Initialize SecretGPTee service (will be created)
            logger.info("Initializing SecretGPTee service...")
            try:
                from interfaces.secret_gptee.service import SecretGPTeeService
                self.secret_gptee_service = SecretGPTeeService(self.hub_router)
            except ImportError as e:
                logger.warning(f"SecretGPTee service not available: {e}")
                self.secret_gptee_service = None
            except Exception as e:
                logger.error(f"Failed to initialize SecretGPTee service: {e}")
                self.secret_gptee_service = None
            
            logger.info("UI services initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize UI services: {e}")
            raise
    
    def _setup_middleware(self):
        """Setup FastAPI middleware"""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Configure appropriately for production
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    def _setup_domain_routing(self):
        """Setup domain-based routing using FastAPI sub-application mounting"""
        
        # Mount interface applications as sub-apps
        try:
            # Mount AttestAI interface
            if self.attest_ai_service:
                attest_ai_app = self.attest_ai_service.get_fastapi_app()
                self.app.mount("/attest_ai", attest_ai_app, name="attest_ai")
                logger.info("AttestAI interface mounted at /attest_ai")
            
            # Mount SecretGPTee interface  
            if self.secret_gptee_service:
                secret_gptee_app = self.secret_gptee_service.get_fastapi_app()
                self.app.mount("/secret_gptee", secret_gptee_app, name="secret_gptee")
                logger.info("SecretGPTee interface mounted at /secret_gptee")
        
        except Exception as e:
            logger.error(f"Failed to mount interface applications: {e}")
        
        # Setup domain routing middleware
        @self.app.middleware("http")
        async def domain_routing_middleware(request: Request, call_next):
            """Route requests based on domain or query parameter override"""
            try:
                # Extract domain from host header
                host = request.headers.get("host", "").lower()
                domain = host.split(":")[0]  # Remove port if present

                # Check for UI override in query parameters (highest priority)
                ui_override = request.query_params.get('ui')
                if ui_override:
                    # Map friendly names to interface types
                    ui_mappings = {
                        'secretgptee': 'secret_gptee',
                        'attestai': 'attest_ai',
                        'secret_gptee': 'secret_gptee',
                        'attest_ai': 'attest_ai',
                        'secret-gptee': 'secret_gptee',  # Alternative format
                        'attest-ai': 'attest_ai'  # Alternative format
                    }
                    interface_type = ui_mappings.get(ui_override.lower())
                    if not interface_type:
                        # If invalid UI parameter, fall back to domain-based routing
                        logger.warning(f"Invalid UI parameter: {ui_override}, falling back to domain routing")
                        interface_type = self.domain_mappings.get(domain, "attest_ai")
                    else:
                        logger.info(f"UI override detected: ?ui={ui_override} -> {interface_type}")
                else:
                    # Check if path already indicates interface type
                    if request.url.path.startswith("/secret_gptee"):
                        interface_type = "secret_gptee"
                    elif request.url.path.startswith("/attest_ai"):
                        interface_type = "attest_ai"
                    else:
                        # Fall back to domain-based routing
                        interface_type = self.domain_mappings.get(domain, "attest_ai")
                
                # Rewrite path based on domain - avoid double prefixes
                original_path = request.url.path
                
                # Only rewrite if path doesn't already have the correct prefix
                if not original_path.startswith(("/attest_ai", "/secret_gptee")):
                    if interface_type == "secret_gptee":
                        request.scope["path"] = f"/secret_gptee{original_path}"
                    else:
                        request.scope["path"] = f"/attest_ai{original_path}"
                # If path already has wrong prefix, fix it
                elif interface_type == "secret_gptee" and original_path.startswith("/attest_ai"):
                    request.scope["path"] = original_path.replace("/attest_ai", "/secret_gptee", 1)
                elif interface_type == "attest_ai" and original_path.startswith("/secret_gptee"):
                    request.scope["path"] = original_path.replace("/secret_gptee", "/attest_ai", 1)
                # If path already has correct prefix, don't change it
                elif interface_type == "secret_gptee" and original_path.startswith("/secret_gptee"):
                    pass  # Keep the path as is
                elif interface_type == "attest_ai" and original_path.startswith("/attest_ai"):
                    pass  # Keep the path as is
                
                # Add interface type to request state for downstream handlers
                request.state.interface_type = interface_type
                request.state.domain = domain
                
                # Log routing decision
                if original_path != request.scope["path"]:
                    logger.info(f"Domain routing: {domain} -> {original_path} -> {request.scope['path']} ({interface_type})")
                else:
                    logger.debug(f"No path rewrite needed: {original_path} for {interface_type}")
                
                response = await call_next(request)
                return response
                
            except Exception as e:
                logger.error(f"Domain routing error: {e}")
                # Fallback to AttestAI interface
                request.state.interface_type = "attest_ai"
                request.state.domain = "fallback"
                response = await call_next(request)
                return response
        
        # Setup health check and basic endpoints
        self._setup_basic_endpoints()
    
    def _setup_basic_endpoints(self):
        """Setup basic endpoints for multi-UI service"""
        
        @self.app.get("/health")
        async def multi_ui_health_check(request: Request):
            """Health check for multi-UI service"""
            try:
                interface_type = getattr(request.state, 'interface_type', 'attest_ai')
                domain = getattr(request.state, 'domain', 'unknown')
                
                # Simple health check without circular hub calls
                interface_available = False
                if interface_type == "attest_ai" and self.attest_ai_service:
                    interface_available = True
                elif interface_type == "secret_gptee" and self.secret_gptee_service:
                    interface_available = True
                
                return {
                    "status": "healthy",
                    "service": "multi_ui",
                    "interface": interface_type,
                    "domain": domain,
                    "hub_connection": "connected",
                    "interface_available": interface_available
                }
            except Exception as e:
                logger.error(f"Multi-UI health check failed: {e}")
                raise HTTPException(status_code=503, detail="Service unavailable")
        
        @self.app.get("/api/system/status")
        async def system_status():
            """Get system status for debugging"""
            return {
                "success": True,
                "service": "SecretGPT Multi-Domain",
                "domains": list(self.domain_mappings.keys()),
                "interfaces": {
                    "attest_ai": self.attest_ai_service is not None,
                    "secret_gptee": self.secret_gptee_service is not None
                },
                "mounted_apps": ["/attest_ai", "/secret_gptee"]
            }
    
    def get_fastapi_app(self) -> FastAPI:
        """Get the FastAPI application instance"""
        return self.app
    
    async def get_status(self) -> Dict[str, Any]:
        """Get multi-UI service status"""
        try:
            # Get safe status from both interfaces without circular hub calls
            attest_ai_status = await self._get_safe_service_status(self.attest_ai_service)
            secret_gptee_status = await self._get_safe_service_status(self.secret_gptee_service)
            
            return {
                "service": "multi_ui",
                "status": "operational",
                "hub_connection": "connected",
                "interfaces": {
                    "attest_ai": attest_ai_status,
                    "secret_gptee": secret_gptee_status
                },
                "domain_mappings": self.domain_mappings,
                "features": {
                    "dual_domain_routing": True,
                    "attest_ai_ready": self.attest_ai_service is not None,
                    "secret_gptee_ready": self.secret_gptee_service is not None
                }
            }
        except Exception as e:
            logger.error(f"Multi-UI status error: {e}")
            return {
                "service": "multi_ui",
                "status": "error",
                "error": str(e)
            }
    
    async def _get_safe_service_status(self, service) -> Dict[str, Any]:
        """Get service status without circular hub calls"""
        if not service:
            return {"status": "unavailable"}
        
        try:
            # Return simplified status to avoid circular references
            return {
                "status": "operational",
                "service_type": type(service).__name__,
                "available": True
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "available": False
            }
    
    async def cleanup(self):
        """Cleanup multi-UI service resources"""
        try:
            if self.attest_ai_service:
                await self.attest_ai_service.cleanup()
            
            if self.secret_gptee_service:
                await self.secret_gptee_service.cleanup()
            
            logger.info("Multi-UI service cleanup complete")
        except Exception as e:
            logger.error(f"Multi-UI cleanup error: {e}")