"""Unified Governance Kernel - Core Foundation.

This is the consolidated governance kernel that unifies the functionality
from governance/, governance_engine/, financial_governance/, and operator_governance/.

The unified kernel provides:
- Central authority management
- Mode management and transitions
- Policy enforcement
- Risk assessment
- Domain-specific governance routing
- Hazard response coordination

Design Principles:
- INV-15: Minimal external dependencies, no blocking IO
- INV-08: Pure governance logic where possible
- Thread-safe operations
- Async processing for performance
- Clear separation of concerns
"""

from __future__ import annotations

import dataclasses
import enum
import logging
import threading
from collections.abc import Callable, Mapping
from types import MappingProxyType
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from governance_unified.domains.financial.capital_governance import FinancialGovernanceDomain
    from governance_unified.domains.operator.operator_governance import OperatorGovernanceDomain

_logger = logging.getLogger(__name__)


class GovernanceOutcome(str, enum.Enum):
    """Outcomes from governance decisions."""

    APPROVED = "EXECUTION_APPROVED"
    REJECTED = "EXECUTION_REJECTED"
    MODIFIED = "EXECUTION_MODIFIED"
    SAFE_MODE = "SYSTEM_SAFE_MODE_TRIGGERED"
    HALT = "TRADING_HALTED"
    DEFERRED = "DEFERRED_TO_OPERATOR"
    CONDITIONAL = "CONDITIONAL_APPROVAL"


class SystemMode(str, enum.Enum):
    """System operating modes."""

    NORMAL = "NORMAL"
    CONSERVATIVE = "CONSERVATIVE"
    AGGRESSIVE = "AGGRESSIVE"
    SAFE = "SAFE_MODE"
    MAINTENANCE = "MAINTENANCE"
    TESTING = "TESTING"


class IntentType(str, enum.Enum):
    """Types of intents processed by governance."""

    MARKET_INTENT = "MARKET_INTENT"  # From Indira
    SYSTEM_INTENT = "SYSTEM_INTENT"  # From Dyon
    HAZARD_EVENT = "HAZARD_EVENT"  # Hazard bus
    OPERATOR_REQUEST = "OPERATOR_REQUEST"  # Dashboard/operator
    POLICY_REQUEST = "POLICY_REQUEST"  # Policy changes


@dataclasses.dataclass(frozen=True, slots=True)
class GovernanceRequest:
    """A request for governance decision.

    Fields:
        request_id: Unique identifier for this request
        intent_type: Type of intent/governance request
        source: Origin of the request
        payload: Request content (key-value pairs)
        priority: Request priority (0-10, 10 = highest)
        timestamp_ns: Nanosecond timestamp of request
        metadata: Additional metadata
    """

    request_id: str
    intent_type: IntentType
    source: str
    payload: Mapping[str, str] = dataclasses.field(default_factory=lambda: MappingProxyType({}))
    priority: int = 5
    timestamp_ns: int = 0
    metadata: Mapping[str, str] = dataclasses.field(default_factory=lambda: MappingProxyType({}))

    def __post_init__(self) -> None:
        if not self.request_id:
            raise ValueError("GovernanceRequest.request_id must be non-empty")
        if not 0 <= self.priority <= 10:
            raise ValueError(f"GovernanceRequest.priority must be 0-10, got {self.priority}")
        if not isinstance(self.payload, MappingProxyType):
            object.__setattr__(self, "payload", MappingProxyType(dict(self.payload)))
        if not isinstance(self.metadata, MappingProxyType):
            object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))


@dataclasses.dataclass(frozen=True, slots=True)
class GovernanceDecision:
    """A governance decision response.

    Fields:
        decision_id: Unique identifier for this decision
        request_id: Corresponding request ID
        outcome: Governance outcome
        reason: Explanation for the decision
        modifications: Any modifications to the original request
        allowed: Boolean flag (compatibility)
        conditions: Any conditions for approval
        confidence: Decision confidence (0.0-1.0)
        timestamp_ns: Nanosecond timestamp of decision
    """

    decision_id: str
    request_id: str
    outcome: GovernanceOutcome
    reason: str
    modifications: Mapping[str, str] = dataclasses.field(default_factory=lambda: MappingProxyType({}))
    allowed: bool = True
    conditions: Mapping[str, str] = dataclasses.field(default_factory=lambda: MappingProxyType({}))
    confidence: float = 1.0
    timestamp_ns: int = 0

    def __post_init__(self) -> None:
        if not self.decision_id:
            raise ValueError("GovernanceDecision.decision_id must be non-empty")
        if not self.request_id:
            raise ValueError("GovernanceDecision.request_id must be non-empty")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"GovernanceDecision.confidence must be 0.0-1.0, got {self.confidence}")
        if not isinstance(self.modifications, MappingProxyType):
            object.__setattr__(self, "modifications", MappingProxyType(dict(self.modifications)))
        if not isinstance(self.conditions, MappingProxyType):
            object.__setattr__(self, "conditions", MappingProxyType(dict(self.conditions)))


@dataclasses.dataclass(frozen=True, slots=True)
class AuthorityRequest:
    """Request for authority check.

    Fields:
        request_id: Unique identifier
        actor: Entity requesting authority
        action: Action being requested
        resource: Resource being accessed
        context: Additional context
        timestamp_ns: Timestamp
    """

    request_id: str
    actor: str
    action: str
    resource: str
    context: Mapping[str, str] = dataclasses.field(default_factory=lambda: MappingProxyType({}))
    timestamp_ns: int = 0

    def __post_init__(self) -> None:
        if not isinstance(self.context, MappingProxyType):
            object.__setattr__(self, "context", MappingProxyType(dict(self.context)))


@dataclasses.dataclass(frozen=True, slots=True)
class AuthorityDecision:
    """Decision on authority request.

    Fields:
        decision_id: Unique identifier
        request_id: Corresponding request ID
        authorized: Whether the request is authorized
        reason: Explanation
        restrictions: Any restrictions applied
        timestamp_ns: Timestamp
    """

    decision_id: str
    request_id: str
    authorized: bool
    reason: str
    restrictions: tuple[str, ...] = ()
    timestamp_ns: int = 0


@dataclasses.dataclass(frozen=True, slots=True)
class ModeTransitionRequest:
    """Request to transition system modes.

    Fields:
        request_id: Unique identifier
        current_mode: Current system mode
        target_mode: Desired target mode
        reason: Reason for transition
        requested_by: Who requested the transition
        timestamp_ns: Timestamp
    """

    request_id: str
    current_mode: SystemMode
    target_mode: SystemMode
    reason: str
    requested_by: str
    timestamp_ns: int = 0


@dataclasses.dataclass(frozen=True, slots=True)
class ModeTransitionResult:
    """Result of mode transition attempt.

    Fields:
        transition_id: Unique identifier
        request_id: Corresponding request ID
        success: Whether transition succeeded
        new_mode: New system mode (if successful)
        reason: Explanation
        timestamp_ns: Timestamp
    """

    transition_id: str
    request_id: str
    success: bool
    new_mode: SystemMode | None = None
    reason: str = ""
    timestamp_ns: int = 0


@dataclasses.dataclass(frozen=True, slots=True)
class RiskAssessment:
    """Risk assessment for an action.

    Fields:
        assessment_id: Unique identifier
        risk_level: Overall risk level (0.0-1.0)
        risk_categories: Category-specific risks
        mitigations: Suggested mitigations
        confidence: Assessment confidence
        timestamp_ns: Timestamp
    """

    assessment_id: str
    risk_level: float
    risk_categories: Mapping[str, float] = dataclasses.field(default_factory=lambda: MappingProxyType({}))
    mitigations: tuple[str, ...] = ()
    confidence: float = 0.8
    timestamp_ns: int = 0

    def __post_init__(self) -> None:
        if not 0.0 <= self.risk_level <= 1.0:
            raise ValueError(f"RiskAssessment.risk_level must be 0.0-1.0, got {self.risk_level}")
        if not isinstance(self.risk_categories, MappingProxyType):
            object.__setattr__(self, "risk_categories", MappingProxyType(dict(self.risk_categories)))


class UnifiedGovernanceKernel:
    """Unified governance kernel consolidating all governance functionality.

    This kernel provides the central authority for all governance decisions,
    integrating domain-specific governance (financial, operator, cognitive, execution)
    while maintaining clear separation of concerns.

    Key Responsibilities:
    - Process governance requests and make decisions
    - Manage system modes and transitions
    - Enforce policies across all domains
    - Assess risks for proposed actions
    - Coordinate hazard responses
    - Route to domain-specific governance modules
    - Maintain authority graphs and permissions
    """

    def __init__(self) -> None:
        self._lock: threading.Lock = threading.Lock()
        
        # Domain governance modules (to be initialized)
        self._financial_governance: FinancialGovernanceDomain | None = None
        self._operator_governance: OperatorGovernanceDomain | None = None
        self._cognitive_governance: Any = None  # To be implemented
        self._execution_governance: Any = None  # To be implemented
        
        # Governance state
        self._current_mode: SystemMode = SystemMode.NORMAL
        self._decision_history: dict[str, GovernanceDecision] = {}
        self._authority_graph: dict[str, set[str]] = {}  # actor -> permissions
        self._active_policies: dict[str, Any] = {}
        
        # Statistics
        self._total_decisions: int = 0
        self._total_authority_checks: int = 0
        self._total_mode_transitions: int = 0

    def register_domain(
        self,
        domain: FinancialGovernanceDomain | OperatorGovernanceDomain | Any,
    ) -> None:
        """Register a domain-specific governance module.

        Args:
            domain: Domain governance module to register
        """
        domain_type = type(domain).__name__.lower()

        with self._lock:
            if "financial" in domain_type:
                self._financial_governance = domain
            elif "operator" in domain_type:
                self._operator_governance = domain
            elif "cognitive" in domain_type:
                self._cognitive_governance = domain
            elif "execution" in domain_type:
                self._execution_governance = domain
            else:
                _logger.warning(f"Unknown domain type: {domain_type}")

        _logger.info(f"Registered governance domain: {domain_type}")

    def enforce_policy(
        self,
        policy: Any,
        context: Mapping[str, str],
    ) -> GovernanceDecision:
        """Enforce a policy against a given context.

        Args:
            policy: Policy to enforce
            context: Context for policy evaluation

        Returns:
            GovernanceDecision with enforcement result
        """
        # TODO: Implement policy enforcement logic
        decision_id = f"policy_decision_{self._get_timestamp()}"

        # Placeholder decision
        return GovernanceDecision(
            decision_id=decision_id,
            request_id="policy_enforcement",
            outcome=GovernanceOutcome.APPROVED,
            reason="Policy enforcement placeholder",
            confidence=0.8,
            timestamp_ns=self._get_timestamp(),
        )

    def authority_check(self, request: AuthorityRequest) -> AuthorityDecision:
        """Check if an actor has authority for a requested action.

        Args:
            request: Authority request to check

        Returns:
            AuthorityDecision with authorization result
        """
        decision_id = f"authority_decision_{request.request_id}"

        with self._lock:
            self._total_authority_checks += 1

            # Check authority graph
            permissions = self._authority_graph.get(request.actor, set())
            authorized = request.action in permissions

            decision = AuthorityDecision(
                decision_id=decision_id,
                request_id=request.request_id,
                authorized=authorized,
                reason="Authorized" if authorized else "Insufficient permissions",
                timestamp_ns=self._get_timestamp(),
            )

        return decision

    def mode_transition(
        self,
        request: ModeTransitionRequest,
    ) -> ModeTransitionResult:
        """Process a mode transition request.

        Args:
            request: Mode transition request

        Returns:
            ModeTransitionResult with transition outcome
        """
        transition_id = f"mode_transition_{request.request_id}"

        # Validate transition
        if not self._is_valid_transition(request.current_mode, request.target_mode):
            return ModeTransitionResult(
                transition_id=transition_id,
                request_id=request.request_id,
                success=False,
                reason="Invalid mode transition",
                timestamp_ns=self._get_timestamp(),
            )

        # Execute transition
        with self._lock:
            self._current_mode = request.target_mode
            self._total_mode_transitions += 1

        _logger.info(
            "Mode transition: %s -> %s (requested by %s)",
            request.current_mode,
            request.target_mode,
            request.requested_by,
        )

        return ModeTransitionResult(
            transition_id=transition_id,
            request_id=request.request_id,
            success=True,
            new_mode=request.target_mode,
            reason="Mode transition successful",
            timestamp_ns=self._get_timestamp(),
        )

    def risk_assessment(self, action: Mapping[str, str]) -> RiskAssessment:
        """Assess risk for a proposed action.

        Args:
            action: Action to assess

        Returns:
            RiskAssessment with risk analysis
        """
        assessment_id = f"risk_assessment_{self._get_timestamp()}"

        # TODO: Implement sophisticated risk assessment
        # Placeholder implementation
        return RiskAssessment(
            assessment_id=assessment_id,
            risk_level=0.3,  # Default moderate risk
            risk_categories=MappingProxyType({"market": 0.2, "operational": 0.4}),
            mitigations=("Monitor closely", "Have rollback ready"),
            confidence=0.7,
            timestamp_ns=self._get_timestamp(),
        )

    def process_governance_request(self, request: GovernanceRequest) -> GovernanceDecision:
        """Process a governance request and make a decision.

        Args:
            request: Governance request to process

        Returns:
            GovernanceDecision with the governance decision
        """
        decision_id = f"decision_{request.request_id}"

        # Route to appropriate domain based on intent type
        if request.intent_type == IntentType.MARKET_INTENT:
            decision = self._process_market_intent(request)
        elif request.intent_type == IntentType.SYSTEM_INTENT:
            decision = self._process_system_intent(request)
        elif request.intent_type == IntentType.HAZARD_EVENT:
            decision = self._process_hazard_event(request)
        elif request.intent_type == IntentType.OPERATOR_REQUEST:
            decision = self._process_operator_request(request)
        else:
            decision = self._process_generic_request(request)

        # Store decision
        with self._lock:
            self._decision_history[decision_id] = decision
            self._total_decisions += 1

        return decision

    def get_current_mode(self) -> SystemMode:
        """Get the current system mode."""
        with self._lock:
            return self._current_mode

    def get_governance_statistics(self) -> dict[str, int | str]:
        """Get governance statistics."""
        with self._lock:
            return {
                "total_decisions": self._total_decisions,
                "total_authority_checks": self._total_authority_checks,
                "total_mode_transitions": self._total_mode_transitions,
                "current_mode": self._current_mode.value,
                "registered_domains": sum(
                    1
                    for domain in [
                        self._financial_governance,
                        self._operator_governance,
                        self._cognitive_governance,
                        self._execution_governance,
                    ]
                    if domain is not None
                ),
                "active_policies": len(self._active_policies),
            }

    # ------------------------------------------------------------------
    # Private methods for domain-specific processing
    # ------------------------------------------------------------------

    def _process_market_intent(self, request: GovernanceRequest) -> GovernanceDecision:
        """Process market intent from Indira."""
        # Route through financial governance if available
        if self._financial_governance:
            # TODO: Integrate with financial governance domain
            pass

        # Placeholder decision
        return GovernanceDecision(
            decision_id=f"decision_{request.request_id}",
            request_id=request.request_id,
            outcome=GovernanceOutcome.APPROVED,
            reason="Market intent processed",
            confidence=0.8,
            timestamp_ns=self._get_timestamp(),
        )

    def _process_system_intent(self, request: GovernanceRequest) -> GovernanceDecision:
        """Process system intent from Dyon."""
        # Route through cognitive governance if available
        if self._cognitive_governance:
            # TODO: Integrate with cognitive governance domain
            pass

        # Placeholder decision
        return GovernanceDecision(
            decision_id=f"decision_{request.request_id}",
            request_id=request.request_id,
            outcome=GovernanceOutcome.APPROVED,
            reason="System intent processed",
            confidence=0.8,
            timestamp_ns=self._get_timestamp(),
        )

    def _process_hazard_event(self, request: GovernanceRequest) -> GovernanceDecision:
        """Process hazard event."""
        # Assess hazard severity
        severity = request.payload.get("severity", "UNKNOWN")

        if severity in ("CRITICAL", "HIGH"):
            return GovernanceDecision(
                decision_id=f"decision_{request.request_id}",
                request_id=request.request_id,
                outcome=GovernanceOutcome.SAFE_MODE,
                reason=f"Hazard event with {severity} severity - entering safe mode",
                confidence=1.0,
                timestamp_ns=self._get_timestamp(),
            )
        else:
            return GovernanceDecision(
                decision_id=f"decision_{request.request_id}",
                request_id=request.request_id,
                outcome=GovernanceOutcome.APPROVED,
                reason=f"Hazard event with {severity} severity - monitoring",
                confidence=0.7,
                timestamp_ns=self._get_timestamp(),
            )

    def _process_operator_request(self, request: GovernanceRequest) -> GovernanceDecision:
        """Process operator request."""
        # Route through operator governance if available
        if self._operator_governance:
            # TODO: Integrate with operator governance domain
            pass

        # Operator requests are generally approved
        return GovernanceDecision(
            decision_id=f"decision_{request.request_id}",
            request_id=request.request_id,
            outcome=GovernanceOutcome.APPROVED,
            reason="Operator request processed",
            confidence=1.0,
            timestamp_ns=self._get_timestamp(),
        )

    def _process_generic_request(self, request: GovernanceRequest) -> GovernanceDecision:
        """Process generic governance request."""
        return GovernanceDecision(
            decision_id=f"decision_{request.request_id}",
            request_id=request.request_id,
            outcome=GovernanceOutcome.APPROVED,
            reason="Generic request processed",
            confidence=0.5,
            timestamp_ns=self._get_timestamp(),
        )

    def _is_valid_transition(
        self,
        current_mode: SystemMode,
        target_mode: SystemMode,
    ) -> bool:
        """Check if mode transition is valid."""
        # Define valid transitions
        valid_transitions = {
            SystemMode.NORMAL: {
                SystemMode.CONSERVATIVE,
                SystemMode.AGGRESSIVE,
                SystemMode.SAFE,
                SystemMode.MAINTENANCE,
            },
            SystemMode.CONSERVATIVE: {SystemMode.NORMAL, SystemMode.SAFE},
            SystemMode.AGGRESSIVE: {SystemMode.NORMAL, SystemMode.SAFE},
            SystemMode.SAFE: {SystemMode.NORMAL, SystemMode.MAINTENANCE},
            SystemMode.MAINTENANCE: {SystemMode.NORMAL, SystemMode.TESTING},
            SystemMode.TESTING: {SystemMode.NORMAL, SystemMode.MAINTENANCE},
        }

        return target_mode in valid_transitions.get(current_mode, set())

    def _get_timestamp(self) -> int:
        """Get current timestamp in nanoseconds."""
        # In production, this would use the system time source
        return 0  # TODO: Integrate with proper time source


# Singleton instance
_singleton: UnifiedGovernanceKernel | None = None
_lock = threading.Lock()


def get_unified_governance_kernel() -> UnifiedGovernanceKernel:
    """Get the singleton unified governance kernel instance."""
    global _singleton
    if _singleton is None:
        with _lock:
            if _singleton is None:
                _singleton = UnifiedGovernanceKernel()
    return _singleton


__all__ = [
    "UnifiedGovernanceKernel",
    "get_unified_governance_kernel",
    "GovernanceRequest",
    "GovernanceDecision",
    "GovernanceOutcome",
    "AuthorityRequest",
    "AuthorityDecision",
    "ModeTransitionRequest",
    "ModeTransitionResult",
    "RiskAssessment",
    "SystemMode",
    "IntentType",
]