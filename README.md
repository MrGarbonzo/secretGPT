# secretGPT Hub - Phase 1: Core Foundation

## Overview

The secretGPT Hub is a comprehensive system that integrates Secret Network's Confidential AI capabilities with multiple user interfaces. This Phase 1 implementation provides the core foundation with Secret AI integration and hub router architecture.

## ✅ Phase 1 Complete - All Success Criteria Met

### Implemented Features

1. **Secret AI Service Integration** 
   - Model discovery using `get_models()` and `get_urls()`
   - Proper message formatting as tuples `[("role", "content")]`
   - Both sync and async invocation support
   - Response content extraction via `response.content`

2. **Hub Router Architecture**
   - Central message routing system
   - Component registry for managing services
   - Interface abstraction for future UI integrations
   - System status monitoring

3. **Environment Configuration**
   - Secure API key management
   - Configurable settings via environment variables
   - Production-ready configuration system

4. **Docker Containerization**
   - Multi-stage build optimized for SecretVM
   - Production-ready container with security best practices
   - Resource-limited deployment configuration

## Architecture

```
┌─────────────────────────────────────────┐
│              secretGPT Hub               │
│  ┌─────────────────────────────────────┐ │
│  │        Hub Router (Core)            │ │
│  │  - Message routing                  │ │
│  │  - Component registry              │ │
│  │  - System management               │ │
│  └─────────────────────────────────────┘ │
│                   │                     │
│  ┌─────────────────────────────────────┐ │
│  │        Secret AI Service            │ │
│  │  - Model discovery                  │ │
│  │  - Message formatting              │ │
│  │  - Chat invocation                 │ │
│  └─────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

## Quick Start

### 1. Environment Setup

```bash
# Clone and setup environment
cp .env.example .env

# Set your Secret AI API key (or use the provided one)
export SECRET_AI_API_KEY=bWFzdGVyQHNjcnRsYWJzLmNvbTpTZWNyZXROZXR3b3JrTWFzdGVyS2V5X18yMDI1
```

### 2. Local Development

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the hub
python main.py
```

### 3. Docker Deployment

```bash
# Build the image
docker build -t secretgpt-hub:phase1 .

# Run with docker-compose
docker-compose up -d
```

### 4. Validation

```bash
# Run the validation script
python validate_phase1.py
```

## Available Models

The system automatically discovers available Secret AI models:
- `deepseek-r1:70b` (Primary model)
- `llama3.2-vision`
- `gamma3:4b`

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_AI_API_KEY` | Secret AI authentication key | Required |
| `SECRETGPT_HUB_HOST` | Hub server host | `0.0.0.0` |
| `SECRETGPT_HUB_PORT` | Hub server port | `8000` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `ENVIRONMENT` | Environment mode | `development` |

## Project Structure

```
secretGPT/
├── secretGPT/                  # Main package
│   ├── hub/core/              # Hub router and core logic
│   ├── services/secret_ai/    # Secret AI service integration
│   ├── config/                # Configuration management
│   └── utils/                 # Shared utilities
├── main.py                    # Entry point
├── validate_phase1.py         # Validation script
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Container definition
├── docker-compose.yaml        # Docker deployment
└── README.md                  # This file
```

## API Usage

### Basic Message Routing

```python
from secretGPT.hub.core.router import HubRouter, ComponentType
from secretGPT.services.secret_ai.client import SecretAIService

# Initialize components
hub = HubRouter()
secret_ai = SecretAIService()
hub.register_component(ComponentType.SECRET_AI, secret_ai)

# Route a message
response = await hub.route_message(
    interface="your_interface",
    message="Your question here",
    options={"temperature": 0.7}
)

print(response["content"])
```

### Direct Secret AI Service

```python
from secretGPT.services.secret_ai.client import SecretAIService

# Initialize service
service = SecretAIService()

# Format messages (required tuple format)
messages = service.format_messages(
    "You are a helpful assistant",
    "What is the capital of France?"
)

# Get response
response = service.invoke(messages)
print(response["content"])
```

## Development

### Adding New Interfaces

1. Create interface directory under `secretGPT/interfaces/`
2. Implement interface class following the component pattern
3. Register with hub router using `ComponentType`
4. Update configuration as needed

### Testing

```bash
# Run validation
python validate_phase1.py

# Test Secret AI directly
python resources/secretAI/secret-ai-getting-started-example.py
```

## Next Steps: Phase 2

Phase 2 will add:
- Web UI interface with FastAPI
- Attestation service integration
- Dual VM attestation support
- Template and static asset serving

## Security Notes

- API keys are managed via environment variables
- Container runs as non-root user
- Resource limits applied for production deployment
- Confidential computing ready for SecretVM

## Support

For issues and development questions:
- Check validation script output for troubleshooting
- Review DETAILED_BUILD_PLAN.md for implementation details
- Ensure all environment variables are properly configured