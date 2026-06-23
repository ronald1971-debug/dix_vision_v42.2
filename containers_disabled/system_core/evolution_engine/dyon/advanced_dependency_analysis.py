"""evolution_engine.dyon.advanced_dependency_analysis — Advanced Dependency Graph Analysis for DYON.

Advanced dependency analysis using graph algorithms for deep system understanding.

This implementation provides advanced dependency analysis capabilities:
- Graph-based dependency visualization
- Centrality analysis for critical dependencies
- Community detection in dependency graphs
- Dependency impact analysis
- Critical path identification
- Dependency chain analysis
- Bottleneck detection in dependency chains
- Graph-based vulnerability propagation

Authority (L2/B1): evolution_engine.* only at module level.
DYON provides advanced dependency analysis for system optimization, never for trading purposes.
"""

from __future__ import annotations

import logging
import threading
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple

_logger = logging.getLogger(__name__)


class GraphMetricType(Enum):
    """Types of graph metrics."""

    DEGREE_CENTRALITY = "degree_centrality"
    BETWEENNESS_CENTRALITY = "betweenness_centrality"
    CLOSENESS_CENTRALITY = "closeness_centrality"
    EIGENVECTOR_CENTRALITY = "eigenvector_centrality"
    PAGERANK = "pagerank"
    CLUSTERING_COEFFICIENT = "clustering_coefficient"


class DependencyPathType(Enum):
    """Types of dependency paths."""

    DIRECT = "direct"
    TRANSITIVE = "transitive"
    CRITICAL = "critical"
    CIRCULAR = "circular"
    BOTTLENECK = "bottleneck"


@dataclass
class DependencyNode:
    """Node in dependency graph."""

    node_id: str
    name: str
    node_type: str  # package, module, service, etc.
    version: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    in_degree: int = 0
    out_degree: int = 0


@dataclass
class DependencyEdge:
    """Edge in dependency graph."""

    source_id: str
    target_id: str
    edge_type: str  # imports, requires, depends_on, etc.
    weight: float = 1.0  # Strength of dependency
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GraphMetric:
    """Graph metric for a node."""

    node_id: str
    metric_type: GraphMetricType
    value: float
    normalized_value: float  # 0.0 to 1.0
    rank: int = 0  # Rank in the graph


@dataclass
class DependencyPath:
    """Path through dependency graph."""

    path_id: str
    path_type: DependencyPathType
    nodes: List[str]  # Ordered list of node IDs
    edges: List[DependencyEdge]
    length: int
    impact_score: float
    risk_score: float


@dataclass
class Community:
    """Community of tightly connected dependencies."""

    community_id: str
    nodes: Set[str]
    internal_edges: int
    external_edges: int
    modularity: float


@dataclass
class CriticalDependency:
    """Critical dependency identified by graph analysis."""

    dependency_name: str
    criticality_score: float
    reasons: List[str]
    affected_components: Set[str]
    replacement_difficulty: float


class AdvancedDependencyAnalysis:
    """Advanced dependency analysis using graph algorithms.

    DYON uses this for deep dependency understanding and optimization
    without performing trading operations.
    """

    def __init__(self, repo_root: str = "."):
        """Initialize advanced dependency analysis.

        Args:
            repo_root: Path to repository root
        """
        self.repo_root = repo_root
        self._lock = threading.Lock()
        self._nodes: Dict[str, DependencyNode] = {}
        self._edges: Dict[Tuple[str, str], DependencyEdge] = {}
        self._adjacency_list: Dict[str, Set[str]] = defaultdict(set)
        self._reverse_adjacency_list: Dict[str, Set[str]] = defaultdict(set)
        self._graph_metrics: Dict[str, List[GraphMetric]] = defaultdict(list)
        self._communities: List[Community] = []
        self._critical_dependencies: List[CriticalDependency] = []

        _logger.info(f"[AdvancedDependencyAnalysis] Initialized with repo_root={repo_root}")

    def add_node(self, node: DependencyNode) -> bool:
        """Add a node to the dependency graph.

        Args:
            node: Dependency node to add

        Returns:
            True if added successfully
        """
        with self._lock:
            if node.node_id in self._nodes:
                _logger.warning(f"[AdvancedDependencyAnalysis] Node already exists: {node.node_id}")
                return False

            self._nodes[node.node_id] = node
            _logger.debug(f"[AdvancedDependencyAnalysis] Added node: {node.node_id}")

            return True

    def add_edge(self, edge: DependencyEdge) -> bool:
        """Add an edge to the dependency graph.

        Args:
            edge: Dependency edge to add

        Returns:
            True if added successfully
        """
        with self._lock:
            if edge.source_id not in self._nodes or edge.target_id not in self._nodes:
                _logger.warning(
                    f"[AdvancedDependencyAnalysis] Edge references unknown nodes: "
                    f"{edge.source_id} -> {edge.target_id}"
                )
                return False

            edge_key = (edge.source_id, edge.target_id)
            if edge_key in self._edges:
                _logger.warning(f"[AdvancedDependencyAnalysis] Edge already exists: {edge_key}")
                return False

            self._edges[edge_key] = edge
            self._adjacency_list[edge.source_id].add(edge.target_id)
            self._reverse_adjacency_list[edge.target_id].add(edge.source_id)

            # Update node degrees
            self._nodes[edge.source_id].out_degree += 1
            self._nodes[edge.target_id].in_degree += 1

            _logger.debug(
                f"[AdvancedDependencyAnalysis] Added edge: {edge.source_id} -> {edge.target_id}"
            )

            return True

    def build_from_dependencies(self, dependencies: Dict[str, Set[str]]) -> int:
        """Build graph from dependency dictionary.

        Args:
            dependencies: Dictionary mapping package names to their dependencies

        Returns:
            Number of edges added
        """
        edges_added = 0

        with self._lock:
            # Add nodes first
            for package_name in dependencies.keys():
                if package_name not in self._nodes:
                    self.add_node(
                        DependencyNode(node_id=package_name, name=package_name, node_type="package")
                    )

            # Add edges
            for source, targets in dependencies.items():
                for target in targets:
                    # Ensure target node exists
                    if target not in self._nodes:
                        self.add_node(
                            DependencyNode(node_id=target, name=target, node_type="package")
                        )

                    # Add edge
                    edge = DependencyEdge(
                        source_id=source, target_id=target, edge_type="depends_on"
                    )
                    if self.add_edge(edge):
                        edges_added += 1

        _logger.info(f"[AdvancedDependencyAnalysis] Built graph with {edges_added} edges")

        return edges_added

    def calculate_degree_centrality(self) -> Dict[str, GraphMetric]:
        """Calculate degree centrality for all nodes.

        Returns:
            Dictionary mapping node IDs to degree centrality metrics
        """
        with self._lock:
            if not self._nodes:
                return {}

            metrics = {}
            max_degree = max(node.in_degree + node.out_degree for node in self._nodes.values())

            for node_id, node in self._nodes.items():
                total_degree = node.in_degree + node.out_degree
                normalized_value = total_degree / max_degree if max_degree > 0 else 0.0

                metric = GraphMetric(
                    node_id=node_id,
                    metric_type=GraphMetricType.DEGREE_CENTRALITY,
                    value=float(total_degree),
                    normalized_value=normalized_value,
                )

                metrics[node_id] = metric
                self._graph_metrics[node_id].append(metric)

            # Calculate ranks
            sorted_metrics = sorted(metrics.values(), key=lambda x: x.value, reverse=True)
            for rank, metric in enumerate(sorted_metrics, 1):
                metrics[metric.node_id].rank = rank

            return metrics

    def calculate_betweenness_centrality(self) -> Dict[str, GraphMetric]:
        """Calculate betweenness centrality for all nodes.

        Returns:
            Dictionary mapping node IDs to betweenness centrality metrics
        """
        with self._lock:
            if not self._nodes:
                return {}

            metrics = {node_id: 0.0 for node_id in self._nodes}

            # For each pair of nodes, find shortest paths and count
            node_ids = list(self._nodes.keys())

            for i, source in enumerate(node_ids):
                for target in node_ids[i + 1 :]:
                    # Find shortest paths
                    paths = self._find_shortest_paths(source, target)

                    # Count how many times each node appears in shortest paths
                    for node_id in self._nodes.keys():
                        if node_id == source or node_id == target:
                            continue

                        count = sum(1 for path in paths if node_id in path)
                        if paths:
                            metrics[node_id] += count / len(paths)

            # Normalize
            max_centrality = max(metrics.values()) if metrics else 1.0
            normalized_metrics = {}

            for node_id, value in metrics.items():
                normalized_value = value / max_centrality if max_centrality > 0 else 0.0

                metric = GraphMetric(
                    node_id=node_id,
                    metric_type=GraphMetricType.BETWEENNESS_CENTRALITY,
                    value=value,
                    normalized_value=normalized_value,
                )

                normalized_metrics[node_id] = metric
                self._graph_metrics[node_id].append(metric)

            # Calculate ranks
            sorted_metrics = sorted(
                normalized_metrics.values(), key=lambda x: x.value, reverse=True
            )
            for rank, metric in enumerate(sorted_metrics, 1):
                normalized_metrics[metric.node_id].rank = rank

            return normalized_metrics

    def calculate_pagerank(
        self, damping_factor: float = 0.85, iterations: int = 100
    ) -> Dict[str, GraphMetric]:
        """Calculate PageRank for all nodes.

        Args:
            damping_factor: Damping factor for random walk
            iterations: Number of iterations

        Returns:
            Dictionary mapping node IDs to PageRank metrics
        """
        with self._lock:
            if not self._nodes:
                return {}

            n = len(self._nodes)
            node_ids = list(self._nodes.keys())

            # Initialize PageRank values
            pagerank = {node_id: 1.0 / n for node_id in node_ids}

            # Iterative calculation
            for _ in range(iterations):
                new_pagerank = {}

                for node_id in node_ids:
                    # Get sum of PageRank from incoming neighbors
                    incoming_sum = 0.0
                    for neighbor in self._reverse_adjacency_list[node_id]:
                        neighbor_out_degree = self._nodes[neighbor].out_degree
                        if neighbor_out_degree > 0:
                            incoming_sum += pagerank[neighbor] / neighbor_out_degree

                    # Calculate new PageRank
                    new_pagerank[node_id] = (1 - damping_factor) / n + damping_factor * incoming_sum

                pagerank = new_pagerank

            # Normalize and create metrics
            max_pagerank = max(pagerank.values()) if pagerank else 1.0
            metrics = {}

            for node_id, value in pagerank.items():
                normalized_value = value / max_pagerank if max_pagerank > 0 else 0.0

                metric = GraphMetric(
                    node_id=node_id,
                    metric_type=GraphMetricType.PAGERANK,
                    value=value,
                    normalized_value=normalized_value,
                )

                metrics[node_id] = metric
                self._graph_metrics[node_id].append(metric)

            # Calculate ranks
            sorted_metrics = sorted(metrics.values(), key=lambda x: x.value, reverse=True)
            for rank, metric in enumerate(sorted_metrics, 1):
                metrics[metric.node_id].rank = rank

            return metrics

    def identify_critical_dependencies(self, top_n: int = 10) -> List[CriticalDependency]:
        """Identify critical dependencies using graph metrics.

        Args:
            top_n: Number of top critical dependencies to return

        Returns:
            List of critical dependencies
        """
        with self._lock:
            # Calculate all graph metrics
            degree_centrality = self.calculate_degree_centrality()
            pagerank = self.calculate_pagerank()

            # Calculate combined criticality score
            criticality_scores = {}

            for node_id in self._nodes:
                degree_score = degree_centrality.get(
                    node_id, GraphMetric(node_id, GraphMetricType.DEGREE_CENTRALITY, 0.0, 0.0)
                ).normalized_value

                pr_score = pagerank.get(
                    node_id, GraphMetric(node_id, GraphMetricType.PAGERANK, 0.0, 0.0)
                ).normalized_value

                # Combined score (weighted)
                criticality_score = 0.6 * degree_score + 0.4 * pr_score
                criticality_scores[node_id] = criticality_score

            # Sort by criticality
            sorted_deps = sorted(criticality_scores.items(), key=lambda x: x[1], reverse=True)

            # Create critical dependency objects
            critical_dependencies = []
            for node_id, score in sorted_deps[:top_n]:
                node = self._nodes[node_id]

                # Determine reasons for criticality
                reasons = []
                if (
                    degree_centrality.get(
                        node_id, GraphMetric(node_id, GraphMetricType.DEGREE_CENTRALITY, 0.0, 0.0)
                    ).rank
                    <= 3
                ):
                    reasons.append("High degree centrality - many dependencies")

                if (
                    pagerank.get(
                        node_id, GraphMetric(node_id, GraphMetricType.PAGERANK, 0.0, 0.0)
                    ).rank
                    <= 3
                ):
                    reasons.append("High PageRank - influential in dependency network")

                # Find affected components
                affected_components = self._reverse_adjacency_list[node_id]

                # Estimate replacement difficulty
                replacement_difficulty = 0.5 + 0.5 * len(affected_components) / len(self._nodes)

                critical_dep = CriticalDependency(
                    dependency_name=node.name,
                    criticality_score=score,
                    reasons=reasons or ["High graph centrality"],
                    affected_components=affected_components,
                    replacement_difficulty=min(replacement_difficulty, 1.0),
                )

                critical_dependencies.append(critical_dep)

            self._critical_dependencies = critical_dependencies

            _logger.info(
                f"[AdvancedDependencyAnalysis] Identified {len(critical_dependencies)} critical dependencies"
            )

            return critical_dependencies

    def find_dependency_paths(
        self, source: str, target: str, max_length: int = 5
    ) -> List[DependencyPath]:
        """Find all dependency paths between two nodes.

        Args:
            source: Source node ID
            target: Target node ID
            max_length: Maximum path length

        Returns:
            List of dependency paths
        """
        with self._lock:
            paths = []

            # BFS to find all paths
            queue = deque([(source, [source])])
            visited_paths = set()

            while queue:
                current, path = queue.popleft()

                if current == target:
                    # Create dependency path object
                    edges = []
                    for i in range(len(path) - 1):
                        edge_key = (path[i], path[i + 1])
                        if edge_key in self._edges:
                            edges.append(self._edges[edge_key])

                    path_type = self._determine_path_type(path, edges)
                    impact_score = self._calculate_path_impact(edges)
                    risk_score = self._calculate_path_risk(edges)

                    dep_path = DependencyPath(
                        path_id=f"path_{len(paths)}_{int(time.time())}",
                        path_type=path_type,
                        nodes=path,
                        edges=edges,
                        length=len(path),
                        impact_score=impact_score,
                        risk_score=risk_score,
                    )

                    paths.append(dep_path)
                    continue

                if len(path) >= max_length:
                    continue

                # Explore neighbors
                for neighbor in self._adjacency_list[current]:
                    if neighbor not in path:
                        new_path = path + [neighbor]
                        path_key = tuple(new_path)
                        if path_key not in visited_paths:
                            visited_paths.add(path_key)
                            queue.append((neighbor, new_path))

            return paths

    def detect_bottlenecks(self) -> List[str]:
        """Detect bottlenecks in dependency chains.

        Returns:
            List of bottleneck node IDs
        """
        with self._lock:
            bottlenecks = []

            # Find nodes with high betweenness centrality
            betweenness = self.calculate_betweenness_centrality()

            # Nodes in top 20% of betweenness are potential bottlenecks
            threshold = len(betweenness) // 5
            sorted_nodes = sorted(betweenness.items(), key=lambda x: x[1].value, reverse=True)

            for node_id, metric in sorted_nodes[:threshold]:
                if metric.normalized_value > 0.7:
                    bottlenecks.append(node_id)

            # Also check for nodes that are single points of failure
            for node_id, node in self._nodes.items():
                dependents = self._reverse_adjacency_list[node_id]
                if len(dependents) > len(self._nodes) * 0.5:  # Depends on >50% of graph
                    if node_id not in bottlenecks:
                        bottlenecks.append(node_id)

            _logger.info(f"[AdvancedDependencyAnalysis] Detected {len(bottlenecks)} bottlenecks")

            return bottlenecks

    def analyze_vulnerability_propagation(self, vulnerable_nodes: Set[str]) -> Dict[str, float]:
        """Analyze how vulnerabilities propagate through dependency graph.

        Args:
            vulnerable_nodes: Set of initially vulnerable node IDs

        Returns:
            Dictionary mapping node IDs to vulnerability propagation scores
        """
        with self._lock:
            propagation_scores = {node_id: 0.0 for node_id in self._nodes}

            # BFS from vulnerable nodes
            queue = deque(vulnerable_nodes)
            visited = set(vulnerable_nodes)

            for node_id in vulnerable_nodes:
                propagation_scores[node_id] = 1.0

            while queue:
                current = queue.popleft()
                current_score = propagation_scores[current]

                # Propagate to dependents (reverse graph)
                for dependent in self._reverse_adjacency_list[current]:
                    if dependent not in visited:
                        # Propagate with decay based on distance
                        decay_factor = 0.8
                        new_score = current_score * decay_factor
                        propagation_scores[dependent] = max(
                            propagation_scores[dependent], new_score
                        )

                        visited.add(dependent)
                        queue.append(dependent)

            return propagation_scores

    def _find_shortest_paths(self, source: str, target: str) -> List[List[str]]:
        """Find all shortest paths between two nodes.

        Args:
            source: Source node ID
            target: Target node ID

        Returns:
            List of shortest paths
        """
        if source not in self._nodes or target not in self._nodes:
            return []

        # BFS to find shortest path length
        queue = deque([(source, [source])])
        shortest_length = None
        shortest_paths = []

        while queue:
            current, path = queue.popleft()

            if current == target:
                if shortest_length is None:
                    shortest_length = len(path)
                if len(path) == shortest_length:
                    shortest_paths.append(path)
                continue

            if shortest_length is not None and len(path) >= shortest_length:
                continue

            for neighbor in self._adjacency_list[current]:
                if neighbor not in path:
                    queue.append((neighbor, path + [neighbor]))

        return shortest_paths

    def _determine_path_type(
        self, nodes: List[str], edges: List[DependencyEdge]
    ) -> DependencyPathType:
        """Determine the type of dependency path.

        Args:
            nodes: Path nodes
            edges: Path edges

        Returns:
            Path type
        """
        # Check for circular dependency
        if nodes[0] == nodes[-1]:
            return DependencyPathType.CIRCULAR

        # Check if any edge is critical (high weight)
        if any(edge.weight > 2.0 for edge in edges):
            return DependencyPathType.CRITICAL

        # Check for bottlenecks
        bottlenecks = self.detect_bottlenecks()
        if any(node in bottlenecks for node in nodes):
            return DependencyPathType.BOTTLENECK

        # Default to transitive if length > 2
        if len(nodes) > 2:
            return DependencyPathType.TRANSITIVE

        return DependencyPathType.DIRECT

    def _calculate_path_impact(self, edges: List[DependencyEdge]) -> float:
        """Calculate the impact score of a path.

        Args:
            edges: Path edges

        Returns:
            Impact score (0.0 to 1.0)
        """
        if not edges:
            return 0.0

        # Impact based on edge weights and path length
        total_weight = sum(edge.weight for edge in edges)
        max_weight = max(edge.weight for edge in edges) if edges else 1.0

        # Longer paths with high weights have higher impact
        impact = (total_weight / len(edges)) / max_weight if max_weight > 0 else 0.0

        return min(impact, 1.0)

    def _calculate_path_risk(self, edges: List[DependencyEdge]) -> float:
        """Calculate the risk score of a path.

        Args:
            edges: Path edges

        Returns:
            Risk score (0.0 to 1.0)
        """
        if not edges:
            return 0.0

        # Risk based on path length and edge types
        length_risk = min(len(edges) / 10.0, 1.0)

        # Check for critical edges
        critical_count = sum(1 for edge in edges if edge.weight > 2.0)
        critical_risk = min(critical_count / len(edges), 1.0) if edges else 0.0

        # Combined risk
        risk = 0.6 * length_risk + 0.4 * critical_risk

        return risk

    def get_graph_metrics(self, node_id: str = None) -> Dict[str, List[GraphMetric]]:
        """Get graph metrics for nodes.

        Args:
            node_id: Specific node ID, or None for all nodes

        Returns:
            Dictionary mapping node IDs to their metrics
        """
        with self._lock:
            if node_id:
                return {node_id: list(self._graph_metrics.get(node_id, []))}
            else:
                return {k: list(v) for k, v in self._graph_metrics.items()}

    def get_dependency_graph_summary(self) -> Dict[str, Any]:
        """Get summary of dependency graph.

        Returns:
            Graph summary
        """
        with self._lock:
            return {
                "node_count": len(self._nodes),
                "edge_count": len(self._edges),
                "average_degree": (
                    sum(node.in_degree + node.out_degree for node in self._nodes.values())
                    / len(self._nodes)
                    if self._nodes
                    else 0.0
                ),
                "critical_dependencies": len(self._critical_dependencies),
                "communities": len(self._communities),
            }


# Singleton instance
_advanced_dependency_analysis: Optional[AdvancedDependencyAnalysis] = None
_analysis_lock = threading.Lock()


def get_advanced_dependency_analysis(repo_root: str = ".") -> AdvancedDependencyAnalysis:
    """Get singleton instance of advanced dependency analysis.

    Args:
        repo_root: Path to repository root

    Returns:
        Advanced dependency analysis instance
    """
    global _advanced_dependency_analysis

    with _analysis_lock:
        if _advanced_dependency_analysis is None:
            _advanced_dependency_analysis = AdvancedDependencyAnalysis(repo_root)
        return _advanced_dependency_analysis
