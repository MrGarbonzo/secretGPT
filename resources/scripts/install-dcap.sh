#!/bin/bash

# Install Intel DCAP Libraries
# This script installs Intel's Data Center Attestation Primitives libraries

set -e  # Exit on any error

echo "🔐 Installing Intel DCAP Libraries..."

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo "❌ Please run this script as a regular user (not root)"
   echo "   The script will prompt for sudo when needed"
   exit 1
fi

# Detect Ubuntu version for repository selection
if [[ -f /etc/os-release ]]; then
    . /etc/os-release
    OS=$ID
    VERSION_CODENAME=$UBUNTU_CODENAME
    
    if [[ -z "$VERSION_CODENAME" ]]; then
        # Fallback to VERSION_ID to codename mapping
        case $VERSION_ID in
            "20.04") VERSION_CODENAME="focal" ;;
            "22.04") VERSION_CODENAME="jammy" ;;
            "24.04") VERSION_CODENAME="noble" ;;
            *) VERSION_CODENAME="focal" ;; # Default fallback
        esac
    fi
else
    echo "❌ Cannot detect OS version"
    exit 1
fi

echo "📋 Using Ubuntu codename: $VERSION_CODENAME"

# Backup existing sources if they exist
if [[ -f /etc/apt/sources.list.d/intel-sgx.list ]]; then
    echo "📋 Backing up existing Intel SGX repository configuration..."
    sudo cp /etc/apt/sources.list.d/intel-sgx.list /etc/apt/sources.list.d/intel-sgx.list.backup
fi

# Add Intel SGX repository
echo "📦 Adding Intel SGX repository..."
echo "deb [arch=amd64] https://download.01.org/intel-sgx/sgx_repo/ubuntu $VERSION_CODENAME main" | sudo tee /etc/apt/sources.list.d/intel-sgx.list

# Download and add Intel's GPG key
echo "🔑 Adding Intel's repository signing key..."
wget -qO - https://download.01.org/intel-sgx/sgx_repo/ubuntu/intel-sgx-deb.key | sudo apt-key add -

# Alternative method for newer Ubuntu versions that deprecate apt-key
if ! sudo apt-key list | grep -q "Intel SGX"; then
    echo "🔑 Using alternative key import method..."
    wget -qO - https://download.01.org/intel-sgx/sgx_repo/ubuntu/intel-sgx-deb.key | sudo gpg --dearmor -o /usr/share/keyrings/intel-sgx.gpg
    
    # Update sources list to use new key
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/intel-sgx.gpg] https://download.01.org/intel-sgx/sgx_repo/ubuntu $VERSION_CODENAME main" | sudo tee /etc/apt/sources.list.d/intel-sgx.list
fi

# Update package lists
echo "📥 Updating package lists..."
sudo apt update

# Install DCAP development libraries (includes headers)
echo "🔧 Installing DCAP development libraries..."
sudo apt install -y \
    libsgx-dcap-ql-dev \
    libsgx-dcap-quote-verify-dev

# Install DCAP runtime libraries
echo "📚 Installing DCAP runtime libraries..."
sudo apt install -y \
    libsgx-dcap-ql \
    libsgx-dcap-quote-verify

# Install additional DCAP components
echo "🔗 Installing additional DCAP components..."
sudo apt install -y \
    libsgx-dcap-default-qpl \
    libsgx-dcap-default-qpl-dev

# Install Intel SGX driver if available (for SGX support)
echo "🚀 Installing Intel SGX driver (if available)..."
sudo apt install -y libsgx-enclave-common libsgx-enclave-common-dev || echo "ℹ️  SGX driver not available, TDX-only setup"

# Update library cache
echo "🔄 Updating library cache..."
sudo ldconfig

# Verify installation
echo "✅ Verifying DCAP installation..."

# Check if libraries are available
echo "📋 Checking installed libraries..."
LIBRARIES=(
    "libsgx_dcap_ql.so.1"
    "libsgx_dcap_quoteverify.so.1"
)

for lib in "${LIBRARIES[@]}"; do
    if ldconfig -p | grep -q "$lib"; then
        echo "✅ $lib found"
    else
        echo "❌ $lib not found"
    fi
done

# Check header files
echo "📋 Checking header files..."
HEADERS=(
    "/usr/include/sgx_dcap_quoteverify.h"
    "/usr/include/sgx_ql_lib_common.h"
    "/usr/include/sgx_qve_header.h"
)

for header in "${HEADERS[@]}"; do
    if [[ -f "$header" ]]; then
        echo "✅ $header found"
    else
        echo "❌ $header not found"
    fi
done

# Check package installation
echo "📋 Checking installed packages..."
PACKAGES=(
    "libsgx-dcap-ql-dev"
    "libsgx-dcap-quote-verify-dev"
    "libsgx-dcap-ql"
    "libsgx-dcap-quote-verify"
)

for package in "${PACKAGES[@]}"; do
    if dpkg -l | grep -q "$package"; then
        echo "✅ $package installed"
    else
        echo "❌ $package not installed"
    fi
done

# Test basic library loading with Python
echo "🐍 Testing Python library loading..."
if command -v python3 &> /dev/null; then
    python3 -c "
import ctypes
try:
    qv_lib = ctypes.CDLL('libsgx_dcap_quoteverify.so.1')
    print('✅ Quote verification library loaded successfully')
except Exception as e:
    print(f'❌ Failed to load quote verification library: {e}')

try:
    ql_lib = ctypes.CDLL('libsgx_dcap_ql.so.1')
    print('✅ Quote library loaded successfully')
except Exception as e:
    print(f'❌ Failed to load quote library: {e}')
"
else
    echo "⚠️  Python3 not available for testing"
fi

echo ""
echo "🎉 Intel DCAP installation complete!"
echo ""
echo "📋 Installation summary:"
echo "   - Intel SGX repository added"
echo "   - DCAP development libraries installed"
echo "   - DCAP runtime libraries installed"
echo "   - Library cache updated"
echo ""
echo "📝 Next steps:"
echo "   1. Run './scripts/validate-installation.sh' to perform comprehensive validation"
echo "   2. Start implementing the DCAP wrapper in Python"
echo "   3. Test with your existing quote samples"
echo ""
echo "🔧 Troubleshooting:"
echo "   - If libraries not found: sudo ldconfig"
echo "   - If packages missing: sudo apt update && sudo apt install <package>"
echo "   - Check logs: /var/log/apt/history.log"
echo ""
echo "📚 References:"
echo "   - DCAP documentation: /usr/share/doc/libsgx-dcap-*/"
echo "   - Header files: /usr/include/sgx_*"
echo "   - Library files: /usr/lib/x86_64-linux-gnu/libsgx_dcap_*"
