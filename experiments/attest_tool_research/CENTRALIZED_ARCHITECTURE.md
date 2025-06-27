# Centralized Attestation Service - Architecture Specification

## 🎯 **Project Overview**

Build a **single centralized attestation service** that manages TDX attestation for multiple VMs (secretAI, secretGPT, and future VMs) through a unified API interface.

## 🏗️ **Architecture Design**

### **System Architecture**
```
┌─────────────────────────────────────────────────────────────┐
│                Centralized Attestation Service             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │            Attestation Hub Service                  │   │
│  │  • Multi-VM management                              │   │
│  │  • Unified REST API interface                       │   │
│  │  • Configuration-driven VM discovery                │   │
│  │  • Caching & performance optimization               │   │
│  │  • Monitoring & logging                             │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                                │
                    ┌───────────┼───────────┐
                    │           │           │
            ┌───────▼──┐ ┌──────▼──┐ ┌─────▼─────┐
            │secretAI  │ │secretGPT│ │ Future VM │
            │   VM     │ │   VM    │ │     X     │
            └──────────┘ └─────────┘ └───────────┘
```

### **Deployment Model**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   secretAI VM   │    │ AttestationHub  │    │  secretGPT VM   │
│                 │    │    Service      │    │                 │
│ [HTTP Client]───┼────┤ Port 8080       ├────┼───[HTTP Client] │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📁 **Project Structure**

### **Directory Layout**
```
F:\coding\secretGPT\services\attestation_hub\
├── main.py                     # Main service entry point
├── requirements.txt            # Python dependencies
├── config\
│   ├── settings.py            # Service configuration
│   ├── vm_configs.yaml        # VM endpoint configurations
│   └── logging.yaml           # Logging configuration
├── hub\
│   ├── __init__.py
│   ├── service.py             # Core hub service logic
│   ├── vm_manager.py          # VM configuration management
│   └── models.py              # Data models and types
├── parsers\
│   ├── __init__.py
│   ├── base.py                # Base parser interface
│   ├── rest_server.py         # secret-vm-attest-rest-server integration
│   ├── hardcoded.py           # Fallback hardcoded parsing
│   └── dcap.py                # Future Intel DCAP integration
├── api\
│   ├── __init__.py
│   ├── routes.py              # REST API endpoints
│   ├── middleware.py          # Request/response middleware
│   └── schemas.py             # API request/response schemas
├── clients\
│   ├── __init__.py
│   ├── hub_client.py          # Client library for other services
│   └── async_client.py        # Async client implementation
├── utils\
│   ├── __init__.py
│   ├── cache.py               # Caching implementation
│   ├── monitoring.py          # Metrics and health checks
│   └── errors.py              # Custom exceptions
└── tests\
    ├── __init__.py
    ├── test_service.py         # Service integration tests
    ├── test_parsers.py         # Parser unit tests
    ├── test_api.py             # API endpoint tests
    └── fixtures\
        ├── vm_configs.yaml     # Test VM configurations
        └── sample_quotes.json  # Test attestation data
```

## 🔧 **Core Components**

### **1. Hub Service (`hub/service.py`)**
**Primary orchestration logic for multi-VM attestation**

**Key Classes:**
- `AttestationHub` - Main service coordinator
- `VMRegistry` - Manages VM configurations
- `AttestationCache` - TTL-based result caching

**Key Methods:**
- `get_attestation(vm_name: str) -> AttestationData`
- `get_dual_attestation() -> Dict[str, AttestationData]`
- `get_all_attestations() -> Dict[str, AttestationData]`
- `add_vm_config(vm_name: str, config: VMConfig)`
- `health_check() -> ServiceStatus`

### **2. VM Manager (`hub/vm_manager.py`)**
**Configuration-driven VM discovery and management**

**Key Classes:**
- `VMConfig` - VM configuration data model
- `VMManager` - VM lifecycle management
- `EndpointDiscovery` - Dynamic VM endpoint discovery

**Key Methods:**
- `load_vm_configs(config_file: str)`
- `register_vm(vm_name: str, config: VMConfig)`
- `get_vm_config(vm_name: str) -> VMConfig`
- `discover_vm_endpoints() -> List[VMConfig]`

### **3. Parser Strategy (`parsers/`)**
**Pluggable parsing strategies for different VM types**

**Base Interface (`parsers/base.py`):**
- `BaseParser` - Abstract parser interface
- `ParserFactory` - Parser strategy selection
- `ParseResult` - Standardized output format

**Parser Implementations:**
- `RestServerParser` - secret-vm-attest-rest-server integration
- `HardcodedParser` - Fallback byte-offset parsing
- `DCAPParser` - Future Intel DCAP integration

### **4. REST API (`api/routes.py`)**
**Unified REST interface for attestation requests**

**API Endpoints:**
```http
GET  /health                          # Service health check
GET  /attestation/{vm_name}           # Single VM attestation
GET  /attestation/dual                # secretAI + secretGPT
GET  /attestation/all                 # All configured VMs
POST /attestation/batch               # Multiple specific VMs
GET  /vms                             # List configured VMs
POST /vms/{vm_name}/config            # Add/update VM config
GET  /metrics                         # Performance metrics
```

### **5. Client Library (`clients/hub_client.py`)**
**Lightweight client for other services to consume attestations**

**Key Classes:**
- `AttestationHubClient` - Main client interface
- `AsyncAttestationClient` - Async client for high-performance
- `ClientConfig` - Client configuration

**Integration Examples:**
```python
# secretGPT service integration
client = AttestationHubClient("http://attestation-hub:8080")
attestation = await client.get_attestation("secretgpt")

# secretAI service integration  
attestation = await client.get_attestation("secretai")

# Dual attestation for verification
dual = await client.get_dual_attestation()
```

## ⚙️ **Configuration Specifications**

### **VM Configuration (`config/vm_configs.yaml`)**
```yaml
service:
  host: "0.0.0.0"
  port: 8080
  workers: 4
  timeout: 30
  
cache:
  ttl: 300  # 5 minutes
  max_size: 1000
  
monitoring:
  metrics_enabled: true
  health_check_interval: 30
  log_level: "INFO"

vms:
  secretai:
    endpoint: "https://secretai.scrtlabs.com:29343"
    type: "secret-ai"
    parsing_strategy: "rest_server"
    timeout: 30
    retry_attempts: 3
    fallback_strategy: "none"
    health_check_path: "/status"
    
  secretgpt:
    endpoint: "https://localhost:29343"
    type: "secret-gpt" 
    parsing_strategy: "rest_server"
    timeout: 30
    retry_attempts: 3
    fallback_strategy: "hardcoded"
    health_check_path: "/status"
    
  # Future VM template
  future_vm_template:
    endpoint: "https://future-vm:29343"
    type: "custom"
    parsing_strategy: "dcap"
    timeout: 60
    retry_attempts: 2
    fallback_strategy: "rest_server"
    health_check_path: "/status"
```

### **Service Configuration (`config/settings.py`)**
```python
# Configuration data models and validation
@dataclass
class ServiceConfig:
    host: str = "0.0.0.0"
    port: int = 8080
    workers: int = 4
    timeout: int = 30

@dataclass  
class VMConfig:
    endpoint: str
    type: str
    parsing_strategy: str
    timeout: int = 30
    retry_attempts: int = 3
    fallback_strategy: Optional[str] = None
    health_check_path: str = "/status"

@dataclass
class CacheConfig:
    ttl: int = 300
    max_size: int = 1000
```

## 📊 **Data Models**

### **Attestation Data Models (`hub/models.py`)**
```python
@dataclass
class AttestationData:
    vm_name: str
    vm_type: str
    mrtd: str
    rtmr0: str
    rtmr1: str
    rtmr2: str
    rtmr3: str
    report_data: str
    certificate_fingerprint: str
    timestamp: datetime
    raw_quote: str
    parsing_method: str

@dataclass
class DualAttestationData:
    secretai: AttestationData
    secretgpt: AttestationData
    timestamp: datetime
    correlation_id: str

@dataclass
class ServiceStatus:
    status: str  # "healthy", "degraded", "unhealthy"
    vms_online: int
    vms_total: int
    cache_hit_rate: float
    uptime_seconds: int
    version: str
```

### **API Schemas (`api/schemas.py`)**
```python
# Pydantic schemas for API validation
class AttestationResponse(BaseModel):
    success: bool
    data: AttestationData
    errors: List[str] = []

class DualAttestationResponse(BaseModel):
    success: bool
    data: DualAttestationData
    errors: List[str] = []

class BatchAttestationRequest(BaseModel):
    vm_names: List[str]
    correlation_id: Optional[str] = None

class VMConfigRequest(BaseModel):
    endpoint: str
    type: str
    parsing_strategy: str
    timeout: int = 30
```

## 🔄 **Integration Patterns**

### **secretGPT Integration**
**Replace existing AttestationService with hub client:**
```python
# Current: Direct parsing in secretGPT
# New: Hub client integration

class AttestationService:
    def __init__(self):
        self.hub_client = AttestationHubClient(
            base_url=settings.ATTESTATION_HUB_URL,
            timeout=30
        )
    
    async def get_self_attestation(self):
        """Get secretGPT VM attestation via hub"""
        return await self.hub_client.get_attestation("secretgpt")
    
    async def get_secret_ai_attestation(self):
        """Get secretAI VM attestation via hub"""
        return await self.hub_client.get_attestation("secretai")
    
    async def get_dual_attestation(self):
        """Get both attestations via hub"""
        return await self.hub_client.get_dual_attestation()
```

### **secretAI Integration**
**Lightweight client for attestation requests:**
```python
class SecretAIAttestationClient:
    def __init__(self):
        self.hub_client = AttestationHubClient(
            base_url=os.getenv("ATTESTATION_HUB_URL"),
            timeout=30
        )
    
    async def get_self_attestation(self):
        return await self.hub_client.get_attestation("secretai")
```

## 🧪 **Testing Strategy**

### **Unit Tests**
- **Parser Tests** - Validate each parsing strategy
- **VM Manager Tests** - Configuration loading and validation
- **Cache Tests** - TTL and eviction behavior
- **API Tests** - Endpoint request/response validation

### **Integration Tests**
- **End-to-End** - Full attestation flow for each VM
- **Multi-VM** - Concurrent attestation requests
- **Fallback** - Parser strategy fallback behavior
- **Performance** - Load testing with multiple VMs

### **Test Data**
- **Baseline Quotes** - Your production attestation data
- **Mock Responses** - Simulated REST server responses
- **Error Cases** - Invalid quotes, timeouts, failures

## 🚀 **Deployment Requirements**

### **Dependencies (`requirements.txt`)**
```txt
fastapi>=0.104.0
uvicorn>=0.24.0
httpx>=0.25.0
pydantic>=2.4.0
pyyaml>=6.0.1
redis>=5.0.0  # For distributed caching
prometheus-client>=0.19.0  # For metrics
structlog>=23.2.0  # For structured logging
```

### **Environment Variables**
```bash
ATTESTATION_HUB_HOST=0.0.0.0
ATTESTATION_HUB_PORT=8080
ATTESTATION_HUB_WORKERS=4
VM_CONFIG_PATH=/app/config/vm_configs.yaml
CACHE_TTL=300
LOG_LEVEL=INFO
REDIS_URL=redis://localhost:6379  # Optional distributed cache
```

### **Docker Configuration**
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8080

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
```

## 📋 **Implementation Phases**

### **Phase 1: Core Service (Week 1)**
1. **Hub Service** - Basic AttestationHub class
2. **VM Manager** - Configuration loading and VM registry  
3. **REST Server Parser** - Integration with secret-vm-attest-rest-server
4. **Basic API** - Single VM attestation endpoint

### **Phase 2: Multi-VM Support (Week 2)**
1. **Dual Attestation** - secretAI + secretGPT endpoint
2. **Batch Attestation** - Multiple VM support
3. **Fallback Parsing** - Hardcoded parser integration
4. **Caching** - TTL-based result caching

### **Phase 3: Production Ready (Week 3)**
1. **Client Library** - Hub client for service integration
2. **Monitoring** - Health checks and metrics
3. **Testing** - Comprehensive test suite
4. **Documentation** - API docs and deployment guide

### **Phase 4: Integration (Week 4)**
1. **secretGPT Migration** - Replace existing AttestationService
2. **secretAI Integration** - Add hub client
3. **Performance Testing** - Load testing and optimization
4. **Production Deployment** - Staged rollout

## 🎯 **Success Criteria**

### **Functional Requirements**
- ✅ **Multi-VM Support** - Handle secretAI and secretGPT attestations
- ✅ **API Compatibility** - Maintain existing attestation interfaces
- ✅ **Fallback Strategy** - Graceful degradation when parsers fail
- ✅ **Configuration Driven** - Easy addition of new VMs

### **Performance Requirements**
- ✅ **Response Time** - < 10 seconds per attestation
- ✅ **Concurrent Requests** - Handle 50+ simultaneous requests
- ✅ **Cache Hit Rate** - > 80% for repeated requests
- ✅ **Uptime** - > 99.5% availability

### **Scalability Requirements**
- ✅ **New VM Addition** - Add VMs via configuration only
- ✅ **Horizontal Scaling** - Support multiple hub instances
- ✅ **Load Distribution** - Handle increasing VM count
- ✅ **Future Proof** - Easy integration of new parsing strategies

## 🛡️ **Security & Reliability**

### **Security Measures**
- **TLS Verification** - Secure communication with VMs
- **Input Validation** - Sanitize all API inputs
- **Rate Limiting** - Prevent abuse and DoS
- **Access Control** - API key or token-based auth

### **Reliability Features**
- **Circuit Breaker** - Prevent cascading failures
- **Retry Logic** - Automatic retry with backoff
- **Health Monitoring** - Continuous VM health checks
- **Graceful Degradation** - Fallback when VMs unavailable

---

**Status**: ✅ **ARCHITECTURE COMPLETE - READY FOR IMPLEMENTATION**

This specification provides everything needed to build the centralized attestation service using the proven patterns from your research, with proper scalability for future VM additions.
