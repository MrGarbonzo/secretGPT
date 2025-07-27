# Multi-Service Dockerfile
# Builds either secretGPT Hub or Attestation Hub based on context

FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies including Node.js for MCP server
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    libffi-dev \
    libssl-dev \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Copy entire project
COPY . .

# Determine which service to build and install dependencies
# Always build secretGPT Hub Service (main application)
RUN echo "Building secretGPT Hub Service"; \
    pip install --no-cache-dir -r requirements.txt; \
    echo "secretgpt" > /app/service_type;

# Pre-build MCP server (compile TypeScript to JavaScript)
RUN echo "Pre-building MCP servers..."; \
    cd /app/mcp_servers/secret_network && \
    echo "Node.js version: $(node --version)" && \
    echo "NPM version: $(npm --version)" && \
    echo "TypeScript version check..." && \
    npx tsc --version || echo "TypeScript not found, will install" && \
    echo "Installing Node.js dependencies..." && \
    npm ci --only=production && npm install typescript --save-dev && \
    echo "Dependencies installed successfully" && \
    echo "Directory contents before build:" && \
    ls -la && \
    echo "Source directory:" && \
    ls -la src/ && \
    echo "Checking TypeScript source files..." && \
    find src/ -name "*.ts" -exec echo "Found: {}" \; && \
    echo "Ensuring build directory exists..." && \
    mkdir -p build && \
    echo "Building TypeScript MCP server..." && \
    (npx tsc --build --verbose || (echo "Build with --build failed, trying direct compilation..." && npx tsc)) && \
    echo "TypeScript compilation complete" && \
    echo "Verifying MCP server build..." && \
    ls -la build/ && \
    test -f build/index.js || (echo "ERROR: build/index.js not found after compilation!" && \
                               echo "Build directory contents:" && ls -la build/ && \
                               echo "Checking for TypeScript errors..." && \
                               npx tsc --noEmit --listFiles && \
                               exit 1) && \
    chmod 755 build/index.js && \
    echo "Testing Node.js can execute the MCP server..." && \
    timeout 10s node build/index.js --help || echo "MCP server startup test complete (timeout expected)" && \
    echo "Final verification: MCP server file exists and is executable" && \
    head -10 build/index.js && \
    echo "MCP server build verification complete";

# Set environment variables for production
ENV PYTHONPATH=/app
ENV ENVIRONMENT=production
ENV MCP_SERVER_PATH=/app/mcp_servers/secret_network/build/index.js

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