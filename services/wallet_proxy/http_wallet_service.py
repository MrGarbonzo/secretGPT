"""
HTTP-based Wallet Service for SecretGPT
Connects to secret_network_mcp wallet endpoints for Keplr integration
"""
import aiohttp
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class HTTPWalletService:
    """
    HTTP-based wallet service that connects to secret_network_mcp wallet endpoints
    """
    
    def __init__(self, mcp_base_url: str = "http://10.0.1.100:8002"):
        """Initialize HTTP wallet service"""
        self.mcp_base_url = mcp_base_url
        self.session = None
        self.initialized = False
        logger.info(f"HTTP Wallet Service initialized with MCP URL: {mcp_base_url}")
    
    async def initialize(self) -> None:
        """Initialize HTTP session"""
        if self.initialized:
            return
            
        try:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30, connect=10)
            )
            
            # Test connection
            async with self.session.get(f"{self.mcp_base_url}/api/wallet/status") as response:
                if response.status == 200:
                    status = await response.json()
                    logger.info(f"Connected to wallet service: {status}")
                    self.initialized = True
                else:
                    raise Exception(f"Wallet service status check failed: {response.status}")
                    
        except Exception as e:
            logger.error(f"Failed to initialize wallet service: {e}")
            raise
    
    async def connect_wallet(self, address: str, name: Optional[str] = None, 
                           is_hardware_wallet: bool = False) -> Dict[str, Any]:
        """
        Connect a Keplr wallet
        
        Args:
            address: Secret Network address
            name: Wallet name
            is_hardware_wallet: Whether this is a hardware wallet
            
        Returns:
            Connection result
        """
        if not self.initialized:
            await self.initialize()
            
        try:
            async with self.session.post(
                f"{self.mcp_base_url}/api/wallet/connect",
                json={
                    "address": address,
                    "name": name,
                    "isHardwareWallet": is_hardware_wallet
                }
            ) as response:
                result = await response.json()
                
                if response.status == 200 and result.get("success"):
                    logger.info(f"Wallet connected: {address}")
                    return result
                else:
                    logger.error(f"Wallet connection failed: {result}")
                    return result
                    
        except Exception as e:
            logger.error(f"Failed to connect wallet: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_balance(self, address: str) -> Dict[str, Any]:
        """
        Get wallet balance
        
        Args:
            address: Secret Network address
            
        Returns:
            Balance result
        """
        if not self.initialized:
            await self.initialize()
            
        try:
            async with self.session.get(
                f"{self.mcp_base_url}/api/wallet/balance/{address}"
            ) as response:
                result = await response.json()
                
                if response.status == 200 and result.get("success"):
                    logger.info(f"Got balance for {address}: {result.get('formatted')}")
                    return result
                else:
                    logger.error(f"Balance query failed: {result}")
                    return result
                    
        except Exception as e:
            logger.error(f"Failed to get balance: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_transaction_status(self, tx_hash: str) -> Dict[str, Any]:
        """
        Get transaction status
        
        Args:
            tx_hash: Transaction hash
            
        Returns:
            Transaction status
        """
        if not self.initialized:
            await self.initialize()
            
        try:
            async with self.session.get(
                f"{self.mcp_base_url}/api/wallet/transaction/{tx_hash}"
            ) as response:
                result = await response.json()
                
                if response.status == 200 and result.get("success"):
                    logger.info(f"Got tx status for {tx_hash}: {result.get('status')}")
                    return result
                else:
                    logger.error(f"Transaction status query failed: {result}")
                    return result
                    
        except Exception as e:
            logger.error(f"Failed to get transaction status: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_wallet_info(self, address: str) -> Dict[str, Any]:
        """
        Get wallet information
        
        Args:
            address: Secret Network address
            
        Returns:
            Wallet info
        """
        if not self.initialized:
            await self.initialize()
            
        try:
            async with self.session.get(
                f"{self.mcp_base_url}/api/wallet/info/{address}"
            ) as response:
                result = await response.json()
                
                if response.status == 200 and result.get("success"):
                    logger.info(f"Got wallet info for {address}")
                    return result
                elif response.status == 404:
                    return {
                        "success": False,
                        "error": "Wallet not connected"
                    }
                else:
                    logger.error(f"Wallet info query failed: {result}")
                    return result
                    
        except Exception as e:
            logger.error(f"Failed to get wallet info: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def disconnect_wallet(self, address: str) -> Dict[str, Any]:
        """
        Disconnect wallet
        
        Args:
            address: Secret Network address
            
        Returns:
            Disconnect result
        """
        if not self.initialized:
            await self.initialize()
            
        try:
            async with self.session.delete(
                f"{self.mcp_base_url}/api/wallet/disconnect/{address}"
            ) as response:
                result = await response.json()
                
                if response.status == 200:
                    logger.info(f"Wallet disconnected: {address}")
                    return result
                else:
                    logger.error(f"Wallet disconnect failed: {result}")
                    return result
                    
        except Exception as e:
            logger.error(f"Failed to disconnect wallet: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_status(self) -> Dict[str, Any]:
        """
        Get wallet service status
        
        Returns:
            Service status
        """
        if not self.initialized:
            await self.initialize()
            
        try:
            async with self.session.get(
                f"{self.mcp_base_url}/api/wallet/status"
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {
                        "success": False,
                        "error": f"Status check failed: {response.status}"
                    }
                    
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "available": False
            }
    
    async def shutdown(self) -> None:
        """Shutdown wallet service"""
        if self.session:
            await self.session.close()
            self.session = None
        self.initialized = False
        logger.info("HTTP Wallet Service shutdown")