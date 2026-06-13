"""
shared_infrastructure.planning_engine
DIX VISION v42.2 — Planning Engine

Provides planning capabilities for both INDIRA (trading) and DYON (engineering).
Addresses critical gap identified in system preservation analysis.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import StrEnum
from typing import Any, Dict, List, Optional, Callable
from abc import ABC, abstractmethod
import threading


class PlanType(StrEnum):
    """Types of plans."""
    TRADING = "trading"
    PORTFOLIO = "portfolio"
    RISK_MANAGEMENT = "risk_management"
    SYSTEM = "system"
    ENGINEERING = "engineering"
    DEBUGGING = "debugging"
    OPTIMIZATION = "optimization"
    CUSTOM = "custom"


class PlanningHorizon(StrEnum):
    """Planning time horizons."""
    IMMEDIATE = "immediate"  # < 1 hour
    SHORT_TERM = "short_term"  # 1-24 hours
    MEDIUM_TERM = "medium_term"  # 1-7 days
    LONG_TERM = "long_term"  # 1-4 weeks
    STRATEGIC = "strategic"  # 1-12 months


class PlanStatus(StrEnum):
    """Status of plan execution."""
    DRAFT = "draft"
    APPROVED = "approved"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"


@dataclass
class PlanningGoal:
    """A goal for planning."""
    goal_id: str
    goal_type: str  # trading | portfolio | system | engineering
    description: str
    
    # Goal parameters
    target_value: float = 0.0
    current_value: float = 0.0
    tolerance: float = 0.1  # 10% tolerance by default
    
    # Priority and importance
    priority: str = "medium"  # low | medium | high | critical
    importance: float = 0.5  # 0.0 to 1.0
    
    # Time constraints
    deadline: Optional[datetime] = None
    time_sensitive: bool = False
    
    # Dependencies
    depends_on: List[str] = field(default_factory=list)  # Other goal IDs
    blocks: List[str] = field(default_factory=list)  # Goals blocked by this one
    
    # Progress tracking
    progress: float = 0.0  # 0.0 to 1.0
    last_updated: datetime = field(default_factory=datetime.utcnow)
    
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_achieved(self) -> bool:
        """Check if goal is achieved."""
        if self.target_value == 0:
            return False
        return abs(self.current_value - self.target_value) / self.target_value <= self.tolerance
    
    @property
    def is_overdue(self) -> bool:
        """Check if goal is overdue."""
        if self.deadline and self.time_sensitive:
            return datetime.utcnow() > self.deadline
        return False
    
    @property
    def is_blocked(self) -> bool:
        """Check if goal is blocked by unmet dependencies."""
        # This would need dependency resolution logic
        return False


@dataclass
class PlanningConstraint:
    """A constraint for planning."""
    constraint_id: str
    constraint_type: str  # resource | time | risk | regulatory | custom
    
    # Constraint parameters
    min_value: float = 0.0
    max_value: float = 0.0
    target_value: Optional[float] = None
    
    # Constraint scope
    applies_to: List[str] = field(default_factory=list)  # Goal IDs, action IDs
    
    # Constraint strictness
    strictness: str = "soft"  # soft | medium | hard
    
    # Constraint status
    satisfied: bool = True
    violation_reason: str = ""
    
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def check_violation(self, value: float) -> tuple[bool, str]:
        """Check if a value violates the constraint."""
        if self.strictness == "hard":
            if self.min_value > 0 and value < self.min_value:
                return False, f"Value {value} below minimum {self.min_value}"
            if self.max_value > 0 and value > self.max_value:
                return False, f"Value {value} above maximum {self.max_value}"
        elif self.strictness == "medium":
            if self.min_value > 0 and value < self.min_value * 0.9:
                return False, f"Value {value} significantly below minimum {self.min_value}"
            if self.max_value > 0 and value > self.max_value * 1.1:
                return False, f"Value {value} significantly above maximum {self.max_value}"
        
        return True, ""


@dataclass
class PlanningAction:
    """An action in a plan."""
    action_id: str
    action_type: str  # trade | analysis | configuration | system_operation | custom
    
    # Action parameters
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    # Timing
    scheduled_time: Optional[datetime] = None
    estimated_duration_seconds: float = 0.0
    
    # Dependencies
    depends_on: List[str] = field(default_factory=list)  # Other action IDs
    enables: List[str] = field(default_factory=list)  # Actions enabled by this one
    
    # Status
    status: str = "pending"  # pending | in_progress | completed | failed | skipped
    execution_result: Optional[Dict[str, Any]] = None
    
    # Resource requirements
    required_resources: Dict[str, float] = field(default_factory=dict)
    
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_ready(self) -> bool:
        """Check if action is ready to execute."""
        return self.status == "pending" and not self.depends_on
    
    @property
    def is_complete(self) -> bool:
        """Check if action is complete."""
        return self.status in ("completed", "skipped")


@dataclass
class Plan:
    """A comprehensive plan."""
    plan_id: str
    plan_type: PlanType
    horizon: PlanningHorizon
    
    # Plan description
    name: str = ""
    description: str = ""
    
    # Plan components
    goals: List[PlanningGoal] = field(default_factory=list)
    constraints: List[PlanningConstraint] = field(default_factory=list)
    actions: List[PlanningAction] = field(default_factory=list)
    
    # Plan status
    status: PlanStatus = PlanStatus.DRAFT
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Progress tracking
    progress: float = 0.0  # 0.0 to 1.0
    current_action_index: int = 0
    
    # Plan metrics
    total_goals: int = 0
    achieved_goals: int = 0
    total_actions: int = 0
    completed_actions: int = 0
    
    # Plan quality
    estimated_success_probability: float = 0.7
    risk_level: str = "medium"  # low | medium | high
    
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize derived fields."""
        self.total_goals = len(self.goals)
        self.total_actions = len(self.actions)
    
    @property
    def is_active(self) -> bool:
        """Check if plan is currently active."""
        return self.status == PlanStatus.ACTIVE
    
    @property
    def is_complete(self) -> bool:
        """Check if plan is complete."""
        return self.status == PlanStatus.COMPLETED
    
    @property
    def is_failed(self) -> bool:
        """Check if plan has failed."""
        return self.status == PlanStatus.FAILED
    
    @property
    def completion_percentage(self) -> float:
        """Calculate plan completion percentage."""
        if self.total_actions == 0:
            return 0.0
        return (self.completed_actions / self.total_actions) * 100
    
    def update_progress(self) -> None:
        """Update plan progress based on goals and actions."""
        # Update action progress
        self.completed_actions = sum(1 for action in self.actions if action.is_complete)
        
        # Update goal progress
        self.achieved_goals = sum(1 for goal in self.goals if goal.is_achieved)
        
        # Calculate overall progress
        if self.total_goals > 0 and self.total_actions > 0:
            self.progress = (
                (self.achieved_goals / self.total_goals) * 0.4 +
                (self.completed_actions / self.total_actions) * 0.6
            )
        elif self.total_actions > 0:
            self.progress = self.completed_actions / self.total_actions
        elif self.total_goals > 0:
            self.progress = self.achieved_goals / self.total_goals
    
    def get_next_action(self) -> Optional[PlanningAction]:
        """Get the next action to execute."""
        ready_actions = [action for action in self.actions if action.is_ready]
        if ready_actions:
            return ready_actions[0]
        return None
    
    def get_ready_actions(self) -> List[PlanningAction]:
        """Get all actions that are ready to execute."""
        return [action for action in self.actions if action.is_ready]


class PlanningEngineInterface(ABC):
    """Interface for planning engine."""
    
    @abstractmethod
    def create_plan(
        self,
        plan_type: PlanType,
        horizon: PlanningHorizon,
        goals: List[PlanningGoal],
        constraints: List[PlanningConstraint],
        context: Dict[str, Any]
    ) -> Plan:
        """Create a new plan."""
        pass
    
    @abstractmethod
    def execute_plan(self, plan_id: str) -> bool:
        """Execute a plan."""
        pass
    
    @abstractmethod
    def monitor_plan(self, plan_id: str) -> Dict[str, Any]:
        """Monitor plan execution progress."""
        pass
    
    @abstractmethod
    def adjust_plan(
        self,
        plan_id: str,
        adjustments: Dict[str, Any]
    ) -> bool:
        """Adjust an existing plan."""
        pass
    
    @abstractmethod
    def cancel_plan(self, plan_id: str, reason: str = "") -> bool:
        """Cancel a plan."""
        pass
    
    @abstractmethod
    def get_plan(self, plan_id: str) -> Optional[Plan]:
        """Get a plan by ID."""
        pass


class PlanningEngine(PlanningEngineInterface):
    """Concrete implementation of planning engine."""
    
    def __init__(self):
        self._lock = threading.Lock()
        
        # Plan storage
        self._plans: Dict[str, Plan] = {}
        
        # Plan execution
        self._active_plans: Dict[str, Plan] = {}
        
        # Action execution hooks
        self._action_execution_hooks: Dict[str, Callable] = {}
        
        # Planning context
        self._planning_context: Dict[str, Any] = {}
    
    def create_plan(
        self,
        plan_type: PlanType,
        horizon: PlanningHorizon,
        goals: List[PlanningGoal],
        constraints: List[PlanningConstraint],
        context: Dict[str, Any]
    ) -> Plan:
        """Create a new plan."""
        plan_id = f"plan_{plan_type.value}_{int(datetime.utcnow().timestamp())}"
        
        # Generate actions from goals
        actions = self._generate_actions_from_goals(goals, context)
        
        # Validate constraints
        validated_constraints = self._validate_constraints(constraints, context)
        
        # Calculate estimated success probability
        success_probability = self._calculate_success_probability(goals, constraints, context)
        
        # Create plan
        plan = Plan(
            plan_id=plan_id,
            plan_type=plan_type,
            horizon=horizon,
            goals=goals,
            constraints=validated_constraints,
            actions=actions,
            estimated_success_probability=success_probability,
            metadata=context
        )
        
        with self._lock:
            self._plans[plan_id] = plan
        
        return plan
    
    def _generate_actions_from_goals(
        self,
        goals: List[PlanningGoal],
        context: Dict[str, Any]
    ) -> List[PlanningAction]:
        """Generate actions from planning goals."""
        actions = []
        
        for i, goal in enumerate(goals):
            # Generate action based on goal type
            if goal.goal_type == "trading":
                action = PlanningAction(
                    action_id=f"action_{goal.goal_id}",
                    action_type="trade",
                    parameters={
                        "goal_id": goal.goal_id,
                        "target_value": goal.target_value,
                        "current_value": goal.current_value
                    },
                    scheduled_time=datetime.utcnow() + timedelta(minutes=i * 5),
                    depends_on=[]
                )
            elif goal.goal_type == "system":
                action = PlanningAction(
                    action_id=f"action_{goal.goal_id}",
                    action_type="system_operation",
                    parameters={
                        "goal_id": goal.goal_id,
                        "operation": goal.description
                    },
                    scheduled_time=datetime.utcnow() + timedelta(minutes=i * 10),
                    depends_on=[]
                )
            elif goal.goal_type == "engineering":
                action = PlanningAction(
                    action_id=f"action_{goal.goal_id}",
                    action_type="analysis",
                    parameters={
                        "goal_id": goal.goal_id,
                        "analysis_type": goal.description
                    },
                    scheduled_time=datetime.utcnow() + timedelta(minutes=i * 15),
                    depends_on=[]
                )
            else:
                # Generic action
                action = PlanningAction(
                    action_id=f"action_{goal.goal_id}",
                    action_type="custom",
                    parameters={
                        "goal_id": goal.goal_id,
                        "description": goal.description
                    },
                    scheduled_time=datetime.utcnow() + timedelta(minutes=i * 5),
                    depends_on=[]
                )
            
            # Add dependencies if goal has dependencies
            if goal.depends_on:
                action.depends_on = [f"action_{dep}" for dep in goal.depends_on]
            
            actions.append(action)
        
        return actions
    
    def _validate_constraints(
        self,
        constraints: List[PlanningConstraint],
        context: Dict[str, Any]
    ) -> List[PlanningConstraint]:
        """Validate planning constraints."""
        validated = []
        
        for constraint in constraints:
            # Check constraint against context
            is_valid, reason = constraint.check_violation(
                context.get(constraint.constraint_type, 0.0)
            )
            constraint.satisfied = is_valid
            constraint.violation_reason = reason
            validated.append(constraint)
        
        return validated
    
    def _calculate_success_probability(
        self,
        goals: List[PlanningGoal],
        constraints: List[PlanningConstraint],
        context: Dict[str, Any]
    ) -> float:
        """Calculate estimated success probability for the plan."""
        # Base probability
        probability = 0.7
        
        # Adjust based on goal difficulty
        avg_importance = sum(g.importance for g in goals) / len(goals) if goals else 0.5
        probability += (avg_importance - 0.5) * 0.2
        
        # Adjust based on constraint satisfaction
        satisfied_ratio = sum(1 for c in constraints if c.satisfied) / len(constraints) if constraints else 1.0
        probability *= satisfied_ratio
        
        # Adjust based on time sensitivity
        time_sensitive_goals = sum(1 for g in goals if g.time_sensitive)
        if time_sensitive_goals > 0:
            probability -= 0.1 * (time_sensitive_goals / len(goals))
        
        # Ensure probability is in valid range
        return max(0.1, min(0.95, probability))
    
    def execute_plan(self, plan_id: str) -> bool:
        """Execute a plan."""
        with self._lock:
            plan = self._plans.get(plan_id)
            if not plan:
                return False
            
            # Activate plan
            plan.status = PlanStatus.ACTIVE
            plan.started_at = datetime.utcnow()
            self._active_plans[plan_id] = plan
            
            # Start execution loop (simplified for now)
            return self._execute_plan_step(plan)
    
    def _execute_plan_step(self, plan: Plan) -> bool:
        """Execute one step of the plan."""
        # Get next action
        action = plan.get_next_action()
        if not action:
            # No more actions, plan complete
            plan.status = PlanStatus.COMPLETED
            plan.completed_at = datetime.utcnow()
            plan.update_progress()
            return True
        
        # Execute action
        action.status = "in_progress"
        
        # Try to execute action via hook or default handler
        execution_hook = self._action_execution_hooks.get(action.action_type)
        if execution_hook:
            try:
                result = execution_hook(action)
                action.execution_result = {"success": True, "result": result}
                action.status = "completed"
            except Exception as e:
                action.execution_result = {"success": False, "error": str(e)}
                action.status = "failed"
                # Plan failed on action failure
                plan.status = PlanStatus.FAILED
                return False
        else:
            # Default handler - mark as completed
            action.status = "completed"
            action.execution_result = {"success": True, "message": "No handler, auto-completed"}
        
        # Update plan progress
        plan.update_progress()
        
        return True
    
    def monitor_plan(self, plan_id: str) -> Dict[str, Any]:
        """Monitor plan execution progress."""
        with self._lock:
            plan = self._plans.get(plan_id)
            if not plan:
                return {"error": "Plan not found"}
            
            plan.update_progress()
            
            return {
                "plan_id": plan.plan_id,
                "plan_type": plan.plan_type.value,
                "status": plan.status.value,
                "progress": plan.progress,
                "completion_percentage": plan.completion_percentage,
                "goals": {
                    "total": plan.total_goals,
                    "achieved": plan.achieved_goals
                },
                "actions": {
                    "total": plan.total_actions,
                    "completed": plan.completed_actions,
                    "current_action": plan.get_next_action().action_id if plan.get_next_action() else None
                },
                "estimated_success_probability": plan.estimated_success_probability,
                "risk_level": plan.risk_level,
                "started_at": plan.started_at.isoformat() if plan.started_at else None,
                "completed_at": plan.completed_at.isoformat() if plan.completed_at else None
            }
    
    def adjust_plan(
        self,
        plan_id: str,
        adjustments: Dict[str, Any]
    ) -> bool:
        """Adjust an existing plan."""
        with self._lock:
            plan = self._plans.get(plan_id)
            if not plan:
                return False
            
            # Apply adjustments
            if "add_goals" in adjustments:
                plan.goals.extend(adjustments["add_goals"])
                plan.total_goals = len(plan.goals)
            
            if "add_actions" in adjustments:
                plan.actions.extend(adjustments["add_actions"])
                plan.total_actions = len(plan.actions)
            
            if "modify_goal" in adjustments:
                goal_id = adjustments["modify_goal"]["goal_id"]
                for goal in plan.goals:
                    if goal.goal_id == goal_id:
                        for key, value in adjustments["modify_goal"].items():
                            if key != "goal_id":
                                setattr(goal, key, value)
            
            if "modify_constraint" in adjustments:
                constraint_id = adjustments["modify_constraint"]["constraint_id"]
                for constraint in plan.constraints:
                    if constraint.constraint_id == constraint_id:
                        for key, value in adjustments["modify_constraint"].items():
                            if key != "constraint_id":
                                setattr(constraint, key, value)
            
            # Update plan metadata
            plan.metadata.update(adjustments.get("metadata", {}))
            
            return True
    
    def cancel_plan(self, plan_id: str, reason: str = "") -> bool:
        """Cancel a plan."""
        with self._lock:
            plan = self._plans.get(plan_id)
            if not plan:
                return False
            
            plan.status = PlanStatus.CANCELLED
            if plan_id in self._active_plans:
                del self._active_plans[plan_id]
            
            plan.metadata["cancellation_reason"] = reason
            plan.metadata["cancelled_at"] = datetime.utcnow().isoformat()
            
            return True
    
    def get_plan(self, plan_id: str) -> Optional[Plan]:
        """Get a plan by ID."""
        with self._lock:
            return self._plans.get(plan_id)
    
    def register_action_hook(self, action_type: str, hook: Callable) -> None:
        """Register a hook for executing specific action types."""
        self._action_execution_hooks[action_type] = hook
    
    def get_planning_report(self) -> Dict[str, Any]:
        """Get comprehensive planning report."""
        with self._lock:
            total_plans = len(self._plans)
            active_plans = len(self._active_plans)
            completed_plans = sum(1 for p in self._plans.values() if p.is_complete)
            failed_plans = sum(1 for p in self._plans.values() if p.is_failed)
            
            return {
                "summary": {
                    "total_plans": total_plans,
                    "active_plans": active_plans,
                    "completed_plans": completed_plans,
                    "failed_plans": failed_plans,
                    "success_rate": (completed_plans / total_plans * 100) if total_plans > 0 else 0
                },
                "active_plans": [
                    {
                        "plan_id": plan.plan_id,
                        "plan_type": plan.plan_type.value,
                        "progress": plan.progress,
                        "status": plan.status.value
                    }
                    for plan in self._active_plans.values()
                ],
                "recent_plans": [
                    {
                        "plan_id": plan.plan_id,
                        "plan_type": plan.plan_type.value,
                        "status": plan.status.value,
                        "completion_percentage": plan.completion_percentage,
                        "created_at": plan.created_at.isoformat()
                    }
                    for plan in list(self._plans.values())[-10:]
                ]
            }


# Global instance
_planning_engine: Optional[PlanningEngine] = None
_planning_lock = threading.Lock()


def get_planning_engine() -> PlanningEngine:
    """Get global planning engine instance."""
    global _planning_engine
    if _planning_engine is None:
        with _planning_lock:
            if _planning_engine is None:
                _planning_engine = PlanningEngine()
    return _planning_engine


__all__ = [
    "PlanType",
    "PlanningHorizon",
    "PlanStatus",
    "PlanningGoal",
    "PlanningConstraint",
    "PlanningAction",
    "Plan",
    "PlanningEngineInterface",
    "PlanningEngine",
    "get_planning_engine",
]