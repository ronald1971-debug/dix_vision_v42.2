"""Stub service registry module."""

from typing import Any


class ServiceRegistry:
    """Stub service registry."""

    def __init__(self, **kwargs: Any):
        pass


def get_service_registry(**kwargs: Any) -> ServiceRegistry:
    """Get the service registry."""
    return ServiceRegistry()


def register_tier_services(registry: ServiceRegistry = None, tier: str = None, services: list = None, **kwargs: Any) -> None:
    """Register tier services."""
    pass