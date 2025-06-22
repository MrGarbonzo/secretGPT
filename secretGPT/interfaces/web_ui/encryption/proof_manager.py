"""
Proof Manager for secretGPT Web UI
REFERENCE: F:/coding/attest_ai/src/encryption/proof_manager.py
MIGRATE: Existing proof generation logic but integrate with hub's Secret AI service
"""
import json
import logging
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import hashlib
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from secretGPT.interfaces.web_ui.attestation.service import AttestationService

logger = logging.getLogger(__name__)


class ProofManager:
    """
    Proof Manager for generating encrypted proof files with dual VM attestation
    Use existing attest_ai logic but with hub-provided data
    """
    
    def __init__(self, attestation_service: AttestationService):
        """Initialize proof manager with attestation service"""
        self.attestation_service = attestation_service
        self.proof_directory = Path(tempfile.gettempdir()) / "secretgpt_proofs"
        self.proof_directory.mkdir(exist_ok=True)
        logger.info("Proof manager initialized")
    
    async def generate_proof(self, question: str, answer: str, password: str) -> Path:
        """
        Generate encrypted proof file with dual VM attestation
        
        Args:
            question: The question asked to Secret AI
            answer: The response from Secret AI
            password: Password for encrypting the proof file
            
        Returns:
            Path to the generated .attestproof file
        """
        try:
            logger.info("Generating proof with dual VM attestation")
            
            # Get dual VM attestation
            dual_attestation = await self.attestation_service.get_dual_attestation()
            
            # Create proof data structure
            proof_data = {
                "version": "2.0.0",
                "timestamp": datetime.utcnow().isoformat(),
                "interaction": {
                    "question": question,
                    "answer": answer,
                    "question_hash": self._hash_string(question),
                    "answer_hash": self._hash_string(answer)
                },
                "attestation": dual_attestation,
                "metadata": {
                    "generator": "secretGPT",
                    "proof_type": "dual_vm_attestation",
                    "encryption": "Fernet_PBKDF2"
                }
            }
            
            # Convert to JSON
            proof_json = json.dumps(proof_data, indent=2)
            
            # Encrypt the proof data
            encrypted_proof = self._encrypt_data(proof_json, password)
            
            # Generate proof file
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"secretgpt_proof_{timestamp}.attestproof"
            proof_file = self.proof_directory / filename
            
            # Write encrypted proof to file
            with open(proof_file, 'wb') as f:
                f.write(encrypted_proof)
            
            logger.info(f"Proof file generated: {proof_file}")
            return proof_file
            
        except Exception as e:
            logger.error(f"Proof generation failed: {e}")
            raise Exception(f"Failed to generate proof: {e}")
    
    async def verify_proof(self, proof_content: bytes, password: str) -> Dict[str, Any]:
        """
        Verify and decrypt proof file
        
        Args:
            proof_content: Encrypted proof file content
            password: Password for decrypting the proof
            
        Returns:
            Decrypted and verified proof data
        """
        try:
            logger.info("Verifying proof file")
            
            # Decrypt the proof data
            decrypted_json = self._decrypt_data(proof_content, password)
            
            # Parse JSON
            proof_data = json.loads(decrypted_json)
            
            # Verify proof structure
            self._verify_proof_structure(proof_data)
            
            # Verify hashes
            interaction = proof_data["interaction"]
            question_hash = self._hash_string(interaction["question"])
            answer_hash = self._hash_string(interaction["answer"])
            
            if question_hash != interaction["question_hash"]:
                raise Exception("Question hash verification failed")
            
            if answer_hash != interaction["answer_hash"]:
                raise Exception("Answer hash verification failed")
            
            # Verify attestation data (basic checks)
            attestation = proof_data["attestation"]
            if not attestation.get("dual_attestation"):
                raise Exception("Dual attestation not found in proof")
            
            logger.info("Proof verification successful")
            
            return {
                "success": True,
                "verified": True,
                "proof_data": proof_data,
                "verification_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Proof verification failed: {e}")
            return {
                "success": False,
                "verified": False,
                "error": str(e)
            }
    
    def _encrypt_data(self, data: str, password: str) -> bytes:
        """
        Encrypt data using password-based encryption
        Uses Fernet with PBKDF2 key derivation
        """
        # Generate salt
        salt = b'secretgpt_salt_2024'  # In production, use random salt
        
        # Derive key from password
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        
        # Encrypt data
        fernet = Fernet(key)
        encrypted_data = fernet.encrypt(data.encode())
        
        return encrypted_data
    
    def _decrypt_data(self, encrypted_data: bytes, password: str) -> str:
        """
        Decrypt data using password-based decryption
        """
        # Generate same salt
        salt = b'secretgpt_salt_2024'  # In production, use salt from file
        
        # Derive key from password
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        
        # Decrypt data
        fernet = Fernet(key)
        decrypted_data = fernet.decrypt(encrypted_data)
        
        return decrypted_data.decode()
    
    def _hash_string(self, text: str) -> str:
        """Generate SHA-256 hash of string"""
        return hashlib.sha256(text.encode()).hexdigest()
    
    def _verify_proof_structure(self, proof_data: Dict[str, Any]) -> None:
        """Verify that proof data has the required structure"""
        required_fields = [
            "version",
            "timestamp", 
            "interaction",
            "attestation",
            "metadata"
        ]
        
        for field in required_fields:
            if field not in proof_data:
                raise Exception(f"Missing required field: {field}")
        
        # Verify interaction structure
        interaction = proof_data["interaction"]
        interaction_fields = ["question", "answer", "question_hash", "answer_hash"]
        for field in interaction_fields:
            if field not in interaction:
                raise Exception(f"Missing interaction field: {field}")
        
        # Verify attestation structure
        attestation = proof_data["attestation"]
        if not isinstance(attestation, dict):
            raise Exception("Invalid attestation structure")
    
    def list_proofs(self) -> list:
        """List all proof files in the proof directory"""
        try:
            proof_files = list(self.proof_directory.glob("*.attestproof"))
            return [
                {
                    "filename": pf.name,
                    "path": str(pf),
                    "size": pf.stat().st_size,
                    "created": datetime.fromtimestamp(pf.stat().st_ctime).isoformat()
                }
                for pf in sorted(proof_files, key=lambda x: x.stat().st_ctime, reverse=True)
            ]
        except Exception as e:
            logger.error(f"Failed to list proofs: {e}")
            return []
    
    def cleanup_old_proofs(self, max_age_days: int = 30) -> int:
        """Clean up proof files older than specified days"""
        try:
            cutoff_time = datetime.utcnow().timestamp() - (max_age_days * 24 * 3600)
            deleted_count = 0
            
            for proof_file in self.proof_directory.glob("*.attestproof"):
                if proof_file.stat().st_ctime < cutoff_time:
                    proof_file.unlink()
                    deleted_count += 1
            
            logger.info(f"Cleaned up {deleted_count} old proof files")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup proofs: {e}")
            return 0