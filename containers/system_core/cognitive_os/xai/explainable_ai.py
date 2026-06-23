"""Explainable AI (XAI) - Decision Transparency and Interpretability.

This module provides explainable AI capabilities to make decisions transparent,
interpretable, and trustworthy, enabling humans to understand AI decision-making.
"""

from __future__ import annotations

import logging
import threading
import time
from collections import defaultdict, deque
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

import numpy as np

logger = logging.getLogger(__name__)


class ExplanationType(str, Enum):
    """Types of explanations."""

    FEATURE_IMPORTANCE = "FEATURE_IMPORTANCE"
    COUNTERFACTUAL = "COUNTERFACTUAL"
    DECISION_TREE = "DECISION_TREE"
    ATTENTION_MECHANISM = "ATTENTION_MECHANISM"
    EXAMPLE_BASED = "EXAMPLE_BASED"
    RULE_BASED = "RULE_BASED"
    GRADIENT_BASED = "GRADIENT_BASED"


class ExplanationDetail(str, Enum):
    """Detail level of explanations."""

    SIMPLE = "SIMPLE"
    DETAILED = "DETAILED"
    TECHNICAL = "TECHNICAL"
    COMPREHENSIVE = "COMPREHENSIVE"


@dataclass
class FeatureImportance:
    """Feature importance in decision."""

    feature_name: str
    importance_score: float
    direction: str  # "positive" or "negative"
    explanation: str
    value: Optional[float] = None


@dataclass
class DecisionExplanation:
    """Explanation for a decision."""

    explanation_id: str
    decision_id: str
    explanation_type: ExplanationType
    detail_level: ExplanationDetail
    primary_reason: str
    feature_importances: List[FeatureImportance]
    confidence: float
    rationale: str
    alternative_decisions: List[Dict[str, Any]]
    supporting_evidence: List[str]
    potential_concerns: List[str]
    timestamp: float


@dataclass
class CounterfactualExplanation:
    """Counterfactual explanation."""

    explanation_id: str
    original_decision: str
    counterfactual_decision: str
    required_changes: List[Dict[str, Any]]
    feasibility_score: float
    distance: float
    timestamp: float


@dataclass
class AttentionVisualization:
    """Attention mechanism visualization."""

    attention_id: str
    attention_weights: Dict[str, float]
    highlighted_features: List[str]
    context: Dict[str, Any]
    timestamp: float


class ExplainableAI:
    """Explainable AI system for decision transparency."""

    def __init__(self):
        self._lock = threading.Lock()
        self._explanation_history: deque = deque(maxlen=1000)
        self._feature_importance_cache = defaultdict(list)
        self._decision_patterns = defaultdict(list)
        self._feature_explainer = FeatureExplainer()
        self._counterfactual_generator = CounterfactualGenerator()
        self._rule_extractor = RuleExtractor()
        self._attention_analyzer = AttentionAnalyzer()
        self._explanation_formatter = ExplanationFormatter()
        self._initialized = False

    def start(self) -> bool:
        """Start explainable AI system."""
        logger.info("[XAI] Starting explainable AI system...")
        self._initialized = True
        logger.info("[XAI] Explainable AI system started")
        return True

    def stop(self) -> bool:
        """Stop explainable AI system."""
        logger.info("[XAI] Stopping explainable AI system...")
        self._initialized = False
        logger.info("[XAI] Explainable AI system stopped")
        return True

    def explain_decision(
        self,
        decision: Dict[str, Any],
        context: Dict[str, Any],
        explanation_type: ExplanationType = ExplanationType.FEATURE_IMPORTANCE,
        detail_level: ExplanationDetail = ExplanationDetail.DETAILED,
    ) -> DecisionExplanation:
        """Generate explanation for a decision."""
        logger.info(f"[XAI] Generating {explanation_type} explanation for decision")

        explanation_id = f"exp_{int(time.time())}_{hash(str(decision)) % 10000}"

        # Generate feature importances
        feature_importances = self._feature_explainer.explain_features(decision, context)

        # Generate primary reason
        primary_reason = self._generate_primary_reason(decision, feature_importances)

        # Generate rationale
        rationale = self._explanation_formatter.format_rationale(
            decision, feature_importances, detail_level
        )

        # Generate alternative decisions
        alternative_decisions = self._generate_alternative_decisions(decision, context)

        # Generate supporting evidence
        supporting_evidence = self._generate_supporting_evidence(decision, context)

        # Generate potential concerns
        potential_concerns = self._generate_potential_concerns(decision, context)

        explanation = DecisionExplanation(
            explanation_id=explanation_id,
            decision_id=decision.get("decision_id", "unknown"),
            explanation_type=explanation_type,
            detail_level=detail_level,
            primary_reason=primary_reason,
            feature_importances=feature_importances,
            confidence=decision.get("confidence", 0.0),
            rationale=rationale,
            alternative_decisions=alternative_decisions,
            supporting_evidence=supporting_evidence,
            potential_concerns=potential_concerns,
            timestamp=time.time(),
        )

        # Store explanation
        with self._lock:
            self._explanation_history.append(explanation)
            self._decision_patterns[decision.get("decision_type", "unknown")].append(explanation)

        return explanation

    def generate_counterfactual(
        self, decision: Dict[str, Any], context: Dict[str, Any], target_outcome: str
    ) -> CounterfactualExplanation:
        """Generate counterfactual explanation."""
        logger.info(
            f"[XAI] Generating counterfactual explanation for target outcome: {target_outcome}"
        )

        counterfactual = self._counterfactual_generator.generate(decision, context, target_outcome)

        return counterfactual

    def extract_decision_rules(self, decisions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract decision rules from historical decisions."""
        logger.info(f"[XAI] Extracting rules from {len(decisions)} decisions")

        rules = self._rule_extractor.extract_rules(decisions)

        return rules

    def analyze_attention(
        self, decision: Dict[str, Any], context: Dict[str, Any]
    ) -> AttentionVisualization:
        """Analyze attention weights for decision."""
        logger.info("[XAI] Analyzing attention for decision")

        attention = self._attention_analyzer.analyze(decision, context)

        return attention

    def get_explanation_history(
        self, decision_type: Optional[str] = None, limit: int = 10
    ) -> List[DecisionExplanation]:
        """Get explanation history."""
        with self._lock:
            if decision_type:
                explanations = self._decision_patterns.get(decision_type, [])
                return explanations[-limit:]
            else:
                return list(self._explanation_history)[-limit:]

    def get_statistics(self) -> Dict[str, Any]:
        """Get XAI statistics."""
        with self._lock:
            return {
                "total_explanations": len(self._explanation_history),
                "decision_types": list(self._decision_patterns.keys()),
                "explanations_by_type": {
                    dt: len(exps) for dt, exps in self._decision_patterns.items()
                },
                "average_explanation_confidence": (
                    np.mean([exp.confidence for exp in self._explanation_history])
                    if self._explanation_history
                    else 0.0
                ),
            }

    def _generate_primary_reason(
        self, decision: Dict[str, Any], feature_importances: List[FeatureImportance]
    ) -> str:
        """Generate primary reason for decision."""
        if not feature_importances:
            return "No clear primary reason identified."

        # Get most important features
        top_features = sorted(
            feature_importances, key=lambda x: abs(x.importance_score), reverse=True
        )[:3]

        reason_parts = []
        for feature in top_features:
            direction = "increased" if feature.direction == "positive" else "decreased"
            reason_parts.append(f"{feature.feature_name} {direction} decision confidence")

        primary_reason = f"Decision was primarily driven by: " + ", ".join(reason_parts)
        return primary_reason

    def _generate_alternative_decisions(
        self, decision: Dict[str, Any], context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate alternative decisions."""
        alternatives = []

        decision_type = decision.get("decision_type", "trading")

        if decision_type == "trading":
            alternatives = [
                {"decision_type": "hold", "reason": "Wait for more favorable conditions"},
                {
                    "decision_type": "reverse_position",
                    "reason": "Contrarian approach based on market signals",
                },
            ]

        return alternatives

    def _generate_supporting_evidence(
        self, decision: Dict[str, Any], context: Dict[str, Any]
    ) -> List[str]:
        """Generate supporting evidence."""
        evidence = []

        if context.get("market_trend", 0) > 0.02:
            evidence.append("Strong upward market trend supports bullish decisions")
        elif context.get("market_trend", 0) < -0.02:
            evidence.append("Strong downward market trend supports bearish decisions")

        if context.get("volatility", 0) < 0.2:
            evidence.append("Low volatility environment suggests stable conditions")

        if decision.get("confidence", 0) > 0.8:
            evidence.append("High confidence in predictive models")

        return evidence

    def _generate_potential_concerns(
        self, decision: Dict[str, Any], context: Dict[str, Any]
    ) -> List[str]:
        """Generate potential concerns."""
        concerns = []

        if context.get("volatility", 0) > 0.5:
            concerns.append("High volatility may lead to unexpected outcomes")

        if decision.get("confidence", 0) < 0.3:
            concerns.append("Low confidence in decision prediction")

        if context.get("liquidity", 1.0) < 0.5:
            concerns.append("Low liquidity may impact execution")

        return concerns


class FeatureExplainer:
    """Explain feature importance in decisions."""

    def explain_features(
        self, decision: Dict[str, Any], context: Dict[str, Any]
    ) -> List[FeatureImportance]:
        """Explain feature importance for decision."""
        importances = []

        # Extract relevant features
        features = self._extract_features(decision, context)

        # Calculate importance scores
        for feature_name, value in features.items():
            importance = self._calculate_importance(feature_name, value, decision, context)
            direction = "positive" if importance > 0 else "negative"

            explanation = self._generate_feature_explanation(feature_name, importance, direction)

            feature_importance = FeatureImportance(
                feature_name=feature_name,
                importance_score=abs(importance),
                direction=direction,
                explanation=explanation,
                value=value if isinstance(value, (int, float)) else None,
            )

            importances.append(feature_importance)

        # Sort by importance
        importances.sort(key=lambda x: x.importance_score, reverse=True)

        return importances

    def _extract_features(
        self, decision: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Extract features from decision and context."""
        features = {}

        # Add context features
        for key, value in context.items():
            if isinstance(value, (int, float)):
                features[f"ctx_{key}"] = value

        # Add decision features
        for key, value in decision.items():
            if isinstance(value, (int, float)) and key not in ["confidence"]:
                features[f"dec_{key}"] = value

        return features

    def _calculate_importance(
        self, feature_name: str, value: float, decision: Dict[str, Any], context: Dict[str, Any]
    ) -> float:
        """Calculate importance score for feature."""
        # Simplified importance calculation
        # In real implementation, would use more sophisticated methods

        base_importance = abs(value) / max(1.0, abs(value))  # Normalize

        # Adjust based on feature type
        if "volatility" in feature_name.lower():
            importance = base_importance * 1.5  # Volatility is important
        elif "trend" in feature_name.lower():
            importance = base_importance * 1.2  # Trend is important
        else:
            importance = base_importance

        return importance

    def _generate_feature_explanation(
        self, feature_name: str, importance: float, direction: str
    ) -> str:
        """Generate explanation for feature importance."""
        direction_text = "increased" if direction == "positive" else "decreased"

        explanations = {
            "ctx_volatility": f"Market volatility {direction_text} risk and uncertainty",
            "ctx_trend": f"Market trend {direction_text} directional bias",
            "ctx_liquidity": f"Market liquidity {direction_text} execution efficiency",
            "dec_risk": f"Risk parameter {direction_text} conservative approach",
        }

        return explanations.get(
            feature_name, f"Feature {feature_name} {direction_text} decision {direction_text}"
        )


class CounterfactualGenerator:
    """Generate counterfactual explanations."""

    def generate(
        self, decision: Dict[str, Any], context: Dict[str, Any], target_outcome: str
    ) -> CounterfactualExplanation:
        """Generate counterfactual explanation."""
        explanation_id = f"cf_{int(time.time())}_{hash(str(decision)) % 10000}"

        original_decision = decision.get("decision_type", "unknown")

        # Generate required changes
        required_changes = self._generate_required_changes(decision, context, target_outcome)

        # Calculate feasibility and distance
        feasibility_score = self._calculate_feasibility(required_changes, context)
        distance = self._calculate_distance(required_changes)

        counterfactual = CounterfactualExplanation(
            explanation_id=explanation_id,
            original_decision=original_decision,
            counterfactual_decision=target_outcome,
            required_changes=required_changes,
            feasibility_score=feasibility_score,
            distance=distance,
            timestamp=time.time(),
        )

        return counterfactual

    def _generate_required_changes(
        self, decision: Dict[str, Any], context: Dict[str, Any], target_outcome: str
    ) -> List[Dict[str, Any]]:
        """Generate required changes for counterfactual."""
        changes = []

        # Simplified counterfactual generation
        if target_outcome == "hold" and decision.get("decision_type") != "hold":
            changes.append(
                {
                    "feature": "market_volatility",
                    "current_value": context.get("volatility", 0.2),
                    "required_value": 0.5,
                    "change_type": "increase",
                }
            )

        return changes

    def _calculate_feasibility(self, required_changes: List[Dict], context: Dict) -> float:
        """Calculate feasibility of required changes."""
        if not required_changes:
            return 1.0

        # Simple feasibility calculation
        feasible_count = 0
        for change in required_changes:
            # Assume changes are moderately feasible
            feasible_count += 1

        return feasible_count / len(required_changes)

    def _calculate_distance(self, required_changes: List[Dict]) -> float:
        """Calculate distance of counterfactual from original."""
        if not required_changes:
            return 0.0

        # Simple distance calculation
        distance = sum(1.0 for change in required_changes)
        return distance


class RuleExtractor:
    """Extract decision rules from historical decisions."""

    def extract_rules(self, decisions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract decision rules."""
        rules = []

        # Group by decision type
        decision_groups = defaultdict(list)
        for decision in decisions:
            decision_type = decision.get("decision_type", "unknown")
            decision_groups[decision_type].append(decision)

        # Extract rules for each decision type
        for decision_type, group_decisions in decision_groups.items():
            rule = self._extract_rule_for_type(decision_type, group_decisions)
            if rule:
                rules.append(rule)

        return rules

    def _extract_rule_for_type(self, decision_type: str, decisions: List[Dict]) -> Optional[Dict]:
        """Extract rule for specific decision type."""
        if len(decisions) < 5:
            return None

        # Extract common features
        common_features = self._find_common_features(decisions)

        rule = {
            "rule_id": f"rule_{decision_type}",
            "decision_type": decision_type,
            "conditions": common_features,
            "confidence": 0.7,  # Simplified confidence
            "support": len(decisions),
        }

        return rule

    def _find_common_features(self, decisions: List[Dict]) -> List[Dict]:
        """Find common features across decisions."""
        # Simplified common feature detection
        conditions = []

        # Extract from context if available
        if decisions and "context" in decisions[0]:
            context = decisions[0]["context"]
            for key, value in context.items():
                if isinstance(value, (int, float)):
                    conditions.append({"feature": key, "operator": ">", "value": value})

        return conditions


class AttentionAnalyzer:
    """Analyze attention weights for interpretability."""

    def analyze(self, decision: Dict[str, Any], context: Dict[str, Any]) -> AttentionVisualization:
        """Analyze attention for decision."""
        attention_id = f"att_{int(time.time())}"

        # Calculate attention weights (simplified)
        attention_weights = self._calculate_attention_weights(decision, context)

        # Highlight important features
        highlighted_features = self._highlight_important_features(attention_weights)

        attention = AttentionVisualization(
            attention_id=attention_id,
            attention_weights=attention_weights,
            highlighted_features=highlighted_features,
            context=context,
            timestamp=time.time(),
        )

        return attention

    def _calculate_attention_weights(self, decision: Dict, context: Dict) -> Dict[str, float]:
        """Calculate attention weights."""
        weights = {}

        # Simplified attention calculation
        features = len([k for k, v in context.items() if isinstance(v, (int, float))])
        if features > 0:
            weight = 1.0 / features
            for key in context.keys():
                weights[key] = weight

        return weights

    def _highlight_important_features(self, attention_weights: Dict[str, float]) -> List[str]:
        """Highlight important features based on attention."""
        sorted_features = sorted(attention_weights.items(), key=lambda x: x[1], reverse=True)
        top_features = [feature for feature, weight in sorted_features[:5]]
        return top_features


class ExplanationFormatter:
    """Format explanations for human readability."""

    def format_rationale(
        self,
        decision: Dict[str, Any],
        feature_importances: List[FeatureImportance],
        detail_level: ExplanationDetail,
    ) -> str:
        """Format rationale explanation."""
        if detail_level == ExplanationDetail.SIMPLE:
            return self._simple_rationale(feature_importances)
        elif detail_level == ExplanationDetail.DETAILED:
            return self._detailed_rationale(feature_importances)
        elif detail_level == ExplanationDetail.TECHNICAL:
            return self._technical_rationale(decision, feature_importances)
        else:
            return self._comprehensive_rationale(decision, feature_importances)

    def _simple_rationale(self, feature_importances: List[FeatureImportance]) -> str:
        """Generate simple rationale."""
        if not feature_importances:
            return "Decision based on available market conditions."

        top_feature = feature_importances[0]
        return f"Decision primarily because {top_feature.feature_name} had a {top_feature.direction} effect."

    def _detailed_rationale(self, feature_importances: List[FeatureImportance]) -> str:
        """Generate detailed rationale."""
        if not feature_importances:
            return "Decision based on analysis of multiple market factors."

        top_features = feature_importances[:3]
        reasons = []
        for feature in top_features:
            reasons.append(
                f"{feature.feature_name} {feature.direction} decision ({feature.importance_score:.2f} importance)"
            )

        return "Decision based on: " + ", ".join(reasons)

    def _technical_rationale(
        self, decision: Dict, feature_importances: List[FeatureImportance]
    ) -> str:
        """Generate technical rationale."""
        rationale_parts = [
            f"Decision Type: {decision.get('decision_type', 'unknown')}",
            f"Confidence: {decision.get('confidence', 0.0):.2f}",
            "Feature Analysis:",
        ]

        for feature in feature_importances[:5]:
            rationale_parts.append(
                f"  {feature.feature_name}: {feature.importance_score:.3f} ({feature.direction})"
            )

        return "\n".join(rationale_parts)

    def _comprehensive_rationale(
        self, decision: Dict, feature_importances: List[FeatureImportance]
    ) -> str:
        """Generate comprehensive rationale."""
        rationale = self._technical_rationale(decision, feature_importances)
        rationale += f"\n\nDecision made at: {time.time()}"
        rationale += f"\nDecision ID: {decision.get('decision_id', 'unknown')}"

        return rationale


# Singleton instance
_xai_system: Optional[ExplainableAI] = None
_xai_system_lock = threading.Lock()


def get_explainable_ai() -> ExplainableAI:
    """Get the singleton explainable AI instance."""
    global _xai_system
    if _xai_system is None:
        with _xai_system_lock:
            if _xai_system is None:
                _xai_system = ExplainableAI()
    return _xai_system


__all__ = [
    "ExplainableAI",
    "get_explainable_ai",
    "ExplanationType",
    "ExplanationDetail",
    "FeatureImportance",
    "DecisionExplanation",
    "CounterfactualExplanation",
    "AttentionVisualization",
]
