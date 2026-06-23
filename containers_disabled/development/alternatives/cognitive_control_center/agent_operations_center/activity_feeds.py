"""
cognitive_control_center.agent_operations_center.activity_feeds
Real-time Agent Activity Feeds - First-class component for observing agent cognitive processes.

This module provides real-time activity feeds for INDIRA and DYON, allowing the Operator
to observe agents thinking, learning, and working in real-time. This is a critical missing
component identified in the architectural gap analysis.
"""

from __future__ import annotations

import threading
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import StrEnum
from typing import Any, Callable

from cognitive_control_center.core.operating_environment import (
    CognitiveEntityType,
    get_cognitive_environment,
)


class ActivityType(StrEnum):
    """Types of activities in the activity feed."""

    COGNITIVE_PROCESS = "cognitive_process"
    TOOL_USAGE = "tool_usage"
    MEMORY_ACCESS = "memory_access"
    TASK_UPDATE = "task_update"
    GOAL_CHANGE = "goal_change"
    LEARNING_ACTIVITY = "learning_activity"
    COMMUNICATION = "communication"
    ERROR = "error"


@dataclass
class ActivityFeedEvent:
    """Event in the activity feed."""

    agent_type: CognitiveEntityType
    agent_id: str
    activity_type: ActivityType
    timestamp: datetime
    description: str
    data: dict[str, Any] = field(default_factory=dict)
    severity: str = "info"  # info, warning, error, critical


class AgentActivityFeeds:
    """
    Real-time activity feeds for agent observability.

    Provides continuous streams of agent cognitive processes allowing the Operator
    to observe agents thinking, learning, and working in real-time.
    """

    def __init__(self, feed_capacity: int = 1000) -> None:
        self._lock = threading.RLock()
        self._feed_capacity = feed_capacity
        self._feeds: dict[str, deque[ActivityFeedEvent]] = {}  # agent_id -> feed
        self._subscribers: list[Callable[[ActivityFeedEvent], None]] = []
        self._environment = get_cognitive_environment()

    def ensure_feed_exists(self, agent_id: str) -> None:
        """Ensure an activity feed exists for an agent."""
        with self._lock:
            if agent_id not in self._feeds:
                self._feeds[agent_id] = deque(maxlen=self._feed_capacity)

    def publish_activity(
        self,
        agent_type: CognitiveEntityType,
        agent_id: str,
        activity_type: ActivityType,
        description: str,
        data: dict[str, Any] | None = None,
        severity: str = "info",
    ) -> None:
        """Publish an activity event to the agent's feed."""
        event = ActivityFeedEvent(
            agent_type=agent_type,
            agent_id=agent_id,
            activity_type=activity_type,
            timestamp=datetime.utcnow(),
            description=description,
            data=data or {},
            severity=severity,
        )

        with self._lock:
            self.ensure_feed_exists(agent_id)
            self._feeds[agent_id].append(event)

        # Notify subscribers
        for subscriber in self._subscribers:
            try:
                subscriber(event)
            except Exception:
                pass  # Don't let subscriber errors break the feed

    def get_agent_feed(
        self,
        agent_id: str,
        since: datetime | None = None,
        activity_types: set[ActivityType] | None = None,
        limit: int = 100,
    ) -> list[ActivityFeedEvent]:
        """Get activity feed for a specific agent."""
        with self._lock:
            if agent_id not in self._feeds:
                return []

            feed = self._feeds[agent_id]
            events = list(feed)

            # Filter by time
            if since:
                events = [e for e in events if e.timestamp >= since]

            # Filter by activity type
            if activity_types:
                events = [e for e in events if e.activity_type in activity_types]

            # Limit and return most recent
            return events[-limit:]

    def get_all_feeds(
        self,
        since: datetime | None = None,
        severity: str | None = None,
        limit: int = 100,
    ) -> dict[str, list[ActivityFeedEvent]]:
        """Get activity feeds for all agents."""
        with self._lock:
            result = {}
            for agent_id, feed in self._feeds.items():
                events = list(feed)

                # Filter by time
                if since:
                    events = [e for e in events if e.timestamp >= since]

                # Filter by severity
                if severity:
                    events = [e for e in events if e.severity == severity]

                # Limit and return most recent
                result[agent_id] = events[-limit:]

            return result

    def get_recent_activity(
        self,
        minutes: int = 5,
        limit: int = 50,
    ) -> list[ActivityFeedEvent]:
        """Get recent activity across all agents."""
        since = datetime.utcnow() - timedelta(minutes=minutes)
        all_events = []

        with self._lock:
            for feed in self._feeds.values():
                all_events.extend([e for e in feed if e.timestamp >= since])

        # Sort by timestamp and limit
        all_events.sort(key=lambda e: e.timestamp, reverse=True)
        return all_events[:limit]

    def subscribe_to_feed(self, handler: Callable[[ActivityFeedEvent], None]) -> None:
        """Subscribe to activity feed events."""
        with self._lock:
            self._subscribers.append(handler)

    def get_agent_summary(self, agent_id: str) -> dict[str, Any]:
        """Get summary of an agent's recent activity."""
        with self._lock:
            if agent_id not in self._feeds:
                return {
                    "agent_id": agent_id,
                    "status": "inactive",
                    "last_activity": None,
                    "activity_count": 0,
                    "recent_errors": 0,
                }

            feed = self._feeds[agent_id]
            if not feed:
                return {
                    "agent_id": agent_id,
                    "status": "idle",
                    "last_activity": None,
                    "activity_count": 0,
                    "recent_errors": 0,
                }

            recent_events = [
                e for e in feed if e.timestamp >= datetime.utcnow() - timedelta(minutes=5)
            ]
            error_count = len([e for e in recent_events if e.severity in ["error", "critical"]])

            return {
                "agent_id": agent_id,
                "status": "active" if recent_events else "idle",
                "last_activity": feed[-1].timestamp if feed else None,
                "activity_count": len(recent_events),
                "recent_errors": error_count,
                "current_activity": feed[-1].description if feed else None,
            }


_activity_feeds: AgentActivityFeeds | None = None
_feeds_lock = threading.Lock()


def get_activity_feeds() -> AgentActivityFeeds:
    """Get the singleton agent activity feeds."""
    global _activity_feeds
    if _activity_feeds is None:
        with _feeds_lock:
            if _activity_feeds is None:
                _activity_feeds = AgentActivityFeeds()
    return _activity_feeds
