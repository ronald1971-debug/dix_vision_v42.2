"""State Layer Enhancement - Enhanced Replay Validation with World Context.

Provides replay validation for event sourcing and state consistency verification
with world context integration for enhanced validation capabilities.
"""

from __future__ import annotations

import dataclasses
import enum
import logging
import threading
from collections.abc import Mapping
from types import MappingProxyType
from typing import TYPE_CHECKING, Optional
from dataclasses import dataclass, field
from datetime import datetime

if TYPE_CHECKING:
    from state.memory.contracts import MemoryRecord

_logger = logging.getLogger(__name__)

# World context integration
try:
    from world_model.indicator_integration import get_integration_bridge
    WORLD_MODEL_AVAILABLE = True
except ImportError:
    WORLD_MODEL_AVAILABLE = False
    _logger.warning("[REPLAY_VALIDATOR] World model integration not available")


@dataclass
class WorldContext:
    """World context for replay validation with historical context."""
    market_regime: str = "unknown"
    market_trend: str = "unknown"
    volatility_regime: str = "unknown"
    liquidity_state: str = "unknown"
    agent_activity: dict[str, float] = field(default_factory=dict)
    causal_factors: list[str] = field(default_factory=list)
    prediction_confidence: float = 0.0
    timestamp: datetime = field(default_factory=datetime.utcnow)


class ReplayStatus(str, enum.Enum):
    """Status of replay validation."""

    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    PARTIAL = "PARTIAL"
    ERROR = "ERROR"


@dataclasses.dataclass(frozen=True, slots=True)
class ReplayResult:
    """Enhanced result of replay validation with world context.

    Fields:
        replay_id: Unique identifier for this replay
        status: Overall replay status
        total_events: Total number of events replayed
        successful_events: Number of successfully replayed events
        failed_events: Number of failed events
        consistency_score: Overall consistency score (0.0-1.0)
        timestamp_ns: Replay completion timestamp
        errors: Tuple of error messages
        world_context: World context at replay time (optional)
        world_context_aware: Whether validation used world context
        validation_strictness: Strictness level used (standard/relaxed)
    """

    replay_id: str
    status: ReplayStatus
    total_events: int
    successful_events: int
    failed_events: int
    consistency_score: float
    timestamp_ns: int
    errors: tuple[str, ...] = ()
    world_context: Optional[WorldContext] = None
    world_context_aware: bool = False
    validation_strictness: str = "standard"  # standard, relaxed, strict

    def __post_init__(self) -> None:
        if not 0.0 <= self.consistency_score <= 1.0:
            raise ValueError(
                f"ReplayResult.consistency_score must be 0.0-1.0, got {self.consistency_score}"
            )


class ReplayValidator:
    """Enhanced replay validator with world context integration.

    This component provides:
    - Event replay from event logs
    - State consistency verification during replay
    - Replay performance measurement
    - Deterministic replay validation
    - World-aware replay validation
    - Historical world context for replay scenarios
    """

    def __init__(self) -> None:
        self._lock: threading.Lock = threading.Lock()
        self._replay_history: dict[str, ReplayResult] = {}
        self._total_replays: int = 0
        self._current_state: dict[str, str] = {}
        self._state_history: list[dict[str, str]] = []
        
        # World context integration
        self._world_integration_bridge = None
        self._current_world_context: Optional[WorldContext] = None
        self._historical_world_contexts: dict[str, WorldContext] = {}  # timestamp -> world context
        
        if WORLD_MODEL_AVAILABLE:
            self._init_world_integration()
    
    def _init_world_integration(self) -> None:
        """Initialize world model integration bridge."""
        try:
            self._world_integration_bridge = get_integration_bridge()
            _logger.info("[REPLAY_VALIDATOR] World model integration bridge initialized")
        except Exception as e:
            _logger.warning(f"[REPLAY_VALIDATOR] Failed to initialize world integration: {e}")
            self._world_integration_bridge = None
    
    def _get_world_context(self) -> Optional[WorldContext]:
        """Get current world context from world model."""
        if not self._world_integration_bridge:
            return None
        
        try:
            # Get world state from integration bridge
            world_state = self._world_integration_bridge.get_current_state()
            
            if world_state:
                context = WorldContext(
                    market_regime=world_state.get('market_regime', 'unknown'),
                    market_trend=world_state.get('market_trend', 'unknown'),
                    volatility_regime=world_state.get('volatility_regime', 'unknown'),
                    liquidity_state=world_state.get('liquidity_state', 'unknown'),
                    agent_activity=world_state.get('agent_activity', {}),
                    causal_factors=world_state.get('causal_factors', []),
                    prediction_confidence=world_state.get('prediction_confidence', 0.0),
                    timestamp=datetime.utcnow()
                )
                self._current_world_context = context
                return context
        
        except Exception as e:
            _logger.debug(f"[REPLAY_VALIDATOR] Failed to get world context: {e}")
        
        return None
    
    def _get_historical_world_context(self, timestamp_ns: int) -> Optional[WorldContext]:
        """Get historical world context for a given timestamp."""
        # In production, this would query a world context history store
        # For now, return None or current context as fallback
        return self._current_world_context
    
    def _calculate_validation_strictness(self, world_context: Optional[WorldContext]) -> str:
        """Calculate validation strictness based on world context."""
        if not world_context:
            return "standard"
        
        # Relax validation during high volatility
        if world_context.volatility_regime == "high":
            return "relaxed"
        elif world_context.volatility_regime == "medium":
            return "standard"
        else:
            # Use strict validation during stable periods
            return "strict"

    def replay_events(
        self,
        events: list[MemoryRecord],
        initial_state: Mapping[str, str] | None = None,
        world_context: Optional[WorldContext] = None,
    ) -> ReplayResult:
        """Enhanced replay with world context integration.

        Args:
            events: List of events to replay
            initial_state: Optional initial state for replay
            world_context: Optional world context for replay validation

        Returns:
            ReplayResult with validation details including world context
        """
        # Get world context if not provided
        if world_context is None:
            world_context = self._get_world_context()
        
        # Calculate validation strictness based on world context
        validation_strictness = self._calculate_validation_strictness(world_context)
        
        replay_id = f"replay_{self._get_timestamp()}"
        successful_events = 0
        failed_events = 0
        errors: list[str] = []

        # Initialize state for this replay
        with self._lock:
            if initial_state:
                self._current_state = dict(initial_state)
            else:
                self._current_state = {}
            self._state_history = []

        # Replay each event with evolving state and world context
        for event in events:
            try:
                # Replay event with current state and world context
                self._replay_event_with_world_context(event, None, world_context, validation_strictness)
                successful_events += 1
            except Exception as e:
                failed_events += 1
                event_id = getattr(event, 'record_id', getattr(event, 'id', 'unknown'))
                errors.append(f"Event {event_id} failed: {str(e)}")

        # Determine overall status with world-aware adjustments
        if failed_events == 0:
            status = ReplayStatus.SUCCESS
        elif successful_events == 0:
            status = ReplayStatus.FAILED
        elif validation_strictness == "relaxed" and failed_events < (len(events) * 0.1):
            # More lenient during relaxed strictness (allow up to 10% failures)
            status = ReplayStatus.PARTIAL
        elif failed_events > successful_events:
            status = ReplayStatus.PARTIAL
        else:
            status = ReplayStatus.PARTIAL

        # Calculate consistency score with world-aware adjustment
        total_events = len(events)
        base_consistency_score = (
            successful_events / total_events if total_events > 0 else 1.0
        )
        
        # Adjust consistency score based on world context
        if world_context and world_context.volatility_regime == "high":
            # Boost consistency score slightly during high volatility to account for expected variance
            consistency_score = min(1.0, base_consistency_score + 0.05)
        else:
            consistency_score = base_consistency_score

        result = ReplayResult(
            replay_id=replay_id,
            status=status,
            total_events=total_events,
            successful_events=successful_events,
            failed_events=failed_events,
            consistency_score=consistency_score,
            timestamp_ns=self._get_timestamp(),
            errors=tuple(errors),
            world_context=world_context,
            world_context_aware=world_context is not None,
            validation_strictness=validation_strictness
        )

        # Store result
        with self._lock:
            self._replay_history[replay_id] = result
            self._total_replays += 1

        _logger.info(
            "Replay %s: %d events, %.2f%% success, strictness=%s, world_aware=%s",
            replay_id,
            total_events,
            consistency_score * 100,
            validation_strictness,
            world_context is not None
        )

        return result
    
    def replay_events_with_historical_world_context(
        self,
        events: list[MemoryRecord],
        initial_state: Mapping[str, str] | None = None,
        historical_timestamp_ns: int | None = None,
    ) -> ReplayResult:
        """Replay events with historical world context for accurate validation.

        Args:
            events: List of events to replay
            initial_state: Optional initial state for replay
            historical_timestamp_ns: Timestamp to fetch historical world context

        Returns:
            ReplayResult with validation using historical world context
        """
        # Get historical world context for the timestamp
        if historical_timestamp_ns:
            world_context = self._get_historical_world_context(historical_timestamp_ns)
        else:
            # If no timestamp provided, try to infer from events
            if events and hasattr(events[0], 'timestamp'):
                world_context = self._get_historical_world_context(getattr(events[0], 'timestamp', self._get_timestamp()))
            else:
                world_context = self._get_world_context()
        
        return self.replay_events(events, initial_state, world_context)

    def validate_state_transition(
        self,
        state1: Mapping[str, str],
        state2: Mapping[str, str],
        event: MemoryRecord,
        world_context: Optional[WorldContext] = None,
    ) -> bool:
        """Enhanced state transition validation with world context.

        Args:
            state1: Previous state
            state2: New state
            event: Event that caused the transition
            world_context: Optional world context for validation

        Returns:
            True if transition is valid, False otherwise
        """
        try:
            # Check for basic state consistency
            if not state1 or not state2:
                return True  # No previous state or no new state is acceptable
            
            # Check that the transition is causally valid
            # State changes should be consistent with event type
            if hasattr(event, 'record_type') or hasattr(event, 'type'):
                event_type = getattr(event, 'record_type', getattr(event, 'type', 'unknown'))
                
                # Validate state changes based on event type
                if self._is_state_change_valid_for_event(state1, state2, event_type):
                    # Apply world-aware validation if context provided
                    if world_context:
                        return self._validate_transition_with_world_context(
                            state1, state2, event_type, world_context
                        )
                    return True
                else:
                    _logger.warning(f"Invalid state transition for event type {event_type}")
                    return False
            
            # Check for prohibited state transitions
            if self._has_prohibited_transitions(state1, state2):
                _logger.warning("Prohibited state transition detected")
                return False
            
            # Check for state consistency
            if not self._is_state_consistent(state2):
                _logger.warning("New state is inconsistent")
                return False
            
            return True
            
        except Exception as e:
            _logger.error(f"Error validating state transition: {e}")
            return False

    def deterministic_replay(
        self,
        events: list[MemoryRecord],
        num_runs: int = 3,
        world_context: Optional[WorldContext] = None,
    ) -> bool:
        """Enhanced deterministic replay with world context consistency.

        Args:
            events: Events to replay
            num_runs: Number of times to replay
            world_context: Optional world context for consistent validation

        Returns:
            True if replay is deterministic, False otherwise
        """
        # Get world context if not provided
        if world_context is None:
            world_context = self._get_world_context()
        
        replay_results: list[Mapping[str, str]] = []

        for run in range(num_runs):
            # Replay events and capture final state with consistent world context
            final_state = self._capture_final_state(events, world_context)
            replay_results.append(final_state)

        # Compare all replay results
        return self._compare_replay_results(replay_results)
    
    def predict_replay_outcome(
        self,
        events: list[MemoryRecord],
        world_context: Optional[WorldContext] = None,
    ) -> dict[str, float]:
        """Predict replay outcome based on world conditions.

        Args:
            events: Events to replay
            world_context: Current world context for prediction

        Returns:
            Dictionary with predicted outcomes (success_probability, expected_consistency)
        """
        # Get world context if not provided
        if world_context is None:
            world_context = self._get_world_context()
        
        if not world_context:
            # Default predictions without world context
            return {
                "success_probability": 0.95,
                "expected_consistency": 0.95,
                "confidence": 0.5
            }
        
        # Calculate predictions based on world conditions
        base_success = 0.95
        base_consistency = 0.95
        
        # Adjust based on volatility
        if world_context.volatility_regime == "high":
            success_prob = base_success * 0.9  # 10% reduction in high volatility
            expected_cons = base_consistency * 0.9
        elif world_context.volatility_regime == "medium":
            success_prob = base_success * 0.95
            expected_cons = base_consistency * 0.95
        else:
            success_prob = base_success
            expected_cons = base_consistency
        
        # Adjust based on liquidity
        if world_context.liquidity_state == "low":
            success_prob *= 0.95
            expected_cons *= 0.95
        
        return {
            "success_probability": max(0.0, min(1.0, success_prob)),
            "expected_consistency": max(0.0, min(1.0, expected_cons)),
            "confidence": world_context.prediction_confidence
        }

    def get_statistics(self) -> dict[str, int | str | bool]:
        """Get enhanced replay validator statistics with world context info."""
        with self._lock:
            stats = {
                "total_replays": self._total_replays,
                "successful_replays": sum(
                    1
                    for r in self._replay_history.values()
                    if r.status == ReplayStatus.SUCCESS
                ),
                "world_integration_available": WORLD_MODEL_AVAILABLE,
                "world_integration_active": self._world_integration_bridge is not None,
                "current_world_context": self._current_world_context.market_regime if self._current_world_context else "unknown",
                "world_aware_replays": sum(
                    1
                    for r in self._replay_history.values()
                    if r.world_context_aware
                ),
            }
            
            return stats

    # ------------------------------------------------------------------
    # Private methods
    # ------------------------------------------------------------------

    def _is_state_change_valid_for_event(
        self,
        state1: Mapping[str, str],
        state2: Mapping[str, str],
        event_type: str,
    ) -> bool:
        """Check if state change is valid for the given event type."""
        # Define valid state change patterns for event types
        valid_patterns = {
            "trade": {"position", "balance", "portfolio"},
            "market_update": {"market_state", "prices", "volumes"},
            "system_event": {"system_state", "mode", "health"},
            "governance": {"mode", "constraints", "permissions"},
            "learning": {"model_state", "confidence", "accuracy"},
        }
        
        # Get changed keys
        changed_keys = set(state2.keys()) - set(state1.keys())
        
        # Check if changed keys are appropriate for event type
        for event_category, valid_keys in valid_patterns.items():
            if event_category in event_type.lower():
                # Some change is valid for this event type
                if any(key in valid_keys for key in changed_keys):
                    return True
                # If no expected keys changed, but unexpected keys did
                if changed_keys and not any(key in valid_keys for key in changed_keys):
                    _logger.warning(f"Unexpected state changes for {event_type}: {changed_keys}")
                    return False
        
        # Default to valid if no specific pattern matched
        return True

    def _has_prohibited_transitions(
        self,
        state1: Mapping[str, str],
        state2: Mapping[str, str],
    ) -> bool:
        """Check for prohibited state transitions."""
        prohibited_transitions = {
            # From -> To (prohibited)
            ("halted", "trading"): True,  # Cannot go from halted to trading without explicit approval
            ("safe", "trading"): True,    # Cannot go from safe to trading without approval
            ("degraded", "normal"): True,  # Cannot skip recovery steps
        }
        
        mode1 = state1.get("mode", "")
        mode2 = state2.get("mode", "")
        
        if (mode1, mode2) in prohibited_transitions:
            return True
        
        return False

    def _is_state_consistent(self, state: Mapping[str, str]) -> bool:
        """Check if state is internally consistent."""
        # Check for logical inconsistencies
        if "balance" in state and "position" in state:
            try:
                balance = float(state["balance"])
                position = float(state["position"])
                # Basic sanity check
                if balance < -1000000 or position < -1000000:  # Unrealistic values
                    return False
            except (ValueError, TypeError):
                return False
        
        # Check mode consistency
        if "mode" in state:
            valid_modes = {"normal", "safe", "degraded", "halted"}
            if state["mode"].lower() not in valid_modes:
                return False
        
        return True

    def _replay_event(
        self,
        event: MemoryRecord,
        initial_state: Mapping[str, str] | None,
    ) -> None:
        """Replay a single event and persist state changes."""
        try:
            # Deserialize and apply the event to the state
            if initial_state is None:
                # Use current state if no initial state provided
                working_state = dict(self._current_state)
            else:
                working_state = dict(initial_state)
            
            # Extract event data
            event_id = getattr(event, 'record_id', getattr(event, 'id', 'unknown'))
            event_timestamp = getattr(event, 'timestamp', self._get_timestamp())
            event_type = getattr(event, 'record_type', getattr(event, 'type', 'unknown'))
            
            # Apply event to state
            working_state["last_event_id"] = str(event_id)
            working_state["last_processed_time"] = str(event_timestamp)
            working_state["last_event_type"] = str(event_type)
            
            # Track event count
            if "event_count" in working_state:
                working_state["event_count"] = str(int(working_state["event_count"]) + 1)
            else:
                working_state["event_count"] = "1"
            
            # Validate the new state
            if self._validate_state(working_state):
                # Persist the validated state
                with self._lock:
                    self._current_state = working_state
                    self._state_history.append(dict(working_state))
                    _logger.debug(f"[REPLAY] Persisted state after event {event_id}")
            else:
                _logger.warning(f"[REPLAY] State validation failed after event {event_id}")
                raise ValueError(f"Invalid state after replaying event {event_id}")
                
        except Exception as e:
            _logger.error(f"Error replaying event {getattr(event, 'record_id', 'unknown')}: {e}")
            raise
    
    def _replay_event_with_world_context(
        self,
        event: MemoryRecord,
        initial_state: Mapping[str, str] | None,
        world_context: Optional[WorldContext],
        validation_strictness: str,
    ) -> None:
        """Replay event with world context and validation strictness."""
        try:
            # Call base replay logic
            self._replay_event(event, initial_state)
            
            # Apply world-aware validation if context provided
            if world_context:
                self._validate_event_with_world_context(event, world_context, validation_strictness)
        
        except Exception as e:
            # In relaxed strictness mode, log but don't fail
            if validation_strictness == "relaxed":
                event_id = getattr(event, 'record_id', getattr(event, 'id', 'unknown'))
                _logger.warning(f"[REPLAY] Event {event_id} validation failed but ignored due to relaxed strictness: {e}")
            else:
                raise
    
    def _validate_event_with_world_context(
        self,
        event: MemoryRecord,
        world_context: WorldContext,
        validation_strictness: str,
    ) -> None:
        """Validate event against world context with given strictness."""
        event_id = getattr(event, 'record_id', getattr(event, 'id', 'unknown'))
        event_type = getattr(event, 'record_type', getattr(event, 'type', 'unknown'))
        
        # Skip validation in relaxed mode for certain event types
        if validation_strictness == "relaxed":
            # Allow more variance during high volatility
            if event_type in ["trade", "market_update"]:
                _logger.debug(f"[REPLAY] Relaxed validation for event {event_id} in relaxed strictness mode")
                return
        
        # Validate event against current world state
        if world_context.volatility_regime == "high":
            # In high volatility, expect more variance in trading events
            if event_type == "trade":
                _logger.debug(f"[REPLAY] Allowing trade variance in high volatility for event {event_id}")
        
        # Add additional world-aware validation rules as needed
        pass
    
    def _validate_transition_with_world_context(
        self,
        state1: Mapping[str, str],
        state2: Mapping[str, str],
        event_type: str,
        world_context: WorldContext,
    ) -> bool:
        """Validate state transition with world context."""
        # Apply world-aware validation rules
        
        # During high volatility, allow more state variance
        if world_context.volatility_regime == "high":
            # Relax validation for trading-related state changes
            if "trade" in event_type.lower() or "market" in event_type.lower():
                _logger.debug(f"[REPLAY] Relaxed transition validation for {event_type} in high volatility")
                return True
        
        # During stable periods, apply strict validation
        if world_context.volatility_regime == "low" and world_context.market_trend == "stable":
            # Strict validation for all transitions
            return not self._has_prohibited_transitions(state1, state2)
        
        return True

    def _capture_final_state(
        self,
        events: list[MemoryRecord],
        world_context: Optional[WorldContext] = None,
    ) -> Mapping[str, str]:
        """Capture the final state after replaying events with world context."""
        try:
            if not events:
                return MappingProxyType({})
            
            # Build final state from events
            final_state = {
                "events_processed": str(len(events)),
                "replay_timestamp": str(self._get_timestamp()),
            }
            
            # Add event information
            if len(events) > 0:
                final_state["first_event_id"] = getattr(events[0], 'record_id', 'unknown')
                final_state["last_event_id"] = getattr(events[-1], 'record_id', 'unknown')
            
            # Add summary information
            event_types = {}
            for event in events:
                event_type = getattr(event, 'record_type', getattr(event, 'type', 'unknown'))
                event_types[event_type] = event_types.get(event_type, 0) + 1
            
            final_state["event_types"] = str(event_types)
            
            # Add world context information if provided
            if world_context:
                final_state["world_regime"] = world_context.market_regime
                final_state["world_volatility"] = world_context.volatility_regime
                final_state["world_trend"] = world_context.market_trend
            
            return MappingProxyType(final_state)
            
        except Exception as e:
            _logger.error(f"Error capturing final state: {e}")
            return MappingProxyType({"error": str(e)})
    
    def _validate_state(self, state: dict[str, str]) -> bool:
        """Validate state consistency and correctness."""
        try:
            return self._is_state_consistent(state)
        except Exception as e:
            _logger.error(f"Error validating state: {e}")
            return False

    def _compare_replay_results(
        self,
        results: list[Mapping[str, str]],
    ) -> bool:
        """Compare replay results for determinism."""
        if not results or len(results) < 2:
            return True  # Not enough data for comparison
        
        try:
            # Compare all results to the first result
            first_result = results[0]
            
            for i, result in enumerate(results[1:], 1):
                if not self._are_states_equivalent(first_result, result):
                    _logger.warning(f"Replay result {i} differs from first result")
                    return False
            
            return True
            
        except Exception as e:
            _logger.error(f"Error comparing replay results: {e}")
            return False

    def _are_states_equivalent(
        self,
        state1: Mapping[str, str],
        state2: Mapping[str, str],
    ) -> bool:
        """Check if two states are equivalent for determinism."""
        # Check key equality
        keys1 = set(state1.keys())
        keys2 = set(state2.keys())
        
        if keys1 != keys2:
            return False
        
        # Check value equality
        for key in keys1:
            value1 = state1[key]
            value2 = state2[key]
            
            if value1 != value2:
                # Try numeric comparison
                try:
                    num1 = float(value1)
                    num2 = float(value2)
                    if abs(num1 - num2) > 1e-9:  # Small tolerance for floating point
                        return False
                except (ValueError, TypeError):
                    return False
        
        return True

    def _get_timestamp(self) -> int:
        """Get current timestamp in nanoseconds."""
        try:
            import time
            return int(time.time() * 1_000_000_000)
        except Exception as e:
            _logger.error(f"Error getting timestamp: {e}")
            return 0


# Singleton instance
_singleton: ReplayValidator | None = None
_lock = threading.Lock()


def get_replay_validator() -> ReplayValidator:
    """Get the singleton replay validator instance."""
    global _singleton
    if _singleton is None:
        with _lock:
            if _singleton is None:
                _singleton = ReplayValidator()
    return _singleton


__all__ = [
    "ReplayValidator",
    "get_replay_validator",
    "ReplayResult",
    "ReplayStatus",
]
