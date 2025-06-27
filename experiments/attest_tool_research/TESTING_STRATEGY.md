# Testing Strategy and Test Data Specification

## 🧪 **Comprehensive Testing Strategy**

This document outlines the complete testing approach for the centralized attestation service, including test data, validation criteria, and automated test suites.

## 📊 **Test Data Repository**

### **Baseline Test Data**
- **Source**: `sample_data/known_good_quote.hex` - Your production attestation quote
- **Baseline**: `findings/current_parser_baseline.json` - Expected parsing results
- **Length**: 10,020 characters (5,010 bytes)
- **Format**: Intel TDX attestation quote in hex format

### **Expected Baseline Values**
```json
{
  "mrtd": "ba87a347454466680bfd267446df89d8117c04ea9f28234dd3d84e1a8a957d5adaf02d4aa88433b559fb13bd40f0109e",
  "rtmr0": "4bf33b719bd369f3653fcfb0a4d452fe680cac95a3f2f1c4a871e229daca07bf49dd7f7c171f9b7a7971afd52848d79c",
  "rtmr1": "8ad5a890c47b2d5a8a1aa9db240547d8e104c2832a7c127bdac288cdcbac01783493c8ef5a40f4dff840f5c3b568781b",
  "rtmr2": "7724bd8d7167267fb35c030bd60fd9911254629e569c58a152b415f35d945dd1beebe2eafdeb653a969b56c36a4011fc",
  "rtmr3": "056cae9f6b4ccb3bf3087d2c22549e96ab4c7d2d415d7ec3d467db7131bffabb974a94a3e0596f46c64a53d16e353401",
  "report_data": "5b38e33a6487958b72c3c12a938eaa5e3fd4510c51aeeab58c7d5ecee41d7c43"
}
```

### **Error Test Cases**
- **Empty Quote**: `sample_data/empty_quote.hex` - Empty file
- **Invalid Hex**: `sample_data/invalid_quote.hex` - Non-hex characters
- **Truncated Quote**: `sample_data/truncated_quote.hex` - Incomplete quote (1000 chars)

## 🔍 **Unit Test Specifications**

### **1. Parser Unit Tests (`tests/test_parsers.py`)**

#### **RestServerParser Tests**
```python
class TestRestServerParser:
    """Test secret-vm-attest-rest-server integration"""
    
    async def test_parse_with_cpu_endpoint(self):
        """Test parsing using /cpu endpoint"""
        # Mock successful REST response
        # Validate AttestationData output
        # Compare with baseline values
        
    async def test_parse_with_attestation_endpoint(self):
        """Test parsing using /attestation endpoint"""
        
    async def test_parse_with_timeout(self):
        """Test timeout handling"""
        
    async def test_parse_with_invalid_response(self):
        """Test handling of invalid JSON responses"""
```

#### **HardcodedParser Tests**
```python
class TestHardcodedParser:
    """Test byte-offset parsing (fallback method)"""
    
    async def test_parse_baseline_quote(self):
        """Test parsing with known good quote"""
        parser = HardcodedParser()
        result = await parser.parse_attestation(baseline_quote, vm_config)
        
        # Validate all fields match baseline
        assert result.mrtd == baseline['mrtd']
        assert result.rtmr0 == baseline['rtmr0']
        # ... validate all fields
        
    async def test_parse_truncated_quote(self):
        """Test error handling with truncated quote"""
        
    async def test_parse_empty_quote(self):
        """Test error handling with empty quote"""
```

#### **Parser Factory Tests**
```python
class TestParserFactory:
    """Test parser strategy selection"""
    
    def test_get_rest_server_parser(self):
        """Test creation of RestServerParser"""
        
    def test_get_hardcoded_parser(self):
        """Test creation of HardcodedParser"""
        
    def test_fallback_strategy(self):
        """Test fallback parser selection"""
```

### **2. VM Manager Tests (`tests/test_vm_manager.py`)**

#### **Configuration Loading Tests**
```python
class TestVMManager:
    """Test VM configuration management"""
    
    def test_load_vm_configs(self):
        """Test YAML configuration loading"""
        manager = VMManager()
        manager.load_vm_configs('test_vm_configs.yaml')
        
        # Validate secretai config
        secretai_config = manager.get_vm_config('secretai')
        assert secretai_config.endpoint == "https://secretai.scrtlabs.com:29343"
        assert secretai_config.parsing_strategy == "rest_server"
        
    def test_invalid_config_validation(self):
        """Test validation of invalid configurations"""
        
    def test_add_vm_config_runtime(self):
        """Test adding VM config at runtime"""
```

### **3. Hub Service Tests (`tests/test_service.py`)**

#### **Core Service Tests**
```python
class TestAttestationHub:
    """Test main hub service functionality"""
    
    async def test_get_single_attestation(self):
        """Test single VM attestation"""
        hub = AttestationHub()
        result = await hub.get_attestation('secretgpt')
        
        # Validate result structure
        assert isinstance(result, AttestationData)
        assert result.vm_name == 'secretgpt'
        assert len(result.mrtd) == 96  # 48 bytes hex
        
    async def test_get_dual_attestation(self):
        """Test dual VM attestation"""
        hub = AttestationHub()
        result = await hub.get_dual_attestation()
        
        # Validate both VMs present
        assert 'secretai' in result
        assert 'secretgpt' in result
        
    async def test_fallback_strategy(self):
        """Test parser fallback behavior"""
        # Mock REST server failure
        # Validate fallback to hardcoded parsing
        
    async def test_caching_behavior(self):
        """Test TTL-based caching"""
        # First request should hit VM
        # Second request should use cache
        # Expired cache should hit VM again
```

## 🔗 **Integration Test Specifications**

### **4. API Integration Tests (`tests/test_api.py`)**

#### **Endpoint Tests**
```python
class TestAPIEndpoints:
    """Test REST API endpoints"""
    
    async def test_health_endpoint(self):
        """Test /health endpoint"""
        response = await client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
        
    async def test_single_attestation_endpoint(self):
        """Test /attestation/{vm_name} endpoint"""
        response = await client.get("/attestation/secretgpt")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "mrtd" in data["data"]
        
    async def test_dual_attestation_endpoint(self):
        """Test /attestation/dual endpoint"""
        response = await client.get("/attestation/dual")
        assert response.status_code == 200
        
        data = response.json()
        assert "secretai" in data["data"]
        assert "secretgpt" in data["data"]
        
    async def test_batch_attestation_endpoint(self):
        """Test /attestation/batch endpoint"""
        request_data = {"vm_names": ["secretai", "secretgpt"]}
        response = await client.post("/attestation/batch", json=request_data)
        assert response.status_code == 200
        
    async def test_vm_config_endpoints(self):
        """Test VM configuration management"""
        # Test listing VMs
        response = await client.get("/vms")
        assert response.status_code == 200
        
        # Test adding VM config
        new_vm_config = {
            "endpoint": "https://test-vm:29343",
            "type": "test",
            "parsing_strategy": "rest_server"
        }
        response = await client.post("/vms/test_vm/config", json=new_vm_config)
        assert response.status_code == 201
```

### **5. Client Library Tests (`tests/test_client.py`)**

#### **Hub Client Tests**
```python
class TestAttestationHubClient:
    """Test client library functionality"""
    
    async def test_client_initialization(self):
        """Test client setup and configuration"""
        client = AttestationHubClient("http://localhost:8080")
        assert client.base_url == "http://localhost:8080"
        
    async def test_get_attestation(self):
        """Test single attestation via client"""
        client = AttestationHubClient("http://localhost:8080")
        result = await client.get_attestation("secretgpt")
        
        # Validate baseline values
        assert result.mrtd == baseline['mrtd']
        assert result.rtmr0 == baseline['rtmr0']
        
    async def test_get_dual_attestation(self):
        """Test dual attestation via client"""
        
    async def test_error_handling(self):
        """Test client error handling"""
        # Test with invalid VM name
        # Test with server unavailable
        # Test with timeout
```

## 🎯 **Performance Test Specifications**

### **6. Performance Tests (`tests/test_performance.py`)**

#### **Load Testing**
```python
class TestPerformance:
    """Test service performance characteristics"""
    
    async def test_concurrent_requests(self):
        """Test handling 50+ concurrent requests"""
        tasks = []
        for i in range(50):
            task = client.get("/attestation/secretgpt")
            tasks.append(task)
            
        results = await asyncio.gather(*tasks)
        
        # All requests should succeed
        assert all(r.status_code == 200 for r in results)
        
    async def test_response_time(self):
        """Test response time < 10 seconds"""
        start_time = time.time()
        response = await client.get("/attestation/secretgpt")
        end_time = time.time()
        
        assert (end_time - start_time) < 10.0
        assert response.status_code == 200
        
    async def test_cache_performance(self):
        """Test cache hit rate > 80%"""
        # Make 100 requests
        # Monitor cache hits vs misses
        # Validate hit rate > 80%
```

## 🔄 **End-to-End Test Scenarios**

### **7. E2E Tests (`tests/test_e2e.py`)**

#### **Complete Workflow Tests**
```python
class TestEndToEnd:
    """Test complete attestation workflows"""
    
    async def test_secretgpt_integration_workflow(self):
        """Test full secretGPT integration"""
        # 1. Start hub service
        # 2. Configure secretGPT VM
        # 3. Request attestation via client
        # 4. Validate response matches baseline
        # 5. Test fallback scenario
        
    async def test_secretai_integration_workflow(self):
        """Test full secretAI integration"""
        
    async def test_dual_vm_workflow(self):
        """Test dual VM attestation workflow"""
        
    async def test_new_vm_addition_workflow(self):
        """Test adding new VM via configuration"""
        # 1. Add new VM config
        # 2. Request attestation
        # 3. Validate successful parsing
```

## 🛡️ **Error Scenario Testing**

### **8. Error Handling Tests (`tests/test_errors.py`)**

#### **Failure Mode Tests**
```python
class TestErrorHandling:
    """Test error scenarios and recovery"""
    
    async def test_vm_unavailable(self):
        """Test behavior when VM is down"""
        # Mock VM endpoint returning 500/timeout
        # Validate proper error response
        # Test fallback strategy activation
        
    async def test_invalid_quote_data(self):
        """Test handling of malformed quotes"""
        
    async def test_parser_fallback_chain(self):
        """Test complete fallback chain"""
        # 1. Primary parser fails
        # 2. Fallback parser succeeds
        # 3. Validate result accuracy
        
    async def test_circuit_breaker_behavior(self):
        """Test circuit breaker pattern"""
        # Trigger multiple failures
        # Validate circuit opens
        # Test circuit recovery
```

## 📋 **Test Fixtures and Mocks**

### **Test Configuration (`tests/fixtures/test_vm_configs.yaml`)**
```yaml
vms:
  test_secretgpt:
    endpoint: "http://localhost:29343"
    type: "secret-gpt"
    parsing_strategy: "rest_server"
    fallback_strategy: "hardcoded"
    timeout: 10
    
  test_secretai:
    endpoint: "http://localhost:29344"
    type: "secret-ai"
    parsing_strategy: "rest_server"
    timeout: 10
```

### **Mock Responses (`tests/fixtures/mock_responses.json`)**
```json
{
  "rest_server_success": {
    "status_code": 200,
    "content": "040002008100000000000000939a7233...",
    "headers": {"Content-Type": "text/plain"}
  },
  "rest_server_json": {
    "status_code": 200,
    "content": {
      "mrtd": "ba87a347454466680bfd267446df89d8...",
      "rtmr0": "4bf33b719bd369f3653fcfb0a4d452fe...",
      "rtmr1": "8ad5a890c47b2d5a8a1aa9db240547d8..."
    },
    "headers": {"Content-Type": "application/json"}
  }
}
```

## ⚡ **Test Automation**

### **Continuous Testing Setup**
```python
# conftest.py - Pytest configuration
@pytest.fixture
async def hub_service():
    """Fixture for hub service instance"""
    hub = AttestationHub()
    await hub.initialize()
    yield hub
    await hub.cleanup()

@pytest.fixture
def baseline_data():
    """Fixture for baseline test data"""
    with open('findings/current_parser_baseline.json') as f:
        return json.load(f)

@pytest.fixture
def test_quote():
    """Fixture for test attestation quote"""
    with open('sample_data/known_good_quote.hex') as f:
        return f.read().strip()
```

### **Test Commands**
```bash
# Run all tests
pytest tests/ -v

# Run specific test categories
pytest tests/test_parsers.py -v
pytest tests/test_api.py -v
pytest tests/test_performance.py -v

# Run with coverage
pytest tests/ --cov=hub --cov-report=html

# Run integration tests only
pytest tests/test_e2e.py -v
```

## 📊 **Test Success Criteria**

### **Unit Test Criteria**
- ✅ **Parser Accuracy**: All baseline values match exactly
- ✅ **Error Handling**: Graceful handling of all error scenarios
- ✅ **Configuration**: Valid VM config loading and validation
- ✅ **Fallback Strategy**: Proper fallback chain execution

### **Integration Test Criteria**
- ✅ **API Functionality**: All endpoints return correct responses
- ✅ **Client Integration**: Hub client works for other services
- ✅ **Multi-VM Support**: Dual and batch attestations work
- ✅ **Dynamic Configuration**: Runtime VM addition works

### **Performance Test Criteria**
- ✅ **Response Time**: < 10 seconds per attestation
- ✅ **Concurrent Load**: Handle 50+ simultaneous requests
- ✅ **Cache Efficiency**: > 80% cache hit rate for repeated requests
- ✅ **Resource Usage**: Reasonable memory and CPU consumption

### **E2E Test Criteria**
- ✅ **secretGPT Integration**: Complete workflow from current system
- ✅ **secretAI Integration**: Full integration with existing setup
- ✅ **New VM Addition**: Add VM through configuration only
- ✅ **Production Readiness**: Service ready for production deployment

## 🔧 **Test Data Generation**

### **Additional Test Quotes**
```python
# Generate test variations
def create_test_quotes():
    """Create additional test quote variations"""
    base_quote = load_baseline_quote()
    
    return {
        'valid_quote': base_quote,
        'truncated_quote': base_quote[:1000],
        'corrupted_quote': corrupt_random_bytes(base_quote),
        'invalid_hex': 'invalid_hex_data_12345',
        'empty_quote': '',
        'short_quote': '1234567890abcdef'
    }
```

### **Mock VM Endpoints**
```python
# Mock secret-vm-attest-rest-server responses
@pytest.fixture
def mock_vm_server():
    """Mock VM server for testing"""
    with responses.RequestsMock() as rsps:
        # Mock successful response
        rsps.add(responses.GET, 
                'http://localhost:29343/cpu',
                body=load_baseline_quote(),
                status=200)
                
        # Mock status endpoint
        rsps.add(responses.GET,
                'http://localhost:29343/status', 
                json={'status': 'alive'},
                status=200)
                
        yield rsps
```

---

**Status**: ✅ **TESTING STRATEGY COMPLETE**

This comprehensive testing strategy ensures the centralized attestation service meets all functional, performance, and reliability requirements while maintaining compatibility with existing systems.
