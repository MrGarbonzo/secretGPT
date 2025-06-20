"""
secretGPT Hub - Main Entry Point
Phase 1: Core Foundation with Secret AI Integration
"""
import asyncio
import logging
import sys
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


async def main():
    """Main entry point for secretGPT hub"""
    logger.info("Starting secretGPT Hub - Phase 1")
    
    # Validate settings
    if not validate_settings():
        logger.error("Invalid settings configuration")
        return
    
    logger.info("Settings validated successfully")
    
    # Run test
    await test_secret_ai_integration()


if __name__ == "__main__":
    asyncio.run(main())