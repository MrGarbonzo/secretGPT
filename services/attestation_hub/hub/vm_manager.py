"""VM configuration and lifecycle management"""

import logging
from typing import Dict, Optional, List
from datetime import datetime

from config.settings import VMConfig, ConfigManager
from hub.models import VMStatus, AttestationError

logger = logging.getLogger(__name__)


class VMManager:
    """Manages VM configurations and status tracking"""
    
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.vm_statuses: Dict[str, VMStatus] = {}
        self._initialize_vm_statuses()
    
    def _initialize_vm_statuses(self):
        """Initialize status tracking for all configured VMs"""
        for vm_name, vm_config in self.config_manager.list_vms().items():
            self.vm_statuses[vm_name] = VMStatus(
                vm_name=vm_name,
                endpoint=vm_config.endpoint,
                status="unknown"
            )
            logger.info(f"Initialized VM: {vm_name} at {vm_config.endpoint}")
    
    def get_vm_config(self, vm_name: str) -> Optional[VMConfig]:
        """Get configuration for specific VM"""
        config = self.config_manager.get_vm_config(vm_name)
        if not config:
            logger.warning(f"VM configuration not found: {vm_name}")
        return config
    
    def list_vms(self) -> Dict[str, VMConfig]:
        """List all configured VMs"""
        return self.config_manager.list_vms()
    
    def add_vm(self, vm_name: str, config: VMConfig):
        """Add or update VM configuration"""
        self.config_manager.add_vm_config(vm_name, config)
        
        # Initialize status tracking
        self.vm_statuses[vm_name] = VMStatus(
            vm_name=vm_name,
            endpoint=config.endpoint,
            status="unknown"
        )
        
        logger.info(f"Added VM configuration: {vm_name}")
    
    def remove_vm(self, vm_name: str) -> bool:
        """Remove VM configuration"""
        if vm_name in self.vm_statuses:
            del self.vm_statuses[vm_name]
            # Note: ConfigManager would need remove_vm_config method
            logger.info(f"Removed VM: {vm_name}")
            return True
        return False
    
    def update_vm_status(self, vm_name: str, status: str, error: Optional[str] = None):
        """Update VM status after attestation attempt"""
        if vm_name not in self.vm_statuses:
            logger.warning(f"Attempted to update unknown VM: {vm_name}")
            return
        
        vm_status = self.vm_statuses[vm_name]
        vm_status.status = status
        
        if status == "healthy":
            vm_status.last_successful_attestation = datetime.utcnow()
            vm_status.error_count = 0
            vm_status.last_error = None
        else:
            vm_status.error_count += 1
            vm_status.last_error = error
        
        logger.debug(f"Updated VM status: {vm_name} -> {status}")
    
    def get_vm_status(self, vm_name: str) -> Optional[VMStatus]:
        """Get current status for specific VM"""
        return self.vm_statuses.get(vm_name)
    
    def get_all_statuses(self) -> Dict[str, VMStatus]:
        """Get status for all VMs"""
        return self.vm_statuses.copy()
    
    def get_healthy_vms(self) -> List[str]:
        """Get list of healthy VM names"""
        return [
            vm_name for vm_name, status in self.vm_statuses.items()
            if status.status == "healthy"
        ]
    
    def get_unhealthy_vms(self) -> List[str]:
        """Get list of unhealthy VM names"""
        return [
            vm_name for vm_name, status in self.vm_statuses.items()
            if status.status != "healthy"
        ]
    
    def should_retry_vm(self, vm_name: str) -> bool:
        """Check if VM should be retried based on error count"""
        vm_config = self.get_vm_config(vm_name)
        vm_status = self.get_vm_status(vm_name)
        
        if not vm_config or not vm_status:
            return False
        
        return vm_status.error_count < vm_config.retry_attempts
    
    def get_vm_by_type(self, vm_type: str) -> List[str]:
        """Get VMs by type (e.g., 'secret-ai', 'secret-gpt')"""
        matching_vms = []
        for vm_name, vm_config in self.list_vms().items():
            if vm_config.type == vm_type:
                matching_vms.append(vm_name)
        return matching_vms