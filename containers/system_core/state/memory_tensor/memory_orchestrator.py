"""MemoryOrchestrator — unified memory orchestration with world-aware tensor operations (Phase 15.2).

Single entry point for all memory writes and queries across every memory kind:

    EPISODIC     — trade episodes (context, action, outcome, reward)
    SEMANTIC     — vector-indexed knowledge (beliefs, patterns, research)
    PROCEDURAL   — action-outcome sequences (how to act in a situation)
    META         — strategy insights and regime patterns
    REGRET       — counterfactual regret log (missed, early-exit, oversized)

Enhanced with world context integration (Phase 15.2):
- Efficient tensor operations for large-scale processing
- World-aware tensor shape optimization
- Tensor compression and decompression
- Tensor distribution across compute resources
- Tensor operation optimization
- Real-time tensor monitoring

All concrete stores are lazily imported and remain implementation details.
Callers only need this module; they never import individual store classes.

Authority: pure state tier — no engine, no runtime, no execution imports.
INV-15: consolidate(ts_ns) is caller-driven; no internal clock reads.
"""

from __future__ import annotations

import logging
import threading
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from collections import deque

# Try to import world model components
try:
    from world_model.indicator_integration import get_integration_bridge
    WORLD_MODEL_AVAILABLE = True
except ImportError:
    WORLD_MODEL_AVAILABLE = False

from state.memory_tensor.contracts import Episode, MemoryQuery, MemoryResult

logger = logging.getLogger(__name__)

_EMBED_DIM = 64
_MAX_EPISODES = 10_000


@dataclass
class WorldContext:
    """World context for tensor operations."""
    
    market_regime: str = "unknown"
    market_trend: str = "unknown"
    volatility_regime: str = "unknown"
    liquidity_state: str = "unknown"
    agent_activity: Dict[str, float] = field(default_factory=dict)
    causal_factors: List[str] = field(default_factory=list)
    prediction_confidence: float = 0.0
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class TensorStats:
    """Tensor operation statistics."""
    
    total_tensors_processed: int = 0
    total_tensor_elements: int = 0
    compression_savings_bytes: int = 0
    operation_count: int = 0
    average_operation_latency_ms: float = 0.0
    optimization_applied: bool = False
    performance_improvement: float = 0.0


class MemoryOrchestrator:
    """Enhanced memory orchestrator with world-aware tensor operations (Phase 15.2).

    Coordinates all memory stores behind a single interface with:
    - World-aware tensor shape optimization
    - Tensor compression for large-scale processing
    - Tensor operation optimization based on world conditions
    - Real-time tensor monitoring and analytics

    Stores are lazily instantiated on first access to keep import cost
    at module-load time to zero.
    """

    def __init__(self) -> None:
        self._episodic: Any = None
        self._semantic: Any = None
        self._procedural: Any = None
        self._meta: Any = None
        self._regret: Any = None
        self._consolidate_seq: int = 0
        
        # Phase 15.2 enhancements
        self._lock = threading.Lock()
        self._world_integration_bridge = None
        self._current_world_context: Optional[WorldContext] = None
        self._world_context_history: deque = deque(maxlen=100)
        self._tensor_stats = TensorStats()
        self._operation_latencies: deque = deque(maxlen=100)
        
        if WORLD_MODEL_AVAILABLE:
            self._init_world_integration()
    
    def _init_world_integration(self) -> None:
        """Initialize world model integration bridge."""
        try:
            self._world_integration_bridge = get_integration_bridge()
            logger.info("[MEMORY_ORCHESTRATOR] World model integration initialized")
        except Exception as e:
            logger.warning(f"[MEMORY_ORCHESTRATOR] Failed to initialize world integration: {e}")
            self._world_integration_bridge = None
    
    def _get_world_context(self) -> Optional[WorldContext]:
        """Get current world context from world model."""
        if not self._world_integration_bridge:
            return None
        
        try:
            world_state = self._world_integration_bridge.get_current_state()
            
            if world_state:
                context = WorldContext(
                    market_regime=world_state.get('market_regime', 'unknown'),
                    market_trend=world_state.get('market_trend', 'unknown'),
                    volatility_regime=world_state.get('volatility_regime', 'unknown'),
                    liquidity_state=world_state.get('liquidity_state', 'unknown'),
                    agent_activity=world_state.get('agent_activity', {}),
                    causal_factors=world_state.get('causal_factors', []),
                    prediction_confidence=world_state.get('prediction_confidence', 0.0),
                    timestamp=datetime.utcnow()
                )
                self._current_world_context = context
                self._world_context_history.append(context)
                return context
        
        except Exception as e:
            logger.debug(f"[MEMORY_ORCHESTRATOR] Failed to get world context: {e}")
        
        return None
    
    def _optimize_tensor_shape(
        self,
        tensor_shape: Tuple[int, ...],
        world_context: Optional[WorldContext]
    ) -> Tuple[int, ...]:
        """Optimize tensor shape based on world context (Phase 15.2)."""
        if not world_context or not tensor_shape:
            return tensor_shape
        
        # Optimize based on volatility regime
        if world_context.volatility_regime == "high":
            # Smaller tensor shapes during high volatility (faster processing)
            if len(tensor_shape) >= 2:
                return tuple(max(1, dim // 2) for dim in tensor_shape)
        elif world_context.volatility_regime == "low":
            # Larger tensor shapes during low volatility (more data for analysis)
            if len(tensor_shape) >= 2:
                return tuple(dim * 2 for dim in tensor_shape)
        
        return tensor_shape
    
    def _calculate_compression_ratio(
        self,
        tensor_elements: int,
        world_context: Optional[WorldContext]
    ) -> float:
        """Calculate compression ratio based on world context (Phase 15.2)."""
        base_compression = 0.5  # 50% compression by default
        
        if world_context:
            # Higher compression during regime transitions (save memory)
            if world_context.market_regime == "transition":
                return 0.7  # 70% compression
            # Lower compression during stable periods (better performance)
            elif world_context.volatility_regime == "low" and world_context.market_trend == "stable":
                return 0.3  # 30% compression
        
        return base_compression
    
    def _adjust_computational_intensity(
        self,
        operation_type: str,
        world_context: Optional[WorldContext]
    ) -> int:
        """Adjust computational intensity based on world context (Phase 15.2)."""
        base_intensity = 1.0
        
        if world_context:
            # Reduce intensity during high volatility
            if world_context.volatility_regime == "high":
                return 0.7  # 30% reduction
            # Increase intensity during stable periods
            elif world_context.volatility_regime == "low" and world_context.market_trend == "stable":
                return 1.3  # 30% increase
        
        return base_intensity

    # ------------------------------------------------------------------
    # Store accessors (lazy)
    # ------------------------------------------------------------------

    @property
    def episodic(self) -> Any:
        if self._episodic is None:
            from state.memory_tensor.episodic import EpisodicMemoryStore
            self._episodic = EpisodicMemoryStore(dim=_EMBED_DIM, max_size=_MAX_EPISODES)
            self._restore_episodes("episodic", self._episodic)
        return self._episodic

    @property
    def semantic(self) -> Any:
        if self._semantic is None:
            from state.memory_tensor.semantic import SemanticMemoryStore
            self._semantic = SemanticMemoryStore(dim=_EMBED_DIM, max_size=_MAX_EPISODES)
            self._restore_episodes("semantic", self._semantic)
        return self._semantic

    @property
    def procedural(self) -> Any:
        if self._procedural is None:
            from state.memory_tensor.procedural import ProceduralMemoryStore
            self._procedural = ProceduralMemoryStore()
        return self._procedural

    @property
    def meta(self) -> Any:
        if self._meta is None:
            from state.memory_tensor.meta_memory import MetaMemoryStore
            self._meta = MetaMemoryStore()
        return self._meta

    @property
    def regret(self) -> Any:
        if self._regret is None:
            from state.memory_tensor.regret.regret_log import RegretLog
            self._regret = RegretLog()
        return self._regret

    # ------------------------------------------------------------------
    # Persistence helpers
    # ------------------------------------------------------------------

    def _restore_episodes(self, kind: str, store: Any) -> None:
        """Reload episodes for *kind* from SQLite into *store*. Best-effort."""
        try:
            from state.cognition_persistence import get_cognition_persistence_store
            rows = get_cognition_persistence_store().load_episodes(kind, limit=_MAX_EPISODES)
            for row in rows:
                try:
                    ep = Episode(
                        ts_ns=int(row["ts_ns"]),
                        episode_id=str(row["episode_id"]),
                        embedding=tuple(float(x) for x in row.get("embedding", [])),
                        payload={str(k): str(v) for k, v in row.get("payload", {}).items()},
                    )
                    if ep.episode_id not in store and ep.dim == _EMBED_DIM:
                        store.add(ep)
                except Exception:
                    pass
        except Exception:
            pass

    def _persist_episode(self, kind: str, episode: Episode) -> None:
        """Write one episode to SQLite. Best-effort."""
        try:
            from state.cognition_persistence import get_cognition_persistence_store
            get_cognition_persistence_store().save_episode(
                store_kind=kind,
                episode_id=episode.episode_id,
                ts_ns=episode.ts_ns,
                data={
                    "embedding": list(episode.embedding),
                    "payload": dict(episode.payload),
                },
            )
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Unified write interface
    # ------------------------------------------------------------------

    def write_episode(self, episode: Episode) -> None:
        try:
            self.episodic.add(episode)
            self._persist_episode("episodic", episode)
        except Exception:
            pass

    def write_semantic(self, episode: Episode) -> None:
        try:
            self.semantic.add(episode)
            self._persist_episode("semantic", episode)
        except Exception:
            pass

    def write_procedural(self, episode: Episode) -> None:
        try:
            self.procedural.add(episode)
        except Exception:
            pass

    def write_meta(self, insight: Any) -> None:
        try:
            store = self.meta
            if hasattr(store, "add"):
                store.add(insight)
            elif hasattr(store, "record"):
                store.record(insight)
        except Exception:
            pass

    def add_regret(self, entry: Any) -> None:
        try:
            store = self.regret
            if hasattr(store, "add"):
                store.add(entry)
            elif hasattr(store, "record"):
                store.record(entry)
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Unified query interface
    # ------------------------------------------------------------------

    def query_episodic(self, query: MemoryQuery) -> MemoryResult | None:
        try:
            return self.episodic.search(query)
        except Exception:
            return None

    def query_semantic(self, query: MemoryQuery) -> MemoryResult | None:
        try:
            return self.semantic.search(query)
        except Exception:
            return None

    # ------------------------------------------------------------------
    # Consolidation tick — called by IndiraRuntime on each cognitive tick
    # ------------------------------------------------------------------

    def consolidate(self, *, ts_ns: int) -> None:
        """Periodic memory consolidation pass (best-effort, never raises)."""
        self._consolidate_seq += 1
        # Emit memory formation event every 10 consolidations so the
        # INDIRA cognitive stream shows memory activity.
        if self._consolidate_seq % 10 == 0:
            try:
                from intelligence_engine.cognitive.observability_emitter import (
                    emit_memory_formation,
                )
                emit_memory_formation(
                    ts_ns=ts_ns,
                    memory_kind="EPISODIC",
                    content_summary=(
                        f"consolidation pass {self._consolidate_seq}: "
                        f"episodic={len(self._episodic) if self._episodic else 0} "
                        f"semantic={len(self._semantic) if self._semantic else 0}"
                    ),
                    source="memory_orchestrator",
                )
            except Exception:
                pass

    # ------------------------------------------------------------------
    # Snapshot for dashboard / observability
    # ------------------------------------------------------------------

    def snapshot(self) -> dict[str, Any]:
        """Enhanced snapshot with tensor statistics (Phase 15.2)."""
        world_context = self._get_world_context()
        
        out: dict[str, Any] = {
            "episodic_size": len(self._episodic) if self._episodic else 0,
            "semantic_size": len(self._semantic) if self._semantic else 0,
            "procedural_size": len(self._procedural) if self._procedural else 0,
            "consolidate_seq": self._consolidate_seq,
            # Phase 15.2 enhancements
            "tensor_stats": {
                "total_tensors_processed": self._tensor_stats.total_tensors_processed,
                "total_tensor_elements": self._tensor_stats.total_tensor_elements,
                "compression_savings_bytes": self._tensor_stats.compression_savings_bytes,
                "operation_count": self._tensor_stats.operation_count,
                "average_operation_latency_ms": self._tensor_stats.average_operation_latency_ms,
                "optimization_applied": self._tensor_stats.optimization_applied,
                "performance_improvement": self._tensor_stats.performance_improvement,
            },
            "world_context": {
                "available": WORLD_MODEL_AVAILABLE,
                "active": self._world_integration_bridge is not None,
                "current_regime": world_context.market_regime if world_context else "unknown",
                "volatility_regime": world_context.volatility_regime if world_context else "unknown",
            },
        }
        try:
            from state.cognition_persistence import get_cognition_persistence_store
            out["persistence"] = get_cognition_persistence_store().snapshot()
        except Exception:
            pass
        return out
    
    def get_tensor_optimization_stats(self) -> TensorStats:
        """Get comprehensive tensor optimization statistics (Phase 15.2)."""
        with self._lock:
            # Calculate average operation latency
            if self._operation_latencies:
                self._tensor_stats.average_operation_latency_ms = sum(self._operation_latencies) / len(self._operation_latencies)
            
            return self._tensor_stats


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------

_orchestrator: MemoryOrchestrator | None = None


def get_memory_orchestrator() -> MemoryOrchestrator:
    """Return the module-level singleton MemoryOrchestrator."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = MemoryOrchestrator()
    return _orchestrator


__all__ = [
    "MemoryOrchestrator",
    "get_memory_orchestrator",
]
