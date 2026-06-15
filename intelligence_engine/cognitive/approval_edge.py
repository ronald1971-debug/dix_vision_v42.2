"""Stub cognitive approval edge."""

from typing import Any

FEATURE_FLAG_ENV_VAR = "COGNITIVE_CHAT_FEATURE_FLAG"


class ApprovalAlreadyDecidedError(Exception):
    """Stub error when approval already decided."""
    pass


class ApprovalNotFoundError(Exception):
    """Stub error when approval not found."""
    pass


class ApprovalEdge:
    """Stub ApprovalEdge."""

    def __init__(self, **kwargs: Any):
        pass