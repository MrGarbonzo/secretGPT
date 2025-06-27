# Implementation Guide for Claude Code

## 🎯 **Project Briefing**

**Objective**: Build a centralized attestation service that manages TDX attestation for multiple VMs (secretAI, secretGPT, and future VMs) through a unified REST API interface.

**Current Problem**: secretGPT uses hardcoded byte-offset parsing for TDX attestation quotes. Need to replace with specification-compliant parsing using Secret Labs tools while supporting multiple VMs.

**Solution**: Single centralized service that orchestrates attestation for all VMs with fallback strategies.

## 📁 **Implementation Location**

**Create new service at**: `F:\coding\secretGPT\services\attestation_hub\`

## 🏗️ **Architecture Reference**

Review these files for complete specifications:
- `CENTRALIZED_ARCHITECTURE.md` - Complete system design
- `VM_CONFIGURATION_SPEC.md` - Configuration examples and templates
- `findings/current_parser_baseline.json` - Baseline parsing results
- `prototype/enhanced_attestation_service.py` - Reference implementation pattern

## 🔧 **Core Implementation Requirements**

### **1. Project Structure**
```
F:\coding\secretGPT\services\attestation_hub\
├── main.py                     # FastAPI service entry point
├── requirements.txt            # Dependencies
├── config\
│   ├── settings.py            # Configuration management
│   ├── vm_configs.yaml        # VM definitions
│   └── logging.yaml           # Logging setup
├── hub\
│   ├── service.py             # Core AttestationHub class
│   ├── vm_manager.py          # VM configuration management
│   └── models.py              # Data models
├── parsers\
│   ├── base.py                # Parser interface
│   ├── rest_server.py         # secret-vm-attest-rest-server integration
│   ├── hardcoded.py           # Fallback byte-offset parsing
│   └── dcap.py                # Future Intel DCAP
├── api\
│   ├── routes.py              # REST endpoints
│   └── schemas.py             # Pydantic schemas
├── clients\
│   └── hub_client.py          # Client library for other services
└── tests\
    ├── test_service.py         # Integration tests
    └── test_parsers.py         # Parser tests
```

### **2. Key Classes to Implement**

#### **AttestationHub (`hub/service.py`)**
```python
class AttestationHub:
    """Main orchestration service for multi-VM attestation"""
    
    async def get_attestation(self, vm_name: str) -> AttestationData:
        """Get attestation for specific VM"""
        
    async def get_dual_attestation(self) -> DualAttestationData:
        """Get secretAI + secretGPT attestations"""
        
    async def get_all_attestations(self) -> Dict[str, AttestationData]:
        """Get attestations for all configured VMs"""
```

#### **VMManager (`hub/vm_manager.py`)**
```python
class VMManager:
    """Configuration-driven VM discovery and management"""
    
    def load_vm_configs(self, config_file: str):
        """Load VM configurations from YAML"""
        
    def get_vm_config(self, vm_name: str) -> VMConfig:
        """Get configuration for specific VM"""
```

#### **BaseParser (`parsers/base.py`)**
```python
class BaseParser:
    """Abstract parser interface for different strategies"""
    
    async def parse_attestation(self, quote: str, vm_config: VMConfig) -> AttestationData:
        """Parse attestation quote using specific strategy"""
```

#### **RestServerParser (`parsers/rest_server.py`)**
```python
class RestServerParser(BaseParser):
    """Parser using secret-vm-attest-rest-server endpoints"""
    
    async def parse_attestation(self, quote: str, vm_config: VMConfig) -> AttestationData:
        """Use /cpu, /attestation, or /self endpoints"""
```

#### **HardcodedParser (`parsers/hardcoded.py`)**
```python
class HardcodedParser(BaseParser):
    """Fallback parser using byte offsets (current secretGPT method)"""
    
    async def parse_attestation(self, quote: str, vm_config: VMConfig) -> AttestationData:
        """Extract using hardcoded byte positions"""
```

### **3. API Endpoints (`api/routes.py`)**

**Required endpoints:**
```python
@app.get("/health")
async def health_check():
    """Service health status"""

@app.get("/attestation/{vm_name}")  
async def get_vm_attestation(vm_name: str):
    """Single VM attestation"""

@app.get("/attestation/dual")
async def get_dual_attestation():
    """secretAI + secretGPT attestations"""

@app.get("/attestation/all")
async def get_all_attestations():
    """All configured VM attestations"""

@app.post("/attestation/batch")
async def get_batch_attestations(request: BatchAttestationRequest):
    """Multiple specific VMs"""

@app.get("/vms")
async def list_vms():
    """List configured VMs"""

@app.post("/vms/{vm_name}/config")
async def add_vm_config(vm_name: str, config: VMConfigRequest):
    """Add/update VM configuration"""
```

### **4. Data Models (`hub/models.py`)**

**Use these exact data structures:**
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
class VMConfig:
    endpoint: str
    type: str
    parsing_strategy: str
    timeout: int = 30
    retry_attempts: int = 3
    fallback_strategy: Optional[str] = None
    tls_verify: bool = False
```

### **5. Client Library (`clients/hub_client.py`)**
```python
class AttestationHubClient:
    """Lightweight client for other services"""
    
    def __init__(self, base_url: str, timeout: int = 30):
        """Initialize client with hub URL"""
        
    async def get_attestation(self, vm_name: str) -> AttestationData:
        """Get attestation for specific VM"""
        
    async def get_dual_attestation(self) -> DualAttestationData:
        """Get dual attestation"""
```

## 📊 **Configuration Implementation**

### **VM Configuration (`config/vm_configs.yaml`)**
```yaml
vms:
  secretai:
    endpoint: "https://secretai.scrtlabs.com:29343"
    type: "secret-ai"
    parsing_strategy: "rest_server"
    timeout: 30
    
  secretgpt:
    endpoint: "https://localhost:29343"
    type: "secret-gpt"
    parsing_strategy: "rest_server"
    fallback_strategy: "hardcoded"
```

### **Dependencies (`requirements.txt`)**
```txt
fastapi>=0.104.0
uvicorn>=0.24.0
httpx>=0.25.0
pydantic>=2.4.0
pyyaml>=6.0.1
structlog>=23.2.0
```

## 🧪 **Testing Requirements**

### **Essential Tests**
1. **Parser Tests** - Validate each parsing strategy with baseline data
2. **VM Manager Tests** - Configuration loading and validation
3. **API Tests** - All endpoint functionality
4. **Integration Tests** - End-to-end attestation flow

### **Test Data**
- Use `sample_data/known_good_quote.hex` for testing
- Compare results against `findings/current_parser_baseline.json`
- Test error scenarios with invalid quotes

## 🔄 **Integration Patterns**

### **Current secretGPT Integration**
**Replace this pattern:**
```python
# OLD: Direct parsing in secretGPT
attestation_data = self._parse_attestation_quote(quote, cert, vm_type)
```

**With this pattern:**
```python
# NEW: Hub client integration
hub_client = AttestationHubClient("http://localhost:8080")
attestation_data = await hub_client.get_attestation("secretgpt")
```

## 🛡️ **Error Handling Requirements**

### **Parser Fallback Chain**
1. **Primary**: Try configured parsing_strategy
2. **Fallback**: Try fallback_strategy if primary fails
3. **Final**: Return error if all strategies fail

### **VM Health Monitoring**
- Health check endpoints for each VM
- Circuit breaker pattern for failed VMs
- Graceful degradation when VMs unavailable

## 📋 **Implementation Phases**

### **Phase 1: Core Service**
1. Basic AttestationHub class
2. VM configuration loading
3. RestServerParser implementation
4. Single VM attestation endpoint

### **Phase 2: Multi-VM Support**
1. Dual attestation endpoint
2. Batch attestation support
3. HardcodedParser implementation
4. Fallback strategy logic

### **Phase 3: Production Ready**
1. Client library implementation
2. Comprehensive error handling
3. Health monitoring
4. Complete test suite

### **Phase 4: Integration**
1. secretGPT service integration
2. secretAI service integration
3. Performance testing
4. Documentation

## 🎯 **Validation Criteria**

### **Functional Validation**
- ✅ Parse secretGPT attestation matching baseline values
- ✅ Parse secretAI attestation successfully  
- ✅ Handle dual attestation requests
- ✅ Fallback to hardcoded parsing when REST fails

### **Performance Validation**
- ✅ Response time < 10 seconds per attestation
- ✅ Handle 50+ concurrent requests
- ✅ Cache hit rate > 80%

### **Integration Validation**
- ✅ secretGPT can replace current AttestationService
- ✅ Client library works for other services
- ✅ Configuration-driven VM addition works

## 🔧 **Development Environment Setup**

### **Local Development**
```bash
cd F:\coding\secretGPT\services\attestation_hub
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8080 --reload
```

### **Testing**
```bash
pytest tests/ -v
python -m pytest tests/test_parsers.py -v
```

## 📚 **Reference Materials**

### **Use these files for reference:**
- `prototype/enhanced_attestation_service.py` - Working parser implementation
- `findings/current_parser_baseline.json` - Expected output values
- `sample_data/known_good_quote.hex` - Test data
- `CENTRALIZED_ARCHITECTURE.md` - Complete system design

### **Current secretGPT AttestationService**
- Location: `secretGPT/interfaces/web_ui/attestation/service.py`
- Study current `_parse_attestation_quote()` method for hardcoded parsing
- Maintain compatibility with existing `AttestationData` structure

## 🚀 **Success Metrics**

**Project is successful when:**
1. ✅ **Hub service** runs on port 8080 and responds to health checks
2. ✅ **Dual attestation** returns both secretAI and secretGPT data  
3. ✅ **Parsing accuracy** matches baseline values from current system
4. ✅ **Fallback strategy** works when REST server unavailable
5. ✅ **Client integration** allows secretGPT to use hub instead of direct parsing
6. ✅ **New VM addition** works through configuration only

---

**Status**: ✅ **READY FOR CLAUDE CODE IMPLEMENTATION**

This guide provides everything needed to implement the centralized attestation service using the proven patterns from the research phase.
