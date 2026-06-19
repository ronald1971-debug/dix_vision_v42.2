"""Belief Engine — Core belief state management.

Stage 10 — Belief Engine Creation

Responsible for:
- belief updates
- belief validation
- belief consistency
- belief replay
- belief snapshots
- belief versioning
- belief consensus and arbitration
- confidence fusion

This becomes the heart of DIXVISION.
"""

from core.belief_engine.arbitration import (
    ArbitrationContext,
    ArbitrationResult,
    ArbitrationRule,
    arbitrate,
)
from core.belief_engine.confidence_fusion import (
    ConfidenceSource,
    FusionMethod,
    compute_fused_confidence,
    fuse_bayesian,
    fuse_max,
    fuse_min,
    fuse_weighted,
)
from core.belief_engine.consensus import BeliefVote, ConsensusResult, compute_consensus
from core.belief_engine.consistency import check_consistency
from core.belief_engine.replay import replay_to_belief
from core.belief_engine.snapshots import BeliefSnapshotStore
from core.belief_engine.updates import BeliefUpdate
from core.belief_engine.validation import validate_belief_state
from core.belief_engine.versioning import BeliefVersion

__all__ = [
    "ArbitrationContext",
    "ArbitrationResult",
    "ArbitrationRule",
    "BeliefSnapshotStore",
    "BeliefUpdate",
    "BeliefVersion",
    "BeliefVote",
    "ConsensusResult",
    "ConfidenceSource",
    "FusionMethod",
    "arbitrate",
    "check_consistency",
    "compute_consensus",
    "compute_fused_confidence",
    "fuse_bayesian",
    "fuse_max",
    "fuse_min",
    "fuse_weighted",
    "replay_to_belief",
    "validate_belief_state",
]