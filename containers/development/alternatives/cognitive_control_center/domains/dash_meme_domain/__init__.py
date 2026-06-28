"""
cognitive_control_center/domains/dash_meme_domain
DashMeme Domain Integration - Memecoin trading as integrated domain within cognitive control center

This module provides the integration of the dash_meme application as a domain
within the unified cognitive control center, rather than as a separate application.

PRESERVED FEATURES from dash_meme/:
- 8 memecoin-specific pages (Sniper, BigSwap, CopyTrading, etc.)
- 3 unique components (HoldersPanel, HotPairsTicker, RugScoreCard)
- All trading functionality
- Token sniping capabilities
- Pool and pair exploration
- Copy trading interface

INTEGRATION STRATEGY:
- DashMeme becomes a domain within cognitive_control_center/domains/dash_meme_domain/
- Uses unified workspace model
- Integrates with agent operations center
- Shares cognitive environment infrastructure
- Preserves all memecoin-specific functionality
"""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any

from cognitive_control_center.core.operating_environment import (
    get_cognitive_environment,
)
from cognitive_control_center.core.workspace_manager import (
    WorkspaceType,
    get_workspace_manager,
)


class MemecoinDomainFeature(StrEnum):
    """Types of memecoin domain features."""

    TOKEN_SNIIPING = "token_sniping"
    BIG_SWAP_DETECTION = "big_swap_detection"
    COPY_TRADING = "copy_trading"
    POOL_EXPLORATION = "pool_exploration"
    PAIR_EXPLORATION = "pair_exploration"
    HOLDER_ANALYSIS = "holder_analysis"
    RUG_SCORE_CALCULATION = "rug_score_calculation"
    MULTI_SWAP_ROUTING = "multi_swap_routing"


@dataclass
class MemecoinActivity:
    """Activity specific to memecoin domain."""

    activity_type: MemecoinDomainFeature
    token_address: str
    timestamp: datetime
    data: dict[str, Any] = field(default_factory=dict)
    value_usd: float = 0.0


@dataclass
class MemecoinTradingSession:
    """Active memecoin trading session."""

    session_id: str
    operator_id: str
    token_address: str
    start_time: datetime
    current_position_usd: float = 0.0
    pnl_usd: float = 0.0
    status: str = "active"
    activities: list[MemecoinActivity] = field(default_factory=list)


class DashMemeDomain:
    """
    DashMeme domain integrated into cognitive control center.

    Provides memecoin-specific functionality as an integrated domain,
    preserving all dash_meme/ features while leveraging cognitive environment infrastructure.
    """

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._environment = get_cognitive_environment()
        self._workspace_manager = get_workspace_manager()
        self._active_sessions: dict[str, MemecoinTradingSession] = {}
        self._activity_feed: list[MemecoinActivity] = []

    def initialize_domain(self) -> None:
        """Initialize the memecoin domain in the cognitive environment."""
        # Register memecoin as a specialized workspace
        self._workspace_manager.activate_workspace(
            WorkspaceType.MEMECOIN_DOMAIN,
            {
                "name": "Memecoin Trading Domain",
                "description": "Specialized memecoin trading with advanced tools",
                "shared_tools": [
                    "dex_analysis",
                    "token_sniping",
                    "liquidity_analysis",
                    "holder_tracking",
                    "rug_detection",
                ],
            },
        )

    def start_trading_session(
        self,
        operator_id: str,
        token_address: str,
        initial_position_usd: float = 0.0,
    ) -> MemecoinTradingSession:
        """Start a new memecoin trading session."""
        import uuid

        session_id = uuid.uuid4().hex
        session = MemecoinTradingSession(
            session_id=session_id,
            operator_id=operator_id,
            token_address=token_address,
            start_time=datetime.utcnow(),
            current_position_usd=initial_position_usd,
        )

        with self._lock:
            self._active_sessions[session_id] = session

        # Transition operator to memecoin workspace
        self._workspace_manager.transition_entity(
            operator_id,
            WorkspaceType.MEMECOIN_DOMAIN,
            reason=f"Started memecoin trading session for {token_address}",
        )

        return session

    def record_activity(self, activity: MemecoinActivity) -> None:
        """Record memecoin domain activity."""
        with self._lock:
            self._activity_feed.append(activity)
            # Keep last 1000 activities
            if len(self._activity_feed) > 1000:
                self._activity_feed = self._activity_feed[-1000:]

            # Add to session if applicable
            for session in self._active_sessions.values():
                if session.token_address == activity.token_address:
                    session.activities.append(activity)
                    break

    def get_active_sessions(self) -> list[MemecoinTradingSession]:
        """Get all active memecoin trading sessions."""
        with self._lock:
            return list(self._active_sessions.values())

    def get_recent_activities(
        self,
        token_address: str | None = None,
        limit: int = 50,
    ) -> list[MemecoinActivity]:
        """Get recent memecoin activities."""
        with self._lock:
            activities = self._activity_feed

            if token_address:
                activities = [a for a in activities if a.token_address == token_address]

            return list(activities[-limit:])

    def end_session(self, session_id: str) -> bool:
        """End a memecoin trading session."""
        with self._lock:
            if session_id not in self._active_sessions:
                return False

            session = self._active_sessions[session_id]
            session.status = "completed"

            # Remove from active sessions
            del self._active_sessions[session_id]
            return True

    def get_domain_status(self) -> dict[str, Any]:
        """Get memecoin domain status."""
        with self._lock:
            return {
                "active_sessions": len(self._active_sessions),
                "recent_activities": len(self._activity_feed),
                "total_value_usd": sum(
                    s.current_position_usd for s in self._active_sessions.values()
                ),
                "total_pnl_usd": sum(s.pnl_usd for s in self._active_sessions.values()),
            }


_dashmeme_domain: DashMemeDomain | None = None
_domain_lock = threading.Lock()


def get_dashmeme_domain() -> DashMemeDomain:
    """Get the singleton DashMeme domain instance."""
    global _dashmeme_domain
    if _dashmeme_domain is None:
        with _domain_lock:
            if _dashmeme_domain is None:
                _dashmeme_domain = DashMemeDomain()
    return _dashmeme_domain
