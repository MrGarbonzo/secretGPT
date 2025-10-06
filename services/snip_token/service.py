"""
SNIP Token Service Implementation
Handles SNIP-20 and SNIP-721 token queries with viewing key management
"""
import asyncio
import logging
import json
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

# Import secret.py SDK v1.8.2
from secret_sdk.client.lcd.lcdclient import AsyncLCDClient
from secret_sdk.core import Coins
from secret_sdk.exceptions import LCDResponseError

from .models import (
    SNIPTokenType, ViewingKeyAction, ViewingKeyRequest, 
    SNIPBalanceQuery, SNIPBalanceResponse, SNIPNFT
)
from .config import (
    SNIP_TOKEN_CONTRACTS, SECRET_LCD_ENDPOINT, SNIP_TOKEN_CACHE_TTL,
    HTTP_TIMEOUT, QUERY_RETRY_COUNT, get_token_config, is_supported_token
)

logger = logging.getLogger(__name__)


class ViewingKeyManager:
    """Manages viewing keys for SNIP tokens"""
    
    def __init__(self):
        """Initialize viewing key manager with in-memory storage"""
        self.viewing_keys: Dict[str, Dict[str, str]] = {}  # {wallet_address: {token_symbol: viewing_key}}
        self.key_timestamps: Dict[str, Dict[str, datetime]] = {}  # Track key creation times
    
    def _get_key_id(self, wallet_address: str, token_symbol: str) -> str:
        """Generate unique key ID for wallet-token pair"""
        return f"{wallet_address}:{token_symbol.lower()}"
    
    def has_viewing_key(self, wallet_address: str, token_symbol: str) -> bool:
        """Check if viewing key exists for wallet-token pair"""
        key_id = self._get_key_id(wallet_address, token_symbol)
        return (wallet_address in self.viewing_keys and 
                token_symbol.lower() in self.viewing_keys[wallet_address])
    
    def get_viewing_key(self, wallet_address: str, token_symbol: str) -> Optional[str]:
        """Get viewing key for wallet-token pair"""
        if self.has_viewing_key(wallet_address, token_symbol):
            return self.viewing_keys[wallet_address][token_symbol.lower()]
        return None
    
    def set_viewing_key(self, wallet_address: str, token_symbol: str, viewing_key: str) -> bool:
        """Store viewing key for wallet-token pair"""
        try:
            if wallet_address not in self.viewing_keys:
                self.viewing_keys[wallet_address] = {}
                self.key_timestamps[wallet_address] = {}
            
            self.viewing_keys[wallet_address][token_symbol.lower()] = viewing_key
            self.key_timestamps[wallet_address][token_symbol.lower()] = datetime.now()
            
            logger.info(f"Viewing key stored for {wallet_address}:{token_symbol}")
            return True
        except Exception as e:
            logger.error(f"Failed to store viewing key: {e}")
            return False
    
    def remove_viewing_key(self, wallet_address: str, token_symbol: str) -> bool:
        """Remove viewing key for wallet-token pair"""
        try:
            if (wallet_address in self.viewing_keys and 
                token_symbol.lower() in self.viewing_keys[wallet_address]):
                
                del self.viewing_keys[wallet_address][token_symbol.lower()]
                del self.key_timestamps[wallet_address][token_symbol.lower()]
                
                logger.info(f"Viewing key removed for {wallet_address}:{token_symbol}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to remove viewing key: {e}")
            return False


class SNIPTokenService:
    """
    SNIP Token Service for secretGPT Hub
    Provides SNIP-20 and SNIP-721 token query capabilities
    """
    
    def __init__(self):
        """Initialize SNIP Token Service"""
        self.viewing_key_manager = ViewingKeyManager()
        self.initialized = False
        self.lcd_endpoint = SECRET_LCD_ENDPOINT
        self.cache_ttl = SNIP_TOKEN_CACHE_TTL
        
        # Secret SDK client will be initialized in initialize() method
        self.secret_client: Optional[AsyncLCDClient] = None
        
        logger.info(f"SNIP Token Service initialized with LCD: {self.lcd_endpoint}")
    
    async def initialize(self) -> None:
        """Initialize the SNIP Token Service with Secret SDK v1.8.2"""
        if self.initialized:
            logger.warning("SNIP Token Service already initialized")
            return

        try:
            # Initialize Secret Network LCD client
            logger.info(f"Initializing Secret SDK client with LCD endpoint: {self.lcd_endpoint}")

            self.secret_client = AsyncLCDClient(
                url=self.lcd_endpoint,
                chain_id="secret-4"  # Secret Network mainnet
            )

            # Test connection with a simple query
            try:
                # Try to get latest block info to verify connection
                await self.secret_client.tendermint.block_info()
                logger.info("Secret SDK client connection verified")
            except Exception as conn_error:
                logger.warning(f"Could not verify Secret SDK connection: {conn_error}")
                # Continue anyway - connection might work for contract queries

            self.initialized = True
            logger.info("SNIP Token Service initialized successfully with Secret SDK v1.8.2")

        except Exception as e:
            logger.error(f"Failed to initialize SNIP Token Service: {e}")
            raise
    
    async def get_status(self) -> Dict[str, Any]:
        """Get service status"""
        return {
            "service": "snip_token",
            "status": "initialized" if self.initialized else "not_initialized",
            "lcd_endpoint": self.lcd_endpoint,
            "supported_tokens": list(SNIP_TOKEN_CONTRACTS.keys()),
            "viewing_keys_stored": len(self.viewing_key_manager.viewing_keys),
            "features": {
                "snip20_queries": True,
                "snip721_queries": False,  # TODO: Implement in future phase
                "viewing_key_management": True,
                "query_caching": False     # TODO: Implement caching
            }
        }
    
    def is_snip_token_query(self, message: str) -> Optional[str]:
        """
        Detect if message is asking about SNIP token balance
        Returns token symbol if detected, None otherwise
        """
        message_lower = message.lower()
        
        # Check for supported tokens in the message
        for token_symbol in SNIP_TOKEN_CONTRACTS.keys():
            patterns = [
                f"{token_symbol} balance",
                f"my {token_symbol}",
                f"how much {token_symbol}",
                f"{token_symbol} amount",
                f"balance of {token_symbol}",
                f"check {token_symbol}"
            ]
            
            for pattern in patterns:
                if pattern in message_lower:
                    logger.info(f"SNIP token query detected: {token_symbol}")
                    return token_symbol
        
        return None
    
    async def handle_snip_query(
        self,
        wallet_address: str,
        message: str,
        viewing_keys: Optional[Dict[str, str]] = None,
        viewing_key: Optional[str] = None  # Keep for backward compatibility
    ) -> Dict[str, Any]:
        """
        Handle SNIP token query from user message
        Main entry point for SNIP token queries
        """
        logger.info(f"Handling SNIP query for {wallet_address}: {message}")
        
        # Detect token type
        token_symbol = self.is_snip_token_query(message)
        if not token_symbol:
            return {
                "success": False,
                "error": "No supported SNIP token detected in query"
            }
        
        # Get token configuration
        token_config = get_token_config(token_symbol)
        if not token_config:
            return {
                "success": False,
                "error": f"Unsupported token: {token_symbol}"
            }
        
        # Check for viewing key (priority order: provided keys -> passed key -> stored key)
        logger.info(f"DEBUG: Checking viewing keys for {token_symbol}")
        logger.info(f"DEBUG: viewing_keys parameter: {viewing_keys}")
        logger.info(f"DEBUG: viewing_key parameter: {viewing_key}")

        provided_key = None
        if viewing_keys and token_symbol.lower() in viewing_keys:
            provided_key = viewing_keys[token_symbol.lower()]
            logger.info(f"✅ Using provided viewing key for {token_symbol}: {provided_key[:10]}...")
        else:
            logger.info(f"❌ No provided viewing key found for {token_symbol}")
            if viewing_keys:
                logger.info(f"DEBUG: Available keys in viewing_keys: {list(viewing_keys.keys())}")

        stored_key = self.viewing_key_manager.get_viewing_key(wallet_address, token_symbol)
        if stored_key:
            logger.info(f"Found stored viewing key for {token_symbol}")
        else:
            logger.info(f"No stored viewing key for {token_symbol}")

        active_viewing_key = provided_key or viewing_key or stored_key
        logger.info(f"Final active_viewing_key for {token_symbol}: {'EXISTS' if active_viewing_key else 'NONE'}")
        
        if not active_viewing_key:
            # Return viewing key required response with action flag
            return {
                "success": False,
                "error_type": "viewing_key_required",
                "requires_user_action": True,  # Flag for frontend to auto-trigger Keplr
                "token_symbol": token_symbol,
                "contract_address": token_config.contract_address,
                "message": f"Viewing key required to query {token_symbol.upper()} balance"
            }
        
        # Store viewing key if provided and not already stored
        if viewing_key and not stored_key:
            self.viewing_key_manager.set_viewing_key(wallet_address, token_symbol, viewing_key)
        
        # Query token balance
        try:
            balance_response = await self._query_snip20_balance(
                wallet_address, token_config, active_viewing_key
            )
            return balance_response.to_dict()
            
        except Exception as e:
            logger.error(f"SNIP balance query failed: {e}")
            return {
                "success": False,
                "error": f"Failed to query {token_symbol.upper()} balance: {str(e)}"
            }
    
    async def _query_snip20_balance(
        self,
        address: str,
        token_config,
        viewing_key: str
    ) -> SNIPBalanceResponse:
        """
        Query SNIP-20 token balance using Secret Network LCD client
        Implementation based on dash.scrt.network patterns
        """
        logger.info(f"Querying {token_config.symbol} balance for {address}")

        try:
            # Import batch query contract config
            from .config import BATCH_QUERY_CONTRACT_ADDRESS, BATCH_QUERY_CONTRACT_CODE_HASH

            # Construct batch query message (following dash.scrt.network pattern)
            # Note: Uses camelCase for JavaScript compatibility
            batch_query_msg = {
                "batch": {
                    "queries": [{
                        "id": token_config.contract_address,  # Use contract address as ID
                        "contract": {
                            "address": token_config.contract_address,
                            "codeHash": token_config.code_hash  # camelCase!
                        },
                        "queryMsg": {  # queryMsg, not query!
                            "balance": {
                                "address": address,
                                "key": viewing_key
                            }
                        }
                    }]
                }
            }

            logger.info(f"🔍 SNIP DEBUG - Using batch query contract")
            logger.info(f"🔍 SNIP DEBUG - Batch contract: {BATCH_QUERY_CONTRACT_ADDRESS}")
            logger.info(f"🔍 SNIP DEBUG - Token contract: {token_config.contract_address}")
            logger.info(f"🔍 SNIP DEBUG - Token code hash: {token_config.code_hash}")

            # Execute batch query through the batch query contract
            try:
                batch_result = await self.secret_client.wasm.contract_query(
                    contract_address=BATCH_QUERY_CONTRACT_ADDRESS,
                    query=batch_query_msg,
                    contract_code_hash=BATCH_QUERY_CONTRACT_CODE_HASH
                )
                logger.info(f"🔍 SNIP DEBUG - Batch query result: {batch_result}")

                # Extract the result for our specific token
                if "batch" in batch_result and "results" in batch_result["batch"]:
                    results = batch_result["batch"]["results"]
                    if results and len(results) > 0:
                        result = results[0].get("response", {})
                    else:
                        result = {}
                else:
                    result = batch_result

            except Exception as e:
                logger.error(f"Batch query failed: {e}")
                raise e

            logger.debug(f"Raw query result: {result}")

            # Check for viewing key error (common SNIP-20 error pattern)
            if "viewing_key_error" in result:
                error_msg = result["viewing_key_error"].get("msg", "Invalid viewing key")
                logger.warning(f"Viewing key error for {token_config.symbol}: {error_msg}")

                return SNIPBalanceResponse(
                    success=False,
                    token_symbol=token_config.symbol,
                    error_type="viewing_key_error",
                    error_message=error_msg,
                    viewing_key_required=True,
                    requires_user_action=True,  # Flag for frontend to auto-trigger Keplr
                    contract_address=token_config.contract_address
                )

            # Extract balance from successful response
            if "balance" in result and "amount" in result["balance"]:
                raw_balance = result["balance"]["amount"]

                # Format balance with proper decimals
                formatted_balance = self._format_token_balance(raw_balance, token_config.decimals)

                logger.info(f"Successfully queried {token_config.symbol} balance: {formatted_balance}")

                return SNIPBalanceResponse(
                    success=True,
                    token_symbol=token_config.symbol,
                    balance=raw_balance,
                    formatted_balance=formatted_balance,
                    viewing_key_required=False,
                    contract_address=token_config.contract_address
                )
            else:
                # Unexpected response format
                error_msg = f"Unexpected response format: {result}"
                logger.error(error_msg)

                return SNIPBalanceResponse(
                    success=False,
                    token_symbol=token_config.symbol,
                    error_type="invalid_response",
                    error_message=error_msg,
                    viewing_key_required=False,
                    contract_address=token_config.contract_address
                )

        except LCDResponseError as e:
            # Handle LCD client specific errors
            logger.error(f"LCD error querying {token_config.symbol}: {e}")

            # Check if it's a viewing key related error
            error_msg = str(e)
            is_viewing_key_error = any(keyword in error_msg.lower() for keyword in [
                "viewing key", "unauthorized", "access denied", "forbidden"
            ])

            return SNIPBalanceResponse(
                success=False,
                token_symbol=token_config.symbol,
                error_type="viewing_key_error" if is_viewing_key_error else "lcd_error",
                error_message=error_msg,
                viewing_key_required=is_viewing_key_error,
                requires_user_action=is_viewing_key_error,  # Auto-trigger Keplr if it's a viewing key error
                contract_address=token_config.contract_address
            )

        except Exception as e:
            # Handle unexpected errors
            logger.error(f"Unexpected error querying {token_config.symbol}: {e}")
            return SNIPBalanceResponse(
                success=False,
                token_symbol=token_config.symbol,
                error_type="query_failed",
                error_message=f"Query failed: {str(e)}",
                viewing_key_required=False,
                contract_address=token_config.contract_address
            )

    def _format_token_balance(self, raw_balance: str, decimals: int) -> str:
        """
        Format raw token balance with proper decimal places

        Args:
            raw_balance: Raw balance string from contract (e.g., "1000000")
            decimals: Number of decimal places for the token (e.g., 6 for sSCRT)

        Returns:
            Formatted balance string (e.g., "1.000000")
        """
        try:
            # Convert to integer, then format with decimals
            balance_int = int(raw_balance)

            # Handle zero balance
            if balance_int == 0:
                return "0." + "0" * decimals

            # Convert to decimal format
            balance_decimal = balance_int / (10 ** decimals)

            # Format with appropriate decimal places
            formatted = f"{balance_decimal:.{decimals}f}"

            return formatted

        except (ValueError, TypeError) as e:
            logger.error(f"Error formatting balance {raw_balance}: {e}")
            return "0." + "0" * decimals

    async def set_viewing_key(
        self, 
        wallet_address: str, 
        token_symbol: str, 
        viewing_key: str
    ) -> Dict[str, Any]:
        """Set viewing key for a wallet-token pair"""
        try:
            if not is_supported_token(token_symbol):
                return {
                    "success": False,
                    "error": f"Unsupported token: {token_symbol}"
                }
            
            success = self.viewing_key_manager.set_viewing_key(
                wallet_address, token_symbol, viewing_key
            )
            
            return {
                "success": success,
                "message": f"Viewing key {'stored' if success else 'failed to store'} for {token_symbol.upper()}"
            }
            
        except Exception as e:
            logger.error(f"Failed to set viewing key: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def cleanup(self):
        """Cleanup service resources"""
        try:
            # TODO: Cleanup Secret Network client if needed
            logger.info("SNIP Token Service cleanup complete")
        except Exception as e:
            logger.error(f"SNIP Token Service cleanup error: {e}")