"""Failing Engine — tracks and classifies failures, maintains statistics."""

from cognitive_engine.failing_engine.failure_tracker import (
    FailureTracker,
    get_failure_tracker,
)

__all__ = [
    "FailureTracker",
    "get_failure_tracker",
]
