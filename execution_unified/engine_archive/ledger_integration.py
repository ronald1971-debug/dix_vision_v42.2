"""
execution_engine/paper_trading/ledger_integration.py
DIX VISION v42.2 — Paper Trade Ledger Integration (Phase 13)

Ensures full ledger recording for all paper trades as required by Phase 13.
Every paper trade execution is recorded to the event store with:
- Paper trade flag (INV-56 Triad Lock)
- Venue information
- Full execution details
- P&L impact
- Decision trace links

This module integrates the paper trading system with the state ledger
to meet Phase 13 requirement: "Full ledger recording"
"""

from __future__ import annotations

import threading
from dataclasses import dataclass, field

from core.contracts.events import ExecutionEvent, SignalEvent
from state.ledger.event_store import append_event


@dataclass
class PaperTradeRecord:
    """Structured record for paper trade ledger entries."""

    trade_id: str
    venue: str
    symbol: str
    side: str
    qty: float
    price: float
    executed_qty: float
    executed_price: float
    status: str
    timestamp_ns: int
    paper_flag: str = "1"  # INV-56: paper=1
    pnl_usd: float = 0.0
    fee_usd: float = 0.0
    slippage_usd: float = 0.0
    decision_trace_id: str = ""
    signal_id: str = ""
    portfolio_cash_before: float = 0.0
    portfolio_cash_after: float = 0.0
    portfolio_positions: dict[str, float] = field(default_factory=dict)


class PaperTradeLedgerIntegrator:
    """Integrates paper trading with the ledger for full trade recording.

    Every paper trade execution is recorded to the event store to ensure
    complete audit trail and meet Phase 13 requirements.

    Thread-safe singleton pattern.
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._trade_counter: int = 0
        self._enabled: bool = True

    def record_trade(
        self,
        signal: SignalEvent,
        execution: ExecutionEvent,
        venue: str,
        portfolio_cash_before: float,
        portfolio_cash_after: float,
        portfolio_positions: dict[str, float],
    ) -> str:
        """Record a paper trade to the ledger.

        Args:
            signal: The original signal event
            execution: The execution event from the paper adapter
            venue: The venue identifier (e.g., "binance_paper")
            portfolio_cash_before: Cash balance before trade
            portfolio_cash_after: Cash balance after trade
            portfolio_positions: Current portfolio positions

        Returns:
            The ledger event ID
        """
        with self._lock:
            if not self._enabled:
                return ""

            self._trade_counter += 1
            trade_id = f"paper_trade_{self._trade_counter}"

            # Calculate P&L and costs
            fee_usd = self._calculate_fee(execution)
            slippage_usd = self._calculate_slippage(signal, execution)
            pnl_usd = self._calculate_pnl(execution, fee_usd, slippage_usd)

            # Build paper trade record
            record = PaperTradeRecord(
                trade_id=trade_id,
                venue=venue,
                symbol=execution.symbol,
                side=execution.side.value if hasattr(execution.side, "value") else str(execution.side),
                qty=signal.qty,
                price=signal.price,
                executed_qty=execution.qty,
                executed_price=execution.price,
                status=execution.status.value if hasattr(execution.status, "value") else str(execution.status),
                timestamp_ns=execution.ts_ns,
                paper_flag="1",  # INV-56: always mark as paper
                pnl_usd=pnl_usd,
                fee_usd=fee_usd,
                slippage_usd=slippage_usd,
                decision_trace_id=signal.meta.get("decision_trace_id", "") if signal.meta else "",
                signal_id=str(signal.event_id) if hasattr(signal, "event_id") else "",
                portfolio_cash_before=portfolio_cash_before,
                portfolio_cash_after=portfolio_cash_after,
                portfolio_positions=portfolio_positions.copy(),
            )

            # Record to ledger
            event = append_event(
                event_type="MARKET",
                sub_type="PAPER_TRADE_EXECUTION",
                source="PAPER_TRADING_HUB",
                payload={
                    "trade_id": record.trade_id,
                    "venue": record.venue,
                    "symbol": record.symbol,
                    "side": record.side,
                    "qty": record.qty,
                    "price": record.price,
                    "executed_qty": record.executed_qty,
                    "executed_price": record.executed_price,
                    "status": record.status,
                    "timestamp_ns": record.timestamp_ns,
                    "paper": record.paper_flag,  # INV-56 compliance
                    "pnl_usd": record.pnl_usd,
                    "fee_usd": record.fee_usd,
                    "slippage_usd": record.slippage_usd,
                    "decision_trace_id": record.decision_trace_id,
                    "signal_id": record.signal_id,
                    "portfolio_cash_before": record.portfolio_cash_before,
                    "portfolio_cash_after": record.portfolio_cash_after,
                    "portfolio_positions": record.portfolio_positions,
                },
            )

            return event.event_id

    def _calculate_fee(self, execution: ExecutionEvent) -> float:
        """Calculate trading fee from execution event."""
        # Fee calculation depends on venue configuration
        # This is a simplified calculation - in production would use venue-specific rates
        if execution.meta:
            fee_bps = execution.meta.get("fee_bps", 0)
            if fee_bps:
                return abs(execution.qty * execution.price * fee_bps / 10000)
        return 0.0

    def _calculate_slippage(self, signal: SignalEvent, execution: ExecutionEvent) -> float:
        """Calculate slippage from signal to execution."""
        if signal.price and execution.price:
            price_diff = abs(execution.price - signal.price)
            return abs(execution.qty * price_diff)
        return 0.0

    def _calculate_pnl(self, execution: ExecutionEvent, fee_usd: float, slippage_usd: float) -> float:
        """Calculate realized P&L for the trade."""
        # P&L calculation simplified - would be more complex in production
        return -(fee_usd + slippage_usd)  # Paper trades have negative cost impact

    def enable(self) -> None:
        """Enable ledger recording."""
        with self._lock:
            self._enabled = True

    def disable(self) -> None:
        """Disable ledger recording (for testing only)."""
        with self._lock:
            self._enabled = False

    def is_enabled(self) -> bool:
        """Check if ledger recording is enabled."""
        with self._lock:
            return self._enabled

    def get_trade_count(self) -> int:
        """Get the total number of recorded paper trades."""
        with self._lock:
            return self._trade_counter


# Singleton instance
_integrator: PaperTradeLedgerIntegrator | None = None
_integrator_lock = threading.Lock()


def get_paper_trade_ledger_integrator() -> PaperTradeLedgerIntegrator:
    """Get the singleton paper trade ledger integrator."""
    global _integrator
    with _integrator_lock:
        if _integrator is None:
            _integrator = PaperTradeLedgerIntegrator()
    return _integrator


__all__ = [
    "PaperTradeLedgerIntegrator",
    "PaperTradeRecord",
    "get_paper_trade_ledger_integrator",
]
