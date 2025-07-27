"""REST server parser using secret-vm-attest-rest-server"""

import httpx
import json
import re
import logging
from datetime import datetime
from typing import Optional, Dict, Any

from parsers.base import BaseParser, ParserFactory
from config.settings import VMConfig
from hub.models import AttestationData, ParsingError

logger = logging.getLogger(__name__)


class RestServerParser(BaseParser):
    """Parser using secret-vm-attest-rest-server endpoints"""
    
    def __init__(self):
        super().__init__()
        self.client: Optional[httpx.AsyncClient] = None
    
    async def _get_client(self, vm_config: VMConfig) -> httpx.AsyncClient:
        """Get or create HTTP client"""
        if not self.client:
            self.client = httpx.AsyncClient(
                verify=vm_config.tls_verify,
                timeout=httpx.Timeout(vm_config.timeout),
                headers={'User-Agent': 'attestation-hub/1.0'}
            )
        return self.client
    
    async def parse_attestation(
        self, 
        quote: str, 
        vm_config: VMConfig,
        certificate_fingerprint: str = ""
    ) -> AttestationData:
        """Parse using REST server endpoints"""
        
        if not self.validate_quote(quote):
            raise ParsingError("Invalid quote format")
        
        client = await self._get_client(vm_config)
        
        # Try different endpoints in order
        methods = [
            self._try_cpu_endpoint,
            self._try_attestation_endpoint,
            self._try_self_endpoint
        ]
        
        last_error = None
        for method in methods:
            try:
                logger.debug(f"Trying {method.__name__} for {vm_config.endpoint}")
                result = await method(client, vm_config, quote, certificate_fingerprint)
                if result:
                    return result
            except Exception as e:
                last_error = e
                logger.warning(f"{method.__name__} failed: {e}")
        
        raise ParsingError(f"All REST server methods failed. Last error: {last_error}")
    
    async def _try_cpu_endpoint(
        self, 
        client: httpx.AsyncClient,
        vm_config: VMConfig,
        quote: str,
        cert_fingerprint: str
    ) -> Optional[AttestationData]:
        """Try /cpu endpoint for TDX reports"""
        
        response = await client.get(f"{vm_config.endpoint}/cpu")
        
        if response.status_code != 200:
            return None
        
        # Try to parse JSON response first
        try:
            if response.headers.get('content-type', '').startswith('application/json'):
                data = response.json()
                return self._parse_json_response(data, vm_config, quote, cert_fingerprint)
        except:
            pass
        
        # Otherwise try to extract hex quote from HTML/text
        hex_pattern = r'([0-9a-fA-F]{2000,})'
        matches = re.findall(hex_pattern, response.text)
        
        if matches:
            extracted_quote = matches[0]
            logger.info(f"Extracted quote from /cpu: {len(extracted_quote)} chars")
            # Parse with hardcoded offsets
            from parsers.hardcoded import HardcodedParser
            parser = HardcodedParser()
            return await parser.parse_attestation(extracted_quote, vm_config, cert_fingerprint)
        
        return None
    
    async def _try_attestation_endpoint(
        self,
        client: httpx.AsyncClient,
        vm_config: VMConfig,
        quote: str,
        cert_fingerprint: str
    ) -> Optional[AttestationData]:
        """Try /attestation endpoint"""
        
        # Try POST with quote data
        response = await client.post(
            f"{vm_config.endpoint}/attestation",
            json={"quote": quote, "format": "json"}
        )
        
        if response.status_code != 200:
            return None
        
        try:
            data = response.json()
            return self._parse_json_response(data, vm_config, quote, cert_fingerprint)
        except:
            return None
    
    async def _try_self_endpoint(
        self,
        client: httpx.AsyncClient,
        vm_config: VMConfig,
        quote: str,
        cert_fingerprint: str
    ) -> Optional[AttestationData]:
        """Try /self endpoint for self-attestation"""
        
        response = await client.get(f"{vm_config.endpoint}/self")
        
        if response.status_code != 200:
            return None
        
        try:
            data = response.json()
            return self._parse_json_response(data, vm_config, quote, cert_fingerprint)
        except:
            return None
    
    def _parse_json_response(
        self,
        data: Dict[str, Any],
        vm_config: VMConfig,
        quote: str,
        cert_fingerprint: str
    ) -> AttestationData:
        """Parse JSON response from REST server"""
        
        # Extract fields from JSON
        vm_name = data.get('vm_name', vm_config.endpoint.split('//')[1].split(':')[0])
        
        return AttestationData(
            vm_name=vm_name,
            vm_type=vm_config.type,
            mrtd=data.get('mrtd', ''),
            rtmr0=data.get('rtmr0', ''),
            rtmr1=data.get('rtmr1', ''),
            rtmr2=data.get('rtmr2', ''),
            rtmr3=data.get('rtmr3', ''),
            report_data=data.get('report_data', ''),
            certificate_fingerprint=cert_fingerprint or data.get('certificate_fingerprint', ''),
            timestamp=datetime.utcnow(),
            raw_quote=quote,
            parsing_method="rest_server"
        )
    
    async def health_check(self, vm_config: VMConfig) -> bool:
        """Check REST server health"""
        try:
            client = await self._get_client(vm_config)
            response = await client.get(
                f"{vm_config.endpoint}{vm_config.health_check_path}",
                timeout=5.0
            )
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"Health check failed for {vm_config.endpoint}: {e}")
            return False
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.client:
            await self.client.aclose()
            self.client = None


# Register parser
ParserFactory.register_parser("rest_server", RestServerParser)