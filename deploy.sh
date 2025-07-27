#!/bin/bash
# Deployment script for secretGPT with automatic host IP discovery

echo "=== secretGPT Auto-Deploy Script ==="
echo "Discovering host external IP for attestation endpoint..."

# Get the host's external IP
EXTERNAL_IP=""

# Try multiple external IP services
for service in "https://ipv4.icanhazip.com" "https://api.ipify.org" "https://checkip.amazonaws.com/"; do
    echo "Trying $service..."
    EXTERNAL_IP=$(curl -s --connect-timeout 5 --max-time 10 "$service" 2>/dev/null | tr -d '\n\r ')
    
    # Validate IP format and ensure it's not private
    if [[ $EXTERNAL_IP =~ ^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$ ]] && \
       [[ ! $EXTERNAL_IP =~ ^(127\.|172\.|10\.|192\.168\.) ]]; then
        echo "✓ External IP discovered: $EXTERNAL_IP"
        break
    fi
    EXTERNAL_IP=""
done

if [ -z "$EXTERNAL_IP" ]; then
    echo "❌ Could not discover external IP automatically"
    echo "Please set SECRETGPT_ATTESTATION_ENDPOINT manually or check internet connectivity"
    exit 1
fi

# Set the attestation endpoint
ATTESTATION_ENDPOINT="https://${EXTERNAL_IP}:29343/cpu.html"
echo "✓ Attestation endpoint: $ATTESTATION_ENDPOINT"

# Export for docker-compose
export SECRETGPT_ATTESTATION_ENDPOINT="$ATTESTATION_ENDPOINT"

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose not found. Please install docker-compose."
    exit 1
fi

# Start the services
echo ""
echo "Starting secretGPT with attestation endpoint: $ATTESTATION_ENDPOINT"
echo "Running: docker-compose up -d"

docker-compose up -d

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ secretGPT started successfully!"
    echo "📊 Web UI: http://localhost:8003"
    echo "🔒 Attestation: $ATTESTATION_ENDPOINT"
    echo ""
    echo "To check logs: docker-compose logs -f"
    echo "To stop: docker-compose down"
else
    echo "❌ Failed to start secretGPT"
    exit 1
fi