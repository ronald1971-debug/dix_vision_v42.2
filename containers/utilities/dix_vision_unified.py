"""
DIX VISION v42.2 — Unified System Entry Point

This is the main entry point that wires together all phases and modules
into a cohesive, production-ready system with full integration of:
- Phase 1: Knowledge Layer
- Phase 2: Governance System
- Phase 3: Advanced Cognitive Modules (RL, XAI, Multi-Agent, Temporal, Risk)
- Phase 4: Advanced AI (Neuro-Symbolic, Meta-Cognitive, Causal)
- Phase 5: Neuromorphic Computing (INDIRA & DYON SNN + LSM)
- Priority 3: Advanced AI Capabilities (Semantic Reasoning, AutoML, Knowledge Graph, Multi-Agent Orchestration, Cross-Modal)
- Execution System
- Configuration Management

This provides the true "all phases integrated and wired" experience.
"""

from __future__ import annotations

import logging
import threading
from datetime import datetime
from typing import Any, Dict, Optional

# Configuration
from cognitive_os.config import get_config_manager

# Cognitive OS
from cognitive_os.core import (
    CognitiveOSKernel,
    get_cognitive_os_kernel,
)

# Complete System Integration (All Priorities)
# Priority 3 Advanced AI Integration
from cognitive_os.integration import get_advanced_ai_integration, get_complete_system_integration
from dyon_cognitive.dyon_brain.concrete_enhanced import get_dyon_brain_enhanced

# Execution System
from execution_unified import get_unified_execution_kernel

# Enhanced Brains with Neuromorphic Integration
from indira_cognitive.indira_brain.concrete_enhanced import get_indira_brain_enhanced

logger = logging.getLogger(__name__)


class UnifiedDIXVISIONSystem:
    """Unified DIX VISION system with all phases integrated and wired."""

    def __init__(self):
        self._lock = threading.Lock()
        self._initialized = False

        # Core systems
        self._cognitive_os: Optional[CognitiveOSKernel] = None
        self._execution_kernel: Optional[Any] = None

        # Enhanced brains (Phase 5 neuromorphic integration)
        self._indira_brain_enhanced: Optional[Any] = None
        self._dyon_brain_enhanced: Optional[Any] = None

        # Priority 3 Advanced AI Integration
        self._advanced_ai_integration: Optional[Any] = None

        # Complete System Integration (All Priorities)
        self._complete_system_integration: Optional[Any] = None

        # Configuration
        self._config_manager = get_config_manager()

        # System metrics
        self._start_time: Optional[datetime] = None
        self._total_requests: int = 0
        self._successful_requests: int = 0

        logger.info("[DIX_VISION_UNIFIED] Unified DIX VISION System instance created")

    def initialize(self) -> bool:
        """Initialize the complete unified system with all phases."""
        with self._lock:
            if self._initialized:
                logger.warning("[DIX_VISION_UNIFIED] System already initialized")
                return True

            logger.info("[DIX_VISION_UNIFIED] Initializing complete DIX VISION v42.2 system...")

            try:
                # 1. Load configuration
                config = self._config_manager.get_config()
                logger.info(
                    f"[DIX_VISION_UNIFIED] Configuration loaded for environment: {config.environment}"
                )

                # 2. Initialize Cognitive OS (all phases integrated in kernel)
                self._cognitive_os = get_cognitive_os_kernel()
                self._cognitive_os.initialize_system()
                logger.info("[DIX_VISION_UNIFIED] Cognitive OS initialized with all phases")

                # 3. Initialize Enhanced Brains with Neuromorphic Integration
                self._indira_brain_enhanced = get_indira_brain_enhanced()
                self._dyon_brain_enhanced = get_dyon_brain_enhanced()

                # Apply neuromorphic configuration
                neuromorphic_config = self._config_manager.get_neuromorphic_config()
                self._indira_brain_enhanced._enable_neuromorphic = (
                    neuromorphic_config.indira_snn_enabled
                )
                self._indira_brain_enhanced._neuromorphic_confidence_weight = (
                    neuromorphic_config.indira_snn_confidence_weight
                )
                self._dyon_brain_enhanced._enable_neuromorphic = (
                    neuromorphic_config.dyon_snn_enabled
                )

                logger.info(
                    "[DIX_VISION_UNIFIED] Enhanced brains initialized with neuromorphic components"
                )

                # 4. Initialize Execution Kernel
                self._execution_kernel = get_unified_execution_kernel()
                logger.info("[DIX_VISION_UNIFIED] Execution kernel initialized")

                # 5. Initialize Priority 3 Advanced AI Integration
                self._advanced_ai_integration = get_advanced_ai_integration()
                logger.info("[DIX_VISION_UNIFIED] Priority 3 Advanced AI Integration initialized")

                # 6. Initialize Complete System Integration (All Priorities)
                self._complete_system_integration = get_complete_system_integration()
                logger.info(
                    "[DIX_VISION_UNIFIED] Complete System Integration initialized with all priorities"
                )

                # 7. Mark system as initialized

                # 7. Mark system as initialized
                self._initialized = True
                self._start_time = datetime.utcnow()

                logger.info(
                    "[DIX_VISION_UNIFIED] Complete DIX VISION v42.2 system initialization SUCCESS"
                )
                return True

            except Exception as e:
                logger.error(f"[DIX_VISION_UNIFIED] System initialization FAILED: {e}")
                self._initialized = False
                return False

    def execute_trading_decision(self, market_state: Dict[str, Any], asset: str) -> Dict[str, Any]:
        """Execute trading decision with full neuromorphic integration."""
        if not self._initialized:
            raise RuntimeError("System not initialized. Call initialize() first.")

        self._total_requests += 1

        try:
            # Use enhanced INDIRA brain with neuromorphic integration
            decision = self._indira_brain_enhanced.execute_fast_trading_decision(
                market_state, asset
            )

            self._successful_requests += 1

            return {
                "success": True,
                "decision": {
                    "asset": decision.asset,
                    "side": decision.side,
                    "size_usd": decision.size_usd,
                    "confidence": decision.confidence,
                    "decision_type": decision.decision_type,
                    "reasoning_chain": decision.reasoning_chain,
                    "neuromorphic_enhanced": decision.metadata.get("neuromorphic_enhanced", False),
                    "neuromorphic_latency_ms": decision.metadata.get(
                        "neuromorphic_latency_ms", 0.0
                    ),
                    "confidence_breakdown": decision.confidence_breakdown,
                },
                "latency_ms": decision.execution_latency_ms,
                "timestamp": decision.decision_timestamp.isoformat(),
            }

        except Exception as e:
            logger.error(f"[DIX_VISION_UNIFIED] Trading decision execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
            }

    def analyze_system_with_neuromorphic(
        self, system_metrics: Dict[str, float], target: str = "system"
    ) -> Dict[str, Any]:
        """Analyze system with full neuromorphic integration."""
        if not self._initialized:
            raise RuntimeError("System not initialized. Call initialize() first.")

        try:
            # Use enhanced DYON brain with neuromorphic integration
            analysis = self._dyon_brain_enhanced.analyze_system_with_neuromorphic(
                system_metrics, target
            )

            return {
                "success": True,
                "analysis": {
                    "target": analysis.target,
                    "quality_score": analysis.quality_score,
                    "performance_score": analysis.performance_score,
                    "complexity_score": analysis.complexity_score,
                    "findings": analysis.findings,
                    "issues": analysis.issues,
                    "recommendations": analysis.recommendations,
                    "neuromorphic_enhanced": analysis.metadata.get("neuromorphic_enhanced", False),
                    "neuromorphic_anomaly_score": analysis.code_metrics.get(
                        "neuromorphic_anomaly_score", 0.0
                    ),
                },
                "timestamp": analysis.metadata.get("timestamp", datetime.utcnow().isoformat()),
            }

        except Exception as e:
            logger.error(f"[DIX_VISION_UNIFIED] System analysis failed: {e}")
            return {
                "success": False,
                "error": str(e),
            }

    def get_advanced_ai_capabilities(self) -> Dict[str, Any]:
        """Get Priority 3 advanced AI capabilities."""
        if not self._initialized:
            raise RuntimeError("System not initialized. Call initialize() first.")

        return self._advanced_ai_integration.get_system_status()

    def reason_semantically(
        self, query: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Perform semantic reasoning using Priority 3 capabilities."""
        if not self._initialized:
            raise RuntimeError("System not initialized. Call initialize() first.")

        return self._advanced_ai_integration.reason_semantically(query, context)

    def run_automl(
        self, model_type: str, data: Optional[Dict[str, Any]] = None, optimization_budget: int = 10
    ) -> Dict[str, Any]:
        """Run automated machine learning using Priority 3 capabilities."""
        if not self._initialized:
            raise RuntimeError("System not initialized. Call initialize() first.")

        return self._advanced_ai_integration.run_automl(model_type, data, optimization_budget)

    def analyze_knowledge_graph(
        self, centrality_type: str = "PAGE_RANK", detect_patterns: bool = True
    ) -> Dict[str, Any]:
        """Analyze knowledge graph using Priority 3 capabilities."""
        if not self._initialized:
            raise RuntimeError("System not initialized. Call initialize() first.")

        return self._advanced_ai_integration.analyze_knowledge_graph(
            centrality_type, detect_patterns
        )

    def orchestrate_task(
        self,
        task_type: str,
        task_description: str,
        priority: int = 5,
        required_capabilities: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Orchestrate task using multi-agent system from Priority 3."""
        if not self._initialized:
            raise RuntimeError("System not initialized. Call initialize() first.")

        return self._advanced_ai_integration.orchestrate_task(
            task_type, task_description, priority, required_capabilities
        )

    def process_cross_modal(
        self, modality_data: Dict[str, Any], operation: str = "fusion"
    ) -> Dict[str, Any]:
        """Process cross-modal data using Priority 3 capabilities."""
        if not self._initialized:
            raise RuntimeError("System not initialized. Call initialize() first.")

        return self._advanced_ai_integration.process_cross_modal(modality_data, operation)

    # Complete System Integration Methods (Quick Wins, Priority 1, 2, 3)

    def get_complete_system_status(self) -> Dict[str, Any]:
        """Get comprehensive status of all enhancement components."""
        if not self._initialized:
            raise RuntimeError("System not initialized. Call initialize() first.")

        return self._complete_system_integration.get_complete_system_status()

    # Quick Wins Capabilities
    def create_checkpoint(self, component_id: str, state_data: Dict[str, Any]) -> str:
        """Create checkpoint using Quick Wins capability."""
        if not self._initialized:
            raise RuntimeError("System not initialized. Call initialize() first.")
        return self._complete_system_integration.create_checkpoint(component_id, state_data)

    def restore_checkpoint(self, checkpoint_id: str) -> Optional[Dict[str, Any]]:
        """Restore checkpoint using Quick Wins capability."""
        if not self._initialized:
            raise RuntimeError("System not initialized. Call initialize() first.")
        return self._complete_system_integration.restore_checkpoint(checkpoint_id)

    def execute_with_circuit_breaker(self, circuit_id: str, operation: callable, **kwargs) -> Any:
        """Execute operation with circuit breaker protection."""
        if not self._initialized:
            raise RuntimeError("System not initialized. Call initialize() first.")
        return self._complete_system_integration.execute_with_circuit_breaker(
            circuit_id, operation, **kwargs
        )

    def execute_with_retry(
        self, operation: callable, retry_policy: str = "EXPONENTIAL", **kwargs
    ) -> Any:
        """Execute operation with adaptive retry."""
        if not self._initialized:
            raise RuntimeError("System not initialized. Call initialize() first.")
        return self._complete_system_integration.execute_with_retry(
            operation, retry_policy, **kwargs
        )

    def get_system_health(self) -> Dict[str, Any]:
        """Get system health status."""
        if not self._initialized:
            raise RuntimeError("System not initialized. Call initialize() first.")
        return self._complete_system_integration.get_system_health()

    # Priority 1 Capabilities
    def execute_with_resilience(self, service_name: str, operation: callable, **kwargs) -> Any:
        """Execute operation with distributed resilience."""
        if not self._initialized:
            raise RuntimeError("System not initialized. Call initialize() first.")
        return self._complete_system_integration.execute_with_resilience(
            service_name, operation, **kwargs
        )

    def recover_state(self, component_id: str) -> Optional[Dict[str, Any]]:
        """Recover state for a component."""
        if not self._initialized:
            raise RuntimeError("System not initialized. Call initialize() first.")
        return self._complete_system_integration.recover_state(component_id)

    def propose_code_modification(
        self, code_context: Dict[str, Any], objective: str
    ) -> Dict[str, Any]:
        """Propose intelligent code modification."""
        if not self._initialized:
            raise RuntimeError("System not initialized. Call initialize() first.")
        return self._complete_system_integration.propose_code_modification(code_context, objective)

    def detect_and_heal_anomalies(self, system_metrics: Dict[str, float]) -> Dict[str, Any]:
        """Detect and heal system anomalies."""
        if not self._initialized:
            raise RuntimeError("System not initialized. Call initialize() first.")
        return self._complete_system_integration.detect_and_heal_anomalies(system_metrics)

    # Priority 2 Capabilities
    def forecast_evolution(self, system_trends: Dict[str, List[float]]) -> Dict[str, Any]:
        """Forecast system evolution."""
        if not self._initialized:
            raise RuntimeError("System not initialized. Call initialize() first.")
        return self._complete_system_integration.forecast_evolution(system_trends)

    def optimize_resources(self, workload_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize system resources."""
        if not self._initialized:
            raise RuntimeError("System not initialized. Call initialize() first.")
        return self._complete_system_integration.optimize_resources(workload_metrics)

    def select_execution_strategy(self, conditions: Dict[str, Any]) -> Dict[str, Any]:
        """Select optimal execution strategy."""
        if not self._initialized:
            raise RuntimeError("System not initialized. Call initialize() first.")
        return self._complete_system_integration.select_execution_strategy(conditions)

    def balance_load(self, traffic_data: Dict[str, Any]) -> Dict[str, Any]:
        """Balance load using intelligent algorithms."""
        if not self._initialized:
            raise RuntimeError("System not initialized. Call initialize() first.")
        return self._complete_system_integration.balance_load(traffic_data)

    def check_governance(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Check governance constraints."""
        if not self._initialized:
            raise RuntimeError("System not initialized. Call initialize() first.")
        return self._complete_system_integration.check_governance(action)

    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""
        if not self._initialized:
            return {
                "initialized": False,
                "status": "NOT_INITIALIZED",
            }

        # Get Cognitive OS metrics
        cognitive_metrics = self._cognitive_os.get_system_metrics()
        component_status = self._cognitive_os.get_component_status()

        # Get neuromorphic statistics
        indira_stats = self._indira_brain_enhanced.get_neuromorphic_statistics()
        dyon_stats = self._dyon_brain_enhanced.get_neuromorphic_statistics()

        # Get Priority 3 advanced AI status
        advanced_ai_status = self._advanced_ai_integration.get_system_status()

        # Get complete system integration status
        complete_system_status = self._complete_system_integration.get_complete_system_status()

        # Get configuration
        config = self._config_manager.get_config()

        return {
            "initialized": True,
            "status": "OPERATIONAL",
            "system_id": config.system_id,
            "environment": config.environment,
            "cognitive_os": {
                "health_score": cognitive_metrics.health_score,
                "performance_score": cognitive_metrics.performance_score,
                "status": cognitive_metrics.status,
                "active_layers": cognitive_metrics.active_layers,
                "components": dict(component_status),
            },
            "neuromorphic": {
                "indira": indira_stats,
                "dyon": dyon_stats,
            },
            "priority3_advanced_ai": advanced_ai_status,
            "complete_system_integration": complete_system_status,
            "performance": {
                "total_requests": self._total_requests,
                "successful_requests": self._successful_requests,
                "success_rate": (
                    self._successful_requests / self._total_requests
                    if self._total_requests > 0
                    else 1.0
                ),
                "uptime_seconds": (
                    (datetime.utcnow() - self._start_time).total_seconds()
                    if self._start_time
                    else 0
                ),
            },
            "configuration": {
                "neuromorphic_enabled": config.neuromorphic.indira_snn_enabled,
                "phase3_enabled": config.phase3.rl_enabled,
                "phase4_enabled": config.phase4.neuro_symbolic_enabled,
                "priority3_enabled": True,
                "quick_wins_enabled": True,
                "priority1_enabled": True,
                "priority2_enabled": True,
            },
        }

    def shutdown(self) -> None:
        """Shutdown the unified system gracefully."""
        with self._lock:
            if not self._initialized:
                return

            logger.info("[DIX_VISION_UNIFIED] Shutting down DIX VISION system...")

            try:
                # Shutdown enhanced brains
                if self._indira_brain_enhanced:
                    self._indira_brain_enhanced.shutdown()
                if self._dyon_brain_enhanced:
                    self._dyon_brain_enhanced.shutdown()

                logger.info("[DIX_VISION_UNIFIED] System shutdown complete")

            except Exception as e:
                logger.error(f"[DIX_VISION_UNIFIED] Shutdown error: {e}")
            finally:
                self._initialized = False


# Singleton instance
_unified_system: Optional[UnifiedDIXVISIONSystem] = None
_unified_system_lock = threading.Lock()


def get_unified_system() -> UnifiedDIXVISIONSystem:
    """Get the singleton unified DIX VISION system instance."""
    global _unified_system
    if _unified_system is None:
        with _unified_system_lock:
            if _unified_system is None:
                _unified_system = UnifiedDIXVISIONSystem()
    return _unified_system


def initialize_dix_vision() -> bool:
    """Initialize the complete DIX VISION system (convenience function)."""
    system = get_unified_system()
    return system.initialize()


__all__ = [
    "UnifiedDIXVISIONSystem",
    "get_unified_system",
    "initialize_dix_vision",
]
