"""Stub runtime context."""

DEFAULT_LATENCY_BUDGET_NS = 100000000  # 100ms


class RuntimeMonitorView:
    """Stub runtime monitor view."""

    def __init__(self, **kwargs: object):
        pass


class RuntimeContext:
    """Stub runtime context."""

    def __init__(self, **kwargs: object):
        pass


def build_runtime_context(**kwargs: object) -> RuntimeContext:
    """Stub runtime context builder."""
    return RuntimeContext()