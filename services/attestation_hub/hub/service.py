"""Core attestation hub service"""

import asyncio
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Tuple
from collections import OrderedDict

from config.settings import ConfigManager
from hub.models import (
    AttestationData, DualAttestationData, ServiceHealth, 
    ServiceStatus, AttestationError, VMConnectionError,
    CacheEntry
)
from hub.vm_manager import VMManager
from parsers.base import ParserFactory

logger = logging.getLogger(__name__)


class AttestationHub:
    """Main orchestration service for multi-VM attestation"""
    
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.vm_manager = VMManager(config_manager)
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.start_time = datetime.utcnow()
        self.cache_hits = 0
        self.cache_misses = 0
        
        # Import parsers to register them
        import parsers.rest_server
        import parsers.hardcoded
        
        logger.info(f"AttestationHub initialized with {len(self.vm_manager.list_vms())} VMs")
    
    async def get_attestation(self, vm_name: str) -> AttestationData:
        """Get attestation for specific VM"""
        
        # Check cache first
        cached = self._get_cached_attestation(vm_name)
        if cached:
            self.cache_hits += 1
            logger.info(f"Cache hit for {vm_name}")
            return cached
        
        self.cache_misses += 1
        
        # Get VM configuration
        vm_config = self.vm_manager.get_vm_config(vm_name)
        if not vm_config:
            raise AttestationError(f"VM not configured: {vm_name}")
        
        # Try primary parsing strategy
        primary_parser = ParserFactory.create_parser(vm_config.parsing_strategy)
        if not primary_parser:
            raise AttestationError(f"Parser not found: {vm_config.parsing_strategy}")
        
        last_error = None
        
        try:
            logger.info(f"Attempting {vm_config.parsing_strategy} parsing for {vm_name}")
            
            # For now, we'll fetch the quote from the VM's endpoint
            # In production, this would be integrated with the actual quote retrieval
            quote = await self._fetch_quote_from_vm(vm_name, vm_config)
            
            attestation = await primary_parser.parse_attestation(
                quote, vm_config, certificate_fingerprint=""
            )
            
            # Update VM status
            self.vm_manager.update_vm_status(vm_name, "healthy")
            
            # Cache the result
            self._cache_attestation(vm_name, attestation)
            
            return attestation
            
        except Exception as e:
            last_error = e
            logger.warning(f"Primary parser failed for {vm_name}: {e}")
            self.vm_manager.update_vm_status(vm_name, "unhealthy", str(e))
        
        # Try fallback strategy if configured
        if vm_config.fallback_strategy:
            fallback_parser = ParserFactory.create_parser(vm_config.fallback_strategy)
            if fallback_parser:
                try:
                    logger.info(f"Attempting fallback {vm_config.fallback_strategy} for {vm_name}")
                    
                    quote = await self._fetch_quote_from_vm(vm_name, vm_config)
                    attestation = await fallback_parser.parse_attestation(
                        quote, vm_config, certificate_fingerprint=""
                    )
                    
                    # Partial success - update status
                    self.vm_manager.update_vm_status(vm_name, "degraded", 
                        f"Using fallback parser: {vm_config.fallback_strategy}")
                    
                    # Cache the result
                    self._cache_attestation(vm_name, attestation)
                    
                    return attestation
                    
                except Exception as e:
                    logger.error(f"Fallback parser also failed for {vm_name}: {e}")
                    last_error = e
        
        raise AttestationError(f"All parsing strategies failed for {vm_name}: {last_error}")
    
    async def get_dual_attestation(self) -> DualAttestationData:
        """Get secretAI + secretGPT attestations"""
        
        correlation_id = str(uuid.uuid4())
        logger.info(f"Getting dual attestation, correlation_id: {correlation_id}")
        
        # Run attestations in parallel
        results = await asyncio.gather(
            self.get_attestation("secretai"),
            self.get_attestation("secretgpt"),
            return_exceptions=True
        )
        
        errors = []
        secretai_attestation = None
        secretgpt_attestation = None
        
        if isinstance(results[0], Exception):
            errors.append(f"secretai: {results[0]}")
        else:
            secretai_attestation = results[0]
        
        if isinstance(results[1], Exception):
            errors.append(f"secretgpt: {results[1]}")
        else:
            secretgpt_attestation = results[1]
        
        if errors:
            raise AttestationError(f"Dual attestation failed: {'; '.join(errors)}")
        
        return DualAttestationData(
            secretai=secretai_attestation,
            secretgpt=secretgpt_attestation,
            timestamp=datetime.utcnow(),
            correlation_id=correlation_id
        )
    
    async def get_all_attestations(self) -> Dict[str, AttestationData]:
        """Get attestations for all configured VMs"""
        
        vm_names = list(self.vm_manager.list_vms().keys())
        logger.info(f"Getting attestations for all {len(vm_names)} VMs")
        
        # Run all attestations in parallel
        tasks = {
            vm_name: self.get_attestation(vm_name)
            for vm_name in vm_names
        }
        
        results = await asyncio.gather(*tasks.values(), return_exceptions=True)
        
        attestations = {}
        for vm_name, result in zip(tasks.keys(), results):
            if isinstance(result, Exception):
                logger.warning(f"Failed to get attestation for {vm_name}: {result}")
            else:
                attestations[vm_name] = result
        
        return attestations
    
    async def get_batch_attestations(self, vm_names: List[str]) -> Dict[str, AttestationData]:
        """Get attestations for specific VMs"""
        
        logger.info(f"Getting batch attestations for {len(vm_names)} VMs")
        
        # Validate VM names
        configured_vms = set(self.vm_manager.list_vms().keys())
        invalid_vms = set(vm_names) - configured_vms
        if invalid_vms:
            raise AttestationError(f"Unknown VMs: {invalid_vms}")
        
        # Run attestations in parallel
        tasks = {
            vm_name: self.get_attestation(vm_name)
            for vm_name in vm_names
        }
        
        results = await asyncio.gather(*tasks.values(), return_exceptions=True)
        
        attestations = {}
        for vm_name, result in zip(tasks.keys(), results):
            if isinstance(result, Exception):
                logger.warning(f"Failed to get attestation for {vm_name}: {result}")
            else:
                attestations[vm_name] = result
        
        return attestations
    
    async def _fetch_quote_from_vm(self, vm_name: str, vm_config) -> str:
        """Fetch attestation quote from VM endpoint"""
        
        # This is a placeholder - in production this would:
        # 1. Connect to VM's attestation endpoint
        # 2. Retrieve the raw quote data
        # 3. Return the hex-encoded quote string
        
        # For testing, load from sample data if available
        try:
            import os
            sample_file = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "experiments/attest_tool_research/sample_data/known_good_quote.hex"
            )
            if os.path.exists(sample_file):
                with open(sample_file, 'r') as f:
                    return f.read().strip()
        except:
            pass
        
        # Placeholder quote
        raise VMConnectionError(f"Quote retrieval not implemented for {vm_name}")
    
    def _get_cached_attestation(self, vm_name: str) -> Optional[AttestationData]:
        """Get attestation from cache if valid"""
        
        if vm_name not in self.cache:
            return None
        
        entry = self.cache[vm_name]
        if entry.is_expired(self.config_manager.cache_config.ttl):
            del self.cache[vm_name]
            return None
        
        # Move to end (LRU)
        self.cache.move_to_end(vm_name)
        return entry.data
    
    def _cache_attestation(self, vm_name: str, attestation: AttestationData):
        """Cache attestation data"""
        
        # Enforce cache size limit
        if len(self.cache) >= self.config_manager.cache_config.max_size:
            # Remove oldest entry
            self.cache.popitem(last=False)
        
        self.cache[vm_name] = CacheEntry(
            data=attestation,
            created_at=datetime.utcnow()
        )
    
    def get_cache_hit_rate(self) -> float:
        """Calculate cache hit rate"""
        total = self.cache_hits + self.cache_misses
        if total == 0:
            return 0.0
        return self.cache_hits / total
    
    def get_service_health(self) -> ServiceHealth:
        """Get overall service health status"""
        
        vm_statuses = self.vm_manager.get_all_statuses()
        healthy_vms = len([s for s in vm_statuses.values() if s.status == "healthy"])
        total_vms = len(vm_statuses)
        
        # Determine overall status
        if healthy_vms == total_vms:
            status = ServiceStatus.HEALTHY
        elif healthy_vms > 0:
            status = ServiceStatus.DEGRADED
        else:
            status = ServiceStatus.UNHEALTHY
        
        uptime = (datetime.utcnow() - self.start_time).total_seconds()
        
        return ServiceHealth(
            status=status,
            vms_online=healthy_vms,
            vms_total=total_vms,
            cache_hit_rate=self.get_cache_hit_rate(),
            uptime_seconds=int(uptime),
            version="1.0.0",
            vm_statuses=vm_statuses
        )
    
    async def cleanup(self):
        """Cleanup resources"""
        logger.info("Cleaning up AttestationHub resources")
        # Clean up any parser resources
        for parser_name in ParserFactory.list_parsers():
            parser = ParserFactory.create_parser(parser_name)
            if hasattr(parser, 'cleanup'):
                await parser.cleanup()