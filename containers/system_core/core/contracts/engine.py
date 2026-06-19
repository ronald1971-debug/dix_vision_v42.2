from __future__ import annotations

from abc import ABC
from collections.abc import Sequence
from dataclasses import dataclass
from enum import StrEnum
from typing import TYPE_CHECKING

from core.contracts.belief_state import Belief, BeliefState

if TYPE_CHECKING:
    from core.contracts.events import SignalEvent
    from core.contracts.market import MarketTick


class HealthState(StrEnum):
    ALIVE = "alive"
    OK = "alive"  # Alias for backward compatibility
    DEGRADED = "degraded"
    HALTED = "halted"
    OFFLINE = "offline"
    FAIL = "fail"  # Alias for DEGRADED, used when check fails


@dataclass(frozen=True, slots=True)
class HealthStatus:
    engine_name: str
    state: HealthState
    detail: str = ""
    plugin_states: dict[str, dict[str, HealthState]] | None = None


class PluginLifecycle(StrEnum):
    PROPOSED = "PROPOSED"
    ACTIVE = "ACTIVE"
    DISABLED = "DISABLED"
    RETIRED = "RETIRED"


@dataclass(slots=True)
class Plugin:
    name: str
    lifecycle: PluginLifecycle
    version: str = ""


# ---------------------------------------------------------------------------
# MicrostructurePlugin — abstract base for microstructure intelligence plugins
# ---------------------------------------------------------------------------


class MicrostructurePlugin(ABC, Plugin):
    """Abstract base for microstructure signal plugins.

    A microstructure plugin transforms a :class:`MarketTick` into zero or more
    :class:`SignalEvent` outputs. Concrete plugins implement ``on_tick`` to
    encode their specific signal logic (order flow imbalance, footprint delta,
    liquidity physics, etc.).
    """

    def on_tick(self, tick: MarketTick) -> Sequence[SignalEvent]:
        """Process a market tick and emit signals.

        Args:
            tick: The market tick to process.

        Returns:
            A sequence of SignalEvents (may be empty).
        """
        ...  # pragma: no cover


class EngineTier(StrEnum):
    RUNTIME = "runtime"
    OFFLINE = "offline"
    COGNITIVE = "cognitive"


class Engine:
    """Base engine contract — aligns with GovernanceEngine / ExecutionEngine
    / IntelligenceEngine / SystemEngine / LearningEngine / EvolutionEngine
    constructor shapes used throughout the harness."""

    name: str

    def engine_name(self) -> str:
        return self.name


class DixVisionEngine(ABC):
    """
    Base contract for all six engines in DIX VISION v42.2.
    Enforces ownership boundaries.
    """

    engine_tier: EngineTier = EngineTier.RUNTIME

    @property
    def engine_name(self) -> str:
        """Return the engine name. Subclasses typically set ``name = \"X\"``
        as a class attribute; this property exposes it through the
        contract interface so callers never reach into ``cls.name``
        directly."""
        return getattr(self, "name", type(self).__name__)

    async def perceive(self, current_belief: BeliefState) -> None:
        """Default no-op perception hook for engines that have no
        perception step yet. Override in subclasses that do."""
        return None

    async def reason(self) -> list[Belief]:
        """Default no-op reasoning hook. Override in subclasses."""
        return []


class RuntimeEngine(DixVisionEngine):
    """Tier marker for runtime engines."""
    pass


class OfflineEngine(DixVisionEngine):
    """Tier marker for offline engines."""
    pass


# Implementation continues for Governance, Execution, and Learning engines...