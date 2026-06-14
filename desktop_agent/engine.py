"""
DIX VISION v42.2+ Desktop Agent - Core Engine
Main orchestration engine for the Desktop Agent System
"""

from __future__ import annotations

import asyncio
import logging
import sys
from pathlib import Path
from typing import Any, Dict, Optional

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))
sys.path.append(str(Path(__file__).parent.parent / "governance"))
sys.path.append(str(Path(__file__).parent.parent / "coordination_layer"))
sys.path.append(str(Path(__file__).parent.parent / "system"))


class DesktopAgentEngine:
    """Core orchestration engine for Desktop Agent System."""
    
    def __init__(self):
        """Initialize the Desktop Agent Engine."""
        self.logger = logging.getLogger("desktop_agent_engine")
        self.logger.setLevel(logging.INFO)
        
        # Core components
        self._orchestrator: Optional[Any] = None
        self._authority_router: Optional[Any] = None
        self._session_manager: Optional[Any] = None
        self._activity_tracker: Optional[Any] = None
        
        # State management
        self._running = False
        self._initialized = False
        
        # Configuration
        self._config: Dict[str, Any] = {}
        
        self.logger.info("Desktop Agent Engine initialized")
    
    async def initialize(self, config: Optional[Dict[str, Any]] = None) -> bool:
        """Initialize all Desktop Agent components."""
        try:
            self.logger.info("Initializing Desktop Agent components...")
            
            # Load configuration
            self._config = config or {}
            
            # Initialize orchestrator (will be imported after creation)
            from orchestrator import DesktopAgentOrchestrator
            self._orchestrator = DesktopAgentOrchestrator(self)
            await self._orchestrator.initialize()
            
            # Initialize authority router
            from authority_router import DesktopAgentAuthorityRouter
            self._authority_router = DesktopAgentAuthorityRouter()
            await self._authority_router.initialize()
            
            # Initialize session manager
            from session_manager import DesktopAgentSessionManager
            self._session_manager = DesktopAgentSessionManager()
            await self._session_manager.initialize()
            
            # Initialize activity tracker
            from activity_tracker import DesktopAgentActivityTracker
            self._activity_tracker = DesktopAgentActivityTracker()
            await self._activity_tracker.initialize()
            
            self._initialized = True
            self.logger.info("Desktop Agent components initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Desktop Agent: {e}")
            return False
    
    async def start(self) -> bool:
        """Start the Desktop Agent Engine."""
        try:
            if not self._initialized:
                await self.initialize()
            
            self.logger.info("Starting Desktop Agent Engine...")
            
            # Start orchestrator
            if self._orchestrator:
                await self._orchestrator.start()
            
            # Start session manager
            if self._session_manager:
                await self._session_manager.start()
            
            # Start activity tracker
            if self._activity_tracker:
                await self._activity_tracker.start()
            
            self._running = True
            self.logger.info("Desktop Agent Engine started successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start Desktop Agent Engine: {e}")
            return False
    
    async def stop(self) -> bool:
        """Stop the Desktop Agent Engine."""
        try:
            self.logger.info("Stopping Desktop Agent Engine...")
            
            # Stop activity tracker
            if self._activity_tracker:
                await self._activity_tracker.stop()
            
            # Stop session manager
            if self._session_manager:
                await self._session_manager.stop()
            
            # Stop orchestrator
            if self._orchestrator:
                await self._orchestrator.stop()
            
            self._running = False
            self.logger.info("Desktop Agent Engine stopped successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to stop Desktop Agent Engine: {e}")
            return False
    
    @property
    def orchestrator(self) -> Optional[Any]:
        """Get the orchestrator component."""
        return self._orchestrator
    
    @property
    def authority_router(self) -> Optional[Any]:
        """Get the authority router component."""
        return self._authority_router
    
    @property
    def session_manager(self) -> Optional[Any]:
        """Get the session manager component."""
        return self._session_manager
    
    @property
    def activity_tracker(self) -> Optional[Any]:
        """Get the activity tracker component."""
        return self._activity_tracker
    
    @property
    def is_running(self) -> bool:
        """Check if the engine is running."""
        return self._running
    
    @property
    def is_initialized(self) -> bool:
        """Check if the engine is initialized."""
        return self._initialized
    
    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the engine."""
        return {
            "running": self._running,
            "initialized": self._initialized,
            "orchestrator_status": self._orchestrator.get_status() if self._orchestrator else None,
            "authority_router_status": self._authority_router.get_status() if self._authority_router else None,
            "session_manager_status": self._session_manager.get_status() if self._session_manager else None,
            "activity_tracker_status": self._activity_tracker.get_status() if self._activity_tracker else None,
        }


async def main():
    """Main entry point for Desktop Agent Engine."""
    engine = DesktopAgentEngine()
    
    try:
        success = await engine.start()
        if success:
            print("Desktop Agent Engine started successfully")
            # Keep engine running
            while engine.is_running:
                await asyncio.sleep(1)
        else:
            print("Failed to start Desktop Agent Engine")
            sys.exit(1)
    except KeyboardInterrupt:
        print("Shutting down Desktop Agent Engine...")
        await engine.stop()
    except Exception as e:
        print(f"Desktop Agent Engine error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
