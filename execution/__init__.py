"""execution — Trade execution + emergency execution domain.

⚠️ DEPRECATED - This package is the pre-convergence execution layer.

The canonical execution engine lives in ``execution_engine/``. New code
should import from ``execution_engine`` instead. This package is
retained for backward compatibility and will be removed in a future
major version.

Migration:
  - execution.live_trading → execution_engine.live_trading
  - execution.protections.* → execution_engine.protections.*
  - execution.monitoring.* → execution_engine.monitoring.*
  - execution.testing.* → execution_engine.testing.*
  - execution.analysis.* → execution_engine.analysis.*

Canonical split:
  Indira (market) → ``trade_executor`` → adapters
  Hazard      → ``emergency_executor`` → mode transitions / kill switch

Dyon system maintenance lives under the same package but CANNOT touch
adapters or the trade_executor.
"""

import warnings

# Issue deprecation warning on import
warnings.warn(
    "The 'execution' package is deprecated. Please use 'execution_engine' instead. "
    "See package docstring for migration guide.",
    DeprecationWarning,
    stacklevel=2,
)

from .engine import DyonEngine, get_dyon_engine

__all__ = ["DyonEngine", "get_dyon_engine"]
