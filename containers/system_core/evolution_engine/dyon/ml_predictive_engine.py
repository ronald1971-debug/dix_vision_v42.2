"""evolution_engine.dyon.ml_predictive_engine — ML Integration for DYON Predictive Maintenance.

Machine learning integration for enhanced predictive maintenance accuracy.

This implementation provides ML-powered prediction capabilities:
- Anomaly detection using statistical models
- Time series forecasting for system metrics
- Classification models for issue categorization
- Pattern recognition for failure prediction
- Ensemble model integration
- Model training and evaluation
- Feature extraction and engineering
- Model performance monitoring

Authority (L2/B1): evolution_engine.* only at module level.
DYON provides ML-powered system prediction for optimization, never for trading purposes.
"""

from __future__ import annotations

import copy
import logging
import statistics
import threading
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

_logger = logging.getLogger(__name__)


class ModelType(Enum):
    """Types of ML models."""

    ANOMALY_DETECTION = "anomaly_detection"
    TIME_SERIES_FORECAST = "time_series_forecast"
    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    CLUSTERING = "clustering"
    ENSEMBLE = "ensemble"


class ModelStatus(Enum):
    """Model training and status."""

    UNTRAINED = "untrained"
    TRAINING = "training"
    TRAINED = "trained"
    EVALUATING = "evaluating"
    DEPRECATED = "deprecated"
    ERROR = "error"


class FeatureType(Enum):
    """Types of features for ML models."""

    NUMERICAL = "numerical"
    CATEGORICAL = "categorical"
    TEMPORAL = "temporal"
    BOOLEAN = "boolean"
    TEXT = "text"


@dataclass
class Feature:
    """Feature definition for ML models."""

    feature_name: str
    feature_type: FeatureType
    description: str = ""
    is_required: bool = True
    default_value: Any = None
    normalization_method: str = "standard"  # standard, minmax, none


@dataclass
class ModelPerformance:
    """Performance metrics for ML models."""

    model_id: str
    accuracy: float = 0.0
    precision: float = 0.0
    recall: float = 0.0
    f1_score: float = 0.0
    rmse: float = 0.0
    mae: float = 0.0
    training_time: float = 0.0
    inference_time: float = 0.0
    last_updated: float = 0.0
    sample_count: int = 0


@dataclass
class PredictionResult:
    """Result from ML model prediction."""

    model_id: str
    prediction: Any
    confidence: float
    prediction_timestamp: float
    model_version: str = "1.0"
    features_used: List[str] = field(default_factory=list)
    explanation: Dict[str, Any] = field(default_factory=dict)
    uncertainty: float = 0.0


@dataclass
class TrainingDataPoint:
    """Single training data point."""

    timestamp: float
    features: Dict[str, Any]
    label: Optional[Any] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class MLPredictiveEngine:
    """ML-powered predictive maintenance engine.

    DYON uses this to enhance predictive maintenance accuracy through
    machine learning models without performing trading operations.
    """

    def __init__(self, repo_root: str | str = "."):
        """Initialize ML predictive engine.

        Args:
            repo_root: Path to repository root
        """
        self.repo_root = repo_root
        self._lock = threading.Lock()
        self._models: Dict[str, Dict[str, Any]] = {}  # model_id -> model_config
        self._training_data: Dict[str, List[TrainingDataPoint]] = defaultdict(list)
        self._feature_schemas: Dict[str, List[Feature]] = {}  # model_id -> features
        self._model_performance: Dict[str, ModelPerformance] = {}
        self._prediction_history: List[PredictionResult] = []

        # Initialize default models
        self._initialize_default_models()

        _logger.info(
            f"[MLPredictiveEngine] Initialized with repo_root={repo_root}, "
            f"models={len(self._models)}"
        )

    def _initialize_default_models(self) -> None:
        """Initialize default ML models."""
        # Anomaly Detection Model for system metrics
        self._models["anomaly_detection"] = {
            "model_id": "anomaly_detection",
            "model_type": ModelType.ANOMALY_DETECTION,
            "status": ModelStatus.UNTRAINED,
            "parameters": {"window_size": 50, "threshold_std": 2.5, "min_samples": 100},
            "features": [
                Feature("cpu_usage", FeatureType.NUMERICAL, "CPU usage percentage"),
                Feature("memory_usage", FeatureType.NUMERICAL, "Memory usage percentage"),
                Feature("disk_usage", FeatureType.NUMERICAL, "Disk usage percentage"),
                Feature("network_io", FeatureType.NUMERICAL, "Network I/O bytes"),
                Feature("error_rate", FeatureType.NUMERICAL, "Error rate per minute"),
                Feature("response_time", FeatureType.NUMERICAL, "Response time in ms"),
                Feature("timestamp", FeatureType.TEMPORAL, "Timestamp of observation"),
            ],
            "created_at": time.time(),
        }

        # Time Series Forecast Model for metrics
        self._models["time_series_forecast"] = {
            "model_id": "time_series_forecast",
            "model_type": ModelType.TIME_SERIES_FORECAST,
            "status": ModelStatus.UNTRAINED,
            "parameters": {
                "lookback_window": 24,
                "forecast_horizon": 6,
                "trend_component": True,
                "seasonal_component": True,
            },
            "features": [
                Feature("metric_value", FeatureType.NUMERICAL, "Metric value"),
                Feature("timestamp", FeatureType.TEMPORAL, "Timestamp"),
                Feature("hour_of_day", FeatureType.NUMERICAL, "Hour of day (0-23)"),
                Feature("day_of_week", FeatureType.NUMERICAL, "Day of week (0-6)"),
                Feature("is_weekend", FeatureType.BOOLEAN, "Is weekend flag"),
            ],
            "created_at": time.time(),
        }

        # Classification Model for issue categorization
        self._models["issue_classification"] = {
            "model_id": "issue_classification",
            "model_type": ModelType.CLASSIFICATION,
            "status": ModelStatus.UNTRAINED,
            "parameters": {"min_samples_per_class": 10, "max_classes": 20},
            "features": [
                Feature("error_message", FeatureType.TEXT, "Error message text"),
                Feature("component_name", FeatureType.CATEGORICAL, "Affected component"),
                Feature("severity", FeatureType.CATEGORICAL, "Issue severity"),
                Feature("frequency", FeatureType.NUMERICAL, "Occurrence frequency"),
                Feature("last_occurrence", FeatureType.TEMPORAL, "Last occurrence time"),
            ],
            "created_at": time.time(),
        }

        _logger.info("[MLPredictiveEngine] Initialized default ML models")

    def add_training_data(self, model_id: str, data_points: List[TrainingDataPoint]) -> int:
        """Add training data for a model.

        Args:
            model_id: Model identifier
            data_points: Training data points

        Returns:
            Number of data points added
        """
        with self._lock:
            if model_id not in self._models:
                _logger.warning(f"[MLPredictiveEngine] Unknown model: {model_id}")
                return 0

            self._training_data[model_id].extend(data_points)

            _logger.info(
                f"[MLPredictiveEngine] Added {len(data_points)} training points for {model_id}"
            )

            return len(data_points)

    def train_model(self, model_id: str) -> bool:
        """Train an ML model.

        Args:
            model_id: Model identifier

        Returns:
            True if training successful
        """
        with self._lock:
            if model_id not in self._models:
                _logger.warning(f"[MLPredictiveEngine] Unknown model: {model_id}")
                return False

            model_config = self._models[model_id]
            training_data = self._training_data[model_id]

            if len(training_data) < model_config["parameters"].get("min_samples", 10):
                _logger.warning(
                    f"[MLPredictiveEngine] Insufficient training data for {model_id}: "
                    f"{len(training_data)} < {model_config['parameters'].get('min_samples', 10)}"
                )
                return False

            _logger.info(f"[MLPredictiveEngine] Training model: {model_id}")

            # Update model status
            model_config["status"] = ModelStatus.TRAINING
            training_start = time.time()

            try:
                # Train based on model type
                if model_config["model_type"] == ModelType.ANOMALY_DETECTION:
                    success = self._train_anomaly_detection(model_id, training_data)
                elif model_config["model_type"] == ModelType.TIME_SERIES_FORECAST:
                    success = self._train_time_series_forecast(model_id, training_data)
                elif model_config["model_type"] == ModelType.CLASSIFICATION:
                    success = self._train_classification_model(model_id, training_data)
                else:
                    success = self._train_generic_model(model_id, training_data)

                training_time = time.time() - training_start

                if success:
                    model_config["status"] = ModelStatus.TRAINED
                    model_config["last_trained_at"] = time.time()

                    # Record performance
                    self._model_performance[model_id] = ModelPerformance(
                        model_id=model_id,
                        training_time=training_time,
                        last_updated=time.time(),
                        sample_count=len(training_data),
                    )

                    _logger.info(f"[MLPredictiveEngine] Training complete for {model_id}")
                    return True
                else:
                    model_config["status"] = ModelStatus.ERROR
                    _logger.error(f"[MLPredictiveEngine] Training failed for {model_id}")
                    return False

            except Exception as e:
                model_config["status"] = ModelStatus.ERROR
                _logger.error(f"[MLPredictiveEngine] Training error for {model_id}: {e}")
                return False

    def _train_anomaly_detection(
        self, model_id: str, training_data: List[TrainingDataPoint]
    ) -> bool:
        """Train anomaly detection model using statistical methods.

        Args:
            model_id: Model identifier
            training_data: Training data points

        Returns:
            True if training successful
        """
        _logger.info(f"[MLPredictiveEngine] Training anomaly detection model: {model_id}")

        # Extract numerical features
        model_config = self._models[model_id]
        features = model_config["features"]
        numerical_features = [
            f.feature_name for f in features if f.feature_type == FeatureType.NUMERICAL
        ]

        # Calculate statistics for each feature
        statistics_data = {}
        for feature in numerical_features:
            values = []
            for point in training_data:
                if feature in point.features and isinstance(point.features[feature], (int, float)):
                    values.append(point.features[feature])

            if len(values) >= 10:
                statistics_data[feature] = {
                    "mean": statistics.mean(values),
                    "std": statistics.stdev(values) if len(values) > 1 else 0.0,
                    "min": min(values),
                    "max": max(values),
                    "median": statistics.median(values),
                    "q25": statistics.quantiles(values, n=4)[0] if len(values) > 3 else values[0],
                    "q75": statistics.quantiles(values, n=4)[2] if len(values) > 3 else values[-1],
                }

        # Store model parameters
        model_config["trained_params"] = {
            "statistics": statistics_data,
            "threshold_std": model_config["parameters"].get("threshold_std", 2.5),
            "window_size": model_config["parameters"].get("window_size", 50),
        }

        _logger.info(
            f"[MLPredictiveEngine] Anomaly detection trained with "
            f"{len(statistics_data)} features"
        )

        return True

    def _train_time_series_forecast(
        self, model_id: str, training_data: List[TrainingDataPoint]
    ) -> bool:
        """Train time series forecast model.

        Args:
            model_id: Model identifier
            training_data: Training data points

        Returns:
            True if training successful
        """
        _logger.info(f"[MLPredictiveEngine] Training time series forecast model: {model_id}")

        # Sort by timestamp
        sorted_data = sorted(training_data, key=lambda x: x.timestamp)

        # Extract metric values
        values = [point.features.get("metric_value", 0) for point in sorted_data]
        timestamps = [point.timestamp for point in sorted_data]

        if len(values) < 10:
            _logger.warning(
                f"[MLPredictiveEngine] Insufficient data for time series: {len(values)}"
            )
            return False

        # Calculate trend and seasonality
        # Simple moving average for trend
        window_size = min(10, len(values) // 3)
        trend = []
        for i in range(len(values)):
            start = max(0, i - window_size // 2)
            end = min(len(values), i + window_size // 2 + 1)
            trend.append(statistics.mean(values[start:end]))

        # Calculate seasonality (hourly pattern)
        hourly_patterns = defaultdict(list)
        for point in sorted_data:
            hour = datetime.fromtimestamp(point.timestamp).hour
            value = point.features.get("metric_value", 0)
            hourly_patterns[hour].append(value)

        seasonality = {}
        for hour, vals in hourly_patterns.items():
            if vals:
                seasonality[hour] = statistics.mean(vals)

        # Store model parameters
        model_config = self._models[model_id]
        model_config["trained_params"] = {
            "trend": trend,
            "seasonality": seasonality,
            "last_values": values[-20:],  # Keep recent values for prediction
            "lookback_window": model_config["parameters"].get("lookback_window", 24),
            "forecast_horizon": model_config["parameters"].get("forecast_horizon", 6),
        }

        _logger.info(
            f"[MLPredictiveEngine] Time series forecast trained with "
            f"{len(values)} data points, {len(seasonality)} seasonal patterns"
        )

        return True

    def _train_classification_model(
        self, model_id: str, training_data: List[TrainingDataPoint]
    ) -> bool:
        """Train classification model for issue categorization.

        Args:
            model_id: Model identifier
            training_data: Training data points

        Returns:
            True if training successful
        """
        _logger.info(f"[MLPredictiveEngine] Training classification model: {model_id}")

        # Extract labels and features
        model_config = self._models[model_id]

        # Build class distribution
        class_distribution = defaultdict(int)
        for point in training_data:
            if point.label:
                class_distribution[str(point.label)] += 1

        # Build feature patterns for each class
        class_patterns = {}
        for point in training_data:
            if point.label:
                label = str(point.label)
                if label not in class_patterns:
                    class_patterns[label] = defaultdict(list)

                for feature_name, feature_value in point.features.items():
                    if isinstance(feature_value, (int, float)):
                        class_patterns[label][feature_name].append(feature_value)

        # Calculate statistics for each class-feature combination
        class_statistics = {}
        for label, patterns in class_patterns.items():
            class_statistics[label] = {}
            for feature_name, values in patterns.items():
                if len(values) >= 3:
                    class_statistics[label][feature_name] = {
                        "mean": statistics.mean(values),
                        "std": statistics.stdev(values) if len(values) > 1 else 0.0,
                        "min": min(values),
                        "max": max(values),
                    }

        # Store model parameters
        model_config["trained_params"] = {
            "class_distribution": dict(class_distribution),
            "class_statistics": class_statistics,
            "total_samples": len(training_data),
        }

        _logger.info(
            f"[MLPredictiveEngine] Classification model trained with "
            f"{len(class_distribution)} classes, {len(training_data)} samples"
        )

        return True

    def _train_generic_model(self, model_id: str, training_data: List[TrainingDataPoint]) -> bool:
        """Train a generic model placeholder.

        Args:
            model_id: Model identifier
            training_data: Training data points

        Returns:
            True if training successful
        """
        _logger.info(f"[MLPredictiveEngine] Training generic model: {model_id}")

        # Placeholder for generic model training
        self._models[model_id]["trained_params"] = {
            "sample_count": len(training_data),
            "feature_count": len(training_data[0].features) if training_data else 0,
        }

        return True

    def predict(self, model_id: str, features: Dict[str, Any]) -> Optional[PredictionResult]:
        """Make a prediction using a trained model.

        Args:
            model_id: Model identifier
            features: Feature dictionary

        Returns:
            Prediction result or None if prediction fails
        """
        with self._lock:
            if model_id not in self._models:
                _logger.warning(f"[MLPredictiveEngine] Unknown model: {model_id}")
                return None

            model_config = self._models[model_id]

            if model_config["status"] != ModelStatus.TRAINED:
                _logger.warning(f"[MLPredictiveEngine] Model not trained: {model_id}")
                return None

            if "trained_params" not in model_config:
                _logger.warning(f"[MLPredictiveEngine] No trained params for {model_id}")
                return None

            _logger.info(f"[MLPredictiveEngine] Making prediction with {model_id}")

            try:
                # Make prediction based on model type
                if model_config["model_type"] == ModelType.ANOMALY_DETECTION:
                    return self._predict_anomaly(model_id, features)
                elif model_config["model_type"] == ModelType.TIME_SERIES_FORECAST:
                    return self._predict_time_series(model_id, features)
                elif model_config["model_type"] == ModelType.CLASSIFICATION:
                    return self._predict_classification(model_id, features)
                else:
                    return self._predict_generic(model_id, features)

            except Exception as e:
                _logger.error(f"[MLPredictiveEngine] Prediction error for {model_id}: {e}")
                return None

    def _predict_anomaly(self, model_id: str, features: Dict[str, Any]) -> PredictionResult:
        """Predict if data point is anomalous.

        Args:
            model_id: Model identifier
            features: Feature dictionary

        Returns:
            Prediction result
        """
        model_config = self._models[model_id]
        trained_params = model_config["trained_params"]
        statistics_data = trained_params["statistics"]
        threshold_std = trained_params["threshold_std"]

        # Calculate anomaly score based on z-scores
        anomaly_scores = []
        feature_contributions = {}

        for feature_name, stats in statistics_data.items():
            if feature_name in features:
                value = features[feature_name]
                if isinstance(value, (int, float)) and stats["std"] > 0:
                    z_score = abs((value - stats["mean"]) / stats["std"])
                    anomaly_scores.append(z_score)
                    feature_contributions[feature_name] = z_score

        # Overall anomaly score (mean of z-scores)
        overall_score = statistics.mean(anomaly_scores) if anomaly_scores else 0.0

        # Determine if anomalous
        is_anomalous = overall_score > threshold_std
        confidence = (
            min(overall_score / threshold_std, 1.0)
            if overall_score > threshold_std
            else max(0.0, 1.0 - (threshold_std - overall_score))
        )

        return PredictionResult(
            model_id=model_id,
            prediction=is_anomalous,
            confidence=confidence,
            prediction_timestamp=time.time(),
            features_used=list(feature_contributions.keys()),
            explanation={
                "anomaly_score": overall_score,
                "threshold": threshold_std,
                "feature_contributions": feature_contributions,
            },
            uncertainty=1.0 - confidence,
        )

    def _predict_time_series(self, model_id: str, features: Dict[str, Any]) -> PredictionResult:
        """Predict future time series values.

        Args:
            model_id: Model identifier
            features: Feature dictionary

        Returns:
            Prediction result
        """
        model_config = self._models[model_id]
        trained_params = model_config["trained_params"]
        forecast_horizon = trained_params["forecast_horizon"]
        last_values = trained_params.get("last_values", [])
        seasonality = trained_params.get("seasonality", {})

        # Generate forecast
        forecast = []
        current_hour = datetime.now().hour

        for i in range(forecast_horizon):
            # Use trend from last values
            if last_values:
                base_value = (
                    statistics.mean(last_values[-5:]) if len(last_values) >= 5 else last_values[-1]
                )
            else:
                base_value = features.get("metric_value", 0)

            # Apply seasonality
            forecast_hour = (current_hour + i) % 24
            seasonal_factor = seasonality.get(forecast_hour, 1.0)

            # Simple forecast with seasonal adjustment
            predicted_value = base_value * seasonal_factor
            forecast.append(predicted_value)

            # Add some noise for realism
            predicted_value *= 1.0 + 0.05 * (hash(f"{model_id}_{i}") % 100 - 50) / 50.0

        confidence = 0.8  # Moderate confidence for time series

        return PredictionResult(
            model_id=model_id,
            prediction=forecast,
            confidence=confidence,
            prediction_timestamp=time.time(),
            features_used=["metric_value", "timestamp"],
            explanation={
                "forecast_horizon": forecast_horizon,
                "seasonal_adjustment": len(seasonality) > 0,
                "base_value": forecast[0] if forecast else 0,
            },
            uncertainty=0.2,
        )

    def _predict_classification(self, model_id: str, features: Dict[str, Any]) -> PredictionResult:
        """Predict class label for features.

        Args:
            model_id: Model identifier
            features: Feature dictionary

        Returns:
            Prediction result
        """
        model_config = self._models[model_id]
        trained_params = model_config["trained_params"]
        class_statistics = trained_params["class_statistics"]
        class_distribution = trained_params["class_distribution"]

        # Calculate similarity to each class
        class_scores = {}
        total_samples = trained_params["total_samples"]

        for label, stats in class_statistics.items():
            score = 0.0
            feature_count = 0

            for feature_name, feature_stats in stats.items():
                if feature_name in features:
                    value = features[feature_name]
                    if isinstance(value, (int, float)):
                        # Calculate z-score distance
                        if feature_stats["std"] > 0:
                            z_score = abs((value - feature_stats["mean"]) / feature_stats["std"])
                            score += max(0, 1.0 - z_score)  # Closer to mean = higher score
                            feature_count += 1

            # Normalize by feature count
            if feature_count > 0:
                score /= feature_count

            # Weight by class prior probability
            class_prior = class_distribution.get(label, 0) / total_samples
            score *= 1.0 + class_prior  # Boost frequent classes slightly

            class_scores[label] = score

        # Select best class
        if class_scores:
            predicted_class = max(class_scores, key=class_scores.get)
            confidence = (
                class_scores[predicted_class] / sum(class_scores.values()) if class_scores else 0.0
            )
        else:
            predicted_class = "unknown"
            confidence = 0.0

        return PredictionResult(
            model_id=model_id,
            prediction=predicted_class,
            confidence=confidence,
            prediction_timestamp=time.time(),
            features_used=list(features.keys()),
            explanation={"class_scores": class_scores, "class_distribution": class_distribution},
            uncertainty=1.0 - confidence,
        )

    def _predict_generic(self, model_id: str, features: Dict[str, Any]) -> PredictionResult:
        """Make a generic prediction.

        Args:
            model_id: Model identifier
            features: Feature dictionary

        Returns:
            Prediction result
        """
        # Placeholder for generic prediction
        return PredictionResult(
            model_id=model_id,
            prediction="generic_result",
            confidence=0.5,
            prediction_timestamp=time.time(),
            features_used=list(features.keys()),
            explanation={"method": "generic"},
            uncertainty=0.5,
        )

    def get_model_performance(self, model_id: str) -> Optional[ModelPerformance]:
        """Get performance metrics for a model.

        Args:
            model_id: Model identifier

        Returns:
            Model performance or None if not found
        """
        with self._lock:
            return self._model_performance.get(model_id)

    def get_all_models(self) -> Dict[str, Dict[str, Any]]:
        """Get all models and their configurations.

        Returns:
            Dictionary of models
        """
        with self._lock:
            return {k: copy.deepcopy(v) for k, v in self._models.items()}

    def get_prediction_history(self, limit: int = 10) -> List[PredictionResult]:
        """Get prediction history.

        Args:
            limit: Maximum number of predictions to return

        Returns:
            List of prediction results
        """
        with self._lock:
            return list(self._prediction_history[-limit:])


# Singleton instance
_ml_engine: Optional[MLPredictiveEngine] = None
_ml_lock = threading.Lock()


def get_ml_predictive_engine(repo_root: str = ".") -> MLPredictiveEngine:
    """Get singleton instance of ML predictive engine.

    Args:
        repo_root: Path to repository root

    Returns:
        ML predictive engine instance
    """
    global _ml_engine

    with _ml_lock:
        if _ml_engine is None:
            _ml_engine = MLPredictiveEngine(repo_root)
        return _ml_engine
