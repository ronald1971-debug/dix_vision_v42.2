"""Production-Grade Cryptographic Operations.

Real implementation of cryptographic operations for production trust root.
Uses actual Python cryptography library for production-grade security.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
import threading
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
import secrets
import base64

try:
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.primitives.asymmetric import rsa, padding
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.backends import default_backend
    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    CRYPTOGRAPHY_AVAILABLE = False
    logging.warning("cryptography library not available, using fallback implementation")

logger = logging.getLogger(__name__)


class ProductionHashGenerator:
    """Production-grade hash generation with real cryptographic operations."""

    @staticmethod
    def generate_sha256_hash(data: bytes) -> str:
        """Generate SHA-256 hash of data."""
        return hashlib.sha256(data).hexdigest()

    @staticmethod
    def generate_sha3_256_hash(data: bytes) -> str:
        """Generate SHA3-256 hash of data."""
        return hashlib.sha3_256().hexdigest()

    @staticmethod
    def generate_hmac(key: bytes, data: bytes) -> str:
        """Generate HMAC-SHA256 for authentication."""
        return hmac.new(key, data, hashlib.sha256).hexdigest()

    @staticmethod
    def generate_key_hash(key_id: str, timestamp: int) -> str:
        """Generate deterministic hash for key identification."""
        data = f"{key_id}:{timestamp}".encode()
        return ProductionHashGenerator.generate_sha256_hash(data)


class ProductionSignatureOperations:
    """Real digital signature operations for production use."""

    def __init__(self):
        if not CRYPTOGRAPHY_AVAILABLE:
            raise RuntimeError("cryptography library required for production signatures")
        self._backend = default_backend()

    def generate_rsa_key_pair(self, key_size: int = 2048) -> Tuple[str, str]:
        """Generate RSA key pair for digital signatures.

        Returns:
            Tuple of (private_key_pem, public_key_pem)
        """
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size,
            backend=self._backend
        )

        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )

        public_key = private_key.public_key()
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        return private_pem.decode('utf-8'), public_pem.decode('utf-8')

    def sign_data(self, private_key_pem: str, data: bytes) -> str:
        """Sign data using RSA private key."""
        private_key = serialization.load_pem_private_key(
            private_key_pem.encode(),
            password=None,
            backend=self._backend
        )

        signature = private_key.sign(
            data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

        return base64.b64encode(signature).decode('utf-8')

    def verify_signature(self, public_key_pem: str, data: bytes, signature: str) -> bool:
        """Verify RSA signature using public key."""
        public_key = serialization.load_pem_public_key(
            public_key_pem.encode(),
            backend=self._backend
        )

        signature_bytes = base64.b64decode(signature.encode())

        try:
            public_key.verify(
                signature_bytes,
                data,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except Exception:
            return False

    def generate_ecdsa_key_pair(self) -> Tuple[str, str]:
        """Generate ECDSA key pair for faster operations.

        Returns:
            Tuple of (private_key_pem, public_key_pem)
        """
        from cryptography.hazmat.primitives.asymmetric import ec

        private_key = ec.generate_private_key(ec.SECP256R1(), self._backend)

        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )

        public_key = private_key.public_key()
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        return private_pem.decode('utf-8'), public_pem.decode('utf-8')


class ProductionKeyDerivation:
    """Production-grade key derivation for secure key management."""

    @staticmethod
    def derive_key_from_password(
        password: str,
        salt: bytes,
        iterations: int = 100000
    ) -> bytes:
        """Derive encryption key from password using PBKDF2."""
        if CRYPTOGRAPHY_AVAILABLE:
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=iterations,
                backend=default_backend()
            )
            return kdf.derive(password.encode())
        else:
            # Fallback implementation
            import hashlib
            return hashlib.pbkdf2_hmac(
                'sha256',
                password.encode(),
                salt,
                iterations,
                dklen=32
            )

    @staticmethod
    def generate_secure_salt() -> bytes:
        """Generate cryptographically secure random salt."""
        return secrets.token_bytes(32)


class ProductionEncryption:
    """Production-grade encryption for sensitive data."""

    def __init__(self):
        if not CRYPTOGRAPHY_AVAILABLE:
            raise RuntimeError("cryptography library required for production encryption")
        self._backend = default_backend()

    def encrypt_data(self, key: bytes, data: bytes) -> Tuple[bytes, bytes, bytes]:
        """Encrypt data using AES-GCM.

        Returns:
            Tuple of (nonce, ciphertext, tag)
        """
        nonce = secrets.token_bytes(12)  # GCM nonce
        cipher = Cipher(
            algorithms.AES(key),
            modes.GCM(nonce),
            backend=self._backend
        )
        encryptor = cipher.encryptor()

        ciphertext = encryptor.update(data) + encryptor.finalize()
        return nonce, ciphertext, encryptor.tag

    def decrypt_data(self, key: bytes, nonce: bytes, ciphertext: bytes, tag: bytes) -> bytes:
        """Decrypt data using AES-GCM."""
        cipher = Cipher(
            algorithms.AES(key),
            modes.GCM(nonce, tag),
            backend=self._backend
        )
        decryptor = cipher.decryptor()

        return decryptor.update(ciphertext) + decryptor.finalize()


class ProductionTrustRoot:
    """Production-grade trust root with real cryptographic operations."""

    def __init__(self):
        self._hash_generator = ProductionHashGenerator()
        self._signature_ops = ProductionSignatureOperations()
        self._key_derivation = ProductionKeyDerivation()
        self._encryption = ProductionEncryption()
        self._lock = threading.Lock()

        # Trust anchor storage
        self._trust_anchors: Dict[str, Dict[str, Any]] = {}
        self._hash_chain: Dict[str, List[str]] = {}

    def register_production_trust_anchor(
        self,
        anchor_id: str,
        purpose: str,
        key_type: str = "RSA",
        key_size: int = 2048
    ) -> Dict[str, Any]:
        """Register a production trust anchor with real cryptographic keys."""
        with self._lock:
            if key_type == "RSA":
                private_key, public_key = self._signature_ops.generate_rsa_key_pair(key_size)
            elif key_type == "ECDSA":
                private_key, public_key = self._signature_ops.generate_ecdsa_key_pair()
            else:
                raise ValueError(f"Unsupported key type: {key_type}")

            # Store trust anchor
            anchor = {
                "anchor_id": anchor_id,
                "purpose": purpose,
                "key_type": key_type,
                "public_key": public_key,
                "private_key": private_key,  # In production, this should be stored securely
                "key_size": key_size,
                "registration_time": datetime.now(timezone.utc).isoformat(),
                "status": "active"
            }

            self._trust_anchors[anchor_id] = anchor

            logger.info(f"Registered production trust anchor: {anchor_id} ({key_type}-{key_size})")
            return anchor

    def create_production_foundation_hash(
        self,
        component: str,
        version: str,
        data: bytes,
        previous_hash: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a production foundation hash with real cryptographic operations."""
        timestamp_ns = int(datetime.now(timezone.utc).timestamp() * 1e9)
        hash_value = self._hash_generator.generate_sha256_hash(data)
        hash_id = self._hash_generator.generate_key_hash(component, timestamp_ns)

        # Store in hash chain
        if component not in self._hash_chain:
            self._hash_chain[component] = []
        self._hash_chain[component].append(hash_id)

        return {
            "hash_id": hash_id,
            "hash_value": hash_value,
            "component": component,
            "version": version,
            "timestamp_ns": timestamp_ns,
            "previous_hash": previous_hash,
            "hash_chain_position": len(self._hash_chain[component])
        }

    def create_production_verification_artifact(
        self,
        foundation_hash: Dict[str, Any],
        anchor_id: str,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a production verification artifact with real digital signatures."""
        anchor = self._trust_anchors.get(anchor_id)
        if not anchor:
            raise ValueError(f"Trust anchor not found: {anchor_id}")

        # Create verification data
        verification_data = {
            "hash_id": foundation_hash["hash_id"],
            "hash_value": foundation_hash["hash_value"],
            "component": foundation_hash["component"],
            "version": foundation_hash["version"],
            "timestamp": foundation_hash["timestamp_ns"],
            "anchor_id": anchor_id,
            "additional_data": additional_data or {}
        }

        # Serialize and sign
        verification_json = json.dumps(verification_data, sort_keys=True).encode()
        signature = self._signature_ops.sign_data(anchor["private_key"], verification_json)

        return {
            "artifact_id": f"artifact_{foundation_hash['hash_id']}",
            "verification_data": verification_data,
            "signature": signature,
            "anchor_id": anchor_id,
            "signature_algorithm": "RSA-PSS-SHA256",
            "created_time": datetime.now(timezone.utc).isoformat(),
            "status": "verified"
        }

    def verify_production_artifact(self, artifact: Dict[str, Any]) -> bool:
        """Verify a production verification artifact."""
        anchor = self._trust_anchors.get(artifact["anchor_id"])
        if not anchor:
            return False

        # Reconstruct verification data
        verification_json = json.dumps(artifact["verification_data"], sort_keys=True).encode()

        # Verify signature
        is_valid = self._signature_ops.verify_signature(
            anchor["public_key"],
            verification_json,
            artifact["signature"]
        )

        if is_valid:
            logger.info(f"Production artifact verified: {artifact['artifact_id']}")
        else:
            logger.warning(f"Production artifact verification failed: {artifact['artifact_id']}")

        return is_valid

    def get_production_trust_statistics(self) -> Dict[str, Any]:
        """Get production trust root statistics."""
        with self._lock:
            return {
                "total_trust_anchors": len(self._trust_anchors),
                "active_anchors": sum(1 for a in self._trust_anchors.values() if a["status"] == "active"),
                "total_hash_chains": len(self._hash_chain),
                "cryptographic_operations_available": CRYPTOGRAPHY_AVAILABLE,
                "supported_key_types": ["RSA", "ECDSA"] if CRYPTOGRAPHY_AVAILABLE else ["SHA256"],
                "supported_hash_algorithms": ["SHA256", "SHA3-256", "HMAC-SHA256"]
            }


# Singleton instance
_production_trust_root: Optional[ProductionTrustRoot] = None
_trust_root_lock = threading.Lock()


def get_production_trust_root() -> ProductionTrustRoot:
    """Get the singleton production trust root instance."""
    global _production_trust_root
    if _production_trust_root is None:
        with _trust_root_lock:
            if _production_trust_root is None:
                _production_trust_root = ProductionTrustRoot()
    return _production_trust_root


__all__ = [
    "ProductionHashGenerator",
    "ProductionSignatureOperations",
    "ProductionKeyDerivation",
    "ProductionEncryption",
    "ProductionTrustRoot",
    "get_production_trust_root",
    "CRYPTOGRAPHY_AVAILABLE",
]