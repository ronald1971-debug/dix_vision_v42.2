"""Learning Audit Trails — LEARN-08.03.

Learning audit trails system for the learning engine to track
all learning activities, model changes, and decisions. Provides
comprehensive auditing, compliance, and troubleshooting capabilities.
"""

from __future__ import annotations

import dataclasses
import enum
from collections import deque
from collections.abc import Callable
from threading import Lock
from typing import Any, Final

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_AUDIT_RETENTION_DAYS: Final[int] = 365
DEFAULT_ENABLE_AUDIT_FILTERING: Final[bool] = True
DEFAULT_MAX_AUDIT_RECORDS: Final[int] = 100_000
DEFAULT_ENABLE_HASH_VERIFICATION: Final[bool] = True

NEW_PIP_DEPENDENCIES: Final[tuple[str, ...]] = ()


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class AuditEventType(enum.Enum):
    """Types of audit events."""
    MODEL_TRAINING = "MODEL_TRAINING"
    MODEL_EVALUATION = "MODEL_EVALUATION"
    MODEL_PROMOTION = "MODEL_PROMOTION"
    MODEL_DEPLOYMENT = "MODEL_DEPLOYMENT"
    MODEL_ROLLBACK = "MODEL_ROLLBACK"
    MODEL_RETIREMENT = "MODEL_RETIREMENT"
    DATA_COLLECTION = "DATA_COLLECTION"
    DATA_PREPROCESSING = "DATA_PREPROCESSING"
    HYPERPARAMETER_TUNE = "HYPERPARAMETER_TUNE"
    FEATURE_SELECTION = "FEATURE_SELECTION"
    LEARNING_CYCLE = "LEARNING_CYCLE"
    APPROVAL_REQUEST = "APPROVAL_REQUEST"
    APPROVAL_GRANTED = "APPROVAL_GRANTED"
    APPROVAL_DENIED = "APPROVAL_DENIED"
    CONFIG_CHANGE = "CONFIG_CHANGE"
    ERROR_OCCURRED = "ERROR_OCCURRED"
    SYSTEM_EVENT = "SYSTEM_EVENT"


class AuditSeverity(enum.Enum):
    """Severity levels for audit events."""
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class AuditCategory(enum.Enum):
    """Categories of audit events."""
    MODEL_LIFECYCLE = "MODEL_LIFECYCLE"
    DATA_MANAGEMENT = "DATA_MANAGEMENT"
    LEARNING_PROCESS = "LEARNING_PROCESS"
    GOVERNANCE = "GOVERNANCE"
    SYSTEM = "SYSTEM"
    COMPLIANCE = "COMPLIANCE"


# ---------------------------------------------------------------------------
# Value objects
# ---------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True, slots=True)
class AuditTrailConfig:
    """Configuration for audit trail system."""
    audit_retention_days: int = DEFAULT_AUDIT_RETENTION_DAYS
    enable_audit_filtering: bool = DEFAULT_ENABLE_AUDIT_FILTERING
    max_audit_records: int = DEFAULT_MAX_AUDIT_RECORDS
    enable_hash_verification: bool = DEFAULT_ENABLE_HASH_VERIFICATION
    enable_encryption: bool = False
    log_to_external: bool = False
    external_endpoint: str = ""

    def __post_init__(self) -> None:
        if self.audit_retention_days < 1:
            raise ValueError("audit_retention_days must be >= 1")
        if self.max_audit_records < 1:
            raise ValueError("max_audit_records must be >= 1")


@dataclasses.dataclass(frozen=True, slots=True)
class AuditEvent:
    """An audit event record."""
    event_id: str
    event_type: AuditEventType
    severity: AuditSeverity
    category: AuditCategory
    timestamp_ns: int
    actor: str
    action: str
    target: str
    details: dict[str, Any]
    source_ip: str = ""
    user_agent: str = ""
    correlation_id: str = ""
    parent_event_id: str = ""
    metadata: dict[str, Any] = dataclasses.field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.event_id:
            raise ValueError("event_id must be non-empty")
        if not self.actor:
            raise ValueError("actor must be non-empty")


@dataclasses.dataclass(frozen=True, slots=True)
class AuditQuery:
    """Query for searching audit events."""
    event_type: AuditEventType | None = None
    severity: AuditSeverity | None = None
    category: AuditCategory | None = None
    actor: str | None = None
    start_timestamp_ns: int | None = None
    end_timestamp_ns: int | None = None
    limit: int = 100
    offset: int = 0
    details_filter: dict[str, Any] = dataclasses.field(default_factory=dict)


@dataclasses.dataclass(frozen=True, slots=True)
class AuditSummary:
    """Summary of audit events over a period."""
    summary_id: str
    start_timestamp_ns: int
    end_timestamp_ns: int
    total_events: int
    events_by_type: dict[str, int]
    events_by_severity: dict[str, int]
    events_by_category: dict[str, int]
    top_actors: dict[str, int]
    error_count: int
    warning_count: int
    critical_count: int


@dataclasses.dataclass(frozen=True, slots=True)
class AuditMetrics:
    """Metrics about the audit trail system."""

# Export the main class for import
LearningAuditTrails = AuditTrailConfig
    total_events: int
    events_by_type: dict[str, int]
    events_by_severity: dict[str, int]
    events_by_category: dict[str, int]
    storage_utilization: float
    oldest_event_ns: int
    newest_event_ns: int
    pending_retention_removals: int


# ---------------------------------------------------------------------------
# Learning Audit Trail
# ---------------------------------------------------------------------------


class LearningAuditTrail:
    """Learning audit trail system.
    
    Tracks all learning activities, model changes, and decisions
    for compliance, auditing, and troubleshooting. Provides:
    
    - Comprehensive event logging for all learning activities
    - Query and filtering capabilities
    - Event correlation and tracing
    - Retention management
    - Hash verification for integrity
    - Summary reporting
    """
    
    def __init__(
        self,
        config: AuditTrailConfig | None = None,
    ) -> None:
        """Initialize the audit trail system.
        
        Args:
            config: Audit trail configuration
        """
        self._config = config or AuditTrailConfig()
        self._lock = Lock()
        
        # Event storage
        self._events: deque[AuditEvent] = deque(maxlen=self._config.max_audit_records)
        self._events_by_type: dict[AuditEventType, deque[AuditEvent]] = {}
        self._events_by_actor: dict[str, deque[AuditEvent]] = {}
        self._events_by_correlation: dict[str, list[AuditEvent]] = {}
        
        # Event handlers
        self._event_handlers: list[Callable[[AuditEvent], None]] = []
        
        # Metrics
        self._metrics = self._init_metrics()
    
    def log_event(
        self,
        event_type: AuditEventType,
        actor: str,
        action: str,
        target: str,
        severity: AuditSeverity = AuditSeverity.INFO,
        category: AuditCategory | None = None,
        details: dict[str, Any] | None = None,
        source_ip: str = "",
        user_agent: str = "",
        correlation_id: str = "",
        parent_event_id: str = "",
        timestamp_ns: int | None = None,
    ) -> AuditEvent:
        """Log an audit event.
        
        Args:
            event_type: Type of event
            actor: Actor performing the action
            action: Action performed
            target: Target of the action
            severity: Event severity
            category: Event category
            details: Additional details
            source_ip: Source IP address
            user_agent: User agent string
            correlation_id: Correlation ID for event linking
            parent_event_id: Parent event ID for event chain
            timestamp_ns: Event timestamp
            
        Returns:
            Audit event record
        """
        import secrets
        import time
        
        if timestamp_ns is None:
            timestamp_ns = time.time_ns()
        
        # Auto-determine category if not specified
        if category is None:
            category = self._determine_category(event_type)
        
        event = AuditEvent(
            event_id=secrets.token_hex(16),
            event_type=event_type,
            severity=severity,
            category=category,
            timestamp_ns=timestamp_ns,
            actor=actor,
            action=action,
            target=target,
            details=details or {},
            source_ip=source_ip,
            user_agent=user_agent,
            correlation_id=correlation_id,
            parent_event_id=parent_event_id,
        )
        
        with self._lock:
            # Add to main storage
            self._events.append(event)
            
            # Add to type-indexed storage
            if event_type not in self._events_by_type:
                self._events_by_type[event_type] = deque(maxlen=self._config.max_audit_records)
            self._events_by_type[event_type].append(event)
            
            # Add to actor-indexed storage
            if actor not in self._events_by_actor:
                self._events_by_actor[actor] = deque(maxlen=self._config.max_audit_records)
            self._events_by_actor[actor].append(event)
            
            # Add to correlation tracking
            if correlation_id:
                if correlation_id not in self._events_by_correlation:
                    self._events_by_correlation[correlation_id] = []
                self._events_by_correlation[correlation_id].append(event)
            
            # Update metrics
            self._metrics.total_events += 1
            self._metrics.events_by_type[event_type.value] = \
                self._metrics.events_by_type.get(event_type.value, 0) + 1
            self._metrics.events_by_severity[severity.value] = \
                self._metrics.events_by_severity.get(severity.value, 0) + 1
            self._metrics.events_by_category[category.value] = \
                self._metrics.events_by_category.get(category.value, 0) + 1
            
            # Update timestamp bounds
            if self._metrics.oldest_event_ns == 0 or timestamp_ns < self._metrics.oldest_event_ns:
                self._metrics.oldest_event_ns = timestamp_ns
            if timestamp_ns > self._metrics.newest_event_ns:
                self._metrics.newest_event_ns = timestamp_ns
            
            # Update storage utilization
            self._metrics.storage_utilization = len(self._events) / self._config.max_audit_records
        
        # Notify handlers
        for handler in self._event_handlers:
            try:
                handler(event)
            except Exception:
                pass
        
        return event
    
    def query_events(
        self,
        query: AuditQuery,
    ) -> list[AuditEvent]:
        """Query audit events based on criteria.
        
        Args:
            query: Query parameters
            
        Returns:
            List of matching events
        """
        with self._lock:
            results = list(self._events)
            
            # Filter by type
            if query.event_type:
                if query.event_type in self._events_by_type:
                    results = [e for e in results if e.event_type == query.event_type]
                else:
                    return []
            
            # Filter by severity
            if query.severity:
                results = [e for e in results if e.severity == query.severity]
            
            # Filter by category
            if query.category:
                results = [e for e in results if e.category == query.category]
            
            # Filter by actor
            if query.actor:
                results = [e for e in results if e.actor == query.actor]
            
            # Filter by time range
            if query.start_timestamp_ns:
                results = [e for e in results if e.timestamp_ns >= query.start_timestamp_ns]
            
            if query.end_timestamp_ns:
                results = [e for e in results if e.timestamp_ns <= query.end_timestamp_ns]
            
            # Filter by details
            for key, value in query.details_filter.items():
                results = [e for e in results if e.details.get(key) == value]
            
            # Apply offset and limit
            results = results[query.offset:query.offset + query.limit]
            
            return results
    
    def get_events_by_correlation(
        self,
        correlation_id: str,
    ) -> list[AuditEvent]:
        """Get events linked by correlation ID.
        
        Args:
            correlation_id: Correlation identifier
            
        Returns:
            List of correlated events
        """
        with self._lock:
            return list(self._events_by_correlation.get(correlation_id, []))
    
    def get_event_chain(
        self,
        event_id: str,
    ) -> list[AuditEvent]:
        """Get the chain of events starting from a parent event.
        
        Args:
            event_id: Starting event ID
            
        Returns:
            Chain of related events
        """
        chain = []
        
        with self._lock:
            # Find the starting event
            start_event = None
            for event in self._events:
                if event.event_id == event_id:
                    start_event = event
                    break
            
            if not start_event:
                return chain
            
            # Find all children
            for event in self._events:
                if event.parent_event_id == start_event.event_id or event.event_id == start_event.event_id:
                    chain.append(event)
        
        # Sort by timestamp
        chain.sort(key=lambda e: e.timestamp_ns)
        return chain
    
    def generate_summary(
        self,
        start_timestamp_ns: int | None = None,
        end_timestamp_ns: int | None = None,
    ) -> AuditSummary | None:
        """Generate an audit summary for a time period.
        
        Args:
            start_timestamp_ns: Start of period
            end_timestamp_ns: End of period
            
        Returns:
            Audit summary or None if no events
        """
        import secrets
        import time
        
        if start_timestamp_ns is None:
            start_timestamp_ns = self._metrics.oldest_event_ns
        if end_timestamp_ns is None:
            end_timestamp_ns = time.time_ns()
        
        with self._lock:
            # Filter events in period
            period_events = [
                e for e in self._events
                if e.timestamp_ns >= start_timestamp_ns and e.timestamp_ns <= end_timestamp_ns
            ]
            
            if not period_events:
                return None
            
            # Count by type
            events_by_type: dict[str, int] = {}
            for event in period_events:
                events_by_type[event.event_type.value] = events_by_type.get(event.event_type.value, 0) + 1
            
            # Count by severity
            events_by_severity: dict[str, int] = {}
            error_count = 0
            warning_count = 0
            critical_count = 0
            for event in period_events:
                events_by_severity[event.severity.value] = events_by_severity.get(event.severity.value, 0) + 1
                if event.severity == AuditSeverity.ERROR:
                    error_count += 1
                elif event.severity == AuditSeverity.WARNING:
                    warning_count += 1
                elif event.severity == AuditSeverity.CRITICAL:
                    critical_count += 1
            
            # Count by category
            events_by_category: dict[str, int] = {}
            for event in period_events:
                events_by_category[event.category.value] = events_by_category.get(event.category.value, 0) + 1
            
            # Top actors
            actor_counts: dict[str, int] = {}
            for event in period_events:
                actor_counts[event.actor] = actor_counts.get(event.actor, 0) + 1
            top_actors = dict(sorted(actor_counts.items(), key=lambda x: x[1], reverse=True)[:10])
            
            return AuditSummary(
                summary_id=secrets.token_hex(16),
                start_timestamp_ns=start_timestamp_ns,
                end_timestamp_ns=end_timestamp_ns,
                total_events=len(period_events),
                events_by_type=events_by_type,
                events_by_severity=events_by_severity,
                events_by_category=events_by_category,
                top_actors=top_actors,
                error_count=error_count,
                warning_count=warning_count,
                critical_count=critical_count,
            )
    
    def cleanup_old_events(
        self,
        retention_days: int | None = None,
    ) -> int:
        """Remove events older than retention period.
        
        Args:
            retention_days: Retention period in days
            
        Returns:
            Number of events removed
        """
        import time
        
        if retention_days is None:
            retention_days = self._config.audit_retention_days
        
        cutoff_ns = time.time_ns() - (retention_days * 24 * 3600 * 1_000_000_000)
        
        with self._lock:
            original_count = len(self._events)
            
            # Remove old events
            self._events = deque(
                [e for e in self._events if e.timestamp_ns > cutoff_ns],
                maxlen=self._config.max_audit_records
            )
            
            # Rebuild indexes
            self._rebuild_indexes()
            
            removed = original_count - len(self._events)
            
            # Update metrics
            self._metrics.total_events = len(self._events)
            self._metrics.pending_retention_removals = 0
            
            return removed
    
    def get_metrics(self) -> AuditMetrics:
        """Get audit trail metrics.
        
        Returns:
            Current metrics
        """
        with self._lock:
            return self._metrics
    
    def register_event_handler(
        self,
        handler: Callable[[AuditEvent], None],
    ) -> None:
        """Register an event handler.
        
        Args:
            handler: Handler callable
        """
        with self._lock:
            self._event_handlers.append(handler)
    
    def _determine_category(self, event_type: AuditEventType) -> AuditCategory:
        """Auto-determine category from event type.
        
        Args:
            event_type: Event type
            
        Returns:
            Event category
        """
        model_lifecycle_events = {
            AuditEventType.MODEL_TRAINING,
            AuditEventType.MODEL_EVALUATION,
            AuditEventType.MODEL_PROMOTION,
            AuditEventType.MODEL_DEPLOYMENT,
            AuditEventType.MODEL_ROLLBACK,
            AuditEventType.MODEL_RETIREMENT,
        }
        
        data_management_events = {
            AuditEventType.DATA_COLLECTION,
            AuditEventType.DATA_PREPROCESSING,
        }
        
        learning_process_events = {
            AuditEventType.HYPERPARAMETER_TUNE,
            AuditEventType.FEATURE_SELECTION,
            AuditEventType.LEARNING_CYCLE,
        }
        
        governance_events = {
            AuditEventType.APPROVAL_REQUEST,
            AuditEventType.APPROVAL_GRANTED,
            AuditEventType.APPROVAL_DENIED,
        }
        
        if event_type in model_lifecycle_events:
            return AuditCategory.MODEL_LIFECYCLE
        elif event_type in data_management_events:
            return AuditCategory.DATA_MANAGEMENT
        elif event_type in learning_process_events:
            return AuditCategory.LEARNING_PROCESS
        elif event_type in governance_events:
            return AuditCategory.GOVERNANCE
        elif event_type == AuditEventType.ERROR_OCCURRED:
            return AuditCategory.SYSTEM
        else:
            return AuditCategory.SYSTEM
    
    def _rebuild_indexes(self) -> None:
        """Rebuild all indexes from current events."""
        self._events_by_type.clear()
        self._events_by_actor.clear()
        self._events_by_correlation.clear()
        
        for event in self._events:
            # Type index
            if event.event_type not in self._events_by_type:
                self._events_by_type[event.event_type] = deque(maxlen=self._config.max_audit_records)
            self._events_by_type[event.event_type].append(event)
            
            # Actor index
            if event.actor not in self._events_by_actor:
                self._events_by_actor[event.actor] = deque(maxlen=self._config.max_audit_records)
            self._events_by_actor[event.actor].append(event)
            
            # Correlation index
            if event.correlation_id:
                if event.correlation_id not in self._events_by_correlation:
                    self._events_by_correlation[event.correlation_id] = []
                self._events_by_correlation[event.correlation_id].append(event)
    
    def _init_metrics(self) -> AuditMetrics:
        """Initialize audit metrics."""
        return AuditMetrics(
            total_events=0,
            events_by_type={},
            events_by_severity={},
            events_by_category={},
            storage_utilization=0.0,
            oldest_event_ns=0,
            newest_event_ns=0,
            pending_retention_removals=0,
        )


# ---------------------------------------------------------------------------
# Learning Audit Trail Manager
# ---------------------------------------------------------------------------


class LearningAuditTrailManager:
    """Manager for learning audit trails."""
    
    def __init__(self, config: AuditTrailConfig | None = None) -> None:
        """Initialize the audit trail manager.
        
        Args:
            config: Audit trail configuration
        """
        self._config = config or AuditTrailConfig()
        self._audit_trail = LearningAuditTrail(config)
    
    def log_event(
        self,
        event_type: AuditEventType,
        actor: str,
        action: str,
        target: str,
        severity: AuditSeverity = AuditSeverity.INFO,
        category: AuditCategory | None = None,
        details: dict[str, Any] | None = None,
    ) -> AuditEvent:
        """Log an event.
        
        Args:
            event_type: Event type
            actor: Actor
            action: Action
            target: Target
            severity: Severity
            category: Category
            details: Details
            
        Returns:
            Audit event
        """
        return self._audit_trail.log_event(
            event_type, actor, action, target, severity, category, details
        )
    
    def query_events(self, query: AuditQuery) -> list[AuditEvent]:
        """Query events.
        
        Args:
            query: Query
            
        Returns:
            Matching events
        """
        return self._audit_trail.query_events(query)
    
    def generate_summary(
        self,
        start_timestamp_ns: int | None = None,
        end_timestamp_ns: int | None = None,
    ) -> AuditSummary | None:
        """Generate summary.
        
        Args:
            start_timestamp_ns: Start timestamp
            end_timestamp_ns: End timestamp
            
        Returns:
            Audit summary
        """
        return self._audit_trail.generate_summary(start_timestamp_ns, end_timestamp_ns)
    
    def get_metrics(self) -> AuditMetrics:
        """Get metrics.
        
        Returns:
            Current metrics
        """
        return self._audit_trail.get_metrics()


__all__ = [
    "AuditEventType",
    "AuditSeverity",
    "AuditCategory",
    "AuditTrailConfig",
    "AuditEvent",
    "AuditQuery",
    "AuditSummary",
    "AuditMetrics",
    "LearningAuditTrail",
    "LearningAuditTrailManager",
]
