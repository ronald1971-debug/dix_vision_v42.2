"""
Core Contracts API Operator
Real implementation for operator API contracts
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, List, Optional
import time

class OperatorStatus(Enum):
    """Operator status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    BUSY = "busy"
    UNAVAILABLE = "unavailable"
    SUSPENDED = "suspended"

class OperatorRole(Enum):
    """Operator role enumeration"""
    ADMINISTRATOR = "administrator"
    OPERATOR = "operator"
    OBSERVER = "observer"
    AUDITOR = "auditor"
    SUPERVISOR = "supervisor"

@dataclass
class Operator:
    """Operator information"""
    operator_id: str
    name: str
    role: OperatorRole
    status: OperatorStatus = OperatorStatus.ACTIVE
    permissions: List[str] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_active(self) -> bool:
        """Check if operator is active"""
        return self.status == OperatorStatus.ACTIVE
    
    def has_permission(self, permission: str) -> bool:
        """Check if operator has permission"""
        return permission in self.permissions
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "operator_id": self.operator_id,
            "name": self.name,
            "role": self.role.value,
            "status": self.status.value,
            "permissions": self.permissions,
            "timestamp": self.timestamp,
            "metadata": self.metadata
        }

@dataclass
class DevelopmentModeRequest:
    """Development mode request information"""
    request_id: str
    operator_id: str
    mode: str
    action: str
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "request_id": self.request_id,
            "operator_id": self.operator_id,
            "mode": self.mode,
            "action": self.action,
            "timestamp": self.timestamp,
            "metadata": self.metadata
        }

@dataclass
class DevelopmentModeResponse:
    """Development mode response information"""
    response_id: str
    request_id: str
    status: str
    message: str = ""
    development_enabled: bool = False
    trading_allowed: bool = False
    mode: str = ""
    learning_unblocked: bool = False
    trading_unblocked: bool = False
    policy_version: str = ""
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "response_id": self.response_id,
            "request_id": self.request_id,
            "status": self.status,
            "message": self.message,
            "development_enabled": self.development_enabled,
            "trading_allowed": self.trading_allowed,
            "mode": self.mode,
            "learning_unblocked": self.learning_unblocked,
            "trading_unblocked": self.trading_unblocked,
            "policy_version": self.policy_version,
            "timestamp": self.timestamp,
            "metadata": self.metadata
        }

@dataclass
class LearningOverrideRequest:
    """Learning override request information"""
    request_id: str
    operator_id: str
    learning_key: str
    override_value: str
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "request_id": self.request_id,
            "operator_id": self.operator_id,
            "learning_key": self.learning_key,
            "override_value": self.override_value,
            "timestamp": self.timestamp,
            "metadata": self.metadata
        }

@dataclass
class LearningOverrideResponse:
    """Learning override response information"""
    response_id: str
    request_id: str
    status: str
    message: str = ""
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "response_id": self.response_id,
            "request_id": self.request_id,
            "status": self.status,
            "message": self.message,
            "timestamp": self.timestamp,
            "metadata": self.metadata
        }

@dataclass
class OperatorActionResponse:
    """Operator action response information"""
    response_id: str
    action: str
    status: str
    message: str = ""
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "response_id": self.response_id,
            "action": self.action,
            "status": self.status,
            "message": self.message,
            "timestamp": self.timestamp,
            "metadata": self.metadata
        }

@dataclass
class ExternalSourceRequest:
    """External source request information"""
    request_id: str
    source_type: str
    source_url: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "request_id": self.request_id,
            "source_type": self.source_type,
            "source_url": self.source_url,
            "parameters": self.parameters,
            "timestamp": self.timestamp,
            "metadata": self.metadata
        }

@dataclass
class LearningProgressResponse:
    """Learning progress response information"""
    response_id: str
    learning_updates: List[str] = field(default_factory=list)
    strategy_improvements: List[str] = field(default_factory=list)
    confidence_deltas: Dict[str, float] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "response_id": self.response_id,
            "learning_updates": self.learning_updates,
            "strategy_improvements": self.strategy_improvements,
            "confidence_deltas": self.confidence_deltas,
            "timestamp": self.timestamp,
            "metadata": self.metadata
        }

@dataclass
class ManualOrderRequest:
    """Manual order request information"""
    request_id: str
    operator_id: str
    order_type: str
    symbol: str
    quantity: float
    price: float = 0.0
    order_side: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "request_id": self.request_id,
            "operator_id": self.operator_id,
            "order_type": self.order_type,
            "symbol": self.symbol,
            "quantity": self.quantity,
            "price": self.price,
            "order_side": self.order_side,
            "parameters": self.parameters,
            "timestamp": self.timestamp,
            "metadata": self.metadata
        }

@dataclass
class OperatorAuthorityRequest:
    """Operator authority request information"""
    request_id: str
    operator_id: str
    requested_level: str
    reason: str = ""
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "request_id": self.request_id,
            "operator_id": self.operator_id,
            "requested_level": self.requested_level,
            "reason": self.reason,
            "timestamp": self.timestamp,
            "metadata": self.metadata
        }

@dataclass
class OperatorAuthorityResponse:
    """Operator authority response information"""
    response_id: str
    request_id: str
    granted: bool
    granted_level: str = ""
    expires_at: float = 0.0
    reason: str = ""
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "response_id": self.response_id,
            "request_id": self.request_id,
            "granted": self.granted,
            "granted_level": self.granted_level,
            "expires_at": self.expires_at,
            "reason": self.reason,
            "timestamp": self.timestamp,
            "metadata": self.metadata
        }

@dataclass
class PromoteBuildoutParamsRequest:
    """Promote buildout params request information"""
    request_id: str
    operator_id: str
    target_engine: str
    params: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "request_id": self.request_id,
            "operator_id": self.operator_id,
            "target_engine": self.target_engine,
            "params": self.params,
            "timestamp": self.timestamp,
            "metadata": self.metadata
        }

@dataclass
class SemiAutoApprovalRequest:
    """Semi-auto approval request information"""
    request_id: str
    operator_id: str
    action_type: str
    action_data: Dict[str, Any] = field(default_factory=dict)
    requires_approval: bool = True
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "request_id": self.request_id,
            "operator_id": self.operator_id,
            "action_type": self.action_type,
            "action_data": self.action_data,
            "requires_approval": self.requires_approval,
            "timestamp": self.timestamp,
            "metadata": self.metadata
        }

@dataclass
class SemiAutoPolicyRequest:
    """Semi-auto policy request information"""
    request_id: str
    operator_id: str
    policy_type: str
    policy_data: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "request_id": self.request_id,
            "operator_id": self.operator_id,
            "policy_type": self.policy_type,
            "policy_data": self.policy_data,
            "timestamp": self.timestamp,
            "metadata": self.metadata
        }

@dataclass
class SemiAutoQueueResponse:
    """Semi-auto approval queue response information"""
    pending: List[Dict[str, Any]] = field(default_factory=list)
    queue_size: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "pending": self.pending,
            "queue_size": self.queue_size
        }

@dataclass
class SemiAutoRejectRequest:
    """Semi-auto rejection request information"""
    request_id: str
    operator_id: str
    approval_id: str
    reason: str = ""
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "request_id": self.request_id,
            "operator_id": self.operator_id,
            "approval_id": self.approval_id,
            "reason": self.reason,
            "timestamp": self.timestamp,
            "metadata": self.metadata
        }

@dataclass
class TradingModeRequest:
    """Trading mode request information"""
    request_id: str
    operator_id: str
    domain: str
    mode: str
    requestor: str = ""
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "request_id": self.request_id,
            "operator_id": self.operator_id,
            "domain": self.domain,
            "mode": self.mode,
            "requestor": self.requestor,
            "timestamp": self.timestamp,
            "metadata": self.metadata
        }

@dataclass
class OperatorAuditRequest:
    """Operator audit request information"""
    request_id: str
    operator_id: str
    audit_type: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "request_id": self.request_id,
            "operator_id": self.operator_id,
            "audit_type": self.audit_type,
            "parameters": self.parameters,
            "timestamp": self.timestamp,
            "metadata": self.metadata
        }

@dataclass
class OperatorAuditResponse:
    """Operator audit response information"""
    response_id: str
    request_id: str
    audit_results: Dict[str, Any] = field(default_factory=dict)
    status: str = ""
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "response_id": self.response_id,
            "request_id": self.request_id,
            "audit_results": self.audit_results,
            "status": self.status,
            "timestamp": self.timestamp,
            "metadata": self.metadata
        }

@dataclass
class OperatorEngineRow:
    """Operator engine row information"""
    engine_name: str
    bucket: str = ""
    detail: str = ""
    plugin_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "engine_name": self.engine_name,
            "bucket": self.bucket,
            "detail": self.detail,
            "plugin_count": self.plugin_count,
        }

@dataclass
class OperatorKillRequest:
    """Operator kill request information"""
    request_id: str
    operator_id: str
    target: str
    reason: str = ""
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "request_id": self.request_id,
            "operator_id": self.operator_id,
            "target": self.target,
            "reason": self.reason,
            "timestamp": self.timestamp,
            "metadata": self.metadata
        }

@dataclass
class OperatorMemecoinSnapshot:
    """Operator memecoin snapshot information"""
    enabled: bool = False
    killed: bool = False
    summary: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "enabled": self.enabled,
            "killed": self.killed,
            "summary": self.summary,
        }

@dataclass
class OperatorModeRequest:
    """Operator mode request information"""
    request_id: str
    operator_id: str
    mode: str
    action: str
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "request_id": self.request_id,
            "operator_id": self.operator_id,
            "mode": self.mode,
            "action": self.action,
            "timestamp": self.timestamp,
            "metadata": self.metadata
        }

@dataclass
class OperatorModeSnapshot:
    """Operator mode snapshot information"""
    current_mode: str
    legal_targets: List[str] = field(default_factory=list)
    is_locked: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "current_mode": self.current_mode,
            "legal_targets": self.legal_targets,
            "is_locked": self.is_locked,
        }

@dataclass
class OperatorStrategyCounts:
    """Operator strategy counts information"""
    proposed: int = 0
    canary: int = 0
    live: int = 0
    retired: int = 0
    failed: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "proposed": self.proposed,
            "canary": self.canary,
            "live": self.live,
            "retired": self.retired,
            "failed": self.failed,
        }

@dataclass
class OperatorSummaryResponse:
    """Operator summary response information"""
    mode: OperatorModeSnapshot
    engines: List[OperatorEngineRow] = field(default_factory=list)
    strategies: OperatorStrategyCounts = field(default_factory=OperatorStrategyCounts)
    memecoin: OperatorMemecoinSnapshot = field(default_factory=OperatorMemecoinSnapshot)
    decision_chain_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "mode": self.mode.to_dict(),
            "engines": [e.to_dict() for e in self.engines],
            "strategies": self.strategies.to_dict(),
            "memecoin": self.memecoin.to_dict(),
            "decision_chain_count": self.decision_chain_count,
        }

@dataclass
class OperatorUnlockRequest:
    """Operator unlock request information"""
    request_id: str
    operator_id: str
    target: str
    reason: str = ""
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "request_id": self.request_id,
            "operator_id": self.operator_id,
            "target": self.target,
            "reason": self.reason,
            "timestamp": self.timestamp,
            "metadata": self.metadata
        }

@dataclass
class TradingAllowedRequest:
    """Trading allowed request information"""
    request_id: str
    operator_id: str
    allowed: bool
    reason: str = ""
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "request_id": self.request_id,
            "operator_id": self.operator_id,
            "allowed": self.allowed,
            "reason": self.reason,
            "timestamp": self.timestamp,
            "metadata": self.metadata
        }

@dataclass
class WalletInfoResponse:
    """Wallet info response information"""
    response_id: str
    wallet_address: str
    balance: float = 0.0
    network: str = ""
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "response_id": self.response_id,
            "wallet_address": self.wallet_address,
            "balance": self.balance,
            "network": self.network,
            "timestamp": self.timestamp,
            "metadata": self.metadata
        }

class OperatorRegistry:
    """Registry for operators"""
    def __init__(self):
        self._operators: Dict[str, Operator] = {}
        self._operators_by_role: Dict[OperatorRole, List[str]] = {
            role: [] for role in OperatorRole
        }
    
    def register_operator(self, operator: Operator) -> bool:
        """Register an operator"""
        self._operators[operator.operator_id] = operator
        self._operators_by_role[operator.role].append(operator.operator_id)
        return True
    
    def get_operator(self, operator_id: str) -> Optional[Operator]:
        """Get a specific operator"""
        return self._operators.get(operator_id)
    
    def get_operators_by_role(self, role: OperatorRole) -> List[Operator]:
        """Get operators by role"""
        operator_ids = self._operators_by_role.get(role, [])
        return [self._operators[oid] for oid in operator_ids if oid in self._operators]
    
    def get_active_operators(self) -> List[Operator]:
        """Get all active operators"""
        return [o for o in self._operators.values() if o.is_active()]

# Global operator registry
_operator_registry: Optional[OperatorRegistry] = None

def get_operator_registry() -> OperatorRegistry:
    """Get the global operator registry"""
    global _operator_registry
    if _operator_registry is None:
        _operator_registry = OperatorRegistry()
    return _operator_registry

__all__ = [
    "OperatorStatus",
    "OperatorRole",
    "Operator",
    "DevelopmentModeRequest",
    "DevelopmentModeResponse",
    "LearningOverrideRequest",
    "LearningOverrideResponse",
    "OperatorActionResponse",
    "ExternalSourceRequest",
    "LearningProgressResponse",
    "ManualOrderRequest",
    "OperatorAuthorityRequest",
    "OperatorAuthorityResponse",
    "PromoteBuildoutParamsRequest",
    "SemiAutoApprovalRequest",
    "SemiAutoPolicyRequest",
    "SemiAutoQueueResponse",
    "SemiAutoRejectRequest",
    "TradingModeRequest",
    "OperatorAuditRequest",
    "OperatorAuditResponse",
    "OperatorEngineRow",
    "OperatorKillRequest",
    "OperatorMemecoinSnapshot",
    "OperatorModeRequest",
    "OperatorModeSnapshot",
    "OperatorStrategyCounts",
    "OperatorSummaryResponse",
    "OperatorUnlockRequest",
    "TradingAllowedRequest",
    "WalletInfoResponse",
    "OperatorRegistry",
    "get_operator_registry"
]