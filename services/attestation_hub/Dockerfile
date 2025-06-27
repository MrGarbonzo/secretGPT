# Attestation Hub Service Dockerfile
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
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Set environment variables for production
ENV PYTHONPATH=/app
ENV ENVIRONMENT=production
ENV ATTESTATION_HUB_HOST=0.0.0.0
ENV ATTESTATION_HUB_PORT=8080
ENV LOG_LEVEL=INFO

# Create logs directory
RUN mkdir -p logs

# Expose port
EXPOSE 8080

# Create a non-root user for security
RUN useradd -m -u 1001 attestationhub
RUN chown -R attestationhub:attestationhub /app
USER attestationhub

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1

# Run the attestation hub service
CMD ["python", "main.py"]