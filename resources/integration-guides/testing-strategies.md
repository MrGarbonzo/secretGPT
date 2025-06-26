# Testing Strategy for Intel DCAP Integration

## 🎯 **Testing Goals**

Ensure the Intel DCAP integration correctly replaces hardcoded quote parsing while maintaining system reliability and performance.

## 📋 **Testing Phases**

### **Phase 1: Unit Testing (DCAP Wrapper)**

**Objective:** Validate individual DCAP wrapper functions work correctly

**Test Categories:**

**1. Library Loading Tests**
```python
def test_dcap_library_loading():
    """Test DCAP shared libraries load correctly"""
    wrapper = DCAPWrapper()
    assert wrapper.qv_lib is not None
    assert wrapper.ql_lib is not None

def test_function_prototypes():
    """Test ctypes function prototypes are set up correctly"""
    wrapper = DCAPWrapper()
    # Verify function signatures match expectations
    assert hasattr(wrapper.qv_lib, 'sgx_qv_verify_quote')
    assert hasattr(wrapper.qv_lib, 'sgx_qv_get_quote_supplemental_data_size')
```

**2. Data Structure Tests**
```python
def test_tdx_measurement_structure():
    """Test TDX measurement structure size and conversion"""
    measurement = TDXMeasurement()
    assert ctypes.sizeof(measurement) == 48
    
    # Test hex conversion
    test_bytes = b'\x01\x02\x03' + b'\x00' * 45
    measurement = TDXMeasurement.from_buffer_copy(test_bytes)
    hex_str = measurement.to_hex()
    assert hex_str.startswith('010203')
    assert len(hex_str) == 96  # 48 bytes * 2 hex chars

def test_report_data_structure():
    """Test report data structure and conversion"""
    report_data = TDXReportData()
    assert ctypes.sizeof(report_data) == 64
```

**3. Quote Parsing Tests**
```python
def test_parse_valid_quote():
    """Test parsing a known-good TDX quote"""
    wrapper = DCAPWrapper()
    
    # Use your existing demo quote
    demo_quote = "your_demo_quote_hex_here"
    
    result = wrapper.parse_quote(demo_quote)
    
    # Validate structure
    assert "verification_status" in result
    assert "measurements" in result
    assert "mrtd" in result["measurements"]
    assert "rtmr0" in result["measurements"]
    assert "rtmr1" in result["measurements"]
    assert "rtmr2" in result["measurements"]
    assert "rtmr3" in result["measurements"]
    assert "report_data" in result["measurements"]

def test_parse_invalid_quote():
    """Test error handling with invalid quote data"""
    wrapper = DCAPWrapper()
    
    with pytest.raises(DCAPError):
        wrapper.parse_quote("invalid_hex_data")
    
    with pytest.raises(DCAPError):
        wrapper.parse_quote("1234")  # Too short

def test_measurement_extraction_accuracy():
    """Compare DCAP parsing vs known-good values"""
    wrapper = DCAPWrapper()
    
    # Test with quote where you know the expected values
    test_quote = "your_test_quote_hex"
    expected_mrtd = "expected_mrtd_value"
    
    result = wrapper.parse_quote(test_quote)
    actual_mrtd = result["measurements"]["mrtd"]
    
    assert actual_mrtd == expected_mrtd
```

### **Phase 2: Integration Testing (Service Level)**

**Objective:** Validate DCAP integration works within AttestationService

**Test Categories:**

**1. Service Integration Tests**
```python
def test_attestation_service_with_dcap():
    """Test AttestationService uses DCAP wrapper correctly"""
    service = AttestationService()
    
    # Mock quote extraction
    mock_quote = "your_test_quote_hex"
    mock_cert = "sha256:test_cert_fingerprint"
    
    attestation_data = service._parse_attestation_quote(
        mock_quote, mock_cert, "test_vm"
    )
    
    # Validate AttestationData structure
    assert attestation_data.mrtd != "parse_error_test_vm"
    assert len(attestation_data.mrtd) == 96  # 48 bytes hex
    assert attestation_data.certificate_fingerprint == mock_cert

def test_dual_vm_attestation():
    """Test dual VM attestation workflow"""
    service = AttestationService()
    
    # Mock both VM endpoints
    with patch('service.get_self_attestation') as mock_self, \
         patch('service.get_secret_ai_attestation') as mock_secretai:
        
        mock_self.return_value = {"success": True, "attestation": {...}}
        mock_secretai.return_value = {"success": True, "attestation": {...}}
        
        result = service.get_dual_attestation()
        
        assert result["dual_attestation"] is True
        assert "self_vm" in result
        assert "secret_ai_vm" in result
```

**2. Error Handling Tests**
```python
def test_dcap_failure_fallback():
    """Test graceful handling when DCAP libraries fail"""
    service = AttestationService()
    
    # Simulate DCAP library failure
    with patch.object(service._dcap_wrapper, 'parse_quote') as mock_parse:
        mock_parse.side_effect = DCAPError("Library not available")
        
        attestation_data = service._parse_attestation_quote(
            "test_quote", "test_cert", "test_vm"
        )
        
        # Should return error attestation, not crash
        assert attestation_data.mrtd == "parse_error_test_vm"

def test_memory_cleanup():
    """Test no memory leaks during repeated parsing"""
    service = AttestationService()
    
    import psutil
    import gc
    
    process = psutil.Process()
    initial_memory = process.memory_info().rss
    
    # Parse many quotes
    for _ in range(100):
        service._parse_attestation_quote(
            "test_quote_hex", "test_cert", "test_vm"
        )
    
    gc.collect()
    final_memory = process.memory_info().rss
    
    # Memory increase should be minimal
    memory_increase = final_memory - initial_memory
    assert memory_increase < 50 * 1024 * 1024  # Less than 50MB
```

### **Phase 3: Performance Testing**

**Objective:** Ensure DCAP integration doesn't degrade performance

**Test Categories:**

**1. Latency Tests**
```python
def test_parsing_performance():
    """Compare old vs new parsing performance"""
    import time
    
    # Test current implementation
    start_time = time.time()
    for _ in range(100):
        old_result = old_parse_function("test_quote")
    old_duration = time.time() - start_time
    
    # Test DCAP implementation
    wrapper = DCAPWrapper()
    start_time = time.time()
    for _ in range(100):
        new_result = wrapper.parse_quote("test_quote")
    new_duration = time.time() - start_time
    
    # DCAP should be reasonably fast (allow 2x slower)
    assert new_duration < old_duration * 2

def test_concurrent_parsing():
    """Test performance under concurrent load"""
    import concurrent.futures
    import time
    
    wrapper = DCAPWrapper()
    
    def parse_quote_task():
        return wrapper.parse_quote("test_quote_hex")
    
    start_time = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(parse_quote_task) for _ in range(50)]
        results = [future.result() for future in futures]
    duration = time.time() - start_time
    
    # All tasks should complete successfully
    assert len(results) == 50
    assert all("measurements" in result for result in results)
    
    # Should complete within reasonable time
    assert duration < 30  # 30 seconds for 50 concurrent parses
```

**2. Resource Usage Tests**
```python
def test_memory_usage():
    """Test memory usage during quote parsing"""
    import psutil
    
    process = psutil.Process()
    wrapper = DCAPWrapper()
    
    # Measure baseline memory
    baseline_memory = process.memory_info().rss
    
    # Parse a large quote
    large_quote = "01" * 10000  # Large hex string
    try:
        wrapper.parse_quote(large_quote)
    except DCAPError:
        pass  # Expected to fail, just testing memory
    
    peak_memory = process.memory_info().rss
    memory_increase = peak_memory - baseline_memory
    
    # Memory increase should be reasonable
    assert memory_increase < 100 * 1024 * 1024  # Less than 100MB

def test_thread_safety():
    """Test DCAP wrapper thread safety"""
    import threading
    import time
    
    wrapper = DCAPWrapper()
    results = []
    errors = []
    
    def worker_thread():
        try:
            result = wrapper.parse_quote("test_quote_hex")
            results.append(result)
        except Exception as e:
            errors.append(e)
    
    # Start multiple threads
    threads = [threading.Thread(target=worker_thread) for _ in range(20)]
    for thread in threads:
        thread.start()
    
    for thread in threads:
        thread.join()
    
    # All threads should complete without errors
    assert len(errors) == 0
    assert len(results) == 20
```

### **Phase 4: End-to-End Testing**

**Objective:** Validate complete attestation workflow

**Test Categories:**

**1. Real Environment Tests**
```python
def test_real_tdx_quote_parsing():
    """Test with real TDX quotes from actual hardware"""
    # This requires running on actual TDX hardware
    service = AttestationService()
    
    # Get real attestation from endpoints
    self_attestation = service.get_self_attestation()
    secretai_attestation = service.get_secret_ai_attestation()
    
    # Validate real quotes parse correctly
    assert self_attestation["success"] is True
    assert secretai_attestation["success"] is True
    
    # Check measurements are valid hex
    self_mrtd = self_attestation["attestation"]["mrtd"]
    assert len(self_mrtd) == 96
    assert all(c in "0123456789abcdef" for c in self_mrtd.lower())

def test_multiple_quote_formats():
    """Test parsing different quote versions/formats"""
    wrapper = DCAPWrapper()
    
    # Test with different quote samples if available
    quote_samples = [
        "tdx_quote_v4_sample",
        "tdx_quote_v5_sample",
        # Add more samples as available
    ]
    
    for quote_sample in quote_samples:
        try:
            result = wrapper.parse_quote(quote_sample)
            assert "measurements" in result
        except DCAPError as e:
            # Document which formats fail
            print(f"Quote format failed: {e}")
```

**2. Regression Tests**
```python
def test_api_compatibility():
    """Ensure API remains compatible after DCAP integration"""
    service = AttestationService()
    
    # Test existing API endpoints still work
    status = service.get_status()
    assert "service" in status
    assert status["service"] == "attestation"
    
    # Test data structures haven't changed
    attestation = service.get_self_attestation()
    assert "success" in attestation
    assert "attestation" in attestation
    
    # Test AttestationData structure
    data = attestation["attestation"]
    required_fields = ["mrtd", "rtmr0", "rtmr1", "rtmr2", "rtmr3", 
                      "report_data", "certificate_fingerprint", "timestamp"]
    for field in required_fields:
        assert field in data

def test_error_responses():
    """Test error handling produces consistent responses"""
    service = AttestationService()
    
    # Simulate various error conditions
    with patch('service._extract_attestation_quote') as mock_extract:
        mock_extract.return_value = ""  # Empty quote
        
        result = service.get_self_attestation()
        
        # Should handle gracefully
        assert result["success"] is False or \
               result["attestation"]["mrtd"].startswith("error_")
```

## 🔧 **Test Environment Setup**

### **1. Development Environment**
```bash
# Install test dependencies
pip install pytest pytest-cov pytest-mock psutil

# Install DCAP libraries (as per installation guide)
sudo apt install libsgx-dcap-ql-dev libsgx-dcap-quote-verify-dev

# Set up test data directory
mkdir -p tests/data/quotes
```

### **2. Test Data Collection**
```python
# collect_test_quotes.py
"""Collect sample TDX quotes for testing"""

def collect_demo_quotes():
    """Extract quotes from your current demo data"""
    quotes = {
        "self_vm_demo": "d1b2c3a4f5e6d7c8b9a0...",  # Your demo data
        "secretai_vm_demo": "e5f6a7b8c9d0e1f2a3b4...",  # Your demo data
    }
    return quotes

def collect_real_quotes():
    """Collect quotes from real TDX environment (if available)"""
    try:
        # Use your existing attestation service
        service = AttestationService()
        
        self_result = service.get_self_attestation()
        secretai_result = service.get_secret_ai_attestation()
        
        if self_result["success"]:
            return {
                "real_self_vm": self_result["attestation"]["raw_quote"],
                "real_secretai_vm": secretai_result["attestation"]["raw_quote"]
            }
    except Exception as e:
        print(f"Could not collect real quotes: {e}")
        return {}
```

### **3. CI/CD Integration**
```yaml
# .github/workflows/dcap-integration-test.yml
name: DCAP Integration Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-20.04
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.8
    
    - name: Install DCAP libraries
      run: |
        echo 'deb [arch=amd64] https://download.01.org/intel-sgx/sgx_repo/ubuntu focal main' | sudo tee /etc/apt/sources.list.d/intel-sgx.list
        wget -qO - https://download.01.org/intel-sgx/sgx_repo/ubuntu/intel-sgx-deb.key | sudo apt-key add -
        sudo apt update
        sudo apt install libsgx-dcap-ql-dev libsgx-dcap-quote-verify-dev
    
    - name: Install Python dependencies
      run: |
        pip install pytest pytest-cov
        pip install -r requirements.txt
    
    - name: Run DCAP tests
      run: |
        pytest tests/test_dcap_wrapper.py -v
        pytest tests/test_attestation_service.py -v
```

## 🎯 **Success Criteria**

**Functional Tests:**
- ✅ All quote parsing tests pass with real TDX quotes
- ✅ DCAP wrapper correctly extracts MRTD, RTMR0-3 values
- ✅ Error handling works for invalid/malformed quotes
- ✅ API compatibility maintained with existing clients

**Performance Tests:**
- ✅ Parsing latency < 2x current implementation
- ✅ Memory usage remains stable under load
- ✅ Concurrent requests handled without deadlocks

**Integration Tests:**
- ✅ Dual VM attestation workflow works end-to-end
- ✅ Certificate validation integration successful
- ✅ Service health checks pass consistently

**Regression Tests:**
- ✅ No existing functionality broken
- ✅ All API endpoints maintain compatibility
- ✅ Error responses remain consistent

This comprehensive testing strategy ensures the DCAP integration is reliable, performant, and maintains compatibility with your existing attestation service.
