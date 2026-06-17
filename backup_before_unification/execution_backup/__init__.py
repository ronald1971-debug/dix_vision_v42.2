"""execution — DEPRECATED: Use execution_unified instead.

DEPRECATED: This package is deprecated. All execution functionality
has been consolidated into the single unified execution system at
``execution_unified/`` as specified in the DIX VISION comprehensive
integration plan.

New code should import from ``execution_unified`` instead.
This package is retained only for backward compatibility during the
transition period and will be removed in a future major version.

The system now has ONE unified execution system instead of the
previously fragmented approach (execution/, execution_engine/).

Migration: Replace imports like:
  from execution.engine import DyonEngine
With:
  from execution_unified import UnifiedExecutionKernel
"""

import warnings

warnings.warn(
    "The 'execution' package is deprecated. "
    "Use 'execution_unified' instead. "
    "This module will be removed in a future version.",
    DeprecationWarning,
    stacklevel=2,
)

# Redirect to unified execution system for backward compatibility
try:
    from execution_unified import (
        UnifiedExecutionKernel as DyonEngine,
        get_unified_execution_kernel as get_dyon_engine,
    )
    
    __all__ = ["DyonEngine", "get_dyon_engine"]
except ImportError:
    # If execution_unified is not available, fall back to legacy
    from .engine import DyonEngine, get_dyon_engine
    
    __all__ = ["DyonEngine", "get_dyon_engine"]
