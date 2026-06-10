"""
Desktop AgentOS - Cognitive Environment Platform for DIXVISION v42.2

This module provides the foundational runtime and orchestration layer for
INDIRA and DYON agents to interact with browsers, desktop applications,
and other cognitive environments through governed and observable interfaces.
"""

__version__ = "42.2.0"
__author__ = "DIXVISION"

# Lazy imports to avoid circular dependencies
def __getattr__(name):
    if name == "AgentRuntime":
        from .runtime import AgentRuntime
        return AgentRuntime
    elif name == "INDIRAAgent":
        from .agents import INDIRAAgent
        return INDIRAAgent
    elif name == "DYONAgent":
        from .agents import DYONAgent
        return DYONAgent
    elif name == "BrowserCognitiveBridge":
        from .browser import BrowserCognitiveBridge
        return BrowserCognitiveBridge
    elif name == "DesktopCognitiveBridge":
        from .desktop import DesktopCognitiveBridge
        return DesktopCognitiveBridge
    else:
        raise AttributeError(f"module {__name__} has no attribute {name}")

__all__ = [
    "AgentRuntime",
    "INDIRAAgent",
    "DYONAgent",
    "BrowserCognitiveBridge",
    "DesktopCognitiveBridge",
]
