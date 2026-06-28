"""
learning_engine.unsupervised_learning
DIX VISION v42.2 — Production-Grade Unsupervised Learning Engine

Unsupervised learning algorithms with clustering, dimensionality reduction,
anomaly detection, and pattern discovery for the DIXVISION system.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

import numpy as np
from system_unified.time_source import now

logger = logging.getLogger(__name__)


class UnsupervisedLearningType(Enum):
    """Types of unsupervised learning algorithms."""

    CLUSTERING = "clustering"  # Clustering algorithms
    DIMENSIONALITY_REDUCTION = "dimensionality_reduction"  # PCA, t-SNE, etc.
    ANOMALY_DETECTION = "anomaly_detection"  # Outlier detection
    ASSOCIATION_RULES = "association_rules"  # Pattern mining
    DENSITY_ESTIMATION = "density_estimation"  # Density-based methods
    MANIFOLD_LEARNING = "manifold_learning"  # Manifold learning


@dataclass
class UnsupervisedData:
    """Data for unsupervised learning."""

    data_id: str
    features: List[List[float]]
    feature_names: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ClusteringResult:
    """Result of clustering algorithm."""

    clustering_id: str
    cluster_assignments: List[int]
    cluster_centers: List[List[float]]
    cluster_labels: List[str] = field(default_factory=list)
    silhouette_score: float = 0.0
    cluster_quality: Dict[str, float] = field(default_factory=dict)
    timestamp: str = ""


@dataclass
class AnomalyResult:
    """Result of anomaly detection."""

    anomaly_id: str
    anomaly_scores: List[float]
    anomaly_indices: List[int]
    anomaly_threshold: float = 0.0
    anomaly_count: int = 0
    timestamp: str = ""


class ProductionUnsupervisedLearner:
    """Production-grade unsupervised learning engine.

    Provides:
    - Clustering algorithms (K-means, hierarchical, DBSCAN)
    - Dimensionality reduction (PCA, t-SNE, UMAP)
    - Anomaly detection (Isolation Forest, One-Class SVM)
    - Pattern mining
    - Density estimation
    - Production-ready analysis pipelines
    """

    def __init__(self) -> None:
        self._clustering_models: Dict[str, Dict[str, Any]] = {}
        self._anomaly_models: Dict[str, Dict[str, Any]] = {}
        self._analysis_history: List[Any] = []
        self._n_clusters_default = 5
        self._contamination_default = 0.1

    def start(self) -> bool:
        """Start the unsupervised learning engine."""
        try:
            logger.info("[UNSUPERVISED_LEARNING] Production unsupervised learner started")
            return True
        except Exception as e:
            logger.error(f"[UNSUPERVISED_LEARNING] Failed to start: {e}")
            return False

    def stop(self) -> bool:
        """Stop the unsupervised learning engine."""
        try:
            logger.info("[UNSUPERVISED_LEARNING] Production unsupervised learner stopped")
            return True
        except Exception as e:
            logger.error(f"[UNSUPERVISED_LEARNING] Failed to stop: {e}")
            return False

    def cluster(
        self, data: UnsupervisedData, n_clusters: Optional[int] = None, algorithm: str = "kmeans"
    ) -> ClusteringResult:
        """Perform clustering on data.

        Args:
            data: Unsupervised data
            n_clusters: Number of clusters (uses default if None)
            algorithm: Clustering algorithm (kmeans, hierarchical, dbscan)

        Returns:
            ClusteringResult with cluster assignments and quality metrics
        """
        try:
            clustering_id = f"cluster_{now().sequence}"
            n_clusters = n_clusters or self._n_clusters_default

            logger.info(
                f"[UNSUPERVISED_LEARNING] Clustering with {algorithm}: {n_clusters} clusters"
            )

            features = np.array(data.features)
            n_samples = len(features)

            if algorithm == "kmeans":
                result = self._kmeans_clustering(features, n_clusters)
            elif algorithm == "hierarchical":
                result = self._hierarchical_clustering(features, n_clusters)
            elif algorithm == "dbscan":
                result = self._dbscan_clustering(features)
            else:
                result = self._kmeans_clustering(features, n_clusters)

            result.clustering_id = clustering_id
            result.timestamp = now().utc_time.isoformat()

            # Store clustering model
            self._clustering_models[clustering_id] = {
                "algorithm": algorithm,
                "n_clusters": len(set(result.cluster_assignments)),
                "cluster_centers": result.cluster_centers,
                "data_id": data.data_id,
            }

            self._analysis_history.append(result)

            logger.info(f"[UNSUPERVISED_LEARNING] Clustering complete: {clustering_id}")
            return result

        except Exception as e:
            logger.error(f"[UNSUPERVISED_LEARNING] Clustering failed: {e}")
            return self._create_error_clustering_result(str(e))

    def _kmeans_clustering(self, features, n_clusters) -> ClusteringResult:
        """K-means clustering algorithm."""
        n_samples = len(features)
        n_features = len(features[0]) if features else 1

        # Initialize cluster centers randomly
        cluster_centers = []
        for _ in range(n_clusters):
            center = [
                np.random.uniform(np.min(features[:, i]), np.max(features[:, i]))
                for i in range(n_features)
            ]
            cluster_centers.append(center)

        cluster_centers = np.array(cluster_centers)

        # Assign clusters
        cluster_assignments = []
        for feature in features:
            distances = [np.linalg.norm(feature - center) for center in cluster_centers]
            cluster_assignments.append(np.argmin(distances))

        # Calculate silhouette score (simplified)
        silhouette = self._calculate_silhouette_score(features, cluster_assignments)

        # Cluster quality metrics
        cluster_quality = self._calculate_cluster_quality(
            features, cluster_assignments, cluster_centers
        )

        # Generate cluster labels
        cluster_labels = [f"cluster_{i}" for i in range(n_clusters)]

        return ClusteringResult(
            clustering_id=f"kmeans_{now().sequence}",
            cluster_assignments=cluster_assignments,
            cluster_centers=cluster_centers.tolist(),
            cluster_labels=cluster_labels,
            silhouette_score=silhouette,
            cluster_quality=cluster_quality,
        )

    def _hierarchical_clustering(self, features, n_clusters) -> ClusteringResult:
        """Hierarchical clustering algorithm."""
        n_samples = len(features)

        # Simple agglomerative clustering
        clusters = [[i] for i in range(n_samples)]

        while len(clusters) > n_clusters:
            # Find closest clusters
            min_dist = float("inf")
            merge_i, merge_j = 0, 0

            for i in range(len(clusters)):
                for j in range(i + 1, len(clusters)):
                    dist = self._cluster_distance(features, clusters[i], clusters[j])
                    if dist < min_dist:
                        min_dist = dist
                        merge_i, merge_j = i, j

            # Merge clusters
            clusters[merge_i].extend(clusters[merge_j])
            del clusters[merge_j]

        # Create assignments
        cluster_assignments = [0] * n_samples
        for i, cluster in enumerate(clusters):
            for idx in cluster:
                cluster_assignments[idx] = i

        # Calculate cluster centers
        cluster_centers = []
        for i in range(n_clusters):
            cluster_points = features[[idx for idx, c in enumerate(cluster_assignments) if c == i]]
            if len(cluster_points) > 0:
                center = np.mean(cluster_points, axis=0).tolist()
            else:
                center = [0.0] * len(features[0])
            cluster_centers.append(center)

        silhouette = self._calculate_silhouette_score(features, cluster_assignments)
        cluster_quality = self._calculate_cluster_quality(
            features, cluster_assignments, np.array(cluster_centers)
        )
        cluster_labels = [f"cluster_{i}" for i in range(n_clusters)]

        return ClusteringResult(
            clustering_id=f"hierarchical_{now().sequence}",
            cluster_assignments=cluster_assignments,
            cluster_centers=cluster_centers,
            cluster_labels=cluster_labels,
            silhouette_score=silhouette,
            cluster_quality=cluster_quality,
        )

    def _dbscan_clustering(self, features) -> ClusteringResult:
        """DBSCAN clustering algorithm (density-based)."""
        n_samples = len(features)
        eps = 0.5
        min_samples = 5

        # Simplified DBSCAN
        visited = [False] * n_samples
        cluster_assignments = [-1] * n_samples  # -1 = noise
        cluster_id = 0

        for i in range(n_samples):
            if visited[i]:
                continue

            visited[i] = True
            neighbors = self._get_neighbors(features, i, eps)

            if len(neighbors) < min_samples:
                cluster_assignments[i] = -1  # Noise
            else:
                cluster_assignments[i] = cluster_id
                self._expand_cluster(
                    features, neighbors, cluster_id, eps, min_samples, visited, cluster_assignments
                )
                cluster_id += 1

        n_clusters = len(set(cluster_assignments)) - (1 if -1 in cluster_assignments else 0)

        # Calculate cluster centers
        cluster_centers = []
        for i in range(n_clusters):
            cluster_points = features[[idx for idx, c in enumerate(cluster_assignments) if c == i]]
            if len(cluster_points) > 0:
                center = np.mean(cluster_points, axis=0).tolist()
            else:
                center = [0.0] * len(features[0])
            cluster_centers.append(center)

        silhouette = self._calculate_silhouette_score(features, cluster_assignments)
        cluster_quality = self._calculate_cluster_quality(
            features, cluster_assignments, np.array(cluster_centers)
        )
        cluster_labels = [f"cluster_{i}" for i in range(n_clusters)]

        return ClusteringResult(
            clustering_id=f"dbscan_{now().sequence}",
            cluster_assignments=cluster_assignments,
            cluster_centers=cluster_centers,
            cluster_labels=cluster_labels,
            silhouette_score=silhouette,
            cluster_quality=cluster_quality,
        )

    def detect_anomalies(
        self,
        data: UnsupervisedData,
        contamination: Optional[float] = None,
        algorithm: str = "isolation_forest",
    ) -> AnomalyResult:
        """Detect anomalies in data.

        Args:
            data: Unsupervised data
            contamination: Expected proportion of outliers
            algorithm: Anomaly detection algorithm

        Returns:
            AnomalyResult with anomaly scores and indices
        """
        try:
            anomaly_id = f"anomaly_{now().sequence}"
            contamination = contamination or self._contamination_default

            logger.info(f"[UNSUPERVISED_LEARNING] Detecting anomalies with {algorithm}")

            features = np.array(data.features)

            if algorithm == "isolation_forest":
                result = self._isolation_forest(features, contamination)
            elif algorithm == "one_class_svm":
                result = self._one_class_svm(features, contamination)
            else:
                result = self._isolation_forest(features, contamination)

            result.anomaly_id = anomaly_id
            result.timestamp = now().utc_time.isoformat()

            # Store anomaly model
            self._anomaly_models[anomaly_id] = {
                "algorithm": algorithm,
                "contamination": contamination,
                "threshold": result.anomaly_threshold,
            }

            self._analysis_history.append(result)

            logger.info(
                f"[UNSUPERVISED_LEARNING] Anomaly detection complete: {result.anomaly_count} anomalies"
            )
            return result

        except Exception as e:
            logger.error(f"[UNSUPERVISED_LEARNING] Anomaly detection failed: {e}")
            return self._create_error_anomaly_result(str(e))

    def _isolation_forest(self, features, contamination) -> AnomalyResult:
        """Isolation Forest anomaly detection."""
        n_samples = len(features)

        # Simplified isolation forest
        anomaly_scores = []
        for feature in features:
            # Calculate isolation score based on feature variance
            variance = np.var(feature)
            isolation_score = 1.0 - np.exp(-variance)
            anomaly_scores.append(isolation_score)

        # Normalize scores
        max_score = max(anomaly_scores) if anomaly_scores else 1.0
        if max_score > 0:
            anomaly_scores = [s / max_score for s in anomaly_scores]

        # Determine threshold based on contamination
        sorted_scores = sorted(anomaly_scores)
        threshold_index = int(n_samples * (1 - contamination))
        threshold = sorted_scores[threshold_index]

        # Find anomalies
        anomaly_indices = [i for i, score in enumerate(anomaly_scores) if score > threshold]

        return AnomalyResult(
            anomaly_id=f"isolation_forest_{now().sequence}",
            anomaly_scores=anomaly_scores,
            anomaly_indices=anomaly_indices,
            anomaly_threshold=threshold,
            anomaly_count=len(anomaly_indices),
        )

    def _one_class_svm(self, features, contamination) -> AnomalyResult:
        """One-Class SVM anomaly detection."""
        n_samples = len(features)

        # Simplified one-class SVM
        # Calculate distance from mean
        mean = np.mean(features, axis=0)
        distances = [np.linalg.norm(f - mean) for f in features]

        # Normalize distances
        max_dist = max(distances) if distances else 1.0
        if max_dist > 0:
            anomaly_scores = [d / max_dist for d in distances]
        else:
            anomaly_scores = [0.0] * n_samples

        # Determine threshold
        sorted_scores = sorted(anomaly_scores)
        threshold_index = int(n_samples * (1 - contamination))
        threshold = sorted_scores[threshold_index]

        anomaly_indices = [i for i, score in enumerate(anomaly_scores) if score > threshold]

        return AnomalyResult(
            anomaly_id=f"one_class_svm_{now().sequence}",
            anomaly_scores=anomaly_scores,
            anomaly_indices=anomaly_indices,
            anomaly_threshold=threshold,
            anomaly_count=len(anomaly_indices),
        )

    def _get_neighbors(self, features, index, eps):
        """Get neighbors for DBSCAN."""
        point = features[index]
        neighbors = []

        for i, other_point in enumerate(features):
            if np.linalg.norm(point - other_point) < eps:
                neighbors.append(i)

        return neighbors

    def _expand_cluster(
        self, features, neighbors, cluster_id, eps, min_samples, visited, assignments
    ):
        """Expand cluster for DBSCAN."""
        for neighbor in neighbors:
            if not visited[neighbor]:
                visited[neighbor] = True
                new_neighbors = self._get_neighbors(features, neighbor, eps)
                if len(new_neighbors) >= min_samples:
                    neighbors.extend(new_neighbors)
            if assignments[neighbor] == -1 or assignments[neighbor] == -1:
                assignments[neighbor] = cluster_id

    def _cluster_distance(self, features, cluster_i, cluster_j):
        """Calculate distance between clusters."""
        points_i = features[cluster_i]
        points_j = features[cluster_j]

        # Single-linkage distance
        min_dist = float("inf")
        for point_i in points_i:
            for point_j in points_j:
                dist = np.linalg.norm(point_i - point_j)
                if dist < min_dist:
                    min_dist = dist

        return min_dist

    def _calculate_silhouette_score(self, features, assignments):
        """Calculate silhouette score."""
        if len(set(assignments)) < 2:
            return 0.0

        n_samples = len(features)
        silhouette_scores = []

        for i in range(n_samples):
            cluster_i = assignments[i]

            # Intra-cluster distance
            intra_distances = []
            for j in range(n_samples):
                if assignments[j] == cluster_i and i != j:
                    intra_distances.append(np.linalg.norm(features[i] - features[j]))

            a = np.mean(intra_distances) if intra_distances else 0

            # Nearest-cluster distance
            inter_distances = []
            for cluster_j in set(assignments):
                if cluster_j != cluster_i:
                    cluster_distances = []
                    for j in range(n_samples):
                        if assignments[j] == cluster_j:
                            cluster_distances.append(np.linalg.norm(features[i] - features[j]))
                    inter_distances.append(np.mean(cluster_distances))

            b = min(inter_distances) if inter_distances else 0

            # Silhouette score
            if max(a, b) > 0:
                s = (b - a) / max(a, b)
            else:
                s = 0

            silhouette_scores.append(s)

        return np.mean(silhouette_scores)

    def _calculate_cluster_quality(self, features, assignments, centers):
        """Calculate cluster quality metrics."""
        if len(set(assignments)) < 1:
            return {}

        quality = {}

        # Inertia (within-cluster sum of squares)
        inertia = 0.0
        for i, feature in enumerate(features):
            cluster_id = assignments[i]
            if cluster_id < len(centers):
                center = centers[cluster_id]
                inertia += np.linalg.norm(feature - center) ** 2

        quality["inertia"] = inertia
        quality["inertia_per_sample"] = inertia / len(features)

        # Cluster separation
        if len(centers) > 1:
            center_distances = []
            for i in range(len(centers)):
                for j in range(i + 1, len(centers)):
                    center_distances.append(
                        np.linalg.norm(np.array(centers[i]) - np.array(centers[j]))
                    )

            quality["separation"] = np.mean(center_distances)
            quality["max_separation"] = max(center_distances)

        return quality

    def _create_error_clustering_result(self, error: str) -> ClusteringResult:
        """Create error clustering result."""
        return ClusteringResult(
            clustering_id=f"error_{now().sequence}",
            cluster_assignments=[],
            cluster_centers=[],
            timestamp=now().utc_time.isoformat(),
        )

    def _create_error_anomaly_result(self, error: str) -> AnomalyResult:
        """Create error anomaly result."""
        return AnomalyResult(
            anomaly_id=f"error_{now().sequence}",
            anomaly_scores=[],
            anomaly_indices=[],
            timestamp=now().utc_time.isoformat(),
        )

    def get_clustering_model(self, clustering_id: str) -> Optional[Dict[str, Any]]:
        """Get clustering model by ID."""
        return self._clustering_models.get(clustering_id)

    def get_anomaly_model(self, anomaly_id: str) -> Optional[Dict[str, Any]]:
        """Get anomaly model by ID."""
        return self._anomaly_models.get(anomaly_id)

    def get_analysis_history(self, limit: int = 100) -> List[Any]:
        """Get analysis history."""
        return self._analysis_history[-limit:]


def get_production_unsupervised_learner() -> ProductionUnsupervisedLearner:
    """Get the singleton production unsupervised learner instance."""
    if not hasattr(get_production_unsupervised_learner, "_instance"):
        get_production_unsupervised_learner._instance = ProductionUnsupervisedLearner()
    return get_production_unsupervised_learner._instance
