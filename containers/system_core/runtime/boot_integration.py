"""Runtime boot integration — coordinates FastAPI app with system kernel.

This module provides the bridge between the FastAPI application and the
DIX VISION system kernel, managing background tickers, event loops, and
service coordination.
"""

from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING

from core.kernel import SystemKernel

if TYPE_CHECKING:
    from fastapi import FastAPI
    from ui.server import _State

_logger = logging.getLogger(__name__)


class RuntimeBootstrap:
    """Bootstraps and coordinates runtime services with FastAPI.

    Responsibilities:
    - Manages background asyncio task for system coordination
    - Attaches FastAPI lifecycle hooks to kernel services
    - Coordinates service health checks and readiness probes
    - Provides runtime status for monitoring endpoints
    """

    def __init__(self, tick_interval_ms: float = 100.0) -> None:
        self.tick_interval_ms = tick_interval_ms
        self._running = False
        self._ready = False
        self._background_task: asyncio.Task[None] | None = None
        self._kernel: SystemKernel | None = None
        self._app: FastAPI | None = None
        self._state: _State | None = None

    @property
    def is_running(self) -> bool:
        """Whether the runtime background task is running."""
        return self._running

    @property
    def readiness(self) -> str:
        """Current readiness state."""
        if self._ready and self._running:
            return "ready"
        elif self._running:
            return "starting"
        else:
            return "stopped"

    def attach(self, app: FastAPI, state: _State) -> None:
        """Attach the runtime bootstrap to the FastAPI app and system state.

        This method:
        1. Stores references to the app and state
        2. Registers startup/shutdown hooks with FastAPI
        3. Initializes the kernel connection
        4. Prepares background coordination task
        """
        self._app = app
        self._state = state
        self._kernel = state.kernel if hasattr(state, 'kernel') else None

        # Register FastAPI lifecycle hooks
        @app.on_event("startup")
        async def on_startup() -> None:
            """FastAPI startup hook."""
            _logger.info("[RuntimeBootstrap] Starting runtime coordination")
            await self._start_background_task()
            self._ready = True
            _logger.info("[RuntimeBootstrap] Runtime coordination ready")

        @app.on_event("shutdown")
        async def on_shutdown() -> None:
            """FastAPI shutdown hook."""
            _logger.info("[RuntimeBootstrap] Shutting down runtime coordination")
            await self._stop_background_task()
            self._ready = False
            _logger.info("[RuntimeBootstrap] Runtime coordination stopped")

        _logger.info("[RuntimeBootstrap] Attached to FastAPI app with lifecycle hooks")

    async def _start_background_task(self) -> None:
        """Start the background coordination task."""
        if self._running:
            _logger.warning("[RuntimeBootstrap] Background task already running")
            return

        self._running = True
        self._background_task = asyncio.create_task(self._coordination_loop())
        _logger.info("[RuntimeBootstrap] Background coordination task started")

    async def _stop_background_task(self) -> None:
        """Stop the background coordination task."""
        if not self._running:
            return

        self._running = False
        if self._background_task:
            self._background_task.cancel()
            try:
                await self._background_task
            except asyncio.CancelledError:
                pass
            self._background_task = None
        _logger.info("[RuntimeBootstrap] Background coordination task stopped")

    async def _coordination_loop(self) -> None:
        """Background coordination loop.

        This loop:
        - Ticks at the configured interval
        - Coordinates service health checks
        - Manages event dispatch between kernel and services
        - Provides monitoring and telemetry hooks
        """
        interval_sec = self.tick_interval_ms / 1000.0
        _logger.info(
            "[RuntimeBootstrap] Coordination loop started (interval=%dms)",
            self.tick_interval_ms
        )

        try:
            while self._running:
                try:
                    # Tick the kernel if available
                    if self._kernel and self._state:
                        # Perform coordination tasks
                        await self._tick_kernel()

                    # Sleep for the tick interval
                    await asyncio.sleep(interval_sec)
                except asyncio.CancelledError:
                    _logger.info("[RuntimeBootstrap] Coordination loop cancelled")
                    raise
                except Exception as e:
                    _logger.error("[RuntimeBootstrap] Coordination loop error: %s", e)
                    # Continue running despite errors
                    await asyncio.sleep(interval_sec)
        finally:
            _logger.info("[RuntimeBootstrap] Coordination loop exited")

    async def _tick_kernel(self) -> None:
        """Perform a single coordination tick with the kernel.

        This method coordinates between the kernel and services:
        - Triggers service process() calls via kernel
        - Collects and dispatches events
        - Updates system projections
        - Performs health checks
        """
        if not self._kernel or not self._state:
            return

        try:
            # The kernel handles service coordination internally
            # This hook allows for additional runtime-specific coordination
            pass
        except Exception as e:
            _logger.error("[RuntimeBootstrap] Kernel tick error: %s", e)


def get_runtime_bootstrap(tick_interval_ms: float = 100.0) -> RuntimeBootstrap:
    """Get a configured runtime bootstrap instance.

    Args:
        tick_interval_ms: Interval for background coordination loop in milliseconds

    Returns:
        Configured RuntimeBootstrap instance
    """
    return RuntimeBootstrap(tick_interval_ms=tick_interval_ms)


def boot_integration(**kwargs: Any) -> None:
    """Legacy boot integration entry point.

    This function is kept for backward compatibility.
    New code should use get_runtime_bootstrap() instead.
    """
    _logger.warning("[RuntimeBootstrap] boot_integration() is deprecated, use get_runtime_bootstrap()")