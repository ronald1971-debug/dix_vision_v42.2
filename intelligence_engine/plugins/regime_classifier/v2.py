"""Enhanced regime classifier plugin v2 with adaptive thresholds.

Based on alternative implementation with contract compliance and
adaptive threshold adjustment based on market conditions.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Sequence
from enum import Enum
import statistics

from core.contracts.engine import (
    HealthState,
    HealthStatus,
    PluginLifecycle,
    MicrostructurePlugin,
)
from core.contracts.events import Side, SignalEvent
from core.contracts.market import MarketTick


class MarketRegime(Enum):
    """Market regime classifications."""
    QUIET_LOW_VOLATILITY = "quiet_low_volatility"
    NORMAL_TRADING = "normal_trading"
    HIGH_VOLATILITY = "high_volatility"
    EXTREME_VOLATILITY = "extreme_volatility"
    TRENDING_UP = "trending_up"
    TRENDING_DOWN = "trending_down"
    RANGE_BOUND = "range_bound"
    BREAKOUT = "breakout"


@dataclass(slots=True)
class RegimeClassifierV2(MicrostructurePlugin):
    """Enhanced regime classifier with adaptive thresholds.
    
    v2 features:
    - Adaptive threshold adjustment
    - Multi-regime classification
    - Trend detection
    - Volatility regime identification
    - Statistical regime confirmation
    """
    
    name: str = "regime_classifier_v2"
    version: str = "2.0.0"
    lifecycle: PluginLifecycle = PluginLifecycle.ACTIVE
    
    # Analysis parameters
    window_size: int = 32  # Analysis window
    vol_low_threshold: float = 0.001  # Low volatility threshold
    vol_high_threshold: float = 0.01  # High volatility threshold
    drift_threshold: float = 0.0005  # Drift threshold for trend detection
    trend_confirmation_bars: int = 5  # Bars needed for trend confirmation
    
    # Adaptive parameters
    adaptive_thresholds: bool = True  # Enable adaptive threshold adjustment
    adaptation_rate: float = 0.1  # Rate of threshold adaptation
    min_samples_for_adaptation: int = 100  # Minimum samples before adaptation
    
    # Internal state
    _price_history: deque[float] = field(init=False, repr=False)
    _return_history: deque[float] = field(init=False, repr=False)
    _volatility_history: deque[float] = field(init=False, repr=False)
    _current_regime: MarketRegime = field(init=False, repr=False, default=MarketRegime.NORMAL_TRADING)
    _adaptive_vol_low: float = field(init=False, repr=False, default=0.001)
    _adaptive_vol_high: float = field(init=False, repr=False, default=0.01)
    _sample_count: int = field(init=False, repr=False, default=0)
    
    def __post_init__(self) -> None:
        if self.window_size < 2:
            raise ValueError("window_size must be >= 2")
        if self.vol_low_threshold <= 0:
            raise ValueError("vol_low_threshold must be > 0")
        if self.vol_high_threshold <= self.vol_low_threshold:
            raise ValueError("vol_high_threshold must be > vol_low_threshold")
        if self.drift_threshold < 0:
            raise ValueError("drift_threshold must be >= 0")
        if self.trend_confirmation_bars < 1:
            raise ValueError("trend_confirmation_bars must be >= 1")
        if not (0.0 < self.adaptation_rate <= 1.0):
            raise ValueError("adaptation_rate must be in (0.0, 1.0]")
        
        self._price_history = deque(maxlen=self.window_size)
        self._return_history = deque(maxlen=self.window_size)
        self._volatility_history = deque(maxlen=self.window_size)
        self._adaptive_vol_low = self.vol_low_threshold
        self._adaptive_vol_high = self.vol_high_threshold
    
    def on_tick(self, tick: MarketTick) -> Sequence[SignalEvent]:
        """Process a market tick and emit regime-based signals."""
        price = tick.last
        
        # Calculate returns
        if len(self._price_history) > 0:
            last_price = self._price_history[-1]
            if last_price > 0:
                price_return = (price - last_price) / last_price
                self._return_history.append(price_return)
                self._sample_count += 1
        
        self._price_history.append(price)
        
        # Calculate volatility if we have enough data
        if len(self._return_history) >= 10:
            volatility = self._calculate_volatility()
            self._volatility_history.append(volatility)
            
            # Adapt thresholds if enabled
            if self.adaptive_thresholds and self._sample_count >= self.min_samples_for_adaptation:
                self._adapt_thresholds(volatility)
        
        # Classify regime
        signals = []
        
        if len(self._return_history) >= self.trend_confirmation_bars:
            new_regime = self._classify_regime()
            
            # Emit signal on regime change
            if new_regime != self._current_regime:
                self._current_regime = new_regime
                signal = self._generate_regime_signal(tick, new_regime)
                if signal:
                    signals.append(signal)
        
        return signals
    
    def _calculate_volatility(self) -> float:
        """Calculate current volatility."""
        if len(self._return_history) < 2:
            return 0.0
        
        return statistics.stdev(self._return_history) if len(self._return_history) > 1 else 0.0
    
    def _adapt_thresholds(self, current_volatility: float) -> None:
        """Adapt volatility thresholds based on recent market conditions."""
        # Blend current thresholds with recent volatility
        self._adaptive_vol_low = (1 - self.adaptation_rate) * self._adaptive_vol_low + self.adaptation_rate * current_volatility * 0.5
        self._adaptive_vol_high = (1 - self.adaptation_rate) * self._adaptive_vol_high + self.adaptation_rate * current_volatility * 2.0
    
    def _classify_regime(self) -> MarketRegime:
        """Classify current market regime."""
        if len(self._volatility_history) < 5:
            return MarketRegime.NORMAL_TRADING
        
        current_vol = self._volatility_history[-1]
        avg_vol = sum(self._volatility_history) / len(self._volatility_history)
        
        # Classify by volatility
        if current_vol < self._adaptive_vol_low:
            vol_regime = "low"
        elif current_vol < self._adaptive_vol_high:
            vol_regime = "normal"
        else:
            vol_regime = "high"
        
        # Check for trend
        if len(self._return_history) >= self.trend_confirmation_bars:
            recent_returns = list(self._return_history)[-self.trend_confirmation_bars:]
            avg_return = sum(recent_returns) / len(recent_returns)
            
            if abs(avg_return) > self.drift_threshold:
                if avg_return > 0:
                    if vol_regime == "high":
                        return MarketRegime.BREAKOUT
                    else:
                        return MarketRegime.TRENDING_UP
                else:
                    if vol_regime == "high":
                        return MarketRegime.BREAKOUT
                    else:
                        return MarketRegime.TRENDING_DOWN
        
        # Map volatility regime
        vol_regime_map = {
            "low": MarketRegime.QUIET_LOW_VOLATILITY,
            "normal": MarketRegime.NORMAL_TRADING,
            "high": MarketRegime.HIGH_VOLATILITY if current_vol < self._adaptive_vol_high * 2 else MarketRegime.EXTREME_VOLATILITY
        }
        
        return vol_regime_map.get(vol_regime, MarketRegime.NORMAL_TRADING)
    
    def _generate_regime_signal(self, tick: MarketTick, regime: MarketRegime) -> SignalEvent:
        """Generate signal event for regime change."""
        # Calculate confidence based on volatility stability
        if len(self._volatility_history) >= 5:
            vol_std = statistics.stdev(self._volatility_history) if len(self._volatility_history) > 1 else 0.0
            vol_mean = sum(self._volatility_history) / len(self._volatility_history)
            confidence = max(0.5, min(1.0, 1.0 - vol_std / (vol_mean + 1e-9)))
        else:
            confidence = 0.7
        
        # Determine side based on regime
        side_map = {
            MarketRegime.QUIET_LOW_VOLATILITY: Side.HOLD,
            MarketRegime.NORMAL_TRADING: Side.HOLD,
            MarketRegime.HIGH_VOLATILITY: Side.HOLD,
            MarketRegime.EXTREME_VOLATILITY: Side.HOLD,
            MarketRegime.TRENDING_UP: Side.BUY,
            MarketRegime.TRENDING_DOWN: Side.SELL,
            MarketRegime.RANGE_BOUND: Side.HOLD,
            MarketRegime.BREAKOUT: Side.BUY,  # Assume breakout direction based on price
        }
        
        # Special case for breakout - determine direction from recent price action
        if regime == MarketRegime.BREAKOUT and len(self._return_history) >= self.trend_confirmation_bars:
            recent_returns = list(self._return_history)[-self.trend_confirmation_bars:]
            avg_return = sum(recent_returns) / len(recent_returns)
            side = Side.BUY if avg_return > 0 else Side.SELL
        else:
            side = side_map.get(regime, Side.HOLD)
        
        return SignalEvent(
            source=self.name,
            timestamp_ns=tick.timestamp_ns,
            symbol=tick.symbol,
            side=side,
            confidence=confidence,
            reason=f"regime_change:{regime.value}",
            metadata={
                "regime": regime.value,
                "volatility": self._volatility_history[-1] if self._volatility_history else 0.0,
                "adaptive_vol_low": self._adaptive_vol_low,
                "adaptive_vol_high": self._adaptive_vol_high,
                "samples": self._sample_count
            }
        )
    
    def check_self(self) -> HealthStatus:
        """Health check for the enhanced regime classifier."""
        try:
            if len(self._price_history) == 0:
                return HealthStatus(
                    engine_name=self.name,
                    state=HealthState.ALIVE,
                    detail=f"{self.name} v{self.version} lifecycle={self.lifecycle} window={self.window_size} (awaiting data)"
                )
            
            current_vol = self._volatility_history[-1] if self._volatility_history else 0.0
            
            return HealthStatus(
                engine_name=self.name,
                state=HealthState.ALIVE,
                detail=f"{self.name} v{self.version} lifecycle={self.lifecycle} window={self.window_size} regime={self._current_regime.value} vol={current_vol:.4f} samples={self._sample_count}"
            )
            
        except Exception as e:
            return HealthStatus(
                engine_name=self.name,
                state=HealthState.FAIL,
                detail=f"Health check failed: {str(e)}"
            )


__all__ = ["RegimeClassifierV2", "MarketRegime"]