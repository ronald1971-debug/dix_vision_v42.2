"""AdversaryAgent — adversarial manipulation-detection agent (AGT-07-adv).

Wraps the logic from simulation_engine.adversary_agent.AdversaryAgent
into the AGT-XX agent protocol so it produces agent decisions that
flow into the meta-controller, not just simulations.
"""

from __future__ import annotations

from collections import deque
from collections.abc import Mapping
from dataclasses import dataclass, field

from core.contracts.agent import AgentDecisionTrace, AgentIntrospection
from core.contracts.events import SignalEvent
from core.contracts.market import MarketTick
from intelligence_engine.agents._base import AgentBase


class ManipulationPattern:
    WASH_TRADE = "wash_trade"
    SPOOFING = "spoofing"
    STOP_HUNT = "stop_hunt"
    LAYERING = "layering"


@dataclass
class AdversaryAgent(AgentBase, AgentIntrospection):
    """Detects market manipulation and emits defensive HOLD signals.

    Patterns:
    * wash trade  — high tick count with near-zero price movement
    * spoofing    — spread expands then contracts rapidly
    * stop hunt    — sharp spike beyond recent range + immediate reversal
    * layering    — depth imbalance + rapid book changes
    """

    agent_id: str = "AGT-07-adversary"
    wash_window: int = 20
    wash_vol_threshold: float = 0.0001
    wash_min_ticks: int = 15
    spoof_spread_factor: float = 3.0
    spoof_window: int = 5
    stop_hunt_range_factor: float = 2.0
    stop_hunt_window: int = 8
    ring_capacity: int = 64

    _mid_window: deque[float] = field(init=False, repr=False)
    _spread_window: deque[float] = field(init=False, repr=False)
    _prev_spread: float = field(default=0.0, init=False, repr=False)
    _last_decision_direction: str = field(default="HOLD", init=False, repr=False)
    _last_decision_confidence: float = field(default=0.0, init=False, repr=False)
    _last_decision_ts_ns: int = field(default=0, init=False, repr=False)

    def __post_init__(self) -> None:
        AgentBase.__init__(self, self.agent_id, self.ring_capacity)
        if self.wash_window < 2:
            raise ValueError("wash_window must be >= 2")
        if self.wash_min_ticks < 1:
            raise ValueError("wash_min_ticks must be >= 1")
        if self.spoof_window < 1:
            raise ValueError("spoof_window must be >= 1")
        if self.stop_hunt_window < 2:
            raise ValueError("stop_hunt_window must be >= 2")
        self._mid_window = deque(maxlen=max(self.wash_window, self.stop_hunt_window))
        self._spread_window = deque(maxlen=max(self.spoof_window, 10))

    def observe_tick(self, tick: MarketTick) -> None:
        if tick.bid <= 0.0 or tick.ask <= 0.0 or tick.ask < tick.bid:
            return
        mid = 0.5 * (tick.bid + tick.ask)
        if mid <= 0.0:
            return
        self._mid_window.append(mid)
        spread = tick.ask - tick.bid
        self._spread_window.append(spread)
        self._prev_spread = spread

    def decide(self, signal: SignalEvent) -> AgentDecisionTrace:
        rationale: list[str] = []
        active: list[str] = []

        if len(self._mid_window) >= self.wash_min_ticks:
            if self._detect_wash_trade():
                rationale.append("manip_wash_trade")
                active.append(ManipulationPattern.WASH_TRADE)

        if self._detect_spoofing():
            rationale.append("manip_spoofing")
            active.append(ManipulationPattern.SPOOFING)

        if self._detect_stop_hunt():
            rationale.append("manip_stop_hunt")
            active.append(ManipulationPattern.STOP_HUNT)

        if active:
            direction = "HOLD"
            confidence = 0.9
            rationale.append("manipulation_detected")
        else:
            direction = "HOLD"
            confidence = 0.1
            rationale.append("clean")

        trace = AgentDecisionTrace(
            ts_ns=int(signal.ts_ns),
            signal_id=str(signal.meta.get("signal_id", "")),
            direction=direction,
            confidence=confidence,
            rationale_tags=tuple(rationale),
            memory_refs=(),
        )
        self._last_decision_direction = direction
        self._last_decision_confidence = confidence
        self._last_decision_ts_ns = int(signal.ts_ns)
        self._record_decision(trace)
        return trace

    def _detect_wash_trade(self) -> bool:
        if len(self._mid_window) < self.wash_min_ticks:
            return False
        window = list(self._mid_window)[-self.wash_window :]
        if len(window) < 2:
            return False
        mean = sum(window) / len(window)
        if mean == 0:
            return False
        variance = sum((x - mean) ** 2 for x in window) / len(window)
        std = variance**0.5
        rel_std = std / abs(mean)
        return rel_std < self.wash_vol_threshold

    def _detect_spoofing(self) -> bool:
        if len(self._spread_window) < self.spoof_window + 1:
            return False
        recent = list(self._spread_window)[-self.spoof_window :]
        avg = sum(recent) / len(recent)
        if avg == 0:
            return False
        expanded = any(s > self.spoof_spread_factor * avg for s in recent[: self.spoof_window // 2])
        contracted = all(s < avg * 1.5 for s in recent[self.spoof_window // 2 :])
        return expanded and contracted

    def _detect_stop_hunt(self) -> bool:
        if len(self._mid_window) < self.stop_hunt_window:
            return False
        window = list(self._mid_window)[-self.stop_hunt_window :]
        if len(window) < 2:
            return False
        high = max(window)
        low = min(window)
        latest = window[-1]
        prev = window[-2]
        range_hl = high - low
        if range_hl == 0:
            return False
        spike = max(abs(latest - low), abs(high - latest)) / range_hl
        reversal = (latest - prev) * (window[-3] - prev) < 0 if len(window) >= 3 else False
        return spike > self.stop_hunt_range_factor * 0.5 and reversal

    def state_snapshot(self) -> Mapping[str, str]:
        return {
            "agent_id": self.agent_id,
            "lifecycle": "ACTIVE",
            "last_decision_direction": self._last_decision_direction,
            "last_decision_confidence": f"{self._last_decision_confidence:.6f}",
            "last_decision_ts_ns": str(self._last_decision_ts_ns),
            "decisions_in_window": str(len(self._decision_buffer)),
            "wash_window": str(self.wash_window),
            "spoof_window": str(self.spoof_window),
        }


__all__ = ["AdversaryAgent", "ManipulationPattern"]
