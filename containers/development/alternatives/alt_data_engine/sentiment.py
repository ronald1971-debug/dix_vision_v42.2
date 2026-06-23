"""Sentiment analyzer for alternative data.

Combines news, social, and order-flow sentiment into a single
bounded composite score.
"""

from __future__ import annotations

from collections import deque


class SentimentAnalyzer:
    """Aggregates multi-source sentiment into a single score.

    The result is bounded to [-1.0, 1.0] where:
      * -1.0 = strong bearish sentiment
      *  0.0 = neutral
      * +1.0 = strong bullish sentiment

    A rolling trend is also maintained to detect sentiment shifts.
    """

    def __init__(
        self, *, news_weight: float = 0.4, social_weight: float = 0.4, orderflow_weight: float = 0.2
    ) -> None:
        self._news_weight = news_weight
        self._social_weight = social_weight
        self._orderflow_weight = orderflow_weight
        self._history: deque[float] = deque(maxlen=200)

    def score(
        self,
        news_sentiment: float,
        social_sentiment: float,
        orderflow_bias: float = 0.0,
    ) -> float:
        composite = (
            self._news_weight * news_sentiment
            + self._social_weight * social_sentiment
            + self._orderflow_weight * orderflow_bias
        )
        composite = max(-1.0, min(1.0, composite))
        self._history.append(composite)
        return composite

    def trend(self) -> float:
        """Slope of sentiment over the last 8 ticks. Positive means improving."""
        if len(self._history) < 4:
            return 0.0
        recent = list(self._history)[-8:]
        n = len(recent)
        x_mean = (n - 1) / 2.0
        y_mean = sum(recent) / n
        num = sum((i - x_mean) * (y - y_mean) for i, y in enumerate(recent))
        denom = sum((i - x_mean) ** 2 for i in range(n))
        return num / denom if abs(denom) > 1e-10 else 0.0

    def current(self) -> float:
        if not self._history:
            return 0.0
        return self._history[-1]


__all__ = ["SentimentAnalyzer"]
