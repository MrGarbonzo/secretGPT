"""Hardcoded parser using byte offsets (fallback)"""

import logging
from datetime import datetime

from parsers.base import BaseParser, ParserFactory
from config.settings import VMConfig
from hub.models import AttestationData, ParsingError

logger = logging.getLogger(__name__)


class HardcodedParser(BaseParser):
    """Fallback parser using hardcoded byte offsets (current secretGPT method)"""
    
    # Byte offsets for TDX quote fields (from research)
    OFFSETS = {
        "report_data": (128, 192),    # 64 hex chars (32 bytes)
        "mrtd": (368, 464),           # 96 hex chars (48 bytes)
        "rtmr0": (752, 848),          # 96 hex chars (48 bytes)
        "rtmr1": (848, 944),          # 96 hex chars (48 bytes)
        "rtmr2": (944, 1040),         # 96 hex chars (48 bytes)
        "rtmr3": (1040, 1136),        # 96 hex chars (48 bytes)
    }
    
    async def parse_attestation(
        self, 
        quote: str, 
        vm_config: VMConfig,
        certificate_fingerprint: str = ""
    ) -> AttestationData:
        """Parse using hardcoded byte positions"""
        
        if not self.validate_quote(quote):
            raise ParsingError("Invalid quote format")
        
        try:
            # Extract fields using hardcoded offsets
            report_data = self._extract_field(quote, "report_data")
            mrtd = self._extract_field(quote, "mrtd")
            rtmr0 = self._extract_field(quote, "rtmr0")
            rtmr1 = self._extract_field(quote, "rtmr1")
            rtmr2 = self._extract_field(quote, "rtmr2")
            rtmr3 = self._extract_field(quote, "rtmr3")
            
            # Validate all fields were extracted
            if not all([mrtd, rtmr0, rtmr1, rtmr2, rtmr3]):
                raise ParsingError("Failed to extract all required fields")
            
            # Get VM name from endpoint
            vm_name = vm_config.endpoint.split('//')[1].split(':')[0]
            if vm_name == "localhost":
                vm_name = "secretgpt"
            elif "secretai" in vm_name:
                vm_name = "secretai"
            
            return AttestationData(
                vm_name=vm_name,
                vm_type=vm_config.type,
                mrtd=mrtd,
                rtmr0=rtmr0,
                rtmr1=rtmr1,
                rtmr2=rtmr2,
                rtmr3=rtmr3,
                report_data=report_data,
                certificate_fingerprint=certificate_fingerprint,
                timestamp=datetime.utcnow(),
                raw_quote=quote,
                parsing_method="hardcoded"
            )
            
        except Exception as e:
            logger.error(f"Hardcoded parsing failed: {e}")
            raise ParsingError(f"Hardcoded parsing failed: {e}")
    
    def _extract_field(self, quote: str, field_name: str) -> str:
        """Extract field from quote using offset"""
        start, end = self.OFFSETS[field_name]
        
        if len(quote) < end:
            logger.warning(f"Quote too short for {field_name}: {len(quote)} < {end}")
            return ""
        
        value = quote[start:end]
        logger.debug(f"Extracted {field_name}: {value[:32]}...")
        return value
    
    async def health_check(self, vm_config: VMConfig) -> bool:
        """Hardcoded parser is always healthy"""
        return True
    
    def validate_baseline(self, attestation_data: AttestationData, baseline: dict) -> dict:
        """Validate parsed data against baseline"""
        validation = {
            "mrtd_match": attestation_data.mrtd == baseline.get("mrtd", ""),
            "rtmr0_match": attestation_data.rtmr0 == baseline.get("rtmr0", ""),
            "rtmr1_match": attestation_data.rtmr1 == baseline.get("rtmr1", ""),
            "rtmr2_match": attestation_data.rtmr2 == baseline.get("rtmr2", ""),
            "rtmr3_match": attestation_data.rtmr3 == baseline.get("rtmr3", ""),
            "report_data_match": attestation_data.report_data == baseline.get("report_data", ""),
        }
        
        validation["all_match"] = all(validation.values())
        return validation


# Register parser
ParserFactory.register_parser("hardcoded", HardcodedParser)