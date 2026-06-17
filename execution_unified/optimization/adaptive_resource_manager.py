"""
execution_unified.optimization.adaptive_resource_manager
DIX VISION v42.2 — Adaptive Resource Manager (Priority 2)

Provides intelligent resource allocation based on execution patterns.
This is a Priority 2 enhancement for performance optimization.
"""

from __future__ import annotations

import logging
import threading
import time
from datetime import datetime
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class ResourceType(Enum):
    """Types of resources to manage."""
    CPU = "CPU"
    MEMORY = "MEMORY"
    NETWORK = "NETWORK"
    IO = "IO"
    DATABASE = "DATABASE"


@dataclass
class ResourceAllocation:
    """Current resource allocation."""
    
    resource_type: ResourceType
    allocated_amount: float
    maximum_capacity: float
    utilization_percent: float
    allocated_to: str  # Component or service name


@dataclass
class WorkloadPrediction:
    """Predicted workload for resource planning."""
    
    resource_type: ResourceType
    current_load: float
    predicted_load: float
    time_horizon_minutes: int
    confidence: float = 0.0


@dataclass
class ResourceOptimization:
    """Resource optimization recommendation."""
    
    optimization_id: str
    resource_type: ResourceType
    current_allocation: float
    recommended_allocation: float
    reason: str
    expected_improvement: float
    priority: str  # LOW, MEDIUM, HIGH


@dataclass
class ScalingPlan:
    """Plan for resource scaling."""
    
    resource_type: ResourceType
    scale_up_threshold: float
    scale_down_threshold: float
    current_instances: int
    recommended_instances: int
    estimated_time_minutes: float = 5.0


class WorkloadPredictor:
    """Predicts future workload based on patterns."""
    
    def __init__(self):
        self._lock = threading.Lock()
        self._workload_history: Dict[str, List[float]] = {}
        self._history_size = 30  # Keep 30 data points
        
        logger.info("[WORKLOAD_PREDICTOR] Initialized")
    
    def predict(
        self,
        current_metrics: Dict[str, float],
        time_horizon_minutes: int = 30
    ) -> List[WorkloadPrediction]:
        """
        Predict future workload based on current metrics and history.
        
        Args:
            current_metrics: Current resource metrics
            time_horizon_minutes: Time horizon for prediction
            
        Returns:
            Workload predictions for each resource
        """
        with self._lock:
            predictions = []
            
            # Update history and predict for each metric
            metric_mappings = [
                ("cpu_usage", ResourceType.CPU),
                ("memory_usage", ResourceType.MEMORY),
                ("network_usage", ResourceType.NETWORK),
                ("io_usage", ResourceType.IO)
            ]
            
            for metric_name, resource_type in metric_mappings:
                if metric_name in current_metrics:
                    current_value = current_metrics[metric_name]
                    
                    # Update history
                    if metric_name not in self._workload_history:
                        self._workload_history[metric_name] = []
                    self._workload_history[metric_name].append(current_value)
                    
                    # Keep only recent data
                    if len(self._workload_history[metric_name]) > self._history_size:
                        self._workload_history[metric_name] = self._workload_history[metric_name][-self._history_size:]
                    
                    # Predict future load
                    predicted_value = self._predict_value(self._workload_history[metric_name])
                    confidence = self._calculate_confidence(self._workload_history[metric_name])
                    
                    predictions.append(WorkloadPrediction(
                        resource_type=resource_type,
                        current_load=current_value,
                        predicted_load=predicted_value,
                        time_horizon_minutes=time_horizon_minutes,
                        confidence=confidence
                    ))
            
            return predictions
    
    def _predict_value(self, history: List[float]) -> float:
        """Predict future value based on history."""
        if len(history) < 2:
            return history[-1] if history else 0.0
        
        # Simple moving average with trend
        recent = history[-5:] if len(history) >= 5 else history
        moving_avg = sum(recent) / len(recent)
        
        # Calculate trend
        if len(history) >= 3:
            older = history[-10:-5] if len(history) >= 10 else history[:-5]
            if older:
                older_avg = sum(older) / len(older)
                trend = (moving_avg - older_avg) / older_avg if older_avg > 0 else 0
                predicted = moving_avg * (1 + trend * 0.1)  # Conservative trend
                return max(predicted, 0.0)
        
        return moving_avg
    
    def _calculate_confidence(self, history: List[float]) -> float:
        """Calculate confidence in prediction."""
        if len(history) < 5:
            return 0.3
        
        # More history = higher confidence
        confidence = min(len(history) / self._history_size, 1.0)
        
        # Lower variance = higher confidence
        variance = max(history) - min(history)
        avg_value = sum(history) / len(history)
        if avg_value > 0 and variance > 0:
            volatility = variance / avg_value
            confidence *= (1.0 - min(volatility, 0.5))
        
        return max(confidence, 0.0)


class ResourceAllocator:
    """Allocates resources based on predictions and requirements."""
    
    def __init__(self):
        self._lock = threading.Lock()
        self._current_allocations: Dict[str, ResourceAllocation] = {}
        
        logger.info("[RESOURCE_ALLOCATOR] Initialized")
    
    def optimize(
        self,
        current_resources: Dict[str, float],
        predicted_workload: List[WorkloadPrediction],
        performance_targets: Dict[str, float]
    ) -> List[ResourceOptimization]:
        """
        Optimize resource allocation based on predictions.
        
        Args:
            current_resources: Current resource allocations
            predicted_workload: Predicted workload
            performance_targets: Performance targets
            
        Returns:
            Resource optimization recommendations
        """
        with self._lock:
            optimizations = []
            
            for prediction in predicted_workload:
                resource_name = prediction.resource_type.value.lower() + "_allocation"
                current_allocation = current_resources.get(resource_name, 0.0)
                max_capacity = current_resources.get(f"{resource_name}_max", 100.0)
                
                # Calculate recommended allocation
                if prediction.predicted_load > prediction.current_load * 1.1:
                    # Workload increasing
                    recommended = current_allocation * 1.2  # Scale up
                    recommended = min(recommended, max_capacity)
                    reason = f"Workload predicted to increase from {prediction.current_load:.1f}% to {prediction.predicted_load:.1f}%"
                    priority = "HIGH" if prediction.confidence > 0.7 else "MEDIUM"
                elif prediction.predicted_load < prediction.current_load * 0.8:
                    # Workload decreasing
                    recommended = current_allocation * 0.8  # Scale down
                    reason = f"Workload predicted to decrease from {prediction.current_load:.1f}% to {prediction.predicted_load:.1f}%"
                    priority = "LOW"
                else:
                    # Workload stable
                    recommended = current_allocation
                    reason = "Workload predicted to remain stable"
                    priority = "MEDIUM"
                
                # Calculate expected improvement
                improvement = abs(prediction.predicted_load - prediction.current_load) / prediction.current_load if prediction.current_load > 0 else 0.0
                
                if recommended != current_allocation:
                    optimization_id = f"opt_{int(datetime.utcnow().timestamp() * 1000)}"
                    optimizations.append(ResourceOptimization(
                        optimization_id=optimization_id,
                        resource_type=prediction.resource_type,
                        current_allocation=current_allocation,
                        recommended_allocation=recommended,
                        reason=reason,
                        expected_improvement=improvement * 100,  # Percentage
                        priority=priority
                    ))
            
            # Sort by priority
            priority_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
            optimizations.sort(key=lambda o: priority_order.get(o.priority, 99))
            
            return optimizations


class ScalingOptimizer:
    """Optimizes scaling decisions for resources."""
    
    def __init__(self):
        self._lock = threading.Lock()
        
        # Scaling thresholds
        self._scale_up_thresholds = {
            ResourceType.CPU: 80.0,
            ResourceType.MEMORY: 85.0,
            ResourceType.NETWORK: 75.0,
            ResourceType.IO: 80.0
        }
        
        self._scale_down_thresholds = {
            ResourceType.CPU: 30.0,
            ResourceType.MEMORY: 40.0,
            ResourceType.NETWORK: 25.0,
            ResourceType.IO: 30.0
        }
        
        logger.info("[SCALING_OPTIMIZER] Initialized")
    
    def generate_scaling_plan(
        self,
        optimized_allocation: ResourceOptimization
    ) -> ScalingPlan:
        """
        Generate scaling plan based on resource optimization.
        
        Args:
            optimized_allocation: Resource optimization recommendation
            
        Returns:
            Scaling plan
        """
        with self._lock:
            resource_type = optimized_allocation.resource_type
            current = optimized_allocation.current_allocation
            recommended = optimized_allocation.recommended_allocation
            
            # Determine scaling direction
            if recommended > current:
                # Scale up
                scale_factor = recommended / current if current > 0 else 1.5
                recommended_instances = int(max(scale_factor, 1.0) * 10) / 10  # Round to 1 decimal
                scale_up_threshold = self._scale_up_thresholds.get(resource_type, 80.0)
                scale_down_threshold = self._scale_down_thresholds.get(resource_type, 30.0)
            else:
                # Scale down
                scale_factor = recommended / current if current > 0 else 0.8
                recommended_instances = int(max(scale_factor, 0.5) * 10) / 10
                scale_up_threshold = self._scale_up_thresholds.get(resource_type, 80.0)
                scale_down_threshold = self._scale_down_thresholds.get(resource_type, 30.0)
            
            current_instances = int(current * 10) / 10 if current > 0 else 1
            
            return ScalingPlan(
                resource_type=resource_type,
                scale_up_threshold=scale_up_threshold,
                scale_down_threshold=scale_down_threshold,
                current_instances=current_instances,
                recommended_instances=recommended_instances,
                estimated_time_minutes=5.0
            )


class AdaptiveResourceManager:
    """
    Intelligent resource allocation based on execution patterns.
    
    Features:
    - Workload prediction
    - Resource optimization
    - Scaling plan generation
    - Performance target management
    - Adaptive resource adjustment
    """
    
    def __init__(self):
        self._lock = threading.Lock()
        
        # Components
        self._workload_predictor = WorkloadPredictor()
        self._resource_allocator = ResourceAllocator()
        self._scaling_optimizer = ScalingOptimizer()
        
        # Performance targets
        self._performance_targets = {
            "max_cpu_usage": 80.0,
            "max_memory_usage": 85.0,
            "max_latency_ms": 100.0,
            "min_throughput": 1000.0
        }
        
        # Resource monitoring
        self._current_resources: Dict[str, float] = {}
        
        logger.info("[ADAPTIVE_RESOURCE_MANAGER] Initialized")
    
    def optimize_resources(
        self,
        execution_metrics: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Optimize resource allocation based on execution patterns.
        
        Args:
            execution_metrics: Current execution metrics
            
        Returns:
            Resource optimization results
        """
        with self._lock:
            # Step 1: Predict workload
            predictions = self._workload_predictor.predict(execution_metrics)
            
            # Step 2: Get current resources
            current_resources = self._get_current_resources(execution_metrics)
            self._current_resources = current_resources
            
            # Step 3: Optimize allocation
            optimizations = self._resource_allocator.optimize(
                current_resources, predictions, self._performance_targets
            )
            
            # Step 4: Generate scaling plans
            scaling_plans = []
            for optimization in optimizations:
                scaling_plan = self._scaling_optimizer.generate_scaling_plan(optimization)
                scaling_plans.append(scaling_plan)
            
            # Step 5: Estimate improvement
            expected_improvement = self._estimate_improvement(optimizations, predictions)
            
            return {
                "predictions": [
                    {
                        "resource_type": p.resource_type.value,
                        "current_load": p.current_load,
                        "predicted_load": p.predicted_load,
                        "confidence": p.confidence
                    }
                    for p in predictions
                ],
                "optimizations": [
                    {
                        "resource_type": o.resource_type.value,
                        "current": o.current_allocation,
                        "recommended": o.recommended_allocation,
                        "reason": o.reason,
                        "priority": o.priority,
                        "expected_improvement": o.expected_improvement
                    }
                    for o in optimizations
                ],
                "scaling_plans": [
                    {
                        "resource_type": s.resource_type.value,
                        "current_instances": s.current_instances,
                        "recommended_instances": s.recommended_instances,
                        "estimated_time_minutes": s.estimated_time_minutes
                    }
                    for s in scaling_plans
                ],
                "expected_improvement": expected_improvement,
                "performance_targets": self._performance_targets
            }
    
    def _get_current_resources(self, execution_metrics: Dict[str, float]) -> Dict[str, float]:
        """Get current resource allocations from execution metrics."""
        return {
            "cpu_allocation": execution_metrics.get("cpu_usage", 0.0),
            "cpu_allocation_max": 100.0,
            "memory_allocation": execution_metrics.get("memory_usage", 0.0),
            "memory_allocation_max": 100.0,
            "network_allocation": execution_metrics.get("network_usage", 0.0),
            "network_allocation_max": 100.0,
            "io_allocation": execution_metrics.get("io_usage", 0.0),
            "io_allocation_max": 100.0
        }
    
    def _estimate_improvement(
        self,
        optimizations: List[ResourceOptimization],
        predictions: List[WorkloadPrediction]
    ) -> float:
        """Estimate expected improvement from optimizations."""
        if not optimizations:
            return 0.0
        
        total_improvement = sum(o.expected_improvement for o in optimizations)
        avg_improvement = total_improvement / len(optimizations)
        
        # Weight by prediction confidence
        avg_confidence = sum(p.confidence for p in predictions) / len(predictions) if predictions else 0.5
        
        return avg_improvement * avg_confidence
    
    def update_performance_targets(self, targets: Dict[str, float]) -> None:
        """Update performance targets."""
        with self._lock:
            self._performance_targets.update(targets)
            logger.info(f"[ADAPTIVE_RESOURCE_MANAGER] Updated performance targets: {targets}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get resource manager statistics."""
        with self._lock:
            return {
                "performance_targets": self._performance_targets,
                "current_resources": self._current_resources,
                "workload_history_size": self._workload_predictor._history_size
            }


# Singleton instance
_adaptive_resource_manager: Optional[AdaptiveResourceManager] = None
_adaptive_resource_manager_lock = threading.Lock()

def get_adaptive_resource_manager() -> AdaptiveResourceManager:
    """Get the singleton adaptive resource manager instance."""
    global _adaptive_resource_manager
    if _adaptive_resource_manager is None:
        with _adaptive_resource_manager_lock:
            if _adaptive_resource_manager is None:
                _adaptive_resource_manager = AdaptiveResourceManager()
    return _adaptive_resource_manager


__all__ = [
    "ResourceType",
    "ResourceAllocation",
    "WorkloadPrediction",
    "ResourceOptimization",
    "ScalingPlan",
    "WorkloadPredictor",
    "ResourceAllocator",
    "ScalingOptimizer",
    "AdaptiveResourceManager",
    "get_adaptive_resource_manager",
]