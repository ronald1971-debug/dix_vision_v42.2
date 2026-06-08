"""Hypothesis Generation – INDIRA forms and evaluates trading hypotheses.

A hypothesis is a structured prediction about future market behavior
that can be tested and converted into an ExecutionIntent.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any


class HypothesisStatus(Enum):
    FORMING = auto()
    ACTIVE = auto()
    VALIDATED = auto()
    INVALIDATED = auto()
    EXPIRED = auto()
    EXECUTED = auto()


@dataclass
class Hypothesis:
    hypothesis_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    title: str = ""
    thesis: str = ""
    symbol: str = ""
    direction: str = ""  # long | short
    confidence: float = 0.0
    evidence_ids: list[str] = field(default_factory=list)
    belief_ids: list[str] = field(default_factory=list)
    status: HypothesisStatus = HypothesisStatus.FORMING
    expected_return: float = 0.0
    risk_estimate: float = 0.0
    time_horizon_seconds: float = 0.0
    formed_at: float = field(default_factory=time.time)
    expires_at: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def risk_reward_ratio(self) -> float:
        if self.risk_estimate == 0:
            return 0.0
        return self.expected_return / self.risk_estimate

    def is_expired(self) -> bool:
        if self.expires_at <= 0:
            return False
        return time.time() > self.expires_at


class HypothesisEngine:
    """Generates, tracks, and evaluates hypotheses."""

    def __init__(self, max_active: int = 10) -> None:
        self._hypotheses: dict[str, Hypothesis] = {}
        self._max_active = max_active
        self._history: list[Hypothesis] = []

    def generate(
        self,
        title: str,
        thesis: str,
        symbol: str,
        direction: str,
        confidence: float,
        expected_return: float = 0.0,
        risk_estimate: float = 0.0,
        time_horizon_seconds: float = 3600.0,
        belief_ids: list[str] | None = None,
    ) -> Hypothesis | None:
        active_count = sum(
            1
            for h in self._hypotheses.values()
            if h.status in (HypothesisStatus.FORMING, HypothesisStatus.ACTIVE)
        )
        if active_count >= self._max_active:
            return None

        h = Hypothesis(
            title=title,
            thesis=thesis,
            symbol=symbol,
            direction=direction,
            confidence=max(0.0, min(1.0, confidence)),
            expected_return=expected_return,
            risk_estimate=risk_estimate,
            time_horizon_seconds=time_horizon_seconds,
            belief_ids=belief_ids or [],
            status=HypothesisStatus.FORMING,
            expires_at=time.time() + time_horizon_seconds,
        )
        self._hypotheses[h.hypothesis_id] = h
        self._history.append(h)
        return h

    def activate(self, hypothesis_id: str) -> bool:
        h = self._hypotheses.get(hypothesis_id)
        if h and h.status == HypothesisStatus.FORMING:
            h.status = HypothesisStatus.ACTIVE
            return True
        return False

    def validate(self, hypothesis_id: str) -> bool:
        h = self._hypotheses.get(hypothesis_id)
        if h and h.status == HypothesisStatus.ACTIVE:
            h.status = HypothesisStatus.VALIDATED
            return True
        return False

    def invalidate(self, hypothesis_id: str) -> bool:
        h = self._hypotheses.get(hypothesis_id)
        if h and h.status in (HypothesisStatus.FORMING, HypothesisStatus.ACTIVE):
            h.status = HypothesisStatus.INVALIDATED
            return True
        return False

    def mark_executed(self, hypothesis_id: str) -> bool:
        h = self._hypotheses.get(hypothesis_id)
        if h and h.status == HypothesisStatus.VALIDATED:
            h.status = HypothesisStatus.EXECUTED
            return True
        return False

    def expire_stale(self) -> int:
        expired = 0
        for h in self._hypotheses.values():
            if h.is_expired() and h.status in (
                HypothesisStatus.FORMING,
                HypothesisStatus.ACTIVE,
            ):
                h.status = HypothesisStatus.EXPIRED
                expired += 1
        return expired

    def get_active(self) -> list[Hypothesis]:
        return [
            h
            for h in self._hypotheses.values()
            if h.status in (HypothesisStatus.FORMING, HypothesisStatus.ACTIVE)
        ]

    def get_validated(self) -> list[Hypothesis]:
        return [
            h for h in self._hypotheses.values()
            if h.status == HypothesisStatus.VALIDATED
        ]

    def get_best_hypothesis(self) -> Hypothesis | None:
        validated = self.get_validated()
        if not validated:
            active = self.get_active()
            if not active:
                return None
            return max(active, key=lambda h: h.confidence)
        return max(validated, key=lambda h: h.confidence)
