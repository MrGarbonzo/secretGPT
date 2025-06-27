"""Pydantic schemas for API validation"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class AttestationDataResponse(BaseModel):
    """Attestation data response schema"""
    vm_name: str
    vm_type: str
    mrtd: str
    rtmr0: str
    rtmr1: str
    rtmr2: str
    rtmr3: str
    report_data: str
    certificate_fingerprint: str
    timestamp: str
    parsing_method: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "vm_name": "secretgpt",
                "vm_type": "secret-gpt",
                "mrtd": "ba87a347454466680bfd267446df89d8...",
                "rtmr0": "4bf33b719bd369f3653fcfb0a4d452fe...",
                "rtmr1": "8ad5a890c47b2d5a8a1aa9db240547d8...",
                "rtmr2": "7724bd8d7167267fb35c030bd60fd991...",
                "rtmr3": "056cae9f6b4ccb3bf3087d2c22549e96...",
                "report_data": "5b38e33a6487958b72c3c12a938eaa5e...",
                "certificate_fingerprint": "test_cert_fingerprint",
                "timestamp": "2025-01-01T00:00:00.000Z",
                "parsing_method": "rest_server"
            }
        }


class AttestationResponse(BaseModel):
    """Single attestation response"""
    success: bool
    data: Optional[AttestationDataResponse] = None
    errors: List[str] = Field(default_factory=list)


class DualAttestationResponse(BaseModel):
    """Dual attestation response"""
    success: bool
    data: Optional[Dict[str, AttestationDataResponse]] = None
    correlation_id: str
    timestamp: str
    errors: List[str] = Field(default_factory=list)


class BatchAttestationRequest(BaseModel):
    """Batch attestation request"""
    vm_names: List[str]
    correlation_id: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "vm_names": ["secretai", "secretgpt"],
                "correlation_id": "optional-correlation-id"
            }
        }


class BatchAttestationResponse(BaseModel):
    """Batch attestation response"""
    success: bool
    data: Dict[str, AttestationDataResponse] = Field(default_factory=dict)
    errors: Dict[str, str] = Field(default_factory=dict)
    correlation_id: str


class VMConfigRequest(BaseModel):
    """VM configuration request"""
    endpoint: str
    type: str
    parsing_strategy: str = "rest_server"
    timeout: int = 30
    retry_attempts: int = 3
    fallback_strategy: Optional[str] = None
    health_check_path: str = "/status"
    tls_verify: bool = False
    
    class Config:
        json_schema_extra = {
            "example": {
                "endpoint": "https://new-vm:29343",
                "type": "custom-vm",
                "parsing_strategy": "rest_server",
                "fallback_strategy": "hardcoded"
            }
        }


class VMInfo(BaseModel):
    """VM information"""
    name: str
    endpoint: str
    type: str
    parsing_strategy: str
    status: str
    last_successful_attestation: Optional[str] = None
    error_count: int = 0


class VMListResponse(BaseModel):
    """VM list response"""
    vms: Dict[str, VMInfo]
    total: int


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    vms_online: int
    vms_total: int
    cache_hit_rate: float
    uptime_seconds: int
    version: str
    vm_statuses: Dict[str, Dict[str, Any]]
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "vms_online": 2,
                "vms_total": 2,
                "cache_hit_rate": 0.85,
                "uptime_seconds": 3600,
                "version": "1.0.0",
                "vm_statuses": {
                    "secretai": {
                        "status": "healthy",
                        "last_successful_attestation": "2025-01-01T00:00:00.000Z"
                    }
                }
            }
        }


class ErrorResponse(BaseModel):
    """Error response"""
    error: str
    details: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())