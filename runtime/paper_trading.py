"""Paper Trading Environment – Phase 13.

Requirements:
  - No capital risk
  - Full ledger recording
  - Promotion gate approval

100% paper environment.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

from core.kernel import BeliefState
from core.types import ExecutionIntent, PromotionStage, TradeResult
from governance.kernel import GovernanceKernel
from state.ledger.event_store import EventStore
from state.ledger.writer import LedgerWriter


@dataclass
class PaperTradingConfig:
    initial_balance: float = 100_000.0
    max_positions: int = 10
    record_all_events: bool = True


@dataclass
class PaperPosition:
    symbol: str = ""
    direction: str = ""
    quantity: float = 0.0
    entry_price: float = 0.0
    current_price: float = 0.0
    unrealized_pnl: float = 0.0
    opened_at: float = field(default_factory=time.time)

    def update_price(self, price: float) -> None:
        self.current_price = price
        if self.direction == "long":
            self.unrealized_pnl = (price - self.entry_price) * self.quantity
        else:
            self.unrealized_pnl = (self.entry_price - price) * self.quantity


@dataclass
class PaperTradingState:
    balance: float = 100_000.0
    positions: list[PaperPosition] = field(default_factory=list)
    realized_pnl: float = 0.0
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0

    @property
    def unrealized_pnl(self) -> float:
        return sum(p.unrealized_pnl for p in self.positions)

    @property
    def equity(self) -> float:
        return self.balance + self.unrealized_pnl

    @property
    def win_rate(self) -> float:
        if self.total_trades == 0:
            return 0.0
        return self.winning_trades / self.total_trades


class PaperTradingEnvironment:
    """Full paper trading environment with no capital risk."""

    def __init__(
        self,
        governance: GovernanceKernel,
        config: PaperTradingConfig | None = None,
    ) -> None:
        self._governance = governance
        self._config = config or PaperTradingConfig()
        self._store = EventStore()
        self._ledger = LedgerWriter(self._store)
        self._router = AdapterRouter()
        self._orchestrator = ExecutionOrchestrator(governance, self._router, self._ledger)
        self._state = PaperTradingState(balance=self._config.initial_balance)

    def ensure_paper_stage(self) -> bool:
        """Verify we are at paper trading promotion stage."""
        return self._governance.current_stage in (
            PromotionStage.SIMULATION,
            PromotionStage.BACKTEST,
            PromotionStage.PAPER,
        )

    def execute_intent(
        self, intent: ExecutionIntent, belief: BeliefState
    ) -> TradeResult | None:
        result = self._orchestrator.process_intent(intent, belief, venue="paper")
        if result.was_executed and result.trade_result:
            trade = result.trade_result
            self._state.total_trades += 1

            if trade.direction in ("long", "short"):
                pos = PaperPosition(
                    symbol=trade.symbol,
                    direction=trade.direction,
                    quantity=trade.fill_quantity,
                    entry_price=trade.fill_price,
                    current_price=trade.fill_price,
                )
                self._state.positions.append(pos)
            return trade
        return None

    def close_position(self, symbol: str, price: float) -> float:
        pnl = 0.0
        remaining: list[PaperPosition] = []
        for pos in self._state.positions:
            if pos.symbol == symbol:
                pos.update_price(price)
                pnl += pos.unrealized_pnl
                self._state.realized_pnl += pos.unrealized_pnl
                self._state.balance += pos.unrealized_pnl
                if pos.unrealized_pnl > 0:
                    self._state.winning_trades += 1
                else:
                    self._state.losing_trades += 1
            else:
                remaining.append(pos)
        self._state.positions = remaining
        return pnl

    def get_state(self) -> PaperTradingState:
        return self._state

    @property
    def ledger(self) -> LedgerWriter:
        return self._ledger

    @property
    def event_store(self) -> EventStore:
        return self._store
