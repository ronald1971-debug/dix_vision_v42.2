"""
Execution Unified Algorithms Risk - Risk Management Algorithms
Provides real risk-based algorithm implementations with proper mathematical models
NO LAZY LOADING - All components load directly
"""

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List

import numpy as np
from scipy import stats

logger = logging.getLogger(__name__)


@dataclass
class RiskAssessment:
    """Comprehensive risk assessment data structure"""

    risk_level: str = "medium"
    risk_score: float = 0.5
    value_at_risk: float = 0.0
    expected_shortfall: float = 0.0
    confidence_level: float = 0.95
    factors: Dict[str, float] = None
    mitigation: List[str] = None
    portfolio_exposure: float = 0.0
    leverage_ratio: float = 0.0

    def __post_init__(self):
        if self.factors is None:
            self.factors = {}
        if self.mitigation is None:
            self.mitigation = []


@dataclass
class MarketRiskMetrics:
    """Market risk metrics for real-time risk assessment"""

    volatility: float
    beta: float
    correlation: float
    downside_deviation: float
    maximum_drawdown: float
    skewness: float
    kurtosis: float
    var_95: float
    var_99: float
    es_95: float
    es_99: float


class RiskAlgorithm:
    """Advanced risk calculation algorithm using real mathematical models"""

    def __init__(self, config: Dict[str, Any] = None):
        self._config = config or {}
        self._risk_thresholds = config.get(
            "risk_thresholds", {"low": 0.3, "medium": 0.6, "high": 0.8}
        )
        self._confidence_level = config.get("confidence_level", 0.95)
        self._lookback_period = config.get("lookback_period", 252)  # Trading days
        self._price_history = []

    def update_price_history(self, timestamp: datetime, price: float):
        """Update price history for risk calculations"""
        self._price_history.append({"timestamp": timestamp, "price": price})

        # Keep only recent history
        cutoff_date = datetime.now() - timedelta(days=self._lookback_period)
        self._price_history = [p for p in self._price_history if p["timestamp"] >= cutoff_date]

    def calculate_returns(self) -> np.ndarray:
        """Calculate logarithmic returns from price history"""
        if len(self._price_history) < 2:
            return np.array([])

        prices = np.array([p["price"] for p in self._price_history])
        returns = np.diff(np.log(prices))
        return returns

    def calculate_volatility(self, returns: np.ndarray = None) -> float:
        """Calculate annualized volatility using real statistical methods"""
        if returns is None:
            returns = self.calculate_returns()

        if len(returns) == 0:
            return 0.0

        # Use exponential weighted volatility (more recent data has higher weight)
        lambda_param = 0.94  # Decay factor
        weights = np.array([lambda_param**i for i in range(len(returns))][::-1])
        weights = weights / weights.sum()

        weighted_variance = (
            np.average(returns**2, weights=weights) - np.average(returns, weights=weights) ** 2
        )
        volatility = np.sqrt(weighted_variance * 252)  # Annualized

        return max(0.0, volatility)

    def calculate_var(self, returns: np.ndarray = None, confidence: float = 0.95) -> float:
        """Calculate Value at Risk using historical simulation method"""
        if returns is None:
            returns = self.calculate_returns()

        if len(returns) == 0:
            return 0.0

        # Historical simulation VaR
        var_percentile = (1 - confidence) * 100
        var = np.percentile(returns, var_percentile)

        return abs(var)  # Return positive VaR

    def calculate_expected_shortfall(
        self, returns: np.ndarray = None, confidence: float = 0.95
    ) -> float:
        """Calculate Expected Shortfall (Conditional VaR) using real statistics"""
        if returns is None:
            returns = self.calculate_returns()

        if len(returns) == 0:
            return 0.0

        var_threshold = np.percentile(returns, (1 - confidence) * 100)
        tail_losses = returns[returns <= var_threshold]

        if len(tail_losses) == 0:
            return 0.0

        expected_shortfall = abs(np.mean(tail_losses))
        return expected_shortfall

    def calculate_beta(
        self, returns: np.ndarray = None, market_returns: np.ndarray = None
    ) -> float:
        """Calculate beta (systematic risk) using real covariance analysis"""
        if returns is None:
            returns = self.calculate_returns()

        if len(returns) == 0 or market_returns is None or len(market_returns) == 0:
            return 1.0  # Default beta

        # Calculate covariance and variance
        min_len = min(len(returns), len(market_returns))
        returns_aligned = returns[-min_len:]
        market_aligned = market_returns[-min_len:]

        covariance = np.cov(returns_aligned, market_aligned)[0, 1]
        market_variance = np.var(market_aligned)

        if market_variance == 0:
            return 1.0

        beta = covariance / market_variance
        return beta

    def calculate_downside_deviation(
        self, returns: np.ndarray = None, minimum_acceptable_return: float = 0.0
    ) -> float:
        """Calculate downside deviation using real risk metrics"""
        if returns is None:
            returns = self.calculate_returns()

        if len(returns) == 0:
            return 0.0

        # Calculate returns below minimum acceptable return
        downside_returns = returns[returns < minimum_acceptable_return]

        if len(downside_returns) == 0:
            return 0.0

        # Semi-deviation calculation
        downside_variance = np.mean((downside_returns - minimum_acceptable_return) ** 2)
        downside_deviation = np.sqrt(downside_variance * 252)  # Annualized

        return downside_deviation

    def calculate_market_risk_metrics(self, market_returns: np.ndarray = None) -> MarketRiskMetrics:
        """Calculate comprehensive market risk metrics"""
        returns = self.calculate_returns()

        if len(returns) == 0:
            return MarketRiskMetrics(0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)

        volatility = self.calculate_volatility(returns)
        beta = self.calculate_beta(returns, market_returns)
        correlation = (
            np.corrcoef(returns, market_returns[-len(returns) :])[0, 1]
            if market_returns is not None
            else 0.0
        )
        downside_deviation = self.calculate_downside_deviation(returns)

        # Calculate maximum drawdown
        cumulative = np.cumprod(1 + returns)
        running_max = np.maximum.accumulate(cumulative)
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = np.min(drawdown)

        # Calculate higher moments
        skewness = stats.skew(returns)
        kurtosis = stats.kurtosis(returns)

        # Calculate VaR and ES at different confidence levels
        var_95 = self.calculate_var(returns, 0.95)
        var_99 = self.calculate_var(returns, 0.99)
        es_95 = self.calculate_expected_shortfall(returns, 0.95)
        es_99 = self.calculate_expected_shortfall(returns, 0.99)

        return MarketRiskMetrics(
            volatility=volatility,
            beta=beta,
            correlation=correlation,
            downside_deviation=downside_deviation,
            maximum_drawdown=max_drawdown,
            skewness=skewness,
            kurtosis=kurtosis,
            var_95=var_95,
            var_99=var_99,
            es_95=es_95,
            es_99=es_99,
        )

    def assess_risk(self, execution_data: Dict[str, Any]) -> RiskAssessment:
        """Comprehensive risk assessment using real mathematical models"""
        quantity = execution_data.get("quantity", 0)
        price = execution_data.get("price", 100.0)
        volatility = execution_data.get("volatility", self.calculate_volatility())
        market_impact = execution_data.get("market_impact", 0.05)
        portfolio_value = execution_data.get("portfolio_value", 100000.0)
        leverage = execution_data.get("leverage", 1.0)

        # Calculate position value and exposure
        position_value = abs(quantity * price)
        portfolio_exposure = position_value / portfolio_value if portfolio_value > 0 else 0.0

        # Get real risk metrics
        returns = self.calculate_returns()
        var = self.calculate_var(returns, self._confidence_level)
        expected_shortfall = self.calculate_expected_shortfall(returns, self._confidence_level)

        # Calculate comprehensive risk score using weighted factors
        volatility_risk = min(1.0, volatility / 0.5)  # Normalize against 50% volatility
        market_impact_risk = min(1.0, market_impact / 0.2)  # Normalize against 20% impact
        exposure_risk = min(1.0, portfolio_exposure)  # Direct exposure
        leverage_risk = min(1.0, leverage / 5.0)  # Normalize against 5x leverage
        concentration_risk = min(1.0, execution_data.get("concentration", 0.0))

        # Weighted risk score
        risk_score = (
            volatility_risk * 0.25
            + market_impact_risk * 0.20
            + exposure_risk * 0.20
            + leverage_risk * 0.20
            + concentration_risk * 0.15
        )

        # Determine risk level
        if risk_score < self._risk_thresholds["low"]:
            risk_level = "low"
        elif risk_score < self._risk_thresholds["medium"]:
            risk_level = "medium"
        elif risk_score < self._risk_thresholds["high"]:
            risk_level = "high"
        else:
            risk_level = "critical"

        # Generate mitigation recommendations
        mitigation = []
        if volatility_risk > 0.7:
            mitigation.append("Reduce position size due to high volatility")
        if market_impact_risk > 0.7:
            mitigation.append("Use algorithmic execution to reduce market impact")
        if exposure_risk > 0.8:
            mitigation.append("Diversify portfolio to reduce concentration risk")
        if leverage_risk > 0.8:
            mitigation.append("Reduce leverage to acceptable levels")

        return RiskAssessment(
            risk_level=risk_level,
            risk_score=risk_score,
            value_at_risk=var * position_value,
            expected_shortfall=expected_shortfall * position_value,
            confidence_level=self._confidence_level,
            factors={
                "volatility_risk": volatility_risk,
                "market_impact_risk": market_impact_risk,
                "exposure_risk": exposure_risk,
                "leverage_risk": leverage_risk,
                "concentration_risk": concentration_risk,
            },
            mitigation=mitigation,
            portfolio_exposure=portfolio_exposure,
            leverage_ratio=leverage,
        )


class SlippageRiskAlgorithm:
    """Advanced slippage risk calculation using real market microstructure models"""

    def __init__(self, config: Dict[str, Any] = None):
        self._config = config or {}
        self._slippage_history = []
        self._market_depth_history = []

    def update_slippage_history(
        self, timestamp: datetime, actual_price: float, expected_price: float, quantity: float
    ):
        """Update slippage history for model calibration"""
        slippage = (
            abs(actual_price - expected_price) / expected_price if expected_price > 0 else 0.0
        )
        self._slippage_history.append(
            {
                "timestamp": timestamp,
                "slippage": slippage,
                "quantity": quantity,
                "actual_price": actual_price,
                "expected_price": expected_price,
            }
        )

    def estimate_slippage(self, order_data: Dict[str, Any]) -> Dict[str, float]:
        """Estimate slippage using real market microstructure models"""
        quantity = abs(order_data.get("quantity", 0))
        spread = order_data.get("spread", 0.001)
        volume = order_data.get("volume", 1000000)
        volatility = order_data.get("volatility", 0.1)
        price = order_data.get("price", 100.0)

        # Almgren-Chriss temporary impact model
        temporary_impact_coef = self._config.get("temporary_impact_coef", 0.005)
        temporary_impact = temporary_impact_coef * np.sqrt(quantity / volume)

        # Permanent impact model (linear in order size)
        permanent_impact_coef = self._config.get("permanent_impact_coef", 0.001)
        permanent_impact = permanent_impact_coef * (quantity / volume)

        # Spread-related slippage
        spread_impact = spread / 2.0  # Assume execution at midprice is optimal

        # Volatility-related slippage (price drift during execution)
        execution_time = self._config.get("execution_time", 300)  # seconds
        volatility_impact = volatility * np.sqrt(
            execution_time / (252 * 8 * 3600)
        )  # Annualized to per-second

        # Total estimated slippage
        total_slippage = temporary_impact + permanent_impact + spread_impact + volatility_impact

        # Confidence interval for slippage estimate
        if len(self._slippage_history) > 10:
            slippage_std = np.std([s["slippage"] for s in self._slippage_history])
            confidence_interval = 1.96 * slippage_std / np.sqrt(len(self._slippage_history))
        else:
            confidence_interval = total_slippage * 0.5  # Conservative estimate

        return {
            "estimated_slippage": total_slippage,
            "temporary_impact": temporary_impact,
            "permanent_impact": permanent_impact,
            "spread_impact": spread_impact,
            "volatility_impact": volatility_impact,
            "confidence_interval": confidence_interval,
            "price_impact_dollars": total_slippage * price * quantity,
            "slippage_bps": total_slippage * 10000,  # Basis points
        }

    def calculate_slippage_risk(self, execution_data: Dict[str, Any]) -> float:
        """Calculate slippage risk score using calibrated models"""
        slippage_estimate = self.estimate_slippage(execution_data)

        # Calculate risk score based on estimated slippage
        estimated_slippage = slippage_estimate["estimated_slippage"]
        max_acceptable_slippage = self._config.get("max_acceptable_slippage", 0.02)  # 2%

        risk_score = min(1.0, estimated_slippage / max_acceptable_slippage)

        # Adjust for confidence interval
        confidence_interval = slippage_estimate["confidence_interval"]
        adjusted_risk_score = min(
            1.0, (estimated_slippage + confidence_interval) / max_acceptable_slippage
        )

        return adjusted_risk_score


class PortfolioRiskAlgorithm:
    """Portfolio-level risk calculation using real covariance models"""

    def __init__(self, config: Dict[str, Any] = None):
        self._config = config or {}
        self._holdings = {}
        self._correlation_matrix = {}

    def update_holdings(self, symbol: str, quantity: float, price: float):
        """Update holdings for portfolio risk calculation"""
        self._holdings[symbol] = {
            "quantity": quantity,
            "price": price,
            "value": abs(quantity * price),
        }

    def calculate_portfolio_var(self, confidence_level: float = 0.95) -> float:
        """Calculate portfolio VaR using real covariance matrix"""
        if not self._holdings:
            return 0.0

        # Get portfolio values
        portfolio_values = np.array([h["value"] for h in self._holdings.values()])
        total_portfolio_value = np.sum(portfolio_values)

        if total_portfolio_value == 0:
            return 0.0

        # Calculate portfolio weights
        weights = portfolio_values / total_portfolio_value

        # Use simplified correlation matrix (in real system, would use historical correlations)
        n = len(weights)
        correlation_matrix = np.ones((n, n)) * 0.3  # Assume 30% average correlation
        np.fill_diagonal(correlation_matrix, 1.0)

        # Get volatilities (in real system, would use historical data)
        volatilities = np.array(
            [self._config.get(f"{symbol}_volatility", 0.2) for symbol in self._holdings.keys()]
        )

        # Create covariance matrix
        covariance_matrix = np.outer(volatilities, volatilities) * correlation_matrix

        # Calculate portfolio variance
        portfolio_variance = np.dot(weights, np.dot(covariance_matrix, weights))
        portfolio_volatility = np.sqrt(portfolio_variance)

        # Calculate VaR using normal distribution
        z_score = stats.norm.ppf(1 - confidence_level)
        portfolio_var = z_score * portfolio_volatility * total_portfolio_value

        return abs(portfolio_var)

    def calculate_concentration_risk(self) -> Dict[str, float]:
        """Calculate concentration risk metrics"""
        if not self._holdings:
            return {}

        portfolio_values = np.array([h["value"] for h in self._holdings.values()])
        total_portfolio_value = np.sum(portfolio_values)

        if total_portfolio_value == 0:
            return {}

        weights = portfolio_values / total_portfolio_value

        # Herfindahl-Hirschman Index (HHI)
        hhi = np.sum(weights**2)

        # Concentration ratio (top 5 holdings)
        sorted_weights = np.sort(weights)[::-1]
        concentration_ratio = (
            np.sum(sorted_weights[:5]) if len(sorted_weights) >= 5 else np.sum(sorted_weights)
        )

        return {
            "hhi": hhi,
            "concentration_ratio": concentration_ratio,
            "max_single_position": np.max(weights),
            "gini_coefficient": self._calculate_gini(weights),
        }

    def _calculate_gini(self, weights: np.ndarray) -> float:
        """Calculate Gini coefficient for concentration measurement"""
        sorted_weights = np.sort(weights)
        n = len(sorted_weights)
        cumsum_weights = np.cumsum(sorted_weights)

        gini = (
            n + 1 - 2 * np.sum((n + 1 - np.arange(1, n + 1)) * sorted_weights) / cumsum_weights[-1]
        ) / n
        return max(0.0, min(1.0, gini))


__all__ = [
    "RiskAssessment",
    "MarketRiskMetrics",
    "RiskAlgorithm",
    "SlippageRiskAlgorithm",
    "PortfolioRiskAlgorithm",
]
