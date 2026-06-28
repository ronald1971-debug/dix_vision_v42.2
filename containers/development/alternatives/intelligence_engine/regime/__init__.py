"""Advanced Regime Modeling for INDIRA.

This package provides advanced regime modeling capabilities including:
- Hidden Markov Models for regime transitions
- Bayesian regime change detection
- Multi-timescale regime detection
- Cross-asset regime synchronization
- Regime persistence prediction

Per INV-15: Pure computation, no clock reads, no PRNG, no IO. Deterministic replays.
"""

from intelligence_engine.regime.advanced_regime_model import (
    AdvancedRegimeModel,
    BayesianChangeDetector,
    HMMDetector,
    MultiTimescaleRegimeModel,
    RegimeState,
    RegimeTransition,
)

__all__ = [
    "AdvancedRegimeModel",
    "MultiTimescaleRegimeModel",
    "RegimeState",
    "RegimeTransition",
    "HMMDetector",
    "BayesianChangeDetector",
]
