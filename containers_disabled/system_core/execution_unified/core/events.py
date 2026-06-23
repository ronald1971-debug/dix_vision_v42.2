"""
execution_unified.core.events
DIX VISION v42.2 — Unified Execution Event Types

Simplified event types for unified execution system.
This provides the minimal interfaces needed by migrated adapters
while maintaining compatibility with the core system events.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


class Side(StrEnum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


class ExecutionStatus(StrEnum):
    """Execution event status types."""

    PENDING = "PENDING"
    SUBMITTED = "SUBMITTED"
    FILLED = "FILLED"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"
    FAILED = "FAILED"
    EXPIRED = "EXPIRED"


@dataclass(frozen=True)
class SignalEvent:
    """Base signal event for unified execution system."""

    symbol: str
    side: Side
    quantity: float
    price: float = 0.0
    timestamp_ns: int = 0
    metadata: dict = field(default_factory=dict)


@dataclass(frozen=True)
class ExecutionEvent:
    """Base execution event for unified execution system."""

    status: ExecutionStatus
    symbol: str
    side: Side
    quantity: float
    price: float = 0.0
    order_id: str = ""
    timestamp_ns: int = 0
    metadata: dict = field(default_factory=dict)
    error: str = ""


# Maintain backward compatibility with core system imports
# This allows adapters that import from core.contracts.events to work
class EventKind(StrEnum):
    """Discriminator for the four canonical event kinds."""

    SIGNAL = "SIGNAL_EVENT"
    EXECUTION = "EXECUTION_EVENT"
    SYSTEM = "SYSTEM_EVENT"
    HAZARD = "HAZARD_EVENT"


__all__ = [
    "Side",
    "ExecutionStatus",
    "SignalEvent",
    "ExecutionEvent",
    "EventKind",
]
