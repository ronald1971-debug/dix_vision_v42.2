"""
execution_unified.resilience.checkpoint_manager
DIX VISION v42.2 — State Checkpoint Manager (Quick Win)

Provides basic checkpointing capabilities for state synchronization and recovery.
This is a quick win implementation for execution resilience.
"""

from __future__ import annotations

import hashlib
import json
import logging
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


@dataclass
class Checkpoint:
    """System state checkpoint."""

    checkpoint_id: str
    timestamp: datetime
    component: str
    state_data: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)
    checksum: str = ""

    def __post_init__(self):
        # Calculate checksum for data integrity
        state_hash = hashlib.sha256(
            json.dumps(self.state_data, sort_keys=True).encode()
        ).hexdigest()
        self.checksum = state_hash


@dataclass
class CheckpointRestoreResult:
    """Result of checkpoint restoration."""

    success: bool
    checkpoint_id: str
    restored_state: Optional[Dict[str, Any]] = None
    verification_passed: bool = False
    error_message: str = ""
    restoration_time_ms: float = 0.0


class CheckpointManager:
    """Manages system state checkpoints for resilience and recovery."""

    def __init__(self, checkpoint_dir: str = "checkpoints", max_checkpoints: int = 10):
        self._lock = threading.Lock()
        self._checkpoint_dir = Path(checkpoint_dir)
        self._max_checkpoints = max_checkpoints
        self._checkpoints: Dict[str, Checkpoint] = {}

        # Create checkpoint directory
        self._checkpoint_dir.mkdir(parents=True, exist_ok=True)

        # Load existing checkpoints
        self._load_existing_checkpoints()

        logger.info(
            f"[CHECKPOINT_MANAGER] Initialized with {len(self._checkpoints)} existing checkpoints"
        )

    def create_checkpoint(
        self, component: str, state_data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None
    ) -> Checkpoint:
        """
        Create a checkpoint for component state.

        Args:
            component: Component name (e.g., "execution_kernel", "indira_brain")
            state_data: Current state data to checkpoint
            metadata: Additional metadata

        Returns:
            Created checkpoint
        """
        with self._lock:
            checkpoint_id = f"{component}_{int(time.time() * 1000)}"

            checkpoint = Checkpoint(
                checkpoint_id=checkpoint_id,
                timestamp=datetime.utcnow(),
                component=component,
                state_data=state_data,
                metadata=metadata or {},
            )

            # Store in memory
            self._checkpoints[checkpoint_id] = checkpoint

            # Persist to disk
            self._persist_checkpoint(checkpoint)

            # Remove old checkpoints if exceeding limit
            self._cleanup_old_checkpoints(component)

            logger.info(f"[CHECKPOINT_MANAGER] Created checkpoint {checkpoint_id} for {component}")

            return checkpoint

    def get_latest_checkpoint(self, component: str) -> Optional[Checkpoint]:
        """Get the latest checkpoint for a component."""
        with self._lock:
            component_checkpoints = [
                cp for cp in self._checkpoints.values() if cp.component == component
            ]

            if component_checkpoints:
                # Sort by timestamp, most recent first
                component_checkpoints.sort(key=lambda cp: cp.timestamp, reverse=True)
                return component_checkpoints[0]

            return None

    def restore_checkpoint(self, checkpoint_id: str) -> CheckpointRestoreResult:
        """
        Restore system state from a checkpoint.

        Args:
            checkpoint_id: Checkpoint to restore

        Returns:
            Restore result
        """
        start_time = time.time()

        with self._lock:
            if checkpoint_id not in self._checkpoints:
                return CheckpointRestoreResult(
                    success=False, checkpoint_id=checkpoint_id, error_message="Checkpoint not found"
                )

            checkpoint = self._checkpoints[checkpoint_id]

            # Verify checksum
            current_hash = hashlib.sha256(
                json.dumps(checkpoint.state_data, sort_keys=True).encode()
            ).hexdigest()

            verification_passed = current_hash == checkpoint.checksum

            if not verification_passed:
                logger.error(
                    f"[CHECKPOINT_MANAGER] Checkpoint {checkpoint_id} checksum verification failed"
                )
                return CheckpointRestoreResult(
                    success=False,
                    checkpoint_id=checkpoint_id,
                    verification_passed=False,
                    error_message="Checksum verification failed",
                    restoration_time_ms=(time.time() - start_time) * 1000,
                )

            restoration_time_ms = (time.time() - start_time) * 1000

            logger.info(
                f"[CHECKPOINT_MANAGER] Restored checkpoint {checkpoint_id} in {restoration_time_ms:.2f}ms"
            )

            return CheckpointRestoreResult(
                success=True,
                checkpoint_id=checkpoint_id,
                restored_state=checkpoint.state_data,
                verification_passed=True,
                restoration_time_ms=restoration_time_ms,
            )

    def _persist_checkpoint(self, checkpoint: Checkpoint) -> None:
        """Persist checkpoint to disk."""
        try:
            checkpoint_file = self._checkpoint_dir / f"{checkpoint.checkpoint_id}.json"

            checkpoint_data = {
                "checkpoint_id": checkpoint.checkpoint_id,
                "timestamp": checkpoint.timestamp.isoformat(),
                "component": checkpoint.component,
                "state_data": checkpoint.state_data,
                "metadata": checkpoint.metadata,
                "checksum": checkpoint.checksum,
            }

            with open(checkpoint_file, "w") as f:
                json.dump(checkpoint_data, f, indent=2)

        except Exception as e:
            logger.error(
                f"[CHECKPOINT_MANAGER] Failed to persist checkpoint {checkpoint.checkpoint_id}: {e}"
            )

    def _load_existing_checkpoints(self) -> None:
        """Load existing checkpoints from disk."""
        try:
            for checkpoint_file in self._checkpoint_dir.glob("*.json"):
                with open(checkpoint_file, "r") as f:
                    checkpoint_data = json.load(f)

                checkpoint = Checkpoint(
                    checkpoint_id=checkpoint_data["checkpoint_id"],
                    timestamp=datetime.fromisoformat(checkpoint_data["timestamp"]),
                    component=checkpoint_data["component"],
                    state_data=checkpoint_data["state_data"],
                    metadata=checkpoint_data.get("metadata", {}),
                    checksum=checkpoint_data.get("checksum", ""),
                )

                self._checkpoints[checkpoint.checkpoint_id] = checkpoint

        except Exception as e:
            logger.warning(f"[CHECKPOINT_MANAGER] Failed to load existing checkpoints: {e}")

    def _cleanup_old_checkpoints(self, component: str) -> None:
        """Remove old checkpoints for a component, keeping only the most recent."""
        component_checkpoints = [
            (cp_id, cp) for cp_id, cp in self._checkpoints.items() if cp.component == component
        ]

        if len(component_checkpoints) > self._max_checkpoints:
            # Sort by timestamp, oldest first
            component_checkpoints.sort(key=lambda x: x[1].timestamp)

            # Remove oldest checkpoints
            for cp_id, _ in component_checkpoints[: -self._max_checkpoints]:
                del self._checkpoints[cp_id]

                # Remove from disk
                checkpoint_file = self._checkpoint_dir / f"{cp_id}.json"
                if checkpoint_file.exists():
                    checkpoint_file.unlink()

    def get_checkpoint_statistics(self) -> Dict[str, Any]:
        """Get checkpoint statistics."""
        with self._lock:
            component_counts = {}
            for checkpoint in self._checkpoints.values():
                component_counts[checkpoint.component] = (
                    component_counts.get(checkpoint.component, 0) + 1
                )

            return {
                "total_checkpoints": len(self._checkpoints),
                "checkpoint_dir": str(self._checkpoint_dir),
                "max_checkpoints": self._max_checkpoints,
                "component_counts": component_counts,
                "oldest_checkpoint": (
                    min(cp.timestamp for cp in self._checkpoints.values())
                    if self._checkpoints
                    else None
                ),
                "newest_checkpoint": (
                    max(cp.timestamp for cp in self._checkpoints.values())
                    if self._checkpoints
                    else None
                ),
            }


# Singleton instance
_checkpoint_manager: Optional[CheckpointManager] = None
_checkpoint_manager_lock = threading.Lock()


def get_checkpoint_manager(
    checkpoint_dir: str = "checkpoints", max_checkpoints: int = 10
) -> CheckpointManager:
    """Get the singleton checkpoint manager instance."""
    global _checkpoint_manager
    if _checkpoint_manager is None:
        with _checkpoint_manager_lock:
            if _checkpoint_manager is None:
                _checkpoint_manager = CheckpointManager(checkpoint_dir, max_checkpoints)
    return _checkpoint_manager


__all__ = [
    "Checkpoint",
    "CheckpointRestoreResult",
    "CheckpointManager",
    "get_checkpoint_manager",
]
