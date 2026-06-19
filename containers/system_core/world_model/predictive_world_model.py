"""Predictive World Model - Advanced Predictive Capabilities.

This module provides advanced predictive capabilities for the world model, including
future state prediction, scenario analysis, probabilistic forecasting, and predictive
confidence intervals.
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
import math

logger = logging.getLogger(__name__)


class PredictionHorizon(str, Enum):
    """Prediction time horizons."""
    IMMEDIATE = "IMMEDIATE"  # Minutes to hours
    SHORT_TERM = "SHORT_TERM"  # Hours to days
    MEDIUM_TERM = "MEDIUM_TERM"  # Days to weeks
    LONG_TERM = "LONG_TERM"  # Weeks to months


class PredictionType(str, Enum):
    """Types of predictions."""
    DETERMINISTIC = "DETERMINISTIC"
    PROBABILISTIC = "PROBABILISTIC"
    SCENARIO_BASED = "SCENARIO_BASED"
    ENSEMBLE = "ENSEMBLE"


@dataclass
class Prediction:
    """Single prediction result."""
    prediction_id: str
    target_variable: str
    predicted_value: float
    confidence: float
    confidence_interval: Tuple[float, float]
    prediction_type: PredictionType
    horizon: PredictionHorizon
    timestamp: float
    prediction_time: float  # Time when prediction was made
    actual_value: Optional[float] = None
    accuracy: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Scenario:
    """Scenario for scenario-based prediction."""
    scenario_id: str
    scenario_name: str
    scenario_type: str  # "bullish", "bearish", "neutral", "extreme"
    conditions: Dict[str, Any]
    probability: float
    predicted_outcomes: Dict[str, float]
    confidence: float
    timestamp: float


@dataclass
class EnsemblePrediction:
    """Ensemble prediction combining multiple models."""
    prediction_id: str
    target_variable: str
    individual_predictions: List[Prediction]
    ensemble_value: float
    ensemble_confidence: float
    ensemble_interval: Tuple[float, float]
    weights: List[float]
    timestamp: float


@dataclass
class MarketForecast:
    """Comprehensive market forecast."""
    forecast_id: str
    symbol: str
    price_forecast: EnsemblePrediction
    volatility_forecast: EnsemblePrediction
    volume_forecast: EnsemblePrediction
    regime_forecast: str
    confidence: float
    time_horizon: PredictionHorizon
    scenarios: List[Scenario]
    risk_factors: List[str]
    opportunities: List[str]
    timestamp: float


class PredictiveWorldModel:
    """Predictive world model with advanced forecasting capabilities."""

    def __init__(self, history_window: int = 1000):
        self._lock = threading.Lock()
        self._history_window = history_window
        self._prediction_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=history_window))
        self._scenarios: Dict[str, Scenario] = {}
        self._prediction_models = {
            "linear_regression": LinearRegressionPredictor(),
            "moving_average": MovingAveragePredictor(),
            "exponential_smoothing": ExponentialSmoothingPredictor(),
            "momentum_model": MomentumPredictor(),
            "mean_reversion": MeanReversionPredictor()
        }
        self._ensemble_builder = EnsembleBuilder()
        self._scenario_generator = ScenarioGenerator()
        self._confidence_calculator = ConfidenceCalculator()
        self._initialized = False

    def start(self) -> bool:
        """Start predictive world model."""
        logger.info("[PREDICTIVE_MODEL] Starting predictive world model...")
        self._initialized = True
        logger.info("[PREDICTIVE_MODEL] Predictive world model started")
        return True

    def stop(self) -> bool:
        """Stop predictive world model."""
        logger.info("[PREDICTIVE_MODEL] Stopping predictive world model...")
        self._initialized = False
        logger.info("[PREDICTIVE_MODEL] Predictive world model stopped")
        return True

    def predict_future_state(self, current_state: Dict[str, float], target_variable: str, 
                           horizon: PredictionHorizon, prediction_type: PredictionType = PredictionType.ENSEMBLE) -> Prediction:
        """Predict future state of a variable."""
        logger.info(f"[PREDICTIVE_MODEL] Predicting future state for {target_variable} with horizon {horizon}")
        
        prediction_id = f"pred_{int(time.time())}_{target_variable}_{hash(str(current_state)) % 10000}"
        
        # Generate individual predictions from different models
        individual_predictions = []
        for model_name, model in self._prediction_models.items():
            try:
                model_prediction = model.predict(current_state, target_variable, horizon)
                if model_prediction:
                    individual_predictions.append(model_prediction)
            except Exception as e:
                logger.warning(f"[PREDICTIVE_MODEL] Model {model_name} prediction failed: {e}")
        
        # Combine predictions based on type
        if prediction_type == PredictionType.ENSEMBLE and len(individual_predictions) > 1:
            ensemble = self._ensemble_builder.build_ensemble(individual_predictions)
            final_prediction = Prediction(
                prediction_id=prediction_id,
                target_variable=target_variable,
                predicted_value=ensemble.ensemble_value,
                confidence=ensemble.ensemble_confidence,
                confidence_interval=ensemble.ensemble_interval,
                prediction_type=prediction_type,
                horizon=horizon,
                timestamp=time.time() + self._horizon_to_seconds(horizon),
                prediction_time=time.time(),
                metadata={"ensemble": True, "individual_count": len(individual_predictions)}
            )
        else:
            # Use best individual prediction or first available
            if individual_predictions:
                best_prediction = max(individual_predictions, key=lambda p: p.confidence)
                final_prediction = best_prediction
                final_prediction.prediction_id = prediction_id
                final_prediction.prediction_type = prediction_type
            else:
                # Fallback prediction
                final_prediction = Prediction(
                    prediction_id=prediction_id,
                    target_variable=target_variable,
                    predicted_value=current_state.get(target_variable, 0.0),
                    confidence=0.5,
                    confidence_interval=(0.0, 0.0),
                    prediction_type=prediction_type,
                    horizon=horizon,
                    timestamp=time.time() + self._horizon_to_seconds(horizon),
                    prediction_time=time.time(),
                    metadata={"fallback": True}
                )
        
        # Store prediction
        with self._lock:
            self._prediction_history[target_variable].append(final_prediction)
        
        return final_prediction

    def generate_scenarios(self, current_state: Dict[str, float], num_scenarios: int = 5) -> List[Scenario]:
        """Generate alternative scenarios for future states."""
        logger.info(f"[PREDICTIVE_MODEL] Generating {num_scenarios} scenarios")
        
        scenarios = self._scenario_generator.generate(current_state, num_scenarios)
        
        # Store scenarios
        with self._lock:
            for scenario in scenarios:
                self._scenarios[scenario.scenario_id] = scenario
        
        return scenarios

    def create_market_forecast(self, symbol: str, current_market_state: Dict[str, float], 
                            horizon: PredictionHorizon) -> MarketForecast:
        """Create comprehensive market forecast."""
        logger.info(f"[PREDICTIVE_MODEL] Creating market forecast for {symbol}")
        
        forecast_id = f"forecast_{int(time.time())}_{symbol}"
        
        # Generate individual forecasts
        price_forecast = self.predict_future_state(current_market_state, "price", horizon, PredictionType.ENSEMBLE)
        volatility_forecast = self.predict_future_state(current_market_state, "volatility", horizon, PredictionType.ENSEMBLE)
        volume_forecast = self.predict_future_state(current_market_state, "volume", horizon, PredictionType.ENSEMBLE)
        
        # Generate scenarios
        scenarios = self.generate_scenarios(current_market_state, 3)
        
        # Determine regime forecast
        regime_forecast = self._predict_regime(current_market_state, scenarios)
        
        # Calculate overall confidence
        overall_confidence = self._confidence_calculator.calculate_overall_confidence(
            price_forecast, volatility_forecast, volume_forecast
        )
        
        # Identify risk factors
        risk_factors = self._identify_risk_factors(current_market_state, scenarios)
        
        # Identify opportunities
        opportunities = self._identify_opportunities(current_market_state, scenarios)
        
        forecast = MarketForecast(
            forecast_id=forecast_id,
            symbol=symbol,
            price_forecast=price_forecast,
            volatility_forecast=volatility_forecast,
            volume_forecast=volume_forecast,
            regime_forecast=regime_forecast,
            confidence=overall_confidence,
            time_horizon=horizon,
            scenarios=scenarios,
            risk_factors=risk_factors,
            opportunities=opportunities,
            timestamp=time.time()
        )
        
        return forecast

    def update_prediction_accuracy(self, prediction_id: str, actual_value: float) -> None:
        """Update prediction accuracy when actual value becomes known."""
        with self._lock:
            # Find the prediction
            for variable, predictions in self._prediction_history.items():
                for prediction in predictions:
                    if prediction.prediction_id == prediction_id:
                        prediction.actual_value = actual_value
                        # Calculate accuracy
                        prediction.accuracy = self._calculate_accuracy(prediction.predicted_value, actual_value)
                        logger.info(f"[PREDICTIVE_MODEL] Updated accuracy for prediction {prediction_id}: {prediction.accuracy:.2f}")
                        return

    def get_prediction_statistics(self) -> Dict[str, Any]:
        """Get prediction statistics."""
        with self._lock:
            total_predictions = sum(len(preds) for preds in self._prediction_history.values())
            
            if total_predictions > 0:
                accuracies = []
                for predictions in self._prediction_history.values():
                    for prediction in predictions:
                        if prediction.accuracy is not None:
                            accuracies.append(prediction.accuracy)
                
                avg_accuracy = np.mean(accuracies) if accuracies else 0.0
                avg_confidence = np.mean([p.confidence for preds in self._prediction_history.values() for p in preds])
            else:
                avg_accuracy = 0.0
                avg_confidence = 0.0
            
            return {
                "total_predictions": total_predictions,
                "variables_tracked": len(self._prediction_history),
                "average_accuracy": avg_accuracy,
                "average_confidence": avg_confidence,
                "total_scenarios": len(self._scenarios),
                "available_models": list(self._prediction_models.keys())
            }

    def _horizon_to_seconds(self, horizon: PredictionHorizon) -> float:
        """Convert prediction horizon to seconds."""
        horizon_seconds = {
            PredictionHorizon.IMMEDIATE: 3600.0,      # 1 hour
            PredictionHorizon.SHORT_TERM: 86400.0,    # 1 day
            PredictionHorizon.MEDIUM_TERM: 604800.0,   # 1 week
            PredictionHorizon.LONG_TERM: 2592000.0     # 1 month
        }
        return horizon_seconds.get(horizon, 3600.0)

    def _predict_regime(self, current_state: Dict[str, float], scenarios: List[Scenario]) -> str:
        """Predict market regime based on scenarios."""
        # Find most probable scenario
        if scenarios:
            most_probable = max(scenarios, key=lambda s: s.probability)
            return most_probable.scenario_type
        
        # Fallback regime prediction based on current state
        trend = current_state.get("trend", 0.0)
        volatility = current_state.get("volatility", 0.2)
        
        if trend > 0.02 and volatility < 0.3:
            return "bullish"
        elif trend < -0.02 and volatility < 0.3:
            return "bearish"
        elif volatility > 0.5:
            return "volatile"
        else:
            return "neutral"

    def _identify_risk_factors(self, current_state: Dict[str, float], scenarios: List[Scenario]) -> List[str]:
        """Identify risk factors from current state and scenarios."""
        risk_factors = []
        
        volatility = current_state.get("volatility", 0.2)
        if volatility > 0.5:
            risk_factors.append("high_volatility")
        
        trend = current_state.get("trend", 0.0)
        if abs(trend) > 0.05:
            risk_factors.append("strong_trend_exhaustion_risk")
        
        # Check scenario-based risks
        bearish_scenarios = [s for s in scenarios if "bear" in s.scenario_name.lower()]
        if len(bearish_scenarios) > len(scenarios) / 2:
            risk_factors.append("bearish_scenario_dominance")
        
        return risk_factors

    def _identify_opportunities(self, current_state: Dict[str, float], scenarios: List[Scenario]) -> List[str]:
        """Identify trading opportunities from current state and scenarios."""
        opportunities = []
        
        trend = current_state.get("trend", 0.0)
        volatility = current_state.get("volatility", 0.2)
        
        if trend > 0.01 and volatility < 0.4:
            opportunities.append("bullish_momentum")
        elif trend < -0.01 and volatility < 0.4:
            opportunities.append("bearish_momentum")
        elif volatility > 0.6:
            opportunities.append("volatility_trading")
        elif abs(trend) < 0.005:
            opportunities.append("range_trading")
        
        # Scenario-based opportunities
        bullish_scenarios = [s for s in scenarios if "bull" in s.scenario_name.lower()]
        if len(bullish_scenarios) > len(scenarios) / 2:
            opportunities.append("bullish_scenario_opportunity")
        
        return opportunities

    def _calculate_accuracy(self, predicted: float, actual: float) -> float:
        """Calculate prediction accuracy."""
        if actual == 0:
            return 1.0 if predicted == 0 else 0.0
        
        # Relative error
        relative_error = abs(predicted - actual) / abs(actual)
        
        # Accuracy = 1 - relative error (capped at 0-1)
        accuracy = max(0.0, min(1.0, 1.0 - relative_error))
        return accuracy


class LinearRegressionPredictor:
    """Linear regression prediction model."""
    
    def predict(self, current_state: Dict[str, float], target_variable: str, 
                horizon: PredictionHorizon) -> Optional[Prediction]:
        """Predict using linear regression."""
        if target_variable not in current_state:
            return None
        
        current_value = current_state[target_variable]
        trend = current_state.get("trend", 0.0)
        
        # Simple linear extrapolation
        horizon_seconds = 3600.0  # Assume 1 hour for simplicity
        predicted_change = trend * horizon_seconds
        predicted_value = current_value + predicted_change
        
        # Calculate confidence based on trend strength
        confidence = min(1.0, abs(trend) * 10)
        
        # Calculate confidence interval
        interval_size = abs(predicted_change) * 0.5
        confidence_interval = (predicted_value - interval_size, predicted_value + interval_size)
        
        return Prediction(
            prediction_id=f"lr_{int(time.time())}",
            target_variable=target_variable,
            predicted_value=predicted_value,
            confidence=confidence,
            confidence_interval=confidence_interval,
            prediction_type=PredictionType.DETERMINISTIC,
            horizon=horizon,
            timestamp=time.time() + horizon_seconds,
            prediction_time=time.time(),
            metadata={"model": "linear_regression", "trend": trend}
        )


class MovingAveragePredictor:
    """Moving average prediction model."""
    
    def __init__(self):
        self.history = defaultdict(lambda: deque(maxlen=20))
    
    def predict(self, current_state: Dict[str, float], target_variable: str, 
                horizon: PredictionHorizon) -> Optional[Prediction]:
        """Predict using moving average."""
        if target_variable not in current_state:
            return None
        
        # Add current value to history
        self.history[target_variable].append(current_state[target_variable])
        
        if len(self.history[target_variable]) < 5:
            return None
        
        # Calculate moving average
        values = list(self.history[target_variable])
        moving_avg = np.mean(values)
        
        # Predict based on moving average (assumes mean reversion)
        current_value = current_state[target_variable]
        predicted_value = moving_avg + (moving_avg - current_value) * 0.5  # Partial mean reversion
        
        confidence = min(1.0, len(values) / 10.0)  # Confidence increases with history
        
        # Confidence interval based on volatility
        volatility = np.std(values)
        confidence_interval = (predicted_value - volatility, predicted_value + volatility)
        
        return Prediction(
            prediction_id=f"ma_{int(time.time())}",
            target_variable=target_variable,
            predicted_value=predicted_value,
            confidence=confidence,
            confidence_interval=confidence_interval,
            prediction_type=PredictionType.DETERMINISTIC,
            horizon=horizon,
            timestamp=time.time() + 3600.0,
            prediction_time=time.time(),
            metadata={"model": "moving_average", "history_length": len(values)}
        )


class ExponentialSmoothingPredictor:
    """Exponential smoothing prediction model."""
    
    def __init__(self):
        self.history = defaultdict(lambda: deque(maxlen=20))
    
    def predict(self, current_state: Dict[str, float], target_variable: str, 
                horizon: PredictionHorizon) -> Optional[Prediction]:
        """Predict using exponential smoothing."""
        if target_variable not in current_state:
            return None
        
        # Add current value to history
        self.history[target_variable].append(current_state[target_variable])
        
        if len(self.history[target_variable]) < 5:
            return None
        
        values = list(self.history[target_variable])
        
        # Exponential smoothing
        alpha = 0.3  # Smoothing factor
        smoothed = values[0]
        for val in values[1:]:
            smoothed = alpha * val + (1 - alpha) * smoothed
        
        # Predict with trend continuation
        current_value = current_state[target_variable]
        trend = smoothed - current_value
        predicted_value = smoothed + trend * 0.5
        
        confidence = min(1.0, len(values) / 10.0)
        
        # Confidence interval
        volatility = np.std(values)
        confidence_interval = (predicted_value - volatility, predicted_value + volatility)
        
        return Prediction(
            prediction_id=f"es_{int(time.time())}",
            target_variable=target_variable,
            predicted_value=predicted_value,
            confidence=confidence,
            confidence_interval=confidence_interval,
            prediction_type=PredictionType.DETERMINISTIC,
            horizon=horizon,
            timestamp=time.time() + 3600.0,
            prediction_time=time.time(),
            metadata={"model": "exponential_smoothing", "alpha": alpha}
        )


class MomentumPredictor:
    """Momentum-based prediction model."""
    
    def __init__(self):
        self.history = defaultdict(lambda: deque(maxlen=20))
    
    def predict(self, current_state: Dict[str, float], target_variable: str, 
                horizon: PredictionHorizon) -> Optional[Prediction]:
        """Predict using momentum."""
        if target_variable not in current_state:
            return None
        
        self.history[target_variable].append(current_state[target_variable])
        
        if len(self.history[target_variable]) < 10:
            return None
        
        values = list(self.history[target_variable])
        
        # Calculate momentum
        short_momentum = values[-1] - values[-5]  # 5-period momentum
        long_momentum = values[-1] - values[-10]  # 10-period momentum
        
        # Predict with momentum continuation
        current_value = current_state[target_variable]
        predicted_value = current_value + (short_momentum + long_momentum) / 2
        
        # Confidence based on momentum consistency
        momentum_consistency = 1.0 if (short_momentum * long_momentum > 0) else 0.5
        confidence = momentum_consistency * min(1.0, len(values) / 10.0)
        
        # Confidence interval
        volatility = np.std(values)
        confidence_interval = (predicted_value - volatility * 2, predicted_value + volatility * 2)
        
        return Prediction(
            prediction_id=f"mom_{int(time.time())}",
            target_variable=target_variable,
            predicted_value=predicted_value,
            confidence=confidence,
            confidence_interval=confidence_interval,
            prediction_type=PredictionType.DETERMINISTIC,
            horizon=horizon,
            timestamp=time.time() + 3600.0,
            prediction_time=time.time(),
            metadata={"model": "momentum", "short_momentum": short_momentum, "long_momentum": long_momentum}
        )


class MeanReversionPredictor:
    """Mean reversion prediction model."""
    
    def __init__(self):
        self.history = defaultdict(lambda: deque(maxlen=20))
    
    def predict(self, current_state: Dict[str, float], target_variable: str, 
                horizon: PredictionHorizon) -> Optional[Prediction]:
        """Predict using mean reversion."""
        if target_variable not in current_state:
            return None
        
        self.history[target_variable].append(current_state[target_variable])
        
        if len(self.history[target_variable]) < 10:
            return None
        
        values = list(self.history[target_variable])
        
        # Calculate mean and deviation
        mean_value = np.mean(values)
        current_value = current_state[target_variable]
        deviation = current_value - mean_value
        
        # Predict mean reversion
        reversion_rate = 0.5  # 50% reversion per period
        predicted_value = current_value - deviation * reversion_rate
        
        # Confidence based on how far from mean
        distance_from_mean = abs(deviation) / (np.std(values) if np.std(values) > 0 else 1.0)
        confidence = min(1.0, distance_from_mean / 2.0)
        
        # Confidence interval
        volatility = np.std(values)
        confidence_interval = (predicted_value - volatility, predicted_value + volatility)
        
        return Prediction(
            prediction_id=f"mr_{int(time.time())}",
            target_variable=target_variable,
            predicted_value=predicted_value,
            confidence=confidence,
            confidence_interval=confidence_interval,
            prediction_type=PredictionType.DETERMINISTIC,
            horizon=horizon,
            timestamp=time.time() + 3600.0,
            prediction_time=time.time(),
            metadata={"model": "mean_reversion", "deviation": deviation, "mean": mean_value}
        )


class EnsembleBuilder:
    """Build ensemble predictions from individual model predictions."""
    
    def build_ensemble(self, individual_predictions: List[Prediction]) -> EnsemblePrediction:
        """Build ensemble prediction from individual predictions."""
        if not individual_predictions:
            raise ValueError("No individual predictions to ensemble")
        
        target_variable = individual_predictions[0].target_variable
        horizon = individual_predictions[0].horizon
        
        # Calculate weights based on confidence
        confidences = [p.confidence for p in individual_predictions]
        total_confidence = sum(confidences)
        weights = [c / total_confidence for c in confidences] if total_confidence > 0 else [1.0 / len(individual_predictions)] * len(individual_predictions)
        
        # Calculate ensemble value
        ensemble_value = sum(w * p.predicted_value for w, p in zip(weights, individual_predictions))
        
        # Calculate ensemble confidence
        ensemble_confidence = np.mean(confidences)
        
        # Calculate ensemble confidence interval
        lower_bounds = [p.confidence_interval[0] for p in individual_predictions]
        upper_bounds = [p.confidence_interval[1] for p in individual_predictions]
        ensemble_lower = sum(w * lb for w, lb in zip(weights, lower_bounds))
        ensemble_upper = sum(w * ub for w, ub in zip(weights, upper_bounds))
        
        return EnsemblePrediction(
            prediction_id=f"ensemble_{int(time.time())}_{target_variable}",
            target_variable=target_variable,
            individual_predictions=individual_predictions,
            ensemble_value=ensemble_value,
            ensemble_confidence=ensemble_confidence,
            ensemble_interval=(ensemble_lower, ensemble_upper),
            weights=weights,
            timestamp=time.time()
        )


class ScenarioGenerator:
    """Generate alternative scenarios for prediction."""
    
    def generate(self, current_state: Dict[str, float], num_scenarios: int) -> List[Scenario]:
        """Generate alternative scenarios."""
        scenarios = []
        
        current_price = current_state.get("price", 100.0)
        current_volatility = current_state.get("volatility", 0.2)
        current_trend = current_state.get("trend", 0.0)
        
        # Generate different scenario types
        scenario_types = ["bullish", "bearish", "neutral", "extreme_bull", "extreme_bear"]
        
        for i in range(num_scenarios):
            scenario_type = scenario_types[i % len(scenario_types)]
            
            if scenario_type == "bullish":
                conditions = {"price_change": 0.05, "volatility_change": -0.1, "trend_change": 0.02}
                outcomes = {"price": current_price * 1.05, "volatility": max(0.1, current_volatility * 0.9)}
                probability = 0.25 if current_trend > 0 else 0.15
            
            elif scenario_type == "bearish":
                conditions = {"price_change": -0.05, "volatility_change": -0.1, "trend_change": -0.02}
                outcomes = {"price": current_price * 0.95, "volatility": max(0.1, current_volatility * 0.9)}
                probability = 0.25 if current_trend < 0 else 0.15
            
            elif scenario_type == "neutral":
                conditions = {"price_change": 0.0, "volatility_change": 0.0, "trend_change": 0.0}
                outcomes = {"price": current_price, "volatility": current_volatility}
                probability = 0.3
            
            elif scenario_type == "extreme_bull":
                conditions = {"price_change": 0.15, "volatility_change": 0.3, "trend_change": 0.05}
                outcomes = {"price": current_price * 1.15, "volatility": current_volatility * 1.3}
                probability = 0.05
            
            elif scenario_type == "extreme_bear":
                conditions = {"price_change": -0.15, "volatility_change": 0.3, "trend_change": -0.05}
                outcomes = {"price": current_price * 0.85, "volatility": current_volatility * 1.3}
                probability = 0.05
            
            scenario = Scenario(
                scenario_id=f"scenario_{int(time.time())}_{i}",
                scenario_name=f"{scenario_type}_scenario",
                scenario_type=scenario_type,
                conditions=conditions,
                probability=probability,
                predicted_outcomes=outcomes,
                confidence=0.7,  # Moderate confidence for scenarios
                timestamp=time.time()
            )
            
            scenarios.append(scenario)
        
        return scenarios


class ConfidenceCalculator:
    """Calculate confidence for predictions and forecasts."""
    
    def calculate_overall_confidence(self, *predictions) -> float:
        """Calculate overall confidence from multiple predictions."""
        if not predictions:
            return 0.5
        
        confidences = [p.confidence for p in predictions]
        weights = []
        
        # Calculate weights based on prediction age and accuracy
        for p in predictions:
            weight = p.confidence
            if p.accuracy is not None:
                weight *= (0.5 + 0.5 * p.accuracy)  # Adjust based on accuracy
            weights.append(weight)
        
        total_weight = sum(weights)
        if total_weight > 0:
            weighted_confidence = sum(c * w for c, w in zip(confidences, weights)) / total_weight
            return weighted_confidence
        
        return np.mean(confidences)


# Singleton instance
_predictive_world_model: Optional[PredictiveWorldModel] = None
_predictive_world_model_lock = threading.Lock()


def get_predictive_world_model(history_window: int = 1000) -> PredictiveWorldModel:
    """Get the singleton predictive world model instance."""
    global _predictive_world_model
    if _predictive_world_model is None:
        with _predictive_world_model_lock:
            if _predictive_world_model is None:
                _predictive_world_model = PredictiveWorldModel(history_window)
    return _predictive_world_model


__all__ = [
    "PredictiveWorldModel",
    "get_predictive_world_model",
    "PredictionHorizon",
    "PredictionType",
    "Prediction",
    "Scenario",
    "EnsemblePrediction",
    "MarketForecast",
]