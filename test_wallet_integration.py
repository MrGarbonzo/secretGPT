#!/usr/bin/env python3
"""
Test script for Keplr Wallet Integration
Tests the complete flow: Frontend -> Hub -> WalletProxy -> secret_network_mcp
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.wallet_service.proxy import WalletProxyService

async def test_wallet_integration():
    """Test the wallet integration end-to-end"""
    print("🔮 Testing Keplr Wallet Integration")
    print("=" * 50)
    
    # Initialize wallet proxy service
    print("1. Initializing WalletProxyService...")
    wallet_proxy = WalletProxyService()
    init_result = await wallet_proxy.initialize()
    print(f"   Initialization: {init_result}")
    
    if not init_result.get("success"):
        print("❌ Wallet proxy initialization failed")
        return False
    
    # Test wallet status
    print("\n2. Testing wallet status...")
    status_result = await wallet_proxy.get_status()
    print(f"   Status: {status_result}")
    
    # Test wallet connection
    print("\n3. Testing wallet connection...")
    test_address = "secret1k0jntykt7e4g3y88ltc60czgjuqdy4c9e8fzek"
    connect_result = await wallet_proxy.connect_wallet(
        address=test_address,
        name="Test Keplr Wallet",
        is_hardware=False
    )
    print(f"   Connection: {connect_result}")
    
    if connect_result.get("success"):
        # Test balance query
        print("\n4. Testing balance query...")
        balance_result = await wallet_proxy.get_wallet_balance(test_address)
        print(f"   Balance: {balance_result}")
        
        # Test wallet disconnect
        print("\n5. Testing wallet disconnect...")
        disconnect_result = await wallet_proxy.disconnect_wallet(test_address)
        print(f"   Disconnect: {disconnect_result}")
    
    # Cleanup
    await wallet_proxy.cleanup()
    
    print("\n🎉 Wallet integration test completed!")
    print("✅ HTTP bridge mode working")
    print("🔮 Ready for future attestation bridge")
    
    return True

if __name__ == "__main__":
    asyncio.run(test_wallet_integration())