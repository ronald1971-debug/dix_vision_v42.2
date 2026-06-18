"""
INDIRA Edge Case Memory - Knowledge Layer Component  
Handles edge cases and exceptional market conditions with learning capabilities
Per Rule 6 of the DIX VISION Tier-0 Production Implementation Contract
"""

import logging
from typing import Dict, List, Set, Any, Optional, Tuple, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict

logger = logging.getLogger(__name__)

class EdgeCaseType(Enum):
    """Types of edge cases in market conditions"""
    EXTREME_VOLATILITY = "extreme_volatility"
    LIQUIDITY_CRISIS = "liquidity_crisis"
    FLASH_CRASH = "flash_crash"
    MARKET_MELTDOWN = "market_meltup"
    REGIME_SWITCH = "regime_switch"
    BLACK_SWAN_EVENT = "black_swan"
    ANOMALOUS_PATTERN = "anomalous_pattern"
    SYSTEM_OUTAGE = "system_outage"
    DATA_CORRUPTION = "data_corruption"

class EdgeCaseSeverity(Enum):
    """Severity levels for edge cases"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

@dataclass
class EdgeCaseRecord:
    """Record of an edge case event"""
    edge_case_id: str
    edge_case_type: EdgeCaseType
    severity: EdgeCaseSeverity
    trigger_conditions: Dict[str, Any]
    market_state: Dict[str, Any]
    timestamp: datetime
    resolution: Optional[str] = None
    outcome: Optional[str] = None
    lessons_learned: List[str] = field(default_factory=list)
    recurrence_count: int = 0
    prevention_strategies: List[str] = field(default_factory=list)

@dataclass
class EdgeCasePattern:
    """Pattern recognition for edge cases"""
    pattern_id: str
    pattern_type: EdgeCaseType
    precursors: List[str]
    confidence: float
    trigger_thresholds: Dict[str, float]
    historical_frequency: int
    last_occurrence: Optional[datetime] = None

class EdgeCaseMemory:
    """
    Memory system for edge cases and exceptional market conditions
    Enables learning from rare but critical events
    """
    
    def __init__(self):
        self._edge_case_records: Dict[str, EdgeCaseRecord] = {}
        self._pattern_recognition: Dict[str, EdgeCasePattern] = defaultdict(EdgeCasePattern)
        self._prevention_strategies: Dict[str, List[str]] = defaultdict(list)
        self._recurrence_tracking: Dict[EdgeCaseType, List[datetime]] = defaultdict(list)
        self._recovery_actions: Dict[str, Callable] = {}
        self._learning_confidence: Dict[str, float] = defaultdict(lambda: 0.5)
        
        # Define edge case patterns
        self._initialize_edge_case_patterns()
        
    def _initialize_edge_case_patterns(self) -> None:
        """Initialize known edge case patterns"""
        patterns = {
            "flash_crash_v3": EdgeCasePattern(
                pattern_id="flash_crash_v3",
                pattern_type=EdgeCaseType.FLASH_CRASH,
                precursors=["volume_spike", "order_imbalance", "price_momentum"],
                confidence=0.85,
                trigger_thresholds={
                    "volume_increase_ratio": 5.0,
                    "price_drop_percent": 10.0,
                    "time_window_seconds": 60
                },
                historical_frequency=3
            ),
            "liquidity_crisis_v2": EdgeCasePattern(
                pattern_id="liquidity_crisis_v2",
                pattern_type=EdgeCaseType.LIQUIDITY_CRISIS,
                precursors=["spread_widening", "depth_reduction", "volume_drop"],
                confidence=0.90,
                trigger_thresholds={
                    "spread_bps": 50,
                    "depth_reduction_percent": 80,
                    "volume_drop_percent": 50
                },
                historical_frequency=5
            ),
            "regime_switch_v1": EdgeCasePattern(
                pattern_id="regime_switch_v1",
                pattern_type=EdgeCaseType.REGIME_SWITCH,
                precursors=["correlation_breakdown", "volatility_structure_change", "trend_reversal"],
                confidence=0.75,
                trigger_thresholds={
                    "correlation_coefficient": 0.3,
                    "volatility_change_percent": 50,
                    "trend_reversal_strength": 2.0
                },
                historical_frequency=2
            )
        }
        
        for pattern_id, pattern in patterns.items():
            self._pattern_recognition[pattern_id] = pattern
    
    def record_edge_case(
        self,
        edge_case_type: EdgeCaseType,
        trigger_conditions: Dict[str, Any],
        market_state: Dict[str, Any],
        severity: EdgeCaseSeverity = EdgeCaseSeverity.WARNING
    ) -> str:
        """Record an edge case event"""
        edge_case_id = f"{edge_case_type.value}_{datetime.utcnow().timestamp()}:{datetime.utcnow().nanosecond()}"
        
        record = EdgeCaseRecord(
            edge_case_id=edge_case_id,
            edge_case_type=edge_case_type,
            severity=severity,
            trigger_conditions=trigger_conditions,
            market_state=market_state,
            timestamp=datetime.utcnow(),
            recurrence_count=len(self._recurrence_tracking[edge_case_type])
        )
        
        self._edge_case_records[edge_case_id] = record
        self._recurrence_tracking[edge_case_type].append(datetime.utcnow())
        
        # Check for pattern match
        self._detect_pattern_match(record)
        
        # Apply learned prevention strategies if available
        self._apply_prevention_strategies(record)
        
        logger.info(f"Recorded edge case: {edge_case_id} ({severity.value})")
        return edge_case_id
    
    def _detect_pattern_match(self, record: EdgeCaseRecord) -> Optional[str]:
        """Detect if the edge case matches a known pattern"""
        for pattern_id, pattern in self._pattern_recognition.items():
            if pattern.pattern_type == record.edge_case_type:
                # Check if precursors match trigger thresholds
                if self._check_precursor_thresholds(record.trigger_conditions, pattern.trigger_thresholds):
                    self._learning_confidence[pattern_id] = min(1.0, self._learning_confidence[pattern_id] + 0.1)
                    pattern.last_occurrence = datetime.utcnow()
                    pattern.historical_frequency += 1
                    return pattern_id
        return None
    
    def _check_precursor_thresholds(self, conditions: Dict[str, Any], thresholds: Dict[str, float]) -> bool:
        """Check if trigger conditions meet pattern thresholds"""
        for key, threshold in thresholds.items():
            if key not in conditions:
                continue
            try:
                value = float(conditions[key])
                if isinstance(threshold, dict):
                    # Handle nested threshold checks
                    if key == "time_window_seconds" and key in conditions:
                        return True
                elif isinstance(value, (int, float)):
                    if isinstance(threshold, (int, float)):
                        return abs(value - threshold) < threshold * 0.1  # 10% tolerance
            except (TypeError, ValueError):
                continue
        return False
    
    def _apply_prevention_strategies(self, record: EdgeCaseRecord) -> None:
        """Apply learned prevention strategies for similar edge cases"""
        pattern_id = f"{record.edge_case_type.value}_prevention"
        strategies = self._prevention_strategies[pattern_id]
        
        if strategies:
            for strategy in strategies:
                try:
                    recovery_action = self._recovery_actions.get(strategy)
                    if recovery_action:
                        recovery_action(record)
                        record.lessons_learned.append(f"Applied prevention strategy: {strategy}")
                except Exception as e:
                    logger.error(f"Failed to apply prevention strategy {strategy}: {e}")
    
    def resolve_edge_case(
        self,
        edge_case_id: str,
        resolution: str,
        outcome: str,
        lessons: Optional[List[str]] = None
    ) -> None:
        """Resolve an edge case with lessons learned"""
        if edge_case_id not in self._edge_case_records:
            return
        
        record = self._edge_case_records[edge_case_id]
        record.resolution = resolution
        record.outcome = outcome
        
        if lessons:
            record.lessons_learned.extend(lessons)
        
        # Extract and store prevention strategies
        prevention_strategies = self._extract_prevention_strategies(record)
        for strategy in prevention_strategies:
            pattern_id = f"{record.edge_case_type.value}_prevention"
            self._prevention_strategies[pattern_id].append(strategy)
        
        logger.info(f"Resolved edge case {edge_case_id}: {outcome}")
    
    def _extract_prevention_strategies(self, record: EdgeCaseRecord) -> List[str]:
        """Extract prevention strategies from edge case resolution"""
        strategies = []
        
        # Analyze trigger conditions and outcome
        if record.outcome == "successful":
            if "volume_spike" in str(record.trigger_conditions):
                strategies.append("Monitor volume surges for similar events")
            if "price_momentum" in str(record.trigger_conditions):
                strategies.append("Implement circuit breakers for momentum crashes")
            if "spread_widening" in str(record.trigger_conditions):
                strategies.append("Pre-position liquidity during spread stress")
        
        return strategies
    
    def get_edge_case_by_type(self, edge_case_type: EdgeCaseType) -> List[EdgeCaseRecord]:
        """Get all edge cases of a specific type"""
        return [
            record for record in self._edge_case_records.values()
            if record.edge_case_type == edge_case_type
        ]
    
    def get_edge_case_by_severity(self, severity: EdgeCaseSeverity) -> List[EdgeCaseRecord]:
        """Get all edge cases of a specific severity"""
        return [
            record for record in self._edge_case_records.values()
            if record.severity == severity
        ]
    
    def get_recurring_edge_cases(self, threshold: int = 3) -> List[EdgeCaseType]:
        """Get edge case types that have occurred frequently"""
        recurring = []
        for edge_case_type, occurrences in self._recurrence_tracking.items():
            if len(occurrences) >= threshold:
                recurring.append(edge_case_type)
        return recurring
    
    def get_learning_summary(self) -> Dict[str, Any]:
        """Get summary of learning from edge cases"""
        total_records = len(self._edge_case_records)
        resolved_count = sum(1 for r in self._edge_case_records.values() if r.resolution)
        
        pattern_performance = {}
        for pattern_id, pattern in self._pattern_recognition.items():
            pattern_performance[pattern_id] = {
                "confidence": self._learning_confidence[pattern_id],
                "frequency": pattern.historical_frequency,
                "last_occurrence": pattern.last_occurrence.isoformat() if pattern.last_occurrence else None
            }
        
        return {
            "total_edge_cases": total_records,
            "resolved_cases": resolved_count,
            "resolution_rate": resolved_count / total_records if total_records > 0 else 0,
            "pattern_recognition_performance": pattern_performance,
            "total_prevention_strategies": sum(len(strategies) for strategies in self._prevention_strategies.values()),
            "edge_case_types_with_recurrence": len([t for t, occ in self._recurrence_tracking.items() if len(occ) >= 3]),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def register_recovery_action(self, action_name: str, action: Callable) -> None:
        """Register a recovery action for edge cases"""
        self._recovery_actions[action_name] = action
        logger.info(f"Registered recovery action: {action_name}")
    
    def get_prevention_strategies(self, edge_case_type: EdgeCaseType) -> List[str]:
        """Get all learned prevention strategies for an edge case type"""
        pattern_id = f"{edge_case_type.value}_prevention"
        return list(self._prevention_strategies.get(pattern_id, []))
    
    def cleanup_old_records(self, older_than_days: int = 30) -> int:
        """Clean up old edge case records"""
        cutoff = datetime.utcnow() - timedelta(days=older_than_days)
        records_to_remove = []
        
        for edge_case_id, record in self._edge_case_records.items():
            if record.timestamp < cutoff and record.resolution:
                records_to_remove.append(edge_case_id)
        
        for edge_case_id in records_to_remove:
            del self._edge_case_records[edge_case_id]
        
        logger.info(f"Cleaned up {len(records_to_remove)} old edge case records")
        return len(records_to_remove)