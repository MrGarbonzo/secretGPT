#!/bin/bash
# SecretVM Deployment Script for secretGPT
# This script prepares and deploys secretGPT in a SecretVM environment

set -e

echo "=== SecretGPT SecretVM Deployment Script ==="
echo "Preparing deployment for arrestai.io..."

# Define the deployment directory used by SecretVM
DEPLOY_DIR="/mnt/secure/docker_wd/usr"
CURRENT_DIR="$(pwd)"

# Create deployment directory structure
echo "Creating deployment directory structure..."
sudo mkdir -p "$DEPLOY_DIR"

# Copy required files to SecretVM deployment directory
echo "Copying deployment files..."
sudo cp -f docker-compose.secretvm.yml "$DEPLOY_DIR/docker-compose.yml"

# Check if .env exists
if [ -f ".env" ]; then
    echo "Found .env file, copying to deployment directory..."
    sudo cp -f .env "$DEPLOY_DIR/.env"
else
    echo "WARNING: .env file not found!"
    echo "Please ensure you upload the .env file with SECRET_AI_API_KEY to:"
    echo "  $DEPLOY_DIR/.env"
    echo "The .env file should contain:"
    echo "  SECRET_AI_API_KEY=your_actual_api_key"
    
    # Check if the deployment directory already has an .env file
    if [ ! -f "$DEPLOY_DIR/.env" ]; then
        echo ""
        echo "ERROR: No .env file found in deployment directory either."
        echo "Deployment cannot proceed without the SECRET_AI_API_KEY."
        exit 1
    else
        echo ""
        echo "Using existing .env file in deployment directory."
    fi
fi

# Ensure proper permissions
sudo chmod 644 "$DEPLOY_DIR/docker-compose.yml"
sudo chmod 600 "$DEPLOY_DIR/.env"

# Change to deployment directory
cd "$DEPLOY_DIR"

# Pull the latest image
echo "Pulling latest Docker image..."
sudo docker pull ghcr.io/mrgarbonzo/secretgpt:latest

# Stop any existing containers
echo "Stopping any existing containers..."
sudo docker-compose down 2>/dev/null || true

# Start the service
echo "Starting secretGPT service..."
sudo docker-compose up -d

# Wait for service to be healthy
echo "Waiting for service to become healthy..."
for i in {1..30}; do
    if sudo docker-compose ps | grep -q "healthy"; then
        echo "✅ Service is healthy!"
        break
    fi
    echo -n "."
    sleep 2
done

# Show container status
echo ""
echo "Container status:"
sudo docker-compose ps

# Show logs
echo ""
echo "Recent logs:"
sudo docker-compose logs --tail=20

echo ""
echo "=== Deployment Complete ==="
echo "✅ secretGPT should now be accessible at: https://arrestai.io"
echo "🔒 Attestation endpoint: https://localhost:29343/cpu.html"
echo ""
echo "To check logs: sudo docker-compose logs -f"
echo "To stop: sudo docker-compose down"

cd "$CURRENT_DIR"