"""
system_monitor/dyon_engine.py
DIX VISION v42.2 — Dyon System Maintenance Engine

Dyon's domain: system health, maintenance, hazard detection.
CANNOT execute trades. CANNOT call exchange trading APIs.
Emits SYSTEM_HAZARD_EVENTs via async bus only.
"""

from __future__ import annotations

from core.authority import assert_no_adapter_import

assert_no_adapter_import(__name__)

import threading
import time

from system.audit_logger import get_audit_logger
from system.health_monitor import get_health_monitor
from system.logger import get_logger
from system.state import get_state_manager

# Use canonical import paths
from system_monitor.hazard_bus import get_hazard_detector, get_hazard_emitter


class DyonEngine:
    """
    System maintenance and observation engine.

    Can:  monitor health, emit hazards, manage patches, restart services
    Cannot: execute trades, call exchange APIs, override governance
    """

    def __init__(self) -> None:
        self._state = get_state_manager()
        self._log = get_logger("dyon")
        self._health = get_health_monitor()
        self._audit = get_audit_logger()
        self._detector = get_hazard_detector()
        self._emitter = get_hazard_emitter("dyon.engine")
        self._running = False
        self._thread: threading.Thread | None = None

        # NEW: DYON brain adapter integration (v42.2)
        self._dyon_brain_adapter = None
        try:
            from system_monitor.dyon_brain_adapter import get_dyon_brain_adapter

            self._dyon_brain_adapter = get_dyon_brain_adapter()
            self._dyon_adapter_initialized = True
        except Exception:
            # New brain integration optional - fail gracefully
            self._dyon_brain_adapter = None
            self._dyon_adapter_initialized = False

    def start(self) -> None:
        self._detector.start()
        self._running = True
        # ``Thread`` objects cannot be restarted; re-create on every
        # ``start()`` so graceful restart (stop → start) works.
        if self._thread is None or not self._thread.is_alive():
            self._thread = threading.Thread(target=self._loop, daemon=True, name="Dyon-Engine")
            self._thread.start()
        self._log.info("Dyon system engine started")
        self._audit.log("SYSTEM", "dyon.engine", {"event": "ENGINE_START"})

    def stop(self) -> None:
        self._running = False
        self._detector.stop()

    def _loop(self) -> None:
        while self._running:
            try:
                self._health_check()
                self._state.heartbeat()  # Dyon updates its own domain heartbeat
            except Exception as e:
                self._log.error("Dyon loop error", error=str(e))
            time.sleep(1.0)

    def _health_check(self) -> None:
        state = self._state.get()
        is_ok = state.health >= 0.5 and state.mode not in {"EMERGENCY_HALT"}
        self._health.report("dyon", is_ok)

    def record_feed_tick(self, feed_name: str) -> None:
        """Inform hazard detector that a feed is alive."""
        self._detector.record_feed_tick(feed_name)

    def record_execution_latency(self, component: str, ms: float) -> None:
        """Pass execution latency to hazard detector for spike detection."""
        self._detector.record_latency(component, ms)

    def analyze_system_issue_with_new_architecture(self, issue: str, context: dict = None) -> dict:
        """
        Analyze system issue with optional new cognitive architecture enhancement.

        This method provides enhanced system analysis using the new DYON Brain Adapter
        when available, while maintaining backward compatibility with the legacy system.

        Args:
            issue: Description of the system issue to analyze.
            context: Additional context about the issue (optional).

        Returns:
            dict: Analysis results with optional cognitive enhancement.
        """
        context = context or {}
        system_data = {
            "issue": issue,
            "context": context,
            "health": self._health.get_status() if hasattr(self._health, "get_status") else {},
            "state": self._state.get().__dict__ if hasattr(self._state, "get") else {},
        }

        # Try to enhance with new DYON brain adapter
        if self._dyon_brain_adapter:
            try:
                enhanced = self._dyon_brain_adapter.analyze_system_issue(
                    issue=issue,
                    context=system_data,
                    reasoning_mode="causal",  # Default to causal reasoning for system issues
                )

                if enhanced and enhanced.get("analysis_type") == "enhanced_cognitive":
                    return enhanced
            except Exception as e:
                self._log.warning(f"New DYON brain analysis failed: {e}")

        # Fallback to legacy analysis
        return {
            "analysis_type": "legacy",
            "issue": issue,
            "conclusion": f"Standard analysis: {issue}",
            "confidence": 0.5,
            "reasoning_mode": "simple",
            "reasoning_steps": ["Basic system check"],
            "neural_reasoning": "",
            "symbolic_reasoning": "",
            "recommendations": ["Monitor system health", "Check hazard detector"],
            "latency_ms": 0.0,
            "integration_mode": "fallback",
            "reasoning_quality": "basic",
        }


_dyon: DyonEngine | None = None
_lock = threading.Lock()


def get_dyon_engine() -> DyonEngine:
    global _dyon
    if _dyon is None:
        with _lock:
            if _dyon is None:
                _dyon = DyonEngine()
    return _dyon
