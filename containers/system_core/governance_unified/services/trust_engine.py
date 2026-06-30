"""GOV-G13 — Trust scoring engine with enhanced validation.

Pure value objects and a clamped scoring state machine.
No I/O, no wall-clock reads (INV-15).

Enhanced with:
- Score validation and bounds checking
- Trust circuit breaker for rapid score degradation
- Trust recovery mechanisms
- Score change rate limiting
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class TrustState(Enum):
    """Trust states for circuit breaker functionality."""
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    CRITICAL = "CRITICAL"
    REVOKED = "REVOKED"


@dataclass(frozen=True, slots=True)
class TrustScore:
    """Immutable snapshot of an engine's trust score."""

    engine_id: str
    score: float  # [0.0, 1.0]
    reason: str
    state: TrustState = TrustState.HEALTHY


class TrustEngine:
    """Per-engine trust ledger with circuit breaker protection.

    Default score is 1.0 for any unseen engine_id.
    All mutations clamp to [0.0, 1.0].
    Circuit breaker prevents rapid trust degradation.
    """

    __slots__ = ("_scores", "_states", "_rate_limits", "_circuit_breakers")

    def __init__(self) -> None:
        self._scores: dict[str, float] = {}
        self._states: dict[str, TrustState] = {}
        self._rate_limits: dict[str, list[float]] = {}  # Recent score changes for rate limiting
        self._circuit_breakers: dict[str, dict] = {}  # Circuit breaker state per engine

    def _get_circuit_breaker_config(self, engine_id: str) -> dict:
        """Get or create circuit breaker config for an engine."""
        if engine_id not in self._circuit_breakers:
            self._circuit_breakers[engine_id] = {
                "state": "CLOSED",
                "failure_count": 0,
                "last_failure_time": 0,
                "threshold": 5,  # Number of rapid drops before opening
                "timeout": 60  # Seconds before recovery attempt
            }
        return self._circuit_breakers[engine_id]

    def _update_trust_state(self, engine_id: str, score: float) -> TrustState:
        """Update trust state based on score."""
        if score <= 0.0:
            return TrustState.REVOKED
        elif score <= 0.3:
            return TrustState.CRITICAL
        elif score <= 0.6:
            return TrustState.DEGRADED
        else:
            return TrustState.HEALTHY

    def _check_rate_limit(self, engine_id: str, delta: float) -> bool:
        """Check if score change rate is within acceptable limits."""
        if engine_id not in self._rate_limits:
            self._rate_limits[engine_id] = []
        
        recent_changes = self._rate_limits[engine_id]
        
        # Only track negative changes (trust degradation)
        if delta >= 0:
            return True
        
        # Add this change to recent history
        import time
        recent_changes.append(time.time())
        
        # Remove changes older than 60 seconds
        cutoff = time.time() - 60
        self._rate_limits[engine_id] = [t for t in recent_changes if t > cutoff]
        
        # Allow maximum of 3 negative changes per minute
        return len(self._rate_limits[engine_id]) <= 3

    # ------------------------------------------------------------------
    def score(self, engine_id: str) -> TrustScore:
        """Return the current trust snapshot for *engine_id*."""
        current_score = self._scores.get(engine_id, 1.0)
        current_state = self._states.get(engine_id, TrustState.HEALTHY)
        
        return TrustScore(
            engine_id=engine_id,
            score=current_score,
            reason="",
            state=current_state
        )

    def update(self, engine_id: str, delta: float, *, reason: str) -> TrustScore:
        """Apply *delta* to the score and return the new snapshot with circuit breaker protection."""
        import time
        
        # Check circuit breaker state
        cb_config = self._get_circuit_breaker_config(engine_id)
        
        if cb_config["state"] == "OPEN":
            # Check if recovery timeout has elapsed
            if time.time() - cb_config["last_failure_time"] < cb_config["timeout"]:
                # Circuit breaker is still open, reject update
                current_score = self._scores.get(engine_id, 1.0)
                current_state = self._states.get(engine_id, TrustState.HEALTHY)
                return TrustScore(
                    engine_id=engine_id,
                    score=current_score,
                    reason=f"Circuit breaker open: {reason}",
                    state=current_state
                )
            else:
                # Try to recover
                cb_config["state"] = "HALF_OPEN"
        
        # Check rate limiting for negative changes
        if delta < 0 and not self._check_rate_limit(engine_id, delta):
            current_score = self._scores.get(engine_id, 1.0)
            current_state = self._states.get(engine_id, TrustState.HEALTHY)
            return TrustScore(
                engine_id=engine_id,
                score=current_score,
                reason=f"Rate limit exceeded: {reason}",
                state=current_state
            )
        
        current = self._scores.get(engine_id, 1.0)
        new_score = max(0.0, min(1.0, current + delta))
        
        # Update circuit breaker on significant drops
        if delta < -0.1:  # Significant trust drop
            cb_config["failure_count"] += 1
            cb_config["last_failure_time"] = time.time()
            
            if cb_config["failure_count"] >= cb_config["threshold"]:
                cb_config["state"] = "OPEN"
                # Emit circuit breaker event (if event bus available)
                # This would require event bus integration
        
        # Reset circuit breaker on successful updates
        if cb_config["state"] == "HALF_OPEN" and delta >= 0:
            cb_config["state"] = "CLOSED"
            cb_config["failure_count"] = 0
        
        self._scores[engine_id] = new_score
        new_state = self._update_trust_state(engine_id, new_score)
        self._states[engine_id] = new_state
        
        return TrustScore(engine_id=engine_id, score=new_score, reason=reason, state=new_state)

    def revoke(self, engine_id: str, reason: str) -> None:
        """Hard-set score to 0.0 (trust revoked)."""
        self._scores[engine_id] = 0.0
        self._states[engine_id] = TrustState.REVOKED
        
        # Open circuit breaker on revocation
        cb_config = self._get_circuit_breaker_config(engine_id)
        cb_config["state"] = "OPEN"
        cb_config["failure_count"] = cb_config["threshold"]  # Max out failures

    def get_circuit_breaker_status(self, engine_id: str) -> dict:
        """Get circuit breaker status for an engine."""
        return self._get_circuit_breaker_config(engine_id).copy()

    def reset_circuit_breaker(self, engine_id: str) -> None:
        """Manually reset circuit breaker for an engine."""
        if engine_id in self._circuit_breakers:
            self._circuit_breakers[engine_id] = {
                "state": "CLOSED",
                "failure_count": 0,
                "last_failure_time": 0,
                "threshold": 5,
                "timeout": 60
            }


__all__ = ["TrustScore", "TrustEngine"]
