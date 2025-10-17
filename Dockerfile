# Multi-Service Dockerfile
# Builds either secretGPT Hub or Attestation Hub based on context

FROM python:3.12-slim

# Build arguments for attestation
ARG BUILD_TAG
ARG BUILD_DATE
ARG GIT_COMMIT
ARG VERSION

# Labels for image metadata and attestation
LABEL org.opencontainers.image.title="secretGPT"
LABEL org.opencontainers.image.description="SecretGPT Hub - Confidential AI with Secret Network"
LABEL org.opencontainers.image.version="${VERSION}"
LABEL org.opencontainers.image.created="${BUILD_DATE}"
LABEL org.opencontainers.image.revision="${GIT_COMMIT}"
LABEL org.opencontainers.image.source="https://github.com/mrgarbonzo/secretGPT"
LABEL build.tag="${BUILD_TAG}"

# Set working directory
WORKDIR /app

# Install system dependencies with retry logic for network issues
RUN apt-get update || true && \
    apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    make \
    libffi-dev \
    libssl-dev \
    curl \
    || echo "Warning: Some packages may not have installed" && \
    rm -rf /var/lib/apt/lists/* || true

# Copy entire project
COPY . .

# Determine which service to build and install dependencies
# Always build secretGPT Hub Service (main application)
RUN echo "Building secretGPT Hub Service"; \
    pip install --no-cache-dir -r requirements.txt; \
    echo "secretgpt" > /app/service_type;

# Phase 1: MCP server moved to standalone repository
# No MCP server build steps needed - using HTTP client instead

# Set environment variables for production
ENV PYTHONPATH=/app
ENV ENVIRONMENT=production
ENV LOG_LEVEL=DEBUG

# Enable dual-domain mode for AttestAI and SecretGPTee
ENV SECRETGPT_DUAL_DOMAIN=true
# Enable Web UI by default
ENV SECRETGPT_ENABLE_WEB_UI=true

# MCP Configuration - disabled by default
ENV MCP_ENABLED=false
ENV SECRET_MCP_URL=http://host.docker.internal:8002

# SNIP Token Service Configuration
ENV SNIP_TOKEN_SERVICE_ENABLED=true
ENV SECRET_LCD_ENDPOINT=https://lcd.secret.adrius.starshell.net/
ENV SNIP_TOKEN_CACHE_TTL=300
ENV VIEWING_KEY_STORAGE_BACKEND=memory

# SecretVM Attestation Configuration
ENV SECRETGPT_ATTESTATION_ENDPOINT=https://host.docker.internal:29343/cpu.html

# Host configuration for external access
ENV SECRETGPT_HUB_HOST=0.0.0.0
ENV SECRETGPT_HUB_PORT=8000

# SECRET_AI_API_KEY must be provided at runtime via docker-compose or -e flag
# Do not hardcode the API key in the Dockerfile for security

# Secret AI Node Configuration - TESTNET (SDK 0.1.3)
# Using testnet configuration for compatibility with SDK 0.1.3
ENV SECRET_AI_NODE_URL=https://pulsar.lcd.secretnodes.com
ENV SECRET_AI_CHAIN_ID=pulsar-3
ENV SECRET_WORKER_SMART_CONTRACT=secret18cy3cgnmkft3ayma4nr37wgtj4faxfnrnngrlq

# Create a non-root user for security
RUN useradd -m -u 1001 appuser
RUN chown -R appuser:appuser /app
USER appuser

# Create startup script with error capture
RUN echo '#!/bin/bash\n\
SERVICE_TYPE=$(cat /app/service_type)\n\
if [ "$SERVICE_TYPE" = "attestation_hub" ]; then\n\
  echo "Starting Attestation Hub Service on port 8080"\n\
  export ATTESTATION_HUB_HOST=0.0.0.0\n\
  export ATTESTATION_HUB_PORT=8080\n\
  export LOG_LEVEL=INFO\n\
  cd /app/services/attestation_hub\n\
  exec python main.py\n\
else\n\
  echo "Starting secretGPT Hub Service on port 8000"\n\
  echo "SNIP Token Service: $SNIP_TOKEN_SERVICE_ENABLED"\n\
  echo "Web UI Enabled: $SECRETGPT_ENABLE_WEB_UI"\n\
  echo "LOG_LEVEL: $LOG_LEVEL"\n\
  echo "SECRET_AI_API_KEY: ${SECRET_AI_API_KEY:+set}"\n\
  echo "Python version:"\n\
  python --version\n\
  echo "Starting Python application..."\n\
  cd /app\n\
  python main.py --webui 2>&1 || { echo "Python exited with code $?"; sleep 10; }\n\
fi' > /app/start.sh && chmod +x /app/start.sh

# Expose both possible ports
EXPOSE 8000 8080

# Health check that works for both services
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD SERVICE_TYPE=$(cat /app/service_type) && \
      if [ "$SERVICE_TYPE" = "attestation_hub" ]; then \
        curl -f http://localhost:8080/health || exit 1; \
      else \
        curl -f http://localhost:8000/health || exit 1; \
      fi

# Run the appropriate service
CMD ["/app/start.sh"]