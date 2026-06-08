"""RUNTIME-ENGINE-02 Execution (Phase E0 shell).

Owner of hot-path order routing, exchange/broker adapters, and
slippage/protection plugins. Strictly deterministic. Subject to lint rules
T1, B1, W1, L3.
"""

from execution_engine.engine import ExecutionEngine

# Phase 2 migration additions
from execution_engine.fast_lane import FastLane, FastLaneHandler, get_fast_lane
from execution_engine.hazard import (
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
from execution_engine.live_trading import (
    LiveTradingAuditSystem,
    LiveTradingGovernanceLayer,
    LiveTradingLedgerBackedOperations,
    LiveTradingRiskConstraints,
    get_live_trading_audit_system,
    get_live_trading_governance_layer,
    get_live_trading_ledger_backed_operations,
    get_live_trading_risk_constraints,
)
from execution_engine.offline.lane import OfflineLane, OfflineLaneHandler, get_offline_lane

__all__ = [
    "ExecutionEngine",
    # Fast lane (migrated from execution/fast_lane)
    "FastLane",
    "FastLaneHandler",
    "get_fast_lane",
    # Hazard detection (migrated from execution/hazard)
    "HazardEvent",
    "HazardSeverity",
    "HazardType",
    "get_hazard_bus",
    "get_hazard_detector",
    "get_hazard_emitter",
    "classify_response",
    "should_enter_safe_mode",
    "should_halt_trading",
    # Offline lane (migrated from execution/offline_lane)
    "OfflineLane",
    "OfflineLaneHandler",
    "get_offline_lane",
    # Live trading (Phase 14)
    "LiveTradingAuditSystem",
    "LiveTradingGovernanceLayer",
    "LiveTradingLedgerBackedOperations",
    "LiveTradingRiskConstraints",
    "get_live_trading_audit_system",
    "get_live_trading_governance_layer",
    "get_live_trading_ledger_backed_operations",
    "get_live_trading_risk_constraints",
]
