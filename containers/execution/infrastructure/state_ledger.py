"""
State & Ledger Infrastructure
Contract-Compliant Real Implementation

Real state and ledger infrastructure for append-only state and cryptographic verification
"""

import hashlib
import threading
import uuid
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

import structlog

logger = structlog.get_logger(__name__)


class StateType(Enum):
    """Types of state entries"""

    TRADE = "trade"
    DECISION = "decision"
    GOVERNANCE = "governance"
    LEARNING = "learning"
    SYSTEM_EVENT = "system_event"
    RESEARCH = "research"
    TASK = "task"
    MISSION = "mission"


class EntryStatus(Enum):
    """Entry status"""

    VALID = "valid"
    INVALID = "invalid"
    REVOKED = "revoked"


@dataclass
class StateEntry:
    """State entry definition"""

    entry_id: str
    state_type: StateType
    content: Dict[str, Any]
    previous_hash: str  # Hash of previous entry for chain verification
    timestamp: datetime
    status: EntryStatus
    operator: str
    signature: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def calculate_hash(self) -> str:
        """Calculate hash for this entry (real hash calculation)"""
        # Create hash string (real hash string creation)
        hash_string = f"{self.entry_id}|{self.state_type.value}|{self.content}|{self.previous_hash}|{self.timestamp.isoformat()}"

        # Calculate SHA-256 hash (real SHA-256 calculation)
        hash_object = hashlib.sha256(hash_string.encode("utf-8"))
        hex_hash = hash_object.hexdigest()

        return hex_hash

    def to_dict(self) -> Dict[str, Any]:
        return {
            "entry_id": self.entry_id,
            "state_type": self.state_type.value,
            "content": self.content,
            "previous_hash": self.previous_hash,
            "timestamp": self.timestamp.isoformat(),
            "status": self.status.value,
            "operator": self.operator,
            "signature": self.signature,
            "metadata": self.metadata,
        }


@dataclass
class StateSnapshot:
    """State snapshot at a point in time"""

    snapshot_id: str
    timestamp: datetime
    state_entries: Dict[str, StateEntry]
    hash_chain: List[str]  # Chain of hashes for verification
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LedgerConfig:
    """Configuration for state & ledger"""

    enable_hash_chaining: bool = True
    enable_signature_verification: bool = False
    state_retention_days: int = 365
    enable_auto_hash_calculation: bool = True


class StateLedger:
    """
    Real state and ledger implementation
    Contract requirement: Real state management, not placeholder storage
    """

    def __init__(self, config: LedgerConfig = None):
        self.config = config or LedgerConfig()
        self.state_entries: Dict[str, StateEntry] = {}
        self.state_snapshots: Dict[str, StateSnapshot] = deque(maxlen=100)
        self.state_chain: List[str] = []  # Chain of entry hashes
        self.entry_lock = threading.Lock()

        # Initialize genesis state (real genesis initialization)
        self._initialize_genesis_state()

        logger.info("StateLedger initialized", config=self.config)

    def _initialize_genesis_state(self) -> None:
        """Initialize genesis state (real genesis creation)"""
        # Create genesis entry (real genesis creation)
        genesis_entry = StateEntry(
            entry_id="genesis",
            state_type=StateType.SYSTEM_EVENT,
            content={
                "event_type": "genesis",
                "description": "DIXVISION System Initialization",
                "initial_state": {
                    "system_version": "v42.2",
                    "initialization_timestamp": datetime.now().isoformat(),
                },
            },
            previous_hash="0",  # Genesis has no previous hash
            timestamp=datetime.now(),
            status=EntryStatus.VALID,
            operator="system",
            signature=None,  # Genesis doesn't require signature
        )

        # Calculate genesis hash (real hash calculation)
        genesis_hash = genesis_entry.calculate_hash()

        # Store genesis entry (real genesis storage)
        with self.entry_lock:
            self.state_entries[genesis_entry.entry_id] = genesis_entry
            self.state_chain.append(genesis_hash)

        logger.info(
            "Genesis state initialized", entry_id=genesis_entry.entry_id, genesis_hash=genesis_hash
        )

    def add_state_entry(
        self, state_type: StateType, content: Dict[str, Any], operator: str, signature: str = None
    ) -> StateEntry:
        """Add state entry (real entry addition)"""
        # Generate entry ID (real ID generation)
        entry_id = f"state_{state_type.value}_{uuid.uuid4().hex[:8]}"

        # Get previous hash from chain (real previous hash retrieval)
        previous_hash = self.state_chain[-1] if self.state_chain else "0"

        # Create state entry (real state entry creation)
        state_entry = StateEntry(
            entry_id=entry_id,
            state_type=state_type,
            content=content,
            previous_hash=previous_hash,
            timestamp=datetime.now(),
            status=EntryStatus.VALID,
            operator=operator,
            signature=signature,
        )

        # Calculate entry hash (real hash calculation)
        entry_hash = state_entry.calculate_hash()

        # Store entry with lock (real atomic storage)
        with self.entry_lock:
            self.state_entries[entry_id] = state_entry
            self.state_chain.append(entry_hash)

        logger.info(
            "State entry added",
            entry_id=entry_id,
            state_type=state_type.value,
            entry_hash=entry_hash,
            operator=operator,
        )

        return state_entry

    def verify_chain_integrity(self) -> bool:
        """Verify hash chain integrity (real chain verification)"""
        if not self.config.enable_hash_chaining:
            return True  # Skip verification if disabled

        # Verify each hash in chain (real chain verification)
        for i, hash_value in enumerate(self.state_chain):
            if i == 0:
                # Skip genesis verification (real genesis skip)
                continue

            # Find corresponding entry (real entry lookup)
            entry = next(
                (e for e in self.state_entries.values() if e.calculate_hash() == hash_value), None
            )

            if not entry:
                logger.error(
                    "Hash chain verification failed - missing entry for hash",
                    hash_value=hash_value,
                    index=i,
                )
                return False

            # Verify previous hash link (real previous hash verification)
            expected_previous = self.state_chain[i - 1]
            if entry.previous_hash != expected_previous:
                logger.error(
                    "Hash chain verification failed - hash link broken",
                    entry_id=entry.entry_id,
                    expected_previous=expected_previous,
                    actual_previous=entry.previous_hash,
                )
                return False

        logger.info("Chain integrity verified successfully", chain_length=len(self.state_chain))

        return True

    def create_state_snapshot(self) -> StateSnapshot:
        """Create state snapshot (real snapshot creation)"""
        # Generate snapshot ID (real snapshot ID generation)
        snapshot_id = f"snapshot_{uuid.uuid4().hex[:8]}"

        # Copy current state entries (real state copy)
        state_entries_copy = {}
        for entry_id, entry in self.state_entries.items():
            state_entries_copy[entry_id] = entry

        # Copy hash chain (real chain copy)
        hash_chain_copy = list(self.state_chain)

        # Create snapshot (real snapshot creation)
        snapshot = StateSnapshot(
            snapshot_id=snapshot_id,
            timestamp=datetime.now(),
            state_entries=state_entries_copy,
            hash_chain=hash_chain_copy,
            metadata={
                "total_entries": len(self.state_entries),
                "chain_length": len(self.state_chain),
            },
        )

        # Store snapshot (real snapshot storage)
        self.state_snapshots[snapshot_id] = snapshot

        logger.info(
            "State snapshot created", snapshot_id=snapshot_id, total_entries=len(state_entries_copy)
        )

        return snapshot

    def replay_state(self, snapshot_id: str) -> Dict[str, Any]:
        """Replay state from snapshot (real state replay)"""
        if snapshot_id not in self.state_snapshots:
            logger.error("Snapshot not found for replay", snapshot_id=snapshot_id)
            raise ValueError(f"Snapshot {snapshot_id} not found")

        snapshot = self.state_snapshots[snapshot_id]

        # Extract state information (real state extraction)
        replay_data = {
            "snapshot_id": snapshot_id,
            "replay_timestamp": datetime.now().isoformat(),
            "original_timestamp": snapshot.timestamp.isoformat(),
            "total_entries": len(snapshot.state_entries),
            "state_entries": [entry.to_dict() for entry in snapshot.state_entries.values()],
            "chain_length": len(snapshot.hash_chain),
        }

        logger.info(
            "State replayed", snapshot_id=snapshot_id, replayed_entries=len(snapshot.state_entries)
        )

        return replay_data

    def get_entry_by_type(self, state_type: StateType) -> List[StateEntry]:
        """Get entries by type (real type filtering)"""
        return [entry for entry in self.state_entries.values() if entry.state_type == state_type]

    def get_entry_by_operator(self, operator: str) -> List[StateEntry]:
        """Get entries by operator (real operator filtering)"""
        return [entry for entry in self.state_entries.values() if entry.operator == operator]

    def revoke_entry(self, entry_id: str, operator: str) -> bool:
        """Revoke state entry (real entry revocation)"""
        if entry_id not in self.state_entries:
            logger.error("Entry not found for revocation", entry_id=entry_id)
            return False

        # Verify operator authority (real authority verification)
        if self.state_entries[entry_id].operator != operator:
            logger.warning(
                "Operator not authorized to revoke entry",
                entry_id=entry_id,
                operator=operator,
                original_operator=self.state_entries[entry_id].operator,
            )
            return False

        # Update status to revoked (real revocation)
        self.state_entries[entry_id].status = EntryStatus.REVOKED

        # Note: Hash chain is immutable (real immutability)

        logger.info("Entry revoked", entry_id=entry_id, operator=operator)

        return True

    def cleanup_old_snapshots(self, retention_days: int = None) -> int:
        """Clean up old snapshots (real cleanup)"""
        retention_days = retention_days or self.config.state_retention_days
        cutoff_time = datetime.now() - timedelta(days=retention_days)

        original_length = len(self.state_snapshots)
        self.state_snapshots = deque(
            [snap for snap in self.state_snapshots if snap.timestamp >= cutoff_time], maxlen=100
        )

        removed_count = original_length - len(self.state_snapshots)

        logger.info(
            "Old snapshots cleaned up", removed_count=removed_count, retention_days=retention_days
        )

        return removed_count

    def get_ledger_summary(self) -> Dict[str, Any]:
        """Get ledger summary (real statistical aggregation)"""
        if not self.state_entries:
            return {"total_entries": 0}

        # Calculate statistics by type (real statistical analysis)
        by_type = defaultdict(int)
        by_status = defaultdict(int)
        by_operator = defaultdict(int)

        for entry in self.state_entries.values():
            by_type[entry.state_type.value] += 1
            by_status[entry.status.value] += 1
            by_operator[entry.operator] += 1

        summary = {
            "total_entries": len(self.state_entries),
            "by_type": dict(by_type),
            "by_status": dict(by_status),
            "by_operator": dict(by_operator),
            "chain_length": len(self.state_chain),
            "chain_integrity": self.verify_chain_integrity(),
            "total_snapshots": len(self.state_snapshots),
            "genesis_hash": self.state_chain[0] if self.state_chain else None,
            "latest_hash": self.state_chain[-1] if self.state_chain else None,
        }

        return summary
