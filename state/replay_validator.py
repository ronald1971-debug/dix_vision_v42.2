"""State Layer Enhancement - Replay Validation.

Provides replay validation for event sourcing and state consistency verification.
"""

from __future__ import annotations

import dataclasses
import enum
import logging
import threading
from collections.abc import Mapping
from types import MappingProxyType
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from state.memory.contracts import MemoryRecord

_logger = logging.getLogger(__name__)


class ReplayStatus(str, enum.Enum):
    """Status of replay validation."""

    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    PARTIAL = "PARTIAL"
    ERROR = "ERROR"


@dataclasses.dataclass(frozen=True, slots=True)
class ReplayResult:
    """Result of replay validation.

    Fields:
        replay_id: Unique identifier for this replay
        status: Overall replay status
        total_events: Total number of events replayed
        successful_events: Number of successfully replayed events
        failed_events: Number of failed events
        consistency_score: Overall consistency score (0.0-1.0)
        timestamp_ns: Replay completion timestamp
        errors: Tuple of error messages
    """

    replay_id: str
    status: ReplayStatus
    total_events: int
    successful_events: int
    failed_events: int
    consistency_score: float
    timestamp_ns: int
    errors: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not 0.0 <= self.consistency_score <= 1.0:
            raise ValueError(
                f"ReplayResult.consistency_score must be 0.0-1.0, got {self.consistency_score}"
            )


class ReplayValidator:
    """Validates event replay for state consistency.

    This component provides:
    - Event replay from event logs
    - State consistency verification during replay
    - Replay performance measurement
    - Deterministic replay validation
    """

    def __init__(self) -> None:
        self._lock: threading.Lock = threading.Lock()
        self._replay_history: dict[str, ReplayResult] = {}
        self._total_replays: int = 0
        self._current_state: dict[str, str] = {}
        self._state_history: list[dict[str, str]] = []

    def replay_events(
        self,
        events: list[MemoryRecord],
        initial_state: Mapping[str, str] | None = None,
    ) -> ReplayResult:
        """Replay events and validate state consistency.

        Args:
            events: List of events to replay
            initial_state: Optional initial state for replay

        Returns:
            ReplayResult with validation details
        """
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

        # Replay each event with evolving state
        for event in events:
            try:
                # Replay event with current state (not initial state)
                self._replay_event(event, None)  # None means use current state
                successful_events += 1
            except Exception as e:
                failed_events += 1
                event_id = getattr(event, 'record_id', getattr(event, 'id', 'unknown'))
                errors.append(f"Event {event_id} failed: {str(e)}")

        # Determine overall status
        if failed_events == 0:
            status = ReplayStatus.SUCCESS
        elif successful_events == 0:
            status = ReplayStatus.FAILED
        elif failed_events > successful_events:
            status = ReplayStatus.PARTIAL
        else:
            status = ReplayStatus.PARTIAL

        # Calculate consistency score
        total_events = len(events)
        consistency_score = (
            successful_events / total_events if total_events > 0 else 1.0
        )

        result = ReplayResult(
            replay_id=replay_id,
            status=status,
            total_events=total_events,
            successful_events=successful_events,
            failed_events=failed_events,
            consistency_score=consistency_score,
            timestamp_ns=self._get_timestamp(),
            errors=tuple(errors),
        )

        # Store result
        with self._lock:
            self._replay_history[replay_id] = result
            self._total_replays += 1

        _logger.info(
            "Replay %s: %d events, %.2f%% success",
            replay_id,
            total_events,
            consistency_score * 100,
        )

        return result

    def validate_state_transition(
        self,
        state1: Mapping[str, str],
        state2: Mapping[str, str],
        event: MemoryRecord,
    ) -> bool:
        """Validate a state transition given an event.

        Args:
            state1: Previous state
            state2: New state
            event: Event that caused the transition

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
    ) -> bool:
        """Verify deterministic replay (same events produce same state).

        Args:
            events: Events to replay
            num_runs: Number of times to replay

        Returns:
            True if replay is deterministic, False otherwise
        """
        replay_results: list[Mapping[str, str]] = []

        for run in range(num_runs):
            # Replay events and capture final state
            final_state = self._capture_final_state(events)
            replay_results.append(final_state)

        # Compare all replay results
        return self._compare_replay_results(replay_results)

    def get_statistics(self) -> dict[str, int]:
        """Get replay validator statistics."""
        with self._lock:
            return {
                "total_replays": self._total_replays,
                "successful_replays": sum(
                    1
                    for r in self._replay_history.values()
                    if r.status == ReplayStatus.SUCCESS
                ),
            }

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

    def _capture_final_state(
        self,
        events: list[MemoryRecord],
    ) -> Mapping[str, str]:
        """Capture the final state after replaying events."""
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
            
            return MappingProxyType(final_state)
            
        except Exception as e:
            _logger.error(f"Error capturing final state: {e}")
            return MappingProxyType({"error": str(e)})

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
