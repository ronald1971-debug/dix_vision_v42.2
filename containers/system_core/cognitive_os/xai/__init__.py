"""Explainable AI System."""

from .explainable_ai import (
    ExplainableAI,
    get_explainable_ai,
)

# Alias for consistency
get_xai_system = get_explainable_ai

__all__ = [
    "ExplainableAI",
    "get_explainable_ai",
    "get_xai_system",
]
