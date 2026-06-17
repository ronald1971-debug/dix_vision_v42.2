"""Capability - defines system capabilities."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class CapabilityStatus(Enum):
    """Status of a capability."""

    ACTIVE = "active"
    DISABLED = "disabled"
    LIMITED = "limited"
    DEGRADED = "degraded"


@dataclass(frozen=True, slots=True)
class Capability:
    """A system capability."""

    name: str
    description: str
    status: CapabilityStatus = CapabilityStatus.ACTIVE
    operational_limits: dict[str, Any] = field(default_factory=dict)
    performance_score: float = 1.0
    last_tested: int = 0

    def is_operational(self) -> bool:
        """Check if capability is operational."""
        return self.status in (CapabilityStatus.ACTIVE, CapabilityStatus.LIMITED)