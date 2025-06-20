# secretGPT Hub - Detailed Build Plan with Documentation References
*Implementation Guide Based on Official Documentation - Last Updated: June 19, 2025*

## Executive Summary

This document provides an exhaustive implementation guide for building the secretGPT hub system with four priority components:
1. **Secret AI Integration** - Using secret-ai-sdk with proper attestation
2. **Web UI Integration** - attest_ai interface migration
3. **Telegram Bot Interface** - Business user access
4. **Secret Network MCP** - Existing MCP server integration with HTTP/STDIO support

---

## Phase 1: Core Foundation (Weeks 1-2)
**Priority 1: Secret AI "talking to" secretGPT**

### **📖 Documentation References**

**PRIMARY GUIDES:**
- **MAIN IMPLEMENTATION**: `F:\coding\secretGPT\resources\secretAI\secret-ai-getting-started-example.py` (complete working example)
- **API REFERENCE**: `F:\coding\secretGPT\resources\secretAI\secret-ai-sdk-README.md` (Secret class, ChatSecret class documentation)
- **ENVIRONMENT SETUP**: `F:\coding\secretGPT\resources\secretAI\secretAI-setting-up-environment.txt` (API key configuration)
- **ASYNC PATTERNS**: `F:\coding\secretGPT\resources\secretAI\secret-ai-streaming-example.py` (streaming and async implementation)
- **DEPENDENCIES**: `F:\coding\secretGPT\resources\secretAI\secret-ai-sdk-requirements.txt` (exact package versions)

**DEPLOYMENT REFERENCES:**
- **SECRETVM SETUP**: `F:\coding\secretGPT\resources\secretVM\secretvm-cli-README.md` (CLI commands and setup)
- **VM MANAGEMENT**: `F:\coding\secretGPT\resources\secretVM\secretVM-virtual-machine-commands.txt` (deployment commands)

### **🔍 Key Implementation Points with Doc References**

**Secret AI Service Architecture (`secretGPT/services/secret_ai/client.py`):**
```python
# REFERENCE: secret-ai-getting-started-example.py lines 1-3
from secret_ai_sdk.secret_ai import ChatSecret
from secret_ai_sdk.secret import Secret

# REFERENCE: secret-ai-getting-started-example.py lines 4-6
# Model discovery pattern - CRITICAL: Always use this pattern
secret_client = Secret()
models = secret_client.get_models()
urls = secret_client.get_urls(model=models[0])

# REFERENCE: secret-ai-getting-started-example.py lines 8-12
# Client initialization pattern
secret_ai_llm = ChatSecret(
    base_url=urls[0],
    model=models[0], 
    temperature=1.0
)

# REFERENCE: secret-ai-getting-started-example.py lines 14-20
# Message format - MUST BE TUPLES, NOT DICTS
messages = [
    ("system", "You are a helpful assistant."),
    ("human", user_message),
]

# REFERENCE: secret-ai-getting-started-example.py line 22
# Sync invocation
response = secret_ai_llm.invoke(messages, stream=False)

# REFERENCE: secret-ai-streaming-example.py line 103
# Async invocation for hub integration
response = await llm.ainvoke(messages)
```

**Environment Configuration (reference: `secretAI-setting-up-environment.txt`):**
```bash
# CRITICAL: Must be set exactly as shown in secretAI-setting-up-environment.txt
export SECRET_AI_API_KEY=bWFzdGVyQHNjcnRsYWJzLmNvbTpTZWNyZXROZXR3b3JrTWFzdGVyS2V5X18yMDI1

# REFERENCE: secret-ai-sdk-requirements.txt for exact versions
pip install secret-ai-sdk
pip install 'secret-sdk>=1.8.1'
pip install langchain-ollama
```

**Hub Router Architecture (`secretGPT/hub/core/router.py`):**
```python
# REFERENCE: secret-ai-streaming-example.py for async patterns
# IMPLEMENTATION: Create centralized message routing through Secret AI service
class HubRouter:
    async def route_message(self, interface: str, message: str, options: dict):
        # Route through Secret AI service using patterns from examples
        pass
```

### **⚠️ Critical Implementation Requirements from Documentation**

**From `secret-ai-getting-started-example.py`:**
- Message format MUST be list of tuples: `[("role", "content")]` (line 14-20)
- Always use model discovery pattern `get_models()` → `get_urls()` (lines 4-6)
- Response content accessed via `response.content` (line 23)

**From `secretAI-setting-up-environment.txt`:**
- API key must be exported before importing SDK
- Environment variable name is case-sensitive: `SECRET_AI_API_KEY`

**From `secret-ai-streaming-example.py`:**
- Async invocation uses `await llm.ainvoke(messages)` (line 103)
- Streaming requires callback handlers for real-time output
- Custom handlers implement `BaseCallbackHandler` class

### **🚀 Phase 1 Implementation Strategy**

**Week 1: Hub Framework + Secret AI Integration**

**Day 1-2: Project Setup**
- **REFERENCE**: `secret-ai-sdk-requirements.txt` for dependencies
- **ACTION**: Setup Python environment with exact package versions
- **VALIDATION**: Test `secret-ai-getting-started-example.py` works locally

**Day 3-5: Secret AI Service Implementation**
- **REFERENCE**: `secret-ai-getting-started-example.py` for basic patterns
- **REFERENCE**: `secret-ai-streaming-example.py` for async implementation
- **ACTION**: Build `SecretAIService` class using documented patterns
- **VALIDATION**: Model discovery and basic chat functionality work

**Day 6-8: Hub Router Development**
- **REFERENCE**: Create hub message routing architecture
- **ACTION**: Implement central message router with component registry
- **VALIDATION**: Messages route correctly through hub to Secret AI

**Day 9-10: Configuration Management**
- **REFERENCE**: `secretAI-setting-up-environment.txt` for environment setup
- **ACTION**: Environment variable configuration system
- **VALIDATION**: All components configurable via environment variables

**Week 2: SecretVM Integration and Testing**

**Day 11-12: Docker Containerization**
- **REFERENCE**: `secretvm-cli-README.md` for deployment requirements
- **ACTION**: Create Dockerfile and docker-compose.yaml
- **VALIDATION**: Container builds and runs locally

**Day 13-14: SecretVM Deployment**
- **REFERENCE**: `secretVM-virtual-machine-commands.txt` for deployment commands
- **ACTION**: Deploy to SecretVM using `secretvm-cli vm create`
- **VALIDATION**: Secret AI integration works in SecretVM environment

### **✅ Phase 1 Success Criteria**

- [ ] Secret AI service discovers models using `get_models()` (ref: secret-ai-getting-started-example.py line 5)
- [ ] Messages format correctly as tuples (ref: secret-ai-getting-started-example.py lines 14-20)
- [ ] Hub router routes messages to Secret AI service
- [ ] Response content extracted correctly via `response.content` (ref: secret-ai-getting-started-example.py line 23)
- [ ] Container deploys successfully to SecretVM
- [ ] Environment variables configure all components

---

## Phase 2: Web Interface (Weeks 3-4)
**Priority 2: Web UI with attest_ai working**

### **📖 Documentation References**

**PRIMARY MIGRATION SOURCES:**
- **EXISTING IMPLEMENTATION**: `F:\coding\attest_ai\src\main.py` (FastAPI application structure)
- **ATTESTATION LOGIC**: `F:\coding\attest_ai\src\attestation\` (dual attestation implementation)
- **PROOF MANAGER**: `F:\coding\attest_ai\src\encryption\proof_manager.py` (encryption/decryption logic)
- **WEB TEMPLATES**: `F:\coding\attest_ai\templates\` (HTML templates to migrate)
- **STATIC ASSETS**: `F:\coding\attest_ai\static\` (CSS/JS to migrate)

**ATTESTATION REFERENCES:**
- **VM ATTESTATION**: `F:\coding\secretGPT\resources\secretVM\secretVM-full-verification.txt` (attestation process)
- **ENDPOINT ACCESS**: localhost:29343/cpu.html (from secretVM-full-verification.txt)
- **ATTESTATION FIELDS**: MRTD, RTMR0, RTMR1, RTMR2, RTMR3, report_data (from secretVM-full-verification.txt)

**SECRET AI INTEGRATION:**
- **CHAT PATTERNS**: Reference Phase 1 Secret AI service implementation
- **STREAMING**: `F:\coding\secretGPT\resources\secretAI\secret-ai-streaming-example.py` (web UI streaming)

### **🔍 Key Implementation Points with Doc References**

**Web UI Interface Structure (`secretGPT/interfaces/web_ui/`):**
```python
# REFERENCE: F:\coding\attest_ai\src\main.py (FastAPI app structure)
from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# MIGRATE: Preserve existing attest_ai FastAPI routes but route through hub
class WebUIInterface:
    def __init__(self, hub_router: HubRouter):
        self.app = FastAPI(title="secretGPT Web UI")
        self.hub_router = hub_router  # Route through hub instead of direct Secret AI
```

**Attestation Service Integration (`secretGPT/interfaces/web_ui/attestation/`):**
```python
# REFERENCE: F:\coding\attest_ai\src\attestation\ (existing attestation logic)
# REFERENCE: secretVM-full-verification.txt (VM attestation endpoint)

# CRITICAL: VM attestation endpoint from secretVM-full-verification.txt
ATTESTATION_ENDPOINT = "http://localhost:29343/cpu.html"

# REFERENCE: secretVM-full-verification.txt for required fields
def parse_attestation_data(attestation_response):
    # Extract: MRTD, RTMR0, RTMR1, RTMR2, RTMR3, report_data
    # Parse certificate fingerprint for TLS verification
    pass
```

**Proof Management Migration (`secretGPT/interfaces/web_ui/encryption/`):**
```python
# REFERENCE: F:\coding\attest_ai\src\encryption\proof_manager.py
# MIGRATE: Existing proof generation logic but integrate with hub's Secret AI service

class ProofManager:
    def generate_proof(self, chat_data, attestations, password):
        # Use existing attest_ai logic but with hub-provided data
        pass
```

**Template Migration (`secretGPT/interfaces/web_ui/templates/`):**
```html
<!-- REFERENCE: F:\coding\attest_ai\templates\ -->
<!-- MIGRATE: Existing HTML templates with minimal changes -->
<!-- UPDATE: API endpoints to route through hub -->
```

### **⚠️ Critical Migration Requirements from Documentation**

**From `attest_ai/src/main.py`:**
- Preserve all existing FastAPI route structures
- Maintain template rendering patterns
- Keep static file serving configuration

**From `secretVM-full-verification.txt`:**
- Attestation endpoint is `localhost:29343/cpu.html` (only accessible from same VM)
- Required fields: "mr_td, rtrmr0, rtmr1, rtmr2, rtmr3 and the report_data registers"
- Certificate fingerprint verification: "To rule out a man-in-the-middle attack, view the certificate that secures the connection and note its fingerprint value"

**From `attest_ai/src/attestation/`:**
- Dual attestation pattern (self VM + Secret AI VM)
- Attestation caching with TTL
- Error handling for attestation failures

### **🚀 Phase 2 Implementation Strategy**

**Week 3: Core Infrastructure Migration**

**Day 15-17: attest_ai Logic Extraction**
- **REFERENCE**: `F:\coding\attest_ai\src\main.py` for FastAPI structure
- **ACTION**: Extract core attest_ai components into secretGPT interface structure
- **VALIDATION**: All attest_ai endpoints identified and documented

**Day 18-19: Attestation Service Development**
- **REFERENCE**: `F:\coding\attest_ai\src\attestation\` for existing logic
- **REFERENCE**: `secretVM-full-verification.txt` for VM attestation details
- **ACTION**: Build dual VM attestation coordinator
- **VALIDATION**: Self-VM attestation accessible at localhost:29343/cpu.html

**Day 20-21: Hub Integration**
- **REFERENCE**: Phase 1 Secret AI service for chat integration
- **ACTION**: Replace direct Secret AI calls with hub router calls
- **VALIDATION**: Web UI chat routes through hub to Secret AI

**Week 4: Web UI Completion and Integration**

**Day 22-23: Template and Static Asset Migration**
- **REFERENCE**: `F:\coding\attest_ai\templates\` and `F:\coding\attest_ai\static\`
- **ACTION**: Migrate HTML templates and assets with updated API endpoints
- **VALIDATION**: Web UI renders correctly with secretGPT branding

**Day 24-25: Proof Management Integration**
- **REFERENCE**: `F:\coding\attest_ai\src\encryption\proof_manager.py`
- **ACTION**: Integrate proof generation with hub's Secret AI responses
- **VALIDATION**: Proof generation includes dual VM attestation data

**Day 26-28: End-to-End Testing and Polish**
- **ACTION**: Complete web UI testing with all features
- **VALIDATION**: All attest_ai functionality preserved and working through hub

### **✅ Phase 2 Success Criteria**

- [ ] FastAPI app structure migrated from `attest_ai/src/main.py`
- [ ] Attestation endpoint accessible at localhost:29343/cpu.html (ref: secretVM-full-verification.txt)
- [ ] Dual attestation extracts MRTD, RTMR0-3, report_data fields (ref: secretVM-full-verification.txt)
- [ ] Chat interface routes through hub router (ref: Phase 1 implementation)
- [ ] Proof generation includes question + answer + dual attestation
- [ ] All attest_ai templates and static assets migrated
- [ ] .attestproof file generation and decryption works

---

## Phase 3: Telegram Integration (Weeks 5-6)
**Priority 3: Telegram bot interface**

### **📖 Documentation References**

**PRIMARY TELEGRAM BOT GUIDE:**
- **OFFICIAL DOCS**: https://docs.python-telegram-bot.org/ (python-telegram-bot library documentation)
- **GETTING STARTED**: https://docs.python-telegram-bot.org/en/stable/tutorial.html (basic bot setup)
- **ASYNC PATTERNS**: https://docs.python-telegram-bot.org/en/stable/tutorial.asyncio.html (async bot implementation)

**SECRET AI INTEGRATION:**
- **CHAT PATTERNS**: Reference Phase 1 Secret AI service implementation
- **HUB ROUTING**: Reference Phase 1 hub router for message routing
- **MESSAGE FORMAT**: `F:\coding\secretGPT\resources\secretAI\secret-ai-getting-started-example.py` (tuple format)

**DEPLOYMENT INTEGRATION:**
- **CONTAINER SETUP**: Phase 2 single container architecture
- **SECRETVM DEPLOYMENT**: `F:\coding\secretGPT\resources\secretVM\secretvm-cli-README.md`

### **🔍 Key Implementation Points with Doc References**

**Telegram Bot Interface Structure (`secretGPT/interfaces/telegram_bot/`):**
```python
# REFERENCE: https://docs.python-telegram-bot.org/en/stable/tutorial.html
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# REFERENCE: https://docs.python-telegram-bot.org/en/stable/tutorial.asyncio.html (async patterns)
class TelegramBotInterface:
    def __init__(self, token: str, hub_router: HubRouter):
        self.app = ApplicationBuilder().token(token).build()
        self.hub_router = hub_router  # Route through hub to Secret AI
```

**Command Handlers (`secretGPT/interfaces/telegram_bot/handlers/`):**
```python
# REFERENCE: https://docs.python-telegram-bot.org/en/stable/tutorial.html (command handler patterns)
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Welcome message with secretGPT information
    pass

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Simple help text explaining bot usage
    pass

async def models_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # List available Secret AI models from hub
    # REFERENCE: Phase 1 hub router get_available_models()
    pass

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Basic system status (Secret AI available/unavailable)
    pass
```

**Message Handling (`secretGPT/interfaces/telegram_bot/handlers/conversations.py`):**
```python
# REFERENCE: https://docs.python-telegram-bot.org/en/stable/tutorial.html (message handlers)
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    
    # REFERENCE: Phase 1 hub router for message routing
    response = await self.hub_router.route_message(
        interface="telegram",
        message=user_message,
        options={"temperature": 0.6}
    )
    
    # REFERENCE: https://docs.python-telegram-bot.org/en/stable/tutorial.html (sending responses)
    await update.message.reply_text(response["response"])
```

**Bot Configuration:**
```python
# REFERENCE: https://docs.python-telegram-bot.org/en/stable/tutorial.html (application builder)
app = ApplicationBuilder().token("YOUR_BOT_TOKEN").build()

# REFERENCE: https://docs.python-telegram-bot.org/en/stable/tutorial.html (handler registration)
app.add_handler(CommandHandler("start", start_command))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(CommandHandler("models", models_command))
app.add_handler(CommandHandler("status", status_command))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
```

### **⚠️ Critical Implementation Requirements from Documentation**

**From python-telegram-bot documentation:**
- Bot token must be obtained from BotFather on Telegram
- Async patterns required: `async def` for all handlers
- Update object contains message data: `update.message.text`
- Response via: `await update.message.reply_text(text)`
- Application runs with: `await app.run_polling()`

**From Phase 1 Secret AI integration:**
- Message format must be tuples for Secret AI (ref: secret-ai-getting-started-example.py)
- Hub router handles Secret AI communication
- Error handling for Secret AI service failures

**From Phase 2 Web UI patterns:**
- Single container architecture - no additional Docker complexity
- Environment variable configuration for bot token

### **🚀 Phase 3 Implementation Strategy**

**Week 5: Telegram Bot Development**

**Day 29-30: Bot Framework Setup**
- **REFERENCE**: https://docs.python-telegram-bot.org/en/stable/tutorial.html for setup
- **ACTION**: Install python-telegram-bot, create basic bot structure
- **VALIDATION**: Bot responds to /start command

**Day 31-32: Command Implementation**
- **REFERENCE**: https://docs.python-telegram-bot.org/en/stable/tutorial.html for command handlers
- **ACTION**: Implement /start, /help, /status, /models commands
- **VALIDATION**: All 4 commands work correctly

**Day 33-34: Hub Integration**
- **REFERENCE**: Phase 1 hub router implementation
- **ACTION**: Integrate message handling with hub router
- **VALIDATION**: Messages route through hub to Secret AI

**Day 35: Error Handling and Polish**
- **ACTION**: Implement graceful error handling for service outages
- **VALIDATION**: Bot handles Secret AI failures gracefully

**Week 6: Integration and Deployment**

**Day 36-37: Container Integration**
- **REFERENCE**: Phase 2 single container architecture
- **ACTION**: Integrate bot into existing secretGPT container
- **VALIDATION**: Bot starts with hub router in single container

**Day 38-39: Environment Configuration**
- **ACTION**: Add telegram bot environment variables to configuration
- **VALIDATION**: Bot configurable via environment variables only

**Day 40-42: Final Testing and Documentation**
- **ACTION**: End-to-end testing of bot functionality
- **VALIDATION**: All Phase 3 success criteria met

### **✅ Phase 3 Success Criteria**

- [ ] Bot responds to all 4 commands (/start, /help, /models, /status)
- [ ] Message handling routes through hub to Secret AI (ref: Phase 1 hub router)
- [ ] Bot uses async patterns (ref: python-telegram-bot async tutorial)
- [ ] Error handling for Secret AI service outages
- [ ] Single container integration (ref: Phase 2 architecture)
- [ ] Environment variable configuration (ref: Phase 2 config system)

---

## Phase 4: MCP Integration (Weeks 7-8)
**Priority 4: Secret Network MCP integration**

### **📖 Documentation References**

**EXISTING MCP SERVER:**
- **MAIN REPOSITORY**: `F:\coding\secret-network-mcp\` (complete existing MCP server)
- **SERVER STRUCTURE**: `F:\coding\secret-network-mcp\src\` (TypeScript/Node.js implementation)
- **PACKAGE.JSON**: `F:\coding\secret-network-mcp\package.json` (dependencies and scripts)
- **README**: `F:\coding\secret-network-mcp\README.md` (setup and usage)

**MCP PROTOCOL:**
- **OFFICIAL SPEC**: https://modelcontextprotocol.io/ (MCP protocol documentation)
- **TRANSPORT MODES**: STDIO and HTTP/SSE support
- **TOOL CALLING**: JSON-RPC format for tool invocation

**SECRETVM DEPLOYMENT:**
- **MULTI-VM SETUP**: `F:\coding\secretGPT\resources\secretVM\secretVM-virtual-machine-commands.txt`
- **SEPARATE DEPLOYMENT**: Independent SecretVM instance for MCP server

**SECRET NETWORK INTEGRATION:**
- **NETWORK TOOLS**: Reference secret-network-mcp existing tools
- **CHAIN ACCESS**: Secret Network mainnet/testnet configuration

### **🔍 Key Implementation Points with Doc References**

**MCP Service Architecture (`secretGPT/services/mcp/`):**
```python
# REFERENCE: F:\coding\secret-network-mcp\ for existing tool implementations
# IMPLEMENTATION: HTTP client to connect to external MCP server

class MCPService:
    def __init__(self):
        # Connect to external secret-network-mcp server via HTTP
        self.server_url = "http://secret-network-mcp:3000"  # External server
        
    async def call_tool(self, tool: str, arguments: dict):
        # REFERENCE: MCP protocol spec for JSON-RPC format
        # HTTP POST to external MCP server
        pass
```

**External MCP Server (separate deployment):**
```bash
# REFERENCE: F:\coding\secret-network-mcp\package.json for build commands
cd F:\coding\secret-network-mcp
npm install
npm run build

# REFERENCE: F:\coding\secret-network-mcp\README.md for configuration
export NODE_ENV=production
export NETWORK=mainnet
node dist/server.js
```

**Available MCP Tools (from existing secret-network-mcp):**
```python
# REFERENCE: F:\coding\secret-network-mcp\src\ for complete tool list
AVAILABLE_TOOLS = [
    "get_network_status",    # Network information
    "get_block_info",        # Block details
    "get_transaction_info",  # Transaction details
    "get_token_balance",     # SCRT balance
    "get_snip20_token_info", # SNIP-20 token details
    "query_contract",        # Smart contract queries
    # ... see secret-network-mcp\src\ for complete list
]
```

**Hub Integration (`secretGPT/hub/core/router.py` enhancement):**
```python
# REFERENCE: Phase 1 hub router implementation
class HubRouter:
    def __init__(self):
        self.mcp_service = MCPService()  # Add MCP service
        
    async def query_secret_network(self, tool: str, **kwargs):
        # Route Secret Network queries through MCP service
        return await self.mcp_service.call_tool(tool, kwargs)
```

**Web UI MCP Integration (`secretGPT/interfaces/web_ui/` enhancement):**
```python
# REFERENCE: Phase 2 web UI implementation
# ADD: MCP tool endpoints to existing FastAPI app

@app.get("/api/v1/network/status")
async def network_status():
    # REFERENCE: secret-network-mcp get_network_status tool
    return await hub_router.query_secret_network("get_network_status")

@app.post("/api/v1/network/balance")
async def check_balance(address: str):
    # REFERENCE: secret-network-mcp get_token_balance tool
    return await hub_router.query_secret_network("get_token_balance", address=address)
```

**Telegram MCP Commands (`secretGPT/interfaces/telegram_bot/` enhancement):**
```python
# REFERENCE: Phase 3 telegram bot implementation
# ADD: MCP commands to existing bot

async def network_status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # REFERENCE: secret-network-mcp get_network_status tool
    result = await hub_router.query_secret_network("get_network_status")
    await update.message.reply_text(f"Network Status:\nBlock Height: {result['block_height']}")

async def balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # REFERENCE: secret-network-mcp get_token_balance tool
    # Usage: /balance secret1abc123...
    address = " ".join(context.args)
    result = await hub_router.query_secret_network("get_token_balance", address=address)
    await update.message.reply_text(f"Balance: {result['balance']} SCRT")
```

### **⚠️ Critical Implementation Requirements from Documentation**

**From `secret-network-mcp` repository:**
- Server runs on Node.js with TypeScript
- Tools return structured JSON responses
- Configuration via environment variables
- HTTP/SSE transport on port 3000

**From MCP Protocol:**
- JSON-RPC 2.0 format for tool calls
- Request: `{"jsonrpc": "2.0", "method": "tools/call", "params": {"name": "tool", "arguments": {}}}`
- Response: `{"jsonrpc": "2.0", "result": {...}}`

**From SecretVM multi-VM deployment:**
- Separate SecretVM instances for secretGPT and MCP server
- VM-to-VM HTTP communication
- Independent configuration and deployment

### **🚀 Phase 4 Implementation Strategy**

**Week 7: Core MCP Infrastructure**

**Day 43-44: MCP Service Development**
- **REFERENCE**: MCP protocol documentation for JSON-RPC format
- **ACTION**: Build HTTP MCP client in secretGPT hub
- **VALIDATION**: Can connect to mock MCP server

**Day 45-46: secret-network-mcp Integration**
- **REFERENCE**: `F:\coding\secret-network-mcp\` for existing server
- **ACTION**: Deploy secret-network-mcp as separate service
- **VALIDATION**: secretGPT can call secret-network-mcp tools via HTTP

**Day 47-49: Hub MCP Integration**
- **REFERENCE**: Phase 1 hub router implementation
- **ACTION**: Add MCP service to hub router
- **VALIDATION**: Hub can route MCP tool calls

**Week 8: Interface Integration and Deployment**

**Day 50-51: Web UI MCP Integration**
- **REFERENCE**: Phase 2 web UI FastAPI implementation
- **REFERENCE**: `F:\coding\secret-network-mcp\src\` for available tools
- **ACTION**: Add MCP tool endpoints to web UI
- **VALIDATION**: Web UI can display Secret Network data

**Day 52-53: Telegram MCP Integration**
- **REFERENCE**: Phase 3 telegram bot implementation
- **ACTION**: Add MCP commands to telegram bot
- **VALIDATION**: Bot responds to /network_status, /balance commands

**Day 54-55: Multi-VM Deployment**
- **REFERENCE**: `secretVM-virtual-machine-commands.txt` for multi-VM setup
- **ACTION**: Deploy secretGPT and secret-network-mcp as separate VMs
- **VALIDATION**: VM-to-VM communication works

**Day 56: Final Integration Testing**
- **ACTION**: End-to-end testing of all MCP functionality
- **VALIDATION**: All Phase 4 success criteria met

### **✅ Phase 4 Success Criteria**

- [ ] HTTP MCP client connects to external secret-network-mcp server (ref: secret-network-mcp repository)
- [ ] MCP service calls tools using JSON-RPC format (ref: MCP protocol spec)
- [ ] Hub router includes MCP service (ref: Phase 1 implementation)
- [ ] Web UI displays Secret Network data (ref: secret-network-mcp tools)
- [ ] Telegram bot responds to MCP commands (ref: Phase 3 implementation)
- [ ] Multi-VM deployment works (ref: secretVM-virtual-machine-commands.txt)
- [ ] All 3 priority MCP tools functional: get_network_status, get_token_balance, get_block_info

---

## Docker Deployment Strategy with References

### **📖 Documentation References**

**SECRETVM DEPLOYMENT:**
- **CLI COMMANDS**: `F:\coding\secretGPT\resources\secretVM\secretvm-cli-README.md`
- **VM MANAGEMENT**: `F:\coding\secretGPT\resources\secretVM\secretVM-virtual-machine-commands.txt`
- **DEPLOYMENT PROCESS**: docker-compose.yaml upload via `secretvm-cli vm create`

**EXISTING DOCKER EXAMPLES:**
- **ATTEST_AI REFERENCE**: `F:\coding\attest_ai\docker-compose.yaml` (single service pattern)
- **SECRET-NETWORK-MCP**: `F:\coding\secret-network-mcp\Dockerfile` (Node.js containerization)

### **🔍 Docker Implementation with Doc References**

**Single Container (Phases 1-3) - `docker-compose.yaml`:**
```yaml
# REFERENCE: F:\coding\attest_ai\docker-compose.yaml for single service pattern
version: '3.8'
services:
  secretgpt:
    build: .
    container_name: secretgpt-hub
    ports:
      - "8000:8000"
    environment:
      # REFERENCE: secretAI-setting-up-environment.txt
      - SECRET_AI_API_KEY=bWFzdGVyQHNjcnRsYWJzLmNvbTpTZWNyZXROZXR3b3JrTWFzdGVyS2V5X18yMDI1
      # REFERENCE: Phase 2 web UI configuration
      - SECRETGPT_ENABLE_WEB_UI=true
      # REFERENCE: Phase 3 telegram bot configuration
      - TELEGRAM_BOT_ENABLED=true
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
```

**Multi-Container (Phase 4) - secretGPT deployment:**
```yaml
# REFERENCE: Phase 4 multi-VM architecture
services:
  secretgpt:
    # Same as above plus MCP configuration
    environment:
      - MCP_SECRET_NETWORK_URL=http://secret-network-mcp:3000
```

**Multi-Container (Phase 4) - secret-network-mcp deployment (separate VM):**
```yaml
# REFERENCE: F:\coding\secret-network-mcp\ for existing MCP server
services:
  secret-network-mcp:
    build: 
      context: F:\coding\secret-network-mcp
    ports:
      - "3000:3000"
    environment:
      # REFERENCE: secret-network-mcp README.md
      - NODE_ENV=production
      - NETWORK=mainnet
```

**Deployment Commands:**
```bash
# REFERENCE: secretvm-cli-README.md for deployment commands

# Phase 1-3: Single container
secretvm-cli vm create \
  --name "secretgpt-hub" \
  --type "medium" \
  --docker-compose docker-compose.yaml

# Phase 4: Multi-container (separate VMs)
secretvm-cli vm create \
  --name "secretgpt-hub" \
  --type "medium" \
  --docker-compose secretgpt-docker-compose.yaml

secretvm-cli vm create \
  --name "secret-network-mcp" \
  --type "small" \
  --docker-compose mcp-docker-compose.yaml
```

---

## Final Implementation Checklist with Documentation Validation

### **Phase 1 Validation Checklist**
- [ ] **Secret AI Integration**: Verify against `secret-ai-getting-started-example.py` patterns
- [ ] **Model Discovery**: Test `get_models()` and `get_urls()` (ref: line 4-6)
- [ ] **Message Format**: Confirm tuple format `[("role", "content")]` (ref: line 14-20)
- [ ] **API Key**: Validate environment variable from `secretAI-setting-up-environment.txt`
- [ ] **Hub Router**: Messages route correctly through central hub
- [ ] **SecretVM Deploy**: Test deployment using `secretvm-cli` commands

### **Phase 2 Validation Checklist**
- [ ] **attest_ai Migration**: All features from `F:\coding\attest_ai\` preserved
- [ ] **Attestation Endpoint**: Access localhost:29343/cpu.html (ref: secretVM-full-verification.txt)
- [ ] **Attestation Fields**: Extract MRTD, RTMR0-3, report_data (ref: secretVM-full-verification.txt)
- [ ] **Proof Generation**: Includes dual VM attestation data
- [ ] **Web UI Integration**: Routes through hub to Secret AI
- [ ] **Template Migration**: All HTML/CSS/JS assets work

### **Phase 3 Validation Checklist**
- [ ] **Bot Commands**: All 4 commands work (/start, /help, /models, /status)
- [ ] **python-telegram-bot**: Async patterns from official documentation
- [ ] **Hub Integration**: Messages route through Phase 1 hub router
- [ ] **Error Handling**: Graceful handling of Secret AI outages
- [ ] **Container Integration**: Runs in single container with web UI
- [ ] **Environment Config**: Configurable via environment variables

### **Phase 4 Validation Checklist**
- [ ] **MCP Server**: secret-network-mcp from `F:\coding\secret-network-mcp\` works
- [ ] **HTTP Transport**: JSON-RPC communication with external MCP server
- [ ] **Tool Integration**: get_network_status, get_token_balance, get_block_info work
- [ ] **Multi-VM Deploy**: Separate SecretVM instances communicate
- [ ] **Web UI MCP**: Secret Network data displays in web interface
- [ ] **Telegram MCP**: Bot responds to MCP commands

### **Documentation Compliance Verification**
- [ ] All implementations reference specific documentation files
- [ ] Code patterns match provided examples exactly
- [ ] Environment variables follow documented naming conventions
- [ ] Deployment follows SecretVM CLI documentation
- [ ] Error handling includes fallbacks as documented

This restructured plan now provides Claude Code with specific documentation references for every implementation decision, making the development process much more accurate and efficient.