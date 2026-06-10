"""
Cognitive Environment Layer - Universal environment abstraction
"""

__all__ = [
    "EnvironmentInterface",
    "EnvironmentRegistry", 
    "EnvironmentManager",
]

def __getattr__(name):
    if name == "EnvironmentInterface":
        from .interface import EnvironmentInterface
        return EnvironmentInterface
    elif name == "EnvironmentRegistry":
        from .registry import EnvironmentRegistry
        return EnvironmentRegistry
    elif name == "EnvironmentManager":
        from .manager import EnvironmentManager
        return EnvironmentManager
    else:
        raise AttributeError(f"module {__name__} has no attribute {name}")
