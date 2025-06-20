"""
secretGPT Hub - Phase 2: Web UI Integration
Includes all Phase 1 functionality plus Web UI with attestation
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


async def run_web_ui_server():
    """Run the Web UI server with hub integration"""
    
    # Validate settings
    if not validate_settings():
        logger.error("Invalid settings configuration")
        return
    
    logger.info("Starting secretGPT Hub - Phase 2 (Web UI)")
    
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
    
    # Get system status
    status = await hub.get_system_status()
    logger.info(f"System status: {status}")
    
    # Start the web server
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
    
    try:
        await server.serve()
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    finally:
        # Cleanup
        await web_ui_service.cleanup()
        await hub.shutdown()


async def test_phase2_integration():
    """Test Phase 2 integration without starting web server"""
    logger.info("Testing Phase 2 integration...")
    
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
    
    # Test hub routing
    test_message = "What is the capital of France?"
    logger.info(f"Testing hub routing with: {test_message}")
    
    response = await hub.route_message(
        interface="web_ui",
        message=test_message,
        options={
            "temperature": 0.7,
            "system_prompt": "You are a helpful geography assistant."
        }
    )
    
    if response["success"]:
        logger.info(f"Hub routing test: SUCCESS")
        logger.info(f"Response length: {len(response['content'])} characters")
    else:
        logger.error(f"Hub routing test: FAILED - {response['error']}")
    
    # Test attestation service
    logger.info("Testing attestation service...")
    try:
        attestation_status = await web_ui_service.attestation_service.get_status()
        logger.info(f"Attestation service status: {attestation_status}")
        
        # Test self attestation (will use mock data in development)
        self_attestation = await web_ui_service.attestation_service.get_self_attestation()
        logger.info(f"Self attestation test: {'SUCCESS' if self_attestation['success'] else 'FAILED'}")
        
    except Exception as e:
        logger.error(f"Attestation service test failed: {e}")
    
    # Test Web UI service status
    web_ui_status = await web_ui_service.get_status()
    logger.info(f"Web UI service status: {web_ui_status}")
    
    # Cleanup
    await web_ui_service.cleanup()
    await hub.shutdown()
    
    logger.info("Phase 2 integration test complete")


async def main():
    """Main entry point"""
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        await test_phase2_integration()
    else:
        await run_web_ui_server()


if __name__ == "__main__":
    asyncio.run(main())