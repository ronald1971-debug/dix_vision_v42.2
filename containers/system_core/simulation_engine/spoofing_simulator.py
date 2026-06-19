"""Spoofing Simulator — adversarial market manipulation modeling.

Simulates spoofing behavior for strategy testing and robustness.
Part of adversarial modeling (TIS Section 4).
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass

from simulation.multi_agent_market import SimFill, SimOrder


@dataclass(frozen=True, slots=True)
class SpoofingReport:
    """Detected spoofing event during simulation."""

    detector_id: str
    symbol: str
    ts_ns: int
    spoof_size: float
    cancel_probability: float
    estimated_impact_bps: float
    confidence: float


class SpoofingSimulator:
    """Simulates spoofing behavior for testing.

    Detects and models spoofing patterns in market simulations:
    - Large orders placed away from best bid/ask
    - High cancel rates
    - No genuine intent to trade

    Used in adversarial testing and strategy robustness validation.
    """

    def __init__(
        self,
        *,
        large_order_threshold: float = 100.0,
        cancel_rate_threshold: float = 0.8,
        observation_window: int = 50,
    ) -> None:
        self._size_thresh = large_order_threshold
        self._cancel_thresh = cancel_rate_threshold
        self._window = observation_window
        self._order_history: dict[str, deque] = {}
        self._reports: list[SpoofingReport] = []

    def observe(
        self,
        symbol: str,
        orders: list[SimOrder],
        fills: list[SimFill],
        ts_ns: int,
    ) -> list[SpoofingReport]:
        """Observe orders and fills, detect spoofing.

        Returns list of SpoofingReports for any detected spoofing.
        """
        if symbol not in self._order_history:
            self._order_history[symbol] = deque(maxlen=self._window)

        history = self._order_history[symbol]

        # Filter large orders
        large_orders = [o for o in orders if o.quantity > self._size_thresh]

        for order in large_orders:
            # Track order lifecycle
            history.append(
                {
                    "order": order,
                    "filled": sum(1 for f in fills if f.agent_id == order.agent_id),
                    "ts_ns": ts_ns,
                }
            )

        # Analyze for spoofing patterns
        reports: list[SpoofingReport] = []
        for snapshot in list(history):
            order = snapshot["order"]
            filled = snapshot["filled"]

            # Calculate cancel probability
            total_time = ts_ns - snapshot["ts_ns"]
            cancel_prob = 1.0 - (filled / order.quantity)

            if cancel_prob > self._cancel_thresh:
                # Calculate estimated market impact
                impact_bps = self._estimate_impact(symbol, order, fills)

                report = SpoofingReport(
                    detector_id=f"spoof-{symbol}",
                    symbol=symbol,
                    ts_ns=ts_ns,
                    spoof_size=order.quantity,
                    cancel_probability=cancel_prob,
                    estimated_impact_bps=impact_bps,
                    confidence=min(cancel_prob * 1.2, 1.0),
                )
                reports.append(report)
                self._reports.append(report)

        return reports

    def _estimate_impact(self, symbol: str, order: SimOrder, fills: list[SimFill]) -> float:
        """Estimate market impact of a spoofing order in basis points."""
        if not fills:
            return 0.0

        # Simple estimation based on order size vs total volume
        total_fill_size = sum(f.quantity for f in fills)
        if total_fill_size == 0:
            return 0.0

        size_ratio = order.quantity / total_fill_size
        return size_ratio * 100.0  # basis points estimate

    @property
    def reports(self) -> list[SpoofingReport]:
        """All detected spoofing reports."""
        return list(self._reports)


__all__ = [
    "SpoofingReport",
    "SpoofingSimulator",
]