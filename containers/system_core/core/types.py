"""Shared type definitions used across the ."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any


class Engine(Enum):
    INDIRA = "indira"
    EXECUTION = "execution"
    GOVERNANCE = "governance"
    DYON = "dyon"
    LEARNING = "learning"
    SYSTEM = "system"


class Stream(Enum):
    GOVERNANCE = "governance"
    COGNITION = "cognition"
    EXECUTION = "execution"
    SYSTEM = "system"
    LEARNING = "learning"
    EVOLUTION = "evolution"


class Severity(Enum):
    INFO = auto()
    WARNING = auto()
    CRITICAL = auto()
    FATAL = auto()


class ApprovalStatus(Enum):
    PENDING = auto()
    APPROVED = auto()
    REJECTED = auto()
    EXPIRED = auto()


class PromotionStage(Enum):
    SIMULATION = "simulation"
    BACKTEST = "backtest"
    PAPER = "paper"
    SHADOW = "shadow"
    CANARY = "canary"
    PRODUCTION = "production"


@dataclass(frozen=True)
class ExecutionIntent:
    """An intent to execute a trade, produced by INDIRA, gated by Governance."""

    intent_id: str = ""
    symbol: str = ""
    direction: str = ""  # "long" | "short" | "close"
    quantity: float = 0.0
    price_limit: float | None = None
    confidence: float = 0.0
    reasoning: str = ""
    hypothesis_id: str = ""
    constraints: dict[str, Any] = field(default_factory=dict)
    timestamp: float = 0.0


@dataclass(frozen=True)
class TradeResult:
    """Outcome of an executed trade."""

    trade_id: str = ""
    intent_id: str = ""
    symbol: str = ""
    direction: str = ""
    fill_price: float = 0.0
    fill_quantity: float = 0.0
    fees: float = 0.0
    slippage: float = 0.0
    timestamp: float = 0.0
    venue: str = ""
    status: str = ""  # "filled" | "partial" | "rejected" | "cancelled"


@dataclass(frozen=True)
class HazardEvent:
    """System hazard detected by DYON."""

    hazard_id: str = ""
    hazard_type: str = ""  # stale_feed | dead_service | contract_violation | dependency_failure
    severity: Severity = Severity.WARNING
    source: str = ""
    description: str = ""
    timestamp: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)
