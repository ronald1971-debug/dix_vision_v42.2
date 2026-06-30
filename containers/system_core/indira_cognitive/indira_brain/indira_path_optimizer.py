"""
DIX VISION INDIRA Brain Sub-5ms Path Optimization

Optimizes INDIRA's decision-making path to consistently achieve sub-5ms latency
through advanced caching, pre-computation, and path optimization techniques.
"""

from __future__ import annotations

import logging
import threading
import time
from collections import deque, defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
import hashlib
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class FastPathCacheEntry:
    """Cache entry for fast-path decisions."""
    cache_key: str
    decision: Dict[str, Any]
    confidence: float
    latency_ms: float
    hit_count: int
    last_accessed: float
    access_pattern: List[float] = field(default_factory=list)


@dataclass
class PreComputedDecision:
    """Pre-computed decision for common scenarios."""
    scenario_id: str
    scenario_pattern: Dict[str, Any]
    decision: Dict[str, Any]
    expected_confidence: float
    computation_cost: float
    usage_count: int
    last_used: float


@dataclass
class PathOptimizationMetrics:
    """Metrics for path optimization."""
    total_decisions: int
    fast_path_hits: int
    slow_path_usage: int
    cache_hit_rate: float
    average_latency_ms: float
    fast_path_latency_ms: float
    slow_path_latency_ms: float
    optimization_effectiveness: float


class INDIRAPathOptimizer:
    """
    Optimizes INDIRA's decision-making path for sub-5ms latency.
    
    Techniques:
    - Multi-level caching (L1, L2, L3)
    - Pattern-based pre-computation
    - Adaptive path selection
    - Latency-aware routing
    - Memory-efficient storage
    """
    
    def __init__(self):
        # Multi-level cache
        self._l1_cache: Dict[str, FastPathCacheEntry] = {}  # Hot path - 10ms LRU
        self._l2_cache: Dict[str, FastPathCacheEntry] = {}  # Warm path - 100ms LRU
        self._l3_cache: Dict[str, FastPathCacheEntry] = {}  # Cold path - 1s LRU
        
        # Pre-computed decisions
        self._pre_computed: Dict[str, PreComputedDecision] = {}
        
        # Path selection logic
        self._path_selection_thresholds = {
            "l1": 0.95,  # Use L1 if confidence >= 95%
            "l2": 0.85,  # Use L2 if confidence >= 85%
            "l3": 0.70,  # Use L3 if confidence >= 70%
        }
        
        # Metrics
        self._metrics = PathOptimizationMetrics(
            total_decisions=0,
            fast_path_hits=0,
            slow_path_usage=0,
            cache_hit_rate=0.0,
            average_latency_ms=0.0,
            fast_path_latency_ms=0.0,
            slow_path_latency_ms=0.0,
            optimization_effectiveness=0.0
        )
        
        # Access patterns for optimization
        self._access_patterns: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        
        # Latency tracking
        self._latency_history: deque = deque(maxlen=1000)
        
        self._lock = threading.Lock()
        
        logger.info("INDIRA Path Optimizer initialized")
    
    def generate_cache_key(self, market_state: Dict[str, Any]) -> str:
        """Generate a cache key from market state."""
        # Create a deterministic hash from key market features
        key_features = {
            "signal": market_state.get("signal", 0.0),
            "volatility": market_state.get("volatility", 0.0),
            "regime": market_state.get("regime", "UNKNOWN"),
            "trend": market_state.get("trend", "NEUTRAL"),
        }
        
        key_string = f"{key_features['signal']:.4f}_{key_features['volatility']:.4f}_{key_features['regime']}_{key_features['trend']}"
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def check_l1_cache(self, cache_key: str) -> Optional[FastPathCacheEntry]:
        """Check L1 cache (fastest)."""
        if cache_key in self._l1_cache:
            entry = self._l1_cache[cache_key]
            entry.hit_count += 1
            entry.last_accessed = time.time()
            entry.access_pattern.append(time.time())
            return entry
        return None
    
    def check_l2_cache(self, cache_key: str) -> Optional[FastPathCacheEntry]:
        """Check L2 cache (medium speed)."""
        if cache_key in self._l2_cache:
            entry = self._l2_cache[cache_key]
            entry.hit_count += 1
            entry.last_accessed = time.time()
            entry.access_pattern.append(time.time())
            
            # Promote to L1 if frequently accessed
            if entry.hit_count > 10:
                self._l1_cache[cache_key] = entry
                del self._l2_cache[cache_key]
            
            return entry
        return None
    
    def check_l3_cache(self, cache_key: str) -> Optional[FastPathCacheEntry]:
        """Check L3 cache (slowest)."""
        if cache_key in self._l3_cache:
            entry = self._l3_cache[cache_key]
            entry.hit_count += 1
            entry.last_accessed = time.time()
            entry.access_pattern.append(time.time())
            
            # Promote to L2 if frequently accessed
            if entry.hit_count > 5:
                self._l2_cache[cache_key] = entry
                del self._l3_cache[cache_key]
            
            return entry
        return None
    
    def store_in_cache(self, cache_key: str, decision: Dict[str, Any], 
                      confidence: float, latency_ms: float) -> None:
        """Store decision in appropriate cache level."""
        entry = FastPathCacheEntry(
            cache_key=cache_key,
            decision=decision,
            confidence=confidence,
            latency_ms=latency_ms,
            hit_count=1,
            last_accessed=time.time(),
            access_pattern=[time.time()]
        )
        
        with self._lock:
            # Store in L1 if high confidence
            if confidence >= self._path_selection_thresholds["l1"]:
                self._l1_cache[cache_key] = entry
            # Store in L2 if medium confidence
            elif confidence >= self._path_selection_thresholds["l2"]:
                self._l2_cache[cache_key] = entry
            # Store in L3 if lower confidence
            else:
                self._l3_cache[cache_key] = entry
    
    def pre_compute_decision(self, scenario_pattern: Dict[str, Any], 
                           decision: Dict[str, Any], confidence: float) -> str:
        """Pre-compute a decision for a common scenario."""
        scenario_id = hashlib.md5(str(scenario_pattern).encode()).hexdigest()
        
        pre_computed = PreComputedDecision(
            scenario_id=scenario_id,
            scenario_pattern=scenario_pattern,
            decision=decision,
            expected_confidence=confidence,
            computation_cost=0.0,  # Pre-computed, so effectively free
            usage_count=0,
            last_used=0.0
        )
        
        with self._lock:
            self._pre_computed[scenario_id] = pre_computed
        
        return scenario_id
    
    def check_pre_computed(self, market_state: Dict[str, Any]) -> Optional[PreComputedDecision]:
        """Check if we have a pre-computed decision for this scenario."""
        # Find matching pre-computed decision
        for scenario_id, pre_comp in self._pre_computed.items():
            if self._scenario_matches(market_state, pre_comp.scenario_pattern):
                pre_comp.usage_count += 1
                pre_comp.last_used = time.time()
                return pre_comp
        return None
    
    def _scenario_matches(self, market_state: Dict[str, Any], 
                         pattern: Dict[str, Any]) -> bool:
        """Check if market state matches a pre-computed pattern."""
        for key, value in pattern.items():
            if key not in market_state:
                return False
            if isinstance(value, float):
                if abs(market_state[key] - value) > 0.1:  # 10% tolerance
                    return False
            elif market_state[key] != value:
                return False
        return True
    
    def optimize_decision_path(self, market_state: Dict[str, Any], 
                             decision_fn) -> Tuple[Dict[str, Any], float]:
        """Optimize the decision path for sub-5ms latency."""
        start_time = time.time()
        
        # Step 1: Check pre-computed decisions (fastest path)
        pre_computed = self.check_pre_computed(market_state)
        if pre_computed:
            latency_ms = (time.time() - start_time) * 1000
            with self._lock:
                self._metrics.fast_path_hits += 1
                self._metrics.fast_path_latency_ms = (
                    (self._metrics.fast_path_latency_ms * (self._metrics.fast_path_hits - 1) + latency_ms) /
                    self._metrics.fast_path_hits
                )
            return pre_computed.decision, latency_ms
        
        # Step 2: Check L1 cache
        cache_key = self.generate_cache_key(market_state)
        l1_entry = self.check_l1_cache(cache_key)
        if l1_entry:
            latency_ms = (time.time() - start_time) * 1000
            with self._lock:
                self._metrics.fast_path_hits += 1
                self._metrics.fast_path_latency_ms = (
                    (self._metrics.fast_path_latency_ms * (self._metrics.fast_path_hits - 1) + latency_ms) /
                    self._metrics.fast_path_hits
                )
            return l1_entry.decision, latency_ms
        
        # Step 3: Check L2 cache
        l2_entry = self.check_l2_cache(cache_key)
        if l2_entry:
            latency_ms = (time.time() - start_time) * 1000
            with self._lock:
                self._metrics.fast_path_hits += 1
                self._metrics.fast_path_latency_ms = (
                    (self._metrics.fast_path_latency_ms * (self._metrics.fast_path_hits - 1) + latency_ms) /
                    self._metrics.fast_path_hits
                )
            return l2_entry.decision, latency_ms
        
        # Step 4: Check L3 cache
        l3_entry = self.check_l3_cache(cache_key)
        if l3_entry:
            latency_ms = (time.time() - start_time) * 1000
            with self._lock:
                self._metrics.fast_path_hits += 1
                self._metrics.fast_path_latency_ms = (
                    (self._metrics.fast_path_latency_ms * (self._metrics.fast_path_hits - 1) + latency_ms) /
                    self._metrics.fast_path_hits
                )
            return l3_entry.decision, latency_ms
        
        # Step 5: Slow path - compute decision
        decision, confidence = decision_fn(market_state)
        latency_ms = (time.time() - start_time) * 1000
        
        # Cache the result
        self.store_in_cache(cache_key, decision, confidence, latency_ms)
        
        with self._lock:
            self._metrics.slow_path_usage += 1
            self._metrics.slow_path_latency_ms = (
                (self._metrics.slow_path_latency_ms * (self._metrics.slow_path_usage - 1) + latency_ms) /
                self._metrics.slow_path_usage
            )
        
        return decision, latency_ms
    
    def cleanup_cache(self) -> None:
        """Clean up cache entries based on access patterns."""
        current_time = time.time()
        
        with self._lock:
            # Clean L1 cache (keep entries from last 10ms)
            self._l1_cache = {
                k: v for k, v in self._l1_cache.items()
                if current_time - v.last_accessed < 0.01
            }
            
            # Clean L2 cache (keep entries from last 100ms)
            self._l2_cache = {
                k: v for k, v in self._l2_cache.items()
                if current_time - v.last_accessed < 0.1
            }
            
            # Clean L3 cache (keep entries from last 1s)
            self._l3_cache = {
                k: v for k, v in self._l3_cache.items()
                if current_time - v.last_accessed < 1.0
            }
    
    def get_metrics(self) -> PathOptimizationMetrics:
        """Get path optimization metrics."""
        with self._lock:
            total = self._metrics.fast_path_hits + self._metrics.slow_path_usage
            self._metrics.cache_hit_rate = (
                self._metrics.fast_path_hits / total if total > 0 else 0.0
            )
            self._metrics.total_decisions = total
            
            # Calculate average latency
            if total > 0:
                self._metrics.average_latency_ms = (
                    (self._metrics.fast_path_latency_ms * self._metrics.fast_path_hits +
                     self._metrics.slow_path_latency_ms * self._metrics.slow_path_usage) / total
                )
            
            # Calculate optimization effectiveness
            if self._metrics.slow_path_latency_ms > 0:
                self._metrics.optimization_effectiveness = (
                    1.0 - (self._metrics.fast_path_latency_ms / self._metrics.slow_path_latency_ms)
                )
            
            return self._metrics
    
    def analyze_access_patterns(self) -> Dict[str, Any]:
        """Analyze access patterns for optimization insights."""
        pattern_analysis = {}
        
        with self._lock:
            for cache_key, entry in self._l1_cache.items():
                if len(entry.access_pattern) > 2:
                    intervals = [
                        entry.access_pattern[i] - entry.access_pattern[i-1]
                        for i in range(1, len(entry.access_pattern))
                    ]
                    pattern_analysis[cache_key] = {
                        "avg_interval": np.mean(intervals),
                        "std_interval": np.std(intervals),
                        "trend": "increasing" if intervals[-1] > intervals[0] else "decreasing"
                    }
        
        return pattern_analysis


class EnhancedINDIRABrainOptimized:
    """
    Enhanced INDIRA Brain with sub-5ms path optimization.
    
    Integrates path optimization with existing INDIRA capabilities.
    """
    
    def __init__(self):
        self._path_optimizer = INDIRAPathOptimizer()
        self._decision_history: List[Dict[str, Any]] = []
        self._performance_metrics: Dict[str, float] = {
            "total_decisions": 0,
            "successful_decisions": 0,
            "average_latency_ms": 0.0,
            "average_confidence": 0.0,
        }
        
        # Pre-compute common scenarios
        self._pre_compute_common_scenarios()
        
        self._lock = threading.Lock()
        
        logger.info("Enhanced INDIRA Brain with sub-5ms optimization initialized")
    
    def _pre_compute_common_scenarios(self):
        """Pre-compute decisions for common market scenarios."""
        common_scenarios = [
            {"signal": 0.5, "volatility": 0.3, "regime": "BULLISH", "trend": "UP"},
            {"signal": -0.5, "volatility": 0.3, "regime": "BEARISH", "trend": "DOWN"},
            {"signal": 0.0, "volatility": 0.1, "regime": "SIDEWAYS", "trend": "NEUTRAL"},
            {"signal": 0.8, "volatility": 0.5, "regime": "HIGH_VOLATILITY", "trend": "VOLATILE"},
        ]
        
        for scenario in common_scenarios:
            decision = self._compute_decision_for_scenario(scenario)
            self._path_optimizer.pre_compute_decision(
                scenario, decision, 0.90
            )
    
    def _compute_decision_for_scenario(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Compute decision for a given scenario."""
        signal = scenario.get("signal", 0.0)
        volatility = scenario.get("volatility", 0.0)
        
        if signal > 0.3:
            decision_type = "BUY"
            side = "BUY"
        elif signal < -0.3:
            decision_type = "SELL"
            side = "SELL"
        else:
            decision_type = "HOLD"
            side = "HOLD"
        
        return {
            "decision_type": decision_type,
            "side": side,
            "confidence": min(abs(signal), 0.95),
            "reasoning": f"Signal: {signal:.3f}, Volatility: {volatility:.3f}"
        }
    
    def execute_fast_trading_decision(self, market_state: Dict[str, Any], 
                                    asset: str) -> Dict[str, Any]:
        """Execute fast trading decision with sub-5ms optimization."""
        start_time = time.time()
        
        # Use path optimizer for sub-5ms latency
        decision, latency_ms = self._path_optimizer.optimize_decision_path(
            market_state, self._compute_decision_for_scenario
        )
        
        # Enhance decision with asset-specific information
        decision["asset"] = asset
        decision["timestamp"] = datetime.now().isoformat()
        decision["latency_ms"] = latency_ms
        decision["path_optimized"] = True
        
        # Update performance metrics
        with self._lock:
            self._decision_history.append(decision)
            self._performance_metrics["total_decisions"] += 1
            self._performance_metrics["average_latency_ms"] = (
                (self._performance_metrics["average_latency_ms"] * 
                 (self._performance_metrics["total_decisions"] - 1) + latency_ms) /
                self._performance_metrics["total_decisions"]
            )
            self._performance_metrics["average_confidence"] = (
                (self._performance_metrics["average_confidence"] * 
                 (self._performance_metrics["total_decisions"] - 1) + 
                 decision.get("confidence", 0.0)) /
                self._performance_metrics["total_decisions"]
            )
        
        # Check if we achieved sub-5ms target
        if latency_ms < 5.0:
            logger.info(f"✅ Sub-5ms achieved: {latency_ms:.2f}ms for {asset}")
        else:
            logger.warning(f"⚠️ Missed sub-5ms target: {latency_ms:.2f}ms for {asset}")
        
        return decision
    
    def get_optimization_metrics(self) -> Dict[str, Any]:
        """Get comprehensive optimization metrics."""
        path_metrics = self._path_optimizer.get_metrics()
        
        return {
            "path_optimization": path_metrics.__dict__,
            "brain_performance": self._performance_metrics,
            "sub_5ms_achievement_rate": (
                len([d for d in self._decision_history if d["latency_ms"] < 5.0]) /
                len(self._decision_history) if self._decision_history else 0.0
            )
        }
    
    def cleanup_cache(self):
        """Clean up cache to maintain performance."""
        self._path_optimizer.cleanup_cache()


# Global instance
_enhanced_indira_optimized: Optional[EnhancedINDIRABrainOptimized] = None


def get_enhanced_indira_optimized() -> EnhancedINDIRABrainOptimized:
    """Get global enhanced INDIRA brain instance."""
    global _enhanced_indira_optimized
    if _enhanced_indira_optimized is None:
        _enhanced_indira_optimized = EnhancedINDIRABrainOptimized()
    return _enhanced_indira_optimized