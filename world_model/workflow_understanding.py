"""Workflow Understanding Layer - Advanced Workflow Modeling and Process Optimization.

This module provides sophisticated workflow understanding capabilities including
workflow modeling, process efficiency analysis, bottleneck identification, and
automation opportunity detection.
"""

from __future__ import annotations

import logging
import threading
import time
import numpy as np
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum
from collections import defaultdict, deque
import hashlib

logger = logging.getLogger(__name__)


class WorkflowType(str, Enum):
    """Classification of workflow types."""
    TRADING_EXECUTION = "TRADING_EXECUTION"
    RISK_ASSESSMENT = "RISK_ASSESSMENT"
    SIGNAL_GENERATION = "SIGNAL_GENERATION"
    POSITION_MANAGEMENT = "POSITION_MANAGEMENT"
    PORTFOLIO_REBALANCING = "PORTFOLIO_REBALANCING"
    MARKET_ANALYSIS = "MARKET_ANALYSIS"
    DATA_PROCESSING = "DATA_PROCESSING"
    REPORTING = "REPORTING"


class WorkflowStatus(str, Enum):
    """Workflow execution status."""
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    TIMEOUT = "TIMEOUT"


@dataclass
class WorkflowStep:
    """Individual step in a workflow."""
    step_id: str
    step_name: str
    step_type: str  # "computation", "api_call", "database_query", "external_service"
    dependencies: List[str]  # Step IDs this step depends on
    estimated_duration: float
    resource_requirements: Dict[str, Any]
    retry_policy: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Workflow:
    """Complete workflow definition."""
    workflow_id: str
    workflow_name: str
    workflow_type: WorkflowType
    steps: List[WorkflowStep]
    priority: int
    timeout: float
    retry_policy: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowExecution:
    """Execution instance of a workflow."""
    execution_id: str
    workflow_id: str
    start_time: float
    end_time: Optional[float]
    status: WorkflowStatus
    steps_executed: List[str]
    step_timings: Dict[str, float]
    resource_usage: Dict[str, Any]
    error_info: Optional[Dict[str, Any]]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProcessEfficiencyAnalysis:
    """Analysis of process efficiency."""
    workflow_id: str
    total_efficiency_score: float
    step_efficiencies: Dict[str, float]
    bottlenecks: List[Dict[str, Any]]
    optimization_opportunities: List[Dict[str, Any]]
    resource_utilization: Dict[str, float]
    parallelization_potential: float
    estimated_optimization_gain: float


@dataclass
class WorkflowOptimization:
    """Recommended workflow optimization."""
    optimization_id: str
    workflow_id: str
    optimization_type: str  # "parallelization", "caching", "batching", "simplification"
    description: str
    expected_improvement: float
    implementation_complexity: str
    priority: int


class WorkflowUnderstanding:
    """Advanced workflow understanding with comprehensive analysis."""

    def __init__(self, history_window: int = 1000):
        self._lock = threading.Lock()
        self._history_window = history_window
        self._workflows: Dict[str, Workflow] = {}
        self._execution_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=history_window))
        self._active_executions: Dict[str, WorkflowExecution] = {}
        self._workflow_analyzer = WorkflowAnalyzer()
        self._efficiency_analyzer = EfficiencyAnalyzer()
        self._bottleneck_detector = BottleneckDetector()
        self._optimization_engine = OptimizationEngine()
        self._initialized = False

    def start(self) -> bool:
        """Start workflow understanding system."""
        logger.info("[WORKFLOW_UNDERSTANDING] Starting advanced workflow understanding...")
        self._initialized = True
        logger.info("[WORKFLOW_UNDERSTANDING] Advanced workflow understanding started")
        return True

    def stop(self) -> bool:
        """Stop workflow understanding system."""
        logger.info("[WORKFLOW_UNDERSTANDING] Stopping advanced workflow understanding...")
        self._initialized = False
        logger.info("[WORKFLOW_UNDERSTANDING] Advanced workflow understanding stopped")
        return True

    def register_workflow(self, workflow: Workflow) -> None:
        """Register a workflow for analysis."""
        with self._lock:
            self._workflows[workflow.workflow_id] = workflow
            logger.info(f"[WORKFLOW_UNDERSTANDING] Registered workflow {workflow.workflow_id}")

    def start_workflow_execution(self, workflow_id: str, execution_params: Dict[str, Any]) -> str:
        """Start execution of a workflow."""
        workflow = self._workflows.get(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")

        execution_id = f"exec_{int(time.time())}_{hash(workflow_id + str(time.time())) % 10000}"
        
        execution = WorkflowExecution(
            execution_id=execution_id,
            workflow_id=workflow_id,
            start_time=time.time(),
            end_time=None,
            status=WorkflowStatus.RUNNING,
            steps_executed=[],
            step_timings={},
            resource_usage={},
            error_info=None,
            metadata=execution_params
        )
        
        with self._lock:
            self._active_executions[execution_id] = execution
        
        logger.info(f"[WORKFLOW_UNDERSTANDING] Started execution {execution_id} for workflow {workflow_id}")
        return execution_id

    def complete_workflow_execution(self, execution_id: str, status: WorkflowStatus, results: Dict[str, Any]) -> None:
        """Complete execution of a workflow."""
        with self._lock:
            if execution_id not in self._active_executions:
                return
            
            execution = self._active_executions[execution_id]
            execution.end_time = time.time()
            execution.status = status
            execution.metadata.update(results)
            
            # Store in history
            workflow_id = execution.workflow_id
            self._execution_history[workflow_id].append(execution)
            
            # Remove from active executions
            del self._active_executions[execution_id]
        
        logger.info(f"[WORKFLOW_UNDERSTANDING] Completed execution {execution_id} with status {status}")

    def record_step_execution(self, execution_id: str, step_id: str, duration: float, resource_usage: Dict[str, Any]) -> None:
        """Record execution of a workflow step."""
        with self._lock:
            if execution_id in self._active_executions:
                execution = self._active_executions[execution_id]
                execution.steps_executed.append(step_id)
                execution.step_timings[step_id] = duration
                
                # Update resource usage
                for resource, amount in resource_usage.items():
                    if resource not in execution.resource_usage:
                        execution.resource_usage[resource] = 0.0
                    execution.resource_usage[resource] += amount

    def analyze_workflow_efficiency(self, workflow_id: str) -> ProcessEfficiencyAnalysis:
        """Analyze process efficiency for a workflow."""
        logger.info(f"[WORKFLOW_UNDERSTANDING] Analyzing efficiency for workflow {workflow_id}")
        
        workflow = self._workflows.get(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        executions = list(self._execution_history[workflow_id])
        
        if not executions:
            return ProcessEfficiencyAnalysis(
                workflow_id=workflow_id,
                total_efficiency_score=0.5,
                step_efficiencies={},
                bottlenecks=[],
                optimization_opportunities=[],
                resource_utilization={},
                parallelization_potential=0.0,
                estimated_optimization_gain=0.0
            )
        
        # Analyze efficiency
        analysis = self._efficiency_analyzer.analyze_efficiency(workflow, executions)
        
        return analysis

    def detect_workflow_bottlenecks(self, workflow_id: str) -> List[Dict[str, Any]]:
        """Detect bottlenecks in workflow execution."""
        logger.info(f"[WORKFLOW_UNDERSTANDING] Detecting bottlenecks for workflow {workflow_id}")
        
        workflow = self._workflows.get(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        executions = list(self._execution_history[workflow_id])
        
        if not executions:
            return []
        
        # Detect bottlenecks
        bottlenecks = self._bottleneck_detector.detect_bottlenecks(workflow, executions)
        
        return bottlenecks

    def optimize_workflow(self, workflow_id: str) -> List[WorkflowOptimization]:
        """Generate workflow optimization recommendations."""
        logger.info(f"[WORKFLOW_UNDERSTANDING] Optimizing workflow {workflow_id}")
        
        workflow = self._workflows.get(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        executions = list(self._execution_history[workflow_id])
        
        # Generate optimizations
        optimizations = self._optimization_engine.generate_optimizations(workflow, executions)
        
        return optimizations

    def model_trading_workflow(self, workflow_type: WorkflowType) -> Workflow:
        """Model end-to-end trading workflow."""
        workflow_id = f"trading_{workflow_type.value.lower()}_{int(time.time())}"
        
        # Define workflow steps based on type
        if workflow_type == WorkflowType.TRADING_EXECUTION:
            steps = [
                WorkflowStep(
                    step_id="signal_analysis",
                    step_name="Signal Analysis",
                    step_type="computation",
                    dependencies=[],
                    estimated_duration=0.1,
                    resource_requirements={"cpu": 0.2, "memory": 0.1},
                    retry_policy={"max_retries": 3, "backoff": 1.0}
                ),
                WorkflowStep(
                    step_id="risk_assessment",
                    step_name="Risk Assessment",
                    step_type="computation",
                    dependencies=["signal_analysis"],
                    estimated_duration=0.05,
                    resource_requirements={"cpu": 0.1, "memory": 0.05},
                    retry_policy={"max_retries": 2, "backoff": 0.5}
                ),
                WorkflowStep(
                    step_id="position_sizing",
                    step_name="Position Sizing",
                    step_type="computation",
                    dependencies=["risk_assessment"],
                    estimated_duration=0.03,
                    resource_requirements={"cpu": 0.05, "memory": 0.02},
                    retry_policy={"max_retries": 1, "backoff": 0.2}
                ),
                WorkflowStep(
                    step_id="order_submission",
                    step_name="Order Submission",
                    step_type="api_call",
                    dependencies=["position_sizing"],
                    estimated_duration=0.5,
                    resource_requirements={"network": 0.3, "cpu": 0.1},
                    retry_policy={"max_retries": 5, "backoff": 2.0}
                ),
                WorkflowStep(
                    step_id="execution_confirmation",
                    step_name="Execution Confirmation",
                    step_type="api_call",
                    dependencies=["order_submission"],
                    estimated_duration=1.0,
                    resource_requirements={"network": 0.2, "cpu": 0.05},
                    retry_policy={"max_retries": 3, "backoff": 1.0}
                )
            ]
        else:
            # Generic workflow steps
            steps = [
                WorkflowStep(
                    step_id="initialization",
                    step_name="Initialization",
                    step_type="computation",
                    dependencies=[],
                    estimated_duration=0.1,
                    resource_requirements={"cpu": 0.1, "memory": 0.1},
                    retry_policy={"max_retries": 2, "backoff": 0.5}
                ),
                WorkflowStep(
                    step_id="processing",
                    step_name="Processing",
                    step_type="computation",
                    dependencies=["initialization"],
                    estimated_duration=0.5,
                    resource_requirements={"cpu": 0.3, "memory": 0.2},
                    retry_policy={"max_retries": 3, "backoff": 1.0}
                ),
                WorkflowStep(
                    step_id="finalization",
                    step_name="Finalization",
                    step_type="computation",
                    dependencies=["processing"],
                    estimated_duration=0.1,
                    resource_requirements={"cpu": 0.1, "memory": 0.1},
                    retry_policy={"max_retries": 2, "backoff": 0.5}
                )
            ]
        
        workflow = Workflow(
            workflow_id=workflow_id,
            workflow_name=f"{workflow_type.value} Workflow",
            workflow_type=workflow_type,
            steps=steps,
            priority=5,
            timeout=30.0,
            retry_policy={"max_retries": 3, "backoff": 1.0},
            metadata={"created_at": time.time()}
        )
        
        self.register_workflow(workflow)
        return workflow

    def get_statistics(self) -> Dict[str, Any]:
        """Get workflow understanding statistics (alias for get_workflow_statistics)."""
        return self.get_workflow_statistics()
    
    def get_workflow_statistics(self) -> Dict[str, Any]:
        """Get workflow understanding statistics."""
        with self._lock:
            return {
                "total_workflows": len(self._workflows),
                "total_executions": sum(len(history) for history in self._execution_history.values()),
                "active_executions": len(self._active_executions),
                "workflows_by_type": self._count_by_workflow_type(),
                "avg_execution_time": self._calculate_avg_execution_time()
            }
    
    def _count_by_workflow_type(self) -> Dict[str, int]:
        """Count workflows by type."""
        counts = defaultdict(int)
        for workflow in self._workflows.values():
            counts[workflow.workflow_type.value] += 1
        return dict(counts)
    
    def _calculate_avg_execution_time(self) -> float:
        """Calculate average execution time across all workflows."""
        all_executions = []
        for history in self._execution_history.values():
            all_executions.extend([exec for exec in history if exec.end_time])
        
        if not all_executions:
            return 0.0
        
        execution_times = [exec.end_time - exec.start_time for exec in all_executions]
        return np.mean(execution_times)

    def _count_by_workflow_type(self) -> Dict[str, int]:
        """Count workflows by type."""
        counts = defaultdict(int)
        for workflow in self._workflows.values():
            counts[workflow.workflow_type.value] += 1
        return dict(counts)

    def _calculate_avg_execution_time(self) -> float:
        """Calculate average execution time across all workflows."""
        all_executions = []
        for history in self._execution_history.values():
            all_executions.extend([exec for exec in history if exec.end_time])
        
        if not all_executions:
            return 0.0
        
        execution_times = [exec.end_time - exec.start_time for exec in all_executions]
        return np.mean(execution_times)


class WorkflowAnalyzer:
    """Comprehensive workflow analysis capabilities."""
    
    def analyze_workflow_structure(self, workflow: Workflow) -> Dict[str, Any]:
        """Analyze workflow structure and dependencies."""
        # Build dependency graph
        dependency_graph = {step.step_id: step.dependencies for step in workflow.steps}
        
        # Analyze critical path
        critical_path = self._find_critical_path(workflow)
        
        # Calculate complexity metrics
        complexity = self._calculate_workflow_complexity(workflow)
        
        # Analyze parallelization potential
        parallelization = self._analyze_parallelization_potential(workflow)
        
        return {
            "dependency_graph": dependency_graph,
            "critical_path": critical_path,
            "complexity_metrics": complexity,
            "parallelization_potential": parallelization
        }
    
    def _find_critical_path(self, workflow: Workflow) -> List[str]:
        """Find critical path through workflow."""
        # Build step duration mapping
        step_durations = {step.step_id: step.estimated_duration for step in workflow.steps}
        
        # Topological sort and longest path calculation
        # Simplified implementation - in production would use proper topological sort
        critical_path = []
        remaining_steps = workflow.steps.copy()
        
        while remaining_steps:
            # Find step with no unsatisfied dependencies
            executable = []
            for step in remaining_steps:
                deps_satisfied = all(dep in critical_path for dep in step.dependencies)
                if deps_satisfied:
                    executable.append(step)
            
            if not executable:
                # Circular dependency or missing step
                break
            
            # Choose the longest duration executable step
            chosen = max(executable, key=lambda s: s.estimated_duration)
            critical_path.append(chosen.step_id)
            remaining_steps.remove(chosen)
        
        return critical_path
    
    def _calculate_workflow_complexity(self, workflow: Workflow) -> Dict[str, Any]:
        """Calculate workflow complexity metrics."""
        step_count = len(workflow.steps)
        dependency_count = sum(len(step.dependencies) for step in workflow.steps)
        avg_dependencies = dependency_count / step_count if step_count > 0 else 0
        
        # Calculate cyclomatic complexity approximation
        cyclomatic_complexity = dependency_count - step_count + 2
        
        return {
            "step_count": step_count,
            "dependency_count": dependency_count,
            "average_dependencies": avg_dependencies,
            "cyclomatic_complexity": cyclomatic_complexity,
            "complexity_level": self._categorize_complexity(cyclomatic_complexity)
        }
    
    def _analyze_parallelization_potential(self, workflow: Workflow) -> Dict[str, Any]:
        """Analyze potential for workflow parallelization."""
        # Find independent steps
        step_dependencies = {step.step_id: set(step.dependencies) for step in workflow.steps}
        
        parallelizable_groups = []
        remaining_steps = workflow.steps.copy()
        
        while remaining_steps:
            # Find steps that can run in parallel (no dependencies on each other)
            current_group = []
            for step in remaining_steps:
                # Check if this step doesn't depend on other steps in current group
                can_parallelize = all(
                    step_id not in step_dependencies[other_step.step_id]
                    for other_step in current_group
                )
                if can_parallelize:
                    current_group.append(step)
            
            if not current_group:
                break
            
            parallelizable_groups.append([step.step_id for step in current_group])
            
            # Remove these steps from remaining
            for step in current_group:
                remaining_steps.remove(step)
        
        # Calculate parallelization potential
        sequential_time = sum(step.estimated_duration for step in workflow.steps)
        parallel_time = sum(
            max(group_steps)  # Max duration in parallel group
            for group_steps in [
                [step.estimated_duration for step in workflow.steps if step.step_id in group]
                for group in parallelizable_groups
            ]
        )
        
        speedup_potential = sequential_time / parallel_time if parallel_time > 0 else 1.0
        
        return {
            "parallelizable_groups": parallelizable_groups,
            "sequential_time": sequential_time,
            "parallel_time": parallel_time,
            "speedup_potential": speedup_potential,
            "parallelization_ratio": 1.0 - (parallel_time / sequential_time) if sequential_time > 0 else 0.0
        }
    
    def _categorize_complexity(self, cyclomatic_complexity: int) -> str:
        """Categorize complexity level."""
        if cyclomatic_complexity < 5:
            return "simple"
        elif cyclomatic_complexity < 10:
            return "moderate"
        elif cyclomatic_complexity < 20:
            return "complex"
        else:
            return "very_complex"


class EfficiencyAnalyzer:
    """Process efficiency analysis capabilities."""
    
    def analyze_efficiency(self, workflow: Workflow, executions: List[WorkflowExecution]) -> ProcessEfficiencyAnalysis:
        """Comprehensive process efficiency analysis."""
        if not executions:
            return ProcessEfficiencyAnalysis(
                workflow_id=workflow.workflow_id,
                total_efficiency_score=0.5,
                step_efficiencies={},
                bottlenecks=[],
                optimization_opportunities=[],
                resource_utilization={},
                parallelization_potential=0.0,
                estimated_optimization_gain=0.0
            )
        
        # Calculate step efficiencies
        step_efficiencies = self._calculate_step_efficiencies(workflow, executions)
        
        # Calculate total efficiency score
        total_efficiency = np.mean(list(step_efficiencies.values())) if step_efficiencies else 0.5
        
        # Detect bottlenecks
        bottlenecks = self._identify_bottlenecks(workflow, executions, step_efficiencies)
        
        # Identify optimization opportunities
        optimization_opportunities = self._identify_optimization_opportunities(workflow, executions, step_efficiencies)
        
        # Analyze resource utilization
        resource_utilization = self._analyze_resource_utilization(executions)
        
        # Calculate parallelization potential
        parallelization_potential = self._calculate_parallelization_potential(workflow)
        
        # Estimate optimization gain
        estimated_gain = self._estimate_optimization_gain(optimization_opportunities)
        
        return ProcessEfficiencyAnalysis(
            workflow_id=workflow.workflow_id,
            total_efficiency_score=total_efficiency,
            step_efficiencies=step_efficiencies,
            bottlenecks=bottlenecks,
            optimization_opportunities=optimization_opportunities,
            resource_utilization=resource_utilization,
            parallelization_potential=parallelization_potential,
            estimated_optimization_gain=estimated_gain
        )
    
    def _calculate_step_efficiencies(self, workflow: Workflow, executions: List[WorkflowExecution]) -> Dict[str, float]:
        """Calculate efficiency for each workflow step."""
        step_efficiencies = {}
        
        for step in workflow.steps:
            # Get actual durations for this step
            actual_durations = []
            for execution in executions:
                if step.step_id in execution.step_timings:
                    actual_durations.append(execution.step_timings[step.step_id])
            
            if not actual_durations:
                step_efficiencies[step.step_id] = 0.5  # Default if no data
                continue
            
            # Compare actual vs estimated duration
            avg_actual = np.mean(actual_durations)
            estimated = step.estimated_duration
            
            # Efficiency = estimated / actual (capped at 1.0)
            efficiency = min(1.0, estimated / avg_actual) if avg_actual > 0 else 0.5
            step_efficiencies[step.step_id] = efficiency
        
        return step_efficiencies
    
    def _identify_bottlenecks(self, workflow: Workflow, executions: List[WorkflowExecution], step_efficiencies: Dict[str, float]) -> List[Dict[str, Any]]:
        """Identify workflow bottlenecks."""
        bottlenecks = []
        
        for step_id, efficiency in step_efficiencies.items():
            if efficiency < 0.5:  # Less than 50% efficient
                step = next((s for s in workflow.steps if s.step_id == step_id), None)
                if step:
                    bottlenecks.append({
                        "step_id": step_id,
                        "step_name": step.step_name,
                        "efficiency_score": efficiency,
                        "severity": "high" if efficiency < 0.3 else "medium",
                        "impact": self._calculate_bottleneck_impact(step_id, workflow, executions)
                    })
        
        return bottlenecks
    
    def _calculate_bottleneck_impact(self, step_id: str, workflow: Workflow, executions: List[WorkflowExecution]) -> float:
        """Calculate impact of bottleneck on overall workflow."""
        # Find steps that depend on this bottleneck
        dependent_steps = [step for step in workflow.steps if step_id in step.dependencies]
        
        # Calculate impact based on number of dependents and their efficiency
        impact = len(dependent_steps) * 0.1  # Base impact per dependent
        impact += (1.0 - step_efficiencies.get(step_id, 0.5)) * 0.5  # Add efficiency impact
        
        return min(1.0, impact)
    
    def _identify_optimization_opportunities(self, workflow: Workflow, executions: List[WorkflowExecution], step_efficiencies: Dict[str, float]) -> List[Dict[str, Any]]:
        """Identify optimization opportunities."""
        opportunities = []
        
        for step_id, efficiency in step_efficiencies.items():
            if efficiency < 0.7:  # Less than 70% efficient
                step = next((s for s in workflow.steps if s.step_id == step_id), None)
                if step:
                    opportunities.append({
                        "step_id": step_id,
                        "step_name": step.step_name,
                        "current_efficiency": efficiency,
                        "potential_improvement": 1.0 - efficiency,
                        "optimization_type": self._suggest_optimization_type(step, efficiency),
                        "estimated_gain": (1.0 - efficiency) * 0.5  # Conservative estimate
                    })
        
        return opportunities
    
    def _suggest_optimization_type(self, step: WorkflowStep, efficiency: float) -> str:
        """Suggest optimization type for a step."""
        if step.step_type == "api_call":
            if efficiency < 0.3:
                return "caching_or_batching"
            else:
                return "retry_optimization"
        elif step.step_type == "computation":
            if efficiency < 0.3:
                return "parallelization"
            else:
                return "algorithm_optimization"
        elif step.step_type == "database_query":
            return "index_optimization"
        else:
            return "general_optimization"
    
    def _analyze_resource_utilization(self, executions: List[WorkflowExecution]) -> Dict[str, float]:
        """Analyze resource utilization across executions."""
        if not executions:
            return {}
        
        resource_totals = defaultdict(float)
        resource_counts = defaultdict(int)
        
        for execution in executions:
            for resource, amount in execution.resource_usage.items():
                resource_totals[resource] += amount
                resource_counts[resource] += 1
        
        # Calculate average utilization
        utilization = {}
        for resource in resource_totals:
            utilization[resource] = resource_totals[resource] / resource_counts[resource]
        
        return utilization
    
    def _calculate_parallelization_potential(self, workflow: Workflow) -> float:
        """Calculate potential for workflow parallelization."""
        # Count independent steps
        independent_step_pairs = 0
        total_step_pairs = 0
        
        steps = workflow.steps
        for i, step1 in enumerate(steps):
            for step2 in steps[i+1:]:
                total_step_pairs += 1
                # Check if steps are independent (no dependencies)
                if (step1.step_id not in step2.dependencies and 
                    step2.step_id not in step1.dependencies):
                    independent_step_pairs += 1
        
        if total_step_pairs == 0:
            return 0.0
        
        return independent_step_pairs / total_step_pairs
    
    def _estimate_optimization_gain(self, optimization_opportunities: List[Dict[str, Any]]) -> float:
        """Estimate overall optimization gain."""
        if not optimization_opportunities:
            return 0.0
        
        total_potential = sum(opp["estimated_gain"] for opp in optimization_opportunities)
        
        # Apply diminishing returns
        return min(0.5, total_potential * 0.5)  # Cap at 50% overall improvement


class BottleneckDetector:
    """Advanced bottleneck detection capabilities."""
    
    def detect_bottlenecks(self, workflow: Workflow, executions: List[WorkflowExecution]) -> List[Dict[str, Any]]:
        """Detect various types of bottlenecks."""
        bottlenecks = []
        
        # Time-based bottlenecks
        time_bottlenecks = self._detect_time_bottlenecks(workflow, executions)
        bottlenecks.extend(time_bottlenecks)
        
        # Resource-based bottlenecks
        resource_bottlenecks = self._detect_resource_bottlenecks(executions)
        bottlenecks.extend(resource_bottlenecks)
        
        # Dependency-based bottlenecks
        dependency_bottlenecks = self._detect_dependency_bottlenecks(workflow, executions)
        bottlenecks.extend(dependency_bottlenecks)
        
        return bottlenecks
    
    def _detect_time_bottlenecks(self, workflow: Workflow, executions: List[WorkflowExecution]) -> List[Dict[str, Any]]:
        """Detect time-based bottlenecks."""
        bottlenecks = []
        
        for step in workflow.steps:
            # Get actual durations for this step
            actual_durations = []
            for execution in executions:
                if step.step_id in execution.step_timings:
                    actual_durations.append(execution.step_timings[step.step_id])
            
            if not actual_durations:
                continue
            
            avg_actual = np.mean(actual_durations)
            std_actual = np.std(actual_durations)
            
            # Check if significantly slower than estimated
            if avg_actual > step.estimated_duration * 2.0:
                bottlenecks.append({
                    "bottleneck_type": "time",
                    "step_id": step.step_id,
                    "step_name": step.step_name,
                    "severity": "high",
                    "description": f"Step takes {avg_actual:.2f}s vs estimated {step.estimated_duration:.2f}s",
                    "metrics": {
                        "avg_duration": avg_actual,
                        "estimated_duration": step.estimated_duration,
                        "std_duration": std_actual
                    }
                })
        
        return bottlenecks
    
    def _detect_resource_bottlenecks(self, executions: List[WorkflowExecution]) -> List[Dict[str, Any]]:
        """Detect resource-based bottlenecks."""
        bottlenecks = []
        
        # Aggregate resource usage
        resource_totals = defaultdict(float)
        for execution in executions:
            for resource, amount in execution.resource_usage.items():
                resource_totals[resource] += amount
        
        # Check for high resource usage
        for resource, total_usage in resource_totals.items():
            avg_usage = total_usage / len(executions)
            if avg_usage > 0.8:  # More than 80% utilization
                bottlenecks.append({
                    "bottleneck_type": "resource",
                    "resource": resource,
                    "severity": "high" if avg_usage > 0.9 else "medium",
                    "description": f"High {resource} usage: {avg_usage:.2f}",
                    "metrics": {"avg_usage": avg_usage}
                })
        
        return bottlenecks
    
    def _detect_dependency_bottlenecks(self, workflow: Workflow, executions: List[WorkflowExecution]) -> List[Dict[str, Any]]:
        """Detect dependency-based bottlenecks."""
        bottlenecks = []
        
        # Find steps with many dependencies
        for step in workflow.steps:
            dependency_count = len(step.dependencies)
            
            if dependency_count > 3:  # More than 3 dependencies
                bottlenecks.append({
                    "bottleneck_type": "dependency",
                    "step_id": step.step_id,
                    "step_name": step.step_name,
                    "severity": "medium",
                    "description": f"Step has {dependency_count} dependencies",
                    "metrics": {"dependency_count": dependency_count}
                })
        
        return bottlenecks


class OptimizationEngine:
    """Workflow optimization recommendation engine."""
    
    def generate_optimizations(self, workflow: Workflow, executions: List[WorkflowExecution]) -> List[WorkflowOptimization]:
        """Generate comprehensive workflow optimization recommendations."""
        optimizations = []
        
        # Parallelization opportunities
        parallelization = self._suggest_parallelization(workflow)
        if parallelization:
            optimizations.append(parallelization)
        
        # Caching opportunities
        caching = self._suggest_caching(workflow, executions)
        if caching:
            optimizations.append(caching)
        
        # Batching opportunities
        batching = self._suggest_batching(workflow, executions)
        if batching:
            optimizations.append(batching)
        
        # Simplification opportunities
        simplification = self._suggest_simplification(workflow)
        if simplification:
            optimizations.append(simplification)
        
        return optimizations
    
    def _suggest_parallelization(self, workflow: Workflow) -> Optional[WorkflowOptimization]:
        """Suggest workflow parallelization opportunities."""
        # Find independent steps
        independent_steps = []
        for step in workflow.steps:
            # Check if this step has no dependencies on other steps
            has_dependencies = any(
                other_step.step_id in step.dependencies
                for other_step in workflow.steps
                if other_step.step_id != step.step_id
            )
            
            if not has_dependencies:
                independent_steps.append(step)
        
        if len(independent_steps) >= 2:
            potential_improvement = (len(independent_steps) - 1) / len(workflow.steps)
            
            return WorkflowOptimization(
                optimization_id=f"parallel_{int(time.time())}",
                workflow_id=workflow.workflow_id,
                optimization_type="parallelization",
                description=f"Parallelize {len(independent_steps)} independent steps: {[s.step_id for s in independent_steps]}",
                expected_improvement=potential_improvement * 0.3,  # Conservative 30% of theoretical max
                implementation_complexity="medium",
                priority=1
            )
        
        return None
    
    def _suggest_caching(self, workflow: Workflow, executions: List[WorkflowExecution]) -> Optional[WorkflowOptimization]:
        """Suggest caching opportunities."""
        # Look for API calls or expensive computations
        cacheable_steps = []
        for step in workflow.steps:
            if step.step_type in ["api_call", "database_query"]:
                # Check if results could be cached
                if self._is_cacheable(step):
                    cacheable_steps.append(step)
        
        if cacheable_steps:
            potential_improvement = 0.4  # 40% improvement for cached steps
            
            return WorkflowOptimization(
                optimization_id=f"cache_{int(time.time())}",
                workflow_id=workflow.workflow_id,
                optimization_type="caching",
                description=f"Add caching for {len(cacheable_steps)} steps: {[s.step_id for s in cacheable_steps]}",
                expected_improvement=potential_improvement * len(cacheable_steps) / len(workflow.steps),
                implementation_complexity="low",
                priority=2
            )
        
        return None
    
    def _is_cacheable(self, step: WorkflowStep) -> bool:
        """Check if a step is cacheable."""
        # API calls with read operations are cacheable
        if step.step_type == "api_call":
            return "read" in step.step_name.lower() or "get" in step.step_name.lower()
        
        # Database queries are cacheable
        if step.step_type == "database_query":
            return True
        
        return False
    
    def _suggest_batching(self, workflow: Workflow, executions: List[WorkflowExecution]) -> Optional[WorkflowOptimization]:
        """Suggest batching opportunities."""
        # Look for similar steps that could be batched
        step_groups = defaultdict(list)
        for step in workflow.steps:
            step_groups[step.step_type].append(step)
        
        batchable_groups = []
        for step_type, steps in step_groups.items():
            if len(steps) >= 2 and step_type in ["api_call", "database_query"]:
                batchable_groups.append((step_type, steps))
        
        if batchable_groups:
            # Pick the most promising batchable group
            step_type, steps = max(batchable_groups, key=lambda x: len(x[1]))
            
            return WorkflowOptimization(
                optimization_id=f"batch_{int(time.time())}",
                workflow_id=workflow.workflow_id,
                optimization_type="batching",
                description=f"Batch {len(steps)} {step_type} steps: {[s.step_id for s in steps]}",
                expected_improvement=0.25,  # 25% improvement for batching
                implementation_complexity="medium",
                priority=3
            )
        
        return None
    
    def _suggest_simplification(self, workflow: Workflow) -> Optional[WorkflowOptimization]:
        """Suggest workflow simplification opportunities."""
        # Check for excessive complexity
        if len(workflow.steps) > 10:
            potential_improvement = (len(workflow.steps) - 10) / len(workflow.steps) * 0.5
            
            return WorkflowOptimization(
                optimization_id=f"simplify_{int(time.time())}",
                workflow_id=workflow.workflow_id,
                optimization_type="simplification",
                description=f"Simplify workflow by reducing step count from {len(workflow.steps)} to 10",
                expected_improvement=potential_improvement,
                implementation_complexity="high",
                priority=4
            )
        
        return None


# Singleton instance
_workflow_understanding: Optional[WorkflowUnderstanding] = None
_workflow_understanding_lock = threading.Lock()


def get_workflow_understanding(history_window: int = 1000) -> WorkflowUnderstanding:
    """Get the singleton workflow understanding instance."""
    global _workflow_understanding
    if _workflow_understanding is None:
        with _workflow_understanding_lock:
            if _workflow_understanding is None:
                _workflow_understanding = WorkflowUnderstanding(history_window)
    return _workflow_understanding


__all__ = [
    "WorkflowUnderstanding",
    "get_workflow_understanding",
    "WorkflowType",
    "WorkflowStatus",
    "WorkflowStep",
    "Workflow",
    "WorkflowExecution",
    "ProcessEfficiencyAnalysis",
    "WorkflowOptimization",
]