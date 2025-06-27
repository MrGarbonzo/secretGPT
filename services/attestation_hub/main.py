"""Main entry point for Attestation Hub Service"""

import asyncio
import logging
import logging.config
import os
import yaml
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from config.settings import ConfigManager
from hub.service import AttestationHub
from api.routes import create_routes

# Setup logging
log_config_path = Path(__file__).parent / "config" / "logging.yaml"
if log_config_path.exists():
    with open(log_config_path, 'r') as f:
        logging_config = yaml.safe_load(f)
        # Create logs directory if needed
        os.makedirs("logs", exist_ok=True)
        logging.config.dictConfig(logging_config)
else:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

logger = logging.getLogger(__name__)

# Global hub instance
attestation_hub: AttestationHub = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    global attestation_hub
    
    # Startup
    logger.info("Starting Attestation Hub Service")
    
    # Initialize configuration
    config_manager = ConfigManager()
    
    # Initialize hub
    attestation_hub = AttestationHub(config_manager)
    
    # Create routes with hub instance
    api_router = create_routes(attestation_hub)
    app.include_router(api_router)
    
    logger.info(f"Attestation Hub started on {config_manager.service_config.host}:{config_manager.service_config.port}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Attestation Hub Service")
    if attestation_hub:
        await attestation_hub.cleanup()


# Create FastAPI app
app = FastAPI(
    title="Attestation Hub Service",
    description="Centralized attestation service for multiple VMs",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def main():
    """Run the service"""
    config_manager = ConfigManager()
    
    uvicorn.run(
        "main:app",
        host=config_manager.service_config.host,
        port=config_manager.service_config.port,
        workers=config_manager.service_config.workers,
        log_level=config_manager.service_config.log_level.lower(),
        access_log=True
    )


if __name__ == "__main__":
    main()