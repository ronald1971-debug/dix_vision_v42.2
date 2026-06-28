"""Operator Intent - defines operator objectives."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class IntentPriority(Enum):
    """Priority levels for operator intents."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass(frozen=True, slots=True)
class OperatorIntent:
    """An operator intent for system guidance."""

    intent_id: str = field(default_factory=lambda: f"intent_{time.time_ns()}")
    description: str = ""
    priority: IntentPriority = IntentPriority.MEDIUM
    domain: str = ""
    created_at: int = field(default_factory=lambda: time.time_ns())
    active: bool = True
    progress: float = 0.0
    target_completion: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def deactivate(self) -> OperatorIntent:
        """Deactivate this intent."""
        return OperatorIntent(
            intent_id=self.intent_id,
            description=self.description,
            priority=self.priority,
            domain=self.domain,
            created_at=self.created_at,
            active=False,
            progress=self.progress,
            target_completion=self.target_completion,
            metadata=self.metadata,
        )

    def update_progress(self, progress: float) -> OperatorIntent:
        """Update intent progress."""
        return OperatorIntent(
            intent_id=self.intent_id,
            description=self.description,
            priority=self.priority,
            domain=self.domain,
            created_at=self.created_at,
            active=self.active,
            progress=min(1.0, max(0.0, progress)),
            target_completion=self.target_completion,
            metadata=self.metadata,
        )
