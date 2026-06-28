"""
execution_unified.resilience.state_recovery
DIX VISION v42.2 — State Recovery System (Priority 1)

Provides advanced state synchronization and recovery for distributed execution.
Builds on checkpoint manager to add multi-replica state management.
"""

from __future__ import annotations

import hashlib
import json
import logging
import threading
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from .checkpoint_manager import CheckpointManager, get_checkpoint_manager

logger = logging.getLogger(__name__)


class ReplicaState(Enum):
    """Replica state synchronization status."""

    SYNCHRONIZED = "SYNCHRONIZED"
    OUT_OF_SYNC = "OUT_OF_SYNC"
    RECOVERING = "RECOVERING"
    UNKNOWN = "UNKNOWN"


@dataclass
class StateDifference:
    """Difference between two state snapshots."""

    field_name: str
    old_value: Any
    new_value: Any
    difference_type: str  # ADDED, MODIFIED, DELETED
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class StateComparisonResult:
    """Result of state comparison between replicas."""

    replica_id: str
    is_synchronized: bool
    differences: List[StateDifference] = field(default_factory=list)
    similarity_score: float = 0.0
    comparison_timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class StateReconciliationResult:
    """Result of state reconciliation."""

    success: bool
    reconciled_fields: List[str] = field(default_factory=list)
    failed_fields: List[str] = field(default_factory=list)
    reconciliation_time_ms: float = 0.0
    final_state: Optional[Dict[str, Any]] = None
    error_message: str = ""


@dataclass
class TransactionValidation:
    """Transaction validation for state updates."""

    transaction_id: str
    is_valid: bool
    validation_errors: List[str] = field(default_factory=list)
    rollback_data: Optional[Dict[str, Any]] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)


class ReplicaStateManager:
    """Manages state for a specific replica."""

    def __init__(self, replica_id: str, initial_state: Optional[Dict[str, Any]] = None):
        self._replica_id = replica_id
        self._lock = threading.Lock()
        self._current_state = initial_state or {}
        self._state_history: List[Dict[str, Any]] = []
        self._last_updated = datetime.utcnow()
        self._replica_state = ReplicaState.UNKNOWN

        logger.info(f"[STATE_RECOVERY] Replica state manager initialized for {replica_id}")

    def update_state(self, new_state: Dict[str, Any]) -> None:
        """Update replica state."""
        with self._lock:
            # Store previous state in history
            if self._current_state:
                self._state_history.append(self._current_state.copy())

            self._current_state = new_state.copy()
            self._last_updated = datetime.utcnow()
            self._replica_state = ReplicaState.SYNCHRONIZED

    def get_state(self) -> Dict[str, Any]:
        """Get current state."""
        with self._lock:
            return self._current_state.copy()

    def get_state_hash(self) -> str:
        """Get hash of current state."""
        with self._lock:
            state_str = json.dumps(self._current_state, sort_keys=True)
            return hashlib.sha256(state_str.encode()).hexdigest()

    def compare_state(self, other_state: Dict[str, Any]) -> StateComparisonResult:
        """Compare current state with another state."""
        with self._lock:
            differences = []

            # Compare fields
            all_keys = set(self._current_state.keys()) | set(other_state.keys())

            for key in all_keys:
                if key not in self._current_state:
                    differences.append(
                        StateDifference(
                            field_name=key,
                            old_value=None,
                            new_value=other_state.get(key),
                            difference_type="ADDED",
                        )
                    )
                elif key not in other_state:
                    differences.append(
                        StateDifference(
                            field_name=key,
                            old_value=self._current_state.get(key),
                            new_value=None,
                            difference_type="DELETED",
                        )
                    )
                elif self._current_state[key] != other_state[key]:
                    differences.append(
                        StateDifference(
                            field_name=key,
                            old_value=self._current_state[key],
                            new_value=other_state[key],
                            difference_type="MODIFIED",
                        )
                    )

            # Calculate similarity score
            if len(all_keys) == 0:
                similarity_score = 1.0
            else:
                similarity_score = 1.0 - (len(differences) / len(all_keys))

            is_synchronized = len(differences) == 0

            return StateComparisonResult(
                replica_id=self._replica_id,
                is_synchronized=is_synchronized,
                differences=differences,
                similarity_score=similarity_score,
            )


class StateRecoverySystem:
    """
    Advanced state synchronization and recovery system.

    Features:
    - Multi-replica state management
    - State comparison and reconciliation
    - Transaction validation
    - Automatic recovery coordination
    - Conflict resolution
    """

    def __init__(self, checkpoint_manager: Optional[CheckpointManager] = None):
        self._lock = threading.Lock()
        self._checkpoint_manager = checkpoint_manager or get_checkpoint_manager()
        self._replicas: Dict[str, ReplicaStateManager] = {}
        self._active_recovery: Optional[str] = None
        self._recovery_coordinator = RecoveryCoordinator(self)

        # Transaction tracking
        self._active_transactions: Dict[str, Dict[str, Any]] = {}

        logger.info("[STATE_RECOVERY] State Recovery System initialized")

    def register_replica(
        self, replica_id: str, initial_state: Optional[Dict[str, Any]] = None
    ) -> None:
        """Register a replica for state management."""
        with self._lock:
            replica = ReplicaStateManager(replica_id, initial_state)
            self._replicas[replica_id] = replica
            logger.info(f"[STATE_RECOVERY] Registered replica: {replica_id}")

    def synchronize_state(
        self, component: str, target_state: Dict[str, Any], replica_ids: Optional[List[str]] = None
    ) -> StateReconciliationResult:
        """
        Synchronize state across all replicas.

        Args:
            component: Component name
            target_state: Desired state
            replica_ids: Specific replicas to sync (None = all)

        Returns:
            Reconciliation result
        """
        start_time = datetime.utcnow()

        with self._lock:
            if not self._replicas:
                return StateReconciliationResult(
                    success=False, error_message="No replicas registered"
                )

            target_replicas = replica_ids or list(self._replicas.keys())
            reconciled_fields = []
            failed_fields = []

            for replica_id in target_replicas:
                if replica_id in self._replicas:
                    try:
                        replica = self._replicas[replica_id]

                        # Update state
                        replica.update_state(target_state)
                        reconciled_fields.append(replica_id)

                    except Exception as e:
                        logger.error(f"[STATE_RECOVERY] Failed to sync {replica_id}: {e}")
                        failed_fields.append(replica_id)
                else:
                    logger.warning(f"[STATE_RECOVERY] Replica {replica_id} not found")
                    failed_fields.append(replica_id)

            # Create checkpoint after synchronization
            try:
                self._checkpoint_manager.create_checkpoint(
                    component=component,
                    state_data=target_state,
                    metadata={"sync_replicas": target_replicas},
                )
            except Exception as e:
                logger.warning(f"[STATE_RECOVERY] Failed to create checkpoint: {e}")

        reconciliation_time_ms = (datetime.utcnow() - start_time).total_seconds() * 1000

        return StateReconciliationResult(
            success=len(failed_fields) == 0,
            reconciled_fields=reconciled_fields,
            failed_fields=failed_fields,
            reconciliation_time_ms=reconciliation_time_ms,
            final_state=target_state,
        )

    def compare_replica_states(
        self, replica_ids: Optional[List[str]] = None
    ) -> Dict[str, StateComparisonResult]:
        """
        Compare state across replicas to detect divergence.

        Args:
            replica_ids: Specific replicas to compare (None = all)

        Returns:
            Comparison results for each replica
        """
        with self._lock:
            if len(self._replicas) < 2:
                logger.warning("[STATE_RECOVERY] Need at least 2 replicas to compare states")
                return {}

            target_replicas = replica_ids or list(self._replicas.keys())

            # Use first replica as baseline
            baseline_replica = self._replicas[target_replicas[0]]
            baseline_state = baseline_replica.get_state()

            comparison_results = {}

            for replica_id in target_replicas[1:]:
                if replica_id in self._replicas:
                    comparison = self._replicas[replica_id].compare_state(baseline_state)
                    comparison_results[replica_id] = comparison

            return comparison_results

    def reconcile_state_differences(
        self,
        differences: Dict[str, StateComparisonResult],
        conflict_resolution: str = "LATEST_WINS",  # LATEST_WINS, MAJORITY_WINS, MANUAL
    ) -> StateReconciliationResult:
        """
        Reconcile state differences across replicas.

        Args:
            differences: State differences to reconcile
            conflict_resolution: Strategy for conflict resolution

        Returns:
            Reconciliation result
        """
        start_time = datetime.utcnow()

        try:
            reconciled_state = self._recovery_coordinator.reconcile(
                differences, conflict_resolution
            )

            # Apply reconciled state to all replicas
            component = "reconciled_state"
            sync_result = self.synchronize_state(
                component, reconciled_state, list(differences.keys())
            )

            reconciliation_time_ms = (datetime.utcnow() - start_time).total_seconds() * 1000

            return StateReconciliationResult(
                success=sync_result.success,
                reconciled_fields=sync_result.reconciled_fields,
                failed_fields=sync_result.failed_fields,
                reconciliation_time_ms=reconciliation_time_ms,
                final_state=reconciled_state,
            )

        except Exception as e:
            logger.error(f"[STATE_RECOVERY] State reconciliation failed: {e}")
            return StateReconciliationResult(
                success=False,
                error_message=str(e),
                reconciliation_time_ms=(datetime.utcnow() - start_time).total_seconds() * 1000,
            )

    def validate_transaction(
        self, transaction_id: str, state_changes: Dict[str, Any], component: str
    ) -> TransactionValidation:
        """
        Validate a state change transaction.

        Args:
            transaction_id: Transaction identifier
            state_changes: State changes to apply
            component: Component name

        Returns:
            Validation result
        """
        validation_errors = []

        # Check if transaction already exists
        if transaction_id in self._active_transactions:
            validation_errors.append(f"Transaction {transaction_id} already active")

        # Validate state changes
        try:
            # Get current state from primary replica
            if self._replicas:
                primary_replica = list(self._replicas.values())[0]
                current_state = primary_replica.get_state()

                # Check for conflicts
                for field, new_value in state_changes.items():
                    if field in current_state and current_state[field] != new_value:
                        # Check for conflicting transactions
                        if self._has_conflicting_transaction(field, transaction_id):
                            validation_errors.append(
                                f"Conflict on field {field} with another transaction"
                            )

        except Exception as e:
            validation_errors.append(f"State validation error: {str(e)}")

        is_valid = len(validation_errors) == 0

        if is_valid:
            # Store transaction
            self._active_transactions[transaction_id] = {
                "state_changes": state_changes,
                "component": component,
                "timestamp": datetime.utcnow(),
            }

        return TransactionValidation(
            transaction_id=transaction_id, is_valid=is_valid, validation_errors=validation_errors
        )

    def commit_transaction(self, transaction_id: str) -> bool:
        """Commit a validated transaction."""
        with self._lock:
            if transaction_id not in self._active_transactions:
                logger.error(f"[STATE_RECOVERY] Transaction {transaction_id} not found")
                return False

            transaction = self._active_transactions[transaction_id]

            try:
                # Apply state changes
                if self._replicas:
                    for replica in self._replicas.values():
                        current_state = replica.get_state()
                        current_state.update(transaction["state_changes"])
                        replica.update_state(current_state)

                # Create checkpoint
                self._checkpoint_manager.create_checkpoint(
                    component=transaction["component"],
                    state_data=self._replicas[list(self._replicas.keys())[0]].get_state(),
                    metadata={"transaction_id": transaction_id},
                )

                # Remove from active transactions
                del self._active_transactions[transaction_id]

                logger.info(f"[STATE_RECOVERY] Transaction {transaction_id} committed successfully")
                return True

            except Exception as e:
                logger.error(f"[STATE_RECOVERY] Failed to commit transaction {transaction_id}: {e}")
                return False

    def rollback_transaction(self, transaction_id: str) -> bool:
        """Rollback a transaction."""
        with self._lock:
            if transaction_id not in self._active_transactions:
                logger.error(f"[STATE_RECOVERY] Transaction {transaction_id} not found")
                return False

            # Remove from active transactions (state remains unchanged)
            del self._active_transactions[transaction_id]

            logger.info(f"[STATE_RECOVERY] Transaction {transaction_id} rolled back")
            return True

    def _has_conflicting_transaction(self, field: str, transaction_id: str) -> bool:
        """Check if field has conflicting transactions."""
        for trans_id, trans_data in self._active_transactions.items():
            if trans_id != transaction_id:
                if field in trans_data["state_changes"]:
                    return True
        return False

    def get_recovery_statistics(self) -> Dict[str, Any]:
        """Get state recovery statistics."""
        with self._lock:
            return {
                "registered_replicas": len(self._replicas),
                "replica_ids": list(self._replicas.keys()),
                "active_transactions": len(self._active_transactions),
                "active_recovery": self._active_recovery,
                "checkpoint_count": len(
                    self._checkpoint_manager.get_checkpoint_statistics()["component_counts"]
                ),
            }


class RecoveryCoordinator:
    """Coordinates recovery operations across replicas."""

    def __init__(self, recovery_system: StateRecoverySystem):
        self._recovery_system = recovery_system
        self._lock = threading.Lock()

    def reconcile(
        self,
        differences: Dict[str, StateComparisonResult],
        conflict_resolution: str = "LATEST_WINS",
    ) -> Dict[str, Any]:
        """Reconcile state differences."""
        if not differences:
            return {}

        if conflict_resolution == "LATEST_WINS":
            # Use most recent state
            return self._reconcile_latest_wins(differences)
        elif conflict_resolution == "MAJORITY_WINS":
            # Use state from majority of replicas
            return self._reconcile_majority_wins(differences)
        elif conflict_resolution == "MANUAL":
            # Leave for manual intervention
            logger.warning("[RECOVERY_COORDINATOR] Manual reconciliation requested")
            return {}
        else:
            logger.error(
                f"[RECOVERY_COORDINATOR] Unknown conflict resolution: {conflict_resolution}"
            )
            return {}

    def _reconcile_latest_wins(
        self, differences: Dict[str, StateComparisonResult]
    ) -> Dict[str, Any]:
        """Reconcile using latest state (by timestamp)."""
        # Placeholder - implement latest wins logic
        return {"strategy": "LATEST_WINS", "reconciled": True}

    def _reconcile_majority_wins(
        self, differences: Dict[str, StateComparisonResult]
    ) -> Dict[str, Any]:
        """Reconcile using majority state."""
        # Placeholder - implement majority wins logic
        return {"strategy": "MAJORITY_WINS", "reconciled": True}


# Singleton instance
_state_recovery_system: Optional[StateRecoverySystem] = None
_state_recovery_lock = threading.Lock()


def get_state_recovery_system(
    checkpoint_manager: Optional[CheckpointManager] = None,
) -> StateRecoverySystem:
    """Get the singleton state recovery system instance."""
    global _state_recovery_system
    if _state_recovery_system is None:
        with _state_recovery_lock:
            if _state_recovery_system is None:
                _state_recovery_system = StateRecoverySystem(checkpoint_manager)
    return _state_recovery_system


def get_state_recovery(
    checkpoint_manager: Optional[CheckpointManager] = None,
) -> StateRecoverySystem:
    """Get the singleton state recovery system instance (alias for get_state_recovery_system)."""
    return get_state_recovery_system(checkpoint_manager)


__all__ = [
    "ReplicaState",
    "StateDifference",
    "StateComparisonResult",
    "StateReconciliationResult",
    "TransactionValidation",
    "ReplicaStateManager",
    "StateRecoverySystem",
    "get_state_recovery_system",
    "get_state_recovery",
]
