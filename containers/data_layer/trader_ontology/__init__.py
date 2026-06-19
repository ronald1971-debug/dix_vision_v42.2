"""Trader Ontology — machine-understandable trader relationships.

Manages 5000+ trader profiles with:
    - Type-based clustering
    - Similarity relationships
    - Performance tracking
"""

from trader_ontology.ontology import (
    RelationshipType,
    TraderOntology,
    TraderProfile,
    TraderRelationship,
    TraderType,
    derive_trader_type,
)

__all__ = [
    "RelationshipType",
    "TraderOntology",
    "TraderProfile",
    "TraderRelationship",
    "TraderType",
    "derive_trader_type",
]