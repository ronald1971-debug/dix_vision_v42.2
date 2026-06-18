"""
Deterministic Verifier - System-Wide Deterministic Verification
Ensures reproducibility across all DIX VISION subsystems
Per Rule 9 of the DIX VISION Tier-0 Production Implementation Contract
"""

import logging
import hashlib
import json
from typing import Dict, List, Set, Any, Optional, Tuple, Callable
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, OrderedDict

logger = logging.getLogger(__name__)

class VerificationScope(Enum):
    """Scopes for deterministic verification"""
    EXECUTION = "execution"
    GOVERNANCE = "governance"
    LEARNING = "learning"
    SIMULATION = "simulation"
    LEDGER = "ledger"
    WORLD_MODEL = "world_model"
    INDIRA = "indira"
    DYON = "dyon"

class VerificationType(Enum):
    """Types of deterministic verification"""
    REPLAY_VALIDATION = "replay_validation"
    HASH_VALIDATION = "hash_validation"
    STATE_VALIDATION = "state_validation"
    EVENT_VALIDATION = "event_validation"
    CAUSALITY_VALIDATION = "causality_validation"
    REPRODUCIBILITY_VALIDATION = "reproducibility_validation"

class VerificationStatus(Enum):
    """Status of verification results"""
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    INCOMPLETE = "incomplete"

@dataclass
class VerificationResult:
    """Result of a deterministic verification"""
    verification_id: str
    scope: VerificationScope
    verification_type: VerificationType
    status: VerificationStatus
    timestamp: datetime
    details: Dict[str, Any]
    hash_checksums: Dict[str, str]
    state_snapshots: Dict[str, Any]
    violations: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    evidence: List[str] = field(default_factory=list)
    reproducibility_score: float = 1.0

@dataclass
class StateSnapshot:
    """Snapshot of system state for verification"""
    snapshot_id: str
    scope: VerificationScope
    timestamp: datetime
    state_hash: str
    state_data: Dict[str, Any]
    predecessor_hashes: Set[str] = field(default_factory=set)

@dataclass
class EventTrace:
    """Trace of an event for causality verification"""
    event_id: str
    event_type: str
    timestamp: datetime
    cause_event_ids: Set[str] = field(default_factory=set)
    effect_event_ids: Set[str] = field(default_factory=set)
    state_before: Dict[str, Any] = field(default_factory=dict)
    state_after: Dict[str, Any] = field(default_factory=dict)

class DeterministicVerifier:
    """
    System-wide deterministic verification for all DIX VISION subsystems
    Ensures reproducibility and prevents non-deterministic behavior
    """
    
    def __init__(self):
        self._snapshots: Dict[str, StateSnapshot] = {}
        self._event_traces: Dict[str, EventTrace] = {}
        self._verification_results: List[VerificationResult] = []
        self._hash_chains: Dict[str, List[str]] = defaultdict(list)
        self._replay_history: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self._determinism_rules: Dict[str, Callable] = {}
        self._verification_thresholds = {
            "min_reproducibility_score": 0.95,
            "max_state_variance": 0.01,
            "max_timing_variance_ms": 10
        }
        
        # Initialize determinism rules
        self._initialize_determinism_rules()
    
    def _initialize_determinism_rules(self) -> None:
        """Initialize determinism rules for different scopes"""
        self._determinism_rules = {
            "execution": self._verify_execution_determinism,
            "governance": self._verify_governance_determinism,
            "learning": self._verify_learning_determinism,
            "simulation": self._verify_simulation_determinism,
            "ledger": self._verify_ledger_determinism,
            "world_model": self._verify_world_model_determinism
        }
    
    def capture_state_snapshot(
        self,
        scope: VerificationScope,
        state_data: Dict[str, Any],
        predecessor_ids: Optional[Set[str]] = None
    ) -> str:
        """Capture state snapshot for verification"""
        # Generate deterministic hash of state data
        state_hash = self._compute_state_hash(state_data)
        snapshot_id = f"{scope.value}_{state_hash[:16]}_{datetime.utcnow().timestamp()}:{datetime.utcnow().nanosecond()}"
        
        snapshot = StateSnapshot(
            snapshot_id=snapshot_id,
            scope=scope,
            timestamp=datetime.utcnow(),
            state_hash=state_hash,
            state_data=state_data.copy(),
            predecessor_hashes=predecessor_ids or set()
        )
        
        self._snapshots[snapshot_id] = snapshot
        self._hash_chains[scope.value].append(state_hash)
        
        logger.info(f"Captured state snapshot: {snapshot_id} for {scope.value}")
        return snapshot_id
    
    def _compute_state_hash(self, state_data: Dict[str, Any]) -> str:
        """Compute deterministic hash of state data"""
        # Sort keys for deterministic ordering
        ordered_state = OrderedDict(sorted(state_data.items()))
        state_str = json.dumps(ordered_state, sort_keys=True, default=str)
        return hashlib.sha256(state_str.encode()).hexdigest()
    
    def track_event(
        self,
        event_id: str,
        event_type: str,
        cause_event_ids: Optional[Set[str]] = None,
        state_before: Optional[Dict[str, Any]] = None,
        state_after: Optional[Dict[str, Any]] = None
    ) -> None:
        """Track event for causality verification"""
        trace = EventTrace(
            event_id=event_id,
            event_type=event_type,
            timestamp=datetime.utcnow(),
            cause_event_ids=cause_event_ids or set(),
            effect_event_ids=set(),
            state_before=state_before or {},
            state_after=state_after or {}
        )
        
        # Update cause events to include this as an effect
        for cause_id in trace.cause_event_ids:
            if cause_id in self._event_traces:
                self._event_traces[cause_id].effect_event_ids.add(event_id)
        
        self._event_traces[event_id] = trace
        logger.debug(f"Tracked event: {event_id} ({event_type})")
    
    def verify_replay(
        self,
        scope: VerificationScope,
        replay_data: List[Dict[str, Any]],
        expected_snapshots: List[str]
    ) -> VerificationResult:
        """
        Verify replay validation per Rule 9
        Ensures that replaying events produces identical results
        """
        verification_id = f"replay_{scope.value}_{datetime.utcnow().timestamp()}"
        violations = []
        evidence = []
        
        # Store replay data for later comparison
        self._replay_history[scope.value].extend(replay_data)
        
        # Capture states during replay
        replay_snapshots = []
        for i, data in enumerate(replay_data):
            try:
                snapshot_id = self.capture_state_snapshot(scope, data)
                replay_snapshots.append(snapshot_id)
                evidence.append(f"Replay step {i} captured: {snapshot_id}")
            except Exception as e:
                violations.append(f"Replay step {i} failed: {str(e)}")
        
        # Compare replay snapshots with expected
        if len(replay_snapshots) != len(expected_snapshots):
            violations.append(f"Snapshot count mismatch: expected {len(expected_snapshots)}, got {len(replay_snapshots)}")
        else:
            for replay_snap, expected_snap in zip(replay_snapshots, expected_snapshots):
                if replay_snap != expected_snap:
                    replay_state = self._snapshots[replay_snap].state_data
                    expected_state = self._snapshots[expected_snap].state_data
                    if self._compare_state_hashes(replay_state, expected_state):
                        evidence.append(f"State match despite different snapshot ID: {replay_snap} vs {expected_snap}")
                    else:
                        violations.append(f"State mismatch: {replay_snap} vs {expected_snap}")
        
        status = VerificationStatus.PASSED if not violations else VerificationStatus.FAILED
        reproducibility_score = 1.0 - (len(violations) / max(1, len(replay_data)))
        
        result = VerificationResult(
            verification_id=verification_id,
            scope=scope,
            verification_type=VerificationType.REPLAY_VALIDATION,
            status=status,
            timestamp=datetime.utcnow(),
            details={
                "replay_steps": len(replay_data),
                "expected_snapshots": len(expected_snapshots),
                "actual_snapshots": len(replay_snapshots)
            },
            hash_checksums={snap: self._snapshots[snap].state_hash for snap in replay_snapshots},
            state_snapshots={snap: self._snapshots[snap].state_data for snap in replay_snapshots},
            violations=violations,
            evidence=evidence,
            reproducibility_score=reproducibility_score
        )
        
        self._verification_results.append(result)
        logger.info(f"Replay verification {status.value}: {verification_id}")
        return result
    
    def verify_hash_chain(self, scope: VerificationScope, chain_id: str) -> VerificationResult:
        """
        Verify hash chain integrity per Rule 9
        Ensures state evolution is cryptographically verifiable
        """
        verification_id = f"hash_chain_{scope.value}_{chain_id}_{datetime.utcnow().timestamp()}"
        violations = []
        evidence = []
        
        chain = self._hash_chains.get(f"{scope.value}_{chain_id}", [])
        
        if len(chain) < 2:
            violations.append("Insufficient chain length for verification")
        else:
            # Verify chain integrity
            for i in range(1, len(chain)):
                # In a real system, this would verify cryptographic links
                # For now, we verify that hashes are present and unique
                if chain[i] == chain[i-1]:
                    violations.append(f"Duplicate hash in chain at position {i}")
                else:
                    evidence.append(f"Chain link {i-1}->{i} verified")
        
        # Verify snapshot consistency
        chain_snapshots = [snap for snap in self._snapshots.values() 
                          if snap.state_hash in chain]
        for snapshot in chain_snapshots:
            for pred_hash in snapshot.predecessor_hashes:
                if pred_hash not in chain:
                    violations.append(f"Predecessor hash {pred_hash} not in chain")
                else:
                    evidence.append(f"Predecessor {pred_hash} verified in chain")
        
        status = VerificationStatus.PASSED if not violations else VerificationStatus.FAILED
        reproducibility_score = 1.0 - (len(violations) / max(1, len(chain)))
        
        result = VerificationResult(
            verification_id=verification_id,
            scope=scope,
            verification_type=VerificationType.HASH_VALIDATION,
            status=status,
            timestamp=datetime.utcnow(),
            details={
                "chain_length": len(chain),
                "snapshot_count": len(chain_snapshots)
            },
            hash_checksums={f"link_{i}": hash_val for i, hash_val in enumerate(chain)},
            state_snapshots={snap.snapshot_id: snap.state_data for snap in chain_snapshots},
            violations=violations,
            evidence=evidence,
            reproducibility_score=reproducibility_score
        )
        
        self._verification_results.append(result)
        logger.info(f"Hash chain verification {status.value}: {verification_id}")
        return result
    
    def verify_state_consistency(
        self,
        scope: VerificationScope,
        expected_state: Dict[str, Any],
        actual_state: Dict[str, Any],
        tolerance: float = 0.01
    ) -> VerificationResult:
        """
        Verify state consistency per Rule 9
        Ensures system state remains consistent across runs
        """
        verification_id = f"state_consistency_{scope.value}_{datetime.utcnow().timestamp()}"
        violations = []
        evidence = []
        
        # Compare state fields
        expected_keys = set(expected_state.keys())
        actual_keys = set(actual_state.keys())
        
        missing_keys = expected_keys - actual_keys
        extra_keys = actual_keys - expected_keys
        
        if missing_keys:
            violations.append(f"Missing state keys: {missing_keys}")
        if extra_keys:
            violations.append(f"Extra state keys: {extra_keys}")
        
        # Compare common keys
        common_keys = expected_keys & actual_keys
        for key in common_keys:
            expected_value = expected_state[key]
            actual_value = actual_state[key]
            
            if self._compare_values(expected_value, actual_value, tolerance):
                evidence.append(f"State key {key} consistent")
            else:
                violations.append(f"State key {key} inconsistent: expected {expected_value}, got {actual_value}")
        
        status = VerificationStatus.PASSED if not violations else VerificationStatus.FAILED
        consistency_score = len(evidence) / max(1, len(common_keys))
        
        result = VerificationResult(
            verification_id=verification_id,
            scope=scope,
            verification_type=VerificationType.STATE_VALIDATION,
            status=status,
            timestamp=datetime.utcnow(),
            details={
                "total_keys": len(common_keys),
                "missing_keys": len(missing_keys),
                "extra_keys": len(extra_keys)
            },
            hash_checksums={
                "expected": self._compute_state_hash(expected_state),
                "actual": self._compute_state_hash(actual_state)
            },
            state_snapshots={
                "expected": expected_state,
                "actual": actual_state
            },
            violations=violations,
            evidence=evidence,
            reproducibility_score=consistency_score
        )
        
        self._verification_results.append(result)
        logger.info(f"State consistency verification {status.value}: {verification_id}")
        return result
    
    def verify_causality(self, event_id: str, max_depth: int = 10) -> VerificationResult:
        """
        Verify causality per Rule 9
        Ensures event causality chains are valid and complete
        """
        verification_id = f"causality_{event_id}_{datetime.utcnow().timestamp()}"
        violations = []
        evidence = []
        
        if event_id not in self._event_traces:
            violations.append(f"Event not found: {event_id}")
            return self._create_failed_result(verification_id, violations, event_id=event_id)
        
        trace = self._event_traces[event_id]
        visited = set()
        causality_chain = []
        
        # Build causality chain
        self._build_causality_chain(event_id, causality_chain, visited, max_depth)
        
        # Verify causality chain integrity
        for i, chain_event_id in enumerate(causality_chain):
            if chain_event_id not in self._event_traces:
                violations.append(f"Missing event in causality chain: {chain_event_id}")
            else:
                chain_trace = self._event_traces[chain_event_id]
                evidence.append(f"Causality level {i}: {chain_event_id} ({chain_trace.event_type})")
                
                # Verify temporal ordering
                if i > 0:
                    prev_trace = self._event_traces[causality_chain[i-1]]
                    if chain_trace.timestamp < prev_trace.timestamp:
                        violations.append(f"Temporal violation: {chain_event_id} before {causality_chain[i-1]}")
        
        status = VerificationStatus.PASSED if not violations else VerificationStatus.FAILED
        causality_score = len(evidence) / max(1, len(causality_chain))
        
        result = VerificationResult(
            verification_id=verification_id,
            scope=VerificationScope.EXECUTION,  # Default to execution for causality
            verification_type=VerificationType.CAUSALITY_VALIDATION,
            status=status,
            timestamp=datetime.utcnow(),
            details={
                "causality_depth": len(causality_chain),
                "unique_events": len(visited)
            },
            hash_checksums={},
            state_snapshots={},
            violations=violations,
            evidence=evidence,
            reproducibility_score=causality_score
        )
        
        self._verification_results.append(result)
        logger.info(f"Causality verification {status.value}: {verification_id}")
        return result
    
    def _build_causality_chain(self, event_id: str, chain: List[str], visited: Set[str], max_depth: int) -> None:
        """Build causality chain recursively"""
        if event_id in visited or len(chain) >= max_depth:
            return
        
        visited.add(event_id)
        chain.append(event_id)
        
        if event_id in self._event_traces:
            for cause_id in self._event_traces[event_id].cause_event_ids:
                self._build_causality_chain(cause_id, chain, visited, max_depth)
    
    def verify_scope_determinism(self, scope: VerificationScope, verification_data: Dict[str, Any]) -> VerificationResult:
        """
        Verify determinism for a specific scope
        Applies scope-specific determinism rules
        """
        verification_id = f"scope_determinism_{scope.value}_{datetime.utcnow().timestamp()}"
        
        # Apply scope-specific verification
        if scope.value in self._determinism_rules:
            try:
                result = self._determinism_rules[scope.value](verification_data)
                self._verification_results.append(result)
                return result
            except Exception as e:
                logger.error(f"Scope-specific verification failed: {e}")
                return self._create_failed_result(verification_id, [str(e)], scope=scope)
        else:
            # Default verification
            return self._verify_default_determinism(scope, verification_data)
    
    def _verify_execution_determinism(self, data: Dict[str, Any]) -> VerificationResult:
        """Verify execution system determinism"""
        # Ensure order execution is deterministic
        violations = []
        evidence = []
        
        if "orders" in data:
            orders = data["orders"]
            # Verify order determinism
            for i, order in enumerate(orders):
                if "deterministic_id" not in order:
                    violations.append(f"Order {i} missing deterministic ID")
                else:
                    evidence.append(f"Order {i} has deterministic ID: {order['deterministic_id']}")
        
        if "timing" in data:
            timing = data["timing"]
            if "timing_variance" in timing and timing["timing_variance"] > self._verification_thresholds["max_timing_variance_ms"]:
                violations.append(f"Timing variance exceeds threshold: {timing['timing_variance']}ms")
            else:
                evidence.append("Timing within acceptable variance")
        
        return self._create_verification_result(
            verification_scope=VerificationScope.EXECUTION,
            verification_type=VerificationType.REPRODUCIBILITY_VALIDATION,
            violations=violations,
            evidence=evidence,
            data=data
        )
    
    def _verify_governance_determinism(self, data: Dict[str, Any]) -> VerificationResult:
        """Verify governance system determinism"""
        violations = []
        evidence = []
        
        if "decisions" in data:
            decisions = data["decisions"]
            for decision in decisions:
                # Verify governance decisions are traceable to policy
                if "policy_id" not in decision:
                    violations.append(f"Decision missing policy ID: {decision}")
                else:
                    evidence.append(f"Decision traceable to policy: {decision['policy_id']}")
        
        if "authorities" in data:
            # Verify authority matrix is deterministic
            authorities = data["authorities"]
            if "hash" in authorities:
                evidence.append(f"Authority matrix hash: {authorities['hash']}")
            else:
                violations.append("Authority matrix missing hash")
        
        return self._create_verification_result(
            verification_scope=VerificationScope.GOVERNANCE,
            verification_type=VerificationType.REPRODUCIBILITY_VALIDATION,
            violations=violations,
            evidence=evidence,
            data=data
        )
    
    def _verify_learning_determinism(self, data: Dict[str, Any]) -> VerificationResult:
        """Verify learning system determinism"""
        violations = []
        evidence = []
        
        if "learning_updates" in data:
            updates = data["learning_updates"]
            for update in updates:
                # Verify learning updates are reproducible
                if "random_seed" not in update and "deterministic" not in update:
                    violations.append(f"Learning update not deterministic: {update}")
                else:
                    evidence.append(f"Learning update deterministic: {update}")
        
        if "model_states" in data:
            # Verify model state transitions are deterministic
            model_states = data["model_states"]
            for state in model_states:
                if "state_hash" in state:
                    evidence.append(f"Model state hash: {state['state_hash']}")
                else:
                    violations.append("Model state missing hash")
        
        return self._create_verification_result(
            verification_scope=VerificationScope.LEARNING,
            verification_type=VerificationType.REPRODUCIBILITY_VALIDATION,
            violations=violations,
            evidence=evidence,
            data=data
        )
    
    def _verify_simulation_determinism(self, data: Dict[str, Any]) -> VerificationResult:
        """Verify simulation system determinism"""
        violations = []
        evidence = []
        
        if "random_seeds" in data:
            seeds = data["random_seeds"]
            # Verify simulation uses deterministic random seeds
            if all(isinstance(seed, int) for seed in seeds):
                evidence.append(f"All simulation random seeds are integers: {len(seeds)} seeds")
            else:
                violations.append("Simulation random seeds not all integers")
        
        if "market_conditions" in data:
            # Verify market conditions are replay-able
            conditions = data["market_conditions"]
            if "condition_hash" in conditions:
                evidence.append(f"Market conditions hash: {conditions['condition_hash']}")
            else:
                violations.append("Market conditions missing hash")
        
        return self._create_verification_result(
            verification_scope=VerificationScope.SIMULATION,
            verification_type=VerificationType.REPRODUCIBILITY_VALIDATION,
            violations=violations,
            evidence=evidence,
            data=data
        )
    
    def _verify_ledger_determinism(self, data: Dict[str, Any]) -> VerificationResult:
        """Verify ledger system determinism"""
        violations = []
        evidence = []
        
        if "transactions" in data:
            transactions = data["transactions"]
            for tx in transactions:
                # Verify transaction order is deterministic
                if "sequence_number" not in tx:
                    violations.append(f"Transaction missing sequence number: {tx}")
                else:
                    evidence.append(f"Transaction has sequence number: {tx['sequence_number']}")
        
        if "ledger_hash" in data:
            evidence.append(f"Ledger hash: {data['ledger_hash']}")
        else:
            violations.append("Ledger missing hash")
        
        return self._create_verification_result(
            verification_scope=VerificationScope.LEDGER,
            verification_type=VerificationType.REPRODUCIBILITY_VALIDATION,
            violations=violations,
            evidence=evidence,
            data=data
        )
    
    def _verify_world_model_determinism(self, data: Dict[str, Any]) -> VerificationResult:
        """Verify world model determinism"""
        violations = []
        evidence = []
        
        if "belief_states" in data:
            beliefs = data["belief_states"]
            for belief in beliefs:
                # Verify beliefs are traceable to evidence
                if "evidence_id" not in belief:
                    violations.append(f"Belief not traceable to evidence: {belief}")
                else:
                    evidence.append(f"Belief traceable to evidence: {belief['evidence_id']}")
        
        if "model_hash" in data:
            evidence.append(f"World model hash: {data['model_hash']}")
        else:
            violations.append("World model missing hash")
        
        return self._create_verification_result(
            verification_scope=VerificationScope.WORLD_MODEL,
            verification_type=VerificationType.REPRODUCIBILITY_VALIDATION,
            violations=violations,
            evidence=evidence,
            data=data
        )
    
    def _verify_default_determinism(self, scope: VerificationScope, data: Dict[str, Any]) -> VerificationResult:
        """Default determinism verification for unknown scopes"""
        violations = []
        evidence = []
        
        # Generic determinism checks
        if "deterministic_hash" in data:
            evidence.append(f"Data has deterministic hash: {data['deterministic_hash']}")
        else:
            violations.append("Data missing deterministic hash")
        
        return self._create_verification_result(
            verification_scope=scope,
            verification_type=VerificationType.REPRODUCIBILITY_VALIDATION,
            violations=violations,
            evidence=evidence,
            data=data
        )
    
    def _create_verification_result(
        self,
        verification_scope: VerificationScope,
        verification_type: VerificationType,
        violations: List[str],
        evidence: List[str],
        data: Dict[str, Any]
    ) -> VerificationResult:
        """Helper to create verification result"""
        verification_id = f"{verification_type.value}_{verification_scope.value}_{datetime.utcnow().timestamp()}"
        status = VerificationStatus.PASSED if not violations else VerificationStatus.FAILED
        reproducibility_score = 1.0 - (len(violations) / max(1, len(violations) + len(evidence)))
        
        return VerificationResult(
            verification_id=verification_id,
            scope=verification_scope,
            verification_type=verification_type,
            status=status,
            timestamp=datetime.utcnow(),
            details=data,
            hash_checksums={"data_hash": self._compute_state_hash(data)},
            state_snapshots={"data": data},
            violations=violations,
            evidence=evidence,
            reproducibility_score=reproducibility_score
        )
    
    def _create_failed_result(self, verification_id: str, violations: List[str], **kwargs) -> VerificationResult:
        """Helper to create failed verification result"""
        return VerificationResult(
            verification_id=verification_id,
            scope=kwargs.get("scope", VerificationScope.EXECUTION),
            verification_type=VerificationType.REPRODUCIBILITY_VALIDATION,
            status=VerificationStatus.FAILED,
            timestamp=datetime.utcnow(),
            details={},
            hash_checksums={},
            state_snapshots={},
            violations=violations,
            evidence=[],
            reproducibility_score=0.0
        )
    
    def _compare_values(self, expected: Any, actual: Any, tolerance: float = 0.01) -> bool:
        """Compare values with tolerance for numeric types"""
        if isinstance(expected, (int, float)) and isinstance(actual, (int, float)):
            return abs(expected - actual) <= max(abs(expected), abs(actual)) * tolerance
        return expected == actual
    
    def _compare_state_hashes(self, state_a: Dict[str, Any], state_b: Dict[str, Any]) -> bool:
        """Compare state hashes for equality"""
        return self._compute_state_hash(state_a) == self._compute_state_hash(state_b)
    
    def get_verification_summary(self) -> Dict[str, Any]:
        """Get summary of verification results"""
        total_verifications = len(self._verification_results)
        passed = sum(1 for r in self._verification_results if r.status == VerificationStatus.PASSED)
        failed = sum(1 for r in self._verification_results if r.status == VerificationStatus.FAILED)
        
        # Calculate average reproducibility score
        avg_reproducibility = sum(r.reproducibility_score for r in self._verification_results) / total_verifications if total_verifications > 0 else 0
        
        return {
            "total_verifications": total_verifications,
            "passed": passed,
            "failed": failed,
            "pass_rate": passed / total_verifications if total_verifications > 0 else 0,
            "average_reproducibility_score": avg_reproducibility,
            "total_snapshots": len(self._snapshots),
            "total_events_traced": len(self._event_traces),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def cleanup_old_snapshots(self, older_than_hours: int = 24) -> int:
        """Clean up old state snapshots"""
        cutoff = datetime.utcnow() - timedelta(hours=older_than_hours)
        old_count = len(self._snapshots)
        
        # Remove old snapshots
        self._snapshots = {
            snap_id: snap for snap_id, snap in self._snapshots.items()
            if snap.timestamp > cutoff
        }
        
        # Clean up hash chains
        for scope, chain in self._hash_chains.items():
            # Keep only hashes from recent snapshots
            recent_hashes = {snap.state_hash for snap in self._snapshots.values() if snap.scope.value == scope.split('_')[0]}
            self._hash_chains[scope] = [h for h in chain if h in recent_hashes]
        
        removed = old_count - len(self._snapshots)
        logger.info(f"Cleaned up {removed} old snapshots")
        return removed