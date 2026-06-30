"""
DIX VISION Data Security Service

Provides data encryption, key management, access control, 
audit logging, and data protection for enhanced security.
"""

from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple
from collections import defaultdict, deque
from datetime import datetime, timedelta
import secrets
import json
import hashlib

try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    import base64
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    logger.warning("cryptography library not available, using fallback encryption")

from runtime.event_bus import EventBus, Event, EventType, get_event_bus
from runtime.service_manager import Service, ServiceState, ServiceHealth

logger = logging.getLogger(__name__)


class EncryptionType(Enum):
    """Types of encryption."""
    AES_256 = "aes_256"
    FERNET = "fernet"
    RSA = "rsa"


class AccessLevel(Enum):
    """Access levels."""
    PUBLIC = "public"
    READ_ONLY = "read_only"
    READ_WRITE = "read_write"
    ADMIN = "admin"


@dataclass
class EncryptionKey:
    """Encryption key information."""
    key_id: str
    key_name: str
    key_type: EncryptionType
    key_value: bytes
    salt: bytes = b""
    created_at: float = field(default_factory=time.time)
    expires_at: Optional[float] = None
    is_active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_expired(self) -> bool:
        """Check if key is expired."""
        if self.expires_at is None:
            return False
        return time.time() > self.expires_at


@dataclass
class AccessControl:
    """Access control rule."""
    rule_id: str
    resource: str
    user_id: str
    access_level: AccessLevel
    conditions: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    expires_at: Optional[float] = None


@dataclass
class SecurityAudit:
    """Security audit log entry."""
    audit_id: str
    action: str  # "encrypt", "decrypt", "access_granted", "access_denied", "key_created", "key_deleted"
    user_id: str
    resource: str
    success: bool
    timestamp: float = field(default_factory=time.time)
    details: Dict[str, Any] = field(default_factory=dict)


class DataSecurityService(Service):
    """Data security service as per Runtime Specification."""
    
    # Service dependencies
    DEPENDENCIES = []
    
    def __init__(self):
        super().__init__("data_security_service")
        self._encryption_keys: Dict[str, EncryptionKey] = {}
        self._access_controls: Dict[str, AccessControl] = {}
        self._security_audits: List[SecurityAudit] = []
        self._audit_history: deque = deque(maxlen=10000)
        self._lock = threading.Lock()
        self._master_key: Optional[bytes] = None
        self._fernet_instances: Dict[str, Fernet] = {}
        self._key_rotation_interval = 2592000  # 30 days in seconds
        
    def init(self, event_bus: EventBus, config: Dict[str, Any]) -> bool:
        """Initialize the data security service."""
        try:
            self.event_bus = event_bus
            self.state = ServiceState.INITIALIZING
            
            # Load configuration
            security_config = config.get("data_security", {})
            self._key_rotation_interval = security_config.get("key_rotation_interval", 2592000)
            
            # Initialize master key
            master_key = security_config.get("master_key")
            if master_key:
                self._master_key = master_key.encode() if isinstance(master_key, str) else master_key
            else:
                self._master_key = self._generate_master_key()
            
            # Initialize default encryption key
            self._init_default_keys()
            
            logger.info("Data Security Service initialized")
            return True
        except Exception as e:
            logger.error(f"Data Security Service initialization failed: {e}")
            self.state = ServiceState.ERROR
            return False
    
    def start(self) -> bool:
        """Start the data security service."""
        try:
            self.state = ServiceState.STARTING
            
            # Start background key rotation
            self._start_key_rotation()
            
            # Start background audit cleanup
            self._start_audit_cleanup()
            
            self.state = ServiceState.RUNNING
            self.emit_event(str(EventType.SERVICE_START), {"service": self.name})
            logger.info("Data Security Service started")
            return True
        except Exception as e:
            logger.error(f"Data Security Service start failed: {e}")
            self.state = ServiceState.ERROR
            self.emit_event(str(EventType.SERVICE_CRASH), {"service": self.name, "error": str(e)})
            return False
    
    def stop(self) -> bool:
        """Stop the data security service."""
        try:
            self.state = ServiceState.STOPPING
            self.state = ServiceState.STOPPED
            self.emit_event(str(EventType.SERVICE_STOP), {"service": self.name})
            logger.info("Data Security Service stopped")
            return True
        except Exception as e:
            logger.error(f"Data Security Service stop failed: {e}")
            self.state = ServiceState.ERROR
            return False
    
    def health(self) -> ServiceHealth:
        """Get data security service health."""
        return ServiceHealth(
            service=self.name,
            state=self.state,
            healthy=self.state == ServiceState.RUNNING,
            message=f"Data Security Service - {len(self._encryption_keys)} encryption keys",
            details={
                "total_keys": len(self._encryption_keys),
                "active_keys": sum(1 for k in self._encryption_keys.values() if k.is_active),
                "access_controls": len(self._access_controls),
                "security_audits": len(self._security_audits),
                "master_key_set": self._master_key is not None
            },
            timestamp=time.time()
        )
    
    def create_encryption_key(self, key_name: str, key_type: EncryptionType = EncryptionType.FERNET,
                            expires_days: int = None) -> EncryptionKey:
        """Create a new encryption key."""
        key_id = self._generate_id()
        
        if key_type == EncryptionType.FERNET:
            key_value = Fernet.generate_key()
        elif key_type == EncryptionType.AES_256:
            key_value = secrets.token_bytes(32)  # 256 bits
        else:
            key_value = secrets.token_bytes(32)
        
        salt = secrets.token_bytes(16)
        expires_at = None
        if expires_days:
            expires_at = time.time() + (expires_days * 86400)
        
        encryption_key = EncryptionKey(
            key_id=key_id,
            key_name=key_name,
            key_type=key_type,
            key_value=key_value,
            salt=salt,
            expires_at=expires_at
        )
        
        with self._lock:
            self._encryption_keys[key_id] = encryption_key
            
            # Create Fernet instance if applicable
            if key_type == EncryptionType.FERNET:
                self._fernet_instances[key_id] = Fernet(key_value)
        
        self._log_audit("key_created", "system", key_name, True, {"key_id": key_id, "key_type": key_type.value})
        
        logger.info(f"Created encryption key: {key_name}")
        return encryption_key
    
    def encrypt_data(self, data: str, key_id: str) -> Optional[bytes]:
        """Encrypt data using specified key."""
        with self._lock:
            key = self._encryption_keys.get(key_id)
            if not key or not key.is_active:
                self._log_audit("encrypt", "system", key_id, False, {"reason": "key_not_found_or_inactive"})
                return None
            
            if key.is_expired():
                self._log_audit("encrypt", "system", key_id, False, {"reason": "key_expired"})
                return None
            
            try:
                if key.key_type == EncryptionType.FERNET and key_id in self._fernet_instances:
                    fernet = self._fernet_instances[key_id]
                    encrypted = fernet.encrypt(data.encode())
                else:
                    # Fallback encryption
                    encrypted = self._fallback_encrypt(data.encode(), key.key_value, key.salt)
                
                self._log_audit("encrypt", "system", key_id, True, {"data_length": len(data)})
                return encrypted
                
            except Exception as e:
                self._log_audit("encrypt", "system", key_id, False, {"error": str(e)})
                logger.error(f"Encryption failed: {e}")
                return None
    
    def decrypt_data(self, encrypted_data: bytes, key_id: str) -> Optional[str]:
        """Decrypt data using specified key."""
        with self._lock:
            key = self._encryption_keys.get(key_id)
            if not key or not key.is_active:
                self._log_audit("decrypt", "system", key_id, False, {"reason": "key_not_found_or_inactive"})
                return None
            
            if key.is_expired():
                self._log_audit("decrypt", "system", key_id, False, {"reason": "key_expired"})
                return None
            
            try:
                if key.key_type == EncryptionType.FERNET and key_id in self._fernet_instances:
                    fernet = self._fernet_instances[key_id]
                    decrypted = fernet.decrypt(encrypted_data)
                else:
                    # Fallback decryption
                    decrypted = self._fallback_decrypt(encrypted_data, key.key_value, key.salt)
                
                self._log_audit("decrypt", "system", key_id, True, {"data_length": len(decrypted)})
                return decrypted.decode()
                
            except Exception as e:
                self._log_audit("decrypt", "system", key_id, False, {"error": str(e)})
                logger.error(f"Decryption failed: {e}")
                return None
    
    def grant_access(self, resource: str, user_id: str, access_level: AccessLevel,
                   conditions: Dict[str, Any] = None, expires_hours: int = None) -> bool:
        """Grant access to a resource."""
        rule_id = self._generate_id()
        expires_at = None
        if expires_hours:
            expires_at = time.time() + (expires_hours * 3600)
        
        access_control = AccessControl(
            rule_id=rule_id,
            resource=resource,
            user_id=user_id,
            access_level=access_level,
            conditions=conditions or {},
            expires_at=expires_at
        )
        
        with self._lock:
            self._access_controls[rule_id] = access_control
        
        self._log_audit("access_granted", user_id, resource, True, {"access_level": access_level.value})
        
        logger.info(f"Granted {access_level.value} access to {resource} for user {user_id}")
        return True
    
    def revoke_access(self, resource: str, user_id: str) -> bool:
        """Revoke access to a resource."""
        with self._lock:
            revoked_rules = []
            for rule_id, access_control in self._access_controls.items():
                if access_control.resource == resource and access_control.user_id == user_id:
                    del self._access_controls[rule_id]
                    revoked_rules.append(rule_id)
            
            if revoked_rules:
                self._log_audit("access_revoked", user_id, resource, True, {"revoked_rules": len(revoked_rules)})
                logger.info(f"Revoked access to {resource} for user {user_id}")
                return True
            
            return False
    
    def check_access(self, resource: str, user_id: str, required_level: AccessLevel = AccessLevel.READ_ONLY) -> bool:
        """Check if user has required access level to resource."""
        with self._lock:
            for access_control in self._access_controls.values():
                if access_control.resource == resource and access_control.user_id == user_id:
                    # Check if expired
                    if access_control.expires_at and time.time() > access_control.expires_at:
                        continue
                    
                    # Check conditions
                    if access_control.conditions:
                        # In a real implementation, check conditions here
                        pass
                    
                    # Check access level
                    level_hierarchy = {
                        AccessLevel.PUBLIC: 0,
                        AccessLevel.READ_ONLY: 1,
                        AccessLevel.READ_WRITE: 2,
                        AccessLevel.ADMIN: 3
                    }
                    
                    if level_hierarchy.get(access_control.access_level, 0) >= level_hierarchy.get(required_level, 0):
                        self._log_audit("access_granted", user_id, resource, True, {"access_level": access_control.access_level.value})
                        return True
            
            self._log_audit("access_denied", user_id, resource, True, {"required_level": required_level.value})
            return False
    
    def rotate_key(self, key_id: str) -> Optional[EncryptionKey]:
        """Rotate an encryption key."""
        with self._lock:
            old_key = self._encryption_keys.get(key_id)
            if not old_key:
                return None
            
            # Create new key
            new_key = self.create_encryption_key(
                f"{old_key.key_name}_rotated",
                old_key.key_type,
                None if old_key.expires_at is None else int((old_key.expires_at - time.time()) / 86400)
            )
            
            # Mark old key as inactive
            old_key.is_active = False
            
            self._log_audit("key_rotated", "system", key_id, True, {"old_key_id": key_id, "new_key_id": new_key.key_id})
            
            logger.info(f"Rotated encryption key: {key_id}")
            return new_key
    
    def delete_key(self, key_id: str) -> bool:
        """Delete an encryption key."""
        with self._lock:
            if key_id not in self._encryption_keys:
                return False
            
            del self._encryption_keys[key_id]
            
            if key_id in self._fernet_instances:
                del self._fernet_instances[key_id]
            
            self._log_audit("key_deleted", "system", key_id, True, {})
            
            logger.info(f"Deleted encryption key: {key_id}")
            return True
    
    def get_security_audits(self, user_id: str = None, action: str = None,
                          limit: int = 100) -> List[SecurityAudit]:
        """Get security audit logs."""
        with self._lock:
            audits = self._security_audits
            
            if user_id:
                audits = [a for a in audits if a.user_id == user_id]
            
            if action:
                audits = [a for a in audits if a.action == action]
            
            return audits[-limit:]
    
    def get_security_stats(self) -> Dict[str, Any]:
        """Get security statistics."""
        with self._lock:
            total_audits = len(self._security_audits)
            successful_ops = sum(1 for a in self._security_audits if a.success)
            failed_ops = sum(1 for a in self._security_audits if not a.success)
            
            # Calculate success rate
            success_rate = successful_ops / total_audits if total_audits > 0 else 0.0
            
            # Count by action type
            action_counts = defaultdict(int)
            for audit in self._security_audits:
                action_counts[audit.action] += 1
            
            return {
                "total_audits": total_audits,
                "successful_operations": successful_ops,
                "failed_operations": failed_ops,
                "success_rate": success_rate,
                "active_keys": sum(1 for k in self._encryption_keys.values() if k.is_active),
                "access_controls": len(self._access_controls),
                "action_counts": dict(action_counts)
            }
    
    def _fallback_encrypt(self, data: bytes, key: bytes, salt: bytes) -> bytes:
        """Fallback encryption when cryptography library not available."""
        # Simple XOR-based encryption (not secure, only for fallback)
        key_extended = (key + salt) * ((len(data) // len(key + salt)) + 1)
        encrypted = bytes(a ^ b for a, b in zip(data, key_extended[:len(data)]))
        return encrypted
    
    def _fallback_decrypt(self, encrypted: bytes, key: bytes, salt: bytes) -> bytes:
        """Fallback decryption when cryptography library not available."""
        # Simple XOR-based decryption (not secure, only for fallback)
        key_extended = (key + salt) * ((len(encrypted) // len(key + salt)) + 1)
        decrypted = bytes(a ^ b for a, b in zip(encrypted, key_extended[:len(encrypted)]))
        return decrypted
    
    def _generate_master_key(self) -> bytes:
        """Generate a master key."""
        return secrets.token_bytes(32)
    
    def _log_audit(self, action: str, user_id: str, resource: str, success: bool,
                 details: Dict[str, Any] = None) -> None:
        """Log a security audit entry."""
        audit = SecurityAudit(
            audit_id=self._generate_id(),
            action=action,
            user_id=user_id,
            resource=resource,
            success=success,
            details=details or {}
        )
        
        self._security_audits.append(audit)
        self._audit_history.append(audit)
        
        # Emit high-priority events
        if not success and action in ["encrypt", "decrypt", "access_granted"]:
            self.emit_event(str(EventType.AI_DECISION), {
                "service": self.name,
                "action": action,
                "user_id": user_id,
                "resource": resource,
                "details": details
            })
    
    def _init_default_keys(self) -> None:
        """Initialize default encryption keys."""
        # Create default encryption key
        default_key = self.create_encryption_key(
            "default",
            EncryptionType.FERNET,
            expires_days=365
        )
        logger.info(f"Created default encryption key: {default_key.key_id}")
    
    def _start_key_rotation(self) -> None:
        """Start background key rotation."""
        def rotate_keys():
            while self.state == ServiceState.RUNNING:
                try:
                    with self._lock:
                        current_time = time.time()
                        for key_id, key in self._encryption_keys.items():
                            if key.is_active and key.expires_at and current_time > key.expires_at:
                                self.rotate_key(key_id)
                    
                    time.sleep(3600)  # Check every hour
                except Exception as e:
                    logger.error(f"Key rotation error: {e}")
                    time.sleep(300)
        
        thread = threading.Thread(target=rotate_keys, daemon=True)
        thread.start()
        logger.info("Key rotation started")
    
    def _start_audit_cleanup(self) -> None:
        """Start background audit cleanup."""
        def cleanup_audits():
            while self.state == ServiceState.RUNNING:
                try:
                    with self._lock:
                        cutoff_time = time.time() - (90 * 86400)  # 90 days
                        self._security_audits = [a for a in self._security_audits if a.timestamp > cutoff_time]
                    
                    logger.info(f"Audit cleanup: {len(self._security_audits)} audits retained")
                    time.sleep(86400)  # Clean up daily
                except Exception as e:
                    logger.error(f"Audit cleanup error: {e}")
                    time.sleep(3600)
        
        thread = threading.Thread(target=cleanup_audits, daemon=True)
        thread.start()
        logger.info("Audit cleanup started")
    
    def _generate_id(self) -> str:
        """Generate unique ID."""
        import uuid
        return str(uuid.uuid4())


# Global instance
_data_security_service: Optional[DataSecurityService] = None


def get_data_security_service() -> DataSecurityService:
    """Get global data security service instance."""
    global _data_security_service
    if _data_security_service is None:
        _data_security_service = DataSecurityService()
    return _data_security_service