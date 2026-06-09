"""
DIX VISION Desktop AgentOS - Main Launcher

Launches the DIX VISION Desktop AgentOS with integrated
interactive desktop capabilities based on Komorebi.
"""

import sys
import os
import subprocess
import asyncio
import logging
from pathlib import Path

# Add desktop_agent to path
sys.path.insert(0, str(Path(__file__).parent))

from desktop_agent.runtime import AgentRuntime
from desktop_agent.environment import EnvironmentManager, EnvironmentRegistry
from desktop_agent.browser import BrowserCognitiveBridge
from desktop_agent.agents import INDIRAAgent, DYONAgent
from desktop_agent.memory import INDIRAMemory, DYONMemory
from desktop_agent.skills import SkillRegistry
from desktop_agent.hud import INDIRAHUD, DYONHUD
from desktop_agent.telemetry import TelemetrySystem

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('dix_vision_desktop.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class DesktopAgentOSLauncher:
    """Main launcher for Desktop AgentOS."""
    
    def __init__(self):
        """Initialize launcher."""
        self.runtime = None
        self.indira_agent = None
        self.dyon_agent = None
        self.telemetry = None
        
    async def initialize_backend(self):
        """Initialize the Python backend components."""
        logger.info("Initializing DIX VISION Desktop AgentOS Backend...")
        
        # Create runtime
        self.runtime = AgentRuntime()
        await self.runtime.initialize()
        
        # Create environment manager
        env_registry = EnvironmentRegistry()
        env_manager = EnvironmentManager(env_registry)
        
        # Register browser environment
        env_registry.register(
            "browser",
            BrowserCognitiveBridge,
            {"description": "Browser automation environment"}
        )
        
        # Create agents
        self.indira_agent = INDIRAAgent(self.runtime)
        self.dyon_agent = DYONAgent(self.runtime)
        
        # Initialize agents
        await self.indira_agent.initialize()
        await self.dyon_agent.initialize()
        
        # Register agents with runtime
        self.runtime.register_agent("indira", self.indira_agent)
        self.runtime.register_agent("dyon", self.dyon_agent)
        
        # Create memory systems
        indira_memory = INDIRAMemory()
        dyon_memory = DYONMemory()
        await indira_memory.initialize()
        await dyon_memory.initialize()
        
        # Create skill registry
        skill_registry = SkillRegistry(self.runtime)
        
        # Create HUD systems
        indira_hud = INDIRAHUD()
        dyon_hud = DYONHUD()
        await indira_hud.initialize()
        await dyon_hud.initialize()
        
        # Create telemetry system
        self.telemetry = TelemetrySystem()
        await self.telemetry.initialize()
        
        logger.info("Backend components initialized successfully")
        
    async def start_backend(self):
        """Start the Python backend."""
        logger.info("Starting DIX VISION Desktop AgentOS Backend...")
        await self.runtime.start()
        logger.info("Backend started successfully")
        
    async def launch_desktop_app(self):
        """Launch the Tauri desktop application."""
        logger.info("Launching DIX VISION Desktop Application...")
        
        komorebi_path = Path(__file__).parent / "komorebi_desktop"
        
        if not komorebi_path.exists():
            logger.error(f"Desktop app path not found: {komorebi_path}")
            return False
            
        try:
            # Change to the desktop app directory
            os.chdir(komorebi_path)
            
            # Check if node_modules exists, if not install dependencies
            if not (komorebi_path / "node_modules").exists():
                logger.info("Installing dependencies...")
                subprocess.run(["npm", "install"], check=True)
                
            # Start the Tauri dev server
            logger.info("Starting Tauri application...")
            subprocess.run(["npm", "run", "tauri", "dev"], check=True)
            
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to launch desktop app: {e}")
            return False
        except Exception as e:
            logger.error(f"Error launching desktop app: {e}")
            return False
            
    async def run(self):
        """Run the complete Desktop AgentOS."""
        try:
            # Initialize backend
            await self.initialize_backend()
            
            # Start backend
            await self.start_backend()
            
            # Launch desktop app
            await self.launch_desktop_app()
            
        except KeyboardInterrupt:
            logger.info("Shutting down...")
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
        finally:
            # Cleanup
            if self.runtime:
                await self.runtime.stop()
            logger.info("DIX VISION Desktop AgentOS shutdown complete")


async def main():
    """Main entry point."""
    launcher = DesktopAgentOSLauncher()
    await launcher.run()


if __name__ == "__main__":
    asyncio.run(main())
