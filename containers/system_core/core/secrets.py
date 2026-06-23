"""
core/secrets.py
Central secrets management module (single source per manifest §3).

This module re-exports the canonical secrets manager from security.secrets_manager
to provide a single, consistent import path for secrets management across the system.
"""

from __future__ import annotations

from security.secrets_manager import (
    SecretsManager,
    get_secret,
    get_secrets_manager,
    set_secret,
)

__all__ = [
    "SecretsManager",
    "get_secrets_manager",
    "get_secret",
    "set_secret",
]
