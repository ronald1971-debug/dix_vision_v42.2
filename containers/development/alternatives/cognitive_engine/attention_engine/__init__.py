"""Attention Engine - allocate cognitive resources dynamically.

As DIXVISION scales (10→100→1000→5000 traders), INDIRA cannot
think equally about everything. Attention directs cognitive bandwidth.

Resources are allocated to:
- High Opportunity
- High Risk
- High Novelty
- High Uncertainty
"""

from cognitive_engine.attention_engine.attention_manager import AttentionManager
from cognitive_engine.attention_engine.focus_policy import FocusPolicy, FocusTarget
from cognitive_engine.attention_engine.priority import AttentionPriority, AttentionWeight

__all__ = [
    "AttentionManager",
    "AttentionPriority",
    "AttentionWeight",
    "FocusPolicy",
    "FocusTarget",
]