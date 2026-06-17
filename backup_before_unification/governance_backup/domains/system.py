"""System Governance Domain.

Governs system health requirements – latency bounds, feed freshness,
service availability, and hardware health prerequisites.
"""

from __future__ import annotations

from dataclasses import dataclass

from governance.mcos_kernel import PolicyRule


@dataclass
class SystemGovernancePolicy:
    max_feed_age_seconds: float = 5.0
    max_order_latency_ms: float = 100.0
    min_active_feeds: int = 1
    require_heartbeat: bool = True
    max_cpu_usage_pct: float = 90.0
    max_memory_usage_pct: float = 85.0

    def to_rules(self) -> list[PolicyRule]:
        return [
            PolicyRule(
                name="system_feed_freshness",
                domain="system",
                description=f"Feed must be < {self.max_feed_age_seconds}s old",
            ),
            PolicyRule(
                name="system_latency_bound",
                domain="system",
                description=f"Order latency must be < {self.max_order_latency_ms}ms",
            ),
        ]
