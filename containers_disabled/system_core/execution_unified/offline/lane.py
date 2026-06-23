"""
execution_engine.offline.lane
Buffered offline lane for SystemEvent coordination.

Migrated from execution/offline_lane.py

The offline lane buffers SYSTEM events for offline engine consumption.
Drainable in batch — offline engines pull when ready rather than being
pushed. Only SYSTEM events are accepted.

B1:       No imports from engine tiers.
B27/B28:  Never constructs typed events.
INV-15:   Drain order is FIFO; deterministic for a given input sequence.
"""

from __future__ import annotations

import threading
from collections import deque
from collections.abc import Callable


# Lazy import to avoid circular dependency when loaded through execution_unified/__init__.py
def _get_event_types():
    from core.contracts.events import EventKind, SystemEvent

    return EventKind, SystemEvent


__all__ = ["OfflineLane", "OfflineLaneHandler", "get_offline_lane"]

OfflineLaneHandler = Callable[[object], None]  # Changed to generic object to avoid import


class OfflineLane:
    """FIFO buffer for SystemEvent (offline coordination lane).

    Offline engines call ``drain()`` at their own cadence. Push-based
    handlers may also be registered for immediate delivery.
    """

    def __init__(self, maxsize: int = 100_000) -> None:
        self._buffer: deque = deque(maxlen=maxsize)
        self._handlers: list = []
        self._lock = threading.Lock()
        self._emitted = 0
        self._dropped = 0

    def subscribe(self, handler: Callable[[object], None]) -> None:
        with self._lock:
            self._handlers.append(handler)

    def emit(self, event: object) -> bool:
        # Lazy import to avoid circular dependency
        EventKind, _ = _get_event_types()
        if getattr(event, "kind", None) != EventKind.SYSTEM:
            return False
        with self._lock:
            if len(self._buffer) >= (self._buffer.maxlen or 100_000):
                self._dropped += 1
                return False
            self._buffer.append(event)
            self._emitted += 1
            handlers = list(self._handlers)
        for h in handlers:
            try:
                h(event)
            except Exception:  # noqa: BLE001
                pass
        return True

    def drain(self) -> tuple:
        """Remove and return all buffered events (FIFO order)."""
        with self._lock:
            batch = tuple(self._buffer)
            self._buffer.clear()
        return batch

    def peek(self) -> tuple:
        """Return buffered events without removing them."""
        with self._lock:
            return tuple(self._buffer)

    @property
    def emitted(self) -> int:
        return self._emitted

    @property
    def dropped(self) -> int:
        return self._dropped

    @property
    def pending(self) -> int:
        with self._lock:
            return len(self._buffer)


_lane: OfflineLane | None = None
_lane_lock = threading.Lock()


def get_offline_lane() -> OfflineLane:
    global _lane
    if _lane is None:
        with _lane_lock:
            if _lane is None:
                _lane = OfflineLane()
    return _lane
