"""AgentOrchestrator — peer coordinator for AGT-XX agents.

The meta-controller makes execution decisions; this module coordinates
which agents see which signals and fuses their independent decisions
into a single composite signal before that signal reaches the
meta-controller / signal funnel.

Wave 2 additions:
* ``RegimeAgentPool`` — regime-keyed agent subsets so only agents
  relevant to the current market regime participate.
* ``AgentSelector`` — picks the active pool per tick based on the
  committed regime from the meta-controller router.
"""

from __future__ import annotations

from collections import deque
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from core.contracts.agent import AgentDecisionTrace, AgentIntrospection
from core.contracts.events import Side, SignalEvent
from core.contracts.market import MarketTick

# ---------------------------------------------------------------------------
# DTOs
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class AgentSignal:
    symbol: str
    ts_ns: int
    side: Side
    confidence: float
    participating_agents: tuple[str, ...]
    decision_traces: tuple[AgentDecisionTrace, ...]
    conflict_resolution: str = "unanimous"
    regime_override: str | None = None
    pool_name: str = "default"


# ---------------------------------------------------------------------------
# Agent pool + selector (Wave 2)
# ---------------------------------------------------------------------------


class RegimeAgentPool:
    """Maps regime labels to agent subsets.

    An agent can belong to multiple pools.  When no pool is registered
    for the current regime the ``fallback`` pool is used (defaults to
    all agents).
    """

    def __init__(
        self,
        agents: Mapping[str, AgentIntrospection] | None = None,
        *,
        fallback: str = "default",
    ) -> None:
        self._all = dict(agents or {})
        self._pools: dict[str, set[str]] = {}
        self._fallback = fallback

    @property
    def agent_ids(self) -> tuple[str, ...]:
        return tuple(self._all.keys())

    def add_pool(self, name: str, agent_ids: Sequence[str]) -> None:
        self._pools[name] = set(agent_ids)

    def agents_for_regime(self, regime: str) -> Mapping[str, AgentIntrospection]:
        pool_name = AgentSelector.pick(regime)
        pool = self._pools.get(pool_name)
        if pool is None:
            return dict(self._all)
        return {aid: self._all[aid] for aid in pool if aid in self._all}

    def register(self, agent_id: str, agent: AgentIntrospection) -> None:
        self._all[agent_id] = agent

    def unregister(self, agent_id: str) -> None:
        self._all.pop(agent_id, None)
        for ids in self._pools.values():
            ids.discard(agent_id)


class AgentSelector:
    """Pure helper: pick a pool name from a regime string.

    Mapping (configurable via registry/agent_orchestrator.yaml):
        TREND_UP   -> trend_pool
        TREND_DOWN -> trend_pool
        RANGE      -> range_pool
        VOL_SPIKE  -> vol_pool
        default/fallback -> default
    """

    _MAP: dict[str, str] = {
        "TREND_UP": "trend_pool",
        "TREND_DOWN": "trend_pool",
        "RANGE": "range_pool",
        "VOL_SPIKE": "vol_pool",
    }

    @classmethod
    def pick(cls, regime: str) -> str:
        return cls._MAP.get(regime, "default")


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------


class AgentOrchestrator:
    DEFAULT_RING = 128

    def __init__(
        self,
        pool: RegimeAgentPool | None = None,
        *,
        ring_capacity: int = DEFAULT_RING,
    ) -> None:
        if ring_capacity <= 0:
            raise ValueError("ring_capacity must be > 0")
        self._pool = pool or RegimeAgentPool()
        self._signals: deque[AgentSignal] = deque(maxlen=ring_capacity)
        self._tick_seq: int = 0
        self._last_regime: str = "default"

    @property
    def agent_ids(self) -> tuple[str, ...]:
        return self._pool.agent_ids

    def register(self, agent_id: str, agent: AgentIntrospection) -> None:
        self._pool.register(agent_id, agent)

    def unregister(self, agent_id: str) -> None:
        self._pool.unregister(agent_id)

    def add_pool(self, name: str, agent_ids: Sequence[str]) -> None:
        self._pool.add_pool(name, agent_ids)

    def observe_tick(self, tick: MarketTick) -> None:
        active = self._pool.agents_for_regime(self._last_regime)
        for agent in active.values():
            fn = getattr(agent, "observe_tick", None)
            if fn is not None:
                fn(tick)

    def decide(
        self,
        *,
        ts_ns: int,
        signal: SignalEvent,
        symbol: str,
        regime: str | None = None,
    ) -> AgentSignal:
        self._tick_seq += 1
        if regime is not None:
            self._last_regime = regime
        pool_name = AgentSelector.pick(self._last_regime)
        active = self._pool.agents_for_regime(self._last_regime)
        traces: list[AgentDecisionTrace] = []
        for agent_id, agent in active.items():
            fn = getattr(agent, "decide", None)
            if fn is None:
                continue
            trace = fn(signal)
            if not trace.signal_id:
                trace = AgentDecisionTrace(
                    ts_ns=trace.ts_ns,
                    signal_id=f"orch-{self._tick_seq}-{agent_id}",
                    direction=trace.direction,
                    confidence=trace.confidence,
                    rationale_tags=trace.rationale_tags,
                    memory_refs=trace.memory_refs,
                )
            traces.append(trace)

        side, confidence, conflict = AgentOrchestrator._fuse(traces)
        out = AgentSignal(
            symbol=symbol,
            ts_ns=ts_ns,
            side=side,
            confidence=confidence,
            participating_agents=tuple(
                a for a, t in zip(active.keys(), traces) if t.direction != "HOLD"
            ),
            decision_traces=tuple(traces),
            conflict_resolution=conflict,
            regime_override=self._last_regime if self._last_regime != "default" else None,
            pool_name=pool_name,
        )
        self._signals.append(out)
        return out

    def recent(self, n: int = 10) -> tuple[AgentSignal, ...]:
        if n <= 0:
            return ()
        items = tuple(self._signals)
        return items[-n:] if n < len(items) else items

    def snapshot(self) -> dict[str, Any]:
        return {
            "agent_count": len(self._pool.agent_ids),
            "last_regime": self._last_regime,
            "signal_history": len(self._signals),
            "tick_seq": self._tick_seq,
        }

    @staticmethod
    def _fuse(
        traces: Sequence[AgentDecisionTrace],
    ) -> tuple[Side, float, str]:
        if not traces:
            return Side.HOLD, 0.0, "no_agents"

        buy_w = sum(t.confidence for t in traces if t.direction == "BUY")
        sell_w = sum(t.confidence for t in traces if t.direction == "SELL")
        hold_w = sum(t.confidence for t in traces if t.direction == "HOLD")
        participants = [t for t in traces if t.direction != "HOLD"]

        if not participants:
            return Side.HOLD, 0.0, "all_hold"

        if buy_w > sell_w and buy_w > hold_w:
            side = Side.BUY
            conflict = "majority_buy"
        elif sell_w > buy_w and sell_w > hold_w:
            side = Side.SELL
            conflict = "majority_sell"
        else:
            side = Side.HOLD
            conflict = "hold_dominant"

        winner_w = buy_w if side is Side.BUY else sell_w if side is Side.SELL else hold_w
        total = buy_w + sell_w + hold_w
        confidence = min(1.0, winner_w / total) if total > 0 else 0.0
        return side, confidence, conflict


__all__ = [
    "AgentOrchestrator",
    "AgentSelector",
    "AgentSignal",
    "RegimeAgentPool",
]
