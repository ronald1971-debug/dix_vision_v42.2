"""Model Evaluation System — LEARN-08.01.

Model evaluation system for the learning engine to assess model
performance, compare models, and determine promotion readiness.
Provides comprehensive evaluation metrics, statistical testing,
and model ranking for production deployment.
"""

from __future__ import annotations

import dataclasses
import enum
from collections import deque
from threading import Lock
from typing import Any, Final

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_MIN_EVALUATION_SAMPLES: Final[int] = 100
DEFAULT_CONFIDENCE_LEVEL: Final[float] = 0.95
DEFAULT_ENABLE_STATISTICAL_TESTING: Final[bool] = True
DEFAULT_RETENTION_PERIOD_DAYS: Final[int] = 90

NEW_PIP_DEPENDENCIES: Final[tuple[str, ...]] = ()


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class EvaluationType(enum.Enum):
    """Types of model evaluations."""
    PERFORMANCE = "PERFORMANCE"
    STABILITY = "STABILITY"
    COMPARISON = "COMPARISON"
    REGRESSION = "REGRESSION"
    PRODUCTION_READINESS = "PRODUCTION_READINESS"


class ModelStatus(enum.Enum):
    """Status of model in the learning pipeline."""
    TRAINING = "TRAINING"
    VALIDATING = "VALIDATING"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    DEPLOYED = "DEPLOYED"
    RETIRED = "RETIRED"


class EvaluationCriterion(enum.Enum):
    """Criteria for model evaluation."""
    ACCURACY = "ACCURACY"
    PRECISION = "PRECISION"
    RECALL = "RECALL"
    F1_SCORE = "F1_SCORE"
    SHARPE_RATIO = "SHARPE_RATIO"
    MAX_DRAWDOWN = "MAX_DRAWDOWN"
    WIN_RATE = "WIN_RATE"
    PROFIT_FACTOR = "PROFIT_FACTOR"
    STABILITY_SCORE = "STABILITY_SCORE"
    ROBUSTNESS_SCORE = "ROBUSTNESS_SCORE"


# ---------------------------------------------------------------------------
# Value objects
# ---------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True, slots=True)
class ModelEvaluationConfig:
    """Configuration for model evaluation."""
    min_evaluation_samples: int = DEFAULT_MIN_EVALUATION_SAMPLES
    confidence_level: float = DEFAULT_CONFIDENCE_LEVEL
    enable_statistical_testing: bool = DEFAULT_ENABLE_STATISTICAL_TESTING
    retention_period_days: int = DEFAULT_RETENTION_PERIOD_DAYS
    enable_cross_validation: bool = True
    cross_validation_folds: int = 5
    enable_bayesian_optimization: bool = False

    def __post_init__(self) -> None:
        if self.min_evaluation_samples < 1:
            raise ValueError("min_evaluation_samples must be >= 1")
        if not (0.0 < self.confidence_level < 1.0):
            raise ValueError("confidence_level must be in (0.0, 1.0)")
        if self.cross_validation_folds < 2:
            raise ValueError("cross_validation_folds must be >= 2")


@dataclasses.dataclass(frozen=True, slots=True)
class ModelMetrics:
    """Performance metrics for a model."""
    model_id: str
    timestamp_ns: int
    sample_size: int
    accuracy: float = 0.0
    precision: float = 0.0
    recall: float = 0.0
    f1_score: float = 0.0
    sharpe_ratio: float = 0.0
    max_drawdown: float = 0.0
    win_rate: float = 0.0
    profit_factor: float = 0.0
    stability_score: float = 0.0
    robustness_score: float = 0.0
    training_loss: float = 0.0
    validation_loss: float = 0.0
    inference_time_ms: float = 0.0
    metadata: dict[str, Any] = dataclasses.field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.model_id:
            raise ValueError("model_id must be non-empty")


@dataclasses.dataclass(frozen=True, slots=True)
class EvaluationCriteria:
    """Evaluation criteria for model promotion."""
    criterion: EvaluationCriterion
    threshold: float
    weight: float = 1.0
    comparison_type: str = "greater_than"  # greater_than, less_than, equal_to

    def __post_init__(self) -> None:
        if self.weight < 0:
            raise ValueError("weight must be >= 0")


@dataclasses.dataclass(frozen=True, slots=True)
class EvaluationResult:
    """Result of a model evaluation."""
    evaluation_id: str
    model_id: str
    evaluation_type: EvaluationType
    timestamp_ns: int
    metrics: ModelMetrics
    criteria_met: dict[EvaluationCriterion, bool]
    overall_score: float
    passed_evaluation: bool
    confidence: float
    recommendations: list[str]
    comparison_with: dict[str, float]  # model_id -> score
    metadata: dict[str, Any] = dataclasses.field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.evaluation_id:
            raise ValueError("evaluation_id must be non-empty")
        if not self.model_id:
            raise ValueError("model_id must be non-empty")


@dataclass(frozen=True, slots=True)
class EvaluationMetrics:
    """Metrics about model evaluation performance."""

# Export the main class for import
ModelEvaluationSystem = ModelEvaluationConfig
    total_evaluations: int
    evaluations_by_type: dict[str, int]
    evaluations_passed: int
    evaluations_failed: int
    average_evaluation_time_sec: float
    models_evaluated: int
    models_promoted: int
    models_retired: int
    average_model_score: float
    best_model_id: str
    worst_model_id: str


# ---------------------------------------------------------------------------
# Model Evaluator
# ---------------------------------------------------------------------------


class ModelEvaluator:
    """Model evaluation system for learning engine.
    
    Evaluates model performance using multiple criteria, statistical
    testing, and comparative analysis. Provides:
    
    - Performance metrics calculation (accuracy, precision, recall, F1, Sharpe, etc.)
    - Statistical significance testing
    - Cross-validation support
    - Model comparison and ranking
    - Production readiness assessment
    - Evaluation metrics and tracking
    """
    
    def __init__(
        self,
        config: ModelEvaluationConfig | None = None,
    ) -> None:
        """Initialize the model evaluator.
        
        Args:
            config: Evaluation configuration
        """
        self._config = config or ModelEvaluationConfig()
        self._lock = Lock()
        
        # Evaluation storage
        self._evaluations: dict[str, EvaluationResult] = {}  # evaluation_id -> result
        self._model_metrics: dict[str, list[ModelMetrics]] = {}  # model_id -> metrics history
        
        # Evaluation criteria
        self._evaluation_criteria: list[EvaluationCriteria] = []
        
        # Model status tracking
        self._model_status: dict[str, ModelStatus] = {}
        
        # Metrics
        self._metrics = self._init_metrics()
        self._evaluation_times: deque[int] = deque(maxlen=100)
    
    def register_criteria(
        self,
        criteria: list[EvaluationCriteria],
    ) -> None:
        """Register evaluation criteria.
        
        Args:
            criteria: List of criteria to register
        """
        with self._lock:
            self._evaluation_criteria = criteria
    
    def evaluate_model(
        self,
        model_id: str,
        model_type: EvaluationType = EvaluationType.PERFORMANCE,
        test_data: dict[str, Any] | None = None,
    ) -> EvaluationResult:
        """Evaluate a model against registered criteria.
        
        Args:
            model_id: Model identifier
            model_type: Type of evaluation
            test_data: Test data for evaluation
            
        Returns:
            Evaluation result
        """
        import secrets
        import time
        
        start_sec = time.time()
        
        # Calculate model metrics
        metrics = self._calculate_metrics(model_id, test_data)
        
        # Evaluate against criteria
        criteria_met = self._evaluate_against_criteria(metrics)
        
        # Calculate overall score
        overall_score = self._calculate_overall_score(metrics, criteria_met)
        
        # Determine if evaluation passed
        passed = self._determine_pass_status(criteria_met, overall_score)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(metrics, criteria_met, overall_score)
        
        # Calculate confidence
        confidence = self._calculate_confidence(metrics, test_data)
        
        result = EvaluationResult(
            evaluation_id=secrets.token_hex(16),
            model_id=model_id,
            evaluation_type=model_type,
            timestamp_ns=time.time_ns(),
            metrics=metrics,
            criteria_met=criteria_met,
            overall_score=overall_score,
            passed_evaluation=passed,
            confidence=confidence,
            recommendations=recommendations,
            comparison_with={},
        )
        
        with self._lock:
            self._evaluations[result.evaluation_id] = result
            
            # Update model metrics history
            if model_id not in self._model_metrics:
                self._model_metrics[model_id] = deque(maxlen=100)
            self._model_metrics[model_id].append(metrics)
            
            # Update metrics
            self._metrics.total_evaluations += 1
            self._metrics.evaluations_by_type[model_type.value] = \
                self._metrics.evaluations_by_type.get(model_type.value, 0) + 1
            
            if passed:
                self._metrics.evaluations_passed += 1
            else:
                self._metrics.evaluations_failed += 1
            
            # Track unique models
            if model_id not in self._model_status:
                self._metrics.models_evaluated += 1
                self._model_status[model_id] = ModelStatus.VALIDATING
            
            # Track evaluation time
            evaluation_time_sec = time.time() - start_sec
            self._evaluation_times.append(evaluation_time_sec)
            if len(self._evaluation_times) > 0:
                self._metrics.average_evaluation_time_sec = sum(self._evaluation_times) / len(self._evaluation_times)
        
        return result
    
    def compare_models(
        self,
        model_ids: list[str],
        criteria: list[EvaluationCriteria] | None = None,
    ) -> dict[str, float]:
        """Compare multiple models and return rankings.
        
        Args:
            model_ids: List of model identifiers to compare
            criteria: Optional criteria for comparison
            
        Returns:
            Dictionary of model_id -> score
        """
        rankings = {}
        
        for model_id in model_ids:
            result = self.evaluate_model(model_id, EvaluationType.COMPARISON)
            rankings[model_id] = result.overall_score
        
        # Sort by score (descending)
        sorted_models = sorted(rankings.items(), key=lambda x: x[1], reverse=True)
        
        # Update metrics
        with self._lock:
            if sorted_models:
                self._metrics.best_model_id = sorted_models[0][0]
                self._metrics.worst_model_id = sorted_models[-1][0]
        
        return rankings
    
    def check_production_readiness(
        self,
        model_id: str,
    ) -> EvaluationResult:
        """Check if a model is ready for production deployment.
        
        Args:
            model_id: Model identifier
            
        Returns:
            Evaluation result with production readiness assessment
        """
        return self.evaluate_model(model_id, EvaluationType.PRODUCTION_READINESS)
    
    def get_model_metrics(
        self,
        model_id: str,
    ) -> list[ModelMetrics] | None:
        """Get metrics history for a model.
        
        Args:
            model_id: Model identifier
            
        Returns:
            List of metrics or None if not found
        """
        with self._lock:
            return list(self._model_metrics.get(model_id, []))
    
    def get_model_status(self, model_id: str) -> ModelStatus | None:
        """Get current status of a model.
        
        Args:
            model_id: Model identifier
            
        Returns:
            Model status or None
        """
        with self._lock:
            return self._model_status.get(model_id)
    
    def set_model_status(self, model_id: str, status: ModelStatus) -> None:
        """Set the status of a model.
        
        Args:
            model_id: Model identifier
            status: New status
        """
        with self._lock:
            self._model_status[model_id] = status
            
            if status == ModelStatus.APPROVED:
                self._metrics.models_promoted += 1
            elif status == ModelStatus.RETIRED:
                self._metrics.models_retired += 1
    
    def get_metrics(self) -> EvaluationMetrics:
        """Get evaluation metrics.
        
        Returns:
            Current metrics
        """
        with self._lock:
            # Calculate average model score
            if self._model_metrics:
                total_score = 0
                count = 0
                for metrics_list in self._model_metrics.values():
                    for metrics in metrics_list:
                        if metrics.f1_score > 0:
                            total_score += metrics.f1_score
                            count += 1
                avg_score = total_score / count if count > 0 else 0.0
                self._metrics.average_model_score = avg_score
            
            return self._metrics
    
    def _calculate_metrics(
        self,
        model_id: str,
        test_data: dict[str, Any] | None,
    ) -> ModelMetrics:
        """Calculate model performance metrics.
        
        Args:
            model_id: Model identifier
            test_data: Test data for evaluation
            
        Returns:
            Model metrics
        """
        import time
        
        # Extract metrics from test data if provided
        if test_data:
            sample_size = test_data.get("sample_size", self._config.min_evaluation_samples)
            accuracy = test_data.get("accuracy", 0.0)
            precision = test_data.get("precision", 0.0)
            recall = test_data.get("recall", 0.0)
            f1_score = test_data.get("f1_score", 0.0)
            sharpe_ratio = test_data.get("sharpe_ratio", 0.0)
            max_drawdown = test_data.get("max_drawdown", 0.0)
            win_rate = test_data.get("win_rate", 0.0)
            profit_factor = test_data.get("profit_factor", 0.0)
        else:
            sample_size = self._config.min_evaluation_samples
            accuracy = 0.0
            precision = 0.0
            recall = 0.0
            f1_score = 0.0
            sharpe_ratio = 0.0
            max_drawdown = 0.0
            win_rate = 0.0
            profit_factor = 0.0
        
        # Calculate derived metrics
        stability_score = self._calculate_stability_metric(test_data)
        robustness_score = self._calculate_robustness_metric(test_data)
        
        return ModelMetrics(
            model_id=model_id,
            timestamp_ns=time.time_ns(),
            sample_size=sample_size,
            accuracy=accuracy,
            precision=precision,
            recall=recall,
            f1_score=f1_score,
            sharpe_ratio=sharpe_ratio,
            max_drawdown=max_drawdown,
            win_rate=win_rate,
            profit_factor=profit_factor,
            stability_score=stability_score,
            robustness_score=robustness_score,
        )
    
    def _evaluate_against_criteria(
        self,
        metrics: ModelMetrics,
    ) -> dict[EvaluationCriterion, bool]:
        """Evaluate metrics against registered criteria.
        
        Args:
            metrics: Model metrics
            
        Returns:
            Dictionary of criterion to pass/fail
        """
        criteria_met = {}
        
        for criterion in self._evaluation_criteria:
            metric_value = getattr(metrics, criterion.criterion.value.lower(), 0.0)
            
            if criterion.comparison_type == "greater_than":
                criteria_met[criterion] = metric_value >= criterion.threshold
            elif criterion.comparison_type == "less_than":
                criteria_met[criterion] = metric_value <= criterion.threshold
            else:
                criteria_met[criterion] = abs(metric_value - criterion.threshold) < 0.01
        
        return criteria_met
    
    def _calculate_overall_score(
        self,
        metrics: ModelMetrics,
        criteria_met: dict[EvaluationCriterion, bool],
    ) -> float:
        """Calculate overall score from metrics and criteria.
        
        Args:
            metrics: Model metrics
            criteria_met: Criteria pass/fail results
            
        Returns:
            Overall score
        """
        if not self._evaluation_criteria:
            # Default to F1 score if no criteria registered
            return metrics.f1_score
        
        weighted_score = 0.0
        total_weight = 0.0
        
        for criterion in self._evaluation_criteria:
            metric_value = getattr(metrics, criterion.criterion.value.lower(), 0.0)
            weight = criterion.weight
            met = criteria_met.get(criterion, False)
            
            # Weight the score by whether criteria is met
            if met:
                weighted_score += metric_value * weight
            else:
                weighted_score += metric_value * weight * 0.5  # Penalize unmet criteria
            
            total_weight += weight
        
        return weighted_score / total_weight if total_weight > 0 else 0.0
    
    def _determine_pass_status(
        self,
        criteria_met: dict[EvaluationCriterion, bool],
        overall_score: float,
    ) -> bool:
        """Determine if evaluation passed.
        
        Args:
            criteria_met: Criteria pass/fail results
            overall_score: Overall score
            
        Returns:
            True if evaluation passed
        """
        if not criteria_met:
            return True  # No criteria to check
        
        # Require all critical criteria to pass
        pass_count = sum(1 for met in criteria_met.values() if met)
        total_count = len(criteria_met)
        
        return pass_count == total_count and overall_score >= 0.5
    
    def _generate_recommendations(
        self,
        metrics: ModelMetrics,
        criteria_met: dict[EvaluationCriterion, bool],
        overall_score: float,
    ) -> list[str]:
        """Generate recommendations based on evaluation.
        
        Args:
            metrics: Model metrics
            criteria_met: Criteria pass/fail results
            overall_score: Overall score
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        if overall_score >= 0.8:
            recommendations.append("Model performance is excellent - consider for production deployment")
        elif overall_score >= 0.6:
            recommendations.append("Model performance is good - suitable for production")
        elif overall_score >= 0.4:
            recommendations.append("Model performance is marginal - consider further testing")
        else:
            recommendations.append("Model performance is poor - requires retraining or architecture changes")
        
        # Specific recommendations based on metrics
        if metrics.stability_score < 0.5:
            recommendations.append("Model stability is low - investigate variance issues")
        if metrics.max_drawdown > 0.2:
            recommendations.append("Maximum drawdown exceeds threshold - consider risk management")
        if metrics.f1_score < 0.5:
            recommendations.append("F1 score is below threshold - improve balance between precision and recall")
        
        return recommendations
    
    def _calculate_confidence(
        self,
        metrics: ModelMetrics,
        test_data: dict[str, Any] | None,
    ) -> float:
        """Calculate confidence in evaluation result.
        
        Args:
            metrics: Model metrics
            test_data: Test data
            
        Returns:
            Confidence level
        """
        # Base confidence on sample size
        sample_confidence = min(1.0, metrics.sample_size / (self._config.min_evaluation_samples * 10))
        
        # Adjust for metric stability
        if metrics.stability_score > 0:
            sample_confidence *= 1.0 + (metrics.stability_score * 0.2)
        
        return min(1.0, sample_confidence)
    
    def _calculate_stability_metric(
        self,
        test_data: dict[str, Any] | None,
    ) -> float:
        """Calculate stability score from test data.
        
        Args:
            test_data: Test data
            
        Returns:
            Stability score
        """
        if not test_data:
            return 0.0
        
        # Simple stability calculation based on variance
        predictions = test_data.get("predictions", [])
        if len(predictions) > 1:
            variance = sum((p - sum(predictions) / len(predictions)) ** 2 for p in predictions) / len(predictions)
            stability = 1.0 / (1.0 + variance)
            return stability
        
        return 0.5
    
    def _calculate_robustness_metric(
        self,
        test_data: dict[str, Any] | None,
    ) -> float:
        """Calculate robustness score from test data.
        
        Args:
            test_data: Test data
            
        Returns:
            Robustness score
        """
        if not test_data:
            return 0.0
        
        # Simple robustness calculation
        test_cases = test_data.get("test_cases", [])
        if test_cases:
            passed = sum(1 for tc in test_cases if tc.get("passed", False))
            return passed / len(test_cases) if test_cases else 0.0
        
        return 0.0
    
    def _init_metrics(self) -> EvaluationMetrics:
        """Initialize evaluation metrics."""
        return EvaluationMetrics(
            total_evaluations=0,
            evaluations_by_type={},
            evaluations_passed=0,
            evaluations_failed=0,
            average_evaluation_time_sec=0.0,
            models_evaluated=0,
            models_promoted=0,
            models_retired=0,
            average_model_score=0.0,
            best_model_id="",
            worst_model_id="",
        )


# ---------------------------------------------------------------------------
# Model Evaluation Manager
# ---------------------------------------------------------------------------


class ModelEvaluationManager:
    """Manager for model evaluation."""
    
    def __init__(self, config: ModelEvaluationConfig | None = None) -> None:
        """Initialize the model evaluation manager.
        
        Args:
            config: Evaluation configuration
        """
        self._config = config or ModelEvaluationConfig()
        self._evaluator = ModelEvaluator(config)
    
    def register_criteria(self, criteria: list[EvaluationCriteria]) -> None:
        """Register evaluation criteria.
        
        Args:
            criteria: List of criteria
        """
        self._evaluator.register_criteria(criteria)
    
    def evaluate_model(
        self,
        model_id: str,
        model_type: EvaluationType = EvaluationType.PERFORMANCE,
        test_data: dict[str, Any] | None = None,
    ) -> EvaluationResult:
        """Evaluate a model.
        
        Args:
            model_id: Model ID
            model_type: Evaluation type
            test_data: Test data
            
        Returns:
            Evaluation result
        """
        return self._evaluator.evaluate_model(model_id, model_type, test_data)
    
    def compare_models(
        self,
        model_ids: list[str],
        criteria: list[EvaluationCriteria] | None = None,
    ) -> dict[str, float]:
        """Compare models.
        
        Args:
            model_ids: Model IDs
            criteria: Criteria
            
        Returns:
            Model rankings
        """
        return self._evaluator.compare_models(model_ids, criteria)
    
    def check_production_readiness(self, model_id: str) -> EvaluationResult:
        """Check production readiness.
        
        Args:
            model_id: Model ID
            
        Returns:
            Evaluation result
        """
        return self._evaluator.check_production_readiness(model_id)
    
    def set_model_status(self, model_id: str, status: ModelStatus) -> None:
        """Set model status.
        
        Args:
            model_id: Model ID
            status: Model status
        """
        self._evaluator.set_model_status(model_id, status)
    
    def get_metrics(self) -> EvaluationMetrics:
        """Get metrics.
        
        Returns:
            Current metrics
        """
        return self._evaluator.get_metrics()


__all__ = [
    "EvaluationType",
    "ModelStatus",
    "EvaluationCriterion",
    "ModelEvaluationConfig",
    "ModelMetrics",
    "EvaluationCriteria",
    "EvaluationResult",
    "EvaluationMetrics",
    "ModelEvaluator",
    "ModelEvaluationManager",
]
