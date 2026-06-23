"""Market structure — understanding of price levels and order book shape."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class MarketStructure:
    """Knowledge about market microstructure and price structure.

    Captures:
        - Key price levels (support/resistance)
        - Order book shape (depth profile)
        - Volatility regime
        - Session characteristics
    """

    symbol: str
    key_levels: tuple[float, ...] = ()  # support/resistance levels
    order_book_shape: str = "unknown"  # "normal", "steep", "flat"
    volatility_regime: str = "medium"  # "low", "medium", "high"
    session_phase: str = "open"  # "open", "close", "asia", "europe", "us"
    microstructure_features: dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0

    @property
    def level_count(self) -> int:
        return len(self.key_levels)


class MarketStructureBuilder:
    """Builds market structure understanding from price/volume observations."""

    def __init__(self) -> None:
        self._structures: dict[str, MarketStructure] = {}

    def update(
        self,
        symbol: str,
        price: float,
        volume: float,
        order_book_signals: dict[str, Any] | None = None,
    ) -> MarketStructure:
        existing = self._structures.get(symbol)
        levels = list(existing.key_levels) if existing else []

        if len(levels) < 10:
            levels.append(price)

        structure = MarketStructure(
            symbol=symbol,
            key_levels=tuple(sorted(set(levels))),
            order_book_shape=(
                order_book_signals.get("shape", "unknown") if order_book_signals else "unknown"
            ),
            volatility_regime=(
                order_book_signals.get("vol_regime", "medium") if order_book_signals else "medium"
            ),
            microstructure_features=order_book_signals or {},
        )
        self._structures[symbol] = structure
        return structure

    def get(self, symbol: str) -> MarketStructure | None:
        return self._structures.get(symbol)
