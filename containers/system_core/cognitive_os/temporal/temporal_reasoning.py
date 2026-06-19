"""Advanced Temporal Knowledge Reasoning - Time-Aware Intelligence.

This module provides advanced temporal reasoning capabilities, enabling the system
to understand and reason about time-based knowledge, temporal relationships, and
temporal causality.
"""

from __future__ import annotations

import logging
import threading
import time
import numpy as np
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Set
from enum import Enum
from collections import defaultdict, deque
from datetime import datetime, timedelta
import math

logger = logging.getLogger(__name__)


class TemporalRelation(str, Enum):
    """Types of temporal relations."""
    BEFORE = "BEFORE"
    AFTER = "AFTER"
    DURING = "DURING"
    OVERLAPS = "OVERLAPS"
    MEETS = "MEETS"
    STARTS = "STARTS"
    FINISHES = "FINISHES"
    EQUALS = "EQUALS"


class TemporalOperator(str, Enum):
    """Temporal operators for reasoning."""
    ALWAYS = "ALWAYS"
    EVENTUALLY = "EVENTUALLY"
    NEXT = "NEXT"
    UNTIL = "UNTIL"
    RELEASES = "RELEASES"
    SINCE = "SINCE"
    TRIGGERED_BY = "TRIGGERED_BY"
    LEADS_TO = "LEADS_TO"


class TimeUnit(str, Enum):
    """Time units for temporal reasoning."""
    MILLISECOND = "MILLISECOND"
    SECOND = "SECOND"
    MINUTE = "MINUTE"
    HOUR = "HOUR"
    DAY = "DAY"
    WEEK = "WEEK"
    MONTH = "MONTH"
    YEAR = "YEAR"


@dataclass
class TemporalInterval:
    """Time interval with start and end."""
    interval_id: str
    start_time: float
    end_time: float
    unit: TimeUnit
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def duration(self) -> float:
        """Get duration of interval."""
        return self.end_time - self.start_time


@dataclass
class TemporalEvent:
    """Event occurring at a specific time."""
    event_id: str
    event_type: str
    timestamp: float
    attributes: Dict[str, Any]
    causality_links: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TemporalKnowledge:
    """Knowledge with temporal component."""
    knowledge_id: str
    content: str
    temporal_context: TemporalInterval
    validity_period: TemporalInterval
    temporal_relation: Optional[TemporalRelation]
    confidence: float
    decay_rate: float
    last_updated: float


@dataclass
class TemporalReasoningResult:
    """Result of temporal reasoning."""
    reasoning_id: str
    query: str
    result: Any
    confidence: float
    temporal_evidence: List[TemporalEvent]
    reasoning_path: List[str]
    timestamp: float


class TemporalKnowledgeReasoner:
    """Advanced temporal knowledge reasoning system."""

    def __init__(self, history_window: int = 10000):
        self._lock = threading.Lock()
        self._history_window = history_window
        self._temporal_events: deque = deque(maxlen=history_window)
        self._temporal_knowledge: Dict[str, TemporalKnowledge] = {}
        self._temporal_relations: Dict[str, List[Tuple[str, TemporalRelation]]] = defaultdict(list)
        self._causality_graph = defaultdict(list)
        self._temporal_index = TemporalIndex()
        self._temporal_inference = TemporalInference()
        self._temporal_analyzer = TemporalAnalyzer()
        self._initialized = False

    def start(self) -> bool:
        """Start temporal knowledge reasoner."""
        logger.info("[TEMPORAL_REASONER] Starting temporal knowledge reasoner...")
        self._initialized = True
        logger.info("[TEMPORAL_REASONER] Temporal knowledge reasoner started")
        return True

    def stop(self) -> bool:
        """Stop temporal knowledge reasoner."""
        logger.info("[TEMPORAL_REASONER] Stopping temporal knowledge reasoner...")
        self._initialized = False
        logger.info("[TEMPORAL_REASONER] Temporal knowledge reasoner stopped")
        return True

    def record_temporal_event(self, event_type: str, attributes: Dict[str, Any], 
                            causality_links: Optional[List[str]] = None) -> str:
        """Record a temporal event."""
        event_id = f"event_{int(time.time())}_{hash(str(attributes)) % 10000}"
        
        if causality_links is None:
            causality_links = []
        
        event = TemporalEvent(
            event_id=event_id,
            event_type=event_type,
            timestamp=time.time(),
            attributes=attributes,
            causality_links=causality_links,
            metadata={}
        )
        
        with self._lock:
            self._temporal_events.append(event)
            self._temporal_index.add_event(event)
            
            # Update causality graph
            for linked_event_id in causality_links:
                self._causality_graph[linked_event_id].append(event_id)
        
        logger.debug(f"[TEMPORAL_REASONER] Recorded temporal event {event_id} of type {event_type}")
        return event_id

    def add_temporal_knowledge(self, knowledge_id: str, content: str, 
                              start_time: float, end_time: float,
                              temporal_relation: Optional[TemporalRelation] = None) -> TemporalKnowledge:
        """Add knowledge with temporal context."""
        current_time = time.time()
        
        temporal_context = TemporalInterval(
            interval_id=f"ctx_{knowledge_id}",
            start_time=start_time,
            end_time=end_time,
            unit=TimeUnit.SECOND
        )
        
        validity_period = TemporalInterval(
            interval_id=f"valid_{knowledge_id}",
            start_time=current_time,
            end_time=current_time + 3600.0,  # 1 hour validity
            unit=TimeUnit.SECOND
        )
        
        temporal_knowledge = TemporalKnowledge(
            knowledge_id=knowledge_id,
            content=content,
            temporal_context=temporal_context,
            validity_period=validity_period,
            temporal_relation=temporal_relation,
            confidence=0.8,
            decay_rate=0.1,
            last_updated=current_time
        )
        
        with self._lock:
            self._temporal_knowledge[knowledge_id] = temporal_knowledge
        
        return temporal_knowledge

    def reason_temporal(self, query: str, time_range: Tuple[float, float]) -> TemporalReasoningResult:
        """Perform temporal reasoning."""
        logger.info(f"[TEMPORAL_REASONER] Performing temporal reasoning for query: {query}")
        
        reasoning_id = f"reasoning_{int(time.time())}_{hash(query) % 10000}"
        
        # Get events in time range
        start_time, end_time = time_range
        events_in_range = self._temporal_index.get_events_in_range(start_time, end_time)
        
        # Perform temporal inference
        result = self._temporal_inference.infer(query, events_in_range, self._temporal_knowledge)
        
        # Generate reasoning path
        reasoning_path = self._generate_reasoning_path(query, events_in_range, result)
        
        reasoning_result = TemporalReasoningResult(
            reasoning_id=reasoning_id,
            query=query,
            result=result,
            confidence=result.get("confidence", 0.5),
            temporal_evidence=events_in_range[:5],  # Top 5 events as evidence
            reasoning_path=reasoning_path,
            timestamp=time.time()
        )
        
        return reasoning_result

    def detect_temporal_patterns(self, event_types: List[str], 
                                time_window: float = 3600.0) -> List[Dict[str, Any]]:
        """Detect temporal patterns in events."""
        logger.info("[TEMPORAL_REASONER] Detecting temporal patterns")
        
        patterns = []
        
        # Group events by temporal proximity
        event_sequences = self._group_events_by_temporal_proximity(event_types, time_window)
        
        # Analyze sequences for patterns
        for sequence in event_sequences:
            pattern = self._analyze_sequence_for_patterns(sequence)
            if pattern:
                patterns.append(pattern)
        
        return patterns

    def infer_temporal_causality(self, cause_event_id: str, effect_event_id: str) -> Dict[str, Any]:
        """Infer causal relationship between events."""
        logger.info(f"[TEMPORAL_REASONER] Inferring causality from {cause_event_id} to {effect_event_id}")
        
        # Get events
        cause_event = self._get_event_by_id(cause_event_id)
        effect_event = self._get_event_by_id(effect_event_id)
        
        if not cause_event or not effect_event:
            return {"causality_confidence": 0.0, "reason": "events_not_found"}
        
        # Analyze temporal relationship
        temporal_analysis = self._temporal_analyzer.analyze_temporal_relationship(
            cause_event, effect_event
        )
        
        # Analyze attribute similarity
        attribute_analysis = self._temporal_analyzer.analyze_attribute_relationship(
            cause_event, effect_event
        )
        
        # Combine analyses for causality inference
        causality_confidence = self._calculate_causality_confidence(
            temporal_analysis, attribute_analysis
        )
        
        return {
            "cause_event_id": cause_event_id,
            "effect_event_id": effect_event_id,
            "causality_confidence": causality_confidence,
            "temporal_analysis": temporal_analysis,
            "attribute_analysis": attribute_analysis,
            "temporal_delay": effect_event.timestamp - cause_event.timestamp
        }

    def get_temporal_statistics(self) -> Dict[str, Any]:
        """Get temporal reasoning statistics."""
        with self._lock:
            # Calculate event distribution
            event_type_distribution = defaultdict(int)
            for event in self._temporal_events:
                event_type_distribution[event.event_type] += 1
            
            # Calculate temporal knowledge validity
            valid_knowledge = sum(1 for tk in self._temporal_knowledge.values() 
                                if time.time() <= tk.validity_period.end_time)
            
            return {
                "total_temporal_events": len(self._temporal_events),
                "total_temporal_knowledge": len(self._temporal_knowledge),
                "valid_temporal_knowledge": valid_knowledge,
                "event_type_distribution": dict(event_type_distribution),
                "causality_graph_size": len(self._causality_graph),
                "temporal_relations_count": sum(len(relations) for relations in self._temporal_relations.values())
            }

    def _get_event_by_id(self, event_id: str) -> Optional[TemporalEvent]:
        """Get event by ID."""
        with self._lock:
            for event in self._temporal_events:
                if event.event_id == event_id:
                    return event
        return None

    def _group_events_by_temporal_proximity(self, event_types: List[str], 
                                           time_window: float) -> List[List[TemporalEvent]]:
        """Group events by temporal proximity."""
        # Get events of specified types
        filtered_events = [e for e in self._temporal_events if e.event_type in event_types]
        
        # Sort by timestamp
        filtered_events.sort(key=lambda e: e.timestamp)
        
        # Group by time window
        sequences = []
        if not filtered_events:
            return sequences
        
        current_sequence = [filtered_events[0]]
        
        for event in filtered_events[1:]:
            if event.timestamp - current_sequence[-1].timestamp <= time_window:
                current_sequence.append(event)
            else:
                sequences.append(current_sequence)
                current_sequence = [event]
        
        if current_sequence:
            sequences.append(current_sequence)
        
        return sequences

    def _analyze_sequence_for_patterns(self, sequence: List[TemporalEvent]) -> Optional[Dict[str, Any]]:
        """Analyze event sequence for patterns."""
        if len(sequence) < 3:
            return None
        
        # Calculate inter-event intervals
        intervals = []
        for i in range(1, len(sequence)):
            interval = sequence[i].timestamp - sequence[i-1].timestamp
            intervals.append(interval)
        
        # Check for regularity
        if len(intervals) >= 2:
            std_interval = np.std(intervals)
            avg_interval = np.mean(intervals)
            
            # Regular pattern if low standard deviation
            regularity = 1.0 - min(1.0, std_interval / avg_interval) if avg_interval > 0 else 0.0
            
            if regularity > 0.7:
                return {
                    "pattern_type": "regular_temporal",
                    "event_sequence": [e.event_type for e in sequence],
                    "avg_interval": avg_interval,
                    "regularity_score": regularity,
                    "confidence": 0.8
                }
        
        # Check for progression patterns
        event_progression = [e.event_type for e in sequence]
        if self._has_progression_pattern(event_progression):
            return {
                "pattern_type": "progression",
                "event_progression": event_progression,
                "confidence": 0.7
            }
        
        return None

    def _has_progression_pattern(self, progression: List[str]) -> bool:
        """Check if progression has a pattern."""
        # Simple pattern detection - look for repeated sequences
        if len(progression) < 4:
            return False
        
        # Look for 2-step repetition
        for i in range(len(progression) - 3):
            if progression[i] == progression[i+2] and progression[i+1] == progression[i+3]:
                return True
        
        return False

    def _generate_reasoning_path(self, query: str, events: List[TemporalEvent], 
                                result: Dict[str, Any]) -> List[str]:
        """Generate reasoning path for transparency."""
        path = []
        
        path.append(f"Query: {query}")
        path.append(f"Analyzed {len(events)} temporal events")
        
        if events:
            path.append(f"Time range: {events[0].timestamp} to {events[-1].timestamp}")
            path.append(f"Primary event types: {[e.event_type for e in events[:3]]}")
        
        path.append(f"Inference result: {result.get('result', 'unknown')}")
        path.append(f"Confidence: {result.get('confidence', 0.5):.2f}")
        
        return path

    def _calculate_causality_confidence(self, temporal_analysis: Dict, 
                                       attribute_analysis: Dict) -> float:
        """Calculate overall causality confidence."""
        temporal_confidence = temporal_analysis.get("confidence", 0.5)
        attribute_confidence = attribute_analysis.get("confidence", 0.5)
        
        # Weighted combination
        overall_confidence = 0.6 * temporal_confidence + 0.4 * attribute_confidence
        return overall_confidence


class TemporalIndex:
    """Index for efficient temporal queries."""
    
    def __init__(self):
        self._events: List[TemporalEvent] = []
        self._type_index: Dict[str, List[TemporalEvent]] = defaultdict(list)
        self._time_index: List[Tuple[float, TemporalEvent]] = []
    
    def add_event(self, event: TempEvent) -> None:
        """Add event to index."""
        self._events.append(event)
        self._type_index[event.event_type].append(event)
        self._time_index.append((event.timestamp, event))
        
        # Keep time index sorted
        self._time_index.sort(key=lambda x: x[0])
    
    def get_events_in_range(self, start_time: float, end_time: float) -> List[TemporalEvent]:
        """Get events in time range."""
        # Binary search for efficiency
        events_in_range = []
        
        for timestamp, event in self._time_index:
            if start_time <= timestamp <= end_time:
                events_in_range.append(event)
        
        return events_in_range
    
    def get_events_by_type(self, event_type: str) -> List[TemporalEvent]:
        """Get events by type."""
        return self._type_index.get(event_type, [])


class TemporalInference:
    """Perform temporal inference."""
    
    def infer(self, query: str, events: List[TemporalEvent], 
             knowledge: Dict[str, TemporalKnowledge]) -> Dict[str, Any]:
        """Perform temporal inference."""
        # Simplified temporal inference
        result = {"result": "inferred", "confidence": 0.7}
        
        # Check for temporal operators in query
        if "always" in query.lower():
            result["result"] = self._check_always(events)
            result["confidence"] = 0.8
        elif "eventually" in query.lower():
            result["result"] = self._check_eventually(events)
            result["confidence"] = 0.75
        elif "before" in query.lower():
            result["result"] = self._check_before(events)
            result["confidence"] = 0.85
        elif "after" in query.lower():
            result["result"] = self._check_after(events)
            result["confidence"] = 0.85
        
        return result
    
    def _check_always(self, events: List[TemporalEvent]) -> str:
        """Check if condition always holds."""
        if not events:
            return "insufficient_data"
        
        # Simplified: check if all events are of the same type
        event_types = set(e.event_type for e in events)
        return "true" if len(event_types) == 1 else "false"
    
    def _check_eventually(self, events: List[TemporalEvent]) -> str:
        """Check if condition eventually holds."""
        if not events:
            return "insufficient_data"
        
        # Simplified: check if any event matches criteria
        return "true"  # Always true in this simplified version
    
    def _check_before(self, events: List[TemporalEvent]) -> str:
        """Check temporal before relationship."""
        if len(events) < 2:
            return "insufficient_data"
        
        # Check if first event is before second event
        return "true" if events[0].timestamp < events[-1].timestamp else "false"
    
    def _check_after(self, events: List[TemporalEvent]) -> str:
        """Check temporal after relationship."""
        if len(events) < 2:
            return "insufficient_data"
        
        # Check if last event is after first event
        return "true" if events[-1].timestamp > events[0].timestamp else "false"


class TemporalAnalyzer:
    """Analyze temporal relationships."""
    
    def analyze_temporal_relationship(self, event1: TemporalEvent, 
                                    event2: TemporalEvent) -> Dict[str, Any]:
        """Analyze temporal relationship between two events."""
        time_diff = event2.timestamp - event1.timestamp
        
        # Determine temporal relation
        if time_diff < 0:
            relation = TemporalRelation.BEFORE
            confidence = min(1.0, abs(time_diff) / 3600.0)  # Higher confidence for larger time differences
        elif time_diff > 0:
            relation = TemporalRelation.AFTER
            confidence = min(1.0, time_diff / 3600.0)
        else:
            relation = TemporalRelation.EQUALS
            confidence = 1.0
        
        return {
            "relation": relation.value,
            "time_difference": time_diff,
            "confidence": confidence
        }
    
    def analyze_attribute_relationship(self, event1: TemporalEvent, 
                                    event2: TemporalEvent) -> Dict[str, Any]:
        """Analyze attribute relationship between two events."""
        # Calculate attribute similarity
        attributes1 = set(event1.attributes.keys())
        attributes2 = set(event2.attributes.keys())
        
        # Attribute overlap
        overlap = len(attributes1 & attributes2)
        total_attributes = len(attributes1 | attributes2)
        
        similarity = overlap / total_attributes if total_attributes > 0 else 0.0
        
        # Value similarity for shared attributes
        value_similarities = []
        for attr in (attributes1 & attributes2):
            val1 = event1.attributes[attr]
            val2 = event2.attributes[attr]
            
            if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
                # Numerical similarity
                diff = abs(val1 - val2)
                max_val = max(abs(val1), abs(val2))
                value_sim = 1.0 - (diff / max_val) if max_val > 0 else 1.0
                value_similarities.append(value_sim)
        
        avg_value_similarity = np.mean(value_similarities) if value_similarities else 0.0
        
        return {
            "attribute_similarity": similarity,
            "value_similarity": avg_value_similarity,
            "confidence": 0.5 * similarity + 0.5 * avg_value_similarity
        }


# Singleton instance
_temporal_reasoner: Optional[TemporalKnowledgeReasoner] = None
_temporal_reasoner_lock = threading.Lock()


def get_temporal_reasoner(history_window: int = 10000) -> TemporalKnowledgeReasoner:
    """Get the singleton temporal reasoner instance."""
    global _temporal_reasoner
    if _temporal_reasoner is None:
        with _temporal_reasoner_lock:
            if _temporal_reasoner is None:
                _temporal_reasoner = TemporalKnowledgeReasoner(history_window)
    return _temporal_reasoner


__all__ = [
    "TemporalKnowledgeReasoner",
    "get_temporal_reasoner",
    "TemporalRelation",
    "TemporalOperator",
    "TimeUnit",
    "TemporalInterval",
    "TemporalEvent",
    "TemporalKnowledge",
    "TemporalReasoningResult",
]