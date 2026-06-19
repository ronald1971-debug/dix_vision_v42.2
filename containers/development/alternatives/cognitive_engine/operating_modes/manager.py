"""Mode Manager - manages cognitive operating modes."""

from __future__ import annotations

import time

from cognitive_engine.operating_modes.modes import ModeTransition, OperatingMode


class ModeManager:
    """Manages INDIRA's cognitive operating modes.

    Mode determines system behavior:
    - Research: Exploring new strategies, no live signals
    - Learning: Model updates, cautious execution
    - Simulation: Running scenarios, no live signals
    - Discovery: Finding patterns, logging only
    - Validation: Testing hypotheses, limited execution
    - Execution: Full signal processing and trading
    """

    def __init__(self, initial_mode: OperatingMode = OperatingMode.SHADOW) -> None:
        self._current_mode = initial_mode
        self._transitions: list[ModeTransition] = []
        self._mode_constraints: dict[OperatingMode, set[str]] = {
            OperatingMode.RESEARCH: {"no_live_signals"},
            OperatingMode.LEARNING: {"cautious_execution"},
            OperatingMode.SIMULATION: {"no_live_signals"},
            OperatingMode.DISCOVERY: {"logging_only"},
            OperatingMode.VALIDATION: {"limited_execution"},
            OperatingMode.FROZEN: {"no_execution"},
        }

    def current_mode(self) -> OperatingMode:
        """Get current operating mode."""
        return self._current_mode

    def transition_to(self, mode: OperatingMode, reason: str, approved_by: str = "") -> ModeTransition:
        """Transition to a new mode."""
        transition = ModeTransition(
            from_mode=self._current_mode,
            to_mode=mode,
            reason=reason,
            approved_by=approved_by,
        )
        self._current_mode = mode
        self._transitions.append(transition)
        return transition

    def can_execute(self) -> bool:
        """Check if system can execute trades."""
        constraints = self._mode_constraints.get(self._current_mode, set())
        return "no_execution" not in constraints and "limited_execution" not in constraints

    def can_emit_signals(self) -> bool:
        """Check if system can emit signals."""
        constraints = self._mode_constraints.get(self._current_mode, set())
        return "no_live_signals" not in constraints

    def get_constraints(self) -> set[str]:
        """Get current mode constraints."""
        return self._mode_constraints.get(self._current_mode, set()).copy()

    def add_constraint(self, constraint: str) -> None:
        """Add a constraint for current mode."""
        current_constraints = self._mode_constraints.get(self._current_mode, set())
        self._mode_constraints[self._current_mode] = (*current_constraints, constraint)

    def transition_history(self, limit: int = 50) -> list[ModeTransition]:
        """Get mode transition history."""
        return self._transitions[-limit:]

    def time_in_mode(self) -> int:
        """Get time spent in current mode (seconds)."""
        if not self._transitions:
            return 0
        last_transition = self._transitions[-1]
        current_time = time.time_ns()
        return int((current_time - last_transition.transitioned_at) / 1e9)