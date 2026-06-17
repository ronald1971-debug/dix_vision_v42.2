"""Cognitive OS Integration.

Integration layer for connecting all components into the unified architecture.
"""

from .advanced_ai_integration import (
    AdvancedAIIntegration,
    get_advanced_ai_integration,
)
from .complete_system_integration import (
    CompleteSystemIntegration,
    get_complete_system_integration,
)

__all__ = [
    "AdvancedAIIntegration",
    "get_advanced_ai_integration",
    "CompleteSystemIntegration",
    "get_complete_system_integration",
]
