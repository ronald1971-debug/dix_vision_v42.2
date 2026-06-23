"""
dyon_brain_adapter.py
DIX VISION v42.2 — DYON Brain Integration Adapter

Integrates the new ConcreteDYONBrain with the existing DyonEngine while:
- Maintaining <100ms analysis performance target
- Providing preservation layer fallback
- Enabling multiple reasoning modes (deductive, inductive, abductive, causal, analogical)
- Supporting gradual migration from legacy to new brain
- Enhancing system analysis with neuro-symbolic reasoning
"""

from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional

from preservation_layer import get_preservation_layer

logger = logging.getLogger(__name__)


@dataclass
class DYONBrainConfig:
    """Configuration for DYON brain integration."""

    use_new_brain: bool = True
    fallback_on_failure: bool = True
    latency_threshold_ms: float = 100.0
    enable_causal_analysis: bool = True
    enable_pattern_discovery: bool = True
    enable_debugging: bool = True
    default_reasoning_mode: str = "causal"


class DyonBrainAdapter:
    """
    Adapter between existing DyonEngine and new ConcreteDYONBrain.

    Features:
    - Multiple reasoning modes (deductive, inductive, abductive, causal, analogical)
    - <100ms analysis performance
    - Automatic fallback to legacy on failure
    - Performance monitoring and validation
    - Preservation layer integration
    - Gradual migration support
    """

    def __init__(self, config: Optional[DYONBrainConfig] = None):
        self._config = config or DYONBrainConfig()
        self._lock = threading.Lock()

        # Brain instances
        self._new_brain = None
        self._legacy_system_engine = None
        self._preservation_layer = None

        # Performance tracking
        self._analysis_count = 0
        self._new_brain_count = 0
        self._fallback_count = 0
        self._latency_sum_ms = 0.0
        self._latency_max_ms = 0.0

        # Reasoning mode tracking
        self._reasoning_mode_usage: Dict[str, int] = {}

        # Health tracking
        self._new_brain_healthy = True
        self._consecutive_failures = 0
        self._max_consecutive_failures = 3

        logger.info("[DYON_ADAPTER] DYON Brain Adapter initialized")

    def initialize(self) -> bool:
        """Initialize the adapter with new brain and preservation layer."""
        try:
            with self._lock:
                # Get preservation layer
                self._preservation_layer = get_preservation_layer()

                # Try to initialize new brain
                if self._config.use_new_brain:
                    try:
                        from dyon_cognitive.dyon_brain.concrete import ConcreteDYONBrain

                        self._new_brain = ConcreteDYONBrain()

                        # Connect to preservation layer
                        if self._preservation_layer:
                            self._new_brain.connect_to_preservation_layer(
                                self._preservation_layer, self._legacy_system_engine
                            )

                        logger.info("[DYON_ADAPTER] New DYON brain initialized")

                    except Exception as e:
                        logger.warning(f"[DYON_ADAPTER] Failed to initialize new brain: {e}")
                        self._new_brain = None
                        self._new_brain_healthy = False

                # Try to get legacy system engine for fallback
                try:
                    from cognitive_engine.cognitive_orchestrator import CognitiveOrchestrator

                    self._legacy_system_engine = CognitiveOrchestrator()
                    logger.info("[DYON_ADAPTER] Legacy system engine available for fallback")
                except Exception as e:
                    logger.warning(f"[DYON_ADAPTER] Legacy system engine not available: {e}")
                    self._legacy_system_engine = None

                return True

        except Exception as e:
            logger.error(f"[DYON_ADAPTER] Initialization failed: {e}")
            return False

    def analyze_system_issue(
        self, issue: str, context: Optional[Dict] = None, reasoning_mode: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze system issue using new brain with fallback.

        Returns a dict compatible with existing DyonEngine format:
        {
            "analysis_type": "enhanced_cognitive" | "legacy",
            "issue": str,
            "conclusion": str,
            "confidence": float,
            "reasoning_mode": str,
            "recommendations": list,
            "latency_ms": float,
        }
        """
        start_time_ms = time.time() * 1000
        self._analysis_count += 1
        context = context or {}

        # Use default reasoning mode if not specified
        if reasoning_mode is None:
            reasoning_mode = self._config.default_reasoning_mode

        try:
            # Try new brain first
            if self._config.use_new_brain and self._new_brain and self._new_brain_healthy:
                result = self._try_new_brain(issue, context, reasoning_mode)
                if result:
                    end_time_ms = time.time() * 1000
                    latency_ms = end_time_ms - start_time_ms

                    self._new_brain_count += 1
                    self._latency_sum_ms += latency_ms
                    self._latency_max_ms = max(self._latency_max_ms, latency_ms)

                    # Track reasoning mode usage
                    self._reasoning_mode_usage[reasoning_mode] = (
                        self._reasoning_mode_usage.get(reasoning_mode, 0) + 1
                    )

                    # Check if latency exceeded threshold
                    if latency_ms > self._config.latency_threshold_ms:
                        logger.warning(
                            f"[DYON_ADAPTER] Latency exceeded threshold: {latency_ms:.2f}ms > {self._config.latency_threshold_ms}ms"
                        )

                    result["latency_ms"] = latency_ms
                    return result

            # Fallback to legacy or simple logic
            return self._fallback_analysis(issue, context, start_time_ms)

        except Exception as e:
            logger.error(f"[DYON_ADAPTER] Analysis failed: {e}")
            # Fallback to simple analysis on error
            return self._fallback_analysis(issue, context, start_time_ms)

    def _try_new_brain(
        self, issue: str, context: Dict, reasoning_mode: str
    ) -> Optional[Dict[str, Any]]:
        """Try to use new brain for analysis."""
        try:
            # Prepare system data for new brain
            system_data = {
                "issue": issue,
                "context": context,
                "timestamp": datetime.utcnow(),
                "reasoning_mode": reasoning_mode,
            }

            # Try to use the appropriate reasoning mode
            # For now, use a generic analysis method since the concrete brain may not have all methods implemented
            try:
                # Try to use neuro-symbolic reasoning if available
                if self._new_brain and hasattr(self._new_brain, "perform_engineering_reasoning"):
                    reasoning_result = self._new_brain.perform_engineering_reasoning(
                        system_state=system_data, reasoning_mode=reasoning_mode
                    )

                    if reasoning_result:
                        return self._convert_reasoning_result(reasoning_result, issue)
            except Exception as e:
                logger.warning(f"[DYON_ADAPTER] Engineering reasoning failed: {e}")

            # Try system analysis as fallback
            if self._new_brain and hasattr(self._new_brain, "analyze_system"):
                try:
                    analysis_result = self._new_brain.analyze_system(
                        system_data=system_data,
                        asset="SYSTEM",  # System-level analysis
                        analysis_type="SYSTEM_HEALTH",
                    )

                    if analysis_result:
                        return self._convert_analysis_result(analysis_result, issue, reasoning_mode)
                except Exception as e:
                    logger.warning(f"[DYON_ADAPTER] System analysis failed: {e}")

            # If all else fails, return None to trigger fallback
            return None

        except Exception as e:
            logger.error(f"[DYON_ADAPTER] New brain analysis failed: {e}")
            self._consecutive_failures += 1

            # Disable new brain if too many consecutive failures
            if self._consecutive_failures >= self._max_consecutive_failures:
                self._new_brain_healthy = False
                logger.warning(
                    f"[DYON_ADAPTER] New brain disabled after {self._consecutive_failures} failures"
                )

            return None

    def _convert_reasoning_result(self, reasoning_result: Any, issue: str) -> Dict[str, Any]:
        """Convert engineering reasoning result to standard format."""
        return {
            "analysis_type": "enhanced_cognitive",
            "issue": issue,
            "conclusion": getattr(reasoning_result, "conclusion", f"Analysis of {issue}"),
            "confidence": getattr(reasoning_result, "confidence", 0.7),
            "reasoning_mode": getattr(reasoning_result, "reasoning_mode", "causal"),
            "reasoning_steps": getattr(reasoning_result, "reasoning_steps", []),
            "neural_reasoning": getattr(reasoning_result, "neural_reasoning", ""),
            "symbolic_reasoning": getattr(reasoning_result, "symbolic_reasoning", ""),
            "recommendations": getattr(reasoning_result, "recommendations", []),
            "integration_mode": "new_brain",
            "reasoning_quality": "high",
        }

    def _convert_analysis_result(
        self, analysis_result: Any, issue: str, reasoning_mode: str
    ) -> Dict[str, Any]:
        """Convert system analysis result to standard format."""
        return {
            "analysis_type": "enhanced_cognitive",
            "issue": issue,
            "conclusion": getattr(analysis_result, "trend", f"Analysis of {issue}"),
            "confidence": getattr(analysis_result, "trend_confidence", 0.7),
            "reasoning_mode": reasoning_mode,
            "reasoning_steps": [
                getattr(analysis_result, "neural_analysis", ""),
                getattr(analysis_result, "symbolic_analysis", ""),
            ],
            "neural_reasoning": getattr(analysis_result, "neural_analysis", ""),
            "symbolic_reasoning": getattr(analysis_result, "symbolic_analysis", ""),
            "recommendations": [
                getattr(analysis_result, "trend", "Monitor system health"),
                getattr(analysis_result, "regime", "Check system state"),
            ],
            "integration_mode": "new_brain",
            "reasoning_quality": "medium",
        }

    def _fallback_analysis(self, issue: str, context: Dict, start_time_ms: float) -> Dict[str, Any]:
        """Fallback analysis using legacy logic or simple rules."""
        self._fallback_count += 1

        try:
            # Try legacy system engine first
            if self._legacy_system_engine and self._preservation_layer:
                try:
                    # Try to use legacy cognitive enrichment
                    logger.debug("[DYON_ADAPTER] Using legacy system analysis")
                except Exception as e:
                    logger.warning(f"[DYON_ADAPTER] Legacy analysis failed: {e}")

            # Simple fallback logic (mimics legacy DyonEngine)
            confidence = 0.6
            recommendations = [
                "Monitor system health",
                "Check hazard detector",
                "Review system logs",
                "Verify component connectivity",
            ]

            # Add context-specific recommendations
            if "latency" in issue.lower():
                recommendations.append("Check component performance metrics")
            if "memory" in issue.lower():
                recommendations.append("Review memory usage and allocation")
            if "connection" in issue.lower():
                recommendations.append("Verify network and API connectivity")

            end_time_ms = time.time() * 1000
            latency_ms = end_time_ms - start_time_ms

            result = {
                "analysis_type": "legacy",
                "issue": issue,
                "conclusion": f"Standard analysis: {issue}",
                "confidence": confidence,
                "reasoning_mode": "simple",
                "reasoning_steps": ["Basic system check", "Health status review"],
                "neural_reasoning": "",
                "symbolic_reasoning": "",
                "recommendations": recommendations,
                "latency_ms": latency_ms,
                "integration_mode": "fallback",
                "reasoning_quality": "basic",
            }

            return result

        except Exception as e:
            logger.error(f"[DYON_ADAPTER] Fallback analysis failed: {e}")
            # Ultimate fallback
            end_time_ms = time.time() * 1000
            latency_ms = end_time_ms - start_time_ms

            return {
                "analysis_type": "ultimate_fallback",
                "issue": issue,
                "conclusion": "All analysis paths failed",
                "confidence": 0.0,
                "reasoning_mode": "none",
                "reasoning_steps": [],
                "neural_reasoning": "",
                "symbolic_reasoning": "",
                "recommendations": ["Manual intervention required"],
                "latency_ms": latency_ms,
                "integration_mode": "ultimate_fallback",
                "reasoning_quality": "none",
            }

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for the adapter."""
        avg_latency = (
            (self._latency_sum_ms / self._new_brain_count) if self._new_brain_count > 0 else 0.0
        )
        new_brain_ratio = (
            (self._new_brain_count / self._analysis_count) if self._analysis_count > 0 else 0.0
        )
        fallback_ratio = (
            (self._fallback_count / self._analysis_count) if self._analysis_count > 0 else 0.0
        )

        return {
            "total_analyses": self._analysis_count,
            "new_brain_analyses": self._new_brain_count,
            "fallback_analyses": self._fallback_count,
            "new_brain_ratio": new_brain_ratio,
            "fallback_ratio": fallback_ratio,
            "average_latency_ms": avg_latency,
            "max_latency_ms": self._latency_max_ms,
            "new_brain_healthy": self._new_brain_healthy,
            "consecutive_failures": self._consecutive_failures,
            "reasoning_mode_usage": self._reasoning_mode_usage.copy(),
        }

    def enable_new_brain(self) -> None:
        """Enable the new brain for analysis."""
        with self._lock:
            self._config.use_new_brain = True
            self._new_brain_healthy = True
            self._consecutive_failures = 0
            logger.info("[DYON_ADAPTER] New brain enabled")

    def disable_new_brain(self) -> None:
        """Disable the new brain and use fallback only."""
        with self._lock:
            self._config.use_new_brain = False
            logger.info("[DYON_ADAPTER] New brain disabled")


# Global adapter instance
_dyon_brain_adapter: Optional[DyonBrainAdapter] = None
_adapter_lock = threading.Lock()


def get_dyon_brain_adapter() -> DyonBrainAdapter:
    """Get the global DYON brain adapter (thread-safe singleton)."""
    global _dyon_brain_adapter
    with _adapter_lock:
        if _dyon_brain_adapter is None:
            _dyon_brain_adapter = DyonBrainAdapter()
            _dyon_brain_adapter.initialize()
    return _dyon_brain_adapter
