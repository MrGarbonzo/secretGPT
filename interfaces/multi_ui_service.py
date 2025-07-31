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
            "attestai.io": "attest_ai",
            "www.attestai.io": "attest_ai",
            "secretgptee.com": "secret_gptee", 
            "www.secretgptee.com": "secret_gptee",
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
            except ImportError:
                logger.warning("SecretGPTee service not yet implemented, creating placeholder")
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
        """Setup domain-based routing middleware"""
        
        @self.app.middleware("http")
        async def domain_routing_middleware(request: Request, call_next):
            """Route requests based on domain"""
            try:
                # Extract domain from host header
                host = request.headers.get("host", "").lower()
                domain = host.split(":")[0]  # Remove port if present
                
                # Determine target interface
                interface_type = self.domain_mappings.get(domain, "attest_ai")
                
                # Add interface type to request state for downstream handlers
                request.state.interface_type = interface_type
                request.state.domain = domain
                
                # Log routing decision
                logger.debug(f"Routing request from {domain} to {interface_type}")
                
                response = await call_next(request)
                return response
                
            except Exception as e:
                logger.error(f"Domain routing error: {e}")
                # Fallback to AttestAI interface
                request.state.interface_type = "attest_ai"
                request.state.domain = "fallback"
                response = await call_next(request)
                return response
        
        # Mount interface applications
        self._mount_interface_apps()
    
    def _mount_interface_apps(self):
        """Mount the interface applications with routing logic"""
        
        @self.app.get("/health")
        async def multi_ui_health_check(request: Request):
            """Health check for multi-UI service"""
            try:
                interface_type = getattr(request.state, 'interface_type', 'attest_ai')
                domain = getattr(request.state, 'domain', 'unknown')
                
                # Get hub status
                hub_status = await self.hub_router.get_system_status()
                
                # Get interface-specific status
                interface_status = {}
                if interface_type == "attest_ai" and self.attest_ai_service:
                    interface_status = await self.attest_ai_service.get_status()
                elif interface_type == "secret_gptee" and self.secret_gptee_service:
                    interface_status = await self.secret_gptee_service.get_status()
                
                return {
                    "status": "healthy",
                    "service": "multi_ui",
                    "interface": interface_type,
                    "domain": domain,
                    "hub_status": hub_status,
                    "interface_status": interface_status
                }
            except Exception as e:
                logger.error(f"Multi-UI health check failed: {e}")
                raise HTTPException(status_code=503, detail="Service unavailable")
        
        @self.app.get("/")
        async def root_handler(request: Request):
            """Root handler that routes to appropriate interface"""
            interface_type = getattr(request.state, 'interface_type', 'attest_ai')
            
            if interface_type == "secret_gptee":
                if self.secret_gptee_service:
                    # Route to SecretGPTee interface
                    return await self._route_to_secret_gptee(request)
                else:
                    # SecretGPTee not ready, redirect to AttestAI with notice
                    return RedirectResponse(
                        url="/?notice=secretgptee_coming_soon", 
                        status_code=302
                    )
            else:
                # Route to AttestAI interface
                return await self._route_to_attest_ai(request)
        
        # Setup catch-all routing for interface-specific endpoints
        self._setup_catch_all_routing()
    
    def _setup_catch_all_routing(self):
        """Setup catch-all routing for interface-specific endpoints"""
        
        @self.app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
        async def catch_all_handler(request: Request, path: str):
            """Route all other requests to appropriate interface"""
            interface_type = getattr(request.state, 'interface_type', 'attest_ai')
            
            if interface_type == "secret_gptee" and self.secret_gptee_service:
                return await self._route_to_secret_gptee(request, path)
            else:
                return await self._route_to_attest_ai(request, path)
    
    async def _route_to_attest_ai(self, request: Request, path: str = ""):
        """Route request to AttestAI interface"""
        try:
            if not self.attest_ai_service:
                raise HTTPException(status_code=503, detail="AttestAI service unavailable")
            
            # Get the FastAPI app from AttestAI service
            attest_ai_app = self.attest_ai_service.get_fastapi_app()
            
            # Create a new request for the target app
            # Note: This is a simplified approach - in production, consider using
            # FastAPI sub-applications or a reverse proxy
            scope = request.scope.copy()
            scope["path"] = f"/{path}" if path else "/"
            
            # Use the AttestAI app to handle the request
            from fastapi.testclient import TestClient
            client = TestClient(attest_ai_app)
            
            # Forward the request (simplified - real implementation would preserve all details)
            if request.method == "GET":
                response = client.get(scope["path"], headers=dict(request.headers))
            elif request.method == "POST":
                body = await request.body()
                response = client.post(scope["path"], content=body, headers=dict(request.headers))
            else:
                # Handle other methods as needed
                response = client.get(scope["path"], headers=dict(request.headers))
            
            return response
            
        except Exception as e:
            logger.error(f"Error routing to AttestAI: {e}")
            raise HTTPException(status_code=500, detail="AttestAI routing error")
    
    async def _route_to_secret_gptee(self, request: Request, path: str = ""):
        """Route request to SecretGPTee interface"""
        try:
            if not self.secret_gptee_service:
                raise HTTPException(status_code=503, detail="SecretGPTee service unavailable")
            
            # Similar routing logic for SecretGPTee
            # This will be implemented when SecretGPTee service is created
            secret_gptee_app = self.secret_gptee_service.get_fastapi_app()
            
            # Implement routing logic similar to AttestAI
            # For now, return a placeholder response
            return {
                "message": "SecretGPTee interface",
                "path": path,
                "status": "coming_soon"
            }
            
        except Exception as e:
            logger.error(f"Error routing to SecretGPTee: {e}")
            raise HTTPException(status_code=500, detail="SecretGPTee routing error")
    
    def get_fastapi_app(self) -> FastAPI:
        """Get the FastAPI application instance"""
        return self.app
    
    async def get_status(self) -> Dict[str, Any]:
        """Get multi-UI service status"""
        try:
            hub_status = await self.hub_router.get_system_status()
            
            # Get status from both interfaces
            attest_ai_status = None
            if self.attest_ai_service:
                attest_ai_status = await self.attest_ai_service.get_status()
            
            secret_gptee_status = None
            if self.secret_gptee_service:
                secret_gptee_status = await self.secret_gptee_service.get_status()
            
            return {
                "service": "multi_ui",
                "status": "operational",
                "hub_status": hub_status,
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