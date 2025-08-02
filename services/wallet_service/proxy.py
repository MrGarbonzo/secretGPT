"""
Wallet Proxy Service - Bridge-Ready Architecture

This service provides wallet functionality bridging between secretGPT Hub and secret_network_mcp.
Designed to support both current HTTP communication and future attestation-based verified messaging.
"""

import aiohttp
import os
import logging
from typing import Dict, Any, Optional, Union
from enum import Enum

logger = logging.getLogger(__name__)

class BridgeMode(Enum):
    """Bridge communication modes"""
    HTTP = "http"          # Current: Direct HTTP to secret_network_mcp
    ATTESTED = "attested"  # Future: Verified message signing

class WalletRequest:
    """Standardized wallet request structure for future attestation"""
    def __init__(self, method: str, params: Dict[str, Any], attestation_context: Optional[Dict[str, Any]] = None):
        self.method = method
        self.params = params
        self.attestation_context = attestation_context or {
            "ui_source": "secret_gptee",
            "verification_required": False,
            "signing_mode": "http"
        }

class WalletProxyService:
    """
    Proxy service to communicate with secret_network_mcp
    
    Architecture designed for transition from HTTP to attestation-based bridge:
    - Current: HTTP client to secret_network_mcp:8002  
    - Future: Verified message signing with attestation
    """
    
    def __init__(self):
        self.mcp_base_url = os.getenv("SECRET_NETWORK_MCP_URL", "http://localhost:8002")
        self.bridge_mode = BridgeMode.HTTP  # Will become ATTESTED later
        self.session: Optional[aiohttp.ClientSession] = None
        self.attestation_context = {
            "service": "wallet_proxy",
            "version": "1.0.0",
            "bridge_ready": True
        }
    
    async def initialize(self) -> Dict[str, Any]:
        """Initialize the proxy service with bridge readiness"""
        try:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30),
                headers={
                    "User-Agent": "secretGPT-WalletProxy/1.0",
                    "X-Bridge-Mode": self.bridge_mode.value,
                    "X-Attestation-Ready": "true"
                }
            )
            
            # Test connection to secret_network_mcp
            health_status = await self._health_check()
            
            logger.info(f"Wallet proxy initialized in {self.bridge_mode.value} mode")
            logger.info(f"MCP connection: {health_status.get('success', False)}")
            
            return {
                "success": True, 
                "message": "Wallet proxy initialized",
                "bridge_mode": self.bridge_mode.value,
                "mcp_connection": health_status.get("success", False),
                "attestation_ready": True
            }
            
        except Exception as e:
            logger.error(f"Failed to initialize wallet proxy: {e}")
            return {
                "success": False, 
                "error": f"Failed to connect to MCP service: {e}",
                "bridge_mode": self.bridge_mode.value
            }
    
    async def _health_check(self) -> Dict[str, Any]:
        """Check if secret_network_mcp is accessible"""
        try:
            async with self.session.get(f"{self.mcp_base_url}/api/health") as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"success": False, "error": f"HTTP {response.status}"}
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _send_request(self, wallet_request: WalletRequest) -> Dict[str, Any]:
        """
        Send wallet request through current bridge mode
        Future: This will route to attestation-based messaging
        """
        if self.bridge_mode == BridgeMode.HTTP:
            return await self._http_send(wallet_request)
        else:
            # Future: return await self._attested_send(wallet_request)
            raise NotImplementedError("Attested bridge mode not yet implemented")
    
    async def _http_send(self, wallet_request: WalletRequest) -> Dict[str, Any]:
        """Send request via HTTP bridge (current implementation)"""
        try:
            method = wallet_request.method
            params = wallet_request.params
            
            if method == "connect":
                return await self._http_connect_wallet(params)
            elif method == "balance":
                return await self._http_get_balance(params)
            elif method == "transaction_status":
                return await self._http_get_transaction_status(params)
            elif method == "disconnect":
                return await self._http_disconnect_wallet(params)
            elif method == "status":
                return await self._http_get_status()
            else:
                return {"success": False, "error": f"Unknown wallet method: {method}"}
                
        except Exception as e:
            logger.error(f"HTTP wallet request failed: {e}")
            return {"success": False, "error": f"Request failed: {str(e)}"}
    
    async def _http_connect_wallet(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """HTTP: Connect wallet to secret_network_mcp"""
        async with self.session.post(
            f"{self.mcp_base_url}/api/wallet/connect",
            json=params
        ) as response:
            result = await response.json()
            return result
    
    async def _http_get_balance(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """HTTP: Get wallet balance from secret_network_mcp"""
        address = params.get("address")
        if not address:
            return {"success": False, "error": "Address required"}
            
        async with self.session.get(
            f"{self.mcp_base_url}/api/wallet/balance/{address}"
        ) as response:
            result = await response.json()
            return result
    
    async def _http_get_transaction_status(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """HTTP: Check transaction status via secret_network_mcp"""
        tx_hash = params.get("tx_hash")
        if not tx_hash:
            return {"success": False, "error": "Transaction hash required"}
            
        async with self.session.get(
            f"{self.mcp_base_url}/api/wallet/transaction/{tx_hash}"
        ) as response:
            result = await response.json()
            return result
    
    async def _http_disconnect_wallet(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """HTTP: Disconnect wallet from secret_network_mcp"""
        address = params.get("address")
        if not address:
            return {"success": False, "error": "Address required"}
            
        async with self.session.delete(
            f"{self.mcp_base_url}/api/wallet/disconnect/{address}"
        ) as response:
            result = await response.json()
            return result
    
    async def _http_get_status(self) -> Dict[str, Any]:
        """HTTP: Get wallet service status"""
        async with self.session.get(
            f"{self.mcp_base_url}/api/wallet/status"
        ) as response:
            result = await response.json()
            return result
    
    # Public API methods (attestation-ready)
    
    async def connect_wallet(self, address: str, name: str = None, is_hardware: bool = False) -> Dict[str, Any]:
        """Connect wallet with attestation context"""
        wallet_request = WalletRequest(
            method="connect",
            params={
                "address": address,
                "name": name or "Keplr Wallet", 
                "isHardwareWallet": is_hardware
            },
            attestation_context={
                "ui_source": "secret_gptee",
                "verification_required": self.bridge_mode == BridgeMode.ATTESTED,
                "signing_mode": self.bridge_mode.value,
                "operation": "wallet_connect"
            }
        )
        
        result = await self._send_request(wallet_request)
        
        # Add attestation metadata to response
        if result.get("success"):
            result["attestation_context"] = wallet_request.attestation_context
            
        return result
    
    async def get_wallet_balance(self, address: str) -> Dict[str, Any]:
        """Get wallet balance with attestation context"""
        wallet_request = WalletRequest(
            method="balance",
            params={"address": address},
            attestation_context={
                "ui_source": "secret_gptee",
                "verification_required": self.bridge_mode == BridgeMode.ATTESTED,
                "signing_mode": self.bridge_mode.value,
                "operation": "balance_query"
            }
        )
        
        result = await self._send_request(wallet_request)
        
        # Add attestation metadata to response
        if result.get("success"):
            result["attestation_context"] = wallet_request.attestation_context
            
        return result
    
    async def get_transaction_status(self, tx_hash: str) -> Dict[str, Any]:
        """Check transaction status with attestation context"""
        wallet_request = WalletRequest(
            method="transaction_status",
            params={"tx_hash": tx_hash},
            attestation_context={
                "ui_source": "secret_gptee",
                "verification_required": self.bridge_mode == BridgeMode.ATTESTED,
                "signing_mode": self.bridge_mode.value,
                "operation": "transaction_status"
            }
        )
        
        result = await self._send_request(wallet_request)
        
        # Add attestation metadata to response
        if result.get("success"):
            result["attestation_context"] = wallet_request.attestation_context
            
        return result
    
    async def disconnect_wallet(self, address: str) -> Dict[str, Any]:
        """Disconnect wallet with attestation context"""
        wallet_request = WalletRequest(
            method="disconnect",
            params={"address": address},
            attestation_context={
                "ui_source": "secret_gptee",
                "verification_required": self.bridge_mode == BridgeMode.ATTESTED,
                "signing_mode": self.bridge_mode.value,
                "operation": "wallet_disconnect"
            }
        )
        
        result = await self._send_request(wallet_request)
        
        # Add attestation metadata to response
        if result.get("success"):
            result["attestation_context"] = wallet_request.attestation_context
            
        return result
    
    async def get_status(self) -> Dict[str, Any]:
        """Get wallet service status with bridge information"""
        try:
            # Get MCP status
            wallet_request = WalletRequest(
                method="status",
                params={},
                attestation_context={
                    "ui_source": "secret_gptee", 
                    "verification_required": False,
                    "signing_mode": self.bridge_mode.value,
                    "operation": "status_check"
                }
            )
            
            mcp_status = await self._send_request(wallet_request)
            
            return {
                "success": True,
                "service": "Wallet Proxy",
                "bridge_mode": self.bridge_mode.value,
                "attestation_ready": True,
                "mcp_connection": mcp_status.get("success", False),
                "mcp_url": self.mcp_base_url,
                "mcp_status": mcp_status
            }
            
        except Exception as e:
            logger.error(f"Status check failed: {e}")
            return {
                "success": False,
                "service": "Wallet Proxy",
                "bridge_mode": self.bridge_mode.value,
                "error": f"Status check failed: {str(e)}"
            }
    
    async def switch_bridge_mode(self, mode: BridgeMode) -> Dict[str, Any]:
        """Switch between HTTP and attestation bridge modes (future)"""
        if mode == BridgeMode.ATTESTED:
            return {
                "success": False,
                "error": "Attested bridge mode not yet implemented",
                "current_mode": self.bridge_mode.value
            }
        
        self.bridge_mode = mode
        logger.info(f"Switched to bridge mode: {mode.value}")
        
        return {
            "success": True,
            "message": f"Switched to {mode.value} bridge mode",
            "bridge_mode": self.bridge_mode.value
        }
    
    async def cleanup(self):
        """Clean shutdown"""
        if self.session:
            await self.session.close()
            logger.info("Wallet proxy session closed")