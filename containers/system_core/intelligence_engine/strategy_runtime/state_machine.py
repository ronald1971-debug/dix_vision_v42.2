"""Stub strategy runtime."""

from typing import Any


class StrategyState:
    """Stub strategy state."""

    PROPOSED = "proposed"
    TESTING = "testing"
    CANARY = "canary"
    LIVE = "live"
    PAUSED = "paused"
    STOPPED = "stopped"
    RETIRED = "retired"
    FAILED = "failed"

    def __init__(self, **kwargs: Any):
        pass


class StrategyRecord:
    """Stub strategy record."""

    def __init__(self, **kwargs: Any):
        pass


class StrategyStateMachine:
    """Stub strategy state machine."""

    def __init__(self, **kwargs: Any):
        pass
