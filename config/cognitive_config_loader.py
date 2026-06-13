"""
cognitive_config_loader.py
DIX VISION v42.2 — Cognitive Architecture Configuration Loader

Loads and manages configuration for the new cognitive architecture components.
"""

import os
import yaml
import logging
from pathlib import Path
from typing import Any, Dict, Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class CognitiveArchitectureConfig:
    """Configuration for cognitive architecture."""
    
    # Global settings
    enabled: bool = True
    version: str = "42.2.0"
    
    # Component configs
    preservation_layer: Dict[str, Any] = field(default_factory=dict)
    indira_brain: Dict[str, Any] = field(default_factory=dict)
    dyon_brain: Dict[str, Any] = field(default_factory=dict)
    coordination_layer: Dict[str, Any] = field(default_factory=dict)
    cognitive_economy: Dict[str, Any] = field(default_factory=dict)
    operating_modes: Dict[str, Any] = field(default_factory=dict)
    learning_gate: Dict[str, Any] = field(default_factory=dict)
    planning_engine: Dict[str, Any] = field(default_factory=dict)
    signal_processing: Dict[str, Any] = field(default_factory=dict)
    shared_infrastructure: Dict[str, Any] = field(default_factory=dict)
    
    # Monitoring and health
    monitoring: Dict[str, Any] = field(default_factory=dict)
    health_checks: Dict[str, Any] = field(default_factory=dict)
    alerting: Dict[str, Any] = field(default_factory=dict)
    feature_flags: Dict[str, Any] = field(default_factory=dict)
    
    # Global settings
    global_settings: Dict[str, Any] = field(default_factory=dict)


class CognitiveConfigLoader:
    """Loads and manages cognitive architecture configuration."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize configuration loader.
        
        Args:
            config_path: Path to configuration file. If None, uses default path.
        """
        if config_path is None:
            # Default path relative to project root
            project_root = Path(__file__).parent.parent
            config_path = project_root / "config" / "cognitive_architecture_config.yaml"
        
        self.config_path = Path(config_path)
        self._config: Optional[CognitiveArchitectureConfig] = None
        self._raw_config: Optional[Dict[str, Any]] = None
        
        logger.info(f"[CONFIG] Cognitive config loader initialized with path: {self.config_path}")
    
    def load_config(self) -> CognitiveArchitectureConfig:
        """Load configuration from file.
        
        Returns:
            CognitiveArchitectureConfig: Loaded configuration.
            
        Raises:
            FileNotFoundError: If config file doesn't exist.
            yaml.YAMLError: If config file is invalid YAML.
        """
        if not self.config_path.exists():
            logger.warning(f"[CONFIG] Config file not found at {self.config_path}, using defaults")
            return self._get_default_config()
        
        try:
            with open(self.config_path, 'r') as f:
                self._raw_config = yaml.safe_load(f)
            
            logger.info(f"[CONFIG] Configuration loaded from {self.config_path}")
            
            # Parse into structured config
            self._config = self._parse_config(self._raw_config)
            
            # Apply environment overrides
            self._apply_environment_overrides()
            
            # Validate configuration
            self._validate_config()
            
            return self._config
            
        except yaml.YAMLError as e:
            logger.error(f"[CONFIG] Error parsing YAML config: {e}")
            return self._get_default_config()
        except Exception as e:
            logger.error(f"[CONFIG] Error loading config: {e}")
            return self._get_default_config()
    
    def _parse_config(self, raw_config: Dict[str, Any]) -> CognitiveArchitectureConfig:
        """Parse raw config into structured format.
        
        Args:
            raw_config: Raw configuration dictionary.
            
        Returns:
            CognitiveArchitectureConfig: Parsed configuration.
        """
        cognitive_config = raw_config.get('cognitive_architecture', {})
        
        return CognitiveArchitectureConfig(
            enabled=cognitive_config.get('enabled', True),
            version=cognitive_config.get('version', '42.2.0'),
            global_settings=cognitive_config.get('global', {}),
            preservation_layer=cognitive_config.get('preservation_layer', {}),
            indira_brain=cognitive_config.get('indira_brain', {}),
            dyon_brain=cognitive_config.get('dyon_brain', {}),
            coordination_layer=cognitive_config.get('coordination_layer', {}),
            cognitive_economy=cognitive_config.get('cognitive_economy', {}),
            operating_modes=cognitive_config.get('operating_modes', {}),
            learning_gate=cognitive_config.get('learning_gate', {}),
            planning_engine=cognitive_config.get('planning_engine', {}),
            signal_processing=cognitive_config.get('signal_processing', {}),
            shared_infrastructure=cognitive_config.get('shared_infrastructure', {}),
            monitoring=raw_config.get('monitoring', {}),
            health_checks=raw_config.get('health_checks', {}),
            alerting=raw_config.get('alerting', {}),
            feature_flags=raw_config.get('feature_flags', {})
        )
    
    def _apply_environment_overrides(self):
        """Apply environment variable overrides to configuration."""
        if not self._config:
            return
        
        # Master enable/disable
        if os.getenv('DIX_COGNITIVE_ARCHITECTURE') == 'disabled':
            self._config.enabled = False
            logger.info("[CONFIG] Cognitive architecture disabled via environment")
        
        # Individual component overrides
        component_env_vars = {
            'DIX_PRESERVATION_LAYER': 'preservation_layer_enabled',
            'DIX_INDIRA_BRAIN': 'indira_brain_enabled',
            'DIX_DYON_BRAIN': 'dyon_brain_enabled',
            'DIX_COORDINATION_LAYER': 'coordination_layer_enabled',
            'DIX_COGNITIVE_ECONOMY': 'cognitive_economy_enabled',
            'DIX_OPERATING_MODES': 'operating_modes_enabled',
            'DIX_LEARNING_GATE': 'learning_gate_enabled',
            'DIX_PLANNING_ENGINE': 'planning_engine_enabled',
            'DIX_SIGNAL_PROCESSING': 'signal_processing_enabled',
        }
        
        for env_var, flag_name in component_env_vars.items():
            env_value = os.getenv(env_var)
            if env_value:
                enabled = env_value.lower() in ('true', '1', 'enabled', 'yes')
                self._config.feature_flags[flag_name] = enabled
                logger.info(f"[CONFIG] {flag_name} set to {enabled} via environment")
        
        # Operating mode override
        if os.getenv('DIX_OPERATING_MODE'):
            mode = os.getenv('DIX_OPERATING_MODE')
            self._config.operating_modes['default_mode'] = mode
            logger.info(f"[CONFIG] Operating mode set to {mode} via environment")
        
        # Learning gate override
        if os.getenv('DIX_LEARNING_GATE'):
            state = os.getenv('DIX_LEARNING_GATE')
            self._config.learning_gate['default_state'] = state
            logger.info(f"[CONFIG] Learning gate state set to {state} via environment")
    
    def _validate_config(self):
        """Validate configuration values."""
        if not self._config:
            return
        
        # Validate operating mode
        valid_modes = ['offline', 'passive', 'observation', 'shadow', 'active', 
                      'aggressive', 'emergency', 'maintenance', 'development']
        current_mode = self._config.operating_modes.get('default_mode', 'active')
        if current_mode not in valid_modes:
            logger.warning(f"[CONFIG] Invalid operating mode: {current_mode}, using 'active'")
            self._config.operating_modes['default_mode'] = 'active'
        
        # Validate learning gate state
        valid_states = ['open', 'restricted', 'closed', 'maintenance']
        current_state = self._config.learning_gate.get('default_state', 'restricted')
        if current_state not in valid_states:
            logger.warning(f"[CONFIG] Invalid learning gate state: {current_state}, using 'restricted'")
            self._config.learning_gate['default_state'] = 'restricted'
        
        # Validate resource limits
        for component in ['indira_brain', 'dyon_brain']:
            max_cpu = self._config._config.get(component, {}).get('performance', {}).get('max_cpu_usage', 1.0)
            if not 0.0 <= max_cpu <= 1.0:
                logger.warning(f"[CONFIG] Invalid max_cpu_usage for {component}: {max_cpu}")
    
    def _get_default_config(self) -> CognitiveArchitectureConfig:
        """Get default configuration.
        
        Returns:
            CognitiveArchitectureConfig: Default configuration.
        """
        return CognitiveArchitectureConfig(
            enabled=True,
            version="42.2.0",
            global_settings={
                'performance_monitoring': True,
                'health_check_interval_seconds': 30,
                'log_level': 'INFO',
                'debug_mode': False
            },
            preservation_layer={'enabled': True},
            indira_brain={'enabled': True},
            dyon_brain={'enabled': True},
            coordination_layer={'enabled': True},
            cognitive_economy={'enabled': True},
            operating_modes={'default_mode': 'active'},
            learning_gate={'default_state': 'restricted'},
            planning_engine={'enabled': True},
            signal_processing={'enabled': True},
            shared_infrastructure={'enabled': True},
            monitoring={'enabled': True},
            health_checks={'enabled': True},
            alerting={'enabled': True},
            feature_flags={
                'cognitive_architecture_enabled': True,
                'preservation_layer_enabled': True,
                'indira_brain_enabled': True,
                'dyon_brain_enabled': True,
                'coordination_layer_enabled': True,
            }
        )
    
    def get_config(self) -> CognitiveArchitectureConfig:
        """Get current configuration.
        
        Returns:
            CognitiveArchitectureConfig: Current configuration.
        """
        if self._config is None:
            self.load_config()
        return self._config
    
    def get_raw_config(self) -> Dict[str, Any]:
        """Get raw configuration dictionary.
        
        Returns:
            Dict[str, Any]: Raw configuration.
        """
        if self._raw_config is None:
            self.load_config()
        return self._raw_config or {}
    
    def reload_config(self) -> CognitiveArchitectureConfig:
        """Reload configuration from file.
        
        Returns:
            CognitiveArchitectureConfig: Reloaded configuration.
        """
        logger.info("[CONFIG] Reloading configuration")
        self._config = None
        self._raw_config = None
        return self.load_config()
    
    def is_component_enabled(self, component_name: str) -> bool:
        """Check if a component is enabled.
        
        Args:
            component_name: Name of component to check.
            
        Returns:
            bool: True if component is enabled.
        """
        config = self.get_config()
        
        # Check master enable
        if not config.enabled:
            return False
        
        # Check component-specific flag
        flag_name = f"{component_name}_enabled"
        if flag_name in config.feature_flags:
            return config.feature_flags[flag_name]
        
        # Check component config
        component_config = getattr(config, component_name, {})
        if isinstance(component_config, dict):
            return component_config.get('enabled', True)
        
        return True
    
    def get_component_config(self, component_name: str) -> Dict[str, Any]:
        """Get configuration for a specific component.
        
        Args:
            component_name: Name of component.
            
        Returns:
            Dict[str, Any]: Component configuration.
        """
        config = self.get_config()
        return getattr(config, component_name, {})


# Global config loader instance
_global_config_loader: Optional[CognitiveConfigLoader] = None


def get_config_loader(config_path: Optional[str] = None) -> CognitiveConfigLoader:
    """Get global config loader instance.
    
    Args:
        config_path: Optional path to config file.
        
    Returns:
        CognitiveConfigLoader: Config loader instance.
    """
    global _global_config_loader
    if _global_config_loader is None:
        _global_config_loader = CognitiveConfigLoader(config_path)
    return _global_config_loader


def load_cognitive_config(config_path: Optional[str] = None) -> CognitiveArchitectureConfig:
    """Load cognitive architecture configuration.
    
    Args:
        config_path: Optional path to config file.
        
    Returns:
        CognitiveArchitectureConfig: Loaded configuration.
    """
    loader = get_config_loader(config_path)
    return loader.load_config()


def is_cognitive_architecture_enabled() -> bool:
    """Check if cognitive architecture is enabled.
    
    Returns:
        bool: True if cognitive architecture is enabled.
    """
    loader = get_config_loader()
    config = loader.get_config()
    return config.enabled


def is_component_enabled(component_name: str) -> bool:
    """Check if a component is enabled.
    
    Args:
        component_name: Name of component.
        
    Returns:
        bool: True if component is enabled.
    """
    loader = get_config_loader()
    return loader.is_component_enabled(component_name)