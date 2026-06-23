"""
cognitive_control_center.compat.cockpit_compat
Cockpit compatibility layer - Provides compatibility shims for migrating from cockpit.

This module provides compatibility shims that allow the existing ui/cockpit_routes.py to work
while we migrate functionality from the deprecated cockpit directory to the cognitive control
center. This is a temporary migration layer ensuring ZERO FEATURE LOSS.

PRESERVED FEATURES:
- All cockpit API endpoints
- All cockpit services (auth, chat, pairing, llm, qr)
- All cockpit widgets
- All cockpit integrations
"""

from __future__ import annotations

from cognitive_control_center.shared_services.auth import (
    PUBLIC_PATH_PREFIXES,
    PUBLIC_PATHS_EXACT,
    CognitiveAuthService,
    CognitiveTokenAuthMiddleware,
    _extract,
    get_cognitive_auth_service,
    get_or_create_token,
)
from cognitive_control_center.shared_services.chat import (
    ChatTurn,
    CognitiveChat,
    Router,
    available_voices,
    get_chat,
)
from cognitive_control_center.shared_services.llm import (
    Capability,
    CognitiveLLMRouter,
    LLMResponse,
    Provider,
    ProviderStatus,
    get_router,
)

# Import the new cognitive control center services
from cognitive_control_center.shared_services.pairing import (
    get_device_pairing_service,
)
from cognitive_control_center.shared_services.qr import (
    encode_qr,
    qr_png_bytes,
)


# Create compatibility shims that mimic the cockpit API
class PairingCompat:
    """Compatibility shim for cockpit.pairing module."""

    def __init__(self) -> None:
        self._service = get_device_pairing_service()

    def issue_token(self, label: str, ttl_sec: int = 900) -> str:
        """Issue a pairing token (compatibility API)."""
        token = self._service.issue_pairing_token(label, ttl_sec)
        return token.token_id

    def claim_token(self, token: str, device: str = "unknown") -> dict | None:
        """Claim a pairing token (compatibility API)."""
        paired_device = self._service.claim_pairing_token(token, device)
        if paired_device:
            return {
                "device_id": paired_device.device_id,
                "label": paired_device.label,
                "device_type": paired_device.device_type,
                "paired_at": paired_device.paired_at.isoformat(),
            }
        return None

    def list_devices(self) -> list[dict]:
        """List all paired devices (compatibility API)."""
        devices = self._service.get_paired_devices()
        return [
            {
                "device_id": d.device_id,
                "label": d.label,
                "device_type": d.device_type,
                "paired_at": d.paired_at.isoformat(),
                "last_seen": d.last_seen.isoformat(),
            }
            for d in devices
        ]


# Create singleton compatibility instances
_pairing_compat = PairingCompat()


# Re-export compatibility APIs that mimic cockpit module structure
def issue_token(label: str, ttl_sec: int = 900) -> str:
    """Compatibility shim for cockpit.pairing.issue_token."""
    return _pairing_compat.issue_token(label, ttl_sec)


def claim_token(token: str, device: str = "unknown") -> dict | None:
    """Compatibility shim for cockpit.pairing.claim_token."""
    return _pairing_compat.claim_token(token, device)


def list_devices() -> list[dict]:
    """Compatibility shim for cockpit.pairing.list_devices."""
    return _pairing_compat.list_devices()


# For direct import compatibility (mimics cockpit.pairing module structure)
class PairingModuleCompat:
    """Module-level compatibility shim for cockpit.pairing."""

    def __getattr__(self, name: str):
        """Forward attribute access to compatibility functions."""
        if name == "issue_token":
            return issue_token
        elif name == "claim_token":
            return claim_token
        elif name == "list_devices":
            return list_devices
        raise AttributeError(f"module 'cockpit.pairing' has no attribute '{name}'")


# Create module-level compatibility
_sys_modules = None
try:
    import sys as _sys_modules
except ImportError:
    pass

if _sys_modules:
    _sys_modules["cockpit_pairing_compat"] = PairingModuleCompat()
    _sys_modules["cockpit_auth_compat"] = CognitiveAuthService
    _sys_modules["cockpit_chat_compat"] = CognitiveChat


# Provide module-level shims for backward compatibility
class CockpitAuthCompat:
    """Module-level compatibility for cockpit.auth."""

    def __getattr__(self, name: str):
        """Forward auth-related attributes to cognitive control center."""
        if name == "get_or_create_token":
            return get_or_create_token
        elif name == "TokenAuthMiddleware":
            return CognitiveTokenAuthMiddleware
        elif name == "_extract":
            return _extract
        elif name == "PUBLIC_PATHS_EXACT":
            return PUBLIC_PATHS_EXACT
        elif name == "PUBLIC_PATH_PREFIXES":
            return PUBLIC_PATH_PREFIXES
        raise AttributeError(f"module 'cockpit.auth' has no attribute '{name}'")


class CockpitChatCompat:
    """Module-level compatibility for cockpit.chat."""

    def __getattr__(self, name: str):
        """Forward chat-related attributes to cognitive control center."""
        if name == "get_chat":
            return get_chat
        elif name == "Chat":
            return CognitiveChat
        elif name == "ChatTurn":
            return ChatTurn
        elif name == "Router":
            return Router
        elif name == "available_voices":
            return available_voices
        raise AttributeError(f"module 'cockpit.chat' has no attribute '{name}'")


class CockpitLLMCompat:
    """Module-level compatibility for cockpit.llm."""

    def __getattr__(self, name: str):
        """Forward llm-related attributes to cognitive control center."""
        if name == "Capability":
            return Capability
        elif name == "Provider":
            return Provider
        elif name == "ProviderStatus":
            return ProviderStatus
        elif name == "LLMResponse":
            return LLMResponse
        elif name == "LLMRouter":
            return CognitiveLLMRouter
        elif name == "get_router":
            return get_router
        raise AttributeError(f"module 'cockpit.llm' has no attribute '{name}'")


class CockpitQRCompat:
    """Module-level compatibility for cockpit.qr."""

    def __getattr__(self, name: str):
        """Forward qr-related attributes to cognitive control center."""
        if name == "encode_qr":
            return encode_qr
        elif name == "qr_png_bytes":
            return qr_png_bytes
        raise AttributeError(f"module 'cockpit.qr' has no attribute '{name}'")


# Create additional module-level compatibility
if _sys_modules:
    _sys_modules["cockpit.auth"] = CockpitAuthCompat()
    _sys_modules["cockpit.chat"] = CockpitChatCompat()
    _sys_modules["cockpit.llm"] = CockpitLLMCompat()
    _sys_modules["cockpit.qr"] = CockpitQRCompat()


__all__ = [
    "PairingCompat",
    "CockpitAuthCompat",
    "CockpitChatCompat",
    "CockpitLLMCompat",
    "CockpitQRCompat",
    "get_device_pairing_service",
    "get_cognitive_auth_service",
    "get_or_create_token",
    "CognitiveTokenAuthMiddleware",
    "get_chat",
    "available_voices",
    "CognitiveChat",
    "ChatTurn",
    "Router",
    "Capability",
    "Provider",
    "ProviderStatus",
    "LLMResponse",
    "CognitiveLLMRouter",
    "get_router",
    "encode_qr",
    "qr_png_bytes",
]
