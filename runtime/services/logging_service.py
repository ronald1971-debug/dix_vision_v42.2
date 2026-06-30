"""
DIX VISION Enhanced Logging Service

Provides structured logging, log aggregation, analysis, pattern detection,
and log-based metrics extraction for enhanced system observability.
"""

from __future__ import annotations

import json
import logging
import logging.handlers
import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple
from collections import defaultdict, deque
from datetime import datetime
import re

from runtime.event_bus import EventBus, Event, EventType, get_event_bus
from runtime.service_manager import Service, ServiceState, ServiceHealth

logger = logging.getLogger(__name__)


class LogLevel(Enum):
    """Log levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogFormat(Enum):
    """Log formats."""
    STRUCTURED = "structured"
    TEXT = "text"
    JSON = "json"


@dataclass
class LogEntry:
    """Structured log entry."""
    timestamp: float
    level: LogLevel
    logger_name: str
    message: str
    context: Dict[str, Any] = field(default_factory=dict)
    service: str = ""
    trace_id: str = ""
    span_id: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert log entry to dictionary."""
        return {
            "timestamp": self.timestamp,
            "datetime": datetime.fromtimestamp(self.timestamp).isoformat(),
            "level": self.level.value,
            "logger": self.logger_name,
            "message": self.message,
            "context": self.context,
            "service": self.service,
            "trace_id": self.trace_id,
            "span_id": self.span_id
        }
    
    def to_json(self) -> str:
        """Convert log entry to JSON string."""
        return json.dumps(self.to_dict())


@dataclass
class LogPattern:
    """Log pattern for analysis."""
    pattern_id: str
    regex: str
    description: str
    severity: LogLevel = LogLevel.INFO
    action: str = "log"  # log, alert, block


@dataclass
class LogStats:
    """Logging statistics."""
    total_logs: int = 0
    logs_by_level: Dict[str, int] = field(default_factory=dict)
    logs_by_service: Dict[str, int] = field(default_factory=dict)
    logs_per_second: float = 0.0
    error_rate: float = 0.0
    pattern_matches: Dict[str, int] = field(default_factory=dict)


class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured logging."""
    
    def __init__(self, service_name: str = ""):
        super().__init__()
        self.service_name = service_name
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as structured JSON."""
        log_entry = LogEntry(
            timestamp=record.created,
            level=LogLevel(record.levelname),
            logger_name=record.name,
            message=record.getMessage(),
            context=getattr(record, 'context', {}),
            service=self.service_name,
            trace_id=getattr(record, 'trace_id', ''),
            span_id=getattr(record, 'span_id', '')
        )
        return log_entry.to_json()


class LoggingService(Service):
    """Enhanced logging service as per Runtime Specification."""
    
    # Service dependencies
    DEPENDENCIES = []
    
    def __init__(self):
        super().__init__("logging_service")
        self._log_entries: deque = deque(maxlen=100000)
        self._log_aggregates: Dict[str, List[LogEntry]] = defaultdict(list)
        self._patterns: Dict[str, LogPattern] = {}
        self._stats = LogStats()
        self._lock = threading.Lock()
        self._log_handlers: Dict[str, logging.Handler] = {}
        self._retention_hours = 24
        self._pattern_compiled: Dict[str, re.Pattern] = {}
        
    def init(self, event_bus: EventBus, config: Dict[str, Any]) -> bool:
        """Initialize the logging service."""
        try:
            self.event_bus = event_bus
            self.state = ServiceState.INITIALIZING
            
            # Load configuration
            logging_config = config.get("logging", {})
            self._retention_hours = logging_config.get("retention_hours", 24)
            
            # Initialize default patterns
            self._init_default_patterns()
            
            # Setup structured logging
            self._setup_structured_logging(logging_config)
            
            logger.info("Logging Service initialized")
            return True
        except Exception as e:
            logger.error(f"Logging Service initialization failed: {e}")
            self.state = ServiceState.ERROR
            return False
    
    def start(self) -> bool:
        """Start the logging service."""
        try:
            self.state = ServiceState.STARTING
            
            # Start background log analyzer
            self._start_log_analyzer()
            
            # Start background log cleanup
            self._start_log_cleanup()
            
            # Start background stats collector
            self._start_stats_collector()
            
            self.state = ServiceState.RUNNING
            self.emit_event(str(EventType.SERVICE_START), {"service": self.name})
            logger.info("Logging Service started")
            return True
        except Exception as e:
            logger.error(f"Logging Service start failed: {e}")
            self.state = ServiceState.ERROR
            self.emit_event(str(EventType.SERVICE_CRASH), {"service": self.name, "error": str(e)})
            return False
    
    def stop(self) -> bool:
        """Stop the logging service."""
        try:
            self.state = ServiceState.STOPPING
            
            # Close all handlers
            for handler in self._log_handlers.values():
                handler.close()
            
            self.state = ServiceState.STOPPED
            self.emit_event(str(EventType.SERVICE_STOP), {"service": self.name})
            logger.info("Logging Service stopped")
            return True
        except Exception as e:
            logger.error(f"Logging Service stop failed: {e}")
            self.state = ServiceState.ERROR
            return False
    
    def health(self) -> ServiceHealth:
        """Get logging service health."""
        return ServiceHealth(
            service=self.name,
            state=self.state,
            healthy=self.state == ServiceState.RUNNING,
            message=f"Logging Service - {self._stats.total_logs} total logs",
            details={
                "total_logs": self._stats.total_logs,
                "logs_per_second": self._stats.logs_per_second,
                "error_rate": self._stats.error_rate,
                "logs_by_level": self._stats.logs_by_level,
                "logs_by_service": self._stats.logs_by_service,
                "active_patterns": len(self._patterns),
                "log_entries_size": len(self._log_entries)
            },
            timestamp=time.time()
        )
    
    def log(self, level: LogLevel, message: str, context: Dict[str, Any] = None, 
            service: str = "", trace_id: str = "", span_id: str = "") -> None:
        """Log a structured entry."""
        log_entry = LogEntry(
            timestamp=time.time(),
            level=level,
            logger_name="dix_vision",
            message=message,
            context=context or {},
            service=service,
            trace_id=trace_id,
            span_id=span_id
        )
        
        with self._lock:
            self._log_entries.append(log_entry)
            self._stats.total_logs += 1
            self._stats.logs_by_level[level.value] = self._stats.logs_by_level.get(level.value, 0) + 1
            if service:
                self._stats.logs_by_service[service] = self._stats.logs_by_service.get(service, 0) + 1
            
            # Aggregate by service
            if service:
                self._log_aggregates[service].append(log_entry)
                if len(self._log_aggregates[service]) > 10000:
                    self._log_aggregates[service] = self._log_aggregates[service][-10000:]
        
        # Check patterns
        self._check_patterns(log_entry)
    
    def register_pattern(self, pattern: LogPattern) -> None:
        """Register a log pattern for analysis."""
        with self._lock:
            self._patterns[pattern.pattern_id] = pattern
            try:
                self._pattern_compiled[pattern.pattern_id] = re.compile(pattern.regex)
            except re.error as e:
                logger.error(f"Invalid regex pattern {pattern.pattern_id}: {e}")
    
    def query_logs(self, service: str = "", level: LogLevel = None, 
                   start_time: float = None, end_time: float = None,
                   pattern: str = "") -> List[LogEntry]:
        """Query logs with filters."""
        with self._lock:
            results = []
            
            for entry in self._log_entries:
                # Service filter
                if service and entry.service != service:
                    continue
                
                # Level filter
                if level and entry.level != level:
                    continue
                
                # Time filter
                if start_time and entry.timestamp < start_time:
                    continue
                if end_time and entry.timestamp > end_time:
                    continue
                
                # Pattern filter
                if pattern and pattern not in entry.message:
                    continue
                
                results.append(entry)
            
            return results
    
    def get_log_stats(self) -> LogStats:
        """Get logging statistics."""
        with self._lock:
            return self._stats
    
    def get_service_logs(self, service: str, limit: int = 100) -> List[LogEntry]:
        """Get recent logs for a specific service."""
        with self._lock:
            if service not in self._log_aggregates:
                return []
            
            return self._log_aggregates[service][-limit:]
    
    def extract_metrics_from_logs(self) -> Dict[str, Any]:
        """Extract metrics from log entries."""
        with self._lock:
            metrics = {}
            
            # Error rate by service
            error_by_service = defaultdict(int)
            total_by_service = defaultdict(int)
            
            for entry in self._log_entries:
                if entry.service:
                    total_by_service[entry.service] += 1
                    if entry.level in [LogLevel.ERROR, LogLevel.CRITICAL]:
                        error_by_service[entry.service] += 1
            
            for service in total_by_service:
                if total_by_service[service] > 0:
                    metrics[f"{service}_error_rate"] = error_by_service[service] / total_by_service[service]
            
            # Log volume by service
            for service, count in total_by_service.items():
                metrics[f"{service}_log_volume"] = count
            
            return metrics
    
    def _setup_structured_logging(self, config: Dict[str, Any]) -> None:
        """Setup structured logging configuration."""
        # Get root logger
        root_logger = logging.getLogger()
        
        # Create structured formatter
        service_name = config.get("service_name", "dix_vision")
        formatter = StructuredFormatter(service_name)
        
        # Setup console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.DEBUG)
        
        root_logger.addHandler(console_handler)
        self._log_handlers["console"] = console_handler
        
        # Setup file handler if configured
        log_file = config.get("log_file")
        if log_file:
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5
            )
            file_handler.setFormatter(formatter)
            file_handler.setLevel(logging.DEBUG)
            
            root_logger.addHandler(file_handler)
            self._log_handlers["file"] = file_handler
        
        root_logger.setLevel(logging.DEBUG)
    
    def _init_default_patterns(self) -> None:
        """Initialize default log patterns."""
        default_patterns = [
            LogPattern(
                pattern_id="error_pattern",
                regex=r"error|exception|failed",
                description="Error indicators",
                severity=LogLevel.ERROR
            ),
            LogPattern(
                pattern_id="timeout_pattern",
                regex=r"timeout|timed out",
                description="Timeout indicators",
                severity=LogLevel.WARNING
            ),
            LogPattern(
                pattern_id="connection_pattern",
                regex=r"connection|connect",
                description="Connection issues",
                severity=LogLevel.WARNING
            ),
            LogPattern(
                pattern_id="memory_pattern",
                regex=r"memory|out of memory|oom",
                description="Memory issues",
                severity=LogLevel.ERROR
            ),
        ]
        
        for pattern in default_patterns:
            self.register_pattern(pattern)
    
    def _check_patterns(self, entry: LogEntry) -> None:
        """Check log entry against registered patterns."""
        for pattern_id, pattern in self._patterns.items():
            if pattern_id in self._pattern_compiled:
                compiled = self._pattern_compiled[pattern_id]
                if compiled.search(entry.message.lower()):
                    with self._lock:
                        self._stats.pattern_matches[pattern_id] = self._stats.pattern_matches.get(pattern_id, 0) + 1
                    
                    # Take action based on pattern severity
                    if pattern.severity == LogLevel.CRITICAL:
                        self.emit_event(str(EventType.AI_DECISION), {
                            "service": self.name,
                            "pattern_id": pattern_id,
                            "severity": pattern.severity.value,
                            "message": entry.message
                        })
    
    def _start_log_analyzer(self) -> None:
        """Start background log analyzer."""
        def analyze_logs():
            while self.state == ServiceState.RUNNING:
                try:
                    self._analyze_logs()
                    time.sleep(60)  # Analyze every minute
                except Exception as e:
                    logger.error(f"Log analysis error: {e}")
                    time.sleep(30)
        
        thread = threading.Thread(target=analyze_logs, daemon=True)
        thread.start()
        logger.info("Log analyzer started")
    
    def _analyze_logs(self) -> None:
        """Analyze logs for patterns and anomalies."""
        with self._lock:
            if len(self._log_entries) < 100:
                return
            
            recent_logs = list(self._log_entries)[-100:]
            
            # Calculate error rate
            error_count = sum(1 for entry in recent_logs if entry.level in [LogLevel.ERROR, LogLevel.CRITICAL])
            self._stats.error_rate = error_count / len(recent_logs)
    
    def _start_log_cleanup(self) -> None:
        """Start background log cleanup."""
        def cleanup_logs():
            while self.state == ServiceState.RUNNING:
                try:
                    current_time = time.time()
                    cutoff_time = current_time - (self._retention_hours * 3600)
                    
                    with self._lock:
                        # Remove old log entries
                        while self._log_entries and self._log_entries[0].timestamp < cutoff_time:
                            self._log_entries.popleft()
                    
                    time.sleep(300)  # Clean up every 5 minutes
                except Exception as e:
                    logger.error(f"Log cleanup error: {e}")
                    time.sleep(60)
        
        thread = threading.Thread(target=cleanup_logs, daemon=True)
        thread.start()
        logger.info("Log cleanup started")
    
    def _start_stats_collector(self) -> None:
        """Start background stats collector."""
        def collect_stats():
            last_count = 0
            last_time = time.time()
            
            while self.state == ServiceState.RUNNING:
                try:
                    current_time = time.time()
                    with self._lock:
                        current_count = self._stats.total_logs
                    
                    time_diff = current_time - last_time
                    if time_diff > 0:
                        logs_per_second = (current_count - last_count) / time_diff
                        with self._lock:
                            self._stats.logs_per_second = logs_per_second
                    
                    last_count = current_count
                    last_time = current_time
                    time.sleep(10)  # Collect every 10 seconds
                except Exception as e:
                    logger.error(f"Stats collection error: {e}")
                    time.sleep(30)
        
        thread = threading.Thread(target=collect_stats, daemon=True)
        thread.start()
        logger.info("Stats collector started")


# Global instance
_logging_service: Optional[LoggingService] = None


def get_logging_service() -> LoggingService:
    """Get global logging service instance."""
    global _logging_service
    if _logging_service is None:
        _logging_service = LoggingService()
    return _logging_service