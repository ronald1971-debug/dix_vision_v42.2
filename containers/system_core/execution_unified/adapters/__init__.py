"""Adapters.

Venue and protocol adapters for execution connectivity.
"""

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class AdapterState(Enum):
    """Adapter state enumeration"""

    INITIALIZING = "initializing"
    READY = "ready"
    DISCONNECTED = "disconnected"
    ERROR = "error"


@dataclass
class Adapter:
    """Base adapter class"""

    adapter_id: str
    adapter_type: str
    enabled: bool = True
    config: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

    # Additional fields for compatibility with execution_routes
    name: str = ""
    venue: str = ""
    state: AdapterState = field(default_factory=lambda: AdapterState.DISCONNECTED)
    detail: str = ""
    last_heartbeat_ns: int = 0

    def is_enabled(self) -> bool:
        """Check if adapter is enabled"""
        return self.enabled

    def enable(self) -> None:
        """Enable the adapter"""
        self.enabled = True
        self.timestamp = time.time()

    def disable(self) -> None:
        """Disable the adapter"""
        self.enabled = False
        self.timestamp = time.time()


@dataclass
class AdapterRegistry:
    """Registry for adapters"""

    def __init__(self):
        self._adapters: Dict[str, Adapter] = {}

    def register_adapter(self, adapter: Adapter) -> bool:
        """Register an adapter"""
        self._adapters[adapter.adapter_id] = adapter
        return True

    def get_adapter(self, adapter_id: str) -> Optional[Adapter]:
        """Get a specific adapter"""
        return self._adapters.get(adapter_id)

    def get_all_adapters(self) -> List[Adapter]:
        """Get all adapters"""
        return list(self._adapters.values())

    def get_enabled_adapters(self) -> List[Adapter]:
        """Get all enabled adapters"""
        return [a for a in self._adapters.values() if a.is_enabled()]

    def snapshot(self) -> List[Adapter]:
        """Get snapshot of all adapters (compatibility with execution_routes)"""
        return self.get_all_adapters()


# Global default registry
_default_registry: Optional[AdapterRegistry] = None


def get_default_registry() -> AdapterRegistry:
    """Get the default adapter registry"""
    global _default_registry
    if _default_registry is None:
        _default_registry = AdapterRegistry()
    return _default_registry


def default_registry() -> AdapterRegistry:
    """Get the default adapter registry (alias)"""
    return get_default_registry()


__all__ = ["Adapter", "AdapterRegistry", "get_default_registry", "default_registry"]
