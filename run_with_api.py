"""
run_with_api.py
DIX VISION v42.2 — Runtime with API Server

Runs both the main runtime kernel and the FastAPI API server simultaneously.
This enables the Dashboard2026 to connect to real system data.
"""

import asyncio
import signal as signal_mod
import sys
import threading
import subprocess
from typing import Optional

import uvicorn


def run_main_system():
    """Run the main DIX VISION system in a separate thread."""
    from main import main
    try:
        main()
    except KeyboardInterrupt:
        pass


def run_api_server_thread(host: str = "127.0.0.1", port: int = 8000):
    """Run the API server in a separate thread."""
    from api_server import app
    
    # Configure uvicorn
    config = uvicorn.Config(
        app=app,
        host=host,
        port=port,
        log_level="info",
        access_log=True
    )
    
    server = uvicorn.Server(config)
    
    try:
        # Run in current thread (will be run in separate thread)
        asyncio.run(server.serve())
    except KeyboardInterrupt:
        pass


def main_with_api():
    """Run both the main system and API server."""
    import logging
    logger = logging.getLogger(__name__)
    
    host = "127.0.0.1"
    port = 8000
    
    # Parse command line args
    if "--host" in sys.argv:
        host_idx = sys.argv.index("--host")
        if host_idx + 1 < len(sys.argv):
            host = sys.argv[host_idx + 1]
    
    if "--port" in sys.argv:
        port_idx = sys.argv.index("--port")
        if port_idx + 1 < len(sys.argv):
            port = int(sys.argv[port_idx + 1])
    
    logger.info(f"[DIX VISION] Starting system with API server on {host}:{port}")
    
    # Start API server in separate thread
    api_thread = threading.Thread(
        target=run_api_server_thread,
        args=(host, port),
        daemon=True,
        name="API-Server"
    )
    api_thread.start()
    
    logger.info(f"[DIX VISION] API server thread started")
    
    # Run main system in main thread
    try:
        from main import main
        main()
    except KeyboardInterrupt:
        logger.info("[DIX VISION] Shutdown signal received")
    finally:
        logger.info("[DIX VISION] Shutting down")


if __name__ == "__main__":
    main_with_api()
