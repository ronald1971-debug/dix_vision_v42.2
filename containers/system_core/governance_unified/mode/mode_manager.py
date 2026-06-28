"""governance_unified.mode.mode_manager — Re-export of the canonical ModeManager.

This module re-exports all public names from governance_unified.mode_manager
so both import paths work identically.
"""

from __future__ import annotations

from governance_unified.mode_manager import (
    FsmMode,
    ModeManager,
    OperationalMode,
    get_mode_manager,
)

__all__ = [
    "ModeManager",
    "OperationalMode",
    "FsmMode",
    "get_mode_manager",
]
