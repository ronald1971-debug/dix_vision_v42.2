"""governance_engine.hardening — Capital-grade governance hardening layer.

Seven subsystems:
  invariant_monitor   — Runtime formal + lightweight invariant proving
  replay_engine       — Deterministic full-stream replay + golden digest
  mutation_firewall   — Mutation containment (CLASS_A/B/C + trust gating)
  policy_lock         — Hard policy lock with drift detection
  isolation_boundary  — Cross-engine call authority enforcement
  trust_scorer        — Hazard-driven trust erosion + ExecutionDisposition
  execution_auditor   — Execution decision log + anomaly detection
  coordinator         — Single tick() entry point wiring all 7 subsystems
"""

from .coordinator import (
    GovernanceHardeningCoordinator,
    get_hardening_coordinator,
)
from .execution_auditor import (
    AnomalyReport,
    AuditOutcome,
    ExecutionAuditor,
    ExecutionDecision,
    get_execution_auditor,
)
from .invariant_monitor import (
    InvariantResult,
    InvariantSeverity,
    MonitorReport,
    RuntimeInvariantMonitor,
    get_invariant_monitor,
)
from .isolation_boundary import (
    AUTHORITY_EDGES,
    KNOWN_ENGINES,
    BoundaryViolation,
    RuntimeIsolationBoundary,
    get_isolation_boundary,
)
from .mutation_firewall import (
    FirewallDecision,
    FirewallVerdict,
    MutationFirewall,
    QuarantineEntry,
    get_mutation_firewall,
)
from .policy_lock import (
    LockStatus,
    PolicyLockManager,
    PolicyLockState,
    get_policy_lock_manager,
)
from .replay_engine import (
    KNOWN_STREAMS,
    BatchReplayResult,
    DeterministicReplayEngine,
    ReplayResult,
    get_replay_engine,
)
from .trust_scorer import (
    ExecutionDisposition,
    TrustRecord,
    TrustScorer,
    get_trust_scorer,
)

__all__ = [
    # coordinator
    "GovernanceHardeningCoordinator",
    "get_hardening_coordinator",
    # execution_auditor
    "AnomalyReport",
    "AuditOutcome",
    "ExecutionAuditor",
    "ExecutionDecision",
    "get_execution_auditor",
    # invariant_monitor
    "InvariantResult",
    "InvariantSeverity",
    "MonitorReport",
    "RuntimeInvariantMonitor",
    "get_invariant_monitor",
    # isolation_boundary
    "AUTHORITY_EDGES",
    "BoundaryViolation",
    "KNOWN_ENGINES",
    "RuntimeIsolationBoundary",
    "get_isolation_boundary",
    # mutation_firewall
    "FirewallDecision",
    "FirewallVerdict",
    "MutationFirewall",
    "QuarantineEntry",
    "get_mutation_firewall",
    # policy_lock
    "LockStatus",
    "PolicyLockManager",
    "PolicyLockState",
    "get_policy_lock_manager",
    # replay_engine
    "BatchReplayResult",
    "DeterministicReplayEngine",
    "KNOWN_STREAMS",
    "ReplayResult",
    "get_replay_engine",
    # trust_scorer
    "ExecutionDisposition",
    "TrustRecord",
    "TrustScorer",
    "get_trust_scorer",
]
