"""
cognitive_os.knowledge.advanced_graph_reasoning
DIX VISION v42.2 — Advanced Knowledge Graph Reasoning (Priority 3)

Provides advanced knowledge graph reasoning capabilities for the Cognitive OS.
This is a Priority 3 enhancement for advanced AI capabilities.
"""

from __future__ import annotations

import logging
import threading
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)


class CentralityType(Enum):
    """Types of centrality measures."""

    DEGREE = "DEGREE"
    BETWEENNESS = "BETWEENNESS"
    CLOSENESS = "CLOSENESS"
    EIGENVECTOR = "EIGENVECTOR"
    PAGE_RANK = "PAGE_RANK"


class GraphPatternType(Enum):
    """Types of graph patterns."""

    STAR = "STAR"
    CHAIN = "CHAIN"
    CYCLE = "CYCLE"
    CLUSTER = "CLUSTER"
    PATH = "PATH"


class RelationType(Enum):
    """Types of relations in knowledge graph."""

    SUBCLASS_OF = "SUBCLASS_OF"
    PART_OF = "PART_OF"
    RELATED_TO = "RELATED_TO"
    CAUSES = "CAUSES"
    ENABLES = "ENABLES"
    REQUIRES = "REQUIRES"
    SIMILAR_TO = "SIMILAR_TO"
    OPPOSITE_OF = "OPPOSITE_OF"
    TRANSITIVE = "TRANSITIVE"


@dataclass
class GraphNode:
    """Node in advanced knowledge graph."""

    node_id: str
    concept: str
    node_type: str  # ENTITY, CONCEPT, ATTRIBUTE, RELATION
    properties: Dict[str, Any] = field(default_factory=dict)
    embedding: Optional[List[float]] = None  # Graph embedding vector
    confidence: float = 0.0
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class GraphEdge:
    """Edge in advanced knowledge graph."""

    edge_id: str
    source_node: str
    target_node: str
    relation_type: RelationType
    weight: float = 1.0
    confidence: float = 0.0
    transitive: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GraphPattern:
    """Pattern in knowledge graph."""

    pattern_id: str
    pattern_type: GraphPatternType
    center_node: str
    member_nodes: List[str] = field(default_factory=list)
    edges: List[str] = field(default_factory=list)
    confidence: float = 0.0


@dataclass
class CentralityResult:
    """Result of centrality calculation."""

    node_id: str
    centrality_type: CentralityType
    centrality_value: float
    rank: int = 0


@dataclass
class GraphEmbedding:
    """Graph embedding for a node."""

    node_id: str
    embedding_vector: List[float]
    embedding_dimension: int = 0
    method: str = "node2vec"


@dataclass
class InferenceResult:
    """Result of knowledge graph inference."""

    result_id: str
    inference_type: str  # COMPLETION, REASONING, PREDICTION
    source_nodes: List[str] = field(default_factory=list)
    inferred_relations: List[Dict[str, Any]] = field(default_factory=list)
    confidence: float = 0.0
    timestamp: datetime = field(default_factory=datetime.utcnow)


class AdvancedKnowledgeGraph:
    """Advanced knowledge graph with reasoning capabilities."""

    def __init__(self):
        self._lock = threading.Lock()
        self._nodes: Dict[str, GraphNode] = {}
        self._edges: Dict[str, GraphEdge] = {}
        self._adjacency_list: Dict[str, Set[str]] = {}

        logger.info("[ADV_KNOWLEDGE_GRAPH] Advanced Knowledge Graph initialized")

    def add_node(self, node: GraphNode) -> None:
        """Add a node to the knowledge graph."""
        with self._lock:
            self._nodes[node.node_id] = node
            if node.node_id not in self._adjacency_list:
                self._adjacency_list[node.node_id] = set()
            logger.debug(f"[ADV_KNOWLEDGE_GRAPH] Added node: {node.concept}")

    def add_edge(self, edge: GraphEdge) -> None:
        """Add an edge to the knowledge graph."""
        with self._lock:
            self._edges[edge.edge_id] = edge

            # Update adjacency list
            if edge.source_node not in self._adjacency_list:
                self._adjacency_list[edge.source_node] = set()
            if edge.target_node not in self._adjacency_list:
                self._adjacency_list[edge.target_node] = set()

            self._adjacency_list[edge.source_node].add(edge.target_node)

            logger.debug(f"[ADV_KNOWLEDGE_GRAPH] Added edge: {edge.relation_type.value}")

    def calculate_centrality(self, centrality_type: CentralityType) -> List[CentralityResult]:
        """
        Calculate centrality measures for all nodes.

        Args:
            centrality_type: Type of centrality to calculate

        Returns:
            List of centrality results
        """
        with self._lock:
            results = []

            if centrality_type == CentralityType.DEGREE:
                results = self._calculate_degree_centrality()
            elif centrality_type == CentralityType.PAGE_RANK:
                results = self._calculate_page_rank()
            else:
                # For other centrality types, return degree centrality as default
                results = self._calculate_degree_centrality()

            # Rank nodes by centrality
            results.sort(key=lambda x: x.centrality_value, reverse=True)
            for i, result in enumerate(results):
                result.rank = i + 1

            return results

    def _calculate_degree_centrality(self) -> List[CentralityResult]:
        """Calculate degree centrality for all nodes."""
        results = []
        total_edges = len(self._edges)

        if total_edges == 0:
            return results

        for node_id, neighbors in self._adjacency_list.items():
            degree = len(neighbors)
            centrality = degree / (len(self._nodes) - 1) if len(self._nodes) > 1 else 0.0

            results.append(
                CentralityResult(
                    node_id=node_id,
                    centrality_type=CentralityType.DEGREE,
                    centrality_value=centrality,
                )
            )

        return results

    def _calculate_page_rank(
        self, iterations: int = 10, damping_factor: float = 0.85
    ) -> List[CentralityResult]:
        """Calculate PageRank for all nodes."""
        if not self._nodes:
            return []

        # Initialize PageRank values
        pagerank = {node_id: 1.0 / len(self._nodes) for node_id in self._nodes}

        for _ in range(iterations):
            new_pagerank = {}
            for node_id in self._nodes:
                # Calculate sum of PageRank from incoming neighbors
                sum_pr = 0.0
                for neighbor_id in self._adjacency_list:
                    if node_id in self._adjacency_list[neighbor_id]:
                        neighbor_degree = len(self._adjacency_list[neighbor_id])
                        if neighbor_degree > 0:
                            sum_pr += pagerank[neighbor_id] / neighbor_degree

                # Apply damping factor
                new_pagerank[node_id] = (1 - damping_factor) / len(
                    self._nodes
                ) + damping_factor * sum_pr

            pagerank = new_pagerank

        # Convert to CentralityResult
        results = []
        for node_id, pr_value in pagerank.items():
            results.append(
                CentralityResult(
                    node_id=node_id,
                    centrality_type=CentralityType.PAGE_RANK,
                    centrality_value=pr_value,
                )
            )

        return results

    def detect_patterns(self, pattern_type: GraphPatternType) -> List[GraphPattern]:
        """
        Detect patterns in the knowledge graph.

        Args:
            pattern_type: Type of pattern to detect

        Returns:
            List of detected patterns
        """
        with self._lock:
            patterns = []

            if pattern_type == GraphPatternType.STAR:
                patterns = self._detect_star_patterns()
            elif pattern_type == GraphPatternType.CLUSTER:
                patterns = self._detect_clusters()
            elif pattern_type == GraphPatternType.CYCLE:
                patterns = self._detect_cycles()
            else:
                # Default to star patterns
                patterns = self._detect_star_patterns()

            return patterns

    def _detect_star_patterns(self) -> List[GraphPattern]:
        """Detect star patterns (central node connected to many others)."""
        patterns = []

        for node_id, neighbors in self._adjacency_list.items():
            if len(neighbors) >= 3:  # At least 3 connections for a star
                pattern = GraphPattern(
                    pattern_id=f"star_{node_id}",
                    pattern_type=GraphPatternType.STAR,
                    center_node=node_id,
                    member_nodes=list(neighbors),
                    confidence=0.8,
                )
                patterns.append(pattern)

        return patterns

    def _detect_clusters(self) -> List[GraphPattern]:
        """Detect clusters using simple connected component analysis."""
        patterns = []
        visited = set()

        for node_id in self._nodes:
            if node_id not in visited:
                # BFS to find connected component
                cluster = []
                queue = [node_id]
                visited.add(node_id)

                while queue:
                    current = queue.pop(0)
                    cluster.append(current)

                    for neighbor in self._adjacency_list.get(current, set()):
                        if neighbor not in visited:
                            visited.add(neighbor)
                            queue.append(neighbor)

                if len(cluster) >= 3:  # At least 3 nodes for a cluster
                    pattern = GraphPattern(
                        pattern_id=f"cluster_{node_id}",
                        pattern_type=GraphPatternType.CLUSTER,
                        center_node=cluster[0],  # Use first node as center
                        member_nodes=cluster[1:],
                        confidence=0.7,
                    )
                    patterns.append(pattern)

        return patterns

    def _detect_cycles(self) -> List[GraphPattern]:
        """Detect cycles in the graph using DFS."""
        patterns = []
        visited = set()
        path = []

        for node_id in self._nodes:
            if node_id not in visited:
                self._dfs_cycle_detection(node_id, visited, path, patterns)

        return patterns

    def _dfs_cycle_detection(
        self, node_id: str, visited: Set[str], path: List[str], patterns: List[GraphPattern]
    ) -> None:
        """DFS to detect cycles."""
        if node_id in path:
            # Cycle detected
            cycle_start = path.index(node_id)
            cycle_nodes = path[cycle_start:] + [node_id]

            if len(cycle_nodes) >= 3:  # At least 3 nodes for a cycle
                pattern = GraphPattern(
                    pattern_id=f"cycle_{node_id}_{len(cycle_nodes)}",
                    pattern_type=GraphPatternType.CYCLE,
                    center_node=cycle_nodes[0],
                    member_nodes=cycle_nodes[1:],
                    confidence=0.9,
                )
                patterns.append(pattern)
            return

        visited.add(node_id)
        path.append(node_id)

        for neighbor in self._adjacency_list.get(node_id, set()):
            self._dfs_cycle_detection(neighbor, visited, path, patterns)

        path.pop()

    def find_shortest_path(self, source: str, target: str) -> Optional[List[str]]:
        """Find shortest path between two nodes using BFS."""
        with self._lock:
            if source not in self._nodes or target not in self._nodes:
                return None

            visited = {source}
            queue = [[source]]

            while queue:
                path = queue.pop(0)
                last_node = path[-1]

                if last_node == target:
                    return path

                for neighbor in self._adjacency_list.get(last_node, set()):
                    if neighbor not in visited:
                        visited.add(neighbor)
                        new_path = path + [neighbor]
                        queue.append(new_path)

            return None


class KnowledgeGraphReasoner:
    """Advanced reasoning over knowledge graph."""

    def __init__(self, knowledge_graph: Optional[AdvancedKnowledgeGraph] = None):
        self._lock = threading.Lock()
        self._knowledge_graph = knowledge_graph or AdvancedKnowledgeGraph()

        logger.info("[KG_REASONER] Knowledge Graph Reasoner initialized")

    def infer_relations(self, source_nodes: List[str]) -> InferenceResult:
        """
        Infer missing relations from source nodes.

        Args:
            source_nodes: List of source node IDs

        Returns:
            Inference result with inferred relations
        """
        with self._lock:
            inferred_relations = []

            for source_id in source_nodes:
                if source_id in self._knowledge_graph._nodes:
                    # Find patterns and infer relations
                    neighbors = self._knowledge_graph._adjacency_list.get(source_id, set())

                    # Infer transitive relations
                    for neighbor_id in neighbors:
                        for second_neighbor in self._knowledge_graph._adjacency_list.get(
                            neighbor_id, set()
                        ):
                            if second_neighbor != source_id and second_neighbor not in neighbors:
                                # Infer potential relation
                                inferred_relations.append(
                                    {
                                        "source": source_id,
                                        "target": second_neighbor,
                                        "relation": "POTENTIALLY_RELATED_TO",
                                        "confidence": 0.5,
                                    }
                                )

            return InferenceResult(
                result_id=f"inference_{int(datetime.utcnow().timestamp() * 1000)}",
                inference_type="COMPLETION",
                source_nodes=source_nodes,
                inferred_relations=inferred_relations,
                confidence=0.6,
            )

    def predict_links(self, node_id: str, top_k: int = 5) -> List[Tuple[str, float]]:
        """
        Predict potential links for a node.

        Args:
            node_id: Node to predict links for
            top_k: Number of top predictions

        Returns:
            List of (target_node, confidence) tuples
        """
        with self._lock:
            if node_id not in self._knowledge_graph._nodes:
                return []

            predictions = []
            neighbors = self._knowledge_graph._adjacency_list.get(node_id, set())

            # Use co-occurrence and structural similarity for prediction
            for other_node in self._knowledge_graph._nodes:
                if other_node != node_id and other_node not in neighbors:
                    # Calculate similarity based on common neighbors
                    other_neighbors = self._knowledge_graph._adjacency_list.get(other_node, set())
                    common_neighbors = neighbors.intersection(other_neighbors)

                    if common_neighbors:
                        # Jaccard similarity
                        union_size = len(neighbors.union(other_neighbors))
                        if union_size > 0:
                            similarity = len(common_neighbors) / union_size
                            predictions.append((other_node, similarity))

            # Sort by confidence and return top k
            predictions.sort(key=lambda x: x[1], reverse=True)
            return predictions[:top_k]


class AdvancedGraphReasoningEngine:
    """
    Advanced knowledge graph reasoning engine for the Cognitive OS.

    Features:
    - Advanced knowledge graph management
    - Multiple centrality measures (degree, PageRank, etc.)
    - Pattern detection (stars, clusters, cycles)
    - Shortest path finding
    - Link prediction
    - Relation inference
    """

    def __init__(self):
        self._lock = threading.Lock()

        # Components
        self._knowledge_graph = AdvancedKnowledgeGraph()
        self._reasoner = KnowledgeGraphReasoner(self._knowledge_graph)

        # Statistics
        self._inference_count = 0
        self._pattern_detection_count = 0

        logger.info("[ADV_GRAPH_REASONING_ENGINE] Advanced Graph Reasoning Engine initialized")

    def add_knowledge(self, node: GraphNode, edge: Optional[GraphEdge] = None) -> None:
        """Add knowledge to the graph."""
        with self._lock:
            self._knowledge_graph.add_node(node)
            if edge:
                self._knowledge_graph.add_edge(edge)

    def analyze_graph_structure(
        self, centrality_type: CentralityType = CentralityType.PAGE_RANK
    ) -> List[CentralityResult]:
        """Analyze graph structure using centrality measures."""
        with self._lock:
            return self._knowledge_graph.calculate_centrality(centrality_type)

    def discover_patterns(self, pattern_type: GraphPatternType) -> List[GraphPattern]:
        """Discover patterns in the knowledge graph."""
        with self._lock:
            patterns = self._knowledge_graph.detect_patterns(pattern_type)
            self._pattern_detection_count += 1
            return patterns

    def infer_knowledge(self, source_nodes: List[str]) -> InferenceResult:
        """Infer new knowledge from existing graph."""
        with self._lock:
            result = self._reasoner.infer_relations(source_nodes)
            self._inference_count += 1
            return result

    def predict_missing_links(self, node_id: str, top_k: int = 5) -> List[Tuple[str, float]]:
        """Predict missing links in the graph."""
        with self._lock:
            return self._reasoner.predict_links(node_id, top_k)

    def find_semantic_path(self, source: str, target: str) -> Optional[List[str]]:
        """Find semantic path between concepts."""
        with self._lock:
            return self._knowledge_graph.find_shortest_path(source, target)

    def get_statistics(self) -> Dict[str, Any]:
        """Get reasoning engine statistics."""
        with self._lock:
            return {
                "node_count": len(self._knowledge_graph._nodes),
                "edge_count": len(self._knowledge_graph._edges),
                "inference_count": self._inference_count,
                "pattern_detection_count": self._pattern_detection_count,
            }


# Singleton instance
_advanced_graph_engine: Optional[AdvancedGraphReasoningEngine] = None
_advanced_graph_lock = threading.Lock()


def get_advanced_graph_engine() -> AdvancedGraphReasoningEngine:
    """Get the singleton advanced graph reasoning engine instance."""
    global _advanced_graph_engine
    if _advanced_graph_engine is None:
        with _advanced_graph_lock:
            if _advanced_graph_engine is None:
                _advanced_graph_engine = AdvancedGraphReasoningEngine()
    return _advanced_graph_engine


__all__ = [
    "CentralityType",
    "GraphPatternType",
    "RelationType",
    "GraphNode",
    "GraphEdge",
    "GraphPattern",
    "CentralityResult",
    "GraphEmbedding",
    "InferenceResult",
    "AdvancedKnowledgeGraph",
    "KnowledgeGraphReasoner",
    "AdvancedGraphReasoningEngine",
    "get_advanced_graph_engine",
]
