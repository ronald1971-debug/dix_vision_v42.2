"""Stub pairing service."""

from typing import Any


class DevicePairingService:
    """Stub device pairing service."""

    def __init__(self, **kwargs: Any):
        pass


def get_pairing(**kwargs: Any) -> Any:
    """Stub pairing getter."""
    return None


def get_device_pairing_service(**kwargs: Any) -> DevicePairingService:
    """Stub device pairing service getter."""
    return DevicePairingService()