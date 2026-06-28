"""SIGNAL-01 — Advanced signal processing and quality assessment.

Enhances INDIRA's signal processing with advanced filtering,
noise reduction, signal quality assessment, and multi-signal fusion.

Pure computation. No clocks, no I/O. INV-15 deterministic.
B1: No imports from execution_engine/governance_engine/learning_engine/evolution_engine.
"""

from __future__ import annotations

import math
from collections import deque
from dataclasses import dataclass
from enum import Enum
from typing import Any


class SignalQuality(Enum):
    """Signal quality levels."""

    HIGH = "high"  # Strong, reliable signal
    MEDIUM = "medium"  # Moderate confidence
    LOW = "low"  # Weak, noisy signal
    REJECT = "reject"  # Should not be acted upon


class FilterType(Enum):
    """Types of signal filters."""

    MOVING_AVERAGE = "moving_average"
    EXPONENTIAL = "exponential"
    KALMAN = "kalman"
    MEDIAN = "median"
    LOW_PASS = "low_pass"
    HIGH_PASS = "high_pass"


@dataclass(frozen=True, slots=True)
class SignalMetrics:
    """Metrics for signal quality assessment."""

    signal_id: str
    signal_strength: float  # Magnitude of the signal
    signal_to_noise_ratio: float  # SNR
    consistency: float  # How consistent the signal is over time
    age_bars: int  # How old the signal is
    predictive_accuracy: float  # Historical accuracy
    confidence_level: SignalQuality
    timestamp_ns: int


@dataclass(frozen=True, slots=True)
class FilteredSignal:
    """Signal after processing and filtering."""

    original_signal: dict[str, Any]
    filtered_signal: dict[str, Any]
    filter_applied: FilterType
    noise_removed: float  # Percentage of noise removed
    signal_preserved: float  # Percentage of signal preserved
    quality_improvement: float  # Improvement in signal quality
    timestamp_ns: int


@dataclass(frozen=True, slots=True)
class FusedSignal:
    """Multi-signal fusion result."""

    signal_id: str
    component_signals: tuple[str, ...]  # IDs of component signals
    fused_strength: float
    fused_confidence: float
    fusion_method: str
    component_weights: dict[str, float]
    consensus_level: float  # How much component signals agree
    final_decision: str  # What action the fused signal recommends
    timestamp_ns: int


class AdvancedSignalProcessor:
    """Advanced signal processing with filtering and quality assessment.

    Applies various filters to reduce noise and improve signal quality,
    with comprehensive quality assessment and multi-signal fusion.
    """

    def __init__(self, default_filter: FilterType = FilterType.EXPONENTIAL) -> None:
        self._default_filter = default_filter

        self._signal_history: deque[dict[str, Any]] = deque(maxlen=100)
        self._noise_estimate: float = 0.0
        self._filter_states: dict[str, Any] = {}  # Per-signal filter state

    def apply_filter(
        self, signal: dict[str, Any], filter_type: FilterType | None = None, timestamp_ns: int = 0
    ) -> FilteredSignal:
        """Apply specified filter to signal.

        Args:
            signal: Input signal with 'value' field
            filter_type: Type of filter to apply
            timestamp_ns: Current timestamp

        Returns:
            Filtered signal with quality metrics
        """
        filter_type = filter_type or self._default_filter

        signal_value = signal.get("value", 0.0)

        if filter_type == FilterType.MOVING_AVERAGE:
            filtered_value = self._apply_moving_average(signal_value, timestamp_ns)
        elif filter_type == FilterType.EXPONENTIAL:
            filtered_value = self._apply_exponential_filter(signal_value, timestamp_ns)
        elif filter_type == FilterType.MEDIAN:
            filtered_value = self._apply_median_filter(signal_value, timestamp_ns)
        else:
            filtered_value = signal_value  # No filtering

        # Calculate noise removal and signal preservation
        noise_removed = self._estimate_noise_removal(signal_value, filtered_value)
        signal_preserved = self._estimate_signal_preservation(signal_value, filtered_value)

        # Calculate quality improvement
        quality_improvement = self._calculate_quality_improvement(signal_value, filtered_value)

        # Create filtered signal
        filtered_signal_data = signal.copy()
        filtered_signal_data["value"] = filtered_value
        filtered_signal_data["filter_applied"] = filter_type.value

        return FilteredSignal(
            original_signal=signal,
            filtered_signal=filtered_signal_data,
            filter_applied=filter_type,
            noise_removed=noise_removed,
            signal_preserved=signal_preserved,
            quality_improvement=quality_improvement,
            timestamp_ns=timestamp_ns,
        )

    def _apply_moving_average(self, value: float, timestamp_ns: int) -> float:
        """Apply moving average filter."""
        window_size = 5

        # Get recent values
        recent_values = [s.get("value", 0.0) for s in self._signal_history][-window_size + 1 :]
        recent_values.append(value)

        if len(recent_values) == 0:
            return value

        return sum(recent_values) / len(recent_values)

    def _apply_exponential_filter(self, value: float, timestamp_ns: int) -> float:
        """Apply exponential moving average filter."""
        alpha = 0.2  # Smoothing factor

        # Get previous filtered value
        filter_key = "exp_filter"
        previous_value = self._filter_states.get(filter_key, value)

        # Apply exponential filter
        filtered_value = alpha * value + (1 - alpha) * previous_value

        # Store state
        self._filter_states[filter_key] = filtered_value

        return filtered_value

    def _apply_median_filter(self, value: float, timestamp_ns: int) -> float:
        """Apply median filter."""
        window_size = 7

        # Get recent values
        recent_values = [s.get("value", 0.0) for s in self._signal_history[-window_size + 1 :]]
        recent_values.append(value)

        if len(recent_values) == 0:
            return value

        # Sort and take median
        sorted_values = sorted(recent_values)
        n = len(sorted_values)

        if n % 2 == 0:
            median = (sorted_values[n // 2 - 1] + sorted_values[n // 2]) / 2
        else:
            median = sorted_values[n // 2]

        return median

    def _estimate_noise_removal(self, original: float, filtered: float) -> float:
        """Estimate percentage of noise removed."""
        if original == 0:
            return 0.0

        change = abs(filtered - original)
        noise_estimate = self._noise_estimate if self._noise_estimate > 0 else abs(original) * 0.1

        # Assume difference from original is partially noise
        noise_removed = min(1.0, change / (abs(original) + noise_estimate + 1e-12))

        # Update noise estimate
        self._noise_estimate = noise_estimate * 0.9 + change * 0.1

        return noise_removed

    def _estimate_signal_preservation(self, original: float, filtered: float) -> float:
        """Estimate percentage of signal preserved."""
        if original == 0:
            return 1.0

        # Signal preservation is inversely related to noise removal
        noise_removed = self._estimate_noise_removal(original, filtered)
        signal_preserved = 1.0 - min(0.5, noise_removed * 0.8)  # Preserve at least 50% signal

        return signal_preserved

    def _calculate_quality_improvement(self, original: float, filtered: float) -> float:
        """Calculate improvement in signal quality."""
        # Quality improvement is higher when noise is removed but signal is preserved
        noise_removed = self._estimate_noise_removal(original, filtered)
        signal_preserved = self._estimate_signal_preservation(original, filtered)

        quality_improvement = noise_removed * signal_preserved

        return quality_improvement

    def assess_signal_quality(self, signal: dict[str, Any], timestamp_ns: int = 0) -> SignalMetrics:
        """Assess the quality of a signal.

        Args:
            signal: Signal to assess
            timestamp_ns: Current timestamp

        Returns:
            Signal quality metrics
        """
        signal_id = signal.get("signal_id", "unknown")
        signal_value = signal.get("value", 0.0)
        signal_confidence = signal.get("confidence", 0.5)

        # Signal strength based on absolute value
        signal_strength = min(1.0, abs(signal_value) / 2.0)

        # Estimate SNR
        snr = self._estimate_snr(signal_value)

        # Consistency based on historical signal behavior
        consistency = self._calculate_consistency(signal_id, signal_value, timestamp_ns)

        # Predictive accuracy (simplified)
        predictive_accuracy = min(1.0, signal_confidence * 1.2)

        # Determine confidence level
        overall_quality = (
            signal_strength * 0.3 + snr * 0.3 + consistency * 0.2 + predictive_accuracy * 0.2
        )

        if overall_quality > 0.7:
            confidence_level = SignalQuality.HIGH
        elif overall_quality > 0.4:
            confidence_level = SignalQuality.MEDIUM
        elif overall_quality > 0.2:
            confidence_level = SignalQuality.LOW
        else:
            confidence_level = SignalQuality.REJECT

        # Store signal
        self._signal_history.append(
            {"signal_id": signal_id, "signal": signal, "timestamp_ns": timestamp_ns}
        )

        return SignalMetrics(
            signal_id=signal_id,
            signal_strength=signal_strength,
            signal_to_noise_ratio=snr,
            consistency=consistency,
            age_bars=0,  # Would track signal age in production
            predictive_accuracy=predictive_accuracy,
            confidence_level=confidence_level,
            timestamp_ns=timestamp_ns,
        )

    def _estimate_snr(self, signal_value: float) -> float:
        """Estimate signal-to-noise ratio."""
        # SNR estimation based on noise estimate
        noise_level = self._noise_estimate if self._noise_estimate > 0 else abs(signal_value) * 0.2

        if noise_level == 0:
            return 1.0

        signal_magnitude = abs(signal_value)
        snr = signal_magnitude / (signal_magnitude + noise_level)

        return min(1.0, snr)

    def _calculate_consistency(
        self, signal_id: str, signal_value: float, timestamp_ns: int
    ) -> float:
        """Calculate signal consistency over time."""
        # Get historical values for this signal
        historical = [
            s.get("value", 0.0) for s in self._signal_history if s.get("signal_id") == signal_id
        ]

        if len(historical) < 3:
            return 0.5  # Unknown consistency

        # Calculate coefficient of variation
        mean = sum(historical) / len(historical)
        if mean == 0:
            return 0.5

        variance = sum((h - mean) ** 2 for h in historical) / len(historical)
        std = math.sqrt(variance)

        cv = std / abs(mean) if mean != 0 else 0.0

        # Lower CV = higher consistency
        consistency = max(0.0, 1.0 - cv * 0.5)

        return consistency

    def fuse_signals(
        self,
        signals: tuple[dict[str, Any], ...],
        fusion_method: str = "weighted_average",
        timestamp_ns: int = 0,
    ) -> FusedSignal:
        """Fuse multiple signals into a single decision.

        Args:
            signals: Signals to fuse
            fusion_method: Fusion method to use
            timestamp_ns: Current timestamp

        Returns:
            Fused signal with combined strength and confidence
        """
        if not signals:
            return FusedSignal(
                signal_id=f"fused_{timestamp_ns}",
                component_signals=(),
                fused_strength=0.0,
                fused_confidence=0.0,
                fusion_method=fusion_method,
                component_weights={},
                consensus_level=0.0,
                final_decision="no_decision",
                timestamp_ns=timestamp_ns,
            )

        # Extract signal qualities
        signal_qualities = []
        for signal in signals:
            metrics = self.assess_signal_quality(signal, timestamp_ns)
            signal_qualities.append(metrics)

        # Determine fusion method
        if fusion_method == "weighted_average":
            return self._weighted_average_fusion(signals, signal_qualities, timestamp_ns)
        elif fusion_method == "voting":
            return self._voting_fusion(signals, signal_qualities, timestamp_ns)
        elif fusion_method == "bayesian":
            return self._bayesian_fusion(signals, signal_qualities, timestamp_ns)
        else:
            return self._weighted_average_fusion(signals, signal_qualities, timestamp_ns)

    def _weighted_average_fusion(
        self,
        signals: tuple[dict[str, Any], ...],
        qualities: tuple[SignalMetrics, ...],
        timestamp_ns: int,
    ) -> FusedSignal:
        """Weighted average fusion based on signal quality."""
        component_weights = {}
        total_weight = 0.0

        fused_strength = 0.0
        fused_confidence = 0.0

        for signal, quality in zip(signals, qualities):
            # Weight based on quality (high quality = higher weight)
            quality_score = 0.3  # base score

            if quality.confidence_level == SignalQuality.HIGH:
                quality_score += 0.4
            elif quality.confidence_level == SignalQuality.MEDIUM:
                quality_score += 0.2
            elif quality.confidence_level == SignalQuality.LOW:
                quality_score += 0.1
            else:
                quality_score -= 0.2

            weight = quality_score * signal.get("confidence", 0.5)

            signal_id = signal.get("signal_id", "unknown")
            component_weights[signal_id] = weight
            total_weight += weight

            fused_strength += signal.get("value", 0) * weight
            fused_confidence += signal.get("confidence", 0.0) * weight

        # Normalize
        if total_weight > 0:
            fused_strength = fused_strength / total_weight
            fused_confidence = fused_confidence / total_weight
            component_weights = {k: v / total_weight for k, v in component_weights.items()}

        # Calculate consensus level
        signal_decisions = [s.get("decision", "neutral") for s in signals]
        decision_counts = {}
        for decision in signal_decisions:
            decision_counts[decision] = decision_counts.get(decision, 0) + 1

        if decision_counts:
            max_count = max(decision_counts.values())
            consensus_level = max_count / len(signal_decisions)
        else:
            consensus_level = 0.0

        # Final decision based on weighted average direction
        if fused_strength > 0:
            final_decision = "long"
        elif fused_strength < 0:
            final_decision = "short"
        else:
            final_decision = "hold"

        return FusedSignal(
            signal_id=f"fused_{timestamp_ns}",
            component_signals=tuple(s.get("signal_id", "unknown") for s in signals),
            fused_strength=fused_strength,
            fused_confidence=fused_confidence,
            fusion_method="weighted_average",
            component_weights=component_weights,
            consensus_level=consensus_level,
            final_decision=final_decision,
            timestamp_ns=timestamp_ns,
        )

    def _voting_fusion(
        self,
        signals: tuple[dict[str, Any], ...],
        qualities: tuple[SignalMetrics, ...],
        timestamp_ns: int,
    ) -> FusedSignal:
        """Voting fusion based on component signals."""
        signal_decisions = []

        for signal, quality in zip(signals, qualities):
            # Vote based on signal direction and quality
            signal_value = signal.get("value", 0)
            decision = "long" if signal_value > 0 else ("short" if signal_value < 0 else "hold")

            signal_decisions.append(
                {
                    "signal_id": signal.get("signal_id", "unknown"),
                    "decision": decision,
                    "weight": 1.0 if quality.confidence_level != SignalQuality.REJECT else 0.0,
                }
            )

        # Tally votes
        vote_counts = {"long": 0.0, "short": 0.0, "hold": 0.0}
        for vote in signal_decisions:
            vote_counts[vote["decision"]] += vote["weight"]

        # Determine winner
        max_votes = max(vote_counts.values())
        final_decision = max(vote_counts, key=vote_counts.get)

        # Calculate confidence based on vote distribution
        total_votes = sum(vote_counts.values())
        confidence = max_votes / total_votes if total_votes > 0 else 0.0

        # Calculate component weights (equal for voting)
        component_weights = {
            vote["signal_id"]: 1.0 / len(signal_decisions) for vote in signal_decisions
        }

        return FusedSignal(
            signal_id=f"fused_{timestamp_ns}",
            component_signals=tuple(s["signal_id"] for s in signal_decisions),
            fused_strength=0.5,  # Not applicable for voting
            fused_confidence=confidence,
            fusion_method="voting",
            component_weights=component_weights,
            consensus_level=confidence,
            final_decision=final_decision,
            timestamp_ns=timestamp_ns,
        )

    def _bayesian_fusion(
        self,
        signals: tuple[dict[str, Any], ...],
        qualities: tuple[SignalMetrics, ...],
        timestamp_ns: int,
    ) -> FusedSignal:
        """Bayesian fusion using signal quality as prior."""
        # Simplified Bayesian update
        fused_strength = 0.0
        fused_confidence = 0.0
        component_weights = {}

        prior_belief = 0.5  # Neutral prior

        total_weight = 0.0
        for signal, quality in zip(signals, qualities):
            # Use signal confidence as likelihood
            likelihood = signal.get("confidence", 0.5)

            # Bayesian update
            posterior = prior_belief * likelihood
            weight = posterior / (prior_belief * likelihood + 1e-12)  # Normalized

            signal_id = signal.get("signal_id", "unknown")
            component_weights[signal_id] = weight
            total_weight += weight

            fused_strength += signal.get("value", 0.0) * weight
            fused_confidence += likelihood * weight

        # Normalize
        if total_weight > 0:
            fused_strength = fused_strength / total_weight
            fused_confidence = fused_confidence / total_weight
            component_weights = {k: v / total_weight for k, v in component_weights.items()}

        # Final decision
        if fused_strength > 0:
            final_decision = "long"
        elif fused_strength < 0:
            final_decision = "short"
        else:
            final_decision = "hold"

        # Consensus level (simplified)
        consensus_level = min(1.0, fused_confidence)

        return FusedSignal(
            signal_id=f"fused_{timestamp_ns}",
            component_signals=tuple(s.get("signal_id", "unknown") for s in signals),
            fused_strength=fused_strength,
            fused_confidence=fused_confidence,
            fusion_method="bayesian",
            component_weights=component_weights,
            consensus_level=consensus_level,
            final_decision=final_decision,
            timestamp_ns=timestamp_ns,
        )


__all__ = [
    "SignalQuality",
    "FilterType",
    "SignalMetrics",
    "FilteredSignal",
    "FusedSignal",
    "AdvancedSignalProcessor",
]
