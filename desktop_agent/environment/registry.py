"""
Environment Registry - Environment type registration and discovery
"""

import logging
from typing import Dict, Type, Optional, List
from .interface import EnvironmentInterface


class EnvironmentRegistry:
    """
    Registry for environment types.
    
    Manages registration and discovery of environment implementations
    with support for factory pattern and dependency resolution.
    """
    
    def __init__(self):
        """Initialize environment registry."""
        self.environments: Dict[str, Type[EnvironmentInterface]] = {}
        self.metadata: Dict[str, Dict[str, any]] = {}
        
        self.logger = logging.getLogger(__name__)
        
    def register(
        self,
        env_type: str,
        env_class: Type[EnvironmentInterface],
        metadata: Dict[str, any] = None,
    ) -> None:
        """
        Register an environment type.
        
        Args:
            env_type: Environment type identifier
            env_class: Environment class
            metadata: Optional metadata
        """
        self.environments[env_type] = env_class
        if metadata:
            self.metadata[env_type] = metadata
            
        self.logger.info(f"Registered environment type: {env_type}")
        
    def unregister(self, env_type: str) -> None:
        """
        Unregister an environment type.
        
        Args:
            env_type: Environment type identifier
        """
        if env_type in self.environments:
            del self.environments[env_type]
        if env_type in self.metadata:
            del self.metadata[env_type]
            
        self.logger.info(f"Unregistered environment type: {env_type}")
        
    def get(self, env_type: str) -> Optional[Type[EnvironmentInterface]]:
        """
        Get an environment class by type.
        
        Args:
            env_type: Environment type identifier
            
        Returns:
            Environment class or None
        """
        return self.environments.get(env_type)
        
    def get_metadata(self, env_type: str) -> Optional[Dict[str, any]]:
        """
        Get metadata for an environment type.
        
        Args:
            env_type: Environment type identifier
            
        Returns:
            Metadata dictionary or None
        """
        return self.metadata.get(env_type)
        
    def list_environments(self) -> List[str]:
        """
        List all registered environment types.
        
        Returns:
            List of environment type identifiers
        """
        return list(self.environments.keys())
        
    def is_registered(self, env_type: str) -> bool:
        """
        Check if an environment type is registered.
        
        Args:
            env_type: Environment type identifier
            
        Returns:
            True if registered, False otherwise
        """
        return env_type in self.environments
        
    def create(
        self,
        env_type: str,
        config: Dict[str, any] = None,
    ) -> Optional[EnvironmentInterface]:
        """
        Create an environment instance.
        
        Args:
            env_type: Environment type identifier
            config: Environment configuration
            
        Returns:
            Environment instance or None
        """
        env_class = self.get(env_type)
        if not env_class:
            self.logger.error(f"Unknown environment type: {env_type}")
            return None
            
        try:
            return env_class(config)
        except Exception as e:
            self.logger.error(f"Error creating environment {env_type}: {e}")
            return None
