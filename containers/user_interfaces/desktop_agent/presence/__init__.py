"""
Presence layer - Phase 9 implementation
"""

from activity_monitor import ActivityEvent, ActivityLevel, ActivityMonitor, ActivityType
from presence_detector import PresenceDetector, PresenceEvent, PresenceSource, PresenceState
from user_tracker import UserProfile, UserSession, UserStatus, UserTracker

__all__ = [
    "PresenceDetector",
    "PresenceState",
    "PresenceSource",
    "PresenceEvent",
    "UserTracker",
    "UserStatus",
    "UserProfile",
    "UserSession",
    "ActivityMonitor",
    "ActivityType",
    "ActivityLevel",
    "ActivityEvent",
]
