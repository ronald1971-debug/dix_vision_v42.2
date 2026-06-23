"""Attention Priority - defines priority levels for cognitive allocation."""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum


class AttentionPriority(IntEnum):
    """Priority levels for attention allocation."""

    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass(frozen=True, slots=True)
class AttentionWeight:
    """Weights for attention scoring dimensions."""

    opportunity: float = 1.0
    risk: float = 1.0
    novelty: float = 1.0
    uncertainty: float = 1.0

    def normalize(self) -> AttentionWeight:
        """Return normalized weights summing to 1.0."""
        total = sum([self.opportunity, self.risk, self.novelty, self.uncertainty])
        if total == 0:
            return AttentionWeight(0.25, 0.25, 0.25, 0.25)
        return AttentionWeight(
            self.opportunity / total,
            self.risk / total,
            self.novelty / total,
            self.uncertainty / total,
        )
