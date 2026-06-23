"""
DIX VISION v42.2+ Desktop Agent System
Governed interaction layer between Dashboard2026 and the real world
"""

from .activity_tracker import ActivityLevel, ActivityType, DesktopAgentActivityTracker
from .authority_router import ActionType, DesktopAgentAuthorityRouter, PermissionLevel
from .engine import DesktopAgentEngine
from .orchestrator import DesktopAgentOrchestrator
from .session_manager import DesktopAgentSessionManager, Session, SessionType

__version__ = "42.2.0"
__author__ = "DIX VISION Team"

__all__ = [
    "DesktopAgentEngine",
    "DesktopAgentOrchestrator",
    "DesktopAgentAuthorityRouter",
    "DesktopAgentSessionManager",
    "DesktopAgentActivityTracker",
    "PermissionLevel",
    "ActionType",
    "SessionType",
    "Session",
    "ActivityType",
    "ActivityLevel",
]
