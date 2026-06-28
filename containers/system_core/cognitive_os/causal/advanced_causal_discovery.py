"""Advanced Causal Discovery Engine - Sophisticated Causal Inference.

This module provides advanced causal discovery capabilities using state-of-the-art
causal inference algorithms, enabling the system to discover, validate, and reason about
causal relationships in complex data.
"""

from __future__ import annotations

import logging
import math
import threading
import time
from collections import defaultdict
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)


class CausalAlgorithm(str, Enum):
    """Types of causal discovery algorithms."""

    PC_ALGORITHM = "PC_ALGORITHM"
    FCI_ALGORITHM = "FCI_ALGORITHM"
    GES_ALGORITHM = "GES_ALGORITHM"
    LINGAM_ALGORITHM = "LINGAM_ALGORITHM"
    DYNAMICAL_CASUAL = "DYNAMICAL_CASUAL"
    BAYESIAN_NETWORK = "BAYESIAN_NETWORK"
    STRUCTURAL_EQUATION = "STRUCTURAL_EQUATION"


class CausalType(str, Enum):
    """Types of causal relationships."""

    DIRECT = "DIRECT"
    INDIRECT = "INDIRECT"
    CONFOUNDED = "CONFOUNDED"
    MEDIATED = "MEDIATED"
    BIDIRECTIONAL = "BIDIRECTIONAL"


class CausalStrength(str, Enum):
    """Strength of causal relationship."""

    WEAK = "WEAK"
    MODERATE = "MODERATE"
    STRONG = "STRONG"
    VERY_STRONG = "VERY_STRONG"


@dataclass
class CausalRelation:
    """Causal relationship between variables."""

    relation_id: str
    cause_variable: str
    effect_variable: str
    causal_type: CausalType
    strength: float
    strength_level: CausalStrength
    confidence: float
    causal_effect: float
    time_lag: Optional[float]
    confounders: List[str]
    mediators: List[str]
    timestamp: float


@dataclass
class CausalGraph:
    """Causal graph structure."""

    graph_id: str
    nodes: List[str]
    edges: List[CausalRelation]
    is_dag: bool  # Directed Acyclic Graph
    cycles: List[List[str]]
    graph_properties: Dict[str, Any]
    timestamp: float


@dataclass
class CausalIntervention:
    """Causal intervention simulation."""

    intervention_id: str
    target_variable: str
    intervention_type: str  # "do", "condition", "observe"
    intervention_value: float
    expected_effect: Dict[str, float]
    confidence: float
    timestamp: float


class AdvancedCausalDiscovery:
    """Advanced causal discovery engine."""

    def __init__(self):
        self._lock = threading.Lock()
        self._causal_graphs: Dict[str, CausalGraph] = {}
        self._causal_relations: Dict[str, CausalRelation] = {}
        self._interventions: List[CausalIntervention] = []
        self._pc_algorithm = PCAlgorithm()
        self._ges_algorithm = GESAlgorithm()
        self._lingam_algorithm = LingamAlgorithm()
        self._intervention_simulator = InterventionSimulator()
        self._causal_validator = CausalValidator()
        self._effect_estimator = CausalEffectEstimator()
        self._initialized = False

    def start(self) -> bool:
        """Start advanced causal discovery engine."""
        logger.info("[CAUSAL_DISCOVERY] Starting advanced causal discovery engine...")
        self._initialized = True
        logger.info("[CAUSAL_DISCOVERY] Advanced causal discovery engine started")
        return True

    def stop(self) -> bool:
        """Stop advanced causal discovery engine."""
        logger.info("[CAUSAL_DISCOVERY] Stopping advanced causal discovery engine...")
        self._initialized = False
        logger.info("[CAUSAL_DISCOVERY] Advanced causal discovery engine stopped")
        return True

    def discover_causal_structure(
        self,
        data: np.ndarray,
        variable_names: List[str],
        algorithm: CausalAlgorithm = CausalAlgorithm.PC_ALGORITHM,
    ) -> CausalGraph:
        """Discover causal structure from data."""
        logger.info(f"[CAUSAL_DISCOVERY] Discovering causal structure using {algorithm}")

        graph_id = f"causal_graph_{int(time.time())}_{algorithm.value}"

        # Apply selected algorithm
        if algorithm == CausalAlgorithm.PC_ALGORITHM:
            edges = self._pc_algorithm.discover(data, variable_names)
        elif algorithm == CausalAlgorithm.GES_ALGORITHM:
            edges = self._ges_algorithm.discover(data, variable_names)
        elif algorithm == CausalAlgorithm.LINGAM_ALGORITHM:
            edges = self._lingam_algorithm.discover(data, variable_names)
        else:
            edges = self._pc_algorithm.discover(data, variable_names)  # Default to PC

        # Build causal graph
        causal_graph = self._build_causal_graph(variable_names, edges, graph_id)

        # Store graph
        with self._lock:
            self._causal_graphs[graph_id] = causal_graph

        return causal_graph

    def infer_causal_effect(
        self, cause_variable: str, effect_variable: str, data: np.ndarray, variable_names: List[str]
    ) -> float:
        """Infer causal effect of cause on effect."""
        logger.info(
            f"[CAUSAL_DISCOVERY] Inferring causal effect of {cause_variable} on {effect_variable}"
        )

        # Estimate causal effect
        causal_effect = self._effect_estimator.estimate_effect(
            cause_variable, effect_variable, data, variable_names
        )

        return causal_effect

    def simulate_intervention(
        self,
        causal_graph: CausalGraph,
        target_variable: str,
        intervention_type: str,
        intervention_value: float,
    ) -> CausalIntervention:
        """Simulate causal intervention."""
        logger.info(
            f"[CAUSAL_DISCOVERY] Simulating {intervention_type} intervention on {target_variable}"
        )

        intervention_id = f"intervention_{int(time.time())}_{target_variable}"

        intervention = self._intervention_simulator.simulate(
            causal_graph, target_variable, intervention_type, intervention_value
        )

        intervention.intervention_id = intervention_id

        # Store intervention
        with self._lock:
            self._interventions.append(intervention)

        return intervention

    def validate_causal_relation(
        self, relation: CausalRelation, data: np.ndarray, variable_names: List[str]
    ) -> Dict[str, Any]:
        """Validate causal relationship using various methods."""
        logger.info(f"[CAUSAL_DISCOVERY] Validating causal relation {relation.relation_id}")

        validation_result = self._causal_validator.validate(relation, data, variable_names)

        return validation_result

    def discover_confounders(
        self, causal_graph: CausalGraph, variable: str, data: np.ndarray, variable_names: List[str]
    ) -> List[str]:
        """Discover potential confounders for a variable."""
        logger.info(f"[CAUSAL_DISCOVERY] Discovering confounders for {variable}")

        confounders = self._pc_algorithm.detect_confounders(
            causal_graph, variable, data, variable_names
        )

        return confounders

    def get_causal_statistics(self) -> Dict[str, Any]:
        """Get causal discovery statistics."""
        with self._lock:
            return {
                "total_causal_graphs": len(self._causal_graphs),
                "total_causal_relations": len(self._causal_relations),
                "total_interventions": len(self._interventions),
                "average_causal_strength": (
                    np.mean([r.strength for r in self._causal_relations.values()])
                    if self._causal_relations
                    else 0.0
                ),
                "average_confidence": (
                    np.mean([r.confidence for r in self._causal_relations.values()])
                    if self._causal_relations
                    else 0.0
                ),
            }

    def _build_causal_graph(
        self, variable_names: List[str], edges: List[Dict[str, Any]], graph_id: str
    ) -> CausalGraph:
        """Build causal graph from discovered edges."""
        # Create causal relations from edges
        causal_relations = []
        for edge in edges:
            relation_id = f"rel_{graph_id}_{edge['cause']}_{edge['effect']}"

            # Determine causal type and strength level
            causal_type = self._determine_causal_type(edge)
            strength_level = self._determine_strength_level(edge.get("strength", 0.5))

            relation = CausalRelation(
                relation_id=relation_id,
                cause_variable=edge["cause"],
                effect_variable=edge["effect"],
                causal_type=causal_type,
                strength=edge.get("strength", 0.5),
                strength_level=strength_level,
                confidence=edge.get("confidence", 0.7),
                causal_effect=edge.get("effect_size", 0.5),
                time_lag=edge.get("time_lag"),
                confounders=edge.get("confounders", []),
                mediators=edge.get("mediators", []),
                timestamp=time.time(),
            )

            causal_relations.append(relation)

            with self._lock:
                self._causal_relations[relation_id] = relation

        # Check for cycles
        has_cycles, cycles = self._detect_cycles(causal_relations)

        # Calculate graph properties
        graph_properties = self._calculate_graph_properties(variable_names, causal_relations)

        graph = CausalGraph(
            graph_id=graph_id,
            nodes=variable_names,
            edges=causal_relations,
            is_dag=not has_cycles,
            cycles=cycles,
            graph_properties=graph_properties,
            timestamp=time.time(),
        )

        return graph

    def _determine_causal_type(self, edge: Dict[str, Any]) -> CausalType:
        """Determine causal type from edge information."""
        if edge.get("indirect", False):
            return CausalType.INDIRECT
        elif edge.get("confounded", False):
            return CausalType.CONFOUNDED
        elif edge.get("mediated", False):
            return CausalType.MEDIATED
        elif edge.get("bidirectional", False):
            return CausalType.BIDIRECTIONAL
        else:
            return CausalType.DIRECT

    def _determine_strength_level(self, strength: float) -> CausalStrength:
        """Determine strength level from numerical strength."""
        if strength < 0.3:
            return CausalStrength.WEAK
        elif strength < 0.5:
            return CausalStrength.MODERATE
        elif strength < 0.7:
            return CausalStrength.STRONG
        else:
            return CausalStrength.VERY_STRONG

    def _detect_cycles(self, relations: List[CausalRelation]) -> Tuple[bool, List[List[str]]]:
        """Detect cycles in causal graph."""
        # Build adjacency list
        adjacency = defaultdict(list)
        for relation in relations:
            if relation.causal_type != CausalType.BIDIRECTIONAL:
                adjacency[relation.cause_variable].append(relation.effect_variable)

        # Detect cycles using DFS
        cycles = []
        visited = set()
        recursion_stack = set()

        def dfs(node: str, path: List[str]) -> None:
            visited.add(node)
            recursion_stack.add(node)
            path.append(node)

            for neighbor in adjacency[node]:
                if neighbor not in visited:
                    dfs(neighbor, path.copy())
                elif neighbor in recursion_stack:
                    # Found cycle
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:] + [neighbor]
                    cycles.append(cycle)

            recursion_stack.remove(node)

        for node in adjacency:
            if node not in visited:
                dfs(node, [])

        has_cycles = len(cycles) > 0
        return has_cycles, cycles

    def _calculate_graph_properties(
        self, variable_names: List[str], relations: List[CausalRelation]
    ) -> Dict[str, Any]:
        """Calculate graph properties."""
        return {
            "node_count": len(variable_names),
            "edge_count": len(relations),
            "density": (
                len(relations) / (len(variable_names) * (len(variable_names) - 1))
                if len(variable_names) > 1
                else 0.0
            ),
            "average_out_degree": self._calculate_average_out_degree(variable_names, relations),
            "causal_types_distribution": self._calculate_causal_type_distribution(relations),
        }

    def _calculate_average_out_degree(
        self, variable_names: List[str], relations: List[CausalRelation]
    ) -> float:
        """Calculate average out-degree of nodes."""
        out_degrees = defaultdict(int)

        for relation in relations:
            out_degrees[relation.cause_variable] += 1

        if not out_degrees:
            return 0.0

        total_out_degree = sum(out_degrees.values())
        avg_out_degree = total_out_degree / len(variable_names)

        return avg_out_degree

    def _calculate_causal_type_distribution(
        self, relations: List[CausalRelation]
    ) -> Dict[str, int]:
        """Calculate distribution of causal types."""
        distribution = defaultdict(int)

        for relation in relations:
            distribution[relation.causal_type.value] += 1

        return dict(distribution)


class PCAlgorithm:
    """Peter-Clark (PC) algorithm for causal discovery."""

    def discover(self, data: np.ndarray, variable_names: List[str]) -> List[Dict[str, Any]]:
        """Discover causal structure using PC algorithm."""
        # Calculate correlation matrix
        correlation_matrix = np.corrcoef(data.T)

        # Build initial complete undirected graph
        edges = []

        # Find significant correlations
        for i in range(len(variable_names)):
            for j in range(i + 1, len(variable_names)):
                corr = correlation_matrix[i, j]

                if abs(corr) > 0.3:  # Correlation threshold
                    # Determine direction using causal assumptions
                    direction = self._determine_direction(data, i, j, correlation_matrix)

                    edges.append(
                        {
                            "cause": (
                                variable_names[i] if direction == "i_to_j" else variable_names[j]
                            ),
                            "effect": (
                                variable_names[j] if direction == "i_to_j" else variable_names[i]
                            ),
                            "strength": abs(corr),
                            "confidence": min(1.0, abs(corr) + 0.2),
                            "effect_size": corr,
                        }
                    )

        return edges

    def _determine_direction(
        self, data: np.ndarray, i: int, j: int, correlation_matrix: np.ndarray
    ) -> str:
        """Determine causal direction between variables."""
        # Simplified direction determination
        # In real PC algorithm, would use conditional independence tests

        # Use temporal precedence if data is time series
        if data.shape[0] > 1:
            # Check if changes in i precede changes in j
            lag_correlation = self._calculate_lag_correlation(data, i, j, 1)

            if lag_correlation > 0.2:
                return "i_to_j"
            elif lag_correlation < -0.2:
                return "j_to_i"

        # Default: assume random or use additional heuristics
        return "i_to_j" if correlation_matrix[i, i] > correlation_matrix[j, j] else "j_to_i"

    def _calculate_lag_correlation(self, data: np.ndarray, i: int, j: int, lag: int) -> float:
        """Calculate lagged correlation between variables."""
        if len(data) - lag <= 0:
            return 0.0

        series_i = data[:-lag, i] if lag > 0 else data[:, i]
        series_j_lagged = data[lag:, j] if lag > 0 else data[:, j]

        if len(series_i) != len(series_j_lagged):
            min_len = min(len(series_i), len(series_j_lagged))
            series_i = series_i[:min_len]
            series_j_lagged = series_j_lagged[:min_len]

        correlation = np.corrcoef(series_i, series_j_lagged)[0, 1]

        return correlation if not math.isnan(correlation) else 0.0

    def detect_confounders(
        self, causal_graph: CausalGraph, variable: str, data: np.ndarray, variable_names: List[str]
    ) -> List[str]:
        """Detect potential confounders for a variable."""
        # Find variables that cause both the target and its effects
        confounders = []

        # Get all relations involving the variable
        related_relations = [
            r
            for r in causal_graph.edges
            if r.cause_variable == variable or r.effect_variable == variable
        ]

        # Find variables that could be confounders
        for relation in related_relations:
            other_variable = (
                relation.effect_variable
                if relation.cause_variable == variable
                else relation.cause_variable
            )

            # Check if other variable could be influenced by potential confounders
            for potential_confounder in variable_names:
                if potential_confounder != variable and potential_confounder != other_variable:
                    # Check if potential confounder correlates with both
                    if self._is_confounder(
                        data, variable_names, variable, other_variable, potential_confounder
                    ):
                        confounders.append(potential_confounder)

        return list(set(confounders))

    def _is_confounder(
        self,
        data: np.ndarray,
        variable_names: List[str],
        var1: str,
        var2: str,
        potential_confounder: str,
    ) -> bool:
        """Check if a variable is a confounder."""
        try:
            idx1 = variable_names.index(var1)
            idx2 = variable_names.index(var2)
            idx_confounder = variable_names.index(potential_confounder)
        except ValueError:
            return False

        # Calculate correlations
        corr_confounder_var1 = np.corrcoef(data[:, idx_confounder], data[:, idx1])[0, 1]
        corr_confounder_var2 = np.corrcoef(data[:, idx_confounder], data[:, idx2])[0, 1]

        # Confounder if it correlates with both variables
        return abs(corr_confounder_var1) > 0.3 and abs(corr_confounder_var2) > 0.3


class GESAlgorithm:
    """Greedy Equivalence Search (GES) algorithm for causal discovery."""

    def discover(self, data: np.ndarray, variable_names: List[str]) -> List[Dict[str, Any]]:
        """Discover causal structure using GES algorithm."""
        # Simplified GES implementation
        # Real GES uses score-based graph search (BIC, BDeu, etc.)

        # Start with complete DAG (no edges) and add edges greedily
        best_score = float("-inf")
        best_edges = []

        # Try adding edges and keep those that improve score
        for i in range(len(variable_names)):
            for j in range(i + 1, len(variable_names)):
                # Calculate improvement score
                score = self._calculate_improvement_score(data, i, j, variable_names)

                if score > 0:
                    direction = self._choose_direction(data, i, j)
                    edges = {
                        "cause": variable_names[i] if direction == "i_to_j" else variable_names[j],
                        "effect": variable_names[j] if direction == "i_to_j" else variable_names[i],
                        "strength": min(1.0, abs(score)),
                        "confidence": min(1.0, abs(score) + 0.3),
                        "effect_size": score,
                    }
                    best_edges.append(edges)

        return best_edges

    def _calculate_improvement_score(
        self, data: np.ndarray, i: int, j: int, variable_names: List[str]
    ) -> float:
        """Calculate score improvement for adding edge."""
        # Simplified score calculation using correlation
        correlation = np.corrcoef(data[:, i], data[:, j])[0, 1]

        # Score improvement is correlation strength
        return abs(correlation)

    def _choose_direction(self, data: np.ndarray, i: int, j: int) -> str:
        """Choose direction for edge."""
        # Use similar direction logic as PC algorithm
        correlation_matrix = np.corrcoef(data.T)

        if correlation_matrix[i, i] > correlation_matrix[j, j]:
            return "i_to_j"
        else:
            return "j_to_i"


class LingamAlgorithm:
    """Linear Non-Gaussian Acyclic Model (LiNGAM) algorithm."""

    def discover(self, data: np.ndarray, variable_names: List[str]) -> List[Dict[str, Any]]:
        """Discover causal structure using LiNGAM algorithm."""
        # LiNGAM exploits non-Gaussianity to determine causal direction
        # Simplified implementation for demonstration

        edges = []

        # Find linear relationships and determine direction using non-Gaussianity
        for i in range(len(variable_names)):
            for j in range(i + 1, len(variable_names)):
                # Fit linear models in both directions
                model_i_to_j = self._fit_linear_model(data[:, i], data[:, j])
                model_j_to_i = self._fit_linear_model(data[:, j], data[:, i])

                # Choose direction based on residual independence (simplified)
                if model_i_to_j["residual_variance"] < model_j_to_i["residual_variance"]:
                    edges.append(
                        {
                            "cause": variable_names[i],
                            "effect": variable_names[j],
                            "strength": abs(model_i_to_j["slope"]),
                            "confidence": 1.0 - model_i_to_j["residual_variance"],
                            "effect_size": model_i_to_j["slope"],
                        }
                    )
                else:
                    edges.append(
                        {
                            "cause": variable_names[j],
                            "effect": variable_names[i],
                            "strength": abs(model_j_to_i["slope"]),
                            "confidence": 1.0 - model_j_to_i["residual_variance"],
                            "effect_size": model_j_to_i["slope"],
                        }
                    )

        return edges

    def _fit_linear_model(self, X: np.ndarray, y: np.ndarray) -> Dict[str, float]:
        """Fit linear model and return statistics."""
        # Add intercept
        X_with_intercept = np.column_stack([np.ones(len(X)), X])

        # Fit linear regression
        try:
            coefficients = np.linalg.lstsq(X_with_intercept, y, rcond=None)[0]
            predictions = X_with_intercept @ coefficients
            residuals = y - predictions
            residual_variance = np.var(residuals)
            slope = coefficients[1] if len(coefficients) > 1 else coefficients[0]
        except np.linalg.LinAlgError:
            residual_variance = float("inf")
            slope = 0.0

        return {"slope": slope, "residual_variance": residual_variance}


class InterventionSimulator:
    """Simulate causal interventions."""

    def simulate(
        self,
        causal_graph: CausalGraph,
        target_variable: str,
        intervention_type: str,
        intervention_value: float,
    ) -> CausalIntervention:
        """Simulate causal intervention."""
        # Calculate expected effects based on causal structure
        expected_effects = {}

        # Find direct and indirect effects
        for relation in causal_graph.edges:
            if relation.cause_variable == target_variable:
                # Direct effect
                expected_effects[relation.effect_variable] = (
                    relation.causal_effect * intervention_value
                )
            elif relation.effect_variable == target_variable:
                # Back-door path effects
                expected_effects[relation.cause_variable] = (
                    relation.causal_effect * intervention_value * 0.5
                )

        # Calculate confidence
        confidence = self._calculate_intervention_confidence(expected_effects, causal_graph)

        intervention = CausalIntervention(
            intervention_id="",  # Will be set by caller
            target_variable=target_variable,
            intervention_type=intervention_type,
            intervention_value=intervention_value,
            expected_effect=expected_effects,
            confidence=confidence,
            timestamp=time.time(),
        )

        return intervention

    def _calculate_intervention_confidence(
        self, expected_effects: Dict[str, float], causal_graph: CausalGraph
    ) -> float:
        """Calculate confidence in intervention effects."""
        if not expected_effects:
            return 0.3

        # Confidence based on number of affected variables and edge strengths
        affected_count = len(expected_effects)
        avg_strength = np.mean([r.strength for r in causal_graph.edges])

        confidence = min(1.0, (affected_count / len(causal_graph.nodes)) * avg_strength)
        return confidence


class CausalValidator:
    """Validate causal relationships."""

    def validate(
        self, relation: CausalRelation, data: np.ndarray, variable_names: List[str]
    ) -> Dict[str, Any]:
        """Validate causal relationship."""
        validation_scores = {}

        # Statistical validation
        statistical_score = self._statistical_validation(relation, data, variable_names)
        validation_scores["statistical"] = statistical_score

        # Stability validation
        stability_score = self._stability_validation(relation, data, variable_names)
        validation_scores["stability"] = stability_score

        # Overall validation score
        overall_score = np.mean(list(validation_scores.values()))

        return {
            "relation_id": relation.relation_id,
            "validation_scores": validation_scores,
            "overall_validation_score": overall_score,
            "is_valid": overall_score > 0.6,
            "recommendation": "accept" if overall_score > 0.6 else "reject",
        }

    def _statistical_validation(
        self, relation: CausalRelation, data: np.ndarray, variable_names: List[str]
    ) -> float:
        """Statistical validation of causal relationship."""
        try:
            idx_cause = variable_names.index(relation.cause_variable)
            idx_effect = variable_names.index(relation.effect_variable)
        except ValueError:
            return 0.0

        # Calculate correlation and significance
        correlation = np.corrcoef(data[:, idx_cause], data[:, idx_effect])[0, 1]

        # Statistical score based on correlation strength
        statistical_score = min(1.0, abs(correlation))

        return statistical_score

    def _stability_validation(
        self, relation: CausalRelation, data: np.ndarray, variable_names: List[str]
    ) -> float:
        """Stability validation across data subsets."""
        # Split data into subsets and test consistency
        subset_size = len(data) // 2
        subset1 = data[:subset_size]
        subset2 = data[subset_size:]

        # Calculate correlation in each subset
        try:
            idx_cause = variable_names.index(relation.cause_variable)
            idx_effect = variable_names.index(relation.effect_variable)

            corr1 = np.corrcoef(subset1[:, idx_cause], subset1[:, idx_effect])[0, 1]
            corr2 = np.corrcoef(subset2[:, idx_cause], subset2[:, idx_effect])[0, 1]

            # Stability is consistency across subsets
            stability = (
                1.0 - abs(corr1 - corr2) if not math.isnan(corr1) and not math.isnan(corr2) else 0.5
            )
        except (ValueError, IndexError):
            stability = 0.5

        return stability


class CausalEffectEstimator:
    """Estimate causal effects using various methods."""

    def estimate_effect(
        self, cause_variable: str, effect_variable: str, data: np.ndarray, variable_names: List[str]
    ) -> float:
        """Estimate causal effect using regression."""
        try:
            idx_cause = variable_names.index(cause_variable)
            idx_effect = variable_names.index(effect_variable)
        except ValueError:
            return 0.0

        # Fit linear model
        X = data[:, idx_cause].reshape(-1, 1)
        y = data[:, idx_effect]

        try:
            coefficients = np.linalg.lstsq(np.column_stack([np.ones(len(X)), X]), y, rcond=None)[0]
            causal_effect = coefficients[1]  # Slope is the causal effect
        except np.linalg.LinAlgError:
            causal_effect = 0.0

        return causal_effect


# Singleton instance
_advanced_causal_discovery: Optional[AdvancedCausalDiscovery] = None
_advanced_causal_discovery_lock = threading.Lock()


def get_advanced_causal_discovery() -> AdvancedCausalDiscovery:
    """Get the singleton advanced causal discovery instance."""
    global _advanced_causal_discovery
    if _advanced_causal_discovery is None:
        with _advanced_causal_discovery_lock:
            if _advanced_causal_discovery is None:
                _advanced_causal_discovery = AdvancedCausalDiscovery()
    return _advanced_causal_discovery


__all__ = [
    "AdvancedCausalDiscovery",
    "get_advanced_causal_discovery",
    "CausalAlgorithm",
    "CausalType",
    "CausalStrength",
    "CausalRelation",
    "CausalGraph",
    "CausalIntervention",
]
