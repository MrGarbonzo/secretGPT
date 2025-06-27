"""Configuration management for Attestation Hub Service"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
import os
import yaml
from pathlib import Path


@dataclass
class ServiceConfig:
    """Main service configuration"""
    host: str = "0.0.0.0"
    port: int = 8080
    workers: int = 4
    timeout: int = 30
    log_level: str = "INFO"
    
    @classmethod
    def from_env(cls) -> "ServiceConfig":
        """Load configuration from environment variables"""
        return cls(
            host=os.getenv("ATTESTATION_HUB_HOST", "0.0.0.0"),
            port=int(os.getenv("ATTESTATION_HUB_PORT", "8080")),
            workers=int(os.getenv("ATTESTATION_HUB_WORKERS", "4")),
            timeout=int(os.getenv("ATTESTATION_HUB_TIMEOUT", "30")),
            log_level=os.getenv("LOG_LEVEL", "INFO")
        )


@dataclass
class VMConfig:
    """VM configuration model"""
    endpoint: str
    type: str
    parsing_strategy: str
    timeout: int = 30
    retry_attempts: int = 3
    fallback_strategy: Optional[str] = None
    health_check_path: str = "/status"
    tls_verify: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "endpoint": self.endpoint,
            "type": self.type,
            "parsing_strategy": self.parsing_strategy,
            "timeout": self.timeout,
            "retry_attempts": self.retry_attempts,
            "fallback_strategy": self.fallback_strategy,
            "health_check_path": self.health_check_path,
            "tls_verify": self.tls_verify
        }


@dataclass
class CacheConfig:
    """Cache configuration"""
    ttl: int = 300  # 5 minutes
    max_size: int = 1000
    
    @classmethod
    def from_env(cls) -> "CacheConfig":
        """Load from environment"""
        return cls(
            ttl=int(os.getenv("CACHE_TTL", "300")),
            max_size=int(os.getenv("CACHE_MAX_SIZE", "1000"))
        )


class ConfigManager:
    """Manages all configuration loading"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or os.getenv(
            "VM_CONFIG_PATH", 
            str(Path(__file__).parent / "vm_configs.yaml")
        )
        self.service_config = ServiceConfig.from_env()
        self.cache_config = CacheConfig.from_env()
        self.vm_configs: Dict[str, VMConfig] = {}
        self._load_vm_configs()
    
    def _load_vm_configs(self):
        """Load VM configurations from YAML file"""
        try:
            with open(self.config_file, 'r') as f:
                data = yaml.safe_load(f)
                
            for vm_name, vm_data in data.get('vms', {}).items():
                self.vm_configs[vm_name] = VMConfig(**vm_data)
        except FileNotFoundError:
            # Create default configuration
            self._create_default_config()
        except Exception as e:
            raise RuntimeError(f"Failed to load VM configs: {e}")
    
    def _create_default_config(self):
        """Create default VM configuration"""
        self.vm_configs = {
            "secretai": VMConfig(
                endpoint="https://secretai.scrtlabs.com:29343",
                type="secret-ai",
                parsing_strategy="rest_server",
                timeout=30,
                retry_attempts=3,
                fallback_strategy=None,
                tls_verify=False
            ),
            "secretgpt": VMConfig(
                endpoint="https://localhost:29343",
                type="secret-gpt",
                parsing_strategy="rest_server",
                timeout=30,
                retry_attempts=3,
                fallback_strategy="hardcoded",
                tls_verify=False
            )
        }
        # Save default config
        self.save_vm_configs()
    
    def save_vm_configs(self):
        """Save current VM configurations to file"""
        data = {
            "vms": {
                name: config.to_dict()
                for name, config in self.vm_configs.items()
            }
        }
        
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        with open(self.config_file, 'w') as f:
            yaml.dump(data, f, default_flow_style=False)
    
    def get_vm_config(self, vm_name: str) -> Optional[VMConfig]:
        """Get configuration for specific VM"""
        return self.vm_configs.get(vm_name)
    
    def add_vm_config(self, vm_name: str, config: VMConfig):
        """Add or update VM configuration"""
        self.vm_configs[vm_name] = config
        self.save_vm_configs()
    
    def list_vms(self) -> Dict[str, VMConfig]:
        """List all configured VMs"""
        return self.vm_configs.copy()