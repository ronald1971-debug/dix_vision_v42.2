"""
DIX VISION Feature Flags Service

Provides feature flag management with hot reload, A/B testing support,
and feature rollout capabilities.
"""

from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set
from collections import defaultdict, deque
from datetime import datetime
import random
import hashlib

from runtime.event_bus import EventBus, Event, EventType, get_event_bus
from runtime.service_manager import Service, ServiceState, ServiceHealth

logger = logging.getLogger(__name__)


class FlagType(Enum):
    """Types of feature flags."""
    BOOLEAN = "boolean"
    PERCENTAGE = "percentage"
    WHITELIST = "whitelist"
    BLACKLIST = "blacklist"
    CONDITIONAL = "conditional"


class FlagStatus(Enum):
    """Feature flag status."""
    DISABLED = "disabled"
    ENABLED = "enabled"
    ROLLOUT = "rollout"


@dataclass
class FeatureFlag:
    """Feature flag definition."""
    flag_id: str
    flag_name: str
    flag_type: FlagType
    status: FlagStatus
    default_value: Any = False
    rollout_percentage: float = 0.0
    whitelist: Set[str] = field(default_factory=set)
    blacklist: Set[str] = field(default_factory=set)
    condition: Callable[[Dict[str, Any]], bool] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    
    def is_enabled(self, context: Dict[str, Any] = None) -> bool:
        """Check if flag is enabled for given context."""
        if self.status == FlagStatus.DISABLED:
            return False
        
        if self.status == FlagStatus.ENABLED:
            return True
        
        if self.flag_type == FlagType.BOOLEAN:
            return bool(self.default_value)
        
        if self.flag_type == FlagType.PERCENTAGE:
            if not context:
                return False
            
            # Use user_id or context hash for consistent rollout
            user_id = context.get("user_id", "")
            if user_id:
                hash_value = int(hashlib.md5(user_id.encode()).hexdigest(), 16)
                return (hash_value % 100) < self.rollout_percentage
            else:
                return random.random() < self.rollout_percentage
        
        if self.flag_type == FlagType.WHITELIST:
            if not context:
                return False
            user_id = context.get("user_id", "")
            return user_id in self.whitelist
        
        if self.flag_type == FlagType.BLACKLIST:
            if not context:
                return True
            user_id = context.get("user_id", "")
            return user_id not in self.blacklist
        
        if self.flag_type == FlagType.CONDITIONAL:
            if self.condition and context:
                return self.condition(context)
            return bool(self.default_value)
        
        return bool(self.default_value)


@dataclass
class ABTestVariant:
    """A/B test variant."""
    variant_id: str
    variant_name: str
    weight: float
    config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ABTest:
    """A/B test definition."""
    test_id: str
    test_name: str
    flag_id: str
    variants: List[ABTestVariant]
    enabled: bool = True
    created_at: float = field(default_factory=time.time)
    
    def get_variant(self, context: Dict[str, Any] = None) -> Optional[ABTestVariant]:
        """Get variant for given context."""
        if not self.enabled:
            return None
        
        if not context:
            return None
        
        user_id = context.get("user_id", "")
        if not user_id:
            return None
        
        # Use hash for consistent variant assignment
        hash_value = int(hashlib.md5(user_id.encode()).hexdigest(), 16)
        normalized = hash_value / (2**32)  # Normalize to 0-1
        
        cumulative = 0.0
        for variant in self.variants:
            cumulative += variant.weight
            if normalized < cumulative:
                return variant
        
        return self.variants[-1] if self.variants else None


class FeatureFlagsService(Service):
    """Feature flags service as per Runtime Specification."""
    
    # Service dependencies
    DEPENDENCIES = []
    
    def __init__(self):
        super().__init__("feature_flags_service")
        self._flags: Dict[str, FeatureFlag] = {}
        self._ab_tests: Dict[str, ABTest] = {}
        self._flag_history: deque = deque(maxlen=1000)
        self._subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self._lock = threading.Lock()
        self._auto_reload_enabled = False
        self._storage_path: Optional[str] = None
        
    def init(self, event_bus: EventBus, config: Dict[str, Any]) -> bool:
        """Initialize the feature flags service."""
        try:
            self.event_bus = event_bus
            self.state = ServiceState.INITIALIZING
            
            # Load configuration
            flags_config = config.get("feature_flags", {})
            self._auto_reload_enabled = flags_config.get("auto_reload", False)
            self._storage_path = flags_config.get("storage_path")
            
            # Load initial flags
            initial_flags = flags_config.get("initial_flags", {})
            for flag_id, flag_data in initial_flags.items():
                self._create_flag_from_data(flag_id, flag_data)
            
            logger.info("Feature Flags Service initialized")
            return True
        except Exception as e:
            logger.error(f"Feature Flags Service initialization failed: {e}")
            self.state = ServiceState.ERROR
            return False
    
    def start(self) -> bool:
        """Start the feature flags service."""
        try:
            self.state = ServiceState.STARTING
            
            # Start auto-reload if enabled
            if self._auto_reload_enabled:
                self._start_auto_reload()
            
            self.state = ServiceState.RUNNING
            self.emit_event(str(EventType.SERVICE_START), {"service": self.name})
            logger.info("Feature Flags Service started")
            return True
        except Exception as e:
            logger.error(f"Feature Flags Service start failed: {e}")
            self.state = ServiceState.ERROR
            self.emit_event(str(EventType.SERVICE_CRASH), {"service": self.name, "error": str(e)})
            return False
    
    def stop(self) -> bool:
        """Stop the feature flags service."""
        try:
            self.state = ServiceState.STOPPING
            self._auto_reload_enabled = False
            self.state = ServiceState.STOPPED
            self.emit_event(str(EventType.SERVICE_STOP), {"service": self.name})
            logger.info("Feature Flags Service stopped")
            return True
        except Exception as e:
            logger.error(f"Feature Flags Service stop failed: {e}")
            self.state = ServiceState.ERROR
            return False
    
    def health(self) -> ServiceHealth:
        """Get feature flags service health."""
        return ServiceHealth(
            service=self.name,
            state=self.state,
            healthy=self.state == ServiceState.RUNNING,
            message=f"Feature Flags Service - {len(self._flags)} flags, {len(self._ab_tests)} A/B tests",
            details={
                "total_flags": len(self._flags),
                "enabled_flags": sum(1 for f in self._flags.values() if f.status == FlagStatus.ENABLED),
                "rollout_flags": sum(1 for f in self._flags.values() if f.status == FlagStatus.ROLLOUT),
                "total_ab_tests": len(self._ab_tests),
                "enabled_ab_tests": sum(1 for t in self._ab_tests.values() if t.enabled),
                "auto_reload": self._auto_reload_enabled
            },
            timestamp=time.time()
        )
    
    def create_flag(self, flag: FeatureFlag) -> bool:
        """Create a new feature flag."""
        with self._lock:
            if flag.flag_id in self._flags:
                logger.error(f"Flag {flag.flag_id} already exists")
                return False
            
            self._flags[flag.flag_id] = flag
            self._flag_history.append(("create", flag.flag_id, time.time()))
            
            logger.info(f"Created feature flag: {flag.flag_name}")
            return True
    
    def update_flag(self, flag_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing feature flag."""
        with self._lock:
            if flag_id not in self._flags:
                logger.error(f"Flag {flag_id} not found")
                return False
            
            flag = self._flags[flag_id]
            
            # Apply updates
            for key, value in updates.items():
                if hasattr(flag, key):
                    setattr(flag, key, value)
            
            flag.updated_at = time.time()
            self._flag_history.append(("update", flag_id, time.time()))
            
            # Notify subscribers
            self._notify_subscribers(flag_id)
            
            logger.info(f"Updated feature flag: {flag_id}")
            return True
    
    def delete_flag(self, flag_id: str) -> bool:
        """Delete a feature flag."""
        with self._lock:
            if flag_id not in self._flags:
                logger.error(f"Flag {flag_id} not found")
                return False
            
            del self._flags[flag_id]
            self._flag_history.append(("delete", flag_id, time.time()))
            
            logger.info(f"Deleted feature flag: {flag_id}")
            return True
    
    def is_enabled(self, flag_id: str, context: Dict[str, Any] = None) -> bool:
        """Check if a feature flag is enabled."""
        with self._lock:
            flag = self._flags.get(flag_id)
            if not flag:
                return False
            
            return flag.is_enabled(context)
    
    def get_flag(self, flag_id: str) -> Optional[FeatureFlag]:
        """Get a feature flag."""
        with self._lock:
            return self._flags.get(flag_id)
    
    def get_all_flags(self) -> Dict[str, FeatureFlag]:
        """Get all feature flags."""
        with self._lock:
            return dict(self._flags)
    
    def create_ab_test(self, test: ABTest) -> bool:
        """Create a new A/B test."""
        with self._lock:
            if test.test_id in self._ab_tests:
                logger.error(f"A/B test {test.test_id} already exists")
                return False
            
            # Validate flag exists
            if test.flag_id not in self._flags:
                logger.error(f"Flag {test.flag_id} not found for A/B test")
                return False
            
            # Validate weights sum to 1.0
            total_weight = sum(v.weight for v in test.variants)
            if abs(total_weight - 1.0) > 0.01:
                logger.error(f"Variant weights must sum to 1.0, got {total_weight}")
                return False
            
            self._ab_tests[test.test_id] = test
            logger.info(f"Created A/B test: {test.test_name}")
            return True
    
    def get_variant(self, test_id: str, context: Dict[str, Any] = None) -> Optional[ABTestVariant]:
        """Get variant for A/B test."""
        with self._lock:
            test = self._ab_tests.get(test_id)
            if not test:
                return None
            
            return test.get_variant(context)
    
    def enable_flag(self, flag_id: str) -> bool:
        """Enable a feature flag."""
        return self.update_flag(flag_id, {"status": FlagStatus.ENABLED})
    
    def disable_flag(self, flag_id: str) -> bool:
        """Disable a feature flag."""
        return self.update_flag(flag_id, {"status": FlagStatus.DISABLED})
    
    def set_rollout(self, flag_id: str, percentage: float) -> bool:
        """Set rollout percentage for a flag."""
        return self.update_flag(flag_id, {
            "status": FlagStatus.ROLLOUT,
            "rollout_percentage": percentage
        })
    
    def add_to_whitelist(self, flag_id: str, user_id: str) -> bool:
        """Add user to whitelist."""
        with self._lock:
            flag = self._flags.get(flag_id)
            if not flag:
                return False
            
            flag.whitelist.add(user_id)
            flag.updated_at = time.time()
            return True
    
    def remove_from_whitelist(self, flag_id: str, user_id: str) -> bool:
        """Remove user from whitelist."""
        with self._lock:
            flag = self._flags.get(flag_id)
            if not flag:
                return False
            
            flag.whitelist.discard(user_id)
            flag.updated_at = time.time()
            return True
    
    def add_to_blacklist(self, flag_id: str, user_id: str) -> bool:
        """Add user to blacklist."""
        with self._lock:
            flag = self._flags.get(flag_id)
            if not flag:
                return False
            
            flag.blacklist.add(user_id)
            flag.updated_at = time.time()
            return True
    
    def remove_from_blacklist(self, flag_id: str, user_id: str) -> bool:
        """Remove user from blacklist."""
        with self._lock:
            flag = self._flags.get(flag_id)
            if not flag:
                return False
            
            flag.blacklist.discard(user_id)
            flag.updated_at = time.time()
            return True
    
    def subscribe(self, flag_id: str, callback: Callable[[str], None]) -> None:
        """Subscribe to flag changes."""
        with self._lock:
            self._subscribers[flag_id].append(callback)
    
    def unsubscribe(self, flag_id: str, callback: Callable[[str], None]) -> None:
        """Unsubscribe from flag changes."""
        with self._lock:
            if flag_id in self._subscribers and callback in self._subscribers[flag_id]:
                self._subscribers[flag_id].remove(callback)
    
    def get_flag_history(self, limit: int = 100) -> List[Tuple[str, str, float]]:
        """Get flag change history."""
        with self._lock:
            return list(self._flag_history)[-limit:]
    
    def export_flags(self) -> Dict[str, Any]:
        """Export all flags to dictionary."""
        with self._lock:
            return {
                flag_id: {
                    "flag_name": flag.flag_name,
                    "flag_type": flag.flag_type.value,
                    "status": flag.status.value,
                    "default_value": flag.default_value,
                    "rollout_percentage": flag.rollout_percentage,
                    "whitelist": list(flag.whitelist),
                    "blacklist": list(flag.blacklist),
                    "metadata": flag.metadata,
                    "created_at": flag.created_at,
                    "updated_at": flag.updated_at
                }
                for flag_id, flag in self._flags.items()
            }
    
    def import_flags(self, flags_data: Dict[str, Any]) -> bool:
        """Import flags from dictionary."""
        with self._lock:
            for flag_id, flag_data in flags_data.items():
                self._create_flag_from_data(flag_id, flag_data)
            
            logger.info("Flags imported successfully")
            return True
    
    def save_to_storage(self) -> bool:
        """Save flags to storage."""
        if not self._storage_path:
            logger.error("No storage path configured")
            return False
        
        try:
            import json
            with open(self._storage_path, 'w') as f:
                json.dump(self.export_flags(), f, indent=2)
            
            logger.info(f"Flags saved to {self._storage_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save flags: {e}")
            return False
    
    def reload_from_storage(self) -> bool:
        """Reload flags from storage."""
        if not self._storage_path:
            logger.error("No storage path configured")
            return False
        
        try:
            import json
            with open(self._storage_path, 'r') as f:
                flags_data = json.load(f)
            
            self.import_flags(flags_data)
            logger.info(f"Flags reloaded from {self._storage_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to reload flags: {e}")
            return False
    
    def _create_flag_from_data(self, flag_id: str, flag_data: Dict[str, Any]) -> None:
        """Create flag from data dictionary."""
        flag = FeatureFlag(
            flag_id=flag_id,
            flag_name=flag_data.get("flag_name", flag_id),
            flag_type=FlagType(flag_data.get("flag_type", "boolean")),
            status=FlagStatus(flag_data.get("status", "disabled")),
            default_value=flag_data.get("default_value", False),
            rollout_percentage=flag_data.get("rollout_percentage", 0.0),
            whitelist=set(flag_data.get("whitelist", [])),
            blacklist=set(flag_data.get("blacklist", [])),
            metadata=flag_data.get("metadata", {}),
            created_at=flag_data.get("created_at", time.time()),
            updated_at=flag_data.get("updated_at", time.time())
        )
        
        self._flags[flag_id] = flag
    
    def _notify_subscribers(self, flag_id: str) -> None:
        """Notify subscribers of flag changes."""
        if flag_id in self._subscribers:
            for callback in self._subscribers[flag_id]:
                try:
                    callback(flag_id)
                except Exception as e:
                    logger.error(f"Subscriber callback error: {e}")
    
    def _start_auto_reload(self) -> None:
        """Start auto-reload background task."""
        def auto_reload():
            while self._auto_reload_enabled and self.state == ServiceState.RUNNING:
                try:
                    self.reload_from_storage()
                    time.sleep(60)  # Check every minute
                except Exception as e:
                    logger.error(f"Auto-reload error: {e}")
                    time.sleep(30)
        
        thread = threading.Thread(target=auto_reload, daemon=True)
        thread.start()
        logger.info("Auto-reload started")


# Global instance
_feature_flags_service: Optional[FeatureFlagsService] = None


def get_feature_flags_service() -> FeatureFlagsService:
    """Get global feature flags service instance."""
    global _feature_flags_service
    if _feature_flags_service is None:
        _feature_flags_service = FeatureFlagsService()
    return _feature_flags_service