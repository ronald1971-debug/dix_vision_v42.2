"""Simulation Result - outcome of cognitive simulation."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class RiskLevel(Enum):
    """Risk level from simulation."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    EXTREME = "extreme"


@dataclass
class SimulationResult:
    """Result from a cognitive simulation."""

    simulation_id: str = field(default_factory=lambda: f"sim_{time.time_ns()}")
    scenario_id: str = ""
    risk_level: RiskLevel = RiskLevel.LOW
    estimated_pnl_impact: float = 0.0
    strategy_exposure: dict[str, float] = field(default_factory=dict)
    recommendations: tuple[str, ...] = ()
    confidence: float = 0.0
    run_at: int = field(default_factory=lambda: time.time_ns())
    metadata: dict[str, Any] = field(default_factory=dict)