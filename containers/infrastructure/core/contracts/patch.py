"""
Core Contracts Patch
Real implementation for patch management contracts
"""

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class PatchStage(Enum):
    """Patch stage enumeration"""

    PROPOSED = "proposed"
    ANALYZED = "analyzed"
    VALIDATED = "validated"
    APPROVED = "approved"
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ROLLED_BACK = "rolled_back"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    SANDBOX = "sandbox"
    STATIC_ANALYSIS = "static_analysis"
    DYNAMIC_ANALYSIS = "dynamic_analysis"
    BACKTEST = "backtest"
    SHADOW = "shadow"
    CANARY = "canary"
    PRODUCTION = "production"


class StageVerdict(Enum):
    """Stage verdict enumeration"""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CONDITIONAL = "conditional"
    DEFERRED = "deferred"
    ERROR = "error"


class PatchPriority(Enum):
    """Patch priority enumeration"""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    ROUTINE = "routine"


# Legal patch transitions
LEGAL_PATCH_TRANSITIONS = {
    PatchStage.PROPOSED: [PatchStage.ANALYZED, PatchStage.CANCELLED, PatchStage.REJECTED],
    PatchStage.ANALYZED: [
        PatchStage.VALIDATED,
        PatchStage.REJECTED,
        PatchStage.CANCELLED,
        PatchStage.STATIC_ANALYSIS,
    ],
    PatchStage.STATIC_ANALYSIS: [
        PatchStage.VALIDATED,
        PatchStage.DYNAMIC_ANALYSIS,
        PatchStage.REJECTED,
        PatchStage.CANCELLED,
        PatchStage.BACKTEST,
    ],
    PatchStage.DYNAMIC_ANALYSIS: [
        PatchStage.VALIDATED,
        PatchStage.SANDBOX,
        PatchStage.REJECTED,
        PatchStage.CANCELLED,
    ],
    PatchStage.BACKTEST: [
        PatchStage.VALIDATED,
        PatchStage.SHADOW,
        PatchStage.REJECTED,
        PatchStage.CANCELLED,
    ],
    PatchStage.SHADOW: [
        PatchStage.APPROVED,
        PatchStage.REJECTED,
        PatchStage.CANCELLED,
        PatchStage.CANARY,
    ],
    PatchStage.CANARY: [
        PatchStage.APPROVED,
        PatchStage.REJECTED,
        PatchStage.CANCELLED,
        PatchStage.PRODUCTION,
    ],
    PatchStage.PRODUCTION: [
        PatchStage.COMPLETED,
        PatchStage.FAILED,
        PatchStage.ROLLED_BACK,
        PatchStage.REJECTED,
    ],
    PatchStage.VALIDATED: [
        PatchStage.APPROVED,
        PatchStage.REJECTED,
        PatchStage.CANCELLED,
        PatchStage.SANDBOX,
    ],
    PatchStage.APPROVED: [PatchStage.PLANNED, PatchStage.CANCELLED, PatchStage.REJECTED],
    PatchStage.PLANNED: [
        PatchStage.IN_PROGRESS,
        PatchStage.CANCELLED,
        PatchStage.REJECTED,
        PatchStage.SANDBOX,
    ],
    PatchStage.SANDBOX: [PatchStage.APPROVED, PatchStage.REJECTED, PatchStage.CANCELLED],
    PatchStage.IN_PROGRESS: [
        PatchStage.COMPLETED,
        PatchStage.FAILED,
        PatchStage.ROLLED_BACK,
        PatchStage.REJECTED,
    ],
    PatchStage.COMPLETED: [],
    PatchStage.FAILED: [PatchStage.PROPOSED, PatchStage.CANCELLED, PatchStage.REJECTED],
    PatchStage.ROLLED_BACK: [PatchStage.PROPOSED, PatchStage.CANCELLED, PatchStage.REJECTED],
    PatchStage.CANCELLED: [],
    PatchStage.REJECTED: [PatchStage.PROPOSED],
}


class PatchPipelineError(Exception):
    """Patch pipeline error"""

    def __init__(
        self, message: str, patch_id: str, current_stage: PatchStage, attempted_stage: PatchStage
    ):
        self.patch_id = patch_id
        self.current_stage = current_stage
        self.attempted_stage = attempted_stage
        super().__init__(
            f"{message} (patch: {patch_id}, from {current_stage.value} to {attempted_stage.value})"
        )


def is_legal_transition(current_stage: PatchStage, target_stage: PatchStage) -> bool:
    """Check if a patch transition is legal"""
    return target_stage in LEGAL_PATCH_TRANSITIONS.get(current_stage, [])


@dataclass
class PatchMetadata:
    """Patch metadata information"""

    patch_id: str
    version: str
    author: str
    timestamp: float = field(default_factory=time.time)
    description: str = ""
    dependencies: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "patch_id": self.patch_id,
            "version": self.version,
            "author": self.author,
            "timestamp": self.timestamp,
            "description": self.description,
            "dependencies": self.dependencies,
            "tags": self.tags,
            "metadata": self.metadata,
        }


@dataclass
class PatchRecord:
    """Patch record for tracking"""

    record_id: str
    patch_id: str
    stage: PatchStage
    verdict: StageVerdict
    timestamp: float = field(default_factory=time.time)
    actor: str = ""
    notes: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "record_id": self.record_id,
            "patch_id": self.patch_id,
            "stage": self.stage.value,
            "verdict": self.verdict.value,
            "timestamp": self.timestamp,
            "actor": self.actor,
            "notes": self.notes,
            "metadata": self.metadata,
        }


@dataclass
class PatchTransition:
    """Patch transition information"""

    transition_id: str
    patch_id: str
    from_stage: PatchStage
    to_stage: PatchStage
    timestamp: float = field(default_factory=time.time)
    actor: str = ""
    justification: str = ""
    approved_by: str = ""

    def is_legal(self) -> bool:
        """Check if transition is legal"""
        return is_legal_transition(self.from_stage, self.to_stage)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "transition_id": self.transition_id,
            "patch_id": self.patch_id,
            "from_stage": self.from_stage.value,
            "to_stage": self.to_stage.value,
            "timestamp": self.timestamp,
            "actor": self.actor,
            "justification": self.justification,
            "approved_by": self.approved_by,
        }


class PatchApprovalBridgeProtocol:
    """Protocol for patch approval bridge"""

    def request_approval(self, patch_id: str, stage: PatchStage, context: Dict[str, Any]) -> bool:
        """Request approval for a patch stage transition"""
        return True

    def get_approval_status(self, patch_id: str) -> StageVerdict:
        """Get the approval status for a patch"""
        return StageVerdict.PENDING

    def submit_verdict(
        self, patch_id: str, verdict: StageVerdict, actor: str, notes: str = ""
    ) -> bool:
        """Submit a verdict for a patch"""
        return True

    def get_required_approvers(self, patch_id: str, stage: PatchStage) -> List[str]:
        """Get the list of required approvers for a patch stage"""
        return []

    def notify_approvers(self, patch_id: str, stage: PatchStage) -> bool:
        """Notify required approvers about a patch needing approval"""
        return True


@dataclass
class Patch:
    """Patch definition"""

    patch_id: str
    patch_kind: str
    description: str
    metadata: PatchMetadata
    stage: PatchStage = PatchStage.PROPOSED
    verdict: StageVerdict = StageVerdict.PENDING
    priority: PatchPriority = PatchPriority.MEDIUM
    target_modules: List[str] = field(default_factory=list)
    changes: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

    def is_approved(self) -> bool:
        """Check if patch is approved"""
        return self.verdict == StageVerdict.APPROVED

    def is_complete(self) -> bool:
        """Check if patch is complete"""
        return self.stage == PatchStage.COMPLETED

    def advance_stage(self, new_stage: PatchStage) -> bool:
        """Advance patch to next stage"""
        self.stage = new_stage
        self.timestamp = time.time()
        return True

    def set_verdict(self, verdict: StageVerdict) -> None:
        """Set the verdict for the current stage"""
        self.verdict = verdict
        self.timestamp = time.time()


class PatchPipelineProtocol:
    """Protocol for patch pipeline operations"""

    def submit_patch(self, patch: Patch) -> bool:
        """Submit a patch to the pipeline"""
        return True

    def advance_stage(self, patch_id: str, new_stage: PatchStage, actor: str) -> bool:
        """Advance a patch to the next stage"""
        return (
            is_legal_transition(get_patch_registry().get_patch(patch_id).stage, new_stage)
            if get_patch_registry().get_patch(patch_id)
            else False
        )

    def get_patch_status(self, patch_id: str) -> Optional[Dict[str, Any]]:
        """Get the current status of a patch"""
        patch = get_patch_registry().get_patch(patch_id)
        return patch.to_dict() if patch else None

    def list_patches_by_stage(self, stage: PatchStage) -> List[Patch]:
        """List all patches in a specific stage"""
        return get_patch_registry().get_patches_by_stage(stage)

    def submit_verdict(
        self, patch_id: str, verdict: StageVerdict, actor: str, notes: str = ""
    ) -> bool:
        """Submit a verdict for a patch"""
        return (
            get_patch_registry().approve_patch(patch_id)
            if verdict == StageVerdict.APPROVED
            else False
        )


@dataclass
class PatchApprovalDecision:
    """Patch approval decision"""

    decision_id: str
    patch_id: str
    stage: PatchStage
    verdict: StageVerdict
    approver: str
    timestamp: float = field(default_factory=time.time)
    justification: str = ""
    conditions: List[str] = field(default_factory=list)

    def is_approved(self) -> bool:
        """Check if decision is approved"""
        return self.verdict == StageVerdict.APPROVED

    def is_conditional(self) -> bool:
        """Check if decision is conditional"""
        return self.verdict == StageVerdict.CONDITIONAL

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "decision_id": self.decision_id,
            "patch_id": self.patch_id,
            "stage": self.stage.value,
            "verdict": self.verdict.value,
            "approver": self.approver,
            "timestamp": self.timestamp,
            "justification": self.justification,
            "conditions": self.conditions,
        }


class PatchRegistry:
    """Registry for patch management"""

    def __init__(self):
        self._patches: Dict[str, Patch] = {}
        self._patches_by_stage: Dict[PatchStage, List[str]] = {stage: [] for stage in PatchStage}

    def register_patch(self, patch: Patch) -> bool:
        """Register a patch"""
        self._patches[patch.patch_id] = patch
        self._patches_by_stage[patch.stage].append(patch.patch_id)
        return True

    def get_patch(self, patch_id: str) -> Optional[Patch]:
        """Get a specific patch"""
        return self._patches.get(patch_id)

    def get_patches_by_stage(self, stage: PatchStage) -> List[Patch]:
        """Get all patches in a stage"""
        patch_ids = self._patches_by_stage.get(stage, [])
        return [self._patches[pid] for pid in patch_ids if pid in self._patches]

    def get_approved_patches(self) -> List[Patch]:
        """Get all approved patches"""
        return [p for p in self._patches.values() if p.is_approved()]

    def advance_patch(self, patch_id: str, new_stage: PatchStage) -> bool:
        """Advance a patch to a new stage"""
        patch = self.get_patch(patch_id)
        if patch:
            old_stage = patch.stage
            if patch.advance_stage(new_stage):
                self._patches_by_stage[old_stage].remove(patch_id)
                self._patches_by_stage[new_stage].append(patch_id)
                return True
        return False


# Global patch registry
_patch_registry: Optional[PatchRegistry] = None


def get_patch_registry() -> PatchRegistry:
    """Get the global patch registry"""
    global _patch_registry
    if _patch_registry is None:
        _patch_registry = PatchRegistry()
    return _patch_registry


def create_patch(patch_id: str, patch_kind: str, description: str, author: str) -> Patch:
    """Create a new patch"""
    metadata = PatchMetadata(
        patch_id=patch_id, version="1.0.0", author=author, description=description
    )
    return Patch(
        patch_id=patch_id, patch_kind=patch_kind, description=description, metadata=metadata
    )


__all__ = [
    "PatchStage",
    "StageVerdict",
    "PatchPriority",
    "LEGAL_PATCH_TRANSITIONS",
    "PatchPipelineError",
    "is_legal_transition",
    "PatchMetadata",
    "PatchRecord",
    "PatchTransition",
    "PatchApprovalBridgeProtocol",
    "PatchApprovalDecision",
    "PatchPipelineProtocol",
    "Patch",
    "PatchRegistry",
    "get_patch_registry",
    "create_patch",
]
