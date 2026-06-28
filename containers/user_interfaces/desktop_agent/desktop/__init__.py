"""
Desktop layer - Phase 5 implementation
"""

from application_manager import Application, ApplicationManager, ApplicationState
from desktop_controller import DesktopAction, DesktopActionType, DesktopController, DesktopState
from window_manager import Window, WindowManager, WindowState

__all__ = [
    "DesktopController",
    "DesktopActionType",
    "DesktopState",
    "DesktopAction",
    "ApplicationManager",
    "ApplicationState",
    "Application",
    "WindowManager",
    "WindowState",
    "Window",
]
