"""Macro layer — system-wide market context (regime, breadth, contagion).

This namespace was empty on ``main`` despite the spec calling for a
macro-regime engine, latent embedder, and event aligner. PR D ships the
first module: a rule-based macro regime classifier.
"""

from intelligence_engine.macro.regime_classifier import (
    RegimeClassification,
    RegimeClassifier,
)
from intelligence_engine.macro.regime_engine import (
    MacroRegimeEngine,
    MacroRegimeEngineConfig,
    load_macro_regime_config,
)
from intelligence_engine.macro.regime_transition_adapter import (
    RegimeAdaptationStrategy,
    RegimeTransitionPredictor,
    RegimeTransitionSignal,
    RegimeTransitionType,
    SmoothRegimeAdapter,
    SmoothTransitionState,
)

__all__ = [
    "MacroRegimeEngine",
    "MacroRegimeEngineConfig",
    "load_macro_regime_config",
    "RegimeClassification",
    "RegimeClassifier",
    "RegimeTransitionType",
    "RegimeTransitionSignal",
    "RegimeAdaptationStrategy",
    "SmoothTransitionState",
    "RegimeTransitionPredictor",
    "SmoothRegimeAdapter",
]
