#!/usr/bin/env python3
"""
Test script to debug MCP integration without requiring Secret AI API key
"""
import asyncio
import logging
import sys
import os

# Add project root to path
sys.path.insert(0, '/root/coding/secretGPT')

from hub.core.router import HubRouter, ComponentType
from services.mcp_service.mcp_service import MCPService

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_mcp_integration():
    """Test the MCP service integration without Secret AI"""
    logger.info("🧪 Testing MCP Integration")
    
    hub = None
    try:
        # Initialize hub router
        hub = HubRouter()
        
        # Initialize and register MCP service
        logger.info("Initializing MCP service...")
        mcp_service = MCPService()
        hub.register_component(ComponentType.MCP_SERVICE, mcp_service)
        
        # Initialize the hub (this will initialize MCP service)
        await hub.initialize()
        
        # Test MCP service status
        status = await hub.get_system_status()
        logger.info(f"System status: {status}")
        
        # Test getting available tools
        if mcp_service.initialized:
            logger.info("✅ MCP Service initialized successfully")
            try:
                tools = await mcp_service.get_available_tools()
                logger.info(f"📋 Available MCP tools: {[tool['name'] for tool in tools]}")
                
                # Test pre-detection logic
                test_messages = [
                    "What's the Secret Network status?",
                    "Check the latest block",
                    "Secret Network info",
                    "test secret network"
                ]
                
                for msg in test_messages:
                    logger.info(f"\n🔍 Testing message: '{msg}'")
                    detected_tools = hub._detect_secret_network_queries(msg)
                    if detected_tools:
                        logger.info(f"✅ Pre-detected tools: {[t['name'] for t in detected_tools]}")
                    else:
                        logger.info("❌ No tools pre-detected")
                
            except Exception as e:
                logger.error(f"❌ Error testing MCP tools: {e}")
        else:
            logger.error("❌ MCP Service failed to initialize")
            
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if hub:
            await hub.shutdown()

if __name__ == "__main__":
    asyncio.run(test_mcp_integration())