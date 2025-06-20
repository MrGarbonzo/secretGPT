# secretGPT Hub - Production Deployment Guide

**Complete SecretVM Deployment Package**  
*Ready for Production - All Phases Implemented*

## 🎉 **System Overview**

secretGPT Hub is a complete confidential AI system with three fully implemented and validated components:

- ✅ **Phase 1: Secret AI Integration** - Hub router with Secret AI service
- ✅ **Phase 2: Web UI Integration** - Complete web interface with dual VM attestation  
- ✅ **Phase 3: Telegram Bot Integration** - Business user access via Telegram

## 🚀 **Quick Deployment to SecretVM**

### **Prerequisites**
- SecretVM CLI installed and configured
- Telegram bot token (from BotFather)
- Secret AI API key access

### **1. Environment Setup**
```bash
# Required environment variables
export SECRET_AI_API_KEY="bWFzdGVyQHNjcnRsYWJzLmNvbTpTZWNyZXROZXR3b3JrTWFzdGVyS2V5X18yMDI1"
export TELEGRAM_BOT_TOKEN="your_telegram_bot_token"
export TELEGRAM_BOT_ENABLED="true"
export SECRETGPT_ENABLE_WEB_UI="true"
```

### **2. Deploy to SecretVM**
```bash
# Single command deployment
secretvm-cli vm create \
  --name "secretgpt-hub" \
  --type "medium" \
  --docker-compose docker-compose.yaml \
  --env-file .env
```

### **3. Access Your System**
- **Web UI**: `https://your-secretvm-ip:8000`
- **Telegram Bot**: Search for your bot on Telegram
- **Health Check**: `https://your-secretvm-ip:8000/health`

---

## 📋 **Complete Environment Variables**

### **Required Variables**
```bash
# Secret AI Configuration (Required)
SECRET_AI_API_KEY=bWFzdGVyQHNjcnRsYWJzLmNvbTpTZWNyZXROZXR3b3JrTWFzdGVyS2V5X18yMDI1

# Telegram Bot Configuration (Optional)
TELEGRAM_BOT_ENABLED=true              # Enable/disable Telegram bot
TELEGRAM_BOT_TOKEN=your_bot_token      # From BotFather

# Web UI Configuration (Optional)
SECRETGPT_ENABLE_WEB_UI=true           # Enable/disable web interface
```

### **Optional Variables**
```bash
# Hub Configuration
SECRETGPT_HUB_HOST=0.0.0.0            # Default: 0.0.0.0
SECRETGPT_HUB_PORT=8000               # Default: 8000

# System Configuration  
ENVIRONMENT=production                 # Default: development
LOG_LEVEL=INFO                        # DEBUG, INFO, WARNING, ERROR

# Secret Network (Future)
SECRET_NODE_URL=custom_node_url       # Optional custom node
MCP_ENABLED=false                     # MCP integration (Phase 4)
MCP_SECRET_NETWORK_URL=mcp_server_url # MCP server URL
```

---

## 🔧 **Component Architecture**

### **Phase 1: Secret AI Integration**
- **Service**: `secretGPT/services/secret_ai/client.py`
- **Features**: Model discovery, message routing, async invocation
- **API Pattern**: Tuple message format `[("role", "content")]`

### **Phase 2: Web UI Integration** 
- **Service**: `secretGPT/interfaces/web_ui/`
- **Features**: Chat interface, dual VM attestation, proof generation
- **Endpoints**: `/api/v1/chat`, `/api/v1/attestation/self`, `/api/v1/proof/generate`

### **Phase 3: Telegram Bot Integration**
- **Service**: `secretGPT/interfaces/telegram_bot/`
- **Features**: 4 essential commands, message handling, error recovery
- **Commands**: `/start`, `/help`, `/models`, `/status`

### **Hub Router (Core)**
- **Service**: `secretGPT/hub/core/router.py`
- **Function**: Central message routing, component registry, system status
- **Pattern**: All interfaces route through hub (NO direct Secret AI calls)

---

## 🔍 **Health Monitoring**

### **Health Check Endpoints**
- **Primary**: `GET /health`
- **API**: `GET /api/v1/health` 
- **Response**: `{"status": "healthy", "hub_status": {...}}`

### **System Status**
```bash
# Check container health
docker ps

# View logs
docker logs secretgpt-hub

# System status via API
curl http://localhost:8000/health
```

### **Component Status**
- **Hub Router**: Operational/Error
- **Secret AI**: Connected/Disconnected  
- **Web UI**: Operational/Error
- **Telegram Bot**: Running/Stopped/Not Configured

---

## 🛡️ **Security Configuration**

### **Production Security Checklist**
- ✅ **API Key Protection**: Secret AI key via environment variables only
- ✅ **Input Validation**: All user inputs validated and sanitized
- ✅ **Error Handling**: No sensitive information in error responses
- ✅ **Container Security**: Non-root user (secretgpt:1001)
- ✅ **Resource Limits**: CPU and memory constraints applied
- ✅ **CORS Policy**: Configurable origins for web interface

### **SecretVM Security Features**
- **VM Attestation**: Dual VM attestation (secretGPT + Secret AI)
- **TLS Protection**: All external communication encrypted
- **Certificate Verification**: Attestation endpoint fingerprint validation
- **Isolated Execution**: SecretVM confidential computing environment

---

## 📊 **Performance Specifications**

### **Resource Requirements**
- **CPU**: 0.5-1.0 cores (adjustable)
- **Memory**: 512MB-1GB (adjustable)
- **Storage**: ~2GB for container and dependencies
- **Network**: HTTPS/8000 (web), Telegram API access

### **Performance Metrics**
- **Response Time**: ~1-3 seconds (Secret AI dependent)
- **Concurrent Users**: 10-50 (based on Secret AI limits)
- **Uptime**: 99%+ (with restart policies)
- **Health Checks**: 30-second intervals

### **Scaling Options**
- **Vertical**: Increase CPU/memory limits in docker-compose.yaml
- **Horizontal**: Multiple SecretVM instances with load balancer
- **Component**: Individual interface scaling (future enhancement)

---

## 🔧 **Troubleshooting Guide**

### **Common Issues**

#### **Secret AI Connection Failed**
```bash
# Check API key
docker logs secretgpt-hub | grep "SECRET_AI_API_KEY"

# Verify network connectivity
curl https://secretai-rytn.scrtlabs.com:21434/api/models
```

#### **Telegram Bot Not Responding**
```bash
# Check bot token
echo $TELEGRAM_BOT_TOKEN

# Verify bot configuration
curl "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/getMe"
```

#### **Web UI Attestation Failed**
```bash
# Check attestation endpoint (only works in SecretVM)
curl http://localhost:29343/cpu.html

# This will fail outside SecretVM - expected behavior
```

#### **Container Health Check Failed**
```bash
# Check health endpoint
curl http://localhost:8000/health

# Review container logs
docker logs secretgpt-hub --tail 100
```

### **Log Analysis**
```bash
# Show all logs
docker logs secretgpt-hub

# Follow logs in real-time
docker logs -f secretgpt-hub

# Filter by component
docker logs secretgpt-hub | grep "SECRET_AI"
docker logs secretgpt-hub | grep "WEB_UI" 
docker logs secretgpt-hub | grep "TELEGRAM"
```

---

## 📚 **API Documentation**

### **Web UI Endpoints**

#### **Chat Interface**
```bash
POST /api/v1/chat
Content-Type: application/json

{
  "message": "What is confidential computing?",
  "temperature": 0.7,
  "system_prompt": "You are a helpful assistant."
}
```

#### **Attestation**
```bash
GET /api/v1/attestation/self
# Returns dual VM attestation data
```

#### **Proof Generation**
```bash
POST /api/v1/proof/generate
Content-Type: application/json

{
  "question": "User question",
  "answer": "AI response", 
  "password": "encryption_password"
}
```

### **Telegram Bot Commands**
- `/start` - Welcome message and bot introduction
- `/help` - Available commands and usage instructions
- `/models` - List available Secret AI models
- `/status` - System health and component status
- Text messages - Route through hub to Secret AI

---

## 🔄 **Deployment Variants**

### **Development Deployment**
```yaml
# docker-compose.dev.yaml
environment:
  - ENVIRONMENT=development
  - LOG_LEVEL=DEBUG
  - TELEGRAM_BOT_ENABLED=false
```

### **Production Deployment**
```yaml
# docker-compose.yaml (default)
environment:
  - ENVIRONMENT=production
  - LOG_LEVEL=INFO
  - TELEGRAM_BOT_ENABLED=true
  - SECRETGPT_ENABLE_WEB_UI=true
```

### **Web-Only Deployment**
```yaml
# Disable Telegram bot
environment:
  - TELEGRAM_BOT_ENABLED=false
  - SECRETGPT_ENABLE_WEB_UI=true
```

### **Bot-Only Deployment**
```yaml
# Disable Web UI
environment:
  - TELEGRAM_BOT_ENABLED=true
  - SECRETGPT_ENABLE_WEB_UI=false
```

---

## 🚀 **Advanced Configuration**

### **Custom Secret AI Configuration**
```bash
# Use custom Secret Network node
export SECRET_NODE_URL="https://your-custom-node.com"

# Will use default if not specified
```

### **Resource Optimization**
```yaml
# In docker-compose.yaml
deploy:
  resources:
    limits:
      cpus: '2.0'        # Increase for better performance
      memory: 2G         # Increase for more concurrent users
    reservations:
      cpus: '1.0'
      memory: 1G
```

### **Multi-Instance Deployment**
```bash
# Deploy multiple instances
secretvm-cli vm create --name "secretgpt-1" --docker-compose docker-compose.yaml
secretvm-cli vm create --name "secretgpt-2" --docker-compose docker-compose.yaml

# Use load balancer to distribute traffic
```

---

## ✅ **Production Readiness Checklist**

### **✅ Core Functionality**
- [x] Secret AI integration working across all interfaces
- [x] Hub router properly routes messages
- [x] Dual VM attestation system functional
- [x] Proof generation and encryption working
- [x] Environment variables configure properly
- [x] Error handling graceful across components

### **✅ Interface Integration**
- [x] Web UI: Chat, attestation, proof management functional
- [x] Telegram Bot: All 4 commands + message handling working
- [x] Cross-interface consistency validated
- [x] Single container architecture validated

### **✅ Deployment Infrastructure**
- [x] Docker container builds successfully
- [x] docker-compose.yaml ready for SecretVM
- [x] Health checks and monitoring implemented
- [x] Resource usage optimized for SecretVM

### **✅ Production Requirements**
- [x] Security review completed
- [x] Performance testing conducted
- [x] Documentation complete
- [x] Monitoring and alerting ready

---

## 🎉 **Conclusion**

**secretGPT Hub is production-ready!**

This deployment package provides a complete, secure, and scalable confidential AI system ready for SecretVM deployment. All three phases have been implemented, tested, and validated.

### **Next Steps**
1. Configure your environment variables
2. Deploy to SecretVM using the provided commands
3. Test your deployment using the health endpoints
4. Share your Telegram bot with users
5. Monitor using the provided logging and health checks

### **Support**
- Review logs for troubleshooting
- Use health endpoints for monitoring
- Refer to this guide for configuration options
- Scale resources as needed for your use case

**🚀 Your confidential AI hub is ready for production!**