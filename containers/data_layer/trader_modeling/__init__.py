"""
trader_modeling
DIX VISION v42.2 — Trader Modeling

Production-grade trader modeling capabilities including trader profiling,
behavior analysis, strategy detection, performance tracking, classification,
and prediction.
"""

from trader_modeling.orchestrator import (
    TraderModelingOrchestrator,
    get_trader_modeling_orchestrator,
)

__all__ = [
    "TraderModelingOrchestrator",
    "get_trader_modeling_orchestrator",
]
