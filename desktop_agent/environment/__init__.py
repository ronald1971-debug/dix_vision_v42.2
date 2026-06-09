"""
Cognitive Environment Layer - Universal environment abstraction
"""

from .interface import EnvironmentInterface
from .registry import EnvironmentRegistry
from .manager import EnvironmentManager

__all__ = [
    "EnvironmentInterface",
    "EnvironmentRegistry",
    "EnvironmentManager",
]
