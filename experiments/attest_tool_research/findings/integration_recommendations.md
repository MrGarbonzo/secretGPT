# secret-vm-attest-rest-server Integration Guide

## 🎯 **Strategy Overview**

Rather than trying to access the `attest_tool` binary directly, use the **secret-vm-attest-rest-server** approach. This is the official Secret Labs method for attestation integration.

## 🚀 **Implementation Steps**

### **Step 1: Deploy secret-vm-attest-rest-server**

**Clone and Setup:**
```bash
# On your SecretVM
git clone https://github.com/scrtlabs/secret-vm-attest-rest-server.git
cd secret-vm-attest-rest-server

# Create configuration
cat > .env << EOF
SECRETVM_REPORT_DIR=reports
SECRETVM_REST_SERVER_IP=0.0.0.0
SECRETVM_SECURE=true
SECRETVM_REST_SERVER_PORT=29343
SECRETVM_CERT_PATH=cert/ssl_cert.pem
SECRETVM_KEY_PATH=cert/ssl_key.pem
SECRETVM_ATTEST_TOOL=attest_tool
SECRETVM_ATTEST_TIMEOUT_SEC=10
EOF

# Build and run
go build -o secret-vm-attest-rest-server cmd/main.go
./secret-vm-attest-rest-server
```

### **Step 2: Test Attestation Endpoint**

**Test with your quote:**
```bash
# Create test quote file
echo "040002008100000000000000939a7233f79c4ca9..." > test_quote.hex

# Test the /cpu endpoint (Intel TDX attestation)
curl -k https://localhost:29343/cpu

# Test the /attestation endpoint  
curl -k -X POST https://localhost:29343/attestation \
  -H "Content-Type: application/json" \
  -d '{"quote": "040002008100000000000000939a7233f79c4ca9..."}'
```

### **Step 3: Analyze Response Format**

Document the actual JSON response structure for comparison with your baseline.

### **Step 4: Integrate with secretGPT**

**Enhanced AttestationService:**
```python
class AttestationService:
    def __init__(self):
        self.rest_server_url = "https://localhost:29343"
        self.client = httpx.AsyncClient(verify=False, timeout=30.0)
    
    async def _parse_attestation_with_rest_server(self, quote: str) -> AttestationData:
        """Use secret-vm-attest-rest-server for parsing"""
        try:
            # Option 1: Use /cpu endpoint (reads from file)
            response = await self.client.get(f"{self.rest_server_url}/cpu")
            
            # Option 2: Use /attestation endpoint (direct processing)  
            response = await self.client.post(
                f"{self.rest_server_url}/attestation",
                json={"quote": quote}
            )
            
            if response.status_code != 200:
                raise AttestationError(f"REST server error: {response.text}")
            
            attestation_json = response.json()
            
            return AttestationData(
                mrtd=attestation_json.get('mrtd', ''),
                rtmr0=attestation_json.get('rtmr0', ''),
                rtmr1=attestation_json.get('rtmr1', ''),
                rtmr2=attestation_json.get('rtmr2', ''),
                rtmr3=attestation_json.get('rtmr3', ''),
                report_data=attestation_json.get('report_data', ''),
                certificate_fingerprint=await self._get_certificate_fingerprint(self.rest_server_url),
                timestamp=datetime.utcnow(),
                raw_quote=quote
            )
            
        except Exception as e:
            logger.error(f"REST server attestation failed: {e}")
            raise AttestationError(f"REST server attestation failed: {e}")
    
    async def _parse_attestation_quote(self, quote: str, cert_fingerprint: str, vm_type: str) -> AttestationData:
        """Enhanced parsing with REST server primary, hardcoded fallback"""
        try:
            # Primary: Use REST server
            return await self._parse_attestation_with_rest_server(quote)
        except Exception as e:
            logger.warning(f"REST server parsing failed, using hardcoded fallback: {e}")
            # Fallback: Use current hardcoded parsing
            return self._parse_attestation_hardcoded(quote, cert_fingerprint, vm_type)
```

## 🔧 **Configuration Integration**

**Add to secretGPT configuration:**
```python
# In config/settings.py
ATTESTATION_REST_SERVER_URL = os.getenv("ATTESTATION_REST_SERVER_URL", "https://localhost:29343")
ATTESTATION_USE_REST_SERVER = os.getenv("ATTESTATION_USE_REST_SERVER", "true").lower() == "true"
ATTESTATION_REST_TIMEOUT = int(os.getenv("ATTESTATION_REST_TIMEOUT", "30"))
```

## 🧪 **Testing Strategy**

### **Validation Tests:**
1. **Response Format**: Ensure JSON contains required fields
2. **Value Accuracy**: Compare with your baseline values  
3. **Performance**: Measure response time vs current parsing
4. **Error Handling**: Test with malformed quotes
5. **Fallback**: Verify hardcoded parsing works when REST fails

### **Test Script:**
```python
async def test_rest_server_integration():
    """Test REST server integration with baseline comparison"""
    
    # Load baseline
    with open('findings/current_parser_baseline.json', 'r') as f:
        baseline = json.load(f)
    
    # Test REST server
    service = AttestationService()
    
    try:
        result = await service._parse_attestation_with_rest_server(baseline['raw_quote'])
        
        # Compare results
        comparison = {
            'mrtd_match': result.mrtd == baseline['mrtd'],
            'rtmr0_match': result.rtmr0 == baseline['rtmr0'],
            'rtmr1_match': result.rtmr1 == baseline['rtmr1'],
            'rtmr2_match': result.rtmr2 == baseline['rtmr2'],
            'rtmr3_match': result.rtmr3 == baseline['rtmr3'],
        }
        
        print("Validation Results:", comparison)
        print("All fields match:", all(comparison.values()))
        
    except Exception as e:
        print(f"REST server test failed: {e}")
        print("Fallback to hardcoded parsing recommended")
```

## 📊 **Success Metrics**

✅ **Deployment**: secret-vm-attest-rest-server runs on port 29343  
✅ **Connectivity**: Can reach /status endpoint successfully  
✅ **Processing**: /cpu or /attestation returns JSON data  
✅ **Accuracy**: JSON values match your baseline results  
✅ **Performance**: Response time under 10 seconds  
✅ **Integration**: secretGPT can parse and use the data  

## 🛡️ **Error Handling Strategy**

1. **Connection Failures**: Fall back to hardcoded parsing
2. **Timeout Issues**: Increase timeout, then fallback
3. **Invalid JSON**: Log error, use fallback  
4. **Missing Fields**: Use default values, log warning
5. **REST Server Down**: Automatic fallback to current method

## 🔄 **Deployment Plan**

1. **Testing Environment**: Deploy REST server on test VM first
2. **Validation**: Confirm output accuracy vs baseline
3. **Integration**: Add HTTP client to secretGPT  
4. **Feature Flag**: Enable/disable REST server usage
5. **Production**: Gradual rollout with monitoring
6. **Cleanup**: Remove hardcoded parsing after validation

---

**Next Action**: Deploy secret-vm-attest-rest-server on your SecretVM and test the /cpu endpoint with your production environment.
