"""Operator Intent Layer - aligns engines with operator goals.

Examples:
- Improve trader modeling
- Improve execution quality
- Improve market understanding
- Reduce risk
- Research new asset classes
"""

from cognitive_engine.operator_intent.alignment import IntentAlignment
from cognitive_engine.operator_intent.intent import IntentPriority, OperatorIntent

__all__ = [
    "IntentAlignment",
    "OperatorIntent",
    "IntentPriority",
]