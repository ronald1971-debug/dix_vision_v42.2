"""XAS-04 — Dynamic correlation clustering for cross-asset analysis.

Advanced clustering algorithms that dynamically group assets based on
their evolving correlation structures. Enables detection of changing
market relationships and correlation regime transitions.

Pure computation. No clocks, no I/O. INV-15 deterministic.
B1: No imports from execution_engine/governance_engine/learning_engine/evolution_engine.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any
from collections import deque


@dataclass(frozen=True, slots=True)
class CorrelationCluster:
    """A cluster of assets with high intra-cluster correlation."""
    cluster_id: str
    assets: tuple[str, ...]
    centroid_correlation: float  # Average correlation within cluster
    inter_cluster_separation: float  # Average correlation with other clusters
    stability_score: float  # How stable this cluster has been over time
    last_updated_ns: int


@dataclass(frozen=True, slots=True)
class CorrelationRegime:
    """The current correlation regime of the market."""
    regime_type: str  # "high_correlation", "low_correlation", "fragmented", "converged"
    average_correlation: float
    correlation_volatility: float
    cluster_count: int
    dominant_clusters: tuple[str, ...]  # IDs of largest clusters
    regime_confidence: float
    timestamp_ns: int


class DynamicCorrelationClusterer:
    """Dynamically clusters assets based on correlation structure.
    
    Uses hierarchical clustering with dynamic threshold adaptation
    to detect changing correlation regimes and asset relationships.
    """
    
    def __init__(
        self,
        min_cluster_size: int = 2,
        max_clusters: int = 10,
        correlation_threshold: float = 0.7,
        stability_window: int = 20
    ) -> None:
        self._min_cluster_size = min_cluster_size
        self._max_clusters = max_clusters
        self._correlation_threshold = correlation_threshold
        self._stability_window = stability_window
        
        self._current_clusters: dict[str, CorrelationCluster] = {}
        self._cluster_history: deque[dict[str, CorrelationCluster]] = deque(maxlen=stability_window)
        self._regime_history: deque[CorrelationRegime] = deque(maxlen=50)
        
    def update_correlation_matrix(
        self,
        correlation_matrix: dict[tuple[str, str], float],
        timestamp_ns: int
    ) -> tuple[CorrelationCluster, ..., CorrelationRegime]:
        """Update clustering with new correlation matrix.
        
        Args:
            correlation_matrix: Dictionary of (symbol_a, symbol_b) -> correlation
            timestamp_ns: Current timestamp
            
        Returns:
            Tuple of current clusters and correlation regime
        """
        # Build asset list from correlation matrix
        assets = set()
        for (a, b) in correlation_matrix.keys():
            assets.add(a)
            assets.add(b)
        assets = sorted(assets)
        
        # Perform hierarchical clustering
        clusters = self._hierarchical_clustering(assets, correlation_matrix)
        
        # Update cluster stability scores
        clusters = self._update_stability_scores(clusters)
        
        # Detect correlation regime
        regime = self._detect_correlation_regime(clusters, correlation_matrix, timestamp_ns)
        
        # Store current state
        self._current_clusters = {c.cluster_id: c for c in clusters}
        self._cluster_history.append(self._current_clusters)
        self._regime_history.append(regime)
        
        return tuple(clusters), regime
    
    def _hierarchical_clustering(
        self,
        assets: list[str],
        correlation_matrix: dict[tuple[str, str], float]
    ) -> list[CorrelationCluster]:
        """Perform hierarchical clustering on assets based on correlation."""
        if len(assets) < self._min_cluster_size:
            return []
        
        # Start with each asset as its own cluster
        clusters = [{asset} for asset in assets]
        
        # Iteratively merge clusters until threshold is met
        while len(clusters) > self._max_clusters:
            # Find most similar cluster pair
            best_merge = None
            best_similarity = -1.0
            
            for i in range(len(clusters)):
                for j in range(i + 1, len(clusters)):
                    similarity = self._cluster_similarity(
                        clusters[i], clusters[j], correlation_matrix
                    )
                    if similarity > best_similarity:
                        best_similarity = similarity
                        best_merge = (i, j)
            
            # Stop if best similarity is below threshold
            if best_similarity < self._correlation_threshold:
                break
            
            # Merge the best pair
            i, j = best_merge
            clusters[i] = clusters[i].union(clusters[j])
            clusters.pop(j)
        
        # Convert to CorrelationCluster objects
        result = []
        for i, cluster_assets in enumerate(clusters):
            if len(cluster_assets) >= self._min_cluster_size:
                cluster = self._build_correlation_cluster(
                    cluster_assets, correlation_matrix, i
                )
                result.append(cluster)
        
        return result
    
    def _cluster_similarity(
        self,
        cluster_a: set[str],
        cluster_b: set[str],
        correlation_matrix: dict[tuple[str, str], float]
    ) -> float:
        """Calculate average correlation between two clusters."""
        correlations = []
        
        for asset_a in cluster_a:
            for asset_b in cluster_b:
                key = (min(asset_a, asset_b), max(asset_a, asset_b))
                if key in correlation_matrix:
                    correlations.append(abs(correlation_matrix[key]))
        
        if not correlations:
            return 0.0
        
        return sum(correlations) / len(correlations)
    
    def _build_correlation_cluster(
        self,
        assets: set[str],
        correlation_matrix: dict[tuple[str, str], float],
        cluster_id: int
    ) -> CorrelationCluster:
        """Build a CorrelationCluster from asset set."""
        asset_list = sorted(assets)
        
        # Calculate centroid correlation
        intra_correlations = []
        for i in range(len(asset_list)):
            for j in range(i + 1, len(asset_list)):
                key = (asset_list[i], asset_list[j])
                if key in correlation_matrix:
                    intra_correlations.append(abs(correlation_matrix[key]))
        
        centroid = sum(intra_correlations) / len(intra_correlations) if intra_correlations else 0.0
        
        # Calculate inter-cluster separation (simplified)
        separation = 0.5  # Placeholder - would calculate against other clusters
        
        # Stability score from history
        stability = self._calculate_cluster_stability(asset_list)
        
        return CorrelationCluster(
            cluster_id=f"cluster_{cluster_id}",
            assets=tuple(asset_list),
            centroid_correlation=centroid,
            inter_cluster_separation=separation,
            stability_score=stability,
            last_updated_ns=0  # Would be actual timestamp
        )
    
    def _calculate_cluster_stability(self, assets: set[str]) -> float:
        """Calculate how stable this cluster has been over time."""
        if len(self._cluster_history) < 2:
            return 0.5
        
        # Check how often these assets have been clustered together
        co_occurrence_count = 0
        total_checks = 0
        
        for historical_clusters in self._cluster_history:
            found_together = False
            for cluster in historical_clusters.values():
                if assets.issubset(set(cluster.assets)):
                    found_together = True
                    break
            if found_together:
                co_occurrence_count += 1
            total_checks += 1
        
        if total_checks == 0:
            return 0.5
        
        return co_occurrence_count / total_checks
    
    def _update_stability_scores(
        self,
        clusters: list[CorrelationCluster]
    ) -> list[CorrelationCluster]:
        """Update stability scores for all clusters."""
        updated = []
        
        for cluster in clusters:
            assets = set(cluster.assets)
            stability = self._calculate_cluster_stability(assets)
            
            updated.append(CorrelationCluster(
                cluster_id=cluster.cluster_id,
                assets=cluster.assets,
                centroid_correlation=cluster.centroid_correlation,
                inter_cluster_separation=cluster.inter_cluster_separation,
                stability_score=stability,
                last_updated_ns=cluster.last_updated_ns
            ))
        
        return updated
    
    def _detect_correlation_regime(
        self,
        clusters: list[CorrelationCluster],
        correlation_matrix: dict[tuple[str, str], float],
        timestamp_ns: int
    ) -> CorrelationRegime:
        """Detect the current correlation regime."""
        if not clusters:
            return CorrelationRegime(
                regime_type="fragmented",
                average_correlation=0.0,
                correlation_volatility=0.0,
                cluster_count=0,
                dominant_clusters=(),
                regime_confidence=0.5,
                timestamp_ns=timestamp_ns
            )
        
        # Calculate average correlation across all pairs
        all_correlations = [abs(c) for c in correlation_matrix.values()]
        avg_correlation = sum(all_correlations) / len(all_correlations) if all_correlations else 0.0
        
        # Calculate correlation volatility (standard deviation)
        if len(all_correlations) > 1:
            variance = sum((c - avg_correlation) ** 2 for c in all_correlations) / len(all_correlations)
            corr_volatility = math.sqrt(variance)
        else:
            corr_volatility = 0.0
        
        # Determine regime type
        cluster_count = len(clusters)
        dominant_clusters = tuple(sorted(
            [c.cluster_id for c in clusters],
            key=lambda cid: len(self._current_clusters[cid].assets) if cid in self._current_clusters else 0,
            reverse=True
        ))[:3]
        
        if avg_correlation > 0.7:
            regime_type = "converged"
        elif avg_correlation > 0.4:
            regime_type = "high_correlation"
        elif avg_correlation > 0.2:
            regime_type = "low_correlation"
        else:
            regime_type = "fragmented"
        
        # Calculate regime confidence based on stability
        if len(self._regime_history) > 0:
            recent_regimes = [r.regime_type for r in list(self._regime_history)[-5:]]
            regime_consistency = recent_regimes.count(regime_type) / len(recent_regimes)
            confidence = 0.3 + 0.7 * regime_consistency
        else:
            confidence = 0.5
        
        return CorrelationRegime(
            regime_type=regime_type,
            average_correlation=avg_correlation,
            correlation_volatility=corr_volatility,
            cluster_count=cluster_count,
            dominant_clusters=dominant_clusters,
            regime_confidence=confidence,
            timestamp_ns=timestamp_ns
        )
    
    def get_current_clusters(self) -> tuple[CorrelationCluster, ...]:
        """Get current correlation clusters."""
        return tuple(self._current_clusters.values())
    
    def get_current_regime(self) -> CorrelationRegime | None:
        """Get current correlation regime."""
        return self._regime_history[-1] if self._regime_history else None
    
    def get_regime_transitions(self) -> list[tuple[str, str, int]]:
        """Get historical regime transitions.
        
        Returns:
            List of (from_regime, to_regime, transition_count)
        """
        if len(self._regime_history) < 2:
            return []
        
        transitions = {}
        regimes = list(self._regime_history)
        
        for i in range(len(regimes) - 1):
            from_regime = regimes[i].regime_type
            to_regime = regimes[i + 1].regime_type
            key = (from_regime, to_regime)
            transitions[key] = transitions.get(key, 0) + 1
        
        return [(k[0], k[1], v) for k, v in transitions.items()]


__all__ = [
    "CorrelationCluster",
    "CorrelationRegime", 
    "DynamicCorrelationClusterer"
]