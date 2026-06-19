"""
shared_infrastructure.signal_processing
DIX VISION v42.2 — Signal Processing Service

Processes, aggregates, and transforms signals from multiple sources.
Addresses critical gap identified in system preservation analysis.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any, Dict, List, Optional, Callable
from abc import ABC, abstractmethod
from collections import deque
import threading


class SignalType(StrEnum):
    """Types of signals."""
    MARKET_DATA = "market_data"
    TRADING_SIGNAL = "trading_signal"
    SYSTEM_EVENT = "system_event"
    COGNITIVE_SIGNAL = "cognitive_signal"
    ERROR_SIGNAL = "error_signal"
    PERFORMANCE_SIGNAL = "performance_signal"
    CUSTOM = "custom"


class ProcessingStage(StrEnum):
    """Signal processing stages."""
    RAW = "raw"
    FILTERED = "filtered"
    TRANSFORMED = "transformed"
    ENRICHED = "enriched"
    FINAL = "final"


@dataclass
class SignalEvent:
    """A signal event."""
    signal_id: str
    signal_type: SignalType
    
    # Signal content
    source: str = ""
    symbol: str = ""
    value: float = 0.0
    side: str = "HOLD"  # BUY | SELL | HOLD
    confidence: float = 0.5
    trust: float = 0.9
    
    # Timing
    timestamp_ns: int = 0
    timestamp_utc: str = ""
    
    # Processing metadata
    processing_stage: ProcessingStage = ProcessingStage.RAW
    processed_by: List[str] = field(default_factory=list)
    
    # Signal data
    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize timestamp if not provided."""
        if not self.timestamp_utc:
            self.timestamp_utc = datetime.utcnow().isoformat()
        if self.timestamp_ns == 0:
            try:
                from system.time_source import now
                self.timestamp_ns = now().monotonic_ns()
            except Exception:
                import time
                self.timestamp_ns = int(time.time_ns())


@dataclass
class SignalFilter:
    """A filter for signal processing."""
    filter_id: str
    filter_type: str  # threshold | outlier | noise | custom
    
    # Filter parameters
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    confidence_threshold: float = 0.0
    trust_threshold: float = 0.0
    
    # Filter scope
    applies_to_signal_types: List[SignalType] = field(default_factory=list)
    applies_to_sources: List[str] = field(default_factory=list)
    
    # Filter statistics
    signals_filtered: int = 0
    signals_passed: int = 0
    
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def should_filter(self, signal: SignalEvent) -> tuple[bool, str]:
        """Check if signal should be filtered."""
        reason = ""
        should_filter = False
        
        # Check confidence threshold
        if signal.confidence < self.confidence_threshold:
            should_filter = True
            reason = f"Confidence {signal.confidence} below threshold {self.confidence_threshold}"
        
        # Check trust threshold
        if signal.trust < self.trust_threshold:
            should_filter = True
            reason = f"Trust {signal.trust} below threshold {self.trust_threshold}"
        
        # Check value thresholds
        if self.min_value is not None and signal.value < self.min_value:
            should_filter = True
            reason = f"Value {signal.value} below minimum {self.min_value}"
        
        if self.max_value is not None and signal.value > self.max_value:
            should_filter = True
            reason = f"Value {signal.value} above maximum {self.max_value}"
        
        # Check signal type scope
        if self.applies_to_signal_types and signal.signal_type not in self.applies_to_signal_types:
            return False, "Signal type not in filter scope"
        
        # Check source scope
        if self.applies_to_sources and signal.source not in self.applies_to_sources:
            return False, "Source not in filter scope"
        
        if should_filter:
            self.signals_filtered += 1
        else:
            self.signals_passed += 1
        
        return should_filter, reason


@dataclass
class SignalTransformer:
    """A transformer for signal processing."""
    transformer_id: str
    transformer_type: str  # normalize | scale | aggregate | derive | custom
    
    # Transformer parameters
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    # Transformer scope
    applies_to_signal_types: List[SignalType] = field(default_factory=list)
    applies_to_sources: List[str] = field(default_factory=list)
    
    # Transformer statistics
    signals_transformed: int = 0
    
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def transform(self, signal: SignalEvent) -> SignalEvent:
        """Transform a signal."""
        # Check scope
        if self.applies_to_signal_types and signal.signal_type not in self.applies_to_signal_types:
            return signal
        
        if self.applies_to_sources and signal.source not in self.applies_to_sources:
            return signal
        
        # Apply transformation based on type
        if self.transformer_type == "normalize":
            return self._normalize(signal)
        elif self.transformer_type == "scale":
            return self._scale(signal)
        elif self.transformer_type == "derive":
            return self._derive(signal)
        else:
            return signal
    
    def _normalize(self, signal: SignalEvent) -> SignalEvent:
        """Normalize signal value to [0,1] range."""
        min_val = self.parameters.get("min_value", 0.0)
        max_val = self.parameters.get("max_value", 1.0)
        
        if max_val > min_val:
            normalized_value = (signal.value - min_val) / (max_val - min_val)
            normalized_value = max(0.0, min(1.0, normalized_value))
            
            # Create new signal with transformed value
            transformed_signal = SignalEvent(
                signal_id=f"{signal.signal_id}_normalized",
                signal_type=signal.signal_type,
                source=signal.source,
                symbol=signal.symbol,
                value=normalized_value,
                side=signal.side,
                confidence=signal.confidence,
                trust=signal.trust,
                timestamp_ns=signal.timestamp_ns,
                timestamp_utc=signal.timestamp_utc,
                processing_stage=ProcessingStage.TRANSFORMED,
                processed_by=signal.processed_by + [self.transformer_id],
                data=dict(signal.data),
                metadata=dict(signal.metadata)
            )
            
            self.signals_transformed += 1
            return transformed_signal
        
        return signal
    
    def _scale(self, signal: SignalEvent) -> SignalEvent:
        """Scale signal value by a factor."""
        scale_factor = self.parameters.get("scale_factor", 1.0)
        
        scaled_value = signal.value * scale_factor
        
        # Create new signal with scaled value
        transformed_signal = SignalEvent(
            signal_id=f"{signal.signal_id}_scaled",
            signal_type=signal.signal_type,
            source=signal.source,
            symbol=signal.symbol,
            value=scaled_value,
            side=signal.side,
            confidence=signal.confidence,
            trust=signal.trust,
            timestamp_ns=signal.timestamp_ns,
            timestamp_utc=signal.timestamp_utc,
            processing_stage=ProcessingStage.TRANSFORMED,
            processed_by=signal.processed_by + [self.transformer_id],
            data=dict(signal.data),
            metadata=dict(signal.metadata)
        )
        
        self.signals_transformed += 1
        return transformed_signal
    
    def _derive(self, signal: SignalEvent) -> SignalEvent:
        """Derive new signal from existing signal."""
        derivation_type = self.parameters.get("derivation_type", "momentum")
        
        derived_value = signal.value  # Default
        
        if derivation_type == "momentum":
            # Simple momentum (would need historical data in real implementation)
            derived_value = signal.value * 0.1
        elif derivation_type == "volatility":
            # Simple volatility estimate
            derived_value = abs(signal.value) * 0.5
        
        # Create new derived signal
        derived_signal = SignalEvent(
            signal_id=f"{signal.signal_id}_{derivation_type}",
            signal_type=signal.signal_type,
            source=signal.source,
            symbol=signal.symbol,
            value=derived_value,
            side=signal.side,
            confidence=signal.confidence * 0.9,  # Lower confidence for derived
            trust=signal.trust * 0.9,
            timestamp_ns=signal.timestamp_ns,
            timestamp_utc=signal.timestamp_utc,
            processing_stage=ProcessingStage.TRANSFORMED,
            processed_by=signal.processed_by + [self.transformer_id],
            data=dict(signal.data),
            metadata=dict(signal.metadata)
        )
        
        self.signals_transformed += 1
        return derived_signal


class SignalProcessingServiceInterface(ABC):
    """Interface for signal processing service."""
    
    @abstractmethod
    def funnel_signals(self, signals: List[SignalEvent]) -> SignalEvent:
        """Aggregate signals from multiple sources into a single signal."""
        pass
    
    @abstractmethod
    def process_signals(self, signals: List[SignalEvent]) -> List[SignalEvent]:
        """Process and transform signals through the pipeline."""
        pass
    
    @abstractmethod
    def add_filter(self, filter: SignalFilter) -> bool:
        """Add a signal filter."""
        pass
    
    @abstractmethod
    def add_transformer(self, transformer: SignalTransformer) -> bool:
        """Add a signal transformer."""
        pass
    
    @abstractmethod
    def get_signal_window(self, size: int = 100) -> List[SignalEvent]:
        """Get recent signal window."""
        pass
    
    @abstractmethod
    def get_processing_metrics(self) -> Dict[str, Any]:
        """Get signal processing metrics."""
        pass


class SignalProcessingService(SignalProcessingServiceInterface):
    """Concrete implementation of signal processing service."""
    
    def __init__(self, window_size: int = 1000):
        self._lock = threading.Lock()
        
        # Signal storage
        self._signal_window: deque[SignalEvent] = deque(maxlen=window_size)
        
        # Processing pipeline
        self._filters: List[SignalFilter] = []
        self._transformers: List[SignalTransformer] = []
        
        # Processing metrics
        self._metrics: Dict[str, Any] = {
            "total_signals_processed": 0,
            "signals_filtered": 0,
            "signals_transformed": 0,
            "average_processing_time_ms": 0.0
        }
        
        # Signal funnel configuration
        self._funnel_config: Dict[str, Any] = {
            "aggregation_method": "weighted_average",  # weighted_average | majority_vote | custom
            "confidence_weight": 0.3,
            "trust_weight": 0.2,
            "recency_weight": 0.5
        }
    
    def funnel_signals(self, signals: List[SignalEvent]) -> SignalEvent:
        """Aggregate signals from multiple sources into a single signal."""
        if not signals:
            # Return empty signal if no input
            return SignalEvent(
                signal_id="empty",
                signal_type=SignalType.CUSTOM,
                processing_stage=ProcessingStage.FINAL
            )
        
        aggregation_method = self._funnel_config["aggregation_method"]
        
        if aggregation_method == "weighted_average":
            return self._weighted_average_aggregation(signals)
        elif aggregation_method == "majority_vote":
            return self._majority_vote_aggregation(signals)
        else:
            # Default to weighted average
            return self._weighted_average_aggregation(signals)
    
    def _weighted_average_aggregation(self, signals: List[SignalEvent]) -> SignalEvent:
        """Aggregate signals using weighted average."""
        if not signals:
            return SignalEvent(signal_id="empty", signal_type=SignalType.CUSTOM)
        
        # Calculate weights based on confidence, trust, and recency
        confidence_weight = self._funnel_config["confidence_weight"]
        trust_weight = self._funnel_config["trust_weight"]
        recency_weight = self._funnel_config["recency_weight"]
        
        weighted_values = []
        total_weight = 0.0
        
        # Get most recent timestamp for recency calculation
        current_time_ns = max(s.timestamp_ns for s in signals) if signals else 0
        max_time_diff = max((current_time_ns - s.timestamp_ns) for s in signals) if signals else 1
        
        for signal in signals:
            # Calculate recency weight (more recent = higher weight)
            time_diff = current_time_ns - signal.timestamp_ns
            recency_score = 1.0 - (time_diff / max_time_diff) if max_time_diff > 0 else 1.0
            
            # Calculate total weight
            weight = (
                signal.confidence * confidence_weight +
                signal.trust * trust_weight +
                recency_score * recency_weight
            )
            
            weighted_values.append(signal.value * weight)
            total_weight += weight
        
        # Calculate aggregated value
        if total_weight > 0:
            aggregated_value = sum(weighted_values) / total_weight
        else:
            aggregated_value = sum(s.value for s in signals) / len(signals)
        
        # Aggregate confidence and trust
        aggregated_confidence = sum(s.confidence for s in signals) / len(signals)
        aggregated_trust = sum(s.trust for s in signals) / len(signals)
        
        # Determine side by majority vote
        side_votes = {}
        for signal in signals:
            side_votes[signal.side] = side_votes.get(signal.side, 0) + 1
        
        if side_votes:
            aggregated_side = max(side_votes, key=side_votes.get)
        else:
            aggregated_side = "HOLD"
        
        # Create aggregated signal
        aggregated_signal = SignalEvent(
            signal_id=f"funneled_{int(datetime.utcnow().timestamp())}",
            signal_type=signals[0].signal_type,
            source="signal_funnel",
            symbol=signals[0].symbol,
            value=aggregated_value,
            side=aggregated_side,
            confidence=aggregated_confidence,
            trust=aggregated_trust,
            timestamp_ns=current_time_ns,
            processing_stage=ProcessingStage.FINAL,
            processed_by=["signal_funnel"],
            data={
                "input_signals": len(signals),
                "aggregation_method": "weighted_average",
                "input_sources": list(set(s.source for s in signals))
            }
        )
        
        return aggregated_signal
    
    def _majority_vote_aggregation(self, signals: List[SignalEvent]) -> SignalEvent:
        """Aggregate signals using majority vote."""
        if not signals:
            return SignalEvent(signal_id="empty", signal_type=SignalType.CUSTOM)
        
        # Get most common side
        side_votes = {}
        for signal in signals:
            side_votes[signal.side] = side_votes.get(signal.side, 0) + 1
        
        aggregated_side = max(side_votes, key=side_votes.get)
        
        # Get average value for signals with the winning side
        winning_signals = [s for s in signals if s.side == aggregated_side]
        aggregated_value = sum(s.value for s in winning_signals) / len(winning_signals) if winning_signals else 0.0
        
        # Aggregate confidence and trust
        aggregated_confidence = sum(s.confidence for s in signals) / len(signals)
        aggregated_trust = sum(s.trust for s in signals) / len(signals)
        
        # Create aggregated signal
        aggregated_signal = SignalEvent(
            signal_id=f"funneled_{int(datetime.utcnow().timestamp())}",
            signal_type=signals[0].signal_type,
            source="signal_funnel",
            symbol=signals[0].symbol,
            value=aggregated_value,
            side=aggregated_side,
            confidence=aggregated_confidence,
            trust=aggregated_trust,
            timestamp_ns=max(s.timestamp_ns for s in signals),
            processing_stage=ProcessingStage.FINAL,
            processed_by=["signal_funnel"],
            data={
                "input_signals": len(signals),
                "aggregation_method": "majority_vote",
                "winning_side": aggregated_side,
                "winning_votes": side_votes[aggregated_side]
            }
        )
        
        return aggregated_signal
    
    def process_signals(self, signals: List[SignalEvent]) -> List[SignalEvent]:
        """Process and transform signals through the pipeline."""
        if not signals:
            return []
        
        processed_signals = []
        
        for signal in signals:
            # Start with raw signal
            current_signal = signal
            current_signal.processing_stage = ProcessingStage.FILTERED
            
            # Apply filters
            for signal_filter in self._filters:
                should_filter, reason = signal_filter.should_filter(current_signal)
                if should_filter:
                    self._metrics["signals_filtered"] += 1
                    continue  # Skip this signal
            
            current_signal.processing_stage = ProcessingStage.TRANSFORMED
            
            # Apply transformers
            for transformer in self._transformers:
                current_signal = transformer.transform(current_signal)
                self._metrics["signals_transformed"] += 1
            
            # Final stage
            current_signal.processing_stage = ProcessingStage.FINAL
            processed_signals.append(current_signal)
            
            # Add to window
            self._signal_window.append(current_signal)
        
        # Update metrics
        self._metrics["total_signals_processed"] += len(signals)
        
        return processed_signals
    
    def add_filter(self, filter: SignalFilter) -> bool:
        """Add a signal filter."""
        with self._lock:
            self._filters.append(filter)
            return True
    
    def add_transformer(self, transformer: SignalTransformer) -> bool:
        """Add a signal transformer."""
        with self._lock:
            self._transformers.append(transformer)
            return True
    
    def get_signal_window(self, size: int = 100) -> List[SignalEvent]:
        """Get recent signal window."""
        with self._lock:
            return list(self._signal_window)[-size:]
    
    def get_processing_metrics(self) -> Dict[str, Any]:
        """Get signal processing metrics."""
        with self._lock:
            # Calculate filter statistics
            filter_stats = {
                f.name: {
                    "signals_filtered": f.signals_filtered,
                    "signals_passed": f.signals_passed,
                    "filter_rate": f.signals_filtered / (f.signals_filtered + f.signals_passed) if (f.signals_filtered + f.signals_passed) > 0 else 0
                }
                for f in self._filters
            }
            
            # Calculate transformer statistics
            transformer_stats = {
                t.transformer_id: {
                    "signals_transformed": t.signals_transformed,
                    "transformer_type": t.transformer_type
                }
                for t in self._transformers
            }
            
            return {
                "total_signals_processed": self._metrics["total_signals_processed"],
                "signals_filtered": self._metrics["signals_filtered"],
                "signals_transformed": self._metrics["signals_transformed"],
                "average_processing_time_ms": self._metrics["average_processing_time_ms"],
                "current_window_size": len(self._signal_window),
                "active_filters": len(self._filters),
                "active_transformers": len(self._transformers),
                "filter_statistics": filter_stats,
                "transformer_statistics": transformer_stats,
                "funnel_configuration": self._funnel_config
            }
    
    def set_funnel_config(self, config: Dict[str, Any]) -> bool:
        """Set funnel aggregation configuration."""
        with self._lock:
            self._funnel_config.update(config)
            return True


# Global instance
_signal_processing_service: Optional[SignalProcessingService] = None
_signal_processing_lock = threading.Lock()


def get_signal_processing_service() -> SignalProcessingService:
    """Get global signal processing service instance."""
    global _signal_processing_service
    if _signal_processing_service is None:
        with _signal_processing_lock:
            if _signal_processing_service is None:
                _signal_processing_service = SignalProcessingService()
    return _signal_processing_service


__all__ = [
    "SignalType",
    "ProcessingStage",
    "SignalEvent",
    "SignalFilter",
    "SignalTransformer",
    "SignalProcessingServiceInterface",
    "SignalProcessingService",
    "get_signal_processing_service",
]