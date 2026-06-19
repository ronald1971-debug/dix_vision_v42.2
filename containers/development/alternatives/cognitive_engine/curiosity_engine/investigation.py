"""Investigation - manages investigation lifecycle."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from cognitive_engine.curiosity_engine.question_generator import Question


class InvestigationStatus(Enum):
    """Status of an investigation."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"


@dataclass
class Investigation:
    """An investigation into a question."""

    question: Question
    status: InvestigationStatus = InvestigationStatus.PENDING
    started_at: int = field(default_factory=lambda: time.time_ns())
    completed_at: int | None = None
    findings: tuple[str, ...] = ()
    conclusion: str = ""
    evidence: dict[str, Any] = field(default_factory=dict)

    def start(self) -> None:
        """Start the investigation."""
        self.status = InvestigationStatus.IN_PROGRESS

    def add_finding(self, finding: str, evidence: dict[str, Any] | None = None) -> None:
        """Add a finding to the investigation."""
        self.findings = (*self.findings, finding)
        if evidence:
            self.evidence.update(evidence)

    def complete(self, conclusion: str) -> None:
        """Complete the investigation with a conclusion."""
        self.status = InvestigationStatus.COMPLETED
        self.completed_at = time.time_ns()
        self.conclusion = conclusion

    def block(self, reason: str) -> None:
        """Block the investigation."""
        self.status = InvestigationStatus.BLOCKED


class InvestigationManager:
    """Manages multiple investigations."""

    def __init__(self) -> None:
        self._investigations: dict[str, Investigation] = {}

    def create(self, question: Question) -> Investigation:
        """Create an investigation from a question."""
        inv = Investigation(question=question)
        self._investigations[question.question_id] = inv
        return inv

    def get(self, question_id: str) -> Investigation | None:
        """Get an investigation by question ID."""
        return self._investigations.get(question_id)

    def active(self) -> list[Investigation]:
        """Get active investigations."""
        return [
            i
            for i in self._investigations.values()
            if i.status == InvestigationStatus.IN_PROGRESS
        ]

    def pending(self) -> list[Investigation]:
        """Get pending investigations."""
        return [
            i
            for i in self._investigations.values()
            if i.status == InvestigationStatus.PENDING
        ]