"""
DIX VISION Configuration Management Service

Provides centralized configuration management with versioning, validation,
hot reload, and configuration rollback capabilities.
"""

from __future__ import annotations

import hashlib
import json
import logging
import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple
from collections import defaultdict, deque
from datetime import datetime
import copy

from runtime.event_bus import EventBus, Event, EventType, get_event_bus
from runtime.service_manager import Service, ServiceState, ServiceHealth

logger = logging.getLogger(__name__)


class ConfigChangeType(Enum):
    """Types of configuration changes."""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    ROLLBACK = "rollback"


@dataclass
class ConfigVersion:
    """Configuration version with metadata."""
    version_id: str
    config_data: Dict[str, Any]
    checksum: str
    timestamp: float
    author: str = "system"
    description: str = ""
    parent_version_id: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "version_id": self.version_id,
            "config_data": self.config_data,
            "checksum": self.checksum,
            "timestamp": self.timestamp,
            "datetime": datetime.fromtimestamp(self.timestamp).isoformat(),
            "author": self.author,
            "description": self.description,
            "parent_version_id": self.parent_version_id
        }


@dataclass
class ConfigChange:
    """Configuration change record."""
    change_id: str
    change_type: ConfigChangeType
    config_key: str
    old_value: Any
    new_value: Any
    version_id: str
    timestamp: float
    author: str = "system"
    description: str = ""


@dataclass
class ConfigValidationRule:
    """Configuration validation rule."""
    rule_id: str
    config_key: str
    validator: Callable[[Any], bool]
    error_message: str = ""
    enabled: bool = True


class ConfigurationService(Service):
    """Configuration management service as per Runtime Specification."""
    
    # Service dependencies
    DEPENDENCIES = []
    
    def __init__(self):
        super().__init__("configuration_service")
        self._current_config: Dict[str, Any] = {}
        self._config_versions: Dict[str, ConfigVersion] = {}
        self._version_history: deque = deque(maxlen=100)
        self._config_changes: List[ConfigChange] = []
        self._validation_rules: Dict[str, ConfigValidationRule] = {}
        self._subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self._lock = threading.Lock()
        self._auto_reload_enabled = False
        self._config_file_path: Optional[str] = None
        self._current_version_id: str = ""
        
    def init(self, event_bus: EventBus, config: Dict[str, Any]) -> bool:
        """Initialize the configuration service."""
        try:
            self.event_bus = event_bus
            self.state = ServiceState.INITIALIZING
            
            # Load configuration
            config_service_config = config.get("configuration", {})
            self._auto_reload_enabled = config_service_config.get("auto_reload", False)
            self._config_file_path = config_service_config.get("config_file")
            
            # Load initial configuration
            if self._config_file_path:
                self._load_config_from_file()
            else:
                self._current_config = config.get("initial_config", {})
            
            # Create initial version
            self._create_version("Initial configuration", "system")
            
            # Initialize default validation rules
            self._init_default_validation_rules()
            
            logger.info("Configuration Service initialized")
            return True
        except Exception as e:
            logger.error(f"Configuration Service initialization failed: {e}")
            self.state = ServiceState.ERROR
            return False
    
    def start(self) -> bool:
        """Start the configuration service."""
        try:
            self.state = ServiceState.STARTING
            
            # Start auto-reload if enabled
            if self._auto_reload_enabled:
                self._start_auto_reload()
            
            self.state = ServiceState.RUNNING
            self.emit_event(str(EventType.SERVICE_START), {"service": self.name})
            logger.info("Configuration Service started")
            return True
        except Exception as e:
            logger.error(f"Configuration Service start failed: {e}")
            self.state = ServiceState.ERROR
            self.emit_event(str(EventType.SERVICE_CRASH), {"service": self.name, "error": str(e)})
            return False
    
    def stop(self) -> bool:
        """Stop the configuration service."""
        try:
            self.state = ServiceState.STOPPING
            self._auto_reload_enabled = False
            self.state = ServiceState.STOPPED
            self.emit_event(str(EventType.SERVICE_STOP), {"service": self.name})
            logger.info("Configuration Service stopped")
            return True
        except Exception as e:
            logger.error(f"Configuration Service stop failed: {e}")
            self.state = ServiceState.ERROR
            return False
    
    def health(self) -> ServiceHealth:
        """Get configuration service health."""
        return ServiceHealth(
            service=self.name,
            state=self.state,
            healthy=self.state == ServiceState.RUNNING,
            message=f"Configuration Service - Version {self._current_version_id}",
            details={
                "current_version": self._current_version_id,
                "total_versions": len(self._config_versions),
                "total_changes": len(self._config_changes),
                "validation_rules": len(self._validation_rules),
                "subscribers": len(self._subscribers),
                "auto_reload": self._auto_reload_enabled
            },
            timestamp=time.time()
        )
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        with self._lock:
            keys = key.split(".")
            value = self._current_config
            
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return default
            
            return value
    
    def set(self, key: str, value: Any, author: str = "system", 
            description: str = "") -> bool:
        """Set configuration value."""
        with self._lock:
            # Get old value
            old_value = self.get(key)
            
            # Validate new value
            if not self._validate_config(key, value):
                logger.error(f"Configuration validation failed for {key}")
                return False
            
            # Set new value
            keys = key.split(".")
            config = self._current_config
            
            for k in keys[:-1]:
                if k not in config:
                    config[k] = {}
                config = config[k]
            
            config[keys[-1]] = value
            
            # Record change
            change = ConfigChange(
                change_id=self._generate_id(),
                change_type=ConfigChangeType.UPDATE,
                config_key=key,
                old_value=old_value,
                new_value=value,
                version_id=self._current_version_id,
                timestamp=time.time(),
                author=author,
                description=description
            )
            self._config_changes.append(change)
            
            # Notify subscribers
            self._notify_subscribers(key, old_value, value)
            
            logger.info(f"Configuration updated: {key} = {value}")
            return True
    
    def delete(self, key: str, author: str = "system", 
               description: str = "") -> bool:
        """Delete configuration value."""
        with self._lock:
            old_value = self.get(key)
            if old_value is None:
                return False
            
            keys = key.split(".")
            config = self._current_config
            
            for k in keys[:-1]:
                if k not in config:
                    return False
                config = config[k]
            
            if keys[-1] in config:
                del config[keys[-1]]
                
                # Record change
                change = ConfigChange(
                    change_id=self._generate_id(),
                    change_type=ConfigChangeType.DELETE,
                    config_key=key,
                    old_value=old_value,
                    new_value=None,
                    version_id=self._current_version_id,
                    timestamp=time.time(),
                    author=author,
                    description=description
                )
                self._config_changes.append(change)
                
                # Notify subscribers
                self._notify_subscribers(key, old_value, None)
                
                logger.info(f"Configuration deleted: {key}")
                return True
            
            return False
    
    def create_version(self, description: str = "", author: str = "system") -> str:
        """Create a new configuration version."""
        with self._lock:
            return self._create_version(description, author)
    
    def rollback(self, version_id: str, author: str = "system") -> bool:
        """Rollback to a specific configuration version."""
        with self._lock:
            if version_id not in self._config_versions:
                logger.error(f"Version {version_id} not found")
                return False
            
            version = self._config_versions[version_id]
            
            # Restore configuration
            self._current_config = copy.deepcopy(version.config_data)
            
            # Create new version for rollback
            new_version_id = self._create_version(f"Rollback to {version_id}", author)
            
            # Record rollback change
            change = ConfigChange(
                change_id=self._generate_id(),
                change_type=ConfigChangeType.ROLLBACK,
                config_key="*",
                old_value=self._current_version_id,
                new_value=version_id,
                version_id=new_version_id,
                timestamp=time.time(),
                author=author,
                description=f"Rollback to version {version_id}"
            )
            self._config_changes.append(change)
            
            logger.info(f"Configuration rolled back to version {version_id}")
            return True
    
    def get_version(self, version_id: str) -> Optional[ConfigVersion]:
        """Get a specific configuration version."""
        with self._lock:
            return self._config_versions.get(version_id)
    
    def get_version_history(self, limit: int = 10) -> List[ConfigVersion]:
        """Get configuration version history."""
        with self._lock:
            return list(self._version_history)[-limit:]
    
    def get_changes(self, config_key: str = None, limit: int = 100) -> List[ConfigChange]:
        """Get configuration changes."""
        with self._lock:
            if config_key:
                return [c for c in self._config_changes if c.config_key == config_key][-limit:]
            return self._config_changes[-limit:]
    
    def subscribe(self, key: str, callback: Callable[[str, Any, Any], None]) -> None:
        """Subscribe to configuration changes for a key."""
        with self._lock:
            self._subscribers[key].append(callback)
    
    def unsubscribe(self, key: str, callback: Callable[[str, Any, Any], None]) -> None:
        """Unsubscribe from configuration changes."""
        with self._lock:
            if key in self._subscribers and callback in self._subscribers[key]:
                self._subscribers[key].remove(callback)
    
    def register_validation_rule(self, rule: ConfigValidationRule) -> None:
        """Register a configuration validation rule."""
        with self._lock:
            self._validation_rules[rule.rule_id] = rule
            logger.info(f"Registered validation rule: {rule.rule_id}")
    
    def export_config(self) -> Dict[str, Any]:
        """Export current configuration."""
        with self._lock:
            return copy.deepcopy(self._current_config)
    
    def import_config(self, config: Dict[str, Any], author: str = "system", 
                     description: str = "") -> bool:
        """Import configuration."""
        with self._lock:
            # Validate all configuration
            if not self._validate_all_config(config):
                logger.error("Configuration validation failed during import")
                return False
            
            # Set new configuration
            self._current_config = copy.deepcopy(config)
            
            # Create new version
            self._create_version(description or "Configuration import", author)
            
            logger.info("Configuration imported successfully")
            return True
    
    def save_to_file(self, file_path: str = None) -> bool:
        """Save current configuration to file."""
        try:
            path = file_path or self._config_file_path
            if not path:
                logger.error("No file path specified")
                return False
            
            with open(path, 'w') as f:
                json.dump(self._current_config, f, indent=2)
            
            logger.info(f"Configuration saved to {path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            return False
    
    def reload_from_file(self) -> bool:
        """Reload configuration from file."""
        if not self._config_file_path:
            logger.error("No config file path set")
            return False
        
        return self._load_config_from_file()
    
    def _load_config_from_file(self) -> bool:
        """Load configuration from file."""
        try:
            with open(self._config_file_path, 'r') as f:
                config = json.load(f)
            
            self._current_config = config
            self._create_version("Configuration loaded from file", "system")
            
            logger.info(f"Configuration loaded from {self._config_file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            return False
    
    def _create_version(self, description: str, author: str) -> str:
        """Create a new configuration version."""
        version_id = self._generate_id()
        config_copy = copy.deepcopy(self._current_config)
        checksum = self._calculate_checksum(config_copy)
        
        version = ConfigVersion(
            version_id=version_id,
            config_data=config_copy,
            checksum=checksum,
            timestamp=time.time(),
            author=author,
            description=description,
            parent_version_id=self._current_version_id
        )
        
        self._config_versions[version_id] = version
        self._version_history.append(version)
        self._current_version_id = version_id
        
        return version_id
    
    def _validate_config(self, key: str, value: Any) -> bool:
        """Validate a configuration value."""
        for rule in self._validation_rules.values():
            if rule.enabled and rule.config_key == key:
                if not rule.validator(value):
                    logger.error(f"Validation failed for {key}: {rule.error_message}")
                    return False
        return True
    
    def _validate_all_config(self, config: Dict[str, Any]) -> bool:
        """Validate entire configuration."""
        # Flatten config to check all keys
        def flatten_config(d, parent_key=""):
            items = []
            for k, v in d.items():
                new_key = f"{parent_key}.{k}" if parent_key else k
                if isinstance(v, dict):
                    items.extend(flatten_config(v, new_key))
                else:
                    items.append((new_key, v))
            return items
        
        for key, value in flatten_config(config):
            if not self._validate_config(key, value):
                return False
        
        return True
    
    def _notify_subscribers(self, key: str, old_value: Any, new_value: Any) -> None:
        """Notify subscribers of configuration changes."""
        # Notify exact key subscribers
        if key in self._subscribers:
            for callback in self._subscribers[key]:
                try:
                    callback(key, old_value, new_value)
                except Exception as e:
                    logger.error(f"Subscriber callback error: {e}")
        
        # Notify wildcard subscribers
        for pattern, callbacks in self._subscribers.items():
            if pattern.endswith("*") and key.startswith(pattern[:-1]):
                for callback in callbacks:
                    try:
                        callback(key, old_value, new_value)
                    except Exception as e:
                        logger.error(f"Subscriber callback error: {e}")
    
    def _calculate_checksum(self, config: Dict[str, Any]) -> str:
        """Calculate checksum of configuration."""
        config_str = json.dumps(config, sort_keys=True)
        return hashlib.sha256(config_str.encode()).hexdigest()
    
    def _generate_id(self) -> str:
        """Generate unique ID."""
        import uuid
        return str(uuid.uuid4())
    
    def _init_default_validation_rules(self) -> None:
        """Initialize default validation rules."""
        # Example validation rules
        self.register_validation_rule(ConfigValidationRule(
            rule_id="positive_number",
            config_key="*",
            validator=lambda x: isinstance(x, (int, float)) and x >= 0,
            error_message="Value must be a positive number"
        ))
    
    def _start_auto_reload(self) -> None:
        """Start auto-reload background task."""
        def auto_reload():
            while self._auto_reload_enabled and self.state == ServiceState.RUNNING:
                try:
                    if self._config_file_path:
                        self.reload_from_file()
                    time.sleep(60)  # Check every minute
                except Exception as e:
                    logger.error(f"Auto-reload error: {e}")
                    time.sleep(30)
        
        thread = threading.Thread(target=auto_reload, daemon=True)
        thread.start()
        logger.info("Auto-reload started")


# Global instance
_configuration_service: Optional[ConfigurationService] = None


def get_configuration_service() -> ConfigurationService:
    """Get global configuration service instance."""
    global _configuration_service
    if _configuration_service is None:
        _configuration_service = ConfigurationService()
    return _configuration_service