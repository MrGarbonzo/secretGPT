"""
Data models for SNIP Token Service
"""
from dataclasses import dataclass
from typing import Optional, Dict, Any
from enum import Enum


class SNIPTokenType(Enum):
    """SNIP token types"""
    SNIP20 = "snip20"
    SNIP721 = "snip721"


class ViewingKeyAction(Enum):
    """Viewing key management actions"""
    CHECK = "check"
    CREATE = "create"
    SET = "set"
    REMOVE = "remove"


@dataclass
class ViewingKeyRequest:
    """Request for viewing key operations"""
    wallet_address: str
    token_symbol: str
    contract_address: str
    action: ViewingKeyAction
    viewing_key: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "wallet_address": self.wallet_address,
            "token_symbol": self.token_symbol, 
            "contract_address": self.contract_address,
            "action": self.action.value,
            "viewing_key": self.viewing_key
        }


@dataclass
class SNIPBalanceQuery:
    """SNIP token balance query parameters"""
    address: str
    token_symbol: str
    contract_address: str
    viewing_key: Optional[str] = None
    token_type: SNIPTokenType = SNIPTokenType.SNIP20
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "address": self.address,
            "token_symbol": self.token_symbol,
            "contract_address": self.contract_address,
            "viewing_key": self.viewing_key,
            "token_type": self.token_type.value
        }


@dataclass
class SNIPBalanceResponse:
    """SNIP token balance query response"""
    success: bool
    token_symbol: str
    balance: Optional[str] = None
    formatted_balance: Optional[str] = None
    error_type: Optional[str] = None
    error_message: Optional[str] = None
    viewing_key_required: bool = False
    requires_user_action: bool = False  # Flag for frontend to auto-trigger Keplr
    contract_address: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "token_symbol": self.token_symbol,
            "balance": self.balance,
            "formatted_balance": self.formatted_balance,
            "error_type": self.error_type,
            "error_message": self.error_message,
            "viewing_key_required": self.viewing_key_required,
            "requires_user_action": self.requires_user_action,
            "contract_address": self.contract_address
        }


@dataclass
class SNIPNFT:
    """SNIP-721 NFT data"""
    token_id: str
    contract_address: str
    metadata: Optional[Dict[str, Any]] = None
    owner: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "token_id": self.token_id,
            "contract_address": self.contract_address,
            "metadata": self.metadata,
            "owner": self.owner
        }