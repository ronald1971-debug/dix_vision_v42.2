"""GOV-CP — Governance Control Plane (Phase 1).

The Control Plane is the canonical seven-module pipeline that turns
inbound events and operator requests into authoritative system
changes. Per ``manifest.md`` §0.5 / Build Compiler Spec §0:

* GOV-CP-01 ``policy_engine``                 — constraint store + policy decisions
* GOV-CP-02 ``risk_evaluator``                — exposure + limit checks
* GOV-CP-03 ``state_transition_manager``      — Mode FSM (sole writer)
* GOV-CP-04 ``event_classifier``              — event → CP route
* GOV-CP-05 ``ledger_authority_writer``       — sole authority-ledger writer
* GOV-CP-06 ``compliance_validator``          — domain / jurisdiction
* GOV-CP-07 ``operator_interface_bridge``     — dashboard adapter

The pipeline is deterministic: same inputs → same ledger row → same
decision (INV-15, TEST-01).
"""

from .compliance_validator import (
    ComplianceValidator,
)
from .decision_signer import (
    DecisionSigner,
    make_decision_signer,
)
from .drift_oracle import (
    DEFAULT_AXIS_WEIGHTS,
    DEFAULT_COMPOSITE_THRESHOLD,
    DEFAULT_MIN_SAMPLES,
    DEFAULT_WINDOW_SIZE,
    LEDGER_KIND_DRIFT_OBSERVATION,
    DriftOracle,
    DriftSample,
)
from .event_classifier import (
    EventClassifier,
    PipelineRoute,
)
from .exposure_store import (
    ExposureStore,
    day_iso_from_ns,
)
from .ledger_authority_writer import (
    LedgerAuthorityWriter,
)
from .operator_interface_bridge import (
    OperatorInterfaceBridge,
)
from .policy_engine import (
    POLICY_TABLE_HASH_KEY,
    POLICY_TABLE_INSTALLED_KIND,
    PolicyEngine,
    install_policy_table,
    verify_policy_table_hash,
)
from .policy_hash_anchor import (
    PolicyHashAnchor,
)
from .promotion_gates import (
    DEFAULT_PROMOTION_GATES_PATH,
    LEDGER_KIND_PROMOTION_GATES_BOUND,
    PromotionGates,
    PromotionGatesHashMismatchError,
    compute_file_hash,
)
from .risk_evaluator import RiskEvaluator
from .state_transition_manager import (
    StateTransitionManager,
)

__all__ = [
    "ComplianceValidator",
    "DecisionSigner",
    "make_decision_signer",
    "DEFAULT_AXIS_WEIGHTS",
    "DEFAULT_COMPOSITE_THRESHOLD",
    "DEFAULT_MIN_SAMPLES",
    "DEFAULT_PROMOTION_GATES_PATH",
    "DEFAULT_WINDOW_SIZE",
    "DriftOracle",
    "DriftSample",
    "EventClassifier",
    "ExposureStore",
    "day_iso_from_ns",
    "LEDGER_KIND_DRIFT_OBSERVATION",
    "LEDGER_KIND_PROMOTION_GATES_BOUND",
    "LedgerAuthorityWriter",
    "OperatorInterfaceBridge",
    "PipelineRoute",
    "PolicyHashAnchor",
    "POLICY_TABLE_HASH_KEY",
    "POLICY_TABLE_INSTALLED_KIND",
    "PolicyEngine",
    "PromotionGates",
    "PromotionGatesHashMismatchError",
    "RiskEvaluator",
    "StateTransitionManager",
    "compute_file_hash",
    "install_policy_table",
    "verify_policy_table_hash",
]
