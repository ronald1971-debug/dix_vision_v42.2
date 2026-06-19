"""Meta-learning adapter — integrates MetaLearningLoop into INDIRA runtime.

Wraps :class:`learning_engine.meta_learning_loop.MetaLearningLoop` so
that IndiraRuntime can call it every tick without importing the
learning_engine package directly (B1 compliance).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class MetaLearningUpdate:
    mode: str
    learning_rate: float
    exploration_rate: float
    stability_score: float
    reason: str


class MetaLearningAdapter:
    def __init__(self) -> None:
        self._loop: Any | None = None
        self._last: MetaLearningUpdate | None = None

    def _get_loop(self) -> Any:
        if self._loop is None:
            try:
                from learning_engine.meta_learning_loop import MetaLearningLoop
                self._loop = MetaLearningLoop()
            except Exception:
                return None
        return self._loop

    def update(self, *, ts_ns: int, outcome_pnl: float = 0.0) -> MetaLearningUpdate | None:
        loop = self._get_loop()
        if loop is None:
            return None
        try:
            meta_update = loop.update(outcome_pnl=outcome_pnl, ts_ns=ts_ns)
            self._last = MetaLearningUpdate(
                mode=meta_update.mode.value,
                learning_rate=meta_update.learning_rate,
                exploration_rate=meta_update.exploration_rate,
                stability_score=meta_update.stability_score,
                reason=meta_update.reason,
            )
            return self._last
        except Exception:
            return None

    def last_update(self) -> MetaLearningUpdate | None:
        return self._last


_adapter: MetaLearningAdapter | None = None


def get_meta_learning_adapter() -> MetaLearningAdapter:
    global _adapter
    if _adapter is None:
        _adapter = MetaLearningAdapter()
    return _adapter


__all__ = ["MetaLearningAdapter", "MetaLearningUpdate", "get_meta_learning_adapter"]
