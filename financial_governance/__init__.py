"""
financial_governance — DEPRECATED: Use governance_unified.domains.financial instead.

DEPRECATED: This package is deprecated. All financial governance functionality
has been consolidated into the unified governance system at
``governance_unified/domains/financial/`` as part of the single governance layer.

New code should import from ``governance_unified.domains.financial`` instead.
This package is retained only for backward compatibility during the
transition period and will be removed in a future major version.

The system now has ONE unified governance system instead of the
previously fragmented approach (governance/, governance_engine/,
financial_governance/, operator_governance/).

Protections are now provided by the unified financial domain:
  1. Exposure Guard       — net exposure within declared risk budgets
  2. Leverage Monitor     — leverage bounds never exceeded
  3. Liquidation Sentinel — liquidation distance early warning
  4. Execution Hazard     — execution path hazard detection
  5. Capital Throttle     — capital deployment rate limiting
  6. Kill Switch          — financial-layer emergency halt
"""

import warnings

warnings.warn(
    "The 'financial_governance' package is deprecated. "
    "Use 'governance_unified.domains.financial' instead. "
    "This module will be removed in a future version.",
    DeprecationWarning,
    stacklevel=2,
)

# Redirect to unified governance system for backward compatibility
try:
    from governance_unified.domains import financial as financial_domain
    
    # Legacy compatibility - create a wrapper that mimics the old interface
    class FinancialGovernanceEngine:
        """Legacy compatibility wrapper for financial governance."""
        
        def __init__(self):
            # Reference the unified financial domain
            self.financial_domain = financial_domain
            self.capital_throttle = financial_domain.capital_throttle
            self.exposure_guard = financial_domain.exposure_guard
            self.leverage_monitor = financial_domain.leverage_monitor
            self.liquidation_sentinel = financial_domain.liquidation_sentinel
            self.execution_hazard = financial_domain.execution_hazard
            self.kill_switch = financial_domain.financial_kill_switch_module
    
    def get_financial_governance():
        """Legacy compatibility function."""
        return FinancialGovernanceEngine()
    
    __all__ = [
        "FinancialGovernanceEngine",
        "get_financial_governance",
    ]
except ImportError:
    # If governance_unified is not available, fall back to legacy
    from .engine import FinancialGovernanceEngine, get_financial_governance
    
    __all__ = ["FinancialGovernanceEngine", "get_financial_governance"]
