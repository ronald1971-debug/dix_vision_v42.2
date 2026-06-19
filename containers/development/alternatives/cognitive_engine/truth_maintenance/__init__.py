"""Truth Maintenance System — belief revision + evidence reweighing.

As new evidence arrives, old beliefs must be re-evaluated.

(Item 28 — cognitive operating system roadmap)
"""

from cognitive_engine.truth_maintenance.truth_maintenance import (
    BeliefField,
    EvidenceReweigher,
    TruthMaintenanceEngine,
    get_truth_maintenance,
)

__all__ = [
    "BeliefField",
    "EvidenceReweigher",
    "TruthMaintenanceEngine",
    "get_truth_maintenance",
]
