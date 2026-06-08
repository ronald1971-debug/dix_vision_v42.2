"""Tests for AgentOrchestrator + RegimeAgentPool + AgentSelector."""

from __future__ import annotations

from dataclasses import dataclass

from core.contracts.agent import AgentDecisionTrace
from core.contracts.events import Side, SignalEvent
from core.contracts.market import MarketTick
from intelligence_engine.agents.scalper import ScalperAgent
from intelligence_engine.orchestrators.agent_orchestrator import (
    AgentOrchestrator,
    AgentSelector,
    RegimeAgentPool,
)


@dataclass
class _StubAgent:
    agent_id: str
    direction: str = "BUY"
    confidence: float = 0.8
    ring_capacity: int = 64

    def decide(self, signal):  # type: ignore[override]
        trace = AgentDecisionTrace(
            ts_ns=getattr(signal, "ts_ns", 0),
            signal_id=str(getattr(signal, "meta", {}).get("signal_id", "")),
            direction=self.direction,
            confidence=self.confidence,
            rationale_tags=(),
            memory_refs=(),
        )
        return trace

    def recent_decisions(self, n):  # type: ignore[override]
        return ()

    def state_snapshot(self):  # type: ignore[override]
        return {"agent_id": self.agent_id, "lifecycle": "ACTIVE"}


def _make_tick() -> MarketTick:
    return MarketTick(
        symbol="BTC",
        ts_ns=1_000_000_000,
        bid=100.0,
        ask=100.1,
        bid_size=1.0,
        ask_size=1.0,
    )


def _make_signal(side: Side = Side.BUY) -> SignalEvent:
    return SignalEvent(
        ts_ns=1_000_000_000,
        symbol="BTC",
        side=side,
        confidence=0.9,
        meta={},
        produced_by_engine="test",
        signal_trust="INTERNAL",
        signal_source="test",
    )


class TestRegimeAgentPool:
    def test_agents_for_regime_fallback(self):
        pool = RegimeAgentPool({"a": _StubAgent("a")})
        out = pool.agents_for_regime("UNKNOWN")
        assert "a" in out

    def test_agents_for_regime_specific(self):
        pool = RegimeAgentPool({"a": _StubAgent("a"), "b": _StubAgent("b")})
        pool.add_pool("trend_pool", ["a"])
        out = pool.agents_for_regime("TREND_UP")
        assert "a" in out
        assert "b" not in out

    def test_agents_for_regime_empty_pool_returns_all(self):
        pool = RegimeAgentPool({"a": _StubAgent("a"), "b": _StubAgent("b")})
        out = pool.agents_for_regime("RANDOM")
        assert "a" in out and "b" in out

    def test_unregister_removes_from_pools(self):
        pool = RegimeAgentPool({"a": _StubAgent("a")})
        pool.add_pool("trend_pool", ["a"])
        pool.unregister("a")
        assert "a" not in pool.agent_ids
        assert "a" not in pool._pools["trend_pool"]


class TestAgentSelector:
    def test_trend_regimes_map_to_trend_pool(self):
        assert AgentSelector.pick("TREND_UP") == "trend_pool"
        assert AgentSelector.pick("TREND_DOWN") == "trend_pool"

    def test_vol_regime_maps_to_vol_pool(self):
        assert AgentSelector.pick("VOL_SPIKE") == "vol_pool"

    def test_range_regime_maps_to_range_pool(self):
        assert AgentSelector.pick("RANGE") == "range_pool"

    def test_unknown_regime_falls_back(self):
        assert AgentSelector.pick("UNKNOWN") == "default"


class TestAgentOrchestrator:
    def test_regime_propagation(self):
        pool = RegimeAgentPool({"scalper": ScalperAgent()})
        orch = AgentOrchestrator(pool=pool)
        orch.decide(ts_ns=1_000_000_000, signal=_make_signal(), symbol="BTC", regime="TREND_UP")
        assert orch._last_regime == "TREND_UP"

    def test_hold_when_no_agents(self):
        pool = RegimeAgentPool({})
        orch = AgentOrchestrator(pool=pool)
        sig = orch.decide(ts_ns=1_000_000_000, signal=_make_signal(), symbol="BTC")
        assert sig.side is Side.HOLD
        assert sig.confidence == 0.0

    def test_recent(self):
        pool = RegimeAgentPool({"scalper": ScalperAgent()})
        orch = AgentOrchestrator(pool=pool)
        for _ in range(3):
            orch.decide(ts_ns=1_000_000_000, signal=_make_signal(), symbol="BTC")
        assert len(orch.recent(2)) == 2

    def test_snapshot(self):
        pool = RegimeAgentPool({"scalper": ScalperAgent()})
        orch = AgentOrchestrator(pool=pool)
        snap = orch.snapshot()
        assert "agent_count" in snap
        assert snap["agent_count"] == 1
