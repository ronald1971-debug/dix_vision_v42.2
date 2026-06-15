"""Stub approval projection module."""

from typing import Any, List


DECISION_KINDS = ["approve", "reject", "escalate"]
PENDING_KIND = "pending"


class ProjectionLedgerRow:
    """Stub projection ledger row."""

    def __init__(self, **kwargs: Any):
        pass


class ApprovalProjection:
    """Stub approval projection."""

    def __init__(self, **kwargs: Any):
        pass


def projection_rows_from_payloads(payloads: List[Any], **kwargs: Any) -> List[ProjectionLedgerRow]:
    """Stub projection rows from payloads."""
    return [ProjectionLedgerRow() for _ in payloads]


def get_approval_projection(**kwargs: Any) -> ApprovalProjection:
    """Stub approval projection getter."""
    return ApprovalProjection()