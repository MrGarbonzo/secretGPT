"""Data models for attestation hub"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum


class ParsingMethod(str, Enum):
    """Available parsing methods"""
    REST_SERVER = "rest_server"
    HARDCODED = "hardcoded"
    DCAP = "dcap"
    UNKNOWN = "unknown"


class ServiceStatus(str, Enum):
    """Service health status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


@dataclass
class AttestationData:
    """Structured attestation data matching secretGPT format"""
    vm_name: str
    vm_type: str
    mrtd: str
    rtmr0: str
    rtmr1: str
    rtmr2: str
    rtmr3: str
    report_data: str
    certificate_fingerprint: str
    timestamp: datetime
    raw_quote: str
    parsing_method: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "vm_name": self.vm_name,
            "vm_type": self.vm_type,
            "mrtd": self.mrtd,
            "rtmr0": self.rtmr0,
            "rtmr1": self.rtmr1,
            "rtmr2": self.rtmr2,
            "rtmr3": self.rtmr3,
            "report_data": self.report_data,
            "certificate_fingerprint": self.certificate_fingerprint,
            "timestamp": self.timestamp.isoformat(),
            "raw_quote": self.raw_quote,
            "parsing_method": self.parsing_method
        }
    
    def matches_baseline(self, baseline: Dict[str, str]) -> bool:
        """Check if attestation matches baseline values"""
        return (
            self.mrtd == baseline.get("mrtd", "") and
            self.rtmr0 == baseline.get("rtmr0", "") and
            self.rtmr1 == baseline.get("rtmr1", "") and
            self.rtmr2 == baseline.get("rtmr2", "") and
            self.rtmr3 == baseline.get("rtmr3", "") and
            self.report_data == baseline.get("report_data", "")
        )


@dataclass
class DualAttestationData:
    """Dual attestation data for secretAI + secretGPT"""
    secretai: AttestationData
    secretgpt: AttestationData
    timestamp: datetime
    correlation_id: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "secretai": self.secretai.to_dict(),
            "secretgpt": self.secretgpt.to_dict(),
            "timestamp": self.timestamp.isoformat(),
            "correlation_id": self.correlation_id
        }


@dataclass
class VMStatus:
    """Status of a specific VM"""
    vm_name: str
    endpoint: str
    status: str
    last_successful_attestation: Optional[datetime] = None
    error_count: int = 0
    last_error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "vm_name": self.vm_name,
            "endpoint": self.endpoint,
            "status": self.status,
            "last_successful_attestation": (
                self.last_successful_attestation.isoformat() 
                if self.last_successful_attestation else None
            ),
            "error_count": self.error_count,
            "last_error": self.last_error
        }


@dataclass
class ServiceHealth:
    """Overall service health status"""
    status: ServiceStatus
    vms_online: int
    vms_total: int
    cache_hit_rate: float
    uptime_seconds: int
    version: str
    vm_statuses: Dict[str, VMStatus] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "status": self.status.value,
            "vms_online": self.vms_online,
            "vms_total": self.vms_total,
            "cache_hit_rate": self.cache_hit_rate,
            "uptime_seconds": self.uptime_seconds,
            "version": self.version,
            "vm_statuses": {
                name: status.to_dict() 
                for name, status in self.vm_statuses.items()
            }
        }


@dataclass
class CacheEntry:
    """Cache entry with TTL"""
    data: AttestationData
    created_at: datetime
    
    def is_expired(self, ttl_seconds: int) -> bool:
        """Check if cache entry is expired"""
        age = (datetime.utcnow() - self.created_at).total_seconds()
        return age > ttl_seconds


class AttestationError(Exception):
    """Custom exception for attestation errors"""
    pass


class ParsingError(AttestationError):
    """Error during quote parsing"""
    pass


class VMConnectionError(AttestationError):
    """Error connecting to VM"""
    pass