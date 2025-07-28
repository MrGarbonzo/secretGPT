"""
HTTP-based MCP Service for secretGPT Hub Router
Manages connections to external MCP servers via HTTP API and routes tool/resource requests
"""
import aiohttp
import asyncio
import json
import logging
import time
from typing import Dict, Any, List, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class MCPServerStatus(Enum):
    """Status of MCP server connections"""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"


class HTTPMCPService:
    """
    HTTP-based MCP Service for secretGPT Hub Router
    Manages connections to external MCP servers via HTTP API and routes tool/resource requests
    """
    
    def __init__(self):
        """Initialize HTTP MCP service"""
        self.servers = {}           # server_id -> server_config
        self.capabilities = {}      # server_id -> server_capabilities
        self.tools = {}            # tool_name -> server_id mapping
        self.resources = {}        # resource_uri -> server_id mapping
        self.server_status = {}    # server_id -> MCPServerStatus
        self.initialized = False
        self.operation_log = []    # Track operations for attestation
        self.session = None        # HTTP session
        logger.info("HTTP MCP Service initialized")
    
    async def initialize(self) -> None:
        """Initialize HTTP MCP service and connect to configured servers"""
        if self.initialized:
            logger.warning("HTTP MCP service already initialized")
            return
            
        logger.info("Initializing HTTP MCP service...")
        
        try:
            # Create HTTP session
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30, connect=10)
            )
            
            # Connect to Secret Network MCP server (external HTTP)
            await self._connect_secret_network_server()
            
            # Discover capabilities from all connected servers
            await self._discover_all_capabilities()
            
            self.initialized = True
            logger.info(f"HTTP MCP service initialized with {len(self.servers)} servers")
            
        except Exception as e:
            logger.warning(f"HTTP MCP service initialization failed, but continuing: {e}")
            logger.info("Hub will run without MCP tools - they will be unavailable until MCP server comes online")
            self.initialized = True  # Still mark as initialized, just with no servers
    
    async def _connect_secret_network_server(self) -> None:
        """Connect to the external Secret Network MCP server via HTTP"""
        server_id = "secret_network"
        
        try:
            # Import settings here to get the configurable URL
            from config.settings import settings
            server_url = getattr(settings, 'secret_mcp_url', 'http://10.0.1.100:8002')
            
            logger.info(f"Connecting to {server_id} MCP server at {server_url}...")
            
            # Test connection with health check
            health_url = f"{server_url}/api/health"
            async with self.session.get(health_url) as response:
                if response.status == 200:
                    health_data = await response.json()
                    logger.info(f"Health check successful: {health_data}")
                else:
                    raise Exception(f"Health check failed with status {response.status}")
            
            # Store server configuration
            self.servers[server_id] = {
                "url": server_url,
                "type": "http",
                "endpoints": {
                    "health": f"{server_url}/api/health",
                    "tools_list": f"{server_url}/api/mcp/tools/list",
                    "tools_call": f"{server_url}/api/mcp/tools/call"
                }
            }
            self.server_status[server_id] = MCPServerStatus.CONNECTED
            
            logger.info(f"Successfully connected to {server_id} MCP server via HTTP")
            
        except Exception as e:
            logger.warning(f"Failed to connect to {server_id} MCP server: {e}")
            logger.info(f"MCP server at {server_url} is unavailable - Secret Network tools will not be available")
            self.server_status[server_id] = MCPServerStatus.ERROR
            # Don't raise - let the hub continue without MCP tools
    
    async def _discover_all_capabilities(self) -> None:
        """Discover tools and resources from all connected servers"""
        logger.info("Discovering MCP capabilities...")
        
        for server_id, server_config in self.servers.items():
            try:
                if server_config["type"] != "http":
                    logger.warning(f"Skipping non-HTTP server: {server_id}")
                    continue
                
                # Send tools/list request to server
                tools_list_url = server_config["endpoints"]["tools_list"]
                
                async with self.session.get(tools_list_url) as response:
                    if response.status != 200:
                        raise Exception(f"Tools list request failed with status {response.status}")
                    
                    response_data = await response.json()
                    
                    if "tools" in response_data:
                        tools = response_data["tools"]
                        
                        # Store server capabilities
                        self.capabilities[server_id] = {
                            "tools": tools,
                            "resources": []  # TODO: Add resource discovery
                        }
                        
                        # Map tools to server
                        for tool in tools:
                            tool_name = tool["name"]
                            self.tools[tool_name] = server_id
                            logger.info(f"Discovered tool: {tool_name} from {server_id}")
                    else:
                        logger.warning(f"No tools found in response from {server_id}")
                
            except Exception as e:
                logger.error(f"Failed to discover capabilities for {server_id}: {e}")
                self.server_status[server_id] = MCPServerStatus.ERROR
                continue
        
        logger.info(f"Capability discovery complete: {len(self.tools)} tools available")
    
    async def get_available_tools(self) -> List[Dict[str, Any]]:
        """
        Get list of all available tools from all servers
        
        Returns:
            List of tool definitions
        """
        all_tools = []
        
        for server_id, capabilities in self.capabilities.items():
            if "tools" in capabilities:
                for tool in capabilities["tools"]:
                    tool_with_server = tool.copy()
                    tool_with_server["server_id"] = server_id
                    all_tools.append(tool_with_server)
        
        return all_tools
    
    async def get_available_resources(self) -> List[Dict[str, Any]]:
        """
        Get list of all available resources from all servers
        
        Returns:
            List of resource definitions
        """
        # TODO: Implement resource discovery
        return []
    
    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute tool on appropriate MCP server via HTTP
        
        Args:
            tool_name: Name of the tool to execute
            arguments: Tool arguments
            
        Returns:
            Tool execution result
        """
        # Log operation start for attestation
        operation_id = self._log_operation_start("tool_execution", {
            "tool_name": tool_name,
            "arguments": arguments,
            "timestamp": time.time()
        })
        
        try:
            # Find server for this tool
            server_id = self.tools.get(tool_name)
            if not server_id:
                raise ValueError(f"Tool '{tool_name}' not available - MCP server may be offline")
            
            server_config = self.servers.get(server_id)
            if not server_config:
                raise ValueError(f"Server '{server_id}' not connected - MCP server is unavailable")
            
            # Send tool execution request via HTTP
            tools_call_url = server_config["endpoints"]["tools_call"]
            
            request_data = {
                "name": tool_name,
                "arguments": arguments
            }
            
            async with self.session.post(
                tools_call_url,
                json=request_data,
                headers={'Content-Type': 'application/json'}
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Tool execution failed with status {response.status}: {error_text}")
                
                response_data = await response.json()
                
                if not response_data.get("success", False):
                    error_msg = response_data.get("error", {}).get("message", "Unknown error")
                    raise Exception(f"Tool execution error: {error_msg}")
                
                result = response_data.get("result", {})
            
            # Log successful completion
            self._log_operation_complete(operation_id, {
                "success": True,
                "result_hash": self._hash_result(result)
            })
            
            logger.info(f"Successfully executed tool: {tool_name}")
            return result
            
        except Exception as e:
            # Log error
            self._log_operation_complete(operation_id, {
                "success": False,
                "error": str(e)
            })
            logger.error(f"Failed to execute tool {tool_name}: {e}")
            raise
    
    async def read_resource(self, resource_uri: str) -> Dict[str, Any]:
        """
        Read resource from appropriate MCP server
        
        Args:
            resource_uri: URI of the resource to read
            
        Returns:
            Resource content
        """
        # TODO: Implement resource reading
        raise NotImplementedError("Resource reading not yet implemented")
    
    async def get_status(self) -> Dict[str, Any]:
        """
        Get MCP service status
        
        Returns:
            Status information including server connections and capabilities
        """
        # Check server health
        server_health = {}
        for server_id, server_config in self.servers.items():
            try:
                if server_config["type"] == "http":
                    health_url = server_config["endpoints"]["health"]
                    async with self.session.get(health_url) as response:
                        if response.status == 200:
                            health_data = await response.json()
                            server_health[server_id] = {
                                "status": "healthy",
                                "details": health_data
                            }
                        else:
                            server_health[server_id] = {
                                "status": "unhealthy",
                                "http_status": response.status
                            }
            except Exception as e:
                server_health[server_id] = {
                    "status": "error",
                    "error": str(e)
                }
        
        return {
            "initialized": self.initialized,
            "servers": {
                server_id: status.value 
                for server_id, status in self.server_status.items()
            },
            "server_health": server_health,
            "capabilities": {
                "tools": len(self.tools),
                "resources": len(self.resources),
                "servers_connected": len([
                    s for s in self.server_status.values() 
                    if s == MCPServerStatus.CONNECTED
                ])
            },
            "operations_logged": len(self.operation_log)
        }
    
    def get_attestation_data(self) -> Dict[str, Any]:
        """
        Get MCP operations for inclusion in attestation proof
        
        Returns:
            Attestation data including operations log and capabilities
        """
        return {
            "mcp_operations": self.operation_log,
            "servers_connected": list(self.servers.keys()),
            "capabilities": self.capabilities,
            "tools_available": list(self.tools.keys())
        }
    
    def _log_operation_start(self, operation_type: str, data: Dict[str, Any]) -> str:
        """Log the start of an MCP operation for attestation"""
        operation_id = f"{operation_type}_{int(time.time() * 1000)}"
        
        self.operation_log.append({
            "operation_id": operation_id,
            "type": operation_type,
            "status": "started",
            "data": data,
            "timestamp": time.time()
        })
        
        return operation_id
    
    def _log_operation_complete(self, operation_id: str, result_data: Dict[str, Any]) -> None:
        """Log the completion of an MCP operation for attestation"""
        # Find and update the operation
        for operation in self.operation_log:
            if operation["operation_id"] == operation_id:
                operation["status"] = "completed"
                operation["result"] = result_data
                operation["completed_at"] = time.time()
                break
    
    def _hash_result(self, result: Any) -> str:
        """Generate a hash of the tool result for attestation"""
        import hashlib
        result_str = json.dumps(result, sort_keys=True)
        return hashlib.sha256(result_str.encode()).hexdigest()
    
    async def shutdown(self) -> None:
        """Gracefully shutdown MCP service and all server connections"""
        logger.info("Shutting down HTTP MCP service...")
        
        # Close HTTP session
        if self.session:
            await self.session.close()
            self.session = None
        
        self.servers.clear()
        self.capabilities.clear()
        self.tools.clear()
        self.resources.clear()
        self.server_status.clear()
        self.initialized = False
        
        logger.info("HTTP MCP service shutdown complete")