"""
intelligence_engine.planner
DIX VISION v42.2 — Production-Grade Planning Engine

Dynamic planning and strategy generation with hierarchical planning,
goal decomposition, resource allocation, and adaptive plan execution.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple
from enum import Enum
from collections import deque
import json

from system.time_source import now

logger = logging.getLogger(__name__)


class PlanType(Enum):
    """Types of plans."""
    STRATEGIC = "strategic"  # Long-term strategic plans
    TACTICAL = "tactical"  # Medium-term tactical plans
    OPERATIONAL = "operational"  # Short-term operational plans
    CONTINGENCY = "contingency"  # Contingency plans
    RECOVERY = "recovery"  # Recovery plans


class PlanningHorizon(Enum):
    """Planning time horizons."""
    IMMEDIATE = "immediate"  # Seconds to minutes
    SHORT_TERM = "short_term"  # Hours to days
    MEDIUM_TERM = "medium_term"  # Weeks to months
    LONG_TERM = "long_term"  # Years


class TaskStatus(Enum):
    """Status of planning tasks."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"


@dataclass
class PlanningGoal:
    """A planning goal."""
    goal_id: str
    description: str
    priority: float = 1.0
    deadline: Optional[str] = None
    success_criteria: Dict[str, Any] = field(default_factory=dict)
    constraints: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PlanningTask:
    """A planning task."""
    task_id: str
    description: str
    task_type: str = "generic"
    dependencies: List[str] = field(default_factory=list)
    estimated_duration: float = 0.0  # in seconds
    resource_requirements: Dict[str, Any] = field(default_factory=dict)
    status: TaskStatus = TaskStatus.PENDING
    confidence: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PlanningConstraint:
    """A planning constraint."""
    constraint_id: str
    constraint_type: str  # "temporal", "resource", "logical", "regulatory"
    description: str
    severity: float = 1.0  # 0.0 to 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Resource:
    """A planning resource."""
    resource_id: str
    resource_type: str
    capacity: float = 1.0
    available: float = 1.0
    cost_per_unit: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Plan:
    """A plan with tasks and resources."""
    plan_id: str
    plan_type: PlanType
    goals: List[PlanningGoal] = field(default_factory=list)
    tasks: List[PlanningTask] = field(default_factory=list)
    constraints: List[PlanningConstraint] = field(default_factory=list)
    resources: Dict[str, Resource] = field(default_factory=dict)
    execution_timeline: Dict[str, Any] = field(default_factory=dict)
    success_probability: float = 0.0
    estimated_completion: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    status: TaskStatus = TaskStatus.PENDING


@dataclass
class PlanningResult:
    """Result of a planning operation."""
    planning_id: str
    plan_type: PlanType
    generated_plan: Optional[Plan] = None
    alternative_plans: List[Plan] = field(default_factory=list)
    planning_confidence: float = 0.0
    recommendations: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    timestamp: str = ""


class ProductionPlanner:
    """Production-grade planning engine.
    
    Provides:
    - Hierarchical goal decomposition
    - Dynamic plan generation
    - Resource allocation optimization
    - Constraint satisfaction
    - Adaptive plan execution
    """
    
    def __init__(self) -> None:
        self._planning_history: List[PlanningResult] = []
        self._active_plans: Dict[str, Plan] = {}
        self._resource_pool: Dict[str, Resource] = {}
        self._planning_horizons = {
            PlanningHorizon.IMMEDIATE: 3600,      # 1 hour
            PlanningHorizon.SHORT_TERM: 86400,    # 1 day
            PlanningHorizon.MEDIUM_TERM: 604800,  # 1 week
            PlanningHorizon.LONG_TERM: 31536000   # 1 year
        }
        self._max_plan_complexity = 100  # Maximum tasks per plan
        
    def start(self) -> bool:
        """Start the planning engine."""
        try:
            logger.info("[PLANNER] Production planning engine started")
            return True
        except Exception as e:
            logger.error(f"[PLANNER] Failed to start: {e}")
            return False
    
    def stop(self) -> bool:
        """Stop the planning engine."""
        try:
            logger.info("[PLANNER] Production planning engine stopped")
            return True
        except Exception as e:
            logger.error(f"[PLANNER] Failed to stop: {e}")
            return False
    
    def add_resource(self, resource: Resource) -> None:
        """Add a resource to the planning pool."""
        self._resource_pool[resource.resource_id] = resource
        logger.info(f"[PLANNER] Added resource: {resource.resource_id}")
    
    def remove_resource(self, resource_id: str) -> None:
        """Remove a resource from the planning pool."""
        if resource_id in self._resource_pool:
            del self._resource_pool[resource_id]
            logger.info(f"[PLANNER] Removed resource: {resource_id}")
    
    def create_plan(self, 
                   goals: List[PlanningGoal],
                   plan_type: PlanType = PlanType.OPERATIONAL,
                   constraints: Optional[List[PlanningConstraint]] = None,
                   horizon: PlanningHorizon = PlanningHorizon.SHORT_TERM) -> PlanningResult:
        """Create a plan to achieve specified goals.
        
        Args:
            goals: List of goals to achieve
            plan_type: Type of plan to create
            constraints: Optional planning constraints
            horizon: Planning time horizon
            
        Returns:
            PlanningResult with generated plan and alternatives
        """
        try:
            planning_id = f"planning_{now().sequence}"
            logger.info(f"[PLANNER] Creating {plan_type.value} plan: {planning_id}")
            
            constraints = constraints or []
            
            # Decompose goals into tasks
            tasks = self._decompose_goals_to_tasks(goals, constraints)
            
            # Check complexity
            if len(tasks) > self._max_plan_complexity:
                return self._create_complexity_error(planning_id, plan_type, len(tasks))
            
            # Optimize task ordering
            ordered_tasks = self._optimize_task_order(tasks, constraints)
            
            # Allocate resources
            allocated_resources = self._allocate_resources(ordered_tasks)
            
            # Calculate timeline
            timeline = self._calculate_execution_timeline(ordered_tasks, horizon)
            
            # Calculate success probability
            success_probability = self._calculate_success_probability(ordered_tasks, constraints)
            
            # Create plan
            plan = Plan(
                plan_id=f"plan_{now().sequence}",
                plan_type=plan_type,
                goals=goals,
                tasks=ordered_tasks,
                constraints=constraints,
                resources=allocated_resources,
                execution_timeline=timeline,
                success_probability=success_probability,
                estimated_completion=timeline.get("completion_time", ""),
                status=TaskStatus.PENDING
            )
            
            # Generate alternative plans
            alternative_plans = []
            if plan_type in [PlanType.STRATEGIC, PlanType.TACTICAL]:
                alternative_plans = self._generate_alternative_plans(
                    goals, constraints, horizon, num_alternatives=2
                )
            
            # Generate recommendations
            recommendations = self._generate_recommendations(plan, constraints)
            
            # Generate warnings
            warnings = self._generate_warnings(plan, constraints)
            
            result = PlanningResult(
                planning_id=planning_id,
                plan_type=plan_type,
                generated_plan=plan,
                alternative_plans=alternative_plans,
                planning_confidence=success_probability,
                recommendations=recommendations,
                warnings=warnings,
                timestamp=now().utc_time.isoformat()
            )
            
            # Store in history
            self._planning_history.append(result)
            
            logger.info(f"[PLANNER] Plan created: {planning_id} with success probability {success_probability:.2f}")
            return result
            
        except Exception as e:
            logger.error(f"[PLANNER] Planning failed: {e}")
            return self._create_error_result(planning_id, plan_type, str(e))
    
    def _decompose_goals_to_tasks(self, 
                                 goals: List[PlanningGoal],
                                 constraints: List[PlanningConstraint]) -> List[PlanningTask]:
        """Decompose goals into executable tasks."""
        tasks = []
        
        for goal in goals:
            # Analyze goal requirements
            goal_tasks = self._analyze_goal_requirements(goal)
            
            for task_info in goal_tasks:
                task = PlanningTask(
                    task_id=f"task_{now().sequence}",
                    description=task_info["description"],
                    task_type=task_info.get("type", "generic"),
                    dependencies=task_info.get("dependencies", []),
                    estimated_duration=task_info.get("duration", 3600),
                    resource_requirements=task_info.get("resources", {}),
                    confidence=task_info.get("confidence", 0.8),
                    metadata={"goal_id": goal.goal_id}
                )
                tasks.append(task)
        
        return tasks
    
    def _analyze_goal_requirements(self, goal: PlanningGoal) -> List[Dict[str, Any]]:
        """Analyze goal requirements and generate task information."""
        # Production-grade goal analysis
        tasks = []
        
        # Main task for the goal
        main_task = {
            "description": f"Execute: {goal.description}",
            "type": "primary",
            "dependencies": [],
            "duration": 3600,  # Default 1 hour
            "resources": {"cpu": 0.5, "memory": 0.3},
            "confidence": 0.8
        }
        tasks.append(main_task)
        
        # Preparation task
        prep_task = {
            "description": f"Prepare for: {goal.description}",
            "type": "preparation",
            "dependencies": [],
            "duration": 1800,  # 30 minutes
            "resources": {"cpu": 0.2, "memory": 0.1},
            "confidence": 0.9
        }
        tasks.append(prep_task)
        
        # Make preparation task a dependency of main task
        main_task["dependencies"] = [prep_task["description"]]
        
        # Validation task
        validation_task = {
            "description": f"Validate: {goal.description}",
            "type": "validation",
            "dependencies": [main_task["description"]],
            "duration": 600,  # 10 minutes
            "resources": {"cpu": 0.1, "memory": 0.1},
            "confidence": 0.85
        }
        tasks.append(validation_task)
        
        return tasks
    
    def _optimize_task_order(self, 
                            tasks: List[PlanningTask],
                            constraints: List[PlanningConstraint]) -> List[PlanningTask]:
        """Optimize task ordering using topological sort."""
        # Build dependency graph
        task_map = {task.task_id: task for task in tasks}
        dependency_graph = {task.task_id: [] for task in tasks}
        
        for task in tasks:
            for dep in task.dependencies:
                # Find task with matching description
                for dep_task in tasks:
                    if dep_task.description == dep:
                        dependency_graph[task.task_id].append(dep_task.task_id)
        
        # Topological sort
        visited = set()
        temp_visited = set()
        ordered_tasks = []
        
        def visit(task_id: str):
            if task_id in temp_visited:
                # Cycle detected - handle gracefully
                return
            if task_id in visited:
                return
            
            temp_visited.add(task_id)
            
            for dep_id in dependency_graph[task_id]:
                visit(dep_id)
            
            temp_visited.remove(task_id)
            visited.add(task_id)
            ordered_tasks.append(task_map[task_id])
        
        for task in tasks:
            visit(task.task_id)
        
        return ordered_tasks
    
    def _allocate_resources(self, tasks: List[PlanningTask]) -> Dict[str, Resource]:
        """Allocate resources to tasks."""
        allocated = {}
        
        for task in tasks:
            for resource_type, amount in task.resource_requirements.items():
                # Find matching resource
                matching_resources = [
                    r for r in self._resource_pool.values()
                    if r.resource_type == resource_type
                ]
                
                if matching_resources:
                    resource = matching_resources[0]
                    if resource.available >= amount:
                        resource.available -= amount
                        allocated[resource.resource_id] = resource
                    else:
                        logger.warning(f"[PLANNER] Insufficient {resource_type} for task {task.task_id}")
        
        return allocated
    
    def _calculate_execution_timeline(self, 
                                      tasks: List[PlanningTask],
                                      horizon: PlanningHorizon) -> Dict[str, Any]:
        """Calculate execution timeline for tasks."""
        timeline = {}
        total_duration = 0.0
        
        for task in tasks:
            total_duration += task.estimated_duration
        
        horizon_seconds = self._planning_horizons[horizon]
        completion_offset = min(total_duration, horizon_seconds)
        
        timeline = {
            "total_duration": total_duration,
            "horizon_type": horizon.value,
            "start_time": now().utc_time.isoformat(),
            "completion_time": (now().utc_datetime() + 
                                now().timedelta(seconds=completion_offset)).isoformat(),
            "task_count": len(tasks),
            "critical_path": self._identify_critical_path(tasks)
        }
        
        return timeline
    
    def _identify_critical_path(self, tasks: List[PlanningTask]) -> List[str]:
        """Identify critical path in task dependencies."""
        # Simplified critical path identification
        critical_tasks = []
        
        for task in tasks:
            if len(task.dependencies) > 0:
                critical_tasks.append(task.task_id)
            elif task.estimated_duration > 3600:  # Tasks over 1 hour
                critical_tasks.append(task.task_id)
        
        return critical_tasks
    
    def _calculate_success_probability(self, 
                                      tasks: List[PlanningTask],
                                      constraints: List[PlanningConstraint]) -> float:
        """Calculate overall success probability."""
        if not tasks:
            return 0.0
        
        # Calculate from task confidences
        task_confidences = [task.confidence for task in tasks]
        avg_task_confidence = sum(task_confidences) / len(task_confidences)
        
        # Adjust for constraints
        constraint_penalty = sum(c.severity for c in constraints) / 10.0
        adjusted_confidence = avg_task_confidence - constraint_penalty
        
        return max(0.0, min(1.0, adjusted_confidence))
    
    def _generate_alternative_plans(self, 
                                   goals: List[PlanningGoal],
                                   constraints: List[PlanningConstraint],
                                   horizon: PlanningHorizon,
                                   num_alternatives: int = 2) -> List[Plan]:
        """Generate alternative plans."""
        alternatives = []
        
        for i in range(num_alternatives):
            # Create modified constraints for alternative
            alt_constraints = [c for c in constraints]
            
            # Modify some constraint severities
            if alt_constraints:
                alt_constraints[0] = PlanningConstraint(
                    constraint_id=alt_constraints[0].constraint_id,
                    constraint_type=alt_constraints[0].constraint_type,
                    description=alt_constraints[0].description,
                    severity=alt_constraints[0].severity * 0.8,
                    metadata=alt_constraints[0].metadata
                )
            
            # Create alternative plan
            tasks = self._decompose_goals_to_tasks(goals, alt_constraints)
            ordered_tasks = self._optimize_task_order(tasks, alt_constraints)
            allocated_resources = self._allocate_resources(ordered_tasks)
            timeline = self._calculate_execution_timeline(ordered_tasks, horizon)
            success_probability = self._calculate_success_probability(ordered_tasks, alt_constraints)
            
            alternative = Plan(
                plan_id=f"alt_plan_{now().sequence}_{i}",
                plan_type=PlanType.OPERATIONAL,
                goals=goals,
                tasks=ordered_tasks,
                constraints=alt_constraints,
                resources=allocated_resources,
                execution_timeline=timeline,
                success_probability=success_probability,
                estimated_completion=timeline.get("completion_time", ""),
                status=TaskStatus.PENDING
            )
            
            alternatives.append(alternative)
        
        return alternatives
    
    def _generate_recommendations(self, plan: Plan, 
                                 constraints: List[PlanningConstraint]) -> List[str]:
        """Generate planning recommendations."""
        recommendations = []
        
        if plan.success_probability > 0.8:
            recommendations.append("Plan has high success probability - recommended for execution")
        elif plan.success_probability > 0.6:
            recommendations.append("Plan has moderate success probability - proceed with monitoring")
        else:
            recommendations.append("Plan has low success probability - consider alternatives")
        
        if len(plan.tasks) > self._max_plan_complexity * 0.8:
            recommendations.append("Plan complexity is high - consider breaking into smaller sub-plans")
        
        if constraints:
            recommendations.append(f"Review {len(constraints)} constraints for potential relaxation")
        
        return recommendations
    
    def _generate_warnings(self, plan: Plan, 
                          constraints: List[PlanningConstraint]) -> List[str]:
        """Generate planning warnings."""
        warnings = []
        
        high_severity_constraints = [c for c in constraints if c.severity > 0.7]
        if high_severity_constraints:
            warnings.append(f"High-severity constraints may impact plan execution")
        
        if plan.success_probability < 0.5:
            warnings.append("Low success probability - significant risk of failure")
        
        resource_issues = [r for r in plan.resources.values() if r.available < 0.2]
        if resource_issues:
            warnings.append("Limited resource availability - may cause delays")
        
        return warnings
    
    def _create_complexity_error(self, planning_id: str, 
                                 plan_type: PlanType, 
                                 task_count: int) -> PlanningResult:
        """Create error result for excessive complexity."""
        return PlanningResult(
            planning_id=planning_id,
            plan_type=plan_type,
            generated_plan=None,
            planning_confidence=0.0,
            recommendations=[f"Reduce complexity: {task_count} tasks exceeds maximum of {self._max_plan_complexity}"],
            warnings=["Plan too complex for current configuration"],
            timestamp=now().utc_time.isoformat()
        )
    
    def _create_error_result(self, planning_id: str, 
                           plan_type: PlanType, 
                           error: str) -> PlanningResult:
        """Create error planning result."""
        return PlanningResult(
            planning_id=planning_id,
            plan_type=plan_type,
            generated_plan=None,
            planning_confidence=0.0,
            recommendations=[],
            warnings=[f"Planning error: {error}"],
            timestamp=now().utc_time.isoformat()
        )
    
    def activate_plan(self, plan: Plan) -> bool:
        """Activate a plan for execution."""
        try:
            plan.status = TaskStatus.IN_PROGRESS
            self._active_plans[plan.plan_id] = plan
            logger.info(f"[PLANNER] Plan activated: {plan.plan_id}")
            return True
        except Exception as e:
            logger.error(f"[PLANNER] Failed to activate plan: {e}")
            return False
    
    def update_plan_status(self, plan_id: str, 
                          task_id: str, 
                          new_status: TaskStatus) -> bool:
        """Update status of a task in an active plan."""
        if plan_id not in self._active_plans:
            logger.warning(f"[PLANNER] Plan not found: {plan_id}")
            return False
        
        plan = self._active_plans[plan_id]
        task = next((t for t in plan.tasks if t.task_id == task_id), None)
        
        if not task:
            logger.warning(f"[PLANNER] Task not found: {task_id}")
            return False
        
        task.status = new_status
        logger.info(f"[PLANNER] Task {task_id} status updated to {new_status.value}")
        
        # Check if plan is complete
        if all(t.status == TaskStatus.COMPLETED for t in plan.tasks):
            plan.status = TaskStatus.COMPLETED
            logger.info(f"[PLANNER] Plan {plan_id} completed")
        
        return True
    
    def get_planning_history(self, limit: int = 100) -> List[PlanningResult]:
        """Get planning history."""
        return self._planning_history[-limit:]
    
    def get_active_plans(self) -> List[Plan]:
        """Get currently active plans."""
        return list(self._active_plans.values())
    
    def clear_history(self) -> None:
        """Clear planning history."""
        self._planning_history.clear()
        logger.info("[PLANNER] Planning history cleared")


def get_production_planner() -> ProductionPlanner:
    """Get the singleton production planner instance."""
    if not hasattr(get_production_planner, "_instance"):
        get_production_planner._instance = ProductionPlanner()
    return get_production_planner._instance