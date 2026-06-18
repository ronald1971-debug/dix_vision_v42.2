"""
execution/live_trading/__init__.py
DIX VISION v42.2 — Live Trading Infrastructure Package (Phase 14)

Live trading infrastructure with full governance, risk constraints, ledger backing,
deterministic execution, and complete auditability.

Phase 14 Components:
    - Governance approval layer (governance_layer.py)
    - Risk constraints (risk_constraints.py)
    - Ledger-backed operations (ledger_backed_operations.py)
    - Deterministic executor (deterministic_executor.py)
    - Audit system (audit_system.py)

PHASE 14 REQUIREMENTS:
    - Governance approved
    - Risk constrained
    - Ledger backed
    - Deterministic
    - Auditable

EXIT CRITERIA: Production deployment ready
"""

from .audit_system import (
    AuditEvent,
    AuditEventType,
    AuditReport,
    AuditTrail,
    LiveTradingAuditSystem,
    get_live_trading_audit_system,
)
from .deterministic_executor import (
    DeterminismCheckResult,
    DeterminismViolationType,
    DeterministicExecutionRecord,
    DeterministicLiveTradingExecutor,
    get_deterministic_live_trading_executor,
)
from .governance_layer import (
    GovernanceApprovalDecision,
    GovernanceDecisionType,
    LiveTradeGovernanceContext,
    LiveTradingGovernanceLayer,
    get_live_trading_governance_layer,
)
from .ledger_backed_operations import (
    LedgerBackedOperationResult,
    LiveOperationRecord,
    LiveOperationType,
    LiveTradingLedgerBackedOperations,
    get_live_trading_ledger_backed_operations,
)
from .risk_constraints import (
    LiveTradeRiskContext,
    LiveTradingRiskConstraints,
    RiskCheckResult,
    RiskConstraintConfig,
    RiskConstraintType,
    get_live_trading_risk_constraints,
)

__all__ = [
    # Governance approval layer
    "GovernanceApprovalDecision",
    "GovernanceDecisionType",
    "LiveTradeGovernanceContext",
    "LiveTradingGovernanceLayer",
    "get_live_trading_governance_layer",
    # Risk constraints
    "LiveTradeRiskContext",
    "LiveTradingRiskConstraints",
    "RiskCheckResult",
    "RiskConstraintConfig",
    "RiskConstraintType",
    "get_live_trading_risk_constraints",
    # Ledger-backed operations
    "LedgerBackedOperationResult",
    "LiveOperationRecord",
    "LiveOperationType",
    "LiveTradingLedgerBackedOperations",
    "get_live_trading_ledger_backed_operations",
    # Deterministic executor
    "DeterminismCheckResult",
    "DeterminismViolationType",
    "DeterministicExecutionRecord",
    "DeterministicLiveTradingExecutor",
    "get_deterministic_live_trading_executor",
    # Audit system
    "AuditEvent",
    "AuditReport",
    "AuditTrail",
    "AuditEventType",
    "LiveTradingAuditSystem",
    "get_live_trading_audit_system",
]

PHASE_14_COMPONENTS = [
    "Governance Approval Layer - governance_layer.py",
    "Risk Constraints - risk_constraints.py",
    "Ledger-Backed Operations - ledger_backed_operations.py",
    "Deterministic Executor - deterministic_executor.py",
    "Audit System - audit_system.py",
]

PHASE_14_REQUIREMENTS = [
    "Governance approved",
    "Risk constrained",
    "Ledger backed",
    "Deterministic",
    "Auditable",
]

PHASE_14_EXIT_CRITERIA = "Production deployment ready"
