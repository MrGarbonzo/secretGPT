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
        default="",
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
    
    secret_mcp_url: str = Field(
        default="http://localhost:8002",
        env="SECRET_MCP_URL",
        description="URL for external Secret Network MCP server"
    )
    
    # Removed: mcp_server_path - no longer needed with HTTP MCP integration
    
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
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore"
    }


# Global settings instance
settings = Settings()


def validate_settings() -> bool:
    """
    Validate that required settings are present

    Returns:
        bool: True if all required settings are valid
    """
    import logging
    logger = logging.getLogger(__name__)

    logger.info("Validating configuration settings...")
    logger.info(f"SECRET_AI_API_KEY: {'set' if settings.secret_ai_api_key else 'not set'}")
    logger.info(f"SECRETGPT_ENABLE_WEB_UI: {settings.enable_web_ui}")
    logger.info(f"SECRETGPT_HUB_HOST: {settings.hub_host}")
    logger.info(f"SECRETGPT_HUB_PORT: {settings.hub_port}")
    logger.info(f"ENVIRONMENT: {settings.environment}")
    logger.info(f"LOG_LEVEL: {settings.log_level}")

    # Phase 1: Only Secret AI API key is required
    if not settings.secret_ai_api_key or settings.secret_ai_api_key == "PLEASE_SET_IN_USR_DOT_ENV":
        logger.warning("SECRET_AI_API_KEY not set! Please create usr/.env file with your API key.")
        logger.warning("Copy .env.example to usr/.env and update with your values.")
        # Allow hub to start without API key for now
        return True


    # Phase 1: MCP is optional - hub can run without it
    # No validation needed for SECRET_MCP_URL - hub continues if MCP server unavailable

    logger.info("Configuration validation complete")
    return True