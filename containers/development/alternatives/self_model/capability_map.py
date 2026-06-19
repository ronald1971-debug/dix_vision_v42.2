"""self_model — DIXVISION understands its own capabilities.

Highest-level capability.

Eventually:
    DIXVISION understands:
        - What it knows
        - What it does not know
        - Where it is weak
        - Where it is strong
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class CapabilityMap:
    """Map of system capabilities."""

    domains: dict[str, float] = field(default_factory=dict)  # domain -> capability score
    strengths: tuple[str, ...] = ()
    gaps: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class ConfidenceMap:
    """Map of system confidence by domain."""

    domain_confidence: dict[str, float] = field(default_factory=dict)
    calibration_quality: float = 0.0


@dataclass(frozen=True, slots=True)
class UncertaintyMap:
    """Map of system uncertainty by domain."""

    domain_uncertainty: dict[str, float] = field(default_factory=dict)
    blind_spots: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class BlindSpotDetector:
    """Detects areas where the system lacks knowledge."""

    def detect(self, knowledge_gaps: dict[str, float],
               performance_drops: dict[str, float]) -> tuple[str, ...]:
        return tuple(k for k, v in knowledge_gaps.items() if v < 0.3 or k in performance_drops)


class SelfModel:
    """DIXVISION's self-understanding.

    Provides:
        - Capability awareness
        - Confidence mapping
        - Uncertainty quantification
        - Blind spot detection
    """

    def __init__(self) -> None:
        self._capability_map = CapabilityMap()
        self._confidence_map = ConfidenceMap()
        self._uncertainty_map = UncertaintyMap()
        self._blind_spot_detector = BlindSpotDetector()

    def update_capability(self, domain: str, score: float) -> None:
        domains = dict(self._capability_map.domains)
        domains[domain] = score
        strengths = tuple(d for d, s in domains.items() if s > 0.7)
        gaps = tuple(d for d, s in domains.items() if s < 0.5)
        object.__setattr__(
            self, '_capability_map',
            CapabilityMap(domains=domains, strengths=strengths, gaps=gaps)
        )

    def update_confidence(self, domain: str, confidence: float) -> None:
        confidences = dict(self._confidence_map.domain_confidence)
        confidences[domain] = confidence
        object.__setattr__(self, '_confidence_map', ConfidenceMap(domain_confidence=confidences))

    def update_uncertainty(self, domain: str, uncertainty: float) -> None:
        uncertainties = dict(self._uncertainty_map.domain_uncertainty)
        uncertainties[domain] = uncertainty
        blind_spots = tuple(d for d, u in uncertainties.items() if u > 0.5)
        object.__setattr__(
            self, '_uncertainty_map',
            UncertaintyMap(domain_uncertainty=uncertainties, blind_spots=blind_spots)
        )

    def get_capability_map(self) -> CapabilityMap:
        return self._capability_map

    def get_confidence_map(self) -> ConfidenceMap:
        return self._confidence_map

    def get_uncertainty_map(self) -> UncertaintyMap:
        return self._uncertainty_map

    def get_blind_spots(self) -> tuple[str, ...]:
        return self._uncertainty_map.blind_spots

    def summarize(self) -> dict[str, Any]:
        return {
            "capabilities": self._capability_map.domains,
            "strengths": self._capability_map.strengths,
            "gaps": self._capability_map.gaps,
            "confidence": self._confidence_map.domain_confidence,
            "uncertainty": self._uncertainty_map.domain_uncertainty,
            "blind_spots": self._uncertainty_map.blind_spots,
        }

    def record_discovery(self, discovery: dict) -> None:
        """Integrate a discovery into the self-model.

        Every confirmed discovery:
          - raises capability in the discovery category
          - lowers uncertainty in that category
        """
        category = discovery.get("object_type") or discovery.get("category") or "unknown"
        confidence = float(discovery.get("confidence", 0.0) or 0.0)
        prev_capability = self._capability_map.domains.get(category, 0.0)
        prev_uncertainty = self._uncertainty_map.domain_uncertainty.get(category, 1.0)
        new_capability = min(1.0, prev_capability + confidence * 0.1)
        new_uncertainty = max(0.0, prev_uncertainty - confidence * 0.1)
        self.update_capability(category, new_capability)
        self.update_uncertainty(category, new_uncertainty)

    def record_discoveries(self, discoveries: list[dict]) -> None:
        """Batch integration for multiple discovery records."""
        for d in discoveries:
            self.record_discovery(d)


__all__ = [
    "BlindSpotDetector",
    "CapabilityMap",
    "ConfidenceMap",
    "SelfModel",
    "UncertaintyMap",
]