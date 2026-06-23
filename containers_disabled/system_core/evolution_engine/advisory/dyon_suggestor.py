"""DYON Suggestor — System Engineering Advisory Module (NEW CAPABILITY).

DYON can now provide advisory recommendations for system improvements:
- Architecture suggestions
- Performance optimizations
- Security recommendations
- Scalability improvements
- Observability enhancements
- DevOps best practices
- Database optimizations
- Distributed systems patterns

This makes DYON a true System Engineer and Suggestor, not just a code improver.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum
from typing import Any

LOG = logging.getLogger(__name__)


class AdvisoryCategory(Enum):
    """Categories of advisory recommendations."""

    ARCHITECTURE = "architecture"
    INFRASTRUCTURE = "infrastructure"
    SECURITY = "security"
    PERFORMANCE = "performance"
    SCALABILITY = "scalability"
    OBSERVABILITY = "observability"
    DEVOPS = "devops"
    DATABASE = "database"
    DISTRIBUTED_SYSTEMS = "distributed_systems"


class AdvisoryPriority(Enum):
    """Priority levels for advisory recommendations."""

    CRITICAL = "critical"  # Immediate action required
    HIGH = "high"  # Should address soon
    MEDIUM = "medium"  # Should address
    LOW = "low"  # Nice to have
    INFO = "info"  # Informational


@dataclass(frozen=True, slots=True)
class AdvisoryRecommendation:
    """System engineering advisory recommendation."""

    recommendation_id: str
    category: AdvisoryCategory
    priority: AdvisoryPriority
    title: str
    summary: str
    description: str
    rationale: str  # Why this recommendation is made
    benefits: tuple[str, ...]  # Benefits of implementing
    risks: tuple[str, ...]  # Risks if not implemented
    implementation_steps: tuple[str, ...]  # How to implement
    estimated_effort: str  # Implementation effort estimate
    related_findings: tuple[str, ...]  # Related research finding IDs
    context: str  # System context for recommendation
    confidence: float  # Confidence in recommendation (0.0 to 1.0)
    created_ts_ns: int
    last_updated_ts_ns: int


@dataclass(frozen=True, slots=True)
class AdvisoryPattern:
    """System engineering pattern that DYON recognizes."""

    pattern_id: str
    name: str
    category: AdvisoryCategory
    description: str
    when_to_use: str
    when_not_to_use: str
    benefits: tuple[str, ...]
    drawbacks: tuple[str, ...]
    alternatives: tuple[str, ...]
    examples: tuple[str, ...]


class DYONSuggestor:
    """DYON's system engineering suggestor and advisor.

    Provides advisory recommendations based on:
    - Research findings from DYON research runtime
    - Current system state analysis
    - Known system engineering patterns
    - Best practices from trusted sources
    """

    # Known system engineering patterns
    PATTERNS = {
        "circuit_breaker": AdvisoryPattern(
            pattern_id="circuit_breaker",
            name="Circuit Breaker Pattern",
            category=AdvisoryCategory.PERFORMANCE,
            description="Prevent cascading failures by stopping requests to a failing service",
            when_to_use="When calling external services that may fail or be slow",
            when_not_to_use="When the external service is critical and cannot be safely degraded",
            benefits=(
                "Prevents cascading failures",
                "Graceful degradation",
                "Fast failure detection",
                "Automatic recovery",
            ),
            drawbacks=(
                "Adds complexity",
                "Requires configuration tuning",
                "May mask underlying issues",
            ),
            alternatives=(
                "Retry with exponential backoff",
                "Bulkhead pattern",
                "Timeout pattern",
            ),
            examples=(
                "Netflix Hystrix",
                "Resilience4j",
                "AWS Circuit Breaker",
            ),
        ),
        "caching_read": AdvisoryPattern(
            pattern_id="caching_read",
            name="Read-Through Caching",
            category=AdvisoryCategory.PERFORMANCE,
            description="Cache frequently accessed data to reduce database load",
            when_to_use="For read-heavy workloads with slow data sources",
            when_not_to_use="For write-heavy workloads or real-time data requirements",
            benefits=(
                "Reduced database load",
                "Faster response times",
                "Better scalability",
                "Lower costs",
            ),
            drawbacks=(
                "Cache complexity",
                "Stale data risk",
                "Memory usage",
                "Cache invalidation complexity",
            ),
            alternatives=(
                "Write-through cache",
                "Write-behind cache",
                "Cache aside pattern",
            ),
            examples=(
                "Redis caching",
                "Memcached",
                "CDN caching",
            ),
        ),
        "event_sourcing": AdvisoryPattern(
            pattern_id="event_sourcing",
            name="Event Sourcing",
            category=AdvisoryCategory.ARCHITECTURE,
            description="Store state changes as a sequence of events rather than current state",
            when_to_use="When you need a complete audit trail, temporal queries, or event replay",
            when_not_to_use="For simple CRUD operations or when temporal queries aren't needed",
            benefits=(
                "Complete audit trail",
                "Temporal queries",
                "Event replay",
                "Debugging capabilities",
            ),
            drawbacks=(
                "Complex implementation",
                "Event schema evolution",
                "Event duplication",
                "Query complexity",
            ),
            alternatives=(
                "Traditional CRUD",
                "CQRS",
                "Snapshot pattern",
            ),
            examples=(
                "Axon Framework",
                "EventStoreDB",
                "Apache Kafka",
            ),
        ),
        "cqs": AdvisoryPattern(
            pattern_id="cqs",
            name="CQRS (Command Query Responsibility Segregation)",
            category=AdvisoryCategory.ARCHITECTURE,
            description="Separate read models from write models for scalability",
            when_to_use="For complex domains with different read/write requirements",
            when_not_to_use="For simple CRUD applications",
            benefits=(
                "Optimized read performance",
                "Scalable reads and writes",
                "Separation of concerns",
                "Flexibility in data models",
            ),
            drawbacks=(
                "Increased complexity",
                "Eventual consistency",
                "Multiple data sources",
                "Synchronization challenges",
            ),
            alternatives=(
                "Traditional layered architecture",
                "Event sourcing",
                "Service-oriented architecture",
            ),
            examples=(
                "Axon Framework",
                "MediatR",
                "NCQRS",
            ),
        ),
        "rate_limiting": AdvisoryPattern(
            pattern_id="rate_limiting",
            name="Rate Limiting",
            category=AdvisoryCategory.SECURITY,
            description="Limit the rate of requests to prevent abuse and ensure fairness",
            when_to_use="For public APIs, authentication endpoints, or resource-constrained services",
            when_not_to_use="For internal services with trusted clients",
            benefits=(
                "Prevents abuse",
                "Fair resource allocation",
                "Cost control",
                "System protection",
            ),
            drawbacks=(
                "Configuration complexity",
                "False positives",
                "Burst handling challenges",
            ),
            alternatives=(
                "Throttling",
                "Queue-based processing",
                "Load shedding",
            ),
            examples=(
                "Redis rate limiting",
                "API Gateway rate limiting",
                "Nginx rate limiting",
            ),
        ),
        "circuit_breaker": AdvisoryPattern(
            pattern_id="circuit_breaker",
            name="Circuit Breaker",
            category=AdvisoryCategory.PERFORMANCE,
            description="Prevent cascading failures by stopping requests to failing services",
            when_to_use="When calling external services that may fail",
            when_not_to_use="For critical services that cannot be safely degraded",
            benefits=(
                "Prevents cascading failures",
                "Graceful degradation",
                "Fast failure",
                "Automatic recovery",
            ),
            drawbacks=(
                "Configuration complexity",
                "May mask underlying issues",
                "Requires monitoring",
            ),
            alternatives=(
                "Retry with backoff",
                "Bulkhead pattern",
                "Timeout pattern",
            ),
            examples=(
                "Hystrix",
                "Resilience4j",
                "Istio Circuit Breaker",
            ),
        ),
        "database_sharding": AdvisoryPattern(
            pattern_id="database_sharding",
            name="Database Sharding",
            category=AdvisoryCategory.DATABASE,
            description="Distribute data across multiple database instances for scalability",
            when_to_use="When single database cannot handle load or data volume",
            when_not_to_use="For small datasets or when cross-shard queries are frequent",
            benefits=(
                "Horizontal scalability",
                "Improved performance",
                "Better resource utilization",
                "Geographic distribution",
            ),
            drawbacks=(
                "Complex query routing",
                "Cross-shard transactions",
                "Rebalancing complexity",
                "Operational overhead",
            ),
            alternatives=(
                "Read replicas",
                "Caching",
                "Partitioning",
            ),
            examples=(
                "MongoDB sharding",
                "Citus (PostgreSQL)",
                "Vitess",
            ),
        ),
    }

    def __init__(self):
        self._recommendations: dict[str, AdvisoryRecommendation] = {}
        self._research_findings: dict[str, Any] = {}  # Will be populated from research runtime

    def analyze_system_for_recommendations(
        self,
        system_state: dict[str, Any],
        category: AdvisoryCategory | None = None,
    ) -> list[AdvisoryRecommendation]:
        """Analyze system state and generate advisory recommendations."""
        recommendations = []

        # Analyze different aspects of the system
        if category is None or category == AdvisoryCategory.PERFORMANCE:
            recommendations.extend(self._analyze_performance(system_state))

        if category is None or category == AdvisoryCategory.ARCHITECTURE:
            recommendations.extend(self._analyze_architecture(system_state))

        if category is None or category == AdvisoryCategory.SECURITY:
            recommendations.extend(self._analyze_security(system_state))

        if category is None or category == AdvisoryCategory.SCALABILITY:
            recommendations.extend(self._analyze_scalability(system_state))

        if category is None or category == AdvisoryCategory.OBSERVABILITY:
            recommendations.extend(self._analyze_observability(system_state))

        # Store recommendations
        for rec in recommendations:
            self._recommendations[rec.recommendation_id] = rec

        return recommendations

    def _analyze_performance(self, system_state: dict[str, Any]) -> list[AdvisoryRecommendation]:
        """Analyze system for performance improvements."""
        recommendations = []
        current_ts_ns = int(datetime.now(UTC).timestamp() * 1_000_000_000)

        # Check if circuit breaker pattern is being used
        if "circuit_breaker" not in system_state.get("patterns", []):
            recommendations.append(
                AdvisoryRecommendation(
                    recommendation_id="perf_circuit_breaker",
                    category=AdvisoryCategory.PERFORMANCE,
                    priority=AdvisoryPriority.HIGH,
                    title="Implement Circuit Breaker Pattern",
                    summary="Add circuit breaker pattern for external service calls",
                    description="The system calls external services without circuit breaker protection, risking cascading failures",
                    rationale="Circuit breakers prevent cascading failures by stopping requests to failing services",
                    benefits=(
                        "Prevents cascading failures",
                        "Graceful degradation",
                        "Fast failure detection",
                        "Automatic recovery",
                    ),
                    risks=(
                        "Increased complexity",
                        "Configuration tuning required",
                    ),
                    implementation_steps=(
                        "Identify external service calls",
                        "Add circuit breaker middleware",
                        "Configure thresholds and timeouts",
                        "Add monitoring for circuit state",
                        "Test failure scenarios",
                    ),
                    estimated_effort="2-3 days",
                    related_findings=(),
                    context="System analysis: missing circuit breaker pattern",
                    confidence=0.90,
                    created_ts_ns=current_ts_ns,
                    last_updated_ts_ns=current_ts_ns,
                )
            )

        # Check caching strategy
        if "cache" not in system_state.get("infrastructure", {}):
            recommendations.append(
                AdvisoryRecommendation(
                    recommendation_id="perf_caching",
                    category=AdvisoryCategory.PERFORMANCE,
                    priority=AdvisoryPriority.MEDIUM,
                    title="Implement Caching Layer",
                    summary="Add caching layer for frequently accessed data",
                    description="No caching layer detected. Caching can significantly improve performance for read-heavy workloads",
                    rationale="Caching reduces database load and improves response times",
                    benefits=(
                        "Reduced database load",
                        "Faster response times",
                        "Better scalability",
                        "Lower costs",
                    ),
                    risks=(
                        "Cache complexity",
                        "Stale data risk",
                    ),
                    implementation_steps=(
                        "Identify cacheable data",
                        "Choose caching technology",
                        "Implement cache-aside pattern",
                        "Add cache invalidation",
                        "Monitor cache hit rates",
                    ),
                    estimated_effort="3-5 days",
                    related_findings=(),
                    context="System analysis: no caching detected",
                    confidence=0.85,
                    created_ts_ns=current_ts_ns,
                    last_updated_ts_ns=current_ts_ns,
                )
            )

        return recommendations

    def _analyze_architecture(self, system_state: dict[str, Any]) -> list[AdvisoryRecommendation]:
        """Analyze system for architectural improvements."""
        recommendations = []
        current_ts_ns = int(datetime.now(UTC).timestamp() * 1_000_000_000)

        # Check for CQRS pattern suitability
        read_write_ratio = system_state.get("read_write_ratio", 1.0)
        if read_write_ratio > 5.0:  # More reads than writes
            recommendations.append(
                AdvisoryRecommendation(
                    recommendation_id="arch_cqrs",
                    category=AdvisoryCategory.ARCHITECTURE,
                    priority=AdvisoryPriority.MEDIUM,
                    title="Consider CQRS Pattern",
                    summary="Evaluate CQRS for read-heavy workload",
                    description=f"System has read/write ratio of {read_write_ratio}. CQRS could optimize read performance",
                    rationale="CQRS separates read and write models for different optimization strategies",
                    benefits=(
                        "Optimized read performance",
                        "Scalable reads and writes",
                        "Separation of concerns",
                    ),
                    risks=(
                        "Increased complexity",
                        "Eventual consistency",
                    ),
                    implementation_steps=(
                        "Analyze read/write patterns",
                        "Design separate read/write models",
                        "Implement command handlers",
                        "Implement query handlers",
                        "Add synchronization layer",
                    ),
                    estimated_effort="2-4 weeks",
                    related_findings=(),
                    context=f"Read/write ratio analysis: {read_write_ratio}",
                    confidence=0.75,
                    created_ts_ns=current_ts_ns,
                    last_updated_ts_ns=current_ts_ns,
                )
            )

        return recommendations

    def _analyze_security(self, system_state: dict[str, Any]) -> list[AdvisoryRecommendation]:
        """Analyze system for security improvements."""
        recommendations = []
        current_ts_ns = int(datetime.now(UTC).timestamp() * 1_000_000_000)

        # Check for rate limiting
        if "rate_limiting" not in system_state.get("security", {}):
            recommendations.append(
                AdvisoryRecommendation(
                    recommendation_id="sec_rate_limiting",
                    category=AdvisoryCategory.SECURITY,
                    priority=AdvisoryPriority.HIGH,
                    title="Implement Rate Limiting",
                    summary="Add rate limiting to public APIs",
                    description="No rate limiting detected. This leaves APIs vulnerable to abuse",
                    rationale="Rate limiting prevents abuse and ensures fair resource allocation",
                    benefits=(
                        "Prevents abuse",
                        "Fair resource allocation",
                        "Cost control",
                        "System protection",
                    ),
                    risks=(
                        "Configuration complexity",
                        "False positives",
                    ),
                    implementation_steps=(
                        "Identify public endpoints",
                        "Define rate limits",
                        "Implement rate limiting middleware",
                        "Add monitoring",
                        "Configure alerts",
                    ),
                    estimated_effort="2-3 days",
                    related_findings=(),
                    context="Security analysis: no rate limiting detected",
                    confidence=0.92,
                    created_ts_ns=current_ts_ns,
                    last_updated_ts_ns=current_ts_ns,
                )
            )

        return recommendations

    def _analyze_scalability(self, system_state: dict[str, Any]) -> list[AdvisoryRecommendation]:
        """Analyze system for scalability improvements."""
        recommendations = []
        current_ts_ns = int(datetime.now(UTC).timestamp() * 1_000_000_000)

        # Check database size vs capacity
        db_size = system_state.get("database_size_gb", 0)
        if db_size > 500:  # Large database
            recommendations.append(
                AdvisoryRecommendation(
                    recommendation_id="scalability_sharding",
                    category=AdvisoryCategory.SCALABILITY,
                    priority=AdvisoryPriority.MEDIUM,
                    title="Evaluate Database Sharding",
                    summary=f"Consider sharding for {db_size}GB database",
                    description=f"Database size is {db_size}GB. Sharding could improve scalability",
                    rationale="Sharding distributes data across multiple instances for horizontal scalability",
                    benefits=(
                        "Horizontal scalability",
                        "Improved performance",
                        "Better resource utilization",
                    ),
                    risks=(
                        "Complex query routing",
                        "Cross-shard transactions",
                        "Operational overhead",
                    ),
                    implementation_steps=(
                        "Analyze data access patterns",
                        "Design shard key",
                        "Choose sharding technology",
                        "Migrate data",
                        "Update application routing",
                    ),
                    estimated_effort="4-8 weeks",
                    related_findings=(),
                    context=f"Database size analysis: {db_size}GB",
                    confidence=0.80,
                    created_ts_ns=current_ts_ns,
                    last_updated_ts_ns=current_ts_ns,
                )
            )

        return recommendations

    def _analyze_observability(self, system_state: dict[str, Any]) -> list[AdvisoryRecommendation]:
        """Analyze system for observability improvements."""
        recommendations = []
        current_ts_ns = int(datetime.now(UTC).timestamp() * 1_000_000_000)

        # Check for distributed tracing
        if "tracing" not in system_state.get("observability", {}):
            recommendations.append(
                AdvisoryRecommendation(
                    recommendation_id="obs_tracing",
                    category=AdvisoryCategory.OBSERVABILITY,
                    priority=AdvisoryPriority.MEDIUM,
                    title="Implement Distributed Tracing",
                    summary="Add distributed tracing for observability",
                    description="No distributed tracing detected. Tracing enables end-to-end request visibility",
                    rationale="Distributed tracing provides visibility into request flows across services",
                    benefits=(
                        "End-to-end request visibility",
                        "Performance bottleneck identification",
                        "Debugging support",
                        "Service dependency mapping",
                    ),
                    risks=(
                        "Performance overhead",
                        "Instrumentation effort",
                    ),
                    implementation_steps=(
                        "Choose tracing solution (OpenTelemetry, Jaeger)",
                        "Instrument services",
                        "Configure sampling strategy",
                        "Set up tracing backend",
                        "Create trace queries",
                    ),
                    estimated_effort="1-2 weeks",
                    related_findings=(),
                    context="Observability analysis: no tracing detected",
                    confidence=0.88,
                    created_ts_ns=current_ts_ns,
                    last_updated_ts_ns=current_ts_ns,
                )
            )

        return recommendations

    def get_recommendations_by_category(
        self,
        category: AdvisoryCategory,
    ) -> list[AdvisoryRecommendation]:
        """Get all recommendations for a category."""
        return [r for r in self._recommendations.values() if r.category == category]

    def get_recommendations_by_priority(
        self,
        priority: AdvisoryPriority,
    ) -> list[AdvisoryRecommendation]:
        """Get all recommendations for a priority."""
        return [r for r in self._recommendations.values() if r.priority == priority]

    def get_pattern(self, pattern_id: str) -> AdvisoryPattern | None:
        """Get a known system engineering pattern."""
        return self.PATTERNS.get(pattern_id)

    def get_all_patterns(self) -> dict[str, AdvisoryPattern]:
        """Get all known system engineering patterns."""
        return self.PATTERNS.copy()

    def get_status(self) -> dict[str, Any]:
        """Get suggestor status."""
        return {
            "recommendations_count": len(self._recommendations),
            "patterns_count": len(self.PATTERNS),
            "recommendations_by_category": {
                cat.value: len(self.get_recommendations_by_category(cat))
                for cat in AdvisoryCategory
            },
        }


# Singleton instance
_dyon_suggestor: DYONSuggestor | None = None
_suggestor_lock = threading.Lock()


def get_dyon_suggestor() -> DYONSuggestor:
    """Get the singleton DYON suggestor instance."""
    global _dyon_suggestor, _suggestor_lock

    with _suggestor_lock:
        if _dyon_suggestor is None:
            _dyon_suggestor = DYONSuggestor()
        return _dyon_suggestor
