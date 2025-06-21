"""
Web UI Service Integration with Hub Router
REFERENCE: Phase 1 Secret AI service for chat integration
"""
import logging
from pathlib import Path

from secretGPT.hub.core.router import HubRouter, ComponentType
from secretGPT.interfaces.web_ui.app import WebUIInterface
from secretGPT.interfaces.web_ui.attestation.service import AttestationService
from secretGPT.interfaces.web_ui.encryption.proof_manager import ProofManager

logger = logging.getLogger(__name__)


class WebUIService:
    """
    Web UI Service that integrates with the hub router
    Replace direct Secret AI calls with hub router calls
    """
    
    def __init__(self, hub_router: HubRouter):
        """Initialize Web UI service with hub router integration"""
        self.hub_router = hub_router
        self.attestation_service = None
        self.proof_manager = None
        self.web_ui_interface = None
        
        logger.info("Web UI service initializing...")
        self._initialize()
    
    def _initialize(self):
        """Initialize all Web UI components"""
        try:
            # Get Secret AI service from hub router for attestation discovery
            secret_ai_service = None
            try:
                secret_ai_service = self.hub_router.get_component(ComponentType.SECRET_AI)
            except Exception as e:
                logger.warning(f"Could not get Secret AI service from hub: {e}")
            
            # Initialize attestation service with Secret AI service for endpoint discovery
            self.attestation_service = AttestationService(secret_ai_service)
            
            # Initialize proof manager with attestation service
            self.proof_manager = ProofManager(self.attestation_service)
            
            # Initialize FastAPI web interface with hub router
            self.web_ui_interface = WebUIInterface(self.hub_router)
            
            # Update web interface to use our services
            self._configure_web_interface()
            
            logger.info("Web UI service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Web UI service: {e}")
            raise
    
    def _configure_web_interface(self):
        """Configure the web interface to use our services"""
        # Monkey patch the web interface to provide service instances
        self.web_ui_interface._attestation_service_instance = self.attestation_service
        self.web_ui_interface._proof_manager_instance = self.proof_manager
        
        logger.info("Web interface configured with services")
    
    def get_fastapi_app(self):
        """Get the FastAPI application for mounting"""
        return self.web_ui_interface.get_app()
    
    async def get_status(self):
        """Get Web UI service status"""
        attestation_status = await self.attestation_service.get_status()
        
        return {
            "service": "web_ui",
            "status": "operational",
            "components": {
                "fastapi": "operational",
                "attestation": attestation_status.get("status", "unknown"),
                "proof_manager": "operational"
            },
            "endpoints": {
                "chat": "/api/v1/chat",
                "attestation": "/api/v1/attestation/self",
                "proof_generation": "/api/v1/proof/generate"
            }
        }
    
    async def cleanup(self):
        """Cleanup Web UI service resources"""
        if self.attestation_service:
            await self.attestation_service.cleanup()
        
        logger.info("Web UI service cleanup complete")