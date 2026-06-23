"""Governance Rule - defines governance rules to monitor."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class RuleType(Enum):
    """Types of governance rules."""

    APPROVAL_THRESHOLD = "approval_threshold"
    RISK_LIMIT = "risk_limit"
    POSITION_LIMIT = "position_limit"
    SIGNAL_FILTER = "signal_filter"
    LEARNING_GATE = "learning_gate"


@dataclass
class GovernanceRule:
    """A governance rule with observability."""

    rule_id: str = field(default_factory=lambda: f"rule_{time.time_ns()}")
    name: str = ""
    rule_type: RuleType = RuleType.APPROVAL_THRESHOLD
    description: str = ""
    threshold: float = 0.5
    current_value: float = 0.0
    strictness: float = 1.0  # 1.0 = strict, 0.0 = lenient
    enabled: bool = True
    times_triggered: int = 0
    times_bypassed: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)

    def evaluate(self, value: float) -> bool:
        """Check if value triggers the rule."""
        triggered = value >= self.threshold
        if triggered:
            self.times_triggered += 1
        return triggered

    def evaluate_strict(self, value: float) -> tuple[bool, bool]:
        """Evaluate with strictness consideration.

        Returns: (should_block, was_triggered)
        """
        triggered = self.evaluate(value)
        should_block = triggered and (self.strictness > 0.5)
        return should_block, triggered

    def effectiveness(self) -> float:
        """Get rule effectiveness ratio."""
        total = self.times_triggered + self.times_bypassed
        if total == 0:
            return 0.0
        return self.times_bypassed / total
