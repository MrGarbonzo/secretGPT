# Multi-Service Dockerfile
# Builds either secretGPT Hub or Attestation Hub based on context

FROM python:3.12-slim

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
# SECRET_MCP_URL now comes from .env file for security

# Enable dual-domain mode for AttestAI and SecretGPTee
ENV SECRETGPT_DUAL_DOMAIN=true
# Enable Web UI by default
ENV SECRETGPT_ENABLE_WEB_UI=true

# SNIP Token Service Configuration
ENV SNIP_TOKEN_SERVICE_ENABLED=true
ENV SECRET_LCD_ENDPOINT=https://lcd.secret.adrius.starshell.net/
ENV SNIP_TOKEN_CACHE_TTL=300
ENV VIEWING_KEY_STORAGE_BACKEND=memory

# Host configuration for external access
ENV SECRETGPT_HUB_HOST=0.0.0.0
ENV SECRETGPT_HUB_PORT=8000

# Create a non-root user for security
RUN useradd -m -u 1001 appuser
RUN chown -R appuser:appuser /app
USER appuser

# Create startup script
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
  cd /app\n\
  exec python main.py --webui\n\
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