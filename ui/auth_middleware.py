"""
Stub authentication module for dashboard testing
Provides a minimal implementation when DIX VISION authentication is not available
"""

from fastapi import Depends

def optional_auth():
    """Stub optional authentication dependency."""
    return None

def require_auth():
    """Stub required authentication dependency."""
    return None

def verify_token():
    """Stub token verification."""
    return None
