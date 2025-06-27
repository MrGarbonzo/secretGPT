"""Test API endpoints"""

import pytest
import json
from pathlib import Path
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

from main import app
from config.settings import ConfigManager
from hub.service import AttestationHub


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def mock_hub():
    """Create mock attestation hub"""
    hub = AsyncMock(spec=AttestationHub)
    
    # Mock service health
    from hub.models import ServiceHealth, ServiceStatus
    hub.get_service_health.return_value = ServiceHealth(
        status=ServiceStatus.HEALTHY,
        vms_online=2,
        vms_total=2,
        cache_hit_rate=0.8,
        uptime_seconds=3600,
        version="1.0.0"
    )
    
    return hub


@pytest.fixture
def baseline_data():
    """Load baseline data"""
    baseline_file = Path(__file__).parent.parent.parent.parent / "experiments/attest_tool_research/findings/current_parser_baseline.json"
    with open(baseline_file, 'r') as f:
        return json.load(f)


class TestHealthEndpoint:
    """Test health check endpoint"""
    
    def test_health_check(self, client, mock_hub):
        """Test health endpoint returns correct structure"""
        
        with patch('main.attestation_hub', mock_hub):
            response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "status" in data
        assert "vms_online" in data
        assert "vms_total" in data
        assert "cache_hit_rate" in data
        assert "uptime_seconds" in data
        assert "version" in data


class TestAttestationEndpoints:
    """Test attestation endpoints"""
    
    def test_get_vm_attestation_success(self, client, mock_hub, baseline_data):
        """Test successful VM attestation"""
        
        # Mock successful attestation
        from hub.models import AttestationData
        from datetime import datetime
        
        mock_attestation = AttestationData(
            vm_name="secretgpt",
            vm_type="secret-gpt",
            mrtd=baseline_data["mrtd"],
            rtmr0=baseline_data["rtmr0"],
            rtmr1=baseline_data["rtmr1"],
            rtmr2=baseline_data["rtmr2"],
            rtmr3=baseline_data["rtmr3"],
            report_data=baseline_data["report_data"],
            certificate_fingerprint="test_cert",
            timestamp=datetime.utcnow(),
            raw_quote="test_quote",
            parsing_method="hardcoded"
        )
        
        mock_hub.get_attestation.return_value = mock_attestation
        
        with patch('main.attestation_hub', mock_hub):
            response = client.get("/attestation/secretgpt")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
        assert data["data"]["vm_name"] == "secretgpt"
        assert data["data"]["mrtd"] == baseline_data["mrtd"]
        assert data["data"]["parsing_method"] == "hardcoded"
    
    def test_get_vm_attestation_error(self, client, mock_hub):
        """Test VM attestation error handling"""
        
        from hub.models import AttestationError
        mock_hub.get_attestation.side_effect = AttestationError("VM not found")
        
        with patch('main.attestation_hub', mock_hub):
            response = client.get("/attestation/unknown")
        
        assert response.status_code == 200  # Should not be HTTP error
        data = response.json()
        
        assert data["success"] == False
        assert len(data["errors"]) > 0
        assert "VM not found" in data["errors"][0]
    
    def test_dual_attestation_success(self, client, mock_hub, baseline_data):
        """Test dual attestation endpoint"""
        
        from hub.models import AttestationData, DualAttestationData
        from datetime import datetime
        
        # Create mock attestations
        secretai_attestation = AttestationData(
            vm_name="secretai",
            vm_type="secret-ai",
            mrtd="secretai_mrtd",
            rtmr0="secretai_rtmr0",
            rtmr1="secretai_rtmr1",
            rtmr2="secretai_rtmr2",
            rtmr3="secretai_rtmr3",
            report_data="secretai_report",
            certificate_fingerprint="secretai_cert",
            timestamp=datetime.utcnow(),
            raw_quote="",
            parsing_method="hardcoded"
        )
        
        secretgpt_attestation = AttestationData(
            vm_name="secretgpt",
            vm_type="secret-gpt",
            mrtd=baseline_data["mrtd"],
            rtmr0=baseline_data["rtmr0"],
            rtmr1=baseline_data["rtmr1"],
            rtmr2=baseline_data["rtmr2"],
            rtmr3=baseline_data["rtmr3"],
            report_data=baseline_data["report_data"],
            certificate_fingerprint="secretgpt_cert",
            timestamp=datetime.utcnow(),
            raw_quote="",
            parsing_method="hardcoded"
        )
        
        dual_attestation = DualAttestationData(
            secretai=secretai_attestation,
            secretgpt=secretgpt_attestation,
            timestamp=datetime.utcnow(),
            correlation_id="test-correlation-id"
        )
        
        mock_hub.get_dual_attestation.return_value = dual_attestation
        
        with patch('main.attestation_hub', mock_hub):
            response = client.get("/attestation/dual")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
        assert "secretai" in data["data"]
        assert "secretgpt" in data["data"]
        assert data["correlation_id"] == "test-correlation-id"
        
        # Validate secretGPT matches baseline
        secretgpt_data = data["data"]["secretgpt"]
        assert secretgpt_data["mrtd"] == baseline_data["mrtd"]
        assert secretgpt_data["rtmr0"] == baseline_data["rtmr0"]
    
    def test_batch_attestation(self, client, mock_hub, baseline_data):
        """Test batch attestation endpoint"""
        
        from hub.models import AttestationData
        from datetime import datetime
        
        # Mock batch result
        mock_result = {
            "secretgpt": AttestationData(
                vm_name="secretgpt",
                vm_type="secret-gpt",
                mrtd=baseline_data["mrtd"],
                rtmr0=baseline_data["rtmr0"],
                rtmr1=baseline_data["rtmr1"],
                rtmr2=baseline_data["rtmr2"],
                rtmr3=baseline_data["rtmr3"],
                report_data=baseline_data["report_data"],
                certificate_fingerprint="test_cert",
                timestamp=datetime.utcnow(),
                raw_quote="",
                parsing_method="hardcoded"
            )
        }
        
        mock_hub.get_batch_attestations.return_value = mock_result
        
        with patch('main.attestation_hub', mock_hub):
            response = client.post(
                "/attestation/batch",
                json={"vm_names": ["secretgpt"]}
            )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
        assert "secretgpt" in data["data"]
        assert data["data"]["secretgpt"]["mrtd"] == baseline_data["mrtd"]


class TestVMManagementEndpoints:
    """Test VM management endpoints"""
    
    def test_list_vms(self, client, mock_hub):
        """Test list VMs endpoint"""
        
        # Mock VM manager
        mock_vm_manager = AsyncMock()
        mock_vm_manager.list_vms.return_value = {
            "secretgpt": AsyncMock(endpoint="https://localhost:29343", type="secret-gpt"),
            "secretai": AsyncMock(endpoint="https://secretai.scrtlabs.com:29343", type="secret-ai")
        }
        mock_vm_manager.get_all_statuses.return_value = {}
        
        mock_hub.vm_manager = mock_vm_manager
        
        with patch('main.attestation_hub', mock_hub):
            response = client.get("/vms")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "vms" in data
        assert "total" in data
        assert data["total"] >= 0
    
    def test_add_vm_config(self, client, mock_hub):
        """Test add VM configuration endpoint"""
        
        mock_vm_manager = AsyncMock()
        mock_hub.vm_manager = mock_vm_manager
        
        vm_config = {
            "endpoint": "https://new-vm:29343",
            "type": "custom",
            "parsing_strategy": "rest_server",
            "timeout": 30
        }
        
        with patch('main.attestation_hub', mock_hub):
            response = client.post("/vms/new-vm/config", json=vm_config)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
        assert data["vm_name"] == "new-vm"
        mock_vm_manager.add_vm.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])