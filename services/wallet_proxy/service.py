"""
Wallet Proxy Service for SecretGPTee VM2 Communication
Handles secure wallet operations and blockchain transactions
"""
import logging
import asyncio
import aiohttp
import json
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class TransactionRequest:
    """Data structure for transaction requests"""
    tx_type: str
    from_address: str
    to_address: Optional[str] = None
    amount: Optional[str] = None
    denom: str = "uscrt"
    gas_limit: str = "200000"
    gas_price: str = "0.25"
    memo: str = ""
    contract_address: Optional[str] = None
    contract_msg: Optional[Dict] = None


class WalletProxyService:
    """
    Wallet Proxy Service for VM2 Communication
    Securely handles wallet operations for SecretGPTee interface
    """
    
    def __init__(self, vm2_endpoint: str = None):
        """Initialize wallet proxy service"""
        # VM2 endpoint for secure wallet operations
        self.vm2_endpoint = vm2_endpoint or "http://67.215.13.103:8003"  # Default VM2 endpoint
        self.session = None
        self.initialized = False
        
        # Transaction cache and status tracking
        self.transaction_cache = {}
        self.connection_status = {
            "vm2_connected": False,
            "last_check": None,
            "error": None
        }
        
        logger.info(f"Wallet proxy service initializing with VM2 endpoint: {self.vm2_endpoint}")
    
    async def initialize(self):
        """Initialize the wallet proxy service"""
        try:
            # Create aiohttp session for VM2 communication
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30),
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": "SecretGPT-WalletProxy/1.0"
                }
            )
            
            # Test VM2 connection
            await self._test_vm2_connection()
            
            self.initialized = True
            logger.info("Wallet proxy service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize wallet proxy service: {e}")
            self.connection_status["error"] = str(e)
            raise
    
    async def _test_vm2_connection(self):
        """Test connection to VM2 wallet service"""
        try:
            if not self.session:
                raise Exception("HTTP session not initialized")
            
            # Ping VM2 health endpoint
            async with self.session.get(f"{self.vm2_endpoint}/health") as response:
                if response.status == 200:
                    self.connection_status["vm2_connected"] = True
                    self.connection_status["last_check"] = datetime.now()
                    self.connection_status["error"] = None
                    logger.info("VM2 wallet service connection successful")
                else:
                    raise Exception(f"VM2 health check failed with status {response.status}")
                    
        except Exception as e:
            self.connection_status["vm2_connected"] = False
            self.connection_status["last_check"] = datetime.now()
            self.connection_status["error"] = str(e)
            logger.warning(f"VM2 connection test failed: {e}")
            # Don't raise exception - allow service to start with VM2 unavailable
    
    async def get_status(self) -> Dict[str, Any]:
        """Get wallet proxy service status"""
        return {
            "service": "wallet_proxy",
            "initialized": self.initialized,
            "vm2_endpoint": self.vm2_endpoint,
            "connection_status": self.connection_status,
            "features": {
                "transaction_preparation": True,
                "balance_queries": True,
                "transaction_signing": False,  # Handled by Keplr client-side
                "multi_wallet_support": True,
                "gas_estimation": True
            },
            "supported_operations": [
                "send_scrt",
                "query_balance", 
                "query_transaction",
                "estimate_gas",
                "prepare_contract_execution"
            ]
        }
    
    async def prepare_transaction(self, tx_type: str, tx_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare a Secret Network transaction for client-side signing
        
        Args:
            tx_type: Type of transaction ("send", "contract_execute", etc.)  
            tx_data: Transaction parameters
            
        Returns:
            Prepared transaction data for Keplr signing
        """
        try:
            logger.info(f"Preparing transaction: {tx_type}")
            
            # Create transaction request
            tx_request = self._build_transaction_request(tx_type, tx_data)
            
            # If VM2 is available, use it for advanced preparation
            if self.connection_status["vm2_connected"]:
                return await self._prepare_via_vm2(tx_request)
            else:
                # Fallback to local preparation
                return await self._prepare_locally(tx_request)
                
        except Exception as e:
            logger.error(f"Transaction preparation failed: {e}")
            raise Exception(f"Failed to prepare transaction: {str(e)}")
    
    def _build_transaction_request(self, tx_type: str, tx_data: Dict[str, Any]) -> TransactionRequest:
        """Build transaction request from input data"""
        try:
            if tx_type == "send":
                return TransactionRequest(
                    tx_type="send",
                    from_address=tx_data.get("from_address"),
                    to_address=tx_data.get("to_address"),
                    amount=tx_data.get("amount"),
                    denom=tx_data.get("denom", "uscrt"),
                    gas_limit=tx_data.get("gas_limit", "200000"),
                    gas_price=tx_data.get("gas_price", "0.25"),
                    memo=tx_data.get("memo", "")
                )
            elif tx_type == "contract_execute":
                return TransactionRequest(
                    tx_type="contract_execute",
                    from_address=tx_data.get("from_address"),
                    contract_address=tx_data.get("contract_address"),
                    contract_msg=tx_data.get("msg"),
                    gas_limit=tx_data.get("gas_limit", "300000"),
                    gas_price=tx_data.get("gas_price", "0.25"),
                    memo=tx_data.get("memo", "")
                )
            else:
                raise ValueError(f"Unsupported transaction type: {tx_type}")
                
        except Exception as e:
            logger.error(f"Failed to build transaction request: {e}")
            raise
    
    async def _prepare_via_vm2(self, tx_request: TransactionRequest) -> Dict[str, Any]:
        """Prepare transaction using VM2 service"""
        try:
            if not self.session:
                raise Exception("HTTP session not available")
            
            # Send preparation request to VM2
            payload = {
                "tx_type": tx_request.tx_type,
                "from_address": tx_request.from_address,
                "to_address": tx_request.to_address,
                "amount": tx_request.amount,
                "denom": tx_request.denom,
                "gas_limit": tx_request.gas_limit,
                "gas_price": tx_request.gas_price,
                "memo": tx_request.memo,
                "contract_address": tx_request.contract_address,
                "contract_msg": tx_request.contract_msg
            }
            
            async with self.session.post(
                f"{self.vm2_endpoint}/api/v1/wallet/prepare",
                json=payload
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info("Transaction prepared via VM2")
                    return result
                else:
                    error_text = await response.text()
                    raise Exception(f"VM2 preparation failed: {error_text}")
                    
        except Exception as e:
            logger.warning(f"VM2 preparation failed, falling back to local: {e}")
            # Fallback to local preparation
            return await self._prepare_locally(tx_request)
    
    async def _prepare_locally(self, tx_request: TransactionRequest) -> Dict[str, Any]:
        """Prepare transaction locally without VM2"""
        try:
            logger.info("Preparing transaction locally")
            
            if tx_request.tx_type == "send":
                # Prepare basic send transaction
                tx_data = {
                    "type": "send_scrt",
                    "chain_id": "secret-4",  # Secret Network mainnet
                    "from_address": tx_request.from_address,
                    "to_address": tx_request.to_address,
                    "amount": [
                        {
                            "denom": tx_request.denom,
                            "amount": str(int(float(tx_request.amount) * 1_000_000))  # Convert to uscrt
                        }
                    ],
                    "gas": tx_request.gas_limit,
                    "gas_price": tx_request.gas_price,
                    "memo": tx_request.memo,
                    "fee": {
                        "amount": [
                            {
                                "denom": "uscrt",
                                "amount": str(int(float(tx_request.gas_limit) * float(tx_request.gas_price)))
                            }
                        ],
                        "gas": tx_request.gas_limit
                    }
                }
                
            elif tx_request.tx_type == "contract_execute":
                # Prepare contract execution transaction
                tx_data = {
                    "type": "execute_contract",
                    "chain_id": "secret-4",
                    "from_address": tx_request.from_address,
                    "contract_address": tx_request.contract_address,
                    "msg": tx_request.contract_msg,
                    "gas": tx_request.gas_limit,
                    "gas_price": tx_request.gas_price,
                    "memo": tx_request.memo,
                    "fee": {
                        "amount": [
                            {
                                "denom": "uscrt",
                                "amount": str(int(float(tx_request.gas_limit) * float(tx_request.gas_price)))
                            }
                        ],
                        "gas": tx_request.gas_limit
                    }
                }
            else:
                raise ValueError(f"Unsupported transaction type: {tx_request.tx_type}")
            
            return {
                "success": True,
                "transaction": tx_data,
                "prepared_by": "local",
                "requires_signing": True,
                "sign_with": "keplr"
            }
            
        except Exception as e:
            logger.error(f"Local transaction preparation failed: {e}")
            raise
    
    async def estimate_gas(self, tx_type: str, tx_data: Dict[str, Any]) -> Dict[str, Any]:
        """Estimate gas for a transaction"""
        try:
            # Default gas estimates
            gas_estimates = {
                "send": "80000",
                "contract_execute": "300000",
                "contract_instantiate": "400000",
                "delegate": "200000",
                "undelegate": "250000"
            }
            
            estimated_gas = gas_estimates.get(tx_type, "200000")
            gas_price = "0.25"  # uscrt per gas unit
            
            # Calculate fee
            fee_amount = str(int(float(estimated_gas) * float(gas_price)))
            
            return {
                "success": True,
                "gas_limit": estimated_gas,
                "gas_price": gas_price,
                "fee": {
                    "amount": fee_amount,
                    "denom": "uscrt"
                },
                "estimated_fee_scrt": str(float(fee_amount) / 1_000_000)
            }
            
        except Exception as e:
            logger.error(f"Gas estimation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }  
    
    async def validate_address(self, address: str) -> Dict[str, Any]:
        """Validate a Secret Network address"""
        try:
            # Basic Secret Network address validation
            if not address.startswith("secret1"):
                return {
                    "valid": False,
                    "error": "Address must start with 'secret1'"
                }
            
            if len(address) != 45:  # secret1 + 38 chars
                return {
                    "valid": False,
                    "error": "Invalid address length"
                }
            
            # Check if address contains only valid characters
            valid_chars = "abcdefghijklmnopqrstuvwxyz0123456789"
            address_suffix = address[7:]  # Remove 'secret1' prefix
            
            if not all(c in valid_chars for c in address_suffix):
                return {
                    "valid": False,
                    "error": "Address contains invalid characters"
                }
            
            return {
                "valid": True,
                "address": address,
                "type": "secret_network"
            }
            
        except Exception as e:
            logger.error(f"Address validation failed: {e}")
            return {
                "valid": False,
                "error": str(e)
            }
    
    async def get_network_info(self) -> Dict[str, Any]:
        """Get Secret Network information"""
        return {
            "chain_id": "secret-4",
            "network_name": "Secret Network",
            "rpc_endpoints": [
                "https://scrt-rpc.mesa-network.io",
                "https://rpc.scrt.network"
            ],
            "rest_endpoints": [
                "https://scrt-api.mesa-network.io",
                "https://api.scrt.network"
            ],
            "native_currency": {
                "name": "Secret",
                "symbol": "SCRT",
                "decimals": 6,
                "denom": "uscrt"
            },
            "explorer_urls": [
                "https://www.mintscan.io/secret",
                "https://secretnodes.com"
            ]
        }
    
    async def cleanup(self):
        """Cleanup wallet proxy service resources"""
        try:
            if self.session:
                await self.session.close()
                self.session = None
            
            self.initialized = False
            logger.info("Wallet proxy service cleanup complete")
            
        except Exception as e:
            logger.error(f"Wallet proxy cleanup error: {e}")


# Factory function for service creation
def create_wallet_proxy_service(vm2_endpoint: str = None) -> WalletProxyService:
    """Create and return a new wallet proxy service instance"""
    return WalletProxyService(vm2_endpoint)