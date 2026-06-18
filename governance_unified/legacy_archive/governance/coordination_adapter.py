"""
coordination_adapter.py
DIX VISION v42.2 — Coordination Layer Integration Adapter

Integrates the new coordination layer components with existing governance while:
- Maintaining <10ms ACL message performance
- Bridging existing mode manager with new operating modes
- Integrating cognitive economy with system resource management
- Providing backward compatibility with existing governance
- Supporting agent communication and conflict resolution
"""

from __future__ import annotations

import logging
import threading
import time
from typing import Any, Optional, Dict, List
from datetime import datetime
from dataclasses import dataclass

from governance_unified.mode_manager import get_mode_manager, ModeManager, OperationalMode
from preservation_layer import get_preservation_layer

logger = logging.getLogger(__name__)


@dataclass
class CoordinationConfig:
    """Configuration for coordination layer integration."""
    use_new_coordination: bool = True
    fallback_on_failure: bool = True
    latency_threshold_ms: float = 10.0
    enable_cognitive_economy: bool = True
    enable_advanced_modes: bool = True
    enable_acl_protocol: bool = True


class CoordinationAdapter:
    """
    Adapter between existing governance and new coordination layer.
    
    Features:
    - Bridge existing mode manager with new operating modes
    - Cognitive economy integration
    - ACL protocol for agent communication
    - <10ms ACL message performance
    - Automatic fallback to legacy governance
    - Performance monitoring and validation
    - Preservation layer integration
    """
    
    def __init__(self, config: Optional[CoordinationConfig] = None):
        self._config = config or CoordinationConfig()
        self._lock = threading.Lock()
        
        # Governance integration
        self._mode_manager = None
        self._new_operating_modes = None
        
        # Cognitive economy
        self._cognitive_economy_active = False
        self._resource_budgets: Dict[str, float] = {}
        
        # ACL messaging
        self._acl_message_count = 0
        self._acl_message_queue: List[Dict] = []
        
        # Performance tracking
        self._acl_latencies: List[float] = []
        self._mode_transition_count = 0
        
        # Health tracking
        self._new_coordination_healthy = True
        self._consecutive_failures = 0
        self._max_consecutive_failures = 3
        
        logger.info("[COORDINATION_ADAPTER] Coordination Adapter initialized")
    
    def initialize(self) -> bool:
        """Initialize the adapter with existing governance."""
        try:
            with self._lock:
                # Get existing mode manager
                self._mode_manager = get_mode_manager()
                
                # Try to initialize new coordination components
                if self._config.use_new_coordination:
                    try:
                        # Try to import and initialize new operating modes
                        from coordination_layer.operating_modes import get_operating_mode_manager
                        self._new_operating_modes = get_operating_mode_manager()
                        logger.info("[COORDINATION_ADAPTER] New operating modes initialized")
                    except Exception as e:
                        logger.warning(f"[COORDINATION_ADAPTER] Failed to initialize new operating modes: {e}")
                        self._new_operating_modes = None
                
                # Initialize cognitive economy if enabled
                if self._config.enable_cognitive_economy:
                    try:
                        from coordination_layer.cognitive_economy import get_cognitive_economy_manager
                        cognitive_economy = get_cognitive_economy_manager()
                        logger.info("[COORDINATION_ADAPTER] Cognitive economy initialized")
                        self._cognitive_economy_active = True
                    except Exception as e:
                        logger.warning(f"[COORDINATION_ADAPTER] Failed to initialize cognitive economy: {e}")
                
                return True
                
        except Exception as e:
            logger.error(f"[COORDINATION_ADAPTER] Initialization failed: {e}")
            return False
    
    def request_mode_transition(
        self,
        new_mode: str,
        reason: str = "",
        initiator: str = "system"
    ) -> Dict[str, Any]:
        """
        Request a mode transition using new coordination layer if available,
        otherwise fallback to existing mode manager.
        
        Returns dict with transition result.
        """
        start_time_ms = time.time() * 1000
        self._mode_transition_count += 1
        
        try:
            # Try new operating modes if available
            if self._config.use_new_coordination and self._new_operating_modes and self._new_coordination_healthy:
                result = self._try_new_mode_transition(new_mode, reason, initiator)
                if result and result.get("success"):
                    end_time_ms = time.time() * 1000
                    latency_ms = end_time_ms - start_time_ms
                    result["latency_ms"] = latency_ms
                    return result
            
            # Fallback to existing mode manager
            return self._fallback_mode_transition(new_mode, reason, initiator, start_time_ms)
            
        except Exception as e:
            logger.error(f"[COORDINATION_ADAPTER] Mode transition failed: {e}")
            return self._fallback_mode_transition(new_mode, reason, initiator, start_time_ms)
    
    def _try_new_mode_transition(self, new_mode: str, reason: str, initiator: str) -> Optional[Dict]:
        """Try to use new operating modes for transition."""
        try:
            # Map string mode to enum if possible
            from coordination_layer.operating_modes import OperatingMode
            
            try:
                mode_enum = OperatingMode[new_mode.upper()]
            except KeyError:
                # Mode not recognized, fallback
                return None
            
            # Try to transition using new operating modes
            if self._new_operating_modes and hasattr(self._new_operating_modes, 'request_mode_transition'):
                result = self._new_operating_modes.request_mode_transition(
                    target_mode=mode_enum,
                    reason=reason or "adapter_requested",
                    initiator=initiator
                )
                
                if result:
                    self._consecutive_failures = 0
                    return {
                        "success": True,
                        "from_mode": result.get("from_mode", "UNKNOWN"),
                        "to_mode": result.get("to_mode", new_mode),
                        "reason": result.get("reason", reason),
                        "initiator": initiator,
                        "integration_mode": "new_coordination"
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"[COORDINATION_ADAPTER] New mode transition failed: {e}")
            self._consecutive_failures += 1
            
            if self._consecutive_failures >= self._max_consecutive_failures:
                self._new_coordination_healthy = False
                logger.warning(f"[COORDINATION_ADAPTER] New coordination disabled after failures")
            
            return None
    
    def _fallback_mode_transition(self, new_mode: str, reason: str, initiator: str, start_time_ms: float) -> Dict:
        """Fallback to existing mode manager."""
        try:
            # Map new operating modes to existing FSM modes
            from core.contracts.governance import SystemMode
            
            mode_mapping = {
                "OFFLINE": SystemMode.SAFE,
                "PASSIVE": SystemMode.SAFE,
                "OBSERVATION": SystemMode.PAPER,
                "SHADOW": SystemMode.PAPER,
                "ACTIVE": SystemMode.AUTO,
                "AGGRESSIVE": SystemMode.AUTO,
                "EMERGENCY": SystemMode.LOCKED,
                "MAINTENANCE": SystemMode.SAFE,
                "DEVELOPMENT": SystemMode.PAPER,
            }
            
            target_mode = mode_mapping.get(new_mode.upper(), SystemMode.SAFE)
            
            # Use existing mode manager
            success = self._mode_manager.transition(
                target_mode,
                operational=None,
                reason=reason or f"coordination_adapter_fallback: {new_mode}"
            )
            
            end_time_ms = time.time() * 1000
            latency_ms = end_time_ms - start_time_ms
            
            return {
                "success": success,
                "from_mode": str(self._mode_manager.current_fsm_mode()),
                "to_mode": target_mode.name,
                "reason": reason,
                "initiator": initiator,
                "latency_ms": latency_ms,
                "integration_mode": "fallback"
            }
            
        except Exception as e:
            logger.error(f"[COORDINATION_ADAPTER] Fallback mode transition failed: {e}")
            end_time_ms = time.time() * 1000
            latency_ms = end_time_ms - start_time_ms
            
            return {
                "success": False,
                "from_mode": "UNKNOWN",
                "to_mode": new_mode,
                "reason": reason,
                "initiator": initiator,
                "latency_ms": latency_ms,
                "integration_mode": "ultimate_fallback"
            }
    
    def send_acl_message(
        self,
        sender: str,
        receiver: str,
        message_type: str,
        content: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Send ACL message between agents with <10ms performance target.
        """
        start_time_ms = time.time() * 1000
        self._acl_message_count += 1
        
        try:
            # Create ACL message structure
            acl_message = {
                "message_id": f"acl_{int(time.time() * 1000)}_{self._acl_message_count}",
                "sender": sender,
                "receiver": receiver,
                "message_type": message_type,
                "content": content,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Queue the message
            self._acl_message_queue.append(acl_message)
            
            end_time_ms = time.time() * 1000
            latency_ms = end_time_ms - start_time_ms
            self._acl_latencies.append(latency_ms)
            
            # Check if latency exceeded threshold
            if latency_ms > self._config.latency_threshold_ms:
                logger.warning(
                    f"[COORDINATION_ADAPTER] ACL message latency exceeded threshold: {latency_ms:.2f}ms > {self._config.latency_threshold_ms}ms"
                )
            
            return {
                "success": True,
                "message_id": acl_message["message_id"],
                "latency_ms": latency_ms,
                "integration_mode": "coordination_adapter"
            }
            
        except Exception as e:
            logger.error(f"[COORDINATION_ADAPTER] ACL message failed: {e}")
            end_time_ms = time.time() * 1000
            latency_ms = end_time_ms - start_time_ms
            
            return {
                "success": False,
                "message_id": "failed",
                "latency_ms": latency_ms,
                "integration_mode": "coordination_adapter_error"
            }
    
    def check_cognitive_budget(self, operation_type: str, resource_estimate: float) -> Dict[str, Any]:
        """
        Check if cognitive budget allows operation using new cognitive economy if available.
        """
        try:
            if self._config.enable_cognitive_economy and self._cognitive_economy_active:
                try:
                    from coordination_layer.cognitive_economy import get_cognitive_economy_manager
                    cognitive_economy = get_cognitive_economy_manager()
                    
                    if hasattr(cognitive_economy, 'check_budget'):
                        result = cognitive_economy.check_budget(
                            operation_type=operation_type,
                            resource_estimate=resource_estimate
                        )
                        
                        if result:
                            return {
                                "allowed": result.get("allowed", True),
                                "remaining_budget": result.get("remaining_budget", 0.0),
                                "cost_estimate": result.get("cost_estimate", 0.0),
                                "integration_mode": "new_cognitive_economy"
                            }
                except Exception as e:
                    logger.warning(f"[COORDINATION_ADAPTER] Cognitive economy check failed: {e}")
            
            # Fallback: simple budget check
            default_budget = 100.0
            allocated = self._resource_budgets.get(operation_type, 0.0)
            remaining = default_budget - allocated
            
            return {
                "allowed": remaining >= resource_estimate,
                "remaining_budget": remaining,
                "cost_estimate": resource_estimate,
                "integration_mode": "fallback"
            }
            
        except Exception as e:
            logger.error(f"[COORDINATION_ADAPTER] Budget check failed: {e}")
            return {
                "allowed": False,
                "remaining_budget": 0.0,
                "cost_estimate": resource_estimate,
                "integration_mode": "error"
            }
    
    def get_current_mode(self) -> Dict[str, Any]:
        """Get current operating mode, bridging new and old systems."""
        try:
            # Try new operating modes first
            if self._new_operating_modes and hasattr(self._new_operating_modes, 'get_current_mode'):
                new_mode = self._new_operating_modes.get_current_mode()
                if new_mode:
                    return {
                        "mode": new_mode.get("mode", "UNKNOWN"),
                        "mode_system": "new_coordination",
                        "capabilities": new_mode.get("capabilities", {})
                    }
            
            # Fallback to existing mode manager
            current_fsm = self._mode_manager.current_fsm_mode()
            current_operational = self._mode_manager.current_operational_mode()
            
            return {
                "mode": f"{current_fsm.name}_{current_operational.name}",
                "mode_system": "legacy_governance",
                "fsm_mode": current_fsm.name,
                "operational_mode": current_operational.name
            }
            
        except Exception as e:
            logger.error(f"[COORDINATION_ADAPTER] Get current mode failed: {e}")
            return {
                "mode": "UNKNOWN",
                "mode_system": "error",
                "error": str(e)
            }
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for coordination."""
        avg_acl_latency = sum(self._acl_latencies) / len(self._acl_latencies) if self._acl_latencies else 0.0
        
        return {
            "acl_message_count": self._acl_message_count,
            "mode_transition_count": self._mode_transition_count,
            "average_acl_latency_ms": avg_acl_latency,
            "max_acl_latency_ms": max(self._acl_latencies) if self._acl_latencies else 0.0,
            "acl_queue_size": len(self._acl_message_queue),
            "new_coordination_healthy": self._new_coordination_healthy,
            "cognitive_economy_active": self._cognitive_economy_active
        }
    
    def enable_new_coordination(self) -> None:
        """Enable new coordination components."""
        with self._lock:
            self._config.use_new_coordination = True
            self._new_coordination_healthy = True
            self._consecutive_failures = 0
            logger.info("[COORDINATION_ADAPTER] New coordination enabled")
    
    def disable_new_coordination(self) -> None:
        """Disable new coordination and use legacy only."""
        with self._lock:
            self._config.use_new_coordination = False
            logger.info("[COORDINATION_ADAPTER] New coordination disabled")


# Global coordination adapter instance
_coordination_adapter: Optional[CoordinationAdapter] = None
_adapter_lock = threading.Lock()


def get_coordination_adapter() -> CoordinationAdapter:
    """Get the global coordination adapter (thread-safe singleton)."""
    global _coordination_adapter
    with _adapter_lock:
        if _coordination_adapter is None:
            _coordination_adapter = CoordinationAdapter()
            _coordination_adapter.initialize()
    return _coordination_adapter
