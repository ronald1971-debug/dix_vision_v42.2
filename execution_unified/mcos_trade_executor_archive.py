"""Trade Executor – the actual execution layer.

Receives governed intents and dispatches to venue adapters.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass

from core.types import ExecutionIntent, TradeResult


@dataclass
class ExecutionConfig:
    max_slippage_pct: float = 0.5
    max_retry_attempts: int = 3
    timeout_seconds: float = 10.0
    default_venue: str = "paper"


class TradeExecutor:
    """Executes governed trade intents against venues.

    Only processes intents that have been approved by Governance.
    """

    def __init__(self, config: ExecutionConfig | None = None) -> None:
        self._config = config or ExecutionConfig()
        self._execution_log: list[TradeResult] = []
        self._pending: list[ExecutionIntent] = []
        self._is_live: bool = False

    def submit_intent(self, intent: ExecutionIntent) -> str:
        """Queue an intent for execution. Returns a tracking ID."""
        self._pending.append(intent)
        return intent.intent_id

    def execute_next(self) -> TradeResult | None:
        """Execute the next pending intent."""
        if not self._pending:
            return None

        intent = self._pending.pop(0)
        return self._execute(intent)

    def execute_all(self) -> list[TradeResult]:
        """Execute all pending intents."""
        results: list[TradeResult] = []
        while self._pending:
            result = self.execute_next()
            if result:
                results.append(result)
        return results

    def _execute(self, intent: ExecutionIntent) -> TradeResult:
        """Execute a single intent (paper mode by default)."""
        fill_price = intent.price_limit if intent.price_limit else 0.0
        slippage = fill_price * (self._config.max_slippage_pct / 100) if fill_price else 0.0

        result = TradeResult(
            trade_id=uuid.uuid4().hex[:12],
            intent_id=intent.intent_id,
            symbol=intent.symbol,
            direction=intent.direction,
            fill_price=(
                fill_price + slippage if intent.direction == "long" else fill_price - slippage
            ),
            fill_quantity=intent.quantity,
            fees=0.0,
            slippage=slippage,
            timestamp=time.time(),
            venue=self._config.default_venue,
            status="filled",
        )
        self._execution_log.append(result)
        return result

    def get_execution_log(self) -> list[TradeResult]:
        return list(self._execution_log)

    @property
    def pending_count(self) -> int:
        return len(self._pending)

    @property
    def executed_count(self) -> int:
        return len(self._execution_log)
