"""evolution_engine.dyon.realtime_simulation — Real-time Simulation for DYON System Behavior Modeling.

Real-time simulation capabilities for live system behavior analysis.

This implementation provides real-time simulation capabilities:
- Live data feed integration
- Real-time scenario execution
- Dynamic parameter adjustment
- Live performance monitoring
- Streaming simulation results
- Interactive simulation control
- Real-time anomaly detection
- Live system state prediction

Authority (L2/B1): evolution_engine.* only at module level.
DYON provides real-time system simulation for optimization, never for trading purposes.
"""

from __future__ import annotations

import logging
import math
import queue
import threading
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

_logger = logging.getLogger(__name__)


class SimulationState(Enum):
    """States of real-time simulation."""

    IDLE = "IDLE"
    INITIALIZING = "INITIALIZING"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    STOPPING = "STOPPING"
    ERROR = "ERROR"


class DataFeedType(Enum):
    """Types of data feeds for real-time simulation."""

    SYSTEM_METRICS = "system_metrics"
    APPLICATION_LOGS = "application_logs"
    NETWORK_TRAFFIC = "network_traffic"
    DATABASE_METRICS = "database_metrics"
    USER_ACTIVITY = "user_activity"
    CUSTOM_METRICS = "custom_metrics"


class SimulationEventType(Enum):
    """Types of simulation events."""

    STATE_CHANGE = "state_change"
    DATA_UPDATE = "data_update"
    ANOMALY_DETECTED = "anomaly_detected"
    THRESHOLD_CROSSED = "threshold_crossed"
    PERFORMANCE_ALERT = "performance_alert"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    CUSTOM_EVENT = "custom_event"


@dataclass
class DataFeed:
    """Real-time data feed configuration."""

    feed_id: str
    feed_type: DataFeedType
    source: str
    update_interval: float  # seconds
    is_active: bool = False
    last_update: float = 0.0
    data_buffer: deque = field(default_factory=lambda: deque(maxlen=1000))
    metrics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SimulationEvent:
    """Event from real-time simulation."""

    event_id: str
    event_type: SimulationEventType
    timestamp: float
    severity: str  # info, warning, error, critical
    message: str
    data: Dict[str, Any] = field(default_factory=dict)
    source_component: str = ""


@dataclass
class RealtimeSimulationResult:
    """Result of real-time simulation."""

    simulation_id: str
    start_time: float
    end_time: float
    duration_seconds: float
    state: SimulationState
    events: List[SimulationEvent] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    predictions: List[Dict[str, Any]] = field(default_factory=list)
    anomalies_detected: int = 0
    alerts_generated: int = 0


@dataclass
class SimulationControl:
    """Control parameters for real-time simulation."""

    target_fps: float = 10.0  # frames per second for simulation updates
    time_scale: float = 1.0  # time multiplier (1.0 = real-time, 2.0 = 2x speed)
    enable_predictions: bool = True
    enable_anomaly_detection: bool = True
    enable_alerts: bool = True
    max_duration: float = 3600.0  # maximum simulation duration in seconds


class RealtimeSimulationEngine:
    """Real-time simulation engine for system behavior modeling.

    DYON uses this for real-time system simulation and live behavior analysis
    without performing trading operations.
    """

    def __init__(self, repo_root: str = "."):
        """Initialize real-time simulation engine.

        Args:
            repo_root: Path to repository root
        """
        self.repo_root = repo_root
        self._lock = threading.Lock()
        self._simulation_thread: Optional[threading.Thread] = None
        self._simulation_state = SimulationState.IDLE
        self._data_feeds: Dict[str, DataFeed] = {}
        self._event_queue: queue.Queue = queue.Queue()
        self._event_handlers: Dict[SimulationEventType, List[Callable]] = defaultdict(list)
        self._control_parameters = SimulationControl()
        self._current_simulation_id: Optional[str] = None
        self._simulation_start_time: float = 0.0
        self._simulation_metrics: Dict[str, Any] = {}
        self._live_predictions: List[Dict[str, Any]] = []
        self._anomaly_count: int = 0
        self._alert_count: int = 0

        _logger.info(f"[RealtimeSimulationEngine] Initialized with repo_root={repo_root}")

    def register_data_feed(self, feed: DataFeed) -> bool:
        """Register a data feed for real-time simulation.

        Args:
            feed: Data feed configuration

        Returns:
            True if registration successful
        """
        with self._lock:
            if feed.feed_id in self._data_feeds:
                _logger.warning(
                    f"[RealtimeSimulationEngine] Feed already registered: {feed.feed_id}"
                )
                return False

            self._data_feeds[feed.feed_id] = feed
            _logger.info(f"[RealtimeSimulationEngine] Registered data feed: {feed.feed_id}")

            return True

    def unregister_data_feed(self, feed_id: str) -> bool:
        """Unregister a data feed.

        Args:
            feed_id: Feed identifier

        Returns:
            True if unregistration successful
        """
        with self._lock:
            if feed_id not in self._data_feeds:
                _logger.warning(f"[RealtimeSimulationEngine] Unknown feed: {feed_id}")
                return False

            feed = self._data_feeds[feed_id]
            feed.is_active = False
            del self._data_feeds[feed_id]

            _logger.info(f"[RealtimeSimulationEngine] Unregistered data feed: {feed_id}")

            return True

    def register_event_handler(self, event_type: SimulationEventType, handler: Callable) -> bool:
        """Register an event handler for simulation events.

        Args:
            event_type: Type of event to handle
            handler: Handler function

        Returns:
            True if registration successful
        """
        with self._lock:
            self._event_handlers[event_type].append(handler)
            _logger.info(f"[RealtimeSimulationEngine] Registered handler for {event_type.value}")

            return True

    def start_simulation(self, simulation_id: str = None) -> str:
        """Start real-time simulation.

        Args:
            simulation_id: Optional simulation identifier

        Returns:
            Simulation ID
        """
        with self._lock:
            if self._simulation_state == SimulationState.RUNNING:
                _logger.warning("[RealtimeSimulationEngine] Simulation already running")
                return self._current_simulation_id or "error"

            self._simulation_state = SimulationState.INITIALIZING
            self._current_simulation_id = simulation_id or f"sim_{int(time.time())}"
            self._simulation_start_time = time.time()
            self._anomaly_count = 0
            self._alert_count = 0
            self._live_predictions = []

            _logger.info(
                f"[RealtimeSimulationEngine] Starting simulation: {self._current_simulation_id}"
            )

            # Start simulation thread
            self._simulation_thread = threading.Thread(target=self._simulation_loop, daemon=True)
            self._simulation_thread.start()

            return self._current_simulation_id

    def stop_simulation(self) -> bool:
        """Stop real-time simulation.

        Returns:
            True if stopped successfully
        """
        with self._lock:
            if self._simulation_state != SimulationState.RUNNING:
                _logger.warning("[RealtimeSimulationEngine] Simulation not running")
                return False

            self._simulation_state = SimulationState.STOPPING
            _logger.info(
                f"[RealtimeSimulationEngine] Stopping simulation: {self._current_simulation_id}"
            )

            # Wait for thread to finish
            if self._simulation_thread:
                self._simulation_thread.join(timeout=5.0)

            self._simulation_state = SimulationState.IDLE
            return True

    def pause_simulation(self) -> bool:
        """Pause real-time simulation.

        Returns:
            True if paused successfully
        """
        with self._lock:
            if self._simulation_state != SimulationState.RUNNING:
                _logger.warning("[RealtimeSimulationEngine] Simulation not running")
                return False

            self._simulation_state = SimulationState.PAUSED
            _logger.info(
                f"[RealtimeSimulationEngine] Paused simulation: {self._current_simulation_id}"
            )

            return True

    def resume_simulation(self) -> bool:
        """Resume paused simulation.

        Returns:
            True if resumed successfully
        """
        with self._lock:
            if self._simulation_state != SimulationState.PAUSED:
                _logger.warning("[RealtimeSimulationEngine] Simulation not paused")
                return False

            self._simulation_state = SimulationState.RUNNING
            _logger.info(
                f"[RealtimeSimulationEngine] Resumed simulation: {self._current_simulation_id}"
            )

            return True

    def _simulation_loop(self) -> None:
        """Main simulation loop."""
        try:
            self._simulation_state = SimulationState.RUNNING

            frame_interval = 1.0 / self._control_parameters.target_fps
            last_frame_time = time.time()

            while self._simulation_state == SimulationState.RUNNING:
                # Check for max duration
                if self._control_parameters.max_duration > 0:
                    elapsed = time.time() - self._simulation_start_time
                    if elapsed > self._control_parameters.max_duration:
                        _logger.info(
                            f"[RealtimeSimulationEngine] Max duration reached: {self._control_parameters.max_duration}s"
                        )
                        break

                # Calculate frame timing
                current_time = time.time()
                elapsed_since_last_frame = current_time - last_frame_time

                # Apply time scale
                simulation_time_delta = (
                    elapsed_since_last_frame * self._control_parameters.time_scale
                )

                # Process simulation frame
                self._process_simulation_frame(simulation_time_delta)

                # Update last frame time
                last_frame_time = current_time

                # Sleep to maintain target FPS
                frame_processing_time = time.time() - current_time
                sleep_time = max(0.0, frame_interval - frame_processing_time)
                time.sleep(sleep_time)

            _logger.info(
                f"[RealtimeSimulationEngine] Simulation loop ended: {self._current_simulation_id}"
            )

        except Exception as e:
            _logger.error(f"[RealtimeSimulationEngine] Simulation loop error: {e}")
            self._simulation_state = SimulationState.ERROR

    def _process_simulation_frame(self, time_delta: float) -> None:
        """Process a single simulation frame.

        Args:
            time_delta: Time elapsed since last frame (with time scale applied)
        """
        # Update data feeds
        self._update_data_feeds(time_delta)

        # Collect metrics from all feeds
        current_metrics = self._collect_current_metrics()

        # Update simulation metrics
        self._simulation_metrics.update(current_metrics)

        # Perform anomaly detection if enabled
        if self._control_parameters.enable_anomaly_detection:
            self._detect_anomalies(current_metrics)

        # Generate predictions if enabled
        if self._control_parameters.enable_predictions:
            predictions = self._generate_live_predictions(current_metrics)
            self._live_predictions.append({"timestamp": time.time(), "predictions": predictions})

        # Check thresholds and generate alerts if enabled
        if self._control_parameters.enable_alerts:
            self._check_thresholds(current_metrics)

        # Process queued events
        self._process_events()

    def _update_data_feeds(self, time_delta: float) -> None:
        """Update all active data feeds.

        Args:
            time_delta: Time elapsed since last frame
        """
        current_time = time.time()

        for feed_id, feed in self._data_feeds.items():
            if not feed.is_active:
                continue

            # Check if it's time to update this feed
            if current_time - feed.last_update >= feed.update_interval:
                # Simulate data update (in production, this would read from actual sources)
                new_data = self._generate_feed_data(feed)

                # Add to buffer
                feed.data_buffer.append({"timestamp": current_time, "data": new_data})

                # Update feed metrics
                feed.metrics.update(new_data)
                feed.last_update = current_time

    def _generate_feed_data(self, feed: DataFeed) -> Dict[str, Any]:
        """Generate simulated data for a feed.

        Args:
            feed: Data feed to generate data for

        Returns:
            Generated data
        """
        # Simulate different types of data based on feed type
        if feed.feed_type == DataFeedType.SYSTEM_METRICS:
            return {
                "cpu_usage": 20.0
                + 10.0 * math.sin(time.time() / 10.0)
                + abs(hash(str(time.time())) % 100) / 20.0,
                "memory_usage": 40.0
                + 15.0 * math.cos(time.time() / 15.0)
                + abs(hash(str(time.time())) % 50) / 10.0,
                "disk_usage": 60.0 + 5.0 * math.sin(time.time() / 30.0),
                "network_io": 100.0 + 50.0 * math.sin(time.time() / 5.0),
            }
        elif feed.feed_type == DataFeedType.APPLICATION_LOGS:
            return {
                "log_level": "INFO" if hash(str(time.time())) % 10 > 2 else "WARNING",
                "message_count": int(10 + 5 * math.sin(time.time() / 10.0)),
                "error_count": max(0, int(2 * math.sin(time.time() / 20.0))),
            }
        elif feed.feed_type == DataFeedType.DATABASE_METRICS:
            return {
                "query_count": int(50 + 20 * math.sin(time.time() / 8.0)),
                "avg_query_time": 50.0 + 20.0 * math.cos(time.time() / 12.0),
                "connection_pool_usage": 0.3 + 0.2 * math.sin(time.time() / 15.0),
            }
        else:
            return {"value": 100.0 + 50.0 * math.sin(time.time() / 10.0)}

    def _collect_current_metrics(self) -> Dict[str, Any]:
        """Collect current metrics from all active feeds.

        Returns:
            Current metrics dictionary
        """
        metrics = {}

        for feed_id, feed in self._data_feeds.items():
            if feed.is_active and feed.data_buffer:
                latest_data = feed.data_buffer[-1]["data"]
                for key, value in latest_data.items():
                    metrics[f"{feed_id}_{key}"] = value

        return metrics

    def _detect_anomalies(self, current_metrics: Dict[str, Any]) -> None:
        """Detect anomalies in current metrics.

        Args:
            current_metrics: Current system metrics
        """
        # Simple anomaly detection based on thresholds
        for metric_name, value in current_metrics.items():
            if isinstance(value, (int, float)):
                # Define thresholds (these would be configurable)
                thresholds = {
                    "cpu_usage": 80.0,
                    "memory_usage": 85.0,
                    "disk_usage": 90.0,
                    "error_count": 10,
                    "avg_query_time": 200.0,
                }

                for threshold_key, threshold_value in thresholds.items():
                    if threshold_key in metric_name.lower() and value > threshold_value:
                        self._generate_event(
                            SimulationEventType.ANOMALY_DETECTED,
                            "warning",
                            f"Anomaly detected in {metric_name}: {value:.2f} > {threshold_value}",
                            {"metric": metric_name, "value": value, "threshold": threshold_value},
                        )
                        self._anomaly_count += 1

    def _generate_live_predictions(self, current_metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate live predictions based on current metrics.

        Args:
            current_metrics: Current system metrics

        Returns:
            List of predictions
        """
        predictions = []

        # Simple prediction logic based on trends
        for metric_name, value in current_metrics.items():
            if isinstance(value, (int, float)) and "usage" in metric_name.lower():
                # Predict if usage will exceed threshold in next hour
                predicted_value = value * (1.0 + 0.01)  # Assume 1% growth per frame
                predictions.append(
                    {
                        "metric": metric_name,
                        "current_value": value,
                        "predicted_value": predicted_value,
                        "time_horizon": "1 hour",
                        "confidence": 0.7,
                    }
                )

        return predictions

    def _check_thresholds(self, current_metrics: Dict[str, Any]) -> None:
        """Check metrics against thresholds and generate alerts.

        Args:
            current_metrics: Current system metrics
        """
        # Define alert thresholds
        alert_thresholds = {
            "cpu_usage": 90.0,
            "memory_usage": 95.0,
            "disk_usage": 95.0,
            "error_count": 20,
        }

        for metric_name, value in current_metrics.items():
            if isinstance(value, (int, float)):
                for threshold_key, threshold_value in alert_thresholds.items():
                    if threshold_key in metric_name.lower() and value > threshold_value:
                        self._generate_event(
                            SimulationEventType.PERFORMANCE_ALERT,
                            "error",
                            f"Alert: {metric_name} critical: {value:.2f} > {threshold_value}",
                            {"metric": metric_name, "value": value, "threshold": threshold_value},
                        )
                        self._alert_count += 1

    def _generate_event(
        self,
        event_type: SimulationEventType,
        severity: str,
        message: str,
        data: Dict[str, Any] = None,
    ) -> None:
        """Generate a simulation event.

        Args:
            event_type: Type of event
            severity: Event severity
            message: Event message
            data: Additional event data
        """
        event = SimulationEvent(
            event_id=f"evt_{int(time.time())}_{len(self._live_predictions)}",
            event_type=event_type,
            timestamp=time.time(),
            severity=severity,
            message=message,
            data=data or {},
            source_component="realtime_simulation",
        )

        self._event_queue.put(event)

    def _process_events(self) -> None:
        """Process queued events and call registered handlers."""
        while not self._event_queue.empty():
            try:
                event = self._event_queue.get_nowait()

                # Call registered handlers
                handlers = self._event_handlers.get(event.event_type, [])
                for handler in handlers:
                    try:
                        handler(event)
                    except Exception as e:
                        _logger.error(f"[RealtimeSimulationEngine] Handler error: {e}")

            except queue.Empty:
                break

    def get_simulation_state(self) -> SimulationState:
        """Get current simulation state.

        Returns:
            Current simulation state
        """
        with self._lock:
            return self._simulation_state

    def get_simulation_metrics(self) -> Dict[str, Any]:
        """Get current simulation metrics.

        Returns:
            Simulation metrics
        """
        with self._lock:
            return dict(self._simulation_metrics)

    def get_live_predictions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent live predictions.

        Args:
            limit: Maximum number of predictions to return

        Returns:
            List of predictions
        """
        with self._lock:
            return list(self._live_predictions[-limit:])

    def get_simulation_result(self) -> RealtimeSimulationResult:
        """Get simulation result.

        Returns:
            Simulation result
        """
        with self._lock:
            return RealtimeSimulationResult(
                simulation_id=self._current_simulation_id or "none",
                start_time=self._simulation_start_time,
                end_time=time.time(),
                duration_seconds=(
                    time.time() - self._simulation_start_time
                    if self._simulation_start_time > 0
                    else 0.0
                ),
                state=self._simulation_state,
                metrics=dict(self._simulation_metrics),
                predictions=list(self._live_predictions),
                anomalies_detected=self._anomaly_count,
                alerts_generated=self._alert_count,
            )

    def set_control_parameters(self, parameters: SimulationControl) -> None:
        """Set control parameters for simulation.

        Args:
            parameters: Control parameters
        """
        with self._lock:
            self._control_parameters = parameters
            _logger.info("[RealtimeSimulationEngine] Updated control parameters")


# Singleton instance
_realtime_simulation: Optional[RealtimeSimulationEngine] = None
_simulation_lock = threading.Lock()


def get_realtime_simulation(repo_root: str = ".") -> RealtimeSimulationEngine:
    """Get singleton instance of real-time simulation engine.

    Args:
        repo_root: Path to repository root

    Returns:
        Real-time simulation engine instance
    """
    global _realtime_simulation

    with _simulation_lock:
        if _realtime_simulation is None:
            _realtime_simulation = RealtimeSimulationEngine(repo_root)
        return _realtime_simulation
