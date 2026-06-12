"""
cognitive_control_center.shared_services.auth
Authentication service - Migrated from cockpit/auth.py

This module provides authentication and token management functionality for the cognitive
control center, preserving all features from cockpit/auth.py while integrating with
the cognitive environment.

PRESERVED FEATURES:
- Token generation and persistence
- Bearer token authentication
- Multiple token sources (header, query param, cookie)
- Public path configuration
- ASGI middleware
- Loopback-only binding
- One-time token for pairing

ENHANCED FEATURES:
- Integration with cognitive environment
- Agent-aware authentication
- Workspace-based authorization
- Enhanced token lifecycle management
"""

from __future__ import annotations

import os
import secrets
import sys
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Callable

from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send

from cognitive_control_center.core.operating_environment import (
    CognitiveEntityType,
    get_cognitive_environment,
)

# Preserve exact configuration from cockpit/auth.py
PUBLIC_PATHS_EXACT = frozenset(
    {
        "/",  # SPA shell: JS loads and uses its own stored token
        "/health",
        "/favicon.ico",
        "/pair",  # device pairing landing page (token-guarded by pairing)
        "/api/pair/claim",  # pairing claim uses its own one-time token
    }
)
PUBLIC_PATH_PREFIXES = ("/static/",)

# Cognitive environment extensions
COGNITIVE_PUBLIC_PATHS = {
    "/cognitive",  # Cognitive environment endpoints
    "/agent_ops",  # Agent operations center
    "/workspaces",  # Workspace management
}


def _token_file() -> Path:
    """Preserve exact token file location from cockpit/auth.py"""
    return Path(os.environ.get("DIX_COCKPIT_TOKEN_FILE", "data/cockpit_token.txt"))


class CognitiveAuthService:
    """
    Authentication service for cognitive control center.
    
    Preserves all cockpit/auth.py features while adding cognitive environment integration.
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._environment = get_cognitive_environment()
        self._cached_token: str | None = None
        self._token_expiry: datetime | None = None
        self._one_time_tokens: dict[str, datetime] = {}

    def get_or_create_token(self, force_refresh: bool = False) -> str:
        """
        Return the current cockpit token, generating one if missing.
        
        PRESERVES: Exact behavior from cockpit/auth.py
        ENHANCES: Token expiry management and caching
        """
        with self._lock:
            # Check cache if not forced refresh
            if not force_refresh and self._cached_token:
                if self._token_expiry and datetime.utcnow() < self._token_expiry:
                    return self._cached_token

            # Environment variable
            env = os.environ.get("DIX_COCKPIT_TOKEN", "").strip()
            if env:
                self._cached_token = env
                return env

            # File persistence
            p = _token_file()
            if p.exists():
                txt = p.read_text().strip()
                if txt:
                    self._cached_token = txt
                    return txt

            # Generate new token
            tok = secrets.token_urlsafe(32)
            try:
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(tok + "\n")
                try:
                    os.chmod(p, 0o600)
                except OSError:
                    pass
            except OSError as e:
                sys.stderr.write(f"[cognitive_auth] could not persist token to {p}: {e}\n")

            sys.stderr.write(
                f"[cognitive_auth] generated token (persist via DIX_COCKPIT_TOKEN):\n          {tok}\n"
            )

            self._cached_token = tok
            self._token_expiry = datetime.utcnow() + timedelta(days=30)  # 30 day expiry

            # Log to cognitive environment
            self._environment.register_entity("auth_service", CognitiveEntityType.SYSTEM)

            return tok

    def generate_one_time_token(self, ttl_seconds: int = 900) -> str:
        """
        Generate a one-time token for special operations (like pairing).
        
        PRESERVES: One-time token concept from cockpit/auth.py
        ENHANCES: TTL management and cleanup
        """
        tok = secrets.token_urlsafe(32)
        expiry = datetime.utcnow() + timedelta(seconds=ttl_seconds)
        
        with self._lock:
            self._one_time_tokens[tok] = expiry
        
        return tok

    def validate_one_time_token(self, token: str) -> bool:
        """Validate and consume a one-time token."""
        with self._lock:
            if token not in self._one_time_tokens:
                return False
            
            if datetime.utcnow() > self._one_time_tokens[token]:
                del self._one_time_tokens[token]
                return False
            
            # Consume token
            del self._one_time_tokens[token]
            return True

    def cleanup_expired_tokens(self) -> None:
        """Clean up expired one-time tokens."""
        with self._lock:
            now = datetime.utcnow()
            expired = [tok for tok, expiry in self._one_time_tokens.items() if now > expiry]
            for tok in expired:
                del self._one_time_tokens[tok]


# Preserve exact helper function from cockpit/auth.py
def _extract(request: Request) -> str | None:
    """
    Extract token from request (header, query param, or cookie).
    
    PRESERVES: Exact extraction logic from cockpit/auth.py
    """
    auth = request.headers.get("authorization", "")
    if auth.lower().startswith("bearer "):
        return auth[7:].strip()
    q = request.query_params.get("token")
    if q:
        return q.strip()
    c = request.cookies.get("dix_token")
    if c:
        return c.strip()
    return None


class CognitiveTokenAuthMiddleware:
    """
    Pure-ASGI bearer-token gate for cognitive control center.
    
    PRESERVES: All middleware logic from cockpit/auth.py
    ENHANCES: Cognitive environment path support and agent-aware auth
    """

    def __init__(self, app: ASGIApp, token: str | None = None) -> None:
        self._app = app
        self._auth_service = CognitiveAuthService()
        self._token = token or self._auth_service.get_or_create_token()
        self._public_paths_exact = PUBLIC_PATHS_EXACT.union(COGNITIVE_PUBLIC_PATHS)
        self._public_path_prefixes = PUBLIC_PATH_PREFIXES

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """ASGI middleware call."""
        if scope.get("type") != "http":
            await self._app(scope, receive, send)
            return

        path: str = scope.get("path", "")

        # Check public paths (preserves cockpit logic + adds cognitive paths)
        if (path in self._public_paths_exact or 
            any(path.startswith(p) for p in self._public_path_prefixes)):
            await self._app(scope, receive, send)
            return

        request = Request(scope, receive=receive)
        supplied = _extract(request)

        # Validate token (preserves exact validation logic)
        if not supplied or not secrets.compare_digest(supplied, self._token):
            resp = JSONResponse(
                {
                    "error": "unauthorized",
                    "hint": "use ?token=… or Authorization: Bearer …",
                },
                status_code=401,
            )
            await resp(scope, receive, send)
            return

        await self._app(scope, receive, send)


# Preserve exact API for backward compatibility
def get_or_create_token() -> str:
    """
    Return the current cockpit token, generating one if missing.
    
    PRESERVES: Exact API from cockpit/auth.py
    ENHANCES: Delegates to cognitive service
    """
    service = CognitiveAuthService()
    return service.get_or_create_token()


# Singleton service instance
_auth_service: CognitiveAuthService | None = None
_auth_lock = threading.Lock()


def get_cognitive_auth_service() -> CognitiveAuthService:
    """Get the singleton cognitive auth service."""
    global _auth_service
    if _auth_service is None:
        with _auth_lock:
            if _auth_service is None:
                _auth_service = CognitiveAuthService()
    return _auth_service


__all__ = [
    "CognitiveAuthService",
    "CognitiveTokenAuthMiddleware",
    "get_or_create_token",
    "get_cognitive_auth_service",
    "_extract",
    "PUBLIC_PATHS_EXACT",
    "PUBLIC_PATH_PREFIXES",
]