#!/usr/bin/env python3
"""
Research Kickoff Script

This script helps get the attest_tool research started by:
1. Checking the current environment
2. Guiding through the setup process  
3. Running initial tests
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def check_environment():
    """Check current research environment"""
    print("🔍 Checking research environment...")
    
    checks = []
    
    # Check if we're in the right directory
    current_dir = Path.cwd()
    if "attest_tool_research" in str(current_dir):
        checks.append("✅ In attest_tool_research directory")
    else:
        checks.append("❌ Not in attest_tool_research directory")
    
    # Check directory structure
    required_dirs = ["sample_data", "tools", "integration_tests", "findings", "prototype"]
    for dir_name in required_dirs:
        if os.path.exists(dir_name):
            checks.append(f"✅ {dir_name}/ directory exists")
        else:
            checks.append(f"❌ {dir_name}/ directory missing")
    
    # Check sample data
    sample_files = ["sample_data/known_good_quote.hex", "sample_data/data_manifest.json"]
    for file_path in sample_files:
        if os.path.exists(file_path):
            checks.append(f"✅ {file_path} exists")
        else:
            checks.append(f"❌ {file_path} missing")
    
    # Check for attest_tool
    attest_tool_path = "tools/attest_tool"
    if os.path.exists(attest_tool_path):
        checks.append("✅ attest_tool binary found")
    else:
        checks.append("❌ attest_tool binary not found")
    
    # Check for Git
    try:
        subprocess.run(["git", "--version"], capture_output=True, check=True)
        checks.append("✅ Git available")
    except:
        checks.append("❌ Git not available")
    
    # Check for Python tools
    tools = ["tools/quote_analyzer.py", "tools/current_parser.py"]
    for tool in tools:
        if os.path.exists(tool):
            checks.append(f"✅ {tool} exists")
        else:
            checks.append(f"❌ {tool} missing")
    
    print("\n".join(checks))
    print()
    
    # Return status
    failed_checks = [check for check in checks if check.startswith("❌")]
    return len(failed_checks) == 0, failed_checks

def clone_secret_vm_ops():
    """Clone the secret-vm-ops repository"""
    print("📥 Cloning secret-vm-ops repository...")
    
    try:
        # Clone repository
        result = subprocess.run([
            "git", "clone", 
            "https://github.com/scrtlabs/secret-vm-ops.git",
            "secret-vm-ops"
        ], capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("✅ Successfully cloned secret-vm-ops")
            return True
        else:
            print(f"❌ Failed to clone repository: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Timeout while cloning repository")
        return False
    except Exception as e:
        print(f"❌ Error cloning repository: {e}")
        return False

def find_attest_tool():
    """Search for attest_tool in the cloned repository"""
    print("🔍 Searching for attest_tool...")
    
    if not os.path.exists("secret-vm-ops"):
        print("❌ secret-vm-ops directory not found")
        return False
    
    # Search for attest_tool files
    attest_files = []
    
    for root, dirs, files in os.walk("secret-vm-ops"):
        for file in files:
            if "attest" in file.lower():
                file_path = os.path.join(root, file)
                attest_files.append(file_path)
    
    if attest_files:
        print(f"✅ Found {len(attest_files)} attest-related files:")
        for file_path in attest_files:
            file_size = os.path.getsize(file_path)
            file_type = "binary" if os.access(file_path, os.X_OK) else "text"
            print(f"   📄 {file_path} ({file_size} bytes, {file_type})")
        
        # Try to copy executable files to tools/
        copied_tools = []
        for file_path in attest_files:
            if os.access(file_path, os.X_OK) and "attest" in os.path.basename(file_path):
                dest_path = f"tools/{os.path.basename(file_path)}"
                try:
                    import shutil
                    shutil.copy2(file_path, dest_path)
                    os.chmod(dest_path, 0o755)
                    copied_tools.append(dest_path)
                    print(f"✅ Copied {file_path} to {dest_path}")
                except Exception as e:
                    print(f"❌ Failed to copy {file_path}: {e}")
        
        return len(copied_tools) > 0
    else:
        print("❌ No attest-related files found")
        return False

def test_current_parser():
    """Test the current hardcoded parser"""
    print("🧪 Testing current parser...")
    
    try:
        # Test with known good quote
        result = subprocess.run([
            sys.executable, "tools/current_parser.py", 
            "sample_data/known_good_quote.hex"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Current parser test successful")
            
            # Try to parse output
            try:
                parsed_output = json.loads(result.stdout)
                print(f"   📊 MRTD: {parsed_output['mrtd'][:32]}...")
                print(f"   📊 RTMR0: {parsed_output['rtmr0'][:32]}...")
                
                # Save baseline results
                baseline_file = "findings/current_parser_baseline.json"
                with open(baseline_file, 'w') as f:
                    json.dump(parsed_output, f, indent=2)
                print(f"   💾 Baseline saved to {baseline_file}")
                
                return True
            except json.JSONDecodeError:
                print("⚠️ Could not parse current parser output as JSON")
                print(f"Output: {result.stdout}")
                return False
        else:
            print(f"❌ Current parser test failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing current parser: {e}")
        return False

def test_attest_tool():
    """Test attest_tool if available"""
    print("🧪 Testing attest_tool...")
    
    # Find attest_tool executables
    attest_tools = []
    if os.path.exists("tools"):
        for file in os.listdir("tools"):
            if "attest" in file and os.access(f"tools/{file}", os.X_OK):
                attest_tools.append(f"tools/{file}")
    
    if not attest_tools:
        print("❌ No attest_tool executables found")
        return False
    
    print(f"🔧 Found {len(attest_tools)} attest_tool candidates:")
    for tool in attest_tools:
        print(f"   📄 {tool}")
    
    # Test each tool
    for tool_path in attest_tools:
        print(f"\n🧪 Testing {tool_path}...")
        
        try:
            # Test help command
            result = subprocess.run([
                tool_path, "--help"
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                print(f"✅ {tool_path} responds to --help")
                print(f"   Output: {result.stdout[:200]}...")
                
                # Test with sample quote
                result2 = subprocess.run([
                    tool_path, "--input", "sample_data/known_good_quote.hex"
                ], capture_output=True, text=True, timeout=30)
                
                if result2.returncode == 0:
                    print(f"✅ {tool_path} successfully processed sample quote")
                    return True
                else:
                    print(f"⚠️ {tool_path} failed to process sample quote: {result2.stderr}")
            else:
                print(f"❌ {tool_path} failed help test: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            print(f"❌ {tool_path} timed out")
        except Exception as e:
            print(f"❌ Error testing {tool_path}: {e}")
    
    return False

def generate_next_steps():
    """Generate next steps based on current status"""
    print("📋 Next Steps:")
    
    if os.path.exists("tools/attest_tool"):
        print("✅ attest_tool is ready!")
        print("   🔄 Run: python tools/quote_analyzer.py")
        print("   📊 This will perform comprehensive interface analysis")
    else:
        print("❌ attest_tool not found. Options:")
        print("   1. 📥 Check secret-vm-ops repository for binaries")
        print("   2. 🏗️ Look for build instructions in secret-vm-ops")
        print("   3. 📧 Contact Secret Labs team for attest_tool access")
        print("   4. 🔄 Try secret-vm-attest-rest-server instead")
    
    print("\n📋 Research Tasks:")
    print("   1. 🔍 Document attest_tool interface")
    print("   2. 🧪 Test with sample data")
    print("   3. 📊 Compare output with current parsing")
    print("   4. ⚡ Measure performance")
    print("   5. 🛠️ Design integration strategy")

def main():
    """Main research kickoff function"""
    print("🚀 Secret Labs attest_tool Research Kickoff")
    print("=" * 50)
    
    # Check environment
    env_ok, failed_checks = check_environment()
    
    if not env_ok:
        print(f"\n⚠️ Environment issues found:")
        for check in failed_checks:
            print(f"   {check}")
        print("\nPlease fix these issues before continuing.")
        return 1
    
    print("✅ Environment check passed!")
    
    # Test current parser first
    print("\n" + "=" * 50)
    if test_current_parser():
        print("✅ Current parser baseline established")
    else:
        print("❌ Current parser test failed")
        return 1
    
    # Clone repository if needed
    print("\n" + "=" * 50)
    if not os.path.exists("secret-vm-ops"):
        if clone_secret_vm_ops():
            print("✅ Repository cloned successfully")
        else:
            print("❌ Failed to clone repository")
    else:
        print("✅ secret-vm-ops repository already exists")
    
    # Look for attest_tool
    print("\n" + "=" * 50)
    if find_attest_tool():
        print("✅ attest_tool found and copied")
    else:
        print("❌ attest_tool not found in repository")
    
    # Test attest_tool if available
    print("\n" + "=" * 50)
    if test_attest_tool():
        print("✅ attest_tool is working!")
    else:
        print("❌ attest_tool testing failed")
    
    # Generate next steps
    print("\n" + "=" * 50)
    generate_next_steps()
    
    print("\n🎯 Research kickoff complete!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
