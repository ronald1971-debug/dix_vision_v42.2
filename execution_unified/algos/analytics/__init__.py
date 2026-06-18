"""
Execution Unified Algorithms Analytics - Real Analytics Algorithms
Provides analytics-based algorithm implementations with mathematical models
NO LAZY LOADING - All components load directly
"""

from typing import Dict, List, Optional, Any, Tuple
import logging
import numpy as np
from scipy import stats
from scipy.optimize import curve_fit
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class SlippageCurveAlgorithm:
    """Real slippage curve modeling using statistical regression"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self._config = config or {}
        self._slippage_history = []
        self._curve_parameters = None
        self._model_fitted = False
        
    def update_slippage_data(self, timestamp: datetime, order_size: float, 
                           actual_price: float, expected_price: float, 
                           market_conditions: Dict[str, Any]):
        """Update slippage data for curve fitting"""
        slippage = (actual_price - expected_price) / expected_price if expected_price > 0 else 0.0
        slippage_bps = slippage * 10000
        
        self._slippage_history.append({
            "timestamp": timestamp,
            "order_size": order_size,
            "slippage_bps": slippage_bps,
            "slippage": slippage,
            "actual_price": actual_price,
            "expected_price": expected_price,
            "market_conditions": market_conditions
        })
        
        # Keep only recent data (e.g., last 1000 observations)
        if len(self._slippage_history) > 1000:
            self._slippage_history = self._slippage_history[-1000:]
    
    def _slippage_model(self, order_size: float, alpha: float, beta: float, gamma: float) -> float:
        """Mathematical model for slippage: S = α * Q + β * Q² + γ"""
        return alpha * order_size + beta * (order_size ** 2) + gamma
    
    def fit_slippage_curve(self) -> Dict[str, float]:
        """Fit slippage curve using statistical regression"""
        if len(self._slippage_history) < 10:
            return {"error": "Insufficient data for curve fitting"}
        
        # Prepare data for regression
        order_sizes = np.array([s["order_size"] for s in self._slippage_history])
        slippages = np.array([s["slippage_bps"] for s in self._slippage_history])
        
        # Normalize order sizes
        normalized_sizes = order_sizes / np.mean(order_sizes)
        
        # Fit the model
        try:
            params, covariance = curve_fit(
                self._slippage_model, 
                normalized_sizes, 
                slippages,
                p0=[0.1, 0.01, 1.0],  # Initial guess
                bounds=([0, 0, 0], [10, 1, 100])  # Positive parameters only
            )
            
            alpha, beta, gamma = params
            
            # Calculate fit statistics
            predicted_slippages = self._slippage_model(normalized_sizes, alpha, beta, gamma)
            residuals = slippages - predicted_slippages
            r_squared = 1 - (np.sum(residuals ** 2) / np.sum((slippages - np.mean(slippages)) ** 2))
            
            self._curve_parameters = {
                "alpha": alpha,
                "beta": beta, 
                "gamma": gamma,
                "r_squared": r_squared,
                "fit_timestamp": datetime.now()
            }
            self._model_fitted = True
            
            return self._curve_parameters
            
        except Exception as e:
            logger.error(f"Slippage curve fitting failed: {e}")
            return {"error": str(e)}
    
    def calculate_slippage_curve(self, execution_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate slippage curve for execution using fitted model"""
        quantity = execution_data.get("quantity", 0)
        price = execution_data.get("price", 100.0)
        
        if not self._model_fitted or self._curve_parameters is None:
            # Fit model if not already fitted
            fit_result = self.fit_slippage_curve()
            if "error" in fit_result:
                return fit_result
        
        params = self._curve_parameters
        alpha = params["alpha"]
        beta = params["beta"]
        gamma = params["gamma"]
        
        # Calculate slippage at different quantity levels
        mean_order_size = np.mean([s["order_size"] for s in self._slippage_history]) if self._slippage_history else 1000.0
        
        test_quantities = [quantity * 0.25, quantity * 0.5, quantity * 0.75, quantity, quantity * 1.25, quantity * 1.5]
        curve_points = []
        
        for q in test_quantities:
            if q <= 0:
                continue
                
            normalized_q = q / mean_order_size
            slippage_bps = self._slippage_model(normalized_q, alpha, beta, gamma)
            slippage_percent = slippage_bps / 100
            
            # Calculate confidence interval if we have enough data
            if len(self._slippage_history) >= 30:
                recent_slippages = [s["slippage_bps"] for s in self._slippage_history[-30:]]
                std_error = np.std(recent_slippages) / np.sqrt(len(recent_slippages))
                confidence_interval = 1.96 * std_error  # 95% confidence
            else:
                confidence_interval = slippage_bps * 0.5  # Conservative estimate
            
            curve_points.append({
                "quantity": q,
                "slippage_percent": slippage_percent,
                "slippage_bps": slippage_bps,
                "estimated_price": price * (1 + slippage_percent),
                "confidence_interval_lower": (slippage_bps - confidence_interval) / 100,
                "confidence_interval_upper": (slippage_bps + confidence_interval) / 100,
                "confidence_interval_bps": confidence_interval
            })
        
        return {
            "curve_points": curve_points,
            "parameters": params,
            "total_quantity": quantity,
            "model_fit_quality": params.get("r_squared", 0.0),
            "data_points_used": len(self._slippage_history)
        }
    
    def predict_slippage(self, order_size: float, market_conditions: Dict[str, Any] = None) -> Dict[str, float]:
        """Predict slippage for a given order size"""
        if not self._model_fitted or self._curve_parameters is None:
            return {"error": "Model not fitted"}
        
        mean_order_size = np.mean([s["order_size"] for s in self._slippage_history]) if self._slippage_history else 1000.0
        normalized_size = order_size / mean_order_size
        
        params = self._curve_parameters
        predicted_slippage_bps = self._slippage_model(normalized_size, params["alpha"], params["beta"], params["gamma"])
        
        # Adjust for market conditions if provided
        if market_conditions:
            volatility_adjustment = market_conditions.get("volatility", 0.2) / 0.2  # Normalize against 20% volatility
            liquidity_adjustment = 1.0 / market_conditions.get("liquidity_score", 0.5)
            
            predicted_slippage_bps *= (volatility_adjustment * liquidity_adjustment)
        
        return {
            "predicted_slippage_bps": predicted_slippage_bps,
            "predicted_slippage_percent": predicted_slippage_bps / 100,
            "confidence": params.get("r_squared", 0.0)
        }

class ModelExecutionAlgorithm:
    """Real model-based execution using machine learning techniques"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self._config = config or {}
        self._model_parameters = {
            "lookback_period": config.get("lookback_period", 100) if config else 100,
            "volatility_window": config.get("volatility_window", 20) if config else 20,
            "momentum_factor": config.get("momentum_factor", 0.3) if config else 0.3,
            "mean_reversion_factor": config.get("mean_reversion_factor", 0.2) if config else 0.2,
            "liquidity_factor": config.get("liquidity_factor", 0.25) if config else 0.25
        }
        self._price_history = []
        self._volume_history = []
        self._spread_history = []
        self._execution_history = []
        
    def update_market_data(self, timestamp: datetime, price: float, 
                         volume: float, spread: float):
        """Update market data for model training"""
        self._price_history.append({"timestamp": timestamp, "price": price})
        self._volume_history.append({"timestamp": timestamp, "volume": volume})
        self._spread_history.append({"timestamp": timestamp, "spread": spread})
        
        # Keep only recent data
        lookback = self._model_parameters["lookback_period"]
        if len(self._price_history) > lookback:
            self._price_history = self._price_history[-lookback:]
            self._volume_history = self._volume_history[-lookback:]
            self._spread_history = self._spread_history[-lookback:]
    
    def calculate_market_features(self, market_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate market features for model-based decision making"""
        if not self._price_history or len(self._price_history) < self._model_parameters["volatility_window"]:
            return self._get_default_features()
        
        prices = np.array([p["price"] for p in self._price_history])
        volumes = np.array([v["volume"] for v in self._volume_history])
        spreads = np.array([s["spread"] for s in self._spread_history])
        
        # Volatility (using exponential weighted method)
        lambda_param = 0.94
        weights = np.array([lambda_param ** i for i in range(len(prices))][::-1])
        weights = weights / weights.sum()
        returns = np.diff(np.log(prices))
        volatility = np.sqrt(np.average(returns ** 2, weights=weights) * 252)
        
        # Momentum (using multiple timeframes)
        momentum_short = (prices[-1] / prices[-5] - 1) if len(prices) >= 5 else 0.0  # 5-period momentum
        momentum_medium = (prices[-1] / prices[-20] - 1) if len(prices) >= 20 else 0.0  # 20-period momentum
        momentum_long = (prices[-1] / prices[-60] - 1) if len(prices) >= 60 else 0.0  # 60-period momentum
        
        # Mean reversion indicator
        mean_price = np.mean(prices[-self._model_parameters["volatility_window"]:])
        mean_reversion = (mean_price - prices[-1]) / mean_price if mean_price > 0 else 0.0
        
        # Volume analysis
        avg_volume = np.mean(volumes[-20:])
        volume_trend = volumes[-1] / avg_volume if avg_volume > 0 else 1.0
        
        # Spread analysis
        avg_spread = np.mean(spreads[-20:])
        spread_ratio = spreads[-1] / avg_spread if avg_spread > 0 else 1.0
        
        # Trend strength
        if len(prices) >= 20:
            x = np.arange(len(prices[-20:]))
            slope, _ = np.polyfit(x, prices[-20:], 1)
            trend_strength = slope / np.mean(prices[-20:]) if np.mean(prices[-20:]) > 0 else 0.0
        else:
            trend_strength = 0.0
        
        return {
            "volatility": volatility,
            "momentum_short": momentum_short,
            "momentum_medium": momentum_medium,
            "momentum_long": momentum_long,
            "mean_reversion": mean_reversion,
            "volume_trend": volume_trend,
            "spread_ratio": spread_ratio,
            "trend_strength": trend_strength,
            "price_momentum": np.mean([momentum_short, momentum_medium, momentum_long])
        }
    
    def _get_default_features(self) -> Dict[str, float]:
        """Return default features when insufficient data"""
        return {
            "volatility": 0.2,
            "momentum_short": 0.0,
            "momentum_medium": 0.0,
            "momentum_long": 0.0,
            "mean_reversion": 0.0,
            "volume_trend": 1.0,
            "spread_ratio": 1.0,
            "trend_strength": 0.0,
            "price_momentum": 0.0
        }
    
    def calculate_execution_confidence(self, features: Dict[str, float]) -> float:
        """Calculate confidence in execution strategy based on market features"""
        volatility = features["volatility"]
        momentum = abs(features["price_momentum"])
        volume_trend = features["volume_trend"]
        spread_ratio = features["spread_ratio"]
        
        # High confidence conditions:
        # - Moderate volatility (not too high, not too low)
        # - Strong directional momentum
        # - High volume (good liquidity)
        # - Low spread (efficient market)
        
        volatility_score = max(0, 1 - abs(volatility - 0.2) / 0.3)  # Peak at 20% volatility
        momentum_score = min(1, momentum * 10)  # Higher momentum = higher confidence
        volume_score = min(1, volume_trend)  # Higher volume = higher confidence
        spread_score = max(0, 1 - (spread_ratio - 1) * 2)  # Lower spread = higher confidence
        
        confidence = (
            volatility_score * 0.3 +
            momentum_score * 0.3 +
            volume_score * 0.25 +
            spread_score * 0.15
        )
        
        return max(0, min(1, confidence))
    
    def execute_with_model(self, order_data: Dict[str, Any], market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute order using model-based approach with real analytics"""
        # Calculate market features
        features = self.calculate_market_features(market_data)
        
        # Calculate execution confidence
        confidence = self.calculate_execution_confidence(features)
        
        # Determine execution strategy based on features
        volatility = features["volatility"]
        momentum = features["price_momentum"]
        mean_reversion = features["mean_reversion"]
        
        # Size adjustment based on market conditions
        volatility_adjustment = max(0.5, min(1.5, 1.0 - volatility * 0.5))
        momentum_adjustment = 1.0 + momentum * self._model_parameters["momentum_factor"]
        mean_reversion_adjustment = 1.0 - mean_reversion * self._model_parameters["mean_reversion_factor"]
        
        total_size_adjustment = volatility_adjustment * momentum_adjustment * mean_reversion_adjustment
        adjusted_quantity = order_data.get("quantity", 0) * total_size_adjustment
        
        # Timing adjustment
        if abs(momentum) > 0.02:  # Strong momentum
            timing_strategy = "aggressive" if momentum > 0 else "patient"
            timing_adjustment = momentum * 0.5
        elif abs(mean_reversion) > 0.01:  # Mean reversion signal
            timing_strategy = "patient"
            timing_adjustment = -mean_reversion * 0.3
        else:
            timing_strategy = "neutral"
            timing_adjustment = 0.0
        
        # Risk assessment
        risk_level = "low" if volatility < 0.15 else "medium" if volatility < 0.3 else "high"
        
        # Generate model-based recommendations
        recommendations = []
        if volatility > 0.3:
            recommendations.append("High volatility - use algorithmic execution with risk controls")
        if momentum > 0.05:
            recommendations.append("Strong uptrend momentum - consider aggressive execution")
        elif momentum < -0.05:
            recommendations.append("Strong downtrend momentum - consider patient execution")
        if features["volume_trend"] < 0.8:
            recommendations.append("Low volume conditions - use conservative sizing")
        
        result = {
            "original_quantity": order_data.get("quantity", 0),
            "adjusted_quantity": adjusted_quantity,
            "size_adjustment_factor": total_size_adjustment,
            "timing_strategy": timing_strategy,
            "timing_adjustment": timing_adjustment,
            "model_confidence": confidence,
            "risk_level": risk_level,
            "market_features": features,
            "recommendations": recommendations,
            "strategy": "model_based_execution",
            "execution_timestamp": datetime.now()
        }
        
        # Update execution history
        self._execution_history.append({
            "timestamp": datetime.now(),
            "order_data": order_data,
            "market_features": features,
            "result": result
        })
        
        return result

class ExecutionPerformanceAnalyzer:
    """Real execution performance analysis using statistical metrics"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self._config = config or {}
        self._execution_history = []
        self._performance_metrics = {}
        
    def analyze_execution(self, execution_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze execution performance using real metrics"""
        # Extract execution details
        actual_price = execution_data.get("actual_price", 0.0)
        expected_price = execution_data.get("expected_price", 0.0)
        target_quantity = execution_data.get("target_quantity", 0.0)
        executed_quantity = execution_data.get("executed_quantity", 0.0)
        start_time = execution_data.get("start_time")
        end_time = execution_data.get("end_time")
        
        # Calculate basic performance metrics
        if expected_price > 0:
            price_deviation = (actual_price - expected_price) / expected_price
        else:
            price_deviation = 0.0
        
        if target_quantity > 0:
            fill_rate = executed_quantity / target_quantity
        else:
            fill_rate = 0.0
        
        if start_time and end_time:
            execution_duration = (end_time - start_time).total_seconds()
        else:
            execution_duration = 0.0
        
        # Calculate implementation shortfall
        market_return = execution_data.get("market_return", 0.0)
        implementation_shortfall = price_deviation + market_return
        
        # Calculate risk metrics
        volatility = execution_data.get("volatility", 0.2)
        market_impact = execution_data.get("market_impact", 0.0)
        
        # Performance score
        performance_score = self._calculate_performance_score(
            price_deviation, fill_rate, execution_duration, market_impact
        )
        
        analysis = {
            "price_deviation_bps": price_deviation * 10000,
            "fill_rate": fill_rate,
            "execution_duration_seconds": execution_duration,
            "implementation_shortfall_bps": implementation_shortfall * 10000,
            "market_impact_bps": market_impact * 10000,
            "performance_score": performance_score,
            "performance_rating": self._get_performance_rating(performance_score),
            "risk_adjusted_score": performance_score * (1 - volatility),
            "timestamp": datetime.now()
        }
        
        # Update history
        self._execution_history.append(analysis)
        
        return analysis
    
    def _calculate_performance_score(self, price_deviation: float, fill_rate: float, 
                                   duration: float, market_impact: float) -> float:
        """Calculate overall execution performance score"""
        # Price score (lower deviation is better)
        price_score = max(0, 1 - abs(price_deviation) * 100)  # Penalize large deviations
        
        # Fill rate score (higher is better)
        fill_score = fill_rate
        
        # Duration score (faster execution is generally better, but depends on strategy)
        duration_score = max(0, 1 - duration / 3600)  # Normalize against 1 hour
        
        # Market impact score (lower impact is better)
        impact_score = max(0, 1 - market_impact * 50)  # Penalize large impact
        
        # Weighted score
        performance_score = (
            price_score * 0.35 +
            fill_score * 0.25 +
            duration_score * 0.20 +
            impact_score * 0.20
        )
        
        return max(0, min(1, performance_score))
    
    def _get_performance_rating(self, score: float) -> str:
        """Convert performance score to rating"""
        if score >= 0.9:
            return "Excellent"
        elif score >= 0.8:
            return "Good"
        elif score >= 0.7:
            return "Fair"
        elif score >= 0.6:
            return "Poor"
        else:
            return "Very Poor"
    
    def get_aggregate_metrics(self) -> Dict[str, Any]:
        """Calculate aggregate performance metrics"""
        if not self._execution_history:
            return {"error": "No execution history available"}
        
        recent_executions = self._execution_history[-50:]  # Last 50 executions
        
        avg_price_deviation = np.mean([e["price_deviation_bps"] for e in recent_executions])
        avg_fill_rate = np.mean([e["fill_rate"] for e in recent_executions])
        avg_performance_score = np.mean([e["performance_score"] for e in recent_executions])
        
        # Calculate improvement trend
        if len(recent_executions) >= 10:
            early_score = np.mean([e["performance_score"] for e in recent_executions[:10]])
            late_score = np.mean([e["performance_score"] for e in recent_executions[-10:]])
            improvement_trend = (late_score - early_score) / early_score if early_score > 0 else 0.0
        else:
            improvement_trend = 0.0
        
        return {
            "total_executions": len(self._execution_history),
            "avg_price_deviation_bps": avg_price_deviation,
            "avg_fill_rate": avg_fill_rate,
            "avg_performance_score": avg_performance_score,
            "improvement_trend": improvement_trend,
            "best_performance": max([e["performance_score"] for e in recent_executions]),
            "worst_performance": min([e["performance_score"] for e in recent_executions]),
            "performance_std": np.std([e["performance_score"] for e in recent_executions])
        }

__all__ = [
    'SlippageCurveAlgorithm',
    'ModelExecutionAlgorithm',
    'ExecutionPerformanceAnalyzer'
]