"""Identity - system self-model for INDIRA."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

from cognitive_engine.identity_layer.capabilities import Capability, CapabilityStatus
from cognitive_engine.identity_layer.maturity import MaturityAssessment, MaturityLevel


@dataclass
class Identity:
    """INDIRA's self-model.

    Architectural identity - not philosophical.
    Tracks what the system knows about itself.
    """

    system_name: str = "INDIRA"
    version: str = "42.2"
    created_at: int = field(default_factory=lambda: time.time_ns())
    capabilities: tuple[Capability, ...] = ()
    maturity_assessments: tuple[MaturityAssessment, ...] = ()
    active_objectives: tuple[str, ...] = ()
    disabled_capabilities: tuple[str, ...] = ()

    def add_capability(self, capability: Capability) -> None:
        """Add a capability to the identity."""
        self.capabilities = (*self.capabilities, capability)

    def has_capability(self, name: str) -> bool:
        """Check if system has an active capability."""
        for cap in self.capabilities:
            if cap.name == name and cap.status == CapabilityStatus.ACTIVE:
                return True
        return False

    def get_capability(self, name: str) -> Capability | None:
        """Get a capability by name."""
        for cap in self.capabilities:
            if cap.name == name:
                return cap
        return None

    def set_objective(self, objective: str) -> None:
        """Set an active objective."""
        if objective not in self.active_objectives:
            self.active_objectives = (*self.active_objectives, objective)

    def complete_objective(self, objective: str) -> None:
        """Mark objective as complete (remove from active)."""
        self.active_objectives = tuple(o for o in self.active_objectives if o != objective)

    def disable_capability(self, name: str) -> None:
        """Disable a capability."""
        if name not in self.disabled_capabilities:
            self.disabled_capabilities = (*self.disabled_capabilities, name)

    def get_maturity(self, domain: str) -> MaturityLevel:
        """Get maturity level for a domain."""
        for ma in self.maturity_assessments:
            if ma.domain == domain:
                return ma.current_level
        return MaturityLevel.NOVICE

    def set_maturity(self, domain: str, level: MaturityLevel, evidence: str = "") -> None:
        """Set maturity level for a domain."""
        existing = [
            (ma, i) for i, ma in enumerate(self.maturity_assessments) if ma.domain == domain
        ]

        if existing:
            ma, idx = existing[0]
            # Would need to update - simplified
            self.maturity_assessments = tuple(
                (
                    m
                    if i != idx
                    else MaturityAssessment(
                        domain=domain, current_level=level, evidence=(evidence,)
                    )
                )
                for i, m in enumerate(self.maturity_assessments)
            )
        else:
            ma = MaturityAssessment(domain=domain, current_level=level, evidence=(evidence,))
            self.maturity_assessments = (*self.maturity_assessments, ma)

    def summary(self) -> dict[str, Any]:
        """Get identity summary."""
        return {
            "system_name": self.system_name,
            "version": self.version,
            "capability_count": len(self.capabilities),
            "active_objectives": list(self.active_objectives),
            "disabled_count": len(self.disabled_capabilities),
            "highest_maturity": max(
                (ma.current_level for ma in self.maturity_assessments), default=MaturityLevel.NOVICE
            ),
        }
