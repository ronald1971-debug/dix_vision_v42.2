"""
Lifecycle Management - Agent and component lifecycle control
"""

import asyncio
import logging
from typing import List, Callable, Optional
from enum import Enum


class LifecycleState(Enum):
    """Lifecycle states."""
    INITIALIZED = "initialized"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"


class LifecycleManager:
    """
    Manages lifecycle of runtime and components.
    
    Provides structured startup/shutdown procedures with
    hooks for custom initialization and cleanup logic.
    """
    
    def __init__(self, runtime):
        """
        Initialize lifecycle manager.
        
        Args:
            runtime: Reference to AgentRuntime instance
        """
        self.runtime = runtime
        self.state = LifecycleState.INITIALIZED
        self.startup_hooks: List[Callable] = []
        self.shutdown_hooks: List[Callable] = []
        
        self.logger = logging.getLogger(__name__)
        
    def register_startup_hook(self, hook: Callable) -> None:
        """
        Register a startup hook.
        
        Args:
            hook: Async function to call during startup
        """
        self.startup_hooks.append(hook)
        
    def register_shutdown_hook(self, hook: Callable) -> None:
        """
        Register a shutdown hook.
        
        Args:
            hook: Async function to call during shutdown
        """
        self.shutdown_hooks.append(hook)
        
    async def startup(self) -> None:
        """Execute startup sequence."""
        self.state = LifecycleState.STARTING
        self.logger.info("Starting lifecycle...")
        
        try:
            # Execute startup hooks
            for hook in self.startup_hooks:
                try:
                    if asyncio.iscoroutinefunction(hook):
                        await hook()
                    else:
                        hook()
                except Exception as e:
                    self.logger.error(f"Startup hook error: {e}")
                    
            self.state = LifecycleState.RUNNING
            self.logger.info("Lifecycle startup complete")
            
        except Exception as e:
            self.state = LifecycleState.ERROR
            self.logger.error(f"Startup error: {e}")
            raise
            
    async def shutdown(self) -> None:
        """Execute shutdown sequence."""
        self.state = LifecycleState.STOPPING
        self.logger.info("Stopping lifecycle...")
        
        try:
            # Execute shutdown hooks in reverse order
            for hook in reversed(self.shutdown_hooks):
                try:
                    if asyncio.iscoroutinefunction(hook):
                        await hook()
                    else:
                        hook()
                except Exception as e:
                    self.logger.error(f"Shutdown hook error: {e}")
                    
            self.state = LifecycleState.STOPPED
            self.logger.info("Lifecycle shutdown complete")
            
        except Exception as e:
            self.state = LifecycleState.ERROR
            self.logger.error(f"Shutdown error: {e}")
            raise
            
    def get_state(self) -> LifecycleState:
        """
        Get current lifecycle state.
        
        Returns:
            Current state
        """
        return self.state
        
    def is_running(self) -> bool:
        """
        Check if runtime is running.
        
        Returns:
            True if running, False otherwise
        """
        return self.state == LifecycleState.RUNNING
