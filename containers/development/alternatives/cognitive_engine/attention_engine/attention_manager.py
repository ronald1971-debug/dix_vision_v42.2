"""Attention Manager - allocates cognitive bandwidth across targets.

Manages resource allocation as INDIRA scales:
- 10 traders
- 100 traders
- 1000 traders
- 5000 traders
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

from cognitive_engine.attention_engine.focus_policy import FocusPolicy, FocusTarget


@dataclass
class AttentionAllocation:
    """Record of attention given to a cognitive target."""

    target_id: str
    domain: str
    allocated_at: int = field(default_factory=lambda: time.time_ns())
    duration_ns: int = 0
    reason: str = ""


class AttentionManager:
    """Manages cognitive attention allocation across the system.

    Resources are finite - attention must be prioritized.
    This is the equivalent of "focus" for INDIRA.
    """

    def __init__(
        self,
        policy: FocusPolicy | None = None,
        max_bandwidth: float = 1.0,
    ) -> None:
        self._policy = policy or FocusPolicy()
        self._max_bandwidth = max_bandwidth
        self._current_bandwidth = 0.0
        self._allocations: list[AttentionAllocation] = []
        self._bandwidth_history: list[tuple[int, float]] = []

    def allocate_attention(
        self,
        target_id: str,
        domain: str,
        opportunity: float = 0.5,
        risk: float = 0.5,
        novelty: float = 0.0,
        uncertainty: float = 0.5,
    ) -> FocusTarget | None:
        """Allocate attention to a target if bandwidth available."""
        required = self._calculate_bandwidth(
            opportunity, risk, novelty, uncertainty
        )

        if self._current_bandwidth + required > self._max_bandwidth:
            # Insufficient bandwidth - return None
            return None

        target = self._policy.allocate(
            target_id=target_id,
            domain=domain,
            opportunity=opportunity,
            risk=risk,
            novelty=novelty,
            uncertainty=uncertainty,
            rationale=f"bandwidth_required={required:.3f}",
        )
        self._current_bandwidth += required
        self._allocations.append(
            AttentionAllocation(
                target_id=target_id,
                domain=domain,
                reason=target.rationale,
            )
        )

        return target

    def _calculate_bandwidth(
        self, opportunity: float, risk: float, novelty: float, uncertainty: float
    ) -> float:
        """Calculate required cognitive bandwidth."""
        # Higher opportunity, risk, novelty, uncertainty = more bandwidth needed
        return (opportunity + risk + novelty + uncertainty) / 4.0

    def release_attention(self, target_id: str) -> float:
        """Release attention from a target."""
        for i, alloc in enumerate(self._allocations):
            if alloc.target_id == target_id:
                released = self._calculate_bandwidth(
                    alloc.reason, 0, 0, 0
                ) if "bandwidth" in str(alloc.reason) else 0.1
                self._current_bandwidth = max(0.0, self._current_bandwidth - released)
                self._allocations.pop(i)
                return released
        return 0.0

    def get_available_bandwidth(self) -> float:
        """Get remaining cognitive bandwidth."""
        return self._max_bandwidth - self._current_bandwidth

    def get_top_priorities(self, n: int = 10) -> list[FocusTarget]:
        """Get top attention priorities."""
        return self._policy.top_targets(n)

    def record_bandwidth(self) -> None:
        """Record current bandwidth for monitoring."""
        self._bandwidth_history.append((time.time_ns(), self._current_bandwidth))
        while len(self._bandwidth_history) > 10000:
            self._bandwidth_history.pop(0)

    def bandwidth_utilization(self) -> float:
        """Get average bandwidth utilization."""
        if not self._bandwidth_history:
            return 0.0
        return sum(h[1] for h in self._bandwidth_history) / len(self._bandwidth_history)