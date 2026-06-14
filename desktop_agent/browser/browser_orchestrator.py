"""
DIX VISION v42.2+ Desktop Agent - Browser Layer Orchestrator
Browser system orchestrator - Phase 3 implementation
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, Optional


class BrowserOrchestrator:
    """Browser layer orchestrator - coordinates browser system components."""
    
    def __init__(self, parent_orchestrator):
        """Initialize the browser orchestrator."""
        self.parent = parent_orchestrator
        self.logger = logging.getLogger("browser_orchestrator")
        self.logger.setLevel(logging.INFO)
        
        # Browser system components
        self._browser_controller: Optional[Any] = None
        self._tab_manager: Optional[Any] = None
        self._profile_manager: Optional[Any] = None
        
        # State
        self._initialized = False
        self._running = False
        
        # Workflow tracking
        self._active_workflows: Dict[str, asyncio.Task] = {}
        
        # Browser system status
        self._browser_status = {
            "browser_open": False,
            "current_url": None,
            "active_tab": None,
            "active_profile": None,
            "workflows_executed": 0,
        }
        
        self.logger.info("Browser Orchestrator created")
    
    async def initialize(self) -> bool:
        """Initialize the browser orchestrator."""
        try:
            self.logger.info("Initializing Browser Orchestrator...")
            
            # Initialize browser controller
            try:
                import sys
                import os
                browser_dir = os.path.dirname(os.path.abspath(__file__))
                if browser_dir not in sys.path:
                    sys.path.insert(0, browser_dir)
                
                from browser_controller import BrowserController
                self._browser_controller = BrowserController()
                await self._browser_controller.initialize()
                self.logger.info("Browser Controller initialized")
            except ImportError as ie:
                self.logger.warning(f"Browser controller import failed: {ie}")
                self._browser_controller = None
            except Exception as e:
                self.logger.warning(f"Browser controller initialization failed: {e}")
                self._browser_controller = None
            
            # Initialize tab manager
            try:
                from tab_manager import TabManager
                self._tab_manager = TabManager()
                await self._tab_manager.initialize()
                self.logger.info("Tab Manager initialized")
            except ImportError as ie:
                self.logger.warning(f"Tab manager import failed: {ie}")
                self._tab_manager = None
            except Exception as e:
                self.logger.warning(f"Tab manager initialization failed: {e}")
                self._tab_manager = None
            
            # Initialize profile manager
            try:
                from profile_manager import ProfileManager
                self._profile_manager = ProfileManager()
                await self._profile_manager.initialize()
                self.logger.info("Profile Manager initialized")
            except ImportError as ie:
                self.logger.warning(f"Profile manager import failed: {ie}")
                self._profile_manager = None
            except Exception as e:
                self.logger.warning(f"Profile manager initialization failed: {e}")
                self._profile_manager = None
            
            self._initialized = True
            self.logger.info("Browser Orchestrator initialized successfully (Phase 3)")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Browser Orchestrator: {e}")
            return False
    
    async def start(self) -> bool:
        """Start the browser orchestrator."""
        try:
            if not self._initialized:
                await self.initialize()
            
            self.logger.info("Starting Browser Orchestrator...")
            
            # Start browser controller if available
            if self._browser_controller:
                try:
                    await self._browser_controller.open_browser()
                    self._browser_status["browser_open"] = True
                except Exception as e:
                    self.logger.warning(f"Failed to start browser controller: {e}")
            else:
                self.logger.info("Browser controller not available")
            
            self._running = True
            self.logger.info("Browser Orchestrator started successfully (Phase 3)")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start Browser Orchestrator: {e}")
            return False
    
    async def stop(self) -> bool:
        """Stop the browser orchestrator."""
        try:
            self.logger.info("Stopping Browser Orchestrator...")
            
            # Stop browser controller
            if self._browser_controller:
                try:
                    await self._browser_controller.close_browser()
                    self._browser_status["browser_open"] = False
                except Exception as e:
                    self.logger.warning(f"Failed to stop browser controller: {e}")
            
            # Cancel active workflows
            for workflow_id, task in self._active_workflows.items():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
            
            self._active_workflows.clear()
            self._running = False
            self.logger.info("Browser Orchestrator stopped successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to stop Browser Orchestrator: {e}")
            return False
    
    async def execute_workflow(self, workflow: Dict[str, Any]) -> bool:
        """Execute a browser workflow (Phase 3 implementation)."""
        try:
            workflow_id = workflow.get("id", "unknown")
            
            self.logger.info(f"Executing browser workflow: {workflow_id}")
            
            # Extract workflow details
            action = workflow.get("action", "")
            
            if action == "navigate" and self._browser_controller:
                url = workflow.get("url", "")
                if url:
                    await self._browser_controller.navigate_to(url)
                    self._browser_status["current_url"] = url
            
            elif action == "click" and self._browser_controller:
                selector = workflow.get("selector", "")
                if selector:
                    await self._browser_controller.click_element(selector)
            
            elif action == "type" and self._browser_controller:
                selector = workflow.get("selector", "")
                text = workflow.get("text", "")
                if selector and text:
                    await self._browser_controller.type_text(selector, text)
            
            elif action == "screenshot" and self._browser_controller:
                filename = workflow.get("filename", "screenshot.png")
                await self._browser_controller.take_screenshot(filename)
            
            elif action == "create_tab" and self._tab_manager:
                url = workflow.get("url", None)
                tab_id = await self._tab_manager.create_tab(url)
                if tab_id:
                    self._browser_status["active_tab"] = tab_id
            
            elif action == "switch_tab" and self._tab_manager:
                tab_id = workflow.get("tab_id", "")
                if tab_id:
                    await self._tab_manager.switch_to_tab(tab_id)
                    self._browser_status["active_tab"] = tab_id
            
            elif action == "close_tab" and self._tab_manager:
                tab_id = workflow.get("tab_id", "")
                if tab_id:
                    await self._tab_manager.close_tab(tab_id)
            
            elif action == "switch_profile" and self._profile_manager:
                profile_id = workflow.get("profile_id", "")
                if profile_id:
                    await self._profile_manager.switch_to_profile(profile_id)
                    self._browser_status["active_profile"] = profile_id
            
            self._browser_status["workflows_executed"] += 1
            self.logger.info(f"Browser workflow {workflow_id} completed")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to execute browser workflow: {e}")
            return False
    
    async def get_browser_status(self) -> Optional[str]:
        """Get current browser URL."""
        try:
            if self._browser_controller:
                return await self._browser_controller.get_current_url()
            return None
        except Exception as e:
            self.logger.error(f"Failed to get browser status: {e}")
            return None
    
    async def create_tab(self, url: Optional[str] = None) -> Optional[str]:
        """Create a new browser tab."""
        try:
            if self._tab_manager:
                return await self._tab_manager.create_tab(url)
            return None
        except Exception as e:
            self.logger.error(f"Failed to create tab: {e}")
            return None
    
    async def navigate_to(self, url: str) -> bool:
        """Navigate to a URL."""
        try:
            if self._browser_controller:
                return await self._browser_controller.navigate_to(url)
            return False
        except Exception as e:
            self.logger.error(f"Failed to navigate to {url}: {e}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get orchestrator status."""
        return {
            "initialized": self._initialized,
            "running": self._running,
            "phase": "Phase 3 - Browser System",
            "browser_status": self._browser_status,
            "active_workflows": len(self._active_workflows),
            "components_available": {
                "browser_controller": self._browser_controller is not None,
                "tab_manager": self._tab_manager is not None,
                "profile_manager": self._profile_manager is not None,
            },
            "component_statuses": {
                "browser_controller": self._browser_controller.get_status() if self._browser_controller else None,
                "tab_manager": self._tab_manager.get_status() if self._tab_manager else None,
                "profile_manager": self._profile_manager.get_status() if self._profile_manager else None,
            },
        }
    
    @property
    def browser_controller(self) -> Optional[Any]:
        """Get the browser controller instance."""
        return self._browser_controller
    
    @property
    def is_running(self) -> bool:
        """Check if orchestrator is running."""
        return self._running
