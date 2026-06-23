"""
Browser layer - Phase 3 implementation
"""

from browser_controller import BrowserAction, BrowserController, BrowserState, BrowserType
from profile_manager import BrowserProfile, ProfileManager, ProfileType
from tab_manager import TabInfo, TabManager, TabState

__all__ = [
    "BrowserController",
    "BrowserState",
    "BrowserType",
    "BrowserAction",
    "TabManager",
    "TabState",
    "TabInfo",
    "ProfileManager",
    "ProfileType",
    "BrowserProfile",
]
