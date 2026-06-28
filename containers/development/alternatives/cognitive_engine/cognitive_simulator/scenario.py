"""Scenario - defines simulation scenarios."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ScenarioType(Enum):
    """Types of scenarios to simulate."""

    FED_SURPRISE = "fed_surprise"
    EXCHANGE_FAILURE = "exchange_failure"
    LIQUIDITY_COLLAPSE = "liquidity_collapse"
    VOLATILITY_EXPLOSION = "volatility_explosion"
    REGIME_CHANGE = "regime_change"
    CATALYST_EVENT = "catalyst_event"


@dataclass
class Scenario:
    """A scenario for cognitive simulation."""

    scenario_id: str = field(default_factory=lambda: f"scenario_{time.time_ns()}")
    scenario_type: ScenarioType = ScenarioType.FED_SURPRISE
    description: str = ""
    impact_factors: dict[str, float] = field(default_factory=dict)
    affected_assets: tuple[str, ...] = ()
    duration_seconds: int = 3600
    metadata: dict[str, Any] = field(default_factory=dict)

    def with_impact(self, factor: str, magnitude: float) -> Scenario:
        """Add an impact factor."""
        self.impact_factors[factor] = magnitude
        return self

    def with_assets(self, *assets: str) -> Scenario:
        """Add affected assets."""
        self.affected_assets = (*self.affected_assets, *assets)
        return self
