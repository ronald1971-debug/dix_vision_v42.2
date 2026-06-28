"""
indira_cognitive.shared_interfaces.enhanced_types
DIX VISION v42.2 — Enhanced Cognitive Types

Shared type definitions for enhanced cognitive architecture including:
- Attention types
- Metacognitive states
- Confidence levels
- Neuro-symbolic reasoning modes
- Curiosity scores
- Self-awareness levels
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Dict, List


class AttentionType(StrEnum):
    """Types of attention systems."""

    SINGLE = "single"
    MULTI_HEAD = "multi_head"
    ADAPTIVE = "adaptive"
    HIERARCHICAL = "hierarchical"
    CROSS_MODAL = "cross_modal"


class ConfidenceLevel(StrEnum):
    """Levels of confidence."""

    NONE = "none"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"


class NeuroSymbolicReasoningMode(StrEnum):
    """Modes of neuro-symbolic reasoning."""

    NEURAL_ONLY = "neural_only"
    SYMBOLIC_ONLY = "symbolic_only"
    HYBRID_NEURAL_FIRST = "hybrid_neural_first"
    HYBRID_SYMBOLIC_FIRST = "hybrid_symbolic_first"
    INTEGRATED = "integrated"
    CHAIN_OF_THOUGHT = "chain_of_thought"
    TREE_OF_THOUGHT = "tree_of_thought"


class SelfAwarenessLevel(StrEnum):
    """Levels of self-awareness."""

    AWARE = "aware"
    LEARNING = "learning"
    COMPETENT = "competent"
    CONFIDENT = "confident"
    EXPERT = "expert"


@dataclass
class MetacognitiveState:
    """
    Metacognitive state for monitoring own cognitive processes.
    Enhanced feature: self-explanation, confidence calibration, performance monitoring.
    """

    current_task: str = ""
    current_confidence: float = 0.0
    current_uncertainty: float = 1.0
    self_explanation: str = ""
    calibration_error: float = 0.0
    performance_rating: float = 0.0
    cognitive_load: float = 0.0
    is_monitoring: bool = True

    @property
    def confidence_level(self) -> ConfidenceLevel:
        if self.current_confidence >= 0.8:
            return ConfidenceLevel.VERY_HIGH
        if self.current_confidence >= 0.6:
            return ConfidenceLevel.HIGH
        if self.current_confidence >= 0.4:
            return ConfidenceLevel.MODERATE
        if self.current_confidence >= 0.2:
            return ConfidenceLevel.LOW
        return ConfidenceLevel.NONE


@dataclass
class CuriosityScore:
    """
    Information-theoretic curiosity score for exploration.
    Enhanced feature: curiosity-driven exploration.
    """

    score: float
    information_gain: float
    novelty: float
    importance: float
    exploration_value: float = 0.0

    def __post_init__(self):
        # Calculate overall exploration value
        self.exploration_value = (
            0.4 * self.information_gain + 0.3 * self.novelty + 0.3 * self.importance
        )

    @property
    def should_explore(self, threshold: float = 0.5) -> bool:
        return self.exploration_value > threshold


@dataclass
class NeuroSymbolicReasoningResult:
    """
    Result of neuro-symbolic reasoning.
    Enhanced feature: LLM + knowledge graph integration.
    """

    neural_reasoning: str
    symbolic_reasoning: str
    integrated_reasoning: str
    confidence: float
    reasoning_chain: List[str] = field(default_factory=list)
    knowledge_graph_nodes: List[str] = field(default_factory=list)
    knowledge_graph_edges: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_confident(self) -> bool:
        return self.confidence >= 0.6

    @property
    def reasoning_mode(self) -> NeuroSymbolicReasoningMode:
        if self.neural_reasoning and not self.symbolic_reasoning:
            return NeuroSymbolicReasoningMode.NEURAL_ONLY
        if self.symbolic_reasoning and not self.neural_reasoning:
            return NeuroSymbolicReasoningMode.SYMBOLIC_ONLY
        if self.neural_reasoning and self.symbolic_reasoning:
            return NeuroSymbolicReasoningMode.INTEGRATED
        return NeuroSymbolicReasoningMode.NEURAL_ONLY


@dataclass
class AdvancedAttentionAllocation:
    """
    Advanced attention allocation with multi-head, adaptive, and hierarchical capabilities.
    Enhanced feature: advanced attention systems.
    """

    target_id: str
    attention_score: float
    attention_type: AttentionType
    priority: float
    time_allocation_ms: float
    context_window: List[str] = field(default_factory=list)

    @property
    def is_high_priority(self) -> bool:
        return self.priority > 0.7


@dataclass
class MemoryRetrievalResult:
    """
    Result from unified memory framework retrieval.
    Enhanced feature: vector-first memory with semantic search.
    """

    memory_id: str
    content: str
    memory_type: str  # semantic | episodic | procedural | working
    relevance_score: float
    vector_similarity: float
    temporal_score: float
    combined_score: float
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_relevant(self, threshold: float = 0.7) -> bool:
        return self.combined_score > threshold


@dataclass
class ACLMessage:
    """
    Agent Communication Language (ACL) message for cross-agent communication.
    Enhanced feature: advanced multi-agent coordination.
    """

    message_id: str
    sender_id: str
    receiver_id: str
    performative: str  # INFORM | REQUEST | QUERY | PROPOSE | ACCEPT | REJECT
    content: str
    ontology: str = "default"
    reply_to: str = ""
    reply_by: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def create_reply(self, reply_content: str, performative: str = "INFORM") -> "ACLMessage":
        return ACLMessage(
            message_id=self._generate_id("acl"),
            sender_id=self.receiver_id,
            receiver_id=self.sender_id,
            performative=performative,
            content=reply_content,
            reply_to=self.message_id,
            ontology=self.ontology,
        )

    def _generate_id(self, prefix: str) -> str:
        import time
        import uuid

        return f"{prefix}_{uuid.uuid4().hex[:12]}_{int(time.time())}"


@dataclass
class ConflictResolutionProposal:
    """
    Proposal for resolving cross-agent conflicts.
    Enhanced feature: advanced conflict resolution with negotiation.
    """

    proposal_id: str
    conflict_id: str
    proposing_agent_id: str
    resolution_type: str  # COOPERATE | COMPETE | COMPROMISE | DEFER
    proposed_solution: str
    confidence: float
    utility_score: float
    alternatives: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_high_confidence(self) -> bool:
        return self.confidence > 0.7

    @property
    def is_high_utility(self) -> bool:
        return self.utility_score > 0.7


@dataclass
class SharedMentalModel:
    """
    Shared mental model for cross-agent alignment.
    Enhanced feature: shared mental models with metacognitive alignment.
    """

    model_id: str
    model_type: str
    model_version: str
    beliefs: Dict[str, Any]
    goals: List[str]
    constraints: List[str]
    alignment_score: float
    last_updated: str
    agent_access: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_aligned(self, threshold: float = 0.7) -> bool:
        return self.alignment_score > threshold


__all__ = [
    "AttentionType",
    "ConfidenceLevel",
    "NeuroSymbolicReasoningMode",
    "SelfAwarenessLevel",
    "MetacognitiveState",
    "CuriosityScore",
    "NeuroSymbolicReasoningResult",
    "AdvancedAttentionAllocation",
    "MemoryRetrievalResult",
    "ACLMessage",
    "ConflictResolutionProposal",
    "SharedMentalModel",
]
