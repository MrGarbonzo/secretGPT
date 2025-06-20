# secretGPT Hub Dockerfile
# For SecretVM deployment following the build plan requirements

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

# Expose port
EXPOSE 8000

# Create a non-root user for security
RUN useradd -m -u 1001 secretgpt
RUN chown -R secretgpt:secretgpt /app
USER secretgpt

# Run the application
CMD ["python", "main.py"]