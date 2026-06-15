"""Governance Domains.

Domain-specific governance modules for the consolidated governance system.
Each domain handles specialized governance for its area of responsibility.
"""

# Import domain modules
from . import financial
from . import operator

__all__ = [
    "financial",
    "operator",
]