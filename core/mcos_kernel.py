"""MCOS Core Kernel – BeliefState and system-wide primitives.

The BeliefState is the single source of truth for the system's perception
of market regimes, consensus, and confidence.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any


class MarketRegime(Enum):
    UNKNOWN = auto()
    TRENDING_UP = auto()
    TRENDING_DOWN = auto()
    RANGING = auto()
    VOLATILE = auto()
    MEAN_REVERTING = auto()
    BREAKOUT = auto()
    CRISIS = auto()


class ConfidenceLevel(Enum):
    NONE = 0
    LOW = 1
    MODERATE = 2
    HIGH = 3
    VERY_HIGH = 4


class SystemPhase(Enum):
    INITIALIZING = auto()
    OBSERVING = auto()
    REASONING = auto()
    EXECUTING = auto()
    LEARNING = auto()
    EVOLVING = auto()
    HALTED = auto()


@dataclass(frozen=True)
class MarketView:
    regime: MarketRegime = MarketRegime.UNKNOWN
    confidence: ConfidenceLevel = ConfidenceLevel.NONE
    volatility_estimate: float = 0.0
    trend_strength: float = 0.0
    timestamp: float = field(default_factory=time.time)


@dataclass(frozen=True)
class ConsensusState:
    """Aggregated consensus across all intelligence sources."""
    direction_bias: float = 0.0  # -1.0 (bearish) to 1.0 (bullish)
    strength: float = 0.0
    agreement_ratio: float = 0.0
    source_count: int = 0
    timestamp: float = field(default_factory=time.time)


@dataclass
class BeliefState:
    """Single source of truth for MCOS perception.

    Immutable snapshots are taken via `snapshot()`; mutations go through
    controlled update methods that return a new BeliefState.
    """

    state_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    phase: SystemPhase = SystemPhase.INITIALIZING
    market_view: MarketView = field(default_factory=MarketView)
    consensus: ConsensusState = field(default_factory=ConsensusState)
    active_hypotheses: list[str] = field(default_factory=list)
    risk_budget_remaining: float = 1.0
    kill_switch_active: bool = False
    last_updated: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)

    def snapshot(self) -> BeliefState:
        """Return a frozen copy of the current state."""
        return BeliefState(
            state_id=uuid.uuid4().hex[:12],
            phase=self.phase,
            market_view=self.market_view,
            consensus=self.consensus,
            active_hypotheses=list(self.active_hypotheses),
            risk_budget_remaining=self.risk_budget_remaining,
            kill_switch_active=self.kill_switch_active,
            last_updated=time.time(),
            metadata=dict(self.metadata),
        )

    def with_market_view(self, view: MarketView) -> BeliefState:
        snap = self.snapshot()
        snap.market_view = view
        return snap

    def with_consensus(self, consensus: ConsensusState) -> BeliefState:
        snap = self.snapshot()
        snap.consensus = consensus
        return snap

    def with_phase(self, phase: SystemPhase) -> BeliefState:
        snap = self.snapshot()
        snap.phase = phase
        return snap

    def activate_kill_switch(self) -> BeliefState:
        snap = self.snapshot()
        snap.kill_switch_active = True
        snap.phase = SystemPhase.HALTED
        return snap

    def is_halted(self) -> bool:
        return self.kill_switch_active or self.phase == SystemPhase.HALTED


@dataclass(frozen=True)
class SystemEvent:
    """Base event type for all MCOS events."""
    event_id: str = field(default_factory=lambda: uuid.uuid4().hex)
    event_type: str = ""
    source: str = ""
    timestamp: float = field(default_factory=time.time)
    payload: dict[str, Any] = field(default_factory=dict)
    belief_state_id: str = ""
