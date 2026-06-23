"""Institutional Memory — long-term strategic memory.

Stores: Important Discoveries, Major Mistakes, Successful Evolutions,
Critical Failures for years.

(Item 36 — cognitive operating system roadmap)
"""

from cognitive_engine.institutional_memory.institutional_memory import (
    InstitutionalMemory,
    MemoryEntry,
    get_institutional_memory,
)

__all__ = [
    "InstitutionalMemory",
    "MemoryEntry",
    "get_institutional_memory",
]
