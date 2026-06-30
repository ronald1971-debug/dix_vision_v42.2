"""
DIX VISION Platform Abstraction Layer

Provides a unified interface for platform-specific operations,
normalizing differences between Windows, Linux, WSL, and Docker environments.

Usage:
    from runtime.platform_abstraction import get_platform_adapter, Platform
    
    adapter = get_platform_adapter()
    platform = adapter.detect_platform()
    path = adapter.normalize_path("/some/path")
"""

from __future__ import annotations

import os
import platform
import subprocess
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any


class Platform(Enum):
    """Supported platforms."""
    WINDOWS = "windows"
    LINUX = "linux"
    MACOS = "macos"
    WSL = "wsl"
    DOCKER = "docker"


@dataclass
class PlatformInfo:
    """Platform information."""
    platform: Platform
    python_version: str
    os_version: str
    architecture: str
    is_wsl: bool
    is_docker: bool
    path_separator: str
    line_ending: str


class PlatformAdapter(ABC):
    """Abstract base class for platform-specific operations."""
    
    @abstractmethod
    def detect_platform(self) -> Platform:
        """Detect the current platform."""
        pass
    
    @abstractmethod
    def get_platform_info(self) -> PlatformInfo:
        """Get detailed platform information."""
        pass
    
    @abstractmethod
    def normalize_path(self, path: str) -> str:
        """Normalize a path for the current platform."""
        pass
    
    @abstractmethod
    def get_environment_variable(self, name: str, default: str = None) -> str | None:
        """Get environment variable with platform-specific handling."""
        pass
    
    @abstractmethod
    def set_environment_variable(self, name: str, value: str) -> None:
        """Set environment variable with platform-specific handling."""
        pass
    
    @abstractmethod
    def execute_command(self, command: list[str]) -> subprocess.CompletedProcess:
        """Execute a command with platform-specific handling."""
        pass
    
    @abstractmethod
    def get_user_directory(self) -> Path:
        """Get user home directory."""
        pass
    
    @abstractmethod
    def get_config_directory(self) -> Path:
        """Get user config directory."""
        pass
    
    @abstractmethod
    def get_cache_directory(self) -> Path:
        """Get user cache directory."""
        pass
    
    @abstractmethod
    def get_data_directory(self) -> Path:
        """Get user data directory."""
        pass


class WindowsPlatformAdapter(PlatformAdapter):
    """Windows-specific platform adapter."""
    
    def detect_platform(self) -> Platform:
        return Platform.WINDOWS
    
    def get_platform_info(self) -> PlatformInfo:
        return PlatformInfo(
            platform=Platform.WINDOWS,
            python_version=sys.version,
            os_version=platform.version(),
            architecture=platform.machine(),
            is_wsl=False,
            is_docker=self._check_docker(),
            path_separator="\\",
            line_ending="\r\n"
        )
    
    def _check_docker(self) -> bool:
        """Check if running in Docker."""
        return os.path.exists("/.dockerenv")
    
    def normalize_path(self, path: str) -> str:
        """Normalize path for Windows."""
        # Convert forward slashes to backslashes
        path = path.replace("/", "\\")
        # Expand user home directory
        if path.startswith("~"):
            path = os.path.expanduser(path)
        return str(Path(path).absolute())
    
    def get_environment_variable(self, name: str, default: str = None) -> str | None:
        """Get environment variable."""
        return os.environ.get(name, default)
    
    def set_environment_variable(self, name: str, value: str) -> None:
        """Set environment variable."""
        os.environ[name] = value
    
    def execute_command(self, command: list[str]) -> subprocess.CompletedProcess:
        """Execute command on Windows."""
        return subprocess.run(command, capture_output=True, text=True, shell=True)
    
    def get_user_directory(self) -> Path:
        """Get user home directory on Windows."""
        return Path(os.path.expanduser("~"))
    
    def get_config_directory(self) -> Path:
        """Get user config directory on Windows."""
        # Use AppData/Local for config
        appdata_local = os.environ.get("LOCALAPPDATA")
        if appdata_local:
            return Path(appdata_local) / "DIX VISION"
        return self.get_user_directory() / ".config" / "dix_vision"
    
    def get_cache_directory(self) -> Path:
        """Get user cache directory on Windows."""
        appdata_local = os.environ.get("LOCALAPPDATA")
        if appdata_local:
            return Path(appdata_local) / "DIX VISION" / "cache"
        return self.get_user_directory() / ".cache" / "dix_vision"
    
    def get_data_directory(self) -> Path:
        """Get user data directory on Windows."""
        # Use AppData/Local for data
        appdata_local = os.environ.get("LOCALAPPDATA")
        if appdata_local:
            return Path(appdata_local) / "DIX VISION" / "data"
        return self.get_user_directory() / ".local" / "share" / "dix_vision"


class LinuxPlatformAdapter(PlatformAdapter):
    """Linux-specific platform adapter."""
    
    def __init__(self):
        self._is_wsl = self._check_wsl()
    
    def detect_platform(self) -> Platform:
        if self._is_wsl:
            return Platform.WSL
        return Platform.LINUX
    
    def get_platform_info(self) -> PlatformInfo:
        return PlatformInfo(
            platform=self.detect_platform(),
            python_version=sys.version,
            os_version=platform.version(),
            architecture=platform.machine(),
            is_wsl=self._is_wsl,
            is_docker=self._check_docker(),
            path_separator="/",
            line_ending="\n"
        )
    
    def _check_wsl(self) -> bool:
        """Check if running in WSL."""
        try:
            with open("/proc/version", "r") as f:
                return "microsoft" in f.read().lower()
        except (FileNotFoundError, IOError):
            return False
    
    def _check_docker(self) -> bool:
        """Check if running in Docker."""
        return os.path.exists("/.dockerenv")
    
    def normalize_path(self, path: str) -> str:
        """Normalize path for Linux."""
        # Convert backslashes to forward slashes
        path = path.replace("\\", "/")
        # Expand user home directory
        if path.startswith("~"):
            path = os.path.expanduser(path)
        return str(Path(path).absolute())
    
    def get_environment_variable(self, name: str, default: str = None) -> str | None:
        """Get environment variable."""
        return os.environ.get(name, default)
    
    def set_environment_variable(self, name: str, value: str) -> None:
        """Set environment variable."""
        os.environ[name] = value
    
    def execute_command(self, command: list[str]) -> subprocess.CompletedProcess:
        """Execute command on Linux."""
        return subprocess.run(command, capture_output=True, text=True)
    
    def get_user_directory(self) -> Path:
        """Get user home directory on Linux."""
        return Path(os.path.expanduser("~"))
    
    def get_config_directory(self) -> Path:
        """Get user config directory on Linux."""
        # Follow XDG Base Directory Specification
        xdg_config = os.environ.get("XDG_CONFIG_HOME")
        if xdg_config:
            return Path(xdg_config) / "dix_vision"
        return self.get_user_directory() / ".config" / "dix_vision"
    
    def get_cache_directory(self) -> Path:
        """Get user cache directory on Linux."""
        xdg_cache = os.environ.get("XDG_CACHE_HOME")
        if xdg_cache:
            return Path(xdg_cache) / "dix_vision"
        return self.get_user_directory() / ".cache" / "dix_vision"
    
    def get_data_directory(self) -> Path:
        """Get user data directory on Linux."""
        xdg_data = os.environ.get("XDG_DATA_HOME")
        if xdg_data:
            return Path(xdg_data) / "dix_vision"
        return self.get_user_directory() / ".local" / "share" / "dix_vision"


class MacOSPlatformAdapter(PlatformAdapter):
    """macOS-specific platform adapter."""
    
    def detect_platform(self) -> Platform:
        return Platform.MACOS
    
    def get_platform_info(self) -> PlatformInfo:
        return PlatformInfo(
            platform=Platform.MACOS,
            python_version=sys.version,
            os_version=platform.mac_ver()[0],
            architecture=platform.machine(),
            is_wsl=False,
            is_docker=self._check_docker(),
            path_separator="/",
            line_ending="\n"
        )
    
    def _check_docker(self) -> bool:
        """Check if running in Docker."""
        return os.path.exists("/.dockerenv")
    
    def normalize_path(self, path: str) -> str:
        """Normalize path for macOS."""
        # Convert backslashes to forward slashes
        path = path.replace("\\", "/")
        # Expand user home directory
        if path.startswith("~"):
            path = os.path.expanduser(path)
        return str(Path(path).absolute())
    
    def get_environment_variable(self, name: str, default: str = None) -> str | None:
        """Get environment variable."""
        return os.environ.get(name, default)
    
    def set_environment_variable(self, name: str, value: str) -> None:
        """Set environment variable."""
        os.environ[name] = value
    
    def execute_command(self, command: list[str]) -> subprocess.CompletedProcess:
        """Execute command on macOS."""
        return subprocess.run(command, capture_output=True, text=True)
    
    def get_user_directory(self) -> Path:
        """Get user home directory on macOS."""
        return Path(os.path.expanduser("~"))
    
    def get_config_directory(self) -> Path:
        """Get user config directory on macOS."""
        # Use Library/Application Support
        return self.get_user_directory() / "Library" / "Application Support" / "DIX VISION"
    
    def get_cache_directory(self) -> Path:
        """Get user cache directory on macOS."""
        return self.get_user_directory() / "Library" / "Caches" / "DIX VISION"
    
    def get_data_directory(self) -> Path:
        """Get user data directory on macOS."""
        return self.get_user_directory() / "Library" / "Application Support" / "DIX VISION" / "data"


class PlatformManager:
    """Centralized platform management."""
    
    def __init__(self):
        self.adapter = self._create_adapter()
        self.platform_info = self.adapter.get_platform_info()
    
    def _create_adapter(self) -> PlatformAdapter:
        """Create appropriate platform adapter."""
        system = platform.system().lower()
        
        if system == "windows":
            return WindowsPlatformAdapter()
        elif system == "linux":
            return LinuxPlatformAdapter()
        elif system == "darwin":
            return MacOSPlatformAdapter()
        else:
            # Fallback to Linux adapter for unknown systems
            return LinuxPlatformAdapter()
    
    def get_adapter(self) -> PlatformAdapter:
        """Get the platform adapter."""
        return self.adapter
    
    def get_platform(self) -> Platform:
        """Get the current platform."""
        return self.platform_info.platform
    
    def get_platform_info(self) -> PlatformInfo:
        """Get platform information."""
        return self.platform_info
    
    def normalize_path(self, path: str) -> str:
        """Normalize a path for the current platform."""
        return self.adapter.normalize_path(path)
    
    def get_environment_variable(self, name: str, default: str = None) -> str | None:
        """Get environment variable."""
        return self.adapter.get_environment_variable(name, default)
    
    def set_environment_variable(self, name: str, value: str) -> None:
        """Set environment variable."""
        return self.adapter.set_environment_variable(name, value)
    
    def execute_command(self, command: list[str]) -> subprocess.CompletedProcess:
        """Execute command."""
        return self.adapter.execute_command(command)
    
    def get_user_directory(self) -> Path:
        """Get user home directory."""
        return self.adapter.get_user_directory()
    
    def get_config_directory(self) -> Path:
        """Get user config directory."""
        return self.adapter.get_config_directory()
    
    def get_cache_directory(self) -> Path:
        """Get user cache directory."""
        return self.adapter.get_cache_directory()
    
    def get_data_directory(self) -> Path:
        """Get user data directory."""
        return self.adapter.get_data_directory()
    
    def setup_directories(self) -> dict[str, Path]:
        """Setup and ensure all required directories exist."""
        directories = {
            "config": self.get_config_directory(),
            "cache": self.get_cache_directory(),
            "data": self.get_data_directory(),
        }
        
        for name, path in directories.items():
            path.mkdir(parents=True, exist_ok=True)
        
        return directories


# Global instance
_platform_manager: PlatformManager | None = None


def get_platform_manager() -> PlatformManager:
    """Get global platform manager instance."""
    global _platform_manager
    if _platform_manager is None:
        _platform_manager = PlatformManager()
    return _platform_manager


def get_platform_adapter() -> PlatformAdapter:
    """Get platform adapter (convenience function)."""
    return get_platform_manager().get_adapter()


def get_platform() -> Platform:
    """Get current platform (convenience function)."""
    return get_platform_manager().get_platform()


def normalize_path(path: str) -> str:
    """Normalize path for current platform (convenience function)."""
    return get_platform_manager().normalize_path(path)


__all__ = [
    "Platform",
    "PlatformInfo",
    "PlatformAdapter",
    "WindowsPlatformAdapter",
    "LinuxPlatformAdapter",
    "MacOSPlatformAdapter",
    "PlatformManager",
    "get_platform_manager",
    "get_platform_adapter",
    "get_platform",
    "normalize_path",
]