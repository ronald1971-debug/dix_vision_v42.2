"""
DIX VISION v42.2 - Unified Bootstrap System

This is the SINGLE entry point for the entire DIX VISION system.
It replaces all scattered launch scripts and entry points with a unified
orchestrator that can handle all deployment scenarios.

Usage:
    python bootstrap.py [command] [options]

Commands:
    desktop           - Launch Desktop AgentOS with Tauri frontend
    dashboard        - Launch React dashboard with Python backend
    backend          - Launch Python backend only
    docker           - Launch full Docker stack
    dev              - Launch development environment
    portable         - Launch portable .exe mode

Options:
    --host HOST      - Bind host (default: 127.0.0.1)
    --port PORT      - Port number (default: mode-specific)
    --mode MODE      - Operation mode (desktop/production/dev)
    --no-browser     - Don't auto-open browser
    --help           - Show this help message
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import os
import subprocess
import sys
import threading
import time
import webbrowser
from pathlib import Path
from typing import Any

# Import unified memory manager
try:
    from memory_manager import get_memory_manager, start_memory_monitoring
    MEMORY_MANAGER_AVAILABLE = True
except ImportError as e:
    MEMORY_MANAGER_AVAILABLE = False
    print(f"[WARNING] Memory manager not available: {e}")

# Import unified config manager
try:
    from config_manager import get_config, set_config_value
    CONFIG_MANAGER_AVAILABLE = True
except ImportError as e:
    CONFIG_MANAGER_AVAILABLE = False
    print(f"[WARNING] Config manager not available: {e}")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


class DIXVisionBootstrap:
    """Unified bootstrap system for DIX VISION."""

    def __init__(self):
        """Initialize bootstrap system."""
        self.project_root = Path(__file__).parent
        
        # Initialize unified config manager
        self.config_manager = None
        if CONFIG_MANAGER_AVAILABLE:
            self.config_manager = get_config(self.project_root)
            self.config = self.config_manager.get_all()
            logger.info("Config manager initialized")
        else:
            self.config = self._load_config()
        
        self.processes = []
        
        # Initialize memory manager if available
        self.memory_manager = None
        if MEMORY_MANAGER_AVAILABLE and self.config.get("memory", {}).get("enable_monitoring", True):
            self.memory_manager = get_memory_manager()
            logger.info("Memory manager initialized")

    def _load_config(self) -> dict[str, Any]:
        """Load system configuration."""
        config = {
            "default_mode": "desktop",
            "default_host": "127.0.0.1",
            "ports": {
                "desktop": 8765,
                "dashboard": 8080,
                "backend": 8000,
                "docker_backend": 8080,
                "docker_dashboard": 5173,
            },
            "paths": {
                "desktop_app": self.project_root / "dix_desktop",
                "dashboard": self.project_root / "containers" / "user_interfaces" / "dashboard2026",
                "backend": self.project_root / "containers" / "user_interfaces" / "ui",
                "docker_compose": self.project_root / "docker-compose.main.yml",
            },
            "memory": {
                "warning_threshold": 70,
                "critical_threshold": 85,
                "process_limit": 1024,
                "enable_monitoring": True,
            },
            "features": {
                "enable_metrics": True,
                "enable_monitoring": True,
                "enable_telemetry": False,
                "enable_debug_mode": False,
            },
        }
        
        # Load from config file if exists
        config_file = self.project_root / "config" / "system_config.yaml"
        if config_file.exists():
            try:
                import yaml
                with open(config_file, 'r') as f:
                    file_config = yaml.safe_load(f)
                    if file_config:
                        self._merge_config(config, file_config)
            except ImportError:
                logger.warning("PyYAML not available, using default configuration")
            except Exception as e:
                logger.warning(f"Failed to load config file: {e}")
        
        return config

    def _merge_config(self, base: dict[str, Any], override: dict[str, Any]) -> None:
        """Recursively merge override config into base config."""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_config(base[key], value)
            else:
                base[key] = value

    def _setup_python_path(self):
        """Setup Python path for all containers."""
        paths = [
            str(self.project_root),
            str(self.project_root / "containers" / "infrastructure"),
            str(self.project_root / "containers" / "infrastructure" / "core"),
            str(self.project_root / "containers" / "system_core"),
            str(self.project_root / "containers" / "system_core" / "system"),
            str(self.project_root / "containers" / "system_core" / "system_unified"),
            str(self.project_root / "containers" / "system_core" / "evolution_engine"),
            str(self.project_root / "containers" / "system_core" / "governance_unified"),
            str(self.project_root / "containers" / "system_core" / "execution_unified"),
            str(self.project_root / "containers" / "user_interfaces"),
            str(self.project_root / "containers" / "user_interfaces" / "dashboard_backend"),
        ]
        
        for path in paths:
            if Path(path).exists():
                sys.path.insert(0, path)
        
        os.environ["PYTHONPATH"] = os.pathsep.join(paths)

    def _setup_data_directory(self) -> Path:
        """Setup per-user data directory for portable mode."""
        base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
        root = Path(base) / "DIX VISION"
        (root / "data").mkdir(parents=True, exist_ok=True)
        (root / "logs").mkdir(parents=True, exist_ok=True)
        
        # Set environment variables
        os.environ.setdefault("DIX_MODE", "desktop")
        os.environ.setdefault("DIX_BIND_HOST", "127.0.0.1")
        os.environ["DIX_DATA_ROOT"] = str(root)
        os.environ["DIX_COCKPIT_TOKEN_FILE"] = str(root / "data" / "cockpit_token.txt")
        os.environ["DIX_PAIRING_DB"] = str(root / "data" / "pairing.sqlite")
        os.environ["DIX_LEDGER_DB"] = str(root / "data" / "ledger.sqlite")
        os.environ["DIX_EPISODIC_DB"] = str(root / "data" / "episodes.sqlite")
        os.environ["DIX_WALLET_POLICY_DB"] = str(root / "data" / "wallet_policy.sqlite")
        
        return root

    def _generate_token(self, data_dir: Path) -> str:
        """Generate or retrieve authentication token."""
        import secrets
        
        token_file = data_dir / "cockpit_token.txt"
        if token_file.is_file():
            token = token_file.read_text(encoding="utf-8").strip()
            if token:
                return token
        
        token = secrets.token_urlsafe(32)
        token_file.write_text(token, encoding="utf-8")
        return token

    def _open_browser(self, url: str, delay: float = 1.5):
        """Open browser to specified URL with delay."""
        def open():
            time.sleep(delay)
            webbrowser.open(url, new=2)
        
        threading.Thread(target=open, daemon=True).start()

    async def launch_desktop(self, args: argparse.Namespace):
        """Launch Desktop AgentOS with Tauri frontend."""
        logger.info("Launching DIX VISION Desktop AgentOS...")
        
        # Start memory monitoring if available
        if self.memory_manager:
            self.memory_manager.start_monitoring()
            logger.info("Memory monitoring started")
        
        self._setup_python_path()
        data_root = self._setup_data_directory()
        token = self._generate_token(data_root / "data")
        port = args.port or self.config["ports"]["desktop"]
        
        os.environ["DIX_PORT"] = str(port)
        os.environ["DIX_COCKPIT_TOKEN"] = token
        
        # Open browser to dashboard
        if not args.no_browser:
            self._open_browser(f"http://127.0.0.1:{port}/?token={token}")
        
        # Import and launch desktop components
        try:
            from desktop_agent.agents import DYONAgent, INDIRAAgent
            from desktop_agent.runtime import AgentRuntime
            
            runtime = AgentRuntime()
            await runtime.initialize()
            
            indira_agent = INDIRAAgent(runtime)
            dyon_agent = DYONAgent(runtime)
            
            await indira_agent.initialize()
            await dyon_agent.initialize()
            
            runtime.register_agent("indira", indira_agent)
            runtime.register_agent("dyon", dyon_agent)
            
            await runtime.start()
            
            logger.info("Desktop AgentOS started successfully")
            
            # Keep running
            try:
                while True:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                logger.info("Shutting down...")
                await runtime.stop()
                
        except ImportError as e:
            logger.error(f"Desktop components not available: {e}")
            logger.info("Falling back to backend-only mode")
            await self.launch_backend(args)
        finally:
            # Stop memory monitoring
            if self.memory_manager:
                self.memory_manager.stop_monitoring()
                logger.info("Memory monitoring stopped")

    async def launch_dashboard(self, args: argparse.Namespace):
        """Launch React dashboard with Python backend."""
        logger.info("Launching DIX VISION Dashboard...")
        
        self._setup_python_path()
        port = args.port or self.config["ports"]["dashboard"]
        host = args.host or self.config["default_host"]
        
        # Start backend in background
        backend_process = await self._start_backend_process(host, port)
        self.processes.append(backend_process)
        
        # Start React dashboard
        dashboard_path = self.config["paths"]["dashboard"]
        if dashboard_path.exists():
            os.chdir(dashboard_path)
            
            # Install dependencies if needed
            if not (dashboard_path / "node_modules").exists():
                logger.info("Installing dashboard dependencies...")
                subprocess.run(["npm", "install"], check=True)
            
            # Open browser
            if not args.no_browser:
                self._open_browser(f"http://localhost:5173/dash2/")
            
            # Start development server
            logger.info("Starting React dashboard...")
            subprocess.run(["npm", "run", "dev"])
        else:
            logger.error(f"Dashboard path not found: {dashboard_path}")

    async def launch_backend(self, args: argparse.Namespace):
        """Launch Python backend only."""
        logger.info("Launching DIX VISION Backend...")
        
        self._setup_python_path()
        port = args.port or self.config["ports"]["backend"]
        host = args.host or self.config["default_host"]
        
        # Open browser if requested
        if not args.no_browser:
            self._open_browser(f"http://{host}:{port}/docs")
        
        await self._start_backend_process(host, port, blocking=True)

    async def _start_backend_process(self, host: str, port: int, blocking: bool = False) -> subprocess.Popen:
        """Start backend server process."""
        backend_path = self.config["paths"]["backend"]
        if not backend_path.exists():
            raise FileNotFoundError(f"Backend path not found: {backend_path}")
        
        # Add backend to Python path and change directory
        sys.path.insert(0, str(backend_path))
        os.chdir(backend_path)
        
        if blocking:
            # Import and run server directly
            try:
                # Import server module
                import server
                logger.info(f"Starting backend server on http://{host}:{port}")
                
                # Simple HTTP server implementation
                from http.server import HTTPServer, BaseHTTPRequestHandler
                import json
                
                class BackendHandler(BaseHTTPRequestHandler):
                    def do_GET(self):
                        if self.path == "/health":
                            self.send_response(200)
                            self.send_header("Content-type", "application/json")
                            self.end_headers()
                            self.wfile.write(json.dumps({"status": "healthy"}).encode())
                        else:
                            self.send_response(200)
                            self.send_header("Content-type", "text/html")
                            self.end_headers()
                            self.wfile.write(b"DIX VISION Backend Running")
                    
                    def log_message(self, format, *args):
                        logger.info(format % args)
                
                server = HTTPServer((host, port), BackendHandler)
                logger.info(f"Backend server running on http://{host}:{port}")
                server.serve_forever()
                
            except Exception as e:
                logger.error(f"Failed to start backend: {e}")
                raise
            return None
        else:
            # For non-blocking, use subprocess with python http.server
            cmd = [sys.executable, "-m", "http.server", str(port), "--bind", host]
            process = subprocess.Popen(cmd)
            logger.info(f"Backend started on http://{host}:{port}")
            return process

    async def launch_docker(self, args: argparse.Namespace):
        """Launch full Docker stack."""
        if args.stop:
            await self.stop_docker(args)
            return
            
        logger.info("Launching DIX VISION Docker Stack...")
        
        docker_compose = self.config["paths"]["docker_compose"]
        if not docker_compose.exists():
            raise FileNotFoundError(f"Docker compose file not found: {docker_compose}")
        
        # Check Docker status
        try:
            subprocess.run(["docker", "ps"], check=True, capture_output=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.error("Docker is not running or not installed")
            return
        
        # Start containers
        os.chdir(self.project_root)
        subprocess.run(["docker-compose", "-f", str(docker_compose), "up", "-d"], check=True)
        
        # Wait for services
        logger.info("Waiting for services to initialize...")
        await asyncio.sleep(10)
        
        # Check status
        subprocess.run(["docker-compose", "-f", str(docker_compose), "ps"])
        
        # Open browser
        if not args.no_browser:
            self._open_browser("http://localhost:5173/")
        
        logger.info("Docker stack started successfully")

    async def stop_docker(self, args: argparse.Namespace):
        """Stop Docker stack."""
        logger.info("Stopping DIX VISION Docker Stack...")
        
        docker_compose = self.config["paths"]["docker_compose"]
        if not docker_compose.exists():
            raise FileNotFoundError(f"Docker compose file not found: {docker_compose}")
        
        os.chdir(self.project_root)
        subprocess.run(["docker-compose", "-f", str(docker_compose), "down"], check=True)
        
        logger.info("Docker stack stopped successfully")

    async def launch_dev(self, args: argparse.Namespace):
        """Launch development environment."""
        logger.info("Launching DIX VISION Development Environment...")
        
        self._setup_python_path()
        
        # Start backend in development mode
        await self.launch_dashboard(args)

    async def launch_portable(self, args: argparse.Namespace):
        """Launch portable .exe mode."""
        logger.info("Launching DIX VISION Portable Mode...")
        
        self._setup_data_directory()
        await self.launch_desktop(args)

    async def cleanup(self):
        """Cleanup resources and processes."""
        logger.info("Cleaning up...")
        
        for process in self.processes:
            if process and process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
        
        logger.info("Cleanup complete")


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="DIX VISION v42.2 - Unified Bootstrap System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python bootstrap.py desktop          # Launch Desktop AgentOS
    python bootstrap.py dashboard         # Launch React dashboard
    python bootstrap.py backend --port 9000  # Launch backend on custom port
    python bootstrap.py docker           # Launch Docker stack
    python bootstrap.py dev              # Launch development environment
        """
    )
    
    parser.add_argument(
        "command",
        choices=["desktop", "dashboard", "backend", "docker", "dev", "portable"],
        help="Command to execute"
    )
    
    parser.add_argument("--host", help="Bind host (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, help="Port number")
    parser.add_argument("--mode", help="Operation mode (desktop/production/dev)")
    parser.add_argument("--no-browser", action="store_true", help="Don't auto-open browser")
    parser.add_argument("--stop", action="store_true", help="Stop running services")
    
    return parser.parse_args()


async def main():
    """Main entry point."""
    args = parse_args()
    bootstrap = DIXVisionBootstrap()
    
    try:
        if args.command == "desktop":
            await bootstrap.launch_desktop(args)
        elif args.command == "dashboard":
            await bootstrap.launch_dashboard(args)
        elif args.command == "backend":
            await bootstrap.launch_backend(args)
        elif args.command == "docker":
            await bootstrap.launch_docker(args)
        elif args.command == "dev":
            await bootstrap.launch_dev(args)
        elif args.command == "portable":
            await bootstrap.launch_portable(args)
        else:
            logger.error(f"Unknown command: {args.command}")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)
    finally:
        await bootstrap.cleanup()


if __name__ == "__main__":
    asyncio.run(main())