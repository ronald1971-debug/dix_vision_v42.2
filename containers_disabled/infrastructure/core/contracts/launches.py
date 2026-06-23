"""
Core Contracts Launches
Real implementation for launch event contracts
"""

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class LaunchStatus(Enum):
    """Launch status enumeration"""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class LaunchKind(Enum):
    """Launch kind enumeration"""

    COLD = "cold"
    WARM = "warm"
    HOT = "hot"
    RESTART = "restart"
    UPGRADE = "upgrade"
    MIGRATION = "migration"


@dataclass
class LaunchEvent:
    """Launch event information"""

    event_id: str
    launch_kind: LaunchKind
    status: LaunchStatus
    target: str
    requester: str
    timestamp: float = field(default_factory=time.time)
    parameters: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def is_completed(self) -> bool:
        """Check if launch is completed"""
        return self.status == LaunchStatus.COMPLETED

    def is_failed(self) -> bool:
        """Check if launch is failed"""
        return self.status == LaunchStatus.FAILED

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "event_id": self.event_id,
            "launch_kind": self.launch_kind.value,
            "status": self.status.value,
            "target": self.target,
            "requester": self.requester,
            "timestamp": self.timestamp,
            "parameters": self.parameters,
            "metadata": self.metadata,
        }


@dataclass
class PoolSnapshot:
    """Pool snapshot information"""

    snapshot_id: str
    pool_id: str
    status: str
    timestamp: float = field(default_factory=time.time)
    metrics: Dict[str, float] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "snapshot_id": self.snapshot_id,
            "pool_id": self.pool_id,
            "status": self.status,
            "timestamp": self.timestamp,
            "metrics": self.metrics,
            "metadata": self.metadata,
        }


class LaunchRegistry:
    """Registry for launch events"""

    def __init__(self):
        self._events: Dict[str, LaunchEvent] = {}
        self._events_by_status: Dict[LaunchStatus, List[str]] = {
            status: [] for status in LaunchStatus
        }

    def register_event(self, event: LaunchEvent) -> bool:
        """Register a launch event"""
        self._events[event.event_id] = event
        self._events_by_status[event.status].append(event.event_id)
        return True

    def get_event(self, event_id: str) -> Optional[LaunchEvent]:
        """Get a specific launch event"""
        return self._events.get(event_id)

    def get_events_by_status(self, status: LaunchStatus) -> List[LaunchEvent]:
        """Get all events with a specific status"""
        event_ids = self._events_by_status.get(status, [])
        return [self._events[eid] for eid in event_ids if eid in self._events]


# Global launch registry
_launch_registry: Optional[LaunchRegistry] = None


def get_launch_registry() -> LaunchRegistry:
    """Get the global launch registry"""
    global _launch_registry
    if _launch_registry is None:
        _launch_registry = LaunchRegistry()
    return _launch_registry


def create_launch_event(
    event_id: str, launch_kind: LaunchKind, target: str, requester: str
) -> LaunchEvent:
    """Create a new launch event"""
    return LaunchEvent(
        event_id=event_id, launch_kind=launch_kind, target=target, requester=requester
    )


__all__ = [
    "LaunchStatus",
    "LaunchKind",
    "LaunchEvent",
    "PoolSnapshot",
    "LaunchRegistry",
    "get_launch_registry",
    "create_launch_event",
]
