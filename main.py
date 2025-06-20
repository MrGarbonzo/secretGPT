"""
secretGPT Hub - Main Entry Point
Phase 1: Core Foundation with Secret AI Integration
"""
import asyncio
import logging
import sys
import signal
import os
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from secretGPT.hub.core.router import HubRouter, ComponentType
from secretGPT.services.secret_ai.client import SecretAIService
from secretGPT.config.settings import settings, validate_settings


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
        logger.info(f"Response: {response['content']}")
    else:
        logger.error(f"Error: {response['error']}")
    
    # Shutdown
    await hub.shutdown()


async def run_service_mode():
    """Run the hub in persistent service mode"""
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
    """Run the hub with integrated web UI"""
    # Global hub instance for signal handling
    hub = None
    web_ui = None
    
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
        
        # Initialize Web UI if enabled
        if os.getenv("SECRETGPT_ENABLE_WEB_UI", "false").lower() == "true":
            logger.info("Initializing Web UI interface...")
            try:
                from secretGPT.interfaces.web_ui.app import WebUIInterface
                web_ui = WebUIInterface(hub)
                
                # Start the web UI server
                import uvicorn
                config = uvicorn.Config(
                    app=web_ui.get_app(),
                    host=os.getenv("SECRETGPT_HUB_HOST", "0.0.0.0"),
                    port=int(os.getenv("SECRETGPT_HUB_PORT", "8000")),
                    log_level=settings.log_level.lower()
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
        else:
            logger.info("Web UI disabled, running in service mode only")
            await run_service_mode()
            
    except Exception as e:
        logger.error(f"Service error: {e}")
        raise
    finally:
        if hub:
            logger.info("Shutting down hub...")
            await hub.shutdown()
            logger.info("Hub shutdown complete")


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
    
    if run_mode == "test":
        logger.info("Running in test mode")
        await test_secret_ai_integration()
    elif run_mode == "service":
        logger.info("Running in service mode")
        await run_with_web_ui()
    else:
        logger.error(f"Unknown run mode: {run_mode}")
        logger.info("Valid modes: test, service")
        return


if __name__ == "__main__":
    asyncio.run(main())