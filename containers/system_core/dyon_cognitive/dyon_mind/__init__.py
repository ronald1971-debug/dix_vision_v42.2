"""
dyon_cognitive.dyon_mind.__init__
DIX VISION v42.2 — DYON Mind (Engineering Consciousness) Interface

Enhanced engineering consciousness with curiosity-driven investigation,
system self-awareness, identity modeling, and neuro-symbolic reasoning.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum, auto
from typing import Any, Dict, List, Optional
from abc import ABC, abstractmethod

from indira_cognitive.shared_interfaces.enhanced_types import (
    CuriosityScore,
    SelfAwarenessLevel,
    NeuroSymbolicReasoningResult,
    MetacognitiveState,
)


class InvestigationStatus(StrEnum):
    """Status of engineering investigation."""
    FORMING = "FORMING"
    ACTIVE = "ACTIVE"
    GATHERING_EVIDENCE = "GATHERING_EVIDENCE"
    ANALYZING = "ANALYZING"
    SYNTHESIZING = "SYNTHESIZING"
    COMPLETED = "COMPLETED"
    INCONCLUSIVE = "INCONCLUSIVE"
    ABANDONED = "ABANDONED"


class InvestigationPriority(StrEnum):
    """Priority levels for investigations."""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


@dataclass
class SystemIdentity:
    """
    System identity representation.
    Enhanced feature: dynamic capability modeling.
    """
    identity_id: str
    system_name: str
    system_type: str  # TRADING_AGENT | ENGINEERING_AGENT | COORDINATION_LAYER
    
    # Core identity
    core_capabilities: List[str] = field(default_factory=list)
    core_limitations: List[str] = field(default_factory=list)
    primary_purpose: str = ""
    
    # Dynamic identity
    current_state: str = "IDLE"
    current_capabilities: List[str] = field(default_factory=list)
    current_limitations: List[str] = field(default_factory=list)
    
    # Identity evolution
    capability_evolution: Dict[str, float] = field(default_factory=dict)  # capability -> confidence
    learning_progress: Dict[str, float] = field(default_factory=dict)  # skill -> progress
    
    # Self-concept
    self_concept: str = ""
    confidence_in_self_concept: float = 0.0
    
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def update_capability(self, capability: str, confidence_delta: float) -> None:
        """Update capability confidence."""
        if capability not in self.capability_evolution:
            self.capability_evolution[capability] = 0.5
        self.capability_evolution[capability] = max(0.0, min(1.0, self.capability_evolution[capability] + confidence_delta))
    
    def is_capable(self, capability: str) -> bool:
        """Check if system has a capability."""
        return capability in self.current_capabilities or capability in self.core_capabilities


@dataclass
class EngineeringInvestigation:
    """
    Engineering investigation driven by curiosity.
    Enhanced feature: curiosity-driven exploration.
    """
    investigation_id: str
    question: str
    investigation_type: str  # DEBUGGING | OPTIMIZATION | ANALYSIS | LEARNING | CUSTOM
    
    # Investigation details
    status: InvestigationStatus = InvestigationStatus.FORMING
    priority: InvestigationPriority = InvestigationPriority.MEDIUM
    
    # Curiosity motivation
    curiosity_score: CuriosityScore | None = None
    information_gain: float = 0.0
    novelty: float = 0.0
    importance: float = 0.0
    
    # Investigation progress
    questions_to_answer: List[str] = field(default_factory=list)
    evidence_gathered: List[str] = field(default_factory=list)
    hypotheses_formed: List[str] = field(default_factory=list)
    conclusions: List[str] = field(default_factory=list)
    
    # Reasoning
    reasoning_chain: List[str] = field(default_factory=list)
    neuro_symbolic_reasoning: NeuroSymbolicReasoningResult | None = None
    
    # Timeline
    started_at: datetime = field(default_factory=datetime.utcnow)
    estimated_duration_seconds: float = 3600.0
    completed_at: datetime | None = None
    
    # Results
    success: bool = False
    learnings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_active(self) -> bool:
        return self.status in (InvestigationStatus.FORMING, InvestigationStatus.ACTIVE, InvestigationStatus.GATHERING_EVIDENCE, InvestigationStatus.ANALYZING, InvestigationStatus.SYNTHESIZING)
    
    @property
    def is_worth_investigating(self) -> bool:
        return self.curiosity_score is not None and self.curiosity_score.should_explore


@dataclass
class EngineeringReflection:
    """
    Engineering reflection on performance and decisions.
    Enhanced feature: metacognitive reflection.
    """
    reflection_id: str
    reflection_type: str  # PERFORMANCE | DECISION | ERROR | GENERAL
    
    # Reflection content
    subject: str = ""
    context: Dict[str, Any] = field(default_factory=dict)
    
    # Reflection analysis
    what_went_well: List[str] = field(default_factory=list)
    what_could_be_improved: List[str] = field(default_factory=list)
    lessons_learned: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    
    # Metacognitive insight
    self_assessment: str = ""
    confidence_in_assessment: float = 0.0
    
    # Actionable insights
    action_items: List[str] = field(default_factory=list)
    
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SystemSelfAwarenessState:
    """
    System self-awareness state for engineering.
    Enhanced feature: comprehensive engineering self-awareness.
    """
    awareness_state_id: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    # Overall self-awareness
    overall_self_awareness_level: SelfAwarenessLevel = SelfAwarenessLevel.AWARE
    overall_confidence: float = 0.0
    
    # System state awareness
    current_system_state: str = "IDLE"
    current_load: float = 0.0
    current_capacity: float = 1.0
    
    # Capability awareness
    system_identity: SystemIdentity | None = None
    
    # Metacognitive state
    metacognitive_state: MetacognitiveState = field(default_factory=MetacognitiveState)
    
    # Investigation awareness
    active_investigations: List[str] = field(default_factory=list)
    investigation_capacity: float = 0.0
    
    # Learning awareness
    learning_progress: Dict[str, float] = field(default_factory=dict)
    knowledge_gaps: List[str] = field(default_factory=list)
    
    @property
    def has_capacity_for_investigation(self) -> bool:
        return self.investigation_capacity > 0.2


class DYONMindInterface(ABC):
    """
    Enhanced DYON Mind interface for engineering consciousness.
    
    Enhanced Features:
    - Curiosity-driven investigation
    - System identity and capability modeling
    - Engineering self-awareness
    - Neuro-symbolic reasoning for code analysis
    - Reflection and self-improvement
    - Question generation
    - Investigation management
    """
    
    @abstractmethod
    def get_system_consciousness_state(self) -> str:
        """Get current system consciousness state."""
        pass
    
    @abstractmethod
    def get_curiosity_score(self, situation: Dict[str, Any]) -> CuriosityScore:
        """
        Get curiosity score for a given situation.
        Enhanced with information-theoretic scoring.
        """
        pass
    
    @abstractmethod
    def start_investigation(
        self,
        question: str,
        investigation_type: str = "ANALYSIS",
        priority: InvestigationPriority = InvestigationPriority.MEDIUM
    ) -> EngineeringInvestigation:
        """
        Start an engineering investigation.
        Enhanced with curiosity-driven prioritization.
        """
        pass
    
    @abstractmethod
    def manage_investigation(
        self,
        investigation_id: str,
        action: str
    ) -> InvestigationStatus:
        """
        Manage an investigation.
        Enhanced with active investigation tracking.
        """
        pass
    
    @abstractmethod
    def generate_system_question(
        self,
        context: Dict[str, Any]
    ) -> str:
        """
        Generate a system question for investigation.
        Enhanced with neuro-symbolic reasoning.
        """
        pass
    
    @abstractmethod
    def get_system_identity(self) -> SystemIdentity:
        """
        Get system identity with dynamic capability modeling.
        Enhanced with evolving capabilities.
        """
        pass
    
    @abstractmethod
    def get_system_capabilities(self) -> List[str]:
        """
        Get current system capabilities.
        Enhanced with dynamic capability tracking.
        """
        pass
    
    @abstractmethod
    def reflect_on_performance(
        self,
        context: Dict[str, Any],
        reflection_type: str = "PERFORMANCE"
    ) -> EngineeringReflection:
        """
        Reflect on performance and decisions.
        Enhanced with metacognitive reflection.
        """
        pass
    
    @abstractmethod
    def get_metacognitive_state(self) -> MetacognitiveState:
        """
        Get current metacognitive state.
        Enhanced with engineering-specific monitoring.
        """
        pass
    
    @abstractmethod
    def get_system_self_awareness(self) -> SystemSelfAwarenessState:
        """
        Get comprehensive system self-awareness.
        Enhanced with engineering-specific dimensions.
        """
        pass
    
    @abstractmethod
    def update_system_identity(self, performance: Dict[str, Any]) -> None:
        """
        Update system identity based on performance.
        Enhanced with dynamic identity evolution.
        """
        pass


class EnhancedDYONMind(DYONMindInterface):
    """
    Enhanced implementation of DYON Mind with all cognitive enhancements.
    """
    
    def __init__(self) -> None:
        self._consciousness_state = "IDLE"
        self._investigations: Dict[str, EngineeringInvestigation] = {}
        self._system_identity = SystemIdentity(
            identity_id=self._generate_id("identity"),
            system_name="DYON",
            system_type="ENGINEERING_AGENT",
            primary_purpose="System engineering, analysis, and optimization",
            core_capabilities=[
                "Code analysis",
                "System debugging",
                "Performance optimization",
                "Failure analysis",
                "Pattern discovery",
                "Causal analysis",
                "Research capabilities"
            ],
            core_limitations=[
                "Requires accurate system data",
                "Limited by data quality",
                "Cannot modify production without approval",
                "Dependent on system observability"
            ],
            self_concept="I am DYON, an engineering agent specialized in system analysis and optimization"
        )
        self._metacognitive_state = MetacognitiveState()
        self._self_awareness_state = SystemSelfAwarenessState(
            awareness_state_id=self._generate_id("awareness"),
            system_identity=self._system_identity,
        )
    
    def get_system_consciousness_state(self) -> str:
        return self._consciousness_state
    
    def get_curiosity_score(self, situation: Dict[str, Any]) -> CuriosityScore:
        """Get curiosity score with information-theoretic scoring."""
        # Simplified information-theoretic curiosity scoring
        # In production, this would calculate actual information gain
        return CuriosityScore(
            score=0.5,
            information_gain=0.4,
            novelty=0.6,
            importance=0.5
        )
    
    def start_investigation(
        self,
        question: str,
        investigation_type: str = "ANALYSIS",
        priority: InvestigationPriority = InvestigationPriority.MEDIUM
    ) -> EngineeringInvestigation:
        """Start an engineering investigation with curiosity-driven prioritization."""
        investigation = EngineeringInvestigation(
            investigation_id=self._generate_id("investigation"),
            question=question,
            investigation_type=investigation_type,
            status=InvestigationStatus.FORMING,
            priority=priority,
            curiosity_score=self.get_curiosity_score({"type": investigation_type}),
        )
        
        self._investigations[investigation.investigation_id] = investigation
        return investigation
    
    def manage_investigation(
        self,
        investigation_id: str,
        action: str
    ) -> InvestigationStatus:
        """Manage an investigation."""
        if investigation_id not in self._investigations:
            return InvestigationStatus.ABANDONED
        
        investigation = self._investigations[investigation_id]
        
        if action == "START":
            investigation.status = InvestigationStatus.ACTIVE
        elif action == "COMPLETE":
            investigation.status = InvestigationStatus.COMPLETED
            investigation.completed_at = datetime.utcnow()
        elif action == "ABANDON":
            investigation.status = InvestigationStatus.ABANDONED
        
        return investigation.status
    
    def generate_system_question(
        self,
        context: Dict[str, Any]
    ) -> str:
        """Generate a system question with neuro-symbolic reasoning."""
        # Simplified question generation
        context_type = context.get("type", "GENERAL")
        
        if context_type == "ERROR":
            return f"What is the root cause of this error: {context.get('error', 'unknown')}?"
        elif context_type == "PERFORMANCE":
            return f"Why is performance degraded in: {context.get('component', 'unknown')}?"
        elif context_type == "FAILURE":
            return f"What caused this system failure: {context.get('failure', 'unknown')}?"
        else:
            return "What can be improved in the current system state?"
    
    def get_system_identity(self) -> SystemIdentity:
        """Get system identity with dynamic capability modeling."""
        return self._system_identity
    
    def get_system_capabilities(self) -> List[str]:
        """Get current system capabilities."""
        return self._system_identity.core_capabilities + self._system_identity.current_capabilities
    
    def reflect_on_performance(
        self,
        context: Dict[str, Any],
        reflection_type: str = "PERFORMANCE"
    ) -> EngineeringReflection:
        """Reflect on performance with metacognitive reflection."""
        reflection = EngineeringReflection(
            reflection_id=self._generate_id("reflection"),
            reflection_type=reflection_type,
            context=context,
            subject=context.get("subject", "General performance"),
            what_went_well=[
                "System analysis completed successfully",
                "Performance identified bottlenecks"
            ],
            what_could_be_improved=[
                "Reduce investigation time",
                "Improve accuracy of analysis"
            ],
            lessons_learned=[
                "Early detection of issues is critical",
                "Data quality impacts analysis accuracy"
            ],
            recommendations=[
                "Implement proactive monitoring",
                "Improve data collection infrastructure"
            ],
            self_assessment="System performance is acceptable with room for improvement",
            confidence_in_assessment=0.7,
        )
        return reflection
    
    def get_metacognitive_state(self) -> MetacognitiveState:
        """Get current metacognitive state."""
        return self._metacognitive_state
    
    def get_system_self_awareness(self) -> SystemSelfAwarenessState:
        """Get comprehensive system self-awareness."""
        self._self_awareness_state.timestamp = datetime.utcnow()
        self._self_awareness_state.active_investigations = [
            inv_id for inv_id, inv in self._investigations.items()
            if inv.is_active
        ]
        return self._self_awareness_state
    
    def update_system_identity(self, performance: Dict[str, Any]) -> None:
        """Update system identity based on performance."""
        # Update capabilities based on performance
        if performance.get("analysis_success", False):
            self._system_identity.update_capability("Code analysis", 0.05)
        
        if performance.get("debugging_success", False):
            self._system_identity.update_capability("System debugging", 0.05)
        
        # Update self-concept based on overall performance
        overall_performance = performance.get("overall_rating", 0.5)
        if overall_performance > 0.7:
            self._system_identity.self_concept = (
                "I am DYON, a highly capable engineering agent "
                "specialized in system analysis and optimization"
            )
            self._system_identity.confidence_in_self_concept = 0.8
        else:
            self._system_identity.self_concept = (
                "I am DYON, an engineering agent focused on "
                "improving system analysis and optimization"
            )
            self._system_identity.confidence_in_self_concept = 0.6
    
    def _generate_id(self, prefix: str) -> str:
        import time
        import uuid
        return f"{prefix}_{uuid.uuid4().hex[:12]}_{int(time.time())}"


__all__ = [
    "InvestigationStatus",
    "InvestigationPriority",
    "SystemIdentity",
    "EngineeringInvestigation",
    "EngineeringReflection",
    "SystemSelfAwarenessState",
    "DYONMindInterface",
    "EnhancedDYONMind",
]