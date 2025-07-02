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
        Route a message from an interface through the appropriate service
        
        Args:
            interface: Source interface (web_ui, telegram_bot, etc.)
            message: The user's message
            options: Optional parameters (temperature, model, etc.)
            
        Returns:
            Dict containing the response and metadata
        """
        logger.info(f"Routing message from {interface}: {message[:50]}...")
        
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
            
            # Set default temperature if not specified
            temperature = options.get("temperature", 1.0)
            
            # Format messages using Secret AI's helper method
            system_prompt = options.get("system_prompt", "You are a helpful assistant.")
            messages = secret_ai.format_messages(system_prompt, message)
            
            # Route through Secret AI service
            response = await secret_ai.ainvoke(messages)
            
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
        logger.info(f"Streaming message from {interface}: {message[:50]}...")
        
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
        
        self.initialized = True
        logger.info("Hub router initialization complete")
    
    async def shutdown(self) -> None:
        """
        Gracefully shutdown the hub and all components
        """
        logger.info("Shutting down hub router...")
        
        # Add any cleanup logic here
        
        self.initialized = False
        logger.info("Hub router shutdown complete")