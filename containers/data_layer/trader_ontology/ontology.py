"""Trader Ontology — machine-understandable relationships between traders.

5,000+ trader profiles require:
    - TraderOntology (not just trader records)
    - Relationships become machine-understandable

Example trader types:
    - Scalper
    - Momentum Trader
    - Mean Reversion Trader
    - Options Trader
    - Liquidity Hunter
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class TraderType(StrEnum):
    SCALPER = "SCALPER"
    MOMENTUM = "MOMENTUM"
    MEAN_REVERSION = "MEAN_REVERSION"
    OPTIONS = "OPTIONS"
    LIQUIDITY_HUNTER = "LIQUIDITY_HUNTER"
    ARBITRAGE = "ARBITRAGE"
    SWING = "SWING"
    POSITION = "POSITION"


class RelationshipType(StrEnum):
    SIMILAR = "SIMILAR"
    CONTRARIAN = "CONTRARIAN"
    REPLICATES = "REPLICATES"
    MENTORS = "MENTORS"
    COMPETES_WITH = "COMPETES_WITH"


@dataclass(frozen=True, slots=True)
class TraderProfile:
    """Machine-understandable trader profile."""

    trader_id: str
    trader_type: TraderType
    name: str = ""
    performance: dict[str, float] = field(default_factory=dict)
    regime_performance: dict[str, float] = field(default_factory=dict)
    confidence: float = 0.0
    first_seen: int = field(default_factory=lambda: time.time_ns())
    last_updated: int = field(default_factory=lambda: time.time_ns())
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class TraderRelationship:
    """Relationship between two traders."""

    source_id: str
    target_id: str
    relationship_type: RelationshipType
    strength: float  # 0.0 to 1.0
    evidence: tuple[str, ...] = ()


class TraderOntology:
    """Ontology of trader profiles and their relationships.

    Supports:
        - 5000+ trader profiles
        - Relationship queries
        - Type-based clustering
        - Similarity search
    """

    def __init__(self) -> None:
        self._profiles: dict[str, TraderProfile] = {}
        self._relationships: list[TraderRelationship] = []
        self._type_index: dict[TraderType, list[str]] = {}

    def add_profile(self, profile: TraderProfile) -> None:
        self._profiles[profile.trader_id] = profile
        if profile.trader_type not in self._type_index:
            self._type_index[profile.trader_type] = []
        self._type_index[profile.trader_type].append(profile.trader_id)

    def get_profile(self, trader_id: str) -> TraderProfile | None:
        return self._profiles.get(trader_id)

    def query_by_type(self, trader_type: TraderType) -> tuple[TraderProfile, ...]:
        ids = self._type_index.get(trader_type, [])
        return tuple(self._profiles[pid] for pid in ids if pid in self._profiles)

    def add_relationship(self, rel: TraderRelationship) -> None:
        self._relationships.append(rel)

    def get_relationships(self, trader_id: str) -> tuple[TraderRelationship, ...]:
        return tuple(
            r for r in self._relationships
            if r.source_id == trader_id or r.target_id == trader_id
        )

    def get_similar_traders(
        self, trader_id: str, threshold: float = 0.5
    ) -> tuple[TraderProfile, ...]:
        rels = [
            r for r in self._relationships
            if r.source_id == trader_id
            and r.relationship_type == RelationshipType.SIMILAR
            and r.strength >= threshold
        ]
        return tuple(
            self._profiles[r.target_id] for r in rels if r.target_id in self._profiles
        )

    @property
    def profile_count(self) -> int:
        return len(self._profiles)


def derive_trader_type(profile: TraderProfile) -> TraderType:
    """Infer trader type from profile characteristics."""
    regimes = profile.regime_performance
    if not regimes:
        return TraderType.SCALPER

    if "scalp" in profile.performance:
        return TraderType.SCALPER
    if "trend" in regimes:
        return TraderType.MOMENTUM
    if "range" in regimes:
        return TraderType.MEAN_REVERSION

    return TraderType.SCALPER  # default