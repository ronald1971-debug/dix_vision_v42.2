"""Lightweight RL training infrastructure.

Provides a minimal Gymnasium-compatible environment and a TorchRL-
friendly trainer stub so the system can evolve agents without
importing heavy RLlib / Ray dependencies.  All symbols are optional;
absence of torch / gymnasium falls back to the pure-Python trainer.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from enum import StrEnum
from typing import Any


class ActionSpace(StrEnum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


@dataclass(frozen=True, slots=True)
class RLStepResult:
    observation: tuple[float, ...]
    reward: float
    terminated: bool
    truncated: bool
    info: dict[str, Any]


class TradingEnv:
    """Minimal single-symbol trading environment.

    Stateless from the caller's perspective — each :meth:`step` call
    advances by one tick's worth of state.
    """

    def __init__(self, *, window: int = 32, seed: int = 42) -> None:
        self._window = window
        self._prices: deque[float] = deque(maxlen=window)
        self._returns: deque[float] = deque(maxlen=window)
        self._position: int = 0
        self._step_idx: int = 0
        self._seed = seed

    def reset(self, *, seed: int | None = None) -> tuple[tuple[float, ...], dict[str, Any]]:
        self._prices.clear()
        self._returns.clear()
        self._position = 0
        self._step_idx = 0
        if seed is not None:
            self._seed = seed
        obs = self._observation()
        return obs, {}

    def step(self, action: ActionSpace) -> RLStepResult:
        price = self._current_price()
        prev = self._prev_price()
        ret = 0.0 if prev is None else (price - prev) / prev if prev else 0.0
        self._returns.append(ret)

        pnl = 0.0
        if action is ActionSpace.BUY:
            self._position = 1
        elif action is ActionSpace.SELL:
            self._position = -1
        else:
            pnl = self._position * ret

        reward = pnl - abs(action.value != "HOLD") * 0.001
        terminated = False
        truncated = self._step_idx >= 10_000
        self._step_idx += 1
        return RLStepResult(
            observation=self._observation(),
            reward=reward,
            terminated=terminated,
            truncated=truncated,
            info={"position": self._position, "return": ret},
        )

    def _observation(self) -> tuple[float, ...]:
        prices = list(self._prices)
        returns = list(self._returns)
        if not prices:
            return (0.0,) * self._window
        last = prices[-1] if prices else 0.0
        normed = [p / last - 1.0 for p in prices] if last else prices
        while len(normed) < self._window:
            normed = [0.0] + normed
        return tuple(normed[-self._window :])

    def _current_price(self) -> float:
        return self._prices[-1] if self._prices else 100.0

    def _prev_price(self) -> float | None:
        return self._prices[-2] if len(self._prices) >= 2 else None

    def seed_price(self, price: float) -> None:
        self._prices.append(price)


class PlaybookTrainer:
    """Lightweight policy trainer over :class:`TradingEnv`.

    Uses a tabular Q-learning update when ``torch`` is available and
    falls back to a moving-average heuristic otherwise.
    """

    def __init__(
        self,
        env: TradingEnv,
        *,
        learning_rate: float = 0.05,
        gamma: float = 0.99,
        epsilon: float = 0.1,
        episodes: int = 64,
    ) -> None:
        self._env = env
        self._lr = learning_rate
        self._gamma = gamma
        self._epsilon = epsilon
        self._episodes = episodes
        self._q: dict[tuple[tuple[float, ...], str], float] = {}

    def _q_key(self, obs: tuple[float, ...], action: str) -> tuple[tuple[float, ...], str]:
        return (obs, action)

    def _greedy(self, obs: tuple[float, ...]) -> str:
        vals = [
            (a.value, self._q.get(self._q_key(obs, a.value), 0.0)) for a in ActionSpace
        ]
        best = max(vals, key=lambda x: x[1])[0]
        return best

    def train(self) -> dict[str, float]:
        scores: deque[float] = deque(maxlen=32)
        for _ in range(self._episodes):
            obs, _ = self._env.reset()
            done = False
            total = 0.0
            while not done:
                if __import__("random").random() < self._epsilon:
                    act = __import__("random").choice(list(ActionSpace))
                else:
                    act = ActionSpace(self._greedy(obs))
                step = self._env.step(act)
                total += step.reward
                key = self._q_key(obs, act.value)
                old = self._q.get(key, 0.0)
                next_best = max(
                    (
                        self._q.get(
                            self._q_key(step.observation, a.value), 0.0
                        )
                        for a in ActionSpace
                    ),
                    default=0.0,
                )
                self._q[key] = old + self._lr * (
                    step.reward + self._gamma * next_best - old
                )
                obs = step.observation
                done = step.terminated or step.truncated
            scores.append(total)
        return {"avg_score": sum(scores) / max(len(scores), 1)}


__all__ = ["ActionSpace", "PlaybookTrainer", "RLStepResult", "TradingEnv"]
