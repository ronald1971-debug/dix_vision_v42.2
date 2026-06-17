"""Slippage Control System — EXEC-05.03.

Monitoring and control system for trade slippage to prevent
excessive execution costs. Provides real-time slippage tracking,
adaptive slippage thresholds, and order size adjustments based
on market conditions.
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

DEFAULT_MAX_SLIPPAGE_PCT: Final[float] = 0.5  # 0.5% max slippage
DEFAULT_WARNING_SLIPPAGE_PCT: Final[float] = 0.3  # 0.3% warning threshold
DEFAULT_ADAPTIVE_FACTOR: Final[float] = 1.0
DEFAULT_HISTORY_SIZE: Final[int] = 100
DEFAULT_VOLATILITY_WINDOW: Final[int] = 20  # Number of recent trades to consider
DEFAULT_VOLUME_IMPACT_FACTOR: Final[float] = 0.01  # Volume impact per unit size

NEW_PIP_DEPENDENCIES: Final[tuple[str, ...]] = ()


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class SlippageAction(enum.Enum):
    """Actions to take based on slippage analysis."""
    ALLOW = "ALLOW"  # Allow order with current size
    REDUCE = "REDUCE"  # Reduce order size
    REJECT = "REJECT"  # Reject order entirely
    WARN = "WARN"  # Allow with warning


class SlippageSeverity(enum.Enum):
    """Severity level of slippage."""
    NORMAL = "NORMAL"  # Within acceptable range
    ELEVATED = "ELEVATED"  # Slightly elevated
    HIGH = "HIGH"  # High slippage
    EXTREME = "EXTREME"  # Extremely high slippage


class OrderSide(enum.Enum):
    """Side of the order."""
    BUY = "BUY"
    SELL = "SELL"


# ---------------------------------------------------------------------------
# Value objects
# ---------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True, slots=True)
class SlippageConfig:
    """Configuration for slippage control."""
    max_slippage_pct: float = DEFAULT_MAX_SLIPPAGE_PCT
    warning_slippage_pct: float = DEFAULT_WARNING_SLIPPAGE_PCT
    adaptive_factor: float = DEFAULT_ADAPTIVE_FACTOR
    enable_adaptive: bool = True
    enable_volume_analysis: bool = True
    enable_time_decay: bool = False
    history_size: int = DEFAULT_HISTORY_SIZE
    volatility_window: int = DEFAULT_VOLATILITY_WINDOW
    volume_impact_factor: float = DEFAULT_VOLUME_IMPACT_FACTOR

    def __post_init__(self) -> None:
        if self.max_slippage_pct < 0:
            raise ValueError("max_slippage_pct must be >= 0")
        if self.warning_slippage_pct < 0:
            raise ValueError("warning_slippage_pct must be >= 0")
        if self.warning_slippage_pct > self.max_slippage_pct:
            raise ValueError("warning_slippage_pct must be <= max_slippage_pct")
        if self.adaptive_factor < 0:
            raise ValueError("adaptive_factor must be >= 0")
        if self.history_size < 1:
            raise ValueError("history_size must be >= 1")
        if self.volatility_window < 1:
            raise ValueError("volatility_window must be >= 1")


@dataclasses.dataclass(frozen=True, slots=True)
class SlippageMetrics:
    """Metrics about slippage performance."""
    symbol: str
    total_orders: int
    average_slippage_pct: float
    max_slippage_pct: float
    min_slippage_pct: float
    median_slippage_pct: float
    slippage_std_dev: float
    recent_slippage_pct: float
    volatility_index: float
    volume_impact: float
    orders_above_threshold: int
    orders_above_warning: int


@dataclasses.dataclass(frozen=True, slots=True)
class SlippageAnalysis:
    """Result of slippage analysis for an order."""
    symbol: str
    expected_price: float
    estimated_fill_price: float
    estimated_slippage_pct: float
    severity: SlippageSeverity
    recommended_action: SlippageAction
    recommended_size_reduction: float  # Percentage to reduce size
    confidence: float  # Confidence in the estimate (0-1)
    volatility: float
    volume_impact: float
    timestamp_ns: int
    reason: str
    metadata: dict[str, Any] = dataclasses.field(default_factory=dict)


@dataclasses.dataclass(frozen=True, slots=True)
class TradeRecord:
    """Record of a completed trade for slippage tracking."""
    symbol: str
    side: OrderSide
    expected_price: float
    fill_price: float
    quantity: float
    volume: float  # Trading volume at time of trade
    slippage_pct: float
    timestamp_ns: int
    metadata: dict[str, Any] = dataclasses.field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.symbol:
            raise ValueError("symbol must be non-empty")
        if self.expected_price <= 0:
            raise ValueError("expected_price must be > 0")
        if self.fill_price <= 0:
            raise ValueError("fill_price must be > 0")
        if self.quantity <= 0:
            raise ValueError("quantity must be > 0")


# ---------------------------------------------------------------------------
# Slippage Controller
# ---------------------------------------------------------------------------


class SlippageController:
    """Controller for managing slippage on trades.
    
    Tracks historical slippage data, estimates future slippage,
    and provides recommendations for order sizing and execution
    strategy based on market conditions.
    """
    
    def __init__(
        self,
        config: SlippageConfig | None = None,
    ) -> None:
        """Initialize the slippage controller.
        
        Args:
            config: Slippage control configuration
        """
        self._config = config or SlippageConfig()
        self._lock = Lock()
        
        self._trade_history: dict[str, deque[TradeRecord]] = {}
        self._symbol_metrics: dict[str, SlippageMetrics] = {}
    
    def analyze_order(
        self,
        symbol: str,
        side: OrderSide,
        expected_price: float,
        quantity: float,
        current_volume: float,
        timestamp_ns: int | None = None,
    ) -> SlippageAnalysis:
        """Analyze an order for potential slippage.
        
        Args:
            symbol: Trading symbol
            side: Order side
            expected_price: Expected execution price
            quantity: Order quantity
            current_volume: Current trading volume
            timestamp_ns: Current timestamp
            
        Returns:
            Slippage analysis with recommendations
        """
        import time
        
        if timestamp_ns is None:
            timestamp_ns = time.time_ns()
        
        with self._lock:
            # Get historical slippage for the symbol
            symbol_history = self._trade_history.get(symbol, deque(maxlen=self._config.history_size))
            
            # Calculate estimated slippage
            estimated_slippage = self._estimate_slippage(
                symbol, side, expected_price, quantity, current_volume, symbol_history
            )
            
            # Determine severity
            severity = self._determine_severity(estimated_slippage)
            
            # Determine action
            action = self._determine_action(estimated_slippage, severity)
            
            # Calculate recommended size reduction
            size_reduction = self._calculate_size_reduction(estimated_slippage, action)
            
            # Calculate confidence
            confidence = self._calculate_confidence(symbol_history)
            
            # Calculate volatility
            volatility = self._calculate_volatility(symbol_history)
            
            # Calculate volume impact
            volume_impact = self._calculate_volume_impact(quantity, current_volume)
            
            # Determine reason
            reason = self._generate_reason(estimated_slippage, severity, action)
            
            return SlippageAnalysis(
                symbol=symbol,
                expected_price=expected_price,
                estimated_fill_price=self._calculate_fill_price(
                    side, expected_price, estimated_slippage
                ),
                estimated_slippage_pct=estimated_slippage,
                severity=severity,
                recommended_action=action,
                recommended_size_reduction=size_reduction,
                confidence=confidence,
                volatility=volatility,
                volume_impact=volume_impact,
                timestamp_ns=timestamp_ns,
                reason=reason,
            )
    
    def record_trade(
        self,
        trade: TradeRecord,
    ) -> None:
        """Record a completed trade for historical tracking.
        
        Args:
            trade: Trade record
        """
        with self._lock:
            if trade.symbol not in self._trade_history:
                self._trade_history[trade.symbol] = deque(maxlen=self._config.history_size)
            
            self._trade_history[trade.symbol].append(trade)
            
            # Update symbol metrics
            self._update_symbol_metrics(trade.symbol)
    
    def get_metrics(self, symbol: str) -> SlippageMetrics | None:
        """Get slippage metrics for a symbol.
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Metrics or None if no data available
        """
        with self._lock:
            return self._symbol_metrics.get(symbol)
    
    def _estimate_slippage(
        self,
        symbol: str,
        side: OrderSide,
        expected_price: float,
        quantity: float,
        current_volume: float,
        history: deque[TradeRecord],
    ) -> float:
        """Estimate slippage for an order."""
        if not history:
            # No historical data, use simple volume-based estimate
            volume_impact = self._calculate_volume_impact(quantity, current_volume)
            return volume_impact * 100  # Convert to percentage
        
        # Calculate historical average slippage
        historical_slippages = [trade.slippage_pct for trade in history]
        avg_historical_slippage = sum(historical_slippages) / len(historical_slippages)
        
        # Calculate volume impact
        volume_impact = self._calculate_volume_impact(quantity, current_volume)
        
        # Calculate historical volatility
        volatility = self._calculate_volatility(history)
        
        # Combine factors
        estimated_slippage = avg_historical_slippage
        estimated_slippage *= (1 + volatility * 0.5)  # Volatility factor
        estimated_slippage += volume_impact * 100  # Volume impact in percentage
        
        if self._config.enable_adaptive:
            estimated_slippage *= self._config.adaptive_factor
        
        return max(0, estimated_slippage)
    
    def _determine_severity(self, slippage_pct: float) -> SlippageSeverity:
        """Determine severity level of slippage."""
        if slippage_pct < self._config.warning_slippage_pct:
            return SlippageSeverity.NORMAL
        elif slippage_pct < self._config.max_slippage_pct:
            return SlippageSeverity.ELEVATED
        elif slippage_pct < self._config.max_slippage_pct * 2:
            return SlippageSeverity.HIGH
        else:
            return SlippageSeverity.EXTREME
    
    def _determine_action(
        self,
        slippage_pct: float,
        severity: SlippageSeverity,
    ) -> SlippageAction:
        """Determine recommended action based on slippage."""
        if severity == SlippageSeverity.EXTREME:
            return SlippageAction.REJECT
        elif severity == SlippageSeverity.HIGH:
            return SlippageAction.REDUCE
        elif severity == SlippageSeverity.ELEVATED:
            return SlippageAction.WARN
        else:
            return SlippageAction.ALLOW
    
    def _calculate_size_reduction(
        self,
        slippage_pct: float,
        action: SlippageAction,
    ) -> float:
        """Calculate recommended order size reduction percentage."""
        if action != SlippageAction.REDUCE:
            return 0.0
        
        # Calculate reduction based on how much over limit
        overage = slippage_pct - self._config.max_slippage_pct
        max_overage = self._config.max_slippage_pct  # Assume we want to get to threshold
        
        reduction = min(1.0, overage / max_overage) if max_overage > 0 else 0.5
        return reduction * 100  # Convert to percentage
    
    def _calculate_confidence(self, history: deque[TradeRecord]) -> float:
        """Calculate confidence in slippage estimate."""
        if not history:
            return 0.0
        
        # Confidence increases with more data points
        data_points = len(history)
        confidence = min(1.0, data_points / self._config.history_size)
        
        return confidence
    
    def _calculate_volatility(self, history: deque[TradeRecord]) -> float:
        """Calculate slippage volatility from history."""
        if len(history) < 2:
            return 0.0
        
        slippages = [trade.slippage_pct for trade in history]
        avg_slippage = sum(slippages) / len(slippages)
        
        # Calculate standard deviation
        variance = sum((s - avg_slippage) ** 2 for s in slippages) / len(slippages)
        std_dev = variance ** 0.5
        
        # Normalize by average to get relative volatility
        relative_volatility = std_dev / avg_slippage if avg_slippage > 0 else 0
        
        return relative_volatility
    
    def _calculate_volume_impact(self, quantity: float, current_volume: float) -> float:
        """Calculate volume impact of an order."""
        if current_volume <= 0:
            return 1.0  # Assume maximum impact if no volume data
        
        impact = (quantity / current_volume) * self._config.volume_impact_factor
        return min(1.0, impact)
    
    def _calculate_fill_price(
        self,
        side: OrderSide,
        expected_price: float,
        slippage_pct: float,
    ) -> float:
        """Calculate estimated fill price given slippage."""
        slippage_factor = slippage_pct / 100.0
        
        if side == OrderSide.BUY:
            # Buying: price goes up
            return expected_price * (1 + slippage_factor)
        else:
            # Selling: price goes down
            return expected_price * (1 - slippage_factor)
    
    def _generate_reason(
        self,
        slippage_pct: float,
        severity: SlippageSeverity,
        action: SlippageAction,
    ) -> str:
        """Generate reason for the recommendation."""
        if action == SlippageAction.ALLOW:
            return f"Slippage estimated at {slippage_pct:.3f}% within acceptable range"
        elif action == SlippageAction.WARN:
            return f"Slippage estimated at {slippage_pct:.3f}% slightly elevated"
        elif action == SlippageAction.REDUCE:
            return f"Slippage estimated at {slippage_pct:.3f}% exceeds threshold, reduce order size"
        else:
            return f"Slippage estimated at {slippage_pct:.3f}% too high, reject order"
    
    def _update_symbol_metrics(self, symbol: str) -> None:
        """Update metrics for a symbol."""
        history = self._trade_history.get(symbol)
        if not history or len(history) == 0:
            return
        
        slippages = [trade.slippage_pct for trade in history]
        
        avg_slippage = sum(slippages) / len(slippages)
        max_slippage = max(slippages)
        min_slippage = min(slippages)
        
        # Calculate median
        sorted_slippages = sorted(slippages)
        median_slippage = sorted_slippages[len(sorted_slippages) // 2]
        
        # Calculate standard deviation
        variance = sum((s - avg_slippage) ** 2 for s in slippages) / len(slippages)
        std_dev = variance ** 0.5
        
        # Count orders above thresholds
        orders_above_threshold = sum(1 for s in slippages if s > self._config.max_slippage_pct)
        orders_above_warning = sum(1 for s in slippages if s > self._config.warning_slippage_pct)
        
        # Calculate recent slippage
        recent_window = min(10, len(slippages))
        recent_slippage = sum(slippages[-recent_window:]) / recent_window
        
        # Calculate volatility and volume impact
        volatility = self._calculate_volatility(history)
        
        # Average volume impact
        volume_impacts = [
            self._calculate_volume_impact(trade.quantity, trade.volume)
            for trade in history
        ]
        avg_volume_impact = sum(volume_impacts) / len(volume_impacts) if volume_impacts else 0
        
        self._symbol_metrics[symbol] = SlippageMetrics(
            symbol=symbol,
            total_orders=len(history),
            average_slippage_pct=avg_slippage,
            max_slippage_pct=max_slippage,
            min_slippage_pct=min_slippage,
            median_slippage_pct=median_slippage,
            slippage_std_dev=std_dev,
            recent_slippage_pct=recent_slippage,
            volatility_index=volatility,
            volume_impact=avg_volume_impact,
            orders_above_threshold=orders_above_threshold,
            orders_above_warning=orders_above_warning,
        )


# ---------------------------------------------------------------------------
# Slippage Manager
# ---------------------------------------------------------------------------


class SlippageManager:
    """Manager for slippage control across multiple symbols."""
    
    def __init__(self, config: SlippageConfig | None = None) -> None:
        """Initialize the slippage manager.
        
        Args:
            config: Slippage control configuration
        """
        self._config = config or SlippageConfig()
        self._controller = SlippageController(config)
    
    def analyze_order(
        self,
        symbol: str,
        side: OrderSide,
        expected_price: float,
        quantity: float,
        current_volume: float,
    ) -> SlippageAnalysis:
        """Analyze an order for potential slippage.
        
        Args:
            symbol: Trading symbol
            side: Order side
            expected_price: Expected execution price
            quantity: Order quantity
            current_volume: Current trading volume
            
        Returns:
            Slippage analysis with recommendations
        """
        return self._controller.analyze_order(
            symbol, side, expected_price, quantity, current_volume
        )
    
    def record_trade(self, trade: TradeRecord) -> None:
        """Record a completed trade.
        
        Args:
            trade: Trade record
        """
        self._controller.record_trade(trade)
    
    def get_metrics(self, symbol: str) -> SlippageMetrics | None:
        """Get slippage metrics for a symbol.
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Metrics or None if no data available
        """
        return self._controller.get_metrics(symbol)


__all__ = [
    "SlippageAction",
    "SlippageSeverity",
    "OrderSide",
    "SlippageConfig",
    "SlippageMetrics",
    "SlippageAnalysis",
    "TradeRecord",
    "SlippageController",
    "SlippageManager",
]
