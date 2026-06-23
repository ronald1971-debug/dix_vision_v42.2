"""Shared services module."""

from .auth import get_auth_service, get_or_create_token
from .chat import get_chat
from .llm import get_router
from .pairing import get_device_pairing_service, get_pairing
from .qr import qr_png_bytes

__all__ = [
    "get_pairing",
    "get_device_pairing_service",
    "get_auth_service",
    "get_or_create_token",
    "get_chat",
    "get_router",
    "qr_png_bytes",
]
