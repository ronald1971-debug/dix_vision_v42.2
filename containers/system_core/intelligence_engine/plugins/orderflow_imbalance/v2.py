"""Enhanced orderflow imbalance plugin v2 with advanced features.

Based on the alternative implementation but made contract-compliant with
additional pattern recognition and multi-timeframe analysis.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Sequence
from enum import Enum

from core.contracts.engine import (
    HealthState,
    HealthStatus,
    PluginLifecycle,
    MicrostructurePlugin,
)
from core.contracts.events import Side, SignalEvent
from core.contracts.market import MarketTick


class FlowIntensity(Enum):
    """Order flow intensity levels."""
    EXTREME_BUYING = "extreme_buying"
    STRONG_BUYING = "strong_buying"
    MODERATE_BUYING = "moderate_buying"
    NEUTRAL = "neutral"
    MODERATE_SELLING = "moderate_selling"
    STRONG_SELLING = "strong_selling"
    EXTREME_SELLING = "extreme_selling"


@dataclass(slots=True)
class OrderflowImbalanceV2(MicrostructurePlugin):
    """Enhanced orderflow imbalance plugin with advanced pattern recognition.
    
    v2 features:
    - Multi-timeframe analysis
    - Flow intensity classification
    - Momentum confirmation
    - Volume-weighted imbalance calculation
    """
    
    name: str = "orderflow_imbalance_v2"
    version: str = "2.0.0"
    lifecycle: PluginLifecycle = PluginLifecycle.ACTIVE
    
    # Enhanced parameters
    window_size: int = 64  # Increased window for better analysis
    imbalance_threshold: float = 0.15  # More sensitive threshold
    confidence_scale: float = 0.8  # Enhanced confidence scaling
    min_confidence: float = 0.05
    momentum_window: int = 10  # For momentum confirmation
    volume_weighting: bool = True  # Enable volume-weighted analysis
    
    # Internal state
    _flow_window: deque[tuple[float, float]] = field(init=False, repr=False)
    _momentum_window: deque[float] = field(init=False, repr=False)
    _tick_count: int = field(init=False, repr=False, default=0)
    
    def __post_init__(self) -> None:
        if self.window_size < 2:
            raise ValueError("window_size must be >= 2")
        if not (0.0 < self.imbalance_threshold <= 1.0):
            raise ValueError("imbalance_threshold must be in (0.0, 1.0]")
        if not (0.0 < self.confidence_scale <= 1.0):
            raise ValueError("confidence_scale must be in (0.0, 1.0]")
        if not (0.0 <= self.min_confidence <= 1.0):
            raise ValueError("min_confidence must be in [0.0, 1.0]")
        if self.momentum_window < 1:
            raise ValueError("momentum_window must be >= 1")
        
        self._flow_window = deque(maxlen=self.window_size)
        self._momentum_window = deque(maxlen=self.momentum_window)
    
    def on_tick(self, tick: MarketTick) -> Sequence[SignalEvent]:
        """Process a market tick and emit enhanced orderflow signals."""
        # Calculate signed flow
        mid = (tick.bid + tick.ask) / 2 if hasattr(tick, 'bid') and hasattr(tick, 'ask') else tick.last
        signed_flow = self._calculate_signed_flow(tick, mid)
        
        # Apply volume weighting if enabled
        if self.volume_weighting and hasattr(tick, 'volume'):
            signed_flow *= tick.volume
        
        # Update windows
        self._flow_window.append(signed_flow)
        self._momentum_window.append(signed_flow)
        self._tick_count += 1
        
        # Generate signals if we have enough data
        if len(self._flow_window) < self.window_size // 2:
            return []
        
        signals = []
        
        # Calculate enhanced imbalance
        imbalance = self._calculate_enhanced_imbalance()
        
        # Determine flow intensity
        intensity = self._classify_flow_intensity(imbalance)
        
        # Generate signal based on intensity
        if intensity != FlowIntensity.NEUTRAL:
            signal = self._generate_signal(tick, imbalance, intensity)
            if signal:
                signals.append(signal)
        
        return signals
    
    def _calculate_signed_flow(self, tick: MarketTick, mid: float) -> float:
        """Calculate signed dollar flow for the tick."""
        if hasattr(tick, 'volume') and hasattr(tick, 'last'):
            # Calculate price side
            if tick.last >= mid:
                side = 1.0  # Buy
            else:
                side = -1.0  # Sell
            
            return side * tick.last * tick.volume
        elif hasattr(tick, 'last'):
            # Fallback to price direction
            return 1.0 if tick.last >= mid else -1.0
        else:
            return 0.0
    
    def _calculate_enhanced_imbalance(self) -> float:
        """Calculate enhanced orderflow imbalance with momentum confirmation."""
        if not self._flow_window:
            return 0.0
        
        # Calculate basic imbalance
        total_flow = sum(self._flow_window)
        total_abs_flow = sum(abs(f) for f in self._flow_window)
        
        if total_abs_flow == 0:
            return 0.0
        
        basic_imbalance = total_flow / total_abs_flow
        
        # Apply momentum confirmation if available
        if len(self._momentum_window) >= self.momentum_window:
            momentum = sum(self._momentum_window) / len(self._momentum_window)
            momentum_factor = 0.3  # Weight of momentum in final calculation
            enhanced_imbalance = (1 - momentum_factor) * basic_imbalance + momentum_factor * (momentum / abs(momentum) if momentum != 0 else 0)
            return enhanced_imbalance
        
        return basic_imbalance
    
    def _classify_flow_intensity(self, imbalance: float) -> FlowIntensity:
        """Classify orderflow intensity level."""
        abs_imbalance = abs(imbalance)
        
        if abs_imbalance < self.imbalance_threshold:
            return FlowIntensity.NEUTRAL
        elif abs_imbalance < self.imbalance_threshold * 2:
            return FlowIntensity.MODERATE_BUYING if imbalance > 0 else FlowIntensity.MODERATE_SELLING
        elif abs_imbalance < self.imbalance_threshold * 3:
            return FlowIntensity.STRONG_BUYING if imbalance > 0 else FlowIntensity.STRONG_SELLING
        else:
            return FlowIntensity.EXTREME_BUYING if imbalance > 0 else FlowIntensity.EXTREME_SELLING
    
    def _generate_signal(self, tick: MarketTick, imbalance: float, intensity: FlowIntensity) -> SignalEvent | None:
        """Generate signal event based on flow intensity."""
        # Calculate confidence
        abs_imbalance = abs(imbalance)
        confidence = min(1.0, (abs_imbalance - self.imbalance_threshold) * self.confidence_scale)
        
        if confidence < self.min_confidence:
            return None
        
        # Determine side
        side_map = {
            FlowIntensity.EXTREME_BUYING: Side.BUY,
            FlowIntensity.STRONG_BUYING: Side.BUY,
            FlowIntensity.MODERATE_BUYING: Side.BUY,
            FlowIntensity.NEUTRAL: Side.HOLD,
            FlowIntensity.MODERATE_SELLING: Side.SELL,
            FlowIntensity.STRONG_SELLING: Side.SELL,
            FlowIntensity.EXTREME_SELLING: Side.SELL,
        }
        
        side = side_map.get(intensity, Side.HOLD)
        
        # Create signal with enhanced metadata
        return SignalEvent(
            source=self.name,
            timestamp_ns=tick.timestamp_ns,
            symbol=tick.symbol,
            side=side,
            confidence=confidence,
            reason=f"flow_intensity:{intensity.value}_imbalance:{imbalance:.3f}",
            metadata={
                "imbalance": imbalance,
                "intensity": intensity.value,
                "window_size": len(self._flow_window),
                "momentum_confirmed": len(self._momentum_window) >= self.momentum_window,
                "volume_weighted": self.volume_weighting
            }
        )
    
    def check_self(self) -> HealthStatus:
        """Health check for the enhanced plugin."""
        try:
            if len(self._flow_window) == 0:
                return HealthStatus(
                    engine_name=self.name,
                    state=HealthState.ALIVE,
                    detail=f"{self.name} v{self.version} lifecycle={self.lifecycle} window={self.window_size} (awaiting data)"
                )
            
            current_imbalance = self._calculate_enhanced_imbalance()
            current_intensity = self._classify_flow_intensity(current_imbalance)
            
            return HealthStatus(
                engine_name=self.name,
                state=HealthState.ALIVE,
                detail=f"{self.name} v{self.version} lifecycle={self.lifecycle} window={self.window_size} intensity={current_intensity.value} samples={len(self._flow_window)}"
            )
            
        except Exception as e:
            return HealthStatus(
                engine_name=self.name,
                state=HealthState.FAIL,
                detail=f"Health check failed: {str(e)}"
            )


__all__ = ["OrderflowImbalanceV2", "FlowIntensity"]