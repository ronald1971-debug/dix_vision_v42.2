"""Knowledge Preservation - prevents learning→forgetting."""

from cognitive_engine.knowledge_preservation.archive import KnowledgeArchive
from cognitive_engine.knowledge_preservation.preservation import KnowledgePreserver
from cognitive_engine.knowledge_preservation.snapshot import KnowledgeSnapshot

__all__ = [
    "KnowledgeArchive",
    "KnowledgePreserver",
    "KnowledgeSnapshot",
]
