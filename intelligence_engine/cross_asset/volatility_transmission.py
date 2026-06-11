"""XAS-05 — Cross-asset volatility transmission analysis.

Models how volatility transmits between assets and markets, identifying
volatility spill-over effects and transmission channels. Essential for
risk management and hedging strategies.

Pure computation. No clocks, no I/O. INV-15 deterministic.
B1: No imports from execution_engine/governance_engine/learning_engine/evolution_engine.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any
from collections import deque


@dataclass(frozen=True, slots=True)
class VolatilitySpillover:
    """Volatility spillover from one asset to another."""
    source_asset: str
    target_asset: str
    transmission_strength: float  # 0.0 to 1.0
    lag_bars: int  # Typical lag in transmission
    significance: float  # Statistical significance
    direction: str  # "unidirectional", "bidirectional", "feedback"
    last_updated_ns: int


@dataclass(frozen=True, slots=True)
class VolatilityNetwork:
    """Network representation of volatility transmission relationships."""
    network_id: str
    assets: tuple[str, ...]
    spillovers: tuple[VolatilitySpillover, ...]
    central_assets: tuple[str, ...]  # Assets that are net volatility transmitters
    peripheral_assets: tuple[str, ...]  # Assets that are net volatility receivers
    network_density: float  # How connected the network is
    transmission_intensity: float  # Overall strength of transmissions
    timestamp_ns: int


@dataclass(frozen=True, slots=True)
class VolatilityTransmissionEvent:
    """Detected volatility transmission event."""
    event_id: str
    event_type: str  # "spillover", "contagion", "isolation", "network_shift"
    source_asset: str
    affected_assets: tuple[str, ...]
    magnitude: float  # Strength of transmission
    duration_bars: int  # Expected duration
    risk_implications: tuple[str, ...]
    timestamp_ns: int


class VolatilityTransmissionAnalyzer:
    """Analyzes volatility transmission between assets.
    
    Uses statistical methods to detect and quantify volatility spillovers,
identifying transmission channels and network structure.
    """
    
    def __init__(
        self,
        lookback_window: int = 60,
        significance_threshold: float = 0.05,
        min_transmission_strength: float = 0.1
    ) -> None:
        self._lookback_window = lookback_window
        self._significance_threshold = significance_threshold
        self._min_transmission_strength = min_transmission_strength
        
        self._price_history: dict[str, deque[float]] = {}
        self._volatility_history: dict[str, deque[float]] = {}
        self._spillover_history: deque[VolatilityNetwork] = deque(maxlen=20)
        self._event_history: deque[VolatilityTransmissionEvent] = deque(maxlen=50)
        
    def update_market_data(
        self,
        asset: str,
        price: float,
        timestamp_ns: int
    ) -> None:
        """Update price and volatility history for an asset."""
        if asset not in self._price_history:
            self._price_history[asset] = deque(maxlen=self._lookback_window)
            self._volatility_history[asset] = deque(maxlen=self._lookback_window)
        
        self._price_history[asset].append(price)
        
        # Calculate rolling volatility
        if len(self._price_history[asset]) >= 10:
            prices = list(self._price_history[asset])
            returns = [math.log(prices[i] / prices[i-1]) for i in range(1, len(prices))]
            volatility = math.sqrt(sum(r**2 for r in returns[-10:]) / 10) * math.sqrt(252)  # Annualized
            self._volatility_history[asset].append(volatility)
    
    def analyze_transmission_network(self, timestamp_ns: int) -> VolatilityNetwork:
        """Analyze current volatility transmission network.
        
        Args:
            timestamp_ns: Current timestamp
            
        Returns:
            Current volatility transmission network
        """
        assets = list(self._volatility_history.keys())
        if len(assets) < 2:
            return VolatilityNetwork(
                network_id="empty",
                assets=tuple(assets),
                spillovers=(),
                central_assets=(),
                peripheral_assets=(),
                network_density=0.0,
                transmission_intensity=0.0,
                timestamp_ns=timestamp_ns
            )
        
        # Calculate spillovers between all asset pairs
        spillovers = []
        for i, source in enumerate(assets):
            for target in assets[i+1:]:
                spillover = self._calculate_spillover(source, target, timestamp_ns)
                if spillover and spillover.transmission_strength >= self._min_transmission_strength:
                    spillovers.append(spillover)
                    
                    # Add reverse direction if bidirectional
                    reverse_spillover = self._calculate_spillover(target, source, timestamp_ns)
                    if reverse_spillover and reverse_spillover.transmission_strength >= self._min_transmission_strength:
                        if spillover.transmission_strength > reverse_spillover.transmission_strength:
                            spillovers.append(VolatilitySpillover(
                                source_asset=target,
                                target_asset=source,
                                transmission_strength=reverse_spillover.transmission_strength,
                                lag_bars=reverse_spillover.lag_bars,
                                significance=reverse_spillover.significance,
                                direction="bidirectional",
                                last_updated_ns=timestamp_ns
                            ))
                        else:
                            spillover = VolatilitySpillover(
                                source_asset=spillover.source_asset,
                                target_asset=spillover.target_asset,
                                transmission_strength=spillover.transmission_strength,
                                lag_bars=spillover.lag_bars,
                                significance=spillover.significance,
                                direction="bidirectional",
                                last_updated_ns=timestamp_ns
                            )
        
        # Identify central and peripheral assets
        transmission_scores = {asset: 0.0 for asset in assets}
        for spillover in spillovers:
            transmission_scores[spillover.source_asset] += spillover.transmission_strength
            transmission_scores[spillover.target_asset] -= spillover.transmission_strength * 0.5
        
        sorted_assets = sorted(assets, key=lambda a: transmission_scores[a], reverse=True)
        central_count = max(1, len(assets) // 3)
        central_assets = tuple(sorted_assets[:central_count])
        peripheral_assets = tuple(sorted_assets[central_count:])
        
        # Calculate network metrics
        possible_connections = len(assets) * (len(assets) - 1) / 2
        network_density = len(spillovers) / possible_connections if possible_connections > 0 else 0.0
        transmission_intensity = sum(s.transmission_strength for s in spillovers) / len(spillovers) if spillovers else 0.0
        
        network = VolatilityNetwork(
            network_id=f"network_{timestamp_ns}",
            assets=tuple(assets),
            spillovers=tuple(spillovers),
            central_assets=central_assets,
            peripheral_assets=peripheral_assets,
            network_density=network_density,
            transmission_intensity=transmission_intensity,
            timestamp_ns=timestamp_ns
        )
        
        self._spillover_history.append(network)
        
        # Detect significant events
        self._detect_transmission_events(network, timestamp_ns)
        
        return network
    
    def _calculate_spillover(
        self,
        source: str,
        target: str,
        timestamp_ns: int
    ) -> VolatilitySpillover | None:
        """Calculate volatility spillover from source to target."""
        if (source not in self._volatility_history or 
            target not in self._volatility_history):
            return None
        
        source_vol = list(self._volatility_history[source])
        target_vol = list(self._volatility_history[target])
        
        min_len = min(len(source_vol), len(target_vol))
        if min_len < 20:
            return None
        
        source_vol = source_vol[-min_len:]
        target_vol = target_vol[-min_len:]
        
        # Calculate Granger-causality-like measure
        # (simplified correlation of lagged source with current target)
        max_lag = 5
        best_lag = 0
        best_correlation = 0.0
        
        for lag in range(1, max_lag + 1):
            if lag >= min_len:
                continue
            
            # Correlate lagged source volatility with current target volatility
            lagged_source = source_vol[:-lag]
            current_target = target_vol[lag:]
            
            if len(lagged_source) < 10:
                continue
            
            correlation = self._correlation(lagged_source, current_target)
            if abs(correlation) > abs(best_correlation):
                best_correlation = correlation
                best_lag = lag
        
        # Calculate significance (simplified)
        significance = min(abs(best_correlation), 1.0)
        
        if significance < self._significance_threshold:
            return None
        
        direction = "unidirectional"
        if abs(best_correlation) > 0.3:
            direction = "feedback"
        
        return VolatilitySpillover(
            source_asset=source,
            target_asset=target,
            transmission_strength=abs(best_correlation),
            lag_bars=best_lag,
            significance=significance,
            direction=direction,
            last_updated_ns=timestamp_ns
        )
    
    def _correlation(self, xs: list[float], ys: list[float]) -> float:
        """Calculate correlation between two series."""
        n = len(xs)
        if n < 2 or n != len(ys):
            return 0.0
        
        mean_x = sum(xs) / n
        mean_y = sum(ys) / n
        
        cov = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys)) / n
        std_x = math.sqrt(sum((x - mean_x) ** 2 for x in xs) / n) or 1e-12
        std_y = math.sqrt(sum((y - mean_y) ** 2 for y in ys) / n) or 1e-12
        
        return max(-1.0, min(1.0, cov / (std_x * std_y)))
    
    def _detect_transmission_events(
        self,
        network: VolatilityNetwork,
        timestamp_ns: int
    ) -> None:
        """Detect significant volatility transmission events."""
        if len(self._spillover_history) < 2:
            return
        
        previous_network = self._spillover_history[-2]
        
        # Check for network density changes
        density_change = network.network_density - previous_network.network_density
        if abs(density_change) > 0.2:
            event_type = "network_shift"
            magnitude = abs(density_change)
            risk_implications = ["hedging_requirements_change", "portfolio_rebalance_needed"]
            
            self._event_history.append(VolatilityTransmissionEvent(
                event_id=f"event_{timestamp_ns}",
                event_type=event_type,
                source_asset="network",
                affected_assets=network.assets,
                magnitude=magnitude,
                duration_bars=10,
                risk_implications=tuple(risk_implications),
                timestamp_ns=timestamp_ns
            ))
        
        # Check for intense spillovers
        for spillover in network.spillovers:
            if spillover.transmission_strength > 0.7:
                event_type = "spillover"
                magnitude = spillover.transmission_strength
                risk_implications = ["volatility_inflation", "hedging_opportunity"]
                
                self._event_history.append(VolatilityTransmissionEvent(
                    event_id=f"spillover_{timestamp_ns}_{spillover.source_asset}_{spillover.target_asset}",
                    event_type=event_type,
                    source_asset=spillover.source_asset,
                    affected_assets=(spillover.target_asset,),
                    magnitude=magnitude,
                    duration_bars=spillover.lag_bars * 2,
                    risk_implications=tuple(risk_implications),
                    timestamp_ns=timestamp_ns
                ))
    
    def get_current_network(self) -> VolatilityNetwork | None:
        """Get current volatility transmission network."""
        return self._spillover_history[-1] if self._spillover_history else None
    
    def get_recent_events(self, limit: int = 10) -> tuple[VolatilityTransmissionEvent, ...]:
        """Get recent volatility transmission events."""
        return tuple(list(self._event_history)[-limit:])
    
    def get_asset_transmission_profile(self, asset: str) -> dict[str, Any]:
        """Get volatility transmission profile for a specific asset."""
        if not self._spillover_history:
            return {}
        
        latest_network = self._spillover_history[-1]
        
        outgoing_spillovers = [
            s for s in latest_network.spillovers if s.source_asset == asset
        ]
        incoming_spillovers = [
            s for s in latest_network.spillovers if s.target_asset == asset
        ]
        
        return {
            "asset": asset,
            "is_central": asset in latest_network.central_assets,
            "is_peripheral": asset in latest_network.peripheral_assets,
            "outgoing_count": len(outgoing_spillovers),
            "incoming_count": len(incoming_spillovers),
            "outgoing_strength": sum(s.transmission_strength for s in outgoing_spillovers),
            "incoming_strength": sum(s.transmission_strength for s in incoming_spillovers),
            "net_transmission_strength": (
                sum(s.transmission_strength for s in outgoing_spillovers) -
                sum(s.transmission_strength for s in incoming_spillovers)
            )
        }


__all__ = [
    "VolatilitySpillover",
    "VolatilityNetwork",
    "VolatilityTransmissionEvent",
    "VolatilityTransmissionAnalyzer"
]