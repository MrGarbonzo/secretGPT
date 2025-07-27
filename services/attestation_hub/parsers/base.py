"""Base parser interface and factory"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import logging

from config.settings import VMConfig
from hub.models import AttestationData, ParsingError

logger = logging.getLogger(__name__)


class BaseParser(ABC):
    """Abstract base class for attestation parsers"""
    
    def __init__(self):
        self.name = self.__class__.__name__
    
    @abstractmethod
    async def parse_attestation(
        self, 
        quote: str, 
        vm_config: VMConfig,
        certificate_fingerprint: str = ""
    ) -> AttestationData:
        """
        Parse attestation quote using specific strategy
        
        Args:
            quote: Hex attestation quote string
            vm_config: VM configuration
            certificate_fingerprint: TLS certificate fingerprint
            
        Returns:
            AttestationData with parsed fields
            
        Raises:
            ParsingError: If parsing fails
        """
        pass
    
    @abstractmethod
    async def health_check(self, vm_config: VMConfig) -> bool:
        """
        Check if parser is healthy for given VM
        
        Args:
            vm_config: VM configuration
            
        Returns:
            True if healthy, False otherwise
        """
        pass
    
    def validate_quote(self, quote: str) -> bool:
        """Validate quote format"""
        if not quote:
            return False
        
        # Check if it's a hex string
        try:
            int(quote, 16)
        except ValueError:
            return False
        
        # Check minimum length (TDX quotes are typically > 2000 chars)
        if len(quote) < 2000:
            logger.warning(f"Quote too short: {len(quote)} characters")
            return False
        
        return True


class ParserFactory:
    """Factory for creating parser instances"""
    
    _parsers: Dict[str, type[BaseParser]] = {}
    
    @classmethod
    def register_parser(cls, name: str, parser_class: type[BaseParser]):
        """Register a parser implementation"""
        cls._parsers[name] = parser_class
        logger.info(f"Registered parser: {name}")
    
    @classmethod
    def create_parser(cls, strategy: str) -> Optional[BaseParser]:
        """Create parser instance by strategy name"""
        parser_class = cls._parsers.get(strategy)
        if not parser_class:
            logger.error(f"Unknown parser strategy: {strategy}")
            return None
        
        return parser_class()
    
    @classmethod
    def list_parsers(cls) -> list[str]:
        """List available parser strategies"""
        return list(cls._parsers.keys())