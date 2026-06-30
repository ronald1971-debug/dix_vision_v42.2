"""
DIX VISION Session Restoration Service

Implements session restoration as per Runtime Specification.
Handles session state management, persistence, and recovery.
"""

from __future__ import annotations

import gzip
import json
import logging
import threading
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from runtime.event_bus import EventBus, Event, EventType, get_event_bus
from runtime.service_manager import Service, ServiceState, ServiceHealth
from runtime.platform_abstraction import get_platform_manager

logger = logging.getLogger(__name__)


class SessionState(Enum):
    """Session restoration states."""
    IDLE = "IDLE"
    LOADING = "LOADING"
    SAVING = "SAVING"
    ERROR = "ERROR"
    STOPPED = "STOPPED"


@dataclass
class Session:
    """Represents a user session."""
    session_id: str
    user_id: str
    created_at: float
    last_accessed: float
    state: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


class SessionStorage(ABC):
    """Abstract interface for session storage."""
    
    @abstractmethod
    def save_session(self, session: Session) -> bool:
        """Save session to storage."""
        pass
    
    @abstractmethod
    def load_session(self, session_id: str) -> Optional[Session]:
        """Load session from storage."""
        pass
    
    @abstractmethod
    def delete_session(self, session_id: str) -> bool:
        """Delete session from storage."""
        pass
    
    @abstractmethod
    def list_sessions(self) -> List[str]:
        """List all session IDs."""
        pass


class FileSessionStorage(SessionStorage):
    """File-based session storage implementation with compression support."""
    
    def __init__(self, storage_dir: Optional[Path] = None, enable_compression: bool = True, compression_threshold: int = 1024):
        self.storage_dir = storage_dir or Path.cwd() / "sessions"
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self.enable_compression = enable_compression
        self.compression_threshold = compression_threshold  # Compress sessions larger than this size (bytes)
        self.compression_stats = {
            "compressed_saves": 0,
            "uncompressed_saves": 0,
            "total_compressed_size": 0,
            "total_uncompressed_size": 0
        }
    
    def _get_session_path(self, session_id: str) -> Path:
        """Get file path for a session."""
        return self.storage_dir / f"{session_id}.json"
    
    def _get_compressed_session_path(self, session_id: str) -> Path:
        """Get compressed file path for a session."""
        return self.storage_dir / f"{session_id}.json.gz"
    
    def _should_compress(self, session_data: Dict[str, Any]) -> bool:
        """Determine if session should be compressed based on size."""
        if not self.enable_compression:
            return False
        
        # Calculate size of serialized data
        serialized = json.dumps(session_data).encode('utf-8')
        return len(serialized) > self.compression_threshold
    
    def _compress_data(self, data: str) -> bytes:
        """Compress data using gzip."""
        return gzip.compress(data.encode('utf-8'))
    
    def _decompress_data(self, compressed_data: bytes) -> str:
        """Decompress gzip data."""
        return gzip.decompress(compressed_data).decode('utf-8')
    
    def save_session(self, session: Session) -> bool:
        """Save session to file with optional compression."""
        try:
            session_data = {
                "session_id": session.session_id,
                "user_id": session.user_id,
                "created_at": session.created_at,
                "last_accessed": session.last_accessed,
                "state": session.state,
                "metadata": session.metadata
            }
            
            # Determine if we should compress
            should_compress = self._should_compress(session_data)
            
            with self._lock:
                if should_compress:
                    # Compressed storage
                    session_path = self._get_compressed_session_path(session.session_id)
                    serialized_data = json.dumps(session_data)
                    compressed_data = self._compress_data(serialized_data)
                    
                    with open(session_path, 'wb') as f:
                        f.write(compressed_data)
                    
                    # Update stats
                    self.compression_stats["compressed_saves"] += 1
                    self.compression_stats["total_compressed_size"] += len(compressed_data)
                    self.compression_stats["total_uncompressed_size"] += len(serialized_data)
                    
                    # Remove uncompressed version if it exists
                    uncompressed_path = self._get_session_path(session.session_id)
                    if uncompressed_path.exists():
                        uncompressed_path.unlink()
                    
                    logger.info(f"Session saved (compressed): {session.session_id} - {len(serialized_data)} -> {len(compressed_data)} bytes")
                else:
                    # Uncompressed storage
                    session_path = self._get_session_path(session.session_id)
                    
                    with open(session_path, 'w') as f:
                        json.dump(session_data, f, indent=2)
                    
                    # Update stats
                    self.compression_stats["uncompressed_saves"] += 1
                    
                    # Remove compressed version if it exists
                    compressed_path = self._get_compressed_session_path(session.session_id)
                    if compressed_path.exists():
                        compressed_path.unlink()
                    
                    logger.info(f"Session saved (uncompressed): {session.session_id}")
            
            return True
        except Exception as e:
            logger.error(f"Failed to save session {session.session_id}: {e}")
            return False
    
    def load_session(self, session_id: str) -> Optional[Session]:
        """Load session from file with automatic decompression."""
        try:
            # Check for compressed version first
            compressed_path = self._get_compressed_session_path(session_id)
            uncompressed_path = self._get_session_path(session_id)
            
            session_data = None
            
            with self._lock:
                if compressed_path.exists():
                    # Load and decompress
                    with open(compressed_path, 'rb') as f:
                        compressed_data = f.read()
                    
                    serialized_data = self._decompress_data(compressed_data)
                    session_data = json.loads(serialized_data)
                    logger.info(f"Session loaded (compressed): {session_id}")
                elif uncompressed_path.exists():
                    # Load uncompressed
                    with open(uncompressed_path, 'r') as f:
                        session_data = json.load(f)
                    logger.info(f"Session loaded (uncompressed): {session_id}")
                else:
                    logger.warning(f"Session file not found: {session_id}")
                    return None
            
            session = Session(
                session_id=session_data["session_id"],
                user_id=session_data["user_id"],
                created_at=session_data["created_at"],
                last_accessed=session_data["last_accessed"],
                state=session_data["state"],
                metadata=session_data.get("metadata", {})
            )
            
            return session
        except Exception as e:
            logger.error(f"Failed to load session {session_id}: {e}")
            return None
    
    def delete_session(self, session_id: str) -> bool:
        """Delete session file (both compressed and uncompressed versions)."""
        try:
            compressed_path = self._get_compressed_session_path(session_id)
            uncompressed_path = self._get_session_path(session_id)
            
            with self._lock:
                deleted = False
                if compressed_path.exists():
                    compressed_path.unlink()
                    deleted = True
                if uncompressed_path.exists():
                    uncompressed_path.unlink()
                    deleted = True
                
                if deleted:
                    logger.info(f"Session deleted: {session_id}")
                return deleted
        except Exception as e:
            logger.error(f"Failed to delete session {session_id}: {e}")
            return False
    
    def list_sessions(self) -> List[str]:
        """List all session IDs (both compressed and uncompressed)."""
        try:
            session_ids = set()
            
            # List uncompressed sessions
            for f in self.storage_dir.glob("*.json"):
                if not f.name.endswith(".gz"):  # Exclude compressed files
                    session_ids.add(f.stem)
            
            # List compressed sessions
            for f in self.storage_dir.glob("*.json.gz"):
                # Remove .json.gz extension to get session ID
                session_id = f.name[:-8]  # Remove ".json.gz"
                session_ids.add(session_id)
            
            return list(session_ids)
        except Exception as e:
            logger.error(f"Failed to list sessions: {e}")
            return []
    
    def get_compression_stats(self) -> Dict[str, Any]:
        """Get compression statistics."""
        with self._lock:
            stats = self.compression_stats.copy()
            
            # Calculate compression ratio
            if stats["total_uncompressed_size"] > 0:
                stats["compression_ratio"] = stats["total_compressed_size"] / stats["total_uncompressed_size"]
                stats["space_saved"] = stats["total_uncompressed_size"] - stats["total_compressed_size"]
                stats["space_saved_percent"] = (stats["space_saved"] / stats["total_uncompressed_size"]) * 100
            else:
                stats["compression_ratio"] = 0.0
                stats["space_saved"] = 0
                stats["space_saved_percent"] = 0.0
            
            return stats


class SessionRestorationService(Service):
    """Session restoration service as per Runtime Specification."""
    
    # Service dependencies
    DEPENDENCIES = ["memory_service"]
    
    def __init__(self):
        super().__init__("session_restoration")
        self.session_state = SessionState.IDLE
        self.session_storage: Optional[SessionStorage] = None
        self.active_sessions: Dict[str, Session] = {}
        self._lock = threading.Lock()
        self.quarantined_sessions: Dict[str, str] = {}  # session_id -> error reason
        
    def init(self, event_bus: EventBus, config: Dict[str, Any]) -> bool:
        """Initialize the session restoration service."""
        try:
            self.event_bus = event_bus
            self.config = config
            self.state = ServiceState.INITIALIZING
            
            # Initialize session storage with compression configuration
            platform_manager = get_platform_manager()
            data_dir = platform_manager.get_data_directory()
            
            # Get compression settings from config
            enable_compression = config.get("session_compression", {}).get("enabled", True)
            compression_threshold = config.get("session_compression", {}).get("threshold_bytes", 1024)
            
            self.session_storage = FileSessionStorage(
                data_dir / "sessions",
                enable_compression=enable_compression,
                compression_threshold=compression_threshold
            )
            
            logger.info(f"Session Restoration Service initialized (compression: {enable_compression}, threshold: {compression_threshold} bytes)")
            return True
        except Exception as e:
            logger.error(f"Session Restoration Service initialization failed: {e}")
            self.state = ServiceState.ERROR
            return False
    
    def start(self) -> bool:
        """Start the session restoration service."""
        try:
            self.state = ServiceState.STARTING
            self.session_state = SessionState.IDLE
            
            # Load all sessions from storage
            self._load_all_sessions()
            
            self.state = ServiceState.RUNNING
            self.emit_event(str(EventType.SERVICE_START), {"service": self.name})
            logger.info(f"Session Restoration Service started with {len(self.active_sessions)} sessions")
            return True
        except Exception as e:
            logger.error(f"Session Restoration Service start failed: {e}")
            self.state = ServiceState.ERROR
            self.session_state = SessionState.ERROR
            self.emit_event(str(EventType.SERVICE_CRASH), {"service": self.name, "error": str(e)})
            return False
    
    def stop(self) -> bool:
        """Stop the session restoration service."""
        try:
            self.state = ServiceState.STOPPING
            self.session_state = SessionState.STOPPED
            
            # Save all active sessions
            self._save_all_sessions()
            
            self.state = ServiceState.STOPPED
            self.emit_event(str(EventType.SERVICE_STOP), {"service": self.name})
            logger.info("Session Restoration Service stopped")
            return True
        except Exception as e:
            logger.error(f"Session Restoration Service stop failed: {e}")
            self.state = ServiceState.ERROR
            self.emit_event(str(EventType.SERVICE_CRASH), {"service": self.name, "error": str(e)})
            return False
    
    def health(self) -> ServiceHealth:
        """Get session restoration service health."""
        compression_stats = {}
        if hasattr(self.session_storage, 'get_compression_stats'):
            compression_stats = self.session_storage.get_compression_stats()
        
        return ServiceHealth(
            service=self.name,
            state=self.state,
            healthy=self.state == ServiceState.RUNNING,
            message=f"Session State: {self.session_state.value} - Active: {len(self.active_sessions)}",
            details={
                "session_state": self.session_state.value,
                "active_sessions": len(self.active_sessions),
                "quarantined_sessions": len(self.quarantined_sessions),
                "storage_dir": str(self.session_storage.storage_dir) if self.session_storage else None,
                "compression_stats": compression_stats
            },
            timestamp=time.time()
        )
    
    def _load_all_sessions(self) -> None:
        """Load all sessions from storage with validation."""
        try:
            session_ids = self.session_storage.list_sessions()
            loaded_count = 0
            failed_count = 0
            validation_errors = []
            
            for session_id in session_ids:
                session = self.session_storage.load_session(session_id)
                if session:
                    # Validate session before loading
                    validation_result = self._validate_session(session)
                    if validation_result['valid']:
                        with self._lock:
                            self.active_sessions[session_id] = session
                        loaded_count += 1
                    else:
                        failed_count += 1
                        validation_errors.append({
                            "session_id": session_id,
                            "errors": validation_result['errors']
                        })
                        logger.warning(f"Session validation failed for {session_id}: {validation_result['errors']}")
                        # Optionally move corrupted sessions to quarantine
                        self._quarantine_corrupted_session(session_id)
            
            logger.info(f"Loaded {loaded_count} sessions from storage ({failed_count} failed validation)")
            
            # Emit session loaded event with validation results
            self.emit_event("SESSION_LOADED", {
                "service": self.name,
                "session_count": loaded_count,
                "failed_count": failed_count,
                "session_ids": list(self.active_sessions.keys()),
                "validation_errors": validation_errors
            })
        except Exception as e:
            logger.error(f"Failed to load sessions: {e}")
            self.emit_event("SESSION_LOAD_ERROR", {
                "service": self.name,
                "error": str(e)
            })
    
    def _save_all_sessions(self) -> None:
        """Save all active sessions to storage."""
        try:
            with self._lock:
                for session in self.active_sessions.values():
                    session.last_accessed = time.time()
                    self.session_storage.save_session(session)
            
            logger.info(f"Saved {len(self.active_sessions)} sessions to storage")
            # Emit session saved event
            self.emit_event("SESSION_SAVED", {
                "service": self.name,
                "session_count": len(self.active_sessions),
                "session_ids": list(self.active_sessions.keys())
            })
        except Exception as e:
            logger.error(f"Failed to save sessions: {e}")
            self.emit_event("SESSION_SAVE_ERROR", {
                "service": self.name,
                "error": str(e)
            })
    
    def _validate_session(self, session: Session) -> Dict[str, Any]:
        """Validate a session's structure and data integrity."""
        errors = []
        
        # Validate required fields
        if not session.session_id or not isinstance(session.session_id, str):
            errors.append("Invalid or missing session_id")
        
        if not session.user_id or not isinstance(session.user_id, str):
            errors.append("Invalid or missing user_id")
        
        if session.created_at <= 0:
            errors.append("Invalid created_at timestamp")
        
        if session.last_accessed <= 0:
            errors.append("Invalid last_accessed timestamp")
        
        # Validate state is a dictionary
        if not isinstance(session.state, dict):
            errors.append("Session state must be a dictionary")
        
        # Validate metadata is a dictionary
        if not isinstance(session.metadata, dict):
            errors.append("Session metadata must be a dictionary")
        
        # Check for session age (optional - sessions older than 30 days may be flagged)
        session_age_days = (time.time() - session.created_at) / (24 * 3600)
        if session_age_days > 30:
            errors.append(f"Session is very old: {session_age_days:.1f} days")
        
        # Check state size (optional - very large sessions may indicate corruption)
        if len(str(session.state)) > 10_000_000:  # 10MB of JSON
            errors.append(f"Session state is unusually large: {len(str(session.state))} characters")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "session_age_days": session_age_days,
            "state_size_bytes": len(str(session.state))
        }
    
    def _quarantine_corrupted_session(self, session_id: str) -> None:
        """Move corrupted session to quarantine directory."""
        try:
            if not self.session_storage:
                return
            
            quarantine_dir = self.session_storage.storage_dir / "quarantine"
            quarantine_dir.mkdir(exist_ok=True)
            
            # Move corrupted session file to quarantine
            session_path = self.session_storage._get_session_path(session_id)
            if session_path.exists():
                quarantine_path = quarantine_dir / f"{session_id}_corrupted_{int(time.time())}.json"
                session_path.rename(quarantine_path)
                logger.info(f"Quarantined corrupted session: {session_id} -> {quarantine_path}")
        except Exception as e:
            logger.error(f"Failed to quarantine session {session_id}: {e}")
    
    def create_session(self, user_id: str, initial_state: Dict[str, Any] = None) -> str:
        """Create a new session with validation."""
        try:
            session_id = f"session_{int(time.time() * 1000)}"
            session = Session(
                session_id=session_id,
                user_id=user_id,
                created_at=time.time(),
                last_accessed=time.time(),
                state=initial_state or {},
                metadata={"created_by": "session_restoration_service"}
            )
            
            # Validate new session before adding
            validation_result = self._validate_session(session)
            if not validation_result['valid']:
                logger.error(f"New session validation failed: {validation_result['errors']}")
                raise ValueError(f"Invalid session data: {validation_result['errors']}")
            
            with self._lock:
                self.active_sessions[session_id] = session
            
            # Save to storage
            if self.session_storage.save_session(session):
                logger.info(f"Created session: {session_id} for user: {user_id}")
                self.emit_event("SESSION_CREATED", {
                    "service": self.name,
                    "session_id": session_id,
                    "user_id": user_id
                })
                return session_id
            else:
                raise IOError("Failed to save session to storage")
        except Exception as e:
            logger.error(f"Failed to create session: {e}")
            raise
    
    def get_session(self, session_id: str) -> Optional[Session]:
        """Get an active session."""
        with self._lock:
            session = self.active_sessions.get(session_id)
            if session:
                session.last_accessed = time.time()
            return session
    
    def update_session_state(self, session_id: str, updates: Dict[str, Any]) -> bool:
        """Update session state."""
        try:
            with self._lock:
                session = self.active_sessions.get(session_id)
                if session:
                    session.state.update(updates)
                    session.last_accessed = time.time()
                    return True
            return False
        except Exception as e:
            logger.error(f"Failed to update session state: {e}")
            return False
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session."""
        try:
            with self._lock:
                if session_id in self.active_sessions:
                    del self.active_sessions[session_id]
            
            # Delete from storage
            self.session_storage.delete_session(session_id)
            
            logger.info(f"Deleted session: {session_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete session: {e}")
            return False


__all__ = [
    "SessionRestorationService",
    "SessionState",
    "Session",
    "SessionStorage",
    "FileSessionStorage",
]