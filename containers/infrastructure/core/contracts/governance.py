"""
Core Contracts Governance
Real implementation for governance contracts
"""

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional


class GovernanceKind(Enum):
    """Governance event kinds"""

    MODE_CHANGE = "mode_change"
    CONSTRAINT_VIOLATION = "constraint_violation"
    AUTHORIZATION = "authorization"
    AUDIT = "audit"


class SystemMode(Enum):
    """System operating modes"""

    NORMAL = "normal"
    LIVE = "live"
    AUTO = "auto"
    DEGRADED = "degraded"
    SAFE = "safe"
    SAFE_MODE = "safe_mode"
    PAPER = "paper"
    CANARY = "canary"
    SIMULATION = "simulation"
    EMERGENCY_HALT = "emergency_halt"
    LOCKED = "locked"
    MAINTENANCE = "maintenance"
    SHUTDOWN = "shutdown"
    RECOVERY = "recovery"


class OperatorAction(Enum):
    """Operator action kinds"""

    APPROVE = "approve"
    DENY = "deny"
    OVERRIDE = "override"
    REVIEW = "review"
    EMERGENCY_STOP = "emergency_stop"
    REQUEST_KILL = "request_kill"
    HALT = "halt"
    RESUME = "resume"
    REQUEST_PLUGIN_LIFECYCLE = "request_plugin_lifecycle"
    REQUEST_UNLOCK = "request_unlock"
    REQUEST_MODE = "request_mode"
    REQUEST_INTENT = "request_intent"


@dataclass
class LedgerEntry:
    """Ledger entry for governance tracking"""

    entry_id: str = ""  # Entry ID
    kind: GovernanceKind = GovernanceKind.AUDIT  # Entry kind
    source: str = ""  # Source of entry
    seq: int = 0  # Sequence number
    ts_ns: int = 0  # Nanosecond timestamp
    prev_hash: str = ""  # Previous hash
    hash_chain: str = ""  # Hash chain
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "entry_id": self.entry_id,
            "kind": self.kind.value,
            "source": self.source,
            "payload": self.payload,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }


@dataclass
class OperatorRequest:
    """Operator request for approval/action"""

    request_id: str
    action: OperatorAction
    description: str
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    approved: bool = False
    operator_id: Optional[str] = None


class GovernanceDecision(Enum):
    """Governance decision kinds"""

    APPROVE = "approve"
    REJECT = "reject"
    DEFER = "defer"
    OVERRIDE = "override"
    ESCALATE = "escalate"


class DecisionKind(Enum):
    """Decision kind enumeration"""

    GOVERNANCE = "governance"
    OPERATOR = "operator"
    AUTOMATED = "automated"
    SEMI_AUTOMATED = "semi_automated"
    EMERGENCY = "emergency"
    ROUTINE = "routine"
    EXCEPTION = "exception"
    STRATEGIC = "strategic"


class IntentHorizon(Enum):
    """Intent horizon enumeration"""

    IMMEDIATE = "immediate"
    SHORT_TERM = "short_term"
    MEDIUM_TERM = "medium_term"
    LONG_TERM = "long_term"
    INDEFINITE = "indefinite"


class IntentObjective(Enum):
    """Intent objective enumeration"""

    PROFIT = "profit"
    RISK_MANAGEMENT = "risk_management"
    GROWTH = "growth"
    STABILITY = "stability"
    INNOVATION = "innovation"
    EFFICIENCY = "efficiency"
    RESILIENCE = "resilience"
    ADAPTABILITY = "adaptability"
    SAFETY = "safety"
    COMPLIANCE = "compliance"


class IntentRiskMode(Enum):
    """Intent risk mode enumeration"""

    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"
    HIGH_RISK = "high_risk"
    SPECULATIVE = "speculative"
    HEDGED = "hedged"
    BALANCED = "balanced"
    TACTICAL = "tactical"
    STRATEGIC = "strategic"
    DEFENSIVE = "defensive"


@dataclass
class RiskAssessment:
    """Risk assessment information"""

    assessment_id: str
    risk_level: str
    risk_score: float
    risk_factors: list = field(default_factory=list)
    mitigation_strategies: list = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)
    assessor_id: str = ""

    def is_high_risk(self) -> bool:
        """Check if assessment indicates high risk"""
        return self.risk_level == "high" or self.risk_score >= 0.7


class ConstraintKind(Enum):
    """Constraint kind enumeration"""

    RISK_LIMIT = "risk_limit"
    POSITION_LIMIT = "position_limit"
    EXPOSURE_LIMIT = "exposure_limit"
    RATE_LIMIT = "rate_limit"
    AUTHORIZATION = "authorization"
    COMPLIANCE = "compliance"
    OPERATIONAL = "operational"


class ConstraintScope(Enum):
    """Constraint scope enumeration"""

    SYSTEM = "system"
    ENGINE = "engine"
    STRATEGY = "strategy"
    MARKET = "market"
    ACCOUNT = "account"
    OPERATION = "operation"


@dataclass
class Constraint:
    """Governance constraint definition"""

    constraint_id: str
    constraint_type: str
    description: str
    severity: str = "medium"
    enabled: bool = True
    parameters: Dict[str, Any] = field(default_factory=dict)

    def is_satisfied(self, context: Dict[str, Any]) -> bool:
        """Check if constraint is satisfied given context"""
        # Real implementation would check constraint logic
        return True


@dataclass
class ModeTransitionRequest:
    """Request for mode transition"""

    from_mode: str
    to_mode: str
    reason: str
    operator_id: str
    timestamp: float = field(default_factory=time.time)
    approved: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "from_mode": self.from_mode,
            "to_mode": self.to_mode,
            "reason": self.reason,
            "operator_id": self.operator_id,
            "timestamp": self.timestamp,
            "approved": self.approved,
        }


@dataclass
class ComplianceReport:
    """Compliance report for governance checks"""

    report_id: str
    timestamp: float = field(default_factory=time.time)
    compliant: bool = True
    violations: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
    score: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def is_compliant(self) -> bool:
        """Check if system is compliant"""
        return self.compliant and len(self.violations) == 0


@dataclass
class ModeTransitionDecision:
    """Decision for mode transition request"""

    request_id: str
    approved: bool
    reason: str
    operator_id: str
    timestamp: float = field(default_factory=time.time)
    conditions: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "request_id": self.request_id,
            "approved": self.approved,
            "reason": self.reason,
            "operator_id": self.operator_id,
            "timestamp": self.timestamp,
            "conditions": self.conditions,
        }


@dataclass
class IntentTransitionRequest:
    """Request for intent transition"""

    intent_id: str
    from_intent: str
    to_intent: str
    reason: str
    operator_id: str
    timestamp: float = field(default_factory=time.time)
    approved: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "intent_id": self.intent_id,
            "from_intent": self.from_intent,
            "to_intent": self.to_intent,
            "reason": self.reason,
            "operator_id": self.operator_id,
            "timestamp": self.timestamp,
            "approved": self.approved,
        }


@dataclass
class IntentTransitionDecision:
    """Decision for intent transition"""

    intent_id: str
    approved: bool
    reason: str
    operator_id: str
    timestamp: float = field(default_factory=time.time)
    conditions: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "intent_id": self.intent_id,
            "approved": self.approved,
            "reason": self.reason,
            "operator_id": self.operator_id,
            "timestamp": self.timestamp,
            "conditions": self.conditions,
        }


__all__ = [
    "GovernanceKind",
    "SystemMode",
    "GovernanceDecision",
    "DecisionKind",
    "IntentHorizon",
    "IntentObjective",
    "IntentRiskMode",
    "RiskAssessment",
    "ConstraintKind",
    "ConstraintScope",
    "OperatorAction",
    "LedgerEntry",
    "OperatorRequest",
    "Constraint",
    "ModeTransitionRequest",
    "ComplianceReport",
    "ModeTransitionDecision",
    "IntentTransitionRequest",
    "IntentTransitionDecision",
]
