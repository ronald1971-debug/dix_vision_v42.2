# DIX VISION v42.2 — Canonical System Manifest

> **Last updated:** EPIC-001 COMPLETE + Phase-6 REGEN
> **Authority:** This file is the single source of truth for system architecture. Any contradiction with other documentation is resolved in favor of this file.

---

## ROOT ARCHITECTURE

```
dixvision-1/
├── core/                      (PYTHON — Contracts + Coherence)
│   ├── contracts/             Typed contracts (events, engine, governance)
│   ├── coherence/             BeliefState, PressureVector, SystemIntent
│   ├── belief_engine/         Believes engine (belief updates, validation, replay)
│   ├── cognitive_router/      Task routing + orchestration
│   ├── constraint_engine/     INV-60/61 constraint compilation
│   ├── event_cognition/       LAVA event patterns
│   ├── ontology/              Truth maintenance + cognitive versioning
│   ├── registry.py            Central registry facade
│   └── runtime/               Runtime coordination
├── intelligence_engine/         (PYTHON — INDIRA cognition)
│   ├── agents/                AGT-01..05: Scalper/Swing/Macro/LP/Adversarial
│   ├── cognitive/             Cognitive development pipeline
│   ├── cross_asset/           Cross-asset coupling (Phase 10.7)
│   ├── meta/                  Meta-learning + intent production
│   ├── meta_controller/       Strategy orchestration + shadow policy
│   ├── opponent_model/        Opponent/Opposite modeling
│   ├── plugins/               Plugin ecosystem
│   ├── strategy_runtime/      Strategy lifecycle FSM
│   └── system/               System intelligence domain
├── execution_engine/          (PYTHON — Execution + adapters)
│   ├── adapters/              Real adapters (Binance, Coinbase, Kraken, Raydium, Uniswap)
│   ├── algos/                 Algorithmic order types
│   ├── chaos/                 Chaos engineering hooks
│   ├── confirmations/         Fill reconciliation
│   ├── hazard/                Hazard detection
│   ├── lifecycle/             Order state machine
│   ├── live_trading/          LIVE mode safety
│   └── protections/           Runtime monitoring
├── governance_engine/         (PYTHON — Policy + Control Plane)
│   ├── control_plane/         GOV-CP-01..07 implementation
│   ├── dyon_constraints.py    DYON autonomy boundaries
│   ├── engine.py              Governance core
│   ├── gates/                 Promotion gates
│   ├── hardening/             Hardening-S1 (B33-B36)
│   ├── policies/              Risk + mode policies
│   ├── plugin_lifecycle/      Plugin activation control
│   └── services/              Governance services
├── system_engine/             (PYTHON — DYON system cognition)
│   ├── scvs/                  Source/consumption registry
│   ├── dyon/                  Topology, hazards, drift
│   ├── authority_matrix.yaml  Authority matrix
│   └── time_source.py         Time authority
├── learning_engine/           (PYTHON — Offline learning)
│   ├── closed_loop/           Closed learning loop
│   ├── calibration/           Belief + pressure calibration
│   ├── regret/                Counterfactual memory
│   └── weight_adjuster/       Parameter updates
├── evolution_engine/          (PYTHON — Offline evolution)
│   ├── genetic/               Strategy genetics
│   ├── mutation/              Patch generation
│   ├── patch_pipeline/        Governed mutation pipeline
│   ├── sandboxes/             Evolution sandboxes
│   └── topology_scanner.py    Repository intelligence
├── sensory/                   (PYTHON — Perception layer)
│   ├── web_autolearn/         Auto-learning perimeter
│   ├── onchain/               On-chain data contracts
│   ├── regulatory/            Regulatory data feeds
│   ├── neuromorphic/          NEUR-01..03 sensory
│   └── news/                  News fusion + projection
├── cockpit/                   (PYTHON — Operator IDE)
├── dashboard2026/             (TypeScript — Operator dashboard)
├── dash_meme/                 (TypeScript — Memecoin dashboard)
├── contracts/                 Protobuf contracts
│   ├── events.proto           Canonical 4-event bus
│   ├── belief_state.proto     BeliefState contract
│   ├── execution.proto        Execution contracts
│   ├── governance.proto         Governance contracts
│   └── trader_intelligence.proto
├── registry/
│   ├── engines.yaml           Engine declarations
│   ├── plugins.yaml           Plugin declarations
│   ├── ownership_registry.yaml Owner matrix
│   └── authority_matrix.yaml   Authority matrix
└── tools/
    ├── authority_lint.py      Architecture enforcement (B-DIX-03/04/05)
    ├── total_validation.py    12-phase system audit
    ├── constraint_lint.py     INV-61 enforcement
    ├── authority_matrix_lint.py INV-60 enforcement
    └── scvs_lint.py           INV-57 enforcement
```

---

## ENGINE OWNERSHIP MATRIX

| Engine | Module | Owns | May NOT |
|--------|--------|------|---------|
| INDIRA | `intelligence_engine` | market_intelligence, trader_intelligence, strategy_intelligence, portfolio_intelligence, regime_intelligence, signal_intelligence, execution_feedback_intelligence | strategy_engine (direct construction), DYON domains |
| DYON | `system_engine` | repository_intelligence, architecture_intelligence, runtime_intelligence, infrastructure_intelligence | INDIRA domains, strategy_generation |
| Governance | `governance_engine` | policy, approval, audit, ledger_write | execution_engine (imports), strategy_generation |
| Execution | `execution_engine` | routing, broker_access, exchange_access, order_lifecycle | strategy_engine (creation) |
| Learning | `learning_engine` | experience_transformation, calibration, distillation | runtime engines (imports) |
| Evolution | `evolution_engine` | parameter_proposal, patch_evolution, strategy_genome | execution_engine.hot_path |
| Belief Engine | `core.belief_engine` | belief_updates, belief_validation, belief_consistency, belief_replay, belief_snapshots, belief_versioning | strategy_engine, execution_engine |

---

## ARCHITECTURAL INVARIANTS (CONSTITUTION)

| ID | Invariant | Enforcement |
|----|-----------|-------------|
| INV-DIX-01 | Cognitive system first | B-COGNITIVE-ONLY, policy |
| INV-DIX-02 | BeliefState is single source of truth | core.belief_engine, lint B30 |
| INV-DIX-03 | INDIRA owns market/trader/strategy cognition | B-DIX-03 lint rule |
| INV-DIX-04 | DYON owns system cognition only | B-DIX-04 lint rule |
| INV-DIX-05 | Strategy cognition belongs exclusively to INDIRA | B-DIX-05 lint rule + Policy Compiler |
| INV-DIX-06 | Execution owns interaction, not decisions | T1, B1, B20 |
| INV-DIX-07 | Learning owns experience transformation | L1 |
| INV-DIX-08 | Governance owns accountability | CONF-01, CONF-08, CONF-09 |
| INV-DIX-09 | System owns operational awareness | CONF-02, CONF-03 |
| INV-DIX-010 | Operator is highest authority | GOV-CP-07 |
| INV-DIX-011 | Cognitive development priority | Development Mode |
| INV-DIX-012 | Capital separation | Triad Lock (B20/B21/B22) |
| INV-DIX-013 | Domain separation mandatory | All lint rules |
| INV-DIX-014 | Continuous evolution | DYON mutation pipeline |
| INV-DIX-015 | Mission | All engines |
| INV-DIX-016 | Development Priority | All engines |

---

## BELIEF STATE CONTRACT

All reality domains publish through BeliefState:

- `MarketBeliefs` — price, volatility, regime, consensus
- `TraderBeliefs` — trader profiles, preferences, behavior
- `StrategyBeliefs` — strategy performance, hypotheses, rankings  
- `PortfolioBeliefs` — allocation, exposure, correlation
- `ExecutionBeliefs` — fill data, slippage, latency
- `SystemBeliefs` — health, latency, resource utilization

No hidden realities. Every engine publishes via `core.belief_engine.publish_belief()`.

---

## DYON CONSTRAINTS

DYON may autonomously:
- `refactor`
- `optimize`
- `test`
- `improve_infrastructure`
- `scan_architecture`
- `detect_drift`
- `emit_hazard`
- `propose_patch`

DYON requires operator approval for:
- `change_invariants`
- `change_authority_boundaries`
- `modify_governance`
- `strategy_generation`
- `direct_execution`

---

## MUTATION REVIEW FLOW

```
DYON → PatchProposal → Governance → Replay/Validation → Operator Approval → Merge
```

Every DYON mutation becomes a proposal, never a direct change.

---

## ENFORCEMENT LAYERS

1. **CI:** `tools/authority_lint.py` runs on every PR
2. **Governance:** `governance_engine/policy_compiler.py` validates at runtime
3. **Runtime:** `core.belief_engine.validation` checks belief updates
4. **Audit:** `tools/total_validation.py` 12-phase validation

---

## PROVENANCE

- Architectural Constitution: `docs/architecture/DIXVISION_ARCHITECTURAL_INVARIANTS.md`
- Ownership Registry: `registry/ownership_registry.yaml`
- Invariants List: `docs/invariants_dixvision_v42.2.md` (INV-DIX-01 through INV-DIX-16)
- Policy Rules: `governance_engine/policy_compiler.py`
- Constraint Engine: `core/constraint_engine/compiler.py` (INV-60/61)
- Lint Rules: `tools/authority_lint.py` (B-DIX-03/04/05, B1-B36)
- Runtime Graph: `docs/system_audit/runtime_graph.json`
- Total Validation: `tools/total_validation.py`

---

## BUILD STATUS SUMMARY

| Phase | Status |
|-------|--------|
| Phase 0 — Bootstrap Core | ✅ Complete |
| Phase 1 — Governance Core | ✅ Complete |
| Phase 2 — Execution Core | ✅ Complete |
| Phase 3 — Intelligence Core | ✅ Complete |
| Phase 4 — Learning Core | ✅ Complete |
| Phase 5 — Evolution Core | ✅ Complete |
| Phase 6 — Hardening + Audit | ✅ Complete |
| Phase 7+ | ⏳ Queued |

**Architectural Constitution (EPIC-001):** ✅ Implemented
**Total Validation:** ✅ 12-phase audit passes (1,245 files, 100% coverage)