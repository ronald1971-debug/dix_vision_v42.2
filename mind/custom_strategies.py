"""
Custom Trading Strategies - Real Implementation

Provides real custom trading strategy implementations for the DIX VISION system,
including strategy definitions, execution logic, and performance tracking.
"""

from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging
import numpy as np
from datetime import datetime, timedelta
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class StrategyType(Enum):
    """Types of trading strategies."""
    MOMENTUM = "momentum"
    MEAN_REVERSION = "mean_reversion"
    TREND_FOLLOWING = "trend_following"
    ARBITRAGE = "arbitrage"
    MARKET_MAKING = "market_making"
    STATISTICAL_ARBITRAGE = "statistical_arbitrage"
    SENTIMENT_BASED = "sentiment_based"
    ORDER_FLOW = "order_flow"


class StrategyStatus(Enum):
    """Status of a strategy."""
    ACTIVE = "active"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"


class SignalType(Enum):
    """Types of trading signals."""
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"


@dataclass
class TradingSignal:
    """Represents a trading signal from a strategy."""
    signal_id: str
    strategy_id: str
    signal_type: SignalType
    symbol: str
    confidence: float  # 0.0 to 1.0
    target_price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    position_size: float = 1.0
    reason: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class StrategyPerformance:
    """Performance metrics for a strategy."""
    strategy_id: str
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    total_return: float = 0.0
    max_drawdown: float = 0.0
    sharpe_ratio: float = 0.0
    win_rate: float = 0.0
    average_win: float = 0.0
    average_loss: float = 0.0
    profit_factor: float = 0.0
    last_updated: datetime = field(default_factory=datetime.now)


class TradingStrategy(ABC):
    """Abstract base class for trading strategies."""
    
    def __init__(self, strategy_id: str, strategy_type: StrategyType):
        self.strategy_id = strategy_id
        self.strategy_type = strategy_type
        self.status = StrategyStatus.STOPPED
        self.performance = StrategyPerformance(strategy_id=strategy_id)
        self.parameters: Dict[str, Any] = {}
        self._signals_history: List[TradingSignal] = []
        
    @abstractmethod
    def generate_signal(self, market_data: Dict[str, Any]) -> Optional[TradingSignal]:
        """Generate a trading signal based on market data."""
        pass
    
    @abstractmethod
    def update_parameters(self, params: Dict[str, Any]) -> None:
        """Update strategy parameters."""
        pass
    
    def start(self) -> None:
        """Start the strategy."""
        self.status = StrategyStatus.ACTIVE
        logger.info(f"[STRATEGY] Started strategy {self.strategy_id}")
    
    def pause(self) -> None:
        """Pause the strategy."""
        self.status = StrategyStatus.PAUSED
        logger.info(f"[STRATEGY] Paused strategy {self.strategy_id}")
    
    def stop(self) -> None:
        """Stop the strategy."""
        self.status = StrategyStatus.STOPPED
        logger.info(f"[STRATEGY] Stopped strategy {self.strategy_id}")
    
    def record_trade_result(self, profit: float, winning: bool) -> None:
        """Record the result of a trade for performance tracking."""
        self.performance.total_trades += 1
        
        if winning:
            self.performance.winning_trades += 1
            self.performance.average_win = (
                (self.performance.average_win * (self.performance.winning_trades - 1) + profit) /
                self.performance.winning_trades
            )
        else:
            self.performance.losing_trades += 1
            self.performance.average_loss = (
                (self.performance.average_loss * (self.performance.losing_trades - 1) + abs(profit)) /
                self.performance.losing_trades
            )
        
        self.performance.total_return += profit
        self.performance.win_rate = self.performance.winning_trades / self.performance.total_trades
        
        if self.performance.total_trades > 0:
            self.performance.profit_factor = (
                self.performance.average_win * self.performance.winning_trades /
                (self.performance.average_loss * self.performance.losing_trades) if self.performance.losing_trades > 0 else float('inf')
            )
        
        self.performance.last_updated = datetime.now()
    
    def get_performance(self) -> StrategyPerformance:
        """Get strategy performance metrics."""
        return self.performance


class MomentumStrategy(TradingStrategy):
    """Momentum-based trading strategy."""
    
    def __init__(self, strategy_id: str, lookback_period: int = 20, 
                 threshold: float = 0.02):
        super().__init__(strategy_id, StrategyType.MOMENTUM)
        self.parameters = {
            "lookback_period": lookback_period,
            "threshold": threshold
        }
        self._price_history: Dict[str, List[float]] = {}
    
    def generate_signal(self, market_data: Dict[str, Any]) -> Optional[TradingSignal]:
        """Generate momentum signal based on price trend."""
        if self.status != StrategyStatus.ACTIVE:
            return None
        
        symbol = market_data.get("symbol")
        current_price = market_data.get("price")
        
        if not symbol or not current_price:
            return None
        
        # Update price history
        if symbol not in self._price_history:
            self._price_history[symbol] = []
        
        self._price_history[symbol].append(current_price)
        lookback = self.parameters["lookback_period"]
        
        if len(self._price_history[symbol]) < lookback:
            return None
        
        # Keep only recent prices
        self._price_history[symbol] = self._price_history[symbol][-lookback:]
        
        # Calculate momentum
        prices = np.array(self._price_history[symbol])
        momentum = (prices[-1] - prices[0]) / prices[0]
        
        threshold = self.parameters["threshold"]
        
        # Generate signal
        if momentum > threshold:
            return TradingSignal(
                signal_id=f"signal_{int(datetime.now().timestamp())}",
                strategy_id=self.strategy_id,
                signal_type=SignalType.BUY,
                symbol=symbol,
                confidence=min(1.0, momentum / (2 * threshold)),
                reason=f"Positive momentum: {momentum:.2%}",
                metadata={"momentum": momentum, "lookback": lookback}
            )
        elif momentum < -threshold:
            return TradingSignal(
                signal_id=f"signal_{int(datetime.now().timestamp())}",
                strategy_id=self.strategy_id,
                signal_type=SignalType.SELL,
                symbol=symbol,
                confidence=min(1.0, abs(momentum) / (2 * threshold)),
                reason=f"Negative momentum: {momentum:.2%}",
                metadata={"momentum": momentum, "lookback": lookback}
            )
        
        return None
    
    def update_parameters(self, params: Dict[str, Any]) -> None:
        """Update strategy parameters."""
        for key, value in params.items():
            if key in self.parameters:
                self.parameters[key] = value
        logger.info(f"[STRATEGY] Updated parameters for {self.strategy_id}: {params}")


class MeanReversionStrategy(TradingStrategy):
    """Mean reversion trading strategy."""
    
    def __init__(self, strategy_id: str, lookback_period: int = 20, 
                 std_dev_threshold: float = 2.0):
        super().__init__(strategy_id, StrategyType.MEAN_REVERSION)
        self.parameters = {
            "lookback_period": lookback_period,
            "std_dev_threshold": std_dev_threshold
        }
        self._price_history: Dict[str, List[float]] = {}
    
    def generate_signal(self, market_data: Dict[str, Any]) -> Optional[TradingSignal]:
        """Generate mean reversion signal based on statistical deviation."""
        if self.status != StrategyStatus.ACTIVE:
            return None
        
        symbol = market_data.get("symbol")
        current_price = market_data.get("price")
        
        if not symbol or not current_price:
            return None
        
        # Update price history
        if symbol not in self._price_history:
            self._price_history[symbol] = []
        
        self._price_history[symbol].append(current_price)
        lookback = self.parameters["lookback_period"]
        
        if len(self._price_history[symbol]) < lookback:
            return None
        
        # Keep only recent prices
        self._price_history[symbol] = self._price_history[symbol][-lookback:]
        
        # Calculate mean and standard deviation
        prices = np.array(self._price_history[symbol])
        mean_price = np.mean(prices)
        std_price = np.std(prices)
        
        std_threshold = self.parameters["std_dev_threshold"]
        
        # Calculate z-score
        z_score = (current_price - mean_price) / std_price if std_price > 0 else 0
        
        # Generate signal
        if z_score < -std_threshold:
            return TradingSignal(
                signal_id=f"signal_{int(datetime.now().timestamp())}",
                strategy_id=self.strategy_id,
                signal_type=SignalType.BUY,
                symbol=symbol,
                confidence=min(1.0, abs(z_score) / (2 * std_threshold)),
                target_price=mean_price,
                reason=f"Price below mean by {abs(z_score):.2f} standard deviations",
                metadata={"z_score": z_score, "mean": mean_price, "std": std_price}
            )
        elif z_score > std_threshold:
            return TradingSignal(
                signal_id=f"signal_{int(datetime.now().timestamp())}",
                strategy_id=self.strategy_id,
                signal_type=SignalType.SELL,
                symbol=symbol,
                confidence=min(1.0, abs(z_score) / (2 * std_threshold)),
                target_price=mean_price,
                reason=f"Price above mean by {abs(z_score):.2f} standard deviations",
                metadata={"z_score": z_score, "mean": mean_price, "std": std_price}
            )
        
        return None
    
    def update_parameters(self, params: Dict[str, Any]) -> None:
        """Update strategy parameters."""
        for key, value in params.items():
            if key in self.parameters:
                self.parameters[key] = value
        logger.info(f"[STRATEGY] Updated parameters for {self.strategy_id}: {params}")


class TrendFollowingStrategy(TradingStrategy):
    """Trend following strategy using moving averages."""
    
    def __init__(self, strategy_id: str, fast_period: int = 10, 
                 slow_period: int = 30):
        super().__init__(strategy_id, StrategyType.TREND_FOLLOWING)
        self.parameters = {
            "fast_period": fast_period,
            "slow_period": slow_period
        }
        self._price_history: Dict[str, List[float]] = {}
        self._last_signal: Dict[str, SignalType] = {}
    
    def generate_signal(self, market_data: Dict[str, Any]) -> Optional[TradingSignal]:
        """Generate trend following signal using moving average crossover."""
        if self.status != StrategyStatus.ACTIVE:
            return None
        
        symbol = market_data.get("symbol")
        current_price = market_data.get("price")
        
        if not symbol or not current_price:
            return None
        
        # Update price history
        if symbol not in self._price_history:
            self._price_history[symbol] = []
        
        self._price_history[symbol].append(current_price)
        slow_period = self.parameters["slow_period"]
        
        if len(self._price_history[symbol]) < slow_period:
            return None
        
        # Keep only recent prices
        self._price_history[symbol] = self._price_history[symbol][-slow_period:]
        
        # Calculate moving averages
        prices = np.array(self._price_history[symbol])
        fast_period = self.parameters["fast_period"]
        
        fast_ma = np.mean(prices[-fast_period:])
        slow_ma = np.mean(prices)
        
        last_signal = self._last_signal.get(symbol, SignalType.HOLD)
        
        # Generate signal on crossover
        if fast_ma > slow_ma and last_signal != SignalType.BUY:
            self._last_signal[symbol] = SignalType.BUY
            return TradingSignal(
                signal_id=f"signal_{int(datetime.now().timestamp())}",
                strategy_id=self.strategy_id,
                signal_type=SignalType.BUY,
                symbol=symbol,
                confidence=0.8,
                reason=f"Fast MA ({fast_ma:.2f}) crossed above Slow MA ({slow_ma:.2f})",
                metadata={"fast_ma": fast_ma, "slow_ma": slow_ma}
            )
        elif fast_ma < slow_ma and last_signal != SignalType.SELL:
            self._last_signal[symbol] = SignalType.SELL
            return TradingSignal(
                signal_id=f"signal_{int(datetime.now().timestamp())}",
                strategy_id=self.strategy_id,
                signal_type=SignalType.SELL,
                symbol=symbol,
                confidence=0.8,
                reason=f"Fast MA ({fast_ma:.2f}) crossed below Slow MA ({slow_ma:.2f})",
                metadata={"fast_ma": fast_ma, "slow_ma": slow_ma}
            )
        
        return None
    
    def update_parameters(self, params: Dict[str, Any]) -> None:
        """Update strategy parameters."""
        for key, value in params.items():
            if key in self.parameters:
                self.parameters[key] = value
        logger.info(f"[STRATEGY] Updated parameters for {self.strategy_id}: {params}")


class StrategyManager:
    """Manages multiple trading strategies."""
    
    def __init__(self):
        self._strategies: Dict[str, TradingStrategy] = {}
        self._active_strategies: List[str] = []
        self._signal_history: List[TradingSignal] = []
        
    def register_strategy(self, strategy: TradingStrategy) -> None:
        """Register a trading strategy."""
        self._strategies[strategy.strategy_id] = strategy
        logger.info(f"[STRATEGY_MANAGER] Registered strategy: {strategy.strategy_id}")
    
    def unregister_strategy(self, strategy_id: str) -> bool:
        """Unregister a trading strategy."""
        if strategy_id in self._strategies:
            del self._strategies[strategy_id]
            if strategy_id in self._active_strategies:
                self._active_strategies.remove(strategy_id)
            logger.info(f"[STRATEGY_MANAGER] Unregistered strategy: {strategy_id}")
            return True
        return False
    
    def start_strategy(self, strategy_id: str) -> bool:
        """Start a strategy."""
        if strategy_id in self._strategies:
            self._strategies[strategy_id].start()
            if strategy_id not in self._active_strategies:
                self._active_strategies.append(strategy_id)
            return True
        return False
    
    def stop_strategy(self, strategy_id: str) -> bool:
        """Stop a strategy."""
        if strategy_id in self._strategies:
            self._strategies[strategy_id].stop()
            if strategy_id in self._active_strategies:
                self._active_strategies.remove(strategy_id)
            return True
        return False
    
    def get_strategy(self, strategy_id: str) -> Optional[TradingStrategy]:
        """Get a strategy by ID."""
        return self._strategies.get(strategy_id)
    
    def generate_signals(self, market_data: Dict[str, Any]) -> List[TradingSignal]:
        """Generate signals from all active strategies."""
        signals = []
        
        for strategy_id in self._active_strategies:
            strategy = self._strategies[strategy_id]
            signal = strategy.generate_signal(market_data)
            if signal:
                signals.append(signal)
                self._signal_history.append(signal)
        
        return signals
    
    def get_all_strategies(self) -> Dict[str, TradingStrategy]:
        """Get all registered strategies."""
        return self._strategies.copy()
    
    def get_active_strategies(self) -> List[TradingStrategy]:
        """Get all active strategies."""
        return [self._strategies[sid] for sid in self._active_strategies]


# Global strategy manager and registry
_strategy_manager = StrategyManager()
_strategy_registry: Dict[str, Callable[[], TradingStrategy]] = {}


def register_strategy_factory(strategy_id: str, factory: Callable[[], TradingStrategy]) -> None:
    """Register a strategy factory function."""
    _strategy_registry[strategy_id] = factory


def get_strategy(strategy_id: str, **kwargs: Any) -> Optional[TradingStrategy]:
    """Get a strategy instance by ID.
    
    Args:
        strategy_id: ID of the strategy to retrieve
        **kwargs: Additional parameters for strategy initialization
        
    Returns:
        TradingStrategy instance or None if not found
    """
    # Check if already instantiated
    strategy = _strategy_manager.get_strategy(strategy_id)
    if strategy:
        return strategy
    
    # Try to instantiate from registry
    if strategy_id in _strategy_registry:
        strategy = _strategy_registry[strategy_id]()
        _strategy_manager.register_strategy(strategy)
        return strategy
    
    # Try to create based on strategy type
    strategy_type = kwargs.get("strategy_type", "momentum")
    
    if strategy_type == "momentum":
        strategy = MomentumStrategy(
            strategy_id=strategy_id,
            lookback_period=kwargs.get("lookback_period", 20),
            threshold=kwargs.get("threshold", 0.02)
        )
    elif strategy_type == "mean_reversion":
        strategy = MeanReversionStrategy(
            strategy_id=strategy_id,
            lookback_period=kwargs.get("lookback_period", 20),
            std_dev_threshold=kwargs.get("std_dev_threshold", 2.0)
        )
    elif strategy_type == "trend_following":
        strategy = TrendFollowingStrategy(
            strategy_id=strategy_id,
            fast_period=kwargs.get("fast_period", 10),
            slow_period=kwargs.get("slow_period", 30)
        )
    else:
        logger.warning(f"[STRATEGY] Unknown strategy type: {strategy_type}")
        return None
    
    _strategy_manager.register_strategy(strategy)
    return strategy


def get_strategy_manager() -> StrategyManager:
    """Get the global strategy manager."""
    return _strategy_manager


# Initialize default strategies
def _initialize_default_strategies():
    """Initialize default trading strategies."""
    default_momentum = MomentumStrategy(
        strategy_id="default_momentum",
        lookback_period=20,
        threshold=0.02
    )
    _strategy_manager.register_strategy(default_momentum)
    
    default_mean_reversion = MeanReversionStrategy(
        strategy_id="default_mean_reversion",
        lookback_period=20,
        std_dev_threshold=2.0
    )
    _strategy_manager.register_strategy(default_mean_reversion)
    
    default_trend = TrendFollowingStrategy(
        strategy_id="default_trend_following",
        fast_period=10,
        slow_period=30
    )
    _strategy_manager.register_strategy(default_trend)
    
    logger.info("[STRATEGY] Initialized default strategies")


# Auto-initialize on import
_initialize_default_strategies()


__all__ = [
    "StrategyType",
    "StrategyStatus",
    "SignalType",
    "TradingSignal",
    "StrategyPerformance",
    "TradingStrategy",
    "MomentumStrategy",
    "MeanReversionStrategy",
    "TrendFollowingStrategy",
    "StrategyManager",
    "get_strategy",
    "get_strategy_manager"
]