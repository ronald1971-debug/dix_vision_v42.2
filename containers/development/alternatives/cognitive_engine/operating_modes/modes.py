"""Operating Modes - defines cognitive operating modes."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class OperatingMode(Enum):
    """Cognitive operating modes."""

    FROZEN = "frozen"  # No active trading
    SHADOW = "shadow"  # Observation only
    CANARY = "canary"  # Limited live testing
    LIVE = "live"  # Full trading
    RESEARCH = "research"  # Exploring new strategies
    LEARNING = "learning"  # Model updates active
    SIMULATION = "simulation"  # Running scenarios
    DISCOVERY = "discovery"  # Pattern finding
    VALIDATION = "validation"  # Testing hypotheses


@dataclass
class ModeTransition:
    """A mode transition event."""

    transition_id: str = field(default_factory=lambda: f"transition_{time.time_ns()}")
    from_mode: OperatingMode = OperatingMode.FROZEN
    to_mode: OperatingMode = OperatingMode.SHADOW
    reason: str = ""
    transitioned_at: int = field(default_factory=lambda: time.time_ns())
    approved_by: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)