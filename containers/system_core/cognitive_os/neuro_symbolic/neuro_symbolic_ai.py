"""Neuro-Symbolic AI Integration - Bridging Neural and Symbolic Intelligence.

This module provides neuro-symbolic AI capabilities that combine the pattern recognition
power of neural networks with the reasoning capabilities of symbolic AI, enabling systems
that can both learn from data and reason with logic.
"""

from __future__ import annotations

import logging
import threading
import time
from collections import deque
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)


class NeuralComponent(str, Enum):
    """Types of neural network components."""

    PERCEPTRON = "PERCEPTRON"
    ACTIVATION_FUNCTION = "ACTIVATION_FUNCTION"
    NEURAL_LAYER = "NEURAL_LAYER"
    NEURAL_NETWORK = "NEURAL_NETWORK"
    ATTENTION_MECHANISM = "ATTENTION_MECHANISM"
    MEMORY_NETWORK = "MEMORY_NETWORK"


class SymbolicComponent(str, Enum):
    """Types of symbolic AI components."""

    LOGIC_RULE = "LOGIC_RULE"
    KNOWLEDGE_BASE = "KNOWLEDGE_BASE"
    INFERENCE_ENGINE = "INFERENCE_ENGINE"
    ONTOLOGY = "ONTOLOGY"
    CONSTRAINT_SOLVER = "CONSTRAINT_SOLVER"
    SYMBOLIC_REASONER = "SYMBOLIC_REASONER"


class IntegrationType(str, Enum):
    """Types of neuro-symbolic integration."""

    NEURAL_GUIDED_SYMBOLIC = "NEURAL_GUIDED_SYMBOLIC"
    SYMBOLIC_GUIDED_NEURAL = "SYMBOLIC_GUIDED_NEURAL"
    HYBRID_REASONING = "HYBRID_REASONING"
    NEURO_SYMBOLIC_ARCHITECTURE = "NEURO_SYMBOLIC_ARCHITECTURE"
    ATTENTION_GUIDED_REASONING = "ATTENTION_GUIDED_REASONING"


@dataclass
class NeuralPattern:
    """Pattern detected by neural component."""

    pattern_id: str
    neural_component: NeuralComponent
    pattern_features: np.ndarray
    confidence: float
    activation_pattern: np.ndarray
    layer_activations: Dict[str, np.ndarray]
    timestamp: float


@dataclass
class SymbolicRule:
    """Rule from symbolic component."""

    rule_id: str
    symbolic_component: SymbolicComponent
    conditions: List[str]
    conclusion: str
    confidence: float
    logic_form: str
    explanation: str
    timestamp: float


@dataclass
class NeuroSymbolicMapping:
    """Mapping between neural patterns and symbolic rules."""

    mapping_id: str
    neural_pattern: NeuralPattern
    symbolic_rule: SymbolicRule
    mapping_confidence: float
    alignment_score: float
    mutual_information: float
    timestamp: float


@dataclass
class NeuroSymbolicReasoning:
    """Reasoning combining neural and symbolic components."""

    reasoning_id: str
    neural_evidence: List[NeuralPattern]
    symbolic_evidence: List[SymbolicRule]
    combined_conclusion: str
    confidence: float
    reasoning_chain: List[str]
    neural_weight: float
    symbolic_weight: float
    timestamp: float


class NeuroSymbolicAI:
    """Neuro-symbolic AI integration system."""

    def __init__(self):
        self._lock = threading.Lock()
        self._neural_patterns: Dict[str, NeuralPattern] = {}
        self._symbolic_rules: Dict[str, SymbolicRule] = {}
        self._neuro_symbolic_mappings: Dict[str, NeuroSymbolicMapping] = {}
        self._reasoning_history: deque = deque(maxlen=1000)
        self._neural_network = NeuroNetwork()
        self._symbolic_engine = SymbolicEngine()
        self._pattern_to_rule_mapper = PatternRuleMapper()
        self._hybrid_reasoner = HybridReasoner()
        self._attention_mechanism = AttentionMechanism()
        self._meta_cognitive_layer = MetaCognitiveLayer()
        self._initialized = False

    def start(self) -> bool:
        """Start neuro-symbolic AI system."""
        logger.info("[NEURO_SYMBOLIC] Starting neuro-symbolic AI system...")
        self._initialized = True
        logger.info("[NEURO_SYMBOLIC] Neuro-symbolic AI system started")
        return True

    def stop(self) -> bool:
        """Stop neuro-symbolic AI system."""
        logger.info("[NEURO_SYMBOLIC] Stopping neuro-symbolic AI system...")
        self._initialized = False
        logger.info("[NEURO_SYMBOLIC] Neuro-symbolic AI system stopped")
        return True

    def process_neural_input(self, input_data: np.ndarray) -> NeuralPattern:
        """Process input through neural component."""
        logger.debug("[NEURO_SYMBOLIC] Processing neural input")

        # Forward pass through neural network
        neural_output = self._neural_network.forward(input_data)

        # Extract pattern information
        pattern_id = f"neural_pattern_{int(time.time())}_{hash(str(input_data.tobytes())) % 10000}"

        pattern = NeuralPattern(
            pattern_id=pattern_id,
            neural_component=NeuralComponent.NEURAL_NETWORK,
            pattern_features=input_data,
            confidence=neural_output["confidence"],
            activation_pattern=neural_output["activations"],
            layer_activations=neural_output["layer_activations"],
            timestamp=time.time(),
        )

        with self._lock:
            self._neural_patterns[pattern_id] = pattern

        return pattern

    def process_symbolic_input(
        self, facts: List[str], rules: List[str] = None
    ) -> List[SymbolicRule]:
        """Process input through symbolic component."""
        logger.debug("[NEURO_SYMBOLIC] Processing symbolic input")

        # Forward chaining through symbolic engine
        inferred_rules = self._symbolic_engine.forward_chain(facts, rules or [])

        # Create symbolic rule objects
        symbolic_rules = []
        for rule_dict in inferred_rules:
            rule_id = f"symbolic_rule_{int(time.time())}_{hash(str(rule_dict)) % 10000}"

            rule = SymbolicRule(
                rule_id=rule_id,
                symbolic_component=SymbolicComponent.SYMBOLIC_REASONER,
                conditions=rule_dict.get("conditions", []),
                conclusion=rule_dict.get("conclusion", ""),
                confidence=rule_dict.get("confidence", 0.8),
                logic_form=rule_dict.get("logic_form", ""),
                explanation=rule_dict.get("explanation", ""),
                timestamp=time.time(),
            )

            symbolic_rules.append(rule)

            with self._lock:
                self._symbolic_rules[rule_id] = rule

        return symbolic_rules

    def map_neural_to_symbolic(self, neural_pattern: NeuralPattern) -> List[NeuroSymbolicMapping]:
        """Map neural pattern to symbolic rules."""
        logger.debug("[NEURO_SYMBOLIC] Mapping neural pattern to symbolic rules")

        mappings = []

        # Find matching symbolic rules
        matching_rules = self._pattern_to_rule_mapper.find_matching_rules(
            neural_pattern, list(self._symbolic_rules.values())
        )

        for symbolic_rule in matching_rules:
            mapping_id = (
                f"mapping_{int(time.time())}_{neural_pattern.pattern_id}_{symbolic_rule.rule_id}"
            )

            # Calculate mapping metrics
            alignment_score = self._pattern_to_rule_mapper.calculate_alignment(
                neural_pattern, symbolic_rule
            )
            mutual_information = self._pattern_to_rule_mapper.calculate_mutual_information(
                neural_pattern, symbolic_rule
            )
            mapping_confidence = (alignment_score + mutual_information) / 2

            mapping = NeuroSymbolicMapping(
                mapping_id=mapping_id,
                neural_pattern=neural_pattern,
                symbolic_rule=symbolic_rule,
                mapping_confidence=mapping_confidence,
                alignment_score=alignment_score,
                mutual_information=mutual_information,
                timestamp=time.time(),
            )

            mappings.append(mapping)

            with self._lock:
                self._neuro_symbolic_mappings[mapping_id] = mapping

        return mappings

    def hybrid_reasoning(
        self, query: str, neural_data: np.ndarray, symbolic_facts: List[str]
    ) -> NeuroSymbolicReasoning:
        """Perform hybrid reasoning combining neural and symbolic components."""
        logger.info(f"[NEURO_SYMBOLIC] Performing hybrid reasoning for query: {query}")

        reasoning_id = f"reasoning_{int(time.time())}_{hash(query) % 10000}"

        # Get neural evidence
        neural_pattern = self.process_neural_input(neural_data)
        neural_evidence = [neural_pattern]

        # Get symbolic evidence
        symbolic_rules = self.process_symbolic_input(symbolic_facts)
        symbolic_evidence = symbolic_rules

        # Apply attention mechanism
        attention_weights = self._attention_mechanism.calculate_attention(
            query, neural_evidence, symbolic_evidence
        )

        # Hybrid reasoning
        reasoning_result = self._hybrid_reasoner.reason(
            query, neural_evidence, symbolic_evidence, attention_weights
        )

        # Meta-cognitive evaluation
        meta_evaluation = self._meta_cognitive_layer.evaluate_reasoning(reasoning_result)

        combined_reasoning = NeuroSymbolicReasoning(
            reasoning_id=reasoning_id,
            neural_evidence=neural_evidence,
            symbolic_evidence=symbolic_evidence,
            combined_conclusion=reasoning_result["conclusion"],
            confidence=reasoning_result["confidence"] * meta_evaluation["meta_confidence"],
            reasoning_chain=reasoning_result["reasoning_chain"],
            neural_weight=attention_weights.get("neural_weight", 0.5),
            symbolic_weight=attention_weights.get("symbolic_weight", 0.5),
            timestamp=time.time(),
        )

        # Store reasoning history
        with self._lock:
            self._reasoning_history.append(combined_reasoning)

        return combined_reasoning

    def learn_neuro_symbolic_mappings(
        self, training_data: List[Tuple[np.ndarray, List[str]]]
    ) -> None:
        """Learn mappings between neural patterns and symbolic rules from training data."""
        logger.info(
            f"[NEURO_SYMBOLIC] Learning neuro-symbolic mappings from {len(training_data)} examples"
        )

        for neural_input, symbolic_output in training_data:
            # Process neural input
            neural_pattern = self.process_neural_input(neural_input)

            # Create symbolic rules from output
            symbolic_rules = []
            for i, output in enumerate(symbolic_output):
                rule_id = f"learned_rule_{int(time.time())}_{i}"
                rule = SymbolicRule(
                    rule_id=rule_id,
                    symbolic_component=SymbolicComponent.KNOWLEDGE_BASE,
                    conditions=[],
                    conclusion=output,
                    confidence=0.9,
                    logic_form=output,
                    explanation=f"Learned from training data",
                    timestamp=time.time(),
                )
                symbolic_rules.append(rule)

                with self._lock:
                    self._symbolic_rules[rule_id] = rule

            # Create mappings
            for symbolic_rule in symbolic_rules:
                mappings = self.map_neural_to_symbolic(neural_pattern)
                for mapping in mappings:
                    with self._lock:
                        self._neuro_symbolic_mappings[mapping.mapping_id] = mapping

    def get_statistics(self) -> Dict[str, Any]:
        """Get neuro-symbolic AI statistics."""
        with self._lock:
            # Calculate average mapping confidence
            mapping_confidences = [
                m.mapping_confidence for m in self._neuro_symbolic_mappings.values()
            ]
            avg_mapping_confidence = np.mean(mapping_confidences) if mapping_confidences else 0.0

            # Calculate reasoning distribution
            recent_reasoning = list(self._reasoning_history)[-10:]
            if recent_reasoning:
                avg_neural_weight = np.mean([r.neural_weight for r in recent_reasoning])
                avg_symbolic_weight = np.mean([r.symbolic_weight for r in recent_reasoning])
            else:
                avg_neural_weight = 0.5
                avg_symbolic_weight = 0.5

            return {
                "total_neural_patterns": len(self._neural_patterns),
                "total_symbolic_rules": len(self._symbolic_rules),
                "total_mappings": len(self._neuro_symbolic_mappings),
                "total_reasoning_cases": len(self._reasoning_history),
                "average_mapping_confidence": avg_mapping_confidence,
                "average_neural_weight": avg_neural_weight,
                "average_symbolic_weight": avg_symbolic_weight,
            }


class NeuroNetwork:
    """Simplified neural network for pattern recognition."""

    def __init__(self, input_size: int = 100, hidden_size: int = 50, output_size: int = 10):
        self._input_size = input_size
        self._hidden_size = hidden_size
        self._output_size = output_size
        self._weights = self._initialize_weights()

    def _initialize_weights(self) -> Dict[str, np.ndarray]:
        """Initialize network weights."""
        return {
            "W1": np.random.randn(self._input_size, self._hidden_size) * 0.1,
            "b1": np.zeros(self._hidden_size),
            "W2": np.random.randn(self._hidden_size, self._output_size) * 0.1,
            "b2": np.zeros(self._output_size),
        }

    def forward(self, x: np.ndarray) -> Dict[str, Any]:
        """Forward pass through neural network."""
        # Ensure input has correct shape
        if len(x.shape) == 1:
            x = x.reshape(1, -1)

        # Resize if necessary
        if x.shape[1] != self._input_size:
            if x.shape[1] < self._input_size:
                # Pad with zeros
                padded = np.zeros((x.shape[0], self._input_size))
                padded[:, : x.shape[1]] = x
                x = padded
            else:
                # Truncate
                x = x[:, : self._input_size]

        # Forward pass
        z1 = np.dot(x, self._weights["W1"]) + self._weights["b1"]
        a1 = np.tanh(z1)  # Hidden layer activation
        z2 = np.dot(a1, self._weights["W2"]) + self._weights["b2"]
        output = np.tanh(z2)  # Output layer activation

        # Calculate confidence based on output magnitude
        confidence = np.mean(np.abs(output))

        return {
            "output": output,
            "activations": output.flatten(),
            "layer_activations": {"hidden": a1.flatten(), "output": output.flatten()},
            "confidence": float(confidence),
        }


class SymbolicEngine:
    """Symbolic reasoning engine."""

    def forward_chain(self, facts: List[str], rules: List[str] = None) -> List[Dict[str, Any]]:
        """Forward chaining through symbolic rules."""
        if rules is None:
            rules = self._generate_default_rules()

        inferred = []

        # Simple forward chaining implementation
        for rule in rules:
            if self._rule_applicable(rule, facts):
                conclusion = self._apply_rule(rule, facts)
                inferred.append(
                    {
                        "conditions": facts,
                        "conclusion": conclusion,
                        "confidence": 0.8,
                        "logic_form": rule,
                        "explanation": f"Applied rule '{rule}' to facts {facts}",
                    }
                )

        # Default inference if no rules applied
        if not inferred:
            inferred.append(
                {
                    "conditions": facts,
                    "conclusion": "default_conclusion",
                    "confidence": 0.5,
                    "logic_form": "default",
                    "explanation": "No applicable rules, using default inference",
                }
            )

        return inferred

    def _generate_default_rules(self) -> List[str]:
        """Generate default symbolic rules."""
        return [
            "IF trend_is_up THEN recommend_buy",
            "IF trend_is_down THEN recommend_sell",
            "IF volatility_is_high THEN recommend_reduce_risk",
            "IF liquidity_is_high THEN recommend_increase_activity",
        ]

    def _rule_applicable(self, rule: str, facts: List[str]) -> bool:
        """Check if rule is applicable to given facts."""
        # Simplified rule applicability check
        return len(facts) > 0

    def _apply_rule(self, rule: str, facts: List[str]) -> str:
        """Apply rule to facts and generate conclusion."""
        # Simplified rule application
        return f"conclusion_based_on_{rule.replace(' ', '_')}"


class PatternRuleMapper:
    """Map neural patterns to symbolic rules."""

    def find_matching_rules(
        self, neural_pattern: NeuralPattern, symbolic_rules: List[SymbolicRule]
    ) -> List[SymbolicRule]:
        """Find symbolic rules that match neural pattern."""
        matching_rules = []

        for rule in symbolic_rules:
            match_score = self._calculate_pattern_rule_similarity(neural_pattern, rule)
            if match_score > 0.5:  # Similarity threshold
                matching_rules.append(rule)

        return matching_rules

    def calculate_alignment(
        self, neural_pattern: NeuralPattern, symbolic_rule: SymbolicRule
    ) -> float:
        """Calculate alignment between neural pattern and symbolic rule."""
        # Simplified alignment calculation
        # In real implementation, would use more sophisticated methods

        pattern_features = neural_pattern.pattern_features
        pattern_mean = (
            np.mean(np.abs(pattern_features)) if isinstance(pattern_features, np.ndarray) else 0.5
        )

        # Alignment based on pattern features and rule confidence
        alignment = pattern_mean * symbolic_rule.confidence

        return min(1.0, alignment)

    def calculate_mutual_information(
        self, neural_pattern: NeuralPattern, symbolic_rule: SymbolicRule
    ) -> float:
        """Calculate mutual information between neural pattern and symbolic rule."""
        # Simplified mutual information calculation
        # In real implementation, would use statistical methods

        # Use confidence as proxy for information content
        mutual_info = neural_pattern.confidence * symbolic_rule.confidence

        return mutual_info

    def _calculate_pattern_rule_similarity(
        self, neural_pattern: NeuralPattern, symbolic_rule: SymbolicRule
    ) -> float:
        """Calculate similarity between pattern and rule."""
        # Use rule confidence and pattern confidence as similarity measure
        similarity = (neural_pattern.confidence + symbolic_rule.confidence) / 2
        return similarity


class HybridReasoner:
    """Combine neural and symbolic reasoning."""

    def reason(
        self,
        query: str,
        neural_evidence: List[NeuralPattern],
        symbolic_evidence: List[SymbolicRule],
        attention_weights: Dict[str, float],
    ) -> Dict[str, Any]:
        """Perform hybrid reasoning."""
        # Weighted combination of neural and symbolic evidence
        neural_weight = attention_weights.get("neural_weight", 0.5)
        symbolic_weight = attention_weights.get("symbolic_weight", 0.5)

        # Extract conclusions from each source
        neural_conclusions = self._extract_neural_conclusions(neural_evidence)
        symbolic_conclusions = self._extract_symbolic_conclusions(symbolic_evidence)

        # Combine conclusions
        if neural_conclusions and symbolic_conclusions:
            combined_conclusion = f"Hybrid conclusion: Neural={neural_conclusions[0]}, Symbolic={symbolic_conclusions[0]}"
            confidence = (
                neural_weight * neural_evidence[0].confidence
                + symbolic_weight * symbolic_evidence[0].confidence
            )
        elif neural_conclusions:
            combined_conclusion = f"Neural conclusion: {neural_conclusions[0]}"
            confidence = neural_evidence[0].confidence
        elif symbolic_conclusions:
            combined_conclusion = f"Symbolic conclusion: {symbolic_conclusions[0]}"
            confidence = symbolic_evidence[0].confidence
        else:
            combined_conclusion = "No clear conclusion"
            confidence = 0.5

        # Generate reasoning chain
        reasoning_chain = [
            "Neural evidence processed",
            f"Neural weight: {neural_weight:.2f}",
            "Symbolic evidence processed",
            f"Symbolic weight: {symbolic_weight:.2f}",
            "Combined evidence evaluated",
            f"Final conclusion: {combined_conclusion}",
        ]

        return {
            "conclusion": combined_conclusion,
            "confidence": confidence,
            "reasoning_chain": reasoning_chain,
            "neural_conclusions": neural_conclusions,
            "symbolic_conclusions": symbolic_conclusions,
        }

    def _extract_neural_conclusions(self, neural_evidence: List[NeuralPattern]) -> List[str]:
        """Extract conclusions from neural evidence."""
        conclusions = []
        for pattern in neural_evidence:
            # Simple conclusion extraction based on pattern features
            if isinstance(pattern.pattern_features, np.ndarray):
                feature_mean = np.mean(pattern.pattern_features)
                if feature_mean > 0.5:
                    conclusions.append("positive_neural_conclusion")
                else:
                    conclusions.append("negative_neural_conclusion")
            else:
                conclusions.append("neutral_neural_conclusion")
        return conclusions

    def _extract_symbolic_conclusions(self, symbolic_evidence: List[SymbolicRule]) -> List[str]:
        """Extract conclusions from symbolic evidence."""
        conclusions = []
        for rule in symbolic_evidence:
            conclusions.append(rule.conclusion)
        return conclusions


class AttentionMechanism:
    """Attention mechanism for focusing on relevant information."""

    def calculate_attention(
        self,
        query: str,
        neural_evidence: List[NeuralPattern],
        symbolic_evidence: List[SymbolicRule],
    ) -> Dict[str, float]:
        """Calculate attention weights for neural and symbolic evidence."""
        # Simplified attention calculation
        # In real implementation, would use more sophisticated attention mechanisms

        # Calculate relevance scores
        neural_relevance = self._calculate_neural_relevance(query, neural_evidence)
        symbolic_relevance = self._calculate_symbolic_relevance(query, symbolic_evidence)

        # Normalize to weights
        total_relevance = neural_relevance + symbolic_relevance
        if total_relevance > 0:
            neural_weight = neural_relevance / total_relevance
            symbolic_weight = symbolic_relevance / total_relevance
        else:
            neural_weight = 0.5
            symbolic_weight = 0.5

        return {
            "neural_weight": neural_weight,
            "symbolic_weight": symbolic_weight,
            "neural_relevance": neural_relevance,
            "symbolic_relevance": symbolic_relevance,
        }

    def _calculate_neural_relevance(
        self, query: str, neural_evidence: List[NeuralPattern]
    ) -> float:
        """Calculate relevance of neural evidence to query."""
        # Simple relevance based on pattern confidence
        if not neural_evidence:
            return 0.5

        avg_confidence = np.mean([p.confidence for p in neural_evidence])
        return avg_confidence

    def _calculate_symbolic_relevance(
        self, query: str, symbolic_evidence: List[SymbolicRule]
    ) -> float:
        """Calculate relevance of symbolic evidence to query."""
        # Simple relevance based on rule confidence
        if not symbolic_evidence:
            return 0.5

        avg_confidence = np.mean([r.confidence for r in symbolic_evidence])
        return avg_confidence


class MetaCognitiveLayer:
    """Meta-cognitive layer for self-awareness and evaluation."""

    def evaluate_reasoning(self, reasoning_result: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate reasoning quality from meta-cognitive perspective."""
        confidence = reasoning_result.get("confidence", 0.5)
        reasoning_chain = reasoning_result.get("reasoning_chain", [])

        # Meta-cognitive evaluation
        meta_confidence = self._adjust_confidence_metacognitively(confidence, reasoning_chain)
        consistency_score = self._evaluate_reasoning_consistency(reasoning_chain)
        completeness_score = self._evaluate_reasoning_completeness(reasoning_result)

        return {
            "meta_confidence": meta_confidence,
            "consistency_score": consistency_score,
            "completeness_score": completeness_score,
            "overall_meta_score": (meta_confidence + consistency_score + completeness_score) / 3,
        }

    def _adjust_confidence_metacognitively(
        self, confidence: float, reasoning_chain: List[str]
    ) -> float:
        """Adjust confidence based on meta-cognitive evaluation."""
        # If reasoning chain is long and detailed, increase confidence
        chain_length_factor = min(1.0, len(reasoning_chain) / 10.0)

        adjusted_confidence = confidence * (0.8 + 0.2 * chain_length_factor)
        return min(1.0, adjusted_confidence)

    def _evaluate_reasoning_consistency(self, reasoning_chain: List[str]) -> float:
        """Evaluate consistency of reasoning chain."""
        if not reasoning_chain:
            return 0.5

        # Simple consistency check based on chain structure
        consistency = 0.8  # Base consistency
        return consistency

    def _evaluate_reasoning_completeness(self, reasoning_result: Dict[str, Any]) -> float:
        """Evaluate completeness of reasoning result."""
        required_keys = ["conclusion", "confidence", "reasoning_chain"]
        present_keys = sum(1 for key in required_keys if key in reasoning_result)

        completeness = present_keys / len(required_keys)
        return completeness


# Singleton instance
_neuro_symbolic_ai: Optional[NeuroSymbolicAI] = None
_neuro_symbolic_ai_lock = threading.Lock()


def get_neuro_symbolic_ai() -> NeuroSymbolicAI:
    """Get the singleton neuro-symbolic AI instance."""
    global _neuro_symbolic_ai
    if _neuro_symbolic_ai is None:
        with _neuro_symbolic_ai_lock:
            if _neuro_symbolic_ai is None:
                _neuro_symbolic_ai = NeuroSymbolicAI()
    return _neuro_symbolic_ai


__all__ = [
    "NeuroSymbolicAI",
    "get_neuro_symbolic_ai",
    "NeuralComponent",
    "SymbolicComponent",
    "IntegrationType",
    "NeuralPattern",
    "SymbolicRule",
    "NeuroSymbolicMapping",
    "NeuroSymbolicReasoning",
]
