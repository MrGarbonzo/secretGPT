"""
secretGPT Hub - Unified Main Entry Point
Supports both basic service mode and full Web UI with attestation
"""
import asyncio
import logging
import sys
import signal
import os
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from hub.core.router import HubRouter, ComponentType
from services.secret_ai.client import SecretAIService
from config.settings import settings, validate_settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_secret_ai_integration():
    """Test the Secret AI integration through the hub"""
    # Initialize hub router
    hub = HubRouter()
    
    # Initialize and register Secret AI service
    logger.info("Initializing Secret AI service...")
    secret_ai = SecretAIService()
    hub.register_component(ComponentType.SECRET_AI, secret_ai)
    
    # Initialize the hub
    await hub.initialize()
    
    # Get system status
    status = await hub.get_system_status()
    logger.info(f"System status: {status}")
    
    # Get available models
    models = await hub.get_available_models()
    logger.info(f"Available models: {models}")
    
    # Test message routing
    test_message = "What is the capital of France?"
    logger.info(f"Testing message routing with: {test_message}")
    
    response = await hub.route_message(
        interface="test_console",
        message=test_message,
        options={
            "temperature": 0.7,
            "system_prompt": "You are a helpful geography assistant."
        }
    )
    
    if response["success"]:
        logger.info(f"Response received successfully (length: {len(response['content'])} chars)")
    else:
        logger.error(f"Error: {response['error']}")
    
    # Shutdown
    await hub.shutdown()


async def run_service_mode():
    """Run the hub in persistent service mode without Web UI"""
    # Global hub instance for signal handling
    hub = None
    
    def signal_handler(sig, frame):
        """Handle shutdown signals gracefully"""
        logger.info(f"Received signal {sig}, shutting down...")
        if hub:
            asyncio.create_task(hub.shutdown())
    
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Initialize hub router
        hub = HubRouter()
        
        # Initialize and register Secret AI service
        logger.info("Initializing Secret AI service...")
        secret_ai = SecretAIService()
        hub.register_component(ComponentType.SECRET_AI, secret_ai)
        
        # Initialize the hub
        await hub.initialize()
        
        # Get system status
        status = await hub.get_system_status()
        logger.info(f"System status: {status}")
        
        # Get available models
        models = await hub.get_available_models()
        logger.info(f"Available models: {models}")
        
        logger.info("secretGPT Hub service started successfully")
        logger.info("Hub is running in service mode - use Ctrl+C to stop")
        
        # Keep the service running
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt, shutting down...")
        
    except Exception as e:
        logger.error(f"Service error: {e}")
        raise
    finally:
        if hub:
            logger.info("Shutting down hub...")
            await hub.shutdown()
            logger.info("Hub shutdown complete")


async def run_with_web_ui():
    """Run the hub with integrated Web UI and attestation service"""
    # Global references for signal handling
    hub = None
    web_ui_service = None
    
    def signal_handler(sig, frame):
        """Handle shutdown signals gracefully"""
        logger.info(f"Received signal {sig}, shutting down...")
        if hub:
            asyncio.create_task(hub.shutdown())
    
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Initialize hub router
        hub = HubRouter()
        
        # Initialize and register Secret AI service
        logger.info("Initializing Secret AI service...")
        secret_ai = SecretAIService()
        hub.register_component(ComponentType.SECRET_AI, secret_ai)
        
        # Initialize the hub
        await hub.initialize()
        
        # Initialize Web UI service with proper attestation support
        logger.info("Initializing Web UI service...")
        try:
            from interfaces.web_ui.service import WebUIService
            
            # Use WebUIService (includes attestation) instead of WebUIInterface
            web_ui_service = WebUIService(hub)
            hub.register_component(ComponentType.WEB_UI, web_ui_service)
            
            # Start the web UI server
            import uvicorn
            
            # Get the FastAPI app from web UI service
            app = web_ui_service.get_fastapi_app()
            
            config = uvicorn.Config(
                app=app,
                host=os.getenv("SECRETGPT_HUB_HOST", "0.0.0.0"),
                port=int(os.getenv("SECRETGPT_HUB_PORT", "8000")),
                log_level=settings.log_level.lower(),
                access_log=True
            )
            server = uvicorn.Server(config)
            
            # Get system status
            status = await hub.get_system_status()
            logger.info(f"System status: {status}")
            
            # Get available models
            models = await hub.get_available_models()
            logger.info(f"Available models: {models}")
            
            logger.info("secretGPT Hub with Web UI started successfully")
            logger.info(f"Web UI available at http://{config.host}:{config.port}")
            
            # Run the server
            await server.serve()
            
        except ImportError as e:
            logger.error(f"Web UI dependencies not available: {e}")
            logger.info("Falling back to service mode without Web UI")
            await run_service_mode()
            
    except Exception as e:
        logger.error(f"Service error: {e}")
        raise
    finally:
        if web_ui_service:
            await web_ui_service.cleanup()
        if hub:
            logger.info("Shutting down hub...")
            await hub.shutdown()
            logger.info("Hub shutdown complete")


async def test_web_ui_integration():
    """Test Web UI integration with attestation service"""
    logger.info("Testing Web UI integration...")
    
    # Initialize hub router
    hub = HubRouter()
    
    # Initialize and register Secret AI service
    logger.info("Initializing Secret AI service...")
    secret_ai = SecretAIService()
    hub.register_component(ComponentType.SECRET_AI, secret_ai)
    
    # Initialize and register Web UI service
    logger.info("Initializing Web UI service...")
    from interfaces.web_ui.service import WebUIService
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
        
        # Test self attestation (will work in SecretVM)
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
    
    logger.info("Web UI integration test complete")


async def main():
    """Main entry point for secretGPT hub"""
    logger.info("Starting secretGPT Hub - Phase 1")
    
    # Validate settings
    if not validate_settings():
        logger.error("Invalid settings configuration")
        return
    
    logger.info("Settings validated successfully")
    
    # Determine run mode
    run_mode = os.getenv("SECRETGPT_RUN_MODE", "service").lower()
    web_ui_enabled = os.getenv("SECRETGPT_ENABLE_WEB_UI", "false").lower() == "true"
    
    if run_mode == "test":
        logger.info("Running in test mode")
        if web_ui_enabled:
            await test_web_ui_integration()
        else:
            await test_secret_ai_integration()
    elif run_mode == "service":
        logger.info("Running in service mode")
        if web_ui_enabled:
            await run_with_web_ui()
        else:
            await run_service_mode()
    else:
        logger.error(f"Unknown run mode: {run_mode}")
        logger.info("Valid modes: test, service")
        logger.info("Set SECRETGPT_ENABLE_WEB_UI=true for Web UI with attestation")
        return


if __name__ == "__main__":
    asyncio.run(main())