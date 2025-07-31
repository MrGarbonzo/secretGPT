"""
Wallet Proxy Service Package
Secure wallet operations for SecretGPTee interface
"""
from .service import WalletProxyService, create_wallet_proxy_service

__all__ = ["WalletProxyService", "create_wallet_proxy_service"]