"""
execution_engine.adapters.simple_router
Simple priority-based adapter router.

Migrated from execution/adapter_router.py

Router that resolves a trade intent to a concrete exchange adapter.
This is the simple priority-based router used by legacy code paths.
For domain-based routing, see execution_engine/adapters/router.py

NOTE: This router uses the legacy BaseAdapter interface from execution/adapters/base
for backward compatibility. New code should use execution_engine.adapters.router
which uses BrokerAdapter with domain isolation.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass

# Import legacy BaseAdapter for backward compatibility
from execution.adapters.base import BaseAdapter


@dataclass
class AdapterEntry:
    name: str
    adapter: BaseAdapter
    priority: int = 0


class SimpleAdapterRouter:
    """Simple priority-based adapter router (legacy compatibility).

    This router provides compatibility with the legacy execution/
    adapter_router by using the BaseAdapter interface.

    For new code, prefer the domain-based execution_engine.adapters.router
    which provides hard domain isolation (NORMAL/COPY_TRADING/MEMECOIN).
    """

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._entries: list[AdapterEntry] = []

    def register(self, name: str, adapter: BaseAdapter, priority: int = 0) -> None:
        """Register an adapter with optional priority (higher = first)."""
        with self._lock:
            self._entries.append(AdapterEntry(name, adapter, priority))
            self._entries.sort(key=lambda e: -e.priority)

    def unregister(self, name: str) -> None:
        """Remove an adapter by name."""
        with self._lock:
            self._entries = [e for e in self._entries if e.name != name]

    def route(self, asset: str) -> BaseAdapter | None:
        """Route to the first adapter that supports the asset."""
        with self._lock:
            entries = list(self._entries)
        for e in entries:
            supports = getattr(e.adapter, "supports", None)
            if supports is None or supports(asset):
                return e.adapter
        return None

    def registered(self) -> list[str]:
        """List of registered adapter names."""
        with self._lock:
            return [e.name for e in self._entries]

    def get_by_name(self, name: str) -> BaseAdapter | None:
        """Get adapter by exact name."""
        with self._lock:
            for e in self._entries:
                if e.name == name:
                    return e.adapter
        return None

    def entries(self) -> list[AdapterEntry]:
        """Get all registered entries."""
        with self._lock:
            return list(self._entries)


_router: SimpleAdapterRouter | None = None
_lock = threading.Lock()


def get_simple_adapter_router() -> SimpleAdapterRouter:
    """Get singleton instance of simple adapter router."""
    global _router
    if _router is None:
        with _lock:
            if _router is None:
                _router = SimpleAdapterRouter()
    return _router


# Legacy alias for backward compatibility
get_adapter_router = get_simple_adapter_router


__all__ = [
    "AdapterEntry",
    "SimpleAdapterRouter",
    "get_simple_adapter_router",
    "get_adapter_router",  # Legacy alias
]