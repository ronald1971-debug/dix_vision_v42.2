"""Stub approval queue module."""

from typing import Any, List


class ApprovalQueue:
    """Stub approval queue."""

    def __init__(self, **kwargs: Any):
        pass

    def enqueue(self, item: Any, **kwargs: Any) -> None:
        """Stub enqueue method."""
        pass

    def dequeue(self, **kwargs: Any) -> Any:
        """Stub dequeue method."""
        return None

    def is_empty(self, **kwargs: Any) -> bool:
        """Stub is_empty method."""
        return True

    def size(self, **kwargs: Any) -> int:
        """Stub size method."""
        return 0


def get_approval_queue(**kwargs: Any) -> ApprovalQueue:
    """Stub approval queue getter."""
    return ApprovalQueue()