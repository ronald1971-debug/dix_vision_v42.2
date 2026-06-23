"""Runtime Awareness – DYON maps services, queues, and event buses.

Monitors the live runtime topology and health of all components.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any


class ServiceStatus(Enum):
    HEALTHY = auto()
    DEGRADED = auto()
    UNHEALTHY = auto()
    DEAD = auto()
    UNKNOWN = auto()


@dataclass
class ServiceInfo:
    name: str
    engine: str
    status: ServiceStatus = ServiceStatus.UNKNOWN
    last_heartbeat: float = 0.0
    uptime_seconds: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class QueueInfo:
    name: str
    depth: int = 0
    max_depth: int = 10000
    consumer_count: int = 0
    producer_count: int = 0
    is_healthy: bool = True


@dataclass
class EventBusInfo:
    name: str
    subscriber_count: int = 0
    events_per_second: float = 0.0
    backpressure: bool = False


@dataclass
class RuntimeTopology:
    services: list[ServiceInfo] = field(default_factory=list)
    queues: list[QueueInfo] = field(default_factory=list)
    event_buses: list[EventBusInfo] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)


class RuntimeAwareness:
    """Maintains a live map of the runtime environment."""

    def __init__(self) -> None:
        self._services: dict[str, ServiceInfo] = {}
        self._queues: dict[str, QueueInfo] = {}
        self._event_buses: dict[str, EventBusInfo] = {}
        self._heartbeat_timeout: float = 30.0

    def register_service(self, service: ServiceInfo) -> None:
        self._services[service.name] = service

    def heartbeat(self, service_name: str) -> bool:
        if service_name in self._services:
            self._services[service_name].last_heartbeat = time.time()
            self._services[service_name].status = ServiceStatus.HEALTHY
            return True
        return False

    def register_queue(self, queue: QueueInfo) -> None:
        self._queues[queue.name] = queue

    def register_event_bus(self, bus: EventBusInfo) -> None:
        self._event_buses[bus.name] = bus

    def check_health(self) -> RuntimeTopology:
        now = time.time()
        for svc in self._services.values():
            if svc.last_heartbeat > 0:
                elapsed = now - svc.last_heartbeat
                if elapsed > self._heartbeat_timeout * 2:
                    svc.status = ServiceStatus.DEAD
                elif elapsed > self._heartbeat_timeout:
                    svc.status = ServiceStatus.UNHEALTHY
            else:
                svc.status = ServiceStatus.UNKNOWN

        for q in self._queues.values():
            q.is_healthy = q.depth < q.max_depth

        return RuntimeTopology(
            services=list(self._services.values()),
            queues=list(self._queues.values()),
            event_buses=list(self._event_buses.values()),
        )

    def get_dead_services(self) -> list[ServiceInfo]:
        return [s for s in self._services.values() if s.status == ServiceStatus.DEAD]

    def get_unhealthy_services(self) -> list[ServiceInfo]:
        return [
            s
            for s in self._services.values()
            if s.status in (ServiceStatus.UNHEALTHY, ServiceStatus.DEAD)
        ]
