# Intel DCAP Libraries Installation Guide

## 🎯 **Goal: Install Intel DCAP Libraries for TDX Quote Parsing**

This guide provides step-by-step instructions to install Intel's official DCAP (Data Center Attestation Primitives) libraries for proper TDX quote parsing.

## 📋 **Prerequisites**

**System Requirements:**
- Ubuntu 20.04+ or compatible Linux distribution
- Intel TDX-capable hardware (for production)
- Root/sudo access for package installation
- Internet access for downloading packages

**Development Dependencies:**
- Python 3.8+
- gcc compiler
- make and cmake build tools
- Python development headers

## 🔧 **Installation Steps**

### **Step 1: Add Intel SGX Repository**

```bash
# Add Intel's official repository
echo 'deb [arch=amd64] https://download.01.org/intel-sgx/sgx_repo/ubuntu focal main' | sudo tee /etc/apt/sources.list.d/intel-sgx.list

# Import Intel's signing key
wget -qO - https://download.01.org/intel-sgx/sgx_repo/ubuntu/intel-sgx-deb.key | sudo apt-key add -

# Update package lists
sudo apt update
```

### **Step 2: Install DCAP Libraries**

```bash
# Install development libraries (includes headers)
sudo apt install -y libsgx-dcap-ql-dev
sudo apt install -y libsgx-dcap-quote-verify-dev

# Install runtime libraries
sudo apt install -y libsgx-dcap-ql
sudo apt install -y libsgx-dcap-quote-verify

# Install additional dependencies
sudo apt install -y libsgx-dcap-default-qpl
sudo apt install -y libsgx-dcap-default-qpl-dev
```

### **Step 3: Install Development Tools**

```bash
# Python development headers
sudo apt install -y python3-dev python3-pip

# Build tools
sudo apt install -y build-essential gcc make cmake

# Additional utilities
sudo apt install -y pkg-config
```

### **Step 4: Verify Installation**

```bash
# Check if libraries are installed
ldconfig -p | grep dcap

# Expected output should include:
# libsgx_dcap_ql.so.1 (libc6,x86-64) => /usr/lib/x86_64-linux-gnu/libsgx_dcap_ql.so.1
# libsgx_dcap_quoteverify.so.1 (libc6,x86-64) => /usr/lib/x86_64-linux-gnu/libsgx_dcap_quoteverify.so.1

# Check header files
ls -la /usr/include/sgx_*

# Expected files:
# /usr/include/sgx_dcap_quoteverify.h
# /usr/include/sgx_ql_lib_common.h
# /usr/include/sgx_qve_header.h
```

### **Step 5: Test Basic Library Loading**

Create a test script to verify library loading:

```python
# test_dcap_loading.py
import ctypes
import os

def test_dcap_libraries():
    try:
        # Try to load quote verification library
        qv_lib = ctypes.CDLL('libsgx_dcap_quoteverify.so.1')
        print("✅ Quote verification library loaded successfully")
        
        # Try to load quote library  
        ql_lib = ctypes.CDLL('libsgx_dcap_ql.so.1')
        print("✅ Quote library loaded successfully")
        
        return True
    except Exception as e:
        print(f"❌ Failed to load DCAP libraries: {e}")
        return False

if __name__ == "__main__":
    if test_dcap_libraries():
        print("🎉 DCAP libraries are properly installed!")
    else:
        print("💥 DCAP installation needs troubleshooting")
```

Run the test:
```bash
python3 test_dcap_loading.py
```

## 🐳 **Docker Integration**

If using Docker, add these to your Dockerfile:

```dockerfile
# Add Intel repository
RUN echo 'deb [arch=amd64] https://download.01.org/intel-sgx/sgx_repo/ubuntu focal main' >> /etc/apt/sources.list.d/intel-sgx.list && \
    wget -qO - https://download.01.org/intel-sgx/sgx_repo/ubuntu/intel-sgx-deb.key | apt-key add -

# Install DCAP libraries
RUN apt-get update && apt-get install -y \
    libsgx-dcap-ql \
    libsgx-dcap-quote-verify \
    libsgx-dcap-default-qpl \
    python3-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*
```

## 🔍 **Troubleshooting**

### **Common Issues:**

**1. Repository Key Import Fails**
```bash
# Alternative key import method
curl -fsSL https://download.01.org/intel-sgx/sgx_repo/ubuntu/intel-sgx-deb.key | sudo gpg --dearmor -o /usr/share/keyrings/intel-sgx.gpg

# Update sources list with new key
echo 'deb [arch=amd64 signed-by=/usr/share/keyrings/intel-sgx.gpg] https://download.01.org/intel-sgx/sgx_repo/ubuntu focal main' | sudo tee /etc/apt/sources.list.d/intel-sgx.list
```

**2. Package Not Found**
```bash
# Check if focal is correct for your Ubuntu version
lsb_release -cs  # Should output your Ubuntu codename

# For Ubuntu 22.04 (jammy), use:
echo 'deb [arch=amd64] https://download.01.org/intel-sgx/sgx_repo/ubuntu jammy main' | sudo tee /etc/apt/sources.list.d/intel-sgx.list
```

**3. Library Loading Fails**
```bash
# Update library cache
sudo ldconfig

# Check library dependencies
ldd /usr/lib/x86_64-linux-gnu/libsgx_dcap_quoteverify.so.1
```

**4. Permission Issues**
```bash
# Ensure user is in sgx group (if SGX hardware present)
sudo usermod -a -G sgx $USER
# Logout and login again
```

### **Verification Commands:**

```bash
# Check installed packages
dpkg -l | grep sgx

# Check library locations
find /usr -name "*dcap*" 2>/dev/null

# Check header files
find /usr/include -name "sgx_*" 2>/dev/null

# Test library linking
pkg-config --libs --cflags libsgx_dcap_ql 2>/dev/null || echo "pkg-config not available"
```

## 📚 **Next Steps**

After successful installation:

1. **Study the API:** Review header files in `/usr/include/sgx_*`
2. **Create Python wrapper:** Implement ctypes bindings for DCAP functions
3. **Test with sample quotes:** Validate parsing against known-good quotes
4. **Integrate with service:** Replace current parsing logic

## 🔗 **Reference Links**

**Official Documentation:**
- Intel SGX DCAP Installation Guide: https://download.01.org/intel-sgx/sgx-dcap/
- Intel TDX Developer Guide: https://cc-enabling.trustedservices.intel.com/intel-tdx-enabling-guide/

**Repository Information:**
- Intel SGX Repository: https://download.01.org/intel-sgx/sgx_repo/ubuntu/
- DCAP Source Code: https://github.com/intel/SGXDataCenterAttestationPrimitives

**Community Resources:**
- Intel Developer Forums: https://community.intel.com/t5/Intel-Software-Guard-Extensions/bd-p/sgx
- GitHub Issues: https://github.com/intel/SGXDataCenterAttestationPrimitives/issues

This installation guide provides the foundation for integrating Intel's official DCAP libraries into your TDX attestation service.
