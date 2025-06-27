"""Client library for accessing Attestation Hub Service"""

import httpx
import logging
from typing import Dict, List, Optional
from datetime import datetime

from hub.models import AttestationData, DualAttestationData, AttestationError

logger = logging.getLogger(__name__)


class AttestationHubClient:
    """Lightweight client for other services to consume attestations"""
    
    def __init__(self, base_url: str, timeout: int = 30, api_key: Optional[str] = None):
        """
        Initialize client with hub URL
        
        Args:
            base_url: Base URL of attestation hub service
            timeout: Request timeout in seconds
            api_key: Optional API key for authentication
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        
        headers = {'User-Agent': 'attestation-hub-client/1.0'}
        if api_key:
            headers['Authorization'] = f'Bearer {api_key}'
        
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(timeout),
            headers=headers
        )
        
        logger.info(f"AttestationHubClient initialized: {base_url}")
    
    async def get_attestation(self, vm_name: str) -> AttestationData:
        """
        Get attestation for specific VM
        
        Args:
            vm_name: Name of VM to get attestation for
            
        Returns:
            AttestationData with parsed fields
            
        Raises:
            AttestationError: If request fails
        """
        try:
            response = await self.client.get(f"{self.base_url}/attestation/{vm_name}")
            
            if response.status_code != 200:
                raise AttestationError(f"HTTP {response.status_code}: {response.text}")
            
            data = response.json()
            
            if not data.get('success'):
                errors = data.get('errors', ['Unknown error'])
                raise AttestationError(f"Attestation failed: {'; '.join(errors)}")
            
            attestation_data = data['data']
            
            return AttestationData(
                vm_name=attestation_data['vm_name'],
                vm_type=attestation_data['vm_type'],
                mrtd=attestation_data['mrtd'],
                rtmr0=attestation_data['rtmr0'],
                rtmr1=attestation_data['rtmr1'],
                rtmr2=attestation_data['rtmr2'],
                rtmr3=attestation_data['rtmr3'],
                report_data=attestation_data['report_data'],
                certificate_fingerprint=attestation_data['certificate_fingerprint'],
                timestamp=datetime.fromisoformat(attestation_data['timestamp'].replace('Z', '+00:00')),
                raw_quote="",  # Not returned by API to reduce payload size
                parsing_method=attestation_data['parsing_method']
            )
            
        except httpx.RequestError as e:
            logger.error(f"Request failed for {vm_name}: {e}")
            raise AttestationError(f"Network error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error for {vm_name}: {e}")
            raise AttestationError(f"Client error: {e}")
    
    async def get_dual_attestation(self) -> DualAttestationData:
        """
        Get dual attestation (secretAI + secretGPT)
        
        Returns:
            DualAttestationData with both attestations
            
        Raises:
            AttestationError: If request fails
        """
        try:
            response = await self.client.get(f"{self.base_url}/attestation/dual")
            
            if response.status_code != 200:
                raise AttestationError(f"HTTP {response.status_code}: {response.text}")
            
            data = response.json()
            
            if not data.get('success'):
                errors = data.get('errors', ['Unknown error'])
                raise AttestationError(f"Dual attestation failed: {'; '.join(errors)}")
            
            attestation_data = data['data']
            
            # Parse secretAI attestation
            secretai_data = attestation_data['secretai']
            secretai = AttestationData(
                vm_name=secretai_data['vm_name'],
                vm_type=secretai_data['vm_type'],
                mrtd=secretai_data['mrtd'],
                rtmr0=secretai_data['rtmr0'],
                rtmr1=secretai_data['rtmr1'],
                rtmr2=secretai_data['rtmr2'],
                rtmr3=secretai_data['rtmr3'],
                report_data=secretai_data['report_data'],
                certificate_fingerprint=secretai_data['certificate_fingerprint'],
                timestamp=datetime.fromisoformat(secretai_data['timestamp'].replace('Z', '+00:00')),
                raw_quote="",
                parsing_method=secretai_data['parsing_method']
            )
            
            # Parse secretGPT attestation
            secretgpt_data = attestation_data['secretgpt']
            secretgpt = AttestationData(
                vm_name=secretgpt_data['vm_name'],
                vm_type=secretgpt_data['vm_type'],
                mrtd=secretgpt_data['mrtd'],
                rtmr0=secretgpt_data['rtmr0'],
                rtmr1=secretgpt_data['rtmr1'],
                rtmr2=secretgpt_data['rtmr2'],
                rtmr3=secretgpt_data['rtmr3'],
                report_data=secretgpt_data['report_data'],
                certificate_fingerprint=secretgpt_data['certificate_fingerprint'],
                timestamp=datetime.fromisoformat(secretgpt_data['timestamp'].replace('Z', '+00:00')),
                raw_quote="",
                parsing_method=secretgpt_data['parsing_method']
            )
            
            return DualAttestationData(
                secretai=secretai,
                secretgpt=secretgpt,
                timestamp=datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00')),
                correlation_id=data['correlation_id']
            )
            
        except httpx.RequestError as e:
            logger.error(f"Request failed for dual attestation: {e}")
            raise AttestationError(f"Network error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error for dual attestation: {e}")
            raise AttestationError(f"Client error: {e}")
    
    async def get_batch_attestations(self, vm_names: List[str]) -> Dict[str, AttestationData]:
        """
        Get attestations for multiple VMs
        
        Args:
            vm_names: List of VM names
            
        Returns:
            Dictionary mapping VM names to AttestationData
            
        Raises:
            AttestationError: If request fails
        """
        try:
            response = await self.client.post(
                f"{self.base_url}/attestation/batch",
                json={"vm_names": vm_names}
            )
            
            if response.status_code != 200:
                raise AttestationError(f"HTTP {response.status_code}: {response.text}")
            
            data = response.json()
            
            attestations = {}
            errors = []
            
            # Process successful attestations
            for vm_name, attestation_data in data.get('data', {}).items():
                attestations[vm_name] = AttestationData(
                    vm_name=attestation_data['vm_name'],
                    vm_type=attestation_data['vm_type'],
                    mrtd=attestation_data['mrtd'],
                    rtmr0=attestation_data['rtmr0'],
                    rtmr1=attestation_data['rtmr1'],
                    rtmr2=attestation_data['rtmr2'],
                    rtmr3=attestation_data['rtmr3'],
                    report_data=attestation_data['report_data'],
                    certificate_fingerprint=attestation_data['certificate_fingerprint'],
                    timestamp=datetime.fromisoformat(attestation_data['timestamp'].replace('Z', '+00:00')),
                    raw_quote="",
                    parsing_method=attestation_data['parsing_method']
                )
            
            # Collect errors
            for vm_name, error in data.get('errors', {}).items():
                errors.append(f"{vm_name}: {error}")
            
            if errors:
                logger.warning(f"Some attestations failed: {'; '.join(errors)}")
            
            return attestations
            
        except httpx.RequestError as e:
            logger.error(f"Request failed for batch attestation: {e}")
            raise AttestationError(f"Network error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error for batch attestation: {e}")
            raise AttestationError(f"Client error: {e}")
    
    async def get_service_health(self) -> Dict[str, any]:
        """
        Get service health status
        
        Returns:
            Health status dictionary
            
        Raises:
            AttestationError: If request fails
        """
        try:
            response = await self.client.get(f"{self.base_url}/health")
            
            if response.status_code != 200:
                raise AttestationError(f"HTTP {response.status_code}: {response.text}")
            
            return response.json()
            
        except httpx.RequestError as e:
            logger.error(f"Health check request failed: {e}")
            raise AttestationError(f"Network error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in health check: {e}")
            raise AttestationError(f"Client error: {e}")
    
    async def list_vms(self) -> Dict[str, Dict[str, any]]:
        """
        List all configured VMs
        
        Returns:
            Dictionary of VM configurations and status
            
        Raises:
            AttestationError: If request fails
        """
        try:
            response = await self.client.get(f"{self.base_url}/vms")
            
            if response.status_code != 200:
                raise AttestationError(f"HTTP {response.status_code}: {response.text}")
            
            data = response.json()
            return data['vms']
            
        except httpx.RequestError as e:
            logger.error(f"List VMs request failed: {e}")
            raise AttestationError(f"Network error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error listing VMs: {e}")
            raise AttestationError(f"Client error: {e}")
    
    async def cleanup(self):
        """Cleanup client resources"""
        await self.client.aclose()
        logger.info("AttestationHubClient cleanup complete")


# Convenience functions for common usage patterns
async def get_secretgpt_attestation(hub_url: str = "http://localhost:8080") -> AttestationData:
    """Get secretGPT attestation (convenience function)"""
    client = AttestationHubClient(hub_url)
    try:
        return await client.get_attestation("secretgpt")
    finally:
        await client.cleanup()


async def get_secretai_attestation(hub_url: str = "http://localhost:8080") -> AttestationData:
    """Get secretAI attestation (convenience function)"""
    client = AttestationHubClient(hub_url)
    try:
        return await client.get_attestation("secretai")
    finally:
        await client.cleanup()


async def get_dual_verification(hub_url: str = "http://localhost:8080") -> DualAttestationData:
    """Get dual attestation verification (convenience function)"""
    client = AttestationHubClient(hub_url)
    try:
        return await client.get_dual_attestation()
    finally:
        await client.cleanup()