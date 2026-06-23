"""Health Report - cognitive health status report."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from cognitive_engine.cognitive_health.drift_detector import DriftEvent


class HealthStatus(Enum):
    """Overall cognitive health status."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


@dataclass
class HealthReport:
    """Comprehensive cognitive health report."""

    report_id: str = field(default_factory=lambda: f"health_{time.time_ns()}")
    status: HealthStatus = HealthStatus.HEALTHY
    generated_at: int = field(default_factory=lambda: time.time_ns())
    belief_drift_count: int = 0
    knowledge_drift_count: int = 0
    strategy_drift_count: int = 0
    confidence_inflation_count: int = 0
    memory_corruption_detected: bool = False
    reasoning_quality_score: float = 1.0
    drift_events: tuple[DriftEvent, ...] = ()
    recommendations: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)
