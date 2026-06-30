"""
DIX VISION Causal Discovery for Market Relationships

Applies the existing advanced causal discovery algorithms to discover
causal relationships in market data for better trading decisions.
"""

from __future__ import annotations

import logging
import threading
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd

# Import existing causal discovery
import sys
sys.path.insert(0, "c:/dix_vision_v42.2/containers/system_core/cognitive_os/causal")
from advanced_causal_discovery import (
    AdvancedCausalDiscovery,
    CausalAlgorithm,
    CausalType,
    CausalStrength,
    CausalRelation,
    CausalGraph,
    CausalIntervention
)

logger = logging.getLogger(__name__)


@dataclass
class MarketCausalRelation:
    """Causal relationship between market variables."""
    relation_id: str
    cause_variable: str  # e.g., "RSI", "Volume", "News_Sentiment"
    effect_variable: str  # e.g., "Price", "Volatility", "Trading_Volume"
    causal_type: CausalType
    strength: float
    strength_level: CausalStrength
    confidence: float
    causal_effect: float
    time_lag: Optional[float]  # hours
    market_context: Dict[str, Any]
    timestamp: float


@dataclass
class MarketCausalGraph:
    """Causal graph for market relationships."""
    graph_id: str
    market: str
    nodes: List[str]  # Market variables
    edges: List[MarketCausalRelation]
    is_dag: bool
    graph_properties: Dict[str, Any]
    timestamp: float


@dataclass
class MarketCausalIntervention:
    """Causal intervention simulation for trading."""
    intervention_id: str
    target_variable: str
    intervention_type: str
    intervention_value: float
    expected_price_effect: float
    expected_volatility_effect: float
    trading_implication: str
    confidence: float
    timestamp: float


class MarketCausalDiscovery:
    """
    Applies causal discovery to market data for trading insights.
    
    Uses existing causal discovery algorithms to discover:
    - Price drivers (what causes price movements)
    - Volatility triggers (what causes volatility spikes)
    - Volume patterns (what causes volume changes)
    - Cross-asset relationships (causal links between assets)
    """
    
    def __init__(self):
        # Initialize causal discovery engine
        self._causal_discovery = AdvancedCausalDiscovery()
        
        # Market-specific causal graphs
        self._market_graphs: Dict[str, MarketCausalGraph] = {}
        
        # Historical causal relationships
        self._causal_history: deque = deque(maxlen=1000)
        
        # Intervention results
        self._intervention_results: Dict[str, MarketCausalIntervention] = {}
        
        # Market variables mapping
        self._market_variables = {
            "price": "Price",
            "volume": "Trading Volume",
            "volatility": "Volatility",
            "rsi": "RSI",
            "macd": "MACD",
            "sentiment": "News Sentiment",
            "interest_rate": "Interest Rate",
            "inflation": "Inflation Rate",
            "gdp": "GDP Growth",
            "unemployment": "Unemployment Rate"
        }
        
        self._lock = threading.Lock()
        
        logger.info("Market Causal Discovery initialized")
    
    def prepare_market_data(self, market_data: Dict[str, Any]) -> pd.DataFrame:
        """Prepare market data for causal discovery."""
        # Extract relevant variables
        data_dict = {}
        
        for var_key, var_name in self._market_variables.items():
            if var_key in market_data:
                data_dict[var_name] = [market_data[var_key]]
            else:
                # Generate default values for missing variables
                data_dict[var_name] = [self._get_default_value(var_key)]
        
        return pd.DataFrame(data_dict)
    
    def _get_default_value(self, var_key: str) -> float:
        """Get default value for missing market variable."""
        defaults = {
            "price": 100.0,
            "volume": 1000000.0,
            "volatility": 0.2,
            "rsi": 50.0,
            "macd": 0.0,
            "sentiment": 0.0,
            "interest_rate": 0.05,
            "inflation": 0.02,
            "gdp": 0.03,
            "unemployment": 0.05
        }
        return defaults.get(var_key, 0.0)
    
    def discover_causal_relationships(self, market: str, 
                                     market_data: Dict[str, Any],
                                     algorithm: CausalAlgorithm = CausalAlgorithm.PC_ALGORITHM) -> MarketCausalGraph:
        """Discover causal relationships in market data."""
        # Prepare data
        df = self.prepare_market_data(market_data)
        
        # Apply causal discovery
        causal_graph = self._causal_discovery.discover_causal_graph(
            data=df,
            algorithm=algorithm
        )
        
        # Convert to market-specific causal graph
        market_graph = self._convert_to_market_graph(market, causal_graph, market_data)
        
        with self._lock:
            self._market_graphs[market] = market_graph
            self._causal_history.append(market_graph)
        
        logger.info(f"Discovered {len(market_graph.edges)} causal relationships for {market}")
        
        return market_graph
    
    def _convert_to_market_graph(self, market: str, 
                                causal_graph: CausalGraph,
                                market_data: Dict[str, Any]) -> MarketCausalGraph:
        """Convert general causal graph to market-specific graph."""
        market_edges = []
        
        for edge in causal_graph.edges:
            market_edge = MarketCausalRelation(
                relation_id=f"{market}_{edge.relation_id}",
                cause_variable=edge.cause_variable,
                effect_variable=edge.effect_variable,
                causal_type=edge.causal_type,
                strength=edge.strength,
                strength_level=edge.strength_level,
                confidence=edge.confidence,
                causal_effect=edge.causal_effect,
                time_lag=edge.time_lag,
                market_context={
                    "market": market,
                    "timestamp": datetime.now().isoformat(),
                    "data_context": market_data
                },
                timestamp=datetime.now().timestamp()
            )
            market_edges.append(market_edge)
        
        return MarketCausalGraph(
            graph_id=f"{market}_causal_graph",
            market=market,
            nodes=causal_graph.nodes,
            edges=market_edges,
            is_dag=causal_graph.is_dag,
            graph_properties=causal_graph.graph_properties,
            timestamp=datetime.now().timestamp()
        )
    
    def analyze_price_drivers(self, market: str) -> List[MarketCausalRelation]:
        """Analyze what variables are causal drivers of price."""
        if market not in self._market_graphs:
            return []
        
        graph = self._market_graphs[market]
        
        # Find all causal relations where effect is "Price"
        price_drivers = [
            edge for edge in graph.edges
            if edge.effect_variable == "Price"
        ]
        
        # Sort by strength
        price_drivers.sort(key=lambda x: x.strength, reverse=True)
        
        return price_drivers
    
    def analyze_volatility_triggers(self, market: str) -> List[MarketCausalRelation]:
        """Analyze what variables trigger volatility."""
        if market not in self._market_graphs:
            return []
        
        graph = self._market_graphs[market]
        
        # Find all causal relations where effect is "Volatility"
        volatility_triggers = [
            edge for edge in graph.edges
            if edge.effect_variable == "Volatility"
        ]
        
        # Sort by strength
        volatility_triggers.sort(key=lambda x: x.strength, reverse=True)
        
        return volatility_triggers
    
    def simulate_intervention(self, market: str, target_variable: str,
                            intervention_value: float) -> MarketCausalIntervention:
        """Simulate a causal intervention for trading."""
        if market not in self._market_graphs:
            return None
        
        graph = self._market_graphs[market]
        
        # Find causal chain from target to price/volatility
        price_effects = []
        volatility_effects = []
        
        for edge in graph.edges:
            if edge.cause_variable == target_variable:
                if edge.effect_variable == "Price":
                    price_effects.append(edge)
                elif edge.effect_variable == "Volatility":
                    volatility_effects.append(edge)
        
        # Calculate expected effects
        expected_price_effect = sum(
            edge.causal_effect * intervention_value 
            for edge in price_effects
        ) if price_effects else 0.0
        
        expected_volatility_effect = sum(
            edge.causal_effect * intervention_value 
            for edge in volatility_effects
        ) if volatility_effects else 0.0
        
        # Determine trading implication
        if expected_price_effect > 0.1:
            trading_implication = "BUY signal expected"
        elif expected_price_effect < -0.1:
            trading_implication = "SELL signal expected"
        else:
            trading_implication = "No significant price effect expected"
        
        # Calculate confidence based on edge confidences
        all_edges = price_effects + volatility_effects
        confidence = np.mean([edge.confidence for edge in all_edges]) if all_edges else 0.0
        
        intervention = MarketCausalIntervention(
            intervention_id=f"{market}_{target_variable}_intervention",
            target_variable=target_variable,
            intervention_type="do",
            intervention_value=intervention_value,
            expected_price_effect=expected_price_effect,
            expected_volatility_effect=expected_volatility_effect,
            trading_implication=trading_implication,
            confidence=confidence,
            timestamp=datetime.now().timestamp()
        )
        
        with self._lock:
            self._intervention_results[intervention.intervention_id] = intervention
        
        return intervention
    
    def get_causal_insights(self, market: str) -> Dict[str, Any]:
        """Get comprehensive causal insights for a market."""
        if market not in self._market_graphs:
            return {"error": f"No causal graph found for {market}"}
        
        graph = self._market_graphs[market]
        
        price_drivers = self.analyze_price_drivers(market)
        volatility_triggers = self.analyze_volatility_triggers(market)
        
        return {
            "market": market,
            "total_causal_relations": len(graph.edges),
            "is_dag": graph.is_dag,
            "price_drivers": [
                {
                    "variable": driver.cause_variable,
                    "strength": driver.strength,
                    "confidence": driver.confidence,
                    "effect": driver.causal_effect
                }
                for driver in price_drivers[:5]  # Top 5 drivers
            ],
            "volatility_triggers": [
                {
                    "variable": trigger.cause_variable,
                    "strength": trigger.strength,
                    "confidence": trigger.confidence,
                    "effect": trigger.causal_effect
                }
                for trigger in volatility_triggers[:5]  # Top 5 triggers
            ],
            "graph_properties": graph.graph_properties,
            "timestamp": graph.timestamp
        }
    
    def get_cross_asset_causality(self, market1: str, market2: str) -> Optional[Dict[str, Any]]:
        """Analyze causal relationships between two markets."""
        if market1 not in self._market_graphs or market2 not in self._market_graphs:
            return None
        
        graph1 = self._market_graphs[market1]
        graph2 = self._market_graphs[market2]
        
        # Find cross-asset causal links
        cross_asset_links = []
        
        for edge1 in graph1.edges:
            for edge2 in graph2.edges:
                # Check if same variable appears in both graphs
                if edge1.cause_variable == edge2.cause_variable:
                    cross_asset_links.append({
                        "variable": edge1.cause_variable,
                        "market1_effect": edge1.effect_variable,
                        "market2_effect": edge2.effect_variable,
                        "combined_strength": (edge1.strength + edge2.strength) / 2
                    })
        
        return {
            "market1": market1,
            "market2": market2,
            "cross_asset_links": cross_asset_links,
            "correlation_strength": np.mean([link["combined_strength"] for link in cross_asset_links]) if cross_asset_links else 0.0
        }
    
    def update_causal_graph(self, market: str, new_data: Dict[str, Any]) -> MarketCausalGraph:
        """Update causal graph with new market data."""
        # Re-discover causal relationships with new data
        updated_graph = self.discover_causal_relationships(market, new_data)
        
        logger.info(f"Updated causal graph for {market}")
        
        return updated_graph


class CausalTradingStrategy:
    """
    Trading strategy based on causal discovery insights.
    
    Uses causal relationships to make informed trading decisions
    by understanding what actually drives market movements.
    """
    
    def __init__(self):
        self._causal_discovery = MarketCausalDiscovery()
        self._intervention_history: List[MarketCausalIntervention] = []
        
        self._lock = threading.Lock()
        
        logger.info("Causal Trading Strategy initialized")
    
    def generate_causal_signal(self, market: str, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate trading signal based on causal insights."""
        # Discover causal relationships
        causal_graph = self._causal_discovery.discover_causal_relationships(
            market, market_data
        )
        
        # Analyze price drivers
        price_drivers = self._causal_discovery.analyze_price_drivers(market)
        
        # Analyze volatility triggers
        volatility_triggers = self._causal_discovery.analyze_volatility_triggers(market)
        
        # Generate signal based on causal insights
        signal = self._generate_signal_from_causality(price_drivers, volatility_triggers, market_data)
        
        return {
            "market": market,
            "signal": signal,
            "causal_insights": {
                "price_drivers": len(price_drivers),
                "volatility_triggers": len(volatility_triggers),
                "top_price_driver": price_drivers[0].cause_variable if price_drivers else None,
                "top_volatility_trigger": volatility_triggers[0].cause_variable if volatility_triggers else None
            },
            "confidence": self._calculate_causal_confidence(price_drivers, volatility_triggers)
        }
    
    def _generate_signal_from_causality(self, price_drivers: List[MarketCausalRelation],
                                      volatility_triggers: List[MarketCausalRelation],
                                      market_data: Dict[str, Any]) -> str:
        """Generate trading signal from causal relationships."""
        if not price_drivers:
            return "HOLD"
        
        # Check top price driver's current value
        top_driver = price_drivers[0]
        driver_value = market_data.get(self._get_var_key(top_driver.cause_variable), 0.0)
        
        # Simple causal logic
        if top_driver.causal_effect > 0 and driver_value > 0:
            return "BUY"
        elif top_driver.causal_effect < 0 and driver_value < 0:
            return "SELL"
        else:
            return "HOLD"
    
    def _get_var_key(self, var_name: str) -> str:
        """Get variable key from variable name."""
        var_mapping = {
            "Price": "price",
            "Trading Volume": "volume",
            "Volatility": "volatility",
            "RSI": "rsi",
            "MACD": "macd",
            "News Sentiment": "sentiment"
        }
        return var_mapping.get(var_name, var_name.lower())
    
    def _calculate_causal_confidence(self, price_drivers: List[MarketCausalRelation],
                                    volatility_triggers: List[MarketCausalRelation]) -> float:
        """Calculate confidence based on causal relationship strength."""
        all_relations = price_drivers + volatility_triggers
        
        if not all_relations:
            return 0.0
        
        # Weight by strength and confidence
        weighted_confidence = np.mean([
            relation.strength * relation.confidence 
            for relation in all_relations
        ])
        
        return weighted_confidence
    
    def simulate_causal_intervention(self, market: str, variable: str, 
                                   value: float) -> MarketCausalIntervention:
        """Simulate a causal intervention for trading."""
        intervention = self._causal_discovery.simulate_intervention(
            market, variable, value
        )
        
        with self._lock:
            self._intervention_history.append(intervention)
        
        return intervention


# Global instances
_market_causal_discovery: Optional[MarketCausalDiscovery] = None
_causal_trading_strategy: Optional[CausalTradingStrategy] = None


def get_market_causal_discovery() -> MarketCausalDiscovery:
    """Get global market causal discovery instance."""
    global _market_causal_discovery
    if _market_causal_discovery is None:
        _market_causal_discovery = MarketCausalDiscovery()
    return _market_causal_discovery


def get_causal_trading_strategy() -> CausalTradingStrategy:
    """Get global causal trading strategy instance."""
    global _causal_trading_strategy
    if _causal_trading_strategy is None:
        _causal_trading_strategy = CausalTradingStrategy()
    return _causal_trading_strategy