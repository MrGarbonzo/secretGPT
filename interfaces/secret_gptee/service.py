"""
SecretGPTee Service Integration with Hub Router
Consumer-focused service with enhanced wallet and blockchain integration
"""
import logging
from pathlib import Path

from hub.core.router import HubRouter, ComponentType
from interfaces.secret_gptee.app import SecretGPTeeInterface

logger = logging.getLogger(__name__)


class SecretGPTeeService:
    """
    SecretGPTee Service that integrates with the hub router
    Enhanced consumer-focused interface with full wallet integration
    """
    
    def __init__(self, hub_router: HubRouter):
        """Initialize SecretGPTee service with hub router integration"""
        self.hub_router = hub_router
        self.secret_gptee_interface = None
        
        logger.info("SecretGPTee service initializing...")
        self._initialize()
    
    def _initialize(self):
        """Initialize SecretGPTee components"""
        try:
            # Initialize FastAPI interface with hub router
            self.secret_gptee_interface = SecretGPTeeInterface(self.hub_router)
            
            logger.info("SecretGPTee service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize SecretGPTee service: {e}")
            raise
    
    def get_fastapi_app(self):
        """Get the FastAPI application for mounting"""
        return self.secret_gptee_interface.get_app()
    
    async def get_status(self):
        """Get SecretGPTee service status"""
        try:
            # Check wallet service availability without circular hub calls
            wallet_service = self.hub_router.get_component(ComponentType.WALLET_PROXY)
            wallet_available = wallet_service is not None
            
            # Check MCP service for blockchain tools without circular hub calls
            mcp_service = self.hub_router.get_component(ComponentType.MCP_SERVICE)
            mcp_available = mcp_service is not None and getattr(mcp_service, 'initialized', False)
            
            return {
                "service": "secret_gptee",
                "status": "operational",
                "interface": "consumer_focused",
                "components": {
                    "fastapi": "operational",
                    "wallet_integration": "operational" if wallet_available else "unavailable",
                    "blockchain_tools": "operational" if mcp_available else "unavailable",
                    "chat_streaming": "operational"
                },
                "hub_connection": "connected",
                "features": {
                    "modern_ui": True,
                    "keplr_wallet": wallet_available,
                    "secret_network_tools": mcp_available,
                    "advanced_settings": True,
                    "mobile_responsive": True,
                    "real_time_streaming": True
                },
                "endpoints": {
                    "chat": "/api/v1/chat",
                    "stream": "/api/v1/chat/stream",
                    "wallet_balance": "/api/v1/wallet/balance",
                    "settings": "/api/v1/settings",
                    "tools": "/api/v1/tools"
                }
            }
        except Exception as e:
            logger.error(f"SecretGPTee status error: {e}")
            return {
                "service": "secret_gptee",
                "status": "error",
                "error": str(e)
            }
    
    async def cleanup(self):
        """Cleanup SecretGPTee service resources"""
        try:
            # Add any cleanup logic here
            logger.info("SecretGPTee service cleanup complete")
        except Exception as e:
            logger.error(f"SecretGPTee cleanup error: {e}")