"""
Core Coherence
Real implementation for coherence management
"""

from .belief_state import (
    Belief,
    BeliefState,
    BeliefStateManager,
    BeliefStatus,
    Regime,
    create_belief,
    create_belief_state,
    get_belief_state_manager,
)

__all__ = [
    "Regime",
    "BeliefStatus",
    "Belief",
    "BeliefState",
    "BeliefStateManager",
    "get_belief_state_manager",
    "create_belief_state",
    "create_belief",
]
