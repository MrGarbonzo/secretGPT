#!/usr/bin/env python3
"""
Test script to verify HTTP MCP integration
"""
import asyncio
import os
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Load test environment
from dotenv import load_dotenv
load_dotenv('.env.test')

from services.mcp_service.http_mcp_service import HTTPMCPService

async def test_http_mcp_service():
    """Test the HTTP MCP service directly"""
    print("🧪 Testing HTTP MCP Service...")
    
    mcp_service = HTTPMCPService()
    
    try:
        # Initialize the service
        print("🔌 Initializing HTTP MCP service...")
        await mcp_service.initialize()
        
        # Check status
        print("📊 Getting MCP service status...")
        status = await mcp_service.get_status()
        print(f"Status: {status}")
        
        # Get available tools
        print("🛠️ Getting available tools...")
        tools = await mcp_service.get_available_tools()
        print(f"Found {len(tools)} tools:")
        for tool in tools:
            print(f"  - {tool['name']}: {tool['description']}")
        
        # Test tool execution
        print("🚀 Testing tool execution...")
        result = await mcp_service.execute_tool("secret_network_status", {})
        print(f"Tool result: {result}")
        
        print("✅ HTTP MCP service test completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await mcp_service.shutdown()

if __name__ == "__main__":
    asyncio.run(test_http_mcp_service())