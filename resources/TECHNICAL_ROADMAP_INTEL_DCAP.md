# Intel DCAP Library Integration - Technical Roadmap

## 🎯 **Project Goal**
Replace reverse-engineered TDX quote parsing with Intel's official DCAP libraries for spec-compliant attestation.

## 📋 **Current State Analysis**

**Problem:** Current parsing in `attestation/service.py` uses hardcoded byte offsets:
```python
# PROBLEMATIC - Reverse-engineered offsets
mrtd_bytes = quote_bytes[184:232]     # 48 bytes at offset 184
rtmr0_bytes = quote_bytes[376:424]    # 48 bytes at offset 376
rtmr1_bytes = quote_bytes[424:472]    # 48 bytes at offset 424
# etc...
```

**Issues:**
- Only works with specific quote formats/versions
- No header validation or structure parsing
- Will break with different TDX versions
- Not based on Intel TDX specification

## 🔄 **Target State**

**Solution:** Use Intel DCAP libraries for proper parsing:
```python
# GOAL - Spec-compliant parsing
import dcap_wrapper
result = dcap_wrapper.verify_quote(quote_bytes)
mrtd = result.mrtd
rtmr0 = result.rtmr0
# etc...
```

## 📅 **Implementation Timeline: 2-3 weeks**

### **Phase 1: Environment Setup (2-3 days)**

**Day 1: Repository & Package Setup**
- Add Intel SGX repository to system
- Import Intel signing keys
- Update package manager sources

**Day 2: DCAP Library Installation**
- Install `libsgx-dcap-ql-dev` (Quote Library with headers)
- Install `libsgx-dcap-quote-verify-dev` (Verification Library)
- Install runtime dependencies
- Verify installation with ldconfig

**Day 3: Development Environment**
- Install Python development headers (`python3-dev`)
- Set up build tools (gcc, make)
- Create isolated development environment
- Test basic library loading

### **Phase 2: API Discovery & Analysis (2-3 days)**

**Header File Study:**
- Analyze `/usr/include/sgx_dcap_quoteverify.h`
- Study quote data structures and verification APIs
- Document key functions:
  - `sgx_qv_verify_quote()`
  - `sgx_qv_get_quote_supplemental_data_size()`
- Map error codes and return values

**Sample Code Analysis:**
- Study Intel's C examples from DCAP repository
- Understand memory management patterns
- Document verification workflow
- Identify integration points

### **Phase 3: Python ctypes Wrapper (4-5 days)**

**Day 1: Library Loading**
- Create Python module to load DCAP shared libraries
- Set up ctypes function prototypes
- Handle library loading errors
- Basic smoke tests

**Day 2: Data Structure Mapping**
- Map C structs to Python ctypes
- Handle quote verification result structures
- Memory allocation/deallocation helpers
- Pointer and buffer management

**Day 3: Core Functions**
- Implement quote verification wrapper
- Extract measurements (MRTD, RTMR0-3)
- Certificate chain handling
- Supplemental data processing

**Day 4: Error Handling**
- Map Intel error codes to Python exceptions
- Input validation and sanitization
- Memory cleanup mechanisms
- Comprehensive logging

**Day 5: Testing Framework**
- Unit tests with known quotes
- Error condition testing
- Performance benchmarking
- Validation against demo data

### **Phase 4: Service Integration (3-4 days)**

**Day 1: Interface Adaptation**
- Modify `AttestationData` class for DCAP output
- Update `_parse_attestation_quote()` method
- Maintain backward compatibility
- Handle data format differences

**Day 2: Service Updates**
- Replace parsing logic in `AttestationService`
- Update error handling throughout
- Modify caching if needed
- Test dual-VM attestation flow

**Day 3: Configuration & Deployment**
- Add DCAP library configuration options
- Update Docker containers with dependencies
- Modify deployment scripts
- Environment validation checks

**Day 4: Comprehensive Testing**
- Test multiple quote sources/formats
- Validate measurement extraction accuracy
- Performance testing under load
- Integration with SecretAI service

### **Phase 5: Production Deployment (2-3 days)**

**Day 1: Staging Deployment**
- Deploy to staging with monitoring
- Parallel comparison: old vs new parsing
- Validate no regressions
- Test rollback procedures

**Day 2: Production Migration**
- Gradual rollout with feature flags
- Monitor error rates and performance
- Compare results with baseline
- Emergency rollback preparation

**Day 3: Cleanup & Documentation**
- Remove old hardcoded parsing
- Update API documentation
- Create troubleshooting guides
- Document dependencies

## 🔧 **Technical Implementation Details**

### **Critical Files to Modify:**
1. `secretGPT/interfaces/web_ui/attestation/service.py`
   - Replace `_parse_attestation_quote()` method
   - Update error handling
   - Modify data structures if needed

2. Docker Configuration
   - Add DCAP library installation
   - Update dependency management
   - Environment variable configuration

3. Testing Framework
   - Update unit tests for new parsing
   - Integration tests with real quotes
   - Performance benchmarking

### **Key Technical Challenges:**

**Memory Management:**
- DCAP libraries use C-style allocation
- Need careful cleanup to prevent leaks
- Handle large quotes and certificate chains

**Thread Safety:**
- Verify DCAP library thread safety
- May need synchronization for concurrent requests
- Consider connection pooling

**Error Handling:**
- Map Intel error codes appropriately
- Handle network issues for certificate retrieval
- Graceful degradation on failures

**Dependencies:**
- Complex DCAP dependency chain
- Version compatibility requirements
- Platform-specific installation

### **Success Criteria:**

**Functional Requirements:**
- ✅ Parse all supported TDX quote versions correctly
- ✅ Extract MRTD, RTMR0-3 values accurately
- ✅ Validate certificate chains properly
- ✅ Maintain existing API compatibility

**Performance Requirements:**
- ✅ No significant latency increase
- ✅ Handle concurrent requests
- ✅ Reasonable memory usage

**Reliability Requirements:**
- ✅ Proper error handling and logging
- ✅ Graceful failure modes
- ✅ No memory leaks or crashes

## 🚨 **Risk Mitigation**

**Backup Plan:**
- Keep current parsing as fallback option
- Feature flag system for gradual rollout
- Rollback capability at each phase

**Testing Strategy:**
- Extensive validation with multiple quote sources
- Performance regression testing
- Integration testing with existing workflows

**Monitoring:**
- Comprehensive logging for DCAP operations
- Error rate and performance monitoring
- Alerting for parsing failures

## 📚 **Reference Materials**

**Essential Documentation:**
- Intel TDX DCAP Quoting Library API specification
- Intel TDX Module specification
- DCAP installation and integration guides

**Reference Implementations:**
- entropyxyz/tdx-quote (Rust - spec compliant)
- Intel DCAP C samples
- edgelesssys/go-tdx-qpl (Go implementation)

**Current System:**
- Analysis of existing parsing logic
- API contracts and data structures
- Deployment configuration

This roadmap provides a comprehensive path to replace the reverse-engineered quote parsing with Intel's official, specification-compliant libraries.
