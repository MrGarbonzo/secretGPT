"""
Environment Configuration Management
Handles all environment variables and configuration for secretGPT
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    Following the documentation requirements for configuration
    """
    
    # Secret AI Configuration
    # REFERENCE: secretAI-setting-up-environment.txt
    secret_ai_api_key: str = Field(
        ...,
        env="SECRET_AI_API_KEY",
        description="API key for Secret AI authentication"
    )
    
    secret_node_url: Optional[str] = Field(
        default=None,
        env="SECRET_NODE_URL",
        description="Optional custom Secret Network node URL"
    )
    
    # Hub Configuration
    hub_host: str = Field(
        default="0.0.0.0",
        env="SECRETGPT_HUB_HOST",
        description="Host for the hub server"
    )
    
    hub_port: int = Field(
        default=8000,
        env="SECRETGPT_HUB_PORT",
        description="Port for the hub server"
    )
    
    # Web UI Configuration (Phase 2)
    enable_web_ui: bool = Field(
        default=False,
        env="SECRETGPT_ENABLE_WEB_UI",
        description="Enable web UI interface"
    )
    
    
    # MCP Configuration (Phase 4)
    mcp_enabled: bool = Field(
        default=False,
        env="MCP_ENABLED",
        description="Enable MCP service integration"
    )
    
    mcp_secret_network_url: Optional[str] = Field(
        default=None,
        env="MCP_SECRET_NETWORK_URL",
        description="URL for external Secret Network MCP server"
    )
    
    # Logging Configuration
    log_level: str = Field(
        default="INFO",
        env="LOG_LEVEL",
        description="Logging level (DEBUG, INFO, WARNING, ERROR)"
    )
    
    # Development/Production Mode
    environment: str = Field(
        default="development",
        env="ENVIRONMENT",
        description="Environment mode (development, production)"
    )
    
    class Config:
        """Pydantic configuration"""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()


def validate_settings() -> bool:
    """
    Validate that required settings are present
    
    Returns:
        bool: True if all required settings are valid
    """
    # Phase 1: Only Secret AI API key is required
    if not settings.secret_ai_api_key:
        print("ERROR: SECRET_AI_API_KEY is required but not set!")
        print("Please ensure the .env file contains: SECRET_AI_API_KEY=your_api_key_here")
        print("In SecretVM, the .env file should be at: /mnt/secure/docker_wd/usr/.env")
        return False
    
    
    # Phase 4: If MCP is enabled, URL is required
    if settings.mcp_enabled and not settings.mcp_secret_network_url:
        print("ERROR: MCP_SECRET_NETWORK_URL is required when MCP is enabled!")
        return False
    
    return True