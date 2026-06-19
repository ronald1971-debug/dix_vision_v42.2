"""RISK-01 — Advanced risk management for portfolio optimization.

Enhances INDIRA's risk management capabilities with VaR/CVaR calculation,
dynamic risk budgeting, stress testing, and real-time risk monitoring.

Pure computation. No clocks, no I/O. INV-15 deterministic.
B1: No imports from execution_engine/governance_engine/learning_engine/evolution_engine.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any
from collections import deque
from enum import Enum


class RiskMetric(Enum):
    """Types of risk metrics."""
    VAR = "value_at_risk"
    CVAR = "conditional_var"
    MAX_DRAWDOWN = "max_drawdown"
    VOLATILITY = "volatility"
    BETA = "beta"
    CORRELATION_RISK = "correlation_risk"
    CONCENTRATION_RISK = "concentration_risk"
    LIQUIDITY_RISK = "liquidity_risk"


@dataclass(frozen=True, slots=True)
class VaRResult:
    """Value at Risk calculation result."""
    confidence_level: float  # e.g., 0.95 for 95% VaR
    var_amount: float  # Absolute VaR amount
    var_percentage: float  # VaR as percentage of portfolio value
    method: str  # Calculation method used
    time_horizon_days: int
    timestamp_ns: int


@dataclass(frozen=True, slots=True)
class CVaRResult:
    """Conditional Value at Risk calculation result."""
    confidence_level: float  # e.g., 0.95 for 95% CVaR
    cvar_amount: float  # Expected loss beyond VaR
    cvar_percentage: float  # CVaR as percentage of portfolio value
    var_amount: float  # Corresponding VaR
    expected_shortfall: float  # Average loss in worst cases
    timestamp_ns: int


@dataclass(frozen=True, slots=True)
class StressTestResult:
    """Stress test result."""
    scenario_name: str
    scenario_description: str
    portfolio_value_before: float
    portfolio_value_after: float
    percentage_change: float
    worst_asset: str
    worst_asset_change: float
    best_asset: str
    best_asset_change: float
    risk_contributions: dict[str, float]
    timestamp_ns: int


@dataclass(frozen=True, slots=True)
class RiskBudget:
    """Risk budget allocation for portfolio."""
    total_risk_budget: float
    asset_risk_budgets: dict[str, float]  # Risk allocated to each asset
    strategy_risk_budgets: dict[str, float]  # Risk allocated to each strategy
    current_risk_utilization: float  # Current risk usage as percentage
    risk_adjusted_returns: dict[str, float]
    diversification_benefit: float
    timestamp_ns: int


class AdvancedRiskCalculator:
    """Advanced risk calculator for portfolio risk management.
    
    Calculates VaR, CVaR, stress tests, and provides real-time risk monitoring.
    """
    
    def __init__(
        self,
        default_confidence_level: float = 0.95,
        default_time_horizon: int = 10
    ) -> None:
        self._default_confidence = default_confidence_level
        self._default_horizon = default_time_horizon
        
        self._return_history: dict[str, deque[float]] = {}
        self._risk_history: deque[dict[str, Any]] = deque(maxlen=100)
        
    def update_returns(self, asset: str, return_value: float) -> None:
        """Update return history for an asset."""
        if asset not in self._return_history:
            self._return_history[asset] = deque(maxlen=252)  # 1 year of daily returns
        
        self._return_history[asset].append(return_value)
    
    def calculate_var(
        self,
        portfolio_value: float,
        asset_weights: dict[str, float],
        confidence_level: float | None = None,
        time_horizon_days: int | None = None,
        timestamp_ns: int = 0
    ) -> VaRResult:
        """Calculate Value at Risk for portfolio.
        
        Args:
            portfolio_value: Current portfolio value
            asset_weights: Current asset weights
            confidence_level: Confidence level (e.g., 0.95)
            time_horizon_days: Time horizon in days
            timestamp_ns: Current timestamp
            
        Returns:
            VaR calculation result
        """
        confidence = confidence_level or self._default_confidence
        horizon = time_horizon_days or self._default_horizon
        
        # Calculate portfolio returns from asset returns
        portfolio_returns = self._calculate_portfolio_returns(asset_weights)
        
        if len(portfolio_returns) < 30:
            # Not enough data - use historical volatility approximation
            return self._var_approximation(portfolio_value, confidence, horizon, timestamp_ns)
        
        # Calculate VaR using historical simulation
        sorted_returns = sorted(portfolio_returns)
        
        # Find the percentile corresponding to (1 - confidence)
        var_index = int((1 - confidence) * len(sorted_returns))
        var_return = sorted_returns[var_index] if var_index < len(sorted_returns) else sorted_returns[-1]
        
        var_amount = abs(var_return) * portfolio_value
        var_percentage = abs(var_return)
        
        # Scale to time horizon (square root of time rule)
        scaling_factor = math.sqrt(horizon)
        scaled_var_amount = var_amount * scaling_factor
        scaled_var_percentage = var_percentage * scaling_factor
        
        return VaRResult(
            confidence_level=confidence,
            var_amount=scaled_var_amount,
            var_percentage=scaled_var_percentage,
            method="historical_simulation",
            time_horizon_days=horizon,
            timestamp_ns=timestamp_ns
        )
    
    def calculate_cvar(
        self,
        portfolio_value: float,
        asset_weights: dict[str, float],
        confidence_level: float | None = None,
        timestamp_ns: int = 0
    ) -> CVaRResult:
        """Calculate Conditional Value at Risk (Expected Shortfall).
        
        Args:
            portfolio_value: Current portfolio value
            asset_weights: Current asset weights
            confidence_level: Confidence level (e.g., 0.95)
            timestamp_ns: Current timestamp
            
        Returns:
            CVaR calculation result
        """
        confidence = confidence_level or self._default_confidence
        
        # Calculate portfolio returns
        portfolio_returns = self._calculate_portfolio_returns(asset_weights)
        
        if len(portfolio_returns) < 30:
            # Not enough data - use approximation
            var_result = self.calculate_var(portfolio_value, asset_weights, confidence, 1, timestamp_ns)
            return CVaRResult(
                confidence_level=confidence,
                cvar_amount=var_result.var_amount * 1.2,  # CVaR typically 20% higher than VaR
                cvar_percentage=var_result.var_percentage * 1.2,
                var_amount=var_result.var_amount,
                expected_shortfall=var_result.var_amount * 1.2,
                timestamp_ns=timestamp_ns
            )
        
        # Calculate VaR first
        var_result = self.calculate_var(portfolio_value, asset_weights, confidence, 1, timestamp_ns)
        
        # Calculate average loss in worst (1 - confidence) cases
        sorted_returns = sorted(portfolio_returns)
        tail_losses = [r for r in sorted_returns if r <= -var_result.var_percentage]
        
        if tail_losses:
            expected_shortfall = abs(sum(tail_losses) / len(tail_losses))
        else:
            expected_shortfall = var_result.var_percentage * 1.1  # Conservative fallback
        
        cvar_amount = expected_shortfall * portfolio_value
        cvar_percentage = expected_shortfall
        
        return CVaRResult(
            confidence_level=confidence,
            cvar_amount=cvar_amount,
            cvar_percentage=cvar_percentage,
            var_amount=var_result.var_amount,
            expected_shortfall=expected_shortfall,
            timestamp_ns=timestamp_ns
        )
    
    def run_stress_test(
        self,
        portfolio_value: float,
        asset_weights: dict[str, float],
        scenario_name: str,
        scenario_shocks: dict[str, float],
        scenario_description: str = "",
        timestamp_ns: int = 0
    ) -> StressTestResult:
        """Run stress test with specified scenario.
        
        Args:
            portfolio_value: Current portfolio value
            asset_weights: Current asset weights
            scenario_name: Name of stress scenario
            scenario_shocks: Asset -> shock percentage (e.g., {"BTC": -0.3, "ETH": -0.25})
            scenario_description: Description of scenario
            timestamp_ns: Current timestamp
            
        Returns:
            Stress test result
        """
        # Calculate scenario impact
        portfolio_change = 0.0
        asset_changes = {}
        risk_contributions = {}
        
        for asset, weight in asset_weights.items():
            shock = scenario_shocks.get(asset, 0.0)
            asset_value = portfolio_value * weight
            asset_change = asset_value * shock
            asset_changes[asset] = asset_change
            portfolio_change += asset_change
            
            # Risk contribution = weight * shock^2 (simplified)
            risk_contributions[asset] = abs(weight * shock * shock)
        
        portfolio_value_after = portfolio_value + portfolio_change
        percentage_change = portfolio_change / portfolio_value if portfolio_value > 0 else 0.0
        
        # Find best and worst performers
        sorted_changes = sorted(asset_changes.items(), key=lambda x: x[1])
        worst_asset = sorted_changes[0][0] if sorted_changes else "N/A"
        worst_asset_change = sorted_changes[0][1] / (portfolio_value * asset_weights.get(worst_asset, 1)) if sorted_changes and portfolio_value > 0 else 0.0
        best_asset = sorted_changes[-1][0] if sorted_changes else "N/A"
        best_asset_change = sorted_changes[-1][1] / (portfolio_value * asset_weights.get(best_asset, 1)) if sorted_changes and portfolio_value > 0 else 0.0
        
        return StressTestResult(
            scenario_name=scenario_name,
            scenario_description=scenario_description,
            portfolio_value_before=portfolio_value,
            portfolio_value_after=portfolio_value_after,
            percentage_change=percentage_change,
            worst_asset=worst_asset,
            worst_asset_change=worst_asset_change,
            best_asset=best_asset,
            best_asset_change=best_asset_change,
            risk_contributions=risk_contributions,
            timestamp_ns=timestamp_ns
        )
    
    def _calculate_portfolio_returns(self, asset_weights: dict[str, float]) -> list[float]:
        """Calculate weighted portfolio returns from asset returns."""
        portfolio_returns = []
        
        # Get minimum length across all assets
        min_length = min(
            len(self._return_history.get(asset, []))
            for asset in asset_weights.keys()
        ) if self._return_history else 0
        
        if min_length < 2:
            return []
        
        # Calculate weighted returns for each time period
        for i in range(min_length):
            weighted_return = 0.0
            for asset, weight in asset_weights.items():
                if asset in self._return_history:
                    asset_returns = list(self._return_history[asset])
                    if i < len(asset_returns):
                        weighted_return += asset_returns[i] * weight
            
            portfolio_returns.append(weighted_return)
        
        return portfolio_returns
    
    def _var_approximation(
        self,
        portfolio_value: float,
        confidence_level: float,
        time_horizon_days: int,
        timestamp_ns: int
    ) -> VaRResult:
        """VaR approximation when insufficient historical data."""
        # Use conservative 2% daily volatility approximation
        daily_vol = 0.02
        z_score = 1.96  # Approximate for 95% confidence
        
        var_percentage = z_score * daily_vol
        scaling_factor = math.sqrt(time_horizon_days)
        scaled_var_percentage = var_percentage * scaling_factor
        
        var_amount = scaled_var_percentage * portfolio_value
        
        return VaRResult(
            confidence_level=confidence_level,
            var_amount=var_amount,
            var_percentage=scaled_var_percentage,
            method="approximation",
            time_horizon_days=time_horizon_days,
            timestamp_ns=timestamp_ns
        )


class DynamicRiskBudgeter:
    """Dynamic risk budgeting for portfolio optimization.
    
    Allocates risk budgets across assets and strategies based on
    their risk contributions and expected returns.
    """
    
    def __init__(
        self,
        total_risk_budget: float = 0.15,  # 15% total risk budget (e.g., max portfolio VaR)
        min_diversification_benefit: float = 0.1  # Minimum diversification benefit
    ) -> None:
        self._total_risk_budget = total_risk_budget
        self._min_diversification = min_diversification_benefit
        
        self._current_budget: RiskBudget | None = None
        self._budget_history: deque[RiskBudget] = deque(maxlen=20)
        
    def allocate_risk_budget(
        self,
        portfolio_value: float,
        asset_weights: dict[str, float],
        asset_volatilities: dict[str, float],
        asset_correlations: dict[tuple[str, str], float],
        strategy_weights: dict[str, float],
        expected_returns: dict[str, float],
        timestamp_ns: int = 0
    ) -> RiskBudget:
        """Allocate risk budget across assets and strategies.
        
        Args:
            portfolio_value: Current portfolio value
            asset_weights: Current asset weights
            asset_volatilities: Asset volatilities
            asset_correlations: Correlation matrix
            strategy_weights: Strategy weights
            expected_returns: Expected returns
            timestamp_ns: Current timestamp
            
        Returns:
            Risk budget allocation
        """
        # Calculate asset-level risk budgets based on volatility
        total_volatility_risk = sum(
            asset_weights.get(asset, 0) * vol
            for asset, vol in asset_volatilities.items()
        )
        
        asset_risk_budgets = {}
        for asset, weight in asset_weights.items():
            vol = asset_volatilities.get(asset, 0.15)  # Default 15% vol
            risk_contribution = (weight * vol) / total_volatility_risk if total_volatility_risk > 0 else 0
            asset_risk_budgets[asset] = risk_contribution * self._total_risk_budget
        
        # Calculate strategy-level risk budgets
        strategy_risk_budgets = {}
        for strategy, weight in strategy_weights.items():
            strategy_risk_budgets[strategy] = weight * self._total_risk_budget
        
        # Calculate diversification benefit
        diversification_benefit = self._calculate_diversification_benefit(
            asset_weights, asset_correlations
        )
        
        # Calculate risk-adjusted returns
        risk_adjusted_returns = {}
        for asset, expected_return in expected_returns.items():
            vol = asset_volatilities.get(asset, 0.15)
            risk_adjusted_returns[asset] = expected_return / vol if vol > 0 else expected_return
        
        # Calculate current risk utilization
        current_risk = self._calculate_portfolio_risk(
            asset_weights, asset_volatilities, asset_correlations
        )
        risk_utilization = current_risk / self._total_risk_budget if self._total_risk_budget > 0 else 1.0
        
        risk_budget = RiskBudget(
            total_risk_budget=self._total_risk_budget,
            asset_risk_budgets=asset_risk_budgets,
            strategy_risk_budgets=strategy_risk_budgets,
            current_risk_utilization=min(1.0, risk_utilization),
            risk_adjusted_returns=risk_adjusted_returns,
            diversification_benefit=diversification_benefit,
            timestamp_ns=timestamp_ns
        )
        
        self._current_budget = risk_budget
        self._budget_history.append(risk_budget)
        
        return risk_budget
    
    def _calculate_diversification_benefit(
        self,
        asset_weights: dict[str, float],
        asset_correlations: dict[tuple[str, str], float]
    ) -> float:
        """Calculate diversification benefit from correlation structure."""
        assets = list(asset_weights.keys())
        if len(assets) < 2:
            return 0.0
        
        # Calculate average correlation
        correlations = []
        for i, asset_a in enumerate(assets):
            for asset_b in assets[i+1:]:
                key = (min(asset_a, asset_b), max(asset_a, asset_b))
                if key in asset_correlations:
                    correlations.append(abs(asset_correlations[key]))
        
        if not correlations:
            return 0.0
        
        avg_correlation = sum(correlations) / len(correlations)
        
        # Diversification benefit = 1 - average correlation
        diversification_benefit = 1.0 - avg_correlation
        
        return diversification_benefit
    
    def _calculate_portfolio_risk(
        self,
        asset_weights: dict[str, float],
        asset_volatilities: dict[str, float],
        asset_correlations: dict[tuple[str, str], float]
    ) -> float:
        """Calculate portfolio risk using covariance matrix."""
        assets = list(asset_weights.keys())
        portfolio_variance = 0.0
        
        for i, asset_a in enumerate(assets):
            weight_a = asset_weights.get(asset_a, 0)
            vol_a = asset_volatilities.get(asset_a, 0.15)
            
            # Diagonal term
            portfolio_variance += (weight_a * vol_a) ** 2
            
            # Off-diagonal terms
            for asset_b in assets[i+1:]:
                weight_b = asset_weights.get(asset_b, 0)
                vol_b = asset_volatilities.get(asset_b, 0.15)
                
                key = (min(asset_a, asset_b), max(asset_a, asset_b))
                correlation = asset_correlations.get(key, 0.0)
                
                portfolio_variance += 2 * weight_a * weight_b * vol_a * vol_b * correlation
        
        portfolio_risk = math.sqrt(portfolio_variance)
        
        return portfolio_risk
    
    def get_current_budget(self) -> RiskBudget | None:
        """Get current risk budget."""
        return self._current_budget
    
    def is_risk_budget_exceeded(self) -> bool:
        """Check if current risk utilization exceeds budget."""
        if not self._current_budget:
            return False
        return self._current_budget.current_risk_utilization > 1.0


__all__ = [
    "RiskMetric",
    "VaRResult",
    "CVaRResult",
    "StressTestResult",
    "RiskBudget",
    "AdvancedRiskCalculator",
    "DynamicRiskBudgeter"
]