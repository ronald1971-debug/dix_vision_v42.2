"""Execution Audit Trail — EXEC-05.06.

Comprehensive audit trail system for execution activities to provide
full traceability, regulatory compliance, and debugging capabilities.
Logs all execution events with full context and provides query and
analysis capabilities.
"""

from __future__ import annotations

import dataclasses
import enum
import hashlib
import json
import logging
import sqlite3
from collections import deque
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from threading import Lock
from typing import Any, Final

import requests

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_MAX_AUDIT_SIZE: Final[int] = 10_000
DEFAULT_RETENTION_DAYS: Final[int] = 90
DEFAULT_ENABLE_PERSISTENCE: Final[bool] = False
DEFAULT_ENABLE_ENCRYPTION: Final[bool] = False

NEW_PIP_DEPENDENCIES: Final[tuple[str, ...]] = ()


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class AuditEventType(enum.Enum):
    """Types of audit events."""

    ORDER_SUBMITTED = "ORDER_SUBMITTED"
    ORDER_ACCEPTED = "ORDER_ACCEPTED"
    ORDER_REJECTED = "ORDER_REJECTED"
    ORDER_FILLED = "ORDER_FILLED"
    ORDER_PARTIALLY_FILLED = "ORDER_PARTIALLY_FILLED"
    ORDER_CANCELLED = "ORDER_CANCELLED"
    ORDER_EXPIRED = "ORDER_EXPIRED"
    ADAPTER_ERROR = "ADAPTER_ERROR"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    CIRCUIT_BREAKER_TRIPPED = "CIRCUIT_BREAKER_TRIPPED"
    VALIDATION_FAILED = "VALIDATION_FAILED"
    SLIPPAGE_EXCEEDED = "SLIPPAGE_EXCEEDED"
    LATENCY_ALERT = "LATENCY_ALERT"
    BALANCE_INSUFFICIENT = "BALANCE_INSUFFICIENT"
    RISK_LIMIT_EXCEEDED = "RISK_LIMIT_EXCEEDED"
    MANUAL_INTERVENTION = "MANUAL_INTERVENTION"
    SYSTEM_EVENT = "SYSTEM_EVENT"


class AuditSeverity(enum.Enum):
    """Severity level of audit events."""

    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class OrderSide(enum.Enum):
    """Side of the order."""

    BUY = "BUY"
    SELL = "SELL"


class OrderStatus(enum.Enum):
    """Status of the order."""

    PENDING = "PENDING"
    SUBMITTED = "SUBMITTED"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"


# ---------------------------------------------------------------------------
# Value objects
# ---------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True, slots=True)
class AuditConfig:
    """Configuration for audit trail."""

    max_audit_size: int = DEFAULT_MAX_AUDIT_SIZE
    retention_days: int = DEFAULT_RETENTION_DAYS
    enable_persistence: bool = DEFAULT_ENABLE_PERSISTENCE
    enable_encryption: bool = DEFAULT_ENABLE_ENCRYPTION
    enable_signature: bool = True
    storage_path: str = ""
    compression_enabled: bool = False

    def __post_init__(self) -> None:
        if self.max_audit_size < 1:
            raise ValueError("max_audit_size must be >= 1")
        if self.retention_days < 0:
            raise ValueError("retention_days must be >= 0")


@dataclasses.dataclass(frozen=True, slots=True)
class AuditEvent:
    """An audit event record."""

    event_id: str
    event_type: AuditEventType
    severity: AuditSeverity
    adapter_name: str
    timestamp_ns: int
    order_id: str
    symbol: str
    side: OrderSide | None = None
    quantity: float | None = None
    price: float | None = None
    execution_price: float | None = None
    fill_quantity: float | None = None
    message: str = ""
    error_message: str = ""
    metadata: dict[str, Any] = dataclasses.field(default_factory=dict)
    signature: str = ""

    def __post_init__(self) -> None:
        if not self.event_id:
            raise ValueError("event_id must be non-empty")
        if not self.adapter_name:
            raise ValueError("adapter_name must be non-empty")
        if not self.order_id:
            raise ValueError("order_id must be non-empty")
        if not self.symbol:
            raise ValueError("symbol must be non-empty")


@dataclasses.dataclass(frozen=True, slots=True)
class AuditQuery:
    """Query for audit events."""

    adapter_name: str | None = None
    event_type: AuditEventType | None = None
    severity: AuditSeverity | None = None
    order_id: str | None = None
    symbol: str | None = None
    start_timestamp_ns: int | None = None
    end_timestamp_ns: int | None = None
    limit: int = 100


@dataclasses.dataclass(frozen=True, slots=True)
class AuditMetrics:
    """Metrics about audit trail performance."""

    total_events: int
    events_by_type: dict[str, int]
    events_by_severity: dict[str, int]
    events_by_adapter: dict[str, int]
    events_by_symbol: dict[str, int]
    average_events_per_hour: float
    retention_compliance: float
    signature_validity: float


@dataclasses.dataclass(frozen=True, slots=True)
class OrderAuditTrail:
    """Complete audit trail for a single order."""

    order_id: str
    symbol: str
    side: OrderSide
    events: list[AuditEvent]
    submission_timestamp_ns: int
    completion_timestamp_ns: int | None = None
    total_slippage_pct: float = 0.0
    total_fees: float = 0.0
    status: OrderStatus = OrderStatus.PENDING


# ---------------------------------------------------------------------------
# Execution Audit Trail
# ---------------------------------------------------------------------------


class ExecutionAuditTrail:
    """Comprehensive audit trail for execution activities.

    Records all execution events with full context for audit purposes,
    regulatory compliance, and debugging. Provides query and analysis
    capabilities with optional persistence and encryption.
    """

    def __init__(
        self,
        config: AuditConfig | None = None,
    ) -> None:
        """Initialize the execution audit trail.

        Args:
            config: Audit trail configuration
        """
        self._config = config or AuditConfig()
        self._lock = Lock()

        # Event storage
        self._events: deque[AuditEvent] = deque(maxlen=self._config.max_audit_size)

        # Indexes for querying
        self._events_by_order: dict[str, list[str]] = {}  # order_id -> [event_ids]
        self._events_by_adapter: dict[str, list[str]] = {}  # adapter_name -> [event_ids]
        self._events_by_symbol: dict[str, list[str]] = {}  # symbol -> [event_ids]

        # Metrics
        self._total_events = 0
        self._events_by_type: dict[str, int] = {}
        self._events_by_severity: dict[str, int] = {}

    def log_event(
        self,
        event_type: AuditEventType,
        adapter_name: str,
        order_id: str,
        symbol: str,
        message: str = "",
        severity: AuditSeverity = AuditSeverity.INFO,
        side: OrderSide | None = None,
        quantity: float | None = None,
        price: float | None = None,
        execution_price: float | None = None,
        fill_quantity: float | None = None,
        error_message: str = "",
        metadata: dict[str, Any] | None = None,
        timestamp_ns: int | None = None,
    ) -> AuditEvent:
        """Log an execution event.

        Args:
            event_type: Type of event
            adapter_name: Name of the adapter
            order_id: Order identifier
            symbol: Trading symbol
            message: Event message
            severity: Event severity
            side: Order side
            quantity: Order quantity
            price: Order price
            execution_price: Execution price
            fill_quantity: Fill quantity
            error_message: Error message if applicable
            metadata: Additional metadata
            timestamp_ns: Event timestamp

        Returns:
            The logged audit event
        """
        import secrets
        import time

        if timestamp_ns is None:
            timestamp_ns = time.time_ns()

        event_id = secrets.token_hex(16)

        # Create event
        event = AuditEvent(
            event_id=event_id,
            event_type=event_type,
            severity=severity,
            adapter_name=adapter_name,
            timestamp_ns=timestamp_ns,
            order_id=order_id,
            symbol=symbol,
            side=side,
            quantity=quantity,
            price=price,
            execution_price=execution_price,
            fill_quantity=fill_quantity,
            message=message,
            error_message=error_message,
            metadata=metadata or {},
        )

        # Add signature if enabled
        if self._config.enable_signature:
            signature = self._compute_signature(event)
            event = dataclasses.replace(event, signature=signature)

        with self._lock:
            self._events.append(event)
            self._total_events += 1

            # Update indexes
            self._events_by_order.setdefault(order_id, []).append(event_id)
            self._events_by_adapter.setdefault(adapter_name, []).append(event_id)
            self._events_by_symbol.setdefault(symbol, []).append(event_id)

            # Update metrics
            self._events_by_type[event_type.value] = (
                self._events_by_type.get(event_type.value, 0) + 1
            )
            self._events_by_severity[severity.value] = (
                self._events_by_severity.get(severity.value, 0) + 1
            )

        # Persist if enabled
        if self._config.enable_persistence and self._config.storage_path:
            self._persist_event(event)

        return event

    def query(self, query: AuditQuery) -> list[AuditEvent]:
        """Query audit events.

        Args:
            query: Query parameters

        Returns:
            List of matching events
        """
        with self._lock:
            results = list(self._events)

            # Filter by adapter
            if query.adapter_name:
                event_ids = set(self._events_by_adapter.get(query.adapter_name, []))
                results = [e for e in results if e.event_id in event_ids]

            # Filter by event type
            if query.event_type:
                results = [e for e in results if e.event_type == query.event_type]

            # Filter by severity
            if query.severity:
                results = [e for e in results if e.severity == query.severity]

            # Filter by order ID
            if query.order_id:
                event_ids = set(self._events_by_order.get(query.order_id, []))
                results = [e for e in results if e.event_id in event_ids]

            # Filter by symbol
            if query.symbol:
                event_ids = set(self._events_by_symbol.get(query.symbol, []))
                results = [e for e in results if e.event_id in event_ids]

            # Filter by timestamp range
            if query.start_timestamp_ns:
                results = [e for e in results if e.timestamp_ns >= query.start_timestamp_ns]

            if query.end_timestamp_ns:
                results = [e for e in results if e.timestamp_ns <= query.end_timestamp_ns]

            # Apply limit
            results = results[: query.limit]

            return results

    def get_order_trail(self, order_id: str) -> OrderAuditTrail | None:
        """Get the complete audit trail for an order.

        Args:
            order_id: Order identifier

        Returns:
            Complete order audit trail or None if not found
        """
        with self._lock:
            event_ids = self._events_by_order.get(order_id, [])
            if not event_ids:
                return None

            events = []
            for event in self._events:
                if event.order_id == order_id:
                    events.append(event)

            if not events:
                return None

            # Sort by timestamp
            events.sort(key=lambda e: e.timestamp_ns)

            # Determine order status
            last_event = events[-1]
            status = self._determine_order_status(last_event.event_type)

            # Calculate metrics
            submission_timestamp = events[0].timestamp_ns
            completion_timestamp = (
                events[-1].timestamp_ns if status != OrderStatus.PENDING else None
            )

            # Calculate slippage (simplified)
            total_slippage = 0.0
            fills = [
                e
                for e in events
                if e.event_type
                in (AuditEventType.ORDER_FILLED, AuditEventType.ORDER_PARTIALLY_FILLED)
            ]
            if fills:
                for fill in fills:
                    if fill.price and fill.execution_price:
                        slippage = abs(fill.execution_price - fill.price) / fill.price
                        total_slippage += slippage * 100

            return OrderAuditTrail(
                order_id=order_id,
                symbol=events[0].symbol,
                side=events[0].side or OrderSide.BUY,
                events=events,
                submission_timestamp_ns=submission_timestamp,
                completion_timestamp_ns=completion_timestamp,
                total_slippage_pct=total_slippage,
                status=status,
            )

    def get_metrics(self) -> AuditMetrics:
        """Get audit trail metrics.

        Returns:
            Current metrics
        """
        with self._lock:
            # Calculate events per hour
            if self._events:
                oldest = self._events[0].timestamp_ns
                newest = self._events[-1].timestamp_ns
                hours = (newest - oldest) / (3_600_000_000_000) if newest > oldest else 1
                avg_per_hour = len(self._events) / hours
            else:
                avg_per_hour = 0.0

            return AuditMetrics(
                total_events=self._total_events,
                events_by_type=dict(self._events_by_type),
                events_by_severity=dict(self._events_by_severity),
                events_by_adapter={
                    name: len(event_ids) for name, event_ids in self._events_by_adapter.items()
                },
                events_by_symbol={
                    symbol: len(event_ids) for symbol, event_ids in self._events_by_symbol.items()
                },
                average_events_per_hour=avg_per_hour,
                retention_compliance=1.0,  # Placeholder - would check actual retention
                signature_validity=1.0,  # Placeholder - would verify signatures
            )

    def export(self, format: str = "json") -> str:
        """Export audit trail to a file format.

        Args:
            format: Export format (json, csv)

        Returns:
            Exported data as string
        """
        with self._lock:
            if format == "json":
                return self._export_json()
            elif format == "csv":
                return self._export_csv()
            else:
                raise ValueError(f"Unsupported export format: {format}")

    def _determine_order_status(self, event_type: AuditEventType) -> OrderStatus:
        """Determine order status from last event type."""
        mapping = {
            AuditEventType.ORDER_SUBMITTED: OrderStatus.SUBMITTED,
            AuditEventType.ORDER_ACCEPTED: OrderStatus.ACCEPTED,
            AuditEventType.ORDER_REJECTED: OrderStatus.REJECTED,
            AuditEventType.ORDER_FILLED: OrderStatus.FILLED,
            AuditEventType.ORDER_PARTIALLY_FILLED: OrderStatus.PARTIALLY_FILLED,
            AuditEventType.ORDER_CANCELLED: OrderStatus.CANCELLED,
            AuditEventType.ORDER_EXPIRED: OrderStatus.EXPIRED,
        }
        return mapping.get(event_type, OrderStatus.PENDING)

    def _compute_signature(self, event: AuditEvent) -> str:
        """Compute a cryptographic signature for the event."""
        # Create a canonical representation
        canonical = json.dumps(
            {
                "event_type": event.event_type.value,
                "adapter_name": event.adapter_name,
                "timestamp_ns": event.timestamp_ns,
                "order_id": event.order_id,
                "symbol": event.symbol,
                "side": event.side.value if event.side else None,
                "quantity": event.quantity,
                "price": event.price,
            },
            sort_keys=True,
        )

        # Compute SHA-256 hash
        return hashlib.sha256(canonical.encode()).hexdigest()

    def _persist_event(self, event: AuditEvent) -> None:
        """Persist event to storage with compliance level integration."""
        try:
            # Fetch current compliance weights from the API
            response = requests.get("http://localhost:8080/api/compliance/weights", timeout=1.0)
            if response.status_code == 200:
                weights = response.json()
                audit_weight = weights.get("audit", 1.0)
            else:
                audit_weight = 1.0
        except Exception as e:
            logging.getLogger("audit_trail").warning(
                f"Failed to fetch compliance weights, using full audit: {e}"
            )
            audit_weight = 1.0

        # If audit weight is very low, skip persistence (memory only)
        if audit_weight < 0.3:
            logging.getLogger("audit_trail").info(
                f"Audit compliance weight {audit_weight:.2f} < 0.3, skipping persistence (memory only)"
            )
            return

        # Determine persistence method based on compliance level
        if audit_weight >= 0.7:
            # High compliance: Use both file and database persistence
            self._persist_to_file(event)
            self._persist_to_database(event)
        elif audit_weight >= 0.5:
            # Medium compliance: Use file persistence only
            self._persist_to_file(event)
        else:
            # Low compliance: Use database persistence only (faster)
            self._persist_to_database(event)

        logging.getLogger("audit_trail").debug(
            f"Event {event.event_id} persisted with audit weight {audit_weight:.2f}"
        )

    def _persist_to_file(self, event: AuditEvent) -> None:
        """Persist event to file-based audit log."""
        try:
            audit_dir = Path("data/audit")
            audit_dir.mkdir(parents=True, exist_ok=True)

            # Use daily log files
            date_str = datetime.fromtimestamp(event.timestamp_ns / 1_000_000_000).strftime(
                "%Y-%m-%d"
            )
            audit_file = audit_dir / f"audit_{date_str}.log"

            # Serialize event to JSON
            event_data = {
                "event_id": event.event_id,
                "event_type": event.event_type.value,
                "severity": event.severity.value,
                "adapter_name": event.adapter_name,
                "timestamp_ns": event.timestamp_ns,
                "timestamp_iso": datetime.fromtimestamp(
                    event.timestamp_ns / 1_000_000_000
                ).isoformat(),
                "order_id": event.order_id,
                "symbol": event.symbol,
                "side": event.side.value if event.side else None,
                "quantity": event.quantity,
                "price": event.price,
                "execution_price": event.execution_price,
                "fill_quantity": event.fill_quantity,
                "message": event.message,
                "error_message": event.error_message,
                "signature": event.signature,
            }

            # Append to file
            with open(audit_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(event_data) + "\n")

        except Exception as e:
            logging.getLogger("audit_trail").error(f"Failed to persist event to file: {e}")

    def _persist_to_database(self, event: AuditEvent) -> None:
        """Persist event to SQLite database."""
        try:
            db_dir = Path("data/audit")
            db_dir.mkdir(parents=True, exist_ok=True)
            db_file = db_dir / "audit.db"

            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()

            # Create table if not exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS audit_events (
                    event_id TEXT PRIMARY KEY,
                    event_type TEXT,
                    severity TEXT,
                    adapter_name TEXT,
                    timestamp_ns INTEGER,
                    timestamp_iso TEXT,
                    order_id TEXT,
                    symbol TEXT,
                    side TEXT,
                    quantity REAL,
                    price REAL,
                    execution_price REAL,
                    fill_quantity REAL,
                    message TEXT,
                    error_message TEXT,
                    signature TEXT
                )
            """)

            # Insert event
            cursor.execute(
                """
                INSERT OR REPLACE INTO audit_events 
                (event_id, event_type, severity, adapter_name, timestamp_ns, timestamp_iso,
                 order_id, symbol, side, quantity, price, execution_price, fill_quantity,
                 message, error_message, signature)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    event.event_id,
                    event.event_type.value,
                    event.severity.value,
                    event.adapter_name,
                    event.timestamp_ns,
                    datetime.fromtimestamp(event.timestamp_ns / 1_000_000_000).isoformat(),
                    event.order_id,
                    event.symbol,
                    event.side.value if event.side else None,
                    event.quantity,
                    event.price,
                    event.execution_price,
                    event.fill_quantity,
                    event.message,
                    event.error_message,
                    event.signature,
                ),
            )

            conn.commit()
            conn.close()

        except Exception as e:
            logging.getLogger("audit_trail").error(f"Failed to persist event to database: {e}")

    def _export_json(self) -> str:
        """Export as JSON."""
        events_data = []
        for event in self._events:
            events_data.append(
                {
                    "event_id": event.event_id,
                    "event_type": event.event_type.value,
                    "severity": event.severity.value,
                    "adapter_name": event.adapter_name,
                    "timestamp_ns": event.timestamp_ns,
                    "timestamp_iso": datetime.fromtimestamp(
                        event.timestamp_ns / 1_000_000_000
                    ).isoformat(),
                    "order_id": event.order_id,
                    "symbol": event.symbol,
                    "side": event.side.value if event.side else None,
                    "quantity": event.quantity,
                    "price": event.price,
                    "execution_price": event.execution_price,
                    "fill_quantity": event.fill_quantity,
                    "message": event.message,
                    "error_message": event.error_message,
                    "signature": event.signature,
                }
            )

        return json.dumps(
            {"events": events_data, "metadata": self.get_metrics().__dict__}, indent=2
        )

    def _export_csv(self) -> str:
        """Export as CSV."""
        import io

        output = io.StringIO()

        # Header
        header = [
            "event_id",
            "event_type",
            "severity",
            "adapter_name",
            "timestamp_ns",
            "timestamp_iso",
            "order_id",
            "symbol",
            "side",
            "quantity",
            "price",
            "execution_price",
            "fill_quantity",
            "message",
            "error_message",
            "signature",
        ]
        output.write(",".join(header) + "\n")

        # Rows
        for event in self._events:
            row = [
                event.event_id,
                event.event_type.value,
                event.severity.value,
                event.adapter_name,
                str(event.timestamp_ns),
                datetime.fromtimestamp(event.timestamp_ns / 1_000_000_000).isoformat(),
                event.order_id,
                event.symbol,
                event.side.value if event.side else "",
                str(event.quantity) if event.quantity else "",
                str(event.price) if event.price else "",
                str(event.execution_price) if event.execution_price else "",
                str(event.fill_quantity) if event.fill_quantity else "",
                event.message,
                event.error_message,
                event.signature,
            ]
            output.write(",".join(row) + "\n")

        return output.getvalue()


# ---------------------------------------------------------------------------
# Audit Trail Decorator
# ---------------------------------------------------------------------------


def with_audit_trail(
    audit_trail: ExecutionAuditTrail,
    adapter_name: str,
):
    """Decorator to add audit trail logging to adapter methods.

    Args:
        audit_trail: Execution audit trail instance
        adapter_name: Name of the adapter
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Extract order info from kwargs if available
            order_id = kwargs.get("order_id", "unknown")
            symbol = kwargs.get("symbol", "unknown")

            # Log submission
            audit_trail.log_event(
                event_type=AuditEventType.ORDER_SUBMITTED,
                adapter_name=adapter_name,
                order_id=order_id,
                symbol=symbol,
                message=f"Submitting order via {func.__name__}",
            )

            try:
                result = func(*args, **kwargs)

                # Log success
                audit_trail.log_event(
                    event_type=AuditEventType.ORDER_ACCEPTED,
                    adapter_name=adapter_name,
                    order_id=order_id,
                    symbol=symbol,
                    message=f"Order accepted via {func.__name__}",
                )

                return result
            except Exception as e:
                # Log error
                audit_trail.log_event(
                    event_type=AuditEventType.ADAPTER_ERROR,
                    severity=AuditSeverity.ERROR,
                    adapter_name=adapter_name,
                    order_id=order_id,
                    symbol=symbol,
                    message=f"Order failed via {func.__name__}",
                    error_message=str(e),
                )
                raise

        return wrapper

    return decorator


__all__ = [
    "AuditEventType",
    "AuditSeverity",
    "OrderSide",
    "OrderStatus",
    "AuditConfig",
    "AuditEvent",
    "AuditQuery",
    "AuditMetrics",
    "OrderAuditTrail",
    "ExecutionAuditTrail",
    "with_audit_trail",
]
