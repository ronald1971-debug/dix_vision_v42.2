"""Liquidity Hunter — adversarial agent that hunts liquidity traps.

Specializes in detecting when markets become thin (liquidity depletion)
and when large players position to trap retail liquidity.
Part of adversarial modeling (TIS Section 4).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class LiquidityTrapType(StrEnum):
    """Types of liquidity traps detected."""

    THIN_BOOK = "THIN_BOOK"  # Order book becomes dangerously thin
    LIQUIDITY_VOID = "LIQUIDITY_VOID"  # Depth vanishes at price level
    ICEBERG_MERGE = "ICEBERG_MERGE"  # Hidden large orders coalesce
    RETAIL_HUNT = "RETAIL_HUNT"  # Moves designed to trigger retail stops


@dataclass(frozen=True, slots=True)
class LiquidityTrapAlert:
    """Detected liquidity trap during simulation."""

    trap_type: LiquidityTrapType
    symbol: str
    ts_ns: int
    depth_before: float  # USD depth before event
    depth_after: float  # USD depth after event
    price_level: float
    confidence: float  # [0, 1] how certain
    severity: float  # [0, 1] potential impact
    recommendation: str


@dataclass(frozen=True, slots=True)
class LiquiditySnapshot:
    """Order book liquidity snapshot."""

    symbol: str
    ts_ns: int
    bid_depth: float
    ask_depth: float
    mid_price: float
    spread_bps: float
    top_bid_size: float
    top_ask_size: float


class LiquidityHunter:
    """Detects liquidity trap patterns in order book data.

    Watches for:
    - Sudden depth evaporation (liquidity voids)
    - Thin book conditions before large moves
    - Trap formations at technical levels
    - Iceberg order clustering
    """

    def __init__(
        self,
        *,
        thin_threshold_usd: float = 5000.0,
        depth_drop_threshold: float = 0.5,
        trap_window: int = 100,
    ) -> None:
        self._thin_thresh = thin_threshold_usd
        self._drop_thresh = depth_drop_threshold
        self._history: list[LiquiditySnapshot] = []
        self._max_history = trap_window

    def observe(self, snapshot: LiquiditySnapshot) -> list[LiquidityTrapAlert]:
        """Observe liquidity snapshot; return any trap alerts."""
        alerts: list[LiquidityTrapAlert] = []

        # Add to history
        self._history.append(snapshot)
        if len(self._history) > self._max_history:
            self._history = self._history[-self._max_history :]

        # Check for thin book
        total_depth = snapshot.bid_depth + snapshot.ask_depth
        if total_depth < self._thin_thresh:
            alerts.append(
                LiquidityTrapAlert(
                    trap_type=LiquidityTrapType.THIN_BOOK,
                    symbol=snapshot.symbol,
                    ts_ns=snapshot.ts_ns,
                    depth_before=total_depth,
                    depth_after=total_depth,
                    price_level=snapshot.mid_price,
                    confidence=1.0,
                    severity=0.8,
                    recommendation="Reduce position size; avoid market orders.",
                )
            )

        # Check for sudden depth drop
        if len(self._history) >= 2:
            prev = self._history[-2]
            prev_depth = prev.bid_depth + prev.ask_depth
            if prev_depth > 0 and total_depth < prev_depth * (1 - self._drop_thresh):
                alerts.append(
                    LiquidityTrapAlert(
                        trap_type=LiquidityTrapType.LIQUIDITY_VOID,
                        symbol=snapshot.symbol,
                        ts_ns=snapshot.ts_ns,
                        depth_before=prev_depth,
                        depth_after=total_depth,
                        price_level=snapshot.mid_price,
                        confidence=0.9,
                        severity=0.7,
                        recommendation="Cancel resting orders; wait for liquidity return.",
                    )
                )

        # Check for trap at technical levels (round numbers)
        trap_at_level = self._check_trap_level(snapshot)
        if trap_at_level:
            alerts.append(trap_at_level)

        return alerts

    def _check_trap_level(self, snapshot: LiquiditySnapshot) -> LiquidityTrapAlert | None:
        """Check if liquidity is being hunted at round price levels."""

        # Check if near round number
        price = snapshot.mid_price
        round_levels = [10000, 50000, 100000, 500000]  # example levels

        for level in round_levels:
            distance = abs(price - level) / level
            if distance < 0.02:  # Within 2% of round number
                # Check for asymmetric depth (thin on one side)
                total = snapshot.bid_depth + snapshot.ask_depth
                if total == 0:
                    continue
                imbalance = abs(snapshot.bid_depth - snapshot.ask_depth) / total
                if imbalance > 0.7:  # Heavy imbalance
                    return LiquidityTrapAlert(
                        trap_type=LiquidityTrapType.RETAIL_HUNT,
                        symbol=snapshot.symbol,
                        ts_ns=snapshot.ts_ns,
                        depth_before=total,
                        depth_after=total,
                        price_level=level,
                        confidence=0.75,
                        severity=0.6,
                        recommendation="Avoid round number liquidity; expect wick hunt.",
                    )
        return None


__all__ = [
    "LiquidityHunter",
    "LiquiditySnapshot",
    "LiquidityTrapAlert",
    "LiquidityTrapType",
]
