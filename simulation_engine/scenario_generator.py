"""
simulation_engine.scenario_generator
DIX VISION v42.2 — Production-Grade Scenario Generator

Scenario generation with market stress scenarios, regime transitions,
liquidity events, and production-ready scenario management.
"""

from __future__ import annotations

import logging
import random
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum

from system.time_source import now

logger = logging.getLogger(__name__)


class ScenarioType(Enum):
    """Types of simulation scenarios."""
    MARKET_STRESS = "market_stress"
    REGIME_TRANSITION = "regime_transition"
    LIQUIDITY_CRISIS = "liquidity_crisis"
    VOLATILITY_SPIKE = "volatility_spike"
    CORRELATION_BREAK = "correlation_break"
    FLASH_CRASH = "flash_crash"
    NEWS_DRIVEN = "news_driven"
    ORDER_FLOW_IMBALANCE = "order_flow_imbalance"


@dataclass
class Scenario:
    """A simulation scenario with full parameterization."""
    scenario_id: str
    scenario_type: ScenarioType
    parameters: Dict[str, Any] = field(default_factory=dict)
    description: str = ""
    probability: float = 0.0
    severity: float = 0.0
    affected_assets: List[str] = field(default_factory=list)
    timestamp: str = ""


@dataclass
class MarketConditions:
    """Market conditions for scenario."""
    volatility: float = 0.2
    liquidity: float = 1.0
    correlation: float = 0.5
    trend: float = 0.0
    volume_multiplier: float = 1.0


@dataclass
class StressParameters:
    """Parameters for stress scenarios."""
    shock_magnitude: float = 0.1
    duration_bars: int = 100
    recovery_bars: int = 200
    cascade_probability: float = 0.3
    contagion_assets: List[str] = field(default_factory=list)


class ProductionScenarioGenerator:
    """Production-grade scenario generator.
    
    Generates realistic market scenarios for:
    - Stress testing
    - Backtesting under adverse conditions
    - Strategy robustness validation
    - Risk limit evaluation
    """
    
    def __init__(self) -> None:
        self._scenarios: List[Scenario] = []
        self._historical_scenarios: Dict[str, Scenario] = {}
        self._scenario_templates = self._initialize_templates()
        
    def start(self) -> bool:
        logger.info("[SCENARIO_GENERATOR] Production scenario generator started")
        return True
    
    def stop(self) -> bool:
        logger.info("[SCENARIO_GENERATOR] Production scenario generator stopped")
        return True
    
    def generate_market_stress_scenario(
        self,
        base_conditions: MarketConditions,
        stress_params: Optional[StressParameters] = None,
        affected_assets: Optional[List[str]] = None
    ) -> Scenario:
        """Generate a market stress scenario.
        
        Creates realistic market stress including:
        - Increased volatility
        - Decreased liquidity
        - Correlated price movements
        - Potential cascade effects
        """
        stress_params = stress_params or StressParameters()
        affected_assets = affected_assets or ["BTC-USD", "ETH-USD"]
        
        # Calculate stress impact on conditions
        stressed_volatility = base_conditions.volatility * (1 + stress_params.shock_magnitude)
        stressed_liquidity = base_conditions.liquidity * (1 - stress_params.shock_magnitude * 0.5)
        stressed_correlation = min(1.0, base_conditions.correlation + stress_params.shock_magnitude * 0.3)
        
        parameters = {
            "base_volatility": base_conditions.volatility,
            "stressed_volatility": stressed_volatility,
            "base_liquidity": base_conditions.liquidity,
            "stressed_liquidity": stressed_liquidity,
            "correlation": stressed_correlation,
            "duration_bars": stress_params.duration_bars,
            "recovery_bars": stress_params.recovery_bars,
            "cascade_probability": stress_params.cascade_probability,
            "contagion_assets": stress_params.contagion_assets or []
        }
        
        scenario = Scenario(
            scenario_id=f"stress_{now().sequence}",
            scenario_type=ScenarioType.MARKET_STRESS,
            parameters=parameters,
            description=f"Market stress scenario: {stress_params.shock_magnitude:.1%} shock over {stress_params.duration_bars} bars",
            probability=self._estimate_stress_probability(stress_params),
            severity=stress_params.shock_magnitude,
            affected_assets=affected_assets,
            timestamp=now().utc_time.isoformat()
        )
        
        self._scenarios.append(scenario)
        logger.info(f"[SCENARIO_GENERATOR] Generated stress scenario: {scenario.scenario_id}")
        return scenario
    
    def generate_regime_transition_scenario(
        self,
        from_regime: str,
        to_regime: str,
        transition_duration: int = 50,
        affected_assets: Optional[List[str]] = None
    ) -> Scenario:
        """Generate a regime transition scenario.
        
        Simulates realistic transitions between market regimes:
        - Bull to neutral
        - Neutral to bear
        - Bear to bull
        - High to low volatility
        """
        affected_assets = affected_assets or ["BTC-USD"]
        
        # Calculate transition parameters
        regime_drift = self._calculate_regime_drift(from_regime, to_regime)
        transition_speed = 1.0 / transition_duration
        
        parameters = {
            "from_regime": from_regime,
            "to_regime": to_regime,
            "transition_duration": transition_duration,
            "transition_speed": transition_speed,
            "regime_drift": regime_drift,
            "volatility_impact": self._estimate_volatility_change(from_regime, to_regime),
            "correlation_impact": self._estimate_correlation_change(from_regime, to_regime)
        }
        
        scenario = Scenario(
            scenario_id=f"regime_{now().sequence}",
            scenario_type=ScenarioType.REGIME_TRANSITION,
            parameters=parameters,
            description=f"Regime transition: {from_regime} → {to_regime} over {transition_duration} bars",
            probability=self._estimate_transition_probability(from_regime, to_regime),
            severity=abs(regime_drift),
            affected_assets=affected_assets,
            timestamp=now().utc_time.isoformat()
        )
        
        self._scenarios.append(scenario)
        logger.info(f"[SCENARIO_GENERATOR] Generated regime scenario: {scenario.scenario_id}")
        return scenario
    
    def generate_volatility_spike_scenario(
        self,
        base_volatility: float,
        spike_magnitude: float,
        duration: int = 20,
        affected_assets: Optional[List[str]] = None
    ) -> Scenario:
        """Generate a volatility spike scenario.
        
        Simulates sudden volatility increases such as:
        - News-driven volatility spikes
        - Market opening volatility
        - Event-driven volatility
        """
        affected_assets = affected_assets or ["BTC-USD"]
        
        peak_volatility = base_volatility * (1 + spike_magnitude)
        decay_rate = spike_magnitude / duration
        
        parameters = {
            "base_volatility": base_volatility,
            "peak_volatility": peak_volatility,
            "spike_magnitude": spike_magnitude,
            "duration": duration,
            "decay_rate": decay_rate,
            "decay_model": "exponential"
        }
        
        scenario = Scenario(
            scenario_id=f"vol_spike_{now().sequence}",
            scenario_type=ScenarioType.VOLATILITY_SPIKE,
            parameters=parameters,
            description=f"Volatility spike: {base_volatility:.2%} → {peak_volatility:.2%} over {duration} bars",
            probability=self._estimate_volatility_spike_probability(spike_magnitude),
            severity=spike_magnitude,
            affected_assets=affected_assets,
            timestamp=now().utc_time.isoformat()
        )
        
        self._scenarios.append(scenario)
        logger.info(f"[SCENARIO_GENERATOR] Generated volatility spike scenario: {scenario.scenario_id}")
        return scenario
    
    def generate_liquidity_crisis_scenario(
        self,
        normal_liquidity: float,
        crisis_depth: float,
        duration: int = 100,
        affected_assets: Optional[List[str]] = None
    ) -> Scenario:
        """Generate a liquidity crisis scenario.
        
        Simulates liquidity drying up such as:
        - Market freeze conditions
        - Order book thinning
        - Spread widening
        """
        affected_assets = affected_assets or ["BTC-USD"]
        
        min_liquidity = normal_liquidity * (1 - crisis_depth)
        spread_multiplier = 1 + crisis_depth * 2.0
        
        parameters = {
            "normal_liquidity": normal_liquidity,
            "min_liquidity": min_liquidity,
            "crisis_depth": crisis_depth,
            "duration": duration,
            "spread_multiplier": spread_multiplier,
            "recovery_speed": 0.02
        }
        
        scenario = Scenario(
            scenario_id=f"liq_crisis_{now().sequence}",
            scenario_type=ScenarioType.LIQUIDITY_CRISIS,
            parameters=parameters,
            description=f"Liquidity crisis: {normal_liquidity:.2f} → {min_liquidity:.2f} over {duration} bars",
            probability=self._estimate_liquidity_crisis_probability(crisis_depth),
            severity=crisis_depth,
            affected_assets=affected_assets,
            timestamp=now().utc_time.isoformat()
        )
        
        self._scenarios.append(scenario)
        logger.info(f"[SCENARIO_GENERATOR] Generated liquidity crisis scenario: {scenario.scenario_id}")
        return scenario
    
    def generate_correlation_break_scenario(
        self,
        normal_correlation: float,
        break_magnitude: float,
        affected_pairs: Optional[List[tuple[str, str]]] = None
    ) -> Scenario:
        """Generate a correlation breakdown scenario.
        
        Simulates when normally correlated assets decouple:
        - BTC vs ETH
        - Crypto vs SPX
        - Crypto vs Gold
        """
        affected_pairs = affected_pairs or [("BTC-USD", "ETH-USD")]
        
        min_correlation = max(-1.0, normal_correlation - break_magnitude)
        
        parameters = {
            "normal_correlation": normal_correlation,
            "min_correlation": min_correlation,
            "break_magnitude": break_magnitude,
            "affected_pairs": affected_pairs,
            "duration": random.randint(30, 90)
        }
        
        scenario = Scenario(
            scenario_id=f"corr_break_{now().sequence}",
            scenario_type=ScenarioType.CORRELATION_BREAK,
            parameters=parameters,
            description=f"Correlation break: {normal_correlation:.2f} → {min_correlation:.2f}",
            probability=self._estimate_correlation_break_probability(break_magnitude),
            severity=break_magnitude,
            affected_assets=[f"{a1}/{a2}" for a1, a2 in affected_pairs],
            timestamp=now().utc_time.isoformat()
        )
        
        self._scenarios.append(scenario)
        logger.info(f"[SCENARIO_GENERATOR] Generated correlation break scenario: {scenario.scenario_id}")
        return scenario
    
    def get_scenario(self, scenario_id: str) -> Optional[Scenario]:
        """Get a scenario by ID."""
        for scenario in self._scenarios:
            if scenario.scenario_id == scenario_id:
                return scenario
        return None
    
    def get_scenarios_by_type(self, scenario_type: ScenarioType) -> List[Scenario]:
        """Get all scenarios of a specific type."""
        return [s for s in self._scenarios if s.scenario_type == scenario_type]
    
    def _estimate_stress_probability(self, stress_params: StressParameters) -> float:
        """Estimate probability of stress scenario."""
        base_probability = 0.05  # 5% base probability
        magnitude_factor = min(stress_params.shock_magnitude, 0.5) * 0.1
        return min(0.3, base_probability + magnitude_factor)
    
    def _estimate_transition_probability(self, from_regime: str, to_regime: str) -> float:
        """Estimate probability of regime transition."""
        return 0.15  # 15% probability for any given transition
    
    def _estimate_volatility_spike_probability(self, magnitude: float) -> float:
        """Estimate probability of volatility spike."""
        return min(0.25, 0.1 * magnitude)
    
    def _estimate_liquidity_crisis_probability(self, depth: float) -> float:
        """Estimate probability of liquidity crisis."""
        return min(0.1, 0.05 * depth)
    
    def _estimate_correlation_break_probability(self, magnitude: float) -> float:
        """Estimate probability of correlation break."""
        return min(0.2, 0.1 * magnitude)
    
    def _calculate_regime_drift(self, from_regime: str, to_regime: str) -> float:
        """Calculate regime drift magnitude."""
        regime_values = {"bull": 1.0, "neutral": 0.0, "bear": -1.0}
        from_val = regime_values.get(from_regime.lower(), 0.0)
        to_val = regime_values.get(to_regime.lower(), 0.0)
        return abs(to_val - from_val)
    
    def _estimate_volatility_change(self, from_regime: str, to_regime: str) -> float:
        """Estimate volatility change during regime transition."""
        if from_regime.lower() == "bear" and to_regime.lower() == "bull":
            return 0.3  # Volatility typically decreases
        if from_regime.lower() == "neutral" and to_regime.lower() == "bear":
            return 0.2  # Volatility increases
        return 0.1
    
    def _estimate_correlation_change(self, from_regime: str, to_regime: str) -> float:
        """Estimate correlation change during regime transition."""
        if from_regime.lower() == "neutral" and to_regime.lower() == "bear":
            return 0.3  # Correlations often increase during stress
        return 0.1
    
    def _initialize_templates(self) -> Dict[str, Dict[str, Any]]:
        """Initialize scenario templates."""
        return {
            "moderate_stress": {
                "shock_magnitude": 0.1,
                "duration_bars": 50,
                "cascade_probability": 0.2
            },
            "severe_stress": {
                "shock_magnitude": 0.25,
                "duration_bars": 100,
                "cascade_probability": 0.5
            },
            "extreme_stress": {
                "shock_magnitude": 0.5,
                "duration_bars": 200,
                "cascade_probability": 0.8
            }
        }


def get_production_scenario_generator() -> ProductionScenarioGenerator:
    """Get the singleton production scenario generator instance."""
    if not hasattr(get_production_scenario_generator, "_instance"):
        get_production_scenario_generator._instance = ProductionScenarioGenerator()
    return get_production_scenario_generator._instance