"""Hazard Engine – detects and classifies system hazards.

Hazard types:
  - stale_feed: market data feed is outdated
  - dead_service: a required service has stopped responding
  - contract_violation: a module violated its architectural contract
  - dependency_failure: a dependency is unavailable

DYON detects hazards but NEVER trades.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field

from core.types import HazardEvent, Severity
from system_monitor.runtime_awareness import (
    RuntimeAwareness,
)


@dataclass
class HazardRule:
    rule_id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])
    name: str = ""
    hazard_type: str = ""
    severity: Severity = Severity.WARNING
    check_interval_seconds: float = 10.0
    enabled: bool = True


class HazardEngine:
    """Continuous hazard detection engine.

    Scans for system anomalies and emits SYSTEM_HAZARD_EVENTs.
    """

    def __init__(self, runtime: RuntimeAwareness) -> None:
        self._runtime = runtime
        self._rules: list[HazardRule] = self._default_rules()
        self._active_hazards: dict[str, HazardEvent] = {}
        self._hazard_history: list[HazardEvent] = []
        self._feed_timestamps: dict[str, float] = {}
        self._feed_max_age: float = 5.0

    def register_feed_update(self, feed_name: str) -> None:
        self._feed_timestamps[feed_name] = time.time()

    def scan(self) -> list[HazardEvent]:
        """Run all hazard checks and return newly detected hazards."""
        hazards: list[HazardEvent] = []
        hazards.extend(self._check_stale_feeds())
        hazards.extend(self._check_dead_services())

        for h in hazards:
            self._active_hazards[h.hazard_id] = h
            self._hazard_history.append(h)

        return hazards

    def get_active_hazards(self) -> list[HazardEvent]:
        return list(self._active_hazards.values())

    def resolve_hazard(self, hazard_id: str) -> bool:
        if hazard_id in self._active_hazards:
            del self._active_hazards[hazard_id]
            return True
        return False

    def get_hazard_history(self) -> list[HazardEvent]:
        return list(self._hazard_history)

    def _check_stale_feeds(self) -> list[HazardEvent]:
        hazards: list[HazardEvent] = []
        now = time.time()
        for feed_name, last_update in self._feed_timestamps.items():
            age = now - last_update
            if age > self._feed_max_age:
                hazards.append(
                    HazardEvent(
                        hazard_id=uuid.uuid4().hex[:12],
                        hazard_type="stale_feed",
                        severity=Severity.WARNING if age < 30 else Severity.CRITICAL,
                        source=f"feed:{feed_name}",
                        description=(
                            f"Feed '{feed_name}' is {age:.1f}s old" f" (max: {self._feed_max_age}s)"
                        ),
                        timestamp=now,
                        metadata={"feed": feed_name, "age_seconds": age},
                    )
                )
        return hazards

    def _check_dead_services(self) -> list[HazardEvent]:
        hazards: list[HazardEvent] = []
        dead = self._runtime.get_dead_services()
        for svc in dead:
            hazards.append(
                HazardEvent(
                    hazard_id=uuid.uuid4().hex[:12],
                    hazard_type="dead_service",
                    severity=Severity.CRITICAL,
                    source=f"service:{svc.name}",
                    description=f"Service '{svc.name}' ({svc.engine}) is dead",
                    timestamp=time.time(),
                    metadata={"service": svc.name, "engine": svc.engine},
                )
            )
        return hazards

    def _default_rules(self) -> list[HazardRule]:
        return [
            HazardRule(
                name="stale_feed_check",
                hazard_type="stale_feed",
                severity=Severity.WARNING,
            ),
            HazardRule(
                name="dead_service_check",
                hazard_type="dead_service",
                severity=Severity.CRITICAL,
            ),
            HazardRule(
                name="contract_violation_check",
                hazard_type="contract_violation",
                severity=Severity.CRITICAL,
            ),
            HazardRule(
                name="dependency_failure_check",
                hazard_type="dependency_failure",
                severity=Severity.WARNING,
            ),
        ]
