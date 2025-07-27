# Build Plan: Extract Secret Network MCP to Standalone Project with Verified Message Signing

## Project Overview
Extract the Secret Network MCP server from the secretGPT hub (`F:\coding\secretGPT`) into a standalone `secret_network_mcp` project that communicates with the hub using SecretVM verified message signing. This is a tech demo showcasing SecretVM's advanced capabilities.

## Source Code Analysis Required

### Examine Current Implementation
**Primary Locations to Analyze**:
```
F:\coding\secretGPT\mcp_servers\secret_network\
├── src/                    # TypeScript MCP implementation
├── package.json           # Dependencies and build scripts  
├── tsconfig.json          # TypeScript configuration
└── build/                 # Compiled output

F:\coding\secretGPT\services\mcp_service\mcp_service.py
# Current hub integration - how MCP is spawned and managed

F:\coding\secretGPT\services\attestation_hub\
├── hub/                   # Core attestation logic
├── api/                   # REST API endpoints  
├── clients/               # Client libraries
└── parsers/               # Attestation parsing
```

### Key Analysis Points
1. **Current MCP Tools**: What Secret Network tools are implemented?
2. **Hub Dependencies**: What hub functions does MCP service depend on?
3. **Communication Patterns**: How does stdio JSON-RPC currently work?
4. **Attestation Patterns**: How does attestation_hub structure its code?
5. **Configuration Management**: How are environment variables handled?

## Important Testing Limitations

### TEE Dependency for Full Testing
**Critical Note**: Verified message signing requires actual SecretVM TEE deployment for complete testing.

**What Can Be Tested Locally**:
- HTTP API functionality
- MCP tool logic and responses  
- Docker container building
- Basic networking between containers
- Mock signature workflows

**What Requires TEE Deployment**:
- Real key generation and attestation quotes
- Actual cryptographic signature verification
- Hardware-level security validation
- True inter-VM authenticated communication
- External attestation verification

### Development vs Production Testing Strategy
- **Development**: Mock keys and bypass signatures for rapid iteration
- **Production**: Full TEE deployment with real cryptographic verification
- **Environment Flag**: `DEVELOPMENT_MODE=true/false` to toggle behavior

## Implementation Tasks

### Phase 1: New Repository Setup

#### Task 1.1: Create Repository Structure
**Create new repository**: `secret_network_mcp`

**Directory Structure**:
```
secret_network_mcp/
├── .github/
│   └── workflows/
│       ├── build.yml                    # CI/CD pipeline
│       └── security.yml                 # Security scanning
├── src/
│   ├── server/                          # MCP server core
│   ├── attestation/                     # SecretVM integration
│   ├── wallet/                          # Keplr integration
│   └── api/                             # HTTP/WebSocket server
├── crypto/                              # Key mount points
│   ├── docker_private_key_ed25519.pem   # SecretVM private key
│   ├── docker_public_key_ed25519.pem    # SecretVM public key
│   └── docker_attestation_ed25519.txt   # Attestation quote
├── docker-compose.yml
├── Dockerfile
├── package.json
└── README.md
```

#### Task 1.2: Extract and Refactor MCP Code
- **Copy** entire `F:\coding\secretGPT\mcp_servers\secret_network\src\` to new repository
- **Remove** hub-specific dependencies and stdio transport  
- **Refactor** for standalone HTTP/WebSocket operation
- **Update** package.json with new dependencies for web server
- **Add** TypeScript configurations for standalone build

#### Task 1.3: Dependencies Analysis and Update
**Analyze current package.json** and add required dependencies:
- `express` - HTTP server
- `ws` - WebSocket support  
- `cors` - Cross-origin requests
- `helmet` - Security headers
- Keep existing: `@modelcontextprotocol/sdk`, `secretjs`, etc.

### Phase 2: Verified Message Signing Implementation

#### Task 2.1: SecretVM Key Integration
**Reference**: SecretVM documentation provided

**Implement key loading**:
```typescript
// Load SecretVM generated keys
const privateKey = loadPrivateKey('/app/data/privkey.pem');
const publicKey = loadPublicKey('/app/data/pubkey.pem'); 
const attestationQuote = loadAttestation('/app/data/quote.txt');
```

**Use ed25519 algorithm** as specified in SecretVM docs

#### Task 2.2: Message Signing Infrastructure
**Based on provided code sample**, implement:
- `signMessage(message: string): string` - Sign outbound messages
- `verifyMessage(message: string, signature: string, publicKey: string): boolean` - Verify inbound messages
- Message format with timestamp and nonce for replay protection
- Base64 encoding for signature transport

#### Task 2.3: HTTP API Server
**Replace stdio transport** with HTTP server:

**Required Endpoints**:
```
POST /mcp/tools/call
- Request: Signed JSON with tool name + parameters
- Response: Signed JSON with tool results

GET /mcp/tools/list  
- Response: Signed JSON with available tools

GET /attestation
- Response: Public key + attestation quote for verification

GET /health
- Response: Service health with attestation status

WebSocket /stream
- Signed real-time communication for streaming responses
```

#### Task 2.4: Attestation Service Integration
**Study**: `F:\coding\secretGPT\services\attestation_hub\` patterns

**Implement**:
- Attestation quote validation
- Public key verification endpoints
- TEE integrity proof generation
- External verification support

### Phase 3: Hub Integration Updates

#### Task 3.1: Update MCP Service in Hub
**Modify**: `F:\coding\secretGPT\services\mcp_service\mcp_service.py`

**Replace process spawning** with HTTP client:
- Remove `subprocess` calls to local MCP server
- Add HTTP client for external MCP communication
- Implement message signing for outbound requests
- Add signature verification for responses
- Add error handling for network failures

#### Task 3.2: Hub Configuration Updates
**Update**: `F:\coding\secretGPT\config\settings.py` and `.env.example`

**Add environment variables** for MCP server discovery:
```bash
# MCP Server Discovery
SECRET_MCP_SERVER_URL=https://10.0.1.100:8001
SECRET_MCP_PUBLIC_KEY_PATH=/app/crypto/mcp_public_key.pem
SECRET_MCP_ATTESTATION_ENDPOINT=https://10.0.1.100:8001/attestation

# Development vs Production Mode
DEVELOPMENT_MODE=false  # Set to true for local testing without TEE
```

**Discovery Process**:
1. Hub reads MCP server IP from environment on startup
2. Attempts connection to configured URL
3. Retrieves and validates attestation quote
4. Establishes trusted communication channel

#### Task 3.3: Hub Router Updates
**Update**: `F:\coding\secretGPT\hub\core\router.py`

**Modify MCP component registration**:
- Change from local process to network client
- Add attestation verification step
- Update error handling for network communication
- Maintain same interface for backward compatibility

### Phase 4: Docker and CI/CD Implementation

#### Task 4.1: Docker Configuration
**Create**: `docker-compose.yml` with SecretVM key mounts

**Follow SecretVM documentation pattern**:
```yaml
services:
  secret-network-mcp:
    image: ghcr.io/[org]/secret_network_mcp:latest
    ports:
      - "8001:8001"
    volumes:
      - ./crypto/docker_private_key_ed25519.pem:/app/data/privkey.pem
      - ./crypto/docker_public_key_ed25519.pem:/app/data/pubkey.pem  
      - ./crypto/docker_attestation_ed25519.txt:/app/data/quote.txt
    environment:
      - NODE_ENV=production
      - PORT=8001
```

#### Task 4.2: GitHub Actions Pipeline
**Create**: `.github/workflows/build.yml`

**Pipeline Requirements**:
- Trigger on push to main and PR creation
- Build and test TypeScript code
- Build Docker image  
- Push to GHCR: `ghcr.io/[org]/secret_network_mcp`
- Tag with version and commit SHA
- Security scanning of container image

#### Task 4.3: Multi-Image Strategy
**Update existing secretGPT pipeline** to build both:
- `ghcr.io/[org]/secretgpt` (existing hub)
- `ghcr.io/[org]/secret_network_mcp` (new standalone MCP)

### Phase 5: Service Discovery and Configuration

#### Task 5.1: Hub Discovery Configuration
**Problem**: Hub needs to find and connect to the MCP server
**Solution**: Environment-based configuration

**Update secretGPT Hub Configuration**:
```
# .env additions for MCP server discovery
SECRET_MCP_SERVER_URL=https://10.0.1.100:8001
SECRET_MCP_PUBLIC_KEY_PATH=/app/crypto/mcp_public_key.pem
SECRET_MCP_ATTESTATION_ENDPOINT=https://10.0.1.100:8001/attestation
```

**Configuration Strategy**:
- Manual IP address entry in environment variables
- Public key exchange during initial setup
- Attestation verification on first connection
- Fallback to error state if MCP server unreachable

#### Task 5.2: MCP Server Registration
**Add to MCP server startup**:
- Health check endpoint (`/health`) 
- Attestation endpoint (`/attestation`)
- Service info endpoint (`/info`) with capabilities
- Connection validation endpoint (`/validate`)

#### Task 5.3: Connection Handshake Protocol
1. **Hub Startup**: Attempts connection to configured MCP server URL
2. **Attestation Exchange**: Mutual verification of TEE integrity
3. **Public Key Exchange**: Both VMs share attested public keys
4. **Capability Discovery**: MCP server advertises available tools
5. **Connection Validation**: Test signed message round-trip

### Phase 6: Testing Strategy (TEE-Limited)

#### Task 6.1: Development Testing (Limited Functionality)
**Important Note**: Full verified message signing testing requires actual TEE deployment

**Pre-TEE Testing Implementation**:
- Mock key generation for local development
- HTTP API functionality without real signatures
- MCP tool logic and responses
- Docker container building and networking
- Basic integration without attestation

**Mock Implementation Requirements**:
- Dummy key files for local development
- Warning messages when running without real TEE
- Bypass signature verification in development mode
- Environment flag: `DEVELOPMENT_MODE=true`

#### Task 6.2: TEE Testing Preparation
**Required for Complete Testing**:
- Real SecretVM key generation
- Actual attestation quote verification
- True inter-VM signed communication
- Hardware-level security validation

**TEE-Specific Test Cases to Implement**:
- End-to-end hub-to-MCP communication with real signatures
- Attestation verification workflows with hardware quotes
- Message replay attack prevention with real crypto
- Invalid signature handling with actual key validation
- TEE integrity verification by external parties

#### Task 6.3: Testing Strategy Implementation
**Development Phase**:
```bash
# Local development without TEE
DEVELOPMENT_MODE=true docker-compose up
# Tests HTTP API, mocks signatures
```

**TEE Deployment Phase**:
```bash
# Real TEE deployment
docker-compose up
# Full cryptographic verification
```

## Technical Implementation Details

### Message Format Specification
**Signed Message Structure**:
```json
{
  "timestamp": 1640995200,
  "nonce": "unique-message-id",
  "payload": {
    "method": "tools/call",
    "params": {...}
  },
  "signature": "base64-encoded-signature"
}
```

### Security Requirements
- **ed25519 signatures** for all inter-VM communication
- **Timestamp validation** (reject messages older than 5 minutes)
- **Nonce tracking** to prevent replay attacks
- **Attestation verification** on connection establishment
- **TLS encryption** for transport layer security

### Error Handling Requirements
- **Network failures**: Retry with exponential backoff
- **Invalid signatures**: Immediate rejection with audit log
- **TEE verification failures**: Connection termination
- **Timeout handling**: Configurable request timeouts
- **Graceful degradation**: Continue with cached data when possible

## Success Criteria

### Functional Requirements
- [ ] Standalone MCP server runs independently on port 8001
- [ ] All existing Secret Network tools work via HTTP API
- [ ] Verified message signing between VMs (TEE only)
- [ ] Attestation quotes properly generated and verified (TEE only)
- [ ] GHCR images build automatically via GitHub Actions
- [ ] Hub successfully discovers and connects to MCP server

### Security Requirements  
- [ ] Private keys never leave TEE boundary (TEE only)
- [ ] All messages cryptographically signed (TEE only)
- [ ] Replay attack protection implemented
- [ ] Invalid signatures properly rejected
- [ ] Attestation quotes validate correctly (TEE only)

### Demo Requirements
- [ ] Clear separation between AI hub and wallet operations
- [ ] Verifiable TEE-to-TEE communication (TEE only)
- [ ] End-to-end transaction signing workflow
- [ ] Attestation verification by external parties (TEE only)
- [ ] Both images deployable to separate SecretVMs

## Development Workflow

### Local Development Process
1. **Extract code** from existing secretGPT repository
2. **Set up new repository** with proper structure
3. **Implement HTTP server** with mock signatures
4. **Test basic functionality** without TEE requirements
5. **Update hub integration** with network client
6. **Verify end-to-end** communication in development mode

### TEE Deployment Process
1. **Deploy both images** to separate SecretVMs
2. **Configure environment variables** with actual IP addresses
3. **Enable production mode** (DEVELOPMENT_MODE=false)
4. **Verify cryptographic** signature functionality
5. **Test complete attestation** workflow
6. **Validate external verification** capabilities

## Files That Need Creation/Modification

### New Repository Files
- All files in new `secret_network_mcp` repository
- GitHub Actions workflows
- Docker configuration
- TypeScript HTTP server implementation
- Attestation integration code

### Modified secretGPT Files
- `services/mcp_service/mcp_service.py` - Replace process with HTTP client
- `config/settings.py` - Add MCP server discovery variables
- `hub/core/router.py` - Update component registration
- `.env.example` - Add new environment variables
- GitHub Actions workflows - Add second image build

This comprehensive build plan provides all the details needed to extract the Secret Network MCP into a standalone project with verified message signing capabilities.