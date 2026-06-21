"""
Core Contracts Invariants
Real implementation for invariants management
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, List, Callable, Optional
import time
import uuid

class InvariantKind(Enum):
    """Invariant kind enumeration"""
    SYSTEM = "system"
    SAFETY = "safety"
    PERFORMANCE = "performance"
    COMPLIANCE = "compliance"
    GOVERNANCE = "governance"
    OPERATIONAL = "operational"
    FINANCIAL = "financial"
    SECURITY = "security"

class InvariantSeverity(Enum):
    """Invariant severity enumeration"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

class InvariantStatus(Enum):
    """Invariant status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    VIOLATED = "violated"
    WARNED = "warned"
    SATISFIED = "satisfied"
    DISABLED = "disabled"

@dataclass
class InvariantID:
    """Invariant identifier"""
    namespace: str
    name: str
    version: str = "1.0.0"
    
    def __str__(self) -> str:
        return f"{self.namespace}.{self.name}:{self.version}"
    
    def __eq__(self, other) -> bool:
        return (
            isinstance(other, InvariantID) and
            self.namespace == other.namespace and
            self.name == other.name and
            self.version == other.version
        )
    
    def __hash__(self) -> int:
        return hash((self.namespace, self.name, self.version))
    
    # Predefined invariant IDs as class attributes
    DIX_01 = None  # Will be set after class definition
    DIX_02 = None
    DIX_03 = None
    DIX_04 = None
    DIX_05 = None
    DIX_06 = None
    DIX_07 = None
    DIX_08 = None
    DIX_09 = None
    DIX_10 = None
    DIX_11 = None
    DIX_12 = None
    DIX_13 = None
    DIX_14 = None
    DIX_15 = None
    DIX_16 = None
    DIX_17 = None
    DIX_18 = None
    DIX_19 = None
    DIX_20 = None

# Set the class attributes after class definition
InvariantID.DIX_01 = InvariantID("dix", "mode_safety", "1.0.0")
InvariantID.DIX_02 = InvariantID("dix", "operator_authorization", "1.0.0")
InvariantID.DIX_03 = InvariantID("dix", "strategy_lifecycle", "1.0.0")
InvariantID.DIX_04 = InvariantID("dix", "risk_limits", "1.0.0")
InvariantID.DIX_05 = InvariantID("dix", "position_limits", "1.0.0")
InvariantID.DIX_06 = InvariantID("dix", "data_integrity", "1.0.0")
InvariantID.DIX_07 = InvariantID("dix", "audit_trail", "1.0.0")
InvariantID.DIX_08 = InvariantID("dix", "governance_integrity", "1.0.0")
InvariantID.DIX_09 = InvariantID("dix", "consent_required", "1.0.0")
InvariantID.DIX_10 = InvariantID("dix", "event_lineage", "1.0.0")
InvariantID.DIX_11 = InvariantID("dix", "fallback_safety", "1.0.0")
InvariantID.DIX_12 = InvariantID("dix", "cogov_integrity", "1.0.0")
InvariantID.DIX_13 = InvariantID("dix", "causal_consistency", "1.0.0")
InvariantID.DIX_14 = InvariantID("dix", "belief_state", "1.0.0")
InvariantID.DIX_15 = InvariantID("dix", "meta_learning", "1.0.0")
InvariantID.DIX_16 = InvariantID("dix", "self_model", "1.0.0")
InvariantID.DIX_17 = InvariantID("dix", "knowledge_base", "1.0.0")
InvariantID.DIX_18 = InvariantID("dix", "system_health", "1.0.0")
InvariantID.DIX_19 = InvariantID("dix", "performance_metrics", "1.0.0")
InvariantID.DIX_20 = InvariantID("dix", "resource_usage", "1.0.0")

# Also provide module-level constants for convenience
DIX_01 = InvariantID.DIX_01
DIX_02 = InvariantID.DIX_02
DIX_03 = InvariantID.DIX_03
DIX_04 = InvariantID.DIX_04
DIX_05 = InvariantID.DIX_05
DIX_06 = InvariantID.DIX_06
DIX_07 = InvariantID.DIX_07
DIX_08 = InvariantID.DIX_08
DIX_09 = InvariantID.DIX_09
DIX_10 = InvariantID.DIX_10
DIX_11 = InvariantID.DIX_11
DIX_12 = InvariantID.DIX_12
DIX_13 = InvariantID.DIX_13
DIX_14 = InvariantID.DIX_14
DIX_15 = InvariantID.DIX_15
DIX_16 = InvariantID.DIX_16
DIX_17 = InvariantID.DIX_17
DIX_18 = InvariantID.DIX_18
DIX_19 = InvariantID.DIX_19
DIX_20 = InvariantID.DIX_20

@dataclass
class InvariantDefinition:
    """Invariant definition"""
    id: InvariantID
    kind: InvariantKind
    severity: InvariantSeverity
    description: str
    condition: str
    check_function: Optional[Callable] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    enabled: bool = True
    
    def is_satisfied(self, context: Dict[str, Any]) -> bool:
        """Check if invariant is satisfied"""
        if self.check_function:
            try:
                return self.check_function(context, self.parameters)
            except Exception:
                return False
        return True
    
    def is_critical(self) -> bool:
        """Check if invariant is critical"""
        return self.severity == InvariantSeverity.CRITICAL

@dataclass
class InvariantViolation:
    """Invariant violation record"""
    violation_id: str
    invariant_id: InvariantID
    timestamp: float = field(default_factory=time.time)
    context: Dict[str, Any] = field(default_factory=dict)
    severity: InvariantSeverity = InvariantSeverity.MEDIUM
    resolved: bool = False
    resolution_timestamp: float = 0.0
    resolution_notes: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "violation_id": self.violation_id,
            "invariant_id": str(self.invariant_id),
            "timestamp": self.timestamp,
            "context": self.context,
            "severity": self.severity.value,
            "resolved": self.resolved,
            "resolution_timestamp": self.resolution_timestamp,
            "resolution_notes": self.resolution_notes
        }

class InvariantManager:
    """Manager for invariants and violations"""
    def __init__(self):
        self._invariants: Dict[str, InvariantDefinition] = {}
        self._violations: List[InvariantViolation] = []
    
    def register_invariant(self, invariant: InvariantDefinition) -> bool:
        """Register an invariant"""
        self._invariants[str(invariant.id)] = invariant
        return True
    
    def get_invariant(self, invariant_id: str) -> Optional[InvariantDefinition]:
        """Get a specific invariant"""
        return self._invariants.get(invariant_id)
    
    def check_invariant(self, invariant_id: str, context: Dict[str, Any]) -> bool:
        """Check if an invariant is satisfied"""
        invariant = self.get_invariant(invariant_id)
        if invariant:
            return invariant.is_satisfied(context)
        return True
    
    def record_violation(self, violation: InvariantViolation) -> bool:
        """Record a violation"""
        self._violations.append(violation)
        return True
    
    def resolve_violation(self, violation_id: str, notes: str = "") -> bool:
        """Resolve a violation"""
        for violation in self._violations:
            if violation.violation_id == violation_id:
                violation.resolved = True
                violation.resolution_timestamp = time.time()
                violation.resolution_notes = notes
                return True
        return False
    
    def get_active_violations(self) -> List[InvariantViolation]:
        """Get all active violations"""
        return [v for v in self._violations if not v.resolved]

# Global invariant manager
_invariant_manager: Optional[InvariantManager] = None

def get_invariant_manager() -> InvariantManager:
    """Get the global invariant manager"""
    global _invariant_manager
    if _invariant_manager is None:
        _invariant_manager = InvariantManager()
    return _invariant_manager

def create_violation(invariant_id: InvariantID, context: Dict[str, Any]) -> InvariantViolation:
    """Create a new violation record"""
    return InvariantViolation(
        violation_id=str(uuid.uuid4()),
        invariant_id=invariant_id,
        context=context
    )

__all__ = [
    "InvariantKind",
    "InvariantSeverity",
    "InvariantStatus",
    "InvariantID",
    "DIX_01",
    "DIX_02",
    "DIX_03",
    "DIX_04",
    "DIX_05",
    "DIX_06",
    "DIX_07",
    "DIX_08",
    "DIX_09",
    "DIX_10",
    "DIX_11",
    "DIX_12",
    "DIX_13",
    "DIX_14",
    "DIX_15",
    "DIX_16",
    "DIX_17",
    "DIX_18",
    "DIX_19",
    "DIX_20",
    "InvariantDefinition",
    "InvariantViolation",
    "InvariantManager",
    "get_invariant_manager",
    "create_violation"
]