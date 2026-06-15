"""governance_engine -- DEPRECATED: Use governance_unified instead.

DEPRECATED: This package is deprecated. All governance functionality
has been consolidated into the single unified governance system at
``governance_unified/`` as specified in the DIX VISION system vision:
"a robust governance layer with permission-based access control"

New code should import from ``governance_unified`` instead.
This package is retained only for backward compatibility during the
transition period and will be removed in a future major version.

The system now has ONE unified governance system instead of the
previously fragmented approach (governance/, governance_engine/,
financial_governance/, operator_governance/).

Migration: Replace imports like:
  from governance_engine.engine import GovernanceEngine
With:
  from governance_unified import UnifiedGovernanceKernel
"""

import warnings

warnings.warn(
    "The 'governance_engine' package is deprecated. "
    "Use 'governance_unified' instead. "
    "This module will be removed in a future version.",
    DeprecationWarning,
    stacklevel=2,
)

# Redirect to unified governance system for backward compatibility
try:
    from governance_unified import (
        UnifiedGovernanceKernel as GovernanceEngine,
        get_unified_governance_kernel,
    )
    
    __all__ = ["GovernanceEngine", "get_unified_governance_kernel"]
except ImportError:
    # If governance_unified is not available, fall back to legacy
    from .engine import GovernanceEngine
    
    __all__ = ["GovernanceEngine"]
