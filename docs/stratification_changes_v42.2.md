# Stratification Changes — v42.2 Invariant Registry

Layer: `core/contracts/invariants.py`  
Layer: `governance_engine/hardening/invariants_state.py`  
Layer: `core/contracts/belief_state.py`  
Layer: `core/coherence/belief_state.py`  
Layer: `intelligence_engine/charter/indira.py`  
Docs: `docs/invariants_dixvision_v42.2.md`  
Docs: `docs/enforcement_matrix.md`  
Docs: `docs/manifest_v42.2_cognitive_expansion.md`

Date: 2026-06-06

## Structural change, not content change

This change introduces the canonical architectural invariant registry for DIXVISION v42.2 plus the expanded reality domains required by INDIRA's portfolio cognition.

New files:

- `core/contracts/invariants.py` — single authoritative enum + doc lookup for every invariant ID
- `governance_engine/hardening/invariants_state.py` — runtime descriptor + helper API with enforcement taxonomy

Updated files:

- `core/contracts/belief_state.py` — added `strategy_reality`, `portfolio_reality`, `execution_reality`, `uncertainty_metrics`
- `core/coherence/belief_state.py` — version bumped to `v42.2-T1b`; docstring updated with new reality domains
- `intelligence_engine/charter/indira.py` — expanded portfolio/allocation/position/execution-feedback ownership; references INV-DIX-02
- `docs/enforcement_matrix.md` — enforcement entries for INV-DIX-01 through INV-DIX-16
- `docs/manifest_v42.2_cognitive_expansion.md` — references invariant file and INV-DIX-16 priority order

Drift-killer test:

- `tests/drift_killers/test_invariants_coherence.py` — enforces enum-to-doc completeness; run in CI

NOT changed (different responsibility surface):

- `core/contracts/operator_authority.py` (switch default dataclass)
- `registry/operator.yaml` (operator defaults)

Operator authority is distinct from architectural invariants. These files remain single-owner implementation details for Operator switch state and trading-mode parameters; they do not conflict with the registry layer.
