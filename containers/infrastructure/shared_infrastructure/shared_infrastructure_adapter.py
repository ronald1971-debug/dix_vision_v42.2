"""
shared_infrastructure_adapter.py
DIX VISION v42.2 — Shared Infrastructure Adapter

Integrates shared infrastructure components (planning engine, signal processing) 
with the existing system while maintaining backward compatibility and performance.
"""

from __future__ import annotations

import logging
import threading
import time
from typing import Any, Optional, Dict, List
from datetime import datetime
from dataclasses import dataclass

from preservation_layer import get_preservation_layer

logger = logging.getLogger(__name__)


@dataclass
class SharedInfrastructureConfig:
    """Configuration for shared infrastructure integration."""
    use_new_planning: bool = True
    use_new_signal_processing: bool = True
    fallback_on_failure: bool = True
    enable_component_sharing: bool = True
    enable_resource_monitoring: bool = True


class SharedInfrastructureAdapter:
    """
    Adapter for shared infrastructure components integration.
    
    Features:
    - Planning engine integration
    - Signal processing integration
    - Component sharing between agents
    - Resource monitoring
    - Performance tracking
    - Preservation layer integration
    """
    
    def __init__(self, config: Optional[SharedInfrastructureConfig] = None):
        self._config = config or SharedInfrastructureConfig()
        self._lock = threading.Lock()
        
        # Shared components
        self._planning_engine = None
        self._signal_processing = None
        self._memory_framework = None
        self._knowledge_graph = None
        
        # Component registry
        self._registered_components: Dict[str, Any] = {}
        
        # Performance tracking
        self._plan_count = 0
        self._signal_count = 0
        self._latencies: Dict[str, List[float]] = {"planning": [], "signal": []}
        
        # Health tracking
        self._planning_healthy = True
        self._signal_healthy = True
        
        logger.info("[SHARED_INFRA] Shared Infrastructure Adapter initialized")
    
    def initialize(self) -> bool:
        """Initialize shared infrastructure components."""
        try:
            with self._lock:
                # Try to initialize planning engine
                if self._config.use_new_planning:
                    try:
                        from shared_infrastructure.planning_engine import get_planning_engine
                        self._planning_engine = get_planning_engine()
                        logger.info("[SHARED_INFRA] Planning engine initialized")
                    except Exception as e:
                        logger.warning(f"[SHARED_INFRA] Failed to initialize planning engine: {e}")
                        self._planning_engine = None
                
                # Try to initialize signal processing
                if self._config.use_new_signal_processing:
                    try:
                        from shared_infrastructure.signal_processing import get_signal_processor
                        self._signal_processing = get_signal_processor()
                        logger.info("[SHARED_INFRA] Signal processing initialized")
                    except Exception as e:
                        logger.warning(f"[SHARED_INFRA] Failed to initialize signal processing: {e}")
                        self._signal_processing = None
                
                return True
                
        except Exception as e:
            logger.error(f"[SHARED_INFRA] Initialization failed: {e}")
            return False
    
    def create_plan(
        self,
        plan_type: str,
        goal: str,
        constraints: Optional[Dict] = None,
        requester: str = "system"
    ) -> Dict[str, Any]:
        """
        Create a plan using planning engine if available.
        
        Returns dict with plan details.
        """
        start_time_ms = time.time() * 1000
        self._plan_count += 1
        
        try:
            # Try planning engine
            if self._config.use_new_planning and self._planning_engine and self._planning_healthy:
                result = self._try_create_plan(plan_type, goal, constraints, requester)
                if result:
                    end_time_ms = time.time() * 1000
                    latency_ms = end_time_ms - start_time_ms
                    self._latencies["planning"].append(latency_ms)
                    result["latency_ms"] = latency_ms
                    return result
            
            # Fallback to simple plan creation
            return self._fallback_create_plan(plan_type, goal, constraints, requester, start_time_ms)
            
        except Exception as e:
            logger.error(f"[SHARED_INFRA] Plan creation failed: {e}")
            return self._fallback_create_plan(plan_type, goal, constraints, requester, start_time_ms)
    
    def _try_create_plan(
        self,
        plan_type: str,
        goal: str,
        constraints: Optional[Dict],
        requester: str
    ) -> Optional[Dict]:
        """Try to use planning engine."""
        try:
            if self._planning_engine and hasattr(self._planning_engine, 'create_plan'):
                result = self._planning_engine.create_plan(
                    plan_type=plan_type,
                    goal_description=goal,
                    constraints=constraints or {},
                    requester=requester
                )
                
                if result:
                    return {
                        "success": True,
                        "plan_id": getattr(result, 'plan_id', f"plan_{int(time.time() * 1000)}"),
                        "plan_type": plan_type,
                        "goal": goal,
                        "steps": getattr(result, 'steps', []),
                        "integration_mode": "new_planning_engine"
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"[SHARED_INFRA] Planning engine failed: {e}")
            self._planning_healthy = False
            return None
    
    def _fallback_create_plan(
        self,
        plan_type: str,
        goal: str,
        constraints: Optional[Dict],
        requester: str,
        start_time_ms: float
    ) -> Dict:
        """Fallback to simple plan creation."""
        end_time_ms = time.time() * 1000
        latency_ms = end_time_ms - start_time_ms
        
        # Simple fallback plan
        return {
            "success": True,
            "plan_id": f"fallback_plan_{int(time.time() * 1000)}",
            "plan_type": plan_type,
            "goal": goal,
            "steps": [
                f"Analyze: {goal}",
                "Execute plan for {plan_type}",
                "Validate results"
            ],
            "latency_ms": latency_ms,
            "integration_mode": "fallback"
        }
    
    def process_signals(
        self,
        signals: List[Dict[str, Any]],
        filters: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Process signals using signal processing engine if available.
        
        Returns dict with processed signals.
        """
        start_time_ms = time.time() * 1000
        self._signal_count += 1
        
        try:
            # Try signal processing
            if self._config.use_new_signal_processing and self._signal_processing and self._signal_healthy:
                result = self._try_process_signals(signals, filters)
                if result:
                    end_time_ms = time.time() * 1000
                    latency_ms = end_time_ms - start_time_ms
                    self._latencies["signal"].append(latency_ms)
                    result["latency_ms"] = latency_ms
                    return result
            
            # Fallback to simple signal processing
            return self._fallback_process_signals(signals, filters, start_time_ms)
            
        except Exception as e:
            logger.error(f"[SHARED_INFRA] Signal processing failed: {e}")
            return self._fallback_process_signals(signals, filters, start_time_ms)
    
    def _try_process_signals(
        self,
        signals: List[Dict[str, Any]],
        filters: Optional[Dict]
    ) -> Optional[Dict]:
        """Try to use signal processing engine."""
        try:
            if self._signal_processing and hasattr(self._signal_processing, 'process_signals'):
                result = self._signal_processing.process_signals(
                    signals=signals,
                    filters=filters or {}
                )
                
                if result:
                    return {
                        "success": True,
                        "processed_count": len(signals),
                        "filtered_count": getattr(result, 'filtered_count', 0),
                        "results": getattr(result, 'results', []),
                        "integration_mode": "new_signal_processing"
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"[SHARED_INFRA] Signal processing engine failed: {e}")
            self._signal_healthy = False
            return None
    
    def _fallback_process_signals(
        self,
        signals: List[Dict[str, Any]],
        filters: Optional[Dict],
        start_time_ms: float
    ) -> Dict:
        """Fallback to simple signal processing."""
        end_time_ms = time.time() * 1000
        latency_ms = end_time_ms - start_time_ms
        
        # Simple fallback signal processing
        processed_count = len(signals)
        filtered_count = 0
        
        if filters:
            # Apply simple filtering
            min_value = filters.get('min_threshold', 0.0)
            filtered_signals = [s for s in signals if s.get('value', 0.0) >= min_value]
            filtered_count = len(signals) - len(filtered_signals)
            processed_count = len(filtered_signals)
        
        return {
            "success": True,
            "processed_count": processed_count,
            "filtered_count": filtered_count,
            "results": signals,
            "latency_ms": latency_ms,
            "integration_mode": "fallback"
        }
    
    def register_component(self, component_name: str, component: Any) -> bool:
        """Register a component for shared access."""
        try:
            with self._lock:
                self._registered_components[component_name] = component
                logger.info(f"[SHARED_INFRA] Registered component: {component_name}")
                return True
        except Exception as e:
            logger.error(f"[SHARED_INFRA] Failed to register component {component_name}: {e}")
            return False
    
    def get_component(self, component_name: str) -> Optional[Any]:
        """Get a registered component."""
        return self._registered_components.get(component_name)
    
    def get_shared_memory(self, key: str) -> Optional[Any]:
        """Get value from shared memory (simple implementation)."""
        # Simple shared memory implementation using component registry
        memory_component = self.get_component("shared_memory")
        if memory_component and hasattr(memory_component, 'get'):
            return memory_component.get(key)
        return None
    
    def set_shared_memory(self, key: str, value: Any) -> bool:
        """Set value in shared memory (simple implementation)."""
        memory_component = self.get_component("shared_memory")
        if memory_component and hasattr(memory_component, 'set'):
            memory_component.set(key, value)
            return True
        
        # Create simple dict-based memory if not exists
        if not memory_component:
            self.register_component("shared_memory", {})
            memory_component = self.get_component("shared_memory")
            memory_component[key] = value
            return True
        
        return False
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for shared infrastructure."""
        avg_planning_latency = sum(self._latencies["planning"]) / len(self._latencies["planning"]) if self._latencies["planning"] else 0.0
        avg_signal_latency = sum(self._latencies["signal"]) / len(self._latencies["signal"]) if self._latencies["signal"] else 0.0
        
        return {
            "plan_count": self._plan_count,
            "signal_count": self._signal_count,
            "registered_components": len(self._registered_components),
            "average_planning_latency_ms": avg_planning_latency,
            "average_signal_latency_ms": avg_signal_latency,
            "planning_healthy": self._planning_healthy,
            "signal_healthy": self._signal_healthy
        }
    
    def enable_planning_engine(self) -> None:
        """Enable planning engine."""
        with self._lock:
            self._config.use_new_planning = True
            self._planning_healthy = True
            logger.info("[SHARED_INFRA] Planning engine enabled")
    
    def disable_planning_engine(self) -> None:
        """Disable planning engine."""
        with self._lock:
            self._config.use_new_planning = False
            logger.info("[SHARED_INFRA] Planning engine disabled")


# Global shared infrastructure adapter instance
_shared_infrastructure_adapter: Optional[SharedInfrastructureAdapter] = None
_adapter_lock = threading.Lock()


def get_shared_infrastructure_adapter() -> SharedInfrastructureAdapter:
    """Get the global shared infrastructure adapter (thread-safe singleton)."""
    global _shared_infrastructure_adapter
    with _adapter_lock:
        if _shared_infrastructure_adapter is None:
            _shared_infrastructure_adapter = SharedInfrastructureAdapter()
            _shared_infrastructure_adapter.initialize()
    return _shared_infrastructure_adapter
