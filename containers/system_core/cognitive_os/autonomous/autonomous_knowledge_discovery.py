"""Autonomous Knowledge Discovery - Self-Improving Knowledge System.

This module provides autonomous knowledge discovery capabilities that enable the system
to continuously learn, discover patterns, generate hypotheses, and refine its knowledge base
without human intervention.
"""

from __future__ import annotations

import logging
import math
import threading
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

import numpy as np

logger = logging.getLogger(__name__)


class DiscoveryMode(str, Enum):
    """Autonomous discovery modes."""

    EXPLORATORY = "EXPLORATORY"
    HYPOTHESIS_DRIVEN = "HYPOTHESIS_DRIVEN"
    PATTERN_RECOGNITION = "PATTERN_RECOGNITION"
    KNOWLEDGE_REFINEMENT = "KNOWLEDGE_REFINEMENT"
    CROSS_DOMAIN_LEARNING = "CROSS_DOMAIN_LEARNING"


class ConfidenceLevel(str, Enum):
    """Confidence levels for discovered knowledge."""

    VERY_LOW = "VERY_LOW"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    VERY_HIGH = "VERY_HIGH"
    CERTAIN = "CERTAIN"


@dataclass
class DiscoveredKnowledge:
    """Knowledge discovered autonomously."""

    discovery_id: str
    content: str
    confidence: ConfidenceLevel
    confidence_score: float
    discovery_method: str
    source_data: Dict[str, Any]
    validation_status: str  # "pending", "validated", "rejected"
    validation_score: float
    timestamp: float
    usage_count: int = 0
    feedback_history: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class Hypothesis:
    """Hypothesis generated for testing."""

    hypothesis_id: str
    statement: str
    supporting_evidence: List[str]
    contradictory_evidence: List[str]
    confidence: float
    priority: int
    test_status: str  # "pending", "testing", "validated", "rejected"
    test_results: Dict[str, Any]
    timestamp: float


@dataclass
class Pattern:
    """Pattern discovered in data."""

    pattern_id: str
    pattern_type: str  # "temporal", "correlation", "causal", "behavioral"
    description: str
    strength: float
    frequency: int
    confidence: float
    predictive_power: float
    last_observed: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class KnowledgeEvolution:
    """Evolution of knowledge over time."""

    evolution_id: str
    knowledge_id: str
    original_version: str
    current_version: str
    evolution_type: str  # "refinement", "expansion", "contradiction", "specialization"
    confidence_change: float
    timestamp: float


class AutonomousKnowledgeDiscovery:
    """Autonomous knowledge discovery system."""

    def __init__(self, discovery_interval: float = 300.0):
        self._lock = threading.Lock()
        self._discovery_interval = discovery_interval
        self._discovery_mode = DiscoveryMode.EXPLORATORY
        self._discovered_knowledge: Dict[str, DiscoveredKnowledge] = {}
        self._hypotheses: Dict[str, Hypothesis] = {}
        self._patterns: Dict[str, Pattern] = {}
        self._knowledge_evolution: List[KnowledgeEvolution] = []
        self._data_streams: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self._pattern_recognizer = PatternRecognizer()
        self._hypothesis_generator = HypothesisGenerator()
        self._knowledge_validator = KnowledgeValidator()
        self._adaptive_learner = AdaptiveLearner()
        self._cross_domain_learner = CrossDomainLearner()
        self._discovery_thread = None
        self._stop_event = threading.Event()
        self._initialized = False

    def start(self) -> bool:
        """Start autonomous knowledge discovery."""
        logger.info("[AUTONOMOUS_DISCOVERY] Starting autonomous knowledge discovery...")

        # Start discovery thread
        self._stop_event.clear()
        self._discovery_thread = threading.Thread(target=self._discovery_loop, daemon=True)
        self._discovery_thread.start()

        self._initialized = True
        logger.info("[AUTONOMOUS_DISCOVERY] Autonomous knowledge discovery started")
        return True

    def stop(self) -> bool:
        """Stop autonomous knowledge discovery."""
        logger.info("[AUTONOMOUS_DISCOVERY] Stopping autonomous knowledge discovery...")

        self._stop_event.set()
        if self._discovery_thread:
            self._discovery_thread.join(timeout=10.0)

        self._initialized = False
        logger.info("[AUTONOMOUS_DISCOVERY] Autonomous knowledge discovery stopped")
        return True

    def _discovery_loop(self):
        """Main discovery loop running in background thread."""
        while not self._stop_event.is_set():
            try:
                # Perform discovery based on current mode
                if self._discovery_mode == DiscoveryMode.EXPLORATORY:
                    self._exploratory_discovery()
                elif self._discovery_mode == DiscoveryMode.HYPOTHESIS_DRIVEN:
                    self._hypothesis_driven_discovery()
                elif self._discovery_mode == DiscoveryMode.PATTERN_RECOGNITION:
                    self._pattern_recognition_discovery()
                elif self._discovery_mode == DiscoveryMode.KNOWLEDGE_REFINEMENT:
                    self._knowledge_refinement_discovery()
                elif self._discovery_mode == DiscoveryMode.CROSS_DOMAIN_LEARNING:
                    self._cross_domain_discovery()

                # Adaptive learning from feedback
                self._adaptive_learning_cycle()

                # Wait for next discovery cycle
                self._stop_event.wait(self._discovery_interval)

            except Exception as e:
                logger.error(f"[AUTONOMOUS_DISCOVERY] Discovery cycle error: {e}")

    def set_discovery_mode(self, mode: DiscoveryMode) -> None:
        """Set discovery mode."""
        with self._lock:
            self._discovery_mode = mode
            logger.info(f"[AUTONOMOUS_DISCOVERY] Discovery mode set to {mode}")

    def add_data_stream(self, stream_id: str, data: Any) -> None:
        """Add data to discovery stream."""
        with self._lock:
            self._data_streams[stream_id].append({"data": data, "timestamp": time.time()})

    def _exploratory_discovery(self) -> None:
        """Exploratory discovery - searching for new patterns without specific targets."""
        logger.debug("[AUTONOMOUS_DISCOVERY] Performing exploratory discovery")

        # Analyze all data streams for novel patterns
        for stream_id, data_stream in self._data_streams.items():
            if len(data_stream) < 10:
                continue

            # Extract data for analysis
            data_points = [dp["data"] for dp in list(data_stream)]

            # Discover patterns
            new_patterns = self._pattern_recognizer.discover_patterns(data_points, stream_id)

            # Process discovered patterns
            for pattern in new_patterns:
                pattern_id = f"pattern_{int(time.time())}_{hash(pattern.description) % 10000}"

                # Check if similar pattern exists
                existing = self._find_similar_pattern(pattern)
                if existing:
                    # Strengthen existing pattern
                    existing.frequency += 1
                    existing.strength = min(1.0, existing.strength + 0.1)
                else:
                    # Add new pattern
                    self._patterns[pattern_id] = pattern

    def _hypothesis_driven_discovery(self) -> None:
        """Hypothesis-driven discovery - generate and test hypotheses."""
        logger.debug("[AUTONOMOUS_DISCOVERY] Performing hypothesis-driven discovery")

        # Generate hypotheses from current knowledge
        current_knowledge = list(self._discovered_knowledge.values())
        if len(current_knowledge) < 5:
            return

        # Generate new hypotheses
        new_hypotheses = self._hypothesis_generator.generate(current_knowledge, self._patterns)

        # Process new hypotheses
        for hypothesis in new_hypotheses:
            # Check if similar hypothesis exists
            existing = self._find_similar_hypothesis(hypothesis)
            if not existing:
                self._hypotheses[hypothesis.hypothesis_id] = hypothesis
                logger.info(
                    f"[AUTONOMOUS_DISCOVERY] Generated new hypothesis: {hypothesis.statement[:50]}..."
                )

    def _pattern_recognition_discovery(self) -> None:
        """Pattern recognition discovery - focus on identifying patterns."""
        logger.debug("[AUTONOMOUS_DISCOVERY] Performing pattern recognition discovery")

        # Deep pattern analysis on data streams
        for stream_id, data_stream in self._data_streams.items():
            if len(data_stream) < 20:
                continue

            # Advanced pattern recognition
            data_points = [dp["data"] for dp in list(data_stream)]
            advanced_patterns = self._pattern_recognizer.advanced_recognition(
                data_points, stream_id
            )

            # Process advanced patterns
            for pattern in advanced_patterns:
                if pattern.predictive_power > 0.7:  # High predictive power patterns
                    # Convert to knowledge
                    knowledge = self._pattern_to_knowledge(pattern)
                    if knowledge:
                        self._discovered_knowledge[knowledge.discovery_id] = knowledge
                        logger.info(
                            f"[AUTONOMOUS_DISCOVERY] Discovered high-value knowledge: {knowledge.content[:50]}..."
                        )

    def _knowledge_refinement_discovery(self) -> None:
        """Knowledge refinement discovery - improve existing knowledge."""
        logger.debug("[AUTONOMOUS_DISCOVERY] Performing knowledge refinement discovery")

        # Refine existing knowledge based on new data
        for knowledge_id, knowledge in list(self._discovered_knowledge.items()):
            if knowledge.validation_status == "validated" and knowledge.usage_count > 5:
                # Check for refinement opportunities
                refinement = self._knowledge_validator.refine_knowledge(
                    knowledge, self._data_streams
                )

                if refinement:
                    # Create knowledge evolution record
                    evolution = KnowledgeEvolution(
                        evolution_id=f"evol_{int(time.time())}_{knowledge_id}",
                        knowledge_id=knowledge_id,
                        original_version=knowledge.content,
                        current_version=refinement,
                        evolution_type="refinement",
                        confidence_change=refinement.get("confidence_change", 0.0),
                        timestamp=time.time(),
                    )

                    self._knowledge_evolution.append(evolution)

                    # Update knowledge
                    knowledge.content = refinement
                    knowledge.validation_score += 0.1
                    knowledge.timestamp = time.time()

    def _cross_domain_discovery(self) -> None:
        """Cross-domain discovery - transfer knowledge between domains."""
        logger.debug("[AUTONOMOUS_DISCOVERY] Performing cross-domain discovery")

        # Discover cross-domain patterns
        cross_domain_patterns = self._cross_domain_learner.discover_patterns(
            self._data_streams, self._patterns
        )

        # Process cross-domain patterns
        for pattern in cross_domain_patterns:
            # Create knowledge from cross-domain pattern
            knowledge = self._pattern_to_knowledge(pattern)
            if knowledge:
                knowledge.metadata["cross_domain"] = True
                self._discovered_knowledge[knowledge.discovery_id] = knowledge
                logger.info(
                    f"[AUTONOMOUS_DISCOVERY] Discovered cross-domain knowledge: {knowledge.content[:50]}..."
                )

    def _adaptive_learning_cycle(self) -> None:
        """Adaptive learning cycle from feedback."""
        # Learn from feedback on discovered knowledge
        for knowledge_id, knowledge in self._discovered_knowledge.items():
            if knowledge.feedback_history:
                # Analyze feedback
                feedback_scores = [fb.get("score", 0.5) for fb in knowledge.feedback_history]
                avg_feedback = np.mean(feedback_scores)

                # Adjust confidence based on feedback
                if avg_feedback > 0.7:
                    knowledge.confidence_score = min(1.0, knowledge.confidence_score + 0.05)
                elif avg_feedback < 0.3:
                    knowledge.confidence_score = max(0.0, knowledge.confidence_score - 0.1)

                # Update confidence level
                knowledge.confidence = self._score_to_confidence(knowledge.confidence_score)

    def _find_similar_pattern(self, pattern: Pattern) -> Optional[Pattern]:
        """Find similar existing pattern."""
        for existing_pattern in self._patterns.values():
            similarity = self._calculate_pattern_similarity(pattern, existing_pattern)
            if similarity > 0.8:  # High similarity threshold
                return existing_pattern
        return None

    def _find_similar_hypothesis(self, hypothesis: Hypothesis) -> Optional[Hypothesis]:
        """Find similar existing hypothesis."""
        for existing_hypothesis in self._hypotheses.values():
            if self._calculate_hypothesis_similarity(hypothesis, existing_hypothesis) > 0.8:
                return existing_hypothesis
        return None

    def _pattern_to_knowledge(self, pattern: Pattern) -> Optional[DiscoveredKnowledge]:
        """Convert pattern to knowledge."""
        if pattern.strength < 0.5 or pattern.predictive_power < 0.3:
            return None

        knowledge = DiscoveredKnowledge(
            discovery_id=f"know_{int(time.time())}_{hash(pattern.description) % 10000}",
            content=f"Pattern discovered: {pattern.description}",
            confidence=self._score_to_confidence(pattern.strength),
            confidence_score=pattern.strength,
            discovery_method="pattern_recognition",
            source_data=pattern.metadata,
            validation_status="pending",
            validation_score=pattern.confidence,
            timestamp=time.time(),
        )

        return knowledge

    def _calculate_pattern_similarity(self, pattern1: Pattern, pattern2: Pattern) -> float:
        """Calculate similarity between two patterns."""
        if pattern1.pattern_type != pattern2.pattern_type:
            return 0.0

        # Simple description similarity
        words1 = set(pattern1.description.lower().split())
        words2 = set(pattern2.description.lower().split())

        if not (words1 | words2):
            return 0.0

        similarity = len(words1 & words2) / len(words1 | words2)
        return similarity

    def _calculate_hypothesis_similarity(
        self, hypothesis1: Hypothesis, hypothesis2: Hypothesis
    ) -> float:
        """Calculate similarity between two hypotheses."""
        words1 = set(hypothesis1.statement.lower().split())
        words2 = set(hypothesis2.statement.lower().split())

        if not (words1 | words2):
            return 0.0

        similarity = len(words1 & words2) / len(words1 | words2)
        return similarity

    def _score_to_confidence(self, score: float) -> ConfidenceLevel:
        """Convert score to confidence level."""
        if score > 0.9:
            return ConfidenceLevel.VERY_HIGH
        elif score > 0.75:
            return ConfidenceLevel.HIGH
        elif score > 0.5:
            return ConfidenceLevel.MEDIUM
        elif score > 0.25:
            return ConfidenceLevel.LOW
        elif score > 0.1:
            return ConfidenceLevel.VERY_LOW
        else:
            return ConfidenceLevel.CERTAIN

    def add_feedback(self, knowledge_id: str, feedback: Dict[str, Any]) -> None:
        """Add feedback for discovered knowledge."""
        with self._lock:
            if knowledge_id in self._discovered_knowledge:
                self._discovered_knowledge[knowledge_id].feedback_history.append(
                    {"timestamp": time.time(), **feedback}
                )
                self._discovered_knowledge[knowledge_id].usage_count += 1

    def get_discovery_statistics(self) -> Dict[str, Any]:
        """Get discovery statistics."""
        with self._lock:
            validated_knowledge = sum(
                1 for k in self._discovered_knowledge.values() if k.validation_status == "validated"
            )
            pending_hypotheses = sum(
                1 for h in self._hypotheses.values() if h.test_status == "pending"
            )
            high_value_patterns = sum(
                1 for p in self._patterns.values() if p.predictive_power > 0.7
            )

            return {
                "discovery_mode": self._discovery_mode.value,
                "total_discovered_knowledge": len(self._discovered_knowledge),
                "validated_knowledge": validated_knowledge,
                "total_hypotheses": len(self._hypotheses),
                "pending_hypotheses": pending_hypotheses,
                "total_patterns": len(self._patterns),
                "high_value_patterns": high_value_patterns,
                "knowledge_evolution_count": len(self._knowledge_evolution),
                "active_data_streams": len(self._data_streams),
                "discovery_interval": self._discovery_interval,
            }


class PatternRecognizer:
    """Advanced pattern recognition in data streams."""

    def discover_patterns(self, data_points: List[Any], stream_id: str) -> List[Pattern]:
        """Discover patterns in data stream."""
        patterns = []

        if len(data_points) < 10:
            return patterns

        # Convert to numerical if possible
        numerical_data = self._extract_numerical_features(data_points)
        if not numerical_data:
            return patterns

        # Discover temporal patterns
        temporal_patterns = self._discover_temporal_patterns(numerical_data, stream_id)
        patterns.extend(temporal_patterns)

        # Discover correlation patterns
        correlation_patterns = self._discover_correlation_patterns(numerical_data, stream_id)
        patterns.extend(correlation_patterns)

        # Discover behavioral patterns
        behavioral_patterns = self._discover_behavioral_patterns(data_points, stream_id)
        patterns.extend(behavioral_patterns)

        return patterns

    def advanced_recognition(self, data_points: List[Any], stream_id: str) -> List[Pattern]:
        """Advanced pattern recognition with predictive power assessment."""
        patterns = []

        numerical_data = self._extract_numerical_features(data_points)
        if not numerical_data:
            return patterns

        # Causal pattern discovery
        causal_patterns = self._discover_causal_patterns(numerical_data, stream_id)
        patterns.extend(causal_patterns)

        # Predictive pattern discovery
        predictive_patterns = self._discover_predictive_patterns(numerical_data, stream_id)
        patterns.extend(predictive_patterns)

        # Calculate predictive power for all patterns
        for pattern in patterns:
            pattern.predictive_power = self._calculate_predictive_power(pattern, numerical_data)

        return patterns

    def _extract_numerical_features(self, data_points: List[Any]) -> Optional[List[List[float]]]:
        """Extract numerical features from data points."""
        numerical_data = []

        for dp in data_points:
            if isinstance(dp, (int, float)):
                numerical_data.append([float(dp)])
            elif isinstance(dp, dict):
                # Extract numerical values from dictionary
                numerical_values = []
                for value in dp.values():
                    if isinstance(value, (int, float)):
                        numerical_values.append(float(value))
                if numerical_values:
                    numerical_data.append(numerical_values)
            elif isinstance(dp, list):
                # Extract numerical values from list
                numerical_values = []
                for value in dp:
                    if isinstance(value, (int, float)):
                        numerical_values.append(float(value))
                if numerical_values:
                    numerical_data.append(numerical_values)

        return numerical_data if numerical_data else None

    def _discover_temporal_patterns(self, data: List[List[float]], stream_id: str) -> List[Pattern]:
        """Discover temporal patterns in data."""
        patterns = []

        if len(data) < 10:
            return patterns

        # Analyze time series patterns
        for feature_idx in range(len(data[0])):
            feature_values = [dp[feature_idx] for dp in data]

            # Calculate autocorrelation
            autocorr = self._calculate_autocorrelation(feature_values)

            if abs(autocorr) > 0.7:  # Strong autocorrelation
                pattern_type = (
                    "positive_autocorrelation" if autocorr > 0 else "negative_autocorrelation"
                )

                pattern = Pattern(
                    pattern_id=f"temp_{int(time.time())}_{stream_id}_{feature_idx}",
                    pattern_type="temporal",
                    description=f"{pattern_type} detected in feature {feature_idx}",
                    strength=abs(autocorr),
                    frequency=len(data),
                    confidence=0.8,
                    predictive_power=0.0,  # Will be calculated later
                    last_observed=time.time(),
                    metadata={"feature_index": feature_idx, "autocorrelation": autocorr},
                )
                patterns.append(pattern)

        return patterns

    def _discover_correlation_patterns(
        self, data: List[List[float]], stream_id: str
    ) -> List[Pattern]:
        """Discover correlation patterns between features."""
        patterns = []

        if len(data) < 10 or len(data[0]) < 2:
            return patterns

        # Calculate correlation matrix
        correlation_matrix = self._calculate_correlation_matrix(data)

        # Find strong correlations
        for i in range(len(correlation_matrix)):
            for j in range(i + 1, len(correlation_matrix)):
                corr = correlation_matrix[i][j]
                if abs(corr) > 0.7:  # Strong correlation
                    pattern_type = "positive_correlation" if corr > 0 else "negative_correlation"

                    pattern = Pattern(
                        pattern_id=f"corr_{int(time.time())}_{stream_id}_{i}_{j}",
                        pattern_type="correlation",
                        description=f"{pattern_type} between feature {i} and feature {j}",
                        strength=abs(corr),
                        frequency=len(data),
                        confidence=0.75,
                        predictive_power=0.0,
                        last_observed=time.time(),
                        metadata={"feature_1": i, "feature_2": j, "correlation": corr},
                    )
                    patterns.append(pattern)

        return patterns

    def _discover_behavioral_patterns(self, data: List[Any], stream_id: str) -> List[Pattern]:
        """Discover behavioral patterns in data."""
        patterns = []

        # Simple behavioral pattern detection
        # Look for repeated sequences or state transitions
        if len(data) < 5:
            return patterns

        # Find repeated subsequences
        subsequences = defaultdict(int)
        for i in range(len(data) - 2):
            subsequence = tuple(str(dp) for dp in data[i : i + 3])  # 3-element subsequences
            subsequences[subsequence] += 1

        # Find frequently occurring subsequences
        for subsequence, count in subsequences.items():
            if count >= 3:  # Occurs at least 3 times
                pattern = Pattern(
                    pattern_id=f"behav_{int(time.time())}_{stream_id}",
                    pattern_type="behavioral",
                    description=f"Repeated subsequence pattern (frequency: {count})",
                    strength=count / len(data),
                    frequency=count,
                    confidence=0.6,
                    predictive_power=0.0,
                    last_observed=time.time(),
                    metadata={"subsequence": str(subsequence), "frequency": count},
                )
                patterns.append(pattern)

        return patterns

    def _discover_causal_patterns(self, data: List[List[float]], stream_id: str) -> List[Pattern]:
        """Discover causal patterns using simplified causal inference."""
        patterns = []

        if len(data) < 20 or len(data[0]) < 2:
            return patterns

        # Use Granger causality test (simplified)
        for i in range(len(data[0])):
            for j in range(len(data[0])):
                if i == j:
                    continue

                # Extract time series
                series_i = [dp[i] for dp in data]
                series_j = [dp[j] for dp in data]

                # Simple Granger causality test
                causality_strength = self._test_granger_causality(series_i, series_j)

                if causality_strength > 0.6:  # Strong causality
                    pattern = Pattern(
                        pattern_id=f"causal_{int(time.time())}_{stream_id}_{i}_{j}",
                        pattern_type="causal",
                        description=f"Potential causal relationship from feature {i} to feature {j}",
                        strength=causality_strength,
                        frequency=len(data),
                        confidence=0.7,
                        predictive_power=0.0,
                        last_observed=time.time(),
                        metadata={
                            "cause": i,
                            "effect": j,
                            "causality_strength": causality_strength,
                        },
                    )
                    patterns.append(pattern)

        return patterns

    def _discover_predictive_patterns(
        self, data: List[List[float]], stream_id: str
    ) -> List[Pattern]:
        """Discover predictive patterns with known predictive power."""
        patterns = []

        if len(data) < 20:
            return patterns

        # Test each feature for predictive power
        for i in range(len(data[0])):
            # Test if current value predicts next value
            current_values = [dp[i] for dp in data[:-1]]
            next_values = [dp[i] for dp in data[1:]]

            # Calculate prediction accuracy
            prediction_accuracy = self._calculate_prediction_accuracy(current_values, next_values)

            if prediction_accuracy > 0.7:  # Good predictive power
                pattern = Pattern(
                    pattern_id=f"pred_{int(time.time())}_{stream_id}_{i}",
                    pattern_type="predictive",
                    description=f"Feature {i} has predictive power",
                    strength=prediction_accuracy,
                    frequency=len(data) - 1,
                    confidence=prediction_accuracy,
                    predictive_power=prediction_accuracy,
                    last_observed=time.time(),
                    metadata={"feature": i, "prediction_accuracy": prediction_accuracy},
                )
                patterns.append(pattern)

        return patterns

    def _calculate_autocorrelation(self, series: List[float]) -> float:
        """Calculate autocorrelation of a time series."""
        if len(series) < 2:
            return 0.0

        mean = np.mean(series)
        variance = np.var(series)

        if variance == 0:
            return 0.0

        # Calculate autocorrelation at lag 1
        autocov = np.mean(
            [(series[i] - mean) * (series[i - 1] - mean) for i in range(1, len(series))]
        )
        autocorr = autocov / variance

        return autocorr

    def _calculate_correlation_matrix(self, data: List[List[float]]) -> List[List[float]]:
        """Calculate correlation matrix."""
        n_features = len(data[0])
        matrix = [[0.0] * n_features for _ in range(n_features)]

        for i in range(n_features):
            for j in range(n_features):
                if i == j:
                    matrix[i][j] = 1.0
                else:
                    series_i = [dp[i] for dp in data]
                    series_j = [dp[j] for dp in data]

                    correlation = (
                        np.corrcoef(series_i, series_j)[0, 1] if len(series_i) > 1 else 0.0
                    )
                    matrix[i][j] = correlation if not math.isnan(correlation) else 0.0

        return matrix

    def _test_granger_causality(self, cause: List[float], effect: List[float]) -> float:
        """Test Granger causality (simplified)."""
        if len(cause) < 10 or len(effect) < 10:
            return 0.0

        # Simple test: does past cause predict current effect better than past effect?
        # Use first half for training, second half for testing
        split = len(cause) // 2

        # Train on first half
        train_cause = cause[:split]
        train_effect = effect[:split]

        # Test on second half
        test_cause = cause[split:]
        test_effect = effect[split:]

        # Simple prediction error calculation
        # Predict effect using lagged effect (baseline)
        baseline_errors = [
            abs(test_effect[i] - test_effect[i - 1]) for i in range(1, len(test_effect))
        ]
        baseline_error = np.mean(baseline_errors) if baseline_errors else 0.0

        # Predict effect using lagged cause
        cause_based_errors = [
            abs(test_effect[i] - test_cause[i - 1]) for i in range(1, len(test_cause))
        ]
        cause_error = np.mean(cause_based_errors) if cause_based_errors else 0.0

        # Calculate improvement
        if baseline_error == 0:
            return 0.0

        improvement = (baseline_error - cause_error) / baseline_error
        return max(0.0, improvement)  # Granger causality strength

    def _calculate_prediction_accuracy(
        self, current_values: List[float], next_values: List[float]
    ) -> float:
        """Calculate prediction accuracy."""
        if len(current_values) != len(next_values):
            return 0.0

        # Simple prediction: next value equals current value
        predictions = current_values
        errors = [abs(predictions[i] - next_values[i]) for i in range(len(predictions))]

        # Normalize errors
        max_range = max(next_values) - min(next_values)
        if max_range == 0:
            return 0.0

        normalized_errors = [e / max_range for e in errors]
        avg_error = np.mean(normalized_errors)

        # Accuracy = 1 - error
        accuracy = max(0.0, 1.0 - avg_error)
        return accuracy

    def _calculate_predictive_power(self, pattern: Pattern, data: List[List[float]]) -> float:
        """Calculate predictive power of a pattern."""
        if pattern.pattern_type == "predictive":
            return pattern.predictive_power  # Already calculated

        # For other pattern types, estimate predictive power
        if pattern.pattern_type == "temporal":
            return pattern.strength * 0.6  # Temporal patterns have moderate predictive power
        elif pattern.pattern_type == "correlation":
            return pattern.strength * 0.7  # Correlations are more predictive
        elif pattern.pattern_type == "causal":
            return pattern.strength * 0.8  # Causal patterns are highly predictive
        else:
            return pattern.strength * 0.4  # Behavioral patterns have lower predictive power


class HypothesisGenerator:
    """Generate hypotheses for testing and validation."""

    def generate(
        self, knowledge: List[DiscoveredKnowledge], patterns: Dict[str, Pattern]
    ) -> List[Hypothesis]:
        """Generate hypotheses from current knowledge and patterns."""
        hypotheses = []

        # Generate hypotheses from pattern combinations
        pattern_list = list(patterns.values())
        if len(pattern_list) >= 2:
            combined_hypotheses = self._generate_combination_hypotheses(pattern_list)
            hypotheses.extend(combined_hypotheses)

        # Generate hypotheses from knowledge relationships
        knowledge_hypotheses = self._generate_knowledge_hypotheses(knowledge)
        hypotheses.extend(knowledge_hypotheses)

        # Prioritize hypotheses
        for hypothesis in hypotheses:
            hypothesis.priority = self._calculate_hypothesis_priority(hypothesis)

        # Sort by priority
        hypotheses.sort(key=lambda h: h.priority, reverse=True)

        return hypotheses

    def _generate_combination_hypotheses(self, patterns: List[Pattern]) -> List[Hypothesis]:
        """Generate hypotheses from pattern combinations."""
        hypotheses = []

        # Combine patterns to generate hypotheses
        for i, pattern1 in enumerate(patterns):
            for pattern2 in patterns[i + 1 :]:
                # Generate hypothesis about relationship between patterns
                if pattern1.pattern_type == "correlation" and pattern2.pattern_type == "temporal":
                    hypothesis = Hypothesis(
                        hypothesis_id=f"hyp_{int(time.time())}_{hash(str(pattern1) + str(pattern2)) % 10000}",
                        statement=f"Correlation pattern between {pattern1.description} may be related to temporal pattern {pattern2.description}",
                        supporting_evidence=[pattern1.pattern_id, pattern2.pattern_id],
                        contradictory_evidence=[],
                        confidence=0.5,
                        priority=0,
                        test_status="pending",
                        test_results={},
                        timestamp=time.time(),
                    )
                    hypotheses.append(hypothesis)

        return hypotheses

    def _generate_knowledge_hypotheses(
        self, knowledge: List[DiscoveredKnowledge]
    ) -> List[Hypothesis]:
        """Generate hypotheses from knowledge relationships."""
        hypotheses = []

        # Find contradictory knowledge
        for i, k1 in enumerate(knowledge):
            for k2 in knowledge[i + 1 :]:
                if self._are_contradictory(k1, k2):
                    hypothesis = Hypothesis(
                        hypothesis_id=f"hyp_contradict_{int(time.time())}_{hash(str(k1) + str(k2)) % 10000}",
                        statement=f"Contradictory knowledge detected: '{k1.content[:50]}...' vs '{k2.content[:50]}...'",
                        supporting_evidence=[],
                        contradictory_evidence=[k1.discovery_id, k2.discovery_id],
                        confidence=0.7,
                        priority=0,
                        test_status="pending",
                        test_results={},
                        timestamp=time.time(),
                    )
                    hypotheses.append(hypothesis)

        return hypotheses

    def _are_contradictory(self, k1: DiscoveredKnowledge, k2: DiscoveredKnowledge) -> bool:
        """Check if two knowledge items are contradictory."""
        # Simple contradiction detection
        words1 = set(k1.content.lower().split())
        words2 = set(k2.content.lower().split())

        contradiction_words = {
            "not",
            "never",
            "cannot",
            "false",
            "incorrect",
            "opposite",
            "reverse",
        }

        has_contradiction_1 = any(word in words1 for word in contradiction_words)
        has_contradiction_2 = any(word in words2 for word in contradiction_words)

        if has_contradiction_1 and has_contradiction_2:
            # Check for content similarity despite contradictions
            similarity = len(words1 & words2) / len(words1 | words2) if (words1 | words2) else 0
            if similarity > 0.5:  # High similarity with contradictions
                return True

        return False

    def _calculate_hypothesis_priority(self, hypothesis: Hypothesis) -> int:
        """Calculate priority for hypothesis testing."""
        priority = 0

        # Priority based on confidence
        priority += int(hypothesis.confidence * 10)

        # Priority based on supporting evidence
        priority += len(hypothesis.supporting_evidence)

        # Priority based on contradictory evidence (higher priority to resolve)
        priority += len(hypothesis.contradictory_evidence) * 2

        return priority


class KnowledgeValidator:
    """Validate and refine discovered knowledge."""

    def validate_knowledge(
        self, knowledge: DiscoveredKnowledge, validation_data: Dict[str, Any]
    ) -> float:
        """Validate knowledge against validation data."""
        # Simple validation logic
        confidence = knowledge.confidence_score

        # Adjust confidence based on validation data
        if validation_data.get("supporting_evidence", 0) > 0:
            confidence += 0.1

        if validation_data.get("contradictory_evidence", 0) > 0:
            confidence -= 0.2

        return max(0.0, min(1.0, confidence))

    def refine_knowledge(
        self, knowledge: DiscoveredKnowledge, data_streams: Dict[str, deque]
    ) -> Optional[str]:
        """Refine knowledge based on new data."""
        # Check if knowledge can be refined
        if knowledge.validation_status != "validated":
            return None

        # Simple refinement: add more detail
        refined_content = f"{knowledge.content} (Refined based on recent data)"

        return refined_content


class AdaptiveLearner:
    """Adaptive learning from feedback and experience."""

    def learn_from_feedback(self, feedback_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Learn from feedback history."""
        if not feedback_history:
            return {}

        # Analyze feedback patterns
        successful_feedback = [fb for fb in feedback_history if fb.get("score", 0.0) > 0.7]
        failed_feedback = [fb for fb in feedback_history if fb.get("score", 0.0) < 0.3]

        learning_insights = {
            "success_rate": len(successful_feedback) / len(feedback_history),
            "common_success_factors": self._extract_common_factors(successful_feedback),
            "common_failure_factors": self._extract_common_factors(failed_feedback),
        }

        return learning_insights

    def _extract_common_factors(self, feedback_items: List[Dict]) -> List[str]:
        """Extract common factors from feedback items."""
        if not feedback_items:
            return []

        # Simple factor extraction
        factors = []
        for fb in feedback_items:
            factors.extend(fb.get("factors", []))

        # Find most common factors
        factor_counts = defaultdict(int)
        for factor in factors:
            factor_counts[factor] += 1

        common_factors = sorted(factor_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        return [factor for factor, count in common_factors]


class CrossDomainLearner:
    """Cross-domain knowledge transfer and discovery."""

    def discover_patterns(
        self, data_streams: Dict[str, deque], existing_patterns: Dict[str, Pattern]
    ) -> List[Pattern]:
        """Discover cross-domain patterns."""
        cross_domain_patterns = []

        # Look for similar patterns across different streams
        stream_ids = list(data_streams.keys())

        for i, stream_id1 in enumerate(stream_ids):
            for stream_id2 in stream_ids[i + 1 :]:
                # Check for similar patterns between streams
                similar_patterns = self._find_cross_stream_patterns(
                    data_streams[stream_id1], data_streams[stream_id2]
                )
                cross_domain_patterns.extend(similar_patterns)

        return cross_domain_patterns

    def _find_cross_stream_patterns(self, stream1: deque, stream2: deque) -> List[Pattern]:
        """Find similar patterns between two data streams."""
        patterns = []

        # Extract data from both streams
        data1 = [dp["data"] for dp in list(stream1)]
        data2 = [dp["data"] for dp in list(stream2)]

        if len(data1) < 10 or len(data2) < 10:
            return patterns

        # Simple cross-stream pattern detection
        # Check if both streams have similar temporal patterns
        numerical_data1 = self._extract_numerical(data1)
        numerical_data2 = self._extract_numerical(data2)

        if not numerical_data1 or not numerical_data2:
            return patterns

        # Compare autocorrelations
        autocorr1 = self._calculate_autocorrelation(numerical_data1)
        autocorr2 = self._calculate_autocorrelation(numerical_data2)

        if abs(autocorr1 - autocorr2) < 0.1:  # Similar autocorrelation
            pattern = Pattern(
                pattern_id=f"cross_{int(time.time())}",
                pattern_type="cross_domain",
                description="Similar temporal pattern detected across data streams",
                strength=1.0 - abs(autocorr1 - autocorr2),
                frequency=min(len(data1), len(data2)),
                confidence=0.6,
                predictive_power=0.5,
                last_observed=time.time(),
                metadata={"autocorr1": autocorr1, "autocorr2": autocorr2},
            )
            patterns.append(pattern)

        return patterns

    def _extract_numerical(self, data: List[Any]) -> Optional[List[float]]:
        """Extract numerical data from mixed data types."""
        numerical = []
        for dp in data:
            if isinstance(dp, (int, float)):
                numerical.append(float(dp))
        return numerical if numerical else None

    def _calculate_autocorrelation(self, data: List[float]) -> float:
        """Calculate autocorrelation."""
        if len(data) < 2:
            return 0.0

        mean = np.mean(data)
        variance = np.var(data)

        if variance == 0:
            return 0.0

        autocov = np.mean([(data[i] - mean) * (data[i - 1] - mean) for i in range(1, len(data))])
        return autocov / variance


# Singleton instance
_autonomous_knowledge_discovery: Optional[AutonomousKnowledgeDiscovery] = None
_autonomous_knowledge_discovery_lock = threading.Lock()


def get_autonomous_knowledge_discovery(
    discovery_interval: float = 300.0,
) -> AutonomousKnowledgeDiscovery:
    """Get the singleton autonomous knowledge discovery instance."""
    global _autonomous_knowledge_discovery
    if _autonomous_knowledge_discovery is None:
        with _autonomous_knowledge_discovery_lock:
            if _autonomous_knowledge_discovery is None:
                _autonomous_knowledge_discovery = AutonomousKnowledgeDiscovery(discovery_interval)
    return _autonomous_knowledge_discovery


__all__ = [
    "AutonomousKnowledgeDiscovery",
    "get_autonomous_knowledge_discovery",
    "DiscoveryMode",
    "ConfidenceLevel",
    "DiscoveredKnowledge",
    "Hypothesis",
    "Pattern",
    "KnowledgeEvolution",
]
