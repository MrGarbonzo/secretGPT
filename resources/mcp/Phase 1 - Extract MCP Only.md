# Phase 1: Extract Secret Network MCP to Standalone VM

## Goal
Move the existing Secret Network MCP server from the secretGPT hub into its own standalone project that can be deployed to a separate VM, while maintaining all current functionality.

**Path Context**: 
- **Local Development**: `F:\coding\secretGPT`
- **Build Environment** (GitHub Actions/VMs): Root `/`
- All file paths in this document use local format, adjust for build environment

## Scope (Phase 1 Only)
- ✅ Extract existing Secret Network MCP to new repository
- ✅ Convert from stdio to HTTP API communication
- ✅ Test with existing attestai.io frontend
- ❌ No Keplr wallet integration (future phase)
- ❌ No new secretgptee.com website (future phase)
- ❌ No verified message signing (future phase)

## Current State Analysis

### What exists now:
```
F:\coding\secretGPT\
├── mcp_servers\secret_network\        # Working MCP server
│   ├── src\                          # TypeScript implementation
│   ├── package.json                  # Dependencies
│   └── build\                        # Compiled output
└── services\mcp_service\mcp_service.py # Hub integration (stdio)
```

### What we need to create:
```
New Repository: secret_network_mcp
├── src\                              # Moved from existing MCP
├── api\                             # New HTTP server layer
├── package.json                     # Updated dependencies
├── docker-compose.yml               # Standalone deployment
├── Dockerfile                       # Container image
└── .github\workflows\build.yml      # CI/CD pipeline
```

## Implementation Steps

### Step 1: Repository Setup and Code Migration
**Create new repository**: `secret_network_mcp`

**Copy and Clean Process**:
1. **Copy entire** `F:\coding\secretGPT\mcp_servers\secret_network\` to new repository
2. **DELETE original files** after successful copy:
   ```
   DELETE: F:\coding\secretGPT\mcp_servers\secret_network\
   ```
3. **Keep all existing Secret Network tools unchanged** in new repository
4. **Maintain current package.json dependencies**

**IMPORTANT**: Ensure complete removal of old MCP files from secretGPT repository to avoid confusion and conflicts.

### Step 2: Add HTTP API Layer
**Replace stdio transport** with HTTP server:

**New dependencies to add to secret_network_mcp**:
```json
{
  "express": "^4.18.x",
  "cors": "^2.8.x", 
  "helmet": "^7.0.x"
}
```

**New HTTP endpoints**:
```
POST /api/mcp/tools/call     # Execute MCP tool
GET  /api/mcp/tools/list     # List available tools  
GET  /api/health             # Health check
```

### Step 3: Update Hub Integration
**Modify**: `F:\coding\secretGPT\services\mcp_service\mcp_service.py`

**Replace subprocess calls** with HTTP client:
- Copy the communication pattern from `services/secret_ai/client.py`
- Change from stdio JSON-RPC to HTTP requests
- Maintain same interface for hub router

### Step 4: Configuration
**Add to secretGPT hub** (`.env`):
```bash
SECRET_MCP_URL=http://10.0.1.100:8002
```

**Add to new MCP server** (`.env`):
```bash
PORT=8002
SECRET_NODE_URL=https://api.secret.network
```

### Step 5: Docker Setup - MCP Repository
**Create in secret_network_mcp repository root**:

**File: `docker-compose.yml`** (in secret_network_mcp folder):
```yaml
services:
  secret-network-mcp:
    build: .
    ports:
      - "8002:8002"
    environment:
      - PORT=8002
      - SECRET_NODE_URL=https://api.secret.network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8002/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

**File: `Dockerfile`** (in secret_network_mcp folder):
```dockerfile
FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY . .

# Build TypeScript
RUN npm run build

# Expose port
EXPOSE 8002

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8002/api/health || exit 1

# Start server
CMD ["npm", "start"]
```

## GitHub Actions Strategy - Independent Image Builds

### Two Separate Repositories = Two Independent Pipelines

**Repository 1**: `secretGPT` (existing)
- **Image**: `ghcr.io/[org]/secretgpt:latest`
- **Pipeline**: `.github/workflows/build.yml`
- **Independence**: Builds regardless of MCP status

**Repository 2**: `secret_network_mcp` (new)
- **Image**: `ghcr.io/[org]/secret_network_mcp:latest` 
- **Pipeline**: `.github/workflows/build.yml`
- **Independence**: Builds regardless of hub status

### Completely Independent Build Process

**Hub Image Build** (secretGPT repo):
```yaml
name: Build secretGPT Hub
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build-hub:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout secretGPT
        uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Run tests
        run: pytest tests/
      
      - name: Build Docker image
        run: |
          docker build -t ghcr.io/${{ github.repository_owner }}/secretgpt:${{ github.sha }} .
          docker tag ghcr.io/${{ github.repository_owner }}/secretgpt:${{ github.sha }} ghcr.io/${{ github.repository_owner }}/secretgpt:latest
      
      - name: Push to GHCR
        run: |
          echo ${{ secrets.GITHUB_TOKEN }} | docker login ghcr.io -u ${{ github.actor }} --password-stdin
          docker push ghcr.io/${{ github.repository_owner }}/secretgpt:${{ github.sha }}
          docker push ghcr.io/${{ github.repository_owner }}/secretgpt:latest
```

**MCP Image Build** (secret_network_mcp repo):
```yaml
name: Build Secret Network MCP
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build-mcp:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout secret_network_mcp
        uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Build TypeScript
        run: npm run build
      
      - name: Run tests
        run: npm test
      
      - name: Build Docker image
        run: |
          docker build -t ghcr.io/${{ github.repository_owner }}/secret_network_mcp:${{ github.sha }} .
          docker tag ghcr.io/${{ github.repository_owner }}/secret_network_mcp:${{ github.sha }} ghcr.io/${{ github.repository_owner }}/secret_network_mcp:latest
      
      - name: Push to GHCR
        run: |
          echo ${{ secrets.GITHUB_TOKEN }} | docker login ghcr.io -u ${{ github.actor }} --password-stdin
          docker push ghcr.io/${{ github.repository_owner }}/secret_network_mcp:${{ github.sha }}
          docker push ghcr.io/${{ github.repository_owner }}/secret_network_mcp:latest
```

### Key Benefits of This Approach:

**✅ Complete Independence**: 
- Hub can build and deploy even if MCP repo is broken
- MCP can build and deploy even if Hub repo is broken
- No shared dependencies or cross-repository triggers

**✅ Parallel Development**:
- Teams can work on different repos simultaneously
- Different release schedules for each component
- Independent versioning and tagging

**✅ Fault Isolation**:
- Build failure in one repo doesn't block the other
- Deploy issues in one VM don't affect the other
- Rollback can be done independently

**✅ Clear Ownership**:
- Each repository owns its own build process
- No complex multi-repo orchestration
- Simple troubleshooting when builds fail

### Deployment Strategy:

**VM 1 Deployment** (Hub):
```yaml
# docker-compose.yml for Hub VM
services:
  secretgpt-hub:
    image: ghcr.io/[org]/secretgpt:latest
    ports:
      - "8000:8000"  # attestai.io
    environment:
      - SECRET_MCP_URL=http://[MCP_VM_IP]:8002
```

**VM 2 Deployment** (MCP):
```yaml
# docker-compose.yml for MCP VM  
services:
  secret-network-mcp:
    image: ghcr.io/[org]/secret_network_mcp:latest
    ports:
      - "8002:8002"
    environment:
      - PORT=8002
```

### No Cross-Dependencies:
- Each image builds from its own repository
- Each image can be deployed independently
- Each image has its own version lifecycle
- Updates to one don't require rebuilding the other

## Testing Strategy

### Test with existing attestai.io:
1. **Deploy both images** to separate VMs
2. **Configure hub** to point to external MCP server
3. **Verify all existing Secret Network tools** work through HTTP API
4. **No frontend changes needed** - attestai.io should work unchanged

## What Claude Code Needs

### Critical files to reference:
1. **`F:\coding\secretGPT\services\secret_ai\client.py`**
   - Copy the HTTP client pattern exactly
   - Use same authentication approach
   - Copy error handling and retry logic

2. **`F:\coding\secretGPT\mcp_servers\secret_network\src\`**
   - Copy all existing MCP tools unchanged
   - Maintain current tool structure and interfaces
   - Keep existing dependencies

3. **`F:\coding\secretGPT\services\mcp_service\mcp_service.py`**
   - Understand current stdio communication
   - Replace subprocess calls with HTTP requests
   - Maintain same interface for hub router

### Key patterns to follow:
- **HTTP Client**: Copy from SecretAI service
- **Configuration**: Copy from SecretAI settings pattern
- **Error Handling**: Copy from SecretAI error patterns
- **Logging**: Use same logging format as existing code

## Success Criteria

### Functional Requirements:
- [ ] New `secret_network_mcp` repository created
- [ ] All existing Secret Network tools moved and working
- [ ] HTTP API server responds to tool requests
- [ ] Hub successfully communicates with external MCP server
- [ ] Docker image builds via GitHub Actions
- [ ] attestai.io works unchanged with new architecture

### Technical Requirements:
- [ ] No breaking changes to existing Secret Network tool functionality
- [ ] Same input/output format for all tools
- [ ] Proper error handling and logging
- [ ] Health check endpoints working
- [ ] Clean separation between hub and MCP server

## Implementation Timeline

### Week 1: Repository Setup
- [ ] Create new repository
- [ ] Copy existing MCP code
- [ ] Add basic HTTP server
- [ ] Update package.json

### Week 2: Hub Integration  
- [ ] Modify MCP service to use HTTP client
- [ ] Copy SecretAI communication patterns
- [ ] Add configuration management
- [ ] Test basic communication

### Week 3: Docker & CI/CD
- [ ] Create Dockerfile and docker-compose
- [ ] Set up GitHub Actions pipeline
- [ ] Test image building and deployment
- [ ] End-to-end testing with attestai.io

This focused approach gets the core architecture working before adding complexity like wallets and new frontends.