"""
core/contracts/cognitive_governance.py
DIX VISION v42.2 — Cognitive Governance contract types.

These records cross the boundary between the learning/evolution engines
and the cognitive governance control plane. Like all core.contracts
they are frozen, slotted, replay-deterministic value objects (INV-08,
INV-15). No callables, no IO.

Cognitive Governance protects four complementary integrity properties:

  1. Belief Integrity         — convictions are calibrated and causally grounded
  2. Memory Integrity         — vector stores haven't drifted or been contaminated
  3. Mutation Safety          — strategy evolution stays within reversible bounds
  4. Epistemic Honesty        — learning is grounded in external observation,
                                not synthetic feedback or reward gaming

These protections ARE the P0 safety layer during Phase 0–3 (cognitive
build-out). Capital protection (FinancialGovernance) becomes co-equal in
Phase 4+ once live execution is real.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class CognitiveViolationKind(StrEnum):
    OVERCONFIDENCE = "OVERCONFIDENCE"
    CALIBRATION_DRIFT = "CALIBRATION_DRIFT"
    MAGICAL_BELIEF_JUMP = "MAGICAL_BELIEF_JUMP"
    MEMORY_CONTAMINATION = "MEMORY_CONTAMINATION"
    EMBEDDING_COLLAPSE = "EMBEDDING_COLLAPSE"
    MUTATION_OUT_OF_BUDGET = "MUTATION_OUT_OF_BUDGET"
    MUTATION_IRREVERSIBLE = "MUTATION_IRREVERSIBLE"
    LINEAGE_GAP = "LINEAGE_GAP"
    LINEAGE_CYCLE = "LINEAGE_CYCLE"
    HALLUCINATION_LOOP = "HALLUCINATION_LOOP"
    SELF_REFERENTIAL_REWARD = "SELF_REFERENTIAL_REWARD"
    EPISTEMIC_DRIFT_WARNING = "EPISTEMIC_DRIFT_WARNING"
    EPISTEMIC_DRIFT_CRITICAL = "EPISTEMIC_DRIFT_CRITICAL"
    SYNTHETIC_FEEDBACK = "SYNTHETIC_FEEDBACK"
    REWARD_HACKING = "REWARD_HACKING"
    IDENTITY_INSTABILITY = "IDENTITY_INSTABILITY"
    CAUSAL_GHOST = "CAUSAL_GHOST"
    CAUSAL_DOMAIN_LEAK = "CAUSAL_DOMAIN_LEAK"
    LEARNING_NOT_GROUNDED = "LEARNING_NOT_GROUNDED"
    # ------------------------------------------------------------------
    # v3.7 Epistemology — beliefs must carry their own lineage
    # ------------------------------------------------------------------
    BELIEF_LINEAGE_MISSING = "BELIEF_LINEAGE_MISSING"
    BELIEF_LINEAGE_BROKEN = "BELIEF_LINEAGE_BROKEN"
    # ------------------------------------------------------------------
    # v3.7 Truth Maintenance — auto belief revision on new evidence
    # ------------------------------------------------------------------
    BELIEF_REVISION_TRIGGERED = "BELIEF_REVISION_TRIGGERED"
    # ------------------------------------------------------------------
    # v3.7 Contradiction — first-class contradiction events
    # ------------------------------------------------------------------
    BELIEF_CONTRADICTION = "BELIEF_CONTRADICTION"
    # ------------------------------------------------------------------
    # v3.7 Self-Awareness — system knows its own boundaries
    # ------------------------------------------------------------------
    SELF_AWARENESS_VIOLATION = "SELF_AWARENESS_VIOLATION"
    # ------------------------------------------------------------------
    # v3.7 Failure Intelligence — failures studied as assets
    # ------------------------------------------------------------------
    FAILURE_CLASSIFICATION_PENDING = "FAILURE_CLASSIFICATION_PENDING"
    FAILURE_REPEAT = "FAILURE_REPEAT"
    # ------------------------------------------------------------------
    # v3.7 Meta-Learning — learning about learning
    # ------------------------------------------------------------------
    META_LEARNING_SIGNAL = "META_LEARNING_SIGNAL"


class CognitiveSeverity(StrEnum):
    INFO = "INFO"
    WARNING = "WARNING"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


# ---------------------------------------------------------------------------
# v3.7 Epistemology — belief carries its own lineage
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class BeliefLineage:
    """WHY a belief exists — its complete evidence chain.

    Every belief must carry lineage. Not just value.
    """

    ts_ns: int
    belief_id: str
    domain: str
    claim: str
    confidence: float
    evidence_ids: tuple[str, ...]
    evidence_weights: tuple[float, ...]
    contributor_chain: tuple[str, ...]
    formed_at: int
    last_reinforced: int
    revision_count: int = 0


# ---------------------------------------------------------------------------
# v3.7 Contradiction — first-class contradiction events
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class ContradictionReport:
    """Paired beliefs that contradict each other."""

    ts_ns: int
    contradiction_id: str
    belief_a_id: str
    belief_b_id: str
    domain_a: str
    domain_b: str
    claim_a: str
    claim_b: str
    severity: CognitiveSeverity
    suggested_resolution: str = ""


# ---------------------------------------------------------------------------
# v3.7 Truth Maintenance — belief revision under new evidence
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class BeliefRevision:
    """Revision of an existing belief under new evidence."""

    ts_ns: int
    revision_id: str
    belief_id: str
    domain: str
    old_confidence: float
    new_confidence: float
    triggering_evidence_ids: tuple[str, ...]
    revision_reason: str
    revision_count: int


# ---------------------------------------------------------------------------
# v3.7 Failure Intelligence — failures become assets
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class FailureRecord:
    """A single failure — tracked so failures become assets."""

    ts_ns: int
    failure_id: str
    category: str
    strategy_id: str
    prediction_id: str
    root_cause: str
    severity: CognitiveSeverity = CognitiveSeverity.INFO
    resolved: bool = False
    repeat_count: int = 0


# ---------------------------------------------------------------------------
# v3.7 Meta-Learning — learning about learning
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class MetaLearningReport:
    """Reports which learning approach is performing best."""

    ts_ns: int
    lane_id: str
    approach: str
    knowledge_gain: float
    compute_cost: float
    gain_per_cost: float
    samples_processed: int


# ---------------------------------------------------------------------------
# v3.7 Self-Awareness — system knows its own boundaries
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class SelfAwarenessReport:
    """What DIXVISION knows about itself."""

    ts_ns: int
    known_capabilities: tuple[str, ...]
    known_limitations: tuple[str, ...]
    knowledge_gaps: tuple[str, ...]
    recommended_improvements: tuple[str, ...]
    confidence_in_self_model: float


# ---------------------------------------------------------------------------
# v3.7 Learning closed-loop outcome
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class LearningOutcomeReport:
    """Closed-loop outcome for a learning signal."""

    ts_ns: int
    signal_id: str
    predicted_confidence: float
    actual_outcome: float
    calibration_error: float
    was_correct: bool


# ---------------------------------------------------------------------------
# Pre-existing contracts (preserved from original)
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class BeliefIntegrityReport:
    """Result of a belief-update validation check."""

    ts_ns: int
    belief_id: str
    source: str
    passed: bool
    severity: CognitiveSeverity = CognitiveSeverity.INFO
    violations: tuple[CognitiveViolationKind, ...] = ()
    confidence_score: float = 1.0
    calibration_error: float = 0.0
    detail: str = ""


@dataclass(frozen=True, slots=True)
class MemoryContaminationReport:
    """Result of a vector-memory health scan."""

    ts_ns: int
    store_name: str
    passed: bool
    contamination_score: float
    drift_rate_per_hour: float
    anomalous_clusters: int
    severity: CognitiveSeverity = CognitiveSeverity.INFO
    violations: tuple[CognitiveViolationKind, ...] = ()
    detail: str = ""


@dataclass(frozen=True, slots=True)
class MutationValidationResult:
    """Gate result for a proposed strategy mutation."""

    ts_ns: int
    mutation_id: str
    source: str
    approved: bool
    reversible: bool = True
    scope_exceeded: bool = False
    violations: tuple[CognitiveViolationKind, ...] = ()
    detail: str = ""


@dataclass(frozen=True, slots=True)
class HallucinationReport:
    """Detected self-referential inference loop."""

    ts_ns: int
    source: str
    loop_depth: int
    self_referential: bool
    severity: CognitiveSeverity
    evidence: tuple[str, ...] = ()
    detail: str = ""


@dataclass(frozen=True, slots=True)
class EpistemicDriftReport:
    """Rolling divergence between predicted and observed outcomes."""

    ts_ns: int
    window_ns: int
    drift_score: float
    mean_absolute_error: float
    accumulated_error: float
    n_samples: int
    threshold_breached: bool = False
    severity: CognitiveSeverity = CognitiveSeverity.INFO
    detail: str = ""


@dataclass(frozen=True, slots=True)
class LearningTruthfulnessReport:
    """Ratio of externally-grounded to synthetic learning signals."""

    ts_ns: int
    window_n: int
    external_ratio: float
    synthetic_count: int
    grounded_count: int
    passed: bool
    severity: CognitiveSeverity = CognitiveSeverity.INFO
    detail: str = ""


@dataclass(frozen=True, slots=True)
class LineageValidationResult:
    """Strategy lineage chain integrity check."""

    ts_ns: int
    strategy_id: str
    chain_depth: int
    passed: bool
    violations: tuple[CognitiveViolationKind, ...] = ()
    detail: str = ""


@dataclass(frozen=True, slots=True)
class IdentityStabilityReport:
    """Archetype / behavioral fingerprint drift measurement."""

    ts_ns: int
    trader_id: str
    similarity_score: float
    drift_magnitude: float
    passed: bool
    severity: CognitiveSeverity = CognitiveSeverity.INFO
    detail: str = ""


@dataclass(frozen=True, slots=True)
class SyntheticFeedbackReport:
    """Detection of paper/simulated signals polluting live learning."""

    ts_ns: int
    source: str
    mode: str
    is_synthetic: bool
    severity: CognitiveSeverity = CognitiveSeverity.INFO
    detail: str = ""


@dataclass(frozen=True, slots=True)
class RewardHackingReport:
    """Reward-function gaming detection."""

    ts_ns: int
    strategy_id: str
    reward_trend: float
    objective_trend: float
    correlation: float
    hacking_detected: bool
    severity: CognitiveSeverity = CognitiveSeverity.INFO
    detail: str = ""


@dataclass(frozen=True, slots=True)
class CausalConsistencyReport:
    """Attribution chain causal-consistency check."""

    ts_ns: int
    decision_id: str
    passed: bool
    violations: tuple[CognitiveViolationKind, ...] = ()
    detail: str = ""


@dataclass(frozen=True, slots=True)
class CognitiveIntegrityStatus:
    """Aggregate snapshot of all cognitive-governance guards."""

    ts_ns: int
    overall_healthy: bool
    belief_integrity_ok: bool
    memory_clean: bool
    mutation_safe: bool
    no_hallucination: bool
    epistemic_current: bool
    learning_truthful: bool
    lineage_intact: bool
    identity_stable: bool
    no_synthetic_feedback: bool
    no_reward_hacking: bool
    causal_consistent: bool
    active_violations: tuple[CognitiveViolationKind, ...] = ()
    detail: str = ""


__all__ = [
    "CognitiveViolationKind",
    "CognitiveSeverity",
    "BeliefLineage",
    "ContradictionReport",
    "BeliefRevision",
    "FailureRecord",
    "MetaLearningReport",
    "SelfAwarenessReport",
    "LearningOutcomeReport",
    "BeliefIntegrityReport",
    "MemoryContaminationReport",
    "MutationValidationResult",
    "HallucinationReport",
    "EpistemicDriftReport",
    "LearningTruthfulnessReport",
    "LineageValidationResult",
    "IdentityStabilityReport",
    "SyntheticFeedbackReport",
    "RewardHackingReport",
    "CausalConsistencyReport",
    "CognitiveIntegrityStatus",
]
