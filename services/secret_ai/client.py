"""
Secret AI Service Implementation
Following the exact patterns from secret-ai-getting-started-example.py
"""
import os
import logging
from typing import List, Tuple, Dict, Any, Optional, AsyncGenerator
from secret_ai_sdk.secret_ai import ChatSecret
from secret_ai_sdk.secret import Secret
from .streaming_handler import WebStreamingHandler, StreamingChunkFormatter

logger = logging.getLogger(__name__)

# Fallback LCD nodes for Secret AI model discovery
# These are tried in order until one succeeds
FALLBACK_NODES = [
    {"chain_id": "secret-4", "node_url": "https://lcd.secret.tactus.starshell.net/", "name": "SDK Default (Tactus)"},
    {"chain_id": "secret-4", "node_url": "https://lcd.secret.express", "name": "Secret Express (mainnet)"},
    {"chain_id": "secret-4", "node_url": "https://lcd.secret.adrius.starshell.net/", "name": "StarShell (mainnet)"},
    {"chain_id": "pulsar-3", "node_url": "https://lcd.testnet.secretsaturn.net", "name": "Saturn (testnet)"},
]


class SecretAIService:
    """
    Service class for interacting with Secret AI
    Implements the model discovery pattern and message handling
    """

    def __init__(self):
        """Initialize the Secret AI service with model discovery"""
        self.secret_client = None
        self.models = []
        self.urls = []
        self.chat_client = None
        self._initialization_attempted = False
        self._working_node = None  # Cache the working node config
        self._initialize()
    
    def _initialize(self):
        """Initialize the Secret AI client with fallback node support"""
        if self._initialization_attempted:
            logger.debug("Initialization already attempted, skipping")
            return

        self._initialization_attempted = True

        # Try custom node URL from environment first
        from config.settings import settings
        if settings.secret_ai_node_url:
            chain_id = settings.secret_ai_chain_id or "secret-4"
            logger.info(f"Trying custom node URL: {settings.secret_ai_node_url}")
            if self._try_initialize_with_node(chain_id, settings.secret_ai_node_url, "Custom"):
                return

        # Try fallback nodes in order
        for node_config in FALLBACK_NODES:
            logger.info(f"Trying {node_config['name']}: {node_config['node_url']}")
            if self._try_initialize_with_node(node_config['chain_id'], node_config['node_url'], node_config['name']):
                return

        # All nodes failed
        logger.error("Failed to initialize Secret AI with all available nodes")
        logger.warning("Secret AI service will start in degraded mode. Try again later or check configuration.")

    def _try_initialize_with_node(self, chain_id: str, node_url: str, node_name: str) -> bool:
        """
        Try to initialize Secret AI client with a specific node

        Returns:
            bool: True if initialization successful, False otherwise
        """
        try:
            # REFERENCE: secret-ai-getting-started-example.py lines 4-6
            # Model discovery pattern with explicit node
            logger.debug(f"Creating Secret client with chain_id={chain_id}, node_url={node_url}")
            self.secret_client = Secret(chain_id=chain_id, node_url=node_url)

            logger.debug("Fetching available models...")
            self.models = self.secret_client.get_models()

            if not self.models:
                logger.warning(f"No models available from {node_name}")
                return False

            logger.debug(f"Found models: {self.models}")

            # Get URLs for the first available model
            self.urls = self.secret_client.get_urls(model=self.models[0])

            if not self.urls:
                logger.warning(f"No URLs available for model {self.models[0]} from {node_name}")
                return False

            # REFERENCE: secret-ai-getting-started-example.py lines 8-12
            # Client initialization pattern
            self.chat_client = ChatSecret(
                base_url=self.urls[0],
                model=self.models[0],
                temperature=1.0
            )

            # Cache the working node configuration
            self._working_node = {"chain_id": chain_id, "node_url": node_url, "name": node_name}

            logger.info(f"✓ Successfully initialized Secret AI with {node_name}")
            logger.info(f"  Model: {self.models[0]}")
            logger.info(f"  URL: {self.urls[0]}")

            return True

        except Exception as e:
            logger.warning(f"Failed to initialize with {node_name}: {e}")
            return False

    def retry_initialization(self) -> bool:
        """
        Retry initialization - useful for lazy loading on first request

        Returns:
            bool: True if successful, False otherwise
        """
        if self.chat_client is not None:
            return True  # Already initialized

        logger.info("Retrying Secret AI initialization...")
        self._initialization_attempted = False  # Reset flag
        self._initialize()

        return self.chat_client is not None
    
    def get_available_models(self) -> List[str]:
        """Get list of available models"""
        return self.models
    
    def get_current_model(self) -> Optional[str]:
        """Get the currently selected model"""
        return self.models[0] if self.models else None
    
    def invoke(self, messages: List[Tuple[str, str]], stream: bool = False) -> Dict[str, Any]:
        """
        Invoke the Secret AI chat with the given messages

        Args:
            messages: List of tuples in format [("role", "content")]
                     MUST BE TUPLES, NOT DICTS - as per documentation
            stream: Whether to stream the response

        Returns:
            Dict containing the response
        """
        # Try lazy initialization if not yet initialized
        if not self.chat_client:
            if not self.retry_initialization():
                return {
                    "success": False,
                    "error": "Secret AI service is not available. Please try again later or check your configuration.",
                    "model": None
                }
        
        try:
            # REFERENCE: secret-ai-getting-started-example.py line 22
            # Sync invocation
            response = self.chat_client.invoke(messages, stream=stream)
            
            # REFERENCE: secret-ai-getting-started-example.py line 23
            # Response content accessed via response.content
            return {
                "success": True,
                "content": response.content,
                "model": self.get_current_model()
            }
            
        except Exception as e:
            logger.error(f"Error invoking Secret AI: {e}")
            return {
                "success": False,
                "error": str(e),
                "model": self.get_current_model()
            }
    
    async def ainvoke(self, messages: List[Tuple[str, str]]) -> Dict[str, Any]:
        """
        Async invocation for Secret AI chat

        Args:
            messages: List of tuples in format [("role", "content")]

        Returns:
            Dict containing the response
        """
        # Try lazy initialization if not yet initialized
        if not self.chat_client:
            if not self.retry_initialization():
                return {
                    "success": False,
                    "error": "Secret AI service is not available. Please try again later or check your configuration.",
                    "model": None
                }
        
        try:
            # REFERENCE: secret-ai-streaming-example.py line 103
            # Async invocation for hub integration
            response = await self.chat_client.ainvoke(messages)
            
            return {
                "success": True,
                "content": response.content,
                "model": self.get_current_model()
            }
            
        except Exception as e:
            logger.error(f"Error in async invoke: {e}")
            return {
                "success": False,
                "error": str(e),
                "model": self.get_current_model()
            }
    
    async def stream_invoke(self, messages: List[Tuple[str, str]]) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stream responses from Secret AI using custom web streaming handler

        Args:
            messages: List of tuples in format [("role", "content")]

        Yields:
            Dict containing streaming chunks with type, data, and metadata
        """
        # Try lazy initialization if not yet initialized
        if not self.chat_client:
            if not self.retry_initialization():
                yield {
                    "success": False,
                    "chunk": {
                        "type": "stream_error",
                        "data": "Secret AI service is not available. Please try again later or check your configuration.",
                        "metadata": {"error": True, "initialization_failed": True}
                    },
                    "error": "Secret AI service is not available",
                    "model": None
                }
                return
        
        try:
            # Create web streaming handler
            stream_handler = WebStreamingHandler(width=60)
            
            # Create new chat client with streaming handler
            streaming_client = ChatSecret(
                base_url=self.urls[0],
                model=self.models[0],
                temperature=1.0,
                callbacks=[stream_handler]
            )
            
            # Start streaming invocation
            logger.info(f"Starting streaming invocation with model: {self.get_current_model()}")
            
            # Run the streaming invocation in background
            import asyncio
            response_task = asyncio.create_task(streaming_client.ainvoke(messages))
            
            # Stream chunks as they become available
            while not response_task.done() or stream_handler.has_chunks():
                if stream_handler.has_chunks():
                    chunks = stream_handler.get_chunks()
                    for chunk in chunks:
                        yield {
                            "success": True,
                            "chunk": chunk,
                            "model": self.get_current_model(),
                            "stream_id": id(stream_handler)
                        }
                
                # Small delay to prevent busy waiting
                await asyncio.sleep(0.01)
            
            # Wait for final response and get any remaining chunks
            try:
                final_response = await response_task
                
                # Process any remaining chunks
                if stream_handler.has_chunks():
                    chunks = stream_handler.get_chunks()
                    for chunk in chunks:
                        yield {
                            "success": True,
                            "chunk": chunk,
                            "model": self.get_current_model(),
                            "stream_id": id(stream_handler)
                        }
                
                # Send final completion signal
                yield {
                    "success": True,
                    "chunk": {
                        "type": "stream_complete",
                        "data": "",
                        "metadata": {
                            "final_response": final_response.content,
                            "completed": True
                        }
                    },
                    "model": self.get_current_model(),
                    "stream_id": id(stream_handler)
                }
                
            except Exception as e:
                logger.error(f"Error in streaming response: {e}")
                yield {
                    "success": False,
                    "chunk": {
                        "type": "stream_error",
                        "data": str(e),
                        "metadata": {"error": True}
                    },
                    "error": str(e),
                    "model": self.get_current_model()
                }
                
        except Exception as e:
            logger.error(f"Error starting streaming invocation: {e}")
            yield {
                "success": False,
                "chunk": {
                    "type": "stream_error",
                    "data": str(e),
                    "metadata": {"error": True}
                },
                "error": str(e),
                "model": self.get_current_model()
            }

    def format_messages(self, system_prompt: str, user_message: str) -> List[Tuple[str, str]]:
        """
        Helper to format messages in the required tuple format
        
        REFERENCE: secret-ai-getting-started-example.py lines 14-20
        Message format - MUST BE TUPLES, NOT DICTS
        """
        return [
            ("system", system_prompt),
            ("human", user_message),
        ]