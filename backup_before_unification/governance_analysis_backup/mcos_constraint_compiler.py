"""Policy Constraint Compiler.

Compiles active PolicyRules into an EXECUTION_CONSTRAINT_SET
that the execution layer can evaluate in the hot path.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from governance.mcos_kernel import GovernanceKernel


@dataclass(frozen=True)
class ExecutionConstraint:
    name: str
    constraint_type: str  # "max_position" | "min_confidence" | "regime_filter" | "max_loss"
    value: Any = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionConstraintSet:
    """Compiled constraint set for the execution hot path."""

    constraints: list[ExecutionConstraint] = field(default_factory=list)
    max_position_pct: float = 1.0
    max_loss_pct: float = 1.0
    min_confidence: float = 0.0
    allowed_regimes: list[str] = field(default_factory=list)
    kill_switch_active: bool = False

    def allows_execution(self) -> bool:
        return not self.kill_switch_active

    def check_confidence(self, confidence: float) -> bool:
        return confidence >= self.min_confidence

    def check_regime(self, regime: str) -> bool:
        if not self.allowed_regimes:
            return True
        return regime.lower() in [r.lower() for r in self.allowed_regimes]

    def check_position_size(self, size_pct: float) -> bool:
        return size_pct <= self.max_position_pct


class ConstraintCompiler:
    """Compiles governance policies into an execution-ready constraint set."""

    def __init__(self, governance: GovernanceKernel) -> None:
        self._governance = governance

    def compile(self) -> ExecutionConstraintSet:
        constraint_set = ExecutionConstraintSet(
            kill_switch_active=self._governance.is_halted,
        )

        constraints: list[ExecutionConstraint] = []
        all_regimes: set[str] = set()

        for policy in self._governance._policies.values():
            if not policy.enabled:
                continue

            if policy.max_position_pct < constraint_set.max_position_pct:
                constraint_set.max_position_pct = policy.max_position_pct
                constraints.append(
                    ExecutionConstraint(
                        name=policy.name,
                        constraint_type="max_position",
                        value=policy.max_position_pct,
                    )
                )

            if policy.max_loss_pct < constraint_set.max_loss_pct:
                constraint_set.max_loss_pct = policy.max_loss_pct
                constraints.append(
                    ExecutionConstraint(
                        name=policy.name,
                        constraint_type="max_loss",
                        value=policy.max_loss_pct,
                    )
                )

            if policy.min_confidence > constraint_set.min_confidence:
                constraint_set.min_confidence = policy.min_confidence
                constraints.append(
                    ExecutionConstraint(
                        name=policy.name,
                        constraint_type="min_confidence",
                        value=policy.min_confidence,
                    )
                )

            if policy.allowed_regimes:
                all_regimes.update(policy.allowed_regimes)

        if all_regimes:
            constraint_set.allowed_regimes = sorted(all_regimes)
            constraints.append(
                ExecutionConstraint(
                    name="regime_filter",
                    constraint_type="regime_filter",
                    value=sorted(all_regimes),
                )
            )

        constraint_set.constraints = constraints
        return constraint_set
