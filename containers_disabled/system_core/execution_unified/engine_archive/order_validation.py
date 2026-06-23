"""Order Validation System — EXEC-05.04.

Comprehensive order validation system to ensure orders are safe
and valid before submission to exchanges. Validates order parameters,
balance, symbol validity, and regulatory compliance.
"""

from __future__ import annotations

import dataclasses
import enum
import logging
from threading import Lock
from typing import Any, Final

import requests

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_MIN_ORDER_VALUE: Final[float] = 10.0  # Minimum order value in base currency
DEFAULT_MAX_ORDER_VALUE: Final[float] = 1_000_000.0  # Maximum order value
DEFAULT_MIN_QUANTITY: Final[float] = 0.001  # Minimum quantity
DEFAULT_MAX_QUANTITY: Final[float] = 1_000_000.0  # Maximum quantity
DEFAULT_PRICE_PRECISION: Final[int] = 8  # Decimal places for price
DEFAULT_QUANTITY_PRECISION: Final[int] = 8  # Decimal places for quantity
DEFAULT_ENABLE_REGULATORY: Final[bool] = True

NEW_PIP_DEPENDENCIES: Final[tuple[str, ...]] = ()


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class ValidationErrorType(enum.Enum):
    """Types of validation errors."""

    INVALID_SYMBOL = "INVALID_SYMBOL"
    INVALID_QUANTITY = "INVALID_QUANTITY"
    INVALID_PRICE = "INVALID_PRICE"
    INSUFFICIENT_BALANCE = "INSUFFICIENT_BALANCE"
    INSUFFICIENT_MARGIN = "INSUFFICIENT_MARGIN"
    ORDER_TOO_SMALL = "ORDER_TOO_SMALL"
    ORDER_TOO_LARGE = "ORDER_TOO_LARGE"
    INVALID_SIDE = "INVALID_SIDE"
    INVALID_ORDER_TYPE = "INVALID_ORDER_TYPE"
    MISSING_REQUIRED_FIELD = "MISSING_REQUIRED_FIELD"
    REGULATORY_VIOLATION = "REGULATORY_VIOLATION"
    TIME_IN_FORCE_INVALID = "TIME_IN_FORCE_INVALID"
    PRECISION_ERROR = "PRECISION_ERROR"
    DUPLICATE_ORDER = "DUPLICATE_ORDER"
    RISK_LIMIT_EXCEEDED = "RISK_LIMIT_EXCEEDED"
    UNKNOWN = "UNKNOWN"


class ValidationSeverity(enum.Enum):
    """Severity level of validation errors."""

    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class OrderSide(enum.Enum):
    """Side of the order."""

    BUY = "BUY"
    SELL = "SELL"


class OrderType(enum.Enum):
    """Type of order."""

    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP = "STOP"
    STOP_LIMIT = "STOP_LIMIT"
    TRAILING_STOP = "TRAILING_STOP"
    ICEBERG = "ICEBERG"


class TimeInForce(enum.Enum):
    """Time in force for orders."""

    GTC = "GTC"  # Good Till Cancelled
    IOC = "IOC"  # Immediate Or Cancel
    FOK = "FOK"  # Fill Or Kill
    GTD = "GTD"  # Good Till Date


# ---------------------------------------------------------------------------
# Value objects
# ---------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True, slots=True)
class ValidationConfig:
    """Configuration for order validation."""

    min_order_value: float = DEFAULT_MIN_ORDER_VALUE
    max_order_value: float = DEFAULT_MAX_ORDER_VALUE
    min_quantity: float = DEFAULT_MIN_QUANTITY
    max_quantity: float = DEFAULT_MAX_QUANTITY
    price_precision: int = DEFAULT_PRICE_PRECISION
    quantity_precision: int = DEFAULT_QUANTITY_PRECISION
    enable_regulatory: bool = DEFAULT_ENABLE_REGULATORY
    enable_duplicate_check: bool = True
    enable_risk_limits: bool = True
    custom_validators: list[str] = dataclasses.field(default_factory=list)

    def __post_init__(self) -> None:
        if self.min_order_value < 0:
            raise ValueError("min_order_value must be >= 0")
        if self.max_order_value < self.min_order_value:
            raise ValueError("max_order_value must be >= min_order_value")
        if self.min_quantity < 0:
            raise ValueError("min_quantity must be >= 0")
        if self.max_quantity < self.min_quantity:
            raise ValueError("max_quantity must be >= min_quantity")
        if self.price_precision < 0:
            raise ValueError("price_precision must be >= 0")
        if self.quantity_precision < 0:
            raise ValueError("quantity_precision must be >= 0")


@dataclasses.dataclass(frozen=True, slots=True)
class ValidationError:
    """A validation error."""

    error_type: ValidationErrorType
    severity: ValidationSeverity
    message: str
    field: str = ""
    expected: Any = None
    actual: Any = None
    metadata: dict[str, Any] = dataclasses.field(default_factory=dict)


@dataclasses.dataclass(frozen=True, slots=True)
class ValidationResult:
    """Result of order validation."""

    is_valid: bool
    errors: list[ValidationError]
    warnings: list[ValidationError]
    order_id: str
    timestamp_ns: int
    metadata: dict[str, Any] = dataclasses.field(default_factory=dict)


@dataclasses.dataclass(frozen=True, slots=True)
class Order:
    """Order to validate."""

    order_id: str
    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: float
    price: float | None = None  # None for market orders
    stop_price: float | None = None  # For stop orders
    time_in_force: TimeInForce = TimeInForce.GTC
    account_id: str = ""
    timestamp_ns: int = 0
    metadata: dict[str, Any] = dataclasses.field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.order_id:
            raise ValueError("order_id must be non-empty")
        if not self.symbol:
            raise ValueError("symbol must be non-empty")
        if self.quantity <= 0:
            raise ValueError("quantity must be > 0")
        if self.price is not None and self.price <= 0:
            raise ValueError("price must be > 0 if specified")


@dataclasses.dataclass(frozen=True, slots=True)
class AccountBalance:
    """Account balance information."""

    account_id: str
    base_currency: str
    quote_currency: str
    base_balance: float
    quote_balance: float
    margin_available: float = 0.0
    total_value: float = 0.0
    metadata: dict[str, Any] = dataclasses.field(default_factory=dict)


@dataclasses.dataclass(frozen=True, slots=True)
class ValidationMetrics:
    """Metrics about order validation performance."""

    total_orders: int
    valid_orders: int
    invalid_orders: int
    warning_orders: int
    errors_by_type: dict[str, int]
    validation_rate: float


# ---------------------------------------------------------------------------
# Order Validator
# ---------------------------------------------------------------------------


class OrderValidator:
    """Comprehensive order validator.

    Validates orders against multiple criteria including:
    - Symbol validity
    - Quantity and price ranges
    - Balance and margin requirements
    - Regulatory compliance
    - Risk limits
    - Duplicate detection
    """

    def __init__(
        self,
        config: ValidationConfig | None = None,
    ) -> None:
        """Initialize the order validator.

        Args:
            config: Validation configuration
        """
        self._config = config or ValidationConfig()
        self._lock = Lock()

        # Account balances
        self._account_balances: dict[str, AccountBalance] = {}

        # Symbols registry
        self._valid_symbols: set[str] = set()

        # Duplicate detection
        self._recent_orders: dict[str, int] = {}  # order_hash -> timestamp_ns
        self._duplicate_window_ns = 5_000_000_000  # 5 seconds

        # Metrics
        self._total_orders = 0
        self._valid_orders = 0
        self._invalid_orders = 0
        self._warning_orders = 0
        self._errors_by_type: dict[str, int] = {}

    def validate_order(
        self,
        order: Order,
        timestamp_ns: int | None = None,
    ) -> ValidationResult:
        """Validate an order comprehensively.

        Args:
            order: Order to validate
            timestamp_ns: Current timestamp

        Returns:
            Validation result with any errors or warnings
        """
        import time

        if timestamp_ns is None:
            timestamp_ns = time.time_ns()

        errors = []
        warnings = []

        # Validate required fields
        errors.extend(self._validate_required_fields(order))

        # Validate symbol
        errors.extend(self._validate_symbol(order))

        # Validate quantity
        errors.extend(self._validate_quantity(order))

        # Validate price
        errors.extend(self._validate_price(order))

        # Validate order type specific fields
        errors.extend(self._validate_order_type_fields(order))

        # Validate time in force
        errors.extend(self._validate_time_in_force(order))

        # Validate balance
        balance_errors = self._validate_balance(order)
        errors.extend(balance_errors)

        # Validate risk limits
        risk_errors = self._validate_risk_limits(order)
        errors.extend(risk_errors)

        # Check for duplicates
        if self._config.enable_duplicate_check:
            duplicate_errors = self._check_duplicates(order, timestamp_ns)
            errors.extend(duplicate_errors)

        # Regulatory validation
        if self._config.enable_regulatory:
            regulatory_errors = self._validate_regulatory(order)
            errors.extend(regulatory_errors)

        # Validate precision
        precision_errors = self._validate_precision(order)
        errors.extend(precision_errors)

        # Update metrics
        with self._lock:
            self._total_orders += 1
            is_valid = len(errors) == 0
            if is_valid:
                self._valid_orders += 1
            else:
                self._invalid_orders += 1

            if len(warnings) > 0:
                self._warning_orders += 1

            for error in errors:
                error_type = error.error_type.value
                self._errors_by_type[error_type] = self._errors_by_type.get(error_type, 0) + 1

            # Record order for duplicate detection
            if is_valid:
                order_hash = self._compute_order_hash(order)
                self._recent_orders[order_hash] = timestamp_ns

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            order_id=order.order_id,
            timestamp_ns=timestamp_ns,
        )

    def set_account_balance(self, balance: AccountBalance) -> None:
        """Set account balance information.

        Args:
            balance: Account balance
        """
        with self._lock:
            self._account_balances[balance.account_id] = balance

    def register_symbol(self, symbol: str) -> None:
        """Register a valid trading symbol.

        Args:
            symbol: Trading symbol
        """
        with self._lock:
            self._valid_symbols.add(symbol)

    def unregister_symbol(self, symbol: str) -> None:
        """Unregister a trading symbol.

        Args:
            symbol: Trading symbol
        """
        with self._lock:
            self._valid_symbols.discard(symbol)

    def get_metrics(self) -> ValidationMetrics:
        """Get validation metrics.

        Returns:
            Current metrics
        """
        with self._lock:
            validation_rate = 0.0
            if self._total_orders > 0:
                validation_rate = self._valid_orders / self._total_orders

            return ValidationMetrics(
                total_orders=self._total_orders,
                valid_orders=self._valid_orders,
                invalid_orders=self._invalid_orders,
                warning_orders=self._warning_orders,
                errors_by_type=dict(self._errors_by_type),
                validation_rate=validation_rate,
            )

    def _validate_required_fields(self, order: Order) -> list[ValidationError]:
        """Validate that all required fields are present."""
        errors = []

        if not order.order_id:
            errors.append(
                ValidationError(
                    error_type=ValidationErrorType.MISSING_REQUIRED_FIELD,
                    severity=ValidationSeverity.ERROR,
                    message="order_id is required",
                    field="order_id",
                )
            )

        if not order.symbol:
            errors.append(
                ValidationError(
                    error_type=ValidationErrorType.MISSING_REQUIRED_FIELD,
                    severity=ValidationSeverity.ERROR,
                    message="symbol is required",
                    field="symbol",
                )
            )

        if order.quantity <= 0:
            errors.append(
                ValidationError(
                    error_type=ValidationErrorType.INVALID_QUANTITY,
                    severity=ValidationSeverity.ERROR,
                    message="quantity must be > 0",
                    field="quantity",
                    expected="> 0",
                    actual=order.quantity,
                )
            )

        return errors

    def _validate_symbol(self, order: Order) -> list[ValidationError]:
        """Validate that the symbol is valid."""
        errors = []

        if self._valid_symbols and order.symbol not in self._valid_symbols:
            errors.append(
                ValidationError(
                    error_type=ValidationErrorType.INVALID_SYMBOL,
                    severity=ValidationSeverity.ERROR,
                    message=f"Symbol {order.symbol} is not registered",
                    field="symbol",
                    actual=order.symbol,
                )
            )

        return errors

    def _validate_quantity(self, order: Order) -> list[ValidationError]:
        """Validate order quantity."""
        errors = []

        if order.quantity < self._config.min_quantity:
            errors.append(
                ValidationError(
                    error_type=ValidationErrorType.ORDER_TOO_SMALL,
                    severity=ValidationSeverity.ERROR,
                    message=f"quantity {order.quantity} is below minimum {self._config.min_quantity}",
                    field="quantity",
                    expected=f">= {self._config.min_quantity}",
                    actual=order.quantity,
                )
            )

        if order.quantity > self._config.max_quantity:
            errors.append(
                ValidationError(
                    error_type=ValidationErrorType.ORDER_TOO_LARGE,
                    severity=ValidationSeverity.ERROR,
                    message=f"quantity {order.quantity} exceeds maximum {self._config.max_quantity}",
                    field="quantity",
                    expected=f"<= {self._config.max_quantity}",
                    actual=order.quantity,
                )
            )

        return errors

    def _validate_price(self, order: Order) -> list[ValidationError]:
        """Validate order price."""
        errors = []

        if order.order_type != OrderType.MARKET and order.price is None:
            errors.append(
                ValidationError(
                    error_type=ValidationErrorType.MISSING_REQUIRED_FIELD,
                    severity=ValidationSeverity.ERROR,
                    message="price is required for non-market orders",
                    field="price",
                )
            )

        if order.price is not None and order.price <= 0:
            errors.append(
                ValidationError(
                    error_type=ValidationErrorType.INVALID_PRICE,
                    severity=ValidationSeverity.ERROR,
                    message="price must be > 0",
                    field="price",
                    expected="> 0",
                    actual=order.price,
                )
            )

        return errors

    def _validate_order_type_fields(self, order: Order) -> list[ValidationError]:
        """Validate order type specific fields."""
        errors = []

        if order.order_type == OrderType.STOP and order.stop_price is None:
            errors.append(
                ValidationError(
                    error_type=ValidationErrorType.MISSING_REQUIRED_FIELD,
                    severity=ValidationSeverity.ERROR,
                    message="stop_price is required for stop orders",
                    field="stop_price",
                )
            )

        if order.order_type == OrderType.STOP_LIMIT and (
            order.stop_price is None or order.price is None
        ):
            errors.append(
                ValidationError(
                    error_type=ValidationErrorType.MISSING_REQUIRED_FIELD,
                    severity=ValidationSeverity.ERROR,
                    message="stop_price and price are required for stop-limit orders",
                    field="stop_price,price",
                )
            )

        return errors

    def _validate_time_in_force(self, order: Order) -> list[ValidationError]:
        """Validate time in force."""
        errors = []

        if order.time_in_force == TimeInForce.GTD and order.metadata.get("expiry_date") is None:
            errors.append(
                ValidationError(
                    error_type=ValidationErrorType.TIME_IN_FORCE_INVALID,
                    severity=ValidationSeverity.ERROR,
                    message="expiry_date is required for GTD orders",
                    field="time_in_force",
                )
            )

        return errors

    def _validate_balance(self, order: Order) -> list[ValidationError]:
        """Validate account balance for the order."""
        errors = []

        if not order.account_id:
            return errors

        balance = self._account_balances.get(order.account_id)
        if not balance:
            return errors

        order_value = order.quantity * (order.price or 0)

        if order.side == OrderSide.BUY:
            # Check quote balance
            if balance.quote_balance < order_value:
                errors.append(
                    ValidationError(
                        error_type=ValidationErrorType.INSUFFICIENT_BALANCE,
                        severity=ValidationSeverity.ERROR,
                        message=f"Insufficient quote balance: need {order_value}, have {balance.quote_balance}",
                        field="balance",
                        expected=f">= {order_value}",
                        actual=balance.quote_balance,
                    )
                )
        else:
            # Check base balance
            if balance.base_balance < order.quantity:
                errors.append(
                    ValidationError(
                        error_type=ValidationErrorType.INSUFFICIENT_BALANCE,
                        severity=ValidationSeverity.ERROR,
                        message=f"Insufficient base balance: need {order.quantity}, have {balance.base_balance}",
                        field="balance",
                        expected=f">= {order.quantity}",
                        actual=balance.base_balance,
                    )
                )

        return errors

    def _validate_risk_limits(self, order: Order) -> list[ValidationError]:
        """Validate order against risk limits."""
        errors = []

        if not self._config.enable_risk_limits:
            return errors

        order_value = order.quantity * (order.price or 0)

        if order_value < self._config.min_order_value:
            errors.append(
                ValidationError(
                    error_type=ValidationErrorType.ORDER_TOO_SMALL,
                    severity=ValidationSeverity.ERROR,
                    message=f"Order value {order_value} is below minimum {self._config.min_order_value}",
                    field="order_value",
                    expected=f">= {self._config.min_order_value}",
                    actual=order_value,
                )
            )

        if order_value > self._config.max_order_value:
            errors.append(
                ValidationError(
                    error_type=ValidationErrorType.ORDER_TOO_LARGE,
                    severity=ValidationSeverity.ERROR,
                    message=f"Order value {order_value} exceeds maximum {self._config.max_order_value}",
                    field="order_value",
                    expected=f"<= {self._config.max_order_value}",
                    actual=order_value,
                )
            )

        return errors

    def _check_duplicates(self, order: Order, timestamp_ns: int) -> list[ValidationError]:
        """Check for duplicate orders."""
        errors = []

        order_hash = self._compute_order_hash(order)

        if order_hash in self._recent_orders:
            last_timestamp = self._recent_orders[order_hash]
            if timestamp_ns - last_timestamp < self._duplicate_window_ns:
                errors.append(
                    ValidationError(
                        error_type=ValidationErrorType.DUPLICATE_ORDER,
                        severity=ValidationSeverity.ERROR,
                        message=f"Duplicate order detected (hash: {order_hash[:16]}...)",
                        field="order_id",
                    )
                )

        return errors

    def _validate_regulatory(self, order: Order) -> list[ValidationError]:
        """Validate regulatory requirements with compliance level integration."""
        errors = []

        try:
            # Fetch current compliance weights from the API
            response = requests.get("http://localhost:8080/api/compliance/weights", timeout=1.0)
            if response.status_code == 200:
                weights = response.json()
                regulatory_weight = weights.get("regulatory", 1.0)
            else:
                # Default to full compliance if API unavailable
                regulatory_weight = 1.0
        except Exception as e:
            logging.getLogger("order_validation").warning(
                f"Failed to fetch compliance weights, using full compliance: {e}"
            )
            regulatory_weight = 1.0

        # If regulatory weight is very low, skip most checks
        if regulatory_weight < 0.2:
            logging.getLogger("order_validation").info(
                "Regulatory compliance weight < 0.2, skipping detailed checks"
            )
            return errors

        # Position Limits Validation
        if regulatory_weight >= 0.5:
            max_position_size = (
                self._config.max_position_size
                if hasattr(self._config, "max_position_size")
                else 1000000
            )
            if order.quantity and order.quantity > max_position_size:
                severity = (
                    ValidationSeverity.ERROR
                    if regulatory_weight >= 0.8
                    else ValidationSeverity.WARNING
                )
                errors.append(
                    ValidationError(
                        error_type=ValidationErrorType.REGULATORY_ERROR,
                        severity=severity,
                        message=f"Order quantity {order.quantity} exceeds maximum position size {max_position_size}",
                        field="quantity",
                        expected=f"<= {max_position_size}",
                        actual=order.quantity,
                    )
                )

        # Concentration Limits Validation
        if regulatory_weight >= 0.7:
            max_concentration = (
                self._config.max_concentration
                if hasattr(self._config, "max_concentration")
                else 0.3
            )
            if hasattr(order, "portfolio_value") and order.portfolio_value:
                concentration = (order.quantity * (order.price or 0)) / order.portfolio_value
                if concentration > max_concentration:
                    severity = (
                        ValidationSeverity.ERROR
                        if regulatory_weight >= 0.9
                        else ValidationSeverity.WARNING
                    )
                    errors.append(
                        ValidationError(
                            error_type=ValidationErrorType.REGULATORY_ERROR,
                            severity=severity,
                            message=f"Order concentration {concentration:.2%} exceeds maximum {max_concentration:.2%}",
                            field="concentration",
                            expected=f"<= {max_concentration:.2%}",
                            actual=f"{concentration:.2%}",
                        )
                    )

        # Market Abuse Detection
        if regulatory_weight >= 0.8:
            # Check for suspicious patterns
            if (
                hasattr(order, "time_since_last_order")
                and order.time_since_last_order
                and order.time_since_last_order < 1.0
            ):
                errors.append(
                    ValidationError(
                        error_type=ValidationErrorType.REGULATORY_ERROR,
                        severity=ValidationSeverity.WARNING,
                        message=f"Rapid order detected (time since last: {order.time_since_last_order:.2f}s)",
                        field="timing",
                        expected=">= 1.0s between orders",
                        actual=f"{order.time_since_last_order:.2f}s",
                    )
                )

        # KYC/AML Requirements
        if regulatory_weight >= 0.9:
            if hasattr(order, "kyc_verified") and not order.kyc_verified:
                errors.append(
                    ValidationError(
                        error_type=ValidationErrorType.REGULATORY_ERROR,
                        severity=ValidationSeverity.ERROR,
                        message="KYC verification required for this order",
                        field="kyc_status",
                        expected="verified",
                        actual="unverified",
                    )
                )

        logging.getLogger("order_validation").info(
            f"Regulatory validation completed with weight {regulatory_weight:.2f}: "
            f"{len(errors)} errors found"
        )

        return errors

    def _validate_precision(self, order: Order) -> list[ValidationError]:
        """Validate price and quantity precision."""
        errors = []

        if order.price is not None:
            decimal_places = len(str(order.price).split(".")[1]) if "." in str(order.price) else 0
            if decimal_places > self._config.price_precision:
                errors.append(
                    ValidationError(
                        error_type=ValidationErrorType.PRECISION_ERROR,
                        severity=ValidationSeverity.ERROR,
                        message=f"Price precision {decimal_places} exceeds maximum {self._config.price_precision}",
                        field="price",
                        expected=f"<= {self._config.price_precision} decimal places",
                        actual=decimal_places,
                    )
                )

        decimal_places = len(str(order.quantity).split(".")[1]) if "." in str(order.quantity) else 0
        if decimal_places > self._config.quantity_precision:
            errors.append(
                ValidationError(
                    error_type=ValidationErrorType.PRECISION_ERROR,
                    severity=ValidationSeverity.ERROR,
                    message=f"Quantity precision {decimal_places} exceeds maximum {self._config.quantity_precision}",
                    field="quantity",
                    expected=f"<= {self._config.quantity_precision} decimal places",
                    actual=decimal_places,
                )
            )

        return errors

    def _compute_order_hash(self, order: Order) -> str:
        """Compute a hash of the order for duplicate detection."""
        import hashlib

        # Hash based on symbol, side, type, quantity, price
        hash_input = f"{order.symbol}:{order.side.value}:{order.order_type.value}:{order.quantity}:{order.price}"
        return hashlib.sha256(hash_input.encode()).hexdigest()


# ---------------------------------------------------------------------------
# Order Validation Manager
# ---------------------------------------------------------------------------


class OrderValidationManager:
    """Manager for order validation across the system."""

    def __init__(self, config: ValidationConfig | None = None) -> None:
        """Initialize the order validation manager.

        Args:
            config: Validation configuration
        """
        self._config = config or ValidationConfig()
        self._validator = OrderValidator(config)

    def validate_order(self, order: Order) -> ValidationResult:
        """Validate an order.

        Args:
            order: Order to validate

        Returns:
            Validation result
        """
        return self._validator.validate_order(order)

    def set_account_balance(self, balance: AccountBalance) -> None:
        """Set account balance.

        Args:
            balance: Account balance
        """
        self._validator.set_account_balance(balance)

    def register_symbol(self, symbol: str) -> None:
        """Register a valid symbol.

        Args:
            symbol: Trading symbol
        """
        self._validator.register_symbol(symbol)

    def get_metrics(self) -> ValidationMetrics:
        """Get validation metrics.

        Returns:
            Current metrics
        """
        return self._validator.get_metrics()


__all__ = [
    "ValidationErrorType",
    "ValidationSeverity",
    "OrderSide",
    "OrderType",
    "TimeInForce",
    "ValidationConfig",
    "ValidationError",
    "ValidationResult",
    "Order",
    "AccountBalance",
    "ValidationMetrics",
    "OrderValidator",
    "OrderValidationManager",
]
