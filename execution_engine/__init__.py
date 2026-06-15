"""execution_engine — DEPRECATED: Use execution_unified instead.

DEPRECATED: This package is deprecated. All execution functionality
has been consolidated into the single unified execution system at
``execution_unified/`` as specified in the DIX VISION comprehensive
integration plan.

New code should import from ``execution_unified`` instead.
This package is retained only for backward compatibility during the
transition period and will be removed in a future major version.

The system now has ONE unified execution system instead of the
previously fragmented approach (execution/, execution_engine/).
"""

import warnings

warnings.warn(
    "The 'execution_engine' package is deprecated. "
    "Use 'execution_unified' instead. "
    "This module will be removed in a future version.",
    DeprecationWarning,
    stacklevel=2,
)

# Redirect to unified execution system for backward compatibility
try:
    from execution_unified import (
        UnifiedExecutionKernel as ExecutionEngine,
        get_unified_execution_kernel,
    )
    
    # For now, maintain the comprehensive export list for compatibility
    # These will be gradually migrated to the unified system
    try:
        from .fast_lane import FastLane, FastLaneHandler, get_fast_lane
    except ImportError:
        FastLane = FastLaneHandler = get_fast_lane = None
    
    try:
        from .hazard import (
            HazardEvent,
            HazardSeverity,
            HazardType,
            classify_response,
            get_hazard_bus,
            get_hazard_detector,
            get_hazard_emitter,
            should_enter_safe_mode,
            should_halt_trading,
        )
    except ImportError:
        HazardEvent = HazardSeverity = HazardType = None
        classify_response = get_hazard_bus = get_hazard_detector = None
        get_hazard_emitter = should_enter_safe_mode = should_halt_trading = None
    
    try:
        from .live_trading import (
            LiveTradingAuditSystem,
            LiveTradingGovernanceLayer,
            LiveTradingLedgerBackedOperations,
            LiveTradingRiskConstraints,
            get_live_trading_audit_system,
            get_live_trading_governance_layer,
            get_live_trading_ledger_backed_operations,
            get_live_trading_risk_constraints,
        )
    except ImportError:
        LiveTradingAuditSystem = LiveTradingGovernanceLayer = None
        LiveTradingLedgerBackedOperations = LiveTradingRiskConstraints = None
        get_live_trading_audit_system = get_live_trading_governance_layer = None
        get_live_trading_ledger_backed_operations = get_live_trading_risk_constraints = None
    
    try:
        from .offline.lane import OfflineLane, OfflineLaneHandler, get_offline_lane
    except ImportError:
        OfflineLane = OfflineLaneHandler = get_offline_lane = None
    
    __all__ = [
        "ExecutionEngine",
        "get_unified_execution_kernel",
        # Components that may not be available in unified system yet
        "FastLane",
        "FastLaneHandler",
        "get_fast_lane",
        "HazardEvent",
        "HazardSeverity",
        "HazardType",
        "get_hazard_bus",
        "get_hazard_detector",
        "get_hazard_emitter",
        "classify_response",
        "should_enter_safe_mode",
        "should_halt_trading",
        "OfflineLane",
        "OfflineLaneHandler",
        "get_offline_lane",
        "LiveTradingAuditSystem",
        "LiveTradingGovernanceLayer",
        "LiveTradingLedgerBackedOperations",
        "LiveTradingRiskConstraints",
        "get_live_trading_audit_system",
        "get_live_trading_governance_layer",
        "get_live_trading_ledger_backed_operations",
        "get_live_trading_risk_constraints",
    ]
except ImportError:
    # If execution_unified is not available, fall back to legacy
    from .engine import ExecutionEngine
    
    from .fast_lane import FastLane, FastLaneHandler, get_fast_lane
    from .hazard import (
        HazardEvent,
        HazardSeverity,
        HazardType,
        classify_response,
        get_hazard_bus,
        get_hazard_detector,
        get_hazard_emitter,
        should_enter_safe_mode,
        should_halt_trading,
    )
    from .live_trading import (
        LiveTradingAuditSystem,
        LiveTradingGovernanceLayer,
        LiveTradingLedgerBackedOperations,
        LiveTradingRiskConstraints,
        get_live_trading_audit_system,
        get_live_trading_governance_layer,
        get_live_trading_ledger_backed_operations,
        get_live_trading_risk_constraints,
    )
    from .offline.lane import OfflineLane, OfflineLaneHandler, get_offline_lane
    
    __all__ = [
        "ExecutionEngine",
        "FastLane",
        "FastLaneHandler",
        "get_fast_lane",
        "HazardEvent",
        "HazardSeverity",
        "HazardType",
        "get_hazard_bus",
        "get_hazard_detector",
        "get_hazard_emitter",
        "classify_response",
        "should_enter_safe_mode",
        "should_halt_trading",
        "OfflineLane",
        "OfflineLaneHandler",
        "get_offline_lane",
        "LiveTradingAuditSystem",
        "LiveTradingGovernanceLayer",
        "LiveTradingLedgerBackedOperations",
        "LiveTradingRiskConstraints",
        "get_live_trading_audit_system",
        "get_live_trading_governance_layer",
        "get_live_trading_ledger_backed_operations",
        "get_live_trading_risk_constraints",
    ]
