"""
Custom Streaming Handler for SecretGPT Web Responses
Adapts the existing SecretStreamingHandler to work with web responses instead of console output
"""
import json
import logging
from typing import AsyncGenerator, Dict, Any
from langchain.callbacks.base import BaseCallbackHandler

logger = logging.getLogger(__name__)


class WebStreamingHandler(BaseCallbackHandler):
    """
    Custom callback handler for streaming Secret AI responses to web interface.
    
    Converts the console-based SecretStreamingHandler pattern to web-compatible
    JSON chunks that can be sent via Server-Sent Events.
    
    Features:
    - Yields JSON chunks instead of printing to console
    - Handles <think> tags and special formatting
    - Implements proper buffering for partial tokens
    - Adds stream metadata (progress, completion status)
    """
    
    def __init__(self, width: int = 60):
        """Initialize the web streaming handler"""
        self.width = width
        self.buffer = ""
        self.current_line = ""
        self.current_line_length = 0
        self.in_thinking_mode = False
        self.brain_emoji = "🧠"
        self.chunk_queue = []
        self.stream_metadata = {
            "total_tokens": 0,
            "thinking_sections": 0,
            "started": False,
            "completed": False
        }
    
    def on_llm_start(self, *args, **kwargs):
        """Called when LLM starts generating"""
        self.stream_metadata["started"] = True
        self.chunk_queue.append({
            "type": "stream_start",
            "data": "",
            "metadata": self.stream_metadata.copy()
        })
    
    def on_llm_new_token(self, token: str, **kwargs):
        """Process new token and generate web-compatible chunks"""
        self.stream_metadata["total_tokens"] += 1
        self.buffer += token
        
        # Check for opening thinking tag
        if "<think>" in self.buffer and not self.in_thinking_mode:
            parts = self.buffer.split("<think>", 1)
            before_tag = parts[0]
            after_tag = parts[1]
            
            # Process text before the tag
            if before_tag.strip():
                self._process_text_chunk(before_tag, "normal")
            
            # Start thinking mode
            self.stream_metadata["thinking_sections"] += 1
            self.chunk_queue.append({
                "type": "think_start",
                "data": self.brain_emoji,
                "metadata": {"thinking_section": self.stream_metadata["thinking_sections"]}
            })
            
            self.current_line = ""
            self.current_line_length = 0
            self.buffer = after_tag
            self.in_thinking_mode = True
        
        # Check for closing thinking tag
        elif "</think>" in self.buffer and self.in_thinking_mode:
            parts = self.buffer.split("</think>", 1)
            thinking_content = parts[0]
            after_tag = parts[1]
            
            # Process thinking content
            if thinking_content.strip():
                self._process_text_chunk(thinking_content, "thinking")
            
            # End thinking mode
            self.chunk_queue.append({
                "type": "think_end",
                "data": self.brain_emoji,
                "metadata": {"thinking_section": self.stream_metadata["thinking_sections"]}
            })
            
            self.current_line = ""
            self.current_line_length = 0
            self.buffer = after_tag
            self.in_thinking_mode = False
        
        # Process normal content without tags
        else:
            words = self.buffer.split()
            
            if not words:
                return
            
            # Process complete words, keeping any partial word in the buffer
            if self.buffer.endswith(" "):
                complete_words = words
                self.buffer = ""
            else:
                complete_words = words[:-1]
                self.buffer = words[-1] if words else ""
            
            # Process complete words
            if complete_words:
                content_type = "thinking" if self.in_thinking_mode else "normal"
                self._process_words_chunk(complete_words, content_type)
    
    def _process_text_chunk(self, text: str, content_type: str):
        """Process a text chunk and add to queue"""
        if text.strip():
            self.chunk_queue.append({
                "type": "text_chunk",
                "data": text,
                "content_type": content_type,
                "metadata": {
                    "token_count": len(text.split()),
                    "in_thinking": content_type == "thinking"
                }
            })
    
    def _process_words_chunk(self, words: list, content_type: str):
        """Process words and handle line wrapping"""
        for word in words:
            if self.current_line_length + len(word) + (1 if self.current_line else 0) > self.width:
                # Line is full, emit current line and start new one
                if self.current_line:
                    self.chunk_queue.append({
                        "type": "text_chunk",
                        "data": self.current_line + "\n",
                        "content_type": content_type,
                        "metadata": {
                            "line_break": True,
                            "in_thinking": content_type == "thinking"
                        }
                    })
                
                self.current_line = word
                self.current_line_length = len(word)
            else:
                # Add word to current line
                if self.current_line:
                    self.current_line += " " + word
                    self.current_line_length += len(word) + 1
                else:
                    self.current_line = word
                    self.current_line_length = len(word)
                
                # Emit word immediately for streaming effect
                self.chunk_queue.append({
                    "type": "text_chunk",
                    "data": word + " ",
                    "content_type": content_type,
                    "metadata": {
                        "word": True,
                        "in_thinking": content_type == "thinking"
                    }
                })
    
    def on_llm_end(self, *args, **kwargs):
        """Called when LLM finishes generating"""
        # Process any remaining text in buffer
        if self.buffer.strip():
            content_type = "thinking" if self.in_thinking_mode else "normal"
            self._process_text_chunk(self.buffer, content_type)
        
        # Process any remaining current line
        if self.current_line.strip():
            content_type = "thinking" if self.in_thinking_mode else "normal"
            self.chunk_queue.append({
                "type": "text_chunk",
                "data": self.current_line,
                "content_type": content_type,
                "metadata": {
                    "final_line": True,
                    "in_thinking": content_type == "thinking"
                }
            })
        
        # Mark stream as completed
        self.stream_metadata["completed"] = True
        self.chunk_queue.append({
            "type": "stream_end",
            "data": "",
            "metadata": self.stream_metadata.copy()
        })
    
    def on_llm_error(self, error, **kwargs):
        """Called when LLM encounters an error"""
        logger.error(f"Streaming error: {error}")
        self.chunk_queue.append({
            "type": "stream_error",
            "data": str(error),
            "metadata": {
                "error": True,
                "error_type": type(error).__name__
            }
        })
    
    def get_chunks(self) -> list:
        """Get all queued chunks and clear the queue"""
        chunks = self.chunk_queue.copy()
        self.chunk_queue.clear()
        return chunks
    
    def has_chunks(self) -> bool:
        """Check if there are chunks waiting"""
        return len(self.chunk_queue) > 0


class StreamingChunkFormatter:
    """
    Formats streaming chunks for different output formats (SSE, WebSocket, etc.)
    """
    
    @staticmethod
    def to_sse_event(chunk: Dict[str, Any]) -> str:
        """Format chunk as Server-Sent Event"""
        event_data = {
            "type": chunk["type"],
            "data": chunk["data"],
            "metadata": chunk.get("metadata", {})
        }
        
        if chunk.get("content_type"):
            event_data["content_type"] = chunk["content_type"]
        
        return f"data: {json.dumps(event_data)}\n\n"
    
    @staticmethod
    def to_json(chunk: Dict[str, Any]) -> Dict[str, Any]:
        """Format chunk as JSON object"""
        return {
            "type": chunk["type"],
            "data": chunk["data"],
            "content_type": chunk.get("content_type", "normal"),
            "metadata": chunk.get("metadata", {}),
            "timestamp": chunk.get("timestamp")
        }