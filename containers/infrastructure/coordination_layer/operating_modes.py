"""
coordination_layer.operating_modes
DIX VISION v42.2 — Operating Mode Manager

Manages system operating modes, mode transitions, and mode-specific behaviors.
Addresses critical gap identified in system preservation analysis.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any, Dict, List, Optional, Callable
from abc import ABC, abstractmethod
import threading


class OperatingMode(StrEnum):
    """System operating modes."""
    OFFLINE = "offline"
    PASSIVE = "passive"
    OBSERVATION = "observation"
    SHADOW = "shadow"
    ACTIVE = "active"
    AGGRESSIVE = "aggressive"
    EMERGENCY = "emergency"
    MAINTENANCE = "maintenance"
    DEVELOPMENT = "development"
    CUSTOM = "custom"


class ModeTransitionReason(StrEnum):
    """Reasons for mode transitions."""
    MANUAL = "manual"
    AUTOMATIC = "automatic"
    SCHEDULED = "scheduled"
    CONDITION_TRIGGERED = "condition_triggered"
    ERROR_DETECTED = "error_detected"
    PERFORMANCE_ISSUE = "performance_issue"
    RISK_LIMIT = "risk_limit"
    OPERATOR_REQUEST = "operator_request"
    SYSTEM_INITIATED = "system_initiated"


@dataclass
class ModeCapabilities:
    """Capabilities enabled/disabled in each mode."""
    mode: OperatingMode
    
    # Trading capabilities
    can_trade: bool = False
    can_execute_orders: bool = False
    can_manage_risk: bool = False
    can_analyze_markets: bool = False
    
    # Cognitive capabilities
    can_use_attention: bool = False
    can_form_hypotheses: bool = False
    can_run_investigations: bool = False
    can_learn: bool = False
    
    # System capabilities
    can_modify_config: bool = False
    can_access_external_apis: bool = False
    can_execute_system_commands: bool = False
    can_access_sensitive_data: bool = False
    
    # Performance settings
    max_cpu_usage: float = 1.0  # 0.0 to 1.0
    max_memory_usage: float = 1.0  # 0.0 to 1.0
    max_network_bandwidth: float = 1.0  # 0.0 to 1.0
    
    # Timing constraints
    max_decision_latency_ms: float = 1000.0
    max_analysis_latency_ms: float = 10000.0
    
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ModeTransition:
    """Record of a mode transition."""
    transition_id: str
    from_mode: OperatingMode
    to_mode: OperatingMode
    reason: ModeTransitionReason
    
    # Transition details
    timestamp: datetime = field(default_factory=datetime.utcnow)
    initiator: str = ""  # system, operator, etc.
    conditions: Dict[str, Any] = field(default_factory=dict)
    
    # Transition status
    status: str = "completed"  # pending | in_progress | completed | failed
    duration_ms: float = 0.0
    success: bool = True
    
    # Impact assessment
    affected_components: List[str] = field(default_factory=list)
    performance_impact: str = "none"  # none | low | medium | high
    
    # Rollback information
    can_rollback: bool = True
    rollback_deadline: Optional[datetime] = None
    
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ModePolicy:
    """Policy governing mode behavior and transitions."""
    policy_id: str
    mode: OperatingMode
    
    # Transition policies
    allowed_transitions: List[OperatingMode] = field(default_factory=list)
    forbidden_transitions: List[OperatingMode] = field(default_factory=list)
    transition_conditions: Dict[str, Any] = field(default_factory=dict)
    
    # Time-based policies
    min_duration_seconds: float = 0.0
    max_duration_seconds: float = 0.0  # 0 = no limit
    scheduled_transitions: List[Dict[str, Any]] = field(default_factory=list)
    
    # Condition-based policies
    entry_conditions: List[Dict[str, Any]] = field(default_factory=list)
    exit_conditions: List[Dict[str, Any]] = field(default_factory=list)
    
    # Approval requirements
    requires_approval: bool = False
    required_approvers: List[str] = field(default_factory=list)
    
    # Risk policies
    max_risk_level: str = "medium"  # low | medium | high | extreme
    risk_limits: Dict[str, float] = field(default_factory=dict)
    
    metadata: Dict[str, Any] = field(default_factory=dict)


class OperatingModeManagerInterface(ABC):
    """Interface for operating mode management."""
    
    @abstractmethod
    def get_current_mode(self) -> OperatingMode:
        """Get current operating mode."""
        pass
    
    @abstractmethod
    def transition_to_mode(
        self,
        target_mode: OperatingMode,
        reason: ModeTransitionReason,
        initiator: str = ""
    ) -> ModeTransition:
        """Transition to a new operating mode."""
        pass
    
    @abstractmethod
    def can_transition_to(
        self,
        target_mode: OperatingMode,
        check_policies: bool = True
    ) -> tuple[bool, str]:
        """Check if transition to target mode is allowed."""
        pass
    
    @abstractmethod
    def get_mode_capabilities(self, mode: OperatingMode) -> ModeCapabilities:
        """Get capabilities for a specific mode."""
        pass
    
    @abstractmethod
    def register_mode_policy(self, policy: ModePolicy) -> bool:
        """Register a mode policy."""
        pass
    
    @abstractmethod
    def get_transition_history(self, limit: int = 100) -> List[ModeTransition]:
        """Get history of mode transitions."""
        pass
    
    @abstractmethod
    def check_mode_conditions(self, mode: OperatingMode) -> Dict[str, bool]:
        """Check if conditions for current mode are satisfied."""
        pass


class OperatingModeManager(OperatingModeManagerInterface):
    """Concrete implementation of operating mode management."""
    
    def __init__(self):
        self._lock = threading.Lock()
        
        # Current mode
        self._current_mode = OperatingMode.OFFLINE
        self._mode_since: datetime = datetime.utcnow()
        
        # Mode capabilities
        self._mode_capabilities: Dict[OperatingMode, ModeCapabilities] = {}
        self._initialize_default_capabilities()
        
        # Mode policies
        self._mode_policies: Dict[OperatingMode, ModePolicy] = {}
        self._initialize_default_policies()
        
        # Transition history
        self._transition_history: List[ModeTransition] = []
        
        # Transition hooks
        self._pre_transition_hooks: Dict[OperatingMode, List[Callable]] = {}
        self._post_transition_hooks: Dict[OperatingMode, List[Callable]] = {}
        
        # Current conditions
        self._current_conditions: Dict[str, Any] = {}
    
    def _initialize_default_capabilities(self):
        """Initialize default capabilities for each mode."""
        # OFFLINE mode
        self._mode_capabilities[OperatingMode.OFFLINE] = ModeCapabilities(
            mode=OperatingMode.OFFLINE,
            can_trade=False,
            can_execute_orders=False,
            can_manage_risk=False,
            can_analyze_markets=False,
            can_use_attention=False,
            can_form_hypotheses=False,
            can_run_investigations=False,
            can_learn=False,
            can_modify_config=True,
            can_access_external_apis=False,
            can_execute_system_commands=True,
            can_access_sensitive_data=True
        )
        
        # PASSIVE mode
        self._mode_capabilities[OperatingMode.PASSIVE] = ModeCapabilities(
            mode=OperatingMode.PASSIVE,
            can_trade=False,
            can_execute_orders=False,
            can_manage_risk=True,
            can_analyze_markets=True,
            can_use_attention=True,
            can_form_hypotheses=True,
            can_run_investigations=True,
            can_learn=True,
            can_modify_config=False,
            can_access_external_apis=True,
            can_execute_system_commands=False,
            can_access_sensitive_data=True,
            max_cpu_usage=0.5,
            max_memory_usage=0.5,
            max_decision_latency_ms=1000.0
        )
        
        # OBSERVATION mode
        self._mode_capabilities[OperatingMode.OBSERVATION] = ModeCapabilities(
            mode=OperatingMode.OBSERVATION,
            can_trade=False,
            can_execute_orders=False,
            can_manage_risk=True,
            can_analyze_markets=True,
            can_use_attention=True,
            can_form_hypotheses=True,
            can_run_investigations=True,
            can_learn=True,
            can_modify_config=False,
            can_access_external_apis=True,
            can_execute_system_commands=False,
            can_access_sensitive_data=True,
            max_cpu_usage=0.7,
            max_memory_usage=0.7,
            max_decision_latency_ms=500.0
        )
        
        # SHADOW mode
        self._mode_capabilities[OperatingMode.SHADOW] = ModeCapabilities(
            mode=OperatingMode.SHADOW,
            can_trade=False,
            can_execute_orders=False,
            can_manage_risk=True,
            can_analyze_markets=True,
            can_use_attention=True,
            can_form_hypotheses=True,
            can_run_investigations=True,
            can_learn=True,
            can_modify_config=False,
            can_access_external_apis=True,
            can_execute_system_commands=False,
            can_access_sensitive_data=True,
            max_cpu_usage=0.8,
            max_memory_usage=0.8,
            max_decision_latency_ms=100.0
        )
        
        # ACTIVE mode
        self._mode_capabilities[OperatingMode.ACTIVE] = ModeCapabilities(
            mode=OperatingMode.ACTIVE,
            can_trade=True,
            can_execute_orders=True,
            can_manage_risk=True,
            can_analyze_markets=True,
            can_use_attention=True,
            can_form_hypotheses=True,
            can_run_investigations=True,
            can_learn=True,
            can_modify_config=False,
            can_access_external_apis=True,
            can_execute_system_commands=False,
            can_access_sensitive_data=True,
            max_cpu_usage=0.9,
            max_memory_usage=0.9,
            max_decision_latency_ms=5.0,  # Sub-5ms requirement
            max_analysis_latency_ms=10.0  # Sub-10ms requirement
        )
        
        # AGGRESSIVE mode
        self._mode_capabilities[OperatingMode.AGGRESSIVE] = ModeCapabilities(
            mode=OperatingMode.AGGRESSIVE,
            can_trade=True,
            can_execute_orders=True,
            can_manage_risk=True,
            can_analyze_markets=True,
            can_use_attention=True,
            can_form_hypotheses=True,
            can_run_investigations=True,
            can_learn=True,
            can_modify_config=False,
            can_access_external_apis=True,
            can_execute_system_commands=False,
            can_access_sensitive_data=True,
            max_cpu_usage=1.0,
            max_memory_usage=1.0,
            max_decision_latency_ms=2.0,  # Even faster
            max_analysis_latency_ms=5.0
        )
        
        # EMERGENCY mode
        self._mode_capabilities[OperatingMode.EMERGENCY] = ModeCapabilities(
            mode=OperatingMode.EMERGENCY,
            can_trade=False,
            can_execute_orders=False,
            can_manage_risk=True,
            can_analyze_markets=True,
            can_use_attention=True,
            can_form_hypotheses=False,
            can_run_investigations=False,
            can_learn=False,
            can_modify_config=False,
            can_access_external_apis=True,
            can_execute_system_commands=True,
            can_access_sensitive_data=True,
            max_cpu_usage=1.0,
            max_memory_usage=1.0,
            max_decision_latency_ms=1.0
        )
        
        # MAINTENANCE mode
        self._mode_capabilities[OperatingMode.MAINTENANCE] = ModeCapabilities(
            mode=OperatingMode.MAINTENANCE,
            can_trade=False,
            can_execute_orders=False,
            can_manage_risk=False,
            can_analyze_markets=False,
            can_use_attention=False,
            can_form_hypotheses=False,
            can_run_investigations=False,
            can_learn=False,
            can_modify_config=True,
            can_access_external_apis=False,
            can_execute_system_commands=True,
            can_access_sensitive_data=True
        )
        
        # DEVELOPMENT mode
        self._mode_capabilities[OperatingMode.DEVELOPMENT] = ModeCapabilities(
            mode=OperatingMode.DEVELOPMENT,
            can_trade=True,
            can_execute_orders=True,
            can_manage_risk=True,
            can_analyze_markets=True,
            can_use_attention=True,
            can_form_hypotheses=True,
            can_run_investigations=True,
            can_learn=True,
            can_modify_config=True,
            can_access_external_apis=True,
            can_execute_system_commands=True,
            can_access_sensitive_data=True,
            max_cpu_usage=1.0,
            max_memory_usage=1.0
        )
    
    def _initialize_default_policies(self):
        """Initialize default mode policies."""
        # OFFLINE mode policy
        self._mode_policies[OperatingMode.OFFLINE] = ModePolicy(
            policy_id="offline_policy",
            mode=OperatingMode.OFFLINE,
            allowed_transitions=[
                OperatingMode.PASSIVE,
                OperatingMode.OBSERVATION,
                OperatingMode.MAINTENANCE,
                OperatingMode.DEVELOPMENT
            ],
            requires_approval=False,
            max_risk_level="low"
        )
        
        # ACTIVE mode policy
        self._mode_policies[OperatingMode.ACTIVE] = ModePolicy(
            policy_id="active_policy",
            mode=OperatingMode.ACTIVE,
            forbidden_transitions=[
                OperatingMode.OFFLINE  # Require intermediate step
            ],
            entry_conditions=[
                {"type": "risk_check", "max_level": "high"},
                {"type": "performance_check", "min_score": 0.7}
            ],
            requires_approval=False,
            max_risk_level="medium"
        )
        
        # AGGRESSIVE mode policy
        self._mode_policies[OperatingMode.AGGRESSIVE] = ModePolicy(
            policy_id="aggressive_policy",
            mode=OperatingMode.AGGRESSIVE,
            allowed_transitions=[OperatingMode.ACTIVE],
            requires_approval=True,
            required_approvers=["risk_manager", "operator"],
            max_risk_level="high"
        )
        
        # EMERGENCY mode policy
        self._mode_policies[OperatingMode.EMERGENCY] = ModePolicy(
            policy_id="emergency_policy",
            mode=OperatingMode.EMERGENCY,
            allowed_transitions=[],  # Can enter from any mode in emergency
            requires_approval=False,
            max_risk_level="extreme"
        )
    
    def get_current_mode(self) -> OperatingMode:
        """Get current operating mode."""
        with self._lock:
            return self._current_mode
    
    def transition_to_mode(
        self,
        target_mode: OperatingMode,
        reason: ModeTransitionReason,
        initiator: str = ""
    ) -> ModeTransition:
        """Transition to a new operating mode."""
        with self._lock:
            # Check if transition is allowed
            can_transition, message = self.can_transition_to(target_mode)
            if not can_transition:
                return ModeTransition(
                    transition_id=f"failed_{int(datetime.utcnow().timestamp())}",
                    from_mode=self._current_mode,
                    to_mode=target_mode,
                    reason=reason,
                    status="failed",
                    success=False,
                    initiator=initiator,
                    metadata={"error": message}
                )
            
            # Create transition record
            transition_id = f"transition_{int(datetime.utcnow().timestamp())}"
            transition = ModeTransition(
                transition_id=transition_id,
                from_mode=self._current_mode,
                to_mode=target_mode,
                reason=reason,
                status="in_progress",
                initiator=initiator
            )
            
            # Execute pre-transition hooks
            self._execute_hooks(target_mode, self._pre_transition_hooks)
            
            # Perform transition
            start_time = datetime.utcnow()
            
            try:
                # Update mode
                old_mode = self._current_mode
                self._current_mode = target_mode
                self._mode_since = datetime.utcnow()
                
                # Execute post-transition hooks
                self._execute_hooks(target_mode, self._post_transition_hooks)
                
                # Update transition status
                transition.status = "completed"
                transition.success = True
                transition.duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
                
                # Add to history
                self._transition_history.append(transition)
                
                # Limit history size
                if len(self._transition_history) > 1000:
                    self._transition_history = self._transition_history[-1000:]
                
                return transition
                
            except Exception as e:
                # Rollback on failure
                self._current_mode = old_mode
                transition.status = "failed"
                transition.success = False
                transition.metadata["error"] = str(e)
                return transition
    
    def can_transition_to(
        self,
        target_mode: OperatingMode,
        check_policies: bool = True
    ) -> tuple[bool, str]:
        """Check if transition to target mode is allowed."""
        # Same mode - no transition needed
        if target_mode == self._current_mode:
            return True, "Already in target mode"
        
        # Emergency mode - always allowed
        if target_mode == OperatingMode.EMERGENCY:
            return True, "Emergency mode transition always allowed"
        
        # Check policies if requested
        if check_policies:
            current_policy = self._mode_policies.get(self._current_mode)
            if current_policy:
                # Check forbidden transitions
                if target_mode in current_policy.forbidden_transitions:
                    return False, f"Transition to {target_mode} is forbidden by policy"
                
                # Check allowed transitions (if specified)
                if current_policy.allowed_transitions and target_mode not in current_policy.allowed_transitions:
                    return False, f"Transition to {target_mode} not in allowed transitions"
                
                # Check approval requirements
                if current_policy.requires_approval:
                    return False, f"Transition to {target_mode} requires approval"
        
        return True, "Transition allowed"
    
    def get_mode_capabilities(self, mode: OperatingMode) -> ModeCapabilities:
        """Get capabilities for a specific mode."""
        return self._mode_capabilities.get(mode, ModeCapabilities(mode=mode))
    
    def register_mode_policy(self, policy: ModePolicy) -> bool:
        """Register a mode policy."""
        with self._lock:
            self._mode_policies[policy.mode] = policy
            return True
    
    def get_transition_history(self, limit: int = 100) -> List[ModeTransition]:
        """Get history of mode transitions."""
        with self._lock:
            return self._transition_history[-limit:]
    
    def check_mode_conditions(self, mode: OperatingMode) -> Dict[str, bool]:
        """Check if conditions for current mode are satisfied."""
        conditions = {}
        
        # Get policy for mode
        policy = self._mode_policies.get(mode)
        if policy:
            # Check entry conditions
            for condition in policy.entry_conditions:
                condition_type = condition.get("type", "")
                if condition_type == "risk_check":
                    max_level = condition.get("max_level", "medium")
                    current_risk = self._current_conditions.get("risk_level", "low")
                    conditions[f"risk_check_{max_level}"] = self._risk_level_compare(current_risk, max_level)
                elif condition_type == "performance_check":
                    min_score = condition.get("min_score", 0.7)
                    current_score = self._current_conditions.get("performance_score", 1.0)
                    conditions[f"performance_check_{min_score}"] = current_score >= min_score
        
        return conditions
    
    def _risk_level_compare(self, current: str, max_allowed: str) -> bool:
        """Compare risk levels."""
        risk_levels = ["low", "medium", "high", "extreme"]
        try:
            current_index = risk_levels.index(current.lower())
            max_index = risk_levels.index(max_allowed.lower())
            return current_index <= max_index
        except ValueError:
            return False
    
    def register_pre_transition_hook(self, mode: OperatingMode, hook: Callable) -> None:
        """Register a pre-transition hook for a mode."""
        if mode not in self._pre_transition_hooks:
            self._pre_transition_hooks[mode] = []
        self._pre_transition_hooks[mode].append(hook)
    
    def register_post_transition_hook(self, mode: OperatingMode, hook: Callable) -> None:
        """Register a post-transition hook for a mode."""
        if mode not in self._post_transition_hooks:
            self._post_transition_hooks[mode] = []
        self._post_transition_hooks[mode].append(hook)
    
    def _execute_hooks(self, mode: OperatingMode, hooks_dict: Dict[OperatingMode, List[Callable]]) -> None:
        """Execute hooks for a mode."""
        hooks = hooks_dict.get(mode, [])
        for hook in hooks:
            try:
                hook(mode)
            except Exception as e:
                # Log but don't fail transition
                pass
    
    def update_condition(self, condition_name: str, value: Any) -> None:
        """Update a current condition."""
        with self._lock:
            self._current_conditions[condition_name] = value
    
    def get_mode_report(self) -> Dict[str, Any]:
        """Get comprehensive mode report."""
        with self._lock:
            current_capabilities = self.get_mode_capabilities(self._current_mode)
            condition_check = self.check_mode_conditions(self._current_mode)
            
            return {
                "current_mode": self._current_mode.value,
                "mode_since": self._mode_since.isoformat(),
                "current_capabilities": {
                    "can_trade": current_capabilities.can_trade,
                    "can_execute_orders": current_capabilities.can_execute_orders,
                    "can_manage_risk": current_capabilities.can_manage_risk,
                    "can_analyze_markets": current_capabilities.can_analyze_markets,
                    "can_use_attention": current_capabilities.can_use_attention,
                    "can_form_hypotheses": current_capabilities.can_form_hypotheses,
                    "can_run_investigations": current_capabilities.can_run_investigations,
                    "can_learn": current_capabilities.can_learn,
                    "max_cpu_usage": current_capabilities.max_cpu_usage,
                    "max_memory_usage": current_capabilities.max_memory_usage,
                    "max_decision_latency_ms": current_capabilities.max_decision_latency_ms
                },
                "mode_conditions": condition_check,
                "transition_history_size": len(self._transition_history),
                "recent_transitions": [
                    {
                        "from_mode": t.from_mode.value,
                        "to_mode": t.to_mode.value,
                        "reason": t.reason.value,
                        "timestamp": t.timestamp.isoformat(),
                        "success": t.success,
                        "duration_ms": t.duration_ms
                    }
                    for t in self._transition_history[-10:]
                ]
            }


__all__ = [
    "OperatingMode",
    "ModeTransitionReason",
    "ModeCapabilities",
    "ModeTransition",
    "ModePolicy",
    "OperatingModeManagerInterface",
    "OperatingModeManager",
    "get_operating_mode_manager",
]


# Global instance
_operating_mode_manager: Optional[OperatingModeManager] = None
_mode_lock = threading.Lock()


def get_operating_mode_manager() -> OperatingModeManager:
    """Get global operating mode manager instance."""
    global _operating_mode_manager
    if _operating_mode_manager is None:
        with _mode_lock:
            if _operating_mode_manager is None:
                _operating_mode_manager = OperatingModeManager()
    return _operating_mode_manager