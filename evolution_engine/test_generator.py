"""Test Generation – DYON proposes test cases for system validation.

All generated tests require governance approval before execution.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field

from core.types import ApprovalStatus


@dataclass
class TestProposal:
    test_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    target_module: str = ""
    test_name: str = ""
    test_type: str = ""  # unit | integration | property | regression
    description: str = ""
    test_code: str = ""
    rationale: str = ""
    approval_status: ApprovalStatus = ApprovalStatus.PENDING
    created_at: float = field(default_factory=time.time)


class TestGenerator:
    """Generates test proposals for the evolution engine."""

    def __init__(self) -> None:
        self._proposals: list[TestProposal] = []

    def generate_test(
        self,
        target_module: str,
        test_name: str,
        test_type: str,
        description: str,
        test_code: str = "",
        rationale: str = "",
    ) -> TestProposal:
        proposal = TestProposal(
            target_module=target_module,
            test_name=test_name,
            test_type=test_type,
            description=description,
            test_code=test_code,
            rationale=rationale,
        )
        self._proposals.append(proposal)
        return proposal

    def get_proposals(
        self, module: str | None = None
    ) -> list[TestProposal]:
        if module:
            return [p for p in self._proposals if p.target_module == module]
        return list(self._proposals)

    def get_pending(self) -> list[TestProposal]:
        return [
            p for p in self._proposals if p.approval_status == ApprovalStatus.PENDING
        ]

    @property
    def proposal_count(self) -> int:
        return len(self._proposals)
