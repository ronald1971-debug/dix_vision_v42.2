"""
DIX VISION v42.2 — Unified System Entry Point

This is the main entry point that wires together all phases and modules
into a cohesive, production-ready system with full integration of:
- Phase 1: Knowledge Layer
- Phase 2: Governance System
- Phase 3: Advanced Cognitive Modules (RL, XAI, Multi-Agent, Temporal, Risk)
- Phase 4: Advanced AI (Neuro-Symbolic, Meta-Cognitive, Causal)
- Phase 5: Neuromorphic Computing (INDIRA & DYON SNN + LSM)
- Execution System
- Configuration Management

This provides the true "all phases integrated and wired" experience.
"""

from __future__ import annotations

import logging
import threading
from typing import Any, Dict, Optional
from datetime import datetime

# Cognitive OS
from cognitive_os.core import (
    CognitiveOSKernel,
    get_cognitive_os_kernel,
    SystemStatus,
)

# Configuration
from cognitive_os.config import get_config_manager, SystemConfig

# Enhanced Brains with Neuromorphic Integration
from indira_cognitive.indira_brain.concrete_enhanced import get_indira_brain_enhanced
from dyon_cognitive.dyon_brain.concrete_enhanced import get_dyon_brain_enhanced

# Execution System
from execution_unified import get_unified_execution_kernel

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
                logger.info(f"[DIX_VISION_UNIFIED] Configuration loaded for environment: {config.environment}")
                
                # 2. Initialize Cognitive OS (all phases integrated in kernel)
                self._cognitive_os = get_cognitive_os_kernel()
                self._cognitive_os.initialize_system()
                logger.info("[DIX_VISION_UNIFIED] Cognitive OS initialized with all phases")
                
                # 3. Initialize Enhanced Brains with Neuromorphic Integration
                self._indira_brain_enhanced = get_indira_brain_enhanced()
                self._dyon_brain_enhanced = get_dyon_brain_enhanced()
                
                # Apply neuromorphic configuration
                neuromorphic_config = self._config_manager.get_neuromorphic_config()
                self._indira_brain_enhanced._enable_neuromorphic = neuromorphic_config.indira_snn_enabled
                self._indira_brain_enhanced._neuromorphic_confidence_weight = neuromorphic_config.indira_snn_confidence_weight
                self._dyon_brain_enhanced._enable_neuromorphic = neuromorphic_config.dyon_snn_enabled
                
                logger.info("[DIX_VISION_UNIFIED] Enhanced brains initialized with neuromorphic components")
                
                # 4. Initialize Execution Kernel
                self._execution_kernel = get_unified_execution_kernel()
                logger.info("[DIX_VISION_UNIFIED] Execution kernel initialized")
                
                # 5. Mark system as initialized
                self._initialized = True
                self._start_time = datetime.utcnow()
                
                logger.info("[DIX_VISION_UNIFIED] Complete DIX VISION v42.2 system initialization SUCCESS")
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
            decision = self._indira_brain_enhanced.execute_fast_trading_decision(market_state, asset)
            
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
                    "neuromorphic_latency_ms": decision.metadata.get("neuromorphic_latency_ms", 0.0),
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
    
    def analyze_system_with_neuromorphic(self, system_metrics: Dict[str, float], target: str = "system") -> Dict[str, Any]:
        """Analyze system with full neuromorphic integration."""
        if not self._initialized:
            raise RuntimeError("System not initialized. Call initialize() first.")
        
        try:
            # Use enhanced DYON brain with neuromorphic integration
            analysis = self._dyon_brain_enhanced.analyze_system_with_neuromorphic(system_metrics, target)
            
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
                    "neuromorphic_anomaly_score": analysis.code_metrics.get("neuromorphic_anomaly_score", 0.0),
                },
                "timestamp": analysis.metadata.get("timestamp", datetime.utcnow().isoformat()),
            }
            
        except Exception as e:
            logger.error(f"[DIX_VISION_UNIFIED] System analysis failed: {e}")
            return {
                "success": False,
                "error": str(e),
            }
    
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
            "performance": {
                "total_requests": self._total_requests,
                "successful_requests": self._successful_requests,
                "success_rate": self._successful_requests / self._total_requests if self._total_requests > 0 else 1.0,
                "uptime_seconds": (datetime.utcnow() - self._start_time).total_seconds() if self._start_time else 0,
            },
            "configuration": {
                "neuromorphic_enabled": config.neuromorphic.indira_snn_enabled,
                "phase3_enabled": config.phase3.rl_enabled,
                "phase4_enabled": config.phase4.neuro_symbolic_enabled,
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