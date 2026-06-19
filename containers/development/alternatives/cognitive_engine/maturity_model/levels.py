"""Maturity Levels - defines maturity domains and levels."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum
from typing import Any


class MaturityLevel(IntEnum):
    """Explicit maturity levels (1-10 scale)."""

    NOVICE = 1
    BEGINNER = 2
    DEVELOPING = 3
    COMPETENT = 4
    PROFICIENT = 5
    ADVANCED = 6
    EXPERT = 7
    MASTER = 8
    GRANDMASTER = 9
    TRANSCENDENT = 10


class MaturityDomain(IntEnum):
    """Domains of cognitive maturity."""

    MARKET_UNDERSTANDING = 1
    TRADER_UNDERSTANDING = 2
    STRATEGY_UNDERSTANDING = 3
    EXECUTION_UNDERSTANDING = 4
    SYSTEM_UNDERSTANDING = 5
    SELF_UNDERSTANDING = 6


@dataclass
class DomainMaturity:
    """Maturity assessment for a single domain."""

    domain: MaturityDomain
    level: MaturityLevel = MaturityLevel.NOVICE
    progress: float = 0.0
    last_assessed: int = 0
    evidence: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    def level_value(self) -> int:
        """Get level as integer."""
        return self.level.value

    def describe(self) -> str:
        """Describe current maturity."""
        return f"{self.domain.name}: Level {self.level.value} ({self.level.name})"