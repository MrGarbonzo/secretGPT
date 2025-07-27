# 🔐 secretGPT - Unified Trusted AI Hub

A centralized hub system that provides secure, attestable AI services through multiple interfaces with comprehensive attestation capabilities. Built on the Secret Network for privacy-preserving AI interactions.

## ✨ Overview

secretGPT is a modular AI hub that routes requests between different interfaces (Web UI, API, future integrations) and AI services while providing cryptographic attestation of the execution environment. The system ensures that AI interactions occur within trusted execution environments (TEEs) with verifiable attestation.

### 🎯 Key Features

- **🔄 Hub-Centric Architecture**: Central message routing between interfaces and services
- **🤖 Secret AI Integration**: Seamless integration with Secret Network's confidential AI services  
- **🌐 Web Interface**: FastAPI-based web UI with real-time chat and attestation
- **🛡️ Comprehensive Attestation**: Multi-VM attestation management and verification
- **📡 Streaming Support**: Real-time AI response streaming with custom handlers
- **⚙️ Modular Design**: Component-based architecture for easy extension
- **🔧 Configuration-Driven**: Environment variables and YAML configs for flexibility

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    secretGPT Hub System                    │
│                                                             │
│  ┌─────────────┐    ┌───────────────┐    ┌──────────────┐  │
│  │   Web UI    │    │  Future MCP   │    │  API Client  │  │
│  │ Interface   │    │  Integration  │    │  Interface   │  │
│  └──────┬──────┘    └───────┬───────┘    └──────┬───────┘  │
│         │                   │                   │          │
│         └───────────────────┼───────────────────┘          │
│                             │                              │
│         ┌───────────────────▼───────────────────┐          │
│         │          Hub Router                   │          │
│         │    • Message routing                  │          │
│         │    • Component management             │          │
│         │    • Streaming coordination           │          │
│         └───────────────┬───────────────────────┘          │
│                         │                                  │
│         ┌───────────────▼───────────────────┐              │
│         │        Secret AI Service         │              │
│         │   • Model discovery              │              │
│         │   • Async/sync invocation        │              │
│         │   • Streaming responses          │              │
│         └───────────────┬───────────────────┘              │
│                         │                                  │
└─────────────────────────┼──────────────────────────────────┘
                          │
          ┌───────────────▼───────────────────┐
          │      Attestation Hub Service      │
          │   • Multi-VM attestation          │
          │   • REST API endpoints            │
          │   • Fallback strategies           │
          │   • Configuration management      │
          └───────────────────────────────────┘
                          │
              ┌───────────┼───────────┐
              │           │           │
      ┌───────▼──┐ ┌──────▼──┐ ┌─────▼─────┐
      │secretAI  │ │secretGPT│ │ Future VM │
      │   VM     │ │   VM    │ │     X     │
      └──────────┘ └─────────┘ └───────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Secret AI API key
- Virtual environment (recommended)

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd secretGPT

# Create and activate virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

1. **Create environment file**:
```bash
cp .env.example .env
```

2. **Configure required settings**:
```bash
# Required: Secret AI API key
SECRET_AI_API_KEY=your_secret_ai_api_key_here

# Optional: Custom Secret Network node
SECRET_NODE_URL=https://your-secret-node.com

# Hub configuration
SECRETGPT_HUB_HOST=0.0.0.0
SECRETGPT_HUB_PORT=8000

# Enable Web UI
SECRETGPT_ENABLE_WEB_UI=true

# Logging
LOG_LEVEL=INFO
ENVIRONMENT=development
```

### Running the Service

#### **Service Mode (Hub Only)**
```bash
python main.py
```

#### **Web UI Mode (Hub + Web Interface)**
```bash
# Set environment variable
export SECRETGPT_ENABLE_WEB_UI=true

# Or in .env file
echo "SECRETGPT_ENABLE_WEB_UI=true" >> .env

# Run with Web UI
python main.py
```

#### **Test Mode**
```bash
# Test Secret AI integration
SECRETGPT_RUN_MODE=test python main.py

# Test Web UI integration
SECRETGPT_RUN_MODE=test SECRETGPT_ENABLE_WEB_UI=true python main.py
```

### Access the Application

- **Web UI**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 📁 Project Structure

```
secretGPT/
├── main.py                     # Main entry point with multiple run modes
├── requirements.txt            # Python dependencies
├── .env.example               # Environment configuration template
├── docker-compose.yml         # Docker deployment configuration
├── Dockerfile                 # Container build instructions
│
├── config/                    # Configuration management
│   ├── settings.py           # Pydantic settings with validation
│   └── __init__.py
│
├── hub/                      # Core hub router system
│   └── core/
│       ├── router.py         # Central message routing and component management
│       └── __init__.py
│
├── services/                 # Service implementations
│   ├── secret_ai/           # Secret AI service integration
│   │   ├── client.py        # Secret AI SDK client with streaming
│   │   ├── streaming_handler.py  # Custom web streaming handler
│   │   └── __init__.py
│   │
│   └── attestation_hub/     # Centralized attestation service
│       ├── main.py          # Standalone attestation service
│       ├── hub/             # Core attestation logic
│       ├── parsers/         # Attestation parsing strategies
│       ├── api/             # REST API endpoints
│       ├── clients/         # Client library for integration
│       └── config/          # VM configurations and settings
│
├── interfaces/              # User interface implementations
│   └── web_ui/             # FastAPI web interface
│       ├── app.py          # FastAPI application setup
│       ├── service.py      # Web UI service integration
│       ├── attestation/    # Attestation service components
│       ├── encryption/     # Proof manager for attestation
│       ├── templates/      # Jinja2 HTML templates
│       └── static/         # CSS, JavaScript, and assets
│
├── utils/                   # Shared utilities
├── resources/              # Documentation and scripts
│   ├── secretAI/          # Secret AI SDK documentation
│   ├── scripts/           # Setup and installation scripts
│   └── attest_data/       # Attestation reference data
│
└── preview/               # Static preview files
    ├── chat-preview.html  # Chat interface preview
    └── attestation-preview.html  # Attestation interface preview
```

## 🔧 Components

### **Hub Router** (`hub/core/router.py`)
- Central message routing between interfaces and services
- Component registry for modular service management
- Async message handling with streaming support
- System status monitoring and health checks

### **Secret AI Service** (`services/secret_ai/`)
- Integration with Secret Network's confidential AI services
- Model discovery and endpoint management
- Sync/async invocation with streaming responses
- Message formatting following Secret AI SDK patterns

### **Web UI Interface** (`interfaces/web_ui/`)
- FastAPI-based web application
- Real-time chat interface with streaming
- Integrated attestation verification
- Templated HTML with responsive design

### **Attestation Hub** (`services/attestation_hub/`)
- Standalone microservice for multi-VM attestation
- REST API with comprehensive endpoints
- Multiple parsing strategies with fallbacks
- Configuration-driven VM management

## 🔒 Security Features

### **Trusted Execution Environment**
- Runs within Intel TDX (Trust Domain Extensions)
- Cryptographic attestation of execution environment
- Verifiable proof of code integrity and configuration

### **Attestation Verification**
- Self-attestation capability for current VM
- Multi-VM attestation support via centralized hub
- MRTD, RTMR, and report data validation
- Fallback parsing strategies for reliability

### **Confidential AI**
- Integration with Secret Network for privacy-preserving AI
- Encrypted communication channels
- No data persistence in plaintext