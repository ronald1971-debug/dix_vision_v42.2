"""
shared_infrastructure.knowledge_graph_adapter
DIX VISION v42.2 — Knowledge Graph Adapter

Provides interface for knowledge graph operations supporting neuro-symbolic reasoning.
Adapts to Neo4j or similar graph databases for knowledge storage and retrieval.
"""

from __future__ import annotations

import logging
import threading
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class NodeRelationshipType:
    """Types of node relationships in the knowledge graph."""

    CAUSES = "CAUSES"
    CAUSED_BY = "CAUSED_BY"
    RELATED_TO = "RELATED_TO"
    DEPENDS_ON = "DEPENDS_ON"
    ENABLES = "ENABLES"
    REQUIRES = "REQUIRES"
    CONTAINS = "CONTAINS"
    PART_OF = "PART_OF"
    ASSOCIATED_WITH = "ASSOCIATED_WITH"
    SIMILAR_TO = "SIMILAR_TO"
    OPPOSITE_OF = "OPPOSITE_OF"
    PRECEDES = "PRECEDES"
    FOLLOWS = "FOLLOWS"


class NodeType:
    """Types of nodes in the knowledge graph."""

    CONCEPT = "CONCEPT"
    ENTITY = "ENTITY"
    EVENT = "EVENT"
    RULE = "RULE"
    HYPOTHESIS = "HYPOTHESIS"
    MEMORY = "MEMORY"
    TRADING_SIGNAL = "TRADING_SIGNAL"
    SYSTEM_COMPONENT = "SYSTEM_COMPONENT"
    ERROR = "ERROR"
    CUSTOM = "CUSTOM"


@dataclass
class KnowledgeNode:
    """A node in the knowledge graph."""

    node_id: str
    node_type: NodeType
    label: str
    properties: Dict[str, Any] = field(default_factory=dict)
    embeddings: Optional[List[float]] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class KnowledgeEdge:
    """An edge (relationship) between nodes in the knowledge graph."""

    edge_id: str
    source_node_id: str
    target_node_id: str
    relationship_type: str
    properties: Dict[str, Any] = field(default_factory=dict)
    weight: float = 1.0
    confidence: float = 1.0
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class KnowledgeQuery:
    """A query to the knowledge graph."""

    query_id: str
    query_type: str  # node_query | path_query | pattern_query | custom
    query_string: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    limit: int = 100


@dataclass
class KnowledgeGraphResult:
    """Result from a knowledge graph query."""

    query_id: str
    nodes: List[KnowledgeNode] = field(default_factory=list)
    edges: List[KnowledgeEdge] = field(default_factory=list)
    paths: List[List[Dict[str, Any]]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    execution_time_ms: float = 0.0


class KnowledgeGraphAdapterInterface(ABC):
    """Interface for knowledge graph operations."""

    @abstractmethod
    def add_node(self, node: KnowledgeNode) -> str:
        """Add a node to the knowledge graph."""

    @abstractmethod
    def add_edge(self, edge: KnowledgeEdge) -> str:
        """Add an edge between nodes."""

    @abstractmethod
    def get_node(self, node_id: str) -> Optional[KnowledgeNode]:
        """Get a node by ID."""

    @abstractmethod
    def get_neighbors(
        self,
        node_id: str,
        relationship_types: Optional[List[str]] = None,
        direction: str = "both",  # outgoing | incoming | both
    ) -> List[KnowledgeNode]:
        """Get neighboring nodes."""

    @abstractmethod
    def query(self, query: KnowledgeQuery) -> KnowledgeGraphResult:
        """Execute a query on the knowledge graph."""

    @abstractmethod
    def find_path(
        self, source_node_id: str, target_node_id: str, max_depth: int = 5
    ) -> List[Dict[str, Any]]:
        """Find a path between two nodes."""

    @abstractmethod
    def find_patterns(self, pattern: Dict[str, Any], limit: int = 100) -> KnowledgeGraphResult:
        """Find patterns in the graph."""

    @abstractmethod
    def delete_node(self, node_id: str) -> bool:
        """Delete a node from the graph."""

    @abstractmethod
    def delete_edge(self, edge_id: str) -> bool:
        """Delete an edge from the graph."""

    @abstractmethod
    def get_statistics(self) -> Dict[str, Any]:
        """Get knowledge graph statistics."""


class InMemoryKnowledgeGraphAdapter(KnowledgeGraphAdapterInterface):
    """
    In-memory implementation of knowledge graph for development and testing.
    Can be replaced with Neo4j or other graph database implementations.
    """

    def __init__(self):
        self._lock = threading.Lock()

        # In-memory storage
        self._nodes: Dict[str, KnowledgeNode] = {}
        self._edges: Dict[str, KnowledgeEdge] = {}

        # Adjacency list for fast neighbor lookups
        self._adjacency_outgoing: Dict[str, List[str]] = {}
        self._adjacency_incoming: Dict[str, List[str]] = {}

        # Statistics
        self._query_count = 0
        self._query_total_time_ms = 0.0

        logger.info("[KNOWLEDGE_GRAPH] In-memory adapter initialized")

    def add_node(self, node: KnowledgeNode) -> str:
        """Add a node to the knowledge graph."""
        with self._lock:
            self._nodes[node.node_id] = node

            # Initialize adjacency entries
            if node.node_id not in self._adjacency_outgoing:
                self._adjacency_outgoing[node.node_id] = []
            if node.node_id not in self._adjacency_incoming:
                self._adjacency_incoming[node.node_id] = []

            logger.debug(f"[KNOWLEDGE_GRAPH] Added node: {node.node_id} ({node.node_type})")
            return node.node_id

    def add_edge(self, edge: KnowledgeEdge) -> str:
        """Add an edge between nodes."""
        with self._lock:
            # Validate nodes exist
            if edge.source_node_id not in self._nodes:
                logger.warning(f"[KNOWLEDGE_GRAPH] Source node {edge.source_node_id} not found")
                return ""

            if edge.target_node_id not in self._nodes:
                logger.warning(f"[KNOWLEDGE_GRAPH] Target node {edge.target_node_id} not found")
                return ""

            self._edges[edge.edge_id] = edge

            # Update adjacency lists
            self._adjacency_outgoing[edge.source_node_id].append(edge.edge_id)
            self._adjacency_incoming[edge.target_node_id].append(edge.edge_id)

            logger.debug(f"[KNOWLEDGE_GRAPH] Added edge: {edge.edge_id} ({edge.relationship_type})")
            return edge.edge_id

    def get_node(self, node_id: str) -> Optional[KnowledgeNode]:
        """Get a node by ID."""
        with self._lock:
            return self._nodes.get(node_id)

    def get_neighbors(
        self, node_id: str, relationship_types: Optional[List[str]] = None, direction: str = "both"
    ) -> List[KnowledgeNode]:
        """Get neighboring nodes."""
        with self._lock:
            if node_id not in self._nodes:
                return []

            neighbor_ids = set()

            # Get outgoing edges
            if direction in ["outgoing", "both"]:
                outgoing_edge_ids = self._adjacency_outgoing.get(node_id, [])
                for edge_id in outgoing_edge_ids:
                    edge = self._edges.get(edge_id)
                    if edge:
                        if (
                            relationship_types is None
                            or edge.relationship_type in relationship_types
                        ):
                            neighbor_ids.add(edge.target_node_id)

            # Get incoming edges
            if direction in ["incoming", "both"]:
                incoming_edge_ids = self._adjacency_incoming.get(node_id, [])
                for edge_id in incoming_edge_ids:
                    edge = self._edges.get(edge_id)
                    if edge:
                        if (
                            relationship_types is None
                            or edge.relationship_type in relationship_types
                        ):
                            neighbor_ids.add(edge.source_node_id)

            # Return neighbor nodes
            return [self._nodes[nid] for nid in neighbor_ids if nid in self._nodes]

    def query(self, query: KnowledgeQuery) -> KnowledgeGraphResult:
        """Execute a query on the knowledge graph."""
        start_time = datetime.utcnow()

        try:
            # Simplified query implementation
            result = KnowledgeGraphResult(query_id=query.query_id, execution_time_ms=0.0)

            if query.query_type == "node_query":
                # Query nodes by properties
                matching_nodes = []
                for node in self._nodes.values():
                    match = True
                    for key, value in query.parameters.items():
                        if node.properties.get(key) != value:
                            match = False
                            break
                    if match:
                        matching_nodes.append(node)

                result.nodes = matching_nodes[: query.limit]

            elif query.query_type == "pattern_query":
                # Find pattern matches
                result = self._find_pattern_matches(query, result)

            elif query.query_type == "custom":
                # Custom query string parsing (simplified)
                result.metadata["query_string"] = query.query_string
                result.metadata["parameters"] = query.parameters

            # Calculate execution time
            execution_time_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
            result.execution_time_ms = execution_time_ms

            # Update statistics
            with self._lock:
                self._query_count += 1
                self._query_total_time_ms += execution_time_ms

            logger.info(
                f"[KNOWLEDGE_GRAPH] Query executed: {query.query_type} ({execution_time_ms:.2f}ms, {len(result.nodes)} nodes)"
            )

            return result

        except Exception as e:
            logger.error(f"[KNOWLEDGE_GRAPH] Query failed: {e}")
            return KnowledgeGraphResult(query_id=query.query_id, metadata={"error": str(e)})

    def _find_pattern_matches(
        self, query: KnowledgeQuery, result: KnowledgeGraphResult
    ) -> KnowledgeGraphResult:
        """Find pattern matches in the graph."""
        # Simplified pattern matching
        pattern = query.parameters.get("pattern", {})

        # Example pattern: find all CAUSES relationships
        if "relationship_type" in pattern:
            rel_type = pattern["relationship_type"]
            matching_edges = [
                edge for edge in self._edges.values() if edge.relationship_type == rel_type
            ]
            result.edges = matching_edges[: query.limit]

            # Include connected nodes
            node_ids = set()
            for edge in matching_edges:
                node_ids.add(edge.source_node_id)
                node_ids.add(edge.target_node_id)

            result.nodes = [self._nodes[nid] for nid in node_ids if nid in self._nodes]

        return result

    def find_path(
        self, source_node_id: str, target_node_id: str, max_depth: int = 5
    ) -> List[Dict[str, Any]]:
        """Find a path between two nodes using BFS."""
        with self._lock:
            if source_node_id not in self._nodes or target_node_id not in self._nodes:
                return []

            # BFS for shortest path
            from collections import deque

            queue = deque([(source_node_id, [])])
            visited = {source_node_id}

            while queue and len(queue[0][1]) < max_depth:
                current_node_id, path = queue.popleft()

                if current_node_id == target_node_id:
                    return path + [current_node_id]

                # Get neighbors
                neighbor_edges = self._adjacency_outgoing.get(current_node_id, [])
                for edge_id in neighbor_edges:
                    edge = self._edges.get(edge_id)
                    if edge:
                        if edge.target_node_id not in visited:
                            visited.add(edge.target_node_id)
                            new_path = path + [current_node_id]
                            queue.append((edge.target_node_id, new_path))

            return []  # No path found

    def find_patterns(self, pattern: Dict[str, Any], limit: int = 100) -> KnowledgeGraphResult:
        """Find patterns in the graph."""
        query = KnowledgeQuery(
            query_id=f"pattern_{int(datetime.utcnow().timestamp())}",
            query_type="pattern_query",
            parameters={"pattern": pattern},
            limit=limit,
        )
        return self.query(query)

    def delete_node(self, node_id: str) -> bool:
        """Delete a node from the graph."""
        with self._lock:
            if node_id not in self._nodes:
                return False

            # Delete all edges connected to this node
            edge_ids_to_delete = []

            # Outgoing edges
            for edge_id in self._adjacency_outgoing.get(node_id, []):
                edge_ids_to_delete.append(edge_id)

            # Incoming edges
            for edge_id in self._adjacency_incoming.get(node_id, []):
                edge_ids_to_delete.append(edge_id)

            # Delete edges
            for edge_id in edge_ids_to_delete:
                del self._edges[edge_id]

            # Delete adjacency entries
            del self._adjacency_outgoing[node_id]
            del self._adjacency_incoming[node_id]

            # Remove from other nodes' adjacency lists
            for other_node_id in self._adjacency_outgoing:
                self._adjacency_outgoing[other_node_id] = [
                    eid
                    for eid in self._adjacency_outgoing[other_node_id]
                    if eid not in edge_ids_to_delete
                ]

            for other_node_id in self._adjacency_incoming:
                self._adjacency_incoming[other_node_id] = [
                    eid
                    for eid in self._adjacency_incoming[other_node_id]
                    if eid not in edge_ids_to_delete
                ]

            # Delete node
            del self._nodes[node_id]

            logger.debug(f"[KNOWLEDGE_GRAPH] Deleted node: {node_id}")
            return True

    def delete_edge(self, edge_id: str) -> bool:
        """Delete an edge from the graph."""
        with self._lock:
            if edge_id not in self._edges:
                return False

            edge = self._edges[edge_id]

            # Remove from adjacency lists
            self._adjacency_outgoing[edge.source_node_id] = [
                eid for eid in self._adjacency_outgoing[edge.source_node_id] if eid != edge_id
            ]
            self._adjacency_incoming[edge.target_node_id] = [
                eid for eid in self._adjacency_incoming[edge.target_node_id] if eid != edge_id
            ]

            # Delete edge
            del self._edges[edge_id]

            logger.debug(f"[KNOWLEDGE_GRAPH] Deleted edge: {edge_id}")
            return True

    def get_statistics(self) -> Dict[str, Any]:
        """Get knowledge graph statistics."""
        with self._lock:
            node_type_counts = {}
            for node in self._nodes.values():
                node_type = node.node_type
                node_type_counts[node_type] = node_type_counts.get(node_type, 0) + 1

            relationship_type_counts = {}
            for edge in self._edges.values():
                rel_type = edge.relationship_type
                relationship_type_counts[rel_type] = relationship_type_counts.get(rel_type, 0) + 1

            avg_query_time = (
                self._query_total_time_ms / self._query_count if self._query_count > 0 else 0.0
            )

            return {
                "node_count": len(self._nodes),
                "edge_count": len(self._edges),
                "node_type_counts": node_type_counts,
                "relationship_type_counts": relationship_type_counts,
                "query_count": self._query_count,
                "average_query_time_ms": avg_query_time,
                "adapter_type": "in_memory",
            }


# Global instance
_knowledge_graph_adapter: Optional[KnowledgeGraphAdapterInterface] = None
_knowledge_graph_lock = threading.Lock()


def get_knowledge_graph_adapter() -> KnowledgeGraphAdapterInterface:
    """Get global knowledge graph adapter instance."""
    global _knowledge_graph_adapter
    if _knowledge_graph_adapter is None:
        with _knowledge_graph_lock:
            if _knowledge_graph_adapter is None:
                _knowledge_graph_adapter = InMemoryKnowledgeGraphAdapter()
    return _knowledge_graph_adapter


__all__ = [
    "NodeRelationshipType",
    "NodeType",
    "KnowledgeNode",
    "KnowledgeEdge",
    "KnowledgeQuery",
    "KnowledgeGraphResult",
    "KnowledgeGraphAdapterInterface",
    "InMemoryKnowledgeGraphAdapter",
    "get_knowledge_graph_adapter",
]
