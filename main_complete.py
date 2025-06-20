"""
secretGPT Hub - Complete Integration
Includes Secret AI and Web UI components
"""
import asyncio
import logging
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from secretGPT.hub.core.router import HubRouter, ComponentType
from secretGPT.services.secret_ai.client import SecretAIService
from secretGPT.interfaces.web_ui.service import WebUIService
from secretGPT.config.settings import settings, validate_settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def run_complete_server():
    """Run the complete secretGPT server"""
    
    # Validate settings
    if not validate_settings():
        logger.error("Invalid settings configuration")
        return
    
    logger.info("Starting secretGPT Hub - Complete Integration")
    
    # Initialize hub router
    hub = HubRouter()
    
    # Initialize and register Secret AI service
    logger.info("Initializing Secret AI service...")
    secret_ai = SecretAIService()
    hub.register_component(ComponentType.SECRET_AI, secret_ai)
    
    # Initialize and register Web UI service
    web_ui_service = None
    if settings.enable_web_ui:
        logger.info("Initializing Web UI service...")
        web_ui_service = WebUIService(hub)
        hub.register_component(ComponentType.WEB_UI, web_ui_service)
    else:
        logger.info("Web UI disabled via configuration")
    
    # Initialize the hub
    await hub.initialize()
    
    # Get system status
    status = await hub.get_system_status()
    logger.info(f"System status: {status}")
    
    # Start services
    try:
        # Start web server if Web UI is enabled
        if web_ui_service:
            import uvicorn
            
            # Get the FastAPI app from web UI service
            app = web_ui_service.get_fastapi_app()
            
            logger.info(f"Starting web server on {settings.hub_host}:{settings.hub_port}")
            
            # Configure uvicorn
            config = uvicorn.Config(
                app=app,
                host=settings.hub_host,
                port=settings.hub_port,
                log_level=settings.log_level.lower(),
                access_log=True
            )
            
            server = uvicorn.Server(config)
            await server.serve()
        else:
            logger.info("No services to run - exiting")
    
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    
    finally:
        # Cleanup all services
        logger.info("Shutting down services...")
        
        # Stop Web UI
        if web_ui_service:
            try:
                await web_ui_service.cleanup()
            except Exception as e:
                logger.error(f"Error stopping Web UI: {e}")
        
        # Stop hub
        await hub.shutdown()


async def test_integration():
    """Test integration with all components"""
    logger.info("Testing secretGPT complete integration...")
    
    # Initialize hub router
    hub = HubRouter()
    
    # Initialize and register Secret AI service
    logger.info("Initializing Secret AI service...")
    secret_ai = SecretAIService()
    hub.register_component(ComponentType.SECRET_AI, secret_ai)
    
    # Initialize and register Web UI service
    logger.info("Initializing Web UI service...")
    web_ui_service = WebUIService(hub)
    hub.register_component(ComponentType.WEB_UI, web_ui_service)
    
    # Initialize the hub
    await hub.initialize()
    
    # Test hub routing from Web UI
    test_message = "What is confidential computing?"
    
    logger.info("Testing Web UI routing...")
    web_response = await hub.route_message(
        interface="web_ui",
        message=test_message,
        options={"temperature": 0.7}
    )
    
    if web_response["success"]:
        logger.info(f"Web UI routing test: SUCCESS (response length: {len(web_response['content'])})")
    else:
        logger.error(f"Web UI routing test: FAILED - {web_response['error']}")
    
    # Test system status
    system_status = await hub.get_system_status()
    logger.info(f"System status: {system_status}")
    
    # Test component statuses
    if web_ui_service:
        web_ui_status = await web_ui_service.get_status()
        logger.info(f"Web UI status: {web_ui_status}")
    
    # Cleanup
    try:
        if web_ui_service:
            await web_ui_service.cleanup()
        await hub.shutdown()
    except Exception as e:
        logger.warning(f"Cleanup warning: {e}")
    
    logger.info("Integration test complete")


async def main():
    """Main entry point"""
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        await test_integration()
    else:
        await run_complete_server()


if __name__ == "__main__":
    asyncio.run(main())