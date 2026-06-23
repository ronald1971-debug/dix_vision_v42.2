"""
DIX VISION v42.2+ Desktop Agent - Notifications Layer Orchestrator
Notifications system orchestrator - Phase 8 implementation
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, Optional


class NotificationsOrchestrator:
    """Notifications layer orchestrator - coordinates notifications components."""

    def __init__(self, parent_orchestrator):
        """Initialize the notifications orchestrator."""
        self.parent = parent_orchestrator
        self.logger = logging.getLogger("notifications_orchestrator")
        self.logger.setLevel(logging.INFO)

        # Notifications components
        self._notification_manager: Optional[Any] = None
        self._alert_system: Optional[Any] = None
        self._notification_router: Optional[Any] = None

        # State
        self._initialized = False
        self._running = False

        # Workflow tracking
        self._active_workflows: Dict[str, asyncio.Task] = {}

        # Notifications status
        self._notifications_status = {
            "notifications_created": 0,
            "alerts_created": 0,
            "routes_created": 0,
            "active_notifications": 0,
        }

        self.logger.info("Notifications Orchestrator created")

    async def initialize(self) -> bool:
        """Initialize the notifications orchestrator."""
        try:
            self.logger.info("Initializing Notifications Orchestrator...")

            # Initialize notification manager
            try:
                import os
                import sys

                notifications_dir = os.path.dirname(os.path.abspath(__file__))
                if notifications_dir not in sys.path:
                    sys.path.insert(0, notifications_dir)

                from notification_manager import NotificationManager

                self._notification_manager = NotificationManager()
                await self._notification_manager.initialize()
                self.logger.info("Notification Manager initialized")
            except ImportError as ie:
                self.logger.warning(f"Notification manager import failed: {ie}")
                self._notification_manager = None
            except Exception as e:
                self.logger.warning(f"Notification manager initialization failed: {e}")
                self._notification_manager = None

            # Initialize alert system
            try:
                from alert_system import AlertSystem

                self._alert_system = AlertSystem()
                await self._alert_system.initialize()
                self.logger.info("Alert System initialized")
            except ImportError as ie:
                self.logger.warning(f"Alert system import failed: {ie}")
                self._alert_system = None
            except Exception as e:
                self.logger.warning(f"Alert system initialization failed: {e}")
                self._alert_system = None

            # Initialize notification router
            try:
                from notification_router import NotificationRouter

                self._notification_router = NotificationRouter()
                await self._notification_router.initialize()
                self.logger.info("Notification Router initialized")
            except ImportError as ie:
                self.logger.warning(f"Notification router import failed: {ie}")
                self._notification_router = None
            except Exception as e:
                self.logger.warning(f"Notification router initialization failed: {e}")
                self._notification_router = None

            self._initialized = True
            self.logger.info("Notifications Orchestrator initialized successfully (Phase 8)")
            return True

        except Exception as e:
            self.logger.error(f"Failed to initialize Notifications Orchestrator: {e}")
            return False

    async def start(self) -> bool:
        """Start the notifications orchestrator."""
        try:
            if not self._initialized:
                await self.initialize()

            self.logger.info("Starting Notifications Orchestrator...")

            # Start notifications components
            if self._notification_manager:
                self.logger.info("Notification Manager ready")

            if self._alert_system:
                self.logger.info("Alert System ready")

            if self._notification_router:
                self.logger.info("Notification Router ready")

            self._running = True
            self.logger.info("Notifications Orchestrator started successfully (Phase 8)")
            return True

        except Exception as e:
            self.logger.error(f"Failed to start Notifications Orchestrator: {e}")
            return False

    async def stop(self) -> bool:
        """Stop the notifications orchestrator."""
        try:
            self.logger.info("Stopping Notifications Orchestrator...")

            # Cancel active workflows
            for workflow_id, task in self._active_workflows.items():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

            self._active_workflows.clear()
            self._running = False
            self.logger.info("Notifications Orchestrator stopped successfully")
            return True

        except Exception as e:
            self.logger.error(f"Failed to stop Notifications Orchestrator: {e}")
            return False

    async def execute_workflow(self, workflow: Dict[str, Any]) -> bool:
        """Execute a notifications workflow (Phase 8 implementation)."""
        try:
            workflow_id = workflow.get("id", "unknown")

            self.logger.info(f"Executing notifications workflow: {workflow_id}")

            # Extract workflow details
            action = workflow.get("action", "")

            if action == "create_notification" and self._notification_manager:
                notification_id = workflow.get("notification_id", "")
                title = workflow.get("title", "")
                message = workflow.get("message", "")
                if notification_id and title and message:
                    from notification_manager import NotificationPriority, NotificationType

                    result = await self._notification_manager.create_notification(
                        notification_id,
                        NotificationType.INFO,
                        title,
                        message,
                        NotificationPriority.MEDIUM,
                    )
                    if result:
                        self._notifications_status["notifications_created"] += 1

            elif action == "send_notification" and self._notification_manager:
                notification_id = workflow.get("notification_id", "")
                if notification_id:
                    success = await self._notification_manager.send_notification(notification_id)
                    if success:
                        self._notifications_status["active_notifications"] -= 1

            elif action == "create_alert" and self._alert_system:
                alert_id = workflow.get("alert_id", "")
                name = workflow.get("name", "")
                if alert_id and name:
                    from alert_system import AlertCondition, AlertSeverity

                    result = await self._alert_system.create_alert(
                        alert_id, name, AlertSeverity.WARNING, AlertCondition.THRESHOLD
                    )
                    if result:
                        self._notifications_status["alerts_created"] += 1

            elif action == "add_route" and self._notification_router:
                route_id = workflow.get("route_id", "")
                if route_id:
                    from notification_router import NotificationChannel, NotificationPriority

                    result = await self._notification_router.add_route(
                        route_id, NotificationChannel.EMAIL, NotificationPriority.MEDIUM, {}
                    )
                    if result:
                        self._notifications_status["routes_created"] += 1

            self.logger.info(f"Notifications workflow {workflow_id} completed")
            return True

        except Exception as e:
            self.logger.error(f"Failed to execute notifications workflow: {e}")
            return False

    def get_status(self) -> Dict[str, Any]:
        """Get orchestrator status."""
        return {
            "initialized": self._initialized,
            "running": self._running,
            "phase": "Phase 8 - Notifications",
            "notifications_status": self._notifications_status,
            "active_workflows": len(self._active_workflows),
            "components_available": {
                "notification_manager": self._notification_manager is not None,
                "alert_system": self._alert_system is not None,
                "notification_router": self._notification_router is not None,
            },
            "component_statuses": {
                "notification_manager": (
                    self._notification_manager.get_status() if self._notification_manager else None
                ),
                "alert_system": self._alert_system.get_status() if self._alert_system else None,
                "notification_router": (
                    self._notification_router.get_status() if self._notification_router else None
                ),
            },
        }

    @property
    def notification_manager(self) -> Optional[Any]:
        """Get the notification manager instance."""
        return self._notification_manager

    @property
    def alert_system(self) -> Optional[Any]:
        """Get the alert system instance."""
        return self._alert_system

    @property
    def notification_router(self) -> Optional[Any]:
        """Get the notification router instance."""
        return self._notification_router

    @property
    def is_running(self) -> bool:
        """Check if orchestrator is running."""
        return self._running
