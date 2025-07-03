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
        self.current_line_length = 0
        self.in_thinking_mode = False
        self.brain_emoji = "🧠"
        self.chunk_queue = []
        self.sentences_in_paragraph = 0
        self.max_sentences_per_paragraph = 4  # Adjust for paragraph length
        self.last_char = ""
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
        """Process words and handle line wrapping and paragraph formatting"""
        for word in words:
            # Check if this is a list item marker - be more restrictive
            stripped_word = word.rstrip()
            is_list_marker = (
                # Only consider it a list marker if it's a single digit followed by . or )
                (len(stripped_word) == 2 and stripped_word[0].isdigit() and stripped_word[1] in '.)')
                or word in ['•', '-', '*', '▪', '▸', '◦']  # Bullet points
            )
            
            # Check if we need to start a new paragraph
            # Only break paragraphs after a real sentence (not list items) and if we have enough sentences
            if (self.last_char in '.!?' and 
                self.sentences_in_paragraph >= self.max_sentences_per_paragraph and
                not is_list_marker and
                self.current_line_length > 10):  # Only if we have substantial content on the line
                # Add double newline for paragraph break
                self.chunk_queue.append({
                    "type": "text_chunk",
                    "data": "\n\n",
                    "content_type": content_type,
                    "metadata": {
                        "paragraph_break": True,
                        "in_thinking": content_type == "thinking"
                    }
                })
                self.current_line_length = 0
                self.sentences_in_paragraph = 0
            elif is_list_marker:
                # Always start list items on new lines if not already at start
                if self.current_line_length > 0:
                    self.chunk_queue.append({
                        "type": "text_chunk",
                        "data": "\n",
                        "content_type": content_type,
                        "metadata": {
                            "list_item": True,
                            "in_thinking": content_type == "thinking"
                        }
                    })
                    self.current_line_length = 0
            elif self.current_line_length + len(word) + (1 if self.current_line_length > 0 else 0) > self.width:
                # Line is full, emit newline
                self.chunk_queue.append({
                    "type": "text_chunk",
                    "data": "\n",
                    "content_type": content_type,
                    "metadata": {
                        "line_break": True,
                        "in_thinking": content_type == "thinking"
                    }
                })
                self.current_line_length = 0
            
            # Emit the word with appropriate spacing
            if self.current_line_length > 0:
                # Add space before word if not at start of line
                self.chunk_queue.append({
                    "type": "text_chunk",
                    "data": " " + word,
                    "content_type": content_type,
                    "metadata": {
                        "in_thinking": content_type == "thinking"
                    }
                })
                self.current_line_length += len(word) + 1
            else:
                # First word on line, no space needed
                self.chunk_queue.append({
                    "type": "text_chunk",
                    "data": word,
                    "content_type": content_type,
                    "metadata": {
                        "in_thinking": content_type == "thinking"
                    }
                })
                self.current_line_length = len(word)
            
            # Track sentence endings for paragraph formatting
            if word.rstrip():  # Check non-empty word
                self.last_char = word.rstrip()[-1]
                # Only count as sentence end if it's not a list marker and has proper sentence structure
                if (self.last_char in '.!?' and not is_list_marker and 
                    len(word.rstrip()) > 2):  # Avoid counting single letters with periods
                    self.sentences_in_paragraph += 1
    
    def on_llm_end(self, *args, **kwargs):
        """Called when LLM finishes generating"""
        # Process any remaining text in buffer
        if self.buffer.strip():
            content_type = "thinking" if self.in_thinking_mode else "normal"
            # Process the final word(s) in buffer
            final_words = self.buffer.split()
            if final_words:
                self._process_words_chunk(final_words, content_type)
        
        # No need to process current line anymore since we emit words immediately
        
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