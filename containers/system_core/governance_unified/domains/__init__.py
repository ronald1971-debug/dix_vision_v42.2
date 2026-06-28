"""
governance_engine.domains
Unified domain-specific governance guards for the consolidated governance engine.

This package contains all domain-specific guards migrated from the separate
governance systems:
- cognitive: Cognitive integrity and AI safety guards
- financial: Financial risk management and capital protection guards
- operator: Operator sovereignty and human-in-the-loop guards
- system: System integrity and structural consistency guards
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List


class GovernanceDomain(Enum):
    """Governance domain types"""

    COGNITIVE = "cognitive"
    FINANCIAL = "financial"
    OPERATOR = "operator"
    SYSTEM = "system"
    OPERATIONAL = "operational"


class PolicyStatus(Enum):
    """Policy status"""

    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    REVOKED = "revoked"


@dataclass
class CognitiveGovernancePolicy:
    """Cognitive governance policy data structure"""

    policy_id: str = "cognitive_default"
    domain: GovernanceDomain = GovernanceDomain.COGNITIVE
    title: str = "Cognitive Governance"
    description: str = "Default cognitive governance policy"
    constitution_principles: List[str] = field(default_factory=list)
    invariants: List[str] = field(default_factory=list)
    constraints: Dict[str, Any] = field(default_factory=dict)
    status: PolicyStatus = PolicyStatus.ACTIVE
    updated_at: int = 0

    def __post_init__(self):
        if self.updated_at == 0:
            self.updated_at = int(datetime.now().timestamp() * 1_000_000_000)


# Import domain-specific governance modules
try:
    from .cognitive import (
        BeliefIntegrityGuard,
        CausalConsistencyGuard,
        CognitiveConstitution,
        CognitiveMaturityRegistry,
        CognitivePhysicsEngine,
    )
except ImportError:
    BeliefIntegrityGuard = None
    CausalConsistencyGuard = None
    CognitiveConstitution = None
    CognitiveMaturityRegistry = None
    CognitivePhysicsEngine = None

try:
    from .financial import (
        CapitalThrottle,
        ExecutionHazardDetector,
        ExposureGuard,
        FinancialGovernanceEngine,
        KillSwitch,
        LeverageMonitor,
        LiquidationSentinel,
    )
except ImportError:
    CapitalThrottle = None
    ExecutionHazardDetector = None
    ExposureGuard = None
    KillSwitch = None
    LeverageMonitor = None
    LiquidationSentinel = None
    FinancialGovernanceEngine = None

try:
    from .operator import (
        AuthorityEscalationGuard,
        ConsentRouter,
        GovernanceVisibilityMonitor,
        ManualLockoutGuard,
        OperatorConstitution,
        OverridePriorityManager,
    )
except ImportError:
    AuthorityEscalationGuard = None
    ConsentRouter = None
    GovernanceVisibilityMonitor = None
    ManualLockoutGuard = None
    OperatorConstitution = None
    OverridePriorityManager = None

try:
    from .system import (
        ContractIntegrityGuard,
        ConvergenceMonitor,
        DependencyValidator,
        ReplayIntegrityGuard,
        RuntimeConsistencyMonitor,
        TopologyGuard,
    )
except ImportError:
    ContractIntegrityGuard = None
    TopologyGuard = None
    RuntimeConsistencyMonitor = None
    DependencyValidator = None
    ReplayIntegrityGuard = None
    ConvergenceMonitor = None

__all__ = [
    "GovernanceDomain",
    "PolicyStatus",
    "CognitiveGovernancePolicy",
    # Cognitive domain
    "BeliefIntegrityGuard",
    "CausalConsistencyGuard",
    "CognitiveConstitution",
    "CognitiveMaturityRegistry",
    "CognitivePhysicsEngine",
    # Financial domain
    "CapitalThrottle",
    "ExecutionHazardDetector",
    "ExposureGuard",
    "KillSwitch",
    "LeverageMonitor",
    "LiquidationSentinel",
    "FinancialGovernanceEngine",
    # Operator domain
    "AuthorityEscalationGuard",
    "ConsentRouter",
    "GovernanceVisibilityMonitor",
    "ManualLockoutGuard",
    "OperatorConstitution",
    "OverridePriorityManager",
    # System domain
    "ContractIntegrityGuard",
    "TopologyGuard",
    "RuntimeConsistencyMonitor",
    "DependencyValidator",
    "ReplayIntegrityGuard",
    "ConvergenceMonitor",
]
