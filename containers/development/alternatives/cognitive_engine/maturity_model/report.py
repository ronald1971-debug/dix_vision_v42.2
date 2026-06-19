"""Maturity Report - comprehensive maturity assessment."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

from cognitive_engine.maturity_model.levels import DomainMaturity, MaturityDomain, MaturityLevel


@dataclass
class MaturityReport:
    """Full maturity assessment report."""

    report_id: str = field(default_factory=lambda: f"maturity_{time.time_ns()}")
    generated_at: int = field(default_factory=lambda: time.time_ns())
    domains: tuple[DomainMaturity, ...] = ()
    overall_score: float = 0.0
    highest_domain: str = ""
    lowest_domain: str = ""
    improvement_areas: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    def get_level(self, domain: MaturityDomain) -> MaturityLevel:
        """Get maturity level for a domain."""
        for d in self.domains:
            if d.domain == domain:
                return d.level
        return MaturityLevel.NOVICE

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "generated_at": self.generated_at,
            "overall_score": self.overall_score,
            "domains": {d.domain.value: d.level_value() for d in self.domains},
            "highest": self.highest_domain,
            "lowest": self.lowest_domain,
        }