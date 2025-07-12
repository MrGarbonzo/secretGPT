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
        
        # Get Secret AI service
        secret_ai = self.get_component(ComponentType.SECRET_AI)
        if not secret_ai:
            logger.error("Secret AI service not registered")
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
                system_prompt += f"\n\nYou have access to the following Secret Network tools:\n{tool_descriptions}\n\nWhen a user asks about Secret Network data (balances, blocks, transactions, accounts, contracts, or network status), you should use the appropriate tool by responding with: USE_TOOL: tool_name with arguments {{...}}\n\nFor example:\n- For chain info: USE_TOOL: secret_network_status with arguments {{}}\n- For balance: USE_TOOL: secret_query_balance with arguments {{\"address\": \"secret1abc...\"}}\n- For latest block: USE_TOOL: secret_query_block with arguments {{}}"
            
            # Format messages using Secret AI's helper method
            messages = secret_ai.format_messages(system_prompt, message)
            
            # Route through Secret AI service
            response = await secret_ai.ainvoke(messages)
            
            # Check if AI response requests tool usage
            tool_calls = self._extract_tool_calls(response)
            
            if tool_calls and enable_tools:
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
        mcp_service = self.get_component(ComponentType.MCP_SERVICE)
        if not mcp_service:
            return []
            
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
                logger.error(f"Tool execution failed for {tool_call['name']}: {e}")
        
        return tool_results
    
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