"""
intelligence_engine.evaluator
DIX VISION v42.2 — Production-Grade Evaluation Engine

Comprehensive evaluation metrics with multi-dimensional assessment,
performance tracking, quality assurance, and evaluation confidence calibration.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum
from collections import defaultdict
import statistics

from system.time_source import now

logger = logging.getLogger(__name__)


class EvaluationCategory(Enum):
    """Categories of evaluation."""
    PERFORMANCE = "performance"  # Performance metrics
    QUALITY = "quality"  # Quality metrics
    ROBUSTNESS = "robustness"  # Robustness metrics
    EFFICIENCY = "efficiency"  # Efficiency metrics
    COMPLIANCE = "compliance"  # Compliance metrics
    RELIABILITY = "reliability"  # Reliability metrics
    SCALABILITY = "scalability"  # Scalability metrics
    MAINTAINABILITY = "maintainability"  # Maintainability metrics


class EvaluationDimension(Enum):
    """Specific evaluation dimensions."""
    ACCURACY = "accuracy"
    PRECISION = "precision"
    RECALL = "recall"
    F1_SCORE = "f1_score"
    LATENCY = "latency"
    THROUGHPUT = "throughput"
    ERROR_RATE = "error_rate"
    COVERAGE = "coverage"
    STABILITY = "stability"
    CONSISTENCY = "consistency"


@dataclass
class EvaluationMetric:
    """A single evaluation metric."""
    metric_id: str
    name: str
    category: EvaluationCategory
    dimension: EvaluationDimension
    value: float = 0.0
    target: float = 0.0
    tolerance: float = 0.1
    unit: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_within_target(self) -> bool:
        """Check if metric is within target tolerance."""
        return abs(self.value - self.target) <= self.tolerance
    
    def get_performance_score(self) -> float:
        """Calculate performance score (0.0 to 1.0)."""
        if self.target == 0:
            return 0.5
        
        deviation = abs(self.value - self.target) / max(self.target, 1.0)
        score = max(0.0, 1.0 - deviation)
        return score


@dataclass
class EvaluationContext:
    """Context for evaluation."""
    context_id: str
    evaluation_purpose: str
    time_window: Dict[str, Any] = field(default_factory=dict)
    scope: List[str] = field(default_factory=list)
    benchmark: Optional[str] = None
    constraints: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EvaluationResult:
    """Result of an evaluation."""
    evaluation_id: str
    context: EvaluationContext
    metrics: List[EvaluationMetric] = field(default_factory=list)
    overall_score: float = 0.0
    category_scores: Dict[EvaluationCategory, float] = field(default_factory=dict)
    dimension_scores: Dict[EvaluationDimension, float] = field(default_factory=dict)
    confidence: float = 0.0
    recommendations: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    timestamp: str = ""


class ProductionEvaluator:
    """Production-grade evaluation engine.
    
    Provides:
    - Multi-dimensional evaluation metrics
    - Real-time performance tracking
    - Quality assurance metrics
    - Evaluation confidence calibration
    - Benchmark comparison
    """
    
    def __init__(self) -> None:
        self._evaluation_history: List[EvaluationResult] = []
        self._metric_targets: Dict[str, float] = {}
        self._evaluation_benchmarks: Dict[str, Dict[str, float]] = {}
        self._confidence_threshold = 0.7
        self._evaluation_intervals = {
            EvaluationCategory.PERFORMANCE: 60,    # 1 minute
            EvaluationCategory.QUALITY: 300,        # 5 minutes
            EvaluationCategory.ROBUSTNESS: 1800,    # 30 minutes
            EvaluationCategory.EFFICIENCY: 60,       # 1 minute
            EvaluationCategory.COMPLIANCE: 3600,     # 1 hour
            EvaluationCategory.RELIABILITY: 600,     # 10 minutes
            EvaluationCategory.SCALABILITY: 1800,     # 30 minutes
            EvaluationCategory.MAINTAINABILITY: 3600  # 1 hour
        }
        
    def start(self) -> bool:
        """Start the evaluation engine."""
        try:
            logger.info("[EVALUATOR] Production evaluation engine started")
            return True
        except Exception as e:
            logger.error(f"[EVALUATOR] Failed to start: {e}")
            return False
    
    def stop(self) -> bool:
        """Stop the evaluation engine."""
        try:
            logger.info("[EVALUATOR] Production evaluation engine stopped")
            return True
        except Exception as e:
            logger.error(f"[EVALUATOR] Failed to stop: {e}")
            return False
    
    def set_metric_target(self, metric_name: str, target: float, tolerance: float = 0.1) -> None:
        """Set target value for a metric."""
        self._metric_targets[metric_name] = {
            "target": target,
            "tolerance": tolerance
        }
        logger.info(f"[EVALUATOR] Set target for {metric_name}: {target} ± {tolerance}")
    
    def set_benchmark(self, benchmark_id: str, benchmark_values: Dict[str, float]) -> None:
        """Set benchmark values."""
        self._evaluation_benchmarks[benchmark_id] = benchmark_values
        logger.info(f"[EVALUATOR] Set benchmark: {benchmark_id}")
    
    def evaluate(self, 
                data: Dict[str, Any],
                context: EvaluationContext,
                categories: Optional[List[EvaluationCategory]] = None) -> EvaluationResult:
        """Perform comprehensive evaluation.
        
        Args:
            data: Input data for evaluation
            context: Evaluation context
            categories: Specific categories to evaluate (all if None)
            
        Returns:
            EvaluationResult with metrics and scores
        """
        try:
            evaluation_id = f"evaluation_{now().sequence}"
            logger.info(f"[EVALUATOR] Starting evaluation: {evaluation_id}")
            
            categories = categories or list(EvaluationCategory)
            metrics = []
            
            # Generate metrics for each category
            for category in categories:
                category_metrics = self._evaluate_category(data, category, context)
                metrics.extend(category_metrics)
            
            # Calculate overall score
            overall_score = self._calculate_overall_score(metrics)
            
            # Calculate category scores
            category_scores = self._calculate_category_scores(metrics)
            
            # Calculate dimension scores
            dimension_scores = self._calculate_dimension_scores(metrics)
            
            # Calculate evaluation confidence
            confidence = self._calculate_evaluation_confidence(metrics, context)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(metrics, category_scores)
            
            # Generate warnings
            warnings = self._generate_warnings(metrics, category_scores)
            
            result = EvaluationResult(
                evaluation_id=evaluation_id,
                context=context,
                metrics=metrics,
                overall_score=overall_score,
                category_scores=category_scores,
                dimension_scores=dimension_scores,
                confidence=confidence,
                recommendations=recommendations,
                warnings=warnings,
                timestamp=now().utc_time.isoformat()
            )
            
            # Store in history
            self._evaluation_history.append(result)
            
            logger.info(f"[EVALUATOR] Evaluation complete: {evaluation_id} with score {overall_score:.2f}")
            return result
            
        except Exception as e:
            logger.error(f"[EVALUATOR] Evaluation failed: {e}")
            return self._create_error_result(context, str(e))
    
    def _evaluate_category(self, 
                          data: Dict[str, Any], 
                          category: EvaluationCategory,
                          context: EvaluationContext) -> List[EvaluationMetric]:
        """Evaluate a specific category."""
        metrics = []
        
        # Generate appropriate metrics based on category
        if category == EvaluationCategory.PERFORMANCE:
            metrics.extend(self._evaluate_performance(data, context))
        elif category == EvaluationCategory.QUALITY:
            metrics.extend(self._evaluate_quality(data, context))
        elif category == EvaluationCategory.ROBUSTNESS:
            metrics.extend(self._evaluate_robustness(data, context))
        elif category == EvaluationCategory.EFFICIENCY:
            metrics.extend(self._evaluate_efficiency(data, context))
        elif category == EvaluationCategory.COMPLIANCE:
            metrics.extend(self._evaluate_compliance(data, context))
        elif category == EvaluationCategory.RELIABILITY:
            metrics.extend(self._evaluate_reliability(data, context))
        elif category == EvaluationCategory.SCALABILITY:
            metrics.extend(self._evaluate_scalability(data, context))
        elif category == EvaluationCategory.MAINTAINABILITY:
            metrics.extend(self._evaluate_maintainability(data, context))
        
        return metrics
    
    def _evaluate_performance(self, data: Dict[str, Any], 
                             context: EvaluationContext) -> List[EvaluationMetric]:
        """Evaluate performance metrics."""
        metrics = []
        
        # Latency
        latency = data.get("latency_ms", 100.0)
        latency_target = self._metric_targets.get("latency", {}).get("target", 50.0)
        latency_tolerance = self._metric_targets.get("latency", {}).get("tolerance", 0.1)
        
        metrics.append(EvaluationMetric(
            metric_id=f"perf_latency_{now().sequence}",
            name="Latency",
            category=EvaluationCategory.PERFORMANCE,
            dimension=EvaluationDimension.LATENCY,
            value=latency,
            target=latency_target,
            tolerance=latency_tolerance,
            unit="ms"
        ))
        
        # Throughput
        throughput = data.get("throughput_ops", 100.0)
        throughput_target = self._metric_targets.get("throughput", {}).get("target", 1000.0)
        throughput_tolerance = self._metric_targets.get("throughput", {}).get("tolerance", 0.1)
        
        metrics.append(EvaluationMetric(
            metric_id=f"perf_throughput_{now().sequence}",
            name="Throughput",
            category=EvaluationCategory.PERFORMANCE,
            dimension=EvaluationDimension.THROUGHPUT,
            value=throughput,
            target=throughput_target,
            tolerance=throughput_tolerance,
            unit="ops/sec"
        ))
        
        return metrics
    
    def _evaluate_quality(self, data: Dict[str, Any], 
                        context: EvaluationContext) -> List[EvaluationMetric]:
        """Evaluate quality metrics."""
        metrics = []
        
        # Accuracy
        accuracy = data.get("accuracy", 0.85)
        accuracy_target = self._metric_targets.get("accuracy", {}).get("target", 0.95)
        accuracy_tolerance = self._metric_targets.get("accuracy", {}).get("tolerance", 0.05)
        
        metrics.append(EvaluationMetric(
            metric_id=f"quality_accuracy_{now().sequence}",
            name="Accuracy",
            category=EvaluationCategory.QUALITY,
            dimension=EvaluationDimension.ACCURACY,
            value=accuracy,
            target=accuracy_target,
            tolerance=accuracy_tolerance
        ))
        
        # Precision
        precision = data.get("precision", 0.88)
        precision_target = self._metric_targets.get("precision", {}).get("target", 0.92)
        precision_tolerance = self._metric_targets.get("precision", {}).get("tolerance", 0.05)
        
        metrics.append(EvaluationMetric(
            metric_id=f"quality_precision_{now().sequence}",
            name="Precision",
            category=EvaluationCategory.QUALITY,
            dimension=EvaluationDimension.PRECISION,
            value=precision,
            target=precision_target,
            tolerance=precision_tolerance
        ))
        
        return metrics
    
    def _evaluate_robustness(self, data: Dict[str, Any], 
                           context: EvaluationContext) -> List[EvaluationMetric]:
        """Evaluate robustness metrics."""
        metrics = []
        
        # Error rate
        error_rate = data.get("error_rate", 0.01)
        error_rate_target = self._metric_targets.get("error_rate", {}).get("target", 0.001)
        error_rate_tolerance = self._metric_targets.get("error_rate", {}).get("tolerance", 0.001)
        
        metrics.append(EvaluationMetric(
            metric_id=f"robust_error_rate_{now().sequence}",
            name="Error Rate",
            category=EvaluationCategory.ROBUSTNESS,
            dimension=EvaluationDimension.ERROR_RATE,
            value=error_rate,
            target=error_rate_target,
            tolerance=error_rate_tolerance
        ))
        
        # Stability
        stability = data.get("stability", 0.9)
        stability_target = self._metric_targets.get("stability", {}).get("target", 0.95)
        stability_tolerance = self._metric_targets.get("stability", {}).get("tolerance", 0.05)
        
        metrics.append(EvaluationMetric(
            metric_id=f"robust_stability_{now().sequence}",
            name="Stability",
            category=EvaluationCategory.ROBUSTNESS,
            dimension=EvaluationDimension.STABILITY,
            value=stability,
            target=stability_target,
            tolerance=stability_tolerance
        ))
        
        return metrics
    
    def _evaluate_efficiency(self, data: Dict[str, Any], 
                            context: EvaluationContext) -> List[EvaluationMetric]:
        """Evaluate efficiency metrics."""
        metrics = []
        
        # Resource utilization
        cpu_usage = data.get("cpu_usage", 0.5)
        cpu_target = self._metric_targets.get("cpu_usage", {}).get("target", 0.7)
        cpu_tolerance = self._metric_targets.get("cpu_usage", {}).get("tolerance", 0.1)
        
        metrics.append(EvaluationMetric(
            metric_id=f"efficiency_cpu_{now().sequence}",
            name="CPU Usage",
            category=EvaluationCategory.EFFICIENCY,
            dimension=EvaluationDimension.CONSISTENCY,
            value=cpu_usage,
            target=cpu_target,
            tolerance=cpu_tolerance
        ))
        
        return metrics
    
    def _evaluate_compliance(self, data: Dict[str, Any], 
                           context: EvaluationContext) -> List[EvaluationMetric]:
        """Evaluate compliance metrics."""
        metrics = []
        
        # Coverage
        coverage = data.get("coverage", 0.8)
        coverage_target = self._metric_targets.get("coverage", {}).get("target", 0.95)
        coverage_tolerance = self._metric_targets.get("coverage", {}).get("tolerance", 0.05)
        
        metrics.append(EvaluationMetric(
            metric_id=f"compliance_coverage_{now().sequence}",
            name="Coverage",
            category=EvaluationCategory.COMPLIANCE,
            dimension=EvaluationDimension.COVERAGE,
            value=coverage,
            target=coverage_target,
            tolerance=coverage_tolerance
        ))
        
        return metrics
    
    def _evaluate_reliability(self, data: Dict[str, Any], 
                             context: EvaluationContext) -> List[EvaluationMetric]:
        """Evaluate reliability metrics."""
        metrics = []
        
        # Uptime
        uptime = data.get("uptime_percentage", 99.5)
        uptime_target = self._metric_targets.get("uptime", {}).get("target", 99.9)
        uptime_tolerance = self._metric_targets.get("uptime", {}).get("tolerance", 0.1)
        
        metrics.append(EvaluationMetric(
            metric_id=f"reliability_uptime_{now().sequence}",
            name="Uptime",
            category=EvaluationCategory.RELIABILITY,
            dimension=EvaluationDimension.CONSISTENCY,
            value=uptime,
            target=uptime_target,
            tolerance=uptime_tolerance,
            unit="%"
        ))
        
        return metrics
    
    def _evaluate_scalability(self, data: Dict[str, Any], 
                            context: EvaluationContext) -> List[EvaluationMetric]:
        """Evaluate scalability metrics."""
        metrics = []
        
        # Concurrent users
        concurrent_users = data.get("concurrent_users", 1000)
        users_target = self._metric_targets.get("concurrent_users", {}).get("target", 10000)
        users_tolerance = self._metric_targets.get("concurrent_users", {}).get("tolerance", 0.2)
        
        metrics.append(EvaluationMetric(
            metric_id=f"scalability_users_{now().sequence}",
            name="Concurrent Users",
            category=EvaluationCategory.SCALABILITY,
            dimension=EvaluationDimension.CONSISTENCY,
            value=concurrent_users,
            target=users_target,
            tolerance=users_tolerance
        ))
        
        return metrics
    
    def _evaluate_maintainability(self, data: Dict[str, Any], 
                                 context: EvaluationContext) -> List[EvaluationMetric]:
        """Evaluate maintainability metrics."""
        metrics = []
        
        # Code complexity
        complexity = data.get("code_complexity", 50)
        complexity_target = self._metric_targets.get("code_complexity", {}).get("target", 30)
        complexity_tolerance = self._metric_targets.get("code_complexity", {}).get("tolerance", 10)
        
        metrics.append(EvaluationMetric(
            metric_id=f"maintain_complexity_{now().sequence}",
            name="Code Complexity",
            category=EvaluationCategory.MAINTAINABILITY,
            dimension=EvaluationDimension.CONSISTENCY,
            value=complexity,
            target=complexity_target,
            tolerance=complexity_tolerance
        ))
        
        return metrics
    
    def _calculate_overall_score(self, metrics: List[EvaluationMetric]) -> float:
        """Calculate overall evaluation score."""
        if not metrics:
            return 0.0
        
        performance_scores = [metric.get_performance_score() for metric in metrics]
        return statistics.mean(performance_scores)
    
    def _calculate_category_scores(self, metrics: List[EvaluationMetric]) -> Dict[EvaluationCategory, float]:
        """Calculate scores by category."""
        category_metrics = defaultdict(list)
        
        for metric in metrics:
            category_metrics[metric.category].append(metric)
        
        category_scores = {}
        for category, cat_metrics in category_metrics.items():
            if cat_metrics:
                scores = [m.get_performance_score() for m in cat_metrics]
                category_scores[category] = statistics.mean(scores)
            else:
                category_scores[category] = 0.0
        
        return category_scores
    
    def _calculate_dimension_scores(self, metrics: List[EvaluationMetric]) -> Dict[EvaluationDimension, float]:
        """Calculate scores by dimension."""
        dimension_metrics = defaultdict(list)
        
        for metric in metrics:
            dimension_metrics[metric.dimension].append(metric)
        
        dimension_scores = {}
        for dimension, dim_metrics in dimension_metrics.items():
            if dim_metrics:
                scores = [m.get_performance_score() for m in dim_metrics]
                dimension_scores[dimension] = statistics.mean(scores)
            else:
                dimension_scores[dimension] = 0.0
        
        return dimension_scores
    
    def _calculate_evaluation_confidence(self, 
                                       metrics: List[EvaluationMetric],
                                       context: EvaluationContext) -> float:
        """Calculate confidence in evaluation."""
        if not metrics:
            return 0.0
        
        # Confidence based on data quality
        data_quality = context.metadata.get("data_quality", 0.8)
        
        # Confidence based on metric count
        metric_count_factor = min(1.0, len(metrics) / 10.0)
        
        # Confidence based on metric variance
        performance_scores = [m.get_performance_score() for m in metrics]
        if performance_scores:
            score_variance = statistics.variance(performance_scores)
            variance_factor = max(0.0, 1.0 - score_variance)
        else:
            variance_factor = 0.0
        
        # Combine factors
        confidence = (data_quality * 0.4 + 
                     metric_count_factor * 0.3 + 
                     variance_factor * 0.3)
        
        return confidence
    
    def _generate_recommendations(self, metrics: List[EvaluationMetric],
                                 category_scores: Dict[EvaluationCategory, float]) -> List[str]:
        """Generate evaluation recommendations."""
        recommendations = []
        
        # Check for metrics not meeting targets
        for metric in metrics:
            if not metric.is_within_target():
                recommendations.append(
                    f"Improve {metric.name}: current {metric.value} vs target {metric.target}"
                )
        
        # Check for low category scores
        for category, score in category_scores.items():
            if score < 0.7:
                recommendations.append(
                    f"Focus on {category.value}: score {score:.2f} below threshold"
                )
        
        if not recommendations:
            recommendations.append("All metrics performing within acceptable ranges")
        
        return recommendations
    
    def _generate_warnings(self, metrics: List[EvaluationMetric],
                          category_scores: Dict[EvaluationCategory, float]) -> List[str]:
        """Generate evaluation warnings."""
        warnings = []
        
        # Critical metric warnings
        for metric in metrics:
            if metric.get_performance_score() < 0.3:
                warnings.append(f"Critical: {metric.name} performance severely degraded")
        
        # Category warnings
        for category, score in category_scores.items():
            if score < 0.5:
                warnings.append(f"Warning: {category.value} category score critical")
        
        return warnings
    
    def _create_error_result(self, context: EvaluationContext, error: str) -> EvaluationResult:
        """Create error evaluation result."""
        return EvaluationResult(
            evaluation_id=f"evaluation_{now().sequence}",
            context=context,
            overall_score=0.0,
            confidence=0.0,
            recommendations=[],
            warnings=[f"Evaluation error: {error}"],
            timestamp=now().utc_time.isoformat()
        )
    
    def get_evaluation_history(self, limit: int = 100) -> List[EvaluationResult]:
        """Get evaluation history."""
        return self._evaluation_history[-limit:]
    
    def get_evaluation_statistics(self) -> Dict[str, Any]:
        """Get evaluation statistics."""
        if not self._evaluation_history:
            return {"message": "No evaluations performed yet"}
        
        by_category = defaultdict(list)
        total_score = 0.0
        
        for evaluation in self._evaluation_history:
            total_score += evaluation.overall_score
            for category, score in evaluation.category_scores.items():
                by_category[category.value].append(score)
        
        avg_score = total_score / len(self._evaluation_history)
        
        category_averages = {}
        for category, scores in by_category.items():
            category_averages[category] = statistics.mean(scores)
        
        return {
            "total_evaluations": len(self._evaluation_history),
            "average_score": avg_score,
            "category_averages": category_averages
        }
    
    def clear_history(self) -> None:
        """Clear evaluation history."""
        self._evaluation_history.clear()
        logger.info("[EVALUATOR] Evaluation history cleared")


def get_production_evaluator() -> ProductionEvaluator:
    """Get the singleton production evaluator instance."""
    if not hasattr(get_production_evaluator, "_instance"):
        get_production_evaluator._instance = ProductionEvaluator()
    return get_production_evaluator._instance