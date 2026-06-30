"""
DIX VISION API Security Service

Provides enhanced API authentication, rate limiting, API key management,
API encryption, and API monitoring for enhanced security.
"""

from __future__ import annotations

import hashlib
import hmac
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

from runtime.event_bus import EventBus, Event, EventType, get_event_bus
from runtime.service_manager import Service, ServiceState, ServiceHealth

logger = logging.getLogger(__name__)


class AuthMethod(Enum):
    """Authentication methods."""
    API_KEY = "api_key"
    JWT = "jwt"
    OAUTH2 = "oauth2"
    BASIC = "basic"
    MUTUAL_TLS = "mutual_tls"


class RateLimitStrategy(Enum):
    """Rate limiting strategies."""
    TOKEN_BUCKET = "token_bucket"
    LEAKY_BUCKET = "leaky_bucket"
    FIXED_WINDOW = "fixed_window"
    SLIDING_WINDOW = "sliding_window"


@dataclass
class APIKey:
    """API key information."""
    key_id: str
    key_value: str
    user_id: str
    permissions: List[str]
    rate_limit: int = 1000  # requests per hour
    created_at: float = field(default_factory=time.time)
    expires_at: Optional[float] = None
    is_active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_expired(self) -> bool:
        """Check if API key is expired."""
        if self.expires_at is None:
            return False
        return time.time() > self.expires_at
    
    def to_dict(self, safe: bool = True) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "key_id": self.key_id,
            "key_value": "***" if safe else self.key_value,
            "user_id": self.user_id,
            "permissions": self.permissions,
            "rate_limit": self.rate_limit,
            "created_at": self.created_at,
            "expires_at": self.expires_at,
            "is_active": self.is_active,
            "metadata": self.metadata
        }


@dataclass
class RateLimitState:
    """Rate limit state for a client."""
    client_id: str
    tokens: float = 1000.0
    last_update: float = field(default_factory=time.time)
    request_count: int = 0
    window_start: float = field(default_factory=time.time)


@dataclass
class SecurityEvent:
    """Security event record."""
    event_id: str
    event_type: str  # "auth_success", "auth_failure", "rate_limit_exceeded", "api_call"
    client_id: str
    endpoint: str
    timestamp: float = field(default_factory=time.time)
    details: Dict[str, Any] = field(default_factory=dict)
    severity: str = "info"


class APISecurityService(Service):
    """API security service as per Runtime Specification."""
    
    # Service dependencies
    DEPENDENCIES = []
    
    def __init__(self):
        super().__init__("api_security_service")
        self._api_keys: Dict[str, APIKey] = {}
        self._user_keys: Dict[str, List[str]] = defaultdict(list)
        self._rate_limits: Dict[str, RateLimitState] = {}
        self._security_events: List[SecurityEvent] = []
        self._event_history: deque = deque(maxlen=10000)
        self._lock = threading.Lock()
        self._rate_limit_strategy = RateLimitStrategy.TOKEN_BUCKET
        self._default_rate_limit = 1000  # requests per hour
        self._rate_limit_window = 3600  # 1 hour
        self._jwt_secret: Optional[str] = None
        self._encryption_key: Optional[str] = None
        
    def init(self, event_bus: EventBus, config: Dict[str, Any]) -> bool:
        """Initialize the API security service."""
        try:
            self.event_bus = event_bus
            self.state = ServiceState.INITIALIZING
            
            # Load configuration
            security_config = config.get("api_security", {})
            self._rate_limit_strategy = RateLimitStrategy(security_config.get("rate_limit_strategy", "token_bucket"))
            self._default_rate_limit = security_config.get("default_rate_limit", 1000)
            self._rate_limit_window = security_config.get("rate_limit_window", 3600)
            self._jwt_secret = security_config.get("jwt_secret")
            self._encryption_key = security_config.get("encryption_key")
            
            # Initialize default admin key
            self._init_default_keys()
            
            logger.info("API Security Service initialized")
            return True
        except Exception as e:
            logger.error(f"API Security Service initialization failed: {e}")
            self.state = ServiceState.ERROR
            return False
    
    def start(self) -> bool:
        """Start the API security service."""
        try:
            self.state = ServiceState.STARTING
            
            # Start background rate limit refiller
            self._start_rate_limit_refiller()
            
            # Start background security event processor
            self._start_security_event_processor()
            
            # Start background key cleanup
            self._start_key_cleanup()
            
            self.state = ServiceState.RUNNING
            self.emit_event(str(EventType.SERVICE_START), {"service": self.name})
            logger.info("API Security Service started")
            return True
        except Exception as e:
            logger.error(f"API Security Service start failed: {e}")
            self.state = ServiceState.ERROR
            self.emit_event(str(EventType.SERVICE_CRASH), {"service": self.name, "error": str(e)})
            return False
    
    def stop(self) -> bool:
        """Stop the API security service."""
        try:
            self.state = ServiceState.STOPPING
            self.state = ServiceState.STOPPED
            self.emit_event(str(EventType.SERVICE_STOP), {"service": self.name})
            logger.info("API Security Service stopped")
            return True
        except Exception as e:
            logger.error(f"API Security Service stop failed: {e}")
            self.state = ServiceState.ERROR
            return False
    
    def health(self) -> ServiceHealth:
        """Get API security service health."""
        return ServiceHealth(
            service=self.name,
            state=self.state,
            healthy=self.state == ServiceState.RUNNING,
            message=f"API Security Service - {len(self._api_keys)} API keys",
            details={
                "total_api_keys": len(self._api_keys),
                "active_api_keys": sum(1 for k in self._api_keys.values() if k.is_active),
                "rate_limited_clients": len(self._rate_limits),
                "security_events": len(self._security_events),
                "rate_limit_strategy": self._rate_limit_strategy.value
            },
            timestamp=time.time()
        )
    
    def create_api_key(self, user_id: str, permissions: List[str], 
                      rate_limit: int = None, expires_hours: int = None) -> APIKey:
        """Create a new API key."""
        key_id = self._generate_id()
        key_value = secrets.token_urlsafe(32)
        
        expires_at = None
        if expires_hours:
            expires_at = time.time() + (expires_hours * 3600)
        
        api_key = APIKey(
            key_id=key_id,
            key_value=key_value,
            user_id=user_id,
            permissions=permissions,
            rate_limit=rate_limit or self._default_rate_limit,
            expires_at=expires_at
        )
        
        with self._lock:
            self._api_keys[key_id] = api_key
            self._user_keys[user_id].append(key_id)
        
        logger.info(f"Created API key for user {user_id}")
        return api_key
    
    def validate_api_key(self, key_value: str) -> Optional[APIKey]:
        """Validate an API key."""
        with self._lock:
            for api_key in self._api_keys.values():
                if hmac.compare_digest(api_key.key_value, key_value):
                    if not api_key.is_active:
                        self._log_security_event("auth_failure", "api_key", api_key.key_id, 
                                               {"reason": "key_inactive"})
                        return None
                    
                    if api_key.is_expired():
                        self._log_security_event("auth_failure", "api_key", api_key.key_id,
                                               {"reason": "key_expired"})
                        return None
                    
                    self._log_security_event("auth_success", "api_key", api_key.key_id,
                                           {"user_id": api_key.user_id})
                    return api_key
            
            self._log_security_event("auth_failure", "api_key", "unknown", {"reason": "invalid_key"})
            return None
    
    def check_permission(self, api_key: APIKey, permission: str) -> bool:
        """Check if API key has a specific permission."""
        return permission in api_key.permissions or "*" in api_key.permissions
    
    def check_rate_limit(self, client_id: str, cost: int = 1) -> Tuple[bool, Dict[str, Any]]:
        """Check if client is within rate limits."""
        with self._lock:
            if client_id not in self._rate_limits:
                self._rate_limits[client_id] = RateLimitState(client_id=client_id)
            
            state = self._rate_limits[client_id]
            
            if self._rate_limit_strategy == RateLimitStrategy.TOKEN_BUCKET:
                return self._check_token_bucket(state, cost)
            elif self._rate_limit_strategy == RateLimitStrategy.LEAKY_BUCKET:
                return self._check_leaky_bucket(state, cost)
            elif self._rate_limit_strategy == RateLimitStrategy.FIXED_WINDOW:
                return self._check_fixed_window(state, cost)
            elif self._rate_limit_strategy == RateLimitStrategy.SLIDING_WINDOW:
                return self._check_sliding_window(state, cost)
            
            return True, {"remaining": state.tokens}
    
    def revoke_api_key(self, key_id: str) -> bool:
        """Revoke an API key."""
        with self._lock:
            if key_id not in self._api_keys:
                return False
            
            api_key = self._api_keys[key_id]
            api_key.is_active = False
            
            self._log_security_event("key_revoked", "api_key", key_id,
                                   {"user_id": api_key.user_id})
            
            logger.info(f"Revoked API key: {key_id}")
            return True
    
    def delete_api_key(self, key_id: str) -> bool:
        """Delete an API key."""
        with self._lock:
            if key_id not in self._api_keys:
                return False
            
            api_key = self._api_keys[key_id]
            user_id = api_key.user_id
            
            del self._api_keys[key_id]
            self._user_keys[user_id].remove(key_id)
            
            logger.info(f"Deleted API key: {key_id}")
            return True
    
    def get_user_keys(self, user_id: str) -> List[APIKey]:
        """Get all API keys for a user."""
        with self._lock:
            key_ids = self._user_keys.get(user_id, [])
            return [self._api_keys.get(key_id) for key_id in key_ids if key_id in self._api_keys]
    
    def update_api_key_permissions(self, key_id: str, permissions: List[str]) -> bool:
        """Update API key permissions."""
        with self._lock:
            if key_id not in self._api_keys:
                return False
            
            self._api_keys[key_id].permissions = permissions
            logger.info(f"Updated permissions for API key: {key_id}")
            return True
    
    def update_rate_limit(self, key_id: str, rate_limit: int) -> bool:
        """Update rate limit for an API key."""
        with self._lock:
            if key_id not in self._api_keys:
                return False
            
            self._api_keys[key_id].rate_limit = rate_limit
            logger.info(f"Updated rate limit for API key: {key_id}")
            return True
    
    def log_api_call(self, client_id: str, endpoint: str, method: str, 
                   status_code: int, duration: float) -> None:
        """Log an API call for monitoring."""
        self._log_security_event("api_call", client_id, endpoint, {
            "method": method,
            "status_code": status_code,
            "duration": duration
        })
    
    def get_security_events(self, client_id: str = None, event_type: str = None,
                          limit: int = 100) -> List[SecurityEvent]:
        """Get security events."""
        with self._lock:
            events = self._security_events
            
            if client_id:
                events = [e for e in events if e.client_id == client_id]
            
            if event_type:
                events = [e for e in events if e.event_type == event_type]
            
            return events[-limit:]
    
    def get_security_stats(self) -> Dict[str, Any]:
        """Get security statistics."""
        with self._lock:
            total_events = len(self._security_events)
            auth_failures = sum(1 for e in self._security_events if e.event_type == "auth_failure")
            rate_limit_exceeded = sum(1 for e in self._security_events if e.event_type == "rate_limit_exceeded")
            api_calls = sum(1 for e in self._security_events if e.event_type == "api_call")
            
            # Calculate auth success rate
            auth_events = [e for e in self._security_events if e.event_type in ["auth_success", "auth_failure"]]
            auth_success_rate = sum(1 for e in auth_events if e.event_type == "auth_success") / len(auth_events) if auth_events else 0.0
            
            return {
                "total_events": total_events,
                "auth_failures": auth_failures,
                "auth_success_rate": auth_success_rate,
                "rate_limit_exceeded": rate_limit_exceeded,
                "api_calls": api_calls,
                "active_keys": sum(1 for k in self._api_keys.values() if k.is_active),
                "rate_limited_clients": len(self._rate_limits)
            }
    
    def _check_token_bucket(self, state: RateLimitState, cost: int) -> Tuple[bool, Dict[str, Any]]:
        """Check token bucket rate limit."""
        current_time = time.time()
        time_passed = current_time - state.last_update
        
        # Refill tokens based on time passed
        refill_rate = state.tokens / self._rate_limit_window if self._rate_limit_window > 0 else 0
        state.tokens = min(state.tokens + time_passed * refill_rate, self._default_rate_limit)
        state.last_update = current_time
        
        if state.tokens >= cost:
            state.tokens -= cost
            return True, {"remaining": state.tokens, "reset_time": current_time + (state.tokens / refill_rate)}
        else:
            self._log_security_event("rate_limit_exceeded", "rate_limit", state.client_id,
                                   {"tokens": state.tokens, "cost": cost})
            return False, {"remaining": state.tokens, "reset_time": current_time + ((cost - state.tokens) / refill_rate)}
    
    def _check_leaky_bucket(self, state: RateLimitState, cost: int) -> Tuple[bool, Dict[str, Any]]:
        """Check leaky bucket rate limit."""
        current_time = time.time()
        time_passed = current_time - state.last_update
        
        # Leak tokens based on time passed
        leak_rate = self._default_rate_limit / self._rate_limit_window
        state.tokens = max(state.tokens - time_passed * leak_rate, 0)
        state.last_update = current_time
        
        if state.tokens + cost <= self._default_rate_limit:
            state.tokens += cost
            return True, {"remaining": self._default_rate_limit - state.tokens}
        else:
            self._log_security_event("rate_limit_exceeded", "rate_limit", state.client_id,
                                   {"tokens": state.tokens, "cost": cost})
            return False, {"remaining": self._default_rate_limit - state.tokens}
    
    def _check_fixed_window(self, state: RateLimitState, cost: int) -> Tuple[bool, Dict[str, Any]]:
        """Check fixed window rate limit."""
        current_time = time.time()
        
        # Reset window if expired
        if current_time - state.window_start >= self._rate_limit_window:
            state.request_count = 0
            state.window_start = current_time
        
        if state.request_count + cost <= self._default_rate_limit:
            state.request_count += cost
            return True, {"remaining": self._default_rate_limit - state.request_count, "reset_time": state.window_start + self._rate_limit_window}
        else:
            self._log_security_event("rate_limit_exceeded", "rate_limit", state.client_id,
                                   {"count": state.request_count, "cost": cost})
            return False, {"remaining": 0, "reset_time": state.window_start + self._rate_limit_window}
    
    def _check_sliding_window(self, state: RateLimitState, cost: int) -> Tuple[bool, Dict[str, Any]]:
        """Check sliding window rate limit."""
        current_time = time.time()
        
        # Remove old requests from window
        cutoff_time = current_time - self._rate_limit_window
        # In a real implementation, we'd track individual request timestamps
        # For simplicity, we'll use a counter-based approximation
        
        state.request_count += cost
        
        if state.request_count <= self._default_rate_limit:
            return True, {"remaining": self._default_rate_limit - state.request_count}
        else:
            self._log_security_event("rate_limit_exceeded", "rate_limit", state.client_id,
                                   {"count": state.request_count, "cost": cost})
            return False, {"remaining": 0}
    
    def _log_security_event(self, event_type: str, resource_type: str, resource_id: str,
                           details: Dict[str, Any] = None) -> None:
        """Log a security event."""
        event = SecurityEvent(
            event_id=self._generate_id(),
            event_type=event_type,
            client_id=resource_id,
            endpoint=resource_type,
            details=details or {},
            severity="error" if "failure" in event_type or "exceeded" in event_type else "info"
        )
        
        self._security_events.append(event)
        self._event_history.append(event)
        
        # Emit high-severity events
        if event.severity == "error":
            self.emit_event(str(EventType.AI_DECISION), {
                "service": self.name,
                "event_type": event_type,
                "resource_id": resource_id,
                "details": details
            })
    
    def _init_default_keys(self) -> None:
        """Initialize default API keys."""
        # Create admin key
        admin_key = self.create_api_key(
            user_id="admin",
            permissions=["*"],
            rate_limit=10000,
            expires_hours=None
        )
        logger.info(f"Created default admin key: {admin_key.key_id}")
    
    def _start_rate_limit_refiller(self) -> None:
        """Start background rate limit refiller."""
        def refill_rate_limits():
            while self.state == ServiceState.RUNNING:
                try:
                    with self._lock:
                        current_time = time.time()
                        for state in self._rate_limits.values():
                            if self._rate_limit_strategy == RateLimitStrategy.TOKEN_BUCKET:
                                # Token bucket refills automatically on check
                                pass
                            elif self._rate_limit_strategy == RateLimitStrategy.LEAKY_BUCKET:
                                # Leaky bucket leaks automatically on check
                                pass
                            elif self._rate_limit_strategy == RateLimitStrategy.FIXED_WINDOW:
                                if current_time - state.window_start >= self._rate_limit_window:
                                    state.request_count = 0
                                    state.window_start = current_time
                    
                    time.sleep(60)  # Check every minute
                except Exception as e:
                    logger.error(f"Rate limit refill error: {e}")
                    time.sleep(30)
        
        thread = threading.Thread(target=refill_rate_limits, daemon=True)
        thread.start()
        logger.info("Rate limit refiller started")
    
    def _start_security_event_processor(self) -> None:
        """Start background security event processor."""
        def process_events():
            while self.state == ServiceState.RUNNING:
                try:
                    # Analyze security events for patterns
                    with self._lock:
                        recent_events = [e for e in self._security_events 
                                       if time.time() - e.timestamp < 3600]
                        
                        # Check for attack patterns
                        auth_failures = [e for e in recent_events if e.event_type == "auth_failure"]
                        if len(auth_failures) > 100:  # More than 100 failures in an hour
                            logger.warning(f"Potential brute force attack detected: {len(auth_failures)} failures")
                    
                    time.sleep(300)  # Analyze every 5 minutes
                except Exception as e:
                    logger.error(f"Security event processing error: {e}")
                    time.sleep(60)
        
        thread = threading.Thread(target=process_events, daemon=True)
        thread.start()
        logger.info("Security event processor started")
    
    def _start_key_cleanup(self) -> None:
        """Start background key cleanup."""
        def cleanup_keys():
            while self.state == ServiceState.RUNNING:
                try:
                    with self._lock:
                        expired_keys = []
                        for key_id, api_key in self._api_keys.items():
                            if api_key.is_expired():
                                expired_keys.append(key_id)
                        
                        for key_id in expired_keys:
                            self.delete_api_key(key_id)
                    
                    if expired_keys:
                        logger.info(f"Cleaned up {len(expired_keys)} expired API keys")
                    
                    time.sleep(3600)  # Check every hour
                except Exception as e:
                    logger.error(f"Key cleanup error: {e}")
                    time.sleep(300)
        
        thread = threading.Thread(target=cleanup_keys, daemon=True)
        thread.start()
        logger.info("Key cleanup started")
    
    def _generate_id(self) -> str:
        """Generate unique ID."""
        import uuid
        return str(uuid.uuid4())


# Global instance
_api_security_service: Optional[APISecurityService] = None


def get_api_security_service() -> APISecurityService:
    """Get global API security service instance."""
    global _api_security_service
    if _api_security_service is None:
        _api_security_service = APISecurityService()
    return _api_security_service