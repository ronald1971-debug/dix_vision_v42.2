"""Execution lifecycle (Phase 2 / v2-C).

The lifecycle layer owns the *post-submit* world of a single order — the
deterministic state machine that an execution event traverses
between ``PROPOSED`` and ``CLOSED`` once it leaves the unified execution system.

Every module here is a pure-Python, IO-free building block consumed by
the unified execution system. No clocks, no randomness, no network — replay
determinism (INV-15) is preserved by construction.
"""

from .fill_handler import (
    FillEvent,
    FillHandler,
    OrderFillState,
)
from .order_state_machine import (
    LEGAL_ORDER_TRANSITIONS,
    OrderRecord,
    OrderState,
    OrderStateMachine,
    StateTransitionError,
)
from .partial_fill_resolver import (
    PartialFillResolution,
    PartialFillResolver,
)
from .retry_logic import (
    RetryClassification,
    RetryDecision,
    RetryPolicy,
)
from .sl_tp_manager import (
    Bracket,
    BracketTrigger,
    SLTPManager,
)

__all__ = [
    "Bracket",
    "BracketTrigger",
    "FillEvent",
    "FillHandler",
    "LEGAL_ORDER_TRANSITIONS",
    "OrderFillState",
    "OrderRecord",
    "OrderState",
    "OrderStateMachine",
    "PartialFillResolution",
    "PartialFillResolver",
    "RetryClassification",
    "RetryDecision",
    "RetryPolicy",
    "SLTPManager",
    "StateTransitionError",
]
