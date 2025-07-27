#!/bin/bash

# Setup Environment for Intel DCAP Integration
# Run this script to prepare a fresh environment for DCAP development

set -e  # Exit on any error

echo "🚀 Setting up Intel DCAP development environment..."

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo "❌ Please run this script as a regular user (not root)"
   echo "   The script will prompt for sudo when needed"
   exit 1
fi

# Detect OS
if [[ -f /etc/os-release ]]; then
    . /etc/os-release
    OS=$ID
    VERSION=$VERSION_ID
else
    echo "❌ Cannot detect OS version"
    exit 1
fi

echo "📋 Detected OS: $OS $VERSION"

# Supported OS check
case $OS in
    ubuntu)
        if [[ "$VERSION" < "20.04" ]]; then
            echo "⚠️  Warning: Ubuntu 20.04+ recommended for DCAP support"
        fi
        ;;
    *)
        echo "⚠️  Warning: This script is optimized for Ubuntu. May need modifications for $OS"
        ;;
esac

# Update system packages
echo "📦 Updating system packages..."
sudo apt update

# Install basic development tools
echo "🔧 Installing development tools..."
sudo apt install -y \
    build-essential \
    gcc \
    make \
    cmake \
    pkg-config \
    wget \
    curl \
    gnupg \
    software-properties-common

# Install Python development dependencies
echo "🐍 Installing Python development dependencies..."
sudo apt install -y \
    python3 \
    python3-dev \
    python3-pip \
    python3-venv

# Verify Python version
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "✅ Python version: $PYTHON_VERSION"

if [[ "$PYTHON_VERSION" < "3.8" ]]; then
    echo "⚠️  Warning: Python 3.8+ recommended for this project"
fi

# Create virtual environment for the project
echo "🌟 Creating Python virtual environment..."
cd "$(dirname "$0")/.."  # Go to project root
if [[ ! -d "venv" ]]; then
    python3 -m venv venv
    echo "✅ Virtual environment created in ./venv"
else
    echo "ℹ️  Virtual environment already exists"
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo "📈 Upgrading pip..."
pip install --upgrade pip

# Install Python testing dependencies
echo "🧪 Installing Python testing dependencies..."
pip install \
    pytest \
    pytest-cov \
    pytest-mock \
    psutil \
    requests

# Install project dependencies if requirements.txt exists
if [[ -f "requirements.txt" ]]; then
    echo "📋 Installing project dependencies..."
    pip install -r requirements.txt
else
    echo "ℹ️  No requirements.txt found, skipping project dependencies"
fi

echo "✅ Environment setup complete!"
echo ""
echo "📋 Next steps:"
echo "   1. Run './scripts/install-dcap.sh' to install Intel DCAP libraries"
echo "   2. Run './scripts/validate-installation.sh' to verify setup"
echo "   3. Activate the virtual environment: source venv/bin/activate"
echo ""
echo "🔗 Useful commands:"
echo "   - Check Python: python3 --version"
echo "   - Check pip: pip --version"
echo "   - List packages: pip list"
echo "   - Run tests: pytest"
