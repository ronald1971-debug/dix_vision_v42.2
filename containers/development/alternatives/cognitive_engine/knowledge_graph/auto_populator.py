"""
cognitive_engine.knowledge_graph.auto_populator
DIX VISION v42.2 — Knowledge Graph Auto-Population

Automatically populates the knowledge graph from trading data, market conditions,
and system operations. Extracts relationships and patterns to build comprehensive
market understanding.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from cognitive_engine.knowledge_graph.edge import EdgeType, KnowledgeEdge
from cognitive_engine.knowledge_graph.graph import KnowledgeGraph
from cognitive_engine.knowledge_graph.node import KnowledgeNode, NodeType
from system.time_source import now

logger = logging.getLogger(__name__)


@dataclass
class KnowledgeExtraction:
    """Extracted knowledge from a data source."""
    
    source_type: str  # "trade" | "market" | "news" | "system"
    entities: list[dict[str, Any]]
    relationships: list[dict[str, Any]]
    confidence: float
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = now().utc_time.isoformat()


class KnowledgeGraphAutoPopulator:
    """Automatically populates knowledge graph from system data.
    
    Extracts and structures knowledge from:
    - Executed trades (trader-strategy relationships)
    - Market conditions (regime detection)
    - News and narratives (market themes)
    - System operations (performance patterns)
    """

    def __init__(self, knowledge_graph: KnowledgeGraph) -> None:
        self._kg = knowledge_graph
        self._extractions_count = 0
        self._last_population_time = None

    def update_from_trade(self, trade_event: dict[str, Any]) -> KnowledgeExtraction:
        """Extract and store knowledge from an executed trade.
        
        Identifies:
        - Trader-strategy relationships
        - Strategy performance patterns
        - Asset liquidity characteristics
        - Execution quality metrics
        """
        try:
            entities = []
            relationships = []
            
            # Extract basic trade information
            asset = trade_event.get("asset", "")
            strategy = trade_event.get("strategy", "default")
            side = trade_event.get("side", "")
            size_usd = trade_event.get("size_usd", 0.0)
            execution_quality = trade_event.get("execution_quality", 1.0)
            
            # Create or get strategy node
            strategy_node = self._get_or_create_strategy_node(strategy, trade_event)
            entities.append({"node_id": strategy_node.node_id, "type": "strategy"})
            
            # Create or get asset node
            asset_node = self._get_or_create_asset_node(asset, trade_event)
            entities.append({"node_id": asset_node.node_id, "type": "asset"})
            
            # Connect strategy to asset
            if side == "BUY":
                self._kg.add_edge(
                    strategy_node.node_id,
                    asset_node.node_id,
                    EdgeType.TRADES,
                    strength=min(1.0, size_usd / 10000.0),
                    evidence=f"buy_order_{now().sequence}"
                )
                relationships.append({
                    "source": strategy_node.node_id,
                    "target": asset_node.node_id,
                    "type": "TRADES",
                    "side": "BUY"
                })
            elif side == "SELL":
                self._kg.add_edge(
                    strategy_node.node_id,
                    asset_node.node_id,
                    EdgeType.TRADES,
                    strength=min(1.0, size_usd / 10000.0),
                    evidence=f"sell_order_{now().sequence}"
                )
                relationships.append({
                    "source": strategy_node.node_id,
                    "target": asset_node.node_id,
                    "type": "TRADES",
                    "side": "SELL"
                })
            
            # Extract performance knowledge
            if execution_quality > 0.8:
                self._update_strategy_performance(strategy_node, "high_execution_quality")
            elif execution_quality < 0.5:
                self._update_strategy_performance(strategy_node, "low_execution_quality")
            
            self._extractions_count += 1
            self._last_population_time = now().utc_time.isoformat()
            
            logger.debug(
                f"[KG_AUTO] Populated knowledge from trade: {strategy} {side} {asset}"
            )
            
            return KnowledgeExtraction(
                source_type="trade",
                entities=entities,
                relationships=relationships,
                confidence=execution_quality
            )
            
        except Exception as e:
            logger.error(f"[KG_AUTO] Failed to extract knowledge from trade: {e}")
            return KnowledgeExtraction(
                source_type="trade",
                entities=[],
                relationships=[],
                confidence=0.0
            )

    def update_from_market(self, market_data: dict[str, Any]) -> KnowledgeExtraction:
        """Extract knowledge from market data.
        
        Identifies:
        - Regime conditions (volatility, trends)
        - Cross-asset correlations
        - Market anomaly patterns
        - Liquidity conditions
        """
        try:
            entities = []
            relationships = []
            
            asset = market_data.get("asset", "")
            signal = market_data.get("signal", 0.0)
            volatility = abs(signal)
            
            # Detect regime
            if volatility > 0.8:
                regime = "high_volatility"
            elif signal > 0.5:
                regime = "bullish_trend"
            elif signal < -0.5:
                regime = "bearish_trend"
            else:
                regime = "neutral"
            
            # Get or create regime node
            regime_node = self._get_or_create_regime_node(regime, market_data)
            entities.append({"node_id": regime_node.node_id, "type": "regime"})
            
            # Get or create asset node
            asset_node = self._get_or_create_asset_node(asset, market_data)
            entities.append({"node_id": asset_node.node_id, "type": "asset"})
            
            # Connect asset to regime
            self._kg.add_edge(
                asset_node.node_id,
                regime_node.node_id,
                EdgeType.APPEARS_WHEN,
                strength=volatility,
                evidence=f"market_signal_{now().sequence}"
            )
            relationships.append({
                "source": asset_node.node_id,
                "target": regime_node.node_id,
                "type": "APPEARS_WHEN",
                "strength": volatility
            })
            
            self._extractions_count += 1
            self._last_population_time = now().utc_time.isoformat()
            
            logger.debug(f"[KG_AUTO] Populated knowledge from market: {asset} regime={regime}")
            
            return KnowledgeExtraction(
                source_type="market",
                entities=entities,
                relationships=relationships,
                confidence=min(1.0, 1.0 - volatility * 0.3)
            )
            
        except Exception as e:
            logger.error(f"[KG_AUTO] Failed to extract knowledge from market: {e}")
            return KnowledgeExtraction(
                source_type="market",
                entities=[],
                relationships=[],
                confidence=0.0
            )

    def update_from_narrative(self, narrative_data: dict[str, Any]) -> KnowledgeExtraction:
        """Extract knowledge from narrative data.
        
        Identifies:
        - Narrative-asset relationships
        - Narrative sentiment patterns
        - Cross-asset narrative themes
        - Temporal narrative patterns
        """
        try:
            entities = []
            relationships = []
            
            narrative_name = narrative_data.get("name", "")
            affected_assets = narrative_data.get("affected_assets", [])
            sentiment = narrative_data.get("sentiment", 0.0)
            
            # Create or get narrative node
            narrative_node = self._get_or_create_narrative_node(narrative_name, narrative_data)
            entities.append({"node_id": narrative_node.node_id, "type": "narrative"})
            
            # Connect narrative to affected assets
            for asset in affected_assets:
                asset_node = self._get_or_create_asset_node(asset, narrative_data)
                entities.append({"node_id": asset_node.node_id, "type": "asset"})
                
                self._kg.add_edge(
                    narrative_node.node_id,
                    asset_node.node_id,
                    EdgeType.AFFECTS,
                    strength=abs(sentiment),
                    evidence=f"narrative_detection_{now().sequence}"
                )
                relationships.append({
                    "source": narrative_node.node_id,
                    "target": asset_node.node_id,
                    "type": "AFFECTS",
                    "sentiment": sentiment
                })
            
            self._extractions_count += 1
            self._last_population_time = now().utc_time.isoformat()
            
            logger.debug(f"[KG_AUTO] Populated knowledge from narrative: {narrative_name}")
            
            return KnowledgeExtraction(
                source_type="narrative",
                entities=entities,
                relationships=relationships,
                confidence=abs(sentiment)
            )
            
        except Exception as e:
            logger.error(f"[KG_AUTO] Failed to extract knowledge from narrative: {e}")
            return KnowledgeExtraction(
                source_type="narrative",
                entities=[],
                relationships=[],
                confidence=0.0
            )

    def _get_or_create_strategy_node(self, strategy: str, context: dict[str, Any]) -> KnowledgeNode:
        """Get existing strategy node or create new one."""
        # Try to find existing strategy node
        for node in self._kg._nodes.values():
            if node.node_type == NodeType.STRATEGY and node.name == strategy:
                # Update with new context
                node.properties.update(context)
                return node
        
        # Create new strategy node
        return self._kg.add_node(
            NodeType.STRATEGY,
            strategy,
            created_at=now().utc_time.isoformat(),
            **context
        )

    def _get_or_create_asset_node(self, asset: str, context: dict[str, Any]) -> KnowledgeNode:
        """Get existing asset node or create new one."""
        # Try to find existing asset node
        for node in self._kg._nodes.values():
            if node.node_type == NodeType.ASSET and node.name == asset:
                # Update with new context
                node.properties.update(context)
                return node
        
        # Create new asset node
        return self._kg.add_node(
            NodeType.ASSET,
            asset,
            created_at=now().utc_time.isoformat(),
            **context
        )

    def _get_or_create_regime_node(self, regime: str, context: dict[str, Any]) -> KnowledgeNode:
        """Get existing regime node or create new one."""
        # Try to find existing regime node
        for node in self._kg._nodes.values():
            if node.node_type == NodeType.CONDITION and node.name == regime:
                # Update with new context
                node.properties.update(context)
                return node
        
        # Create new regime node
        return self._kg.add_node(
            NodeType.CONDITION,
            regime,
            created_at=now().utc_time.isoformat(),
            **context
        )

    def _get_or_create_narrative_node(self, narrative: str, context: dict[str, Any]) -> KnowledgeNode:
        """Get existing narrative node or create new one."""
        # Try to find existing narrative node
        for node in self._kg._nodes.values():
            if node.node_type == NodeType.NARRATIVE and node.name == narrative:
                # Update with new context
                node.properties.update(context)
                return node
        
        # Create new narrative node
        return self._kg.add_node(
            NodeType.NARRATIVE,
            narrative,
            created_at=now().utc_time.isoformat(),
            **context
        )

    def _update_strategy_performance(self, strategy_node: KnowledgeNode, metric: str) -> None:
        """Update strategy performance metrics."""
        if "performance_metrics" not in strategy_node.properties:
            strategy_node.properties["performance_metrics"] = {}
        
        metrics = strategy_node.properties["performance_metrics"]
        metrics[metric] = metrics.get(metric, 0) + 1

    def get_statistics(self) -> dict[str, Any]:
        """Get auto-population statistics."""
        return {
            "extractions_count": self._extractions_count,
            "last_population_time": self._last_population_time,
            "knowledge_graph_nodes": self._kg.get_node_count(),
            "knowledge_graph_edges": self._kg.get_edge_count(),
        }


def get_auto_populator(knowledge_graph: KnowledgeGraph) -> KnowledgeGraphAutoPopulator:
    """Get or create auto-populator for knowledge graph."""
    return KnowledgeGraphAutoPopulator(knowledge_graph)


__all__ = [
    "KnowledgeExtraction",
    "KnowledgeGraphAutoPopulator",
    "get_auto_populator",
]