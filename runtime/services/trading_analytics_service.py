"""
DIX VISION Trading Performance Analytics Service

Provides real-time P&L attribution, strategy performance comparison, 
regime-based analysis, risk-adjusted returns, and drawdown analysis.
"""

from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple
from collections import defaultdict, deque
from datetime import datetime, timedelta
import statistics

from runtime.event_bus import EventBus, Event, EventType, get_event_bus
from runtime.service_manager import Service, ServiceState, ServiceHealth

logger = logging.getLogger(__name__)


class MarketRegime(Enum):
    """Market regimes for analysis."""
    BULL_TREND = "bull_trend"
    BEAR_TREND = "bear_trend"
    SIDEWAYS = "sideways"
    HIGH_VOLATILITY = "high_volatility"
    LOW_VOLATILITY = "low_volatility"


@dataclass
class Trade:
    """Trade record for analytics."""
    trade_id: str
    symbol: str
    direction: str  # "long" or "short"
    entry_price: float
    exit_price: float
    quantity: float
    entry_time: float
    exit_time: float
    strategy: str
    regime: MarketRegime = MarketRegime.SIDEWAYS
    
    @property
    def pnl(self) -> float:
        """Calculate P&L."""
        if self.direction == "long":
            return (self.exit_price - self.entry_price) * self.quantity
        else:
            return (self.entry_price - self.exit_price) * self.quantity
    
    @property
    def pnl_pct(self) -> float:
        """Calculate P&L percentage."""
        if self.direction == "long":
            return (self.exit_price - self.entry_price) / self.entry_price
        else:
            return (self.entry_price - self.exit_price) / self.entry_price
    
    @property
    def duration(self) -> float:
        """Calculate trade duration in seconds."""
        return self.exit_time - self.entry_time


@dataclass
class StrategyPerformance:
    """Strategy performance metrics."""
    strategy_name: str
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    total_pnl: float = 0.0
    total_pnl_pct: float = 0.0
    win_rate: float = 0.0
    avg_win: float = 0.0
    avg_loss: float = 0.0
    profit_factor: float = 0.0
    max_drawdown: float = 0.0
    sharpe_ratio: float = 0.0
    sortino_ratio: float = 0.0
    calmar_ratio: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "strategy_name": self.strategy_name,
            "total_trades": self.total_trades,
            "winning_trades": self.winning_trades,
            "losing_trades": self.losing_trades,
            "total_pnl": self.total_pnl,
            "total_pnl_pct": self.total_pnl_pct,
            "win_rate": self.win_rate,
            "avg_win": self.avg_win,
            "avg_loss": self.avg_loss,
            "profit_factor": self.profit_factor,
            "max_drawdown": self.max_drawdown,
            "sharpe_ratio": self.sharpe_ratio,
            "sortino_ratio": self.sortino_ratio,
            "calmar_ratio": self.calmar_ratio
        }


@dataclass
class RegimePerformance:
    """Performance by market regime."""
    regime: MarketRegime
    total_trades: int = 0
    total_pnl: float = 0.0
    win_rate: float = 0.0
    avg_pnl: float = 0.0
    volatility: float = 0.0


class TradingAnalyticsService(Service):
    """Trading performance analytics service as per Runtime Specification."""
    
    # Service dependencies
    DEPENDENCIES = []
    
    def __init__(self):
        super().__init__("trading_analytics_service")
        self._trades: List[Trade] = []
        self._strategy_performance: Dict[str, StrategyPerformance] = {}
        self._regime_performance: Dict[MarketRegime, RegimePerformance] = {}
        self._equity_curve: List[Tuple[float, float]] = []  # (timestamp, equity)
        self._drawdown_curve: List[Tuple[float, float]] = []  # (timestamp, drawdown)
        self._lock = threading.Lock()
        self._initial_capital: float = 100000.0
        self._current_equity: float = 100000.0
        self._peak_equity: float = 100000.0
        self._risk_free_rate: float = 0.02  # 2% annual
        
    def init(self, event_bus: EventBus, config: Dict[str, Any]) -> bool:
        """Initialize the trading analytics service."""
        try:
            self.event_bus = event_bus
            self.state = ServiceState.INITIALIZING
            
            # Load configuration
            analytics_config = config.get("trading_analytics", {})
            self._initial_capital = analytics_config.get("initial_capital", 100000.0)
            self._current_equity = self._initial_capital
            self._peak_equity = self._initial_capital
            self._risk_free_rate = analytics_config.get("risk_free_rate", 0.02)
            
            # Initialize regime performance
            for regime in MarketRegime:
                self._regime_performance[regime] = RegimePerformance(regime=regime)
            
            logger.info("Trading Analytics Service initialized")
            return True
        except Exception as e:
            logger.error(f"Trading Analytics Service initialization failed: {e}")
            self.state = ServiceState.ERROR
            return False
    
    def start(self) -> bool:
        """Start the trading analytics service."""
        try:
            self.state = ServiceState.STARTING
            
            # Start background analytics updater
            self._start_analytics_updater()
            
            self.state = ServiceState.RUNNING
            self.emit_event(str(EventType.SERVICE_START), {"service": self.name})
            logger.info("Trading Analytics Service started")
            return True
        except Exception as e:
            logger.error(f"Trading Analytics Service start failed: {e}")
            self.state = ServiceState.ERROR
            self.emit_event(str(EventType.SERVICE_CRASH), {"service": self.name, "error": str(e)})
            return False
    
    def stop(self) -> bool:
        """Stop the trading analytics service."""
        try:
            self.state = ServiceState.STOPPING
            self.state = ServiceState.STOPPED
            self.emit_event(str(EventType.SERVICE_STOP), {"service": self.name})
            logger.info("Trading Analytics Service stopped")
            return True
        except Exception as e:
            logger.error(f"Trading Analytics Service stop failed: {e}")
            self.state = ServiceState.ERROR
            return False
    
    def health(self) -> ServiceHealth:
        """Get trading analytics service health."""
        return ServiceHealth(
            service=self.name,
            state=self.state,
            healthy=self.state == ServiceState.RUNNING,
            message=f"Trading Analytics Service - {len(self._trades)} trades analyzed",
            details={
                "total_trades": len(self._trades),
                "strategies_tracked": len(self._strategy_performance),
                "current_equity": self._current_equity,
                "total_return": (self._current_equity - self._initial_capital) / self._initial_capital,
                "max_drawdown": self._calculate_max_drawdown(),
                "strategies": list(self._strategy_performance.keys())
            },
            timestamp=time.time()
        )
    
    def add_trade(self, trade: Trade) -> None:
        """Add a trade record."""
        with self._lock:
            self._trades.append(trade)
            
            # Update equity curve
            self._current_equity += trade.pnl
            self._equity_curve.append((trade.exit_time, self._current_equity))
            
            # Update peak equity
            if self._current_equity > self._peak_equity:
                self._peak_equity = self._current_equity
            
            # Update drawdown curve
            drawdown = (self._peak_equity - self._current_equity) / self._peak_equity
            self._drawdown_curve.append((trade.exit_time, drawdown))
            
            # Update strategy performance
            if trade.strategy not in self._strategy_performance:
                self._strategy_performance[trade.strategy] = StrategyPerformance(strategy_name=trade.strategy)
            
            self._update_strategy_performance(trade)
            
            # Update regime performance
            self._update_regime_performance(trade)
            
            logger.info(f"Trade added: {trade.trade_id}, P&L: {trade.pnl:.2f}")
    
    def get_strategy_performance(self, strategy_name: str) -> Optional[StrategyPerformance]:
        """Get performance metrics for a specific strategy."""
        with self._lock:
            return self._strategy_performance.get(strategy_name)
    
    def get_all_strategy_performance(self) -> Dict[str, StrategyPerformance]:
        """Get performance metrics for all strategies."""
        with self._lock:
            return dict(self._strategy_performance)
    
    def compare_strategies(self, strategy_names: List[str]) -> Dict[str, Dict[str, Any]]:
        """Compare performance of multiple strategies."""
        with self._lock:
            comparison = {}
            
            for strategy_name in strategy_names:
                performance = self._strategy_performance.get(strategy_name)
                if performance:
                    comparison[strategy_name] = performance.to_dict()
            
            return comparison
    
    def get_regime_performance(self, regime: MarketRegime) -> Optional[RegimePerformance]:
        """Get performance for a specific market regime."""
        with self._lock:
            return self._regime_performance.get(regime)
    
    def get_all_regime_performance(self) -> Dict[MarketRegime, RegimePerformance]:
        """Get performance for all market regimes."""
        with self._lock:
            return dict(self._regime_performance)
    
    def get_equity_curve(self) -> List[Tuple[float, float]]:
        """Get equity curve data."""
        with self._lock:
            return list(self._equity_curve)
    
    def get_drawdown_curve(self) -> List[Tuple[float, float]]:
        """Get drawdown curve data."""
        with self._lock:
            return list(self._drawdown_curve)
    
    def calculate_returns(self, period: str = "daily") -> List[float]:
        """Calculate returns for a specific period."""
        with self._lock:
            if not self._equity_curve:
                return []
            
            # Group by period
            period_seconds = {
                "hourly": 3600,
                "daily": 86400,
                "weekly": 604800,
                "monthly": 2592000
            }.get(period, 86400)
            
            returns = []
            prev_equity = self._initial_capital
            prev_time = self._equity_curve[0][0] if self._equity_curve else time.time()
            
            for timestamp, equity in self._equity_curve:
                if timestamp - prev_time >= period_seconds:
                    ret = (equity - prev_equity) / prev_equity
                    returns.append(ret)
                    prev_equity = equity
                    prev_time = timestamp
            
            return returns
    
    def calculate_risk_metrics(self) -> Dict[str, float]:
        """Calculate comprehensive risk metrics."""
        with self._lock:
            if not self._trades:
                return {}
            
            returns = self.calculate_returns("daily")
            if not returns:
                return {}
            
            # Calculate metrics
            total_return = (self._current_equity - self._initial_capital) / self._initial_capital
            max_drawdown = self._calculate_max_drawdown()
            
            # Sharpe ratio
            if len(returns) > 1:
                excess_returns = [r - self._risk_free_rate / 252 for r in returns]  # Daily risk-free rate
                sharpe = statistics.mean(excess_returns) / statistics.stdev(excess_returns) if statistics.stdev(excess_returns) > 0 else 0.0
            else:
                sharpe = 0.0
            
            # Sortino ratio
            negative_returns = [r for r in returns if r < 0]
            if len(negative_returns) > 1:
                downside_deviation = statistics.stdev(negative_returns)
                sortino = statistics.mean(returns) / downside_deviation if downside_deviation > 0 else 0.0
            else:
                sortino = 0.0
            
            # Calmar ratio
            calmar = total_return / abs(max_drawdown) if max_drawdown != 0 else 0.0
            
            return {
                "total_return": total_return,
                "annualized_return": total_return * 252,  # Assuming daily returns
                "max_drawdown": max_drawdown,
                "sharpe_ratio": sharpe,
                "sortino_ratio": sortino,
                "calmar_ratio": calmar,
                "win_rate": sum(1 for t in self._trades if t.pnl > 0) / len(self._trades),
                "profit_factor": self._calculate_profit_factor(),
                "avg_trade": statistics.mean([t.pnl for t in self._trades])
            }
    
    def get_trade_attribution(self, trade_id: str) -> Dict[str, Any]:
        """Get detailed attribution for a specific trade."""
        with self._lock:
            trade = next((t for t in self._trades if t.trade_id == trade_id), None)
            if not trade:
                return {}
            
            return {
                "trade_id": trade.trade_id,
                "symbol": trade.symbol,
                "direction": trade.direction,
                "pnl": trade.pnl,
                "pnl_pct": trade.pnl_pct,
                "duration_hours": trade.duration / 3600,
                "strategy": trade.strategy,
                "regime": trade.regime.value,
                "entry_time": datetime.fromtimestamp(trade.entry_time).isoformat(),
                "exit_time": datetime.fromtimestamp(trade.exit_time).isoformat()
            }
    
    def get_pnl_attribution(self, start_time: float = None, end_time: float = None) -> Dict[str, Any]:
        """Get P&L attribution for a time period."""
        with self._lock:
            filtered_trades = self._trades
            
            if start_time:
                filtered_trades = [t for t in filtered_trades if t.exit_time >= start_time]
            if end_time:
                filtered_trades = [t for t in filtered_trades if t.exit_time <= end_time]
            
            # Attribute by strategy
            strategy_pnl = defaultdict(float)
            for trade in filtered_trades:
                strategy_pnl[trade.strategy] += trade.pnl
            
            # Attribute by symbol
            symbol_pnl = defaultdict(float)
            for trade in filtered_trades:
                symbol_pnl[trade.symbol] += trade.pnl
            
            # Attribute by regime
            regime_pnl = defaultdict(float)
            for trade in filtered_trades:
                regime_pnl[trade.regime.value] += trade.pnl
            
            return {
                "total_pnl": sum(t.pnl for t in filtered_trades),
                "strategy_attribution": dict(strategy_pnl),
                "symbol_attribution": dict(symbol_pnl),
                "regime_attribution": dict(regime_pnl),
                "trade_count": len(filtered_trades)
            }
    
    def _update_strategy_performance(self, trade: Trade) -> None:
        """Update strategy performance metrics."""
        performance = self._strategy_performance[trade.strategy]
        
        performance.total_trades += 1
        performance.total_pnl += trade.pnl
        performance.total_pnl_pct += trade.pnl_pct
        
        if trade.pnl > 0:
            performance.winning_trades += 1
        else:
            performance.losing_trades += 1
        
        # Calculate win rate
        performance.win_rate = performance.winning_trades / performance.total_trades
        
        # Calculate average win/loss
        wins = [t.pnl for t in self._trades if t.strategy == trade.strategy and t.pnl > 0]
        losses = [t.pnl for t in self._trades if t.strategy == trade.strategy and t.pnl < 0]
        
        performance.avg_win = statistics.mean(wins) if wins else 0.0
        performance.avg_loss = statistics.mean(losses) if losses else 0.0
        
        # Calculate profit factor
        total_wins = sum(wins)
        total_losses = abs(sum(losses))
        performance.profit_factor = total_wins / total_losses if total_losses > 0 else float('inf')
        
        # Calculate Sharpe ratio
        strategy_returns = [t.pnl_pct for t in self._trades if t.strategy == trade.strategy]
        if len(strategy_returns) > 1:
            performance.sharpe_ratio = statistics.mean(strategy_returns) / statistics.stdev(strategy_returns)
        
        # Calculate max drawdown for strategy
        strategy_equity = [self._initial_capital]
        for t in self._trades:
            if t.strategy == trade.strategy:
                strategy_equity.append(strategy_equity[-1] + t.pnl)
        
        peak = max(strategy_equity)
        current = strategy_equity[-1]
        performance.max_drawdown = (peak - current) / peak if peak > 0 else 0.0
    
    def _update_regime_performance(self, trade: Trade) -> None:
        """Update regime performance metrics."""
        performance = self._regime_performance[trade.regime]
        
        performance.total_trades += 1
        performance.total_pnl += trade.pnl
        
        if trade.pnl > 0:
            performance.winning_trades = performance.winning_trades + 1 if hasattr(performance, 'winning_trades') else 1
        
        # Calculate win rate
        if hasattr(performance, 'winning_trades'):
            performance.win_rate = performance.winning_trades / performance.total_trades
        
        # Calculate average P&L
        regime_trades = [t for t in self._trades if t.regime == trade.regime]
        performance.avg_pnl = statistics.mean([t.pnl for t in regime_trades])
        
        # Calculate volatility
        if len(regime_trades) > 1:
            performance.volatility = statistics.stdev([t.pnl for t in regime_trades])
    
    def _calculate_max_drawdown(self) -> float:
        """Calculate maximum drawdown."""
        if not self._equity_curve:
            return 0.0
        
        peak = self._initial_capital
        max_dd = 0.0
        
        for _, equity in self._equity_curve:
            if equity > peak:
                peak = equity
            
            drawdown = (peak - equity) / peak if peak > 0 else 0.0
            if drawdown > max_dd:
                max_dd = drawdown
        
        return max_dd
    
    def _calculate_profit_factor(self) -> float:
        """Calculate overall profit factor."""
        wins = [t.pnl for t in self._trades if t.pnl > 0]
        losses = [t.pnl for t in self._trades if t.pnl < 0]
        
        total_wins = sum(wins)
        total_losses = abs(sum(losses))
        
        return total_wins / total_losses if total_losses > 0 else float('inf')
    
    def _start_analytics_updater(self) -> None:
        """Start background analytics updater."""
        def update_analytics():
            while self.state == ServiceState.RUNNING:
                try:
                    # Recalculate all metrics
                    with self._lock:
                        for strategy_name, performance in self._strategy_performance.items():
                            # Recalculate based on all trades for this strategy
                            strategy_trades = [t for t in self._trades if t.strategy == strategy_name]
                            if strategy_trades:
                                for trade in strategy_trades:
                                    self._update_strategy_performance(trade)
                    
                    time.sleep(300)  # Update every 5 minutes
                except Exception as e:
                    logger.error(f"Analytics update error: {e}")
                    time.sleep(60)
        
        thread = threading.Thread(target=update_analytics, daemon=True)
        thread.start()
        logger.info("Analytics updater started")


# Global instance
_trading_analytics_service: Optional[TradingAnalyticsService] = None


def get_trading_analytics_service() -> TradingAnalyticsService:
    """Get global trading analytics service instance."""
    global _trading_analytics_service
    if _trading_analytics_service is None:
        _trading_analytics_service = TradingAnalyticsService()
    return _trading_analytics_service