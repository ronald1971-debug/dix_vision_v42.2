"""
cognitive_os.config.configuration
DIX VISION v42.2 — Unified Configuration Management System

This provides centralized configuration management for all phases and modules
in the DIX VISION system, including neuromorphic components, cognitive OS modules,
and execution system parameters.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional
from pathlib import Path
import os

logger = logging.getLogger(__name__)


@dataclass
class NeuromorphicConfig:
    """Configuration for neuromorphic computing components."""
    
    # INDIRA Neuromorphic
    indira_snn_enabled: bool = True
    indira_snn_neurons: int = 100
    indira_snn_confidence_weight: float = 0.3
    indira_lsm_enabled: bool = True
    indira_lsm_reservoir_size: int = 100
    indira_lsm_pattern_weight: float = 0.2
    
    # DYON Neuromorphic
    dyon_snn_enabled: bool = True
    dyon_snn_neurons: int = 50
    dyon_snn_anomaly_threshold: float = 0.5
    dyon_lsm_enabled: bool = True
    dyon_lsm_reservoir_size: int = 80
    dyon_lsm_anomaly_threshold: float = 0.7
    
    # Performance
    neuromorphic_latency_budget_ms: float = 30.0  # Python simulation (would be 3ms on hardware)
    enable_stdp_learning: bool = True
    stdp_learning_rate: float = 0.1


@dataclass
class Phase3Config:
    """Configuration for Phase 3 Advanced Modules."""
    
    # RL Optimizer
    rl_enabled: bool = True
    rl_learning_rate: float = 0.01
    rl_episodes: int = 1000
    rl_epsilon: float = 0.1
    
    # XAI System
    xai_enabled: bool = True
    xai_explanation_method: str = "shap"  # shap, lime, integrated_gradients
    xai_importance_threshold: float = 0.1
    
    # Multi-Agent System
    multi_agent_enabled: bool = True
    agent_count: int = 5
    agent_communication_protocol: str = "message_passing"
    
    # Temporal Reasoning
    temporal_enabled: bool = True
    temporal_window_size: int = 100
    temporal_prediction_horizon: int = 10
    
    # Dynamic Risk Manager
    risk_manager_enabled: bool = True
    risk_threshold: float = 0.8
    risk_update_interval_ms: int = 1000


@dataclass
class Phase4Config:
    """Configuration for Phase 4 Advanced Modules."""
    
    # Neuro-Symbolic AI
    neuro_symbolic_enabled: bool = True
    neural_symbolic_integration_weight: float = 0.5
    symbolic_reasoning_engine: str = "prolog"
    
    # Meta-Cognitive System
    meta_cognitive_enabled: bool = True
    self_reflection_interval_ms: int = 5000
    meta_learning_enabled: bool = True
    
    # Advanced Causal Discovery
    causal_discovery_enabled: bool = True
    causal_algorithm: str = "pc"  # pc, ges, fci
    causal_significance_level: float = 0.05


@dataclass
class SystemConfig:
    """Unified configuration for the entire DIX VISION system."""
    
    system_id: str = "dix_vision_v42.2"
    environment: str = "production"  # development, staging, production
    
    # Neuromorphic Configuration
    neuromorphic: NeuromorphicConfig = field(default_factory=NeuromorphicConfig)
    
    # Phase 3 Configuration
    phase3: Phase3Config = field(default_factory=Phase3Config)
    
    # Phase 4 Configuration
    phase4: Phase4Config = field(default_factory=Phase4Config)
    
    # Execution System
    execution_latency_budget_ms: float = 5.0
    max_concurrent_orders: int = 10
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "logs/dix_vision.log"
    
    # Performance
    enable_performance_monitoring: bool = True
    performance_metrics_interval_ms: int = 1000


class ConfigurationManager:
    """Centralized configuration management for DIX VISION."""
    
    def __init__(self, config_file: Optional[str] = None):
        self._config: SystemConfig = SystemConfig()
        self._config_file = config_file or "config/system_config.json"
        
        # Load configuration if file exists
        if os.path.exists(self._config_file):
            self.load_config()
    
    def load_config(self) -> None:
        """Load configuration from file."""
        try:
            with open(self._config_file, 'r') as f:
                config_dict = json.load(f)
                self._config = self._dict_to_config(config_dict)
                logger.info(f"Configuration loaded from {self._config_file}")
        except Exception as e:
            logger.warning(f"Failed to load configuration from {self._config_file}: {e}")
            logger.info("Using default configuration")
    
    def save_config(self) -> None:
        """Save configuration to file."""
        try:
            config_dir = os.path.dirname(self._config_file)
            if config_dir and not os.path.exists(config_dir):
                os.makedirs(config_dir)
            
            with open(self._config_file, 'w') as f:
                json.dump(asdict(self._config), f, indent=2)
            logger.info(f"Configuration saved to {self._config_file}")
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
    
    def get_config(self) -> SystemConfig:
        """Get current configuration."""
        return self._config
    
    def update_config(self, config_updates: Dict[str, Any]) -> None:
        """Update configuration with provided updates."""
        try:
            self._merge_config_updates(self._config, config_updates)
            logger.info("Configuration updated")
        except Exception as e:
            logger.error(f"Failed to update configuration: {e}")
    
    def _dict_to_config(self, config_dict: Dict[str, Any]) -> SystemConfig:
        """Convert dictionary to SystemConfig object."""
        # Handle neuromorphic config
        neuromorphic_dict = config_dict.get('neuromorphic', {})
        neuromorphic = NeuromorphicConfig(**neuromorphic_dict)
        
        # Handle phase3 config
        phase3_dict = config_dict.get('phase3', {})
        phase3 = Phase3Config(**phase3_dict)
        
        # Handle phase4 config
        phase4_dict = config_dict.get('phase4', {})
        phase4 = Phase4Config(**phase4_dict)
        
        return SystemConfig(
            system_id=config_dict.get('system_id', 'dix_vision_v42.2'),
            environment=config_dict.get('environment', 'production'),
            neuromorphic=neuromorphic,
            phase3=phase3,
            phase4=phase4,
            execution_latency_budget_ms=config_dict.get('execution_latency_budget_ms', 5.0),
            max_concurrent_orders=config_dict.get('max_concurrent_orders', 10),
            log_level=config_dict.get('log_level', 'INFO'),
            log_file=config_dict.get('log_file', 'logs/dix_vision.log'),
            enable_performance_monitoring=config_dict.get('enable_performance_monitoring', True),
            performance_metrics_interval_ms=config_dict.get('performance_metrics_interval_ms', 1000),
        )
    
    def _merge_config_updates(self, config: Any, updates: Dict[str, Any]) -> None:
        """Recursively merge configuration updates."""
        for key, value in updates.items():
            if hasattr(config, key):
                if isinstance(value, dict) and hasattr(getattr(config, key), '__dict__'):
                    self._merge_config_updates(getattr(config, key), value)
                else:
                    setattr(config, key, value)
    
    def get_neuromorphic_config(self) -> NeuromorphicConfig:
        """Get neuromorphic configuration."""
        return self._config.neuromorphic
    
    def get_phase3_config(self) -> Phase3Config:
        """Get Phase 3 configuration."""
        return self._config.phase3
    
    def get_phase4_config(self) -> Phase4Config:
        """Get Phase 4 configuration."""
        return self._config.phase4


# Singleton instance
_config_manager: Optional[ConfigurationManager] = None
_config_manager_lock = object()  # Using object as lock for simplicity

def get_config_manager(config_file: Optional[str] = None) -> ConfigurationManager:
    """Get the singleton configuration manager instance."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigurationManager(config_file)
    return _config_manager


__all__ = [
    "NeuromorphicConfig",
    "Phase3Config",
    "Phase4Config",
    "SystemConfig",
    "ConfigurationManager",
    "get_config_manager",
]