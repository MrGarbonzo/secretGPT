# MCP Hub Router Integration

**Reference**: secretGPT Hub Architecture + MCP Protocol Integration  
**Target**: secretGPT Phase 1 MCP Implementation

## Overview

This document outlines how to integrate MCP (Model Context Protocol) as a service component within secretGPT's existing hub router architecture, following the same patterns established for Secret AI integration.

## Current Hub Architecture

### Existing Components
```python
# From hub/core/router.py
class ComponentType(Enum):
    SECRET_AI = "secret_ai"
    WEB_UI = "web_ui"
    # MCP_SERVICE = "mcp_service"  # TO BE ADDED
```

### Existing Message Flow
```
AttestAI Web UI → Hub Router → Secret AI Service → Secret Network
```

## Target MCP Integration

### Enhanced Architecture
```
AttestAI Web UI → Hub Router → MCP Service ──→ MCP Servers
                            ↓                   (Tools & Resources)
                     Secret AI Service ──→ Secret Network
```

### Component Registration Pattern
```python
# Following existing Secret AI pattern
class ComponentType(Enum):
    SECRET_AI = "secret_ai"
    WEB_UI = "web_ui"
    MCP_SERVICE = "mcp_service"  # NEW

# Hub Router Integration
hub = HubRouter()
secret_ai = SecretAIService()
mcp_service = MCPService()  # NEW

hub.register_component(ComponentType.SECRET_AI, secret_ai)
hub.register_component(ComponentType.MCP_SERVICE, mcp_service)  # NEW
```

## MCP Service Component Design

### Core Service Structure
```python
class MCPService:
    """
    MCP Service for secretGPT Hub Router
    Manages connections to multiple MCP servers and routes tool/resource requests
    """
    
    def __init__(self):
        self.servers = {}           # server_id -> MCPServerConnection
        self.capabilities = {}      # server_id -> server_capabilities
        self.tools = {}            # tool_name -> server_id mapping
        self.resources = {}        # resource_uri -> server_id mapping
        self.initialized = False
    
    async def initialize(self):
        """Initialize MCP service and connect to configured servers"""
        pass
    
    async def connect_server(self, server_config):
        """Connect to a single MCP server"""
        pass
    
    async def discover_capabilities(self):
        """Discover tools and resources from all connected servers"""
        pass
    
    async def execute_tool(self, tool_name, arguments):
        """Execute tool on appropriate MCP server"""
        pass
    
    async def read_resource(self, resource_uri):
        """Read resource from appropriate MCP server"""
        pass
```

### Server Configuration Management
```python
# config/mcp_servers.yaml
servers:
  local_filesystem:
    transport: "stdio"
    command: ["python", "-m", "mcp_servers.filesystem"]
    args: ["--root", "/app/data"]
    
  secret_network:
    transport: "stdio" 
    command: ["python", "-m", "mcp_servers.secret_network"]
    env:
      SECRET_NODE_URL: "https://api.secretnetwork.io"
      
  remote_api:
    transport: "sse"
    url: "https://api.example.com/mcp"
    headers:
      Authorization: "Bearer ${API_TOKEN}"
```

## Message Routing Enhancements

### Enhanced Route Message Method
```python
async def route_message(self, interface: str, message: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Enhanced message routing with MCP tool integration
    """
    # 1. Check if message indicates tool usage intent
    tool_intent = await self._analyze_tool_intent(message, options)
    
    if tool_intent:
        # 2. Get available tools from MCP service
        mcp_service = self.get_component(ComponentType.MCP_SERVICE)
        if mcp_service:
            available_tools = await mcp_service.get_available_tools()
            # 3. Include tool context in AI prompt
            options = options or {}
            options["available_tools"] = available_tools
    
    # 4. Route to Secret AI as usual
    secret_ai = self.get_component(ComponentType.SECRET_AI)
    response = await secret_ai.ainvoke(messages)
    
    # 5. Check if AI response requests tool usage
    tool_calls = self._extract_tool_calls(response)
    
    if tool_calls:
        # 6. Execute tools via MCP service
        tool_results = await self._execute_tools(tool_calls)
        
        # 7. Send tool results back to AI for final response
        enhanced_response = await self._get_enhanced_response(response, tool_results)
        return enhanced_response
    
    return response
```

### Tool Execution Flow
```python
async def _execute_tools(self, tool_calls):
    """Execute MCP tools and format results for AI"""
    mcp_service = self.get_component(ComponentType.MCP_SERVICE)
    tool_results = []
    
    for tool_call in tool_calls:
        try:
            # Execute tool via MCP service
            result = await mcp_service.execute_tool(
                tool_call["name"],
                tool_call["arguments"]
            )
            
            # Format result for AI consumption
            tool_results.append({
                "tool": tool_call["name"],
                "success": True,
                "result": result
            })
            
        except Exception as e:
            # Handle tool execution errors gracefully
            tool_results.append({
                "tool": tool_call["name"], 
                "success": False,
                "error": str(e)
            })
    
    return tool_results
```

## Streaming Integration

### Enhanced Streaming with Tool Support
```python
async def stream_message(self, interface: str, message: str, options: Optional[Dict[str, Any]] = None) -> AsyncGenerator[Dict[str, Any], None]:
    """
    Enhanced streaming with real-time tool execution updates
    """
    # 1. Start AI streaming as usual
    async for chunk in secret_ai.stream_invoke(messages):
        yield chunk
        
        # 2. Check for tool calls in streaming chunks
        if self._chunk_contains_tool_call(chunk):
            # 3. Yield tool execution start notification
            yield {
                "success": True,
                "chunk": {
                    "type": "tool_execution_start",
                    "data": "Executing tool...",
                    "metadata": {"tool_name": tool_name}
                }
            }
            
            # 4. Execute tool
            tool_result = await mcp_service.execute_tool(tool_name, arguments)
            
            # 5. Yield tool execution result
            yield {
                "success": True,
                "chunk": {
                    "type": "tool_execution_result",
                    "data": tool_result,
                    "metadata": {"tool_name": tool_name}
                }
            }
```

## Component Integration Patterns

### Initialization Sequence
```python
async def initialize(self) -> None:
    """Enhanced hub initialization with MCP support"""
    
    # 1. Initialize Secret AI (existing)
    secret_ai = self.get_component(ComponentType.SECRET_AI)
    if secret_ai:
        logger.info("Secret AI service ready")
    
    # 2. Initialize MCP Service (new)
    mcp_service = self.get_component(ComponentType.MCP_SERVICE)
    if mcp_service:
        await mcp_service.initialize()
        logger.info("MCP service ready")
        
        # 3. Discover and log available capabilities
        tools = await mcp_service.get_available_tools()
        resources = await mcp_service.get_available_resources()
        logger.info(f"MCP capabilities: {len(tools)} tools, {len(resources)} resources")
    
    self.initialized = True
```

### System Status Integration
```python
async def get_system_status(self) -> Dict[str, Any]:
    """Enhanced system status with MCP information"""
    status = {
        "hub": "operational",
        "components": {}
    }
    
    # Check existing components
    for comp_type, component in self.components.items():
        if comp_type == ComponentType.SECRET_AI:
            # Existing Secret AI status check
            status["components"]["secret_ai"] = "operational"
            
        elif comp_type == ComponentType.MCP_SERVICE:
            # New MCP service status check
            mcp_status = await component.get_status()
            status["components"]["mcp_service"] = mcp_status
            
            # Include MCP capabilities summary
            status["mcp_capabilities"] = {
                "servers": len(component.servers),
                "tools": len(component.tools),
                "resources": len(component.resources)
            }
    
    return status
```

## Attestation Integration

### Including MCP Operations in TEE Proofs

```python
class AttestationAwareMCPService(MCPService):
    """MCP Service with TEE attestation integration"""
    
    def __init__(self, attestation_service):
        super().__init__()
        self.attestation_service = attestation_service
        self.operation_log = []  # Track all MCP operations
    
    async def execute_tool(self, tool_name, arguments):
        """Execute tool with attestation logging"""
        # 1. Log operation start
        operation_id = self._log_operation_start("tool_execution", {
            "tool_name": tool_name,
            "arguments": arguments,
            "timestamp": time.time()
        })
        
        try:
            # 2. Execute tool via parent method
            result = await super().execute_tool(tool_name, arguments)
            
            # 3. Log successful completion
            self._log_operation_complete(operation_id, {
                "success": True,
                "result_hash": self._hash_result(result)
            })
            
            return result
            
        except Exception as e:
            # 4. Log error
            self._log_operation_complete(operation_id, {
                "success": False,
                "error": str(e)
            })
            raise
    
    def get_attestation_data(self):
        """Get MCP operations for inclusion in attestation proof"""
        return {
            "mcp_operations": self.operation_log,
            "servers_connected": list(self.servers.keys()),
            "capabilities": self.capabilities
        }
```

### Integration with Proof Generation

```python
# In interfaces/web_ui/encryption/proof_manager.py integration
async def generate_proof_with_mcp(self, question, answer, password, mcp_operations=None):
    """Enhanced proof generation including MCP operations"""
    
    # 1. Get standard attestation data
    attestation_data = await self.attestation_service.get_dual_attestation()
    
    # 2. Get MCP operation data
    if mcp_operations:
        attestation_data["mcp_operations"] = mcp_operations
    
    # 3. Generate proof including MCP context
    proof_data = {
        "conversation": {
            "question": question,
            "answer": answer,
            "mcp_tools_used": mcp_operations or []
        },
        "attestation": attestation_data,
        "timestamp": time.time()
    }
    
    return await self._encrypt_and_save_proof(proof_data, password)
```

## Error Handling and Fallbacks

### Graceful MCP Failures

```python
async def route_message_with_fallback(self, interface: str, message: str, options: Optional[Dict[str, Any]] = None):
    """Message routing with graceful MCP fallback"""
    
    try:
        # Attempt MCP-enhanced routing
        return await self.route_message(interface, message, options)
        
    except MCPServiceUnavailable:
        # Fall back to Secret AI only
        logger.warning("MCP service unavailable, falling back to Secret AI only")
        return await self._route_message_secret_ai_only(interface, message, options)
    
    except MCPToolExecutionError as e:
        # Tool execution failed, but continue with AI response
        logger.error(f"MCP tool execution failed: {e}")
        
        # Include tool failure context in AI prompt
        enhanced_options = options or {}
        enhanced_options["tool_execution_errors"] = [str(e)]
        
        return await self._route_message_secret_ai_only(interface, message, enhanced_options)
```

### Connection Recovery

```python
async def maintain_mcp_connections(self):
    """Background task to maintain MCP server connections"""
    while self.initialized:
        for server_id, connection in self.servers.items():
            try:
                # Health check
                await connection.ping()
                
            except ConnectionError:
                logger.warning(f"MCP server {server_id} disconnected, attempting reconnection")
                
                try:
                    # Attempt reconnection
                    await self._reconnect_server(server_id)
                    logger.info(f"Successfully reconnected to MCP server {server_id}")
                    
                except Exception as e:
                    logger.error(f"Failed to reconnect to MCP server {server_id}: {e}")
        
        # Check every 30 seconds
        await asyncio.sleep(30)
```

## Web UI Integration Points

### Enhanced API Endpoints

```python
# New MCP-specific endpoints in interfaces/web_ui/app.py

@app.get("/api/v1/mcp/tools")
async def get_available_tools():
    """Get list of available MCP tools"""
    mcp_service = hub_router.get_component(ComponentType.MCP_SERVICE)
    if not mcp_service:
        raise HTTPException(status_code=503, detail="MCP service not available")
    
    tools = await mcp_service.get_available_tools()
    return {"tools": tools}

@app.get("/api/v1/mcp/resources")  
async def get_available_resources():
    """Get list of available MCP resources"""
    mcp_service = hub_router.get_component(ComponentType.MCP_SERVICE)
    if not mcp_service:
        raise HTTPException(status_code=503, detail="MCP service not available")
    
    resources = await mcp_service.get_available_resources()
    return {"resources": resources}

@app.post("/api/v1/mcp/tools/{tool_name}/execute")
async def execute_tool_directly(tool_name: str, arguments: dict):
    """Direct tool execution for testing/debugging"""
    mcp_service = hub_router.get_component(ComponentType.MCP_SERVICE)
    if not mcp_service:
        raise HTTPException(status_code=503, detail="MCP service not available")
    
    try:
        result = await mcp_service.execute_tool(tool_name, arguments)
        return {"success": True, "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### Enhanced Chat Interface

```javascript
// Enhanced chat.js with MCP tool awareness
class EnhancedChatInterface {
    
    handleStreamingResponse(eventData) {
        const chunk = eventData.chunk;
        
        switch(chunk.type) {
            case 'tool_execution_start':
                this.showToolExecutionIndicator(chunk.metadata.tool_name);
                break;
                
            case 'tool_execution_result':
                this.displayToolResult(chunk.metadata.tool_name, chunk.data);
                break;
                
            case 'stream_error':
                this.handleStreamError(chunk.data);
                break;
                
            default:
                this.appendMessageChunk(chunk.data);
        }
    }
    
    showToolExecutionIndicator(toolName) {
        const indicator = document.createElement('div');
        indicator.className = 'tool-execution-indicator';
        indicator.innerHTML = `
            <i class="fas fa-cog fa-spin"></i>
            Executing tool: ${toolName}
        `;
        this.chatContainer.appendChild(indicator);
    }
}
```

## Development and Testing Strategy

### Phase 1: Basic Integration
1. **Add MCP service component** to hub router
2. **Implement basic tool discovery** and execution
3. **Test with simple file system tools**
4. **Validate attestation inclusion**

### Phase 2: Advanced Features  
1. **Add resource support** for data access
2. **Implement real-time subscriptions**
3. **Add Secret Network specific tools**
4. **Enhance streaming with tool execution**

### Phase 3: Production Readiness
1. **Comprehensive error handling** and fallbacks
2. **Performance optimization** and caching
3. **Security hardening** and validation
4. **Monitoring and metrics** integration

### Testing Approach

```python
# Example test structure
class TestMCPHubIntegration:
    
    async def test_mcp_service_registration(self):
        """Test MCP service registers correctly with hub"""
        hub = HubRouter()
        mcp_service = MCPService()
        
        hub.register_component(ComponentType.MCP_SERVICE, mcp_service)
        
        assert hub.get_component(ComponentType.MCP_SERVICE) == mcp_service
    
    async def test_enhanced_message_routing(self):
        """Test message routing with MCP tools"""
        # Setup hub with both Secret AI and MCP services
        hub = await self._setup_test_hub()
        
        # Send message that should trigger tool usage
        response = await hub.route_message(
            interface="test",
            message="What files are in the current directory?",
            options={"enable_tools": True}
        )
        
        # Verify tool was executed and result included
        assert response["success"]
        assert "tool_results" in response
    
    async def test_attestation_integration(self):
        """Test MCP operations included in attestation"""
        # Execute some MCP operations
        mcp_service = self._get_mcp_service()
        await mcp_service.execute_tool("list_files", {"path": "/app"})
        
        # Generate attestation proof
        attestation_data = mcp_service.get_attestation_data()
        
        # Verify MCP operations are included
        assert "mcp_operations" in attestation_data
        assert len(attestation_data["mcp_operations"]) > 0
```

---

**Next Steps:**
- Review **[MCP Transport Selection](../transport/mcp-transport-selection.md)** for choosing appropriate communication methods
- Study **[Security Model](../security/mcp-security-model.md)** for TEE integration considerations  
- Explore **[Implementation Guide](../implementation/mcp-server-development.md)** for building custom MCP servers
