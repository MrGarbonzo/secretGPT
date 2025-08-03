"""
Hub Router - Central message routing and component management
Implements the core hub architecture for secretGPT
"""
import asyncio
import logging
from typing import Dict, Any, Optional, Callable, List, AsyncGenerator
from enum import Enum

logger = logging.getLogger(__name__)


class ComponentType(Enum):
    """Types of components that can register with the hub"""
    SECRET_AI = "secret_ai"
    WEB_UI = "web_ui"
    MCP_SERVICE = "mcp_service"
    MULTI_UI_SERVICE = "multi_ui_service"
    SECRET_GPTEE_UI = "secret_gptee_ui"
    WALLET_PROXY = "wallet_proxy"


class HubRouter:
    """
    Central hub router for message routing and component management
    Manages all communication between interfaces and services
    """
    
    def __init__(self):
        """Initialize the hub router with component registry"""
        self.components: Dict[ComponentType, Any] = {}
        self.message_handlers: Dict[str, Callable] = {}
        self.initialized = False
        logger.info("Hub Router initialized")
    
    def register_component(self, component_type: ComponentType, component: Any) -> None:
        """
        Register a component with the hub
        
        Args:
            component_type: Type of component being registered
            component: The component instance
        """
        self.components[component_type] = component
        logger.info(f"Registered component: {component_type.value}")
    
    def get_component(self, component_type: ComponentType) -> Optional[Any]:
        """
        Get a registered component
        
        Args:
            component_type: Type of component to retrieve
            
        Returns:
            Component instance or None if not registered
        """
        return self.components.get(component_type)
    
    async def route_message(self, interface: str, message: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Route a message from an interface through the appropriate service with MCP tool support
        
        Args:
            interface: Source interface (web_ui, telegram_bot, etc.)
            message: The user's message
            options: Optional parameters (temperature, model, enable_tools, etc.)
            
        Returns:
            Dict containing the response and metadata
        """
        logger.info(f"Routing message from {interface} (length: {len(message)} chars)")
        
        # DEBUG: Log the exact message received
        logger.info(f"DEBUG: Raw message received: '{message}'")
        logger.info(f"DEBUG: Message starts with '/mcp': {message.strip().startswith('/mcp')}")
        
        # Handle debug commands first (bypass AI) - support multiple formats
        message_clean = message.strip().lower()
        logger.info(f"DEBUG: Cleaned message: '{message_clean}'")
        
        if (message.strip().startswith('/mcp') or 
            message_clean.startswith('mcp ') or
            message_clean in ['mcp test', 'mcp status', 'mcp tools', 'test mcp', 'mcp help']):
            # Normalize the command format
            logger.info(f"DEBUG: MCP command detected! Processing...")
            if not message.strip().startswith('/'):
                normalized_cmd = f"/mcp {message_clean.replace('mcp ', '').replace('test mcp', 'test').strip()}"
            else:
                normalized_cmd = message.strip()
            logger.info(f"DEBUG: Normalized command: '{normalized_cmd}'")
            return await self._handle_mcp_debug_command(normalized_cmd, interface)
        
        logger.info(f"DEBUG: Not an MCP command, proceeding with Keplr → MCP → LLM priority chain")
        
        # LAYER 1: Check Keplr wallet data first (highest priority)
        wallet_connected = options.get("wallet_connected", False) if options else False
        wallet_address = options.get("wallet_address") if options else None
        
        if wallet_connected and wallet_address:
            logger.info(f"🔵 KEPLR LAYER: Checking if Keplr can handle query...")
            keplr_response = await self._check_keplr_data(message, wallet_connected, wallet_address)
            if keplr_response:
                logger.info(f"🔵 KEPLR LAYER: Query handled directly by Keplr layer")
                return keplr_response
            else:
                logger.info(f"🔵 KEPLR LAYER: Cannot handle query, passing to MCP layer")
        else:
            logger.info(f"🔵 KEPLR LAYER: Wallet not connected, skipping to MCP layer")
        
        # LAYER 2: Check MCP/Secret Network queries (medium priority) 
        logger.info(f"🟠 MCP LAYER: Checking for Secret Network queries...")
        forced_tool_calls = self._detect_secret_network_queries(message, wallet_address)
        if forced_tool_calls:
            logger.info(f"🟠 MCP LAYER: Secret Network query detected, executing tools: {[tc['name'] for tc in forced_tool_calls]}")
            
            # Execute MCP tools and return result
            try:
                tool_results = await self._execute_tools(forced_tool_calls)
                
                # Format tool results for display
                tool_summary = "\n\n".join([
                    f"**{result['tool']}**: " + 
                    (self._format_tool_result(result['result']) if result['success'] else f"Error - {result['error']}")
                    for result in tool_results
                ])
                
                return {
                    "success": True,
                    "content": f"🔗 **Secret Network Tool Results**\n\n{tool_summary}",
                    "interface": interface,
                    "model": "mcp_service",
                    "source": "mcp_layer",
                    "tools_used": [tc['name'] for tc in forced_tool_calls]
                }
                
            except Exception as e:
                logger.error(f"🟠 MCP LAYER: Tool execution failed: {e}")
                # Fall through to LLM layer
                logger.info(f"🟠 MCP LAYER: Failed, passing to LLM layer")
        else:
            logger.info(f"🟠 MCP LAYER: No Secret Network queries detected, passing to LLM layer")
        
        # LAYER 3: Use LLM for general questions (lowest priority)
        logger.info(f"🟢 LLM LAYER: Handling general query with AI...")
        
        # Get Secret AI service
        secret_ai = self.get_component(ComponentType.SECRET_AI)
        if not secret_ai:
            logger.error("🟢 LLM LAYER: Secret AI service not registered")
            return {
                "success": False,
                "error": "Secret AI service not available",
                "interface": interface
            }
        
        try:
            # Use default options if not provided
            if options is None:
                options = {}
            
            # Check if tools are enabled and available
            enable_tools = options.get("enable_tools", True)
            available_tools = []
            
            if enable_tools:
                mcp_service = self.get_component(ComponentType.MCP_SERVICE)
                if mcp_service and mcp_service.initialized:
                    try:
                        available_tools = await mcp_service.get_available_tools()
                        logger.info(f"Found {len(available_tools)} MCP tools available")
                    except Exception as e:
                        logger.warning(f"Failed to get MCP tools: {e}")
            
            # Enhance system prompt with tool information if available
            system_prompt = options.get("system_prompt", "You are a helpful assistant.")
            if available_tools:
                tool_descriptions = "\n".join([
                    f"- {tool['name']}: {tool['description']}"
                    for tool in available_tools
                ])
                system_prompt += f"""\n\n🔗 **IMPORTANT: Secret Network Data Access**

You have access to real-time Secret Network blockchain tools:
{tool_descriptions}

**CRITICAL**: When users ask about Secret Network/SCRT blockchain data, you MUST use these tools because:
1. Blockchain data changes constantly (new blocks, transactions, balances)
2. You cannot provide accurate current information without real-time queries
3. Users expect live, accurate blockchain data, not outdated information

**When to use tools** (be aggressive about this):
- ANY question about Secret Network status, chain info, network details
- ANY balance inquiry (even if just mentioning "balance" + Secret Network)
- ANY block information (latest, specific height, recent blocks)
- ANY transaction lookup or account details
- ANY contract state queries

**How to use tools**:
Respond with: USE_TOOL: tool_name with arguments {{...}}

**Examples**:
- "What's the Secret Network status?" → USE_TOOL: secret_network_status with arguments {{}}
- "Check balance for secret1abc..." → USE_TOOL: secret_query_balance with arguments {{"address": "secret1abc..."}}
- "Latest block info?" → USE_TOOL: secret_query_block with arguments {{}}
- "Chain information?" → USE_TOOL: secret_network_status with arguments {{}}

**Remember**: Always prioritize tool usage for Secret Network queries over general knowledge."""
            
            # Format messages using Secret AI's helper method
            messages = secret_ai.format_messages(system_prompt, message)
            
            # Route through Secret AI service
            response = await secret_ai.ainvoke(messages)
            
            # Check if AI response requests tool usage OR if we pre-detected them
            tool_calls = self._extract_tool_calls(response)
            
            # Use forced tool calls if available (more aggressive detection)
            if forced_tool_calls and enable_tools:
                logger.info(f"🎯 Using pre-detected tool calls instead of AI extraction")
                logger.info(f"🔍 Forced tools: {[tc['name'] for tc in forced_tool_calls]}")
                tool_calls = forced_tool_calls
            elif tool_calls:
                logger.info(f"🤖 AI requested tool calls: {[tc['name'] for tc in tool_calls]}")
            
            if tool_calls and enable_tools:
                logger.info(f"🛠️ TRIGGERING MCP TOOLS: {', '.join([tc['name'] for tc in tool_calls])}")
                # Execute tools via MCP service
                tool_results = await self._execute_tools(tool_calls)
                
                # Send tool results back to AI for final response
                enhanced_response = await self._get_enhanced_response(
                    secret_ai, response, tool_results, messages
                )
                
                # Add interface metadata
                enhanced_response["interface"] = interface
                enhanced_response["options"] = options
                enhanced_response["tools_used"] = [call["name"] for call in tool_calls]
                
                return enhanced_response
            
            # Add interface metadata
            response["interface"] = interface
            response["options"] = options
            
            return response
            
        except Exception as e:
            logger.error(f"Error routing message: {e}")
            return {
                "success": False,
                "error": str(e),
                "interface": interface
            }
    
    async def get_available_models(self) -> List[str]:
        """
        Get list of available models from Secret AI
        
        Returns:
            List of available model names
        """
        secret_ai = self.get_component(ComponentType.SECRET_AI)
        if not secret_ai:
            return []
        
        return secret_ai.get_available_models()
    
    async def stream_message(self, interface: str, message: str, options: Optional[Dict[str, Any]] = None) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stream a message response from an interface through the appropriate service
        
        Args:
            interface: Source interface (web_ui, telegram_bot, etc.)
            message: The user's message
            options: Optional parameters (temperature, model, etc.)
            
        Yields:
            Dict containing streaming chunks and metadata
        """
        logger.info(f"Streaming message from {interface} (length: {len(message)} chars)")
        
        # DEBUG: Log the exact message received for streaming
        logger.info(f"DEBUG STREAM: Raw message received: '{message}'")
        logger.info(f"DEBUG STREAM: Message starts with '/mcp': {message.strip().startswith('/mcp')}")
        
        # Handle debug commands first (bypass AI) - support multiple formats
        message_clean = message.strip().lower()
        logger.info(f"DEBUG STREAM: Cleaned message: '{message_clean}'")
        
        # Implement Keplr → MCP → LLM priority chain for streaming
        wallet_connected = options.get("wallet_connected", False) if options else False
        wallet_address = options.get("wallet_address") if options else None
        
        # LAYER 1: Check Keplr wallet data first
        if wallet_connected and wallet_address:
            logger.info(f"🔵 KEPLR LAYER STREAM: Checking if Keplr can handle query...")
            keplr_response = await self._check_keplr_data(message, wallet_connected, wallet_address)
            if keplr_response:
                logger.info(f"🔵 KEPLR LAYER STREAM: Query handled directly by Keplr layer")
                yield {
                    "success": True,
                    "chunk": {
                        "type": "keplr_response",
                        "data": keplr_response["content"],
                        "metadata": {"keplr_direct": True, "source": "keplr_layer"}
                    },
                    "interface": interface,
                    "model": "keplr_wallet"
                }
                return
            else:
                logger.info(f"🔵 KEPLR LAYER STREAM: Cannot handle query, passing to MCP layer")
        else:
            logger.info(f"🔵 KEPLR LAYER STREAM: Wallet not connected, skipping to MCP layer")
        
        # LAYER 2: Check MCP/Secret Network queries
        logger.info(f"🟠 MCP LAYER STREAM: Checking for Secret Network queries...")
        forced_tool_calls = self._detect_secret_network_queries(message, wallet_address)
        logger.info(f"🟠 MCP LAYER STREAM: Secret Network pre-detection found {len(forced_tool_calls)} tool calls")
        if forced_tool_calls:
            logger.info(f"🟠 MCP LAYER STREAM: Secret Network query detected! Executing tools: {[tc['name'] for tc in forced_tool_calls]}")
            
            # Execute tools and return response
            try:
                tool_results = await self._execute_tools(forced_tool_calls)
                
                # Format tool results for display
                tool_summary = "\n\n".join([
                    f"**{result['tool']}**: " + 
                    (self._format_tool_result(result['result']) if result['success'] else f"Error - {result['error']}")
                    for result in tool_results
                ])
                
                # Create MCP-style response for consistency
                yield {
                    "success": True,
                    "chunk": {
                        "type": "mcp_response",
                        "data": f"🔗 **Secret Network Tool Results**\n\n{tool_summary}",
                        "metadata": {"mcp_command": True, "tool_execution": True, "tools_used": [tc['name'] for tc in forced_tool_calls]}
                    },
                    "interface": interface,
                    "model": "mcp_service"
                }
                return
                
            except Exception as e:
                logger.error(f"🟠 MCP LAYER STREAM: Secret Network tool execution failed: {e}")
                # Fall through to LLM layer
                logger.info("🟠 MCP LAYER STREAM: Falling back to LLM layer")
        else:
            logger.info(f"🟠 MCP LAYER STREAM: No Secret Network queries detected, passing to LLM layer")
        
        # LAYER 3: Use LLM for general questions
        logger.info(f"🟢 LLM LAYER STREAM: Handling general query with AI...")
        
        if (message.strip().startswith('/mcp') or 
            message_clean.startswith('mcp ') or
            message_clean in ['mcp test', 'mcp status', 'mcp tools', 'test mcp', 'mcp help']):
            # MCP commands should return non-streaming response
            logger.info(f"DEBUG STREAM: MCP command detected! Converting to non-streaming response")
            if not message.strip().startswith('/'):
                normalized_cmd = f"/mcp {message_clean.replace('mcp ', '').replace('test mcp', 'test').strip()}"
            else:
                normalized_cmd = message.strip()
            logger.info(f"DEBUG STREAM: Normalized command: '{normalized_cmd}'")
            
            # Get the MCP command response
            mcp_response = await self._handle_mcp_debug_command(normalized_cmd, interface)
            
            # Convert to streaming format
            yield {
                "success": mcp_response.get("success", True),
                "chunk": {
                    "type": "mcp_response",
                    "data": mcp_response.get("content", ""),
                    "metadata": {"mcp_command": True, "debug_command": True}
                },
                "interface": interface,
                "model": "mcp_service"
            }
            return
        
        logger.info(f"DEBUG STREAM: Not an MCP command, proceeding with normal streaming")
        
        # Get Secret AI service
        secret_ai = self.get_component(ComponentType.SECRET_AI)
        if not secret_ai:
            logger.error("Secret AI service not registered")
            yield {
                "success": False,
                "error": "Secret AI service not available",
                "interface": interface,
                "chunk": {
                    "type": "stream_error",
                    "data": "Secret AI service not available",
                    "metadata": {"error": True}
                }
            }
            return
        
        try:
            # Use default options if not provided
            if options is None:
                options = {}
            
            # Format messages using Secret AI's helper method
            system_prompt = options.get("system_prompt", "You are a helpful assistant.")
            messages = secret_ai.format_messages(system_prompt, message)
            
            # Stream through Secret AI service
            async for chunk_response in secret_ai.stream_invoke(messages):
                # Add interface metadata to each chunk
                chunk_response["interface"] = interface
                chunk_response["options"] = options
                
                yield chunk_response
                
        except Exception as e:
            logger.error(f"Error streaming message: {e}")
            yield {
                "success": False,
                "error": str(e),
                "interface": interface,
                "chunk": {
                    "type": "stream_error",
                    "data": str(e),
                    "metadata": {"error": True}
                }
            }

    async def get_system_status(self) -> Dict[str, Any]:
        """
        Get overall system status
        
        Returns:
            Dict containing status of all components
        """
        status = {
            "hub": "operational",
            "components": {}
        }
        
        # Check each registered component
        for comp_type, component in self.components.items():
            try:
                # Basic check - component exists
                status["components"][comp_type.value] = "registered"
                
                # For Secret AI, check if initialized
                if comp_type == ComponentType.SECRET_AI and hasattr(component, 'chat_client'):
                    if component.chat_client:
                        status["components"][comp_type.value] = "operational"
                    else:
                        status["components"][comp_type.value] = "not_initialized"
                        
            except Exception as e:
                status["components"][comp_type.value] = f"error: {str(e)}"
        
        # Check MCP service status
        mcp_service = self.get_component(ComponentType.MCP_SERVICE)
        if mcp_service:
            try:
                mcp_status = await mcp_service.get_status()
                status["components"]["mcp_service"] = "operational" if mcp_status["initialized"] else "not_initialized"
                
                # Include MCP capabilities summary
                status["mcp_capabilities"] = {
                    "servers": len(mcp_status.get("servers", {})),
                    "tools": mcp_status["capabilities"].get("tools", 0),
                    "resources": mcp_status["capabilities"].get("resources", 0)
                }
            except Exception as e:
                status["components"]["mcp_service"] = f"error: {str(e)}"
        
        return status
    
    async def initialize(self) -> None:
        """
        Initialize the hub router and all registered components
        """
        if self.initialized:
            logger.warning("Hub router already initialized")
            return
        
        logger.info("Initializing hub router...")
        
        # Initialize Secret AI if registered
        secret_ai = self.get_component(ComponentType.SECRET_AI)
        if secret_ai:
            logger.info("Secret AI service found and ready")
        
        # Initialize MCP Service if registered
        mcp_service = self.get_component(ComponentType.MCP_SERVICE)
        if mcp_service:
            try:
                await mcp_service.initialize()
                
                # Discover and log available capabilities
                tools = await mcp_service.get_available_tools()
                resources = await mcp_service.get_available_resources()
                logger.info(f"MCP service ready: {len(tools)} tools, {len(resources)} resources")
            except Exception as e:
                logger.error(f"Failed to initialize MCP service: {e}")
        
        self.initialized = True
        logger.info("Hub router initialization complete")
    
    async def shutdown(self) -> None:
        """
        Gracefully shutdown the hub and all components
        """
        logger.info("Shutting down hub router...")
        
        # Add any cleanup logic here
        
        self.initialized = False
        # Shutdown MCP service if registered
        mcp_service = self.get_component(ComponentType.MCP_SERVICE)
        if mcp_service:
            try:
                await mcp_service.shutdown()
            except Exception as e:
                logger.error(f"Error shutting down MCP service: {e}")
        
        logger.info("Hub router shutdown complete")
    
    async def _handle_mcp_debug_command(self, command: str, interface: str) -> Dict[str, Any]:
        """
        Handle MCP debug commands that bypass AI processing
        
        Args:
            command: The debug command (e.g., '/mcp status')
            interface: Source interface
            
        Returns:
            Direct response from MCP operations
        """
        logger.info(f"Processing MCP debug command: {command}")
        
        try:
            parts = command.split()
            if len(parts) < 2:
                return {
                    "success": True,
                    "content": "Available MCP debug commands:\n" +
                              "• /mcp status - Check MCP service status\n" +
                              "• /mcp test - Test Secret Network connection\n" +
                              "• /mcp tools - List available tools\n" +
                              "• /mcp exec <tool_name> - Execute specific tool",
                    "interface": interface,
                    "debug_command": True
                }
            
            sub_command = parts[1].lower()
            mcp_service = self.get_component(ComponentType.MCP_SERVICE)
            
            if sub_command == "status":
                if not mcp_service:
                    return {
                        "success": False,
                        "content": "❌ MCP service not available - service not registered",
                        "interface": interface,
                        "debug_command": True
                    }
                
                status = await mcp_service.get_status()
                status_text = f"""🔧 **MCP Service Status**
                
**Service**: {'✅ Operational' if status['initialized'] else '❌ Not initialized'}
**Servers**: {len(status.get('servers', {}))} connected
**Tools**: {status['capabilities'].get('tools', 0)} available
**Resources**: {status['capabilities'].get('resources', 0)} available
**Operations Logged**: {status.get('operations_logged', 0)}

**Server Details**:
{chr(10).join([f"• {srv}: {stat}" for srv, stat in status.get('servers', {}).items()])}"""
                
                return {
                    "success": True,
                    "content": status_text,
                    "interface": interface,
                    "debug_command": True,
                    "mcp_status": status
                }
            
            elif sub_command == "tools":
                if not mcp_service or not mcp_service.initialized:
                    return {
                        "success": False,
                        "content": "❌ MCP service not available or not initialized",
                        "interface": interface,
                        "debug_command": True
                    }
                
                tools = await mcp_service.get_available_tools()
                tools_text = f"🛠️ **Available MCP Tools** ({len(tools)} total):\n\n"
                for tool in tools:
                    tools_text += f"• **{tool['name']}**: {tool['description']}\n"
                    if 'server_id' in tool:
                        tools_text += f"  ↳ Server: {tool['server_id']}\n"
                
                return {
                    "success": True,
                    "content": tools_text,
                    "interface": interface,
                    "debug_command": True,
                    "available_tools": tools
                }
            
            elif sub_command == "test":
                if not mcp_service or not mcp_service.initialized:
                    return {
                        "success": False,
                        "content": "❌ MCP service not available or not initialized",
                        "interface": interface,
                        "debug_command": True
                    }
                
                logger.info("Executing MCP test - secret_network_status tool")
                try:
                    result = await mcp_service.execute_tool("secret_network_status", {})
                    test_text = f"""🧪 **MCP Test Results**
                    
**Tool**: secret_network_status
**Status**: ✅ Success
**Response**: 
```
{result}
```"""
                    return {
                        "success": True,
                        "content": test_text,
                        "interface": interface,
                        "debug_command": True,
                        "tool_result": result
                    }
                except Exception as e:
                    return {
                        "success": False,
                        "content": f"❌ **MCP Test Failed**\n\nError executing secret_network_status: {str(e)}",
                        "interface": interface,
                        "debug_command": True,
                        "error": str(e)
                    }
            
            elif sub_command == "exec":
                if len(parts) < 3:
                    return {
                        "success": False,
                        "content": "❌ Usage: /mcp exec <tool_name>\nExample: /mcp exec secret_network_status",
                        "interface": interface,
                        "debug_command": True
                    }
                
                if not mcp_service or not mcp_service.initialized:
                    return {
                        "success": False,
                        "content": "❌ MCP service not available or not initialized",
                        "interface": interface,
                        "debug_command": True
                    }
                
                tool_name = parts[2]
                logger.info(f"Executing MCP tool directly: {tool_name}")
                try:
                    result = await mcp_service.execute_tool(tool_name, {})
                    exec_text = f"""⚡ **Direct Tool Execution**
                    
**Tool**: {tool_name}
**Status**: ✅ Success
**Response**:
```
{result}
```"""
                    return {
                        "success": True,
                        "content": exec_text,
                        "interface": interface,
                        "debug_command": True,
                        "tool_result": result
                    }
                except Exception as e:
                    return {
                        "success": False,
                        "content": f"❌ **Tool Execution Failed**\n\nError executing {tool_name}: {str(e)}",
                        "interface": interface,
                        "debug_command": True,
                        "error": str(e)
                    }
            
            else:
                return {
                    "success": False,
                    "content": f"❌ Unknown MCP command: {sub_command}\n\nUse '/mcp' to see available commands",
                    "interface": interface,
                    "debug_command": True
                }
                
        except Exception as e:
            logger.error(f"Error handling MCP debug command: {e}")
            return {
                "success": False,
                "content": f"❌ **MCP Debug Command Error**\n\n{str(e)}",
                "interface": interface,
                "debug_command": True,
                "error": str(e)
            }
    
    async def _check_keplr_data(self, message: str, wallet_connected: bool = False, wallet_address: str = None) -> Dict[str, Any]:
        """
        Check if query can be answered directly from connected Keplr wallet data
        This is the FIRST layer in the Keplr → MCP → LLM chain
        
        Args:
            message: The user's message
            wallet_connected: Whether Keplr wallet is connected
            wallet_address: The connected wallet address
            
        Returns:
            Response dict if handled, None if should pass to next layer
        """
        if not wallet_connected or not wallet_address:
            return None
            
        message_lower = message.lower()
        
        try:
            # Personal balance queries - get directly from wallet API
            if any(keyword in message_lower for keyword in [
                'my balance', 'my scrt', 'my wallet balance', 'my account balance',
                'what is my balance', 'show my balance', 'check my balance',
                'how much scrt do i have', 'how much do i have',
                'what\'s my balance', 'whats my balance',
                'my scrt balance', 'my secret balance'
            ]):
                logger.info(f"🔵 KEPLR LAYER: Handling personal balance query for {wallet_address}")
                
                # Get balance directly from our wallet service
                balance_result = await self.get_wallet_balance(wallet_address)
                if balance_result.get("success"):
                    balance_amount = balance_result.get("balance", {}).get("amount", "0")
                    formatted_balance = balance_result.get("formatted", "0.000000 SCRT")
                    
                    response_text = f"💰 **Your SCRT Balance**\n\n**{formatted_balance}**\n\nAddress: `{wallet_address}`"
                    if balance_result.get("mock_data"):
                        response_text += "\n\n*Note: Using fallback data for testing*"
                    
                    return {
                        "success": True,
                        "content": response_text,
                        "interface": "keplr_direct",
                        "model": "keplr_wallet",
                        "source": "keplr_layer",
                        "wallet_data": balance_result
                    }
            
            # Wallet address queries
            elif any(keyword in message_lower for keyword in [
                'my address', 'my wallet address', 'what is my address',
                'show my address', 'my secret address', 'wallet address'
            ]):
                logger.info(f"🔵 KEPLR LAYER: Handling address query for {wallet_address}")
                
                # Format address for display
                short_address = f"{wallet_address[:10]}...{wallet_address[-8:]}"
                
                return {
                    "success": True,
                    "content": f"🏠 **Your Wallet Address**\n\n**Full Address:**\n`{wallet_address}`\n\n**Short Address:**\n`{short_address}`",
                    "interface": "keplr_direct", 
                    "model": "keplr_wallet",
                    "source": "keplr_layer"
                }
            
            # Wallet connection status
            elif any(keyword in message_lower for keyword in [
                'am i connected', 'is my wallet connected', 'wallet status',
                'connection status', 'is keplr connected'
            ]):
                logger.info(f"🔵 KEPLR LAYER: Handling connection status query")
                
                return {
                    "success": True,
                    "content": f"🟢 **Wallet Connected**\n\nYour Keplr wallet is connected and ready to use.\n\n**Address:** `{wallet_address}`\n**Network:** Secret Network (secret-4)",
                    "interface": "keplr_direct",
                    "model": "keplr_wallet", 
                    "source": "keplr_layer"
                }
                
        except Exception as e:
            logger.error(f"Error in Keplr data layer: {e}")
            
        # If we get here, Keplr layer cannot handle this query
        return None
    
    def _detect_secret_network_queries(self, message: str, wallet_address: str = None) -> List[Dict[str, Any]]:
        """
        Aggressively detect Secret Network queries from user message before AI processing
        This helps with AI models like DeepSeek R1 that might not follow tool instructions
        
        Args:
            message: The user's original message
            wallet_address: The connected wallet address (if any)
            
        Returns:
            List of tool calls that should be executed
        """
        tool_calls = []
        message_lower = message.lower()
        
        try:
            # Personal balance queries are now handled by Keplr layer, so skip them here
            # Balance queries with address detection (check FIRST since personal queries are handled above)
            if 'balance' in message_lower and any(term in message for term in ['secret1', 'SCRT', 'scrt']):
                secret_addr_pattern = r'secret1[a-z0-9]{38}'  # More specific pattern
                addr_matches = re.findall(secret_addr_pattern, message)
                if addr_matches:
                    for addr in addr_matches:
                        tool_calls.append({
                            "name": "secret_query_balance",
                            "arguments": {"address": addr}
                        })
                        logger.info(f"Pre-detected: Balance query for address {addr}")
                        break  # Only do first address to avoid spam
            
            # Block queries
            elif any(keyword in message_lower for keyword in [
                'latest block', 'current block', 'recent block', 'block info',
                'block information', 'block details', 'last block', 'newest block',
                'block height', 'current height', 'latest height', 'what is the block height',
                'get block height', 'show block height', 'block number'
            ]):
                tool_calls.append({
                    "name": "secret_query_block",
                    "arguments": {}
                })
                logger.info("Pre-detected: Block information query")
            
            # Specific block number queries
            elif re.search(r'block\s+(\d+)|block\s+#(\d+)|block\s+height\s+(\d+)', message_lower):
                import re
                block_number_match = re.search(r'block\s+(\d+)|block\s+#(\d+)|block\s+height\s+(\d+)', message_lower)
                block_height = int(block_number_match.group(1) or block_number_match.group(2) or block_number_match.group(3))
                tool_calls.append({
                    "name": "secret_query_block",
                    "arguments": {"height": block_height}
                })
                logger.info(f"Pre-detected: Specific block query for height {block_height}")
            
            # Network status and chain info queries (move to LAST to avoid catching balance queries)
            elif any(keyword in message_lower for keyword in [
                'secret network', 'scrt network', 'chain info', 'network status', 
                'chain information', 'network info', 'secret chain', 'scrt chain',
                'chain status', 'blockchain info', 'blockchain status'
            ]):
                # Check for status/info requests, excluding balance and transaction queries
                if any(term in message_lower for term in [
                    'status', 'info', 'information', 'details'
                ]) and not any(term in message_lower for term in ['balance', 'transaction']):
                    tool_calls.append({
                        "name": "secret_network_status",
                        "arguments": {}
                    })
                    logger.info("Pre-detected: Secret Network status query")
                # Also handle generic network/chain queries without explicit status keywords
                elif 'secret network' in message_lower and len(message_lower.split()) <= 4:
                    tool_calls.append({
                        "name": "secret_network_status",
                        "arguments": {}
                    })
                    logger.info("Pre-detected: Generic Secret Network query")
            
            # Transaction queries
            tx_hash_pattern = r'[a-fA-F0-9]{64}'  # 64-character hex string
            if any(keyword in message_lower for keyword in ['transaction', 'tx', 'txhash', 'hash']):
                tx_matches = re.findall(tx_hash_pattern, message)
                if tx_matches:
                    tool_calls.append({
                        "name": "secret_query_transaction",
                        "arguments": {"txHash": tx_matches[0]}
                    })
                    logger.info(f"Pre-detected: Transaction query for hash {tx_matches[0][:16]}...")
            
            # Account/address queries (not balance)
            if any(keyword in message_lower for keyword in [
                'account info', 'address info', 'account details', 'address details',
                'account number', 'sequence number'
            ]):
                secret_addr_pattern = r'secret1[a-z0-9]{38}'
                addr_matches = re.findall(secret_addr_pattern, message)
                if addr_matches:
                    tool_calls.append({
                        "name": "secret_query_account",
                        "arguments": {"address": addr_matches[0]}
                    })
                    logger.info(f"Pre-detected: Account query for address {addr_matches[0]}")
            
            # Simple test phrases that always trigger MCP (for testing)
            if not tool_calls:
                test_phrases = [
                    'test secret network', 'test mcp connection', 'secret network test',
                    'check secret network', 'ping secret network', 'secret network status',
                    'is secret network working', 'secret network info'
                ]
                if any(phrase in message_lower for phrase in test_phrases):
                    tool_calls.append({
                        "name": "secret_network_status",
                        "arguments": {}
                    })
                    logger.info("Pre-detected: Test phrase triggered Secret Network status")
            
            # Generic Secret Network mentions (fallback) - but exclude balance/personal queries
            if not tool_calls and any(keyword in message_lower for keyword in [
                'secret network', 'secret blockchain'
            ]) and any(question in message_lower for question in [
                'what', 'how', 'show', 'get', 'tell', 'info', 'status', 'current'
            ]) and not any(personal in message_lower for personal in [
                'my', 'balance', 'wallet', 'account', 'i have', 'scrt'
            ]):
                # Default to network status for generic queries (excluding personal/balance queries)
                tool_calls.append({
                    "name": "secret_network_status", 
                    "arguments": {}
                })
                logger.info("Pre-detected: Generic Secret Network query, defaulting to status")
                
        except Exception as e:
            logger.error(f"Error in pre-detection of Secret Network queries: {e}")
        
        logger.info(f"Pre-detection found {len(tool_calls)} tool calls")
        return tool_calls
    
    def _extract_tool_calls(self, response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract tool calls from AI response
        
        Args:
            response: AI response to analyze
            
        Returns:
            List of tool calls found in the response
        """
        tool_calls = []
        
        try:
            # Check if response contains tool call indication
            content = response.get("content", "")
            logger.info(f"Analyzing response for tool calls: {content[:200]}...")
            
            import json
            import re
            
            # Look for USE_TOOL: pattern
            use_tool_pattern = r'USE_TOOL:\s*(\w+)\s+with\s+arguments\s*(\{[^}]*\})'
            matches = re.findall(use_tool_pattern, content, re.IGNORECASE)
            
            for tool_name, args_str in matches:
                try:
                    arguments = json.loads(args_str) if args_str.strip() != '{}' else {}
                    tool_calls.append({
                        "name": tool_name,
                        "arguments": arguments
                    })
                    logger.info(f"Extracted tool call: {tool_name} with args: {arguments}")
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse tool arguments: {args_str}, error: {e}")
                    # Try with empty arguments if JSON parsing fails
                    tool_calls.append({
                        "name": tool_name,
                        "arguments": {}
                    })
            
            # Fallback: Look for old JSON format for backwards compatibility
            if not tool_calls:
                json_pattern = r'\{[^{}]*"tool_name"[^{}]*"arguments"[^{}]*\}'
                json_matches = re.findall(json_pattern, content, re.IGNORECASE)
                
                for match in json_matches:
                    try:
                        tool_call = json.loads(match)
                        if "tool_name" in tool_call and "arguments" in tool_call:
                            tool_calls.append({
                                "name": tool_call["tool_name"],
                                "arguments": tool_call["arguments"]
                            })
                            logger.info(f"Extracted JSON tool call: {tool_call['tool_name']}")
                    except json.JSONDecodeError:
                        continue
            
            # Enhanced keyword-based detection for common queries
            if not tool_calls:
                content_lower = content.lower()
                
                # Network status queries
                if any(keyword in content_lower for keyword in ['chain info', 'network status', 'chain information', 'network info']):
                    tool_calls.append({
                        "name": "secret_network_status",
                        "arguments": {}
                    })
                    logger.info("Detected network status query via keywords")
                
                # Block queries
                elif any(keyword in content_lower for keyword in ['latest block', 'current block', 'block info']):
                    tool_calls.append({
                        "name": "secret_query_block", 
                        "arguments": {}
                    })
                    logger.info("Detected block query via keywords")
                
                # Balance queries (look for secret1 addresses)
                elif 'balance' in content_lower and 'secret1' in content:
                    secret_addr_pattern = r'secret1[a-z0-9]+'
                    addr_matches = re.findall(secret_addr_pattern, content)
                    if addr_matches:
                        tool_calls.append({
                            "name": "secret_query_balance",
                            "arguments": {"address": addr_matches[0]}
                        })
                        logger.info(f"Detected balance query for address: {addr_matches[0]}")
            
            logger.info(f"Total tool calls extracted: {len(tool_calls)}")
                    
        except Exception as e:
            logger.error(f"Error extracting tool calls: {e}")
        
        return tool_calls
    
    async def _execute_tools(self, tool_calls: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute MCP tools and format results for AI"""
        logger.info(f"🔧 EXECUTING MCP TOOLS: {len(tool_calls)} tools requested")
        
        mcp_service = self.get_component(ComponentType.MCP_SERVICE)
        if not mcp_service:
            logger.error("❌ MCP service not available for tool execution")
            return []
            
        tool_results = []
        
        for i, tool_call in enumerate(tool_calls, 1):
            tool_name = tool_call["name"]
            args = tool_call["arguments"]
            
            logger.info(f"🚀 Executing tool {i}/{len(tool_calls)}: {tool_name}")
            logger.info(f"📋 Arguments: {args}")
            
            try:
                # Execute tool via MCP service
                logger.info(f"⏳ Calling Secret Network via MCP server...")
                result = await mcp_service.execute_tool(tool_name, args)
                
                logger.info(f"✅ Tool {tool_name} executed successfully")
                logger.info(f"📊 Result preview: {str(result)[:100]}{'...' if len(str(result)) > 100 else ''}")
                
                # Format result for AI consumption
                tool_results.append({
                    "tool": tool_name,
                    "success": True,
                    "result": result
                })
                
            except Exception as e:
                logger.error(f"❌ Tool {tool_name} execution failed: {str(e)}")
                # Handle tool execution errors gracefully
                tool_results.append({
                    "tool": tool_name, 
                    "success": False,
                    "error": str(e)
                })
        
        logger.info(f"🎯 MCP execution complete: {sum(1 for r in tool_results if r['success'])}/{len(tool_results)} tools succeeded")
        return tool_results
    
    def _format_tool_result(self, result: Any) -> str:
        """Format MCP tool result for display"""
        try:
            if isinstance(result, dict):
                if 'content' in result and isinstance(result['content'], list):
                    # MCP standard format with content array
                    return '\n'.join([item.get('text', str(item)) for item in result['content'] if 'text' in item])
                elif 'content' in result:
                    return str(result['content'])
                else:
                    return str(result)
            else:
                return str(result)
        except Exception as e:
            logger.error(f"Error formatting tool result: {e}")
            return f"Result formatting error: {str(e)}"
    
    async def _get_enhanced_response(self, secret_ai, original_response: Dict[str, Any], 
                                   tool_results: List[Dict[str, Any]], 
                                   original_messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Send tool results back to AI for final response"""
        try:
            # Format tool results for AI
            tool_summary = "\\n\\n".join([
                f"Tool '{result['tool']}': " + 
                (f"Success - {result['result']}" if result['success'] 
                 else f"Error - {result['error']}")
                for result in tool_results
            ])
            
            # Create enhanced prompt with tool results
            enhanced_message = (
                f"Based on the tool execution results:\\n\\n{tool_summary}\\n\\n"
                f"Please provide a comprehensive response to the user's original question."
            )
            
            # Add tool results as a system message
            enhanced_messages = original_messages + [{
                "role": "system",
                "content": enhanced_message
            }]
            
            # Get enhanced response from AI
            enhanced_response = await secret_ai.ainvoke(enhanced_messages)
            
            # Add tool execution metadata
            enhanced_response["tool_results"] = tool_results
            enhanced_response["original_response"] = original_response
            
            return enhanced_response
            
        except Exception as e:
            logger.error(f"Error getting enhanced response: {e}")
            # Fallback to original response with tool results appended
            original_response["tool_results"] = tool_results
            return original_response
    
    # Wallet Proxy Methods (Bridge-Ready for Attestation)
    
    async def connect_wallet(self, address: str, name: str = None, is_hardware: bool = False) -> Dict[str, Any]:
        """Connect wallet through MCP service directly"""
        mcp_service = self.get_component(ComponentType.MCP_SERVICE)
        if not mcp_service:
            logger.error("MCP service not registered")
            return {
                "success": False,
                "error": "MCP service not available",
                "bridge_ready": False
            }
        
        try:
            # Use MCP service to validate wallet address and store connection info
            result = await mcp_service.call_tool("secret_network_status", {})
            if result and "error" not in result:
                # If MCP service is working, consider wallet "connected" 
                # (actual connection is handled by frontend Keplr)
                logger.info(f"Wallet connection successful for address: {address}")
                return {
                    "success": True,
                    "address": address,
                    "name": name or "Keplr Wallet",
                    "isHardwareWallet": is_hardware,
                    "bridge_ready": True,
                    "mcp_available": True
                }
            else:
                return {
                    "success": False,
                    "error": "MCP service not responding",
                    "bridge_ready": True
                }
        except Exception as e:
            logger.error(f"Wallet connection failed: {e}")
            return {
                "success": False,
                "error": f"Connection failed: {str(e)}",
                "bridge_ready": True
            }
    
    async def get_wallet_balance(self, address: str) -> Dict[str, Any]:
        """Get wallet balance through direct HTTP call to secret_network_mcp"""
        import aiohttp
        import os
        
        # Check multiple possible env var names for MCP URL
        mcp_url = os.getenv("SECRET_NETWORK_MCP_URL") or os.getenv("SECRET_MCP_URL") or "http://localhost:8002"
        logger.info(f"Using MCP URL: {mcp_url}")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{mcp_url}/api/wallet/balance/{address}") as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info(f"Balance query successful for address: {address}")
                        logger.info(f"Raw balance response: {data}")
                        
                        if data.get("success"):
                            # Transform response to expected format
                            balance_amount = data.get("balance", "0")
                            return {
                                "success": True,
                                "balance": {
                                    "amount": balance_amount,
                                    "denom": data.get("denom", "uscrt")
                                },
                                "formatted": data.get("formatted", f"{float(balance_amount)/1000000:.6f} SCRT")
                            }
                        else:
                            raise Exception(f"MCP service returned error: {data.get('error', 'Unknown error')}")
                    else:
                        raise Exception(f"HTTP {response.status}: {await response.text()}")
                        
        except Exception as e:
            logger.error(f"Balance query failed: {e}")
            # Return fallback data for testing
            logger.warning(f"Using fallback balance data for address: {address}")
            return {
                "success": True,
                "balance": {
                    "amount": "1000000",  # 1.000000 SCRT fallback
                    "denom": "uscrt"
                },
                "formatted": "1.000000 SCRT",
                "mock_data": True,
                "error_msg": str(e)
            }
    
    async def get_transaction_status(self, tx_hash: str) -> Dict[str, Any]:
        """Get transaction status through MCP service directly"""
        mcp_service = self.get_component(ComponentType.MCP_SERVICE)
        if not mcp_service:
            logger.error("MCP service not registered")
            return {
                "success": False,
                "error": "MCP service not available"
            }
        
        try:
            # Use MCP service to query transaction status
            result = await mcp_service.call_tool("secret_transaction_lookup", {"tx_hash": tx_hash})
            if result and "error" not in result:
                logger.info(f"Transaction status query successful for tx: {tx_hash}")
                return {
                    "success": True,
                    **result
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error", "Transaction status query failed") if result else "No response from MCP service"
                }
        except Exception as e:
            logger.error(f"Transaction status query failed: {e}")
            return {
                "success": False,
                "error": f"Transaction status query failed: {str(e)}"
            }
    
    async def disconnect_wallet(self, address: str) -> Dict[str, Any]:
        """Disconnect wallet - no backend action needed (frontend only)"""
        try:
            # Wallet disconnection is handled entirely on the frontend
            # Just return success since there's no server-side state to clear
            logger.info(f"Wallet disconnect request for address: {address}")
            return {
                "success": True,
                "message": "Wallet disconnected (frontend handled)",
                "address": address
            }
        except Exception as e:
            logger.error(f"Wallet disconnect failed: {e}")
            return {
                "success": False,
                "error": f"Disconnect failed: {str(e)}"
            }
    
    async def get_wallet_status(self) -> Dict[str, Any]:
        """Get wallet service status through MCP service directly"""
        mcp_service = self.get_component(ComponentType.MCP_SERVICE)
        if not mcp_service:
            return {
                "success": False,
                "error": "MCP service not registered",
                "bridge_ready": False
            }
        
        try:
            # Test MCP service connectivity
            result = await mcp_service.call_tool("secret_network_status", {})
            if result and "error" not in result:
                logger.info("Wallet status check - MCP service operational")
                return {
                    "success": True,
                    "service": "Wallet Service (via MCP)",
                    "bridge_mode": "mcp_direct",
                    "attestation_ready": True,
                    "mcp_connection": True,
                    "mcp_status": {
                        "success": True,
                        "message": "Connected via hub router"
                    },
                    "interface": "secret_gptee"
                }
            else:
                return {
                    "success": False,
                    "error": "MCP service not responding",
                    "bridge_ready": True,
                    "mcp_connection": False
                }
        except Exception as e:
            logger.error(f"Wallet status check failed: {e}")
            return {
                "success": False,
                "error": f"Status check failed: {str(e)}",
                "bridge_ready": True,
                "mcp_connection": False
            }