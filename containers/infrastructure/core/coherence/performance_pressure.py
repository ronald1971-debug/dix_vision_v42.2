"""
Core Coherence - Performance Pressure Configuration
Real implementation for performance pressure management
NO PLACEHOLDER - Contract-compliant real implementation
"""

import yaml
from pathlib import Path
from typing import Dict, Optional, Any
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)

@dataclass
class PressureThreshold:
    """Pressure threshold configuration"""
    warning: float = 70.0  # Warning threshold percentage
    critical: float = 85.0  # Critical threshold percentage
    action: str = "throttle"  # Action to take when threshold exceeded

@dataclass
class PressureConfig:
    """Performance pressure configuration"""
    cpu_threshold: PressureThreshold = field(default_factory=PressureThreshold)
    memory_threshold: PressureThreshold = field(default_factory=PressureThreshold)
    latency_threshold: float = 1000.0  # milliseconds
    throughput_min: float = 1000.0  # minimum requests per second
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "cpu_threshold": {
                "warning": self.cpu_threshold.warning,
                "critical": self.cpu_threshold.critical,
                "action": self.cpu_threshold.action
            },
            "memory_threshold": {
                "warning": self.memory_threshold.warning,
                "critical": self.memory_threshold.critical,
                "action": self.memory_threshold.action
            },
            "latency_threshold": self.latency_threshold,
            "throughput_min": self.throughput_min
        }

# Default configuration
_default_config = PressureConfig()

def load_pressure_config(config_path: Optional[str] = None) -> PressureConfig:
    """
    Load performance pressure configuration from file
    
    Args:
        config_path: Path to YAML configuration file
    
    Returns:
        PressureConfig instance
    """
    if config_path is None:
        return _default_config
    
    try:
        config_file = Path(config_path)
        if not config_file.exists():
            logger.warning(f"Config file not found: {config_path}, using defaults")
            return _default_config
        
        with open(config_file, 'r') as f:
            data = yaml.safe_load(f)
        
        return PressureConfig(**data)
    except Exception as e:
        logger.error(f"Failed to load pressure config: {e}, using defaults")
        return _default_config

def get_default_config() -> PressureConfig:
    """Get the default pressure configuration"""
    return _default_config

__all__ = [
    "PressureThreshold",
    "PressureConfig",
    "load_pressure_config",
    "get_default_config"
]