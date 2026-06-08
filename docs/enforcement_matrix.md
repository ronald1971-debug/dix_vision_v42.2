# DIX v42.2 — Enforcement Matrix

Maps each constraint (INV-*/B-*/FAIL-*) to its enforcement mechanism:
test, YAML guard, code assertion, or review gate.

---

## Legend

| Level | Meaning |
|-------|---------|
| **AUTO** | Enforced automatically by CI test |
| **YAML** | Enforced by schema/value in a registry YAML |
| **CODE** | Enforced by runtime assertion or type system |
| **REVIEW** | Enforced by PR review gate (no automated check) |
| **DRIFT-KILLER** | Enforced by a dedicated `tests/drift_killers/` test |

---

## Invariant Enforcement

| ID | Constraint | Level | Enforcement File |
|----|-----------|-------|-----------------|
| INV-08 | Four canonical event types only | CODE | `core/event_types.py` — EventKind enum with exactly 4 members |
| INV-15 | Byte-identical replay | DRIFT-KILLER | `tests/drift_killers/test_replay_gate.py` |
| INV-15 | No wall-clock reads in pure modules | DRIFT-KILLER | `tests/drift_killers/test_no_hidden_channels.py` |
| INV-48 | Fallback lane budget ≤ 1ms | YAML + CODE | `registry/meta_controller.yaml` → `execution/event_emitter.py` |
| INV-49 | Regime hysteresis thresholds | YAML | `registry/regime_hysteresis.yaml` |
| INV-52 | Shadow MetaController non-acting | CODE | `governance_engine/services/patch_pipeline.py` stage guard |
| INV-53 | Calibration loop offline-only | YAML + CODE | `registry/calibration.yaml` + `triple_window_dry_run.py` |
| INV-55 | Calibration changes governance-gated | CODE + REVIEW | `patch_pipeline.py` PatchStage gate |
| INV-71 | No SignalEvent/ExecutionEvent construction in transport | CODE + DRIFT-KILLER | `tests/drift_killers/test_no_hidden_channels.py` |
| INV-DIX-01 | DIXVISION is a cognitive intelligence system, not a trading bot | REVIEW | `docs/invariants_dixvision_v42.2.md` |
| INV-DIX-02 | BeliefState is single source of truth with all reality domains | CODE + DRIFT-KILLER | `core/contracts/belief_state.py`, `core/coherence/belief_state.py` |
| INV-DIX-03 | INDIRA owns cognition domains: market, trader, strategy, portfolio, position, allocation, execution feedback | CODE + REVIEW | `intelligence_engine/charter/indira.py` |
| INV-DIX-04 | DYON owns system cognition; DYON does not own market/strategy cognition | CODE + REVIEW | `evolution_engine/charter/dyon.py` |
| INV-DIX-05 | Strategy cognition belongs exclusively to INDIRA | REVIEW | `intelligence_engine/strategy_composer/composer.py` |
| INV-DIX-06 | Execution engine owns market interaction; does not create decisions | CODE | `execution_engine/` |
| INV-DIX-07 | Learning engine owns experience transformation | CODE | `learning_engine/` |
| INV-DIX-08 | Governance engine owns accountability; does not own cognition | CODE | `governance_engine/` |
| INV-DIX-09 | System engine owns operational awareness | CODE | `system_engine/` |
| INV-DIX-10 | Operator is highest authority | CODE + YAML | `core/contracts/operator_authority.py`, `registry/operator.yaml` |
| INV-DIX-11 | Cognitive development is allowed and primary | REVIEW | `docs/invariants_dixvision_v42.2.md` |
| INV-DIX-12 | Capital deployment is separate from cognitive development | CODE + YAML | `core/contracts/development_mode.py` |
| INV-DIX-13 | Architectural domain separation mandatory | DRIFT-KILLER | `tests/drift_killers/test_domain_isolation.py` |
| INV-DIX-14 | Continuous evolution through observation, reasoning, learning | REVIEW | `docs/invariants_dixvision_v42.2.md` |
| INV-DIX-15 | Mission: continuously improving cognitive system | REVIEW | `docs/invariants_dixvision_v42.2.md` |
| INV-DIX-16 | Development priority: cognitive maturation over capital deployment | REVIEW | `docs/invariants_dixvision_v42.2.md` |

---

## Build Directive Enforcement

| ID | Directive | Level | Enforcement File |
|----|-----------|-------|-----------------|
| B1 | No engine cross-imports in transport | DRIFT-KILLER | `tests/drift_killers/test_no_hidden_channels.py` |
| B15 | Agent context key allowlist | YAML | `registry/agent_context_keys.yaml` |
| B18 | Reward component allowlist | YAML | `registry/reward_components.yaml` |
| B27 | No SignalEvent construction in transport | CODE | `execution/async_bus.py`, `lifecycle_emitter.py` |
| B28 | No ExecutionEvent construction in transport | CODE | `execution/async_bus.py`, `lifecycle_emitter.py` |

---

## Failure Mode Enforcement

| ID | Failure Mode | Level | Enforcement File |
|----|-------------|-------|-----------------|
| FAIL-16 | Boot integrity failure halts system | CODE | `integrity/verify_boot.py` — raises RuntimeError |

---

## Snapshot / Dataclass Enforcement

| Constraint | Level | Enforcement File |
|-----------|-------|-----------------|
| All value objects frozen=True | DRIFT-KILLER | `tests/drift_killers/test_snapshot_boundary.py` |
| All value objects slots=True | DRIFT-KILLER | `tests/drift_killers/test_snapshot_boundary.py` |

---

## Registry Structural Enforcement

| File | Required Keys | Level | Enforcement File |
|------|--------------|-------|-----------------|
| `strategies/definitions.yaml` | `strategies` | AUTO | `tests/drift_killers/test_registry_lock.py` |
| `strategies/lifecycle.yaml` | `states`, `valid_transitions` | AUTO | `tests/drift_killers/test_registry_lock.py` |
| `agent_context_keys.yaml` | `allowed_keys` | AUTO | `tests/drift_killers/test_registry_lock.py` |
| `regime_hysteresis.yaml` | `persistence_ticks`, `confidence_delta` | AUTO | `tests/drift_killers/test_registry_lock.py` |
| `reward_components.yaml` | `allowed_components` | AUTO | `tests/drift_killers/test_registry_lock.py` |
| `calibration.yaml` | `window_ns`, `thresholds` | AUTO | `tests/drift_killers/test_registry_lock.py` |
| `meta_controller.yaml` | `shadow_policy`, `fallback_lane` | AUTO | `tests/drift_killers/test_registry_lock.py` |

---

## Behavior Regression Enforcement

| Test | Covers | Level |
|------|--------|-------|
| `test_behavior_diff.py` | Golden numeric outputs for impact model, TWAP, adversarial executor | AUTO |
| `test_replay_gate.py` | Determinism of all pure-computation modules | AUTO |

---

## Gaps (REVIEW-only, no automated enforcement)

The following constraints rely solely on PR review and have no automated test:

- **B27/B28 completeness**: Only checked for known transport modules; new transport modules added without tests would bypass the check.
- **INV-55 governance gate**: The patch pipeline enforces stage gating, but the governance body approval step is a human process.
- **INV-52 shadow non-acting**: Checked in `patch_pipeline.py` but no isolated unit test for the shadow MetaController path.

*Address these gaps by adding targeted tests when the subsystems stabilise.*

---

*Last updated: 2026-05-28*
