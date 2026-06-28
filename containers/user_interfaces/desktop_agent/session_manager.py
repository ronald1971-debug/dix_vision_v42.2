"""
DIX VISION v42.2+ Desktop Agent - Session Manager
Integrates with coordination layer for session management and operator handoff
"""

from __future__ import annotations

import asyncio
import logging
import sys
import uuid
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))
sys.path.append(str(Path(__file__).parent.parent / "coordination_layer"))


class SessionType(Enum):
    """Types of Desktop Agent sessions."""

    VOICE_INTERACTION = "VOICE_INTERACTION"
    BROWSER_AUTOMATION = "BROWSER_AUTOMATION"
    DESKTOP_CONTROL = "DESKTOP_CONTROL"
    RESEARCH_SESSION = "RESEARCH_SESSION"
    TRADING_ASSISTANCE = "TRADING_ASSISTANCE"
    DOCUMENT_PROCESSING = "DOCUMENT_PROCESSING"


class Session:
    """Desktop Agent session."""

    def __init__(self, session_type: SessionType, operator: Optional[str] = None):
        """Initialize a session."""
        self.session_id = str(uuid.uuid4())
        self.session_type = session_type
        self.operator = operator or "system"
        self.created_at = datetime.now()
        self.last_activity = datetime.now()
        self.status = "active"
        self.context: Dict[str, Any] = {}
        self.metadata: Dict[str, Any] = {}

    def update_activity(self) -> None:
        """Update the last activity timestamp."""
        self.last_activity = datetime.now()

    def is_expired(self, timeout_minutes: int = 30) -> bool:
        """Check if the session has expired."""
        timeout = timedelta(minutes=timeout_minutes)
        return datetime.now() - self.last_activity > timeout

    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary."""
        return {
            "session_id": self.session_id,
            "session_type": self.session_type.value,
            "operator": self.operator,
            "created_at": self.created_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "status": self.status,
            "context": self.context,
            "metadata": self.metadata,
        }


class DesktopAgentSessionManager:
    """Session manager that integrates with coordination layer."""

    def __init__(self):
        """Initialize the Desktop Agent Session Manager."""
        self.logger = logging.getLogger("desktop_agent_session_manager")
        self.logger.setLevel(logging.INFO)

        # Coordination layer integration
        self._cognitive_economy = None
        self._operating_modes = None

        # Session management
        self._active_sessions: Dict[str, Session] = {}
        self._session_history: list = []

        # State
        self._initialized = False
        self._running = False

        # Configuration
        self._session_timeout_minutes = 30
        self._max_sessions = 100

        self.logger.info("Desktop Agent Session Manager initialized")

    async def initialize(self) -> bool:
        """Initialize the session manager with coordination layer."""
        try:
            self.logger.info("Initializing Desktop Agent Session Manager...")

            # Initialize coordination layer integration
            await self._initialize_coordination_integration()

            self._initialized = True
            self.logger.info("Desktop Agent Session Manager initialized successfully")
            return True

        except Exception as e:
            self.logger.error(f"Failed to initialize Session Manager: {e}")
            return False

    async def _initialize_coordination_integration(self) -> bool:
        """Initialize integration with coordination layer."""
        try:
            # Import cognitive economy
            try:
                from coordination_layer.cognitive_economy import CognitiveEconomy

                self._cognitive_economy = CognitiveEconomy()
                self.logger.info("Cognitive economy integrated")
            except Exception as e:
                self.logger.warning(f"Failed to integrate cognitive economy: {e}")

            # Import operating modes
            try:
                from coordination_layer.operating_modes import OperatingModes

                self._operating_modes = OperatingModes()
                self.logger.info("Operating modes integrated")
            except Exception as e:
                self.logger.warning(f"Failed to integrate operating modes: {e}")

            return True

        except Exception as e:
            self.logger.error(f"Failed to initialize coordination integration: {e}")
            return False

    async def start(self) -> bool:
        """Start the session manager."""
        try:
            self.logger.info("Starting Desktop Agent Session Manager...")

            # Start session cleanup task
            asyncio.create_task(self._session_cleanup_task())

            self._running = True
            self.logger.info("Desktop Agent Session Manager started successfully")
            return True

        except Exception as e:
            self.logger.error(f"Failed to start Session Manager: {e}")
            return False

    async def stop(self) -> bool:
        """Stop the session manager."""
        try:
            self.logger.info("Stopping Desktop Agent Session Manager...")

            # End all active sessions
            for session_id in list(self._active_sessions.keys()):
                await self.end_session(session_id)

            self._running = False
            self.logger.info("Desktop Agent Session Manager stopped successfully")
            return True

        except Exception as e:
            self.logger.error(f"Failed to stop Session Manager: {e}")
            return False

    async def create_session(
        self,
        session_type: SessionType,
        operator: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> Optional[Session]:
        """Create a new session."""
        try:
            # Check session limit
            if len(self._active_sessions) >= self._max_sessions:
                self.logger.warning("Maximum session limit reached")
                await self._cleanup_expired_sessions()
                if len(self._active_sessions) >= self._max_sessions:
                    return None

            # Create session
            session = Session(session_type, operator)
            if context:
                session.context.update(context)

            # Store session
            self._active_sessions[session.session_id] = session

            self.logger.info(f"Created session {session.session_id} of type {session_type.value}")
            return session

        except Exception as e:
            self.logger.error(f"Failed to create session: {e}")
            return None

    async def get_session(self, session_id: str) -> Optional[Session]:
        """Get a session by ID."""
        try:
            session = self._active_sessions.get(session_id)
            if session:
                session.update_activity()
            return session
        except Exception as e:
            self.logger.error(f"Failed to get session: {e}")
            return None

    async def update_session_context(self, session_id: str, context: Dict[str, Any]) -> bool:
        """Update session context."""
        try:
            session = self._active_sessions.get(session_id)
            if session:
                session.context.update(context)
                session.update_activity()
                return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to update session context: {e}")
            return False

    async def end_session(self, session_id: str) -> bool:
        """End a session."""
        try:
            session = self._active_sessions.get(session_id)
            if session:
                session.status = "ended"
                session.last_activity = datetime.now()

                # Move to history
                self._session_history.append(session.to_dict())

                # Remove from active sessions
                del self._active_sessions[session_id]

                self.logger.info(f"Ended session {session_id}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to end session: {e}")
            return False

    async def operator_handoff(self, session_id: str, new_operator: str) -> bool:
        """Hand off a session to a new operator."""
        try:
            session = self._active_sessions.get(session_id)
            if session:
                session.operator = new_operator
                session.update_activity()
                self.logger.info(f"Session {session_id} handed off to {new_operator}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to hand off session: {e}")
            return False

    async def _session_cleanup_task(self) -> None:
        """Background task to clean up expired sessions."""
        while self._running:
            try:
                await asyncio.sleep(60)  # Check every minute
                await self._cleanup_expired_sessions()
            except Exception as e:
                self.logger.error(f"Error in session cleanup task: {e}")

    async def _cleanup_expired_sessions(self) -> None:
        """Clean up expired sessions."""
        try:
            expired_sessions = [
                session_id
                for session_id, session in self._active_sessions.items()
                if session.is_expired(self._session_timeout_minutes)
            ]

            for session_id in expired_sessions:
                await self.end_session(session_id)

            if expired_sessions:
                self.logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")

        except Exception as e:
            self.logger.error(f"Error cleaning up expired sessions: {e}")

    def get_active_sessions(self) -> list:
        """Get all active sessions."""
        return [session.to_dict() for session in self._active_sessions.values()]

    def get_session_count(self) -> int:
        """Get the number of active sessions."""
        return len(self._active_sessions)

    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the session manager."""
        return {
            "running": self._running,
            "initialized": self._initialized,
            "active_sessions": self.get_session_count(),
            "session_timeout_minutes": self._session_timeout_minutes,
            "max_sessions": self._max_sessions,
            "cognitive_economy_integrated": self._cognitive_economy is not None,
            "operating_modes_integrated": self._operating_modes is not None,
        }
