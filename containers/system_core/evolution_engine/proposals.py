"""Evolution Proposals – DYON generates improvement proposals.

Critical Rule: Evolution proposes. Governance approves.
Forbidden: Self-deployment, Self-modification.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any

from core.types import ApprovalStatus


class ProposalType(Enum):
    CODE_IMPROVEMENT = auto()
    ARCHITECTURE_CHANGE = auto()
    PARAMETER_TUNING = auto()
    TEST_GENERATION = auto()
    REFACTOR = auto()
    DEPENDENCY_UPDATE = auto()
    PERFORMANCE_OPTIMIZATION = auto()


class ProposalPriority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class EvolutionProposal:
    proposal_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    proposal_type: ProposalType = ProposalType.CODE_IMPROVEMENT
    priority: ProposalPriority = ProposalPriority.MEDIUM
    title: str = ""
    description: str = ""
    target_module: str = ""
    rationale: str = ""
    estimated_impact: str = ""
    risk_assessment: str = ""
    approval_status: ApprovalStatus = ApprovalStatus.PENDING
    created_at: float = field(default_factory=time.time)
    reviewed_at: float = 0.0
    reviewer: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def is_approved(self) -> bool:
        return self.approval_status == ApprovalStatus.APPROVED


class ProposalEngine:
    """Generates and manages evolution proposals.

    DYON never self-deploys or self-modifies. All changes require
    governance approval through the authority graph.
    """

    def __init__(self) -> None:
        self._proposals: dict[str, EvolutionProposal] = {}
        self._history: list[EvolutionProposal] = []

    def propose(
        self,
        proposal_type: ProposalType,
        title: str,
        description: str,
        target_module: str,
        rationale: str = "",
        estimated_impact: str = "",
        risk_assessment: str = "",
        priority: ProposalPriority = ProposalPriority.MEDIUM,
    ) -> EvolutionProposal:
        proposal = EvolutionProposal(
            proposal_type=proposal_type,
            priority=priority,
            title=title,
            description=description,
            target_module=target_module,
            rationale=rationale,
            estimated_impact=estimated_impact,
            risk_assessment=risk_assessment,
        )
        self._proposals[proposal.proposal_id] = proposal
        self._history.append(proposal)
        return proposal

    def approve(self, proposal_id: str, reviewer: str) -> bool:
        p = self._proposals.get(proposal_id)
        if p and p.approval_status == ApprovalStatus.PENDING:
            p.approval_status = ApprovalStatus.APPROVED
            p.reviewed_at = time.time()
            p.reviewer = reviewer
            return True
        return False

    def reject(self, proposal_id: str, reviewer: str) -> bool:
        p = self._proposals.get(proposal_id)
        if p and p.approval_status == ApprovalStatus.PENDING:
            p.approval_status = ApprovalStatus.REJECTED
            p.reviewed_at = time.time()
            p.reviewer = reviewer
            return True
        return False

    def get_pending(self) -> list[EvolutionProposal]:
        return [p for p in self._proposals.values() if p.approval_status == ApprovalStatus.PENDING]

    def get_approved(self) -> list[EvolutionProposal]:
        return [p for p in self._proposals.values() if p.is_approved]

    def get_by_type(self, ptype: ProposalType) -> list[EvolutionProposal]:
        return [p for p in self._proposals.values() if p.proposal_type == ptype]

    def get_by_module(self, module: str) -> list[EvolutionProposal]:
        return [p for p in self._proposals.values() if p.target_module == module]

    @property
    def pending_count(self) -> int:
        return len(self.get_pending())

    @property
    def total_count(self) -> int:
        return len(self._proposals)
