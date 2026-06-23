"""Dashboard Views – authority views, promotion gates, system health, ledger explorer.

Provides structured views into the various system components for the operator.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from core.types import PromotionStage
from governance.authority_graph import AuthorityGraph
from governance.mcos_kernel import GovernanceKernel
from state.ledger.mcos_event_store import EventStore


@dataclass
class AuthorityView:
    chain: list[str] = field(default_factory=list)
    current_stage: str = ""
    kill_switch_active: bool = False
    policy_count: int = 0


@dataclass
class PromotionView:
    current_stage: str = ""
    stages: list[dict[str, Any]] = field(default_factory=list)
    history: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class LedgerView:
    total_events: int = 0
    stream_counts: dict[str, int] = field(default_factory=dict)
    latest_events: list[dict[str, Any]] = field(default_factory=list)
    chain_valid: bool = False


@dataclass
class SystemHealthView:
    services: list[dict[str, Any]] = field(default_factory=list)
    hazards: list[dict[str, Any]] = field(default_factory=list)
    queues: list[dict[str, Any]] = field(default_factory=list)


class DashboardViewBuilder:
    """Builds structured views for the dashboard."""

    def __init__(
        self,
        governance: GovernanceKernel,
        authority_graph: AuthorityGraph,
        event_store: EventStore,
    ) -> None:
        self._governance = governance
        self._authority = authority_graph
        self._store = event_store

    def build_authority_view(self) -> AuthorityView:
        return AuthorityView(
            chain=self._authority.authority_path(),
            current_stage=self._governance.current_stage.value,
            kill_switch_active=self._governance.is_halted,
            policy_count=len(self._governance._policies),
        )

    def build_promotion_view(self) -> PromotionView:
        stages = [{"name": s.value, "order": i + 1} for i, s in enumerate(PromotionStage)]
        history = [
            {
                "request_id": pr.request_id,
                "target": pr.target_stage.value,
                "status": pr.status.name,
            }
            for pr in self._governance._promotion_history
        ]
        return PromotionView(
            current_stage=self._governance.current_stage.value,
            stages=stages,
            history=history,
        )

    def build_ledger_view(self, latest_count: int = 20) -> LedgerView:
        valid, _ = self._store.verify_integrity()
        latest = self._store.get_latest(latest_count)
        stream_counts: dict[str, int] = {}
        for event in self._store.get_latest(self._store.count):
            stream_counts[event.stream] = stream_counts.get(event.stream, 0) + 1

        return LedgerView(
            total_events=self._store.count,
            stream_counts=stream_counts,
            latest_events=[
                {
                    "event_id": e.event_id,
                    "stream": e.stream,
                    "type": e.event_type,
                    "timestamp": e.timestamp,
                }
                for e in latest
            ],
            chain_valid=valid,
        )
