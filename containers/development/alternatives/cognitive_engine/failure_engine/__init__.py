"""Failure Intelligence — failures studied as assets.

(Item 35 — cognitive operating system roadmap)
"""

from cognitive_engine.failure_engine.failure_engine import (
    FailureEngine,
    FailureRecord,
    FailureTracker,
    get_failure_engine,
)

__all__ = [
    "FailureEngine",
    "FailureRecord",
    "FailureTracker",
    "get_failure_engine",
]
