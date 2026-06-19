"""
System Unified Config - Configuration Management Infrastructure
Provides configuration management capabilities
NO LAZY LOADING - All components load directly
"""

import os
import json
from typing import Dict, List, Optional, Any
from pathlib import Path

class SystemConfig:
    """System configuration manager"""
    
    def __init__(self):
        self._config: Dict[str, Any] = {}
        self._config_path = "config/system_config.json"
        self._load_config()
    
    def _load_config(self):
        """Load configuration from file"""
        config_path = Path(self._config_path)
        if config_path.exists():
            with open(config_path, 'r') as f:
                self._config = json.load(f)
        else:
            # Set default configuration
            self._config = {
                'system_mode': 'development',
                'log_level': 'INFO',
                'max_workers': 4,
                'timeout_seconds': 30,
                'enable_metrics': True,
                'enable_monitoring': True
            }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set configuration value"""
        self._config[key] = value
    
    def get_all(self) -> Dict[str, Any]:
        """Get all configuration"""
        return self._config.copy()

# Global instance
_system_config = None

def get_config() -> SystemConfig:
    """Get global system config instance"""
    global _system_config
    if _system_config is None:
        _system_config = SystemConfig()
    return _system_config

def get_config_value(key: str, default: Any = None) -> Any:
    """Get config value (convenience function)"""
    config = get_config()
    return config.get(key, default)

# Add module-level get function for backward compatibility
def get(key: str, default: Any = None) -> Any:
    """Get configuration value (module-level convenience function)"""
    return get_config_value(key, default)

__all__ = [
    'SystemConfig',
    'get_config',
    'get_config_value',
    'get'
]