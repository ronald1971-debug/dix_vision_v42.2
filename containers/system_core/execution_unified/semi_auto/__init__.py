"""execution_engine.semi_auto — Semi-automatic execution subsystem (BUILD-DIRECTIVE §8).

When a domain is in SEMI_AUTO trading mode:
- Entries below threshold go to approval queue
- Exits auto-fire (Indira protects on the way out)
- Risk reductions auto-fire
"""

from .approval_queue import ApprovalQueue
from .auto_exit_handler import AutoExitDecision, ExitReason, should_auto_exit
from .threshold_gate import ThresholdContext, ThresholdVerdict, evaluate_threshold

__all__ = [
    "ApprovalQueue",
    "ExitReason",
    "AutoExitDecision",
    "should_auto_exit",
    "ThresholdVerdict",
    "ThresholdContext",
    "evaluate_threshold",
]
