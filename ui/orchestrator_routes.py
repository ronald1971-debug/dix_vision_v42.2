"""DIX v42.2 — operator UI introspection for the agent orchestrator.

Adds three FastAPI endpoints under ``/api/cognitive/orchestrator``:

  * ``GET /api/cognitive/orchestrator/state`` — orchestrator snapshot
  * ``GET /api/cognitive/orchestrator/agents``  — registered agents
  * ``GET /api/cognitive/orchestrator/recent``  — recent fused signals

Usage:
    uvicorn ui.server:app --reload --port 8080
    # then browse to:
    #   http://localhost:8080/api/cognitive/orchestrator/state
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from fastapi import APIRouter


def build_orchestrator_router(
    state_accessor: Callable[[], Any],
) -> APIRouter:
    """Construct the agent-orchestrator introspection router.

    Args:
        state_accessor: Callable returning the live harness ``_State``
            object.  The router reads the ``IntelligenceEngine`` and
            its ``AgentOrchestrator`` from the accessor; it never
            imports ``ui.server`` directly.
    """
    router = APIRouter(prefix="/api/cognitive/orchestrator", tags=["cognitive-orchestrator"])

    @router.get("/state")
    def orchestrator_state() -> dict[str, Any]:
        state = state_accessor()
        try:
            engine = state.intelligence_engine  # type: ignore[attr-defined]
        except AttributeError:
            return {"error": "intelligence_engine not available on state accessor"}
        orch = getattr(engine, "agent_orchestrator", None)
        if orch is None:
            return {"error": "agent_orchestrator not wired into intelligence engine"}
        return orch.snapshot()

    @router.get("/agents")
    def orchestrator_agents() -> dict[str, Any]:
        state = state_accessor()
        try:
            engine = state.intelligence_engine  # type: ignore[attr-defined]
        except AttributeError:
            return {"agents": []}
        orch = getattr(engine, "agent_orchestrator", None)
        if orch is None:
            return {"agents": []}
        return {
            "agents": [
                {"agent_id": aid, "pool": getattr(orch, "_last_regime", "default")}
                for aid in orch.agent_ids
            ]
        }

    @router.get("/recent")
    def orchestrator_recent(limit: int = 10) -> dict[str, Any]:
        state = state_accessor()
        try:
            engine = state.intelligence_engine  # type: ignore[attr-defined]
        except AttributeError:
            return {"signals": []}
        orch = getattr(engine, "agent_orchestrator", None)
        if orch is None:
            return {"signals": []}
        recents = orch.recent(limit)
        return {
            "signals": [
                {
                    "ts_ns": s.ts_ns,
                    "symbol": s.symbol,
                    "side": s.side.value,
                    "confidence": round(s.confidence, 4),
                    "participating_agents": s.participating_agents,
                    "conflict_resolution": s.conflict_resolution,
                    "pool_name": s.pool_name,
                }
                for s in recents
            ]
        }

    return router


__all__ = ["build_orchestrator_router"]
