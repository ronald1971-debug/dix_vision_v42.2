"""Latent regime embedding adapter — feeds vectorised market state into
the meta-controller and agent layer.

Wraps :class:`intelligence_engine.macro.latent_embedder.LatentEmbedder`
and injects the resulting embedding as an additional feature channel
so that the regime router and agent slates can reason over continuous
market-state vectors rather than discrete labels alone.
"""

from __future__ import annotations

from dataclasses import dataclass

from core.contracts.events import SignalEvent
from intelligence_engine.macro.latent_embedder import LatentEmbedder, LatentEmbedding


@dataclass(frozen=True, slots=True)
class RegimeFeatures:
    ts_ns: int
    vol_spike_z: float = 0.0
    momentum_1m: float = 0.0
    spread_bps: float = 0.0
    depth_imbalance: float = 0.0
    # extend as needed


@dataclass(frozen=True, slots=True)
class LatentRegimeState:
    embedding: tuple[float, ...]
    dim: int
    nearest_regime: str = "UNKNOWN"
    regime_confidence: float = 0.0
    digest: str = ""


class LatentRegimeEmbedder:
    """Turn scalar regime features into a dense latent vector.

    The resulting :class:`LatentRegimeState` is:
    * appended to :class:`SignalEvent.meta` under ``latent_regime`` so
      the meta-controller sees it transitively, and
    * exposed via :meth:`as_belief_extension` so callers can inject it
      directly into a :class:`core.coherence.BeliefState` projection
      or a downstream agent.
    """

    def __init__(self, *, seed: int = 42, dim: int = 32, input_dim: int = 8) -> None:
        self._embedder = LatentEmbedder(seed=seed, dim=dim, input_dim=input_dim)
        self._dim = dim
        self._last: LatentRegimeState | None = None

    def update(self, features: RegimeFeatures) -> LatentRegimeState:
        vec: list[float] = [
            features.vol_spike_z,
            features.momentum_1m,
            features.spread_bps,
            features.depth_imbalance,
        ]
        # Pad / truncate to input_dim.
        while len(vec) < self._embedder._input_dim:
            vec.append(0.0)
        vec = vec[: self._embedder._input_dim]

        emb: LatentEmbedding = self._embedder.embed(
            feature_id="regime",
            ts_ns=features.ts_ns,
            features=vec,
        )
        nearest, conf = _nearest_regime(
            vol_spike_z=features.vol_spike_z,
            momentum=features.momentum_1m,
            spread_bps=features.spread_bps,
        )
        state = LatentRegimeState(
            embedding=emb.embedding,
            dim=emb.dim,
            nearest_regime=nearest,
            regime_confidence=conf,
            digest=emb.digest,
        )
        self._last = state
        return state

    def embed_signal(self, signal: SignalEvent, features: RegimeFeatures) -> SignalEvent:
        state = self.update(features)
        meta = dict(signal.meta)
        meta["latent_regime"] = {
            "nearest_regime": state.nearest_regime,
            "regime_confidence": state.regime_confidence,
            "digest": state.digest,
        }
        return SignalEvent(
            ts_ns=signal.ts_ns,
            source=signal.source,
            symbol=signal.symbol,
            side=signal.side,
            confidence=signal.confidence,
            trust=signal.trust,
            meta=meta,
        )

    def last_state(self) -> LatentRegimeState | None:
        return self._last


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class _RegimeCentroids:
    trend_up: tuple[float, ...] = (0.6, 0.4, 0.0, 0.0)
    trend_down: tuple[float, ...] = (-0.6, -0.4, 0.0, 0.0)
    range: tuple[float, ...] = (0.0, 0.0, 0.3, 0.0)
    vol_spike: tuple[float, ...] = (0.0, 0.0, 0.0, 0.8)


_REGIMES = _RegimeCentroids()


def _nearest_regime(
    *,
    vol_spike_z: float,
    momentum: float,
    spread_bps: float,
) -> tuple[str, float]:
    if vol_spike_z >= 3.0:
        return "VOL_SPIKE", min(1.0, vol_spike_z / 5.0)
    if abs(momentum) > 0.5:
        return "TREND_UP" if momentum > 0 else "TREND_DOWN", min(1.0, abs(momentum))
    if spread_bps < 20.0:
        return "RANGE", 0.6
    return "RANGE", 0.4


__all__ = [
    "LatentRegimeEmbedder",
    "LatentRegimeState",
    "RegimeFeatures",
]
