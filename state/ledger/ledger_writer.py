"""Ledger Writer – typed write interface for the event store.

Provides domain-specific write methods so callers don't need to
construct raw event dicts.
"""

from __future__ import annotations

import time
from typing import Any

from core.types import ExecutionIntent, HazardEvent, TradeResult
from state.ledger.event_store import EventStore, LedgerEvent


class LedgerWriter:
    """High-level writer for the six logical streams."""

    def __init__(self, store: EventStore) -> None:
        self._store = store

    def write_governance_event(
        self, event_type: str, details: dict[str, Any]
    ) -> LedgerEvent:
        return self._store.append(
            stream="governance",
            event_type=event_type,
            payload={"details": details, "recorded_at": time.time()},
        )

    def write_cognition_event(
        self, event_type: str, details: dict[str, Any]
    ) -> LedgerEvent:
        return self._store.append(
            stream="cognition",
            event_type=event_type,
            payload={"details": details, "recorded_at": time.time()},
        )

    def write_execution_intent(self, intent: ExecutionIntent) -> LedgerEvent:
        return self._store.append(
            stream="execution",
            event_type="execution_intent",
            payload={
                "intent_id": intent.intent_id,
                "symbol": intent.symbol,
                "direction": intent.direction,
                "quantity": intent.quantity,
                "confidence": intent.confidence,
                "reasoning": intent.reasoning,
            },
        )

    def write_trade_result(self, result: TradeResult) -> LedgerEvent:
        return self._store.append(
            stream="execution",
            event_type="trade_result",
            payload={
                "trade_id": result.trade_id,
                "intent_id": result.intent_id,
                "symbol": result.symbol,
                "direction": result.direction,
                "fill_price": result.fill_price,
                "fill_quantity": result.fill_quantity,
                "fees": result.fees,
                "slippage": result.slippage,
                "status": result.status,
                "venue": result.venue,
            },
        )

    def write_hazard(self, hazard: HazardEvent) -> LedgerEvent:
        return self._store.append(
            stream="system",
            event_type="hazard_detected",
            payload={
                "hazard_id": hazard.hazard_id,
                "hazard_type": hazard.hazard_type,
                "severity": hazard.severity.name,
                "source": hazard.source,
                "description": hazard.description,
            },
        )

    def write_learning_event(
        self, event_type: str, details: dict[str, Any]
    ) -> LedgerEvent:
        return self._store.append(
            stream="learning",
            event_type=event_type,
            payload={"details": details, "recorded_at": time.time()},
        )

    def write_evolution_event(
        self, event_type: str, details: dict[str, Any]
    ) -> LedgerEvent:
        return self._store.append(
            stream="evolution",
            event_type=event_type,
            payload={"details": details, "recorded_at": time.time()},
        )

    def write_system_event(
        self, event_type: str, details: dict[str, Any]
    ) -> LedgerEvent:
        return self._store.append(
            stream="system",
            event_type=event_type,
            payload={"details": details, "recorded_at": time.time()},
        )
