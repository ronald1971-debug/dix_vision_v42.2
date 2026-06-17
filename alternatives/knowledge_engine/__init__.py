"""
knowledge_engine
DIX VISION v42.2 — Knowledge Engine

Production-grade knowledge management capabilities including knowledge acquisition,
reasoning, inference, validation, retrieval, and updating.
"""

from knowledge_engine.orchestrator import (
    KnowledgeOperation,
    KnowledgeOrchestrator,
    get_knowledge_orchestrator,
)

__all__ = [
    "KnowledgeOperation",
    "KnowledgeOrchestrator",
    "get_knowledge_orchestrator",
]