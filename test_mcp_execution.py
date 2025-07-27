#!/usr/bin/env python3
"""
Test script to execute MCP tools directly
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

async def test_mcp_tool_execution():
    """Test direct MCP tool execution"""
    logger.info("🛠️ Testing MCP Tool Execution")
    
    hub = None
    try:
        # Initialize hub router
        hub = HubRouter()
        
        # Initialize and register MCP service
        mcp_service = MCPService()
        hub.register_component(ComponentType.MCP_SERVICE, mcp_service)
        
        # Initialize the hub
        await hub.initialize()
        
        if mcp_service.initialized:
            logger.info("✅ MCP Service ready")
            
            # Test executing the secret_network_status tool
            try:
                logger.info("🔧 Executing secret_network_status tool...")
                result = await mcp_service.execute_tool("secret_network_status", {})
                logger.info(f"✅ Tool execution result: {result}")
                
            except Exception as e:
                logger.error(f"❌ Tool execution failed: {e}")
                import traceback
                traceback.print_exc()
                
        else:
            logger.error("❌ MCP Service not initialized")
            
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if hub:
            await hub.shutdown()

if __name__ == "__main__":
    asyncio.run(test_mcp_tool_execution())