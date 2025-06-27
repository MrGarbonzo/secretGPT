"""Test parsers with baseline validation"""

import pytest
import json
import os
from pathlib import Path

from parsers.hardcoded import HardcodedParser
from parsers.rest_server import RestServerParser
from config.settings import VMConfig


class TestHardcodedParser:
    """Test hardcoded parser implementation"""
    
    @pytest.fixture
    def parser(self):
        return HardcodedParser()
    
    @pytest.fixture
    def test_quote(self):
        """Load test quote"""
        test_file = Path(__file__).parent.parent.parent.parent / "experiments/attest_tool_research/sample_data/known_good_quote.hex"
        with open(test_file, 'r') as f:
            return f.read().strip()
    
    @pytest.fixture
    def baseline_data(self):
        """Load baseline data"""
        baseline_file = Path(__file__).parent.parent.parent.parent / "experiments/attest_tool_research/findings/current_parser_baseline.json"
        with open(baseline_file, 'r') as f:
            return json.load(f)
    
    @pytest.fixture
    def vm_config(self):
        return VMConfig(
            endpoint="https://localhost:29343",
            type="secret-gpt",
            parsing_strategy="hardcoded"
        )
    
    async def test_parse_baseline_quote(self, parser, test_quote, baseline_data, vm_config):
        """Test parsing with baseline validation"""
        
        # Parse the quote
        attestation = await parser.parse_attestation(test_quote, vm_config, "test_cert")
        
        # Validate against baseline
        assert attestation.mrtd == baseline_data["mrtd"], f"MRTD mismatch: got {attestation.mrtd[:32]}..., expected {baseline_data['mrtd'][:32]}..."
        assert attestation.rtmr0 == baseline_data["rtmr0"], f"RTMR0 mismatch"
        assert attestation.rtmr1 == baseline_data["rtmr1"], f"RTMR1 mismatch"
        assert attestation.rtmr2 == baseline_data["rtmr2"], f"RTMR2 mismatch"
        assert attestation.rtmr3 == baseline_data["rtmr3"], f"RTMR3 mismatch"
        assert attestation.report_data == baseline_data["report_data"], f"Report data mismatch"
        
        # Validate metadata
        assert attestation.vm_name == "secretgpt"
        assert attestation.vm_type == "secret-gpt"
        assert attestation.parsing_method == "hardcoded"
        assert attestation.certificate_fingerprint == "test_cert"
        assert attestation.raw_quote == test_quote
    
    async def test_field_lengths(self, parser, test_quote, vm_config):
        """Test that extracted fields have correct lengths"""
        
        attestation = await parser.parse_attestation(test_quote, vm_config, "")
        
        # All RTMRs and MRTD should be 96 hex chars (48 bytes)
        assert len(attestation.mrtd) == 96, f"MRTD length: {len(attestation.mrtd)}"
        assert len(attestation.rtmr0) == 96, f"RTMR0 length: {len(attestation.rtmr0)}"
        assert len(attestation.rtmr1) == 96, f"RTMR1 length: {len(attestation.rtmr1)}"
        assert len(attestation.rtmr2) == 96, f"RTMR2 length: {len(attestation.rtmr2)}"
        assert len(attestation.rtmr3) == 96, f"RTMR3 length: {len(attestation.rtmr3)}"
        
        # Report data should be 64 hex chars (32 bytes)
        assert len(attestation.report_data) == 64, f"Report data length: {len(attestation.report_data)}"
    
    async def test_baseline_validation_helper(self, parser, test_quote, baseline_data, vm_config):
        """Test the baseline validation helper method"""
        
        attestation = await parser.parse_attestation(test_quote, vm_config, "")
        validation = parser.validate_baseline(attestation, baseline_data)
        
        # All fields should match
        assert validation["all_match"], f"Validation failed: {validation}"
        assert validation["mrtd_match"], "MRTD validation failed"
        assert validation["rtmr0_match"], "RTMR0 validation failed"
        assert validation["rtmr1_match"], "RTMR1 validation failed"
        assert validation["rtmr2_match"], "RTMR2 validation failed"
        assert validation["rtmr3_match"], "RTMR3 validation failed"
        assert validation["report_data_match"], "Report data validation failed"
    
    async def test_invalid_quote(self, parser, vm_config):
        """Test handling of invalid quotes"""
        
        with pytest.raises(Exception):
            await parser.parse_attestation("", vm_config, "")
        
        with pytest.raises(Exception):
            await parser.parse_attestation("not_hex", vm_config, "")
        
        with pytest.raises(Exception):
            await parser.parse_attestation("123", vm_config, "")  # Too short
    
    async def test_health_check(self, parser, vm_config):
        """Test parser health check"""
        
        # Hardcoded parser should always be healthy
        assert await parser.health_check(vm_config) == True


class TestRestServerParser:
    """Test REST server parser implementation"""
    
    @pytest.fixture
    def parser(self):
        return RestServerParser()
    
    @pytest.fixture
    def vm_config(self):
        return VMConfig(
            endpoint="https://localhost:29343",
            type="secret-gpt",
            parsing_strategy="rest_server",
            tls_verify=False
        )
    
    async def test_health_check_offline(self, parser, vm_config):
        """Test health check when server is offline"""
        
        # Should return False for offline server
        result = await parser.health_check(vm_config)
        assert result == False
    
    async def test_parse_invalid_quote(self, parser, vm_config):
        """Test parsing invalid quote"""
        
        with pytest.raises(Exception):
            await parser.parse_attestation("invalid", vm_config, "")
    
    async def test_cleanup(self, parser):
        """Test parser cleanup"""
        
        # Should not raise exception
        await parser.cleanup()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])