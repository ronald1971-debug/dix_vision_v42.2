"""Error Analysis – categorizes and learns from system failures.

Analyzes failed trades, incorrect beliefs, and system errors
to prevent recurrence.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any


class ErrorCategory(Enum):
    BELIEF_ERROR = auto()  # wrong market belief
    TIMING_ERROR = auto()  # right direction, wrong timing
    SIZING_ERROR = auto()  # right trade, wrong size
    EXECUTION_ERROR = auto()  # slippage, latency, fill issues
    REGIME_ERROR = auto()  # misidentified market regime
    DATA_ERROR = auto()  # stale or incorrect data
    GOVERNANCE_ERROR = auto()  # policy misconfiguration


@dataclass
class ErrorRecord:
    error_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    category: ErrorCategory = ErrorCategory.BELIEF_ERROR
    description: str = ""
    trade_id: str = ""
    hypothesis_id: str = ""
    loss_amount: float = 0.0
    root_cause: str = ""
    corrective_action: str = ""
    timestamp: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)


class ErrorAnalyzer:
    """Categorizes errors and extracts learning signals."""

    def __init__(self) -> None:
        self._errors: list[ErrorRecord] = []
        self._category_counts: dict[str, int] = {}

    def record_error(
        self,
        category: ErrorCategory,
        description: str,
        trade_id: str = "",
        hypothesis_id: str = "",
        loss_amount: float = 0.0,
        root_cause: str = "",
    ) -> ErrorRecord:
        error = ErrorRecord(
            category=category,
            description=description,
            trade_id=trade_id,
            hypothesis_id=hypothesis_id,
            loss_amount=loss_amount,
            root_cause=root_cause,
            corrective_action=self._suggest_corrective(category),
        )
        self._errors.append(error)
        cat_name = category.name
        self._category_counts[cat_name] = self._category_counts.get(cat_name, 0) + 1
        return error

    def get_errors(self, category: ErrorCategory | None = None) -> list[ErrorRecord]:
        if category:
            return [e for e in self._errors if e.category == category]
        return list(self._errors)

    def get_error_distribution(self) -> dict[str, int]:
        return dict(self._category_counts)

    def get_total_loss(self) -> float:
        return sum(e.loss_amount for e in self._errors)

    def get_top_error_category(self) -> str | None:
        if not self._category_counts:
            return None
        return max(self._category_counts, key=self._category_counts.get)  # type: ignore[arg-type]

    def _suggest_corrective(self, category: ErrorCategory) -> str:
        suggestions = {
            ErrorCategory.BELIEF_ERROR: "Review belief formation evidence thresholds",
            ErrorCategory.TIMING_ERROR: "Adjust time horizon parameters",
            ErrorCategory.SIZING_ERROR: "Reduce position sizing confidence multiplier",
            ErrorCategory.EXECUTION_ERROR: "Review execution latency and venue selection",
            ErrorCategory.REGIME_ERROR: "Increase regime detection sample window",
            ErrorCategory.DATA_ERROR: "Tighten feed freshness requirements",
            ErrorCategory.GOVERNANCE_ERROR: "Audit governance policy configuration",
        }
        return suggestions.get(category, "Review system logs")
