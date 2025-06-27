"""Integration tests for attestation hub service"""

import pytest
import asyncio
import json
from pathlib import Path

from config.settings import ConfigManager
from hub.service import AttestationHub
from hub.models import AttestationError


class TestAttestationHub:
    """Test AttestationHub service integration"""
    
    @pytest.fixture
    async def hub(self):
        """Create test hub instance"""
        config_manager = ConfigManager()
        hub = AttestationHub(config_manager)
        yield hub
        await hub.cleanup()
    
    @pytest.fixture
    def baseline_data(self):
        """Load baseline data"""
        baseline_file = Path(__file__).parent.parent.parent.parent / "experiments/attest_tool_research/findings/current_parser_baseline.json"
        with open(baseline_file, 'r') as f:
            return json.load(f)
    
    async def test_get_service_health(self, hub):
        """Test service health check"""
        
        health = hub.get_service_health()
        
        assert health.version == "1.0.0"
        assert health.vms_total >= 2  # At least secretai and secretgpt
        assert health.uptime_seconds >= 0
        assert 0.0 <= health.cache_hit_rate <= 1.0
        assert health.status in ["healthy", "degraded", "unhealthy"]
    
    async def test_vm_configuration(self, hub):
        """Test VM configuration management"""
        
        # Check default VMs are configured
        vms = hub.vm_manager.list_vms()
        assert "secretai" in vms
        assert "secretgpt" in vms
        
        # Check secretgpt configuration
        secretgpt_config = hub.vm_manager.get_vm_config("secretgpt")
        assert secretgpt_config is not None
        assert secretgpt_config.type == "secret-gpt"
        assert secretgpt_config.parsing_strategy == "rest_server"
        assert secretgpt_config.fallback_strategy == "hardcoded"
    
    async def test_cache_functionality(self, hub):
        """Test attestation caching"""
        
        # Initial cache should be empty
        assert hub.get_cache_hit_rate() == 0.0
        
        # Cache a test attestation
        from hub.models import AttestationData
        from datetime import datetime
        
        test_attestation = AttestationData(
            vm_name="test",
            vm_type="test",
            mrtd="test_mrtd",
            rtmr0="test_rtmr0",
            rtmr1="test_rtmr1",
            rtmr2="test_rtmr2",
            rtmr3="test_rtmr3",
            report_data="test_report",
            certificate_fingerprint="test_cert",
            timestamp=datetime.utcnow(),
            raw_quote="test_quote",
            parsing_method="test"
        )
        
        hub._cache_attestation("test", test_attestation)
        
        # Should be able to retrieve from cache
        cached = hub._get_cached_attestation("test")
        assert cached is not None
        assert cached.vm_name == "test"
    
    async def test_unknown_vm(self, hub):
        """Test handling of unknown VM"""
        
        with pytest.raises(AttestationError) as exc_info:
            await hub.get_attestation("unknown_vm")
        
        assert "VM not configured" in str(exc_info.value)
    
    async def test_batch_attestations_empty(self, hub):
        """Test batch attestations with empty list"""
        
        result = await hub.get_batch_attestations([])
        assert result == {}
    
    async def test_batch_attestations_invalid_vm(self, hub):
        """Test batch attestations with invalid VM"""
        
        with pytest.raises(AttestationError) as exc_info:
            await hub.get_batch_attestations(["unknown_vm"])
        
        assert "Unknown VMs" in str(exc_info.value)


class TestAttestationHubIntegration:
    """End-to-end integration tests"""
    
    @pytest.fixture
    async def hub(self):
        """Create test hub instance with test data path"""
        config_manager = ConfigManager()
        hub = AttestationHub(config_manager)
        
        # Mock the quote fetching to use test data
        original_fetch = hub._fetch_quote_from_vm
        
        async def mock_fetch_quote(vm_name, vm_config):
            # Return test quote for any VM
            test_file = Path(__file__).parent.parent.parent.parent / "experiments/attest_tool_research/sample_data/known_good_quote.hex"
            if test_file.exists():
                with open(test_file, 'r') as f:
                    return f.read().strip()
            else:
                raise Exception("Test quote file not found")
        
        hub._fetch_quote_from_vm = mock_fetch_quote
        
        yield hub
        
        # Restore original method
        hub._fetch_quote_from_vm = original_fetch
        await hub.cleanup()
    
    @pytest.fixture
    def baseline_data(self):
        """Load baseline data"""
        baseline_file = Path(__file__).parent.parent.parent.parent / "experiments/attest_tool_research/findings/current_parser_baseline.json"
        with open(baseline_file, 'r') as f:
            return json.load(f)
    
    async def test_secretgpt_attestation_with_fallback(self, hub, baseline_data):
        """Test secretGPT attestation using fallback parser"""
        
        # This should use fallback since REST server is not available
        attestation = await hub.get_attestation("secretgpt")
        
        # Validate against baseline
        assert attestation.vm_name == "secretgpt"
        assert attestation.vm_type == "secret-gpt"
        assert attestation.mrtd == baseline_data["mrtd"]
        assert attestation.rtmr0 == baseline_data["rtmr0"]
        assert attestation.rtmr1 == baseline_data["rtmr1"]
        assert attestation.rtmr2 == baseline_data["rtmr2"]
        assert attestation.rtmr3 == baseline_data["rtmr3"]
        assert attestation.report_data == baseline_data["report_data"]
        
        # Should be using hardcoded fallback parser
        assert attestation.parsing_method == "hardcoded"
    
    async def test_dual_attestation_integration(self, hub, baseline_data):
        """Test dual attestation integration"""
        
        dual = await hub.get_dual_attestation()
        
        # Should have both attestations
        assert dual.secretai is not None
        assert dual.secretgpt is not None
        assert dual.correlation_id is not None
        
        # secretGPT should match baseline
        assert dual.secretgpt.mrtd == baseline_data["mrtd"]
        assert dual.secretgpt.rtmr0 == baseline_data["rtmr0"]
        
        # Both should be using fallback parser
        assert dual.secretai.parsing_method == "hardcoded"
        assert dual.secretgpt.parsing_method == "hardcoded"
    
    async def test_cache_hit_on_second_request(self, hub):
        """Test that second request hits cache"""
        
        # First request
        attestation1 = await hub.get_attestation("secretgpt")
        cache_hit_rate_1 = hub.get_cache_hit_rate()
        
        # Second request should hit cache
        attestation2 = await hub.get_attestation("secretgpt")
        cache_hit_rate_2 = hub.get_cache_hit_rate()
        
        # Cache hit rate should increase
        assert cache_hit_rate_2 > cache_hit_rate_1
        
        # Attestations should be identical
        assert attestation1.mrtd == attestation2.mrtd
        assert attestation1.timestamp == attestation2.timestamp


if __name__ == "__main__":
    pytest.main([__file__, "-v"])