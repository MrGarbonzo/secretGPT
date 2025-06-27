# VM Configuration Template and Examples

## 🎯 **VM Configuration Reference**

This file provides the complete VM configuration specifications for the centralized attestation service.

## 📋 **Configuration Schema**

### **vm_configs.yaml Structure**
```yaml
# Service-level configuration
service:
  host: "0.0.0.0"
  port: 8080
  workers: 4
  timeout: 30
  debug: false
  
# Caching configuration
cache:
  ttl: 300  # Time-to-live in seconds (5 minutes)
  max_size: 1000  # Maximum cached entries
  enabled: true
  
# Monitoring and logging
monitoring:
  metrics_enabled: true
  health_check_interval: 30  # seconds
  log_level: "INFO"  # DEBUG, INFO, WARNING, ERROR
  structured_logging: true
  
# Performance tuning
performance:
  max_concurrent_requests: 50
  request_timeout: 30
  retry_attempts: 3
  circuit_breaker_threshold: 5

# VM configurations
vms:
  # Current production VMs
  secretai:
    # Connection details
    endpoint: "https://secretai.scrtlabs.com:29343"
    type: "secret-ai"
    
    # Parsing configuration
    parsing_strategy: "rest_server"
    attestation_endpoint: "/cpu"  # TDX attestation endpoint
    status_endpoint: "/status"    # Health check endpoint
    
    # Timeouts and retries
    timeout: 30
    retry_attempts: 3
    retry_delay: 1  # seconds between retries
    
    # Fallback strategy
    fallback_strategy: "none"  # No fallback for secretAI
    
    # TLS configuration
    tls_verify: false  # Accept self-signed certificates
    tls_timeout: 10
    
    # Specific configurations
    requires_auth: false
    custom_headers: {}
    
  secretgpt:
    # Connection details
    endpoint: "https://localhost:29343"
    type: "secret-gpt"
    
    # Parsing configuration
    parsing_strategy: "rest_server"
    attestation_endpoint: "/cpu"
    status_endpoint: "/status"
    
    # Timeouts and retries
    timeout: 30
    retry_attempts: 3
    retry_delay: 1
    
    # Fallback strategy - IMPORTANT: Has hardcoded fallback
    fallback_strategy: "hardcoded"
    fallback_config:
      use_baseline_offsets: true
      baseline_file: "current_parser_baseline.json"
    
    # TLS configuration
    tls_verify: false
    tls_timeout: 10
    
    # Specific configurations
    requires_auth: false
    custom_headers: {}

# Template for future VM additions
vm_template:
  future_vm_name:
    # Required fields
    endpoint: "https://vm-hostname:29343"
    type: "custom"  # vm type identifier
    parsing_strategy: "rest_server"  # rest_server, hardcoded, dcap
    
    # Optional fields with defaults
    attestation_endpoint: "/cpu"
    status_endpoint: "/status"
    timeout: 30
    retry_attempts: 3
    retry_delay: 1
    fallback_strategy: "hardcoded"  # none, hardcoded, rest_server
    tls_verify: false
    tls_timeout: 10
    requires_auth: false
    custom_headers: {}
```

## 🔧 **Configuration Examples**

### **Example 1: Basic VM Configuration**
```yaml
vms:
  basic_vm:
    endpoint: "https://basic-vm:29343"
    type: "basic"
    parsing_strategy: "rest_server"
```

### **Example 2: VM with Custom Headers**
```yaml
vms:
  authenticated_vm:
    endpoint: "https://secure-vm:29343"
    type: "secure"
    parsing_strategy: "rest_server"
    requires_auth: true
    custom_headers:
      Authorization: "Bearer ${API_TOKEN}"
      X-Client-ID: "attestation-hub"
```

### **Example 3: VM with Intel DCAP Parsing**
```yaml
vms:
  dcap_vm:
    endpoint: "https://dcap-vm:29343"
    type: "dcap-enabled"
    parsing_strategy: "dcap"
    timeout: 60  # DCAP parsing may take longer
    fallback_strategy: "rest_server"
```

### **Example 4: VM with Complex Fallback Chain**
```yaml
vms:
  multi_fallback_vm:
    endpoint: "https://complex-vm:29343"
    type: "enterprise"
    parsing_strategy: "dcap"
    fallback_strategy: "rest_server"
    fallback_config:
      secondary_fallback: "hardcoded"
      fallback_timeout: 15
```

## 📊 **Parsing Strategy Reference**

### **Available Parsing Strategies**

#### **1. rest_server**
**Description**: Uses secret-vm-attest-rest-server endpoints
**Best for**: Standard SecretVM deployments
**Configuration**:
```yaml
parsing_strategy: "rest_server"
attestation_endpoint: "/cpu"  # or "/attestation", "/self"
```

#### **2. hardcoded**
**Description**: Byte-offset parsing (current secretGPT method)
**Best for**: Fallback or direct quote parsing
**Configuration**:
```yaml
parsing_strategy: "hardcoded"
fallback_config:
  use_baseline_offsets: true
  mrtd_offset: 368
  rtmr0_offset: 752
  # ... other offsets
```

#### **3. dcap**
**Description**: Intel DCAP library integration
**Best for**: Specification-compliant parsing
**Configuration**:
```yaml
parsing_strategy: "dcap"
dcap_config:
  library_path: "/usr/lib/x86_64-linux-gnu/libsgx_dcap_ql.so"
  verify_certificate_chain: true
```

### **Fallback Strategy Options**

#### **none**
- No fallback, fail if primary parsing fails
- Use for VMs with reliable parsing

#### **hardcoded**
- Fall back to byte-offset parsing
- Use for VMs with baseline data available

#### **rest_server**
- Fall back to REST server parsing
- Use when primary strategy is DCAP

## 🔄 **Dynamic Configuration**

### **Runtime VM Addition**
```http
POST /vms/new_vm/config
Content-Type: application/json

{
  "endpoint": "https://new-vm:29343",
  "type": "experimental",
  "parsing_strategy": "rest_server",
  "timeout": 45,
  "fallback_strategy": "hardcoded"
}
```

### **Configuration Updates**
```http
PUT /vms/secretgpt/config
Content-Type: application/json

{
  "timeout": 60,
  "retry_attempts": 5,
  "fallback_strategy": "dcap"
}
```

## 🧪 **Test Configurations**

### **Development Configuration**
```yaml
# dev_vm_configs.yaml
service:
  port: 8081
  debug: true
  
cache:
  ttl: 60  # Shorter TTL for testing
  
vms:
  test_vm:
    endpoint: "http://localhost:29343"  # HTTP for local testing
    type: "test"
    parsing_strategy: "rest_server"
    timeout: 10
    tls_verify: false
```

### **Staging Configuration**
```yaml
# staging_vm_configs.yaml
service:
  workers: 2
  
monitoring:
  log_level: "DEBUG"
  
vms:
  secretai_staging:
    endpoint: "https://staging-secretai:29343"
    type: "secret-ai"
    parsing_strategy: "rest_server"
    
  secretgpt_staging:
    endpoint: "https://staging-secretgpt:29343"
    type: "secret-gpt"
    parsing_strategy: "rest_server"
    fallback_strategy: "hardcoded"
```

## 🛡️ **Security Configuration**

### **TLS/SSL Settings**
```yaml
vms:
  secure_vm:
    endpoint: "https://secure-vm:29343"
    tls_verify: true  # Verify certificates
    tls_ca_file: "/path/to/ca-certificates.pem"
    tls_cert_file: "/path/to/client-cert.pem"
    tls_key_file: "/path/to/client-key.pem"
```

### **Authentication Headers**
```yaml
vms:
  auth_vm:
    endpoint: "https://auth-vm:29343"
    requires_auth: true
    custom_headers:
      Authorization: "Bearer ${VM_API_TOKEN}"
      X-API-Version: "v1"
      X-Client-ID: "attestation-hub"
```

## 📋 **Configuration Validation**

### **Required Fields**
- `endpoint` - VM attestation endpoint URL
- `type` - VM type identifier
- `parsing_strategy` - Parsing method to use

### **Optional Fields with Defaults**
- `timeout: 30` - Request timeout in seconds
- `retry_attempts: 3` - Number of retry attempts
- `retry_delay: 1` - Delay between retries
- `tls_verify: false` - TLS certificate verification
- `fallback_strategy: "none"` - Fallback parsing method

### **Validation Rules**
- `endpoint` must be valid HTTPS URL
- `timeout` must be between 5 and 300 seconds
- `retry_attempts` must be between 0 and 10
- `parsing_strategy` must be one of: rest_server, hardcoded, dcap
- `fallback_strategy` must be one of: none, rest_server, hardcoded, dcap

## 🔄 **Migration from Current System**

### **secretGPT Migration Steps**

1. **Current State**:
```python
# Direct hardcoded parsing in secretGPT
attestation_data = self._parse_attestation_quote(quote, cert, vm_type)
```

2. **Migration State**:
```python
# Hub client integration
hub_client = AttestationHubClient("http://localhost:8080")
attestation_data = await hub_client.get_attestation("secretgpt")
```

3. **Configuration for Migration**:
```yaml
vms:
  secretgpt:
    endpoint: "https://localhost:29343"
    type: "secret-gpt"
    parsing_strategy: "rest_server"
    fallback_strategy: "hardcoded"  # Keep current parsing as fallback
    fallback_config:
      use_current_offsets: true
      baseline_validation: true
```

### **secretAI Integration**
```yaml
vms:
  secretai:
    endpoint: "https://secretai.scrtlabs.com:29343"
    type: "secret-ai"
    parsing_strategy: "rest_server"
    # No fallback needed - already working
```

## 🎯 **Production Deployment Configuration**

### **High Availability Setup**
```yaml
service:
  workers: 8  # Multiple workers for load handling
  
cache:
  ttl: 300
  max_size: 10000
  distributed: true  # Use Redis for distributed caching
  redis_url: "redis://attestation-cache:6379"
  
monitoring:
  metrics_enabled: true
  health_check_interval: 15
  prometheus_port: 9090
  
performance:
  max_concurrent_requests: 100
  circuit_breaker_threshold: 10
  
# Load balancer configuration
load_balancer:
  enabled: true
  health_check_path: "/health"
  instances:
    - "https://hub-1:8080"
    - "https://hub-2:8080"
    - "https://hub-3:8080"
```

---

**Status**: ✅ **CONFIGURATION TEMPLATES COMPLETE**

These configuration templates provide everything needed to deploy and manage the centralized attestation service across different environments and VM types.
