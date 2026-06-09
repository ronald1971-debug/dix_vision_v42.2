"""
Agent Runtime - Core orchestration and execution engine
"""

import asyncio
import logging
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime

from .scheduler import TaskScheduler
from .event_bus import EventBus
from .config import Configuration
from .lifecycle import LifecycleManager


class AgentRuntime:
    """
    Core runtime for Desktop AgentOS.
    
    Manages agent lifecycle, task execution, event routing,
    and provides the foundation for cognitive environment interaction.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the Agent Runtime.
        
        Args:
            config_path: Optional path to configuration file
        """
        self.config = Configuration(config_path)
        self.event_bus = EventBus()
        self.scheduler = TaskScheduler(self.event_bus)
        self.lifecycle = LifecycleManager(self)
        
        self.agents: Dict[str, Any] = {}
        self.plugins: Dict[str, Any] = {}
        self.is_running = False
        
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
    async def initialize(self) -> None:
        """Initialize the runtime and all components."""
        self.logger.info("Initializing Desktop AgentOS Runtime...")
        
        # Initialize event bus
        await self.event_bus.initialize()
        
        # Initialize scheduler
        await self.scheduler.initialize()
        
        # Register lifecycle hooks
        self.lifecycle.register_startup_hook(self._on_startup)
        self.lifecycle.register_shutdown_hook(self._on_shutdown)
        
        self.logger.info("Desktop AgentOS Runtime initialized")
        
    async def start(self) -> None:
        """Start the runtime and all agents."""
        self.logger.info("Starting Desktop AgentOS Runtime...")
        
        await self.lifecycle.startup()
        
        self.is_running = True
        
        # Start scheduler
        await self.scheduler.start()
        
        self.logger.info("Desktop AgentOS Runtime started")
        
    async def stop(self) -> None:
        """Stop the runtime and all agents."""
        self.logger.info("Stopping Desktop AgentOS Runtime...")
        
        self.is_running = False
        
        # Stop scheduler
        await self.scheduler.stop()
        
        # Shutdown lifecycle
        await self.lifecycle.shutdown()
        
        self.logger.info("Desktop AgentOS Runtime stopped")
        
    def register_agent(self, name: str, agent: Any) -> None:
        """
        Register an agent with the runtime.
        
        Args:
            name: Agent identifier
            agent: Agent instance
        """
        self.agents[name] = agent
        self.logger.info(f"Registered agent: {name}")
        
    def unregister_agent(self, name: str) -> None:
        """
        Unregister an agent from the runtime.
        
        Args:
            name: Agent identifier
        """
        if name in self.agents:
            del self.agents[name]
            self.logger.info(f"Unregistered agent: {name}")
            
    def get_agent(self, name: str) -> Optional[Any]:
        """
        Get a registered agent.
        
        Args:
            name: Agent identifier
            
        Returns:
            Agent instance or None
        """
        return self.agents.get(name)
        
    def register_plugin(self, name: str, plugin: Any) -> None:
        """
        Register a plugin with the runtime.
        
        Args:
            name: Plugin identifier
            plugin: Plugin instance
        """
        self.plugins[name] = plugin
        self.logger.info(f"Registered plugin: {name}")
        
    def unregister_plugin(self, name: str) -> None:
        """
        Unregister a plugin from the runtime.
        
        Args:
            name: Plugin identifier
        """
        if name in self.plugins:
            del self.plugins[name]
            self.logger.info(f"Unregistered plugin: {name}")
            
    async def _on_startup(self) -> None:
        """Runtime startup hook."""
        self.logger.info("Runtime startup hook executed")
        
    async def _on_shutdown(self) -> None:
        """Runtime shutdown hook."""
        self.logger.info("Runtime shutdown hook executed")
        
    def get_status(self) -> Dict[str, Any]:
        """
        Get current runtime status.
        
        Returns:
            Status dictionary
        """
        return {
            "is_running": self.is_running,
            "agents": list(self.agents.keys()),
            "plugins": list(self.plugins.keys()),
            "timestamp": datetime.utcnow().isoformat(),
        }
