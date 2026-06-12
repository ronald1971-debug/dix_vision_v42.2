"""
ui/auth_middleware.py
FastAPI authentication middleware for DIX VISION v42.2

Per audit M-7: bearer-token middleware that calls
security.authentication.verify_token. Provides optional and
required authentication dependencies for FastAPI endpoints.
"""

from __future__ import annotations

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from security.authentication import get_authenticator

security = HTTPBearer(auto_error=False)
_authenticator = get_authenticator()


async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str | None:
    """
    Verify bearer token and return principal if valid.

    Per audit M-7: adds bearer-token middleware that calls
    security.authentication.verify_token. Allows optional auth
    for read-only endpoints but requires auth for sensitive operations.
    """
    if credentials is None:
        # No token provided - return None to allow optional auth
        return None

    session = _authenticator.verify(credentials.credentials)
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return session.principal


async def optional_auth(principal: str | None = Depends(verify_token)) -> dict[str, str | None]:
    """
    Optional authentication dependency for read-only endpoints.

    Returns principal dict with None if no auth provided.
    """
    return {"principal": principal}


async def require_auth(principal: str = Depends(verify_token)) -> str:
    """
    Required authentication dependency for sensitive operations.

    Raises 401 if no valid token provided.
    """
    if principal is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required for this operation",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return principal


__all__ = ["verify_token", "optional_auth", "require_auth"]