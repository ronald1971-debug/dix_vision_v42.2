"""
operator_governance — DEPRECATED: Use governance_unified.domains.operator instead.

DEPRECATED: This package is deprecated. All operator governance functionality
has been consolidated into the unified governance system at
``governance_unified/domains/operator/`` as part of the single governance layer.

New code should import from ``governance_unified.domains.operator`` instead.
This package is retained only for backward compatibility during the
transition period and will be removed in a future major version.

The system now has ONE unified governance system instead of the
previously fragmented approach (governance/, governance_engine/,
financial_governance/, operator_governance/).

Protections are now provided by the unified operator domain:
  1. Constitutional Authority   — operator retains supreme authority at all times
  2. Override Priority          — higher-priority overrides always supersede lower
  3. Escalation Gating          — autonomy escalation requires explicit operator consent
  4. Manual Lockout             — operator can halt any subsystem at any time
  5. Consent Routing            — no autonomous action without consent record
  6. Governance Visibility      — all governance actions remain visible to operator
"""

import warnings

warnings.warn(
    "The 'operator_governance' package is deprecated. "
    "Use 'governance_unified.domains.operator' instead. "
    "This module will be removed in a future version.",
    DeprecationWarning,
    stacklevel=2,
)

# Redirect to unified governance system for backward compatibility
try:
    from governance_unified.domains import operator as operator_domain
    
    # Legacy compatibility - create a wrapper that mimics the old interface
    class OperatorGovernanceEngine:
        """Legacy compatibility wrapper for operator governance."""
        
        def __init__(self):
            # Reference the unified operator domain
            self.operator_domain = operator_domain
            self.authority_escalation = operator_domain.authority_escalation
            self.consent_router = operator_domain.consent_router
            self.governance_visibility = operator_domain.governance_visibility
            self.manual_lockout = operator_domain.manual_lockout
            self.override_priority = operator_domain.override_priority
            self.operator_constitution = operator_domain.operator_constitution
    
    def get_operator_governance():
        """Legacy compatibility function."""
        return OperatorGovernanceEngine()
    
    __all__ = [
        "OperatorGovernanceEngine",
        "get_operator_governance",
    ]
except ImportError:
    # If governance_unified is not available, fall back to legacy
    from .engine import OperatorGovernanceEngine, get_operator_governance
    
    __all__ = ["OperatorGovernanceEngine", "get_operator_governance"]
