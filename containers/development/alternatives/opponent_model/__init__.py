"""Opponent-model package — OPP-XX deterministic predictors.

Phase 10.10 layer. Modules in this package consume an
:class:`~core.contracts.opponent.OpponentObservation` and produce
typed classifications / predictions about the *other side* of the
market. Every module here is pure: same observation, same config →
byte-identical output (INV-15).

Authority constraints (manifest §H1):

* This package imports only from :mod:`core.contracts` and the
  standard library plus PyYAML. No engine cross-imports.
* No clock, no PRNG, no IO outside config load.
* Replay-deterministic.
"""

# TEMPORARY BOOT FIX: Import what actually exists in behavior_predictor.py
# TODO: Implement expected API (BehaviorPredictor, BehaviorPredictorConfig, load_behavior_predictor_config)
from opponent_model.behavior_predictor import (
    ProductionBehaviorPredictor,
    get_production_behavior_predictor,
)

__all__ = [
    "ProductionBehaviorPredictor",
    "get_production_behavior_predictor",
]
