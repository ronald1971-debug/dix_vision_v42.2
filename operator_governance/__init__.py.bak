"""
Operator Governance Module - Operator-Level Governance Infrastructure
Provides governance capabilities for operator consent and authorization
Required by archival components for governance operations
NO LAZY LOADING - All components load directly
"""

from typing import Dict, List, Optional, Any, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
import asyncio
from datetime import datetime, timedelta
import hashlib
import json

logger = logging.getLogger(__name__)


class OperatorLevel(Enum):
    """Operator permission level"""
    READ_ONLY = "read_only"
    OPERATOR = "operator"
    SUPERVISOR = "supervisor"
    ADMIN = "admin"


class ConsentStatus(Enum):
    """Consent status"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"
    REVOKED = "revoked"


class GovernanceAction(Enum):
    """Governance action types"""
    TRADE_EXECUTION = "trade_execution"
    CONFIGURATION_CHANGE = "configuration_change"
    SYSTEM_START = "system_start"
    SYSTEM_STOP = "system_stop"
    RISK_LIMIT_CHANGE = "risk_limit_change"
    STRATEGY_DEPLOYMENT = "strategy_deployment"
    EMERGENCY_ACTION = "emergency_action"


@dataclass
class ConsentRequest:
    """Consent request data structure"""
    request_id: str
    operator_id: str
    action: GovernanceAction
    action_params: Dict[str, Any]
    operator_level: OperatorLevel = OperatorLevel.OPERATOR
    status: ConsentStatus = ConsentStatus.PENDING
    requested_at_ns: int = 0
    expires_at_ns: Optional[int] = None
    approved_by: Optional[str] = None
    approved_at_ns: Optional[int] = None
    rejection_reason: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if self.requested_at_ns == 0:
            self.requested_at_ns = datetime.now().timestamp_ns()
        if self.expires_at_ns is None:
            self.expires_at_ns = self.requested_at_ns + (5 * 60 * 1_000_000_000)  # 5 minutes default


@dataclass
class ConsentDecision:
    """Consent decision data structure"""
    request_id: str
    approved: bool
    operator_id: str
    decision_at_ns: int = 0
    reason: Optional[str] = None
    conditions: Optional[Dict[str, Any]] = None
    signature: Optional[str] = None
    
    def __post_init__(self):
        if self.decision_at_ns == 0:
            self.decision_at_ns = datetime.now().timestamp_ns()


@dataclass
class OperatorProfile:
    """Operator profile data structure"""
    operator_id: str
    name: str
    level: OperatorLevel
    active: bool = True
    permissions: List[str] = field(default_factory=list)
    created_at_ns: int = 0
    last_activity_ns: int = 0
    
    def __post_init__(self):
        if self.created_at_ns == 0:
            self.created_at_ns = datetime.now().timestamp_ns()
        if self.last_activity_ns == 0:
            self.last_activity_ns = datetime.now().timestamp_ns()


class OperatorGovernanceEngine:
    """
    Operator Governance Engine - Core governance component for operator consent
    
    Manages operator consent, authorization, and governance policies
    Required by archival components for governance operations
    """
    
    def __init__(self):
        self._operators: Dict[str, OperatorProfile] = {}
        self._consent_requests: Dict[str, ConsentRequest] = {}
        self._consent_decisions: Dict[str, ConsentDecision] = {}
        self._governance_policies: Dict[str, Dict[str, Any]] = {}
        self._callbacks: Dict[str, List[Callable]] = {}
        self._lock = asyncio.Lock()
        self._consent_expiration_check_active = False
        
    async def register_operator(self, operator_id: str, name: str, 
                               level: OperatorLevel = OperatorLevel.OPERATOR,
                               permissions: Optional[List[str]] = None) -> OperatorProfile:
        """Register a new operator"""
        operator = OperatorProfile(
            operator_id=operator_id,
            name=name,
            level=level,
            permissions=permissions or []
        )
        
        async with self._lock:
            self._operators[operator_id] = operator
        
        logger.info(f"Registered operator: {operator_id} - {name} ({level.value})")
        
        # Trigger callbacks
        await self._trigger_callbacks(f"operator_registered_{operator_id}")
        
        return operator
    
    async def request_consent(self, operator_id: str, action: GovernanceAction,
                             action_params: Dict[str, Any],
                             expires_in_minutes: int = 5) -> ConsentRequest:
        """Request operator consent for an action"""
        request_id = self._generate_request_id(operator_id, action)
        
        # Check if operator exists
        if operator_id not in self._operators:
            logger.error(f"Operator {operator_id} not found")
            raise ValueError(f"Operator {operator_id} not found")
        
        operator = self._operators[operator_id]
        
        # Check if operator has permission for this action
        if not await self._check_permission(operator_id, action):
            logger.error(f"Operator {operator_id} does not have permission for {action.value}")
            raise PermissionError(f"Operator does not have permission for {action.value}")
        
        request = ConsentRequest(
            request_id=request_id,
            operator_id=operator_id,
            action=action,
            action_params=action_params,
            operator_level=operator.level,
            expires_at_ns=datetime.now().timestamp_ns() + (expires_in_minutes * 60 * 1_000_000_000)
        )
        
        async with self._lock:
            self._consent_requests[request_id] = request
        
        logger.info(f"Consent requested: {request_id} by {operator_id} for {action.value}")
        
        # Trigger callbacks
        await self._trigger_callbacks(f"consent_requested_{request_id}")
        
        return request
    
    async def grant_consent(self, request_id: str, approver_id: str,
                           conditions: Optional[Dict[str, Any]] = None,
                           reason: Optional[str] = None) -> ConsentDecision:
        """Grant consent for a request"""
        if request_id not in self._consent_requests:
            logger.error(f"Request {request_id} not found")
            raise ValueError(f"Request {request_id} not found")
        
        request = self._consent_requests[request_id]
        
        # Check if request is still pending
        if request.status != ConsentStatus.PENDING:
            logger.error(f"Request {request_id} is not pending (status: {request.status.value})")
            raise ValueError(f"Request is not pending")
        
        # Check if request has expired
        if request.expires_at_ns and datetime.now().timestamp_ns() > request.expires_at_ns:
            request.status = ConsentStatus.EXPIRED
            logger.error(f"Request {request_id} has expired")
            raise ValueError(f"Request has expired")
        
        decision = ConsentDecision(
            request_id=request_id,
            approved=True,
            operator_id=approver_id,
            conditions=conditions,
            reason=reason
        )
        
        # Sign decision
        decision.signature = self._sign_decision(decision)
        
        async with self._lock:
            request.status = ConsentStatus.APPROVED
            request.approved_by = approver_id
            request.approved_at_ns = datetime.now().timestamp_ns()
            self._consent_decisions[request_id] = decision
        
        logger.info(f"Consent granted: {request_id} by {approver_id}")
        
        # Trigger callbacks
        await self._trigger_callbacks(f"consent_granted_{request_id}")
        
        return decision
    
    async def deny_consent(self, request_id: str, approver_id: str,
                          reason: Optional[str] = None) -> ConsentDecision:
        """Deny consent for a request"""
        if request_id not in self._consent_requests:
            logger.error(f"Request {request_id} not found")
            raise ValueError(f"Request {request_id} not found")
        
        request = self._consent_requests[request_id]
        
        decision = ConsentDecision(
            request_id=request_id,
            approved=False,
            operator_id=approver_id,
            reason=reason
        )
        
        async with self._lock:
            request.status = ConsentStatus.REJECTED
            request.rejection_reason = reason
            self._consent_decisions[request_id] = decision
        
        logger.info(f"Consent denied: {request_id} by {approver_id} - reason: {reason}")
        
        # Trigger callbacks
        await self._trigger_callbacks(f"consent_denied_{request_id}")
        
        return decision
    
    async def revoke_consent(self, request_id: str, operator_id: str) -> bool:
        """Revoke previously granted consent"""
        if request_id not in self._consent_requests:
            logger.error(f"Request {request_id} not found")
            return False
        
        request = self._consent_requests[request_id]
        
        async with self._lock:
            request.status = ConsentStatus.REVOKED
        
        logger.info(f"Consent revoked: {request_id} by {operator_id}")
        
        # Trigger callbacks
        await self._trigger_callbacks(f"consent_revoked_{request_id}")
        
        return True
    
    async def get_consent_status(self, request_id: str) -> Optional[ConsentStatus]:
        """Get consent status for a request"""
        request = self._consent_requests.get(request_id)
        return request.status if request else None
    
    async def get_operator(self, operator_id: str) -> Optional[OperatorProfile]:
        """Get operator profile"""
        return self._operators.get(operator_id)
    
    async def get_all_operators(self) -> List[OperatorProfile]:
        """Get all operators"""
        return list(self._operators.values())
    
    async def get_pending_requests(self, operator_id: Optional[str] = None) -> List[ConsentRequest]:
        """Get pending consent requests"""
        pending_requests = [
            req for req in self._consent_requests.values()
            if req.status == ConsentStatus.PENDING
        ]
        
        if operator_id:
            pending_requests = [req for req in pending_requests if req.operator_id == operator_id]
        
        return pending_requests
    
    async def set_governance_policy(self, policy_id: str, policy: Dict[str, Any]) -> bool:
        """Set a governance policy"""
        async with self._lock:
            self._governance_policies[policy_id] = policy
        
        logger.info(f"Set governance policy: {policy_id}")
        
        # Trigger callbacks
        await self._trigger_callbacks(f"policy_set_{policy_id}")
        
        return True
    
    async def get_governance_policy(self, policy_id: str) -> Optional[Dict[str, Any]]:
        """Get governance policy"""
        return self._governance_policies.get(policy_id)
    
    async def start_expiration_check(self):
        """Start consent expiration check loop"""
        if self._consent_expiration_check_active:
            logger.warning("Expiration check already active")
            return
        
        self._consent_expiration_check_active = True
        asyncio.create_task(self._expiration_check_loop())
        logger.info("Consent expiration check started")
    
    async def stop_expiration_check(self):
        """Stop consent expiration check loop"""
        self._consent_expiration_check_active = False
        logger.info("Consent expiration check stopped")
    
    async def _expiration_check_loop(self):
        """Check for expired consent requests"""
        while self._consent_expiration_check_active:
            try:
                current_time = datetime.now().timestamp_ns()
                
                async with self._lock:
                    for request_id, request in self._consent_requests.items():
                        if (request.status == ConsentStatus.PENDING and
                            request.expires_at_ns and
                            current_time > request.expires_at_ns):
                            request.status = ConsentStatus.EXPIRED
                            logger.info(f"Consent request {request_id} expired")
                            await self._trigger_callbacks(f"consent_expired_{request_id}")
                
                await asyncio.sleep(60.0)  # Check every minute
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Expiration check error: {e}")
                await asyncio.sleep(60.0)
    
    async def _check_permission(self, operator_id: str, action: GovernanceAction) -> bool:
        """Check if operator has permission for action"""
        operator = self._operators.get(operator_id)
        if not operator:
            return False
        
        # Admin has all permissions
        if operator.level == OperatorLevel.ADMIN:
            return True
        
        # Supervisor has most permissions
        if operator.level == OperatorLevel.SUPERVISOR:
            return action not in [GovernanceAction.SYSTEM_STOP, GovernanceAction.EMERGENCY_ACTION]
        
        # Operator has basic permissions
        if operator.level == OperatorLevel.OPERATOR:
            return action in [
                GovernanceAction.TRADE_EXECUTION,
                GovernanceAction.STRATEGY_DEPLOYMENT
            ]
        
        # Read-only has no permissions
        return False
    
    def _generate_request_id(self, operator_id: str, action: GovernanceAction) -> str:
        """Generate unique request ID"""
        timestamp = datetime.now().timestamp_ns()
        hash_input = f"{operator_id}_{action.value}_{timestamp}"
        hash_value = hashlib.sha256(hash_input.encode()).hexdigest()[:16]
        return f"req_{hash_value}_{timestamp}"
    
    def _sign_decision(self, decision: ConsentDecision) -> str:
        """Sign consent decision"""
        signature_input = f"{decision.request_id}_{decision.approved}_{decision.operator_id}_{decision.decision_at_ns}"
        return hashlib.sha256(signature_input.encode()).hexdigest()
    
    async def register_callback(self, event: str, callback: Callable):
        """Register callback for governance events"""
        if event not in self._callbacks:
            self._callbacks[event] = []
        self._callbacks[event].append(callback)
    
    async def _trigger_callbacks(self, event: str):
        """Trigger registered callbacks for governance events"""
        if event in self._callbacks:
            for callback in self._callbacks[event]:
                try:
                    await callback(event)
                except Exception as e:
                    logger.error(f"Callback error for {event}: {e}")


# Global operator governance engine instance
_operator_governance_engine = None

def get_operator_governance_engine() -> OperatorGovernanceEngine:
    """Get global operator governance engine instance"""
    global _operator_governance_engine
    if _operator_governance_engine is None:
        _operator_governance_engine = OperatorGovernanceEngine()
    return _operator_governance_engine


__all__ = [
    'OperatorLevel',
    'ConsentStatus',
    'GovernanceAction',
    'ConsentRequest',
    'ConsentDecision',
    'OperatorProfile',
    'OperatorGovernanceEngine',
    'get_operator_governance_engine'
]