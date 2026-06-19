"""Stub runtime context builder."""

from .runtime_context import RuntimeContext, DEFAULT_LATENCY_BUDGET_NS, RuntimeMonitorView

def build_runtime_context(**kwargs: object) -> RuntimeContext:
    """Stub runtime context builder."""
    return RuntimeContext()