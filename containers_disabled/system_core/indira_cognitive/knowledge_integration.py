"""INDIRA Knowledge Integration - Integration with Production Knowledge Layer.

This module integrates INDIRA's signal intelligence with the production
knowledge layer to transform it from signal-based to knowledge-based market intelligence.
"""

from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class SignalType(str, Enum):
    """Types of signals processed by INDIRA."""

    PRICE = "PRICE"
    VOLUME = "VOLUME"
    ORDER_FLOW = "ORDER_FLOW"
    SENTIMENT = "SENTIMENT"
    NEWS = "NEWS"
    TECHNICAL = "TECHNICAL"


class KnowledgeLevel(str, Enum):
    """Levels of knowledge validation."""

    RAW = "RAW"
    VALIDATED = "VALIDATED"
    CONFLICTING = "CONFLICTING"
    EDGE_CASE = "EDGE_CASE"
    DRIFTING = "DRIFTING"


@dataclass
class Signal:
    """Raw signal from market data."""

    signal_id: str
    signal_type: SignalType
    symbol: str
    value: float
    source: str
    timestamp: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EnhancedSignal:
    """Enhanced signal with knowledge validation."""

    signal: Signal
    knowledge_level: KnowledgeLevel
    confidence: float
    validation_details: Dict[str, Any] = field(default_factory=dict)
    conflicts: List[str] = field(default_factory=list)
    edge_cases: List[str] = field(default_factory=list)


class INDIRAKnowledgeIntegration:
    """INDIRA with integrated production knowledge layer."""

    def __init__(self):
        self._lock = threading.Lock()
        self._knowledge_validator = self._get_knowledge_validator()
        self._source_conflict_graph = self._get_source_conflict_graph()
        self._edge_case_memory = self._get_edge_case_memory()
        self._drift_monitor = self._get_drift_monitor()
        self._memory_index = self._get_memory_index()
        self._signal_cache: Dict[str, EnhancedSignal] = {}
        self._learning_history: List[Dict[str, Any]] = []

    def _get_knowledge_validator(self):
        """Get knowledge validator instance."""
        try:
            from intelligence_engine.knowledge.knowledge_validator import get_knowledge_validator

            return get_knowledge_validator()
        except ImportError:
            logger.warning(
                "[INDIRA_KNOWLEDGE] Knowledge validator not available, using placeholder"
            )
            return None

    def _get_source_conflict_graph(self):
        """Get source conflict graph instance."""
        try:
            from intelligence_engine.knowledge.source_conflict_graph import (
                get_source_conflict_graph,
            )

            return get_source_conflict_graph()
        except ImportError:
            logger.warning(
                "[INDIRA_KNOWLEDGE] Source conflict graph not available, using placeholder"
            )
            return None

    def _get_edge_case_memory(self):
        """Get edge case memory instance."""
        try:
            from state.memory.edge_case_memory import EdgeCaseMemory

            return EdgeCaseMemory()
        except ImportError:
            logger.warning("[INDIRA_KNOWLEDGE] Edge case memory not available, using placeholder")
            return None

    def _get_drift_monitor(self):
        """Get drift monitor instance."""
        try:
            from intelligence_engine.knowledge.drift_monitor import DriftMonitor

            return DriftMonitor()
        except ImportError:
            logger.warning("[INDIRA_KNOWLEDGE] Drift monitor not available, using placeholder")
            return None

    def _get_memory_index(self):
        """Get memory index instance."""
        try:
            from state.memory.index import get_memory_index

            return get_memory_index()
        except ImportError:
            logger.warning("[INDIRA_KNOWLEDGE] Memory index not available, using placeholder")
            return None

    def process_signal_with_knowledge(self, signal: Signal) -> EnhancedSignal:
        """Process signal through knowledge validation layers."""
        logger.debug(
            f"[INDIRA_KNOWLEDGE] Processing signal: {signal.signal_type} for {signal.symbol}"
        )

        # Level 1: Raw signal
        enhanced = EnhancedSignal(
            signal=signal, knowledge_level=KnowledgeLevel.RAW, confidence=0.5, validation_details={}
        )

        # Level 2: Validation (if knowledge validator available)
        if self._knowledge_validator:
            is_valid, confidence = self._validate_signal(signal)
            enhanced.knowledge_level = KnowledgeLevel.VALIDATED if is_valid else KnowledgeLevel.RAW
            enhanced.confidence = confidence
            enhanced.validation_details["validator_result"] = is_valid

        # Level 3: Conflict detection (if source conflict graph available)
        if self._source_conflict_graph:
            conflicts = self._check_source_conflicts(signal)
            if conflicts:
                enhanced.knowledge_level = KnowledgeLevel.CONFLICTING
                enhanced.conflicts = conflicts
                enhanced.confidence *= 0.5  # Reduce confidence for conflicts
                logger.warning(f"[INDIRA_KNOWLEDGE] Signal conflicts detected: {conflicts}")

        # Level 4: Edge case detection (if edge case memory available)
        if self._edge_case_memory:
            is_edge_case, edge_case_type = self._check_edge_case(signal)
            if is_edge_case:
                enhanced.knowledge_level = KnowledgeLevel.EDGE_CASE
                enhanced.edge_cases.append(edge_case_type)
                enhanced.confidence *= 0.8  # Moderate confidence reduction for edge cases
                logger.info(f"[INDIRA_KNOWLEDGE] Edge case detected: {edge_case_type}")

        # Level 5: Drift detection (if drift monitor available)
        if self._drift_monitor:
            drift_status = self._check_drift(signal)
            if drift_status:
                enhanced.knowledge_level = KnowledgeLevel.DRIFTING
                enhanced.confidence *= 0.7  # Reduce confidence for drift
                logger.warning(f"[INDIRA_KNOWLEDGE] Drift detected: {drift_status}")

        # Cache enhanced signal
        self._cache_enhanced_signal(enhanced)

        return enhanced

    def _validate_signal(self, signal: Signal) -> Tuple[bool, float]:
        """Validate signal using knowledge validator."""
        try:
            # Convert signal to knowledge validator format
            signal_data = {
                "signal_id": signal.signal_id,
                "signal_type": signal.signal_type.value,
                "symbol": signal.symbol,
                "value": signal.value,
                "source": signal.source,
                "timestamp": signal.timestamp,
                "metadata": signal.metadata,
            }
            return self._knowledge_validator.validate_market_signal(signal_data)
        except Exception as e:
            logger.warning(f"[INDIRA_KNOWLEDGE] Signal validation failed: {e}")
            return True, 0.5  # Default to valid with moderate confidence

    def _check_source_conflicts(self, signal: Signal) -> List[str]:
        """Check for source conflicts using conflict graph."""
        try:
            # Create conflict context
            context = {
                "signal_id": signal.signal_id,
                "symbol": signal.symbol,
                "source": signal.source,
                "value": signal.value,
                "timestamp": signal.timestamp,
            }
            return self._source_conflict_graph.check_conflicts(context)
        except Exception as e:
            logger.warning(f"[INDIRA_KNOWLEDGE] Conflict check failed: {e}")
            return []

    def _check_edge_case(self, signal: Signal) -> Tuple[bool, str]:
        """Check if signal represents an edge case."""
        try:
            # Convert signal to edge case memory format
            signal_data = {
                "signal_id": signal.signal_id,
                "symbol": signal.symbol,
                "value": signal.value,
                "timestamp": signal.timestamp,
                "metadata": signal.metadata,
            }
            return self._edge_case_memory.detect_edge_case(signal_data)
        except Exception as e:
            logger.warning(f"[INDIRA_KNOWLEDGE] Edge case detection failed: {e}")
            return False, "unknown"

    def _check_drift(self, signal: Signal) -> bool:
        """Check for distribution drift in signal."""
        try:
            # Create drift monitoring context
            context = {
                "signal_id": signal.signal_id,
                "symbol": signal.symbol,
                "value": signal.value,
                "timestamp": signal.timestamp,
                "metadata": signal.metadata,
            }
            drift_result = self._drift_monitor.check_drift(context)
            return drift_result.drift_detected
        except Exception as e:
            logger.warning(f"[INDIRA_KNOWLEDGE] Drift detection failed: {e}")
            return False

    def _cache_enhanced_signal(self, enhanced: EnhancedSignal):
        """Cache enhanced signal for quick access."""
        with self._lock:
            key = f"{enhanced.signal.symbol}_{enhanced.signal.signal_type}_{enhanced.signal.signal_id}"
            self._signal_cache[key] = enhanced

    def get_cached_signal(self, signal_id: str) -> Optional[EnhancedSignal]:
        """Get cached enhanced signal."""
        with self._lock:
            for enhanced in self._signal_cache.values():
                if enhanced.signal.signal_id == signal_id:
                    return enhanced
        return None

    def query_market_knowledge(self, symbol: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Query market knowledge from memory index."""
        logger.info(f"[INDIRA_KNOWLEDGE] Querying market knowledge for {symbol}")

        if self._memory_index:
            try:
                # Search memory index for symbol-specific knowledge
                keywords = [symbol, "market", "knowledge"]
                if "query_type" in context:
                    keywords.append(context["query_type"])

                records = self._memory_index.search(keywords, limit=10)

                knowledge = {
                    "records_found": len(records),
                    "symbol": symbol,
                    "context": context,
                    "confidence": 0.5 if records else 0.0,
                }

                if records:
                    knowledge["market_knowledge"] = {
                        "latest_records": [
                            {
                                "record_id": r.record_id,
                                "summary": r.summary,
                                "tags": r.tags,
                                "timestamp": r.ts_ns,
                            }
                            for r in records[:5]
                        ]
                    }

                return knowledge
            except Exception as e:
                logger.warning(f"[INDIRA_KNOWLEDGE] Market knowledge query failed: {e}")
                return {"error": str(e), "confidence": 0.0}
        else:
            logger.warning("[INDIRA_KNOWLEDGE] Memory index not available")
            return {"error": "Memory index not available", "confidence": 0.0}

    def apply_market_knowledge_to_strategy(self, strategy: Dict[str, Any]) -> Dict[str, Any]:
        """Apply market knowledge to strategy formulation."""
        logger.info("[INDIRA_KNOWLEDGE] Applying market knowledge to strategy")

        # Extract symbol from strategy
        symbol = strategy.get("symbol", "")
        if symbol:
            knowledge = self.query_market_knowledge(symbol, {"strategy_type": strategy.get("type")})

            # Enhance strategy with knowledge
            enhanced_strategy = {
                "original": strategy,
                "knowledge_applied": True,
                "market_knowledge": knowledge,
                "adjustments": self._make_knowledge_based_adjustments(strategy, knowledge),
            }
            return enhanced_strategy
        else:
            logger.warning("[INDIRA_KNOWLEDGE] No symbol in strategy to apply knowledge")
            return {
                "original": strategy,
                "knowledge_applied": False,
                "market_knowledge": {},
                "adjustments": {},
                "reason": "No symbol in strategy",
            }

    def _make_knowledge_based_adjustments(
        self, strategy: Dict[str, Any], knowledge: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Make knowledge-based adjustments to strategy parameters."""
        adjustments = {}

        # Risk adjustments based on knowledge
        if "risk_level" in knowledge:
            adjustments["risk_adjustment"] = knowledge["risk_level"]

        # Position sizing adjustments
        if "recommended_position_size" in knowledge:
            adjustments["position_size_adjustment"] = knowledge["recommended_position_size"]

        # Timing adjustments
        if "optimal_timing" in knowledge:
            adjustments["timing_adjustment"] = knowledge["optimal_timing"]

        # Confidence adjustments
        if "strategy_confidence" in knowledge:
            adjustments["confidence_adjustment"] = knowledge["strategy_confidence"]

        return adjustments

    def learn_from_execution_results(self, execution_results: List[Dict[str, Any]]) -> None:
        """Learn from execution results to update knowledge base."""
        logger.info(f"[INDIRA_KNOWLEDGE] Learning from {len(execution_results)} execution results")

        for result in execution_results:
            # Extract patterns from successful executions
            if result.get("success"):
                self._extract_successful_patterns(result)
            else:
                self._extract_failure_patterns(result)

        # Update learning history
        self._update_learning_history(execution_results)

    def _extract_successful_patterns(self, result: Dict[str, Any]) -> None:
        """Extract patterns from successful execution."""
        try:
            pattern = {
                "type": "success",
                "symbol": result.get("symbol", "unknown"),
                "strategy": result.get("strategy", "unknown"),
                "timestamp": time.time(),
                "success_factors": self._identify_success_factors(result),
            }

            if self._memory_index:
                # Store successful pattern in memory using the correct interface
                try:
                    from state.memory.contracts import MemoryKind, MemoryRecord

                    record = MemoryRecord(
                        record_id=f"success_pattern_{int(time.time() * 1000)}_{hash(str(result)) % 10000}",
                        ts_ns=int(time.time() * 1_000_000_000),
                        kind=MemoryKind.PROCEDURAL,
                        source="indira_knowledge_integration",
                        summary=f"Successful execution: {result.get('symbol')} using {result.get('strategy')}",
                        tags=[
                            "success",
                            "pattern",
                            result.get("symbol", "unknown"),
                            result.get("strategy", "unknown"),
                        ],
                        body=pattern,
                    )
                    self._memory_index.index(record)
                except Exception as e:
                    logger.warning(f"[INDIRA_KNOWLEDGE] Failed to create memory record: {e}")
        except Exception as e:
            logger.warning(f"[INDIRA_KNOWLEDGE] Successful pattern extraction failed: {e}")

    def _extract_failure_patterns(self, result: Dict[str, Any]) -> None:
        """Extract patterns from failed execution."""
        try:
            pattern = {
                "type": "failure",
                "symbol": result.get("symbol", "unknown"),
                "strategy": result.get("strategy", "unknown"),
                "timestamp": time.time(),
                "failure_factors": self._identify_failure_factors(result),
            }

            if self._memory_index:
                # Store failure pattern in memory using the correct interface
                try:
                    from state.memory.contracts import MemoryKind, MemoryRecord

                    record = MemoryRecord(
                        record_id=f"failure_pattern_{int(time.time() * 1000)}_{hash(str(result)) % 10000}",
                        ts_ns=int(time.time() * 1_000_000_000),
                        kind=MemoryKind.RUNTIME,
                        source="indira_knowledge_integration",
                        summary=f"Failed execution: {result.get('symbol')} using {result.get('strategy')}",
                        tags=[
                            "failure",
                            "pattern",
                            result.get("symbol", "unknown"),
                            result.get("strategy", "unknown"),
                        ],
                        body=pattern,
                    )
                    self._memory_index.index(record)
                except Exception as e:
                    logger.warning(f"[INDIRA_KNOWLEDGE] Failed to create memory record: {e}")
        except Exception as e:
            logger.warning(f"[INDIRA_KNOWLEDGE] Failure pattern extraction failed: {e}")

    def _identify_success_factors(self, result: Dict[str, Any]) -> List[str]:
        """Identify factors that contributed to success."""
        factors = []

        try:
            # Success from good timing?
            exec_time = result.get("execution_time")
            expected_time = result.get("expected_execution_time", float("inf"))
            if exec_time is not None and exec_time < expected_time:
                factors.append("optimal_timing")

            # Success from good position sizing?
            if result.get("position_size_optimal", False):
                factors.append("optimal_position_size")

            # Success from market conditions?
            if result.get("market_conditions_favorable", False):
                factors.append("favorable_market_conditions")
        except Exception as e:
            logger.warning(f"[INDIRA_KNOWLEDGE] Success factor identification error: {e}")

        return factors

    def _identify_failure_factors(self, result: Dict[str, Any]) -> List[str]:
        """Identify factors that contributed to failure."""
        factors = []

        try:
            # Failure from poor timing?
            exec_time = result.get("execution_time")
            expected_time = result.get("expected_execution_time", 0)
            if exec_time is not None and exec_time > expected_time:
                factors.append("suboptimal_timing")

            # Failure from position sizing?
            if result.get("position_size_over_risk", False):
                factors.append("excessive_position_size")

            # Failure from market conditions?
            if result.get("adverse_market_movement", False):
                factors.append("adverse_market_movement")

            # Failure from execution issues?
            if result.get("execution_error", False):
                factors.append("execution_infrastructure_issue")
        except Exception as e:
            logger.warning(f"[INDIRA_KNOWLEDGE] Failure factor identification error: {e}")

        return factors

    def _update_learning_history(self, execution_results: List[Dict[str, Any]]) -> None:
        """Update learning history with execution results."""
        learning_entry = {
            "timestamp": time.time(),
            "results_count": len(execution_results),
            "success_rate": (
                sum(1 for r in execution_results if r.get("success")) / len(execution_results)
                if execution_results
                else 0.0
            ),
            "symbols_traded": list(set(r.get("symbol") for r in execution_results)),
        }

        self._learning_history.append(learning_entry)

        # Keep only recent history
        if len(self._learning_history) > 1000:
            self._learning_history = self._learning_history[-1000:]

    def get_knowledge_statistics(self) -> Dict[str, Any]:
        """Get knowledge integration statistics."""
        with self._lock:
            return {
                "cached_signals": len(self._signal_cache),
                "learning_history_entries": len(self._learning_history),
                "knowledge_validator_available": self._knowledge_validator is not None,
                "source_conflict_graph_available": self._source_conflict_graph is not None,
                "edge_case_memory_available": self._edge_case_memory is not None,
                "drift_monitor_available": self._drift_monitor is not None,
                "memory_index_available": self._memory_index is not None,
            }


class KnowledgeBasedIntelligence:
    """INDIRA with knowledge-based market intelligence rather than signal-only."""

    def __init__(self):
        self._signal_intelligence = self._get_signal_intelligence()
        self.knowledge_intelligence = INDIRAKnowledgeIntegration()
        self._world_understanding = self._get_world_understanding()

    def _get_signal_intelligence(self):
        """Get signal intelligence component."""
        try:
            from indira_cognitive.indira_brain.concrete import get_indira_brain

            return get_indira_brain()
        except ImportError:
            logger.warning("[INDIRA_KNOWLEDGE] Signal intelligence not available")
            return None

    def _get_world_understanding(self):
        """Get world understanding component."""
        try:
            from world_model.world_model import get_production_world_model

            return get_production_world_model()
        except ImportError:
            logger.warning("[INDIRA_KNOWLEDGE] World model not available")
            return None

    def generate_knowledge_based_insights(self, market_state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate insights based on market knowledge rather than just signals."""
        logger.info("[INDIRA_KNOWLEDGE] Generating knowledge-based insights")

        # Query market knowledge
        knowledge = self.knowledge_intelligence.query_market_knowledge(
            market_state.get("symbol", ""), {"market_state": market_state}
        )

        # Get world understanding context
        world_context = {}
        if self._world_understanding:
            world_context = self._world_understanding.get_world_state()

        # Combine with signal intelligence if available
        signal_insights = {}
        if self._signal_intelligence:
            signal_insights = self._generate_signal_insights(market_state)

        # Generate knowledge-based insights
        knowledge_insights = self._generate_knowledge_insights(market_state, knowledge)

        return {
            "signal_insights": signal_insights,
            "knowledge_insights": knowledge_insights,
            "world_context": world_context,
            "combined_intelligence": self._combine_intelligence(
                signal_insights, knowledge_insights, world_context
            ),
        }

    def _generate_signal_insights(self, market_state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate signal-based insights."""
        # Placeholder for signal intelligence integration
        return {"signal_quality": "unknown", "signal_confidence": 0.5}

    def _generate_knowledge_insights(
        self, market_state: Dict[str, Any], knowledge: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate knowledge-based insights."""
        insights = {
            "knowledge_level": "knowledge_based",
            "confidence": 0.0,
            "applicable_knowledge": [],
            "knowledge_sources": [],
        }

        # Extract applicable knowledge
        if "market_knowledge" in knowledge:
            insights["applicable_knowledge"] = list(knowledge.get("market_knowledge", {}).keys())
            insights["confidence"] = knowledge.get("confidence", 0.5)

        return insights

    def _combine_intelligence(self, signals: Dict, knowledge: Dict, world: Dict) -> Dict[str, Any]:
        """Combine signal intelligence, knowledge intelligence, and world understanding."""
        combined = {
            "signal_component_weight": 0.3,
            "knowledge_component_weight": 0.5,
            "world_understanding_weight": 0.2,
            "timestamp": time.time(),
        }

        # Calculate combined confidence
        signal_confidence = signals.get("signal_confidence", 0.5)
        knowledge_confidence = knowledge.get("confidence", 0.5)
        combined["combined_confidence"] = (
            signal_confidence * combined["signal_component_weight"]
            + knowledge_confidence * combined["knowledge_component_weight"]
        )

        return combined


# Singleton instances
_indira_knowledge_integration: Optional[INDIRAKnowledgeIntegration] = None
_knowledge_integration_lock = threading.Lock()
_knowledge_based_intelligence: Optional[KnowledgeBasedIntelligence] = None


def get_indira_knowledge_integration() -> INDIRAKnowledgeIntegration:
    """Get the singleton INDIRA knowledge integration instance."""
    global _indira_knowledge_integration
    if _indira_knowledge_integration is None:
        with _knowledge_integration_lock:
            if _indira_knowledge_integration is None:
                _indira_knowledge_integration = INDIRAKnowledgeIntegration()
    return _indira_knowledge_integration


def get_knowledge_based_intelligence() -> KnowledgeBasedIntelligence:
    """Get the singleton knowledge-based intelligence instance."""
    global _knowledge_based_intelligence
    if _knowledge_based_intelligence is None:
        _knowledge_based_intelligence = KnowledgeBasedIntelligence()
    return _knowledge_based_intelligence


__all__ = [
    "INDIRAKnowledgeIntegration",
    "get_indira_knowledge_integration",
    "KnowledgeBasedIntelligence",
    "get_knowledge_based_intelligence",
    "Signal",
    "EnhancedSignal",
    "SignalType",
    "KnowledgeLevel",
]
