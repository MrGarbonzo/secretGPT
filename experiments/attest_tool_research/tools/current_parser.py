#!/usr/bin/env python3
"""
Current Parser Emulator - Extract current parsing logic for comparison

This script replicates the current hardcoded parsing logic from secretGPT
to enable comparison with attest_tool output.
"""

import sys
import os
from typing import Dict, Any
from dataclasses import dataclass
from datetime import datetime

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


def parse_quote_hardcoded(quote: str, cert_fingerprint: str = "test_cert") -> AttestationData:
    """
    Parse attestation quote using current hardcoded method
    Based on secretGPT's _parse_attestation_quote method
    """
    timestamp = datetime.utcnow()
    
    # If quote is empty or too short, return error values
    if not quote or len(quote) < 500:
        return AttestationData(
            mrtd="error_no_quote",
            rtmr0="error_no_quote",
            rtmr1="error_no_quote",
            rtmr2="error_no_quote",
            rtmr3="error_no_quote",
            report_data="error_no_quote",
            certificate_fingerprint=cert_fingerprint,
            timestamp=timestamp,
            raw_quote=quote
        )
    
    try:
        # Parse hex quote to extract attestation fields
        # Using exact byte positions from TDX quote structure analysis
        
        # Convert hex string to bytes for parsing
        quote_bytes = bytes.fromhex(quote)
        
        # Exact byte offsets from secretGPT:
        # MRTD: Bytes 184-232 (48 bytes / 384 bits)
        # RTMR0: Bytes 376-424 (48 bytes / 384 bits)  
        # RTMR1: Bytes 424-472 (48 bytes / 384 bits)
        # RTMR2: Bytes 472-520 (48 bytes / 384 bits)
        # RTMR3: Bytes 520-568 (48 bytes / 384 bits)
        
        # Extract MRTD (48 bytes at offset 184)
        mrtd_bytes = quote_bytes[184:232]
        mrtd = mrtd_bytes.hex()
        
        # Extract RTMR0 (48 bytes at offset 376)
        rtmr0_bytes = quote_bytes[376:424]
        rtmr0 = rtmr0_bytes.hex()
        
        # Extract RTMR1 (48 bytes at offset 424)
        rtmr1_bytes = quote_bytes[424:472]
        rtmr1 = rtmr1_bytes.hex()
        
        # Extract RTMR2 (48 bytes at offset 472)
        rtmr2_bytes = quote_bytes[472:520]
        rtmr2 = rtmr2_bytes.hex()
        
        # Extract RTMR3 (48 bytes at offset 520)
        rtmr3_bytes = quote_bytes[520:568]
        rtmr3 = rtmr3_bytes.hex()
        
        # Report data (64 bytes near the beginning of quote)
        report_data_bytes = quote_bytes[64:96]  # 32 bytes
        report_data = report_data_bytes.hex()
        
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
        # Return error values instead of mock
        return AttestationData(
            mrtd="parse_error",
            rtmr0="parse_error",
            rtmr1="parse_error",
            rtmr2="parse_error",
            rtmr3="parse_error",
            report_data="parse_error",
            certificate_fingerprint=cert_fingerprint,
            timestamp=timestamp,
            raw_quote=quote[:100] + "..." if quote else ""
        )


def parse_quote_from_file(quote_file: str) -> AttestationData:
    """Parse attestation quote from hex file"""
    try:
        with open(quote_file, 'r') as f:
            quote_hex = f.read().strip()
        
        return parse_quote_hardcoded(quote_hex)
        
    except Exception as e:
        print(f"Error reading quote file {quote_file}: {e}")
        return None


def format_attestation_for_comparison(attestation: AttestationData) -> Dict[str, Any]:
    """Format attestation data for comparison with attest_tool"""
    return {
        "mrtd": attestation.mrtd,
        "rtmr0": attestation.rtmr0,
        "rtmr1": attestation.rtmr1,
        "rtmr2": attestation.rtmr2,
        "rtmr3": attestation.rtmr3,
        "report_data": attestation.report_data,
        "certificate_fingerprint": attestation.certificate_fingerprint,
        "timestamp": attestation.timestamp.isoformat(),
        "parsing_method": "hardcoded_secretgpt",
        "raw_quote_length": len(attestation.raw_quote)
    }


def main():
    """Test current parsing with sample data"""
    if len(sys.argv) != 2:
        print("Usage: python current_parser.py <quote_file.hex>")
        return 1
    
    quote_file = sys.argv[1]
    
    if not os.path.exists(quote_file):
        print(f"Quote file not found: {quote_file}")
        return 1
    
    print(f"Parsing quote file: {quote_file}")
    
    # Parse with current method
    attestation = parse_quote_from_file(quote_file)
    
    if attestation is None:
        print("Failed to parse quote")
        return 1
    
    # Format and display results
    result = format_attestation_for_comparison(attestation)
    
    import json
    print(json.dumps(result, indent=2))
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
