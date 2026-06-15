"""Cognitive Learning Governance.

Provides governance mechanisms for cognitive learning operations,
including safety constraints, ethical boundaries, and learning rate control.
"""

from __future__ import annotations

import dataclasses
import enum
import logging
import threading
from collections.abc import Mapping
from types import MappingProxyType
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

_logger = logging.getLogger(__name__)


class GovernanceAction(str, enum.Enum):
    """Actions that can be taken by learning governance."""

    ALLOW = "ALLOW"
    BLOCK = "BLOCK"
    MODIFY = "MODIFY"
    DEFER = "DEFER"


class LearningPhase(str, enum.Enum):
    """Phases of cognitive learning."""

    EXPLORATION = "EXPLORATION"
    EXPLOITATION = "EXPLOITATION"
    VALIDATION = "VALIDATION"
    FREEZE = "FREEZE"


@dataclasses.dataclass(frozen=True, slots=True)
class LearningConstraint:
    """A constraint on cognitive learning operations.

    Fields:
        constraint_id: Unique identifier for this constraint
        description: Human-readable description
        constraint_type: Type of constraint (safety, ethical, performance)
        severity: Severity of constraint (0.0-1.0)
        threshold: Threshold value for constraint
        is_hard: Whether this is a hard constraint (must be satisfied)
        metadata: Additional metadata
    """

    constraint_id: str
    description: str
    constraint_type: str
    severity: float
    threshold: float
    is_hard: bool
    metadata: Mapping[str, str] = dataclasses.field(default_factory=lambda: MappingProxyType({}))

    def __post_init__(self) -> None:
        if not 0.0 <= self.severity <= 1.0:
            raise ValueError(f"LearningConstraint.severity must be 0.0-1.0, got {self.severity}")


@dataclasses.dataclass(frozen=True, slots=True)
class GovernanceDecision:
    """Decision made by learning governance.

    Fields:
        decision_id: Unique identifier for this decision
        action: Action to take (ALLOW, BLOCK, MODIFY, DEFER)
        reasoning: Explanation for the decision
        confidence: Confidence in the decision (0.0-1.0)
        violated_constraints: List of violated constraint IDs
        timestamp_ns: Decision timestamp
    """

    decision_id: str
    action: GovernanceAction
    reasoning: str
    confidence: float
    violated_constraints: tuple[str, ...] = ()
    timestamp_ns: int = 0

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"GovernanceDecision.confidence must be 0.0-1.0, got {self.confidence}")


class CognitiveLearningGovernance:
    """Governs cognitive learning operations.

    This component provides:
    - Learning constraint enforcement
    - Learning phase management
    - Safety and ethical boundaries
    - Learning rate governance
    - Governance decision making
    """

    def __init__(self) -> None:
        self._lock: threading.Lock = threading.Lock()
        self._constraints: dict[str, LearningConstraint] = {}
        self._current_phase: LearningPhase = LearningPhase.EXPLORATION
        self._governance_decisions: dict[str, GovernanceDecision] = []
        self._total_decisions: int = 0

    def add_constraint(
        self,
        constraint_id: str,
        description: str,
        constraint_type: str,
        severity: float,
        threshold: float,
        is_hard: bool = False,
    ) -> LearningConstraint:
        """Add a learning constraint.

        Args:
            constraint_id: Unique identifier for this constraint
            description: Human-readable description
            constraint_type: Type of constraint (safety, ethical, performance)
            severity: Severity of constraint (0.0-1.0)
            threshold: Threshold value for constraint
            is_hard: Whether this is a hard constraint (must be satisfied)

        Returns:
            LearningConstraint that was added
        """
        constraint = LearningConstraint(
            constraint_id=constraint_id,
            description=description,
            constraint_type=constraint_type,
            severity=severity,
            threshold=threshold,
            is_hard=is_hard,
        )

        with self._lock:
            self._constraints[constraint_id] = constraint

        _logger.info(
            "Added learning constraint %s: type=%s, severity=%.2f, hard=%s",
            constraint_id,
            constraint_type,
            severity,
            is_hard,
        )

        return constraint

    def evaluate_learning_action(
        self,
        action: str,
        parameters: Mapping[str, float],
        context: Mapping[str, str],
    ) -> GovernanceDecision:
        """Evaluate whether to allow a learning action.

        Args:
            action: Learning action to evaluate
            parameters: Action parameters
            context: Additional context

        Returns:
            GovernanceDecision with action to take
        """
        decision_id = f"decision_{self._total_decisions}_{self._get_timestamp()}"
        violated_constraints: list[str] = []

        # Check against all constraints
        for constraint_id, constraint in self._constraints.items():
            if self._check_constraint_violation(constraint, parameters):
                violated_constraints.append(constraint_id)

        # Determine action based on violations
        if violated_constraints:
            # Check if any hard constraints are violated
            hard_violations = [
                c_id
                for c_id in violated_constraints
                if self._constraints[c_id].is_hard
            ]

            if hard_violations:
                action_decision = GovernanceAction.BLOCK
                reasoning = f"Hard constraints violated: {', '.join(hard_violations)}"
            else:
                action_decision = GovernanceAction.MODIFY
                reasoning = f"Soft constraints violated: {', '.join(violated_constraints)}"
        else:
            action_decision = GovernanceAction.ALLOW
            reasoning = "No constraints violated"

        decision = GovernanceDecision(
            decision_id=decision_id,
            action=action_decision,
            reasoning=reasoning,
            confidence=0.9,
            violated_constraints=tuple(violated_constraints),
            timestamp_ns=self._get_timestamp(),
        )

        with self._lock:
            self._governance_decisions.append(decision)
            self._total_decisions += 1

        _logger.info(
            "Governance decision %s: action=%s, %s",
            decision_id,
            action_decision,
            reasoning,
        )

        return decision

    def set_learning_phase(self, phase: LearningPhase) -> None:
        """Set the current learning phase.

        Args:
            phase: Learning phase to set
        """
        with self._lock:
            self._current_phase = phase

        _logger.info("Set learning phase to %s", phase)

    def get_learning_phase(self) -> LearningPhase:
        """Get the current learning phase.

        Returns:
            Current learning phase
        """
        with self._lock:
            return self._current_phase

    def check_learning_rate_compliance(
        self,
        learning_rate: float,
        max_allowed_rate: float = 0.1,
    ) -> bool:
        """Check if learning rate complies with governance limits.

        Args:
            learning_rate: Learning rate to check
            max_allowed_rate: Maximum allowed learning rate

        Returns:
            True if compliant, False otherwise
        """
        return learning_rate <= max_allowed_rate

    def get_statistics(self) -> dict[str, int | str]:
        """Get governance statistics."""
        with self._lock:
            return {
                "total_constraints": len(self._constraints),
                "total_decisions": self._total_decisions,
                "current_phase": self._current_phase,
            }

    # ------------------------------------------------------------------
    # Private methods
    # ------------------------------------------------------------------

    def _check_constraint_violation(
        self,
        constraint: LearningConstraint,
        parameters: Mapping[str, float],
    ) -> bool:
        """Check if a constraint is violated by parameters.

        Args:
            constraint: Constraint to check
            parameters: Parameters to check against

        Returns:
            True if violated, False otherwise
        """
        # TODO: Implement sophisticated constraint checking
        # For now, use simple threshold checking
        # Check if any parameter exceeds the constraint threshold
        for param_name, param_value in parameters.items():
            if param_value > constraint.threshold:
                return True

        return False

    def _get_timestamp(self) -> int:
        """Get current timestamp in nanoseconds."""
        # In production, this would use the system time source
        return 0  # TODO: Integrate with proper time source


# Singleton instance
_singleton: CognitiveLearningGovernance | None = None
_lock = threading.Lock()


def get_cognitive_learning_governance() -> CognitiveLearningGovernance:
    """Get the singleton cognitive learning governance instance."""
    global _singleton
    if _singleton is None:
        with _lock:
            if _singleton is None:
                _singleton = CognitiveLearningGovernance()
    return _singleton


__all__ = [
    "CognitiveLearningGovernance",
    "get_cognitive_learning_governance",
    "LearningConstraint",
    "GovernanceDecision",
    "GovernanceAction",
    "LearningPhase",
]