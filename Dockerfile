# Multi-Service Dockerfile
# Builds either secretGPT Hub or Attestation Hub based on context

FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    libffi-dev \
    libssl-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy entire project
COPY . .

# Determine which service to build and install dependencies
RUN if [ -f "services/attestation_hub/requirements.txt" ] && [ -f "services/attestation_hub/main.py" ]; then \
      echo "Building Attestation Hub Service"; \
      cd services/attestation_hub && pip install --no-cache-dir -r requirements.txt; \
      echo "attestation_hub" > /app/service_type; \
    else \
      echo "Building secretGPT Hub Service"; \
      pip install --no-cache-dir -r requirements.txt; \
      echo "secretgpt" > /app/service_type; \
    fi

# Set environment variables for production
ENV PYTHONPATH=/app
ENV ENVIRONMENT=production

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
  cd /app\n\
  exec python main.py\n\
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