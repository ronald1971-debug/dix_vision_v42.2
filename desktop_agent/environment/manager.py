"""
Environment Manager - Environment lifecycle and coordination
"""

import asyncio
import logging
from typing import Dict, Optional, List, Any
from .interface import EnvironmentInterface, StateSnapshot
from .registry import EnvironmentRegistry


class EnvironmentManager:
    """
    Manager for environment instances.
    
    Handles creation, lifecycle management, and coordination
    of multiple environment instances with session management.
    """
    
    def __init__(self, registry: EnvironmentRegistry):
        """
        Initialize environment manager.
        
        Args:
            registry: Environment registry
        """
        self.registry = registry
        self.environments: Dict[str, EnvironmentInterface] = {}
        self.active_sessions: Dict[str, str] = {}
        
        self.logger = logging.getLogger(__name__)
        
    async def create_environment(
        self,
        env_id: str,
        env_type: str,
        config: Dict[str, Any] = None,
    ) -> Optional[EnvironmentInterface]:
        """
        Create and register a new environment instance.
        
        Args:
            env_id: Environment instance identifier
            env_type: Environment type
            config: Environment configuration
            
        Returns:
            Environment instance or None
        """
        if env_id in self.environments:
            self.logger.warning(f"Environment {env_id} already exists")
            return self.environments[env_id]
            
        env = self.registry.create(env_type, config)
        if not env:
            return None
            
        try:
            connected = await env.connect()
            if not connected:
                self.logger.error(f"Failed to connect environment {env_id}")
                return None
                
            self.environments[env_id] = env
            self.active_sessions[env_id] = env.session_id or env_id
            
            self.logger.info(f"Created environment: {env_id} (type: {env_type})")
            return env
            
        except Exception as e:
            self.logger.error(f"Error creating environment {env_id}: {e}")
            return None
            
    async def destroy_environment(self, env_id: str) -> None:
        """
        Destroy an environment instance.
        
        Args:
            env_id: Environment identifier
        """
        if env_id in self.environments:
            try:
                await self.environments[env_id].disconnect()
                del self.environments[env_id]
                if env_id in self.active_sessions:
                    del self.active_sessions[env_id]
                self.logger.info(f"Destroyed environment: {env_id}")
            except Exception as e:
                self.logger.error(f"Error destroying environment {env_id}: {e}")
                
    def get_environment(self, env_id: str) -> Optional[EnvironmentInterface]:
        """
        Get an environment instance.
        
        Args:
            env_id: Environment identifier
            
        Returns:
            Environment instance or None
        """
        return self.environments.get(env_id)
        
    async def observe_all(self) -> Dict[str, StateSnapshot]:
        """
        Observe all active environments.
        
        Returns:
            Dictionary of environment snapshots
        """
        snapshots = {}
        
        for env_id, env in self.environments.items():
            try:
                snapshot = await env.observe()
                snapshots[env_id] = snapshot
            except Exception as e:
                self.logger.error(f"Error observing {env_id}: {e}")
                
        return snapshots
        
    async def search_all(self, query: str) -> Dict[str, List[Any]]:
        """
        Search across all active environments.
        
        Args:
            query: Search query
            
        Returns:
            Dictionary of search results per environment
        """
        results = {}
        
        for env_id, env in self.environments.items():
            try:
                elements = await env.search(query)
                results[env_id] = elements
            except Exception as e:
                self.logger.error(f"Error searching {env_id}: {e}")
                
        return results
        
    def list_environments(self) -> List[str]:
        """
        List all active environment instances.
        
        Returns:
            List of environment identifiers
        """
        return list(self.environments.keys())
        
    def get_status(self) -> Dict[str, Any]:
        """
        Get manager status.
        
        Returns:
            Status dictionary
        """
        return {
            "environments": list(self.environments.keys()),
            "sessions": self.active_sessions.copy(),
            "registered_types": self.registry.list_environments(),
        }
        
    async def cleanup(self) -> None:
        """Clean up all environment instances."""
        env_ids = list(self.environments.keys())
        
        for env_id in env_ids:
            await self.destroy_environment(env_id)
            
        self.logger.info("Environment manager cleanup complete")
