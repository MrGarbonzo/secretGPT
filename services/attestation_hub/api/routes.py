"""REST API endpoints for attestation hub"""

import logging
import uuid
from typing import Dict
from fastapi import APIRouter, HTTPException, status
from datetime import datetime

from api.schemas import (
    AttestationResponse, AttestationDataResponse,
    DualAttestationResponse, BatchAttestationRequest,
    BatchAttestationResponse, VMConfigRequest,
    VMInfo, VMListResponse, HealthResponse,
    ErrorResponse
)
from hub.service import AttestationHub
from hub.models import AttestationError
from config.settings import VMConfig

logger = logging.getLogger(__name__)

router = APIRouter()


def create_routes(attestation_hub: AttestationHub) -> APIRouter:
    """Create API routes with injected hub instance"""
    
    @router.get("/health", response_model=HealthResponse)
    async def health_check():
        """Service health status"""
        try:
            health = attestation_hub.get_service_health()
            return HealthResponse(
                status=health.status.value,
                vms_online=health.vms_online,
                vms_total=health.vms_total,
                cache_hit_rate=health.cache_hit_rate,
                uptime_seconds=health.uptime_seconds,
                version=health.version,
                vm_statuses={
                    name: status.to_dict() 
                    for name, status in health.vm_statuses.items()
                }
            )
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
    
    @router.get("/attestation/{vm_name}", response_model=AttestationResponse)
    async def get_vm_attestation(vm_name: str):
        """Get attestation for specific VM"""
        try:
            attestation = await attestation_hub.get_attestation(vm_name)
            
            return AttestationResponse(
                success=True,
                data=AttestationDataResponse(
                    vm_name=attestation.vm_name,
                    vm_type=attestation.vm_type,
                    mrtd=attestation.mrtd,
                    rtmr0=attestation.rtmr0,
                    rtmr1=attestation.rtmr1,
                    rtmr2=attestation.rtmr2,
                    rtmr3=attestation.rtmr3,
                    report_data=attestation.report_data,
                    certificate_fingerprint=attestation.certificate_fingerprint,
                    timestamp=attestation.timestamp.isoformat(),
                    parsing_method=attestation.parsing_method
                )
            )
        except AttestationError as e:
            logger.error(f"Attestation failed for {vm_name}: {e}")
            return AttestationResponse(
                success=False,
                errors=[str(e)]
            )
        except Exception as e:
            logger.error(f"Unexpected error for {vm_name}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
    
    @router.get("/attestation/dual", response_model=DualAttestationResponse)
    async def get_dual_attestation():
        """Get secretAI + secretGPT attestations"""
        try:
            dual_attestation = await attestation_hub.get_dual_attestation()
            
            return DualAttestationResponse(
                success=True,
                data={
                    "secretai": AttestationDataResponse(
                        vm_name=dual_attestation.secretai.vm_name,
                        vm_type=dual_attestation.secretai.vm_type,
                        mrtd=dual_attestation.secretai.mrtd,
                        rtmr0=dual_attestation.secretai.rtmr0,
                        rtmr1=dual_attestation.secretai.rtmr1,
                        rtmr2=dual_attestation.secretai.rtmr2,
                        rtmr3=dual_attestation.secretai.rtmr3,
                        report_data=dual_attestation.secretai.report_data,
                        certificate_fingerprint=dual_attestation.secretai.certificate_fingerprint,
                        timestamp=dual_attestation.secretai.timestamp.isoformat(),
                        parsing_method=dual_attestation.secretai.parsing_method
                    ),
                    "secretgpt": AttestationDataResponse(
                        vm_name=dual_attestation.secretgpt.vm_name,
                        vm_type=dual_attestation.secretgpt.vm_type,
                        mrtd=dual_attestation.secretgpt.mrtd,
                        rtmr0=dual_attestation.secretgpt.rtmr0,
                        rtmr1=dual_attestation.secretgpt.rtmr1,
                        rtmr2=dual_attestation.secretgpt.rtmr2,
                        rtmr3=dual_attestation.secretgpt.rtmr3,
                        report_data=dual_attestation.secretgpt.report_data,
                        certificate_fingerprint=dual_attestation.secretgpt.certificate_fingerprint,
                        timestamp=dual_attestation.secretgpt.timestamp.isoformat(),
                        parsing_method=dual_attestation.secretgpt.parsing_method
                    )
                },
                correlation_id=dual_attestation.correlation_id,
                timestamp=dual_attestation.timestamp.isoformat()
            )
        except AttestationError as e:
            logger.error(f"Dual attestation failed: {e}")
            return DualAttestationResponse(
                success=False,
                errors=[str(e)],
                correlation_id=str(uuid.uuid4()),
                timestamp=datetime.utcnow().isoformat()
            )
        except Exception as e:
            logger.error(f"Unexpected error in dual attestation: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
    
    @router.get("/attestation/all")
    async def get_all_attestations():
        """Get attestations for all configured VMs"""
        try:
            attestations = await attestation_hub.get_all_attestations()
            
            data = {}
            errors = []
            
            for vm_name, attestation in attestations.items():
                data[vm_name] = AttestationDataResponse(
                    vm_name=attestation.vm_name,
                    vm_type=attestation.vm_type,
                    mrtd=attestation.mrtd,
                    rtmr0=attestation.rtmr0,
                    rtmr1=attestation.rtmr1,
                    rtmr2=attestation.rtmr2,
                    rtmr3=attestation.rtmr3,
                    report_data=attestation.report_data,
                    certificate_fingerprint=attestation.certificate_fingerprint,
                    timestamp=attestation.timestamp.isoformat(),
                    parsing_method=attestation.parsing_method
                )
            
            # Check for VMs that failed
            all_vms = set(attestation_hub.vm_manager.list_vms().keys())
            successful_vms = set(attestations.keys())
            failed_vms = all_vms - successful_vms
            
            for vm in failed_vms:
                errors.append(f"{vm}: attestation failed")
            
            return {
                "success": len(errors) == 0,
                "data": data,
                "errors": errors,
                "total_vms": len(all_vms),
                "successful_vms": len(successful_vms)
            }
            
        except Exception as e:
            logger.error(f"Get all attestations failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
    
    @router.post("/attestation/batch", response_model=BatchAttestationResponse)
    async def get_batch_attestations(request: BatchAttestationRequest):
        """Get attestations for multiple specific VMs"""
        correlation_id = request.correlation_id or str(uuid.uuid4())
        
        try:
            attestations = await attestation_hub.get_batch_attestations(request.vm_names)
            
            data = {}
            errors = {}
            
            for vm_name in request.vm_names:
                if vm_name in attestations:
                    attestation = attestations[vm_name]
                    data[vm_name] = AttestationDataResponse(
                        vm_name=attestation.vm_name,
                        vm_type=attestation.vm_type,
                        mrtd=attestation.mrtd,
                        rtmr0=attestation.rtmr0,
                        rtmr1=attestation.rtmr1,
                        rtmr2=attestation.rtmr2,
                        rtmr3=attestation.rtmr3,
                        report_data=attestation.report_data,
                        certificate_fingerprint=attestation.certificate_fingerprint,
                        timestamp=attestation.timestamp.isoformat(),
                        parsing_method=attestation.parsing_method
                    )
                else:
                    errors[vm_name] = "Attestation failed"
            
            return BatchAttestationResponse(
                success=len(errors) == 0,
                data=data,
                errors=errors,
                correlation_id=correlation_id
            )
            
        except AttestationError as e:
            logger.error(f"Batch attestation failed: {e}")
            return BatchAttestationResponse(
                success=False,
                errors={vm: str(e) for vm in request.vm_names},
                correlation_id=correlation_id
            )
        except Exception as e:
            logger.error(f"Unexpected error in batch attestation: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
    
    @router.get("/vms", response_model=VMListResponse)
    async def list_vms():
        """List all configured VMs"""
        try:
            vms = attestation_hub.vm_manager.list_vms()
            statuses = attestation_hub.vm_manager.get_all_statuses()
            
            vm_info = {}
            for name, config in vms.items():
                status_info = statuses.get(name)
                vm_info[name] = VMInfo(
                    name=name,
                    endpoint=config.endpoint,
                    type=config.type,
                    parsing_strategy=config.parsing_strategy,
                    status=status_info.status if status_info else "unknown",
                    last_successful_attestation=(
                        status_info.last_successful_attestation.isoformat()
                        if status_info and status_info.last_successful_attestation
                        else None
                    ),
                    error_count=status_info.error_count if status_info else 0
                )
            
            return VMListResponse(
                vms=vm_info,
                total=len(vms)
            )
            
        except Exception as e:
            logger.error(f"List VMs failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
    
    @router.post("/vms/{vm_name}/config")
    async def add_vm_config(vm_name: str, config: VMConfigRequest):
        """Add or update VM configuration"""
        try:
            vm_config = VMConfig(
                endpoint=config.endpoint,
                type=config.type,
                parsing_strategy=config.parsing_strategy,
                timeout=config.timeout,
                retry_attempts=config.retry_attempts,
                fallback_strategy=config.fallback_strategy,
                health_check_path=config.health_check_path,
                tls_verify=config.tls_verify
            )
            
            attestation_hub.vm_manager.add_vm(vm_name, vm_config)
            
            return {
                "success": True,
                "message": f"VM configuration added/updated: {vm_name}",
                "vm_name": vm_name,
                "config": config.model_dump()
            }
            
        except Exception as e:
            logger.error(f"Add VM config failed for {vm_name}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
    
    return router