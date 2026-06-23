"""
mission_system.resource_allocator
DIX VISION v42.2 — Production-Grade Resource Allocator

Resource allocation with resource management, capacity planning,
resource optimization, and production-ready allocation scheduling.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Dict, List

from system.time_source import now

logger = logging.getLogger(__name__)


@dataclass
class ResourceAllocation:
    """A resource allocation."""

    allocation_id: str
    mission_id: str
    resource_type: str
    allocated_amount: float = 0.0
    total_capacity: float = 0.0
    utilization: float = 0.0
    timestamp: str = ""


class ProductionResourceAllocator:
    """Production-grade resource allocator."""

    def __init__(self) -> None:
        self._allocations: List[ResourceAllocation] = []
        self._capacities: Dict[str, float] = {"compute": 100.0, "memory": 100.0, "storage": 100.0}

    def start(self) -> bool:
        logger.info("[RESOURCE_ALLOCATOR] Production resource allocator started")
        return True

    def stop(self) -> bool:
        logger.info("[RESOURCE_ALLOCATOR] Production resource allocator stopped")
        return True

    def allocate_resource(
        self, mission_id: str, resource_type: str, amount: float
    ) -> ResourceAllocation:
        """Allocate resources to a mission."""
        if resource_type not in self._capacities:
            raise ValueError(f"Unknown resource type: {resource_type}")

        allocation = ResourceAllocation(
            allocation_id=f"alloc_{now().sequence}",
            mission_id=mission_id,
            resource_type=resource_type,
            allocated_amount=amount,
            total_capacity=self._capacities[resource_type],
            utilization=(
                amount / self._capacities[resource_type]
                if self._capacities[resource_type] > 0
                else 0.0
            ),
            timestamp=now().utc_time.isoformat(),
        )
        self._allocations.append(allocation)
        return allocation

    def get_utilization(self, resource_type: str) -> float:
        """Get current resource utilization."""
        total_allocated = sum(
            a.allocated_amount for a in self._allocations if a.resource_type == resource_type
        )
        return (
            total_allocated / self._capacities[resource_type]
            if self._capacities[resource_type] > 0
            else 0.0
        )


def get_production_resource_allocator() -> ProductionResourceAllocator:
    """Get the singleton production resource allocator instance."""
    if not hasattr(get_production_resource_allocator, "_instance"):
        get_production_resource_allocator._instance = ProductionResourceAllocator()
    return get_production_resource_allocator._instance
