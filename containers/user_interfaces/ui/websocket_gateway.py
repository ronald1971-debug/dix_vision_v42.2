"""WebSocket Gateway — DASH-06.01.

Unified WebSocket gateway for real-time data streaming to the dashboard.
Consolidates multiple data sources (market data, news, execution events,
governance events, etc.) into a single gateway with standardized protocols,
authentication, and connection management.
"""

from __future__ import annotations

import asyncio
import dataclasses
import enum
import json
import logging
from collections import defaultdict, deque
from collections.abc import Callable
from threading import Lock
from typing import Any, Final

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_MAX_CONNECTIONS: Final[int] = 100
DEFAULT_MESSAGE_QUEUE_SIZE: Final[int] = 1000
DEFAULT_HEARTBEAT_INTERVAL_SEC: Final[int] = 30
DEFAULT_IDLE_TIMEOUT_SEC: Final[int] = 300
DEFAULT_ENABLE_AUTH: Final[bool] = True
DEFAULT_ENABLE_COMPRESSION: Final[bool] = False

NEW_PIP_DEPENDENCIES: Final[tuple[str, ...]] = ()

LOG = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class StreamChannel(enum.Enum):
    """WebSocket stream channels."""
    MARKET_DATA = "MARKET_DATA"
    EXECUTION = "EXECUTION"
    GOVERNANCE = "GOVERNANCE"
    INTELLIGENCE = "INTELLIGENCE"
    LEARNING = "LEARNING"
    SYSTEM = "SYSTEM"
    NEWS = "NEWS"
    ON_CHAIN = "ON_CHAIN"
    PORTFOLIO = "PORTFOLIO"
    RISK = "RISK"
    ALERTS = "ALERTS"


class MessagePriority(enum.Enum):
    """Priority levels for messages."""
    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ConnectionStatus(enum.Enum):
    """Status of WebSocket connections."""
    CONNECTING = "CONNECTING"
    CONNECTED = "CONNECTED"
    DISCONNECTED = "DISCONNECTED"
    ERROR = "ERROR"
    AUTHENTICATED = "AUTHENTICATED"


class GatewayEventType(enum.Enum):
    """Types of gateway events."""
    SUBSCRIPTION = "SUBSCRIPTION"
    UNSUBSCRIPTION = "UNSUBSCRIPTION"
    CONNECTION_OPENED = "CONNECTION_OPENED"
    CONNECTION_CLOSED = "CONNECTION_CLOSED"
    AUTHENTICATION_SUCCESS = "AUTHENTICATION_SUCCESS"
    AUTHENTICATION_FAILURE = "AUTHENTICATION_FAILURE"
    MESSAGE_PUBLISHED = "MESSAGE_PUBLISHED"
    ERROR = "ERROR"


# ---------------------------------------------------------------------------
# Value objects
# ---------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True, slots=True)
class GatewayConfig:
    """Configuration for the WebSocket gateway."""
    max_connections: int = DEFAULT_MAX_CONNECTIONS
    message_queue_size: int = DEFAULT_MESSAGE_QUEUE_SIZE
    heartbeat_interval_sec: int = DEFAULT_HEARTBEAT_INTERVAL_SEC
    idle_timeout_sec: int = DEFAULT_IDLE_TIMEOUT_SEC
    enable_auth: bool = DEFAULT_ENABLE_AUTH
    enable_compression: bool = DEFAULT_ENABLE_COMPRESSION
    enable_metrics: bool = True
    allowed_origins: list[str] = dataclasses.field(default_factory=list)
    rate_limit_per_minute: int = 60

    def __post_init__(self) -> None:
        if self.max_connections < 1:
            raise ValueError("max_connections must be >= 1")
        if self.message_queue_size < 1:
            raise ValueError("message_queue_size must be >= 1")
        if self.heartbeat_interval_sec < 1:
            raise ValueError("heartbeat_interval_sec must be >= 1")
        if self.idle_timeout_sec < 1:
            raise ValueError("idle_timeout_sec must be >= 1")


@dataclasses.dataclass(frozen=True, slots=True)
class StreamMessage:
    """A message to be streamed over WebSocket."""
    channel: StreamChannel
    data: dict[str, Any]
    priority: MessagePriority = MessagePriority.NORMAL
    timestamp_ns: int = 0
    message_id: str = ""
    correlation_id: str = ""

    def __post_init__(self) -> None:
        if self.timestamp_ns == 0:
            import time
            object.__setattr__(self, 'timestamp_ns', time.time_ns())
        if not self.message_id:
            import secrets
            object.__setattr__(self, 'message_id', secrets.token_hex(16))


@dataclasses.dataclass(frozen=True, slots=True)
class Subscription:
    """A client subscription to a channel."""
    client_id: str
    channel: StreamChannel
    filters: dict[str, Any]
    subscribed_at_ns: int


@dataclasses.dataclass(frozen=True, slots=True)
class ClientConnection:
    """A WebSocket client connection."""
    client_id: str
    websocket: Any  # WebSocket connection object
    status: ConnectionStatus
    authenticated: bool = False
    user_id: str = ""
    subscribed_channels: set[StreamChannel] = dataclasses.field(default_factory=set)
    connected_at_ns: int = 0
    last_activity_ns: int = 0
    metadata: dict[str, Any] = dataclasses.field(default_factory=dict)


@dataclasses.dataclass(frozen=True, slots=True)
class GatewayMetrics:
    """Metrics about the gateway performance."""
    total_connections: int
    active_connections: int
    total_messages: int
    messages_by_channel: dict[str, int]
    messages_by_priority: dict[str, int]
    total_subscriptions: int
    active_subscriptions: int
    subscriptions_by_channel: dict[str, int]
    average_message_latency_ms: float
    authentication_successes: int
    authentication_failures: int
    connection_errors: int


# ---------------------------------------------------------------------------
# WebSocket Gateway
# ---------------------------------------------------------------------------


class WebSocketGateway:
    """Unified WebSocket gateway for real-time data streaming.
    
    Provides a single entry point for all real-time data feeds including:
    - Market data (tickers, order books, trades)
    - Execution events (orders, fills, cancellations)
    - Governance events (approvals, risk decisions, mode changes)
    - Intelligence events (signals, strategy updates)
    - Learning events (model updates, training progress)
    - System events (health, errors, warnings)
    - News and on-chain events
    - Portfolio and risk updates
    - Alerts and notifications
    
    The gateway handles connection management, authentication,
    subscription management, message routing, and provides
    comprehensive metrics for monitoring.
    """
    
    def __init__(
        self,
        config: GatewayConfig | None = None,
    ) -> None:
        """Initialize the WebSocket gateway.
        
        Args:
            config: Gateway configuration
        """
        self._config = config or GatewayConfig()
        self._lock = Lock()
        
        # Connection management
        self._connections: dict[str, ClientConnection] = {}
        self._subscriptions: dict[str, list[Subscription]] = defaultdict(list)  # channel -> subscriptions
        
        # Message queues by priority
        self._message_queues: dict[MessagePriority, deque[StreamMessage]] = {
            priority: deque(maxlen=self._config.message_queue_size)
            for priority in MessagePriority
        }
        
        # Event handlers
        self._event_handlers: list[Callable[[GatewayEventType, dict[str, Any]], None]] = []
        
        # Channel data sources
        self._data_sources: dict[StreamChannel, Callable[[], Any]] = {}
        
        # Metrics
        self._metrics = self._init_metrics()
        self._message_latencies: deque[int] = deque(maxlen=100)
        
        # Background task
        self._running = False
        self._broadcast_task: asyncio.Task | None = None
    
    async def start(self) -> None:
        """Start the gateway background tasks."""
        self._running = True
        self._broadcast_task = asyncio.create_task(self._broadcast_loop())
        LOG.info("WebSocket gateway started")
    
    async def stop(self) -> None:
        """Stop the gateway background tasks."""
        self._running = False
        if self._broadcast_task:
            self._broadcast_task.cancel()
            try:
                await self._broadcast_task
            except asyncio.CancelledError:
                pass
        LOG.info("WebSocket gateway stopped")
    
    def register_connection(
        self,
        client_id: str,
        websocket: Any,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Register a new WebSocket connection.
        
        Args:
            client_id: Unique client identifier
            websocket: WebSocket connection object
            metadata: Additional connection metadata
        """
        import time
        
        with self._lock:
            if len(self._connections) >= self._config.max_connections:
                raise RuntimeError("Maximum connections reached")
            
            connection = ClientConnection(
                client_id=client_id,
                websocket=websocket,
                status=ConnectionStatus.CONNECTED,
                connected_at_ns=time.time_ns(),
                last_activity_ns=time.time_ns(),
                metadata=metadata or {},
            )
            
            self._connections[client_id] = connection
            self._metrics.total_connections += 1
            self._metrics.active_connections += 1
            
            self._emit_event(GatewayEventType.CONNECTION_OPENED, {
                "client_id": client_id,
            })
    
    def unregister_connection(self, client_id: str) -> None:
        """Unregister a WebSocket connection.
        
        Args:
            client_id: Client identifier to remove
        """
        with self._lock:
            if client_id in self._connections:
                # Remove subscriptions
                connection = self._connections[client_id]
                for channel in connection.subscribed_channels:
                    self._subscriptions[channel] = [
                        sub for sub in self._subscriptions[channel]
                        if sub.client_id != client_id
                    ]
                
                # Remove connection
                del self._connections[client_id]
                self._metrics.active_connections -= 1
                
                self._emit_event(GatewayEventType.CONNECTION_CLOSED, {
                    "client_id": client_id,
                })
    
    def authenticate(
        self,
        client_id: str,
        token: str,
        user_id: str = "",
    ) -> bool:
        """Authenticate a WebSocket connection.
        
        Args:
            client_id: Client identifier
            token: Authentication token
            user_id: User identifier
            
        Returns:
            True if authentication successful
        """
        import time
        
        if not self._config.enable_auth:
            return True
        
        with self._lock:
            connection = self._connections.get(client_id)
            if not connection:
                return False
            
            # Simple token validation (production would use proper JWT/cookie validation)
            if token and len(token) > 10:
                updated_connection = dataclasses.replace(
                    connection,
                    authenticated=True,
                    status=ConnectionStatus.AUTHENTICATED,
                    user_id=user_id,
                    last_activity_ns=time.time_ns(),
                )
                self._connections[client_id] = updated_connection
                
                self._metrics.authentication_successes += 1
                self._emit_event(GatewayEventType.AUTHENTICATION_SUCCESS, {
                    "client_id": client_id,
                    "user_id": user_id,
                })
                return True
            else:
                self._metrics.authentication_failures += 1
                self._emit_event(GatewayEventType.AUTHENTICATION_FAILURE, {
                    "client_id": client_id,
                })
                return False
    
    def subscribe(
        self,
        client_id: str,
        channel: StreamChannel,
        filters: dict[str, Any] | None = None,
    ) -> bool:
        """Subscribe a client to a channel.
        
        Args:
            client_id: Client identifier
            channel: Channel to subscribe to
            filters: Optional filters for the subscription
            
        Returns:
            True if subscription successful
        """
        import time
        
        with self._lock:
            connection = self._connections.get(client_id)
            if not connection:
                return False
            
            if not connection.authenticated and self._config.enable_auth:
                return False
            
            # Add subscription
            subscription = Subscription(
                client_id=client_id,
                channel=channel,
                filters=filters or {},
                subscribed_at_ns=time.time_ns(),
            )
            
            self._subscriptions[channel].append(subscription)
            connection.subscribed_channels.add(channel)
            
            # Update metrics
            self._metrics.total_subscriptions += 1
            self._metrics.active_subscriptions += 1
            self._metrics.subscriptions_by_channel[channel.value] = \
                self._metrics.subscriptions_by_channel.get(channel.value, 0) + 1
            
            self._emit_event(GatewayEventType.SUBSCRIPTION, {
                "client_id": client_id,
                "channel": channel.value,
            })
            
            return True
    
    def unsubscribe(
        self,
        client_id: str,
        channel: StreamChannel,
    ) -> bool:
        """Unsubscribe a client from a channel.
        
        Args:
            client_id: Client identifier
            channel: Channel to unsubscribe from
            
        Returns:
            True if unsubscription successful
        """
        with self._lock:
            connection = self._connections.get(client_id)
            if not connection:
                return False
            
            # Remove subscription
            self._subscriptions[channel] = [
                sub for sub in self._subscriptions[channel]
                if sub.client_id != client_id
            ]
            
            if channel in connection.subscribed_channels:
                connection.subscribed_channels.remove(channel)
                self._metrics.active_subscriptions -= 1
            
            self._emit_event(GatewayEventType.UNSUBSCRIPTION, {
                "client_id": client_id,
                "channel": channel.value,
            })
            
            return True
    
    def publish(
        self,
        message: StreamMessage,
    ) -> None:
        """Publish a message to a channel.
        
        Args:
            message: Message to publish
        """
        with self._lock:
            # Add to appropriate priority queue
            queue = self._message_queues[message.priority]
            queue.append(message)
            
            # Update metrics
            self._metrics.total_messages += 1
            self._metrics.messages_by_channel[message.channel.value] = \
                self._metrics.messages_by_channel.get(message.channel.value, 0) + 1
            self._metrics.messages_by_priority[message.priority.value] = \
                self._metrics.messages_by_priority.get(message.priority.value, 0) + 1
    
    def register_data_source(
        self,
        channel: StreamChannel,
        data_source: Callable[[], Any],
    ) -> None:
        """Register a data source for a channel.
        
        Args:
            channel: Channel to provide data for
            data_source: Callable that returns data
        """
        with self._lock:
            self._data_sources[channel] = data_source
    
    def register_event_handler(
        self,
        handler: Callable[[GatewayEventType, dict[str, Any]], None],
    ) -> None:
        """Register an event handler.
        
        Args:
            handler: Event handler callable
        """
        with self._lock:
            self._event_handlers.append(handler)
    
    def get_metrics(self) -> GatewayMetrics:
        """Get gateway metrics.
        
        Returns:
            Current metrics
        """
        with self._lock:
            # Calculate average latency
            avg_latency = 0.0
            if self._message_latencies:
                avg_latency = sum(self._message_latencies) / len(self._message_latencies)
            
            return GatewayMetrics(
                total_connections=self._metrics.total_connections,
                active_connections=self._metrics.active_connections,
                total_messages=self._metrics.total_messages,
                messages_by_channel=dict(self._metrics.messages_by_channel),
                messages_by_priority=dict(self._metrics.messages_by_priority),
                total_subscriptions=self._metrics.total_subscriptions,
                active_subscriptions=self._metrics.active_subscriptions,
                subscriptions_by_channel=dict(self._metrics.subscriptions_by_channel),
                average_message_latency_ms=avg_latency,
                authentication_successes=self._metrics.authentication_successes,
                authentication_failures=self._metrics.authentication_failures,
                connection_errors=self._metrics.connection_errors,
            )
    
    async def _broadcast_loop(self) -> None:
        """Background task to broadcast messages to subscribed clients."""
        while self._running:
            try:
                # Process messages in priority order (CRITICAL -> HIGH -> NORMAL -> LOW)
                priorities = [MessagePriority.CRITICAL, MessagePriority.HIGH, 
                            MessagePriority.NORMAL, MessagePriority.LOW]
                
                for priority in priorities:
                    queue = self._message_queues[priority]
                    if queue:
                        message = queue.popleft()
                        await self._broadcast_message(message)
                
                await asyncio.sleep(0.01)  # Small delay to prevent busy waiting
                
            except Exception as e:
                LOG.error(f"Error in broadcast loop: {e}")
                await asyncio.sleep(1)
    
    async def _broadcast_message(self, message: StreamMessage) -> None:
        """Broadcast a message to subscribed clients.
        
        Args:
            message: Message to broadcast
        """
        import time
        
        start_ns = time.time_ns()
        
        # Get subscriptions for the channel
        subscriptions = self._subscriptions.get(message.channel, [])
        
        for subscription in subscriptions:
            try:
                connection = self._connections.get(subscription.client_id)
                if not connection or not connection.websocket:
                    continue
                
                # Apply filters
                if subscription.filters:
                    if not self._apply_filters(message.data, subscription.filters):
                        continue
                
                # Send message
                payload = {
                    "channel": message.channel.value,
                    "priority": message.priority.value,
                    "timestamp_ns": message.timestamp_ns,
                    "message_id": message.message_id,
                    "correlation_id": message.correlation_id,
                    "data": message.data,
                }
                
                # Convert to JSON
                json_payload = json.dumps(payload)
                
                # Send via WebSocket (placeholder - actual implementation depends on WebSocket library)
                # await connection.websocket.send_text(json_payload)
                
                # Update activity
                updated_connection = dataclasses.replace(
                    connection,
                    last_activity_ns=time.time_ns(),
                )
                self._connections[subscription.client_id] = updated_connection
                
            except Exception as e:
                LOG.error(f"Error broadcasting to client {subscription.client_id}: {e}")
                self._metrics.connection_errors += 1
        
        # Track latency
        latency_ms = (time.time_ns() - start_ns) / 1_000_000
        self._message_latencies.append(latency_ms)
    
    def _apply_filters(
        self,
        data: dict[str, Any],
        filters: dict[str, Any],
    ) -> bool:
        """Apply filters to determine if data matches subscription.
        
        Args:
            data: Message data
            filters: Filter criteria
            
        Returns:
            True if data matches filters
        """
        # Simple filter matching (can be extended)
        for key, value in filters.items():
            if key in data and data[key] != value:
                return False
        return True
    
    def _emit_event(
        self,
        event_type: GatewayEventType,
        payload: dict[str, Any],
    ) -> None:
        """Emit a gateway event to handlers.
        
        Args:
            event_type: Type of event
            payload: Event payload
        """
        for handler in self._event_handlers:
            try:
                handler(event_type, payload)
            except Exception as e:
                LOG.error(f"Error in event handler: {e}")
    
    def _init_metrics(self) -> GatewayMetrics:
        """Initialize gateway metrics."""
        return GatewayMetrics(
            total_connections=0,
            active_connections=0,
            total_messages=0,
            messages_by_channel={},
            messages_by_priority={},
            total_subscriptions=0,
            active_subscriptions=0,
            subscriptions_by_channel={},
            average_message_latency_ms=0.0,
            authentication_successes=0,
            authentication_failures=0,
            connection_errors=0,
        )


# ---------------------------------------------------------------------------
# Gateway Factory
# ---------------------------------------------------------------------------


class WebSocketGatewayFactory:
    """Factory for creating and managing WebSocket gateways."""
    
    _instance: WebSocketGateway | None = None
    _lock = Lock()
    
    @classmethod
    def get_instance(
        cls,
        config: GatewayConfig | None = None,
    ) -> WebSocketGateway:
        """Get or create the singleton gateway instance.
        
        Args:
            config: Gateway configuration
            
        Returns:
            Gateway instance
        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = WebSocketGateway(config)
        return cls._instance
    
    @classmethod
    def reset(cls) -> None:
        """Reset the singleton instance (for testing)."""
        with cls._lock:
            cls._instance = None


__all__ = [
    "StreamChannel",
    "MessagePriority",
    "ConnectionStatus",
    "GatewayEventType",
    "GatewayConfig",
    "StreamMessage",
    "Subscription",
    "ClientConnection",
    "GatewayMetrics",
    "WebSocketGateway",
    "WebSocketGatewayFactory",
]
