"""
security/keyring_adapter.py
Optional bridge to the OS keyring. Uses the ``keyring`` library when present;
otherwise falls back to the in-memory SecretsManager.
"""

from __future__ import annotations

import sys
import threading

try:  # pragma: no cover - optional dependency
    import keyring  # type: ignore

    _HAS_KEYRING = True
except Exception:
    keyring = None  # type: ignore
    _HAS_KEYRING = False

from .secrets_manager import get_secrets_manager

SERVICE = "dix_vision_v42_2"


class KeyringAdapter:
    def set(self, key: str, value: str) -> None:
        if _HAS_KEYRING:
            try:
                keyring.set_password(SERVICE, key, value)
                return
            except Exception as exc:
                sys.stderr.write(f"[KeyringAdapter.set] keyring failed: {exc}\n")
        get_secrets_manager().set(key, value)

    def get(self, key: str, default: str = "") -> str:
        if _HAS_KEYRING:
            try:
                v = keyring.get_password(SERVICE, key)
                if v is not None:
                    return str(v)
            except Exception as exc:
                sys.stderr.write(f"[KeyringAdapter.get] keyring failed: {exc}\n")
        return get_secrets_manager().get(key, default)

    def delete(self, key: str) -> None:
        if _HAS_KEYRING:
            try:
                keyring.delete_password(SERVICE, key)
            except Exception as exc:
                sys.stderr.write(f"[KeyringAdapter.delete] keyring failed: {exc}\n")
        get_secrets_manager().delete(key)


_ka: KeyringAdapter | None = None
_lock = threading.Lock()


def get_keyring_adapter() -> KeyringAdapter:
    global _ka
    if _ka is None:
        with _lock:
            if _ka is None:
                _ka = KeyringAdapter()
    return _ka


def get_from_keyring(key: str) -> str | None:
    """Module-level convenience wrapper for KeyringAdapter.get()."""
    return get_keyring_adapter().get(key) or None


def set_in_keyring(key: str, value: str) -> None:
    """Module-level convenience wrapper for KeyringAdapter.set()."""
    get_keyring_adapter().set(key, value)


def delete_from_keyring(key: str) -> None:
    """Module-level convenience wrapper for KeyringAdapter.delete()."""
    get_keyring_adapter().delete(key)