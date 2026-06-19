"""Maturity - tracks cognitive maturity levels."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum
from typing import Any


class MaturityLevel(IntEnum):
    """Levels of cognitive maturity (1-10 scale)."""

    NOVICE = 1
    BEGINNER = 2
    DEVELOPING = 3
    COMPETENT = 4
    PROFICIENT = 5
    SKILLED = 6
    EXPERT = 7
    MASTER = 8
    GRANDMASTER = 9
    TRANSCENDENT = 10


@dataclass
class MaturityAssessment:
    """Maturity assessment for a cognitive domain."""

    domain: str
    current_level: MaturityLevel = MaturityLevel.NOVICE
    max_level: MaturityLevel = MaturityLevel.TRANSCENDENT
    progress_score: float = 0.0
    evidence: tuple[str, ...] = ()
    last_evaluated: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def level(self) -> int:
        """Get current level as int."""
        return self.current_level.value

    @property
    def max_level_value(self) -> int:
        """Get max level as int."""
        return self.max_level.value

    def progress_percentage(self) -> float:
        """Get progress toward next level."""
        return self.progress_score