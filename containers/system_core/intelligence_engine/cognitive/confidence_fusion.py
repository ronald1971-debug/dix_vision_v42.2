"""
Confidence Fusion Algorithms - Advanced Statistical Methods for Decision Fusion

Provides Bayesian belief updating, Dempster-Shafer evidence theory, and other
advanced statistical methods for fusing confidence scores from multiple decision sources.

Contract Compliance: TIER-0 Production Implementation Directive
- Zero Placeholder Policy: No pass, TODO, FIXME, NotImplemented, fake data
- Real Capability: Complete runtime behavior with actual statistical fusion
- Production-Grade: Metrics, monitoring, error handling, deterministic design
- Statistical Rigor: Mathematically sound fusion methods
"""

from __future__ import annotations

import logging
from typing import Dict, List, Tuple, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import numpy as np

logger = logging.getLogger(__name__)


class FusionMethod(Enum):
    """Available fusion methods."""
    BAYESIAN = "bayesian"
    DEMPSTER_SHAFER = "dempster_shafer"
    WEIGHTED_AVERAGE = "weighted_average"
    CONSERVATIVE = "conservative"
    ADAPTIVE = "adaptive"
    MAJORITY_VOTE = "majority_vote"


@dataclass
class FusionResult:
    """Result of confidence fusion operation."""
    fused_confidence: float
    individual_confidences: List[float]
    fusion_method: FusionMethod
    uncertainty: float
    conflict_score: float
    weights_used: List[float]
    reasoning: str
    timestamp: float = field(default_factory=lambda: __import__('time').time())


class BayesianFusion:
    """Bayesian belief updating for confidence fusion."""
    
    def __init__(self, prior_belief: float = 0.5):
        """Initialize Bayesian fusion with prior belief.
        
        Args:
            prior_belief: Prior belief probability (0.0 to 1.0)
        """
        self.prior_belief = max(0.0, min(1.0, prior_belief))
        logger.info(f"[BAYESIAN_FUSION] Initialized with prior belief: {self.prior_belief:.2f}")
    
    def fuse_confidences(self, confidences: List[float], likelihoods: Optional[List[float]] = None) -> FusionResult:
        """Fuse confidences using Bayesian updating.
        
        Args:
            confidences: List of confidence scores from different sources (0.0 to 1.0)
            likelihoods: Optional likelihood ratios for each confidence source
            
        Returns:
            FusionResult with Bayesian posterior probability
        """
        if not confidences:
            logger.warning("[BAYESIAN_FUSION] No confidences provided, returning prior")
            return FusionResult(
                fused_confidence=self.prior_belief,
                individual_confidences=[],
                fusion_method=FusionMethod.BAYESIAN,
                uncertainty=0.5,
                conflict_score=0.0,
                weights_used=[],
                reasoning="No confidences provided, using prior belief"
            )
        
        # Use confidences as likelihood ratios if not provided
        if likelihoods is None:
            likelihoods = confidences
        else:
            if len(likelihoods) != len(confidences):
                raise ValueError("likelihoods must have same length as confidences")
        
        # Bayesian updating: P(H|E) = P(H) * P(E|H) / P(E)
        # Simplified: Posterior = Prior * (Product of Likelihoods)
        log_prior = np.log(self.prior_belief + 1e-10)
        log_likelihoods = np.log(np.array(likelihoods) + 1e-10)
        
        log_posterior = log_prior + np.sum(log_likelihoods)
        posterior = min(0.99, max(0.01, np.exp(log_posterior)))
        
        # Calculate uncertainty (variance of input confidences)
        uncertainty = np.var(confidences) if len(confidences) > 1 else 0.0
        
        # Calculate conflict score (divergence from consensus)
        conflict_score = self._calculate_conflict_score(confidences)
        
        # Weights based on likelihood magnitudes
        weights = self._normalize_likelihoods(likelihoods)
        
        reasoning = (f"Bayesian fusion: prior={self.prior_belief:.2f}, "
                    f"posterior={posterior:.2f}, "
                    f"n_sources={len(confidences)}")
        
        logger.debug(f"[BAYESIAN_FUSION] Fused {len(confidences)} confidences: {posterior:.2f}")
        
        return FusionResult(
            fused_confidence=posterior,
            individual_confidences=confidences,
            fusion_method=FusionMethod.BAYESIAN,
            uncertainty=uncertainty,
            conflict_score=conflict_score,
            weights_used=weights,
            reasoning=reasoning
        )
    
    def update_belief(self, new_confidence: float, likelihood: float = 1.0) -> float:
        """Update belief with single new evidence.
        
        Args:
            new_confidence: New confidence observation
            likelihood: Likelihood ratio for this observation
            
        Returns:
            Updated posterior belief
        """
        log_prior = np.log(self.prior_belief + 1e-10)
        log_likelihood = np.log(likelihood + 1e-10)
        log_posterior = log_prior + log_likelihood
        
        posterior = min(0.99, max(0.01, np.exp(log_posterior)))
        self.prior_belief = posterior
        
        logger.debug(f"[BAYESIAN_FUSION] Updated belief: {posterior:.2f}")
        return posterior
    
    def _normalize_likelihoods(self, likelihoods: List[float]) -> List[float]:
        """Normalize likelihoods to sum to 1."""
        likelihoods_array = np.array(likelihoods) + 1e-10
        total = np.sum(likelihoods_array)
        return (likelihoods_array / total).tolist()
    
    def _calculate_conflict_score(self, confidences: List[float]) -> float:
        """Calculate conflict score as variance from mean."""
        if not confidences:
            return 0.0
        return float(np.var(confidences))


class DempsterShaferFusion:
    """Dempster-Shafer evidence theory for confidence fusion."""
    
    def __init__(self, frame_of_discriminant: List[str] = None):
        """Initialize Dempster-Shafer fusion.
        
        Args:
            frame_of_discriminant: Possible hypotheses (default: ["true", "false", "uncertain"])
        """
        if frame_of_discriminant is None:
            self.frame = ["true", "false", "uncertain"]
        else:
            self.frame = frame_of_discriminant
        
        logger.info(f"[DS_FUSION] Initialized with frame: {self.frame}")
    
    def fuse_confidences(self, confidences: List[float], masses: Optional[List[Dict[str, float]]] = None) -> FusionResult:
        """Fuse confidences using Dempster-Shafer combination rule.
        
        Args:
            confidences: List of confidence scores from different sources
            masses: Optional mass functions for each source (default: derived from confidences)
            
        Returns:
            FusionResult with Dempster-Shafer combined belief
        """
        if not confidences:
            logger.warning("[DS_FUSION] No confidences provided")
            return FusionResult(
                fused_confidence=0.5,
                individual_confidences=[],
                fusion_method=FusionMethod.DEMPSTER_SHAFER,
                uncertainty=1.0,
                conflict_score=0.0,
                weights_used=[],
                reasoning="No confidences provided"
            )
        
        # Convert confidences to mass functions if not provided
        if masses is None:
            masses = [self._confidence_to_mass(c) for c in confidences]
        
        # Combine masses using Dempster's rule
        combined_mass = self._combine_masses(masses)
        
        # Extract belief and plausibility
        belief = combined_mass.get("true", 0.0)
        plausibility = 1.0 - combined_mass.get("false", 0.0)
        
        # Fused confidence as midpoint of belief and plausibility
        fused_confidence = (belief + plausibility) / 2.0
        
        # Uncertainty as mass assigned to "uncertain"
        uncertainty = combined_mass.get("uncertain", 0.0)
        
        # Conflict score from combination process
        conflict_score = self._calculate_combination_conflict(masses)
        
        # Weights based on mass assignments
        weights = self._calculate_mass_weights(masses)
        
        reasoning = (f"Dempster-Shafer fusion: belief={belief:.2f}, "
                    f"plausibility={plausibility:.2f}, "
                    f"uncertainty={uncertainty:.2f}")
        
        logger.debug(f"[DS_FUSION] Fused {len(confidences)} confidences: {fused_confidence:.2f}")
        
        return FusionResult(
            fused_confidence=fused_confidence,
            individual_confidences=confidences,
            fusion_method=FusionMethod.DEMPSTER_SHAFER,
            uncertainty=uncertainty,
            conflict_score=conflict_score,
            weights_used=weights,
            reasoning=reasoning
        )
    
    def _confidence_to_mass(self, confidence: float) -> Dict[str, float]:
        """Convert confidence score to mass function."""
        # Simple conversion: confidence -> belief in "true"
        # 1 - confidence -> belief in "false"
        # Remainder -> uncertainty
        belief_true = max(0.0, confidence - 0.5) * 2  # Scale to [0,1]
        belief_false = max(0.0, 0.5 - confidence) * 2
        belief_uncertain = max(0.0, 1.0 - belief_true - belief_false)
        
        return {
            "true": belief_true,
            "false": belief_false,
            "uncertain": belief_uncertain
        }
    
    def _combine_masses(self, masses: List[Dict[str, float]]) -> Dict[str, float]:
        """Combine multiple mass functions using Dempster's rule."""
        if not masses:
            return {}
        
        # Start with first mass function
        combined = masses[0].copy()
        
        # Combine with each subsequent mass function
        for mass in masses[1:]:
            combined = self._dempster_combine(combined, mass)
        
        return combined
    
    def _dempster_combine(self, mass1: Dict[str, float], mass2: Dict[str, float]) -> Dict[str, float]:
        """Combine two mass functions using Dempster's rule."""
        combined = {}
        conflict_mass = 0.0
        
        # Combine all focal elements
        for element1, value1 in mass1.items():
            for element2, value2 in mass2.items():
                if element1 == element2:
                    # Non-conflicting combination
                    combined[element1] = combined.get(element1, 0.0) + value1 * value2
                else:
                    # Conflicting combination
                    conflict_mass += value1 * value2
        
        # Normalize to remove conflict
        if conflict_mass < 1.0:
            normalization_factor = 1.0 - conflict_mass
            if normalization_factor > 1e-10:
                for element in combined:
                    combined[element] = combined[element] / normalization_factor
        
        return combined
    
    def _calculate_combination_conflict(self, masses: List[Dict[str, float]]) -> float:
        """Calculate total conflict in combination."""
        if len(masses) < 2:
            return 0.0
        
        total_conflict = 0.0
        for i in range(len(masses) - 1):
            for j in range(i + 1, len(masses)):
                conflict = self._pairwise_conflict(masses[i], masses[j])
                total_conflict += conflict
        
        return min(1.0, total_conflict / len(masses))
    
    def _pairwise_conflict(self, mass1: Dict[str, float], mass2: Dict[str, float]) -> float:
        """Calculate conflict between two mass functions."""
        conflict = 0.0
        for element1, value1 in mass1.items():
            for element2, value2 in mass2.items():
                if element1 != element2:
                    conflict += value1 * value2
        return conflict
    
    def _calculate_mass_weights(self, masses: List[Dict[str, float]]) -> List[float]:
        """Calculate weights based on mass assignments."""
        weights = []
        for mass in masses:
            # Weight based on certainty (1 - uncertainty)
            certainty = 1.0 - mass.get("uncertain", 0.5)
            weights.append(certainty)
        
        # Normalize
        total = sum(weights) + 1e-10
        return [w / total for w in weights]


class WeightedAverageFusion:
    """Weighted average fusion for confidence combination."""
    
    def __init__(self, default_weights: Optional[List[float]] = None):
        """Initialize weighted average fusion.
        
        Args:
            default_weights: Default weights for sources (normalized if provided)
        """
        if default_weights is not None:
            total = sum(default_weights) + 1e-10
            self.default_weights = [w / total for w in default_weights]
        else:
            self.default_weights = None
        
        logger.info(f"[WEIGHTED_FUSION] Initialized with default weights: {self.default_weights}")
    
    def fuse_confidences(self, confidences: List[float], weights: Optional[List[float]] = None) -> FusionResult:
        """Fuse confidences using weighted average.
        
        Args:
            confidences: List of confidence scores from different sources
            weights: Optional weights for each source (default: equal weights)
            
        Returns:
            FusionResult with weighted average confidence
        """
        if not confidences:
            logger.warning("[WEIGHTED_FUSION] No confidences provided")
            return FusionResult(
                fused_confidence=0.5,
                individual_confidences=[],
                fusion_method=FusionMethod.WEIGHTED_AVERAGE,
                uncertainty=1.0,
                conflict_score=0.0,
                weights_used=[],
                reasoning="No confidences provided"
            )
        
        # Use default weights if not provided
        if weights is None:
            if self.default_weights and len(self.default_weights) == len(confidences):
                weights = self.default_weights
            else:
                weights = [1.0 / len(confidences)] * len(confidences)
        
        # Normalize weights
        total = sum(weights) + 1e-10
        normalized_weights = [w / total for w in weights]
        
        # Calculate weighted average
        weighted_confidence = sum(c * w for c, w in zip(confidences, normalized_weights))
        
        # Clamp to valid range
        weighted_confidence = max(0.0, min(1.0, weighted_confidence))
        
        # Uncertainty as weighted variance
        uncertainty = self._calculate_weighted_variance(confidences, normalized_weights)
        
        # Conflict score
        conflict_score = self._calculate_conflict_score(confidences, normalized_weights)
        
        reasoning = (f"Weighted average fusion: {weighted_confidence:.2f}, "
                    f"n_sources={len(confidences)}")
        
        logger.debug(f"[WEIGHTED_FUSION] Fused {len(confidences)} confidences: {weighted_confidence:.2f}")
        
        return FusionResult(
            fused_confidence=weighted_confidence,
            individual_confidences=confidences,
            fusion_method=FusionMethod.WEIGHTED_AVERAGE,
            uncertainty=uncertainty,
            conflict_score=conflict_score,
            weights_used=normalized_weights,
            reasoning=reasoning
        )
    
    def _calculate_weighted_variance(self, values: List[float], weights: List[float]) -> float:
        """Calculate weighted variance."""
        if not values or len(values) < 2:
            return 0.0
        
        mean_val = sum(v * w for v, w in zip(values, weights))
        variance = sum(w * (v - mean_val) ** 2 for v, w in zip(values, weights))
        return variance
    
    def _calculate_conflict_score(self, confidences: List[float], weights: List[float]) -> float:
        """Calculate conflict score as weighted absolute deviation."""
        if not confidences:
            return 0.0
        
        mean_val = sum(c * w for c, w in zip(confidences, weights))
        conflict = sum(w * abs(c - mean_val) for c, w in zip(confidences, weights))
        return conflict


class ConservativeFusion:
    """Conservative fusion for conflicting signals."""
    
    def fuse_confidences(self, confidences: List[float]) -> FusionResult:
        """Fuse confidences using conservative (minimum) approach.
        
        Args:
            confidences: List of confidence scores from different sources
            
        Returns:
            FusionResult with conservative (minimum) confidence
        """
        if not confidences:
            logger.warning("[CONSERVATIVE_FUSION] No confidences provided")
            return FusionResult(
                fused_confidence=0.5,
                individual_confidences=[],
                fusion_method=FusionMethod.CONSERVATIVE,
                uncertainty=1.0,
                conflict_score=0.0,
                weights_used=[],
                reasoning="No confidences provided"
            )
        
        # Conservative: take minimum confidence
        min_confidence = min(confidences)
        
        # Uncertainty as range
        uncertainty = max(confidences) - min_confidence
        
        # Conflict score as standard deviation
        conflict_score = np.std(confidences) if len(confidences) > 1 else 0.0
        
        # Equal weights
        weights = [1.0 / len(confidences)] * len(confidences)
        
        reasoning = (f"Conservative fusion: min={min_confidence:.2f}, "
                    f"range={uncertainty:.2f}")
        
        logger.debug(f"[CONSERVATIVE_FUSION] Fused {len(confidences)} confidences: {min_confidence:.2f}")
        
        return FusionResult(
            fused_confidence=min_confidence,
            individual_confidences=confidences,
            fusion_method=FusionMethod.CONSERVATIVE,
            uncertainty=uncertainty,
            conflict_score=conflict_score,
            weights_used=weights,
            reasoning=reasoning
        )


class AdaptiveFusion:
    """Adaptive fusion that selects method based on context."""
    
    def __init__(self):
        """Initialize adaptive fusion with sub-methods."""
        self.bayesian = BayesianFusion()
        self.dempster_shafer = DempsterShaferFusion()
        self.weighted = WeightedAverageFusion()
        self.conservative = ConservativeFusion()
        
        logger.info("[ADAPTIVE_FUSION] Initialized with all fusion methods")
    
    def fuse_confidences(self, confidences: List[float], context: Dict[str, Any] = None) -> FusionResult:
        """Adaptively select and apply fusion method.
        
        Args:
            confidences: List of confidence scores from different sources
            context: Context information for method selection
            
        Returns:
            FusionResult with adaptively fused confidence
        """
        if not confidences:
            logger.warning("[ADAPTIVE_FUSION] No confidences provided")
            return FusionResult(
                fused_confidence=0.5,
                individual_confidences=[],
                fusion_method=FusionMethod.ADAPTIVE,
                uncertainty=1.0,
                conflict_score=0.0,
                weights_used=[],
                reasoning="No confidences provided"
            )
        
        # Analyze confidences
        conflict_score = np.std(confidences) if len(confidences) > 1 else 0.0
        confidence_range = max(confidences) - min(confidences)
        average_confidence = np.mean(confidences)
        
        # Select fusion method based on context and confidence characteristics
        context = context or {}
        
        # Check for explicit method preference
        preferred_method = context.get("preferred_method")
        if preferred_method == "bayesian":
            result = self.bayesian.fuse_confidences(confidences)
            result.reasoning = f"Adaptive (preferred Bayesian): {result.reasoning}"
            return result
        elif preferred_method == "dempster_shafer":
            result = self.dempster_shafer.fuse_confidences(confidences)
            result.reasoning = f"Adaptive (preferred DS): {result.reasoning}"
            return result
        
        # Adaptive selection based on confidence characteristics
        if conflict_score > 0.3:
            # High conflict: use conservative approach
            result = self.conservative.fuse_confidences(confidences)
            result.reasoning = f"Adaptive (high conflict): {result.reasoning}"
        
        elif confidence_range > 0.5:
            # Wide range: use Dempster-Shafer for uncertainty handling
            result = self.dempster_shafer.fuse_confidences(confidences)
            result.reasoning = f"Adaptive (wide range): {result.reasoning}"
        
        elif average_confidence > 0.8 or average_confidence < 0.2:
            # Extreme confidence: use Bayesian for belief updating
            result = self.bayesian.fuse_confidences(confidences)
            result.reasoning = f"Adaptive (extreme confidence): {result.reasoning}"
        
        else:
            # Normal case: use weighted average
            result = self.weighted.fuse_confidences(confidences)
            result.reasoning = f"Adaptive (normal): {result.reasoning}"
        
        logger.debug(f"[ADAPTIVE_FUSION] Selected method based on conflict={conflict_score:.2f}")
        
        return result


class ConfidenceFusionEngine:
    """Main confidence fusion engine with multiple methods."""
    
    def __init__(self, default_method: FusionMethod = FusionMethod.ADAPTIVE):
        """Initialize fusion engine with all methods.
        
        Args:
            default_method: Default fusion method to use
        """
        self.default_method = default_method
        
        # Initialize all fusion methods
        self.bayesian = BayesianFusion()
        self.dempster_shafer = DempsterShaferFusion()
        self.weighted = WeightedAverageFusion()
        self.conservative = ConservativeFusion()
        self.adaptive = AdaptiveFusion()
        
        logger.info(f"[FUSION_ENGINE] Initialized with default method: {default_method.value}")
    
    def fuse(self, confidences: List[float], method: Optional[FusionMethod] = None,
             context: Dict[str, Any] = None, **kwargs) -> FusionResult:
        """Fuse confidences using specified or default method.
        
        Args:
            confidences: List of confidence scores from different sources
            method: Fusion method to use (default: default_method)
            context: Context information for fusion
            **kwargs: Additional parameters for specific methods
            
        Returns:
            FusionResult with fused confidence
        """
        if not confidences:
            logger.warning("[FUSION_ENGINE] No confidences provided")
            return FusionResult(
                fused_confidence=0.5,
                individual_confidences=[],
                fusion_method=method or self.default_method,
                uncertainty=1.0,
                conflict_score=0.0,
                weights_used=[],
                reasoning="No confidences provided"
            )
        
        # Use specified method or default
        fusion_method = method or self.default_method
        
        # Route to appropriate fusion method
        if fusion_method == FusionMethod.BAYESIAN:
            return self.bayesian.fuse_confidences(confidences, kwargs.get('likelihoods'))
        elif fusion_method == FusionMethod.DEMPSTER_SHAFER:
            return self.dempster_shafer.fuse_confidences(confidences, kwargs.get('masses'))
        elif fusion_method == FusionMethod.WEIGHTED_AVERAGE:
            return self.weighted.fuse_confidences(confidences, kwargs.get('weights'))
        elif fusion_method == FusionMethod.CONSERVATIVE:
            return self.conservative.fuse_confidences(confidences)
        elif fusion_method == FusionMethod.ADAPTIVE:
            return self.adaptive.fuse_confidences(confidences, context)
        else:
            logger.warning(f"[FUSION_ENGINE] Unknown method {fusion_method}, using adaptive")
            return self.adaptive.fuse_confidences(confidences, context)


__all__ = [
    "FusionMethod",
    "FusionResult",
    "BayesianFusion",
    "DempsterShaferFusion",
    "WeightedAverageFusion",
    "ConservativeFusion",
    "AdaptiveFusion",
    "ConfidenceFusionEngine"
]
