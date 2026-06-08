"""Hypothesis Engine - supports the observe→hypothesis→test→validate→learn cycle.

Example:
    Hypothesis:
        Crypto market leadership has shifted.

    Evidence:
        ...

    Status:
        Testing → Valid → Invalid → Learned From
"""

from cognitive_engine.hypothesis_engine.hypothesis import (
    Hypothesis,
    HypothesisResult,
    HypothesisStatus,
)
from cognitive_engine.hypothesis_engine.hypothesis_tracker import HypothesisTracker
from cognitive_engine.hypothesis_engine.test_runner import TestRunner

__all__ = [
    "Hypothesis",
    "HypothesisResult",
    "HypothesisStatus",
    "HypothesisTracker",
    "TestRunner",
]