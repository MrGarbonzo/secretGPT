#!/bin/bash

# Validate DCAP Installation
# This script performs comprehensive validation of the Intel DCAP installation

set -e  # Exit on any error

echo "🔍 Validating Intel DCAP Installation..."

VALIDATION_PASSED=true
VALIDATION_WARNINGS=()

# Function to record validation failure
fail_validation() {
    echo "❌ $1"
    VALIDATION_PASSED=false
}

# Function to record validation warning
warn_validation() {
    echo "⚠️  $1"
    VALIDATION_WARNINGS+=("$1")
}

# Function to record validation success
pass_validation() {
    echo "✅ $1"
}

echo "📋 System Information:"
echo "   OS: $(lsb_release -ds 2>/dev/null || echo 'Unknown')"
echo "   Kernel: $(uname -r)"
echo "   Architecture: $(uname -m)"
echo ""

# 1. Check Intel SGX repository
echo "🔍 Checking Intel SGX repository..."
if [[ -f /etc/apt/sources.list.d/intel-sgx.list ]]; then
    pass_validation "Intel SGX repository configuration found"
    
    # Check if repository is accessible
    if apt-cache policy | grep -q "download.01.org/intel-sgx"; then
        pass_validation "Intel SGX repository is accessible"
    else
        warn_validation "Intel SGX repository configured but not accessible"
    fi
else
    fail_validation "Intel SGX repository not configured"
fi

# 2. Check package installation
echo ""
echo "🔍 Checking DCAP package installation..."

REQUIRED_PACKAGES=(
    "libsgx-dcap-ql"
    "libsgx-dcap-ql-dev"
    "libsgx-dcap-quote-verify"
    "libsgx-dcap-quote-verify-dev"
    "libsgx-dcap-default-qpl"
)

for package in "${REQUIRED_PACKAGES[@]}"; do
    if dpkg -l | grep -q "^ii.*$package"; then
        version=$(dpkg -l | grep "^ii.*$package" | awk '{print $3}')
        pass_validation "$package installed (version: $version)"
    else
        fail_validation "$package not installed"
    fi
done

# 3. Check shared libraries
echo ""
echo "🔍 Checking DCAP shared libraries..."

REQUIRED_LIBRARIES=(
    "libsgx_dcap_ql.so.1"
    "libsgx_dcap_quoteverify.so.1"
    "libsgx_dcap_default_qpl.so.1"
)

for lib in "${REQUIRED_LIBRARIES[@]}"; do
    if ldconfig -p | grep -q "$lib"; then
        lib_path=$(ldconfig -p | grep "$lib" | awk '{print $NF}')
        pass_validation "$lib found at $lib_path"
        
        # Check if library is readable
        if [[ -r "$lib_path" ]]; then
            pass_validation "$lib is readable"
        else
            warn_validation "$lib found but not readable"
        fi
    else
        fail_validation "$lib not found in library cache"
    fi
done

# 4. Check header files
echo ""
echo "🔍 Checking DCAP header files..."

REQUIRED_HEADERS=(
    "/usr/include/sgx_dcap_quoteverify.h"
    "/usr/include/sgx_ql_lib_common.h"
    "/usr/include/sgx_qve_header.h"
    "/usr/include/sgx_quote_3.h"
)

for header in "${REQUIRED_HEADERS[@]}"; do
    if [[ -f "$header" ]]; then
        pass_validation "Header file $header exists"
        
        # Check if header is readable
        if [[ -r "$header" ]]; then
            pass_validation "Header file $header is readable"
        else
            warn_validation "Header file $header exists but not readable"
        fi
    else
        fail_validation "Header file $header not found"
    fi
done

# 5. Check Python environment
echo ""
echo "🔍 Checking Python environment..."

if command -v python3 &> /dev/null; then
    python_version=$(python3 --version)
    pass_validation "Python 3 available: $python_version"
    
    # Check Python version
    python_major_minor=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    if [[ "$python_major_minor" > "3.7" ]]; then
        pass_validation "Python version is suitable ($python_major_minor)"
    else
        warn_validation "Python version may be too old ($python_major_minor), recommend 3.8+"
    fi
else
    fail_validation "Python 3 not available"
fi

# Check Python development headers
if dpkg -l | grep -q "python3-dev"; then
    pass_validation "Python development headers installed"
else
    fail_validation "Python development headers (python3-dev) not installed"
fi

# 6. Test Python ctypes library loading
echo ""
echo "🔍 Testing Python library loading..."

python3 << 'EOF'
import sys
import ctypes

def test_library_loading():
    """Test loading DCAP libraries with Python ctypes"""
    
    libraries_to_test = [
        ("libsgx_dcap_quoteverify.so.1", "Quote Verification Library"),
        ("libsgx_dcap_ql.so.1", "Quote Library"),
        ("libsgx_dcap_default_qpl.so.1", "Default Quote Provider Library")
    ]
    
    all_loaded = True
    
    for lib_name, lib_description in libraries_to_test:
        try:
            lib = ctypes.CDLL(lib_name)
            print(f"✅ {lib_description} loaded successfully")
            
            # Test that we can access the library object
            if hasattr(lib, '_name'):
                print(f"   Library path: {lib._name}")
            
        except Exception as e:
            print(f"❌ Failed to load {lib_description}: {e}")
            all_loaded = False
    
    return all_loaded

def test_function_access():
    """Test accessing specific functions in the libraries"""
    
    try:
        qv_lib = ctypes.CDLL('libsgx_dcap_quoteverify.so.1')
        
        # Check if key functions are available
        functions_to_check = [
            'sgx_qv_verify_quote',
            'sgx_qv_get_quote_supplemental_data_size'
        ]
        
        for func_name in functions_to_check:
            if hasattr(qv_lib, func_name):
                print(f"✅ Function {func_name} available")
            else:
                print(f"⚠️  Function {func_name} not found (may be symbol not exported)")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to access library functions: {e}")
        return False

# Run tests
print("🐍 Python Library Loading Tests:")
library_test_passed = test_library_loading()

print("\n🔧 Function Access Tests:")
function_test_passed = test_function_access()

# Exit with appropriate code
if library_test_passed and function_test_passed:
    print("\n✅ Python integration tests passed")
    sys.exit(0)
else:
    print("\n❌ Python integration tests failed")
    sys.exit(1)
EOF

python_test_result=$?
if [[ $python_test_result -eq 0 ]]; then
    pass_validation "Python library loading tests passed"
else
    fail_validation "Python library loading tests failed"
fi

# 7. Check development tools
echo ""
echo "🔍 Checking development tools..."

DEV_TOOLS=(
    "gcc"
    "make"
    "cmake"
    "pkg-config"
)

for tool in "${DEV_TOOLS[@]}"; do
    if command -v "$tool" &> /dev/null; then
        tool_version=$(command "$tool" --version 2>/dev/null | head -n1 || echo "unknown version")
        pass_validation "$tool available: $tool_version"
    else
        warn_validation "$tool not available (may be needed for compilation)"
    fi
done

# 8. Check permissions and access
echo ""
echo "🔍 Checking permissions and access..."

# Check if user can read library directories
if [[ -r /usr/lib/x86_64-linux-gnu/ ]]; then
    pass_validation "Can read system library directory"
else
    warn_validation "Cannot read system library directory"
fi

# Check if user can read include directories
if [[ -r /usr/include/ ]]; then
    pass_validation "Can read system include directory"
else
    warn_validation "Cannot read system include directory"
fi

# 9. Generate validation summary
echo ""
echo "📊 Validation Summary:"
echo "===================="

if [[ $VALIDATION_PASSED == true ]]; then
    echo "🎉 All critical validations passed!"
    
    if [[ ${#VALIDATION_WARNINGS[@]} -gt 0 ]]; then
        echo ""
        echo "⚠️  Warnings (non-critical):"
        for warning in "${VALIDATION_WARNINGS[@]}"; do
            echo "   - $warning"
        done
    fi
    
    echo ""
    echo "✅ Your system is ready for Intel DCAP development!"
    echo ""
    echo "📋 Next steps:"
    echo "   1. Create Python DCAP wrapper module"
    echo "   2. Test with sample TDX quotes"
    echo "   3. Integrate with AttestationService"
    echo "   4. Run comprehensive tests"
    
else
    echo "❌ Some validations failed. Please address the issues above."
    echo ""
    echo "🔧 Common fixes:"
    echo "   - Run: sudo apt update && sudo apt install <missing-package>"
    echo "   - Run: sudo ldconfig (to update library cache)"
    echo "   - Check: /var/log/apt/history.log (for installation issues)"
    echo "   - Verify: Intel repository is accessible"
    
    exit 1
fi

# 10. Create validation report
echo ""
echo "📝 Creating validation report..."

REPORT_FILE="dcap-validation-report.txt"
cat > "$REPORT_FILE" << EOF
Intel DCAP Installation Validation Report
==========================================
Generated: $(date)
System: $(lsb_release -ds 2>/dev/null || echo 'Unknown')
Kernel: $(uname -r)
Architecture: $(uname -m)

Validation Result: $(if [[ $VALIDATION_PASSED == true ]]; then echo "PASSED"; else echo "FAILED"; fi)

Package Versions:
$(dpkg -l | grep libsgx-dcap || echo "No DCAP packages found")

Library Locations:
$(ldconfig -p | grep libsgx_dcap || echo "No DCAP libraries found")

Python Version:
$(python3 --version 2>/dev/null || echo "Python 3 not available")

Warnings:
$(printf '%s\n' "${VALIDATION_WARNINGS[@]}")

EOF

echo "✅ Validation report saved to: $REPORT_FILE"

# Success exit
exit 0
