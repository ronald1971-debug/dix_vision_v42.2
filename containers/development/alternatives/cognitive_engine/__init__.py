"""Cognitive Engine - advanced reasoning capabilities for DIXVISION.

Stage 14+ — Cognitive Systems Implementation

Provides:
- uncertainty_engine: Track known, known unknown, unknown unknown
- attention_engine: Allocate cognitive resources dynamically
- curiosity_engine: Generate investigative questions
- hypothesis_engine: Hypothesis lifecycle management
- knowledge_graph: Connected understanding graph
- cognitive_simulator: Scenario reasoning
- narrative_engine: Market narrative tracking
- cognitive_health: Monitor cognitive failures
- identity_layer: System self-model
- operating_modes: Cognitive operating modes
- knowledge_preservation: Prevent knowledge loss
- operator_intent: Align with operator goals
- meta_governance: Observable governance
- cognitive_maturity: Measure understanding levels
"""

from cognitive_engine.attention_engine.attention_manager import AttentionManager
from cognitive_engine.attention_engine.focus_policy import FocusPolicy, FocusTarget
from cognitive_engine.attention_engine.priority import AttentionPriority, AttentionWeight
from cognitive_engine.cognitive_health.drift_detector import DriftDetector, DriftEvent, DriftType
from cognitive_engine.cognitive_health.health_report import HealthReport, HealthStatus
from cognitive_engine.cognitive_health.monitor import CognitiveHealthMonitor
from cognitive_engine.cognitive_simulator.engine import CognitiveSimulator
from cognitive_engine.cognitive_simulator.result import RiskLevel, SimulationResult
from cognitive_engine.cognitive_simulator.scenario import Scenario, ScenarioType
from cognitive_engine.curiosity_engine.curiosity_scorer import CuriosityScore, CuriosityScorer
from cognitive_engine.curiosity_engine.investigation import Investigation, InvestigationManager
from cognitive_engine.curiosity_engine.question_generator import Question, QuestionGenerator
from cognitive_engine.hypothesis_engine.hypothesis import (
    Hypothesis,
    HypothesisResult,
    HypothesisStatus,
)
from cognitive_engine.hypothesis_engine.hypothesis_tracker import HypothesisTracker
from cognitive_engine.hypothesis_engine.test_runner import TestRunner
from cognitive_engine.identity_layer.capabilities import Capability, CapabilityStatus
from cognitive_engine.identity_layer.identity import Identity
from cognitive_engine.identity_layer.maturity import MaturityAssessment, MaturityLevel
from cognitive_engine.knowledge_graph.edge import EdgeType, KnowledgeEdge
from cognitive_engine.knowledge_graph.graph import KnowledgeGraph
from cognitive_engine.knowledge_graph.node import KnowledgeNode, NodeType
from cognitive_engine.knowledge_preservation.archive import KnowledgeArchive
from cognitive_engine.knowledge_preservation.preservation import KnowledgePreserver
from cognitive_engine.knowledge_preservation.snapshot import KnowledgeSnapshot
from cognitive_engine.maturity_model.levels import DomainMaturity, MaturityDomain
from cognitive_engine.maturity_model.model import CognitiveMaturityModel
from cognitive_engine.maturity_model.report import MaturityReport
from cognitive_engine.meta_governance.meta_governance import GovernanceQuestion, MetaGovernance
from cognitive_engine.meta_governance.rules import GovernanceRule, RuleType
from cognitive_engine.narrative_engine.engine import NarrativeEngine
from cognitive_engine.narrative_engine.narrative import Narrative, NarrativeStage
from cognitive_engine.operating_modes.manager import ModeManager
from cognitive_engine.operating_modes.modes import ModeTransition, OperatingMode
from cognitive_engine.operator_intent.alignment import IntentAlignment
from cognitive_engine.operator_intent.intent import IntentPriority, OperatorIntent
from cognitive_engine.uncertainty_engine.blindspot_detector import BlindspotDetector
from cognitive_engine.uncertainty_engine.confidence_calibrator import ConfidenceCalibrator
from cognitive_engine.uncertainty_engine.uncertainty_tracker import (
    KnowledgeState,
    KnowledgeType,
    UncertaintyTracker,
)

__all__ = [
    "AttentionManager",
    "AttentionPriority",
    "AttentionWeight",
    "BlindspotDetector",
    "Capability",
    "CapabilityStatus",
    "CognitiveHealthMonitor",
    "CognitiveMaturityModel",
    "CognitiveSimulator",
    "ConfidenceCalibrator",
    "CuriosityScorer",
    "CuriosityScore",
    "DomainMaturity",
    "DriftDetector",
    "DriftEvent",
    "DriftType",
    "EdgeType",
    "FocusPolicy",
    "FocusTarget",
    "GovernanceQuestion",
    "GovernanceRule",
    "HealthReport",
    "HealthStatus",
    "Hypothesis",
    "HypothesisResult",
    "HypothesisStatus",
    "HypothesisTracker",
    "Identity",
    "IntentAlignment",
    "IntentPriority",
    "Investigation",
    "InvestigationManager",
    "KnowledgeArchive",
    "KnowledgeGraph",
    "KnowledgeNode",
    "KnowledgePreserver",
    "KnowledgeSnapshot",
    "KnowledgeState",
    "KnowledgeType",
    "MaturityAssessment",
    "MaturityDomain",
    "MaturityLevel",
    "MaturityReport",
    "ModeManager",
    "ModeTransition",
    "Narrative",
    "NarrativeEngine",
    "NarrativeStage",
    "NodeType",
    "OperatingMode",
    "OperatorIntent",
    "Question",
    "QuestionGenerator",
    "RiskLevel",
    "RuleType",
    "Scenario",
    "ScenarioType",
    "SimulationResult",
    "TestRunner",
    "UncertaintyTracker",
]