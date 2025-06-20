"""
Start secretGPT Web UI Server
Launches the complete system with Web UI on port 8000
"""
import asyncio
import logging
import sys
import uvicorn
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from secretGPT.hub.core.router import HubRouter, ComponentType
from secretGPT.services.secret_ai.client import SecretAIService
from secretGPT.interfaces.web_ui.service import WebUIService
from secretGPT.config.settings import settings

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def initialize_secretgpt_system():
    """Initialize the complete secretGPT system"""
    logger.info("🚀 Starting secretGPT Hub with Web UI")
    
    # Initialize hub router
    hub = HubRouter()
    
    # Initialize Secret AI service
    secret_ai = SecretAIService()
    hub.register_component(ComponentType.SECRET_AI, secret_ai)
    
    # Initialize Web UI service
    web_ui_service = WebUIService(hub)
    hub.register_component(ComponentType.WEB_UI, web_ui_service)
    
    # Initialize hub
    await hub.initialize()
    
    logger.info("✅ secretGPT system initialized successfully")
    
    # Get FastAPI app
    app = web_ui_service.get_fastapi_app()
    
    return app, hub, web_ui_service

def start_web_server():
    """Start the web server"""
    logger.info("🌐 Starting secretGPT Web UI Server")
    logger.info("="*50)
    
    # Initialize system
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    app, hub, web_ui_service = loop.run_until_complete(initialize_secretgpt_system())
    
    # Add system references to app state
    app.state.hub = hub
    app.state.web_ui_service = web_ui_service
    
    logger.info(f"🌐 Web UI will be available at: http://localhost:8002")
    logger.info("📋 Available endpoints:")
    logger.info("   • Main page: http://localhost:8002/")
    logger.info("   • Chat API: http://localhost:8002/api/v1/chat")
    logger.info("   • Health check: http://localhost:8002/health")
    logger.info("   • Attestation: http://localhost:8002/api/v1/attestation/self")
    logger.info("="*50)
    
    # Start uvicorn server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8002,
        log_level="info",
        access_log=True
    )

if __name__ == "__main__":
    start_web_server()