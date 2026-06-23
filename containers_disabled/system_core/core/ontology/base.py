from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any


class ObjectKind(StrEnum):
    TRADER = "TRADER"
    STRATEGY = "STRATEGY"
    SIGNAL = "SIGNAL"
    MARKET = "MARKET"
    PORTFOLIO = "PORTFOLIO"
    EXECUTION = "EXECUTION"
    BELIEF = "BELIEF"
    KNOWLEDGE = "KNOWLEDGE"
    THEORY = "THEORY"
    REGIME = "REGIME"
    EVIDENCE = "EVIDENCE"
    AUDIT_RECORD = "AUDIT_RECORD"


@dataclass(frozen=True, slots=True)
class ObjectVersion:
    major: int = 0
    minor: int = 1
    patch: int = 0

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"


@dataclass(frozen=True, slots=True)
class CognitiveObject:
    object_id: str = ""
    object_type: ObjectKind = ObjectKind.BELIEF
    ts_ns: int = 0
    version: ObjectVersion = ObjectVersion()
    evidence_ids: tuple[str, ...] = ()
    contributor_chain: tuple[str, ...] = ()
    tags: tuple[str, ...] = ()

    def with_evidence(self, *evidence_ids: str) -> CognitiveObject:
        new_ids = self.evidence_ids + tuple(evidence_ids)
        return self.replace(evidence_ids=new_ids)

    def with_contributor(self, contributor: str) -> CognitiveObject:
        new_chain = self.contributor_chain + (contributor,)
        return self.replace(contributor_chain=new_chain)

    def replace(self, **changes: Any) -> CognitiveObject:
        import dataclasses

        return dataclasses.replace(self, **changes)

    @classmethod
    def create(cls, **kwargs: Any) -> CognitiveObject:
        defaults: dict[str, Any] = {
            "object_type": ObjectKind.BELIEF,
            "ts_ns": 0,
            "version": ObjectVersion(),
            "evidence_ids": (),
            "contributor_chain": (),
            "tags": (),
        }
        defaults.update(kwargs)
        return cls(**defaults)
