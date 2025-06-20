"""
Web UI Interface for secretGPT
Integration with Phase 1 hub router following DETAILED_BUILD_PLAN.md
"""
from .app import WebUIInterface
from .attestation.service import AttestationService
from .encryption.proof_manager import ProofManager

__all__ = ['WebUIInterface', 'AttestationService', 'ProofManager']