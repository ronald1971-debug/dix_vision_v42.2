"""Hot-path execution package — Phase 2 / EXEC-11.

Modules in this package are subject to lint rule **T1** (fast-path
purity, INV-17): deterministic execution without IO or external engine dependencies.

The hot path runs every signal through a deterministic risk gate
without any IO. It is the *micro* counterpart to execution unified system.
"""

from .fast_execute import (
    FastExecutor,
    HotPathDecision,
    HotPathOutcome,
    RiskSnapshot,
)

from .fast_risk_cache import (
    FastRiskCache,
)

from .fast_structs import (
    FastStructBackend,
    FastSignal,
    FastExecution,
)

from .time_authority import (
    TimeAuthority,
)

__all__ = [
    "FastExecutor",
    "HotPathDecision", 
    "HotPathOutcome",
    "RiskSnapshot",
    "FastRiskCache",
    "FastStructBackend",
    "FastSignal",
    "FastExecution",
    "TimeAuthority",
]