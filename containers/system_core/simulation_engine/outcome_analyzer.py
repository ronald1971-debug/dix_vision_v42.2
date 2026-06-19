"""
simulation_engine.outcome_analyzer
DIX VISION v42.2 — Production-Grade Outcome Analyzer

Outcome analysis with PnL evaluation, drawdown analysis,
risk assessment, and production-ready outcome metrics.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum

from system.time_source import now

logger = logging.getLogger(__name__)


class AnalysisMetric(Enum):
    """Analysis metrics."""
    TOTAL_PNL = "total_pnl"
    FINAL_PNL = "final_pnl"
    MAX_DRAWDOWN = "max_drawdown"
    SHARPE_RATIO = "sharpe_ratio"
    WIN_RATE = "win_rate"
    AVG_WIN = "avg_win"
    AVG_LOSS = "avg_loss"
    PROFIT_FACTOR = "profit_factor"
    TRADE_COUNT = "trade_count"
    DURATION_HOURS = "duration_hours"
    VOLATILITY = "volatility"
    RISK_REWARD = "risk_reward"


@dataclass
class TradeOutcome:
    """Individual trade outcome."""
    trade_id: str
    entry_price: float
    exit_price: float
    side: str
    pnl: float
    duration_bars: int
    max_adverse_excursion: float = 0.0
    max_favorable_excursion: float = 0.0


@dataclass
class RiskAnalysis:
    """Risk assessment from simulation."""
    max_drawdown: float = 0.0
    max_drawdown_duration: int = 0
    var_95: float = 0.0  # Value at Risk 95%
    var_99: float = 0.0  # Value at Risk 99%
    expected_shortfall: float = 0.0
    leverage_used: float = 1.0
    margin_usage: float = 0.0


@dataclass
class OutcomeAnalysis:
    """Comprehensive outcome analysis result."""
    analysis_id: str
    simulation_run_id: str
    metrics: Dict[AnalysisMetric, float] = field(default_factory=dict)
    risk_analysis: RiskAnalysis = field(default_factory=RiskAnalysis)
    trade_outcomes: List[TradeOutcome] = field(default_factory=list)
    insights: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    timestamp: str = ""


class ProductionOutcomeAnalyzer:
    """Production-grade outcome analyzer.
    
    Analyzes simulation outcomes including:
    - PnL metrics (total, final, by trade)
    - Drawdown analysis (max drawdown, duration)
    - Risk metrics (Sharpe, VaR, Expected Shortfall)
    - Trade quality (win rate, profit factor)
    - Performance insights
    """
    
    def __init__(self) -> None:
        self._analyses: List[OutcomeAnalysis] = []
        
    def start(self) -> bool:
        logger.info("[OUTCOME_ANALYZER] Production outcome analyzer started")
        return True
    
    def stop(self) -> bool:
        logger.info("[OUTCOME_ANALYZER] Production outcome analyzer stopped")
        return True
    
    def analyze_outcome(
        self,
        simulation_run_id: str,
        results: Dict[str, Any]
    ) -> OutcomeAnalysis:
        """Analyze simulation outcome comprehensively.
        
        Args:
            simulation_run_id: ID of the simulation run
            results: Dictionary containing simulation results including:
                - trades: list of trade data
                - equity_curve: list of equity values over time
                - returns: list of returns
                - risk_free_rate: risk-free rate for Sharpe calculation
        """
        analysis_id = f"analysis_{now().sequence}"
        
        # Extract data from results
        trades = results.get("trades", [])
        equity_curve = results.get("equity_curve", [])
        returns = results.get("returns", [])
        risk_free_rate = results.get("risk_free_rate", 0.02)
        
        # Calculate metrics
        metrics = {}
        
        if equity_curve:
            initial_equity = equity_curve[0] if equity_curve else 100000
            final_equity = equity_curve[-1] if equity_curve else initial_equity
            total_pnl = final_equity - initial_equity
            pnl_pct = (total_pnl / initial_equity) * 100
            
            metrics[AnalysisMetric.TOTAL_PNL] = total_pnl
            metrics[AnalysisMetric.FINAL_PNL] = pnl_pct
        
        if returns:
            metrics[AnalysisMetric.VOLATILITY] = self._calculate_volatility(returns)
            metrics[AnalysisMetric.SHARPE_RATIO] = self._calculate_sharpe(returns, risk_free_rate)
        
        # Trade analysis
        trade_outcomes = []
        if trades:
            for trade in trades:
                trade_outcome = self._analyze_trade(trade)
                trade_outcomes.append(trade_outcome)
            
            # Trade metrics
            wins = [t for t in trade_outcomes if t.pnl > 0]
            losses = [t for t in trade_outcomes if t.pnl < 0]
            
            if trade_outcomes:
                metrics[AnalysisMetric.TRADE_COUNT] = len(trade_outcomes)
                metrics[AnalysisMetric.WIN_RATE] = len(wins) / len(trade_outcomes) if trade_outcomes else 0
                metrics[AnalysisMetric.AVG_WIN] = sum(t.pnl for t in wins) / len(wins) if wins else 0
                metrics[AnalysisMetric.AVG_LOSS] = sum(t.pnl for t in losses) / len(losses) if losses else 0
                metrics[AnalysisMetric.PROFIT_FACTOR] = abs(sum(t.pnl for t in wins) / sum(t.pnl for t in losses)) if losses else 0
        
        # Drawdown analysis
        risk_analysis = self._analyze_risk(equity_curve, results)
        metrics[AnalysisMetric.MAX_DRAWDOWN] = risk_analysis.max_drawdown
        metrics[AnalysisMetric.RISK_REWARD] = self._calculate_risk_reward(trade_outcomes)
        
        # Generate insights
        insights = self._generate_insights(metrics, risk_analysis, trade_outcomes)
        recommendations = self._generate_recommendations(metrics, risk_analysis)
        
        analysis = OutcomeAnalysis(
            analysis_id=analysis_id,
            simulation_run_id=simulation_run_id,
            metrics=metrics,
            risk_analysis=risk_analysis,
            trade_outcomes=trade_outcomes,
            insights=insights,
            recommendations=recommendations,
            timestamp=now().utc_time.isoformat()
        )
        
        self._analyses.append(analysis)
        logger.info(f"[OUTCOME_ANALYZER] Analyzed outcome: {analysis_id} with {len(insights)} insights")
        return analysis
    
    def _analyze_trade(self, trade: Dict[str, Any]) -> TradeOutcome:
        """Analyze individual trade outcome."""
        return TradeOutcome(
            trade_id=trade.get("trade_id", ""),
            entry_price=trade.get("entry_price", 0.0),
            exit_price=trade.get("exit_price", 0.0),
            side=trade.get("side", ""),
            pnl=trade.get("pnl", 0.0),
            duration_bars=trade.get("duration_bars", 0),
            max_adverse_excursion=trade.get("max_adverse_excursion", 0.0),
            max_favorable_excursion=trade.get("max_favorable_excursion", 0.0)
        )
    
    def _analyze_risk(self, equity_curve: List[float], results: Dict[str, Any]) -> RiskAnalysis:
        """Analyze risk metrics."""
        if not equity_curve:
            return RiskAnalysis()
        
        # Calculate drawdown
        drawdowns = self._calculate_drawdowns(equity_curve)
        max_drawdown = min(drawdowns) if drawdowns else 0.0
        
        # Find drawdown duration
        max_dd_duration = self._calculate_max_drawdown_duration(equity_curve)
        
        # Calculate VaR
        returns = results.get("returns", [])
        var_95 = self._calculate_var(returns, 0.95) if returns else 0.0
        var_99 = self._calculate_var(returns, 0.99) if returns else 0.0
        expected_shortfall = self._calculate_expected_shortfall(returns, var_95) if returns else 0.0
        
        return RiskAnalysis(
            max_drawdown=abs(max_drawdown),
            max_drawdown_duration=max_dd_duration,
            var_95=var_95,
            var_99=var_99,
            expected_shortfall=expected_shortfall,
            leverage_used=results.get("leverage_used", 1.0),
            margin_usage=results.get("margin_usage", 0.0)
        )
    
    def _calculate_volatility(self, returns: List[float]) -> float:
        """Calculate volatility of returns."""
        if len(returns) < 2:
            return 0.0
        import statistics
        return statistics.stdev(returns) if len(returns) > 1 else 0.0
    
    def _calculate_sharpe(self, returns: List[float], risk_free_rate: float) -> float:
        """Calculate Sharpe ratio."""
        if len(returns) < 2:
            return 0.0
        import statistics
        mean_return = statistics.mean(returns)
        std_return = statistics.stdev(returns)
        if std_return == 0:
            return 0.0
        return (mean_return - risk_free_rate) / std_return
    
    def _calculate_drawdowns(self, equity_curve: List[float]) -> List[float]:
        """Calculate drawdown at each point."""
        if not equity_curve:
            return []
        
        peak = equity_curve[0]
        drawdowns = []
        
        for equity in equity_curve:
            if equity > peak:
                peak = equity
            dd = (equity - peak) / peak
            drawdowns.append(dd)
        
        return drawdowns
    
    def _calculate_max_drawdown_duration(self, equity_curve: List[float]) -> int:
        """Calculate maximum drawdown duration in bars."""
        if not equity_curve:
            return 0
        
        peak = equity_curve[0]
        peak_idx = 0
        max_duration = 0
        
        for i, equity in enumerate(equity_curve):
            if equity > peak:
                peak = equity
                peak_idx = i
            else:
                duration = i - peak_idx
                if duration > max_duration:
                    max_duration = duration
        
        return max_duration
    
    def _calculate_var(self, returns: List[float], confidence: float) -> float:
        """Calculate Value at Risk."""
        if not returns:
            return 0.0
        import statistics
        sorted_returns = sorted(returns)
        index = int(len(sorted_returns) * (1 - confidence))
        return abs(sorted_returns[index]) if index < len(sorted_returns) else 0.0
    
    def _calculate_expected_shortfall(self, returns: List[float], var: float) -> float:
        """Calculate Expected Shortfall (average loss beyond VaR)."""
        if not returns:
            return 0.0
        beyond_var = [r for r in returns if r < -var]
        if not beyond_var:
            return 0.0
        import statistics
        return abs(statistics.mean(beyond_var))
    
    def _calculate_risk_reward(self, trade_outcomes: List[TradeOutcome]) -> float:
        """Calculate risk-reward ratio."""
        if not trade_outcomes:
            return 0.0
        
        total_risk = sum(abs(t.max_adverse_excursion) for t in trade_outcomes if t.max_adverse_excursion > 0)
        total_reward = sum(t.pnl for t in trade_outcomes if t.pnl > 0)
        
        return total_reward / total_risk if total_risk > 0 else 0.0
    
    def _generate_insights(
        self,
        metrics: Dict[AnalysisMetric, float],
        risk_analysis: RiskAnalysis,
        trade_outcomes: List[TradeOutcome]
    ) -> List[str]:
        """Generate insights from analysis."""
        insights = []
        
        # PnL insight
        if AnalysisMetric.FINAL_PNL in metrics:
            pnl = metrics[AnalysisMetric.FINAL_PNL]
            if pnl > 0:
                insights.append(f"Simulation profitable: +{pnl:.2f}%")
            else:
                insights.append(f"Simulation unprofitable: {pnl:.2f}%")
        
        # Drawdown insight
        if risk_analysis.max_drawdown > 0.2:
            insights.append(f"High drawdown detected: {risk_analysis.max_drawdown:.2%}")
        
        # Win rate insight
        if AnalysisMetric.WIN_RATE in metrics:
            win_rate = metrics[AnalysisMetric.WIN_RATE]
            if win_rate > 0.6:
                insights.append(f"Strong win rate: {win_rate:.2%}")
            elif win_rate < 0.4:
                insights.append(f"Weak win rate: {win_rate:.2%}")
        
        # Sharpe insight
        if AnalysisMetric.SHARPE_RATIO in metrics:
            sharpe = metrics[AnalysisMetric.SHARPE_RATIO]
            if sharpe > 1.0:
                insights.append(f"Good risk-adjusted returns (Sharpe: {sharpe:.2f})")
            elif sharpe < 0.5:
                insights.append(f"Poor risk-adjusted returns (Sharpe: {sharpe:.2f})")
        
        return insights
    
    def _generate_recommendations(
        self,
        metrics: Dict[AnalysisMetric, float],
        risk_analysis: RiskAnalysis
    ) -> List[str]:
        """Generate recommendations based on analysis."""
        recommendations = []
        
        if risk_analysis.max_drawdown > 0.15:
            recommendations.append("Consider reducing position sizes to limit drawdown")
        
        if risk_analysis.leverage_used > 2.0:
            recommendations.append("High leverage detected - consider reducing exposure")
        
        if AnalysisMetric.PROFIT_FACTOR in metrics and metrics[AnalysisMetric.PROFIT_FACTOR] < 1.5:
            recommendations.append("Improve risk-reward ratio by tightening stop losses or letting winners run")
        
        if AnalysisMetric.SHARPE_RATIO in metrics and metrics[AnalysisMetric.SHARPE_RATIO] < 0.5:
            recommendations.append("Improve risk-adjusted returns by reducing volatility or increasing consistency")
        
        return recommendations


def get_production_outcome_analyzer() -> ProductionOutcomeAnalyzer:
    """Get the singleton production outcome analyzer instance."""
    if not hasattr(get_production_outcome_analyzer, "_instance"):
        get_production_outcome_analyzer._instance = ProductionOutcomeAnalyzer()
    return get_production_outcome_analyzer._instance