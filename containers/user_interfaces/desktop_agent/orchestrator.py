"""
DIX VISION v42.2+ Desktop Agent - Orchestrator
Orchestrates all Desktop Agent components and manages workflow
"""

from __future__ import annotations

import asyncio
import logging
import sys
from pathlib import Path
from typing import Any, Dict, Optional

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))
sys.path.append(str(Path(__file__).parent.parent / "governance"))
sys.path.append(str(Path(__file__).parent.parent / "coordination_layer"))


class DesktopAgentOrchestrator:
    """Orchestrates all Desktop Agent components and manages workflow."""

    def __init__(self, engine):
        """Initialize the Desktop Agent Orchestrator."""
        self.engine = engine
        self.logger = logging.getLogger("desktop_agent_orchestrator")
        self.logger.setLevel(logging.INFO)

        # Layer orchestrators
        self._layer_orchestrators: Dict[str, Any] = {}

        # Active tasks
        self._active_tasks: Dict[str, asyncio.Task] = {}

        # State
        self._running = False
        self._initialized = False

        # Workflow queue
        self._workflow_queue: asyncio.Queue = asyncio.Queue()

        self.logger.info("Desktop Agent Orchestrator initialized")

    async def initialize(self) -> bool:
        """Initialize the orchestrator and all layer orchestrators."""
        try:
            self.logger.info("Initializing Desktop Agent Orchestrator...")

            # Initialize layer orchestrators
            await self._initialize_layer_orchestrators()

            self._initialized = True
            self.logger.info("Desktop Agent Orchestrator initialized successfully")
            return True

        except Exception as e:
            self.logger.error(f"Failed to initialize Orchestrator: {e}")
            return False

    async def _initialize_layer_orchestrators(self) -> bool:
        """Initialize orchestrators for each Desktop Agent layer."""
        try:
            # Voice layer orchestrator
            try:
                import os
                import sys

                voice_dir = os.path.join(os.path.dirname(__file__), "voice")
                if voice_dir not in sys.path:
                    sys.path.insert(0, voice_dir)
                from voice_orchestrator import VoiceOrchestrator

                self._layer_orchestrators["voice"] = VoiceOrchestrator(self)
                await self._layer_orchestrators["voice"].initialize()
                self.logger.info("Voice layer orchestrator initialized")
            except Exception as e:
                self.logger.warning(f"Voice layer orchestrator initialization failed: {e}")

            # Browser layer orchestrator
            try:
                import os
                import sys

                browser_dir = os.path.join(os.path.dirname(__file__), "browser")
                if browser_dir not in sys.path:
                    sys.path.insert(0, browser_dir)
                from browser_orchestrator import BrowserOrchestrator

                self._layer_orchestrators["browser"] = BrowserOrchestrator(self)
                await self._layer_orchestrators["browser"].initialize()
                self.logger.info("Browser layer orchestrator initialized")
            except Exception as e:
                self.logger.warning(f"Browser layer orchestrator initialization failed: {e}")

            # Desktop layer orchestrator
            try:
                import os
                import sys

                desktop_dir = os.path.join(os.path.dirname(__file__), "desktop")
                if desktop_dir not in sys.path:
                    sys.path.insert(0, desktop_dir)
                from desktop_orchestrator import DesktopOrchestrator

                self._layer_orchestrators["desktop"] = DesktopOrchestrator(self)
                await self._layer_orchestrators["desktop"].initialize()
                self.logger.info("Desktop layer orchestrator initialized")
            except Exception as e:
                self.logger.warning(f"Desktop layer orchestrator initialization failed: {e}")

            # Learning layer orchestrator
            try:
                import os
                import sys

                learning_dir = os.path.join(os.path.dirname(__file__), "learning")
                if learning_dir not in sys.path:
                    sys.path.insert(0, learning_dir)
                from learning_orchestrator import LearningOrchestrator

                self._layer_orchestrators["learning"] = LearningOrchestrator(self)
                await self._layer_orchestrators["learning"].initialize()
                self.logger.info("Learning layer orchestrator initialized")
            except Exception as e:
                self.logger.warning(f"Learning layer orchestrator initialization failed: {e}")

            # Documents layer orchestrator
            try:
                import os
                import sys

                documents_dir = os.path.join(os.path.dirname(__file__), "documents")
                if documents_dir not in sys.path:
                    sys.path.insert(0, documents_dir)
                from documents_orchestrator import DocumentsOrchestrator

                self._layer_orchestrators["documents"] = DocumentsOrchestrator(self)
                await self._layer_orchestrators["documents"].initialize()
                self.logger.info("Documents layer orchestrator initialized")
            except Exception as e:
                self.logger.warning(f"Documents layer orchestrator initialization failed: {e}")

            # Research layer orchestrator
            try:
                import os
                import sys

                research_dir = os.path.join(os.path.dirname(__file__), "research")
                if research_dir not in sys.path:
                    sys.path.insert(0, research_dir)
                from research_orchestrator import ResearchOrchestrator

                self._layer_orchestrators["research"] = ResearchOrchestrator(self)
                await self._layer_orchestrators["research"].initialize()
                self.logger.info("Research layer orchestrator initialized")
            except Exception as e:
                self.logger.warning(f"Research layer orchestrator initialization failed: {e}")

            # Notifications layer orchestrator
            try:
                import os
                import sys

                notifications_dir = os.path.join(os.path.dirname(__file__), "notifications")
                if notifications_dir not in sys.path:
                    sys.path.insert(0, notifications_dir)
                from notifications_orchestrator import NotificationsOrchestrator

                self._layer_orchestrators["notifications"] = NotificationsOrchestrator(self)
                await self._layer_orchestrators["notifications"].initialize()
                self.logger.info("Notifications layer orchestrator initialized")
            except Exception as e:
                self.logger.warning(f"Notifications layer orchestrator initialization failed: {e}")

            # Presence layer orchestrator (Phase 9)
            try:
                import os
                import sys

                presence_dir = os.path.join(os.path.dirname(__file__), "presence")
                if presence_dir not in sys.path:
                    sys.path.insert(0, presence_dir)
                from presence_orchestrator import PresenceOrchestrator

                self._layer_orchestrators["presence"] = PresenceOrchestrator(self)
                await self._layer_orchestrators["presence"].initialize()
                self.logger.info("Presence layer orchestrator initialized")
            except Exception as e:
                self.logger.warning(f"Presence layer orchestrator initialization failed: {e}")

            # Automation layer orchestrator (Phase 9)
            try:
                import os
                import sys

                automation_dir = os.path.join(os.path.dirname(__file__), "automation")
                if automation_dir not in sys.path:
                    sys.path.insert(0, automation_dir)
                from automation_orchestrator import AutomationOrchestrator

                self._layer_orchestrators["automation"] = AutomationOrchestrator(self)
                await self._layer_orchestrators["automation"].initialize()
                self.logger.info("Automation layer orchestrator initialized")
            except Exception as e:
                self.logger.warning(f"Automation layer orchestrator initialization failed: {e}")

            # Security layer orchestrator (Phase 9)
            try:
                import os
                import sys

                security_dir = os.path.join(os.path.dirname(__file__), "security")
                if security_dir not in sys.path:
                    sys.path.insert(0, security_dir)
                from security_orchestrator import SecurityOrchestrator

                self._layer_orchestrators["security"] = SecurityOrchestrator(self)
                await self._layer_orchestrators["security"].initialize()
                self.logger.info("Security layer orchestrator initialized")
            except Exception as e:
                self.logger.warning(f"Security layer orchestrator initialization failed: {e}")

            # Memory layer orchestrator (Phase 9)
            try:
                import os
                import sys

                memory_dir = os.path.join(os.path.dirname(__file__), "memory")
                if memory_dir not in sys.path:
                    sys.path.insert(0, memory_dir)
                from memory_orchestrator import MemoryOrchestrator

                self._layer_orchestrators["memory"] = MemoryOrchestrator(self)
                await self._layer_orchestrators["memory"].initialize()
                self.logger.info("Memory layer orchestrator initialized")
            except Exception as e:
                self.logger.warning(f"Memory layer orchestrator initialization failed: {e}")

            # Integrations layer orchestrator (Phase 9)
            try:
                import os
                import sys

                integrations_dir = os.path.join(os.path.dirname(__file__), "integrations")
                if integrations_dir not in sys.path:
                    sys.path.insert(0, integrations_dir)
                from integrations_orchestrator import IntegrationsOrchestrator

                self._layer_orchestrators["integrations"] = IntegrationsOrchestrator(self)
                await self._layer_orchestrators["integrations"].initialize()
                self.logger.info("Integrations layer orchestrator initialized")
            except Exception as e:
                self.logger.warning(f"Integrations layer orchestrator initialization failed: {e}")

            # All layer orchestrators initialized (Phase 9 complete)
            self.logger.info("Layer orchestrators initialized (Phase 9 complete - all 9 phases)")
            return True

        except Exception as e:
            self.logger.error(f"Failed to initialize layer orchestrators: {e}")
            return False

    async def start(self) -> bool:
        """Start the orchestrator and begin processing workflows."""
        try:
            self.logger.info("Starting Desktop Agent Orchestrator...")

            # Start layer orchestrators
            for layer_name, orchestrator in self._layer_orchestrators.items():
                try:
                    await orchestrator.start()
                    self.logger.info(f"{layer_name} layer orchestrator started")
                except Exception as e:
                    self.logger.warning(f"Failed to start {layer_name} layer: {e}")

            # Start workflow processor
            asyncio.create_task(self._process_workflows())

            self._running = True
            self.logger.info("Desktop Agent Orchestrator started successfully")
            return True

        except Exception as e:
            self.logger.error(f"Failed to start Orchestrator: {e}")
            return False

    async def stop(self) -> bool:
        """Stop the orchestrator and all layer orchestrators."""
        try:
            self.logger.info("Stopping Desktop Agent Orchestrator...")

            # Stop layer orchestrators
            for layer_name, orchestrator in self._layer_orchestrators.items():
                try:
                    await orchestrator.stop()
                    self.logger.info(f"{layer_name} layer orchestrator stopped")
                except Exception as e:
                    self.logger.warning(f"Failed to stop {layer_name} layer: {e}")

            # Cancel active tasks
            for task_id, task in self._active_tasks.items():
                try:
                    task.cancel()
                except Exception as e:
                    self.logger.warning(f"Failed to cancel task {task_id}: {e}")

            self._running = False
            self.logger.info("Desktop Agent Orchestrator stopped successfully")
            return True

        except Exception as e:
            self.logger.error(f"Failed to stop Orchestrator: {e}")
            return False

    async def _process_workflows(self) -> None:
        """Process workflows from the queue."""
        while self._running:
            try:
                workflow = await self._workflow_queue.get()
                if workflow:
                    await self._execute_workflow(workflow)
            except Exception as e:
                self.logger.error(f"Error processing workflow: {e}")

    async def _execute_workflow(self, workflow: Dict[str, Any]) -> bool:
        """Execute a single workflow."""
        try:
            workflow_id = workflow.get("id", "unknown")
            workflow_type = workflow.get("type", "unknown")

            self.logger.info(f"Executing workflow {workflow_id} of type {workflow_type}")

            # Route workflow to appropriate layer
            layer_name = workflow.get("layer")
            if layer_name and layer_name in self._layer_orchestrators:
                orchestrator = self._layer_orchestrators[layer_name]
                result = await orchestrator.execute_workflow(workflow)
                return result
            else:
                self.logger.warning(f"No orchestrator found for layer {layer_name}")
                return False

        except Exception as e:
            self.logger.error(f"Error executing workflow: {e}")
            return False

    def queue_workflow(self, workflow: Dict[str, Any]) -> bool:
        """Queue a workflow for execution."""
        try:
            self._workflow_queue.put_nowait(workflow)
            return True
        except Exception as e:
            self.logger.error(f"Failed to queue workflow: {e}")
            return False

    def get_layer_orchestrator(self, layer_name: str) -> Optional[Any]:
        """Get a specific layer orchestrator."""
        return self._layer_orchestrators.get(layer_name)

    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the orchestrator."""
        return {
            "running": self._running,
            "initialized": self._initialized,
            "active_tasks": len(self._active_tasks),
            "layer_orchestrators": {
                layer: orchestrator.get_status() if orchestrator else None
                for layer, orchestrator in self._layer_orchestrators.items()
            },
            "workflow_queue_size": (
                self._workflow_queue.qsize() if hasattr(self._workflow_queue, "qsize") else 0
            ),
        }
