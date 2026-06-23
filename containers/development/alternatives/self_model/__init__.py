"""
self_model
DIX VISION v42.2 — Self-Model

Production-grade self-modeling capabilities including identity representation,
capability modeling, performance tracking, learning state modeling, mental state
representation, and self-awareness capabilities.
"""

from self_model.orchestrator import (
    SelfModelOrchestrator,
    SelfModelState,
    get_self_model_orchestrator,
)

__all__ = [
    "SelfModelState",
    "SelfModelOrchestrator",
    "get_self_model_orchestrator",
]
