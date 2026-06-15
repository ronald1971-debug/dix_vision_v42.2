"""Unified Execution Kernel - Core Foundation.

This is the consolidated execution kernel that unifies the functionality
from execution/ and execution_engine/ into a single coherent execution
system as specified in the DIX VISION comprehensive integration plan.

The unified execution kernel provides:
- Central execution orchestration
- Strategic and tactical execution separation
- Unified adapter management
- Execution protection mechanisms
- Lane-based execution routing
- Execution auditing and monitoring

Design Principles:
- INV-15: Minimal external dependencies, no blocking IO
- INV-08: Pure execution logic where possible
- Thread-safe operations
- Clear strategic/tactical separation
- High-performance execution paths
"""

from __future__ import annotations

import dataclasses
import enum
import logging
import threading
from collections.abc import Mapping
from types import MappingProxyType
from typing import TYPE_CHECKING, Any

_logger = logging.getLogger(__name__)


class ExecutionType(str, enum.Enum):
    """Types of execution operations."""

    STRATEGIC = "STRATEGIC"  # Portfolio-level, macro decisions
    TACTICAL = "TACTICAL"  # Individual trade execution
    EMERGENCY = "EMERGENCY"  # Emergency execution (hazards)
    MANUAL = "MANUAL"  # Operator-initiated execution
    AUTOMATIC = "AUTOMATIC"  # System-initiated execution


class ExecutionLane(str, enum.Enum):
    """Execution lanes for different priority levels."""

    FAST_LANE = "FAST_LANE"  # High-priority, low-latency execution
    NORMAL_LANE = "NORMAL_LANE"  # Standard execution
    HAZARD_LANE = "HAZARD_LANE"  # Hazard handling
    OFFLINE_LANE = "OFFLINE_LANE"  # Offline/backtesting
    PROTECTED_LANE = "PROTECTED_LANE"  # Extra protection for sensitive operations


class ExecutionStatus(str, enum.Enum):
    """Status of execution operations."""

    PENDING = "PENDING"
    SUBMITTED = "SUBMITTED"
    EXECUTING = "EXECUTING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"


@dataclasses.dataclass(frozen=True, slots=True)
class ExecutionRequest:
    """A request for execution.

    Fields:
        request_id: Unique identifier for this request
        execution_type: Type of execution (strategic/tactical/etc)
        source: Origin of the request (e.g., INDIRA, operator, etc.)
        payload: Execution content (key-value pairs)
        priority: Request priority (0-10, 10 = highest)
        preferred_lane: Preferred execution lane
        timestamp_ns: Nanosecond timestamp of request
        metadata: Additional metadata
    """

    request_id: str
    execution_type: ExecutionType
    source: str
    payload: Mapping[str, str] = dataclasses.field(default_factory=lambda: MappingProxyType({}))
    priority: int = 5
    preferred_lane: ExecutionLane = ExecutionLane.NORMAL_LANE
    timestamp_ns: int = 0
    metadata: Mapping[str, str] = dataclasses.field(default_factory=lambda: MappingProxyType({}))

    def __post_init__(self) -> None:
        if not self.request_id:
            raise ValueError("ExecutionRequest.request_id must be non-empty")
        if not 0 <= self.priority <= 10:
            raise ValueError(f"ExecutionRequest.priority must be 0-10, got {self.priority}")
        if not isinstance(self.payload, MappingProxyType):
            object.__setattr__(self, "payload", MappingProxyType(dict(self.payload)))
        if not isinstance(self.metadata, MappingProxyType):
            object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))


@dataclasses.dataclass(frozen=True, slots=True)
class ExecutionResult:
    """Result of an execution request.

    Fields:
        result_id: Unique identifier for this result
        request_id: Corresponding request ID
        status: Execution status
        executed_lane: Lane used for execution
        outcome: Execution outcome data
        error_message: Error message if failed
        execution_time_ns: Time taken to execute in nanoseconds
        timestamp_ns: Nanosecond timestamp of result
    """

    result_id: str
    request_id: str
    status: ExecutionStatus
    executed_lane: ExecutionLane
    outcome: Mapping[str, str] = dataclasses.field(default_factory=lambda: MappingProxyType({}))
    error_message: str = ""
    execution_time_ns: int = 0
    timestamp_ns: int = 0

    def __post_init__(self) -> None:
        if not self.result_id:
            raise ValueError("ExecutionResult.result_id must be non-empty")
        if not self.request_id:
            raise ValueError("ExecutionResult.request_id must be non-empty")
        if not isinstance(self.outcome, MappingProxyType):
            object.__setattr__(self, "outcome", MappingProxyType(dict(self.outcome)))


@dataclasses.dataclass(frozen=True, slots=True)
class Intent:
    """Intent from INDIRA for execution.

    Fields:
        intent_id: Unique identifier
        intent_type: Type of intent (trading, portfolio, risk)
        content: Intent content
        confidence: Intent confidence score
        source: Cognitive source (INDIRA)
        timestamp_ns: Timestamp
    """

    intent_id: str
    intent_type: str
    content: Mapping[str, str] = dataclasses.field(default_factory=lambda: MappingProxyType({}))
    confidence: float = 0.8
    source: str = "INDIRA"
    timestamp_ns: int = 0

    def __post_init__(self) -> None:
        if not isinstance(self.content, MappingProxyType):
            object.__setattr__(self, "content", MappingProxyType(dict(self.content)))


@dataclasses.dataclass(frozen=True, slots=True)
class Action:
    """Action implementation by execution layer.

    Fields:
        action_id: Unique identifier
        intent_id: Corresponding intent ID
        action_type: Type of action (trade_execution, portfolio_rebalance)
        parameters: Action parameters
        status: Action status
        result: Action result
        timestamp_ns: Timestamp
    """

    action_id: str
    intent_id: str
    action_type: str
    parameters: Mapping[str, str] = dataclasses.field(default_factory=lambda: MappingProxyType({}))
    status: str = "PENDING"
    result: Mapping[str, str] = dataclasses.field(default_factory=lambda: MappingProxyType({}))
    timestamp_ns: int = 0

    def __post_init__(self) -> None:
        if not isinstance(self.parameters, MappingProxyType):
            object.__setattr__(self, "parameters", MappingProxyType(dict(self.parameters)))
        if not isinstance(self.result, MappingProxyType):
            object.__setattr__(self, "result", MappingProxyType(dict(self.result)))


class UnifiedExecutionKernel:
    """Unified execution kernel consolidating all execution functionality.

    This kernel provides the central authority for all execution decisions,
    integrating strategic and tactical execution while maintaining clear
    separation of concerns as specified in the comprehensive plan.

    Key Responsibilities:
    - Process execution requests and route to appropriate lanes
    - Execute strategic intents from INDIRA
    - Execute tactical trading operations
    - Manage execution adapters and venues
    - Enforce execution protections
    - Monitor execution performance
    - Maintain execution audit trails
    """

    def __init__(self) -> None:
        self._lock: threading.Lock = threading.Lock()
        
        # Execution state
        self._active_requests: dict[str, ExecutionRequest] = {}
        self._execution_history: dict[str, ExecutionResult] = {}
        self._lane_status: dict[ExecutionLane, bool] = {
            lane: True for lane in ExecutionLane
        }
        
        # Statistics
        self._total_executions: int = 0
        self._total_strategic: int = 0
        self._total_tactical: int = 0
        self._total_failures: int = 0

    def execute_strategy(self, strategy: Mapping[str, str]) -> ExecutionResult:
        """Execute a strategic intent from INDIRA.

        Args:
            strategy: Strategy parameters and intent

        Returns:
            ExecutionResult with strategic execution outcome
        """
        request = ExecutionRequest(
            request_id=f"strategic_{self._get_timestamp()}",
            execution_type=ExecutionType.STRATEGIC,
            source="INDIRA",
            payload=strategy,
            priority=8,
            preferred_lane=ExecutionLane.NORMAL_LANE,
            timestamp_ns=self._get_timestamp(),
        )

        result = self._execute_request(request)

        with self._lock:
            self._total_strategic += 1

        return result

    def execute_trade(self, trade: Mapping[str, str]) -> ExecutionResult:
        """Execute a tactical trade.

        Args:
            trade: Trade parameters (symbol, size, price, etc.)

        Returns:
            ExecutionResult with trade execution outcome
        """
        request = ExecutionRequest(
            request_id=f"tactical_{self._get_timestamp()}",
            execution_type=ExecutionType.TACTICAL,
            source="INDIRA",
            payload=trade,
            priority=7,
            preferred_lane=ExecutionLane.FAST_LANE,
            timestamp_ns=self._get_timestamp(),
        )

        result = self._execute_request(request)

        with self._lock:
            self._total_tactical += 1

        return result

    def route_order(self, order: Mapping[str, str]) -> ExecutionResult:
        """Route an order to appropriate venue/adapter.

        Args:
            order: Order parameters

        Returns:
            ExecutionResult with routing outcome
        """
        request = ExecutionRequest(
            request_id=f"route_{self._get_timestamp()}",
            execution_type=ExecutionType.TACTICAL,
            source="INDIRA",
            payload=order,
            priority=6,
            preferred_lane=ExecutionLane.FAST_LANE,
            timestamp_ns=self._get_timestamp(),
        )

        return self._execute_request(request)

    def monitor_execution(self, execution_id: str) -> ExecutionStatus | None:
        """Monitor the status of an execution.

        Args:
            execution_id: Execution request ID to monitor

        Returns:
            Current execution status, or None if not found
        """
        with self._lock:
            # Check active requests first
            if execution_id in self._active_requests:
                return ExecutionStatus.EXECUTING
            
            # Check execution history
            for result in self._execution_history.values():
                if result.request_id == execution_id:
                    return result.status
            
            # Also check if execution_id matches result_id (some systems use result_id for monitoring)
            if execution_id in self._execution_history:
                return self._execution_history[execution_id].status
            
            return None

    def handle_hazard(self, hazard: Mapping[str, str]) -> ExecutionResult:
        """Handle a hazard event in the execution layer.

        Args:
            hazard: Hazard event details

        Returns:
            ExecutionResult with hazard handling outcome
        """
        request = ExecutionRequest(
            request_id=f"hazard_{self._get_timestamp()}",
            execution_type=ExecutionType.EMERGENCY,
            source="hazard_bus",
            payload=hazard,
            priority=10,
            preferred_lane=ExecutionLane.HAZARD_LANE,
            timestamp_ns=self._get_timestamp(),
        )

        return self._execute_request(request)

    def execute_intent(self, intent: Intent) -> Action:
        """Execute an intent from INDIRA (intent → action boundary).

        Args:
            intent: Intent from INDIRA

        Returns:
            Action implementation result
        """
        action = Action(
            action_id=f"action_{intent.intent_id}",
            intent_id=intent.intent_id,
            action_type=f"{intent.intent_type}_execution",
            parameters=intent.content,
            status="PENDING",
            timestamp_ns=self._get_timestamp(),
        )

        # Execute based on intent type
        if intent.intent_type == "trading":
            # Convert trading intent to trade execution
            result = self.execute_trade(intent.content)
            action = dataclasses.replace(action, status="COMPLETED", result=result.outcome)
        elif intent.intent_type == "portfolio":
            # Convert portfolio intent to strategic execution
            result = self.execute_strategy(intent.content)
            action = dataclasses.replace(action, status="COMPLETED", result=result.outcome)
        else:
            # Unknown intent type
            action = dataclasses.replace(action, status="FAILED", result={"error": "Unknown intent type"})

        return action

    def get_execution_statistics(self) -> dict[str, int | str]:
        """Get execution statistics."""
        with self._lock:
            return {
                "total_executions": self._total_executions,
                "total_strategic": self._total_strategic,
                "total_tactical": self._total_tactical,
                "total_failures": self._total_failures,
                "active_requests": len(self._active_requests),
                "success_rate": (
                    (self._total_executions - self._total_failures) / self._total_executions
                    if self._total_executions > 0
                    else 1.0
                ),
            }

    # ------------------------------------------------------------------
    # Private methods
    # ------------------------------------------------------------------

    def _execute_request(self, request: ExecutionRequest) -> ExecutionResult:
        """Execute an execution request internally."""
        # Store the active request
        with self._lock:
            self._active_requests[request.request_id] = request

        # Execute in the appropriate lane
        lane = self._select_execution_lane(request)
        start_time = self._get_timestamp()

        try:
            # Execute the request (placeholder implementation)
            outcome = self._perform_execution(request, lane)
            status = ExecutionStatus.COMPLETED

            with self._lock:
                self._total_executions += 1

        except Exception as e:
            _logger.error(f"Execution failed for request {request.request_id}: {e}")
            outcome = {"error": str(e)}
            status = ExecutionStatus.FAILED

            with self._lock:
                self._total_executions += 1
                self._total_failures += 1

        end_time = self._get_timestamp()
        execution_time = end_time - start_time

        # Create the result
        result = ExecutionResult(
            result_id=f"result_{request.request_id}",
            request_id=request.request_id,
            status=status,
            executed_lane=lane,
            outcome=MappingProxyType(outcome),
            execution_time_ns=execution_time,
            timestamp_ns=end_time,
        )

        # Update history and remove from active
        with self._lock:
            self._execution_history[result.result_id] = result
            if request.request_id in self._active_requests:
                del self._active_requests[request.request_id]

        return result

    def _select_execution_lane(self, request: ExecutionRequest) -> ExecutionLane:
        """Select the appropriate execution lane for a request."""
        # Check if preferred lane is available
        if self._lane_status.get(request.preferred_lane, False):
            return request.preferred_lane

        # Fall back to normal lane
        if self._lane_status.get(ExecutionLane.NORMAL_LANE, False):
            return ExecutionLane.NORMAL_LANE

        # Last resort: hazard lane (always available)
        return ExecutionLane.HAZARD_LANE

    def _perform_execution(
        self,
        request: ExecutionRequest,
        lane: ExecutionLane,
    ) -> dict[str, str]:
        """Perform the actual execution (placeholder)."""
        # TODO: Implement actual execution logic
        return {"executed": True, "lane": lane.value, "timestamp": str(self._get_timestamp())}

    def _get_timestamp(self) -> int:
        """Get current timestamp in nanoseconds."""
        # In production, this would use the system time source
        return 0  # TODO: Integrate with proper time source


# Singleton instance
_singleton: UnifiedExecutionKernel | None = None
_lock = threading.Lock()


def get_unified_execution_kernel() -> UnifiedExecutionKernel:
    """Get the singleton unified execution kernel instance."""
    global _singleton
    if _singleton is None:
        with _lock:
            if _singleton is None:
                _singleton = UnifiedExecutionKernel()
    return _singleton


__all__ = [
    "UnifiedExecutionKernel",
    "get_unified_execution_kernel",
    "ExecutionRequest",
    "ExecutionResult",
    "ExecutionType",
    "ExecutionLane",
    "ExecutionStatus",
    "Intent",
    "Action",
]