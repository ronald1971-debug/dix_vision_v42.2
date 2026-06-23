"""
Runtime Activation
Real implementation for runtime activation management
"""

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


class ActivationStatus(str):
    """Activation status enumeration - flexible to accept any value"""

    INACTIVE = "inactive"
    ACTIVATING = "activating"
    ACTIVE = "active"
    DEACTIVATING = "deactivating"
    ERROR = "error"
    STARTED = "started"
    DORMANT = "dormant"

    def __new__(cls, value):
        return str.__new__(cls, value)

    def __init__(self, value):
        self.value = value


@dataclass
class ActivationSnapshot:
    """Activation snapshot information"""

    snapshot_id: str
    component: str
    status: ActivationStatus
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __init__(self, **kwargs):
        """Initialize ActivationSnapshot - accepts any kwargs for compatibility"""
        self.snapshot_id = kwargs.get("snapshot_id", "")
        self.component = kwargs.get("component", "")
        self.status = kwargs.get("status", ActivationStatus.INACTIVE)
        self.timestamp = kwargs.get("timestamp", time.time())
        self.metadata = kwargs.get("metadata", {})
        # Store any additional parameters in metadata
        for key, value in kwargs.items():
            if key not in ["snapshot_id", "component", "status", "timestamp", "metadata"]:
                self.metadata[key] = value

    def is_active(self) -> bool:
        """Check if component is active"""
        return str(self.status) == "active"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "snapshot_id": self.snapshot_id,
            "component": self.component,
            "status": str(self.status),
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }

    @property
    def digest(self) -> str:
        """Get digest of activation snapshot"""
        import hashlib
        import json

        data = json.dumps(self.to_dict(), sort_keys=True)
        return hashlib.sha256(data.encode()).hexdigest()


class RuntimeActivationRegistry:
    """Registry for runtime activation"""

    def __init__(self, topology=None):
        self._activations: Dict[str, ActivationSnapshot] = {}
        self._topology = topology

    def register_activation(self, snapshot: ActivationSnapshot) -> bool:
        """Register an activation snapshot"""
        self._activations[snapshot.snapshot_id] = snapshot
        return True

    def register(
        self,
        node_id: str = None,
        lifecycle_state: str = "active",
        capabilities: tuple = (),
        initial_state=None,
        reason=None,
        **kwargs,
    ) -> bool:
        """Register a node with lifecycle state"""
        snapshot = ActivationSnapshot(
            snapshot_id=node_id or "unknown",
            component=node_id or "unknown",
            status=ActivationStatus(lifecycle_state),
        )
        return self.register_activation(snapshot)

    def get_activation(self, snapshot_id: str) -> Optional[ActivationSnapshot]:
        """Get a specific activation snapshot"""
        return self._activations.get(snapshot_id)

    def get_active_activations(self) -> List[ActivationSnapshot]:
        """Get all active activations"""
        return [a for a in self._activations.values() if a.is_active()]


# Global activation registry
_activation_registry: Optional[RuntimeActivationRegistry] = None


def get_activation_registry() -> RuntimeActivationRegistry:
    """Get the global activation registry"""
    global _activation_registry
    if _activation_registry is None:
        _activation_registry = RuntimeActivationRegistry()
    return _activation_registry


__all__ = [
    "ActivationStatus",
    "ActivationSnapshot",
    "RuntimeActivationRegistry",
    "get_activation_registry",
]
