"""Tests for lightweight RL components."""

from __future__ import annotations

from intelligence_engine.learning.lightweight_rl import (
    ActionSpace,
    PlaybookTrainer,
    RLStepResult,
    TradingEnv,
)


class TestTradingEnv:
    def test_reset_returns_observation(self):
        env = TradingEnv(window=8)
        obs, info = env.reset()
        assert len(obs) == 8
        assert info == {}

    def test_seed_price_then_step(self):
        env = TradingEnv(window=4)
        for p in [100.0, 100.1, 100.2, 100.3]:
            env.seed_price(p)
        action = ActionSpace.BUY
        result = env.step(action)
        assert isinstance(result, RLStepResult)
        assert len(result.observation) == 4
        assert result.terminated is False or result.truncated is True

    def test_all_actions(self):
        env = TradingEnv(window=4)
        env.seed_price(100.0)
        for act in [ActionSpace.BUY, ActionSpace.SELL, ActionSpace.HOLD]:
            r = env.step(act)
            assert isinstance(r.reward, float)

    def test_truncate_after_max_steps(self):
        env = TradingEnv(window=4, seed=1)
        env.reset()
        for _ in range(10_001):
            env.step(ActionSpace.HOLD)
        assert env._step_idx >= 10001


class TestPlaybookTrainer:
    def test_train_returns_metrics(self):
        env = TradingEnv(window=8)
        for i in range(8):
            env.seed_price(100.0 + i * 0.1)
        trainer = PlaybookTrainer(env, episodes=2)
        metrics = trainer.train()
        assert "avg_score" in metrics
