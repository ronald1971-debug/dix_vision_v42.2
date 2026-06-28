"""Knowledge Graph - connected understanding of trading universe."""

from __future__ import annotations

import uuid
from typing import Any

from cognitive_engine.knowledge_graph.edge import EdgeType, KnowledgeEdge
from cognitive_engine.knowledge_graph.node import KnowledgeNode, NodeType


class KnowledgeGraph:
    """Connected graph of trading knowledge.

    Connects:
    - Trader nodes
    - Strategy nodes
    - Regime nodes
    - Market nodes
    - Execution nodes
    - Catalyst nodes
    - Narrative nodes
    """

    def __init__(self) -> None:
        self._nodes: dict[str, KnowledgeNode] = {}
        self._edges: dict[str, KnowledgeEdge] = {}
        self._adjacency: dict[str, list[str]] = {}

    def add_node(self, node_type: NodeType, name: str, **properties: Any) -> KnowledgeNode:
        """Add a node to the graph."""
        node = KnowledgeNode(
            node_id=str(uuid.uuid4()),
            node_type=node_type,
            name=name,
            properties=properties,
        )
        self._nodes[node.node_id] = node
        return node

    def add_edge(
        self,
        source_id: str,
        target_id: str,
        edge_type: EdgeType,
        strength: float = 1.0,
        evidence: str | tuple[str, ...] = (),
    ) -> KnowledgeEdge | None:
        """Add an edge between nodes."""
        if source_id not in self._nodes or target_id not in self._nodes:
            return None

        edge = KnowledgeEdge(
            edge_id=str(uuid.uuid4()),
            source_id=source_id,
            target_id=target_id,
            edge_type=edge_type,
            strength=strength,
            evidence=(evidence,) if isinstance(evidence, str) else evidence,
        )
        self._edges[edge.edge_id] = edge

        # Update adjacency
        self._adjacency.setdefault(source_id, []).append(target_id)

        return edge

    def connect_trader_strategy(
        self, trader_id: str, strategy_id: str, strength: float = 1.0
    ) -> KnowledgeEdge | None:
        """Connect a trader to a strategy they use."""
        return self.add_edge(trader_id, strategy_id, EdgeType.USES, strength)

    def connect_strategy_regime(
        self, strategy_id: str, regime_id: str, **props: Any
    ) -> KnowledgeEdge | None:
        """Connect strategy to regime where it works."""
        return self.add_edge(strategy_id, regime_id, EdgeType.WORKS_DURING, **props)

    def connect_regime_condition(
        self, regime_id: str, condition: str, strength: float = 1.0
    ) -> KnowledgeEdge | None:
        """Connect regime to liquidity/volatility condition."""
        return self.add_edge(regime_id, condition, EdgeType.APPEARS_WHEN, strength)

    def get_node(self, node_id: str) -> KnowledgeNode | None:
        """Get a node by ID."""
        return self._nodes.get(node_id)

    def get_neighbors(self, node_id: str) -> list[KnowledgeNode]:
        """Get connected nodes."""
        neighbor_ids = self._adjacency.get(node_id, [])
        return [self._nodes[nid] for nid in neighbor_ids if nid in self._nodes]

    def find_strategies_for_trader(self, trader_id: str) -> list[KnowledgeNode]:
        """Find strategies used by a trader."""
        return [
            self._nodes[tid]
            for tid in self._adjacency.get(trader_id, [])
            if tid in self._nodes and self._nodes[tid].node_type == NodeType.STRATEGY
        ]

    def find_traders_for_strategy(self, strategy_id: str) -> list[KnowledgeNode]:
        """Find traders using a strategy."""
        traders = []
        for edge in self._edges.values():
            if edge.target_id == strategy_id and edge.edge_type == EdgeType.USES:
                if edge.source_id in self._nodes:
                    traders.append(self._nodes[edge.source_id])
        return traders

    def get_edge_count(self) -> int:
        """Get total edge count."""
        return len(self._edges)

    def get_node_count(self) -> int:
        """Get total node count."""
        return len(self._nodes)
