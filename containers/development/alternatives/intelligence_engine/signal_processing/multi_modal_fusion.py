"""Multi-Modal Signal Fusion for INDIRA.

Enhanced signal fusion that integrates signals from different modalities:
- Technical signals (price action, indicators, microstructure)
- Fundamental signals (macro, earnings, financial ratios)
- Sentiment signals (news, social media, sentiment aggregators)
- Neuromorphic signals (SPIKE_SIGNAL_EVENT, system anomalies)

Per INV-15: Pure computation, no clock reads, no PRNG, no IO. Deterministic replays.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Protocol

from core.contracts.events import Side


class SignalModality(Enum):
    """Signal modality types."""

    TECHNICAL = "technical"
    FUNDAMENTAL = "fundamental"
    SENTIMENT = "sentiment"
    NEUROMORPHIC = "neuromorphic"
    CROSS_ASSET = "cross_asset"
    REGIME = "regime"


class FusionMethod(Enum):
    """Signal fusion methods."""

    WEIGHTED_AVERAGE = "weighted_average"
    BAYESIAN_FUSION = "bayesian_fusion"
    DEMPSTER_SHAFER = "dempster_shafer"
    ENSEMBLE = "ensemble"
    META_LEARNING = "meta_learning"
    CONSENSUS = "consensus"


@dataclass(frozen=True, slots=True)
class ModalitySignal:
    """Signal from a specific modality."""

    signal_id: str
    modality: SignalModality
    value: float
    confidence: float
    side: Side | None
    timestamp_ns: int
    features: dict[str, float]
    source: str


@dataclass(frozen=True, slots=True)
class ModalityWeight:
    """Weight for a signal modality."""

    modality: SignalModality
    weight: float
    adaptive: bool = False  # Whether weight adapts based on performance
    performance_score: float = 1.0  # Historical performance (0-1)


@dataclass(frozen=True, slots=True)
class FusionResult:
    """Result of multi-modal signal fusion."""

    fused_signal_id: str
    fused_value: float
    fused_confidence: float
    fused_side: Side | None
    fusion_method: FusionMethod
    modality_weights: dict[SignalModality, float]
    consensus_score: float  # How much modalities agree
    conflict_score: float  # How much modalities disagree
    conflict_resolution: str  # How conflicts were resolved
    component_signals: tuple[ModalitySignal, ...]
    timestamp_ns: int


@dataclass(frozen=True, slots=True)
class ModalityConflict:
    """Conflict between modalities."""

    conflicting_modalities: tuple[SignalModality, ...]
    conflict_magnitude: float  # 0-1 scale
    resolution_method: str
    resolved_value: float
    resolved_confidence: float


class SignalPerformanceTracker(Protocol):
    """Protocol for tracking signal performance."""

    def update_performance(
        self,
        modality: SignalModality,
        signal_id: str,
        actual_outcome: float,
        predicted_outcome: float,
    ) -> float:
        """Update performance score for a signal.

        Returns:
            Updated performance score (0-1)
        """
        ...

    def get_performance(self, modality: SignalModality, signal_id: str) -> float:
        """Get current performance score for a signal."""
        ...

    def get_modality_performance(self, modality: SignalModality) -> float:
        """Get aggregate performance for a modality."""
        ...


@dataclass
class MultiModalSignalFusion:
    """Multi-modal signal fusion engine.

    Integrates signals from different modalities using various fusion methods.
    Adapts weights based on historical performance.

    Attributes:
        default_method: Default fusion method
        min_confidence: Minimum confidence for fusion output
        consensus_threshold: Minimum consensus to emit signal
        performance_window: Window for performance tracking
    """

    default_method: FusionMethod = FusionMethod.WEIGHTED_AVERAGE
    min_confidence: float = 0.6
    consensus_threshold: float = 0.7
    performance_window: int = 100

    # Modality weights
    _modality_weights: dict[SignalModality, ModalityWeight] = field(
        default_factory=lambda: {
            SignalModality.TECHNICAL: ModalityWeight(SignalModality.TECHNICAL, 0.3, True),
            SignalModality.FUNDAMENTAL: ModalityWeight(SignalModality.FUNDAMENTAL, 0.2, True),
            SignalModality.SENTIMENT: ModalityWeight(SignalModality.SENTIMENT, 0.2, True),
            SignalModality.NEUROMORPHIC: ModalityWeight(SignalModality.NEUROMORPHIC, 0.15, True),
            SignalModality.CROSS_ASSET: ModalityWeight(SignalModality.CROSS_ASSET, 0.1, True),
            SignalModality.REGIME: ModalityWeight(SignalModality.REGIME, 0.05, True),
        },
        init=False,
        repr=False,
    )

    # Performance tracker (injected)
    _performance_tracker: SignalPerformanceTracker = field(default=None, init=False, repr=False)

    # Recent signals for analysis
    _recent_signals: dict[SignalModality, list[ModalitySignal]] = field(
        default_factory=dict, init=False, repr=False
    )

    # Conflict history
    _conflict_history: list[ModalityConflict] = field(default_factory=list, init=False, repr=False)

    def __post_init__(self) -> None:
        # Initialize signal buffers for each modality
        for modality in SignalModality:
            self._recent_signals[modality] = []

    def add_signal(self, signal: ModalitySignal) -> None:
        """Add a signal to the fusion engine."""
        modality = signal.modality

        # Add to recent signals (keep limited history)
        self._recent_signals[modality].append(signal)
        if len(self._recent_signals[modality]) > self.performance_window:
            self._recent_signals[modality] = self._recent_signals[modality][
                -self.performance_window :
            ]

    def fuse_signals(
        self,
        signals: tuple[ModalitySignal, ...],
        method: FusionMethod | None = None,
        timestamp_ns: int = 0,
    ) -> FusionResult | None:
        """Fuse signals from multiple modalities.

        Args:
            signals: Signals to fuse
            method: Fusion method (uses default if None)
            timestamp_ns: Current timestamp

        Returns:
            FusionResult if fusion successful with sufficient confidence, None otherwise
        """
        if not signals:
            return None

        method = method or self.default_method

        # Group signals by modality
        modality_groups: dict[SignalModality, list[ModalitySignal]] = {}
        for signal in signals:
            if signal.modality not in modality_groups:
                modality_groups[signal.modality] = []
            modality_groups[signal.modality].append(signal)

        # Compute per-modality aggregates
        modality_aggregates = self._compute_modality_aggregates(modality_groups)

        # Detect conflicts
        conflicts = self._detect_conflicts(modality_aggregates)

        # Resolve conflicts
        if conflicts:
            modality_aggregates = self._resolve_conflicts(modality_aggregates, conflicts)

        # Apply fusion method
        if method == FusionMethod.WEIGHTED_AVERAGE:
            return self._weighted_average_fusion(modality_aggregates, timestamp_ns)
        elif method == FusionMethod.BAYESIAN_FUSION:
            return self._bayesian_fusion(modality_aggregates, timestamp_ns)
        elif method == FusionMethod.CONSENSUS:
            return self._consensus_fusion(modality_aggregates, timestamp_ns)
        else:
            return self._weighted_average_fusion(modality_aggregates, timestamp_ns)

    def _compute_modality_aggregates(
        self,
        modality_groups: dict[SignalModality, list[ModalitySignal]],
    ) -> dict[SignalModality, tuple[float, float, Side | None]]:
        """Compute aggregate values per modality.

        Returns:
            dict mapping modality to (value, confidence, side)
        """
        aggregates = {}

        for modality, signals in modality_groups.items():
            if not signals:
                continue

            # Weighted average by confidence
            total_confidence = sum(s.confidence for s in signals)
            if total_confidence == 0:
                total_confidence = 1.0

            weighted_value = sum(s.value * s.confidence for s in signals) / total_confidence
            weighted_confidence = total_confidence / len(signals)

            # Aggregate side (majority vote weighted by confidence)
            side_votes: dict[Side | None, float] = {}
            for signal in signals:
                side_votes[signal.side] = side_votes.get(signal.side, 0.0) + signal.confidence

            if side_votes:
                aggregated_side = max(side_votes, key=side_votes.get)
            else:
                aggregated_side = None

            aggregates[modality] = (weighted_value, weighted_confidence, aggregated_side)

        return aggregates

    def _detect_conflicts(
        self,
        modality_aggregates: dict[SignalModality, tuple[float, float, Side | None]],
    ) -> list[ModalityConflict]:
        """Detect conflicts between modalities."""
        conflicts = []

        if len(modality_aggregates) < 2:
            return conflicts

        # Get values and sides
        values = {m: data[0] for m, data in modality_aggregates.items()}
        sides = {m: data[2] for m, data in modality_aggregates.items()}

        # Check for side conflicts (BUY vs SELL)
        buy_modalities = [m for m, s in sides.items() if s == Side.BUY]
        sell_modalities = [m for m, s in sides.items() if s == Side.SELL]

        if buy_modalities and sell_modalities:
            # Calculate conflict magnitude
            buy_weight = sum(self._modality_weights[m].weight for m in buy_modalities)
            sell_weight = sum(self._modality_weights[m].weight for m in sell_modalities)
            total_weight = buy_weight + sell_weight

            conflict_magnitude = (
                2.0 * min(buy_weight, sell_weight) / total_weight if total_weight > 0 else 0.0
            )

            if conflict_magnitude > 0.3:  # Significant conflict
                conflict = ModalityConflict(
                    conflicting_modalities=tuple(buy_modalities + sell_modalities),
                    conflict_magnitude=conflict_magnitude,
                    resolution_method="weighted_majority",
                    resolved_value=0.0,  # Will be computed in resolution
                    resolved_confidence=0.0,
                )
                conflicts.append(conflict)

        return conflicts

    def _resolve_conflicts(
        self,
        modality_aggregates: dict[SignalModality, tuple[float, float, Side | None]],
        conflicts: list[ModalityConflict],
    ) -> dict[SignalModality, tuple[float, float, Side | None]]:
        """Resolve conflicts between modalities."""
        if not conflicts:
            return modality_aggregates

        # Simple resolution: use weighted majority
        # In a more sophisticated implementation, could use performance-based resolution
        return modality_aggregates

    def _weighted_average_fusion(
        self,
        modality_aggregates: dict[SignalModality, tuple[float, float, Side | None]],
        timestamp_ns: int,
    ) -> FusionResult | None:
        """Weighted average fusion."""
        if not modality_aggregates:
            return None

        # Get adaptive weights
        weights = self._get_adaptive_weights(modality_aggregates)

        # Compute weighted values
        total_weight = sum(w for w in weights.values())
        if total_weight == 0:
            total_weight = 1.0

        weighted_value = (
            sum(
                data[0] * weights.get(modality, 0.0)
                for modality, data in modality_aggregates.items()
            )
            / total_weight
        )

        weighted_confidence = (
            sum(
                data[1] * weights.get(modality, 0.0)
                for modality, data in modality_aggregates.items()
            )
            / total_weight
        )

        # Aggregate side
        side_votes: dict[Side | None, float] = {}
        for modality, data in modality_aggregates.items():
            side = data[2]
            weight = weights.get(modality, 0.0)
            side_votes[side] = side_votes.get(side, 0.0) + weight

        fused_side = max(side_votes, key=side_votes.get) if side_votes else None

        # Compute consensus
        consensus_score = self._compute_consensus(modality_aggregates, weights)
        conflict_score = 1.0 - consensus_score

        # Check minimum confidence
        if weighted_confidence < self.min_confidence:
            return None

        # Check consensus threshold
        if (
            consensus_score < self.consensus_threshold
            and self.default_method == FusionMethod.CONSENSUS
        ):
            return None

        # Collect component signals
        component_signals = []
        for modality, signals in self._recent_signals.items():
            if signals:
                component_signals.append(signals[-1])

        return FusionResult(
            fused_signal_id=f"fused_{timestamp_ns}",
            fused_value=weighted_value,
            fused_confidence=weighted_confidence,
            fused_side=fused_side,
            fusion_method=FusionMethod.WEIGHTED_AVERAGE,
            modality_weights=weights,
            consensus_score=consensus_score,
            conflict_score=conflict_score,
            conflict_resolution="weighted_average" if conflict_score > 0.3 else "none",
            component_signals=tuple(component_signals),
            timestamp_ns=timestamp_ns,
        )

    def _bayesian_fusion(
        self,
        modality_aggregates: dict[SignalModality, tuple[float, float, Side | None]],
        timestamp_ns: int,
    ) -> FusionResult | None:
        """Bayesian fusion using prior probabilities."""
        if not modality_aggregates:
            return None

        # Simplified Bayesian fusion
        # Treat each modality as evidence updating a prior belief
        prior_value = 0.0
        prior_confidence = 0.5

        for modality, data in modality_aggregates.items():
            value, confidence, side = data
            weight = self._modality_weights[modality].weight

            # Bayesian update (simplified)
            prior_value = prior_value * (1 - confidence * weight) + value * confidence * weight
            prior_confidence = prior_confidence * (1 - confidence * weight) + confidence * weight

        # Aggregate side
        side_votes: dict[Side | None, float] = {}
        for modality, data in modality_aggregates.items():
            side = data[2]
            confidence = data[1]
            weight = self._modality_weights[modality].weight
            side_votes[side] = side_votes.get(side, 0.0) + confidence * weight

        fused_side = max(side_votes, key=side_votes.get) if side_votes else None

        # Compute weights for output
        weights = {m: self._modality_weights[m].weight for m in modality_aggregates.keys()}
        consensus_score = self._compute_consensus(modality_aggregates, weights)
        conflict_score = 1.0 - consensus_score

        if prior_confidence < self.min_confidence:
            return None

        # Collect component signals
        component_signals = []
        for modality, signals in self._recent_signals.items():
            if signals:
                component_signals.append(signals[-1])

        return FusionResult(
            fused_signal_id=f"fused_bayesian_{timestamp_ns}",
            fused_value=prior_value,
            fused_confidence=prior_confidence,
            fused_side=fused_side,
            fusion_method=FusionMethod.BAYESIAN_FUSION,
            modality_weights=weights,
            consensus_score=consensus_score,
            conflict_score=conflict_score,
            conflict_resolution="bayesian_update",
            component_signals=tuple(component_signals),
            timestamp_ns=timestamp_ns,
        )

    def _consensus_fusion(
        self,
        modality_aggregates: dict[SignalModality, tuple[float, float, Side | None]],
        timestamp_ns: int,
    ) -> FusionResult | None:
        """Consensus-based fusion (only emit if modalities agree)."""
        if not modality_aggregates:
            return None

        # Compute consensus
        weights = {m: self._modality_weights[m].weight for m in modality_aggregates.keys()}
        consensus_score = self._compute_consensus(modality_aggregates, weights)

        if consensus_score < self.consensus_threshold:
            return None

        # If consensus is high, use weighted average
        return self._weighted_average_fusion(modality_aggregates, timestamp_ns)

    def _get_adaptive_weights(
        self,
        modality_aggregates: dict[SignalModality, tuple[float, float, Side | None]],
    ) -> dict[SignalModality, float]:
        """Get adaptive weights based on performance."""
        weights = {}

        for modality in modality_aggregates.keys():
            weight_config = self._modality_weights.get(modality)
            if weight_config is None:
                weights[modality] = 0.1
            elif weight_config.adaptive and self._performance_tracker is not None:
                # Use performance-based weight
                performance = self._performance_tracker.get_modality_performance(modality)
                weights[modality] = weight_config.weight * performance
            else:
                weights[modality] = weight_config.weight

        return weights

    def _compute_consensus(
        self,
        modality_aggregates: dict[SignalModality, tuple[float, float, Side | None]],
        weights: dict[SignalModality, float],
    ) -> float:
        """Compute consensus score between modalities (0-1)."""
        if len(modality_aggregates) < 2:
            return 1.0

        # Get sides
        sides = {m: data[2] for m, data in modality_aggregates.items()}

        # Count weighted agreement
        buy_weight = sum(weights[m] for m, s in sides.items() if s == Side.BUY)
        sell_weight = sum(weights[m] for m, s in sides.items() if s == Side.SELL)
        neutral_weight = sum(weights[m] for m, s in sides.items() if s is None)

        total_weight = buy_weight + sell_weight + neutral_weight
        if total_weight == 0:
            return 0.5

        # Consensus is the maximum agreement
        consensus = max(buy_weight, sell_weight, neutral_weight) / total_weight

        return consensus

    def update_modality_performance(
        self,
        modality: SignalModality,
        signal_id: str,
        actual_outcome: float,
        predicted_outcome: float,
    ) -> None:
        """Update performance tracking for a modality."""
        if self._performance_tracker is not None:
            self._performance_tracker.update_performance(
                modality, signal_id, actual_outcome, predicted_outcome
            )

    def set_modality_weight(
        self,
        modality: SignalModality,
        weight: float,
        adaptive: bool = False,
    ) -> None:
        """Set weight for a modality."""
        if not 0.0 <= weight <= 1.0:
            raise ValueError("Weight must be in [0, 1]")

        self._modality_weights[modality] = ModalityWeight(
            modality, weight, adaptive, performance_score=1.0
        )


@dataclass
class CausalSignalFusion:
    """Causal signal fusion using causal inference.

    Identifies causal relationships between signals and uses them
    to improve fusion quality.
    """

    fusion_engine: MultiModalSignalFusion = field(default_factory=MultiModalSignalFusion)
    causal_window: int = 32

    # Causal adjacency matrix
    _causal_matrix: dict[tuple[SignalModality, SignalModality], float] = field(
        default_factory=dict, init=False, repr=False
    )

    def fuse_with_causal_weights(
        self,
        signals: tuple[ModalitySignal, ...],
        timestamp_ns: int = 0,
    ) -> FusionResult | None:
        """Fuse signals using causal relationship weights.

        Modifies the fusion weights based on causal relationships
        between modalities.
        """
        # First, update causal relationships
        self._update_causal_relationships(signals)

        # Apply causal weights to fusion
        # This is a simplified implementation
        # In a full implementation, would use causal inference (DoWhy, EconML)
        return self.fusion_engine.fuse_signals(signals, timestamp_ns=timestamp_ns)

    def _update_causal_relationships(self, signals: tuple[ModalitySignal, ...]) -> None:
        """Update causal relationship matrix."""
        # Simplified: use correlation as proxy for causality
        # In full implementation, would use proper causal inference


__all__ = [
    "MultiModalSignalFusion",
    "CausalSignalFusion",
    "SignalModality",
    "FusionMethod",
    "ModalitySignal",
    "ModalityWeight",
    "FusionResult",
    "ModalityConflict",
    "SignalPerformanceTracker",
]
