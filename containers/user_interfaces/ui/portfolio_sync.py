"""Live Portfolio Sync — DASH-06.02.

Real-time portfolio synchronization system that provides live updates
of positions, balances, P&L, and risk metrics to the dashboard via
the WebSocket gateway. Integrates with execution engines and supports
multi-account portfolio aggregation.
"""

from __future__ import annotations

import dataclasses
import enum
from collections import defaultdict
from collections.abc import Callable
from decimal import Decimal
from threading import Lock
from typing import Any, Final

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_SYNC_INTERVAL_MS: Final[int] = 100  # 100ms sync interval
DEFAULT_ENABLE_AGGREGATION: Final[bool] = True
DEFAULT_ENABLE_PNL_TRACKING: Final[bool] = True
DEFAULT_ENABLE_RISK_SYNC: Final[bool] = True
DEFAULT_HISTORY_SIZE: Final[int] = 1000

NEW_PIP_DEPENDENCIES: Final[tuple[str, ...]] = ()


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class AssetType(enum.Enum):
    """Types of assets in portfolio."""
    CRYPTO = "CRYPTO"
    STOCK = "STOCK"
    FOREX = "FOREX"
    COMMODITY = "COMMODITY"
    CASH = "CASH"
    DERIVATIVE = "DERIVATIVE"


class PositionSide(enum.Enum):
    """Side of a position."""
    LONG = "LONG"
    SHORT = "SHORT"


class SyncEventType(enum.Enum):
    """Types of sync events."""
    POSITION_OPENED = "POSITION_OPENED"
    POSITION_CLOSED = "POSITION_CLOSED"
    POSITION_MODIFIED = "POSITION_MODIFIED"
    BALANCE_CHANGED = "BALANCE_CHANGED"
    PNL_UPDATED = "PNL_UPDATED"
    RISK_UPDATED = "RISK_UPDATED"
    PORTFOLIO_SNAPSHOT = "PORTFOLIO_SNAPSHOT"
    ACCOUNT_ADDED = "ACCOUNT_ADDED"
    ACCOUNT_REMOVED = "ACCOUNT_REMOVED"


# ---------------------------------------------------------------------------
# Value objects
# ---------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True, slots=True)
class PortfolioSyncConfig:
    """Configuration for portfolio synchronization."""
    sync_interval_ms: int = DEFAULT_SYNC_INTERVAL_MS
    enable_aggregation: bool = DEFAULT_ENABLE_AGGREGATION
    enable_pnl_tracking: bool = DEFAULT_ENABLE_PNL_TRACKING
    enable_risk_sync: bool = DEFAULT_ENABLE_RISK_SYNC
    history_size: int = DEFAULT_HISTORY_SIZE
    include_zero_positions: bool = False
    include_closed_positions: bool = False

    def __post_init__(self) -> None:
        if self.sync_interval_ms < 10:
            raise ValueError("sync_interval_ms must be >= 10")
        if self.history_size < 1:
            raise ValueError("history_size must be >= 1")


@dataclasses.dataclass(frozen=True, slots=True)
class Position:
    """A position in the portfolio."""
    account_id: str
    symbol: str
    side: PositionSide
    quantity: Decimal
    entry_price: Decimal
    current_price: Decimal
    unrealized_pnl: Decimal
    realized_pnl: Decimal
    asset_type: AssetType
    opened_at_ns: int
    last_updated_ns: int
    metadata: dict[str, Any] = dataclasses.field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.account_id:
            raise ValueError("account_id must be non-empty")
        if not self.symbol:
            raise ValueError("symbol must be non-empty")


@dataclasses.dataclass(frozen=True, slots=True)
class AccountBalance:
    """Balance information for an account."""
    account_id: str
    base_currency: str
    total_balance: Decimal
    available_balance: Decimal
    locked_balance: Decimal
    unrealized_pnl: Decimal
    realized_pnl: Decimal
    last_updated_ns: int
    metadata: dict[str, Any] = dataclasses.field(default_factory=dict)


@dataclasses.dataclass(frozen=True, slots=True)
class PortfolioSnapshot:
    """A snapshot of the entire portfolio."""
    account_id: str
    positions: dict[str, Position]  # symbol -> position
    balances: dict[str, AccountBalance]  # currency -> balance
    total_value: Decimal
    total_unrealized_pnl: Decimal
    total_realized_pnl: Decimal
    net_liquidation_value: Decimal
    buying_power: Decimal
    margin_used: Decimal
    margin_available: Decimal
    timestamp_ns: int
    metadata: dict[str, Any] = dataclasses.field(default_factory=dict)


@dataclasses.dataclass(frozen=True, slots=True)
class AggregatedPortfolio:
    """Aggregated portfolio across multiple accounts."""
    positions: dict[str, Position]  # symbol -> aggregated position
    balances: dict[str, Decimal]  # currency -> total balance
    total_value: Decimal
    total_unrealized_pnl: Decimal
    total_realized_pnl: Decimal
    account_count: int
    timestamp_ns: int
    metadata: dict[str, Any] = dataclasses.field(default_factory=dict)


@dataclasses.dataclass(frozen=True, slots=True)
class SyncEvent:
    """A portfolio synchronization event."""
    event_id: str
    event_type: SyncEventType
    account_id: str
    timestamp_ns: int
    data: dict[str, Any]
    previous_value: Any = None
    new_value: Any = None
    metadata: dict[str, Any] = dataclasses.field(default_factory=dict)


@dataclasses.dataclass(frozen=True, slots=True)
class PortfolioMetrics:
    """Metrics about portfolio synchronization."""
    total_accounts: int
    total_positions: int
    total_syncs: int
    sync_errors: int
    average_sync_time_ms: float
    last_sync_timestamp_ns: int
    accounts_synced: dict[str, int]


# ---------------------------------------------------------------------------
# Portfolio Synchronizer
# ---------------------------------------------------------------------------


class PortfolioSynchronizer:
    """Real-time portfolio synchronizer.
    
    Tracks portfolio positions, balances, and P&L across multiple
    accounts and provides real-time updates to the dashboard via
    the WebSocket gateway. Supports multi-account aggregation
    and comprehensive metrics tracking.
    """
    
    def __init__(
        self,
        config: PortfolioSyncConfig | None = None,
    ) -> None:
        """Initialize the portfolio synchronizer.
        
        Args:
            config: Portfolio sync configuration
        """
        self._config = config or PortfolioSyncConfig()
        self._lock = Lock()
        
        # Portfolio state by account
        self._portfolios: dict[str, PortfolioSnapshot] = {}
        self._positions: dict[str, dict[str, Position]] = {}  # account_id -> positions
        self._balances: dict[str, dict[str, AccountBalance]] = {}  # account_id -> balances
        
        # Event handlers
        self._event_handlers: list[Callable[[SyncEvent], None]] = []
        
        # History
        self._event_history: list[SyncEvent] = []
        self._snapshot_history: dict[str, list[PortfolioSnapshot]] = defaultdict(list)
        
        # WebSocket gateway integration (placeholder)
        self._gateway = None
        
        # Metrics
        self._metrics = PortfolioMetrics(
            total_accounts=0,
            total_positions=0,
            total_syncs=0,
            sync_errors=0,
            average_sync_time_ms=0.0,
            last_sync_timestamp_ns=0,
            accounts_synced={},
        )
        self._sync_times: list[int] = []
    
    def set_gateway(self, gateway: Any) -> None:
        """Set the WebSocket gateway for broadcasting updates.
        
        Args:
            gateway: WebSocket gateway instance
        """
        self._gateway = gateway
    
    def register_account(self, account_id: str) -> None:
        """Register an account for portfolio tracking.
        
        Args:
            account_id: Account identifier
        """
        import time
        
        with self._lock:
            if account_id in self._portfolios:
                return
            
            # Initialize portfolio state
            snapshot = PortfolioSnapshot(
                account_id=account_id,
                positions={},
                balances={},
                total_value=Decimal('0'),
                total_unrealized_pnl=Decimal('0'),
                total_realized_pnl=Decimal('0'),
                net_liquidation_value=Decimal('0'),
                buying_power=Decimal('0'),
                margin_used=Decimal('0'),
                margin_available=Decimal('0'),
                timestamp_ns=time.time_ns(),
            )
            
            self._portfolios[account_id] = snapshot
            self._positions[account_id] = {}
            self._balances[account_id] = {}
            
            self._metrics.total_accounts += 1
            self._metrics.accounts_synced[account_id] = 0
            
            # Emit event
            event = SyncEvent(
                event_id=self._generate_event_id(),
                event_type=SyncEventType.ACCOUNT_ADDED,
                account_id=account_id,
                timestamp_ns=time.time_ns(),
                data={"account_id": account_id},
            )
            self._emit_event(event)
    
    def unregister_account(self, account_id: str) -> None:
        """Unregister an account from portfolio tracking.
        
        Args:
            account_id: Account identifier
        """
        import time
        
        with self._lock:
            if account_id not in self._portfolios:
                return
            
            del self._portfolios[account_id]
            del self._positions[account_id]
            del self._balances[account_id]
            
            self._metrics.total_accounts -= 1
            if account_id in self._metrics.accounts_synced:
                del self._metrics.accounts_synced[account_id]
            
            # Emit event
            event = SyncEvent(
                event_id=self._generate_event_id(),
                event_type=SyncEventType.ACCOUNT_REMOVED,
                account_id=account_id,
                timestamp_ns=time.time_ns(),
                data={"account_id": account_id},
            )
            self._emit_event(event)
    
    def update_position(
        self,
        account_id: str,
        position: Position,
    ) -> None:
        """Update a position in the portfolio.
        
        Args:
            account_id: Account identifier
            position: Updated position
        """
        import secrets
        import time
        
        timestamp_ns = time.time_ns()
        
        with self._lock:
            if account_id not in self._positions:
                return
            
            old_position = self._positions[account_id].get(position.symbol)
            
            # Update position
            self._positions[account_id][position.symbol] = position
            
            # Determine event type
            if old_position is None:
                event_type = SyncEventType.POSITION_OPENED
            elif position.quantity == Decimal('0'):
                event_type = SyncEventType.POSITION_CLOSED
                del self._positions[account_id][position.symbol]
            else:
                event_type = SyncEventType.POSITION_MODIFIED
            
            # Update snapshot
            self._update_snapshot(account_id, timestamp_ns)
            
            # Emit event
            event = SyncEvent(
                event_id=secrets.token_hex(16),
                event_type=event_type,
                account_id=account_id,
                timestamp_ns=timestamp_ns,
                data={
                    "symbol": position.symbol,
                    "side": position.side.value,
                    "quantity": str(position.quantity),
                    "current_price": str(position.current_price),
                    "unrealized_pnl": str(position.unrealized_pnl),
                },
                previous_value=old_position,
                new_value=position,
            )
            self._emit_event(event)
    
    def update_balance(
        self,
        account_id: str,
        currency: str,
        balance: AccountBalance,
    ) -> None:
        """Update account balance.
        
        Args:
            account_id: Account identifier
            currency: Currency code
            balance: Updated balance
        """
        import secrets
        import time
        
        timestamp_ns = time.time_ns()
        
        with self._lock:
            if account_id not in self._balances:
                return
            
            old_balance = self._balances[account_id].get(currency)
            
            # Update balance
            self._balances[account_id][currency] = balance
            
            # Update snapshot
            self._update_snapshot(account_id, timestamp_ns)
            
            # Emit event
            event = SyncEvent(
                event_id=secrets.token_hex(16),
                event_type=SyncEventType.BALANCE_CHANGED,
                account_id=account_id,
                timestamp_ns=timestamp_ns,
                data={
                    "currency": currency,
                    "total_balance": str(balance.total_balance),
                    "available_balance": str(balance.available_balance),
                },
                previous_value=old_balance,
                new_value=balance,
            )
            self._emit_event(event)
    
    def sync_portfolio(self, account_id: str) -> PortfolioSnapshot | None:
        """Perform a full portfolio sync for an account.
        
        Args:
            account_id: Account identifier
            
        Returns:
            Updated portfolio snapshot or None if account not found
        """
        import secrets
        import time
        
        start_ms = int(time.time() * 1000)
        
        with self._lock:
            if account_id not in self._portfolios:
                return None
            
            timestamp_ns = time.time_ns()
            
            # Update snapshot with current state
            snapshot = self._update_snapshot(account_id, timestamp_ns)
            
            # Add to history
            self._snapshot_history[account_id].append(snapshot)
            if len(self._snapshot_history[account_id]) > self._config.history_size:
                self._snapshot_history[account_id].pop(0)
            
            # Update metrics
            self._metrics.total_syncs += 1
            self._metrics.accounts_synced[account_id] = \
                self._metrics.accounts_synced.get(account_id, 0) + 1
            self._metrics.last_sync_timestamp_ns = timestamp_ns
            
            sync_time_ms = int(time.time() * 1000) - start_ms
            self._sync_times.append(sync_time_ms)
            if len(self._sync_times) > 100:
                self._sync_times.pop(0)
            self._metrics.average_sync_time_ms = sum(self._sync_times) / len(self._sync_times)
            
            # Emit snapshot event
            event = SyncEvent(
                event_id=secrets.token_hex(16),
                event_type=SyncEventType.PORTFOLIO_SNAPSHOT,
                account_id=account_id,
                timestamp_ns=timestamp_ns,
                data=snapshot.__dict__,
            )
            self._emit_event(event)
            
            # Broadcast to gateway
            if self._gateway:
                self._broadcast_snapshot(snapshot)
            
            return snapshot
    
    def get_portfolio(self, account_id: str) -> PortfolioSnapshot | None:
        """Get current portfolio snapshot for an account.
        
        Args:
            account_id: Account identifier
            
        Returns:
            Portfolio snapshot or None if not found
        """
        with self._lock:
            return self._portfolios.get(account_id)
    
    def get_aggregated_portfolio(self) -> AggregatedPortfolio | None:
        """Get aggregated portfolio across all accounts.
        
        Returns:
            Aggregated portfolio or None if no accounts
        """
        import time
        
        if not self._config.enable_aggregation:
            return None
        
        with self._lock:
            if not self._portfolios:
                return None
            
            # Aggregate positions
            aggregated_positions: dict[str, Position] = {}
            aggregated_balances: dict[str, Decimal] = defaultdict(Decimal)
            total_value = Decimal('0')
            total_unrealized_pnl = Decimal('0')
            total_realized_pnl = Decimal('0')
            
            for snapshot in self._portfolios.values():
                # Aggregate positions
                for symbol, position in snapshot.positions.items():
                    if symbol in aggregated_positions:
                        # Combine positions (simplified - would need proper aggregation logic)
                        existing = aggregated_positions[symbol]
                        aggregated_quantity = existing.quantity + position.quantity
                        aggregated_positions[symbol] = dataclasses.replace(
                            position,
                            quantity=aggregated_quantity,
                        )
                    else:
                        aggregated_positions[symbol] = position
                
                # Aggregate balances
                for currency, balance in snapshot.balances.items():
                    aggregated_balances[currency] += balance.total_balance
                
                # Aggregate totals
                total_value += snapshot.total_value
                total_unrealized_pnl += snapshot.total_unrealized_pnl
                total_realized_pnl += snapshot.total_realized_pnl
            
            return AggregatedPortfolio(
                positions=aggregated_positions,
                balances=dict(aggregated_balances),
                total_value=total_value,
                total_unrealized_pnl=total_unrealized_pnl,
                total_realized_pnl=total_realized_pnl,
                account_count=len(self._portfolios),
                timestamp_ns=time.time_ns(),
            )
    
    def get_metrics(self) -> PortfolioMetrics:
        """Get portfolio synchronization metrics.
        
        Returns:
            Current metrics
        """
        with self._lock:
            # Update total positions count
            total_positions = sum(
                len(positions) for positions in self._positions.values()
            )
            
            return dataclasses.replace(
                self._metrics,
                total_positions=total_positions,
            )
    
    def register_event_handler(
        self,
        handler: Callable[[SyncEvent], None],
    ) -> None:
        """Register an event handler.
        
        Args:
            handler: Event handler callable
        """
        with self._lock:
            self._event_handlers.append(handler)
    
    def _update_snapshot(
        self,
        account_id: str,
        timestamp_ns: int,
    ) -> PortfolioSnapshot:
        """Update portfolio snapshot with current state."""
        positions = self._positions.get(account_id, {})
        balances = self._balances.get(account_id, {})
        
        # Calculate totals
        total_value = sum(
            position.quantity * position.current_price
            for position in positions.values()
        ) if positions else Decimal('0')
        
        total_unrealized_pnl = sum(
            position.unrealized_pnl
            for position in positions.values()
        ) if positions else Decimal('0')
        
        total_realized_pnl = sum(
            position.realized_pnl
            for position in positions.values()
        ) if positions else Decimal('0')
        
        net_liquidation_value = total_value + sum(
            balance.available_balance
            for balance in balances.values()
        )
        
        buying_power = net_liquidation_value * Decimal('0.9')  # Simplified calculation
        margin_used = Decimal('0')  # Would need margin calculation
        margin_available = buying_power - margin_used
        
        snapshot = PortfolioSnapshot(
            account_id=account_id,
            positions=dict(positions),
            balances=dict(balances),
            total_value=total_value,
            total_unrealized_pnl=total_unrealized_pnl,
            total_realized_pnl=total_realized_pnl,
            net_liquidation_value=net_liquidation_value,
            buying_power=buying_power,
            margin_used=margin_used,
            margin_available=margin_available,
            timestamp_ns=timestamp_ns,
        )
        
        self._portfolios[account_id] = snapshot
        return snapshot
    
    def _emit_event(self, event: SyncEvent) -> None:
        """Emit a synchronization event to handlers.
        
        Args:
            event: Event to emit
        """
        # Add to history
        self._event_history.append(event)
        if len(self._event_history) > self._config.history_size:
            self._event_history.pop(0)
        
        # Call handlers
        for handler in self._event_handlers:
            try:
                handler(event)
            except Exception:
                self._metrics.sync_errors += 1
    
    def _broadcast_snapshot(self, snapshot: PortfolioSnapshot) -> None:
        """Broadcast portfolio snapshot to WebSocket gateway.
        
        Args:
            snapshot: Portfolio snapshot to broadcast
        """
        if not self._gateway:
            return
        
        # Placeholder - would use the gateway to publish the snapshot
        # This would convert the snapshot to a StreamMessage and publish
        # to the PORTFOLIO channel
    
    def _generate_event_id(self) -> str:
        """Generate a unique event ID."""
        import secrets
        return secrets.token_hex(16)


# ---------------------------------------------------------------------------
# Portfolio Sync Manager
# ---------------------------------------------------------------------------


class PortfolioSyncManager:
    """Manager for portfolio synchronization across the system."""
    
    def __init__(self, config: PortfolioSyncConfig | None = None) -> None:
        """Initialize the portfolio sync manager.
        
        Args:
            config: Portfolio sync configuration
        """
        self._config = config or PortfolioSyncConfig()
        self._synchronizer = PortfolioSynchronizer(config)
    
    def register_account(self, account_id: str) -> None:
        """Register an account for tracking.
        
        Args:
            account_id: Account identifier
        """
        self._synchronizer.register_account(account_id)
    
    def update_position(
        self,
        account_id: str,
        position: Position,
    ) -> None:
        """Update a position.
        
        Args:
            account_id: Account identifier
            position: Updated position
        """
        self._synchronizer.update_position(account_id, position)
    
    def update_balance(
        self,
        account_id: str,
        currency: str,
        balance: AccountBalance,
    ) -> None:
        """Update account balance.
        
        Args:
            account_id: Account identifier
            currency: Currency code
            balance: Updated balance
        """
        self._synchronizer.update_balance(account_id, currency, balance)
    
    def sync_portfolio(self, account_id: str) -> PortfolioSnapshot | None:
        """Sync portfolio for an account.
        
        Args:
            account_id: Account identifier
            
        Returns:
            Portfolio snapshot or None
        """
        return self._synchronizer.sync_portfolio(account_id)
    
    def get_portfolio(self, account_id: str) -> PortfolioSnapshot | None:
        """Get portfolio snapshot.
        
        Args:
            account_id: Account identifier
            
        Returns:
            Portfolio snapshot or None
        """
        return self._synchronizer.get_portfolio(account_id)
    
    def get_aggregated_portfolio(self) -> AggregatedPortfolio | None:
        """Get aggregated portfolio.
        
        Returns:
            Aggregated portfolio or None
        """
        return self._synchronizer.get_aggregated_portfolio()
    
    def get_metrics(self) -> PortfolioMetrics:
        """Get synchronization metrics.
        
        Returns:
            Current metrics
        """
        return self._synchronizer.get_metrics()


__all__ = [
    "AssetType",
    "PositionSide",
    "SyncEventType",
    "PortfolioSyncConfig",
    "Position",
    "AccountBalance",
    "PortfolioSnapshot",
    "AggregatedPortfolio",
    "SyncEvent",
    "PortfolioMetrics",
    "PortfolioSynchronizer",
    "PortfolioSyncManager",
]
    def _get_compliance_weight(self, component: str) -> float:
        """Fetch compliance weight for a specific component."""
        try:
            import requests
            response = requests.get("http://localhost:8080/api/compliance/weights", timeout=1.0)
            if response.status_code == 200:
                weights = response.json()
                return weights.get("data", weights.get("trading", 1.0))
        except Exception as e:
            logger.warning(f"[PORTFOLIO_SYNC] Failed to fetch compliance weights: {e}")
        return 1.0
    
    def _convert_to_stream_message(self, snapshot: PortfolioSnapshot) -> Any:
        """Convert portfolio snapshot to StreamMessage."""
        message_data = {
            "event_type": "portfolio_update",
            "timestamp_ns": snapshot.timestamp_ns,
            "account_id": snapshot.account_id,
            "total_value": snapshot.total_value,
            "positions_count": len(snapshot.positions),
            "positions": [
                {
                    "symbol": pos.symbol,
                    "quantity": pos.quantity,
                    "value": pos.value,
                    "avg_entry_price": pos.avg_entry_price,
                    "unrealized_pnl": pos.unrealized_pnl,
                }
                for pos in snapshot.positions
            ],
            "cash": snapshot.cash,
            "metadata": snapshot.metadata
        }
        return message_data
    
    def _publish_with_guarantee(self, message: Any) -> None:
        """Publish message with guaranteed delivery."""
        try:
            self._gateway.publish("PORTFOLIO", message, qos=1)
        except Exception as e:
            logger.error(f"[PORTFOLIO_SYNC] Guaranteed delivery publish failed: {e}")
            raise
    
    def _publish_standard(self, message: Any) -> None:
        """Publish message with standard delivery."""
        try:
            self._gateway.publish("PORTFOLIO", message, qos=0)
        except Exception as e:
            logger.error(f"[PORTFOLIO_SYNC] Standard publish failed: {e}")
            raise
    
    def _log_snapshot(self, snapshot: PortfolioSnapshot) -> None:
        """Log portfolio snapshot when real-time publishing is disabled."""
        logger.info(
            f"[PORTFOLIO_SYNC] Portfolio snapshot (log mode): "
            f"total_value={snapshot.total_value}, "
            f"positions={len(snapshot.positions)}, "
            f"cash={snapshot.cash}"
        )
