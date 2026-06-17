"""
governance_engine.domains.cognitive
Cognitive integrity and AI safety governance guards.

This module contains guards migrated from cognitive_governance/ to ensure
AI safety, cognitive integrity, and reliable cognitive processing.
"""

from __future__ import annotations

# All 18 cognitive guards migrated (100% complete)
from .belief_integrity import BeliefIntegrityGuard, get_belief_integrity_guard
from .causal_consistency import CausalConsistencyGuard, get_causal_consistency_guard
from .cognitive_constitution import CognitiveConstitution, get_cognitive_constitution
from .cognitive_maturity import CognitiveMaturityRegistry, get_cognitive_maturity_registry
from .cognitive_physics import CognitivePhysicsEngine, get_cognitive_physics
from .epistemic_drift import EpistemicDriftMonitor, get_epistemic_drift_monitor
from .hallucination_guard import HallucinationGuard, get_hallucination_guard
from .identity_stability import IdentityStabilityMonitor, get_identity_stability_monitor
from .knowledge_lifecycle import KnowledgeLifecycleManager, get_knowledge_lifecycle
from .learning_coherence import LearningCoherenceMonitor, get_learning_coherence_monitor
from .learning_truthfulness import (
    LearningTruthfulnessValidator,
    get_learning_truthfulness_validator,
)
from .long_horizon_memory import LongHorizonMemoryStore, get_long_horizon_memory
from .memory_contamination import MemoryContaminationDetector, get_memory_contamination_detector
from .mutation_validator import MutationValidator, get_mutation_validator
from .reward_hacking_detector import RewardHackingDetector, get_reward_hacking_detector
from .strategy_lineage_guard import StrategyLineageGuard, get_strategy_lineage_guard
from .synthetic_feedback_detection import SyntheticFeedbackDetector, get_synthetic_feedback_detector

__all__ = [
    "BeliefIntegrityGuard",
    "get_belief_integrity_guard",
    "CausalConsistencyGuard",
    "get_causal_consistency_guard",
    "CognitiveConstitution",
    "get_cognitive_constitution",
    "CognitiveMaturityRegistry",
    "get_cognitive_maturity_registry",
    "CognitivePhysicsEngine",
    "get_cognitive_physics",
    "EpistemicDriftMonitor",
    "get_epistemic_drift_monitor",
    "HallucinationGuard",
    "get_hallucination_guard",
    "IdentityStabilityMonitor",
    "get_identity_stability_monitor",
    "KnowledgeLifecycleManager",
    "get_knowledge_lifecycle",
    "LearningCoherenceMonitor",
    "get_learning_coherence_monitor",
    "LearningTruthfulnessValidator",
    "get_learning_truthfulness_validator",
    "LongHorizonMemoryStore",
    "get_long_horizon_memory",
    "MemoryContaminationDetector",
    "get_memory_contamination_detector",
    "MutationValidator",
    "get_mutation_validator",
    "RewardHackingDetector",
    "get_reward_hacking_detector",
    "StrategyLineageGuard",
    "get_strategy_lineage_guard",
    "SyntheticFeedbackDetector",
    "get_synthetic_feedback_detector",
]