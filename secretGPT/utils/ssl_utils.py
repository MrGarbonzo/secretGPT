"""
SSL Certificate Utilities
Handles self-signed certificate generation for HTTPS support
"""
import os
import subprocess
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def generate_self_signed_cert(domain: str = "localhost", cert_dir: str = "/app/ssl") -> tuple[str, str]:
    """
    Generate self-signed SSL certificate and private key
    
    Args:
        domain: Domain name for the certificate
        cert_dir: Directory to store certificate files
        
    Returns:
        tuple: (cert_path, key_path) paths to generated files
    """
    # Create SSL directory if it doesn't exist
    ssl_path = Path(cert_dir)
    ssl_path.mkdir(parents=True, exist_ok=True)
    
    cert_file = ssl_path / "cert.pem"
    key_file = ssl_path / "key.pem"
    
    # Check if certificates already exist and are valid
    if cert_file.exists() and key_file.exists():
        logger.info(f"SSL certificates already exist at {cert_dir}")
        return str(cert_file), str(key_file)
    
    logger.info(f"Generating self-signed SSL certificate for domain: {domain}")
    
    try:
        # Generate self-signed certificate
        cmd = [
            "openssl", "req", "-x509", "-newkey", "rsa:4096",
            "-keyout", str(key_file),
            "-out", str(cert_file),
            "-days", "365",
            "-nodes",
            "-subj", f"/CN={domain}"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        # Set proper permissions
        os.chmod(str(key_file), 0o600)  # Private key should be readable only by owner
        os.chmod(str(cert_file), 0o644)  # Certificate can be readable by others
        
        logger.info(f"SSL certificate generated successfully:")
        logger.info(f"  Certificate: {cert_file}")
        logger.info(f"  Private key: {key_file}")
        logger.info(f"  Domain: {domain}")
        logger.info(f"  Valid for: 365 days")
        
        return str(cert_file), str(key_file)
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to generate SSL certificate: {e}")
        logger.error(f"Command output: {e.stdout}")
        logger.error(f"Command error: {e.stderr}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error generating SSL certificate: {e}")
        raise


def validate_ssl_files(cert_path: str, key_path: str) -> bool:
    """
    Validate that SSL certificate and key files exist and are readable
    
    Args:
        cert_path: Path to certificate file
        key_path: Path to private key file
        
    Returns:
        bool: True if both files are valid
    """
    try:
        cert_file = Path(cert_path)
        key_file = Path(key_path)
        
        if not cert_file.exists():
            logger.error(f"Certificate file not found: {cert_path}")
            return False
            
        if not key_file.exists():
            logger.error(f"Private key file not found: {key_path}")
            return False
            
        # Check if files are readable
        with open(cert_path, 'r') as f:
            cert_content = f.read()
            if not cert_content.strip():
                logger.error(f"Certificate file is empty: {cert_path}")
                return False
                
        with open(key_path, 'r') as f:
            key_content = f.read()
            if not key_content.strip():
                logger.error(f"Private key file is empty: {key_path}")
                return False
                
        logger.info("SSL certificate and key files validated successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error validating SSL files: {e}")
        return False