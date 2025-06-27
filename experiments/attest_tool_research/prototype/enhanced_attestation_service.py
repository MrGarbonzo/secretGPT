#!/usr/bin/env python3
"""
Enhanced Attestation Service with secret-vm-attest-rest-server Integration

This prototype shows how to integrate the Secret Labs REST server approach
with your existing secretGPT AttestationService.
"""

import asyncio
import httpx
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class AttestationData:
    """Structured attestation data (matches secretGPT structure)"""
    mrtd: str
    rtmr0: str
    rtmr1: str
    rtmr2: str
    rtmr3: str
    report_data: str
    certificate_fingerprint: str
    timestamp: datetime
    raw_quote: str

class AttestationError(Exception):
    """Custom exception for attestation errors"""
    pass

class EnhancedAttestationService:
    """
    Enhanced Attestation Service with REST server integration
    
    Features:
    - Primary: secret-vm-attest-rest-server JSON API
    - Fallback: Current hardcoded parsing
    - Caching: TTL-based result caching
    - Error handling: Graceful degradation
    """
    
    def __init__(self, rest_server_url: str = "https://localhost:29343"):
        self.rest_server_url = rest_server_url
        self.cache: Dict[str, AttestationData] = {}
        self.cache_ttl = timedelta(minutes=5)
        
        # HTTP client for REST server
        self.client = httpx.AsyncClient(
            verify=False,  # Accept self-signed certificates
            timeout=30.0,
            headers={'User-Agent': 'secretGPT-enhanced-attestation/1.0'}
        )
        
        logger.info(f"Enhanced attestation service initialized with REST server: {rest_server_url}")
    
    async def parse_attestation_quote(self, quote: str, cert_fingerprint: str = "", vm_type: str = "secretvm") -> AttestationData:
        """
        Parse attestation quote with REST server primary, hardcoded fallback
        
        Args:
            quote: Hex attestation quote string
            cert_fingerprint: TLS certificate fingerprint 
            vm_type: VM type identifier
            
        Returns:
            AttestationData with parsed fields
            
        Raises:
            AttestationError: If both methods fail
        """
        cache_key = f"{vm_type}_{quote[:64]}"  # Cache by VM type and quote prefix
        
        # Check cache first
        if self._is_cached_valid(cache_key):
            logger.info(f"Returning cached attestation for {vm_type}")
            return self.cache[cache_key]
        
        # Try REST server first
        try:
            logger.info(f"Attempting REST server attestation for {vm_type}")
            result = await self._parse_with_rest_server(quote, cert_fingerprint, vm_type)
            
            # Cache successful result
            self.cache[cache_key] = result
            logger.info(f"REST server attestation successful for {vm_type}")
            return result
            
        except Exception as e:
            logger.warning(f"REST server attestation failed for {vm_type}: {e}")
            
            # Fallback to hardcoded parsing
            try:
                logger.info(f"Falling back to hardcoded parsing for {vm_type}")
                result = self._parse_with_hardcoded(quote, cert_fingerprint, vm_type)
                
                # Cache fallback result
                self.cache[cache_key] = result
                logger.info(f"Hardcoded parsing successful for {vm_type}")
                return result
                
            except Exception as e2:
                logger.error(f"Both parsing methods failed for {vm_type}: REST={e}, Hardcoded={e2}")
                raise AttestationError(f"All parsing methods failed: REST={e}, Hardcoded={e2}")
    
    async def _parse_with_rest_server(self, quote: str, cert_fingerprint: str, vm_type: str) -> AttestationData:
        """Parse using secret-vm-attest-rest-server"""
        
        # Method 1: Use /cpu endpoint for TDX reports
        try:
            logger.debug(f"Trying /cpu endpoint for {vm_type}")
            response = await self.client.get(f"{self.rest_server_url}/cpu")
            
            if response.status_code == 200:
                return self._parse_rest_response(response.text, cert_fingerprint, quote, "cpu_endpoint")
                
        except Exception as e:
            logger.debug(f"/cpu endpoint failed: {e}")
        
        # Method 2: Use /attestation endpoint with quote data
        try:
            logger.debug(f"Trying /attestation endpoint for {vm_type}")
            
            # Create temporary file or send quote directly
            response = await self.client.post(
                f"{self.rest_server_url}/attestation",
                json={"quote": quote, "format": "json"}
            )
            
            if response.status_code == 200:
                return self._parse_rest_response(response.text, cert_fingerprint, quote, "attestation_endpoint")
                
        except Exception as e:
            logger.debug(f"/attestation endpoint failed: {e}")
        
        # Method 3: Use /self endpoint for self-attestation
        try:
            logger.debug(f"Trying /self endpoint for {vm_type}")
            response = await self.client.get(f"{self.rest_server_url}/self")
            
            if response.status_code == 200:
                return self._parse_rest_response(response.text, cert_fingerprint, quote, "self_endpoint")
                
        except Exception as e:
            logger.debug(f"/self endpoint failed: {e}")
        
        raise AttestationError("All REST server endpoints failed")
    
    def _parse_rest_response(self, response_text: str, cert_fingerprint: str, quote: str, method: str) -> AttestationData:
        """Parse JSON response from REST server"""
        try:
            # Try to parse as JSON first
            if response_text.strip().startswith('{'):
                data = json.loads(response_text)
                
                return AttestationData(
                    mrtd=data.get('mrtd', ''),
                    rtmr0=data.get('rtmr0', ''),
                    rtmr1=data.get('rtmr1', ''),
                    rtmr2=data.get('rtmr2', ''),
                    rtmr3=data.get('rtmr3', ''),
                    report_data=data.get('report_data', ''),
                    certificate_fingerprint=cert_fingerprint,
                    timestamp=datetime.utcnow(),
                    raw_quote=quote
                )
            
            # If not JSON, try to extract hex data (for /cpu endpoint)
            else:
                logger.info(f"Parsing non-JSON response from {method}")
                # Extract hex quote from HTML/text response
                import re
                hex_pattern = r'([0-9a-fA-F]{2000,})'
                matches = re.findall(hex_pattern, response_text)
                
                if matches:
                    extracted_quote = matches[0]
                    logger.info(f"Extracted quote from {method}: {len(extracted_quote)} chars")
                    
                    # Parse the extracted quote with hardcoded method
                    return self._parse_with_hardcoded(extracted_quote, cert_fingerprint, f"extracted_from_{method}")
                
                raise AttestationError(f"No valid data found in {method} response")
                
        except json.JSONDecodeError as e:
            logger.warning(f"JSON parsing failed for {method}: {e}")
            raise AttestationError(f"Invalid JSON response from {method}")
        except Exception as e:
            logger.error(f"Response parsing failed for {method}: {e}")
            raise AttestationError(f"Response parsing failed for {method}: {e}")
    
    def _parse_with_hardcoded(self, quote: str, cert_fingerprint: str, vm_type: str) -> AttestationData:
        """Fallback hardcoded parsing (current secretGPT method)"""
        timestamp = datetime.utcnow()
        
        if not quote or len(quote) < 500:
            raise AttestationError(f"Quote too short for {vm_type}: {len(quote) if quote else 0} chars")
        
        try:
            # Current secretGPT hardcoded parsing logic
            # MRTD: positions 368-464, RTMR0: 752-848, etc.
            
            mrtd = quote[368:464] if len(quote) >= 464 else ""
            rtmr0 = quote[752:848] if len(quote) >= 848 else ""
            rtmr1 = quote[848:944] if len(quote) >= 944 else ""
            rtmr2 = quote[944:1040] if len(quote) >= 1040 else ""
            rtmr3 = quote[1040:1136] if len(quote) >= 1136 else ""
            report_data = quote[128:192] if len(quote) >= 192 else ""
            
            if not all([mrtd, rtmr0, rtmr1, rtmr2, rtmr3]):
                raise AttestationError(f"Incomplete parsing for {vm_type}")
            
            return AttestationData(
                mrtd=mrtd,
                rtmr0=rtmr0,
                rtmr1=rtmr1,
                rtmr2=rtmr2,
                rtmr3=rtmr3,
                report_data=report_data,
                certificate_fingerprint=cert_fingerprint,
                timestamp=timestamp,
                raw_quote=quote
            )
            
        except Exception as e:
            raise AttestationError(f"Hardcoded parsing failed for {vm_type}: {e}")
    
    def _is_cached_valid(self, cache_key: str) -> bool:
        """Check if cached result is still valid"""
        if cache_key not in self.cache:
            return False
        
        attestation = self.cache[cache_key]
        age = datetime.utcnow() - attestation.timestamp
        return age < self.cache_ttl
    
    async def get_status(self) -> Dict[str, Any]:
        """Get service status including REST server connectivity"""
        status = {
            "service": "enhanced_attestation",
            "rest_server_url": self.rest_server_url,
            "cache_entries": len(self.cache),
            "cache_ttl_minutes": self.cache_ttl.total_seconds() / 60
        }
        
        # Test REST server connectivity
        try:
            response = await self.client.get(f"{self.rest_server_url}/status", timeout=5.0)
            status["rest_server_status"] = "online" if response.status_code == 200 else f"error_{response.status_code}"
            status["rest_server_response"] = response.text[:100]
        except Exception as e:
            status["rest_server_status"] = "offline"
            status["rest_server_error"] = str(e)[:100]
        
        return status
    
    async def cleanup(self):
        """Cleanup resources"""
        try:
            await self.client.aclose()
        except Exception as e:
            logger.warning(f"Cleanup warning: {e}")
        logger.info("Enhanced attestation service cleanup complete")


# Example usage and testing
async def test_enhanced_service():
    """Test the enhanced attestation service"""
    
    # Load baseline data
    with open('../findings/current_parser_baseline.json', 'r') as f:
        baseline = json.load(f)
    
    # Initialize service
    service = EnhancedAttestationService()
    
    # Test status
    status = await service.get_status()
    print("Service Status:", json.dumps(status, indent=2))
    
    # Test parsing with production quote
    try:
        with open('../sample_data/known_good_quote.hex', 'r') as f:
            quote = f.read().strip()
        
        result = await service.parse_attestation_quote(quote, "test_cert", "test_vm")
        
        # Compare with baseline
        comparison = {
            'mrtd_match': result.mrtd == baseline['mrtd'],
            'rtmr0_match': result.rtmr0 == baseline['rtmr0'],
            'rtmr1_match': result.rtmr1 == baseline['rtmr1'],
            'rtmr2_match': result.rtmr2 == baseline['rtmr2'],
            'rtmr3_match': result.rtmr3 == baseline['rtmr3'],
        }
        
        print("\nBaseline Comparison:", json.dumps(comparison, indent=2))
        print("All fields match:", all(comparison.values()))
        
        if not all(comparison.values()):
            print("\nMismatches:")
            for field, matches in comparison.items():
                if not matches:
                    baseline_val = baseline[field.replace('_match', '')]
                    result_val = getattr(result, field.replace('_match', ''))
                    print(f"  {field}: baseline={baseline_val[:32]}..., result={result_val[:32]}...")
        
    except Exception as e:
        print(f"Test failed: {e}")
    
    finally:
        await service.cleanup()


if __name__ == "__main__":
    asyncio.run(test_enhanced_service())
