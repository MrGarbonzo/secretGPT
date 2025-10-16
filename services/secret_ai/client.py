"""
Secret AI Service Implementation
Using OpenAI-compatible endpoint (Ollama)
"""
import os
import logging
from typing import List, Tuple, Dict, Any, Optional, AsyncGenerator
from openai import OpenAI, AsyncOpenAI

logger = logging.getLogger(__name__)


class SecretAIService:
    """
    Service class for interacting with Secret AI via OpenAI-compatible endpoint
    """

    def __init__(self):
        """Initialize the Secret AI service with OpenAI client"""
        self.models = []
        self.base_url = None
        self.client = None
        self.async_client = None
        self._initialize()
    
    def _initialize(self):
        """Initialize the Secret AI client using OpenAI-compatible endpoint"""
        try:
            # Secret AI OpenAI-compatible endpoint (Ollama)
            # The /v1 suffix is for OpenAI compatibility
            self.base_url = "https://secretai-rytn.scrtlabs.com:21434/v1"

            # Available models from Secret AI
            # Using full model names with tags as they appear in the API
            self.models = [
                "gemma3:4b",  # Default model (per user request)
                "deepseek-r1:70b",
                "llama3.2-vision:latest",
                "llama3.3:70b"
            ]

            # Get API key from environment
            api_key = os.getenv("SECRET_AI_API_KEY")
            if not api_key:
                raise RuntimeError("SECRET_AI_API_KEY environment variable not set")

            # Initialize OpenAI clients with custom headers for Secret AI
            # Secret AI/Ollama endpoints may expect API key in X-API-Key header
            default_headers = {
                "X-API-Key": api_key
            }

            self.client = OpenAI(
                base_url=self.base_url,
                api_key=api_key,  # Still pass for compatibility
                default_headers=default_headers
            )

            self.async_client = AsyncOpenAI(
                base_url=self.base_url,
                api_key=api_key,  # Still pass for compatibility
                default_headers=default_headers
            )

            logger.info(f"✓ Initialized Secret AI with OpenAI-compatible client")
            logger.info(f"  Endpoint: {self.base_url}")
            logger.info(f"  Available models: {', '.join(self.models)}")
            logger.info(f"  Default model: {self.models[0]}")

        except Exception as e:
            logger.error(f"Failed to initialize Secret AI: {e}")
            logger.warning("Secret AI service will start in degraded mode. Try again later or check configuration.")
    
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
            stream: Whether to stream the response

        Returns:
            Dict containing the response
        """
        if not self.client:
            raise RuntimeError("Secret AI client not initialized")

        try:
            # Convert tuple format to OpenAI dict format
            openai_messages = self._convert_messages(messages)

            # Use OpenAI client
            response = self.client.chat.completions.create(
                model=self.get_current_model(),
                messages=openai_messages,
                stream=stream
            )

            return {
                "success": True,
                "content": response.choices[0].message.content,
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
        if not self.async_client:
            raise RuntimeError("Secret AI async client not initialized")

        try:
            # Convert tuple format to OpenAI dict format
            openai_messages = self._convert_messages(messages)

            # Use async OpenAI client
            response = await self.async_client.chat.completions.create(
                model=self.get_current_model(),
                messages=openai_messages
            )

            return {
                "success": True,
                "content": response.choices[0].message.content,
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
        Stream responses from Secret AI

        Args:
            messages: List of tuples in format [("role", "content")]

        Yields:
            Dict containing streaming chunks
        """
        if not self.async_client:
            raise RuntimeError("Secret AI async client not initialized")

        try:
            # Convert tuple format to OpenAI dict format
            openai_messages = self._convert_messages(messages)

            logger.debug(f"Starting streaming invocation with model: {self.get_current_model()}")

            # Use async OpenAI client with streaming
            stream = await self.async_client.chat.completions.create(
                model=self.get_current_model(),
                messages=openai_messages,
                stream=True
            )

            chunk_count = 0
            # Stream chunks as they arrive
            async for chunk in stream:
                chunk_count += 1
                # Check if chunk has choices and delta content
                if chunk.choices and len(chunk.choices) > 0:
                    delta = chunk.choices[0].delta
                    if hasattr(delta, 'content') and delta.content:
                        content = delta.content
                        yield {
                            "success": True,
                            "chunk": {
                                "type": "content",
                                "data": content,
                                "metadata": {}
                            },
                            "model": self.get_current_model()
                        }

            logger.debug(f"Streaming complete. Total chunks received: {chunk_count}")

            # Send completion signal
            yield {
                "success": True,
                "chunk": {
                    "type": "stream_complete",
                    "data": "",
                    "metadata": {"completed": True}
                },
                "model": self.get_current_model()
            }

        except Exception as e:
            logger.error(f"Error in streaming invocation: {e}", exc_info=True)
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

    def _convert_messages(self, messages: List[Tuple[str, str]]) -> List[Dict[str, str]]:
        """
        Convert tuple message format to OpenAI dict format

        Args:
            messages: List of tuples in format [("role", "content")]

        Returns:
            List of dicts in OpenAI format [{"role": "user", "content": "..."}]
        """
        openai_messages = []
        for role, content in messages:
            # Map role names to OpenAI format
            openai_role = role
            if role == "human":
                openai_role = "user"
            elif role == "system":
                openai_role = "system"
            elif role == "assistant":
                openai_role = "assistant"

            openai_messages.append({
                "role": openai_role,
                "content": content
            })

        return openai_messages

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