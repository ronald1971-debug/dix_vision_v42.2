"""governance.mode — Named mode transition helpers (wrapper around mode_manager)."""

from .degraded_mode import enter_degraded_mode, exit_degraded_mode
from .halted_mode import enter_halted_mode, validate_halted_mode
from .safe_mode import enter_safe_mode, exit_safe_mode, validate_safe_mode
from .mode_manager import FsmMode, ModeManager, OperationalMode, get_mode_manager

__all__ = [
    "ModeManager",
    "OperationalMode",
    "FsmMode",
    "get_mode_manager",
    "enter_safe_mode",
    "exit_safe_mode",
    "enter_degraded_mode",
    "exit_degraded_mode",
    "enter_halted_mode",
    "validate_halted_mode",
    "validate_safe_mode",
]
