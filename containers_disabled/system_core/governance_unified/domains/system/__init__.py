"""
governance_unified.domains.system
System integrity and structural consistency governance guards.

This module contains guards to ensure system structural integrity, contract
compliance, and runtime consistency.
"""

from __future__ import annotations

# System domain guards
from .contract_integrity import ContractIntegrityGuard, get_contract_integrity_guard
from .convergence_monitor import ConvergenceMonitor, get_convergence_monitor
from .dependency_validator import DependencyValidator, get_dependency_validator
from .replay_integrity import ReplayIntegrityGuard, get_replay_integrity_guard
from .runtime_consistency import RuntimeConsistencyMonitor, get_runtime_consistency_monitor
from .topology_guard import TopologyGuard, get_topology_guard

__all__ = [
    "ContractIntegrityGuard",
    "get_contract_integrity_guard",
    "TopologyGuard",
    "get_topology_guard",
    "RuntimeConsistencyMonitor",
    "get_runtime_consistency_monitor",
    "DependencyValidator",
    "get_dependency_validator",
    "ReplayIntegrityGuard",
    "get_replay_integrity_guard",
    "ConvergenceMonitor",
    "get_convergence_monitor",
]
