"""Cognitive KPIs — measure cognitive maturity, not just money.

Currently systems measure:
    PnL, Sharpe, Drawdown

But cognitive maturity requires:
    - Knowledge Growth
    - Prediction Accuracy
    - Trader Model Accuracy
    - Belief Accuracy
    - Strategy Discovery Rate
    - Explanation Quality
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class CognitiveKPIs:
    """Cognitive maturity key performance indicators."""

    knowledge_growth_rate: float = 0.0  # new knowledge items per day
    prediction_accuracy: float = 0.0  # percentage of accurate predictions
    trader_model_accuracy: float = 0.0  # accuracy of trader profile predictions
    belief_accuracy: float = 0.0  # alignment of beliefs with outcomes
    strategy_discovery_rate: float = 0.0  # new strategies discovered per period
    explanation_quality: float = 0.0  # completeness of decision explanations


@dataclass
class CognitiveKPITracker:
    """Tracks cognitive KPIs over time."""

    _kpis: dict[str, list[float]] = field(default_factory=dict)
    _timestamps: dict[str, list[int]] = field(default_factory=dict)

    def record(self, kpi_name: str, value: float, ts_ns: int) -> None:
        if kpi_name not in self._timestamps:
            self._timestamps[kpi_name] = []
            self._kpis[kpi_name] = []
        self._timestamps[kpi_name].append(ts_ns)
        self._kpis[kpi_name].append(value)

    def get_latest(self, kpi_name: str) -> float | None:
        values = self._kpis.get(kpi_name, [])
        return values[-1] if values else None

    def get_trend(self, kpi_name: str) -> float:
        values = self._kpis.get(kpi_name, [])
        if len(values) < 2:
            return 0.0
        return values[-1] - values[0]

    def compute_kpis(self) -> CognitiveKPIs:
        return CognitiveKPIs(
            knowledge_growth_rate=self.get_latest("knowledge_growth_rate") or 0.0,
            prediction_accuracy=self.get_latest("prediction_accuracy") or 0.0,
            trader_model_accuracy=self.get_latest("trader_model_accuracy") or 0.0,
            belief_accuracy=self.get_latest("belief_accuracy") or 0.0,
            strategy_discovery_rate=self.get_latest("strategy_discovery_rate") or 0.0,
            explanation_quality=self.get_latest("explanation_quality") or 0.0,
        )


__all__ = [
    "CognitiveKPIs",
    "CognitiveKPITracker",
]