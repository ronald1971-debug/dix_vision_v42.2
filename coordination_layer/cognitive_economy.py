"""
coordination_layer.cognitive_economy
DIX VISION v42.2 — Cognitive Economy Manager

Manages cognitive resource economics, cost-benefit analysis, and resource optimization.
Addresses critical gap identified in system preservation analysis.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any, Dict, List, Optional
from abc import ABC, abstractmethod


class CognitiveResourceType(StrEnum):
    """Types of cognitive resources."""
    ATTENTION = "attention"
    MEMORY = "memory"
    COMPUTATION = "computation"
    REASONING = "reasoning"
    LEARNING = "learning"
    SIMULATION = "simulation"
    CUSTOM = "custom"


class CognitiveOperationPriority(StrEnum):
    """Priority levels for cognitive operations."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    BACKGROUND = "background"


@dataclass
class CognitiveCost:
    """Cost analysis for a cognitive operation."""
    operation_id: str
    resource_type: CognitiveResourceType
    
    # Computational cost
    cpu_cost: float = 0.0  # CPU cycles/percentage
    memory_cost: float = 0.0  # Memory usage
    time_cost_ms: float = 0.0  # Execution time
    
    # Cognitive cost
    attention_cost: float = 0.0  # Attention bandwidth used
    cognitive_load: float = 0.0  # Overall cognitive load
    
    # Economic cost
    opportunity_cost: float = 0.0  # Opportunity cost
    total_cost: float = 0.0  # Total economic cost
    
    # Benefit analysis
    expected_benefit: float = 0.0  # Expected benefit
    benefit_cost_ratio: float = 0.0  # Benefit/cost ratio
    
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Calculate derived metrics."""
        if self.total_cost == 0 and self.cpu_cost > 0:
            # Calculate total cost if not provided
            self.total_cost = (
                self.cpu_cost * 0.3 +
                self.memory_cost * 0.2 +
                self.time_cost_ms * 0.01 +
                self.attention_cost * 0.3 +
                self.cognitive_load * 0.1
            )
        
        if self.benefit_cost_ratio == 0 and self.total_cost > 0:
            # Calculate benefit/cost ratio
            self.benefit_cost_ratio = self.expected_benefit / self.total_cost if self.total_cost > 0 else 0.0
    
    @property
    def is_cost_effective(self) -> bool:
        """Check if operation is cost-effective."""
        return self.benefit_cost_ratio >= 1.0
    
    @property
    def is_high_value(self) -> bool:
        """Check if operation provides high value."""
        return self.benefit_cost_ratio >= 2.0


@dataclass
class CognitiveBudget:
    """Budget allocation for cognitive resources."""
    budget_id: str
    resource_type: CognitiveResourceType
    
    # Budget limits
    total_budget: float = 100.0  # Total budget units
    allocated_budget: float = 0.0  # Currently allocated
    available_budget: float = 100.0  # Remaining budget
    
    # Budget allocation strategy
    allocation_strategy: str = "proportional"  # proportional | priority | custom
    
    # Budget tracking
    operations_count: int = 0
    overspend_count: int = 0
    
    # Time period
    period_start: datetime = field(default_factory=datetime.utcnow)
    period_end: Optional[datetime] = None
    
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def budget_utilization(self) -> float:
        """Calculate budget utilization percentage."""
        return (self.allocated_budget / self.total_budget * 100) if self.total_budget > 0 else 0.0
    
    @property
    def is_over_budget(self) -> bool:
        """Check if over budget."""
        return self.allocated_budget > self.total_budget
    
    @property
    def is_near_limit(self, threshold: float = 0.9) -> bool:
        """Check if near budget limit."""
        return self.budget_utilization >= (threshold * 100)


@dataclass
class ResourceAllocationDecision:
    """Decision for resource allocation."""
    decision_id: str
    operation_id: str
    resource_type: CognitiveResourceType
    
    # Decision
    approved: bool = False
    allocated_amount: float = 0.0
    priority: CognitiveOperationPriority = CognitiveOperationPriority.MEDIUM
    
    # Rationale
    rationale: str = ""
    cost_benefit_analysis: CognitiveCost | None = None
    
    # Conditions
    conditions: List[str] = field(default_factory=list)
    
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


class CognitiveEconomyManagerInterface(ABC):
    """Interface for cognitive economy management."""
    
    @abstractmethod
    def calculate_cognitive_cost(
        self,
        operation_id: str,
        resource_type: CognitiveResourceType,
        operation_params: Dict[str, Any]
    ) -> CognitiveCost:
        """Calculate cognitive cost for an operation."""
        pass
    
    @abstractmethod
    def optimize_resource_allocation(
        self,
        resources: Dict[str, float],
        demands: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """Optimize cognitive resource distribution."""
        pass
    
    @abstractmethod
    def track_cognitive_budget(
        self,
        budget_id: str,
        resource_type: CognitiveResourceType
    ) -> CognitiveBudget:
        """Track cognitive resource budget."""
        pass
    
    @abstractmethod
    def make_allocation_decision(
        self,
        operation_id: str,
        resource_type: CognitiveResourceType,
        requested_amount: float,
        priority: CognitiveOperationPriority
    ) -> ResourceAllocationDecision:
        """Make resource allocation decision."""
        pass
    
    @abstractmethod
    def analyze_cost_benefit(
        self,
        operation_id: str,
        expected_outcomes: Dict[str, Any]
    ) -> CognitiveCost:
        """Analyze cost-benefit for an operation."""
        pass


class CognitiveEconomyManager(CognitiveEconomyManagerInterface):
    """Concrete implementation of cognitive economy management."""
    
    def __init__(self):
        self._budgets: Dict[str, CognitiveBudget] = {}
        self._cost_history: Dict[str, List[CognitiveCost]] = {}
        self._allocation_decisions: Dict[str, ResourceAllocationDecision] = {}
        
        # Economic parameters
        self._cost_weights = {
            "cpu": 0.3,
            "memory": 0.2,
            "time": 0.01,
            "attention": 0.3,
            "cognitive_load": 0.1
        }
        
        # Budget defaults
        self._default_budgets = {
            CognitiveResourceType.ATTENTION: 100.0,
            CognitiveResourceType.MEMORY: 100.0,
            CognitiveResourceType.COMPUTATION: 100.0,
            CognitiveResourceType.REASONING: 100.0,
            CognitiveResourceType.LEARNING: 100.0,
            CognitiveResourceType.SIMULATION: 100.0,
        }
        
    def calculate_cognitive_cost(
        self,
        operation_id: str,
        resource_type: CognitiveResourceType,
        operation_params: Dict[str, Any]
    ) -> CognitiveCost:
        """Calculate cognitive cost for an operation."""
        # Extract operation parameters
        cpu_usage = operation_params.get("cpu_usage", 0.0)
        memory_usage = operation_params.get("memory_usage", 0.0)
        estimated_time_ms = operation_params.get("estimated_time_ms", 0.0)
        attention_required = operation_params.get("attention_required", 0.0)
        cognitive_load = operation_params.get("cognitive_load", 0.0)
        
        # Calculate costs
        cpu_cost = cpu_usage * self._cost_weights["cpu"]
        memory_cost = memory_usage * self._cost_weights["memory"]
        time_cost = estimated_time_ms * self._cost_weights["time"]
        attention_cost = attention_required * self._cost_weights["attention"]
        load_cost = cognitive_load * self._cost_weights["cognitive_load"]
        
        total_cost = cpu_cost + memory_cost + time_cost + attention_cost + load_cost
        
        # Create cost object
        cost = CognitiveCost(
            operation_id=operation_id,
            resource_type=resource_type,
            cpu_cost=cpu_cost,
            memory_cost=memory_cost,
            time_cost_ms=estimated_time_ms,
            attention_cost=attention_cost,
            cognitive_load=cognitive_load,
            total_cost=total_cost,
            metadata=operation_params
        )
        
        # Store in history
        if operation_id not in self._cost_history:
            self._cost_history[operation_id] = []
        self._cost_history[operation_id].append(cost)
        
        return cost
    
    def optimize_resource_allocation(
        self,
        resources: Dict[str, float],
        demands: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """Optimize cognitive resource distribution."""
        allocation = {}
        
        # Sort demands by priority
        prioritized_demands = sorted(
            demands,
            key=lambda d: self._priority_value(d.get("priority", "medium")),
            reverse=True
        )
        
        # Allocate resources based on priority and benefit
        for demand in prioritized_demands:
            operation_id = demand["operation_id"]
            resource_type = demand["resource_type"]
            requested_amount = demand["requested_amount"]
            priority = demand.get("priority", "medium")
            expected_benefit = demand.get("expected_benefit", 1.0)
            
            # Get available resources
            available = resources.get(resource_type, 0.0)
            
            # Calculate allocation based on priority and benefit
            if available > 0:
                priority_multiplier = self._priority_value(priority)
                benefit_multiplier = expected_benefit
                
                # Allocate amount
                allocation_factor = min(1.0, (priority_multiplier * benefit_multiplier) / 2.0)
                allocated_amount = min(requested_amount * allocation_factor, available)
                
                allocation[operation_id] = allocated_amount
                
                # Update available resources
                resources[resource_type] = available - allocated_amount
            else:
                allocation[operation_id] = 0.0
        
        return allocation
    
    def _priority_value(self, priority_str: str) -> float:
        """Convert priority string to numeric value."""
        priority_map = {
            "critical": 5.0,
            "high": 4.0,
            "medium": 3.0,
            "low": 2.0,
            "background": 1.0
        }
        return priority_map.get(priority_str.lower(), 3.0)
    
    def track_cognitive_budget(
        self,
        budget_id: str,
        resource_type: CognitiveResourceType
    ) -> CognitiveBudget:
        """Track cognitive resource budget."""
        if budget_id not in self._budgets:
            # Create new budget with defaults
            total_budget = self._default_budgets.get(resource_type, 100.0)
            self._budgets[budget_id] = CognitiveBudget(
                budget_id=budget_id,
                resource_type=resource_type,
                total_budget=total_budget,
                available_budget=total_budget
            )
        
        return self._budgets[budget_id]
    
    def make_allocation_decision(
        self,
        operation_id: str,
        resource_type: CognitiveResourceType,
        requested_amount: float,
        priority: CognitiveOperationPriority
    ) -> ResourceAllocationDecision:
        """Make resource allocation decision."""
        # Get budget for this resource type
        budget = self.track_cognitive_budget(
            f"{resource_type.value}_budget",
            resource_type
        )
        
        # Calculate cost
        cost = self.calculate_cognitive_cost(
            operation_id,
            resource_type,
            {"requested_amount": requested_amount}
        )
        
        # Make decision based on budget and priority
        approved = False
        allocated_amount = 0.0
        rationale = ""
        
        priority_value = self._priority_value(priority.value)
        
        if budget.available_budget >= requested_amount:
            # Sufficient budget
            if priority_value >= 4.0:  # High or critical priority
                approved = True
                allocated_amount = requested_amount
                rationale = f"Sufficient budget and {priority.value} priority"
            elif cost.is_cost_effective:
                approved = True
                allocated_amount = min(requested_amount, budget.available_budget)
                rationale = f"Cost-effective operation (benefit/cost ratio: {cost.benefit_cost_ratio:.2f})"
            else:
                approved = False
                rationale = f"Low priority and not cost-effective (benefit/cost ratio: {cost.benefit_cost_ratio:.2f})"
        else:
            # Insufficient budget
            if priority_value >= 5.0:  # Critical priority
                # Allow overspend for critical operations
                approved = True
                allocated_amount = requested_amount
                rationale = f"Critical priority - allowing budget overspend"
                budget.overspend_count += 1
            else:
                approved = False
                allocated_amount = 0.0
                rationale = f"Insufficient budget ({budget.available_budget:.2f} available, {requested_amount:.2f} requested)"
        
        # Update budget if approved
        if approved:
            budget.allocated_budget += allocated_amount
            budget.available_budget -= allocated_amount
            budget.operations_count += 1
        
        # Create decision
        decision = ResourceAllocationDecision(
            decision_id=f"decision_{operation_id}_{int(datetime.utcnow().timestamp())}",
            operation_id=operation_id,
            resource_type=resource_type,
            approved=approved,
            allocated_amount=allocated_amount,
            priority=priority,
            rationale=rationale,
            cost_benefit_analysis=cost
        )
        
        self._allocation_decisions[decision.decision_id] = decision
        
        return decision
    
    def analyze_cost_benefit(
        self,
        operation_id: str,
        expected_outcomes: Dict[str, Any]
    ) -> CognitiveCost:
        """Analyze cost-benefit for an operation."""
        # Get existing cost analysis
        cost_history = self._cost_history.get(operation_id, [])
        
        if cost_history:
            cost = cost_history[-1]  # Use most recent cost analysis
        else:
            # Create new cost analysis
            cost = CognitiveCost(
                operation_id=operation_id,
                resource_type=CognitiveResourceType.CUSTOM
            )
        
        # Update with expected outcomes
        expected_benefit = expected_outcomes.get("expected_benefit", 0.0)
        confidence = expected_outcomes.get("confidence", 0.5)
        
        cost.expected_benefit = expected_benefit * confidence
        cost.benefit_cost_ratio = cost.expected_benefit / cost.total_cost if cost.total_cost > 0 else 0.0
        
        return cost
    
    def get_economy_report(self) -> Dict[str, Any]:
        """Get comprehensive economy report."""
        total_budgets = len(self._budgets)
        over_budget_count = sum(1 for b in self._budgets.values() if b.is_over_budget)
        near_limit_count = sum(1 for b in self._budgets.values() if b.is_near_limit())
        
        total_decisions = len(self._allocation_decisions)
        approved_decisions = sum(1 for d in self._allocation_decisions.values() if d.approved)
        
        return {
            "budget_summary": {
                "total_budgets": total_budgets,
                "over_budget_count": over_budget_count,
                "near_limit_count": near_limit_count,
                "budgets": {
                    budget_id: {
                        "resource_type": budget.resource_type.value,
                        "utilization": budget.budget_utilization,
                        "allocated": budget.allocated_budget,
                        "available": budget.available_budget,
                        "operations": budget.operations_count,
                        "overspends": budget.overspend_count
                    }
                    for budget_id, budget in self._budgets.items()
                }
            },
            "allocation_summary": {
                "total_decisions": total_decisions,
                "approved_decisions": approved_decisions,
                "approval_rate": (approved_decisions / total_decisions * 100) if total_decisions > 0 else 0,
                "decisions": {
                    decision_id: {
                        "operation_id": decision.operation_id,
                        "resource_type": decision.resource_type.value,
                        "approved": decision.approved,
                        "allocated_amount": decision.allocated_amount,
                        "priority": decision.priority.value,
                        "rationale": decision.rationale,
                        "benefit_cost_ratio": decision.cost_benefit_analysis.benefit_cost_ratio if decision.cost_benefit_analysis else 0.0
                    }
                    for decision_id, decision in self._allocation_decisions.items()
                }
            },
            "cost_analysis": {
                "total_operations_analyzed": len(self._cost_history),
                "operations": {
                    operation_id: {
                        "total_cost": costs[-1].total_cost if costs else 0,
                        "expected_benefit": costs[-1].expected_benefit if costs else 0,
                        "benefit_cost_ratio": costs[-1].benefit_cost_ratio if costs else 0,
                        "is_cost_effective": costs[-1].is_cost_effective if costs else False
                    }
                    for operation_id, costs in self._cost_history.items()
                }
            }
        }


__all__ = [
    "CognitiveResourceType",
    "CognitiveOperationPriority",
    "CognitiveCost",
    "CognitiveBudget",
    "ResourceAllocationDecision",
    "CognitiveEconomyManagerInterface",
    "CognitiveEconomyManager",
]