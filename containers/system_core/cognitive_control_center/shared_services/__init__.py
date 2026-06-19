"""Shared services module."""

from .pairing import get_pairing
from .auth import get_or_create_token
from .chat import get_chat
from .llm import get_router
from .qr import qr_png_bytes

__all__ = ["get_pairing", "get_or_create_token", "get_chat", "get_router", "qr_png_bytes"]