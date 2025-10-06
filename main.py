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

# CRITICAL: Load .env file early for secretVM deployment
from dotenv import load_dotenv
load_dotenv()

from hub.core.router import HubRouter, ComponentType
from services.secret_ai.client import SecretAIService
from services.mcp_service.http_mcp_service import HTTPMCPService
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
    
    # Initialize and register HTTP MCP service
    logger.info("Initializing HTTP MCP service...")
    mcp_service = HTTPMCPService()
    hub.register_component(ComponentType.MCP_SERVICE, mcp_service)
    
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
        
        # Initialize and register MCP service
        logger.info("Initializing MCP service...")
        mcp_service = HTTPMCPService()
        hub.register_component(ComponentType.MCP_SERVICE, mcp_service)
        
        # Initialize and register SNIP Token service
        logger.info("Initializing SNIP Token service...")
        try:
            from services.snip_token.service import SNIPTokenService
            snip_service = SNIPTokenService()
            await snip_service.initialize()
            hub.register_component(ComponentType.SNIP_TOKEN_SERVICE, snip_service)
            logger.info("SNIP Token service registered successfully")
        except Exception as e:
            logger.warning(f"SNIP Token service not available: {e}")
        
        # Initialize wallet proxy service for SecretGPTee (Bridge-Ready)
        logger.info("Initializing Wallet Proxy service...")
        try:
            from services.wallet_service.proxy import WalletProxyService
            wallet_proxy = WalletProxyService()
            initialization_result = await wallet_proxy.initialize()
            hub.register_component(ComponentType.WALLET_PROXY, wallet_proxy)
            logger.info(f"Wallet Proxy service registered: {initialization_result.get('message', 'Success')}")
            logger.info(f"Bridge mode: {initialization_result.get('bridge_mode', 'http')}")
        except Exception as e:
            logger.warning(f"Wallet Proxy service not available: {e}")
        
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
    ui_service = None
    
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
        
        # Initialize and register MCP service
        logger.info("Initializing MCP service...")
        mcp_service = HTTPMCPService()
        hub.register_component(ComponentType.MCP_SERVICE, mcp_service)
        
        # Initialize and register SNIP Token service
        logger.info("Initializing SNIP Token service...")
        try:
            from services.snip_token.service import SNIPTokenService
            snip_service = SNIPTokenService()
            await snip_service.initialize()
            hub.register_component(ComponentType.SNIP_TOKEN_SERVICE, snip_service)
            logger.info("SNIP Token service registered successfully")
        except Exception as e:
            logger.warning(f"SNIP Token service not available: {e}")
        
        # Initialize wallet proxy service for SecretGPTee (Bridge-Ready)
        logger.info("Initializing Wallet Proxy service...")
        try:
            from services.wallet_service.proxy import WalletProxyService
            wallet_proxy = WalletProxyService()
            initialization_result = await wallet_proxy.initialize()
            hub.register_component(ComponentType.WALLET_PROXY, wallet_proxy)
            logger.info(f"Wallet Proxy service registered: {initialization_result.get('message', 'Success')}")
            logger.info(f"Bridge mode: {initialization_result.get('bridge_mode', 'http')}")
        except Exception as e:
            logger.warning(f"Wallet Proxy service not available: {e}")
        
        # Initialize the hub
        await hub.initialize()
        
        # Check for dual-domain mode
        dual_domain_mode = os.getenv("SECRETGPT_DUAL_DOMAIN", "false").lower() == "true"
        
        if dual_domain_mode:
            # Initialize Multi-UI service for dual-domain routing
            logger.info("Initializing Multi-UI service for dual-domain routing...")
            try:
                from interfaces.multi_ui_service import MultiUIService
                
                ui_service = MultiUIService(hub)
                hub.register_component(ComponentType.MULTI_UI_SERVICE, ui_service)
                
                # Get the FastAPI app from multi-UI service
                app = ui_service.get_fastapi_app()
                
                logger.info("Multi-UI service initialized - supporting both AttestAI and SecretGPTee")
                
            except ImportError as e:
                logger.error(f"Multi-UI dependencies not available: {e}")
                logger.info("Falling back to single Web UI mode")
                dual_domain_mode = False
        
        if not dual_domain_mode:
            # Initialize single Web UI service (original AttestAI)
            logger.info("Initializing Web UI service (single domain mode)...")
            try:
                from interfaces.web_ui.service import WebUIService
                
                ui_service = WebUIService(hub)
                hub.register_component(ComponentType.WEB_UI, ui_service)
                
                # Get the FastAPI app from web UI service
                app = ui_service.get_fastapi_app()
                
            except ImportError as e:
                logger.error(f"Web UI dependencies not available: {e}")
                logger.info("Falling back to service mode without Web UI")
                await run_service_mode()
                return
        
        # Start the server
        import uvicorn
        
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
        
        mode_info = "Multi-UI (AttestAI + SecretGPTee)" if dual_domain_mode else "Single Web UI (AttestAI)"
        logger.info(f"secretGPT Hub started successfully - Mode: {mode_info}")
        logger.info(f"Web interface available at http://{config.host}:{config.port}")
        
        if dual_domain_mode:
            logger.info("Domain routing:")
            logger.info("  - attestai.io → AttestAI interface")
            logger.info("  - secretgptee.com → SecretGPTee interface") 
            logger.info("  - localhost → AttestAI interface (default)")
        
        # Run the server
        await server.serve()
        
    except Exception as e:
        logger.error(f"Service error: {e}")
        raise
    finally:
        if ui_service:
            await ui_service.cleanup()
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
    
    # Initialize and register HTTP MCP service
    logger.info("Initializing HTTP MCP service...")
    mcp_service = HTTPMCPService()
    hub.register_component(ComponentType.MCP_SERVICE, mcp_service)
    
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