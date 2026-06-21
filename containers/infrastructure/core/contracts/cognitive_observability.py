"""
Core Contracts Cognitive Observability
Real implementation for cognitive observability tracking
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, List, Optional
import time

# Predefined observability streams
DYON_SYSTEM_STREAM = "dyon_system_stream"
DYON_DECISION_STREAM = "dyon_decision_stream"
DYON_REASONING_STREAM = "dyon_reasoning_stream"
DYON_EXPLORATION_STREAM = "dyon_exploration_stream"
DYON_LEARNING_STREAM = "dyon_learning_stream"
DYON_ADAPTATION_STREAM = "dyon_adaptation_stream"

class CognitiveState(Enum):
    """Cognitive state enumeration"""
    NORMAL = "normal"
    UNCERTAIN = "uncertain"
    CONFUSED = "confused"
    UNCERTAINLY = "uncertainly"
    CONFIDENT = "confident"
    EXPLORATORY = "exploratory"
    ANALYZING = "analyzing"
    SYNTHESIZING = "synthesizing"
    DECIDING = "deciding"
    ACTING = "acting"

class ObservabilityLevel(Enum):
    """Observability level enumeration"""
    NONE = "none"
    BASIC = "basic"
    DETAILED = "detailed"
    COMPREHENSIVE = "comprehensive"
    DEBUG = "debug"

class CognitiveEventKind(Enum):
    """Cognitive event kind enumeration"""
    REASONING_START = "reasoning_start"
    REASONING_STEP = "reasoning_step"
    REASONING_COMPLETE = "reasoning_complete"
    DECISION_MADE = "decision_made"
    DECITION_DEFERRED = "decision_deferred"
    ASSUMPTION_MADE = "assumption_made"
    UNCERTAINTY_DETECTED = "uncertainty_detected"
    EXPLORATION_START = "exploration_start"
    EXPLORATION_COMPLETE = "exploration_complete"
    LEARNING_EVENT = "learning_event"
    ADAPTATION_EVENT = "adaptation_event"
    ARCHITECTURAL_DRIFT = "architectural_drift"
    COGNITIVE_DRIFT = "cognitive_drift"
    SYSTEM_STATE_CHANGE = "system_state_change"

class DependencyAnomalyKind(Enum):
    """Dependency anomaly kind enumeration"""
    CYCLICAL_DEPENDENCY = "cyclic_dependency"
    MISSING_DEPENDENCY = "missing_dependency"
    VERSION_MISMATCH = "version_mismatch"
    INCOMPATIBLE_INTERFACE = "incompatible_interface"
    ORPHANED_DEPENDENCY = "orphaned_dependency"
    STALE_DEPENDENCY = "stale_dependency"
    BROKEN_IMPORT = "broken_import"
    RUNTIME_ERROR = "runtime_error"
    LOADING_FAILURE = "loading_failure"

class DriftSeverity(Enum):
    """Drift severity enumeration"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NEGLIGIBLE = "negligible"

class GovernanceStatus(Enum):
    """Governance status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    ERROR = "error"
    MAINTENANCE = "maintenance"
    RECOVERY = "recovery"
    FROZEN = "frozen"
    DEGRADED = "degraded"
    OPTIMAL = "optimal"
    WARNING = "warning"

class PatchKind(Enum):
    """Patch kind enumeration"""
    BUGFIX = "bugfix"
    FEATURE = "feature"
    REFACTOR = "refactor"
    OPTIMIZATION = "optimization"
    SECURITY = "security"
    DEPENDENCY = "dependency"
    CONFIGURATION = "configuration"
    HOTFIX = "hotfix"
    EVOLUTIONARY = "evolutionary"
    REVOLUTIONARY = "revolutionary"

class RepairOutcome(Enum):
    """Repair outcome enumeration"""
    SUCCESS = "success"
    FAILURE = "failure"
    PARTIAL = "partial"
    DEFERRED = "deferred"
    CANCELLED = "cancelled"
    APPROVED = "approved"
    REJECTED = "rejected"
    APPLIED = "applied"
    ROLLED_BACK = "rolled_back"
    PENDING = "pending"

class RepairStage(Enum):
    """Repair stage enumeration"""
    DETECTION = "detection"
    ANALYSIS = "analysis"
    PROPOSAL = "proposal"
    APPROVAL = "approval"
    PLANNING = "planning"
    EXECUTION = "execution"
    VALIDATION = "validation"
    ROLLBACK = "rollback"
    COMPLETION = "completion"
    POST_MORTTEM = "post_mortem"

@dataclass
class CognitiveObservability:
    """Cognitive observability information"""
    observability_id: str
    cognitive_state: CognitiveState
    confidence: float
    reasoning_trace: List[str] = field(default_factory=list)
    decisions: List[str] = field(default_factory=list)
    assumptions: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    observability_level: ObservabilityLevel = ObservabilityLevel.DETAILED
    
    def is_confident(self) -> bool:
        """Check if cognitive state is confident"""
        return self.cognitive_state in [CognitiveState.CONFIDENT, CognitiveState.NORMAL]
    
    def is_uncertain(self) -> bool:
        """Check if cognitive state is uncertain"""
        return self.cognitive_state in [CognitiveState.UNCERTAIN, CognitiveState.CONFUSED, CognitiveState.UNCERTAINLY]
    
    def add_reasoning_step(self, step: str) -> None:
        """Add a reasoning step"""
        self.reasoning_trace.append(step)
    
    def add_decision(self, decision: str) -> None:
        """Add a decision"""
        self.decisions.append(decision)
    
    def add_assumption(self, assumption: str) -> None:
        """Add an assumption"""
        self.assumptions.append(assumption)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "observability_id": self.observability_id,
            "cognitive_state": self.cognitive_state.value,
            "confidence": self.confidence,
            "reasoning_trace": self.reasoning_trace,
            "decisions": self.decisions,
            "assumptions": self.assumptions,
            "context": self.context,
            "timestamp": self.timestamp,
            "observability_level": self.observability_level.value
        }

@dataclass
class ArchitecturalDriftEvent:
    """Architectural drift event"""
    event_id: str
    drift_type: str
    severity: str
    description: str
    timestamp: float = field(default_factory=time.time)
    context: Dict[str, Any] = field(default_factory=dict)
    mitigation: str = ""
    
    def is_critical(self) -> bool:
        """Check if drift event is critical"""
        return self.severity == "critical"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "event_id": self.event_id,
            "drift_type": self.drift_type,
            "severity": self.severity,
            "description": self.description,
            "timestamp": self.timestamp,
            "context": self.context,
            "mitigation": self.mitigation
        }

@dataclass
class DependencyAnomalyEvent:
    """Dependency anomaly event"""
    event_id: str
    anomaly_type: str
    severity: str
    description: str
    affected_modules: List[str] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)
    context: Dict[str, Any] = field(default_factory=dict)
    resolution: str = ""
    
    def is_critical(self) -> bool:
        """Check if anomaly event is critical"""
        return self.severity == "critical"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "event_id": self.event_id,
            "anomaly_type": self.anomaly_type,
            "severity": self.severity,
            "description": self.description,
            "affected_modules": self.affected_modules,
            "timestamp": self.timestamp,
            "context": self.context,
            "resolution": self.resolution
        }

@dataclass
class PatchProposalEvent:
    """Patch proposal event"""
    event_id: str
    patch_kind: PatchKind
    description: str
    target_modules: List[str] = field(default_factory=list)
    confidence: float = 0.0
    timestamp: float = field(default_factory=time.time)
    context: Dict[str, Any] = field(default_factory=dict)
    status: str = "proposed"
    
    def is_confident(self) -> bool:
        """Check if proposal is confident"""
        return self.confidence > 0.7
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "event_id": self.event_id,
            "patch_kind": self.patch_kind.value,
            "description": self.description,
            "target_modules": self.target_modules,
            "confidence": self.confidence,
            "timestamp": self.timestamp,
            "context": self.context,
            "status": self.status
        }

@dataclass
class RepairPipelineEvent:
    """Repair pipeline event"""
    event_id: str
    pipeline_stage: str
    repair_type: str
    description: str
    outcome: RepairOutcome = RepairOutcome.PENDING
    timestamp: float = field(default_factory=time.time)
    context: Dict[str, Any] = field(default_factory=dict)
    metrics: Dict[str, float] = field(default_factory=dict)
    
    def is_successful(self) -> bool:
        """Check if repair was successful"""
        return self.outcome == RepairOutcome.SUCCESS
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "event_id": self.event_id,
            "pipeline_stage": self.pipeline_stage,
            "repair_type": self.repair_type,
            "description": self.description,
            "outcome": self.outcome.value,
            "timestamp": self.timestamp,
            "context": self.context,
            "metrics": self.metrics
        }

@dataclass
class RuntimeAnomalyEvent:
    """Runtime anomaly event"""
    event_id: str
    anomaly_type: str
    severity: str
    description: str
    component: str = ""
    timestamp: float = field(default_factory=time.time)
    context: Dict[str, Any] = field(default_factory=dict)
    resolution: str = ""
    recovery_action: str = ""
    
    def is_critical(self) -> bool:
        """Check if anomaly is critical"""
        return self.severity == "critical"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "event_id": self.event_id,
            "anomaly_type": self.anomaly_type,
            "severity": self.severity,
            "description": self.description,
            "component": self.component,
            "timestamp": self.timestamp,
            "context": self.context,
            "resolution": self.resolution,
            "recovery_action": self.recovery_action
        }

@dataclass
class TopologyDriftEvent:
    """Topology drift event"""
    event_id: str
    drift_type: str
    severity: DriftSeverity
    description: str
    affected_components: List[str] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)
    context: Dict[str, Any] = field(default_factory=dict)
    mitigation: str = ""
    
    def is_critical(self) -> bool:
        """Check if drift is critical"""
        return self.severity == DriftSeverity.CRITICAL
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "event_id": self.event_id,
            "drift_type": self.drift_type,
            "severity": self.severity.value,
            "description": self.description,
            "affected_components": self.affected_components,
            "timestamp": self.timestamp,
            "context": self.context,
            "mitigation": self.mitigation
        }

class CognitiveObservabilityRegistry:
    """Registry for cognitive observability records"""
    def __init__(self):
        self._observability_records: Dict[str, CognitiveObservability] = {}
    
    def register_observability(self, observability: CognitiveObservability) -> bool:
        """Register an observability record"""
        self._observability_records[observability.observability_id] = observability
        return True
    
    def get_observability(self, observability_id: str) -> Optional[CognitiveObservability]:
        """Get a specific observability record"""
        return self._observability_records.get(observability_id)
    
    def get_uncertain_observations(self) -> List[CognitiveObservability]:
        """Get all uncertain observations"""
        return [o for o in self._observability_records.values() if o.is_uncertain()]
    
    def get_confident_observations(self) -> List[CognitiveObservability]:
        """Get all confident observations"""
        return [o for o in self._observability_records.values() if o.is_confident()]

# Global observability registry
_observability_registry: Optional[CognitiveObservabilityRegistry] = None

def get_observability_registry() -> CognitiveObservabilityRegistry:
    """Get the global observability registry"""
    global _observability_registry
    if _observability_registry is None:
        _observability_registry = CognitiveObservabilityRegistry()
    return _observability_registry

def create_observability(observability_id: str, cognitive_state: CognitiveState, confidence: float) -> CognitiveObservability:
    """Create a new cognitive observability record"""
    return CognitiveObservability(
        observability_id=observability_id,
        cognitive_state=cognitive_state,
        confidence=confidence
    )

def track_cognitive_state(cognitive_state: CognitiveState, confidence: float, context: Dict[str, Any] = None) -> CognitiveObservability:
    """Track a cognitive state"""
    observability_id = f"cognitive_{int(time.time())}"
    observability = create_observability(observability_id, cognitive_state, confidence)
    if context:
        observability.context = context
    get_observability_registry().register_observability(observability)
    return observability

__all__ = [
    "DYON_SYSTEM_STREAM",
    "DYON_DECISION_STREAM",
    "DYON_REASONING_STREAM",
    "DYON_EXPLORATION_STREAM",
    "DYON_LEARNING_STREAM",
    "DYON_ADAPTATION_STREAM",
    "CognitiveState",
    "ObservabilityLevel",
    "CognitiveEventKind",
    "DependencyAnomalyKind",
    "DriftSeverity",
    "GovernanceStatus",
    "PatchKind",
    "RepairOutcome",
    "RepairStage",
    "CognitiveObservability",
    "ArchitecturalDriftEvent",
    "DependencyAnomalyEvent",
    "PatchProposalEvent",
    "RepairPipelineEvent",
    "RuntimeAnomalyEvent",
    "TopologyDriftEvent",
    "CognitiveObservabilityRegistry",
    "get_observability_registry",
    "create_observability",
    "track_cognitive_state"
]