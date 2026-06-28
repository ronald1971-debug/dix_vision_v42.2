"""Confidence fusion — combines confidence from multiple sources.

Fusion methods:
    - Bayesian: Treat confidences as probabilities
    - Weighted: Source-weighted combination
    - Max: Conservative max confidence
    - Min: Risk-averse min confidence
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class FusionMethod(StrEnum):
    BAYESIAN = "BAYESIAN"
    WEIGHTED = "WEIGHTED"
    MAX = "MAX"
    MIN = "MIN"


@dataclass(frozen=True, slots=True)
class ConfidenceSource:
    source: str
    confidence: float
    weight: float = 1.0


def fuse_bayesian(confidences: tuple[float, ...]) -> float:
    """Bayesian fusion - treat confidences as independent probabilities.

    Combined = 1 - product of (1 - c_i)
    """
    if not confidences:
        return 0.0
    result = 1.0
    for c in confidences:
        result *= 1 - c
    return 1 - result


def fuse_weighted(sources: tuple[ConfidenceSource, ...]) -> float:
    """Weighted average fusion."""
    if not sources:
        return 0.0
    total_weight = sum(s.weight for s in sources)
    weighted_sum = sum(s.confidence * s.weight for s in sources)
    return weighted_sum / total_weight if total_weight > 0 else 0.0


def fuse_max(confidences: tuple[float, ...]) -> float:
    """Conservative: take the maximum confidence."""
    return max(confidences) if confidences else 0.0


def fuse_min(confidences: tuple[float, ...]) -> float:
    """Risk-averse: take the minimum confidence."""
    return min(confidences) if confidences else 0.0


def compute_fused_confidence(
    sources: tuple[ConfidenceSource, ...],
    method: FusionMethod = FusionMethod.WEIGHTED,
) -> float:
    """Compute fused confidence using the specified method.

    Args:
        sources: Confidence sources with optional weights
        method: Fusion method to use

    Returns:
        Fused confidence value
    """
    confidences = tuple(s.confidence for s in sources)

    match method:
        case FusionMethod.BAYESIAN:
            return fuse_bayesian(confidences)
        case FusionMethod.WEIGHTED:
            return fuse_weighted(sources)
        case FusionMethod.MAX:
            return fuse_max(confidences)
        case FusionMethod.MIN:
            return fuse_min(confidences)
        case _:
            raise ValueError(f"Unknown fusion method: {method}")
