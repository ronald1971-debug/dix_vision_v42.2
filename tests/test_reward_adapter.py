"""Tests for reward adapter."""

from __future__ import annotations

from intelligence_engine.cognitive.reward_adapter import AgentRewardContext, RewardAdapter


class TestRewardAdapter:
    def test_compute_returns_signal(self):
        adapter = RewardAdapter()
        ctx = AgentRewardContext(
            pnl_usd=10.0,
            holding_period_ns=1_000_000,
            entry_slippage_bps=1.0,
            exit_slippage_bps=1.0,
            intended_size=1000.0,
            actual_size=1000.0,
            regime_at_entry="TREND_UP",
            regime_predicted="TREND_UP",
            peak_pnl_usd=15.0,
            portfolio_drawdown_pct=0.01,
        )
        sig = adapter.compute(ctx)
        assert sig is not None
        assert isinstance(sig.composite, float)

    def test_shape_confidence_without_last(self):
        adapter = RewardAdapter()
        out = adapter.shape_confidence(0.5, 1.0)
        assert out == 0.5

    def test_shape_confidence_with_last(self):
        adapter = RewardAdapter()
        adapter.compute(AgentRewardContext(pnl_usd=10.0))
        out = adapter.shape_confidence(0.5, 1.0)
        assert 0.0 <= out <= 1.0
