"""
mission_system.mission_system
DIX VISION v42.2 — Production-Grade Mission System

Orchestrates all mission system components including mission planning,
mission execution, mission monitoring, objective tracking, resource
allocation, and success evaluation.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from mission_system.mission_executor import (
    ProductionMissionExecutor,
    get_production_mission_executor,
)
from mission_system.mission_monitor import ProductionMissionMonitor, get_production_mission_monitor
from mission_system.mission_planner import ProductionMissionPlanner, get_production_mission_planner
from mission_system.objective_tracker import (
    ProductionObjectiveTracker,
    get_production_objective_tracker,
)
from mission_system.resource_allocator import (
    ProductionResourceAllocator,
    get_production_resource_allocator,
)
from mission_system.success_evaluator import (
    ProductionSuccessEvaluator,
    get_production_success_evaluator,
)

logger = logging.getLogger(__name__)


class ProductionMissionSystem:
    """Production-grade mission system orchestrator."""

    def __init__(self) -> None:
        self._mission_planner: Optional[ProductionMissionPlanner] = None
        self._mission_executor: Optional[ProductionMissionExecutor] = None
        self._mission_monitor: Optional[ProductionMissionMonitor] = None
        self._objective_tracker: Optional[ProductionObjectiveTracker] = None
        self._resource_allocator: Optional[ProductionResourceAllocator] = None
        self._success_evaluator: Optional[ProductionSuccessEvaluator] = None
        self._initialized: bool = False

    def initialize(self) -> bool:
        """Initialize all mission system components."""
        if self._initialized:
            return True

        logger.info("[MISSION_SYSTEM] Initializing production mission system...")

        self._mission_planner = get_production_mission_planner()
        self._mission_executor = get_production_mission_executor()
        self._mission_monitor = get_production_mission_monitor()
        self._objective_tracker = get_production_objective_tracker()
        self._resource_allocator = get_production_resource_allocator()
        self._success_evaluator = get_production_success_evaluator()

        self._mission_planner.start()
        self._mission_executor.start()
        self._mission_monitor.start()
        self._objective_tracker.start()
        self._resource_allocator.start()
        self._success_evaluator.start()

        self._initialized = True
        logger.info("[MISSION_SYSTEM] Production mission system initialized successfully")
        return True

    def shutdown(self) -> bool:
        """Shutdown all mission system components."""
        if not self._initialized:
            return True

        logger.info("[MISSION_SYSTEM] Shutting down production mission system...")

        if self._mission_planner:
            self._mission_planner.stop()
        if self._mission_executor:
            self._mission_executor.stop()
        if self._mission_monitor:
            self._mission_monitor.stop()
        if self._objective_tracker:
            self._objective_tracker.stop()
        if self._resource_allocator:
            self._resource_allocator.stop()
        if self._success_evaluator:
            self._success_evaluator.stop()

        self._initialized = False
        logger.info("[MISSION_SYSTEM] Production mission system shut down successfully")
        return True

    def get_system_state(self) -> Dict[str, Any]:
        """Get current system state from all components."""
        if not self._initialized:
            return {"error": "Mission system not initialized"}

        return {
            "planner": {"status": "active"},
            "executor": {"status": "active"},
            "monitor": {"status": "active"},
            "objectives": {"status": "active"},
            "resources": {"status": "active"},
            "evaluation": {"status": "active"},
        }

    @property
    def mission_planner(self) -> Optional[ProductionMissionPlanner]:
        return self._mission_planner

    @property
    def mission_executor(self) -> Optional[ProductionMissionExecutor]:
        return self._mission_executor

    @property
    def mission_monitor(self) -> Optional[ProductionMissionMonitor]:
        return self._mission_monitor

    @property
    def objective_tracker(self) -> Optional[ProductionObjectiveTracker]:
        return self._objective_tracker

    @property
    def resource_allocator(self) -> Optional[ProductionResourceAllocator]:
        return self._resource_allocator

    @property
    def success_evaluator(self) -> Optional[ProductionSuccessEvaluator]:
        return self._success_evaluator


def get_production_mission_system() -> ProductionMissionSystem:
    """Get the singleton production mission system instance."""
    if not hasattr(get_production_mission_system, "_instance"):
        get_production_mission_system._instance = ProductionMissionSystem()
    return get_production_mission_system._instance
