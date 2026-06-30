"""
DIX VISION Unified Configuration Manager

Centralized configuration management system that consolidates all
configuration-related functionality across the DIX VISION system.

Usage:
    from runtime.config_manager import UnifiedConfigManager, get_config
    
    config = get_config()
    value = config.get("system.mode", "development")
"""

from __future__ import annotations

import json
import logging
import os
import threading
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)


class ConfigSource(str, Enum):
    """Source of configuration entries in precedence order (low → high)."""
    DEFAULT = "DEFAULT"
    YAML = "YAML"
    DOTENV = "DOTENV"
    ENV = "ENV"
    CLI = "CLI"


_SOURCE_RANK: dict[ConfigSource, int] = {
    ConfigSource.DEFAULT: 0,
    ConfigSource.YAML: 1,
    ConfigSource.DOTENV: 2,
    ConfigSource.ENV: 3,
    ConfigSource.CLI: 4,
}


@dataclass(frozen=True, slots=True)
class ConfigEntry:
    """One merged config entry with full source provenance."""
    key: str
    value: str | int | float | bool | None
    source: ConfigSource

    def __post_init__(self) -> None:
        if not isinstance(self.key, str) or not self.key:
            raise ValueError(f"ConfigEntry: key must be non-empty str, got {self.key!r}")
        if any(c.isspace() for c in self.key):
            raise ValueError(f"ConfigEntry: key must not contain whitespace, got {self.key!r}")
        if not isinstance(self.source, ConfigSource):
            raise TypeError(
                f"ConfigEntry: source must be ConfigSource, got {type(self.source).__name__}"
            )
        if not isinstance(self.value, (str, int, float, bool, type(None))):
            raise TypeError(
                f"ConfigEntry: value type {type(self.value).__name__} not allowed; "
                "must be str/int/float/bool/None"
            )


@dataclass(frozen=True, slots=True)
class ValidationResult:
    """Result of configuration validation."""
    valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class ConfigSourceBase(ABC):
    """Abstract base class for configuration sources."""
    
    @abstractmethod
    def load(self) -> dict[str, Any]:
        """Load configuration from this source."""
        pass
    
    @abstractmethod
    def get_precedence(self) -> int:
        """Get precedence rank for this source."""
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Get name of this source."""
        pass


class DefaultConfigSource(ConfigSourceBase):
    """Default configuration values."""
    
    def __init__(self, defaults: dict[str, Any] | None = None):
        self.defaults = defaults or self._get_default_config()
    
    def _get_default_config(self) -> dict[str, Any]:
        """Get default configuration values."""
        return {
            "system": {
                "mode": "development",
                "log_level": "INFO",
                "max_workers": 4,
                "timeout_seconds": 30,
            },
            "network": {
                "host": "127.0.0.1",
                "ports": {
                    "desktop": 8765,
                    "dashboard": 8080,
                    "backend": 8000,
                    "docker_backend": 8080,
                    "docker_dashboard": 5173,
                },
            },
            "memory": {
                "warning_threshold": 70,
                "critical_threshold": 85,
                "process_limit": 1024,
                "enable_monitoring": True,
            },
            "paths": {
                "data_root": "~/.local/share/dix_vision",
                "logs": "~/.local/share/dix_vision/logs",
                "cache": "~/.cache/dix_vision",
            },
            "features": {
                "enable_metrics": True,
                "enable_monitoring": True,
                "enable_telemetry": False,
                "enable_debug_mode": False,
            },
        }
    
    def load(self) -> dict[str, Any]:
        """Load default configuration."""
        return self.defaults
    
    def get_precedence(self) -> int:
        return _SOURCE_RANK[ConfigSource.DEFAULT]
    
    def get_name(self) -> str:
        return "Default"


class YAMLConfigSource(ConfigSourceBase):
    """Configuration from YAML files."""
    
    def __init__(self, config_path: str | Path):
        self.config_path = Path(config_path)
    
    def load(self) -> dict[str, Any]:
        """Load configuration from YAML file."""
        if not self.config_path.exists():
            logger.debug(f"YAML config file not found: {self.config_path}")
            return {}
        
        try:
            import yaml
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
                logger.info(f"Loaded YAML config from: {self.config_path}")
                return config or {}
        except ImportError:
            logger.warning("PyYAML not available, skipping YAML config")
            return {}
        except Exception as e:
            logger.error(f"Failed to load YAML config: {e}")
            return {}
    
    def get_precedence(self) -> int:
        return _SOURCE_RANK[ConfigSource.YAML]
    
    def get_name(self) -> str:
        return "YAML"


class DotenvConfigSource(ConfigSourceBase):
    """Configuration from .env files."""
    
    def __init__(self, dotenv_path: str | Path = ".env"):
        self.dotenv_path = Path(dotenv_path)
    
    def load(self) -> dict[str, Any]:
        """Load configuration from .env file."""
        if not self.dotenv_path.exists():
            logger.debug(f".env file not found: {self.dotenv_path}")
            return {}
        
        config = {}
        try:
            with open(self.dotenv_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip().strip('"').strip("'")
                        config[key] = self._coerce_value(value)
            
            logger.info(f"Loaded .env config from: {self.dotenv_path}")
            return config
        except Exception as e:
            logger.error(f"Failed to load .env config: {e}")
            return {}
    
    def _coerce_value(self, value: str) -> str | int | float | bool:
        """Coerce string value to appropriate type."""
        # Try boolean
        if value.lower() in ('true', 'yes', '1'):
            return True
        if value.lower() in ('false', 'no', '0'):
            return False
        
        # Try integer
        try:
            return int(value)
        except ValueError:
            pass
        
        # Try float
        try:
            return float(value)
        except ValueError:
            pass
        
        return value
    
    def get_precedence(self) -> int:
        return _SOURCE_RANK[ConfigSource.DOTENV]
    
    def get_name(self) -> str:
        return "Dotenv"


class EnvironmentConfigSource(ConfigSourceBase):
    """Configuration from environment variables."""
    
    def __init__(self, prefix: str = "DIX_"):
        self.prefix = prefix
    
    def load(self) -> dict[str, Any]:
        """Load configuration from environment variables."""
        config = {}
        for key, value in os.environ.items():
            if key.startswith(self.prefix):
                # Remove prefix and convert to lowercase
                config_key = key[len(self.prefix):].lower()
                config[config_key] = self._coerce_value(value)
        
        if config:
            logger.info(f"Loaded {len(config)} environment variables with prefix {self.prefix}")
        return config
    
    def _coerce_value(self, value: str) -> str | int | float | bool:
        """Coerce string value to appropriate type."""
        # Try boolean
        if value.lower() in ('true', 'yes', '1'):
            return True
        if value.lower() in ('false', 'no', '0'):
            return False
        
        # Try integer
        try:
            return int(value)
        except ValueError:
            pass
        
        # Try float
        try:
            return float(value)
        except ValueError:
            pass
        
        return value
    
    def get_precedence(self) -> int:
        return _SOURCE_RANK[ConfigSource.ENV]
    
    def get_name(self) -> str:
        return "Environment"


class CLIConfigSource(ConfigSourceBase):
    """Configuration from command-line arguments."""
    
    def __init__(self, cli_args: dict[str, Any] | None = None):
        self.cli_args = cli_args or {}
    
    def load(self) -> dict[str, Any]:
        """Load configuration from CLI arguments."""
        return self.cli_args
    
    def get_precedence(self) -> int:
        return _SOURCE_RANK[ConfigSource.CLI]
    
    def get_name(self) -> str:
        return "CLI"


class ConfigValidator:
    """Validates configuration values."""
    
    def __init__(self):
        self.schemas: dict[str, dict] = {}
        self.validators: dict[str, Callable[[Any], bool]] = {}
        self._register_default_schemas()
    
    def _register_default_schemas(self):
        """Register default configuration schemas."""
        self.schemas.update({
            "system.mode": {
                "type": str,
                "allowed": ["development", "production", "desktop", "portable"],
            },
            "system.log_level": {
                "type": str,
                "allowed": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
            },
            "system.max_workers": {
                "type": int,
                "min": 1,
                "max": 32,
            },
            "network.host": {
                "type": str,
            },
            "memory.warning_threshold": {
                "type": (int, float),
                "min": 0,
                "max": 100,
            },
            "memory.critical_threshold": {
                "type": (int, float),
                "min": 0,
                "max": 100,
            },
        })
    
    def register_schema(self, key: str, schema: dict):
        """Register a configuration schema."""
        self.schemas[key] = schema
    
    def register_validator(self, key: str, validator: Callable[[Any], bool]):
        """Register a custom validator."""
        self.validators[key] = validator
    
    def validate(self, key: str, value: Any) -> ValidationResult:
        """Validate a single configuration value."""
        errors = []
        warnings = []
        
        # Check schema if available
        if key in self.schemas:
            schema = self.schemas[key]
            
            # Type check
            expected_type = schema.get("type")
            if expected_type and not isinstance(value, expected_type):
                errors.append(f"Expected type {expected_type}, got {type(value)}")
            
            # Allowed values check
            if "allowed" in schema and value not in schema["allowed"]:
                errors.append(f"Value must be one of {schema['allowed']}")
            
            # Range check
            if "min" in schema and value < schema["min"]:
                errors.append(f"Value must be >= {schema['min']}")
            if "max" in schema and value > schema["max"]:
                errors.append(f"Value must be <= {schema['max']}")
        
        # Check custom validator
        if key in self.validators:
            if not self.validators[key](value):
                errors.append(f"Custom validator failed for {key}")
        
        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    def validate_all(self, config: dict[str, Any]) -> ValidationResult:
        """Validate all configuration values."""
        all_errors = []
        all_warnings = []
        
        for key, value in config.items():
            result = self.validate(key, value)
            all_errors.extend(result.errors)
            all_warnings.extend(result.warnings)
        
        return ValidationResult(
            valid=len(all_errors) == 0,
            errors=all_errors,
            warnings=all_warnings
        )


class ConfigAuditor:
    """Audits configuration changes and access."""
    
    def __init__(self):
        self.log: list[dict] = []
        self.watchers: dict[str, list[Callable]] = {}
        self._lock = threading.Lock()
    
    def log_access(self, key: str, source: str):
        """Log configuration access."""
        with self._lock:
            entry = {
                "type": "access",
                "key": key,
                "source": source,
                "timestamp": self._get_timestamp(),
            }
            self.log.append(entry)
            self._notify_watchers(key, entry)
    
    def log_change(self, key: str, old_value: Any, new_value: Any, source: str):
        """Log configuration change."""
        with self._lock:
            entry = {
                "type": "change",
                "key": key,
                "old_value": old_value,
                "new_value": new_value,
                "source": source,
                "timestamp": self._get_timestamp(),
            }
            self.log.append(entry)
            self._notify_watchers(key, entry)
    
    def register_watcher(self, key: str, callback: Callable):
        """Register a watcher for configuration changes."""
        with self._lock:
            if key not in self.watchers:
                self.watchers[key] = []
            self.watchers[key].append(callback)
    
    def _notify_watchers(self, key: str, entry: dict):
        """Notify watchers of configuration changes."""
        if key in self.watchers:
            for callback in self.watchers[key]:
                try:
                    callback(entry)
                except Exception as e:
                    logger.error(f"Watcher callback failed: {e}")
    
    def get_audit_log(self) -> list[dict]:
        """Get the audit log."""
        with self._lock:
            return self.log.copy()
    
    def _get_timestamp(self) -> float:
        """Get current timestamp."""
        import time
        return time.time()


class UnifiedConfigManager:
    """Centralized configuration management for DIX VISION system."""
    
    def __init__(self, project_root: str | Path | None = None):
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.entries: dict[str, ConfigEntry] = {}
        self.sources: list[ConfigSourceBase] = []
        self.validator = ConfigValidator()
        self.auditor = ConfigAuditor()
        self.cache: dict[str, Any] = {}
        self._lock = threading.Lock()
        
        self._initialize_sources()
        self._load_config()
    
    def _initialize_sources(self):
        """Initialize configuration sources in precedence order."""
        self.sources = [
            DefaultConfigSource(),
            YAMLConfigSource(self.project_root / "config" / "system_config.yaml"),
            DotenvConfigSource(self.project_root / ".env"),
            EnvironmentConfigSource("DIX_"),
            CLIConfigSource({}),  # CLI args can be set later
        ]
    
    def _load_config(self):
        """Load and merge configuration from all sources."""
        merged_config = {}
        
        # Load from each source in precedence order
        for source in self.sources:
            source_config = source.load()
            self._merge_config(merged_config, source_config, source)
        
        # Create config entries
        self._create_entries(merged_config)
        
        # Validate configuration
        validation_result = self.validator.validate_all(self.cache)
        if not validation_result.valid:
            logger.error(f"Configuration validation failed: {validation_result.errors}")
        if validation_result.warnings:
            logger.warning(f"Configuration warnings: {validation_result.warnings}")
    
    def _merge_config(self, base: dict[str, Any], override: dict[str, Any], source: ConfigSourceBase):
        """Recursively merge override config into base config."""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_config(base[key], value, source)
            else:
                base[key] = value
    
    def _create_entries(self, config: dict[str, Any], prefix: str = ""):
        """Create config entries from nested config."""
        for key, value in config.items():
            full_key = f"{prefix}.{key}" if prefix else key
            
            if isinstance(value, dict):
                self._create_entries(value, full_key)
            else:
                # Determine source
                source = self._determine_source(full_key)
                
                entry = ConfigEntry(
                    key=full_key,
                    value=value,
                    source=source
                )
                self.entries[full_key] = entry
                self.cache[full_key] = value
    
    def _determine_source(self, key: str) -> ConfigSource:
        """Determine which source provided this key."""
        # Check sources in reverse precedence order
        for source in reversed(self.sources):
            source_config = source.load()
            if self._key_in_dict(key, source_config):
                return ConfigSource(source.get_name().upper())
        return ConfigSource.DEFAULT
    
    def _key_in_dict(self, key: str, config: dict[str, Any]) -> bool:
        """Check if key exists in nested dict."""
        parts = key.split('.')
        current = config
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return False
        return True
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        with self._lock:
            self.auditor.log_access(key, "get")
            return self.cache.get(key, default)
    
    def set(self, key: str, value: Any, source: str = "runtime"):
        """Set configuration value."""
        with self._lock:
            old_value = self.cache.get(key)
            self.cache[key] = value
            
            entry = ConfigEntry(
                key=key,
                value=value,
                source=ConfigSource.CLI  # Runtime changes get highest precedence
            )
            self.entries[key] = entry
            
            self.auditor.log_change(key, old_value, value, source)
    
    def get_source(self, key: str) -> ConfigSource | None:
        """Get the source of a configuration value."""
        with self._lock:
            entry = self.entries.get(key)
            return entry.source if entry else None
    
    def get_all(self) -> dict[str, Any]:
        """Get all configuration values."""
        with self._lock:
            return self.cache.copy()
    
    def reload(self):
        """Reload configuration from all sources."""
        with self._lock:
            self.entries.clear()
            self.cache.clear()
            self._load_config()
            logger.info("Configuration reloaded")
    
    def export(self, format: str = "json") -> str:
        """Export configuration to specified format."""
        with self._lock:
            if format == "json":
                return json.dumps(self.cache, indent=2)
            elif format == "yaml":
                try:
                    import yaml
                    return yaml.dump(self.cache, default_flow_style=False)
                except ImportError:
                    logger.error("PyYAML not available for YAML export")
                    return json.dumps(self.cache, indent=2)
            else:
                raise ValueError(f"Unsupported export format: {format}")
    
    def set_cli_args(self, cli_args: dict[str, Any]):
        """Set CLI arguments and reload configuration."""
        # Update CLI source
        for i, source in enumerate(self.sources):
            if isinstance(source, CLIConfigSource):
                self.sources[i] = CLIConfigSource(cli_args)
                break
        
        # Reload configuration
        self.reload()


# Global instance
_config_manager: Optional[UnifiedConfigManager] = None
_lock = threading.Lock()


def get_config(project_root: str | Path | None = None) -> UnifiedConfigManager:
    """Get global configuration manager instance."""
    global _config_manager
    if _config_manager is None:
        with _lock:
            if _config_manager is None:
                _config_manager = UnifiedConfigManager(project_root)
    return _config_manager


def get_config_value(key: str, default: Any = None) -> Any:
    """Get configuration value (convenience function)."""
    return get_config().get(key, default)


def set_config_value(key: str, value: Any) -> None:
    """Set configuration value (convenience function)."""
    get_config().set(key, value)


def reload_config() -> None:
    """Reload configuration (convenience function)."""
    get_config().reload()


__all__ = [
    "UnifiedConfigManager",
    "ConfigEntry",
    "ConfigSource",
    "ConfigValidator",
    "ConfigAuditor",
    "get_config",
    "get_config_value",
    "set_config_value",
    "reload_config",
]