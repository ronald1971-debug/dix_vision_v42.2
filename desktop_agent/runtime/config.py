"""
Configuration System - Runtime configuration management
"""

import json
import logging
import os
from typing import Dict, Any, Optional
from pathlib import Path


class Configuration:
    """
    Configuration manager for Desktop AgentOS.
    
    Handles loading, validation, and access to configuration
    parameters with support for environment variables and
    configuration file overlays.
    """
    
    DEFAULT_CONFIG = {
        "runtime": {
            "log_level": "INFO",
            "max_workers": 4,
            "task_timeout": 300,
        },
        "agents": {
            "indira": {
                "enabled": True,
                "research_timeout": 600,
                "max_concurrent_research": 3,
            },
            "dyon": {
                "enabled": True,
                "analysis_timeout": 300,
                "max_concurrent_analysis": 2,
            },
        },
        "browser": {
            "headless": True,
            "timeout": 30,
            "user_agent": "DesktopAgentOS/42.2",
        },
        "memory": {
            "backend": "sqlite",
            "path": "./data/agent_memory.db",
            "max_size_mb": 1000,
        },
        "governance": {
            "enabled": True,
            "policy_path": "./config/policies",
            "audit_log_path": "./data/audit.log",
        },
        "telemetry": {
            "enabled": True,
            "metrics_port": 9090,
            "log_path": "./data/telemetry",
        },
    }
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration.
        
        Args:
            config_path: Optional path to configuration file
        """
        self.config: Dict[str, Any] = self.DEFAULT_CONFIG.copy()
        self.config_path = config_path
        
        self.logger = logging.getLogger(__name__)
        
        if config_path:
            self.load_from_file(config_path)
        else:
            self.load_from_environment()
            
    def load_from_file(self, config_path: str) -> None:
        """
        Load configuration from file.
        
        Args:
            config_path: Path to configuration file
        """
        try:
            path = Path(config_path)
            if path.exists():
                with open(path, 'r') as f:
                    user_config = json.load(f)
                    self._merge_config(user_config)
                    self.logger.info(f"Loaded configuration from {config_path}")
            else:
                self.logger.warning(f"Config file not found: {config_path}")
        except Exception as e:
            self.logger.error(f"Error loading config: {e}")
            
    def load_from_environment(self) -> None:
        """Load configuration from environment variables."""
        env_mappings = {
            "DESKTOP_AGENT_LOG_LEVEL": ("runtime", "log_level"),
            "DESKTOP_AGENT_MAX_WORKERS": ("runtime", "max_workers"),
            "DESKTOP_AGENT_BROWSER_HEADLESS": ("browser", "headless"),
            "DESKTOP_AGENT_MEMORY_PATH": ("memory", "path"),
            "DESKTOP_AGENT_TELEMETRY_ENABLED": ("telemetry", "enabled"),
        }
        
        for env_var, (section, key) in env_mappings.items():
            value = os.getenv(env_var)
            if value:
                self._set_config_value(section, key, value)
                
    def _merge_config(self, user_config: Dict[str, Any]) -> None:
        """
        Merge user configuration with defaults.
        
        Args:
            user_config: User configuration dictionary
        """
        def deep_merge(base: Dict, override: Dict) -> Dict:
            result = base.copy()
            for key, value in override.items():
                if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = deep_merge(result[key], value)
                else:
                    result[key] = value
            return result
            
        self.config = deep_merge(self.config, user_config)
        
    def _set_config_value(self, section: str, key: str, value: str) -> None:
        """
        Set a configuration value.
        
        Args:
            section: Configuration section
            key: Configuration key
            value: Value to set
        """
        if section not in self.config:
            self.config[section] = {}
            
        # Type conversion
        if value.lower() == 'true':
            value = True
        elif value.lower() == 'false':
            value = False
        elif value.isdigit():
            value = int(value)
            
        self.config[section][key] = value
        
    def get(self, section: str, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            section: Configuration section
            key: Configuration key
            default: Default value if not found
            
        Returns:
            Configuration value
        """
        return self.config.get(section, {}).get(key, default)
        
    def get_section(self, section: str) -> Dict[str, Any]:
        """
        Get an entire configuration section.
        
        Args:
            section: Configuration section
            
        Returns:
            Section dictionary
        """
        return self.config.get(section, {})
        
    def set(self, section: str, key: str, value: Any) -> None:
        """
        Set a configuration value.
        
        Args:
            section: Configuration section
            key: Configuration key
            value: Value to set
        """
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value
        
    def save(self, path: Optional[str] = None) -> None:
        """
        Save configuration to file.
        
        Args:
            path: Optional path to save to
        """
        save_path = path or self.config_path
        if not save_path:
            raise ValueError("No config path specified")
            
        try:
            Path(save_path).parent.mkdir(parents=True, exist_ok=True)
            with open(save_path, 'w') as f:
                json.dump(self.config, f, indent=2)
            self.logger.info(f"Saved configuration to {save_path}")
        except Exception as e:
            self.logger.error(f"Error saving config: {e}")
            
    def validate(self) -> bool:
        """
        Validate configuration.
        
        Returns:
            True if valid, False otherwise
        """
        required_sections = ["runtime", "agents", "browser", "memory"]
        
        for section in required_sections:
            if section not in self.config:
                self.logger.error(f"Missing required section: {section}")
                return False
                
        return True
