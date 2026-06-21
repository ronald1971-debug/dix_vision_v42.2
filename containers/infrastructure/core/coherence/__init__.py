"""
Core Coherence
Real implementation for coherence management
"""

from .belief_state import (
    Regime,
    BeliefStatus,
    Belief,
    BeliefState,
    BeliefStateManager,
    get_belief_state_manager,
    create_belief_state,
    create_belief
)

__all__ = [
    "Regime",
    "BeliefStatus",
    "Belief",
    "BeliefState",
    "BeliefStateManager",
    "get_belief_state_manager",
    "create_belief_state",
    "create_belief"
]