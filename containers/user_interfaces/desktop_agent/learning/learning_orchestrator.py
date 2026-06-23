"""
DIX VISION v42.2+ Desktop Agent - Learning Layer Orchestrator
Platform learning system orchestrator - Phase 4 implementation
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, Optional


class LearningOrchestrator:
    """Learning layer orchestrator - coordinates platform learning components."""

    def __init__(self, parent_orchestrator):
        """Initialize the learning orchestrator."""
        self.parent = parent_orchestrator
        self.logger = logging.getLogger("learning_orchestrator")
        self.logger.setLevel(logging.INFO)

        # Learning system components
        self._platform_profiler: Optional[Any] = None
        self._workflow_profiler: Optional[Any] = None
        self._page_mapper: Optional[Any] = None

        # State
        self._initialized = False
        self._running = False

        # Workflow tracking
        self._active_workflows: Dict[str, asyncio.Task] = {}

        # Learning system status
        self._learning_status = {
            "platforms_learned": 0,
            "patterns_learned": 0,
            "pages_mapped": 0,
            "active_learning": False,
            "indira_connected": False,
        }

        self.logger.info("Learning Orchestrator created")

    async def initialize(self) -> bool:
        """Initialize the learning orchestrator."""
        try:
            self.logger.info("Initializing Learning Orchestrator...")

            # Initialize platform profiler
            try:
                import os
                import sys

                learning_dir = os.path.dirname(os.path.abspath(__file__))
                if learning_dir not in sys.path:
                    sys.path.insert(0, learning_dir)

                from platform_profiler import PlatformProfiler

                self._platform_profiler = PlatformProfiler()
                await self._platform_profiler.initialize()
                self.logger.info("Platform Profiler initialized")
            except ImportError as ie:
                self.logger.warning(f"Platform profiler import failed: {ie}")
                self._platform_profiler = None
            except Exception as e:
                self.logger.warning(f"Platform profiler initialization failed: {e}")
                self._platform_profiler = None

            # Initialize workflow profiler
            try:
                from workflow_profiler import WorkflowProfiler

                self._workflow_profiler = WorkflowProfiler()
                await self._workflow_profiler.initialize()
                self.logger.info("Workflow Profiler initialized")
            except ImportError as ie:
                self.logger.warning(f"Workflow profiler import failed: {ie}")
                self._workflow_profiler = None
            except Exception as e:
                self.logger.warning(f"Workflow profiler initialization failed: {e}")
                self._workflow_profiler = None

            # Initialize page mapper
            try:
                from page_mapper import PageMapper

                self._page_mapper = PageMapper()
                await self._page_mapper.initialize()
                self.logger.info("Page Mapper initialized")
            except ImportError as ie:
                self.logger.warning(f"Page mapper import failed: {ie}")
                self._page_mapper = None
            except Exception as e:
                self.logger.warning(f"Page mapper initialization failed: {e}")
                self._page_mapper = None

            self._initialized = True
            self.logger.info("Learning Orchestrator initialized successfully (Phase 4)")
            return True

        except Exception as e:
            self.logger.error(f"Failed to initialize Learning Orchestrator: {e}")
            return False

    async def start(self) -> bool:
        """Start the learning orchestrator."""
        try:
            if not self._initialized:
                await self.initialize()

            self.logger.info("Starting Learning Orchestrator...")

            # Start learning components
            if self._platform_profiler:
                self.logger.info("Platform Profiler ready for learning")

            if self._workflow_profiler:
                self.logger.info("Workflow Profiler ready for analysis")

            if self._page_mapper:
                self.logger.info("Page Mapper ready for mapping")

            self._running = True
            self.logger.info("Learning Orchestrator started successfully (Phase 4)")
            return True

        except Exception as e:
            self.logger.error(f"Failed to start Learning Orchestrator: {e}")
            return False

    async def stop(self) -> bool:
        """Stop the learning orchestrator."""
        try:
            self.logger.info("Stopping Learning Orchestrator...")

            # Stop any active learning sessions
            if self._platform_profiler:
                self._learning_status["active_learning"] = False

            # Cancel active workflows
            for workflow_id, task in self._active_workflows.items():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

            self._active_workflows.clear()
            self._running = False
            self.logger.info("Learning Orchestrator stopped successfully")
            return True

        except Exception as e:
            self.logger.error(f"Failed to stop Learning Orchestrator: {e}")
            return False

    async def execute_workflow(self, workflow: Dict[str, Any]) -> bool:
        """Execute a learning workflow (Phase 4 implementation)."""
        try:
            workflow_id = workflow.get("id", "unknown")

            self.logger.info(f"Executing learning workflow: {workflow_id}")

            # Extract workflow details
            action = workflow.get("action", "")

            if action == "analyze_platform" and self._platform_profiler:
                platform_id = workflow.get("platform_id", "")
                url = workflow.get("url", "")
                if platform_id and url:
                    from platform_profiler import PlatformType

                    platform_type = PlatformType.CUSTOM
                    result = await self._platform_profiler.analyze_platform(
                        platform_id, url, platform_type
                    )
                    if result:
                        self._learning_status["platforms_learned"] += 1

            elif action == "learn_workflow" and self._workflow_profiler:
                workflow_name = workflow.get("workflow_name", "")
                steps = workflow.get("steps", [])
                if workflow_name and steps:
                    from workflow_profiler import WorkflowType

                    result = await self._workflow_profiler.analyze_workflow(
                        workflow_name, WorkflowType.CUSTOM, steps
                    )
                    if result:
                        self._learning_status["patterns_learned"] += 1

            elif action == "map_page" and self._page_mapper:
                page_id = workflow.get("page_id", "")
                url = workflow.get("url", "")
                if page_id and url:
                    result = await self._page_mapper.map_page(page_id, url)
                    if result:
                        self._learning_status["pages_mapped"] += 1

            self.logger.info(f"Learning workflow {workflow_id} completed")
            return True

        except Exception as e:
            self.logger.error(f"Failed to execute learning workflow: {e}")
            return False

    async def start_learning_session(self, platform_id: str) -> bool:
        """Start a learning session for a platform."""
        try:
            if self._platform_profiler:
                result = await self._platform_profiler.start_learning_session(platform_id)
                if result:
                    self._learning_status["active_learning"] = True
                return result
            return False
        except Exception as e:
            self.logger.error(f"Failed to start learning session: {e}")
            return False

    async def stop_learning_session(self, session_id: str) -> bool:
        """Stop a learning session."""
        try:
            if self._platform_profiler:
                result = await self._platform_profiler.stop_learning_session(session_id)
                if result:
                    self._learning_status["active_learning"] = False
                return result
            return False
        except Exception as e:
            self.logger.error(f"Failed to stop learning session: {e}")
            return False

    def get_status(self) -> Dict[str, Any]:
        """Get orchestrator status."""
        return {
            "initialized": self._initialized,
            "running": self._running,
            "phase": "Phase 4 - Platform Learning",
            "learning_status": self._learning_status,
            "active_workflows": len(self._active_workflows),
            "components_available": {
                "platform_profiler": self._platform_profiler is not None,
                "workflow_profiler": self._workflow_profiler is not None,
                "page_mapper": self._page_mapper is not None,
            },
            "component_statuses": {
                "platform_profiler": (
                    self._platform_profiler.get_status() if self._platform_profiler else None
                ),
                "workflow_profiler": (
                    self._workflow_profiler.get_status() if self._workflow_profiler else None
                ),
                "page_mapper": self._page_mapper.get_status() if self._page_mapper else None,
            },
        }

    @property
    def platform_profiler(self) -> Optional[Any]:
        """Get the platform profiler instance."""
        return self._platform_profiler

    @property
    def workflow_profiler(self) -> Optional[Any]:
        """Get the workflow profiler instance."""
        return self._workflow_profiler

    @property
    def page_mapper(self) -> Optional[Any]:
        """Get the page mapper instance."""
        return self._page_mapper

    @property
    def is_running(self) -> bool:
        """Check if orchestrator is running."""
        return self._running
