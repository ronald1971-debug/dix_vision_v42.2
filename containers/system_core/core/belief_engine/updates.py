"""Belief updates — INV-DIX-02 enforcement.

Every engine publishes through the BeliefState contract.
No hidden realities.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class BeliefUpdate:
    """A belief update event from an engine."""

    ts_ns: int
    engine: str
    domain: str
    field: str
    old_value: str
    new_value: str

    def __post_init__(self) -> None:
        if self.domain not in (
            "market_intelligence",
            "trader_intelligence",
            "strategy_intelligence",
            "portfolio_intelligence",
            "allocation_intelligence",
            "position_intelligence",
            "execution_feedback_intelligence",
            "repository_intelligence",
            "architecture_intelligence",
            "runtime_intelligence",
            "infrastructure_intelligence",
        ):
            raise ValueError(f"Unknown domain: {self.domain}")


def publish_belief(
    engine: str,
    domain: str,
    field: str,
    value: str,
    ts_ns: int,
) -> BeliefUpdate:
    """Publish a belief update.

    The single entry point for belief modifications.
    All engines must use this to update beliefs.
    """
    return BeliefUpdate(
        ts_ns=ts_ns,
        engine=engine,
        domain=domain,
        field=field,
        old_value="",
        new_value=value,
    )


__all__ = [
    "BeliefUpdate",
    "publish_belief",
]
