"""
MCP Service for secretGPT Hub Router
Manages connections to multiple MCP servers and routes tool/resource requests
"""
import asyncio
import json
import logging
import subprocess
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


class MCPService:
    """
    MCP Service for secretGPT Hub Router
    Manages connections to multiple MCP servers and routes tool/resource requests
    """
    
    def __init__(self):
        """Initialize MCP service"""
        self.servers = {}           # server_id -> server_process/connection
        self.capabilities = {}      # server_id -> server_capabilities
        self.tools = {}            # tool_name -> server_id mapping
        self.resources = {}        # resource_uri -> server_id mapping
        self.server_status = {}    # server_id -> MCPServerStatus
        self.initialized = False
        self.operation_log = []    # Track operations for attestation
        logger.info("MCP Service initialized")
    
    async def initialize(self) -> None:
        """Initialize MCP service and connect to configured servers"""
        if self.initialized:
            logger.warning("MCP service already initialized")
            return
            
        logger.info("Initializing MCP service...")
        
        try:
            # Connect to Secret Network MCP server (local)
            await self._connect_secret_network_server()
            
            # Discover capabilities from all connected servers
            await self._discover_all_capabilities()
            
            self.initialized = True
            logger.info(f"MCP service initialized with {len(self.servers)} servers")
            
        except Exception as e:
            logger.error(f"Failed to initialize MCP service: {e}")
            raise
    
    async def _connect_secret_network_server(self) -> None:
        """Connect to the local Secret Network MCP server"""
        server_id = "secret_network"
        
        try:
            logger.info(f"Connecting to {server_id} MCP server...")
            
            # Server configuration
            server_path = "/root/coding/secretGPT/mcp_servers/secret_network/build/index.js"
            
            # Start server process with stdio transport
            process = await asyncio.create_subprocess_exec(
                "node", server_path,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Store server connection
            self.servers[server_id] = process
            self.server_status[server_id] = MCPServerStatus.CONNECTED
            
            logger.info(f"Successfully connected to {server_id} MCP server")
            
        except Exception as e:
            logger.error(f"Failed to connect to {server_id} MCP server: {e}")
            self.server_status[server_id] = MCPServerStatus.ERROR
            raise
    
    async def _discover_all_capabilities(self) -> None:
        """Discover tools and resources from all connected servers"""
        logger.info("Discovering MCP capabilities...")
        
        for server_id, process in self.servers.items():
            try:
                # Send tools/list request to server
                request = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "tools/list",
                    "params": {}
                }
                
                # Send request to server
                request_json = json.dumps(request) + "\n"
                process.stdin.write(request_json.encode())
                await process.stdin.drain()
                
                # Read response
                response_line = await process.stdout.readline()
                response_data = json.loads(response_line.decode().strip())
                
                if "result" in response_data and "tools" in response_data["result"]:
                    tools = response_data["result"]["tools"]
                    
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
                
            except Exception as e:
                logger.error(f"Failed to discover capabilities for {server_id}: {e}")
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
        Execute tool on appropriate MCP server
        
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
                raise ValueError(f"Tool '{tool_name}' not found")
            
            process = self.servers.get(server_id)
            if not process:
                raise ValueError(f"Server '{server_id}' not connected")
            
            # Send tool execution request
            request = {
                "jsonrpc": "2.0",
                "id": int(time.time()),
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": arguments
                }
            }
            
            # Send request to server
            request_json = json.dumps(request) + "\n"
            process.stdin.write(request_json.encode())
            await process.stdin.drain()
            
            # Read response
            response_line = await process.stdout.readline()
            response_data = json.loads(response_line.decode().strip())
            
            if "error" in response_data:
                error_msg = response_data["error"].get("message", "Unknown error")
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
        return {
            "initialized": self.initialized,
            "servers": {
                server_id: status.value 
                for server_id, status in self.server_status.items()
            },
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
        logger.info("Shutting down MCP service...")
        
        # Terminate all server processes
        for server_id, process in self.servers.items():
            try:
                logger.info(f"Terminating MCP server: {server_id}")
                process.terminate()
                await process.wait()
            except Exception as e:
                logger.error(f"Error terminating {server_id}: {e}")
        
        self.servers.clear()
        self.capabilities.clear()
        self.tools.clear()
        self.resources.clear()
        self.server_status.clear()
        self.initialized = False
        
        logger.info("MCP service shutdown complete")