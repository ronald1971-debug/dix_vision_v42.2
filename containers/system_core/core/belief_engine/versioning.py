"""Belief versioning — INV-DIX-02 enforcement.

Version belief state schema for compatibility.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class BeliefVersion:
    """Version identifier for belief state schema."""

    major: int
    minor: int
    patch: int

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"


CURRENT_BELIEF_VERSION = BeliefVersion(42, 2, 1)

__all__ = [
    "BeliefVersion",
    "CURRENT_BELIEF_VERSION",
]
