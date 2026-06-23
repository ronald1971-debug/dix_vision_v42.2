"""
Core Contracts - API Module
Real implementations for API-related contracts
"""

from .credentials import (
    CredentialItem,
    CredentialsStatusResponse,
    CredentialsSummary,
    PresenceState,
    PresenceStateApi,
    get_presence_state_api,
)

__all__ = [
    "PresenceState",
    "CredentialItem",
    "CredentialsStatusResponse",
    "CredentialsSummary",
    "PresenceStateApi",
    "get_presence_state_api",
]
