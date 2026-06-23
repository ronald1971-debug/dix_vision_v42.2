"""
Core Contracts Cognitive Governance
Real implementation for cognitive governance contracts
"""

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List


class CognitiveState(Enum):
    """Cognitive state enumeration"""

    NORMAL = "normal"
    DEGRADED = "degraded"
    COMPROMISED = "compromised"
    RECOVERING = "recovering"
    SUSPENDED = "suspended"


class CognitiveSeverity(Enum):
    """Cognitive severity enumeration"""

    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class CognitiveViolationKind(Enum):
    """Cognitive violation kind enumeration"""

    BELIEF_DRIFT = "belief_drift"
    CONFIDENCE_DECAY = "confidence_decay"
    ANOMALY_DETECTED = "anomaly_detected"
    INCONSISTENCY = "inconsistency"
    MANIPULATION = "manipulation"
    DATA_CORRUPTION = "data_corruption"
    EPISTEMIC_DRIFT_CRITICAL = "epistemic_drift_critical"
    EPISTEMIC_DRIFT_HIGH = "epistemic_drift_high"
    EPISTEMIC_DRIFT_MEDIUM = "epistemic_drift_medium"
    EPISTEMIC_DRIFT_WARNING = "epistemic_drift_warning"
    COHERENCE_VIOLATION = "coherence_violation"
    BIAS_INJECTION = "bias_injection"
    MUTATION_IRREVERSIBLE = "mutation_irreversible"
    MUTATION_OUT_OF_BUDGET = "mutation_out_of_budget"
    HALLUCINATION_LOOP = "hallucination_loop"
    CALIBRATION_DRIFT = "calibration_drift"
    REWARD_HACKING = "reward_hacking"
    MEMORY_CONTAMINATION = "memory_contamination"
    LINEAGE_CYCLE = "lineage_cycle"
    LINEAGE_GAP = "lineage_gap"
    SELF_REFERENTIAL_REWARD = "self_referential_reward"
    SYNTHETIC_FEEDBACK = "synthetic_feedback"
    LEARNING_NOT_GROUNDED = "learning_not_grounded"
    IDENTITY_INSTABILITY = "identity_instability"
    CAUSAL_GHOST = "causal_ghost"
    CAUSAL_DOMAIN_LEAK = "causal_domain_leak"
    OVERCONFIDENCE = "overconfidence"
    MAGICAL_BELIEF_JUMP = "magical_belief_jump"
    EMBEDDING_COLLAPSE = "embedding_collapse"


class IntegrityLevel(Enum):
    """Integrity level enumeration"""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    CRITICAL = "critical"


class CognitiveGateKind(Enum):
    """Cognitive gate kind enumeration"""

    BLOCK_LEARNING = "block_learning"
    BLOCK_MUTATION = "block_mutation"
    BLOCK_SIGNAL = "block_signal"
    BLOCK_STRATEGY_SEL = "block_strategy_sel"


@dataclass
class BeliefSnapshot:
    """Snapshot of belief state"""

    snapshot_id: str
    beliefs: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class IntegrityCheck:
    """Integrity check result"""

    check_id: str
    integrity_level: IntegrityLevel
    passed: bool
    details: str = ""
    timestamp: float = field(default_factory=time.time)


@dataclass
class BeliefIntegrityReport:
    """Report on belief integrity"""

    report_id: str
    state: CognitiveState
    overall_integrity: IntegrityLevel
    checks: List[IntegrityCheck] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CausalConsistencyReport:
    """Report on causal consistency"""

    report_id: str
    consistent: bool
    violations: List[str] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EpistemicDriftReport:
    """Report on epistemic drift"""

    report_id: str
    drift_level: CognitiveSeverity
    drift_detected: bool
    metrics: Dict[str, float] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class HallucinationReport:
    """Report on hallucination detection"""

    report_id: str
    hallucinations_detected: int
    severity: CognitiveSeverity
    confidence: float = 0.0
    details: List[str] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class IdentityStabilityReport:
    """Report on identity stability"""

    report_id: str
    identity_stable: bool
    confidence: float = 0.0
    drift_metrics: Dict[str, float] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LearningTruthfulnessReport:
    """Report on learning truthfulness"""

    report_id: str
    learning_truthful: bool
    grounded: bool
    feedback_loop_detected: bool = False
    truthfulness_score: float = 0.0
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MemoryContaminationReport:
    """Report on memory contamination"""

    report_id: str
    contamination_detected: bool
    contaminated_regions: List[str] = field(default_factory=list)
    severity: CognitiveSeverity = CognitiveSeverity.LOW
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MutationValidationResult:
    """Result of mutation validation"""

    mutation_id: str
    valid: bool
    violations: List[CognitiveViolationKind] = field(default_factory=list)
    budget_compliant: bool = True
    irreversible: bool = False
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RewardHackingReport:
    """Report on reward hacking detection"""

    report_id: str
    hacking_detected: bool
    hacking_type: str = ""
    affected_components: List[str] = field(default_factory=list)
    severity: CognitiveSeverity = CognitiveSeverity.MEDIUM
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LineageValidationResult:
    """Result of lineage validation"""

    strategy_id: str
    lineage_valid: bool
    has_cycles: bool = False
    has_gaps: bool = False
    ancestors: List[str] = field(default_factory=list)
    descendants: List[str] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SyntheticFeedbackReport:
    """Report on synthetic feedback detection"""

    report_id: str
    synthetic_feedback_detected: bool
    feedback_sources: List[str] = field(default_factory=list)
    confidence: float = 0.0
    severity: CognitiveSeverity = CognitiveSeverity.MEDIUM
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)


class BeliefIntegrityGuard:
    """Guard for belief integrity"""

    def __init__(self):
        self._checks: List[IntegrityCheck] = []
        self._current_state = CognitiveState.NORMAL

    def check_integrity(self, snapshot: BeliefSnapshot) -> IntegrityCheck:
        """Check integrity of belief snapshot"""
        # Simple integrity check
        integrity_level = (
            IntegrityLevel.HIGH if snapshot.confidence > 0.8 else IntegrityLevel.MEDIUM
        )
        check = IntegrityCheck(
            check_id=f"check_{int(time.time())}",
            integrity_level=integrity_level,
            passed=integrity_level in [IntegrityLevel.HIGH, IntegrityLevel.MEDIUM],
            details=f"Confidence: {snapshot.confidence}",
        )
        self._checks.append(check)
        return check

    def get_state(self) -> CognitiveState:
        """Get current cognitive state"""
        return self._current_state

    def get_checks(self) -> List[IntegrityCheck]:
        """Get all integrity checks"""
        return self._checks


def get_belief_integrity_guard() -> BeliefIntegrityGuard:
    """Get the global belief integrity guard"""
    return BeliefIntegrityGuard()


__all__ = [
    "CognitiveState",
    "CognitiveSeverity",
    "CognitiveViolationKind",
    "CognitiveGateKind",
    "IntegrityLevel",
    "BeliefSnapshot",
    "IntegrityCheck",
    "BeliefIntegrityReport",
    "CausalConsistencyReport",
    "EpistemicDriftReport",
    "HallucinationReport",
    "IdentityStabilityReport",
    "LearningTruthfulnessReport",
    "MemoryContaminationReport",
    "MutationValidationResult",
    "RewardHackingReport",
    "LineageValidationResult",
    "SyntheticFeedbackReport",
    "BeliefIntegrityGuard",
    "get_belief_integrity_guard",
]
