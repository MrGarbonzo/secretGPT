# secretGPT Resources

This folder contains essential documentation and examples copied from `F:/coding/documents` to support the secretGPT implementation. These resources provide official documentation, working examples, and critical implementation details for all project components.

## 📁 Folder Structure

```
resources/
├── secretAI/                    # Secret AI SDK documentation and examples
├── secretVM/                    # SecretVM deployment and management docs
└── README.md                    # This file
```

---

## 🤖 secretAI Resources

### **Core Documentation**
- **`secretAI-setting-up-environment.txt`** - Official Secret AI SDK setup guide
- **`secretAI-running-application.txt`** - Detailed explanation of Secret AI usage patterns
- **`secret-ai-sdk-README.md`** - Complete SDK documentation and API reference

### **Working Examples**
- **`secret-ai-getting-started-example.py`** - Basic Secret AI integration example
- **`secret-ai-streaming-example.py`** - Advanced streaming implementation with custom handlers
- **`secret-ai-sdk-requirements.txt`** - Complete dependency list for Secret AI SDK

### **Key Implementation Details**

**Environment Setup:**
```bash
export SECRET_AI_API_KEY=bWFzdGVyQHNjcnRsYWJzLmNvbTpTZWNyZXROZXR3b3JrTWFzdGVyS2V5X18yMDI1
pip install secret-ai-sdk
pip install 'secret-sdk>=1.8.1'
```

**Basic Usage Pattern:**
```python
from secret_ai_sdk.secret_ai import ChatSecret
from secret_ai_sdk.secret import Secret

# Model discovery
secret_client = Secret()
models = secret_client.get_models()
urls = secret_client.get_urls(model=models[0])

# Chat client
secret_ai_llm = ChatSecret(
    base_url=urls[0],
    model=models[0],
    temperature=1.0
)

# Message format
messages = [
    ("system", "You are a helpful assistant."),
    ("human", "Hello world"),
]

response = secret_ai_llm.invoke(messages, stream=False)
```

**Critical for secretGPT Implementation:**
- Model discovery with `get_models()` and `get_urls()`
- LangChain-based architecture with `ChatSecret`
- Message format: list of tuples `("role", "content")`
- Streaming support with custom callback handlers
- Environment variable configuration

---

## 🔐 secretVM Resources

### **Core Documentation**
- **`secretVM-full-verification.txt`** - Complete VM attestation verification process
- **`secretVM-authentication-commands.txt`** - CLI authentication management
- **`secretVM-virtual-machine-commands.txt`** - VM lifecycle management commands
- **`secretvm-cli-README.md`** - CLI tool setup and usage

### **Key Implementation Details**

**VM Creation Command:**
```bash
secretvm-cli vm create \
  --name "secretgpt-poc" \
  --type "medium" \
  --docker-compose docker-compose.yaml
```

**Attestation Access:**
- **VM Attestation Endpoint**: `<your_machine_url>:29343/cpu.html`
- **Attestation Fields**: MRTD, RTMR0, RTMR1, RTMR2, RTMR3, report_data
- **Certificate Fingerprint**: For TLS verification

**VM Management:**
```bash
secretvm-cli vm ls                    # List VMs
secretvm-cli vm status <vmUUID>       # VM details
secretvm-cli vm logs <vmId>           # Docker logs
secretvm-cli vm attestation <vmId>    # Attestation data
secretvm-cli vm start/stop <vmId>     # VM control
```

**Critical for secretGPT Implementation:**
- Docker-compose based deployment
- Attestation available at localhost:29343
- VM types: small, medium, large
- Complete lifecycle management via CLI
- Multi-VM deployment support (Phase 4)

---

## 🎯 Implementation Guidance by Phase

### **Phase 1: Secret AI Integration**
**Use these resources:**
- `secretAI-setting-up-environment.txt` - Environment setup
- `secret-ai-getting-started-example.py` - Basic integration pattern
- `secret-ai-sdk-README.md` - Complete API reference

**Key Implementation Points:**
- Use model discovery pattern for production
- Handle SDK errors gracefully
- Implement both sync and async patterns
- Environment variable configuration

### **Phase 2: Web UI with Attestation**
**Use these resources:**
- `secretVM-full-verification.txt` - Attestation implementation
- `secret-ai-streaming-example.py` - Streaming patterns for web UI

**Key Implementation Points:**
- Access VM attestation at localhost:29343/cpu.html
- Parse MRTD, RTMR0-3 fields for proof generation
- Implement dual VM attestation coordination
- TLS certificate fingerprint extraction

### **Phase 3: Telegram Bot**
**Use these resources:**
- `secret-ai-getting-started-example.py` - Simple chat patterns
- `secretAI-running-application.txt` - Message handling

**Key Implementation Points:**
- Use same Secret AI patterns as web UI
- Simple message format for bot integration
- Error handling for service outages

### **Phase 4: MCP Integration**
**Use these resources:**
- `secretVM-virtual-machine-commands.txt` - Multi-VM deployment
- `secretvm-cli-README.md` - CLI for separate MCP deployment

**Key Implementation Points:**
- Deploy secret-network-mcp as separate VM
- Use VM-to-VM HTTP communication
- Leverage existing secret-network-mcp server

---

## 🚀 Quick Start Guides

### **Secret AI Setup (5 minutes)**
```bash
# 1. Install dependencies
pip install secret-ai-sdk 'secret-sdk>=1.8.1'

# 2. Set API key
export SECRET_AI_API_KEY=bWFzdGVyQHNjcnRsYWJzLmNvbTpTZWNyZXROZXR3b3JrTWFzdGVyS2V5X18yMDI1

# 3. Test basic connection
python resources/secretAI/secret-ai-getting-started-example.py
```

### **SecretVM CLI Setup (5 minutes)**
```bash
# 1. Install Node.js 16+
# 2. Clone and build CLI
git clone https://github.com/scrtlabs/secretvm-cli.git
cd secretvm-cli
npm install && npm run build

# 3. Test authentication
./dist/cli.js auth login

# 4. List VMs
./dist/cli.js vm ls
```

### **Attestation Test (2 minutes)**
```bash
# Access your VM's attestation endpoint
curl http://localhost:29343/cpu.html

# Should return attestation data with MRTD, RTMR fields
```

---

## ⚠️ Critical Success Factors

### **Secret AI Integration**
1. **Model Discovery**: Always use `get_models()` and `get_urls()` 
2. **Error Handling**: SDK can fail, implement graceful fallbacks
3. **Message Format**: Strict tuple format `("role", "content")`
4. **Environment**: API key must be set correctly

### **SecretVM Deployment**
1. **Docker-Compose**: All services must be containerized
2. **Attestation**: localhost:29343 only accessible from same VM
3. **Multi-VM**: Phase 4 requires VM-to-VM communication setup
4. **Resource Planning**: Choose appropriate VM sizes for workload

### **Implementation Order**
1. **Test Secret AI locally** before SecretVM deployment
2. **Verify attestation access** early in development
3. **Docker-compose validation** before SecretVM upload
4. **Multi-VM networking** testing for Phase 4

---

## 📚 Additional Resources

- **Secret Network Docs**: https://docs.scrt.network/
- **Secret AI Portal**: https://aidev.scrtlabs.com/
- **secretvm-cli Repository**: https://github.com/scrtlabs/secretvm-cli
- **Secret AI SDK Issues**: https://github.com/scrtlabs/secret-ai-sdk/issues

---

*This resources folder contains everything needed for successful secretGPT implementation. All examples are working code copied from official repositories and documentation.*