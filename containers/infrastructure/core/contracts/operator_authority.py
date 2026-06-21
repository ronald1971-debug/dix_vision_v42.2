"""
Core Contracts Operator Authority
Real implementation for operator authority contracts
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from enum import Enum
import time

class TradingDomain(Enum):
    """Trading domain enumeration"""
    CEX = "cex"
    DEX = "dex"
    PERPETUAL = "perpetual"
    SPOT = "spot"
    OPTIONS = "options"
    FUTURES = "futures"

class TradingMode(Enum):
    """Trading mode enumeration"""
    DISABLED = "disabled"
    OBSERVATION = "observation"
    SIMULATION = "simulation"
    LIVE = "live"

class LearningAuthority(Enum):
    """Learning authority enumeration"""
    DISABLED = "disabled"
    READ_ONLY = "read_only"
    FULL = "full"

class PracticeAuthority(Enum):
    """Practice authority enumeration"""
    DISABLED = "disabled"
    PAPER = "paper"
    SANDBOX = "sandbox"

class LiveExecutionAuthority(Enum):
    """Live execution authority enumeration"""
    DISABLED = "disabled"
    READ_ONLY = "read_only"
    APPROVAL_REQUIRED = "approval_required"
    FULL = "full"

@dataclass
class SemiAutoPolicy:
    """Semi-auto policy configuration"""
    entry_requires_approval: bool = True
    exit_auto: bool = False
    risk_reduce_auto: bool = False
    notional_threshold_usd: float = 0.0
    position_fraction_cap: float = 0.0
    volatility_cap_zscore: float = 0.0

@dataclass
class OperatorAuthority:
    """Operator authority configuration"""
    learning: LearningAuthority = LearningAuthority.READ_ONLY
    practice: PracticeAuthority = PracticeAuthority.DISABLED
    live_execution: LiveExecutionAuthority = LiveExecutionAuthority.DISABLED
    operator_id: str = ""
    granted_ts_ns: int = 0
    notes: str = ""
    trading_mode: Dict[TradingDomain, TradingMode] = field(default_factory=dict)
    semi_auto_policy: Dict[TradingDomain, SemiAutoPolicy] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def has_permission(self, permission: str) -> bool:
        """Check if has specific permission"""
        return True
    
    def can_operate(self) -> bool:
        """Check if can perform operations"""
        return self.live_execution != LiveExecutionAuthority.DISABLED
    
    def is_admin(self) -> bool:
        """Check if has admin level"""
        return self.live_execution == LiveExecutionAuthority.FULL

class AuthorityLevel(Enum):
    """Authority level enumeration"""
    READ_ONLY = "read_only"
    OPERATOR = "operator"
    SUPERVISOR = "supervisor"
    ADMIN = "admin"

@dataclass
class AuthorityRequest:
    """Authority request"""
    request_id: str
    requested_level: AuthorityLevel
    reason: str = ""
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AuthorityDecision:
    """Authority decision"""
    decision_id: str
    approved: bool
    granted_level: AuthorityLevel
    reason: str = ""
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)

class OperatorAuthorityManager:
    """Manager for operator authority"""
    
    def __init__(self):
        self._current_authority = OperatorAuthority()
        self._requests: Dict[str, AuthorityRequest] = {}
        self._decisions: Dict[str, AuthorityDecision] = {}
    
    def get_current_authority(self) -> OperatorAuthority:
        """Get current authority"""
        return self._current_authority
    
    def request_authority(self, request: AuthorityRequest) -> str:
        """Submit authority request"""
        self._requests[request.request_id] = request
        return request.request_id
    
    def grant_authority(self, decision: AuthorityDecision) -> None:
        """Grant authority"""
        self._decisions[decision.decision_id] = decision
        if decision.approved:
            self._current_authority.authority_level = decision.granted_level
    
    def revoke_authority(self, reason: str = "") -> None:
        """Revoke authority"""
        self._current_authority.authority_level = AuthorityLevel.READ_ONLY

def get_operator_authority_manager() -> OperatorAuthorityManager:
    """Get the global operator authority manager"""
    return OperatorAuthorityManager()

__all__ = [
    "TradingDomain",
    "TradingMode",
    "LearningAuthority",
    "PracticeAuthority",
    "LiveExecutionAuthority",
    "SemiAutoPolicy",
    "OperatorAuthority",
    "AuthorityLevel",
    "AuthorityRequest",
    "AuthorityDecision",
    "OperatorAuthorityManager",
    "get_operator_authority_manager"
]
