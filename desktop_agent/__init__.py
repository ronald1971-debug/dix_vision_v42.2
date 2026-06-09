"""
Desktop AgentOS - Cognitive Environment Platform for DIXVISION v42.2

This module provides the foundational runtime and orchestration layer for
INDIRA and DYON agents to interact with browsers, desktop applications,
and other cognitive environments through governed and observable interfaces.
"""

__version__ = "42.2.0"
__author__ = "DIXVISION"

from .runtime import AgentRuntime
from .agents import INDIRAAgent, DYONAgent
from .browser import BrowserCognitiveBridge
from .desktop import DesktopCognitiveBridge

__all__ = [
    "AgentRuntime",
    "INDIRAAgent",
    "DYONAgent",
    "BrowserCognitiveBridge",
    "DesktopCognitiveBridge",
]
