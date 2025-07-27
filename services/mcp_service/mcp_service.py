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
            # Import settings here to get the configurable path
            from config.settings import settings
            server_path = settings.mcp_server_path
            
            logger.info(f"Connecting to {server_id} MCP server at {server_path}...")
            
            # Check if server file exists and is executable
            import os
            if not os.path.exists(server_path):
                raise FileNotFoundError(f"MCP server not found at {server_path}")
            
            if not os.access(server_path, os.X_OK):
                logger.warning(f"MCP server at {server_path} is not executable, attempting to fix...")
                os.chmod(server_path, 0o755)
            
            # Start server process with stdio transport
            process = await asyncio.create_subprocess_exec(
                "node", server_path,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=os.path.dirname(server_path)  # Set working directory to server location
            )
            
            # Wait a moment to see if process starts successfully
            await asyncio.sleep(0.5)
            
            # Check if process is still running
            if process.returncode is not None:
                # Process has already exited, capture stderr
                stderr_output = await process.stderr.read()
                stdout_output = await process.stdout.read()
                error_msg = stderr_output.decode() if stderr_output else "No error output"
                stdout_msg = stdout_output.decode() if stdout_output else "No stdout"
                
                logger.error(f"MCP server process exited with code {process.returncode}")
                logger.error(f"STDERR: {error_msg}")
                logger.error(f"STDOUT: {stdout_msg}")
                raise Exception(f"MCP server failed to start: {error_msg}")
            
            # Store server connection
            self.servers[server_id] = process
            self.server_status[server_id] = MCPServerStatus.CONNECTED
            
            logger.info(f"Successfully connected to {server_id} MCP server (PID: {process.pid})")
            
        except Exception as e:
            logger.error(f"Failed to connect to {server_id} MCP server: {e}")
            self.server_status[server_id] = MCPServerStatus.ERROR
            raise
    
    async def _discover_all_capabilities(self) -> None:
        """Discover tools and resources from all connected servers"""
        logger.info("Discovering MCP capabilities...")
        
        for server_id, process in self.servers.items():
            try:
                # Give the server process time to initialize
                await asyncio.sleep(0.5)
                
                # First, send initialize request (MCP protocol requirement)
                init_request = {
                    "jsonrpc": "2.0",
                    "id": 0,
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "roots": {"listChanged": True},
                            "sampling": {}
                        },
                        "clientInfo": {
                            "name": "secretGPT-mcp-client",
                            "version": "1.0.0"
                        }
                    }
                }
                
                # Send initialize request
                request_json = json.dumps(init_request) + "\n"
                process.stdin.write(request_json.encode())
                await process.stdin.drain()
                
                # Read initialize response
                init_response_line = await asyncio.wait_for(
                    process.stdout.readline(), 
                    timeout=5.0
                )
                init_response_text = init_response_line.decode().strip()
                logger.info(f"Initialize response from {server_id}: {init_response_text}")
                
                # Send initialized notification
                initialized_notification = {
                    "jsonrpc": "2.0",
                    "method": "notifications/initialized",
                    "params": {}
                }
                
                request_json = json.dumps(initialized_notification) + "\n"
                process.stdin.write(request_json.encode())
                await process.stdin.drain()
                
                # Wait a moment for the server to process the notification
                await asyncio.sleep(0.2)
                
                # Now send tools/list request to server
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
                
                # Read response with timeout and retry logic
                max_attempts = 3
                for attempt in range(max_attempts):
                    try:
                        # Wait for response with timeout
                        response_line = await asyncio.wait_for(
                            process.stdout.readline(), 
                            timeout=5.0
                        )
                        
                        response_text = response_line.decode().strip()
                        if not response_text:
                            continue
                            
                        # Skip non-JSON lines (debug output)
                        if not response_text.startswith('{'):
                            continue
                            
                        response_data = json.loads(response_text)
                        
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
                            
                            break  # Success, exit retry loop
                            
                    except asyncio.TimeoutError:
                        logger.warning(f"Timeout waiting for response from {server_id}, attempt {attempt + 1}")
                        if attempt == max_attempts - 1:
                            raise Exception("Timeout waiting for server response")
                    except json.JSONDecodeError as e:
                        logger.warning(f"JSON decode error for {server_id}, attempt {attempt + 1}: {e}")
                        if attempt == max_attempts - 1:
                            raise Exception(f"Invalid JSON response: {e}")
                
            except Exception as e:
                logger.error(f"Failed to discover capabilities for {server_id}: {e}")
                
                # Check if process is still alive and capture any error output
                if server_id in self.servers:
                    process = self.servers[server_id]
                    if process.returncode is not None:
                        # Process has died, try to get error output
                        try:
                            stderr_output = await asyncio.wait_for(process.stderr.read(), timeout=1.0)
                            if stderr_output:
                                logger.error(f"MCP server stderr: {stderr_output.decode()}")
                        except asyncio.TimeoutError:
                            logger.warning("Could not read stderr from failed MCP server")
                        except Exception as stderr_e:
                            logger.warning(f"Error reading MCP server stderr: {stderr_e}")
                    else:
                        logger.info(f"MCP server process {server_id} is still running")
                
                # Mark server as error state but continue
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
            
            # Read response with timeout and JSON filtering
            response_line = await asyncio.wait_for(
                process.stdout.readline(), 
                timeout=10.0
            )
            response_text = response_line.decode().strip()
            
            # Skip non-JSON lines (debug output)
            while response_text and not response_text.startswith('{'):
                response_line = await asyncio.wait_for(
                    process.stdout.readline(), 
                    timeout=10.0
                )
                response_text = response_line.decode().strip()
            
            response_data = json.loads(response_text)
            
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