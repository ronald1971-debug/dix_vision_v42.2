"""Adapter Router – routes execution to the correct venue adapter.

Supports multiple venue types with a pluggable adapter interface.
"""

from __future__ import annotations

import time
import uuid
from abc import ABC, abstractmethod

from core.types import ExecutionIntent, TradeResult


class VenueAdapter(ABC):
    """Base class for venue adapters."""

    @abstractmethod
    def name(self) -> str: ...

    @abstractmethod
    def is_available(self) -> bool: ...

    @abstractmethod
    def execute(self, intent: ExecutionIntent) -> TradeResult: ...


class PaperAdapter(VenueAdapter):
    """Paper trading adapter – simulates fills with no capital risk."""

    def __init__(self) -> None:
        self._fills: list[TradeResult] = []

    def name(self) -> str:
        return "paper"

    def is_available(self) -> bool:
        return True

    def execute(self, intent: ExecutionIntent) -> TradeResult:
        result = TradeResult(
            trade_id=uuid.uuid4().hex[:12],
            intent_id=intent.intent_id,
            symbol=intent.symbol,
            direction=intent.direction,
            fill_price=intent.price_limit or 100.0,
            fill_quantity=intent.quantity,
            fees=0.0,
            slippage=0.0,
            timestamp=time.time(),
            venue="paper",
            status="filled",
        )
        self._fills.append(result)
        return result


class AdapterRouter:
    """Routes intents to the appropriate venue adapter."""

    def __init__(self) -> None:
        self._adapters: dict[str, VenueAdapter] = {}
        self._default_venue: str = "paper"

        paper = PaperAdapter()
        self._adapters["paper"] = paper

    def register_adapter(self, adapter: VenueAdapter) -> None:
        self._adapters[adapter.name()] = adapter

    def route(self, intent: ExecutionIntent, venue: str | None = None) -> TradeResult:
        target = venue or self._default_venue
        adapter = self._adapters.get(target)
        if not adapter:
            raise ValueError(f"No adapter for venue '{target}'")
        if not adapter.is_available():
            raise RuntimeError(f"Venue '{target}' is not available")
        return adapter.execute(intent)

    def get_available_venues(self) -> list[str]:
        return [name for name, adapter in self._adapters.items() if adapter.is_available()]

    def set_default_venue(self, venue: str) -> None:
        if venue not in self._adapters:
            raise ValueError(f"Unknown venue: {venue}")
        self._default_venue = venue
