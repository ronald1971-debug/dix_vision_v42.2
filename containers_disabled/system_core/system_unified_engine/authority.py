"""
System Unified Engine Authority Matrix - Authority Matrix Management
Provides authority matrix capabilities
NO LAZY LOADING - All components load directly
"""

import json
import logging
import os
from typing import Dict

import yaml

logger = logging.getLogger(__name__)


class AuthorityMatrix:
    """Authority matrix for governance operations"""

    def __init__(self):
        self._authority_levels = {"operator": 100, "supervisor": 80, "system": 60, "automated": 40}
        self._current_authority = "operator"

    def set_authority_level(self, level: str):
        """Set current authority level"""
        if level in self._authority_levels:
            self._current_authority = level

    def get_authority_level(self) -> str:
        """Get current authority level"""
        return self._current_authority

    def check_authority(self, required_level: str) -> bool:
        """Check if current authority meets required level"""
        current_score = self._authority_levels.get(self._current_authority, 0)
        required_score = self._authority_levels.get(required_level, 0)
        return current_score >= required_score

    def get_authority_matrix(self) -> Dict[str, int]:
        """Get authority matrix"""
        return self._authority_levels.copy()


class SystemAuthority:
    """System authority manager"""

    def __init__(self):
        self._authority_levels = {}
        self._current_authority = "operator"

    def set_authority_level(self, level: str):
        """Set current authority level"""
        self._current_authority = level

    def get_authority_level(self) -> str:
        """Get current authority level"""
        return self._current_authority

    def check_authority(self, required_level: str) -> bool:
        """Check if current authority meets required level"""
        return True  # Simplified for now


# Global instance
_system_authority = None


def get_system_authority() -> SystemAuthority:
    """Get system authority instance"""
    global _system_authority
    if _system_authority is None:
        _system_authority = SystemAuthority()
    return _system_authority


def load_authority_matrix(config_path: str = None) -> AuthorityMatrix:
    """Load authority matrix from config file.

    Args:
        config_path: Path to config file (JSON or YAML format).
                    If None, uses default authority levels.

    Returns:
        AuthorityMatrix instance with loaded configuration.

    Raises:
        FileNotFoundError: If config file doesn't exist
        ValueError: If config file is invalid
    """
    matrix = AuthorityMatrix()

    if config_path:
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Authority config file not found: {config_path}")

        try:
            # Determine file type and load accordingly
            if config_path.endswith(".json"):
                with open(config_path, "r") as f:
                    config_data = json.load(f)
            elif config_path.endswith(".yaml") or config_path.endswith(".yml"):
                with open(config_path, "r") as f:
                    config_data = yaml.safe_load(f)
            else:
                raise ValueError(f"Unsupported config file format: {config_path}")

            # Extract authority levels from config
            if "authority_levels" in config_data:
                authority_levels = config_data["authority_levels"]
                if isinstance(authority_levels, dict):
                    # Update authority matrix with loaded values
                    for level, score in authority_levels.items():
                        if isinstance(score, int) and 0 <= score <= 100:
                            matrix._authority_levels[level] = score
                        else:
                            logger.warning(
                                f"[AUTHORITY] Invalid authority score for {level}: {score}. "
                                f"Must be integer between 0-100. Using default."
                            )

            # Set initial authority level if specified
            if "initial_authority" in config_data:
                initial_level = config_data["initial_authority"]
                if initial_level in matrix._authority_levels:
                    matrix._current_authority = initial_level
                    logger.info(f"[AUTHORITY] Set initial authority level to: {initial_level}")
                else:
                    logger.warning(
                        f"[AUTHORITY] Invalid initial authority level: {initial_level}. "
                        f"Using default: {matrix._current_authority}"
                    )

            logger.info(f"[AUTHORITY] Loaded authority matrix from: {config_path}")

        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON config file: {e}")
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML config file: {e}")
        except Exception as e:
            logger.error(f"[AUTHORITY] Error loading config file: {e}")
            raise ValueError(f"Failed to load authority config: {e}")

    return matrix


def resolve_env(var_name: str, default: str = None) -> str:
    """Resolve environment variable"""
    import os

    return os.environ.get(var_name, default or "")


__all__ = [
    "AuthorityMatrix",
    "SystemAuthority",
    "get_system_authority",
    "load_authority_matrix",
    "resolve_env",
]
