"""
DIX VISION Execution-Learning Feedback Loop

Integrates the execution system with the learning engine to create
a closed feedback loop where execution quality informs learning and
learning improvements enhance execution.
"""

from __future__ import annotations

import logging
import threading
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
import numpy as np

# Import existing execution system
import sys
sys.path.insert(0, "c:/dix_vision_v42.2/containers/system_core/execution_unified")
from adapters.adapter_wrappers import get_all_available_adapters

# Import existing learning engine
import sys
sys.path.insert(0, "c:/dix_vision_v42.2/containers/system_core/learning_engine")
from loops.closed_loop import ClosedLearningLoop
from performance_analysis.execution_quality import ExecutionQualityAnalyzer

logger = logging.getLogger(__name__)


@dataclass
class ExecutionQualityMetrics:
    """Metrics for execution quality."""
    execution_id: str
    strategy: str
    venue: str
    latency_ms: float
    slippage_bps: float
    fill_rate: float
    execution_quality_score: float
    cost_efficiency: float
    timestamp: float


@dataclass
class LearningFeedbackSignal:
    """Feedback signal from execution to learning."""
    feedback_id: str
    execution_quality: ExecutionQualityMetrics
    learning_implications: Dict[str, Any]
    recommended_adjustments: List[str]
    priority: float
    timestamp: float


@dataclass
class LearningExecutionUpdate:
    """Update from learning to execution."""
    update_id: str
    learning_insights: Dict[str, Any]
    execution_recommendations: List[str]
    parameter_adjustments: Dict[str, float]
    expected_improvement: float
    timestamp: float


@dataclass
class FeedbackLoopIteration:
    """Single iteration of the execution-learning feedback loop."""
    iteration_id: str
    execution_metrics: ExecutionQualityMetrics
    learning_feedback: LearningFeedbackSignal
    learning_updates: LearningExecutionUpdate
    iteration_quality_score: float
    improvement_achieved: float
    timestamp: datetime = field(default_factory=datetime.now)


class ExecutionLearningFeedbackLoop:
    """
    Closed feedback loop between execution and learning systems.
    
    Creates a virtuous cycle where:
    - Execution quality metrics inform learning priorities
    - Learning insights guide execution improvements
    - Both systems co-evolve for optimal performance
    """
    
    def __init__(self):
        # Initialize execution system components
        self._available_adapters = get_all_available_adapters()
        
        # Initialize learning system components
        self._learning_loop = ClosedLearningLoop()
        self._execution_analyzer = ExecutionQualityAnalyzer()
        
        # Feedback loop state
        self._execution_history: deque = deque(maxlen=1000)
        self._learning_feedback_history: List[LearningFeedbackSignal] = []
        self._learning_updates_history: List[LearningExecutionUpdate] = []
        self._feedback_loop_iterations: List[FeedbackLoopIteration] = []
        
        # Feedback loop parameters
        self._feedback_threshold = 0.7  # Quality threshold for triggering feedback
        self._learning_rate = 0.1
        self._adaptation_speed = 0.5
        
        # Performance tracking
        self._performance_trend: deque = deque(maxlen=100)
        
        self._lock = threading.Lock()
        
        logger.info("Execution-Learning Feedback Loop initialized")
    
    def capture_execution_metrics(self, execution_data: Dict[str, Any]) -> ExecutionQualityMetrics:
        """Capture and analyze execution quality metrics."""
        # Extract execution data
        execution_id = execution_data.get("execution_id", f"exec_{int(datetime.now().timestamp())}")
        strategy = execution_data.get("strategy", "unknown")
        venue = execution_data.get("venue", "unknown")
        
        # Calculate execution quality metrics
        latency_ms = execution_data.get("latency_ms", 100.0)
        slippage_bps = execution_data.get("slippage_bps", 5.0)
        fill_rate = execution_data.get("fill_rate", 0.95)
        
        # Calculate execution quality score
        execution_quality_score = self._calculate_execution_quality_score(
            latency_ms, slippage_bps, fill_rate
        )
        
        # Calculate cost efficiency
        cost_efficiency = self._calculate_cost_efficiency(
            execution_data.get("execution_cost", 0.0),
            execution_data.get("trade_value", 1.0)
        )
        
        metrics = ExecutionQualityMetrics(
            execution_id=execution_id,
            strategy=strategy,
            venue=venue,
            latency_ms=latency_ms,
            slippage_bps=slippage_bps,
            fill_rate=fill_rate,
            execution_quality_score=execution_quality_score,
            cost_efficiency=cost_efficiency,
            timestamp=datetime.now().timestamp()
        )
        
        with self._lock:
            self._execution_history.append(metrics)
            self._performance_trend.append(execution_quality_score)
        
        return metrics
    
    def _calculate_execution_quality_score(self, latency_ms: float, 
                                          slippage_bps: float, fill_rate: float) -> float:
        """Calculate overall execution quality score (0.0-1.0)."""
        # Normalize metrics
        latency_score = max(0.0, 1.0 - (latency_ms / 1000.0))  # 1s is poor
        slippage_score = max(0.0, 1.0 - (slippage_bps / 50.0))  # 50bps is poor
        fill_score = fill_rate
        
        # Weighted average
        quality_score = (
            latency_score * 0.3 +
            slippage_score * 0.4 +
            fill_score * 0.3
        )
        
        return quality_score
    
    def _calculate_cost_efficiency(self, execution_cost: float, trade_value: float) -> float:
        """Calculate cost efficiency (0.0-1.0)."""
        if trade_value == 0:
            return 0.0
        
        cost_ratio = execution_cost / trade_value
        efficiency = max(0.0, 1.0 - (cost_ratio / 0.01))  # 1% cost is poor
        
        return efficiency
    
    def generate_learning_feedback(self, execution_metrics: ExecutionQualityMetrics) -> LearningFeedbackSignal:
        """Generate learning feedback from execution metrics."""
        learning_implications = {}
        recommended_adjustments = []
        priority = 0.0
        
        # Analyze execution quality for learning implications
        if execution_metrics.execution_quality_score < self._feedback_threshold:
            # Poor execution quality - high priority feedback
            priority = 0.9
            
            learning_implications["execution_quality"] = "poor"
            learning_implications["primary_issues"] = []
            
            if execution_metrics.latency_ms > 500:
                learning_implications["primary_issues"].append("high_latency")
                recommended_adjustments.append("Optimize execution path for reduced latency")
                recommended_adjustments.append("Consider venue switching for faster execution")
            
            if execution_metrics.slippage_bps > 10:
                learning_implications["primary_issues"].append("high_slippage")
                recommended_adjustments.append("Improve order routing algorithms")
                recommended_adjustments.append("Adjust timing strategies for better fill prices")
            
            if execution_metrics.fill_rate < 0.9:
                learning_implications["primary_issues"].append("low_fill_rate")
                recommended_adjustments.append("Review venue selection criteria")
                recommended_adjustments.append("Adjust order sizing for better fills")
        
        else:
            # Good execution quality - lower priority feedback
            priority = 0.3
            learning_implications["execution_quality"] = "good"
            recommended_adjustments.append("Maintain current execution parameters")
            recommended_adjustments.append("Continue monitoring for optimization opportunities")
        
        # Strategy-specific learning implications
        if execution_metrics.strategy == "microstructure":
            if execution_metrics.slippage_bps > 5:
                learning_implications["strategy_focus"] = "spread_optimization"
                recommended_adjustments.append("Enhance spread detection algorithms")
        elif execution_metrics.strategy == "volatility":
            if execution_metrics.latency_ms > 200:
                learning_implications["strategy_focus"] = "speed_optimization"
                recommended_adjustments.append("Prioritize execution speed for volatility strategies")
        
        feedback = LearningFeedbackSignal(
            feedback_id=f"feedback_{int(datetime.now().timestamp())}",
            execution_quality=execution_metrics,
            learning_implications=learning_implications,
            recommended_adjustments=recommended_adjustments,
            priority=priority,
            timestamp=datetime.now().timestamp()
        )
        
        with self._lock:
            self._learning_feedback_history.append(feedback)
        
        return feedback
    
    def generate_learning_updates(self, feedback_signals: List[LearningFeedbackSignal]) -> LearningExecutionUpdate:
        """Generate learning updates for execution system."""
        # Aggregate feedback signals
        high_priority_signals = [f for f in feedback_signals if f.priority > 0.7]
        
        learning_insights = {
            "total_feedback_signals": len(feedback_signals),
            "high_priority_signals": len(high_priority_signals),
            "average_execution_quality": np.mean([
                f.execution_quality.execution_quality_score for f in feedback_signals
            ]) if feedback_signals else 0.0,
            "primary_issues": self._aggregate_primary_issues(feedback_signals)
        }
        
        # Generate execution recommendations
        execution_recommendations = []
        parameter_adjustments = {}
        
        if high_priority_signals:
            # Focus on high-priority issues
            for signal in high_priority_signals:
                execution_recommendations.extend(signal.recommended_adjustments)
            
            # Calculate parameter adjustments
            avg_latency = np.mean([f.execution_quality.latency_ms for f in high_priority_signals])
            avg_slippage = np.mean([f.execution_quality.slippage_bps for f in high_priority_signals])
            
            if avg_latency > 500:
                parameter_adjustments["latency_target"] = 300.0
                parameter_adjustments["timeout_ms"] = 200.0
            if avg_slippage > 10:
                parameter_adjustments["slippage_tolerance"] = 5.0
                parameter_adjustments["order_size_multiplier"] = 0.8
        else:
            execution_recommendations.append("Maintain current execution parameters")
            execution_recommendations.append("Continue performance monitoring")
        
        # Calculate expected improvement
        current_quality = learning_insights["average_execution_quality"]
        expected_improvement = (1.0 - current_quality) * self._adaptation_speed
        
        update = LearningExecutionUpdate(
            update_id=f"update_{int(datetime.now().timestamp())}",
            learning_insights=learning_insights,
            execution_recommendations=execution_recommendations,
            parameter_adjustments=parameter_adjustments,
            expected_improvement=expected_improvement,
            timestamp=datetime.now().timestamp()
        )
        
        with self._lock:
            self._learning_updates_history.append(update)
        
        return update
    
    def execute_feedback_loop_iteration(self, execution_data: Dict[str, Any]) -> FeedbackLoopIteration:
        """Execute a complete feedback loop iteration."""
        # Step 1: Capture execution metrics
        execution_metrics = self.capture_execution_metrics(execution_data)
        
        # Step 2: Generate learning feedback
        learning_feedback = self.generate_learning_feedback(execution_metrics)
        
        # Step 3: Generate learning updates (aggregated from recent feedback)
        recent_feedback = self._learning_feedback_history[-10:] if self._learning_feedback_history else []
        learning_updates = self.generate_learning_updates(recent_feedback)
        
        # Step 4: Calculate iteration quality
        iteration_quality_score = (
            execution_metrics.execution_quality_score * 0.6 +
            (1.0 - learning_feedback.priority) * 0.4
        )
        
        # Step 5: Calculate improvement achieved
        improvement_achieved = 0.0
        if len(self._performance_trend) > 1:
            improvement_achieved = self._performance_trend[-1] - self._performance_trend[-2]
        
        iteration = FeedbackLoopIteration(
            iteration_id=f"iteration_{int(datetime.now().timestamp())}",
            execution_metrics=execution_metrics,
            learning_feedback=learning_feedback,
            learning_updates=learning_updates,
            iteration_quality_score=iteration_quality_score,
            improvement_achieved=improvement_achieved
        )
        
        with self._lock:
            self._feedback_loop_iterations.append(iteration)
        
        logger.info(f"Feedback loop iteration completed: quality={iteration_quality_score:.2f}, improvement={improvement_achieved:.3f}")
        
        return iteration
    
    def apply_learning_updates_to_execution(self, learning_update: LearningExecutionUpdate) -> Dict[str, Any]:
        """Apply learning updates to execution system."""
        applied_changes = {}
        
        # Apply parameter adjustments
        for param, value in learning_update.parameter_adjustments.items():
            # This would interface with actual execution system
            applied_changes[param] = value
            logger.info(f"Applied parameter adjustment: {param} = {value}")
        
        # Log recommendations
        for recommendation in learning_update.execution_recommendations:
            logger.info(f"Execution recommendation: {recommendation}")
        
        return applied_changes
    
    def get_feedback_loop_status(self) -> Dict[str, Any]:
        """Get comprehensive feedback loop status."""
        with self._lock:
            recent_iterations = self._feedback_loop_iterations[-10:] if self._feedback_loop_iterations else []
            
            if not recent_iterations:
                return {"status": "No iterations completed yet"}
            
            average_quality = np.mean([i.iteration_quality_score for i in recent_iterations])
            average_improvement = np.mean([i.improvement_achieved for i in recent_iterations])
            
            improvement_trend = "improving" if average_improvement > 0 else "stable" if abs(average_improvement) < 0.01 else "declining"
            
            return {
                "total_iterations": len(self._feedback_loop_iterations),
                "recent_iterations": len(recent_iterations),
                "average_iteration_quality": average_quality,
                "average_improvement": average_improvement,
                "improvement_trend": improvement_trend,
                "total_executions_analyzed": len(self._execution_history),
                "total_feedback_signals": len(self._learning_feedback_history),
                "total_learning_updates": len(self._learning_updates_history),
                "feedback_threshold": self._feedback_threshold,
                "adaptation_speed": self._adaptation_speed
            }
    
    def adjust_feedback_parameters(self, feedback_threshold: float = None,
                                 learning_rate: float = None,
                                 adaptation_speed: float = None) -> None:
        """Adjust feedback loop parameters."""
        if feedback_threshold is not None:
            self._feedback_threshold = max(0.0, min(1.0, feedback_threshold))
        
        if learning_rate is not None:
            self._learning_rate = max(0.01, min(1.0, learning_rate))
        
        if adaptation_speed is not None:
            self._adaptation_speed = max(0.1, min(1.0, adaptation_speed))
        
        logger.info(f"Adjusted feedback parameters: threshold={self._feedback_threshold}, "
                   f"learning_rate={self._learning_rate}, adaptation_speed={self._adaptation_speed}")


class AdaptiveExecutionOptimizer:
    """
    Adaptive execution optimizer using learning feedback.
    
    Continuously optimizes execution parameters based on
    learning feedback from execution quality analysis.
    """
    
    def __init__(self):
        self._feedback_loop = ExecutionLearningFeedbackLoop()
        self._optimization_history: List[Dict[str, Any]] = []
        
        self._lock = threading.Lock()
        
        logger.info("Adaptive Execution Optimizer initialized")
    
    def optimize_execution(self, execution_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize execution based on learning feedback."""
        # Execute feedback loop iteration
        iteration = self._feedback_loop.execute_feedback_loop_iteration(execution_data)
        
        # Apply learning updates if quality is below threshold
        optimization_applied = False
        if iteration.execution_metrics.execution_quality_score < self._feedback_loop._feedback_threshold:
            applied_changes = self._feedback_loop.apply_learning_updates_to_execution(
                iteration.learning_updates
            )
            optimization_applied = True
            
            with self._lock:
                self._optimization_history.append({
                    "timestamp": datetime.now().isoformat(),
                    "applied_changes": applied_changes,
                    "expected_improvement": iteration.learning_updates.expected_improvement
                })
        
        return {
            "iteration_id": iteration.iteration_id,
            "execution_quality": iteration.execution_metrics.execution_quality_score,
            "optimization_applied": optimization_applied,
            "learning_updates": iteration.learning_updates.execution_recommendations,
            "expected_improvement": iteration.learning_updates.expected_improvement
        }
    
    def get_optimization_status(self) -> Dict[str, Any]:
        """Get optimization status."""
        feedback_status = self._feedback_loop.get_feedback_loop_status()
        
        with self._lock:
            return {
                **feedback_status,
                "total_optimizations": len(self._optimization_history),
                "recent_optimizations": self._optimization_history[-5:] if self._optimization_history else []
            }


# Global instances
_execution_learning_feedback_loop: Optional[ExecutionLearningFeedbackLoop] = None
_adaptive_execution_optimizer: Optional[AdaptiveExecutionOptimizer] = None


def get_execution_learning_feedback_loop() -> ExecutionLearningFeedbackLoop:
    """Get global execution-learning feedback loop instance."""
    global _execution_learning_feedback_loop
    if _execution_learning_feedback_loop is None:
        _execution_learning_feedback_loop = ExecutionLearningFeedbackLoop()
    return _execution_learning_feedback_loop


def get_adaptive_execution_optimizer() -> AdaptiveExecutionOptimizer:
    """Get global adaptive execution optimizer instance."""
    global _adaptive_execution_optimizer
    if _adaptive_execution_optimizer is None:
        _adaptive_execution_optimizer = AdaptiveExecutionOptimizer()
    return _adaptive_execution_optimizer