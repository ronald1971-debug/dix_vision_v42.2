"""Question Generator - generates questions for investigation."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class Question:
    """A generated investigative question."""

    question_id: str = field(default_factory=lambda: f"q_{time.time_ns()}")
    question: str = ""
    domain: str = ""
    priority: float = 0.5
    generated_at: int = field(default_factory=lambda: time.time_ns())
    context: dict[str, Any] = field(default_factory=dict)
    triggered_by: str = ""


class QuestionGenerator:
    """Generates questions to investigate unexpected patterns.

    Triggers on:
    - Performance anomalies
    - Regime changes
    - Strategy effectiveness shifts
    - Trader behavior changes
    """

    def __init__(self) -> None:
        self._questions: list[Question] = []

    def why_trader_performing(self, trader_id: str, performance_spike: float) -> Question:
        """Generate question about trader performance anomaly."""
        q = Question(
            question=f"Why is Trader {trader_id} suddenly outperforming with spike {performance_spike:.2%)}?",
            domain="trader_intelligence",
            priority=min(1.0, performance_spike * 2),
            context={"trader_id": trader_id, "spike": performance_spike},
            triggered_by="performance_anomaly",
        )
        self._questions.append(q)
        return q

    def why_strategy_working(self, strategy_id: str, regime: str) -> Question:
        """Generate question about strategy effectiveness."""
        q = Question(
            question=f"Why is strategy {strategy_id} working in {regime} regime?",
            domain="strategy_evolution",
            priority=0.7,
            context={"strategy_id": strategy_id, "regime": regime},
            triggered_by="strategy_effectiveness",
        )
        self._questions.append(q)
        return q

    def why_volatility_changed(self, symbol: str, vol_change: float) -> Question:
        """Generate question about volatility structure change."""
        q = Question(
            question=f"Why did volatility structure change for {symbol} by {vol_change:.2%)}?",
            domain="market_microstructure",
            priority=min(1.0, abs(vol_change)),
            context={"symbol": symbol, "change": vol_change},
            triggered_by="volatility_structure_change",
        )
        self._questions.append(q)
        return q

    def generate_from_pattern(self, pattern_type: str, context: dict[str, Any]) -> Question:
        """Generate question from detected pattern."""
        templates = {
            "regime_transition": "What caused the regime transition from {from_regime} to {to_regime}?",
            "correlation_breakdown": "Why did correlations break down in {market}?",
            "liquidity_vacuum": "What created the liquidity vacuum in {symbol}?",
            "catalyst_emergence": "What new catalyst is driving {symbol}?",
        }

        template = templates.get(pattern_type, f"What explains this {pattern_type}?")
        q = Question(
            question=template.format(**context),
            domain=context.get("domain", "general"),
            priority=context.get("priority", 0.5),
            context=context,
            triggered_by=pattern_type,
        )
        self._questions.append(q)
        return q

    def get_unanswered(self, limit: int = 50) -> list[Question]:
        """Get unanswered questions."""
        return [q for q in self._questions[-limit:] if not q.context.get("answered")]

    def mark_answered(self, question_id: str, answer: str) -> Question | None:
        """Mark a question as answered."""
        for q in self._questions:
            if q.question_id == question_id:
                # In a real implementation, this would update the question
                return q
        return None