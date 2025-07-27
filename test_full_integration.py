#!/usr/bin/env python3
"""
Test full secretGPT integration with Secret AI + MCP
"""
import asyncio
import logging
import sys
import os

# Add project root to path
sys.path.insert(0, '/root/coding/secretGPT')

from hub.core.router import HubRouter, ComponentType
from services.mcp_service.mcp_service import MCPService
from services.secret_ai.client import SecretAIService

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_full_integration():
    """Test full secretGPT integration"""
    logger.info("🚀 Testing Full secretGPT Integration")
    
    hub = None
    try:
        # Initialize hub router
        hub = HubRouter()
        
        # Initialize Secret AI service
        secret_ai = SecretAIService()
        hub.register_component(ComponentType.SECRET_AI, secret_ai)
        
        # Initialize MCP service
        mcp_service = MCPService()
        hub.register_component(ComponentType.MCP_SERVICE, mcp_service)
        
        # Initialize the hub
        await hub.initialize()
        
        # Test Secret Network query
        test_message = "What's the Secret Network status?"
        logger.info(f"🔍 Testing message: '{test_message}'")
        
        result = await hub.route_message("test", test_message)
        
        if result.get("success"):
            logger.info("✅ Integration test successful!")
            logger.info(f"📄 Response: {result.get('content', '')[:200]}...")
        else:
            logger.error(f"❌ Integration test failed: {result.get('error')}")
            
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if hub:
            await hub.shutdown()

if __name__ == "__main__":
    # Set the environment variable for this test
    os.environ['SECRET_AI_API_KEY'] = 'sk-nDYq9a_mYyF9TSCiF_P-fS18UHk1xSmTS9rmfV3MMKyVA-FmXjKzuhVo1J72wRh6yg-wB3U-'
    asyncio.run(test_full_integration())