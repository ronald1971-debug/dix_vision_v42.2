"""
DIX VISION Desktop AgentOS - Production Startup Script

Production-ready startup script for the DIX VISION backend system.
This script starts the Desktop AgentOS without requiring the Tauri desktop app.
"""

import sys
import os
import asyncio
import logging
import signal
from pathlib import Path

# Add project root to path
project_root = str(Path(__file__).parent)
sys.path.insert(0, project_root)
os.chdir(project_root)

# Set Python path environment variable
os.environ['PYTHONPATH'] = project_root

from desktop_agent.runtime.runtime import AgentRuntime
from desktop_agent.environment.manager import EnvironmentManager
from desktop_agent.environment.registry import EnvironmentRegistry
from desktop_agent.browser.bridge import BrowserCognitiveBridge
from desktop_agent.agents.indira import INDIRAAgent
from desktop_agent.agents.dyon import DYONAgent
from desktop_agent.memory.indira_memory import INDIRAMemory
from desktop_agent.memory.dyon_memory import DYONMemory
from desktop_agent.skills.registry import SkillRegistry

# Optional imports with graceful handling
try:
    from desktop_agent.hud.hud import INDIRAHUD, DYONHUD
    HUD_AVAILABLE = True
except ImportError as e:
    HUD_AVAILABLE = False
    print(f"[INFO] HUD components not available: {e}")

try:
    from desktop_agent.telemetry.telemetry import TelemetrySystem
    TELEMETRY_AVAILABLE = True
except ImportError as e:
    TELEMETRY_AVAILABLE = False
    print(f"[INFO] Telemetry system not available (install psutil with: pip install psutil)")

# Configure production logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('dix_vision_desktop.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class ProductionAgentOS:
    """Production-ready AgentOS launcher."""
    
    def __init__(self):
        """Initialize production AgentOS."""
        self.runtime = None
        self.indira_agent = None
        self.dyon_agent = None
        self.skill_registry = None
        self.is_running = False
        
        self.logger = logger
        
    async def initialize_backend(self):
        """Initialize the Python backend components."""
        self.logger.info("=" * 60)
        self.logger.info("DIX VISION Desktop AgentOS - Production Startup")
        self.logger.info("=" * 60)
        
        try:
            # Create runtime
            self.logger.info("Initializing Agent Runtime...")
            self.runtime = AgentRuntime()
            await self.runtime.initialize()
            
            # Create environment manager
            self.logger.info("Creating Environment Manager...")
            env_registry = EnvironmentRegistry()
            env_manager = EnvironmentManager(env_registry)
            
            # Register browser environment
            env_registry.register(
                "browser",
                BrowserCognitiveBridge,
                {"description": "Browser automation environment"}
            )
            
            # Create agents
            self.logger.info("Initializing INDIRA Agent (Market Intelligence)...")
            self.indira_agent = INDIRAAgent(self.runtime)
            await self.indira_agent.initialize()
            
            self.logger.info("Initializing DYON Agent (Engineering Intelligence)...")
            self.dyon_agent = DYONAgent(self.runtime)
            await self.dyon_agent.initialize()
            
            # Register agents with runtime
            self.runtime.register_agent("indira", self.indira_agent)
            self.runtime.register_agent("dyon", self.dyon_agent)
            
            # Create memory systems
            self.logger.info("Initializing INDIRA Memory...")
            indira_memory = INDIRAMemory()
            await indira_memory.initialize()
            
            self.logger.info("Initializing DYON Memory...")
            dyon_memory = DYONMemory()
            await dyon_memory.initialize()
            
            # Create skill registry
            self.logger.info("Creating Skill Registry...")
            self.skill_registry = SkillRegistry(self.runtime)
            
            # Create HUD systems if available
            if HUD_AVAILABLE:
                self.logger.info("Initializing HUD Systems...")
                indira_hud = INDIRAHUD()
                dyon_hud = DYONHUD()
                await indira_hud.initialize()
                await dyon_hud.initialize()
            else:
                self.logger.info("HUD Systems skipped (not available)")
                
            # Create telemetry system if available
            if TELEMETRY_AVAILABLE:
                self.logger.info("Initializing Telemetry System...")
                self.telemetry = TelemetrySystem()
                await self.telemetry.initialize()
            else:
                self.logger.info("Telemetry System skipped (not available)")
                self.telemetry = None
                
            self.logger.info("=" * 60)
            self.logger.info("✓ Backend Components Initialized Successfully")
            self.logger.info("=" * 60)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Backend initialization failed: {e}")
            return False
            
    async def start_backend(self):
        """Start the Python backend."""
        try:
            self.logger.info("Starting DIX VISION Desktop AgentOS Backend...")
            await self.runtime.start()
            self.is_running = True
            
            self.logger.info("=" * 60)
            self.logger.info("✓ Backend Started Successfully")
            self.logger.info("=" * 60)
            self.logger.info("")
            self.logger.info("SYSTEM READY FOR USE")
            self.logger.info("-" * 60)
            self.logger.info("INDIRA Agent: Ready for market research tasks")
            self.logger.info("DYON Agent: Ready for engineering tasks")
            self.logger.info("Browser Bridge: Ready for web automation")
            self.logger.info("Skill System: Ready for custom automations")
            self.logger.info("-" * 60)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Backend startup failed: {e}")
            return False
            
    async def shutdown(self):
        """Shutdown the system gracefully."""
        self.logger.info("Shutting down DIX VISION Desktop AgentOS...")
        self.is_running = False
        
        if self.runtime:
            await self.runtime.stop()
            
        self.logger.info("DIX VISION Desktop AgentOS shutdown complete")
        
    def get_status(self) -> dict:
        """Get current system status."""
        status = {
            "backend_initialized": self.runtime is not None,
            "agents_loaded": {
                "indira": self.indira_agent is not None,
                "dyon": self.dyon_agent is not None,
            },
            "is_running": self.is_running,
            "components": {
                "hud": HUD_AVAILABLE,
                "telemetry": TELEMETRY_AVAILABLE,
            }
        }
        
        if self.runtime:
            status["runtime_status"] = self.runtime.get_status()
            
        return status


async def main():
    """Main production entry point."""
    agentos = ProductionAgentOS()
    
    # Setup signal handlers for graceful shutdown
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}, shutting down...")
        asyncio.create_task(agentos.shutdown())
        
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Initialize backend
        if not await agentos.initialize_backend():
            logger.error("Failed to initialize backend. Exiting.")
            sys.exit(1)
            
        # Start backend
        if not await agentos.start_backend():
            logger.error("Failed to start backend. Exiting.")
            sys.exit(1)
            
        # Keep running until shutdown signal
        logger.info("System running. Press Ctrl+C to shutdown.")
        logger.info("")
        
        # Display status every 60 seconds
        while agentos.is_running:
            await asyncio.sleep(60)
            status = agentos.get_status()
            logger.info(f"System Status: {status['is_running']}")
            
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down...")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        await agentos.shutdown()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Shutdown complete")
