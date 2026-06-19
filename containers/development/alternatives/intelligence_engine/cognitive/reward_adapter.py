"""Reward adapter — integrates RewardSystem into agent decision-making.

Wraps :class:`learning_engine.reward_system.RewardSystem` so agents
can reward-shape their confidence without depending on learning_engine
directly (B1 boundary).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class AgentRewardContext:
    pnl_usd: float = 0.0
    holding_period_ns: int = 0
    entry_slippage_bps: float = 0.0
    exit_slippage_bps: float = 0.0
    intended_size: float = 0.0
    actual_size: float = 0.0
    regime_at_entry: str = "UNKNOWN"
    regime_predicted: str = "UNKNOWN"
    peak_pnl_usd: float = 0.0
    portfolio_drawdown_pct: float = 0.0


@dataclass(frozen=True, slots=True)
class AgentRewardSignal:
    composite: float
    raw_pnl_reward: float
    risk_adjusted_reward: float
    drawdown_penalty: float
    execution_reward: float
    consistency_reward: float
    regime_reward: float
    slippage_penalty: float


class RewardAdapter:
    def __init__(self) -> None:
        self._system: Any | None = None
        self._last: AgentRewardSignal | None = None

    def _get_system(self) -> Any | None:
        if self._system is None:
            try:
                from learning_engine.reward_system import RewardSystem
                self._system = RewardSystem()
            except Exception:
                return None
        return self._system

    def compute(self, ctx: AgentRewardContext) -> AgentRewardSignal | None:
        system = self._get_system()
        if system is None:
            return None
        try:
            from learning_engine.reward_system import RewardSignal, TradeOutcome
            outcome = TradeOutcome(
                pnl_usd=ctx.pnl_usd,
                holding_period_ns=ctx.holding_period_ns,
                entry_slippage_bps=ctx.entry_slippage_bps,
                exit_slippage_bps=ctx.exit_slippage_bps,
                intended_size=ctx.intended_size,
                actual_size=ctx.actual_size,
                regime_at_entry=ctx.regime_at_entry,
                regime_predicted=ctx.regime_predicted,
                peak_pnl_usd=ctx.peak_pnl_usd,
                portfolio_drawdown_pct=ctx.portfolio_drawdown_pct,
            )
            rs: RewardSignal = system.compute(outcome)
            out = AgentRewardSignal(
                composite=rs.composite_reward,
                raw_pnl_reward=rs.raw_pnl_reward,
                risk_adjusted_reward=rs.risk_adjusted_reward,
                drawdown_penalty=rs.drawdown_penalty,
                execution_reward=rs.execution_reward,
                consistency_reward=rs.consistency_reward,
                regime_reward=rs.regime_reward,
                slippage_penalty=rs.slippage_penalty,
            )
            self._last = out
            return out
        except Exception:
            return None

    def shape_confidence(self, base_confidence: float, reward_composite: float) -> float:
        if self._last is None:
            return base_confidence
        mod = max(0.0, min(1.0, base_confidence + reward_composite * 0.1))
        return mod

    def last_signal(self) -> AgentRewardSignal | None:
        return self._last


__all__ = ["AgentRewardContext", "AgentRewardSignal", "RewardAdapter"]
