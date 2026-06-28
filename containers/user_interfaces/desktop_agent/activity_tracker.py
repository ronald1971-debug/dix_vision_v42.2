"""
DIX VISION v42.2+ Desktop Agent - Activity Tracker
Integrates with system component connection manager for activity tracking
"""

from __future__ import annotations

import logging
import sys
import uuid
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))
sys.path.append(str(Path(__file__).parent.parent / "system"))


class ActivityType(Enum):
    """Types of Desktop Agent activities."""

    STARTUP = "STARTUP"
    SHUTDOWN = "SHUTDOWN"
    VOICE_COMMAND = "VOICE_COMMAND"
    BROWSER_NAVIGATION = "BROWSER_NAVIGATION"
    DESKTOP_OPERATION = "DESKTOP_OPERATION"
    DOCUMENT_ACCESS = "DOCUMENT_ACCESS"
    RESEARCH_QUERY = "RESEARCH_QUERY"
    PERMISSION_REQUEST = "PERMISSION_REQUEST"
    SESSION_CREATION = "SESSION_CREATION"
    SESSION_END = "SESSION_END"
    ERROR = "ERROR"
    GOVERNANCE_CHECK = "GOVERNANCE_CHECK"


class ActivityLevel(Enum):
    """Activity severity levels."""

    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class Activity:
    """Desktop Agent activity record."""

    def __init__(
        self,
        activity_type: ActivityType,
        level: ActivityLevel = ActivityLevel.INFO,
        context: Optional[Dict[str, Any]] = None,
    ):
        """Initialize an activity record."""
        self.activity_id = str(uuid.uuid4())
        self.activity_type = activity_type
        self.level = level
        self.timestamp = datetime.now()
        self.context = context or {}
        self.metadata: Dict[str, Any] = {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert activity to dictionary."""
        return {
            "activity_id": self.activity_id,
            "activity_type": self.activity_type.value,
            "level": self.level.value,
            "timestamp": self.timestamp.isoformat(),
            "context": self.context,
            "metadata": self.metadata,
        }


class DesktopAgentActivityTracker:
    """Activity tracker that integrates with system component connection manager."""

    def __init__(self):
        """Initialize the Desktop Agent Activity Tracker."""
        self.logger = logging.getLogger("desktop_agent_activity_tracker")
        self.logger.setLevel(logging.INFO)

        # System integration
        self._component_connection_manager = None
        self._audit_logger = None

        # Activity storage
        self._activities: List[Activity] = []
        self._activity_limit = 10000  # Keep last 10,000 activities

        # State
        self._initialized = False
        self._running = False

        # Statistics
        self._activity_counts: Dict[ActivityType, int] = {}

        self.logger.info("Desktop Agent Activity Tracker initialized")

    async def initialize(self) -> bool:
        """Initialize the activity tracker with system integration."""
        try:
            self.logger.info("Initializing Desktop Agent Activity Tracker...")

            # Initialize system integration
            await self._initialize_system_integration()

            self._initialized = True
            self.logger.info("Desktop Agent Activity Tracker initialized successfully")
            return True

        except Exception as e:
            self.logger.error(f"Failed to initialize Activity Tracker: {e}")
            return False

    async def _initialize_system_integration(self) -> bool:
        """Initialize integration with system components."""
        try:
            # Import component connection manager
            try:
                from system.component_connection_manager import ComponentConnectionManager

                self._component_connection_manager = ComponentConnectionManager()
                self.logger.info("Component connection manager integrated")
            except Exception as e:
                self.logger.warning(f"Failed to integrate component connection manager: {e}")

            # Import audit logger
            try:
                from system.audit_logger import AuditLogger

                self._audit_logger = AuditLogger()
                self.logger.info("Audit logger integrated")
            except Exception as e:
                self.logger.warning(f"Failed to integrate audit logger: {e}")

            return True

        except Exception as e:
            self.logger.error(f"Failed to initialize system integration: {e}")
            return False

    async def start(self) -> bool:
        """Start the activity tracker."""
        try:
            self.logger.info("Starting Desktop Agent Activity Tracker...")

            # Log startup activity
            await self.log_activity(
                ActivityType.STARTUP, ActivityLevel.INFO, {"message": "Desktop Agent started"}
            )

            self._running = True
            self.logger.info("Desktop Agent Activity Tracker started successfully")
            return True

        except Exception as e:
            self.logger.error(f"Failed to start Activity Tracker: {e}")
            return False

    async def stop(self) -> bool:
        """Stop the activity tracker."""
        try:
            self.logger.info("Stopping Desktop Agent Activity Tracker...")

            # Log shutdown activity
            await self.log_activity(
                ActivityType.SHUTDOWN, ActivityLevel.INFO, {"message": "Desktop Agent stopped"}
            )

            self._running = False
            self.logger.info("Desktop Agent Activity Tracker stopped successfully")
            return True

        except Exception as e:
            self.logger.error(f"Failed to stop Activity Tracker: {e}")
            return False

    async def log_activity(
        self,
        activity_type: ActivityType,
        level: ActivityLevel = ActivityLevel.INFO,
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Log an activity."""
        try:
            # Create activity record
            activity = Activity(activity_type, level, context)

            # Store activity
            self._activities.append(activity)

            # Maintain activity limit
            if len(self._activities) > self._activity_limit:
                self._activities.pop(0)

            # Update statistics
            self._activity_counts[activity_type] = self._activity_counts.get(activity_type, 0) + 1

            # Log to system audit logger if available
            if self._audit_logger:
                try:
                    await self._audit_logger.log_activity(activity.to_dict())
                except Exception as e:
                    self.logger.warning(f"Failed to log to audit logger: {e}")

            # Log to component connection manager if available
            if self._component_connection_manager:
                try:
                    await self._component_connection_manager.record_activity(activity.to_dict())
                except Exception as e:
                    self.logger.warning(f"Failed to record to component manager: {e}")

            # Log to local logger
            log_level = self._map_activity_level(level)
            self.logger.log(log_level, f"Activity: {activity_type.value} - {context}")

            return activity.activity_id

        except Exception as e:
            self.logger.error(f"Failed to log activity: {e}")
            return ""

    def _map_activity_level(self, level: ActivityLevel) -> int:
        """Map activity level to logging level."""
        mapping = {
            ActivityLevel.INFO: logging.INFO,
            ActivityLevel.WARNING: logging.WARNING,
            ActivityLevel.ERROR: logging.ERROR,
            ActivityLevel.CRITICAL: logging.CRITICAL,
        }
        return mapping.get(level, logging.INFO)

    async def log_voice_command(self, command: str, result: Optional[str] = None) -> str:
        """Log a voice command activity."""
        context = {
            "command": command,
            "result": result,
        }
        return await self.log_activity(ActivityType.VOICE_COMMAND, ActivityLevel.INFO, context)

    async def log_browser_navigation(self, url: str, action: str) -> str:
        """Log a browser navigation activity."""
        context = {
            "url": url,
            "action": action,
        }
        return await self.log_activity(ActivityType.BROWSER_NAVIGATION, ActivityLevel.INFO, context)

    async def log_permission_request(self, action_type: str, granted: bool) -> str:
        """Log a permission request activity."""
        context = {
            "action_type": action_type,
            "granted": granted,
        }
        level = ActivityLevel.INFO if granted else ActivityLevel.WARNING
        return await self.log_activity(ActivityType.PERMISSION_REQUEST, level, context)

    async def log_error(self, error_message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Log an error activity."""
        error_context = {
            "error": error_message,
        }
        if context:
            error_context.update(context)
        return await self.log_activity(ActivityType.ERROR, ActivityLevel.ERROR, error_context)

    def get_activities(
        self, activity_type: Optional[ActivityType] = None, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get activities, optionally filtered by type."""
        try:
            activities = self._activities

            # Filter by type if specified
            if activity_type:
                activities = [a for a in activities if a.activity_type == activity_type]

            # Convert to dictionaries and limit
            return [a.to_dict() for a in activities[-limit:]]

        except Exception as e:
            self.logger.error(f"Failed to get activities: {e}")
            return []

    def get_activity_count(self, activity_type: Optional[ActivityType] = None) -> int:
        """Get the count of activities, optionally filtered by type."""
        try:
            if activity_type:
                return self._activity_counts.get(activity_type, 0)
            return len(self._activities)
        except Exception as e:
            self.logger.error(f"Failed to get activity count: {e}")
            return 0

    def get_statistics(self) -> Dict[str, Any]:
        """Get activity statistics."""
        return {
            "total_activities": len(self._activities),
            "activity_counts": {k.value: v for k, v in self._activity_counts.items()},
            "activity_limit": self._activity_limit,
        }

    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the activity tracker."""
        return {
            "running": self._running,
            "initialized": self._initialized,
            "total_activities": len(self._activities),
            "activity_limit": self._activity_limit,
            "component_connection_manager_integrated": self._component_connection_manager
            is not None,
            "audit_logger_integrated": self._audit_logger is not None,
            "statistics": self.get_statistics(),
        }
