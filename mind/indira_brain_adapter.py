"""
indira_brain_adapter.py
DIX VISION v42.2 — INDIRA Brain Integration Adapter

Integrates the new ConcreteINDIRABrain with the existing IndiraEngine while:
- Maintaining sub-5ms decision latency
- Providing preservation layer fallback
- Enabling gradual migration from legacy to new brain
- Supporting both legacy and new cognitive architectures
"""

from __future__ import annotations

import logging
import threading
import time
from typing import Any, Callable, Optional
from datetime import datetime
from dataclasses import dataclass

from preservation_layer import get_preservation_layer
from system.time_source import monotonic_ns as _monotonic_ns

logger = logging.getLogger(__name__)


@dataclass
class BrainIntegrationConfig:
    """Configuration for INDIRA brain integration."""
    use_new_brain: bool = True
    fallback_on_failure: bool = True
    latency_threshold_ms: float = 5.0
    enable_cache: bool = True
    cache_ttl_ms: float = 1000.0
    enable_neuro_symbolic: bool = True
    enable_memory_integration: bool = True


class IndiraBrainAdapter:
    """
    Adapter between existing IndiraEngine and new ConcreteINDIRABrain.
    
    Features:
    - Sub-5ms decision path preservation
    - Automatic fallback to legacy on failure
    - Performance monitoring and validation
    - Preservation layer integration
    - Gradual migration support
    """
    
    def __init__(self, config: Optional[BrainIntegrationConfig] = None):
        self._config = config or BrainIntegrationConfig()
        self._lock = threading.Lock()
        
        # Brain instances
        self._new_brain = None
        self._legacy_intelligence_engine = None
        self._preservation_layer = None
        
        # Performance tracking
        self._decision_count = 0
        self._new_brain_count = 0
        self._fallback_count = 0
        self._latency_sum_ms = 0.0
        self._latency_max_ms = 0.0
        
        # Cache for fast path optimization
        self._decision_cache = {}
        self._cache_timestamps = {}
        
        # Health tracking
        self._new_brain_healthy = True
        self._consecutive_failures = 0
        self._max_consecutive_failures = 3
        
        logger.info("[INDIRA_ADAPTER] INDIRA Brain Adapter initialized")
    
    def initialize(self) -> bool:
        """Initialize the adapter with new brain and preservation layer."""
        try:
            with self._lock:
                # Get preservation layer
                self._preservation_layer = get_preservation_layer()
                
                # Try to initialize new brain
                if self._config.use_new_brain:
                    try:
                        from indira_cognitive.indira_brain.concrete import ConcreteINDIRABrain
                        
                        # Try to instantiate, but handle abstract method errors gracefully
                        try:
                            self._new_brain = ConcreteINDIRABrain()
                            
                            # Connect to preservation layer
                            if self._preservation_layer:
                                self._new_brain.connect_to_preservation_layer(
                                    self._preservation_layer,
                                    self._legacy_intelligence_engine
                                )
                            
                            logger.info("[INDIRA_ADAPTER] New INDIRA brain initialized")
                        except TypeError as te:
                            # Handle abstract method errors
                            if "abstract" in str(te):
                                logger.warning(f"[INDIRA_ADAPTER] New brain has unimplemented abstract methods: {te}")
                                logger.info("[INDIRA_ADAPTER] Using EnhancedINDIRABrain as fallback")
                                
                                # Try EnhancedINDIRABrain which might have complete implementation
                                try:
                                    from indira_cognitive.indira_brain import EnhancedINDIRABrain
                                    self._new_brain = EnhancedINDIRABrain()
                                    
                                    if self._preservation_layer:
                                        self._new_brain.connect_to_preservation_layer(
                                            self._preservation_layer,
                                            self._legacy_intelligence_engine
                                        )
                                    
                                    logger.info("[INDIRA_ADAPTER] Enhanced INDIRA brain initialized")
                                except Exception as e2:
                                    logger.warning(f"[INDIRA_ADAPTER] Enhanced brain also failed: {e2}")
                                    self._new_brain = None
                                    self._new_brain_healthy = False
                            else:
                                raise
                        
                    except Exception as e:
                        logger.warning(f"[INDIRA_ADAPTER] Failed to initialize new brain: {e}")
                        self._new_brain = None
                        self._new_brain_healthy = False
                
                # Try to get legacy intelligence engine for fallback
                try:
                    from cognitive_engine.cognitive_orchestrator import CognitiveOrchestrator
                    self._legacy_intelligence_engine = CognitiveOrchestrator()
                    logger.info("[INDIRA_ADAPTER] Legacy intelligence engine available for fallback")
                except Exception as e:
                    logger.warning(f"[INDIRA_ADAPTER] Legacy intelligence engine not available: {e}")
                    self._legacy_intelligence_engine = None
                
                return True
                
        except Exception as e:
            logger.error(f"[INDIRA_ADAPTER] Initialization failed: {e}")
            return False
    
    def process_trading_decision(
        self,
        market_data: dict[str, Any],
        asset: str,
        risk_constraints: Any,
        portfolio_usd: float
    ) -> dict[str, Any]:
        """
        Process trading decision using new brain with fallback.
        
        Returns a dict compatible with existing IndiraEngine format:
        {
            "decision_type": "BUY" | "SELL" | "HOLD" | "DELEGATE",
            "side": "BUY" | "SELL" | "NONE",
            "size_usd": float,
            "confidence": float,
            "latency_ms": float,
            "source": "new_brain" | "legacy" | "fallback",
            "reasoning": list,
        }
        """
        start_ns = _monotonic_ns()
        self._decision_count += 1
        
        try:
            # Try new brain first
            if self._config.use_new_brain and self._new_brain and self._new_brain_healthy:
                result = self._try_new_brain(market_data, asset, risk_constraints, portfolio_usd)
                if result:
                    end_ns = _monotonic_ns()
                    latency_ms = (end_ns - start_ns) / 1_000_000
                    
                    self._new_brain_count += 1
                    self._latency_sum_ms += latency_ms
                    self._latency_max_ms = max(self._latency_max_ms, latency_ms)
                    
                    # Check if latency exceeded threshold
                    if latency_ms > self._config.latency_threshold_ms:
                        logger.warning(
                            f"[INDIRA_ADAPTER] Latency exceeded threshold: {latency_ms:.2f}ms > {self._config.latency_threshold_ms}ms"
                        )
                    
                    return result
            
            # Fallback to legacy or simple logic
            return self._fallback_decision(market_data, asset, risk_constraints, portfolio_usd)
            
        except Exception as e:
            logger.error(f"[INDIRA_ADAPTER] Decision processing failed: {e}")
            # Fallback to simple decision on error
            return self._fallback_decision(market_data, asset, risk_constraints, portfolio_usd)
    
    def _try_new_brain(
        self,
        market_data: dict[str, Any],
        asset: str,
        risk_constraints: Any,
        portfolio_usd: float
    ) -> Optional[dict[str, Any]]:
        """Try to use new brain for decision."""
        try:
            # Check cache first for fast path
            cache_key = self._get_cache_key(market_data, asset)
            if self._config.enable_cache and cache_key in self._decision_cache:
                cache_time = self._cache_timestamps.get(cache_key, 0)
                if time.time() - cache_time < (self._config.cache_ttl_ms / 1000.0):
                    logger.debug(f"[INDIRA_ADAPTER] Cache hit for {asset}")
                    return self._decision_cache[cache_key]
            
            # Prepare market state for new brain
            market_state = {
                "signal": market_data.get("signal", 0.0),
                "volatility": market_data.get("volatility", 0.0),
                "regime": market_data.get("regime", "UNKNOWN"),
                "price": market_data.get("price", 0.0),
                "data_quality": market_data.get("data_quality", 1.0),
                "timestamp": datetime.utcnow()
            }
            
            # Execute fast trading decision
            decision = self._new_brain.execute_fast_trading_decision(market_state, asset)
            
            # Apply risk constraints from legacy system
            size_usd = decision.size_usd
            if risk_constraints:
                # Check if trade is allowed by risk constraints
                try:
                    ok, reason = risk_constraints.allows_trade(size_usd, portfolio_usd)
                    if not ok:
                        size_usd = 0.0  # Block trade
                        logger.info(f"[INDIRA_ADAPTER] Trade blocked by risk constraints: {reason}")
                except Exception as e:
                    logger.warning(f"[INDIRA_ADAPTER] Risk constraint check failed: {e}")
            
            # Convert to legacy-compatible format
            result = {
                "decision_type": decision.decision_type.value if hasattr(decision.decision_type, 'value') else str(decision.decision_type),
                "side": decision.side,
                "size_usd": size_usd,
                "confidence": decision.confidence,
                "latency_ms": decision.execution_latency_ms,
                "source": "new_brain",
                "reasoning": decision.reasoning_chain,
                "neural_reasoning": decision.neural_reasoning,
                "symbolic_reasoning": decision.symbolic_reasoning,
                "decision_id": decision.decision_id
            }
            
            # Map decision types to legacy format
            if result["decision_type"] not in ["BUY", "SELL", "HOLD"]:
                if result["side"] == "BUY":
                    result["decision_type"] = "BUY"
                elif result["side"] == "SELL":
                    result["decision_type"] = "SELL"
                else:
                    result["decision_type"] = "HOLD"
            
            # Cache the result
            if self._config.enable_cache:
                self._decision_cache[cache_key] = result
                self._cache_timestamps[cache_key] = time.time()
            
            # Reset failure counter on success
            self._consecutive_failures = 0
            self._new_brain_healthy = True
            
            return result
            
        except Exception as e:
            logger.error(f"[INDIRA_ADAPTER] New brain decision failed: {e}")
            self._consecutive_failures += 1
            
            # Disable new brain if too many consecutive failures
            if self._consecutive_failures >= self._max_consecutive_failures:
                self._new_brain_healthy = False
                logger.warning(f"[INDIRA_ADAPTER] New brain disabled after {self._consecutive_failures} failures")
            
            return None
    
    def _fallback_decision(
        self,
        market_data: dict[str, Any],
        asset: str,
        risk_constraints: Any,
        portfolio_usd: float
    ) -> dict[str, Any]:
        """Fallback decision using legacy logic or simple rules."""
        start_ns = _monotonic_ns()
        self._fallback_count += 1
        
        try:
            # Try legacy intelligence engine first
            if self._legacy_intelligence_engine and self._preservation_layer:
                try:
                    # Try to use legacy cognitive enrichment
                    cognitive_enrichment = self._legacy_intelligence_engine.enrich_market_data(market_data)
                    logger.debug("[INDIRA_ADAPTER] Using legacy cognitive enrichment")
                except Exception as e:
                    logger.warning(f"[INDIRA_ADAPTER] Legacy cognitive enrichment failed: {e}")
            
            # Simple fallback logic (mimics legacy IndiraEngine)
            signal = float(market_data.get("signal", 0.0))
            price = float(market_data.get("price", 0.0))
            data_quality = float(market_data.get("data_quality", 1.0))
            execution_quality = float(market_data.get("execution_confidence", 1.0))
            strategy = str(market_data.get("strategy", "default"))
            
            # Intent classification
            confidence = min(abs(signal), 0.95)
            
            # Decision logic
            if signal > 0.3 and confidence > 0.6:
                decision_type = "BUY"
                side = "BUY"
            elif signal < -0.3 and confidence > 0.6:
                decision_type = "SELL"
                side = "SELL"
            else:
                decision_type = "HOLD"
                side = "HOLD"
            
            # Calculate size
            size_usd = 0.0
            if decision_type in ["BUY", "SELL"] and risk_constraints:
                try:
                    max_size = min(
                        portfolio_usd * 0.1,  # 10% of portfolio
                        getattr(risk_constraints, 'max_order_size_usd', 10000.0)
                    )
                    size_usd = max_size * confidence
                except Exception:
                    size_usd = 10000.0 * confidence
            
            end_ns = _monotonic_ns()
            latency_ms = (end_ns - start_ns) / 1_000_000
            
            result = {
                "decision_type": decision_type,
                "side": side,
                "size_usd": size_usd,
                "confidence": confidence,
                "latency_ms": latency_ms,
                "source": "fallback",
                "reasoning": [
                    f"Signal: {signal:.3f}",
                    f"Confidence: {confidence:.2f}",
                    f"Data quality: {data_quality:.2f}",
                    "Execution quality: {execution_quality:.2f}"
                ]
            }
            
            return result
            
        except Exception as e:
            logger.error(f"[INDIRA_ADAPTER] Fallback decision failed: {e}")
            # Ultimate fallback
            return {
                "decision_type": "HOLD",
                "side": "HOLD",
                "size_usd": 0.0,
                "confidence": 0.0,
                "latency_ms": 0.0,
                "source": "ultimate_fallback",
                "reasoning": ["All decision paths failed, defaulting to HOLD"]
            }
    
    def _get_cache_key(self, market_data: dict[str, Any], asset: str) -> str:
        """Generate cache key for decision caching."""
        signal = market_data.get("signal", 0.0)
        volatility = market_data.get("volatility", 0.0)
        regime = market_data.get("regime", "UNKNOWN")
        return f"{asset}_{signal:.3f}_{volatility:.3f}_{regime}"
    
    def get_performance_metrics(self) -> dict[str, Any]:
        """Get performance metrics for the adapter."""
        avg_latency = (self._latency_sum_ms / self._new_brain_count) if self._new_brain_count > 0 else 0.0
        new_brain_ratio = (self._new_brain_count / self._decision_count) if self._decision_count > 0 else 0.0
        fallback_ratio = (self._fallback_count / self._decision_count) if self._decision_count > 0 else 0.0
        
        return {
            "total_decisions": self._decision_count,
            "new_brain_decisions": self._new_brain_count,
            "fallback_decisions": self._fallback_count,
            "new_brain_ratio": new_brain_ratio,
            "fallback_ratio": fallback_ratio,
            "average_latency_ms": avg_latency,
            "max_latency_ms": self._latency_max_ms,
            "new_brain_healthy": self._new_brain_healthy,
            "consecutive_failures": self._consecutive_failures,
            "cache_size": len(self._decision_cache)
        }
    
    def enable_new_brain(self) -> None:
        """Enable the new brain for decision making."""
        with self._lock:
            self._config.use_new_brain = True
            self._new_brain_healthy = True
            self._consecutive_failures = 0
            logger.info("[INDIRA_ADAPTER] New brain enabled")
    
    def disable_new_brain(self) -> None:
        """Disable the new brain and use fallback only."""
        with self._lock:
            self._config.use_new_brain = False
            logger.info("[INDIRA_ADAPTER] New brain disabled")
    
    def clear_cache(self) -> None:
        """Clear the decision cache."""
        with self._lock:
            self._decision_cache.clear()
            self._cache_timestamps.clear()
            logger.info("[INDIRA_ADAPTER] Decision cache cleared")


# Global adapter instance
_indira_brain_adapter: Optional[IndiraBrainAdapter] = None
_adapter_lock = threading.Lock()


def get_indira_brain_adapter() -> IndiraBrainAdapter:
    """Get the global INDIRA brain adapter (thread-safe singleton)."""
    global _indira_brain_adapter
    with _adapter_lock:
        if _indira_brain_adapter is None:
            _indira_brain_adapter = IndiraBrainAdapter()
            _indira_brain_adapter.initialize()
    return _indira_brain_adapter
