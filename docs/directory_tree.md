# DIX v42.2 — Canonical Directory Tree (System Reference, v3.3)

This file is the architectural source of truth for the DIX v42.2 layout. It
**describes the steady-state shape** of the repository — every directory
and module that is canonical under the v42.2 specification, regardless of
whether it is implemented yet.

This is **v3.3 of the canonical tree**, integrating:

1. `manifest.md §A` (engine-led layout) — the binding base
2. The 22 addon directives (Coherence Layer, Mode Engine, Drift Oracle,
   Causal Graph, Meta-Adaptation Bridge, Dashboard OS, hard 3-domain
   isolation, drift killers, plugin budgets, dual-speed system, …)
3. The 10 institutional-grade additions (A–J): Portfolio Brain,
   Strategy Orchestrator, Execution Lifecycle FSM, Market Data
   Normalizer, Simulation Engine, Real-Time Risk Engine, Performance &
   Alpha-Decay Tracking, Data Versioning, Strategy Registry split,
   Operator Audit
4. The 20 extras directives (operator decisions A1 / B1 / C2 / D1 / E1 / F1):
   - Tier 1 follow-ons after Phase 6: Belief State, Pressure Vector,
     Meta-Controller, Confidence Engine, Reward Shaping
   - `agents/` namespace alongside `plugins/` (per C2)
   - **Phase 10: Intelligence Depth Layer** (per E1, after Phase 9):
     Simulation vPro, Trader Intelligence System (full F1), Macro Regime
     Engine, Cross-Asset Coupling, Strategic Execution + Market Impact,
     trader-intelligence proto contract
5. The v3.1 fold-in (operator decisions G1 / G2 / G3 / G4):
   - **System Intent Engine** (read-only projection in `core/coherence/`,
     operator-written via GOV-CP-07) — Phase 6.T1d
   - **Opponent Model** (`intelligence_engine/opponent_model/`,
     extends Trader Intelligence) — Phase 10.10
   - **Reflexive Simulation Layer** (`simulation/reflexive_layer/`,
     market-reacts-to-you) — Phase 10.11
   - **Strategy Genetics** (`evolution_engine/genetic/`,
     mutation/crossover/inheritance) — Phase 10.12
   - **Regret / Counterfactual Memory** (`state/memory_tensor/regret/`,
     missed-opportunity tracking) — Phase 10.13
   - **Internal Debate Round** (`meta_controller/evaluation/debate_round.py`,
     deterministic agent stance scoring — NOT meta-RL) — Phase 10.14
   - **Time Hierarchy + Dynamic Identity** doctrine (manifest §X,
     no new modules — emergent property of existing FSMs)
6. The v3.2 stress-stabilization (operator decisions I1 / I2 / I3 /
   I4 / I5 / I6 / I7):
   - **Meta-Controller `O(1)` fallback lane** (`FALLBACK_POLICY` +
     `_fallback_lane()` in `meta_controller/policy/execution_policy.py`,
     INV-48) — Phase 6.T1b
   - **Regime hysteresis activation** (extends `regime_detector.py` +
     new `registry/regime_hysteresis.yaml`, INV-49) — Phase 6.T1e
   - **Cross-signal entropy in Pressure Vector `uncertainty`**
     (`performance_pressure.py` derivation, INV-50, +
     `registry/pressure.yaml`) — Phase 6.T1a
   - **Typed `agent_context` schema** (`SignalEvent.agent_context:
     Mapping[str, str]` + `registry/agent_context_keys.yaml` allowlist,
     B15) — Phase 10.8
   - **Richer `SimulationOutcome` payload** (`failure_modes`,
     `regime_performance_map`, `adversarial_breakdowns` —
     `simulation/strategy_arena/simulation_outcome.py`) — Phase 10.1
   - **Archetype lifecycle** (`{state, decay_rate, performance_score}`
     in `registry/trader_archetypes.yaml` +
     `intelligence_engine/strategy_runtime/archetype_lifecycle.py`,
     INV-51) — Phase 10.2–10.4
   - **PolicyEngine constant-time decision table** (`I7` reframed —
     internal precompile in `governance_engine/control_plane/
     policy_engine.py`, no parallel approval path) — Phase 7
7. The v3.3 self-correction (operator decisions J1 / J2 / J3 / J4 / J5):
   - **Shadow Meta-Controller** (non-acting divergence tracker in
     `intelligence_engine/meta_controller/policy/shadow_policy.py`,
     INV-52) — Phase 6.T1b
   - **Belief + Pressure calibration loop** (offline, governance-gated
     `learning_engine/calibration/coherence_calibrator.py`,
     INV-53) — Phase 6.T1c
   - **Per-component reward audit** (`RewardBreakdown` ledger row +
     `registry/reward_components.yaml` allowlist, B18; extends v3.1
     INV-47) — Phase 6.T1c
   - **Agent introspection contract** (pure `state_snapshot()` +
     `recent_decisions(n)` on every `agents/` class via
     `core/contracts/agent.py` Protocol +
     `intelligence_engine/agents/_base.py` ABC, INV-54) — Phase 10.8
   - **Sim-realism tracker + reward penalty**
     (`learning_engine/calibration/sim_realism_tracker.py` +
     `sim_overconfidence_penalty` term in reward shaper, INV-55) —
     Phase 10.1 + Phase 6.T1c

References:

- `manifest.md` — invariants, ENGINE-01..06 model, GOV-CP-01..07,
  PLUGIN-ACT-01..07, authority lint rules
- `build_plan.md` — phase-by-phase delivery plan (E0..E9 + v2 steps 8..13)
- `docs/total_recall_index.md` — IND-L01..L31, DYN-L01..L24, HAZ-01..12,
  CORE-01..31, EXEC-01..14, NEUR-01..03, SAFE-01..27, DASH-01..32
- `MAPPING.md` — layer-id → plugin-slot mapping

Annotation legend:

- **[EXISTS]** — present on `main` today (Phases 0–5 shipped)
- **[NEW v1]** — added by the 22 addons (System Coherence Layer,
  Dashboard OS, hard 3-domain isolation, drift killers)
- **[NEW v2-A..J]** — added by the 10 institutional-grade additions
- **[NEW v3-T1]** — Tier 1 extras follow-on (after Phase 6, fits inside
  existing engines, no spec change)
- **[NEW v3-P10]** — Phase 10 Intelligence Depth Layer (extras Tier 2,
  formal phase append after Phase 9)
- **[NEW v3.1]** — v3.1 fold-in (Intent Engine, Opponent Model,
  Reflexive Sim, Strategy Genetics, Regret Memory, Internal Debate)
- **[NEW v3.2]** — v3.2 stress-stabilization (fallback lane,
  hysteresis, entropy uncertainty, agent_context schema, richer
  simulation outcome, archetype lifecycle, PolicyEngine constant-time table)
- **[NEW v3.3]** — v3.3 self-correction (shadow meta-controller,
  belief+pressure calibration loop, per-component reward audit,
  agent introspection contract, sim-realism tracker)
- otherwise — canonical per `manifest.md §A`, not yet implemented

```text
.
├── AUDIT_AND_ROADMAP.md
├── CTemppytest_out.txt
├── CTemppytest_out2.txt
├── DASHBOARD_SPEC.md
├── DIX MEME.lnk
├── DIX VISION v42.2 – CANONICAL BUILD PLAN.txt
├── DIX VISION v42.2 – CANONICAL SYSTEM MANIFEST.txt
├── DIX VISION v42.2 – COMPLETE EXECUTIVE SUMMARY.txt
├── Dockerfile
├── Makefile
├── PHASE10_ASSESSMENT.md
├── PHASE10_FINAL_REPORT.md
├── PHASE11.1_ASSESSMENT.md
├── PHASE11.1_FINAL_REPORT.md
├── PHASE11.1_IMPLEMENTATION_FINAL_REPORT.md
├── PHASE11_ASSESSMENT.md
├── PHASE11_FINAL_REPORT.md
├── PHASE12_ASSESSMENT.md
├── PHASE12_FINAL_REPORT.md
├── PHASE13_ASSESSMENT.md
├── PHASE13_FINAL_REPORT.md
├── PHASE8_ASSESSMENT.md
├── PHASE8_FINAL_REPORT.md
├── PHASE9_ASSESSMENT.md
├── PHASE9_FINAL_REPORT.md
├── README.md
├── Repository Reality Manifest.txt
├── SESSION_LOG.md
├── VERSION
├── all_files.txt
├── alt_data_engine
│   ├── __init__.py
│   ├── macro_feed.py
│   ├── news_parser.py
│   ├── orchestrator.py
│   └── sentiment.py
├── bootstrap_kernel.py
├── build.ps1
├── cleanup_models.py
├── cloud
│   ├── Caddyfile
│   ├── fly.toml
│   ├── k8s
│   │   └── deployment.yaml
│   ├── railway.json
│   ├── render.yaml
│   └── systemd
│       └── dix-vision.service
├── cockpit
│   ├── __init__.py
│   ├── __main__.py
│   ├── api
│   │   ├── __init__.py
│   │   ├── ai.py
│   │   ├── autonomy.py
│   │   ├── charters.py
│   │   ├── custom_strategies.py
│   │   ├── mode.py
│   │   ├── operator.py
│   │   ├── risk.py
│   │   ├── status.py
│   │   └── weekly_scout.py
│   ├── app.py
│   ├── audit
│   │   ├── __init__.py
│   │   ├── decision_diff.py
│   │   ├── operator_actions.py
│   │   └── override_log.py
│   ├── auth.py
│   ├── charter.py
│   ├── chat.py
│   ├── cli
│   │   ├── __init__.py
│   │   └── dix_plugin.py
│   ├── launcher.py
│   ├── llm.py
│   ├── mobile
│   │   ├── README.md
│   │   └── lib
│   │       └── api_client.dart
│   ├── operator_ide.py
│   ├── pairing.py
│   ├── qr.py
│   ├── static
│   │   ├── app.js
│   │   ├── i18n.json
│   │   ├── icon-192.png
│   │   ├── icon-512.png
│   │   ├── index.html
│   │   ├── manifest.webmanifest
│   │   ├── pair.html
│   │   └── service-worker.js
│   ├── voice_alerts.py
│   └── widgets
│       ├── __init__.py
│       ├── alert_center.py
│       ├── decision_trace.py
│       ├── governance_panel.py
│       ├── kill_switch.py
│       ├── master_sliders.py
│       ├── plugin_manager.py
│       ├── portfolio_view.py
│       ├── risk_view.py
│       └── system_health.py
├── cockpit.py
├── cognitive_governance
│   ├── __init__.py
│   ├── belief_integrity.py
│   ├── causal_consistency.py
│   ├── charter.py
│   ├── cognitive_constitution.py
│   ├── cognitive_maturity.py
│   ├── engine.py
│   ├── epistemic_drift.py
│   ├── hallucination_guard.py
│   ├── identity_stability.py
│   ├── learning_coherence.py
│   ├── learning_truthfulness.py
│   ├── long_horizon_memory.py
│   ├── memory_contamination.py
│   ├── mutation_validator.py
│   ├── reward_hacking_detector.py
│   ├── strategy_lineage_guard.py
│   └── synthetic_feedback_detection.py
├── collection_output.txt
├── compose.debug.yaml
├── compose.yaml
├── contracts
│   ├── README.md
│   ├── events.proto
│   ├── execution.proto
│   ├── governance.proto
│   ├── ledger.proto
│   ├── market.proto
│   ├── system.proto
│   └── trader_intelligence.proto
├── core
│   ├── __init__.py
│   ├── authority.py
│   ├── bootstrap
│   │   ├── __init__.py
│   │   ├── dependency_graph.py
│   │   ├── lifecycle.py
│   │   ├── loader.py
│   │   ├── shutdown_sequence.py
│   │   └── startup_sequence.py
│   ├── bootstrap_kernel.py
│   ├── causal_graph.py
│   ├── charter.py
│   ├── cognitive_router
│   │   ├── __init__.py
│   │   ├── router.py
│   │   └── task_class.py
│   ├── coherence
│   │   ├── __init__.py
│   │   ├── belief_state.py
│   │   ├── causal_graph.py
│   │   ├── decision_trace.py
│   │   ├── drift_oracle.py
│   │   ├── engine.py
│   │   ├── meta_adaptation.py
│   │   ├── mode_engine.py
│   │   ├── performance_pressure.py
│   │   ├── reflection_engine.py
│   │   └── system_intent.py
│   ├── constraint_engine
│   │   ├── __init__.py
│   │   ├── compiler.py
│   │   └── expr.py
│   ├── contracts
│   │   ├── __init__.py
│   │   ├── agent.py
│   │   ├── api
│   │   │   ├── __init__.py
│   │   │   ├── backtest_ingestion.py
│   │   │   ├── cognitive_chat.py
│   │   │   ├── cognitive_chat_approvals.py
│   │   │   ├── credentials.py
│   │   │   ├── governance.py
│   │   │   ├── operator.py
│   │   │   └── source_trust.py
│   │   ├── backtest_result.py
│   │   ├── belief_state.py
│   │   ├── cognitive_governance.py
│   │   ├── cognitive_observability.py
│   │   ├── critique.py
│   │   ├── decision_trace.py
│   │   ├── development_mode.py
│   │   ├── engine.py
│   │   ├── event_provenance.py
│   │   ├── events.py
│   │   ├── execution.py
│   │   ├── execution_intent.py
│   │   ├── external_signal_trust.py
│   │   ├── financial_governance.py
│   │   ├── governance.py
│   │   ├── governance_constitution.py
│   │   ├── intelligence.py
│   │   ├── invariants.py
│   │   ├── launches.py
│   │   ├── learning.py
│   │   ├── learning_evolution_freeze.py
│   │   ├── learning_sink.py
│   │   ├── ledger.py
│   │   ├── logger.py
│   │   ├── macro.py
│   │   ├── macro_regime.py
│   │   ├── market.py
│   │   ├── mode_effects.py
│   │   ├── news.py
│   │   ├── observability.py
│   │   ├── operator_authority.py
│   │   ├── operator_consent.py
│   │   ├── operator_governance.py
│   │   ├── opponent.py
│   │   ├── patch.py
│   │   ├── persistence.py
│   │   ├── portfolio.py
│   │   ├── risk.py
│   │   ├── signal_trust.py
│   │   ├── simulation.py
│   │   ├── source_trust_promotions.py
│   │   ├── state.py
│   │   ├── strategy_registry.py
│   │   ├── system_governance.py
│   │   ├── time.py
│   │   ├── trader_intelligence.py
│   │   └── translation.py
│   ├── event_cognition
│   │   ├── __init__.py
│   │   └── lava_patterns.py
│   ├── exceptions.py
│   ├── introspection.py
│   ├── kernel.py
│   ├── mcos_kernel.py
│   ├── registry.py
│   ├── runtime
│   │   ├── __init__.py
│   │   ├── async_runtime.py
│   │   ├── coroutine_manager.py
│   │   ├── execution_context.py
│   │   └── runtime_state.py
│   ├── secrets.py
│   ├── single_instance.py
│   ├── time_source.py
│   └── types.py
├── dash_meme
│   ├── dist
│   │   ├── assets
│   │   │   ├── charts-BtnauOvK.js
│   │   │   ├── charts-BtnauOvK.js.map
│   │   │   ├── icons-CTwBCdTD.js
│   │   │   ├── icons-CTwBCdTD.js.map
│   │   │   ├── index-CU7c-Lbn.css
│   │   │   ├── index-CypWkduA.js
│   │   │   ├── index-CypWkduA.js.map
│   │   │   ├── page-bigswap-TP_cs4IY.js
│   │   │   ├── page-bigswap-TP_cs4IY.js.map
│   │   │   ├── page-copytrading-JadLjE0_.js
│   │   │   ├── page-copytrading-JadLjE0_.js.map
│   │   │   ├── page-multichart-Blyx3G9N.js
│   │   │   ├── page-multichart-Blyx3G9N.js.map
│   │   │   ├── page-multiswap-CQtv4H1U.js
│   │   │   ├── page-multiswap-CQtv4H1U.js.map
│   │   │   ├── page-pairexplorer-C27TmZNe.js
│   │   │   ├── page-pairexplorer-C27TmZNe.js.map
│   │   │   ├── page-poolexplorer-DSDk2n3n.js
│   │   │   ├── page-poolexplorer-DSDk2n3n.js.map
│   │   │   ├── page-sniper-PaiRxMei.js
│   │   │   ├── page-sniper-PaiRxMei.js.map
│   │   │   ├── page-stats-CtW60TSk.js
│   │   │   ├── page-stats-CtW60TSk.js.map
│   │   │   ├── page-trade-DBfR4-kf.js
│   │   │   ├── page-trade-DBfR4-kf.js.map
│   │   │   ├── page-walletinfo-HLss8u0G.js
│   │   │   ├── page-walletinfo-HLss8u0G.js.map
│   │   │   ├── rolldown-runtime-jpDsebLB.js
│   │   │   ├── vendor-Co67Csqk.js
│   │   │   └── vendor-Co67Csqk.js.map
│   │   └── index.html
│   ├── eslint.config.js
│   ├── index.html
│   ├── package-lock.json
│   ├── package.json
│   ├── postcss.config.js
│   ├── src
│   │   ├── App.tsx
│   │   ├── api
│   │   │   ├── base.ts
│   │   │   ├── feeds.ts
│   │   │   └── intent.ts
│   │   ├── components
│   │   │   ├── HoldersPanel.tsx
│   │   │   ├── HotPairsTicker.tsx
│   │   │   ├── Panel.tsx
│   │   │   ├── PriceChart.tsx
│   │   │   ├── RugScoreCard.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   ├── StatusPill.tsx
│   │   │   ├── ToastHost.tsx
│   │   │   ├── TopBar.tsx
│   │   │   ├── TradeForm.tsx
│   │   │   └── TxFeed.tsx
│   │   ├── index.css
│   │   ├── main.tsx
│   │   ├── pages
│   │   │   ├── BigSwapPage.tsx
│   │   │   ├── CopyTradingPage.tsx
│   │   │   ├── MultichartPage.tsx
│   │   │   ├── MultiswapPage.tsx
│   │   │   ├── PairExplorerPage.tsx
│   │   │   ├── PoolExplorerPage.tsx
│   │   │   ├── SniperPage.tsx
│   │   │   ├── StatsPage.tsx
│   │   │   ├── TradePage.tsx
│   │   │   └── WalletInfoPage.tsx
│   │   ├── router.ts
│   │   ├── state
│   │   │   ├── autonomy.ts
│   │   │   ├── pair.ts
│   │   │   └── toast.ts
│   │   └── theme
│   │       └── tokens.css
│   ├── tailwind.config.js
│   ├── tsconfig.app.json
│   ├── tsconfig.app.tsbuildinfo
│   ├── tsconfig.json
│   ├── tsconfig.node.json
│   ├── tsconfig.node.tsbuildinfo
│   └── vite.config.ts
├── dashboard2026
│   ├── Dockerfile
│   ├── README.md
│   ├── __init__.py
│   ├── data
│   │   └── sqlite
│   │       └── ledger.db
│   ├── dist
│   │   ├── assets
│   │   │   ├── grid-Dz9xsc_a.js
│   │   │   ├── grid-Dz9xsc_a.js.map
│   │   │   ├── icons-Dsl7qGmD.js
│   │   │   ├── icons-Dsl7qGmD.js.map
│   │   │   ├── index-Cf-dj7sj.css
│   │   │   ├── index-pcl2W5Km.js
│   │   │   ├── index-pcl2W5Km.js.map
│   │   │   ├── page-adapters-TXymqOK5.js
│   │   │   ├── page-adapters-TXymqOK5.js.map
│   │   │   ├── page-ai-D1NQAZmU.js
│   │   │   ├── page-ai-D1NQAZmU.js.map
│   │   │   ├── page-alerts-BlaiFQHl.js
│   │   │   ├── page-alerts-BlaiFQHl.js.map
│   │   │   ├── page-asset-dex-CS3k-Shs.js
│   │   │   ├── page-asset-dex-CS3k-Shs.js.map
│   │   │   ├── page-asset-forex-D0Q71ktr.js
│   │   │   ├── page-asset-forex-D0Q71ktr.js.map
│   │   │   ├── page-asset-nft-BCQDV1GI.js
│   │   │   ├── page-asset-nft-BCQDV1GI.js.map
│   │   │   ├── page-asset-perps-B8bcuYGB.js
│   │   │   ├── page-asset-perps-B8bcuYGB.js.map
│   │   │   ├── page-asset-spot-HRUPQeJY.js
│   │   │   ├── page-asset-spot-HRUPQeJY.js.map
│   │   │   ├── page-asset-stocks-m0-Asjyz.js
│   │   │   ├── page-asset-stocks-m0-Asjyz.js.map
│   │   │   ├── page-audit-7cwKZytQ.js
│   │   │   ├── page-audit-7cwKZytQ.js.map
│   │   │   ├── page-charting-B-t6KNli.js
│   │   │   ├── page-charting-B-t6KNli.js.map
│   │   │   ├── page-cognitivechat-DER2eTdk.js
│   │   │   ├── page-cognitivechat-DER2eTdk.js.map
│   │   │   ├── page-credentials-B1Y7MQkv.js
│   │   │   ├── page-credentials-B1Y7MQkv.js.map
│   │   │   ├── page-dyonlearning-DDh0xqZI.js
│   │   │   ├── page-dyonlearning-DDh0xqZI.js.map
│   │   │   ├── page-fabric-KQFdlClm.js
│   │   │   ├── page-fabric-KQFdlClm.js.map
│   │   │   ├── page-forms-SbofTHRk.js
│   │   │   ├── page-forms-SbofTHRk.js.map
│   │   │   ├── page-governance-DejE6mCm.js
│   │   │   ├── page-governance-DejE6mCm.js.map
│   │   │   ├── page-hazards-Ch6-DRXr.js
│   │   │   ├── page-hazards-Ch6-DRXr.js.map
│   │   │   ├── page-indiralearning-BB5G_qpV.js
│   │   │   ├── page-indiralearning-BB5G_qpV.js.map
│   │   │   ├── page-ledger-BYYIDd20.js
│   │   │   ├── page-ledger-BYYIDd20.js.map
│   │   │   ├── page-marketcontext-6lvkYjlS.js
│   │   │   ├── page-marketcontext-6lvkYjlS.js.map
│   │   │   ├── page-memory-DC0sRqfu.js
│   │   │   ├── page-memory-DC0sRqfu.js.map
│   │   │   ├── page-observatory-BGj3U5gn.js
│   │   │   ├── page-observatory-BGj3U5gn.js.map
│   │   │   ├── page-onchain-DuL3JjOg.js
│   │   │   ├── page-onchain-DuL3JjOg.js.map
│   │   │   ├── page-operator-B8t4aPUj.js
│   │   │   ├── page-operator-B8t4aPUj.js.map
│   │   │   ├── page-orderflow-B7-OeytU.js
│   │   │   ├── page-orderflow-B7-OeytU.js.map
│   │   │   ├── page-plugins-C2V0Ldzk.js
│   │   │   ├── page-plugins-C2V0Ldzk.js.map
│   │   │   ├── page-positions-VCcCSR9X.js
│   │   │   ├── page-positions-VCcCSR9X.js.map
│   │   │   ├── page-risk-DEFr4Ih-.js
│   │   │   ├── page-risk-DEFr4Ih-.js.map
│   │   │   ├── page-scout-BZGwpRXl.js
│   │   │   ├── page-scout-BZGwpRXl.js.map
│   │   │   ├── page-security-MM9Z26P6.js
│   │   │   ├── page-security-MM9Z26P6.js.map
│   │   │   ├── page-signals-DgGhtrPd.js
│   │   │   ├── page-signals-DgGhtrPd.js.map
│   │   │   ├── page-simulation-B4rWtUKc.js
│   │   │   ├── page-simulation-B4rWtUKc.js.map
│   │   │   ├── page-strategies-CH09hA_l.js
│   │   │   ├── page-strategies-CH09hA_l.js.map
│   │   │   ├── page-systemhealth-CtFoV_s5.js
│   │   │   ├── page-systemhealth-CtFoV_s5.js.map
│   │   │   ├── page-testing-CeEZH8uq.js
│   │   │   ├── page-testing-CeEZH8uq.js.map
│   │   │   ├── page-trading-DPnCQcrW.js
│   │   │   ├── page-trading-DPnCQcrW.js.map
│   │   │   ├── rolldown-runtime-jpDsebLB.js
│   │   │   ├── vendor-BKOGg0tS.js
│   │   │   └── vendor-BKOGg0tS.js.map
│   │   └── index.html
│   ├── eslint.config.js
│   ├── index.html
│   ├── package-lock.json
│   ├── package.json
│   ├── pnpm-lock.yaml
│   ├── postcss.config.js
│   ├── src
│   │   ├── App.tsx
│   │   ├── api
│   │   │   ├── alerts.ts
│   │   │   ├── audit.ts
│   │   │   ├── base.ts
│   │   │   ├── cognitive.ts
│   │   │   ├── cognitive_chat.ts
│   │   │   ├── credentials.ts
│   │   │   ├── dashboard.ts
│   │   │   ├── fabric.ts
│   │   │   ├── governance.ts
│   │   │   ├── memory.ts
│   │   │   ├── operator.ts
│   │   │   ├── plugins.ts
│   │   │   ├── scout.ts
│   │   │   ├── signals.ts
│   │   │   ├── simulation.ts
│   │   │   ├── strategies.ts
│   │   │   ├── syshealth.ts
│   │   │   ├── testing.ts
│   │   │   └── voicealerts.ts
│   │   ├── components
│   │   │   ├── AdapterStatusGrid.tsx
│   │   │   ├── ApprovalPanel.tsx
│   │   │   ├── AssetGrid.tsx
│   │   │   ├── AuthorityViolationCounter.tsx
│   │   │   ├── AutonomyRibbon.tsx
│   │   │   ├── CognitiveHealthStrip.tsx
│   │   │   ├── CommandPalette.tsx
│   │   │   ├── DomainIndicator.tsx
│   │   │   ├── EngineBucketBadge.tsx
│   │   │   ├── HotkeyConfigurator.tsx
│   │   │   ├── KillSwitchPill.tsx
│   │   │   ├── LiveStatusPill.tsx
│   │   │   ├── MockDataBanner.tsx
│   │   │   ├── ModeRibbon.tsx
│   │   │   ├── ModeTimeline.tsx
│   │   │   ├── PadlockFloors.tsx
│   │   │   ├── PlaceholderWidget.tsx
│   │   │   ├── PopoutButton.tsx
│   │   │   ├── PreferencesBar.tsx
│   │   │   ├── PromoteChain.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   ├── StateBadge.tsx
│   │   │   ├── ToastHost.tsx
│   │   │   ├── TradingStatusPill.tsx
│   │   │   ├── WidgetSlot.tsx
│   │   │   ├── WidgetStatusChip.tsx
│   │   │   └── WidgetTogglePanel.tsx
│   │   ├── index.css
│   │   ├── lib
│   │   │   └── fuzzy.ts
│   │   ├── main.tsx
│   │   ├── pages
│   │   │   ├── AIPage.tsx
│   │   │   ├── AdaptersPage.tsx
│   │   │   ├── AlertsPage.tsx
│   │   │   ├── AuditPage.tsx
│   │   │   ├── ChartingPage.tsx
│   │   │   ├── CognitiveChatPage.tsx
│   │   │   ├── CredentialsPage.tsx
│   │   │   ├── DyonLearningPage.tsx
│   │   │   ├── FabricPage.tsx
│   │   │   ├── FormsPage.tsx
│   │   │   ├── GovernancePage.tsx
│   │   │   ├── HazardsPage.tsx
│   │   │   ├── IndiraLearningPage.tsx
│   │   │   ├── LedgerPage.tsx
│   │   │   ├── MarketContextPage.tsx
│   │   │   ├── MemoryPage.tsx
│   │   │   ├── ObservatoryPage.tsx
│   │   │   ├── OnChainPage.tsx
│   │   │   ├── OpenOrdersFillsPage.tsx
│   │   │   ├── OperatorPage.tsx
│   │   │   ├── OrderFlowPage.tsx
│   │   │   ├── PluginsPage.tsx
│   │   │   ├── PositionsPage.tsx
│   │   │   ├── RiskPage.tsx
│   │   │   ├── ScoutPage.tsx
│   │   │   ├── SecurityPage.tsx
│   │   │   ├── SignalsPage.tsx
│   │   │   ├── SimulationPage.tsx
│   │   │   ├── StrategiesPage.tsx
│   │   │   ├── SystemHealthPage.tsx
│   │   │   ├── TestingPage.tsx
│   │   │   ├── TradingPage.tsx
│   │   │   └── asset
│   │   │       ├── AssetPageShell.tsx
│   │   │       ├── DexPage.tsx
│   │   │       ├── ForexPage.tsx
│   │   │       ├── MemecoinPage.tsx
│   │   │       ├── NftPage.tsx
│   │   │       ├── PerpsPage.tsx
│   │   │       ├── SpotPage.tsx
│   │   │       └── StocksPage.tsx
│   │   ├── preferences
│   │   │   └── store.ts
│   │   ├── router.ts
│   │   ├── state
│   │   │   ├── autonomy.ts
│   │   │   ├── cognitive_realtime.ts
│   │   │   ├── hotkeys.ts
│   │   │   ├── popout.ts
│   │   │   ├── realtime.ts
│   │   │   ├── toast.ts
│   │   │   └── widgetVisibility.ts
│   │   ├── theme
│   │   │   └── tokens.css
│   │   ├── types
│   │   │   └── generated
│   │   │       └── api.ts
│   │   ├── ui
│   │   │   └── toast.ts
│   │   ├── vite-env.d.ts
│   │   └── widgets
│   │       ├── AlertsHub.tsx
│   │       ├── ChartPanel.tsx
│   │       ├── CognitiveObservatory.tsx
│   │       ├── CoherencePanel.tsx
│   │       ├── CommandPalette.tsx
│   │       ├── DensityProvider.tsx
│   │       ├── DepthLadder.tsx
│   │       ├── DyonArchitectureStream.tsx
│   │       ├── DyonChat.tsx
│   │       ├── DyonLearningMode.tsx
│   │       ├── DyonWorkspace.tsx
│   │       ├── IndiraChat.tsx
│   │       ├── IndiraCognitiveStream.tsx
│   │       ├── IndiraConsciousnessPanel.tsx
│   │       ├── IndiraLearningMode.tsx
│   │       ├── NewsTicker.tsx
│   │       ├── OrderForm.tsx
│   │       ├── PositionsPanel.tsx
│   │       ├── SLTPBuilder.tsx
│   │       ├── TimeAndSalesTape.tsx
│   │       ├── TradingFormTiles.tsx
│   │       ├── ai
│   │       │   ├── ASKBOrchestrator.tsx
│   │       │   ├── AltSignalDashboard.tsx
│   │       │   ├── CausalRiskAttribution.tsx
│   │       │   ├── CounterfactualPanel.tsx
│   │       │   ├── EarningsRAG.tsx
│   │       │   ├── IntentExecutionPanel.tsx
│   │       │   ├── MultilingualNewsFusion.tsx
│   │       │   ├── NLQConsole.tsx
│   │       │   └── SmartMoneyTracker.tsx
│   │       ├── chart
│   │       │   ├── ADXPanel.tsx
│   │       │   ├── ATRPanel.tsx
│   │       │   ├── ChartTypeSwitcher.tsx
│   │       │   ├── DrawingToolsRail.tsx
│   │       │   ├── EquityCurve.tsx
│   │       │   ├── HeatmapPanel.tsx
│   │       │   ├── MACDPanel.tsx
│   │       │   ├── RSIPanel.tsx
│   │       │   ├── RegimeTimeline.tsx
│   │       │   ├── StochasticPanel.tsx
│   │       │   └── VolumeProfile.tsx
│   │       ├── dex
│   │       │   ├── GasEstimator.tsx
│   │       │   ├── PoolHealth.tsx
│   │       │   └── RouteGraph.tsx
│   │       ├── domains
│   │       │   └── DomainPanel.tsx
│   │       ├── forex
│   │       │   ├── CarryLadder.tsx
│   │       │   ├── CentralBankRates.tsx
│   │       │   ├── CurrencyStrength.tsx
│   │       │   ├── EconomicCalendar.tsx
│   │       │   ├── PipCalc.tsx
│   │       │   └── SessionClock.tsx
│   │       ├── governance
│   │       │   ├── ApprovalQueueWidget.tsx
│   │       │   ├── AuditLedgerViewer.tsx
│   │       │   ├── DriftOraclePanel.tsx
│   │       │   ├── HazardMonitorGrid.tsx
│   │       │   ├── PromotionGatesPanel.tsx
│   │       │   ├── SCVSLivenessGrid.tsx
│   │       │   └── StrategyRegistryFSM.tsx
│   │       ├── market
│   │       │   ├── FearGreed.tsx
│   │       │   ├── HotMovers.tsx
│   │       │   ├── IVSurface.tsx
│   │       │   ├── LongShortRatio.tsx
│   │       │   ├── OpenInterestPanel.tsx
│   │       │   ├── PutCallRatio.tsx
│   │       │   ├── SentimentGauge.tsx
│   │       │   └── Watchlist.tsx
│   │       ├── memecoin
│   │       │   ├── BundleDetector.tsx
│   │       │   ├── CopyLeaderboard.tsx
│   │       │   ├── DevDumpWatchdog.tsx
│   │       │   ├── HolderConcentration.tsx
│   │       │   ├── HoneypotChecker.tsx
│   │       │   ├── LaunchFirehose.tsx
│   │       │   ├── PairCard.tsx
│   │       │   ├── RugScore.tsx
│   │       │   ├── SignalTracker.tsx
│   │       │   ├── SniperQueue.tsx
│   │       │   └── WalletCluster.tsx
│   │       ├── nft
│   │       │   ├── BidLadder.tsx
│   │       │   ├── CollectionVolume.tsx
│   │       │   ├── RarityLens.tsx
│   │       │   ├── SweepCart.tsx
│   │       │   └── TraitFloorGrid.tsx
│   │       ├── onchain
│   │       │   ├── ExchangeFlows.tsx
│   │       │   ├── OpenInterestMatrix.tsx
│   │       │   ├── StablecoinSupply.tsx
│   │       │   ├── TVLDashboard.tsx
│   │       │   └── WhaleWatcher.tsx
│   │       ├── operator
│   │       │   ├── ApprovalQueue.tsx
│   │       │   ├── AuthoritySwitches.tsx
│   │       │   ├── LearningProgress.tsx
│   │       │   └── TradingModePanel.tsx
│   │       ├── orderflow
│   │       │   ├── AggressorRatio.tsx
│   │       │   ├── CVDChart.tsx
│   │       │   ├── DOMClickLadder.tsx
│   │       │   ├── FootprintChart.tsx
│   │       │   ├── LiquidityHeatmap.tsx
│   │       │   └── SweepIcebergMonitor.tsx
│   │       ├── orders
│   │       │   └── OrdersWidgets.tsx
│   │       ├── perps
│   │       │   ├── FundingTable.tsx
│   │       │   ├── LiquidationMap.tsx
│   │       │   └── OracleSpread.tsx
│   │       ├── positions
│   │       │   ├── DrawdownCurve.tsx
│   │       │   ├── ExposureBreakdown.tsx
│   │       │   ├── FillsHistory.tsx
│   │       │   ├── FundingHistory.tsx
│   │       │   ├── IntradayPnLCurve.tsx
│   │       │   ├── OpenOrdersPanel.tsx
│   │       │   ├── PositionManager.tsx
│   │       │   └── RiskParityAllocator.tsx
│   │       ├── research
│   │       │   ├── ActiveResearchPanel.tsx
│   │       │   ├── ArchetypePerformance.tsx
│   │       │   ├── AtomRegistry.tsx
│   │       │   ├── CompositionStatus.tsx
│   │       │   ├── DataSourceHealth.tsx
│   │       │   ├── DivergenceAlerts.tsx
│   │       │   ├── LearningLanesMonitor.tsx
│   │       │   ├── NarrativeTracker.tsx
│   │       │   ├── RegimeClassifier.tsx
│   │       │   ├── ResearchPanel.tsx
│   │       │   └── SentimentStream.tsx
│   │       ├── risk
│   │       │   ├── CorrelationMatrix.tsx
│   │       │   ├── GreeksPanel.tsx
│   │       │   ├── LiqCalc.tsx
│   │       │   ├── OptionsChain.tsx
│   │       │   └── ScenarioBook.tsx
│   │       ├── stocks
│   │       │   ├── AnalystRatings.tsx
│   │       │   ├── Fundamentals.tsx
│   │       │   ├── InsiderTransactions.tsx
│   │       │   ├── SectorHeatmap.tsx
│   │       │   └── ShortInterest.tsx
│   │       ├── testing
│   │       │   ├── Backtester.tsx
│   │       │   ├── CalibrationReliability.tsx
│   │       │   ├── ChampionChallenger.tsx
│   │       │   ├── EquityCurveStudio.tsx
│   │       │   ├── ForwardTester.tsx
│   │       │   ├── MonteCarloPaths.tsx
│   │       │   ├── ParameterSweep.tsx
│   │       │   ├── RegimeShiftBoard.tsx
│   │       │   ├── ReplayHarness.tsx
│   │       │   └── WalkForwardHarness.tsx
│   │       └── trading
│   │           ├── AlgoOrderBuilder.tsx
│   │           ├── BasketOrderEditor.tsx
│   │           ├── ConditionalBracketBuilder.tsx
│   │           ├── OrderHotkeysPanel.tsx
│   │           └── PreTradeSlippageSim.tsx
│   ├── state_sync.py
│   ├── tailwind.config.js
│   ├── tsconfig.app.json
│   ├── tsconfig.app.tsbuildinfo
│   ├── tsconfig.json
│   ├── tsconfig.node.json
│   ├── tsconfig.node.tsbuildinfo
│   ├── views.py
│   ├── vite.config.ts
│   └── websocket_layer.py
├── dashboard_backend
│   ├── __init__.py
│   └── control_plane
│       ├── __init__.py
│       ├── decision_trace.py
│       ├── engine_status_grid.py
│       ├── memecoin_control_panel.py
│       ├── mode_control_bar.py
│       ├── router.py
│       ├── strategy_lifecycle_panel.py
│       └── trader_intelligence_panel.py
├── data
│   ├── audit.jsonl
│   ├── cockpit_token.txt
│   ├── logs
│   │   └── system.log
│   ├── memory_timeline.db
│   ├── sqlite
│   │   ├── cognition.db
│   │   ├── ledger.db
│   │   ├── ledger.db-shm
│   │   └── ledger.db-wal
│   └── unified_fabric.db
├── data_pipeline
│   ├── __init__.py
│   └── normalizer.py
├── data_sources
│   └── external
│       ├── __init__.py
│       ├── news_feed.py
│       ├── reddit_sentiment.py
│       ├── social_sentiment.py
│       ├── tradingview_ideas.py
│       └── x_crypto_sentiment.py
├── dependency_graph.json
├── deployment
│   └── deployment_pipeline.py
├── diagnose_foundation.py
├── dix.py
├── dixvision-1.code-workspace
├── docker-compose.yml
├── docs
│   ├── ARCHITECTURE_V42_2_TIER0.md
│   ├── BUILD_DIRECTIVE_LINT_MAPPING.md
│   ├── CAUSAL_CONTRACT.md
│   ├── CLOUD.md
│   ├── COGNITIVE_OS.md
│   ├── CONVERGENCE_IMPLEMENTATION_PLAN.md
│   ├── DEX_AND_BOT_ADAPTER_ROADMAP.md
│   ├── DIX_VISION_v42_2_COMPILED.md
│   ├── INDIRA_WEB_AUTOLEARN_SPEC.md
│   ├── INSTALL.md
│   ├── MEMECOIN_TRADING_SPEC.md
│   ├── MOBILE.md
│   ├── NEUROMORPHIC_TRIAD_SPEC.md
│   ├── OPTIMIZATION_PLAN.md
│   ├── PHASE_0_ATTESTATION.md
│   ├── PR2_SPEC.md
│   ├── SANDBOX.md
│   ├── TOTAL_VALIDATION_SPEC.md
│   ├── architecture
│   │   ├── aat_async_patterns.md
│   │   ├── aeron_analysis.md
│   │   ├── disruptor_analysis.md
│   │   ├── esper_cep_patterns.md
│   │   └── rust_hot_path_reference.md
│   ├── archive
│   │   └── build_status_v3.3_stale.md
│   ├── autohedge_role_mapping.md
│   ├── build_status.md
│   ├── build_tier_completion.md
│   ├── canonical
│   │   ├── phase_0_status.md
│   │   ├── phase_1_status.md
│   │   ├── phase_2_status.md
│   │   └── phase_3_status.md
│   ├── canonical_pipeline.md
│   ├── coverage_report.md
│   ├── cross_domain_audit_v42.2.md
│   ├── dashboard_2026_wave03_cognitive_plan.md
│   ├── dependency_roadmap.md
│   ├── directory_tree.md
│   ├── enforcement_matrix.md
│   ├── invariants_dixvision_v42.2.md
│   ├── lava_event_driven_patterns.md
│   ├── lob_implementation_decision.md
│   ├── manifest_v3.1_delta.md
│   ├── manifest_v3.2_delta.md
│   ├── manifest_v3.3_delta.md
│   ├── manifest_v3.4_delta.md
│   ├── manifest_v3.5.1_delta.md
│   ├── manifest_v3.5.2_delta.md
│   ├── manifest_v3.5.3_delta.md
│   ├── manifest_v3.5.4_delta.md
│   ├── manifest_v3.5.5_delta.md
│   ├── manifest_v3.5_delta.md
│   ├── manifest_v3.6.0_delta.md
│   ├── manifest_v3.6.1_delta.md
│   ├── manifest_v3.6.2_delta.md
│   ├── manifest_v3.6.3_delta.md
│   ├── manifest_v3.6.4_delta.md
│   ├── manifest_v42.2_cognitive_delta.md
│   ├── manifest_v42.2_cognitive_expansion.md
│   ├── n8n_workflow_setup.md
│   ├── promotion_gates.yaml
│   ├── rust_revival_schedule.yaml
│   ├── sensory
│   │   └── web_autolearn_activation.md
│   ├── sourcegraph_dyon_usage.md
│   ├── stratification_changes_v42.2.md
│   ├── superalgos_patterns.md
│   ├── system_audit
│   │   ├── REPORT.md
│   │   ├── _tools
│   │   │   ├── build_plan_stage.py
│   │   │   ├── build_tracking.py
│   │   │   ├── bulk_scan.py
│   │   │   ├── enumerate.py
│   │   │   ├── finalize_tracking.py
│   │   │   ├── orphan_scan.py
│   │   │   └── registry_coverage.py
│   │   ├── build_plan_stage.csv
│   │   ├── build_plan_stage.json
│   │   ├── build_plan_stage.md
│   │   ├── bulk_findings.json
│   │   ├── coverage_summary.json
│   │   ├── file_index.csv
│   │   ├── import_graph.json
│   │   ├── orphan_modules.csv
│   │   ├── per_directory
│   │   │   ├── core.md
│   │   │   ├── execution_engine.md
│   │   │   ├── governance_engine.md
│   │   │   ├── intelligence_engine.md
│   │   │   ├── registry_tools_tests_misc.md
│   │   │   ├── sensory_learning_evolution.md
│   │   │   ├── system_engine.md
│   │   │   └── ui_dashboards.md
│   │   ├── registry_coverage.csv
│   │   └── tracking.csv
│   ├── total_recall_index.md
│   ├── transformer_policy_research.md
│   └── wave_04_6_plan.md
├── enforcement
│   ├── __init__.py
│   ├── decorators.py
│   ├── hazard_guard.py
│   ├── kill_switch.py
│   ├── policy_enforcer.py
│   ├── resource_enforcer.py
│   └── runtime_guardian.py
├── evolution_engine
│   ├── __init__.py
│   ├── charter
│   │   ├── __init__.py
│   │   ├── dyon.py
│   │   └── dyon_observability_emitter.py
│   ├── critique_loop.py
│   ├── distributed_analytics.py
│   ├── dyon
│   │   ├── __init__.py
│   │   ├── dead_code_detector.py
│   │   ├── dependency_graph.py
│   │   ├── drift_monitor.py
│   │   ├── dyon_engineering_runtime.py
│   │   ├── dyon_memory.py
│   │   ├── dyon_runtime.py
│   │   ├── patch_generator.py
│   │   ├── patch_simulator.py
│   │   ├── repo_inspector.py
│   │   ├── test_coverage_tracker.py
│   │   └── topology_scanner.py
│   ├── engine.py
│   ├── environments
│   │   ├── __init__.py
│   │   ├── anytrading_env.py
│   │   ├── base_env.py
│   │   └── multiagent_env.py
│   ├── evolution_orchestrator.py
│   ├── experiment_tracking.py
│   ├── experimental
│   │   ├── __init__.py
│   │   └── transformer_policy.py
│   ├── genetic
│   │   ├── __init__.py
│   │   ├── cmaes_optimizer.py
│   │   ├── crossover.py
│   │   ├── fitness_inheritance.py
│   │   ├── mutation_operators.py
│   │   └── strategy_chromosome.py
│   ├── governed_pipeline.py
│   ├── gym_env.py
│   ├── intelligence_loops
│   │   ├── __init__.py
│   │   └── mutation_proposer.py
│   ├── jax_policy_search.py
│   ├── kubeflow_pipeline.py
│   ├── lifecycle
│   │   ├── __init__.py
│   │   ├── audit.py
│   │   ├── benchmark.py
│   │   ├── contracts.py
│   │   ├── coordinator.py
│   │   ├── deployment.py
│   │   ├── rollback.py
│   │   ├── sandbox.py
│   │   └── simulation.py
│   ├── loops
│   │   ├── __init__.py
│   │   └── structural_loop.py
│   ├── patch_pipeline
│   │   ├── __init__.py
│   │   ├── backtest.py
│   │   ├── canary.py
│   │   ├── critique_loop.py
│   │   ├── events.py
│   │   ├── firecracker_sandbox.py
│   │   ├── gvisor_sandbox.py
│   │   ├── orchestrator.py
│   │   ├── pipeline.py
│   │   ├── rollback.py
│   │   ├── sandbox.py
│   │   ├── sandbox_openhands.py
│   │   ├── shadow.py
│   │   └── static_analysis.py
│   ├── pipeline.py
│   ├── pipeline_orchestrator.py
│   ├── proposals.py
│   ├── rllib_trainer.py
│   ├── runtime_wiring.py
│   ├── sandbox.py
│   ├── sandbox_elegant.py
│   ├── sandbox_mushroom.py
│   ├── sandbox_sample_factory.py
│   ├── sandbox_tianshou.py
│   ├── strategy_genome
│   │   ├── __init__.py
│   │   ├── mutation_engine.py
│   │   ├── recombination_engine.py
│   │   └── strategy_genome.py
│   ├── task_queue.py
│   ├── test_generator.py
│   └── wandb_tracker.py
├── execution
│   ├── __init__.py
│   ├── adapter_router.py
│   ├── adapters
│   │   ├── __init__.py
│   │   ├── _ccxt_backed.py
│   │   ├── base.py
│   │   ├── binance.py
│   │   ├── coinbase.py
│   │   ├── kraken.py
│   │   ├── raydium.py
│   │   └── uniswap_v3.py
│   ├── algos
│   │   └── __init__.py
│   ├── async_bus.py
│   ├── chaos_engine.py
│   ├── confirmations
│   │   ├── __init__.py
│   │   ├── fill_tracker.py
│   │   └── reconciliation.py
│   ├── emergency_executor.py
│   ├── engine.py
│   ├── event_emitter.py
│   ├── fast_lane.py
│   ├── feedback.py
│   ├── hazard
│   │   ├── __init__.py
│   │   ├── async_bus.py
│   │   ├── detector.py
│   │   ├── event_emitter.py
│   │   └── severity_classifier.py
│   ├── hazard_lane.py
│   ├── live_trading
│   │   ├── __init__.py
│   │   ├── audit_system.py
│   │   ├── deterministic_executor.py
│   │   ├── governance_layer.py
│   │   ├── ledger_backed_operations.py
│   │   ├── phase14_verification.py
│   │   └── risk_constraints.py
│   ├── mcos_adapter_router.py
│   ├── mcos_emergency_executor.py
│   ├── mcos_trade_executor.py
│   ├── mev_guard.py
│   ├── monitoring
│   │   ├── __init__.py
│   │   └── neuromorphic_detector.py
│   ├── offline_lane.py
│   ├── runtime_monitor.py
│   ├── severity_classifier.py
│   ├── slippage.py
│   ├── system_repair_orchestrator.py
│   ├── tca.py
│   └── trade_executor.py
├── execution_engine
│   ├── __init__.py
│   ├── adapters
│   │   ├── __init__.py
│   │   ├── _cache_mixin.py
│   │   ├── _hummingbot_gateway.py
│   │   ├── _live_base.py
│   │   ├── _retry_mixin.py
│   │   ├── _retry_mixin_tenacity.py
│   │   ├── _uniswapx_quote.py
│   │   ├── _uniswapx_signer.py
│   │   ├── alpaca.py
│   │   ├── alphavantage.py
│   │   ├── audit_trail.py
│   │   ├── base.py
│   │   ├── binance.py
│   │   ├── binance_ws.py
│   │   ├── circuit_breaker.py
│   │   ├── coinbase.py
│   │   ├── external
│   │   │   ├── __init__.py
│   │   │   ├── backtrader.py
│   │   │   ├── freqtrade.py
│   │   │   ├── jesse.py
│   │   │   ├── mt5.py
│   │   │   ├── qstrader.py
│   │   │   ├── quantconnect.py
│   │   │   ├── tradingview.py
│   │   │   └── vectorbt.py
│   │   ├── helius.py
│   │   ├── hummingbot.py
│   │   ├── ibkr.py
│   │   ├── iex.py
│   │   ├── ig.py
│   │   ├── kraken.py
│   │   ├── latency_monitor.py
│   │   ├── oanda.py
│   │   ├── order_validation.py
│   │   ├── paper.py
│   │   ├── platforms
│   │   │   ├── __init__.py
│   │   │   ├── alpaca.py
│   │   │   ├── ibkr.py
│   │   │   ├── mt5.py
│   │   │   ├── quantconnect.py
│   │   │   └── tradingview.py
│   │   ├── polygon.py
│   │   ├── pumpfun.py
│   │   ├── rate_limiter.py
│   │   ├── registry.py
│   │   ├── router.py
│   │   ├── slippage_control.py
│   │   ├── solana_native.py
│   │   ├── uniswapx.py
│   │   └── vnpy_bridge.py
│   ├── domains
│   │   ├── __init__.py
│   │   ├── copy_trading
│   │   │   └── __init__.py
│   │   ├── memecoin
│   │   │   └── __init__.py
│   │   └── normal
│   │       └── __init__.py
│   ├── engine.py
│   ├── execution_gate.py
│   ├── hot_path
│   │   ├── __init__.py
│   │   ├── fast_execute.py
│   │   ├── fast_risk_cache.py
│   │   ├── fast_structs.py
│   │   └── time_authority.py
│   ├── intelligence
│   │   ├── __init__.py
│   │   ├── liquidity_model.py
│   │   ├── order_splitter.py
│   │   ├── slippage_predictor.py
│   │   └── smart_router.py
│   ├── lifecycle
│   │   ├── __init__.py
│   │   ├── fill_handler.py
│   │   ├── order_state_machine.py
│   │   ├── partial_fill_resolver.py
│   │   ├── retry_logic.py
│   │   └── sl_tp_manager.py
│   ├── market_data
│   │   ├── __init__.py
│   │   ├── aggregator.py
│   │   ├── book_builder.py
│   │   ├── latency_tracker.py
│   │   ├── normalizer.py
│   │   └── orderbook.py
│   ├── mcos_orchestrator.py
│   ├── memecoin
│   │   ├── __init__.py
│   │   ├── dex_router.py
│   │   ├── meme_risk_policy.py
│   │   ├── paper_broker_meme.py
│   │   └── sniper.py
│   ├── orchestrator.py
│   ├── paper_trading
│   │   ├── __init__.py
│   │   ├── adapter.py
│   │   ├── hub.py
│   │   ├── ledger_integration.py
│   │   ├── paper_only_enforcer.py
│   │   ├── phase13_verification.py
│   │   ├── promotion_gate_integration.py
│   │   └── venue_config.py
│   ├── pipeline_coordinator.py
│   ├── protections
│   │   ├── __init__.py
│   │   ├── circuit_breaker.py
│   │   ├── feedback.py
│   │   ├── reconciliation.py
│   │   └── runtime_monitor.py
│   ├── semi_auto
│   │   ├── __init__.py
│   │   ├── approval_queue.py
│   │   ├── auto_exit_handler.py
│   │   └── threshold_gate.py
│   ├── strategic
│   │   ├── __init__.py
│   │   └── almgren_chriss.py
│   └── strategic_execution
│       ├── __init__.py
│       ├── adversarial_executor.py
│       ├── market_impact
│       │   ├── __init__.py
│       │   ├── depth_estimator.py
│       │   ├── model.py
│       │   └── slippage_curve.py
│       └── optimal_execution.py
├── financial_governance
│   ├── __init__.py
│   ├── capital_throttle.py
│   ├── charter.py
│   ├── engine.py
│   ├── execution_hazard.py
│   ├── exposure_guard.py
│   ├── kill_switch.py
│   ├── leverage_monitor.py
│   └── liquidation_sentinel.py
├── governance
│   ├── __init__.py
│   ├── authority_graph.py
│   ├── charter.py
│   ├── constraint_compiler.py
│   ├── domains
│   │   ├── __init__.py
│   │   ├── cognitive.py
│   │   ├── financial.py
│   │   ├── operator.py
│   │   └── system.py
│   ├── emergency_policy.py
│   ├── escalation_matrix.py
│   ├── hazard_classifier.py
│   ├── hazard_router.py
│   ├── kernel.py
│   ├── market_context_projector.py
│   ├── mcos_constraint_compiler.py
│   ├── mcos_kernel.py
│   ├── mode
│   │   ├── __init__.py
│   │   ├── degraded_mode.py
│   │   ├── halted_mode.py
│   │   ├── mode_manager.py
│   │   └── safe_mode.py
│   ├── mode_manager.py
│   ├── oracle
│   │   ├── __init__.py
│   │   ├── tier_l1_fast.py
│   │   ├── tier_l2_balanced.py
│   │   └── tier_l3_deep.py
│   ├── patch_pipeline.py
│   ├── policy_engine.py
│   ├── risk_engine.py
│   ├── signals
│   │   ├── __init__.py
│   │   └── neuromorphic_risk.py
│   └── unified_graph.py
├── governance_engine
│   ├── __init__.py
│   ├── control_plane
│   │   ├── __init__.py
│   │   ├── compliance_validator.py
│   │   ├── decision_signer.py
│   │   ├── drift_oracle.py
│   │   ├── event_classifier.py
│   │   ├── exposure_store.py
│   │   ├── external_signal_policy.py
│   │   ├── invariant_verifier.py
│   │   ├── learning_evolution_loop.py
│   │   ├── ledger_authority_writer.py
│   │   ├── operator_attention.py
│   │   ├── operator_interface_bridge.py
│   │   ├── patch_signer.py
│   │   ├── policy_drift_sentry.py
│   │   ├── policy_engine.py
│   │   ├── policy_hash_anchor.py
│   │   ├── promotion_gates.py
│   │   ├── risk_evaluator.py
│   │   ├── state_transition_manager.py
│   │   ├── update_applier.py
│   │   └── update_validator.py
│   ├── engine.py
│   ├── gates
│   │   ├── __init__.py
│   │   ├── quantitative_evaluator.py
│   │   └── rulegraph_patch_evaluator.py
│   ├── hardening
│   │   ├── __init__.py
│   │   ├── coordinator.py
│   │   ├── execution_auditor.py
│   │   ├── invariant_monitor.py
│   │   ├── invariants_state.py
│   │   ├── isolation_boundary.py
│   │   ├── mutation_firewall.py
│   │   ├── policy_lock.py
│   │   ├── replay_engine.py
│   │   └── trust_scorer.py
│   ├── harness_approver.py
│   ├── plugin_lifecycle
│   │   ├── __init__.py
│   │   ├── activation_gate.py
│   │   ├── hot_reload_signal.py
│   │   ├── lifecycle_emitter.py
│   │   ├── manager.py
│   │   └── registry_loader.py
│   ├── policies
│   │   ├── autonomy_levels.rego
│   │   ├── execution_gates.rego
│   │   └── position_limits.rego
│   ├── risk_engine
│   │   ├── __init__.py
│   │   ├── drawdown_guard.py
│   │   ├── exposure_limits.py
│   │   ├── kill_conditions.py
│   │   ├── position_limits.py
│   │   ├── real_time_risk.py
│   │   └── risk_tracker.py
│   ├── services
│   │   ├── __init__.py
│   │   ├── audit_replay.py
│   │   ├── liveness_watchdog.py
│   │   ├── opa_policy.py
│   │   ├── overconfidence_guardrail.py
│   │   ├── patch_pipeline.py
│   │   ├── patch_pipeline_bridge.py
│   │   ├── triple_window_dry_run.py
│   │   └── trust_engine.py
│   ├── strategy_registry.py
│   └── workflows
│       ├── __init__.py
│       └── approval_workflow.py
├── immutable_core
│   ├── __init__.py
│   ├── axioms.py
│   ├── constants.py
│   ├── foundation.hash
│   ├── foundation.py
│   ├── genesis.json
│   ├── hazard_axioms.lean
│   ├── kill_switch.py
│   ├── neuromorphic_axioms.lean
│   ├── safety_axioms.lean
│   └── system_identity.py
├── infrastructure
│   └── nomad
│       ├── README.md
│       └── dixvision.nomad
├── insert_models.py
├── integration_matrix.json
├── integrations
│   ├── __init__.py
│   ├── alpaca
│   │   ├── __init__.py
│   │   └── crypto_feed.py
│   ├── ccxt_adapter
│   │   ├── __init__.py
│   │   └── exchange.py
│   ├── duckdb_adapter
│   │   ├── __init__.py
│   │   └── analytics.py
│   ├── feast_adapter
│   │   ├── __init__.py
│   │   └── features.py
│   ├── haystack_adapter
│   │   ├── __init__.py
│   │   └── rag.py
│   ├── kafka_adapter
│   │   ├── __init__.py
│   │   └── streaming.py
│   ├── langgraph_adapter
│   │   ├── __init__.py
│   │   └── orchestrator.py
│   ├── lightning_adapter
│   │   ├── __init__.py
│   │   └── trainer.py
│   ├── opa_adapter
│   │   ├── __init__.py
│   │   └── policy.py
│   ├── openbb_adapter
│   │   ├── __init__.py
│   │   └── financial_data.py
│   ├── otel_adapter
│   │   ├── __init__.py
│   │   ├── metrics.py
│   │   └── tracing.py
│   ├── qdrant_adapter
│   │   ├── __init__.py
│   │   └── memory.py
│   ├── ray_adapter
│   │   ├── __init__.py
│   │   └── compute.py
│   ├── temporal_adapter
│   │   ├── __init__.py
│   │   └── workflows.py
│   └── wiring
│       ├── __init__.py
│       ├── ccxt_execution_bridge.py
│       ├── kafka_event_bridge.py
│       ├── opa_governance_bridge.py
│       └── qdrant_memory_bridge.py
├── integrity
│   └── verify_boot.py
├── intelligence_engine
│   ├── __init__.py
│   ├── agents
│   │   ├── __init__.py
│   │   ├── _base.py
│   │   ├── adversarial.py
│   │   ├── adversarial_observer.py
│   │   ├── adversary_agent.py
│   │   ├── autohedge_patterns.py
│   │   ├── crew_strategy_council.py
│   │   ├── debate_round.py
│   │   ├── liquidity_provider.py
│   │   ├── lp.py
│   │   ├── macro.py
│   │   ├── scalper.py
│   │   ├── strategy_council.py
│   │   ├── swing.py
│   │   ├── swing_trader.py
│   │   └── trading_agents_bridge.py
│   ├── alpha_miner
│   │   ├── __init__.py
│   │   ├── anomaly_detector.py
│   │   ├── correlation_monitor.py
│   │   └── feature_discoverer.py
│   ├── backtesting.py
│   ├── causal_dowhy.py
│   ├── charter
│   │   ├── __init__.py
│   │   └── indira.py
│   ├── closed_feedback_loop.py
│   ├── cognitive
│   │   ├── __init__.py
│   │   ├── _response_cache.py
│   │   ├── approval_edge.py
│   │   ├── approval_projection.py
│   │   ├── approval_queue.py
│   │   ├── behavioral_cluster.py
│   │   ├── causal_graph.py
│   │   ├── chat
│   │   │   ├── __init__.py
│   │   │   ├── cognitive_chat_graph.py
│   │   │   ├── consumes.yaml
│   │   │   ├── http_chat_transport.py
│   │   │   ├── llama_transport.py
│   │   │   ├── local_transport.py
│   │   │   ├── provider_transports.py
│   │   │   ├── registry_driven_chat_model.py
│   │   │   ├── tensorrt_transport.py
│   │   │   └── vllm_transport.py
│   │   ├── checkpointing
│   │   │   ├── __init__.py
│   │   │   └── audit_ledger_checkpoint_saver.py
│   │   ├── cognitive_development_pipeline.py
│   │   ├── consciousness_stream.py
│   │   ├── debate_graph.py
│   │   ├── dspy_optimizer.py
│   │   ├── dyon_signal_bridge.py
│   │   ├── environment_awareness.py
│   │   ├── guidance_adapter.py
│   │   ├── indira_runtime.py
│   │   ├── instructor_adapter.py
│   │   ├── litellm_router.py
│   │   ├── long_horizon_memory.py
│   │   ├── market_observation_session.py
│   │   ├── meta_learning_adapter.py
│   │   ├── observability_emitter.py
│   │   ├── outlines_adapter.py
│   │   ├── proposal_parser.py
│   │   ├── reflection_engine.py
│   │   ├── reward_adapter.py
│   │   ├── semantic_kernel_bridge.py
│   │   ├── thought_runtime.py
│   │   ├── trader_intelligence_runtime.py
│   │   └── typed_ai.py
│   ├── cross_asset
│   │   ├── __init__.py
│   │   ├── basket_constructor.py
│   │   ├── contagion_detector.py
│   │   ├── correlation_matrix.py
│   │   └── lead_lag.py
│   ├── diag_arviz.py
│   ├── engine.py
│   ├── execution_feedback_integration.py
│   ├── hmm_hmmlearn.py
│   ├── horizon
│   │   ├── __init__.py
│   │   └── horizon_engine.py
│   ├── hte_econml.py
│   ├── hypothesis_evaluation.py
│   ├── intent_producer.py
│   ├── knowledge
│   │   ├── __init__.py
│   │   └── news_index.py
│   ├── learning
│   │   ├── __init__.py
│   │   ├── learning_persistence.py
│   │   ├── lightweight_rl.py
│   │   └── slow_loop.py
│   ├── learning_gate.py
│   ├── learning_interface.py
│   ├── macro
│   │   ├── __init__.py
│   │   ├── forecaster.py
│   │   ├── hidden_state_detector.py
│   │   ├── latent_embedder.py
│   │   ├── macro_event_aligner.py
│   │   ├── regime_classifier.py
│   │   └── regime_engine.py
│   ├── market_context_memory.py
│   ├── mcp
│   │   ├── __init__.py
│   │   └── opennews.py
│   ├── meta
│   │   ├── __init__.py
│   │   ├── archetype_arena.py
│   │   ├── archetype_embedding_pipeline.py
│   │   ├── latent_regime_adapter.py
│   │   ├── meta_labeler.py
│   │   ├── strategy_synthesizer.py
│   │   ├── trader_archetypes.py
│   │   └── trader_pattern_selector.py
│   ├── meta_controller
│   │   ├── __init__.py
│   │   ├── allocation
│   │   │   ├── __init__.py
│   │   │   └── position_sizer.py
│   │   ├── config.py
│   │   ├── evaluation
│   │   │   ├── __init__.py
│   │   │   ├── confidence_engine.py
│   │   │   ├── debate_round.py
│   │   │   └── strategy_selector.py
│   │   ├── hot_path.py
│   │   ├── orchestrator.py
│   │   ├── perception
│   │   │   ├── __init__.py
│   │   │   └── regime_router.py
│   │   ├── policy
│   │   │   ├── __init__.py
│   │   │   ├── execution_policy.py
│   │   │   └── shadow_policy.py
│   │   └── runtime_adapter.py
│   ├── news
│   │   ├── __init__.py
│   │   ├── ner_filter.py
│   │   └── news_projection.py
│   ├── opponent_model
│   │   ├── __init__.py
│   │   ├── behavior_predictor.py
│   │   ├── crowd_density.py
│   │   └── strategy_detector.py
│   ├── orchestrators
│   │   ├── __init__.py
│   │   └── agent_orchestrator.py
│   ├── pgm_pgmpy.py
│   ├── plugins
│   │   ├── __init__.py
│   │   ├── footprint_delta
│   │   │   ├── __init__.py
│   │   │   └── v1.py
│   │   ├── liquidity_physics
│   │   │   ├── __init__.py
│   │   │   └── v1.py
│   │   ├── microstructure
│   │   │   ├── __init__.py
│   │   │   └── microstructure_v1.py
│   │   ├── news_reaction
│   │   │   ├── __init__.py
│   │   │   └── v1.py
│   │   ├── on_chain_pulse
│   │   │   ├── __init__.py
│   │   │   └── v1.py
│   │   ├── order_book_pressure
│   │   │   ├── __init__.py
│   │   │   └── v1.py
│   │   ├── orderflow_imbalance
│   │   │   ├── __init__.py
│   │   │   └── v1.py
│   │   ├── regime_classifier
│   │   │   ├── __init__.py
│   │   │   └── v1.py
│   │   ├── sentiment_aggregator
│   │   │   ├── __init__.py
│   │   │   └── v1.py
│   │   ├── trader_imitation
│   │   │   ├── __init__.py
│   │   │   └── v1.py
│   │   └── vpin_imbalance
│   │       ├── __init__.py
│   │       └── v1.py
│   ├── portfolio
│   │   ├── __init__.py
│   │   ├── allocator.py
│   │   ├── capital_scheduler.py
│   │   ├── correlation_engine.py
│   │   ├── exposure_manager.py
│   │   └── risk_parity.py
│   ├── research
│   │   ├── __init__.py
│   │   ├── autonomous_research_runtime.py
│   │   └── browser_research_service.py
│   ├── reward_tracking.py
│   ├── runtime_context.py
│   ├── runtime_context_builder.py
│   ├── signal_funnel.py
│   ├── signal_pipeline.py
│   ├── strategy_arena
│   │   ├── __init__.py
│   │   ├── arena_engine.py
│   │   ├── capital_allocator.py
│   │   ├── kill_underperformers.py
│   │   └── performance_tracker.py
│   ├── strategy_composer
│   │   ├── __init__.py
│   │   ├── atom_registry.py
│   │   ├── composer.py
│   │   ├── composition_validator.py
│   │   └── regime_fitness.py
│   ├── strategy_library
│   │   ├── __init__.py
│   │   ├── components.py
│   │   ├── composition.py
│   │   ├── decomposition.py
│   │   └── registry.py
│   ├── strategy_runtime
│   │   ├── __init__.py
│   │   ├── archetype_lifecycle.py
│   │   ├── conflict_resolver.py
│   │   ├── orchestrator.py
│   │   ├── regime_detector.py
│   │   ├── scheduler.py
│   │   └── state_machine.py
│   ├── svi_numpyro.py
│   ├── svi_pyro.py
│   ├── system
│   │   └── __init__.py
│   ├── trader_modeling
│   │   ├── __init__.py
│   │   ├── aggregator.py
│   │   ├── consumes.yaml
│   │   ├── content_parser.py
│   │   ├── crawler.py
│   │   ├── credibility_filter.py
│   │   ├── identity_resolver.py
│   │   ├── imitation.py
│   │   ├── meta_controller_bridge.py
│   │   ├── narrative_alignment.py
│   │   ├── observation.py
│   │   ├── performance_tracker.py
│   │   ├── philosophy_encoder.py
│   │   ├── strategy_extractor.py
│   │   ├── strategy_similarity_engine.py
│   │   ├── trader_behavior_tracker.py
│   │   ├── trader_clustering.py
│   │   ├── trader_pattern_extractor.py
│   │   ├── trader_profile_engine.py
│   │   └── trader_reliability_engine.py
│   └── uplift_causalml.py
├── interrupt
│   ├── __init__.py
│   ├── dispatcher.py
│   ├── interrupt_executor.py
│   ├── policy_cache.py
│   └── resolver.py
├── launcher_both.log
├── launcher_err.log
├── launcher_meme.log
├── launcher_out.log
├── learning_engine
│   ├── __init__.py
│   ├── analytics
│   │   ├── __init__.py
│   │   ├── backtest_scorer.py
│   │   ├── charts.py
│   │   ├── feature_importance.py
│   │   ├── ledger_query.py
│   │   ├── pnl_attribution.py
│   │   ├── regime_stats.py
│   │   └── rolling_stats.py
│   ├── attribution
│   │   ├── __init__.py
│   │   ├── decision_attributor.py
│   │   ├── edge_decay_tracker.py
│   │   ├── mistake_classifier.py
│   │   ├── outcome_linker.py
│   │   └── pnl_decomposer.py
│   ├── attribution.py
│   ├── calibration
│   │   ├── __init__.py
│   │   ├── coherence_calibrator.py
│   │   └── sim_realism_tracker.py
│   ├── causal
│   │   ├── __init__.py
│   │   └── probabilistic_model.py
│   ├── engine.py
│   ├── error_analysis.py
│   ├── feedback.py
│   ├── lanes
│   │   ├── __init__.py
│   │   ├── continual_distillation.py
│   │   ├── continual_learner.py
│   │   ├── experience_base.py
│   │   ├── federated.py
│   │   ├── federated_dispatcher.py
│   │   ├── federated_fedml.py
│   │   ├── federated_openfl.py
│   │   ├── federated_pysyft.py
│   │   ├── finrl_env.py
│   │   ├── online_feature_learner.py
│   │   ├── patch_outcome_feedback.py
│   │   ├── policy_distillation.py
│   │   ├── policy_distillation_torchrl.py
│   │   ├── ral.py
│   │   ├── reward_shaping.py
│   │   ├── self_learning_loop.py
│   │   └── weight_adjuster.py
│   ├── learning_audit_trails.py
│   ├── loops
│   │   ├── __init__.py
│   │   ├── builders.py
│   │   └── closed_loop.py
│   ├── memory.py
│   ├── meta_learning_loop.py
│   ├── model_evaluation.py
│   ├── model_promotion_workflow.py
│   ├── performance_analysis
│   │   ├── __init__.py
│   │   ├── alpha_decay.py
│   │   ├── archetype_evaluator.py
│   │   ├── execution_quality.py
│   │   ├── latency_impact.py
│   │   ├── pnl_attribution.py
│   │   ├── reward_shaping.py
│   │   └── slippage_analysis.py
│   ├── reward_system.py
│   ├── runtime_wiring.py
│   ├── status
│   │   ├── __init__.py
│   │   └── learning_progress_engine.py
│   ├── trader_abstraction
│   │   ├── __init__.py
│   │   ├── decay_weighter.py
│   │   ├── embedder.py
│   │   ├── encoder.py
│   │   ├── extractor.py
│   │   ├── normalizer.py
│   │   ├── pattern_encoder.py
│   │   ├── philosophy_encoder.py
│   │   └── strategy_synthesizer.py
│   ├── update_emitter.py
│   └── vector_memory
│       ├── __init__.py
│       ├── market_regime_embeddings.py
│       ├── narrative_embeddings.py
│       ├── strategy_embeddings.py
│       └── trader_embeddings.py
├── main.py
├── mind
│   ├── __init__.py
│   ├── beliefs.py
│   ├── charter.py
│   ├── custom_strategies.py
│   ├── custom_submissions
│   │   └── __init__.py
│   ├── engine.py
│   ├── execution_router.py
│   ├── fast_execute.py
│   ├── hypotheses.py
│   ├── intent.py
│   ├── intent_producer.py
│   ├── knowledge
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── drift_monitor.py
│   │   ├── edge_case_memory.py
│   │   ├── feedback_cleaner.py
│   │   ├── knowledge_validator.py
│   │   ├── language.py
│   │   ├── memory_index.py
│   │   ├── seed_traders.py
│   │   ├── source_conflict_graph.py
│   │   └── trader_knowledge.py
│   ├── knowledge.py
│   ├── knowledge_store.py
│   ├── observation.py
│   ├── order_manager.py
│   ├── plugins
│   │   ├── __init__.py
│   │   ├── arbitrage.py
│   │   ├── liquidity.py
│   │   ├── macro.py
│   │   ├── neuromorphic_signal.py
│   │   ├── regime.py
│   │   ├── sentiment.py
│   │   └── technical.py
│   ├── portfolio_manager.py
│   ├── risk_cache.py
│   ├── sources
│   │   ├── __init__.py
│   │   ├── ai_knowledge_input.py
│   │   ├── market_streams.py
│   │   ├── news_streams.py
│   │   ├── onchain_streams.py
│   │   ├── provider_base.py
│   │   ├── providers
│   │   │   ├── __init__.py
│   │   │   ├── api_sniffer.py
│   │   │   ├── code_search.py
│   │   │   ├── market_cex.py
│   │   │   ├── market_expanded.py
│   │   │   ├── news.py
│   │   │   ├── news_expanded.py
│   │   │   ├── onchain.py
│   │   │   └── sentiment.py
│   │   ├── rate_limiter.py
│   │   ├── rest_client.py
│   │   ├── sentiment_streams.py
│   │   ├── source_types.py
│   │   └── websocket_client.py
│   ├── strategies
│   │   └── __init__.py
│   └── strategy_arbiter.py
├── observability
│   ├── __init__.py
│   ├── alerts
│   │   ├── __init__.py
│   │   └── alert_engine.py
│   ├── dashboards
│   │   ├── __init__.py
│   │   └── cockpit_adapter.py
│   ├── exporters
│   │   ├── __init__.py
│   │   └── otlp_exporter.py
│   ├── logs
│   │   ├── __init__.py
│   │   └── log_sink.py
│   ├── metrics
│   │   ├── __init__.py
│   │   ├── metrics_registry.py
│   │   └── prometheus_exporter.py
│   ├── pipeline.py
│   ├── traces
│   │   ├── __init__.py
│   │   └── trace_manager.py
│   └── tracing
│       ├── __init__.py
│       └── trace_manager.py
├── operator_governance
│   ├── __init__.py
│   ├── authority_escalation.py
│   ├── charter.py
│   ├── consent_router.py
│   ├── engine.py
│   ├── governance_visibility.py
│   ├── manual_lockout.py
│   ├── operator_constitution.py
│   └── override_priority.py
├── opponent_model
│   ├── __init__.py
│   └── behavior_predictor.py
├── ownership_map.json
├── pyproject.toml
├── registry
│   ├── agent_context_keys.yaml
│   ├── agent_orchestrator.yaml
│   ├── agent_rationale_tags.yaml
│   ├── agent_state_keys.yaml
│   ├── agents.yaml
│   ├── alerts.yaml
│   ├── alt_data.yaml
│   ├── archetype_seeds.yaml
│   ├── authority_matrix.yaml
│   ├── budgets.yaml
│   ├── calibration.yaml
│   ├── confidence.yaml
│   ├── constraint_rules.yaml
│   ├── data_pipelines.yaml
│   ├── data_source_registry.yaml
│   ├── enforcement_policies.yaml
│   ├── engines.yaml
│   ├── execution_policies.yaml
│   ├── external_signal_trust.yaml
│   ├── external_sources.yaml
│   ├── feast
│   │   └── feature_store.yaml
│   ├── feature_flags.yaml
│   ├── governance_constitution.yaml
│   ├── governance_ruleset.yaml
│   ├── integrations.yaml
│   ├── latent_regime.yaml
│   ├── layers.yaml
│   ├── learning_config.yaml
│   ├── macro_regime.yaml
│   ├── meta_controller.yaml
│   ├── meta_learning.yaml
│   ├── modes.yaml
│   ├── operator.py
│   ├── operator.yaml
│   ├── opponent_behavior.yaml
│   ├── plugins.yaml
│   ├── portfolio_allocator.yaml
│   ├── position_sizer.yaml
│   ├── pressure.yaml
│   ├── regime.yaml
│   ├── regime_hysteresis.yaml
│   ├── reward_components.yaml
│   ├── reward_shaping.yaml
│   ├── risk.yaml
│   ├── simulation_config.yaml
│   ├── strategies
│   │   ├── definitions.yaml
│   │   ├── lifecycle.yaml
│   │   └── performance.yaml
│   ├── strategies.yaml
│   ├── telemetry.yaml
│   ├── trader_archetypes.yaml
│   └── versions.yaml
├── requirements-dev.txt
├── requirements-ml
├── requirements-windows.txt
├── requirements.txt
├── risk
│   ├── __init__.py
│   └── engine.py
├── run.ps1
├── runtime
│   ├── __init__.py
│   ├── authority.py
│   ├── authority_adapter.py
│   ├── boot_integration.py
│   ├── certification.py
│   ├── cognition_daemon.py
│   ├── cognition_scheduler.py
│   ├── cognitive_spine.py
│   ├── contracts.py
│   ├── convergence.py
│   ├── cross_bus_router.py
│   ├── event_fabric.py
│   ├── exchange_connector.py
│   ├── execution_lifecycle.py
│   ├── fabric
│   │   ├── __init__.py
│   │   ├── decision_pipeline.py
│   │   ├── event_loop.py
│   │   ├── execution_router.py
│   │   ├── fill_reconciler.py
│   │   ├── ingestion_bus.py
│   │   ├── market_feed.py
│   │   ├── risk_snapshotter.py
│   │   └── source_registry.py
│   ├── fault_handler.py
│   ├── governance
│   │   ├── __init__.py
│   │   ├── deterministic_arbiter.py
│   │   ├── enforcement_gate.py
│   │   ├── mode_propagator.py
│   │   └── runtime_enforcer.py
│   ├── governance_router.py
│   ├── kernel.py
│   ├── live_trading.py
│   ├── mcos_cognitive_spine.py
│   ├── memory_coordinator.py
│   ├── observability.py
│   ├── operational_readiness.py
│   ├── paper_trading.py
│   ├── projections.py
│   ├── reconciliation.py
│   ├── replay
│   │   ├── __init__.py
│   │   ├── divergence_detector.py
│   │   ├── replay_validator.py
│   │   ├── session_recorder.py
│   │   └── session_replayer.py
│   ├── replay_validator.py
│   ├── service_registry.py
│   ├── service_wiring.py
│   ├── subscriptions.py
│   ├── telemetry_aggregator.py
│   ├── tier_wiring.py
│   ├── unified_fabric
│   │   ├── __init__.py
│   │   ├── authority.py
│   │   ├── bridges.py
│   │   ├── contracts.py
│   │   ├── lineage.py
│   │   ├── persistence.py
│   │   ├── replay.py
│   │   ├── tracing.py
│   │   └── unified.py
│   ├── unified_kernel.py
│   └── writer.py
├── runtime_graph.json
├── scripts
│   ├── check_credentials.py
│   ├── diagnostics.py
│   ├── dix_cli.py
│   ├── generate_hash.py
│   ├── profile_hot_path.py
│   ├── run_chaos_day.py
│   ├── verify.py
│   └── windows
│       ├── install_desktop_shortcut.ps1
│       ├── install_desktop_shortcut_meme.ps1
│       ├── start_dixvision.bat
│       ├── start_dixvision_both.bat
│       ├── start_dixvision_meme.bat
│       └── stop_dixvision.bat
├── security
│   ├── __init__.py
│   ├── audit_trail.py
│   ├── authentication.py
│   ├── authorization.py
│   ├── encryption.py
│   ├── keyring_adapter.py
│   ├── operator.py
│   ├── secrets_manager.py
│   ├── wallet_connect.py
│   └── wallet_policy.py
├── sensory
│   ├── __init__.py
│   ├── alt
│   │   ├── __init__.py
│   │   └── contracts.py
│   ├── cognitive
│   │   ├── __init__.py
│   │   └── contracts.py
│   ├── dev
│   │   ├── __init__.py
│   │   └── contracts.py
│   ├── indicators
│   │   ├── __init__.py
│   │   └── technical.py
│   ├── neuromorphic
│   │   ├── __init__.py
│   │   ├── contracts.py
│   │   ├── dyon_anomaly.py
│   │   ├── governance_risk.py
│   │   ├── governance_risk_snn.py
│   │   ├── indira_signal.py
│   │   ├── nengo_cognitive.py
│   │   ├── neuro_prototype.py
│   │   ├── snn_lif.py
│   │   ├── snntorch_detector.py
│   │   └── spyke_encoder.py
│   ├── onchain
│   │   ├── __init__.py
│   │   ├── arkham.py
│   │   ├── contracts.py
│   │   ├── dune_adapter.py
│   │   ├── glassnode.py
│   │   └── nansen.py
│   ├── regulatory
│   │   ├── __init__.py
│   │   └── contracts.py
│   ├── trader_intelligence
│   │   ├── __init__.py
│   │   ├── discovery.py
│   │   ├── monitor.py
│   │   ├── pipeline.py
│   │   └── scorer.py
│   ├── voice
│   │   ├── __init__.py
│   │   ├── synthesizer.py
│   │   └── transcriber.py
│   └── web_autolearn
│       ├── __init__.py
│       ├── ai_filter.py
│       ├── contracts.py
│       ├── crawler.py
│       ├── crawler_firecrawl.py
│       ├── crawler_playwright.py
│       ├── crawler_scrapy.py
│       ├── curator.py
│       ├── extractors.py
│       ├── n8n_pipeline.py
│       ├── pending_buffer.py
│       ├── seeds.yaml
│       └── trader_intelligence
│           ├── __init__.py
│           ├── archetype_publisher.py
│           ├── behavior_analyzer.py
│           ├── contracts.py
│           ├── crawler.py
│           ├── knowledge_store.py
│           ├── performance_validator.py
│           ├── pipeline.py
│           ├── profile_extractor.py
│           └── source_registry.py
├── simulation
│   ├── __init__.py
│   ├── adversarial
│   │   ├── __init__.py
│   │   ├── flash_crash_synth.py
│   │   ├── jax_lob_sim.py
│   │   ├── liquidity_attacker.py
│   │   ├── manipulation_detector.py
│   │   └── stop_hunter.py
│   ├── backtester.py
│   ├── backtester_zipline.py
│   ├── crowd_density.py
│   ├── distributed_runner.py
│   ├── dominance_runtime.py
│   ├── drawdown_walk.py
│   ├── engine.py
│   ├── engines
│   │   ├── __init__.py
│   │   ├── adversarial_arena.py
│   │   ├── crowd_psychology.py
│   │   ├── exchange_failure.py
│   │   ├── latency_warfare.py
│   │   ├── liquidity_warfare.py
│   │   ├── macro_stress.py
│   │   ├── reflexive.py
│   │   ├── synthetic_market.py
│   │   └── volatility_cascade.py
│   ├── event_replayer.py
│   ├── evolution_sandbox.py
│   ├── fee_inversion.py
│   ├── fill_starvation.py
│   ├── flash_crash_synth.py
│   ├── governance_tester.py
│   ├── impact_feedback.py
│   ├── latency_jitter.py
│   ├── latency_model.py
│   ├── learning_validator.py
│   ├── liquidity_decay.py
│   ├── lob_component.py
│   ├── market_replay.py
│   ├── multi_agent_market.py
│   ├── mutation_tournament.py
│   ├── news_shock_sim.py
│   ├── oracle_lag.py
│   ├── order_book_decay.py
│   ├── parallel_runner.py
│   ├── partial_fill_chaos.py
│   ├── phase10_reflexive_depth.py
│   ├── phase10_scenario_engine.py
│   ├── phase12_verification.py
│   ├── reflexive_layer
│   │   ├── __init__.py
│   │   ├── crowd_density_sim.py
│   │   ├── impact_feedback.py
│   │   └── liquidity_decay.py
│   ├── reflexive_sim.py
│   ├── regime_switch_sim.py
│   ├── scenario_generator.py
│   ├── scenario_testing.py
│   ├── scoring_engine.py
│   ├── simulation_orchestrator.py
│   ├── slippage_walk.py
│   ├── stage8_orchestrator.py
│   ├── state_snapshot.py
│   ├── stop_hunter.py
│   └── strategy_arena
│       ├── __init__.py
│       ├── arena.py
│       ├── capital_allocator.py
│       ├── kill_underperformers.py
│       ├── promotion_engine.py
│       └── simulation_outcome.py
├── simulation_engine
│   ├── __init__.py
│   ├── adversary_agent.py
│   ├── latency_model.py
│   ├── liquidity_hunter.py
│   ├── runner.py
│   ├── slippage_model.py
│   └── spoofing_simulator.py
├── start.py
├── startup_test.py
├── state
│   ├── __init__.py
│   ├── analytics
│   │   ├── __init__.py
│   │   └── clickhouse_store.py
│   ├── cache
│   │   ├── __init__.py
│   │   └── redis_store.py
│   ├── cognition_persistence.py
│   ├── data_versioning
│   │   ├── __init__.py
│   │   ├── dataset_registry.py
│   │   ├── feature_store.py
│   │   └── market_snapshots.py
│   ├── databases
│   │   ├── __init__.py
│   │   ├── connection.py
│   │   ├── migrations.py
│   │   └── schema.py
│   ├── episodic_memory.py
│   ├── event_bus.py
│   ├── feature_store.py
│   ├── feature_store_delta.py
│   ├── feature_store_lakefs.py
│   ├── knowledge_graph.py
│   ├── knowledge_graph_causal.py
│   ├── knowledge_graph_queries.py
│   ├── knowledge_store.py
│   ├── knowledge_store_llamaindex.py
│   ├── knowledge_store_memgraph.py
│   ├── knowledge_store_memgraph_queries.py
│   ├── ledger
│   │   ├── __init__.py
│   │   ├── append.py
│   │   ├── async_writer.py
│   │   ├── bridge.py
│   │   ├── cold_store.py
│   │   ├── event_store.py
│   │   ├── event_types.py
│   │   ├── hash_chain.py
│   │   ├── hazard_stream.py
│   │   ├── hot_store.py
│   │   ├── indexer.py
│   │   ├── integrity.py
│   │   ├── lmdb_store.py
│   │   ├── mcos_event_store.py
│   │   ├── mcos_hash_chain.py
│   │   ├── mcos_stream_router.py
│   │   ├── mcos_writer.py
│   │   ├── postgres_store.py
│   │   ├── projector.py
│   │   ├── questdb_store.py
│   │   ├── reader.py
│   │   ├── reconstructor.py
│   │   ├── risk_resolution_log.py
│   │   ├── snapshot_manager.py
│   │   ├── snapshots.py
│   │   ├── stream_router.py
│   │   └── writer.py
│   ├── market_state.py
│   ├── memory
│   │   ├── __init__.py
│   │   ├── compression.py
│   │   ├── contracts.py
│   │   ├── identity.py
│   │   ├── index.py
│   │   ├── replay.py
│   │   ├── stores
│   │   │   ├── __init__.py
│   │   │   ├── governance.py
│   │   │   ├── runtime_events.py
│   │   │   ├── strategy.py
│   │   │   └── trader.py
│   │   ├── timeline.py
│   │   └── unified.py
│   ├── memory_tensor
│   │   ├── __init__.py
│   │   ├── chroma_store.py
│   │   ├── contracts.py
│   │   ├── embedder.py
│   │   ├── episodic.py
│   │   ├── lancedb_store.py
│   │   ├── memory_orchestrator.py
│   │   ├── meta_memory.py
│   │   ├── procedural.py
│   │   ├── regret
│   │   │   ├── __init__.py
│   │   │   ├── almost_trades.py
│   │   │   ├── missed_opportunity.py
│   │   │   └── regret_log.py
│   │   ├── semantic.py
│   │   ├── semantic_milvus.py
│   │   ├── semantic_qdrant.py
│   │   ├── semantic_weaviate.py
│   │   └── trader_patterns
│   │       ├── __init__.py
│   │       ├── archetype_store.py
│   │       ├── atom_store.py
│   │       ├── pattern_store.py
│   │       └── profile_store.py
│   ├── projectors
│   │   ├── __init__.py
│   │   ├── governance_state.py
│   │   ├── hazard_state.py
│   │   ├── market_state.py
│   │   ├── portfolio_state.py
│   │   └── system_state.py
│   ├── snapshots
│   │   ├── __init__.py
│   │   ├── checkpoint_index.py
│   │   └── snapshot_manager.py
│   ├── state_sync.py
│   ├── telemetry
│   │   ├── __init__.py
│   │   └── cognitive_telemetry.py
│   └── timeseries
│       ├── __init__.py
│       ├── influxdb_store.py
│       └── timescale_store.py
├── system
│   ├── __init__.py
│   ├── audit_logger.py
│   ├── autonomy.py
│   ├── causal_inference_engine.py
│   ├── config.py
│   ├── config_schema.py
│   ├── data_quality.py
│   ├── explainability_engine.py
│   ├── fast_risk_cache.py
│   ├── health_monitor.py
│   ├── kill_switch.py
│   ├── locale.py
│   ├── logger.py
│   ├── metrics.py
│   ├── power_manager.py
│   ├── resilience.py
│   ├── resource_arbiter.py
│   ├── scheduler.py
│   ├── snapshots.py
│   ├── state.py
│   ├── state_persistence.py
│   ├── state_reconstructor.py
│   └── time_source.py
├── system_engine
│   ├── __init__.py
│   ├── adversarial
│   │   ├── __init__.py
│   │   ├── bot_classifier.py
│   │   ├── manipulation_detector.py
│   │   └── trap_detector.py
│   ├── authority
│   │   ├── __init__.py
│   │   └── matrix.py
│   ├── backtest_ingest
│   │   ├── __init__.py
│   │   └── internal
│   │       ├── __init__.py
│   │       └── deterministic.py
│   ├── codec
│   │   ├── __init__.py
│   │   └── json_codec.py
│   ├── config.py
│   ├── coupling
│   │   ├── __init__.py
│   │   ├── hazard_throttle.py
│   │   ├── hazard_throttle_adapter.py
│   │   └── risk_snapshot_throttle.py
│   ├── credentials
│   │   ├── __init__.py
│   │   ├── crypto.py
│   │   ├── dotenv_io.py
│   │   ├── manifest.py
│   │   ├── status.py
│   │   ├── storage.py
│   │   ├── totp.py
│   │   ├── vault_backend.py
│   │   └── verifiers.py
│   ├── data_quality.py
│   ├── dev_logger.py
│   ├── engine.py
│   ├── error_telemetry.py
│   ├── file_watcher.py
│   ├── hazard_sensors
│   │   ├── __init__.py
│   │   ├── clock_drift.py
│   │   ├── exchange_unreachable.py
│   │   ├── heartbeat_missed.py
│   │   ├── latency_spike.py
│   │   ├── market_anomaly.py
│   │   ├── memory_overflow.py
│   │   ├── neuromorphic_detector.py
│   │   ├── news_shock.py
│   │   ├── order_flood.py
│   │   ├── risk_snapshot_stale.py
│   │   ├── runtime_breaker_open.py
│   │   ├── sensor_array.py
│   │   ├── stale_data.py
│   │   ├── system_anomaly.py
│   │   └── ws_timeout.py
│   ├── health_monitors
│   │   ├── __init__.py
│   │   ├── api_changelogs.py
│   │   ├── github_trending.py
│   │   ├── heartbeat.py
│   │   ├── liveness.py
│   │   ├── repo_discovery.py
│   │   ├── stack_overflow.py
│   │   └── watchdog.py
│   ├── logging.py
│   ├── metrics
│   │   ├── __init__.py
│   │   └── exporter.py
│   ├── process_monitor.py
│   ├── scvs
│   │   ├── __init__.py
│   │   ├── ai_validator.py
│   │   ├── consumption_tracker.py
│   │   ├── fallback_audit.py
│   │   ├── lint.py
│   │   ├── schema_guard.py
│   │   ├── source_manager.py
│   │   └── source_registry.py
│   ├── state
│   │   ├── __init__.py
│   │   ├── anomaly_detector.py
│   │   ├── drift_monitor.py
│   │   ├── homeostasis.py
│   │   ├── kill_switch_runtime.py
│   │   ├── runtime_guardian.py
│   │   └── system_state.py
│   ├── streaming
│   │   ├── __init__.py
│   │   ├── event_fabric.py
│   │   ├── faust_bus.py
│   │   ├── kafka_bus.py
│   │   ├── nats_bus.py
│   │   ├── pulsar_bus.py
│   │   └── streamz_cep.py
│   └── tracing
│       ├── __init__.py
│       ├── pixie_tracer.py
│       └── tracer.py
├── system_governance
│   ├── __init__.py
│   ├── charter.py
│   ├── contract_integrity.py
│   ├── convergence_monitor.py
│   ├── dependency_validator.py
│   ├── engine.py
│   ├── replay_integrity.py
│   ├── runtime_consistency.py
│   └── topology_guard.py
├── system_monitor
│   ├── __init__.py
│   ├── anomaly_models.py
│   ├── charter.py
│   ├── checks
│   │   ├── __init__.py
│   │   ├── clock_sync_check.py
│   │   ├── connectivity_check.py
│   │   ├── data_integrity_check.py
│   │   ├── latency_check.py
│   │   └── process_health_check.py
│   ├── dead_man.py
│   ├── dyon_engine.py
│   ├── emitters
│   │   ├── __init__.py
│   │   └── hazard_event_emitter.py
│   ├── engine.py
│   ├── hazard_bus.py
│   ├── hazard_detector.py
│   ├── hazard_engine.py
│   ├── heartbeat_monitor.py
│   ├── latency_guard.py
│   ├── repo_awareness.py
│   ├── runtime_awareness.py
│   ├── telemetry_ingest.py
│   └── weekly_scout.py
├── temp_update_app.py
├── test_out.txt
├── test_output.txt
├── tests
│   ├── __init__.py
│   ├── bench
│   │   ├── __init__.py
│   │   ├── test_lob_performance_bench.py
│   │   ├── test_orderbook_jit_bench.py
│   │   ├── test_slippage_jit_bench.py
│   │   └── test_snn_backend_comparison.py
│   ├── conftest.py
│   ├── dashboard_backend
│   │   ├── __init__.py
│   │   └── control_plane
│   │       ├── __init__.py
│   │       ├── conftest.py
│   │       ├── test_decision_trace.py
│   │       ├── test_engine_status_grid.py
│   │       ├── test_memecoin_control_panel.py
│   │       ├── test_mode_control_bar.py
│   │       ├── test_router.py
│   │       └── test_strategy_lifecycle_panel.py
│   ├── drift_killers
│   │   ├── test_behavior_diff.py
│   │   ├── test_invariants_coherence.py
│   │   ├── test_no_hidden_channels.py
│   │   ├── test_registry_lock.py
│   │   ├── test_replay_gate.py
│   │   └── test_snapshot_boundary.py
│   ├── integration
│   │   ├── __init__.py
│   │   └── test_full_pipeline.py
│   ├── sensory
│   │   ├── __init__.py
│   │   ├── alt
│   │   │   ├── __init__.py
│   │   │   └── test_contracts.py
│   │   ├── cognitive
│   │   │   ├── __init__.py
│   │   │   └── test_contracts.py
│   │   ├── dev
│   │   │   ├── __init__.py
│   │   │   └── test_contracts.py
│   │   ├── neuromorphic
│   │   │   ├── __init__.py
│   │   │   ├── test_contracts.py
│   │   │   ├── test_dyon_anomaly.py
│   │   │   ├── test_governance_risk.py
│   │   │   └── test_indira_signal.py
│   │   ├── onchain
│   │   │   ├── __init__.py
│   │   │   ├── test_contracts.py
│   │   │   └── test_dune_adapter.py
│   │   ├── regulatory
│   │   │   ├── __init__.py
│   │   │   └── test_contracts.py
│   │   └── web_autolearn
│   │       ├── __init__.py
│   │       ├── test_ai_filter.py
│   │       ├── test_contracts.py
│   │       ├── test_crawler.py
│   │       ├── test_curator.py
│   │       ├── test_pending_buffer.py
│   │       └── test_seeds_yaml.py
│   ├── test_adapter_registry.py
│   ├── test_adapter_registry_lazy_uniswapx.py
│   ├── test_adapter_router.py
│   ├── test_adversarial_agent.py
│   ├── test_all.py
│   ├── test_alpaca_adapter.py
│   ├── test_alpha_decay.py
│   ├── test_anytrading_env.py
│   ├── test_approval_edge.py
│   ├── test_approval_projection.py
│   ├── test_approval_queue.py
│   ├── test_archetype_embedding_pipeline.py
│   ├── test_archetype_lifecycle.py
│   ├── test_async_ledger_writer.py
│   ├── test_audit_ledger_checkpoint_saver.py
│   ├── test_audit_p0_2_sqlite_ledger_reader.py
│   ├── test_audit_p0_3_ledger_boot.py
│   ├── test_audit_p0_4_durable_caps.py
│   ├── test_audit_p1_1_decision_signer_wiring.py
│   ├── test_audit_p1_2_kill_switch_protocol.py
│   ├── test_audit_p1_3_system_engine_process.py
│   ├── test_audit_p1_5_missing_endpoints.py
│   ├── test_audit_p1_7_learning_override_route.py
│   ├── test_audit_p2_1_backtest_endpoint.py
│   ├── test_audit_p2_2_hazard_forward.py
│   ├── test_audit_wire_3_feedback.py
│   ├── test_audit_wire_4_sensor_array.py
│   ├── test_audit_wire_5_runtime_context.py
│   ├── test_authority_lint.py
│   ├── test_authority_lint_b23.py
│   ├── test_authority_matrix.py
│   ├── test_authority_symmetry.py
│   ├── test_autohedge_patterns.py
│   ├── test_b30_belief_state_unify.py
│   ├── test_backtest_result.py
│   ├── test_backtest_scorer.py
│   ├── test_backtester.py
│   ├── test_base_env.py
│   ├── test_binance_adapter.py
│   ├── test_binance_public_ws.py
│   ├── test_bls_http_parser.py
│   ├── test_bls_http_pump.py
│   ├── test_build_directive.py
│   ├── test_c1_uniswapx_credential_pipeline.py
│   ├── test_c4_sensory_scvs_registry.py
│   ├── test_caches.py
│   ├── test_causal_dowhy.py
│   ├── test_causal_graph.py
│   ├── test_causal_graph_learning.py
│   ├── test_chroma_store.py
│   ├── test_circuit_breaker.py
│   ├── test_cli_commands.py
│   ├── test_closed_learning_loop.py
│   ├── test_cmaes_optimizer.py
│   ├── test_codebase_intelligence.py
│   ├── test_codegen_pydantic_to_ts.py
│   ├── test_codeql_analyzer.py
│   ├── test_cognitive_approvals_routes.py
│   ├── test_cognitive_chat_graph.py
│   ├── test_cognitive_chat_runtime.py
│   ├── test_cognitive_development.py
│   ├── test_cognitive_governance.py
│   ├── test_cognitive_router.py
│   ├── test_cognitive_routes_extracted.py
│   ├── test_coherence_belief_state.py
│   ├── test_coherence_calibrator.py
│   ├── test_coherence_performance_pressure.py
│   ├── test_coindesk_rss_parser.py
│   ├── test_coindesk_rss_pump.py
│   ├── test_config_schema.py
│   ├── test_constraint_engine.py
│   ├── test_continual_learner.py
│   ├── test_credentials_dotenv_io.py
│   ├── test_credentials_manifest.py
│   ├── test_credentials_route.py
│   ├── test_credentials_set_route.py
│   ├── test_credentials_storage.py
│   ├── test_credentials_verifiers.py
│   ├── test_credentials_verify_route.py
│   ├── test_crew_strategy_council.py
│   ├── test_critique_loop.py
│   ├── test_crossover_operators.py
│   ├── test_crowd_density_sim.py
│   ├── test_dash_meme_mount.py
│   ├── test_dashboard2026_routes.py
│   ├── test_dashboard_projections.py
│   ├── test_dashboard_stream_sse.py
│   ├── test_data_quality.py
│   ├── test_debate_graph.py
│   ├── test_debate_round.py
│   ├── test_decision_signer.py
│   ├── test_decision_trace.py
│   ├── test_decision_trace_why_layer.py
│   ├── test_dev_logger.py
│   ├── test_diag_arviz.py
│   ├── test_distributed_runner.py
│   ├── test_drawdown_walk_sim.py
│   ├── test_drift_oracle.py
│   ├── test_dspy_optimizer.py
│   ├── test_elegantrl_sandbox.py
│   ├── test_embedder.py
│   ├── test_enforcement_facade.py
│   ├── test_engine_contracts.py
│   ├── test_error_telemetry.py
│   ├── test_event_fabric.py
│   ├── test_event_provenance.py
│   ├── test_event_replayer.py
│   ├── test_evolution_gym_env.py
│   ├── test_evolution_pipeline.py
│   ├── test_evolution_sandbox.py
│   ├── test_execution_engine.py
│   ├── test_execution_engine_learning_loop.py
│   ├── test_execution_engine_throttle.py
│   ├── test_execution_gate.py
│   ├── test_execution_hot_path.py
│   ├── test_execution_intent.py
│   ├── test_execution_intent_hash_property.py
│   ├── test_execution_lifecycle.py
│   ├── test_execution_quality.py
│   ├── test_execution_runtime_monitor.py
│   ├── test_experiment_tracking.py
│   ├── test_external_signal_trust.py
│   ├── test_extractors.py
│   ├── test_fast_risk_cache_staleness.py
│   ├── test_fast_structs.py
│   ├── test_faust_bus.py
│   ├── test_feature_extractor.py
│   ├── test_feature_store.py
│   ├── test_federated_learning.py
│   ├── test_fedml.py
│   ├── test_fee_inversion_sim.py
│   ├── test_feeds_routes_extracted.py
│   ├── test_file_watcher.py
│   ├── test_fill_starvation_sim.py
│   ├── test_finrl_env.py
│   ├── test_firecrawl_crawler.py
│   ├── test_flash_crash_synth_sim.py
│   ├── test_footprint_delta_plugin.py
│   ├── test_fred_http_parser.py
│   ├── test_fred_http_pump.py
│   ├── test_full_stack_e2e.py
│   ├── test_governance.py
│   ├── test_governance_alignment.py
│   ├── test_governance_control_plane.py
│   ├── test_governance_fail_closed.py
│   ├── test_governance_risk_snn.py
│   ├── test_guidance_adapter.py
│   ├── test_harness_approver_gate.py
│   ├── test_hazard_flow.py
│   ├── test_hazard_sensors.py
│   ├── test_hazard_throttle.py
│   ├── test_hazard_throttle_adapter.py
│   ├── test_health_monitors.py
│   ├── test_helius_adapter.py
│   ├── test_hmm_hmmlearn.py
│   ├── test_hte_econml.py
│   ├── test_http_chat_transport.py
│   ├── test_hummingbot_adapter.py
│   ├── test_hydra_config.py
│   ├── test_ibkr_adapter.py
│   ├── test_immutable_core_axioms.py
│   ├── test_impact_feedback_sim.py
│   ├── test_indira_intelligence.py
│   ├── test_instructor_adapter.py
│   ├── test_intelligence_engine.py
│   ├── test_intelligence_engine_wave1.py
│   ├── test_invariant_prover.py
│   ├── test_invariant_verifier.py
│   ├── test_jaeger_tracer.py
│   ├── test_jax_lob_sim.py
│   ├── test_kafka_bus.py
│   ├── test_kill_switch.py
│   ├── test_knowledge_graph.py
│   ├── test_knowledge_store.py
│   ├── test_lancedb_store.py
│   ├── test_latency.py
│   ├── test_latency_jitter_sim.py
│   ├── test_latency_model.py
│   ├── test_lava_patterns.py
│   ├── test_learning_evolution_freeze.py
│   ├── test_learning_interface.py
│   ├── test_ledger_hash_chain.py
│   ├── test_ledger_persistence.py
│   ├── test_ledger_query.py
│   ├── test_ledger_snapshots.py
│   ├── test_ledger_tiers.py
│   ├── test_liquidity_decay_sim.py
│   ├── test_liquidity_physics_plugin.py
│   ├── test_litellm_router.py
│   ├── test_llamaindex_store.py
│   ├── test_lob_component.py
│   ├── test_local_transport.py
│   ├── test_lp_agent.py
│   ├── test_macro_agent.py
│   ├── test_macro_regime_engine.py
│   ├── test_market_data_aggregator.py
│   ├── test_memgraph_store.py
│   ├── test_memory_tensor_contracts.py
│   ├── test_memory_tensor_episodic.py
│   ├── test_memory_tensor_semantic.py
│   ├── test_meta_controller_confidence_engine.py
│   ├── test_meta_controller_hot_path.py
│   ├── test_meta_controller_orchestrator.py
│   ├── test_meta_controller_policy.py
│   ├── test_meta_controller_position_sizer.py
│   ├── test_meta_controller_regime_router.py
│   ├── test_meta_controller_runtime_adapter.py
│   ├── test_metrics_exporter.py
│   ├── test_milvus_store.py
│   ├── test_mode_effects.py
│   ├── test_multiagent_env.py
│   ├── test_mushroom_sandbox.py
│   ├── test_mutation_operators.py
│   ├── test_nats_bus.py
│   ├── test_nengo_cognitive.py
│   ├── test_ner_filter.py
│   ├── test_neuro_prototype.py
│   ├── test_neuromorphic.py
│   ├── test_neuromorphic_triad.py
│   ├── test_new_modules.py
│   ├── test_news_fanout.py
│   ├── test_news_feed_runner.py
│   ├── test_news_knowledge_index.py
│   ├── test_news_projection.py
│   ├── test_news_reaction_plugin.py
│   ├── test_news_shock_sensor.py
│   ├── test_news_shock_sim.py
│   ├── test_on_chain_pulse_plugin.py
│   ├── test_online_feature_learner.py
│   ├── test_opa_policy.py
│   ├── test_openfl.py
│   ├── test_openhands_sandbox.py
│   ├── test_opennews_mcp.py
│   ├── test_operator_attention.py
│   ├── test_operator_authority.py
│   ├── test_operator_dashboard.py
│   ├── test_operator_routes_extracted.py
│   ├── test_opponent_behavior_predictor.py
│   ├── test_oracle_lag_sim.py
│   ├── test_order_book_decay_sim.py
│   ├── test_order_book_pressure_plugin.py
│   ├── test_orderbook.py
│   ├── test_orderflow_imbalance_plugin.py
│   ├── test_orjson_codec.py
│   ├── test_oss_batch2.py
│   ├── test_oss_batch3.py
│   ├── test_oss_batch4.py
│   ├── test_oss_integrations.py
│   ├── test_oss_wiring.py
│   ├── test_outlines_adapter.py
│   ├── test_p0a_loops_wiring.py
│   ├── test_paper_broker_s2.py
│   ├── test_paper_s5_signal_trust_cap.py
│   ├── test_paper_s6_source_trust_promotion.py
│   ├── test_paper_s7_decision_trace_audit.py
│   ├── test_partial_fill_chaos_sim.py
│   ├── test_patch_approval_bridge_gates.py
│   ├── test_patch_pipeline.py
│   ├── test_patch_pipeline_orchestrator.py
│   ├── test_pgm_pgmpy.py
│   ├── test_phase0_attestation.py
│   ├── test_phase1_b01_governance_hazard_sink.py
│   ├── test_phase5_closed_loop.py
│   ├── test_phase6_p1_1_governance_trust_cap.py
│   ├── test_phase6_p1_2_observability_extras.py
│   ├── test_phase6_p1_3_dormant_health.py
│   ├── test_playwright_crawler.py
│   ├── test_plugin_routes.py
│   ├── test_pnl_attribution.py
│   ├── test_polars_feature_importance.py
│   ├── test_polars_pnl_attribution.py
│   ├── test_polars_regime_stats.py
│   ├── test_policy_decision_table.py
│   ├── test_policy_distillation.py
│   ├── test_policy_drift_sentry.py
│   ├── test_policy_hash_anchor.py
│   ├── test_portfolio_allocator.py
│   ├── test_portfolio_exposure_manager.py
│   ├── test_pr_dev_a_development_mode.py
│   ├── test_pr_dev_b_indira_unblock.py
│   ├── test_pr_dev_c_dyon_unblock.py
│   ├── test_pr_z1_harden04_conditional_relax.py
│   ├── test_pr_z2_wire_builders.py
│   ├── test_process_monitor.py
│   ├── test_projection_unification.py
│   ├── test_promotion_gates.py
│   ├── test_proposal_parser.py
│   ├── test_proto_python_parity.py
│   ├── test_protos_compile.py
│   ├── test_provider_transports.py
│   ├── test_pulsar_bus.py
│   ├── test_pumpfun_ws.py
│   ├── test_pyproject_runtime_deps.py
│   ├── test_pysyft_federated.py
│   ├── test_qdrant_store.py
│   ├── test_quantitative_evaluator.py
│   ├── test_r4_constraint_engine_no_cycle.py
│   ├── test_r5_dead_file_workflow_callers.py
│   ├── test_raydium_pools.py
│   ├── test_reconciliation.py
│   ├── test_redis_store.py
│   ├── test_regime_classifier_plugin.py
│   ├── test_regime_switch_sim.py
│   ├── test_registry_driven_chat_model.py
│   ├── test_replay.py
│   ├── test_replay_determinism.py
│   ├── test_replay_determinism_property.py
│   ├── test_retry_mixin.py
│   ├── test_retry_mixin_tenacity.py
│   ├── test_reward_shaping.py
│   ├── test_rllib_trainer.py
│   ├── test_rolling_stats.py
│   ├── test_round10_fixes.py
│   ├── test_route_registrar.py
│   ├── test_rulegraph_patch_evaluator.py
│   ├── test_runtime_activation.py
│   ├── test_runtime_authority.py
│   ├── test_runtime_capability.py
│   ├── test_runtime_context_builder.py
│   ├── test_runtime_fabric.py
│   ├── test_runtime_registrar.py
│   ├── test_runtime_routes_extracted.py
│   ├── test_runtime_topology.py
│   ├── test_rust_revival_reminder.py
│   ├── test_sample_factory_sandbox.py
│   ├── test_scalper_agent.py
│   ├── test_scrapy_crawler.py
│   ├── test_scvs_phase1.py
│   ├── test_scvs_phase2.py
│   ├── test_scvs_phase3.py
│   ├── test_semantic_kernel_bridge.py
│   ├── test_semgrep_scanner.py
│   ├── test_semi_auto_and_routing.py
│   ├── test_sentiment_aggregator_plugin.py
│   ├── test_signal_pipeline.py
│   ├── test_signal_trust.py
│   ├── test_simulation_engine.py
│   ├── test_simulation_parallel_runner.py
│   ├── test_slippage_determinism_property.py
│   ├── test_slippage_model.py
│   ├── test_slippage_walk_sim.py
│   ├── test_slow_loop_learner.py
│   ├── test_snapshots.py
│   ├── test_snn_lif.py
│   ├── test_snntorch_detector.py
│   ├── test_solana_native.py
│   ├── test_spyke_encoder.py
│   ├── test_state_reconstructor.py
│   ├── test_static_analysis_ts.py
│   ├── test_stop_hunter_sim.py
│   ├── test_strategic_execution.py
│   ├── test_strategy_arena_arena.py
│   ├── test_strategy_arena_kill_underperformers.py
│   ├── test_strategy_arena_promotion_engine.py
│   ├── test_strategy_chromosome.py
│   ├── test_strategy_composition.py
│   ├── test_strategy_library.py
│   ├── test_strategy_registry.py
│   ├── test_strategy_runtime.py
│   ├── test_streamz_cep.py
│   ├── test_stress_fred_parser_fuzz.py
│   ├── test_stress_mode_effects.py
│   ├── test_stress_strategy_registry.py
│   ├── test_structural_evolution_loop.py
│   ├── test_structured_logging.py
│   ├── test_svi_numpyro.py
│   ├── test_svi_pyro.py
│   ├── test_swing_agent.py
│   ├── test_system_config.py
│   ├── test_system_intent.py
│   ├── test_system_state.py
│   ├── test_technical_indicators.py
│   ├── test_tianshou_sandbox.py
│   ├── test_tier1_strategy_composer.py
│   ├── test_tier1_trader_modeling.py
│   ├── test_tier2_vector_memory.py
│   ├── test_tier3_memecoin.py
│   ├── test_tier3_persistence.py
│   ├── test_tier4_cockpit.py
│   ├── test_tier4_simulation.py
│   ├── test_tier4_trader_intelligence.py
│   ├── test_tier_a_b.py
│   ├── test_tier_c_batch.py
│   ├── test_tier_c_batch2.py
│   ├── test_tier_c_batch3.py
│   ├── test_tier_c_batch4.py
│   ├── test_tier_c_missing.py
│   ├── test_tier_i_remaining.py
│   ├── test_tier_wiring.py
│   ├── test_time_source.py
│   ├── test_torch_tier_isolation.py
│   ├── test_torchrl_policy.py
│   ├── test_total_validation_topology_drift.py
│   ├── test_tracer.py
│   ├── test_trader_archetypes_registry.py
│   ├── test_trader_imitation_plugin.py
│   ├── test_trader_intelligence_contracts.py
│   ├── test_trader_modeling_aggregator.py
│   ├── test_trader_modeling_observation.py
│   ├── test_trader_pattern_selector.py
│   ├── test_trading_agents_bridge.py
│   ├── test_tradingview_alert_endpoint.py
│   ├── test_tradingview_alert_parser.py
│   ├── test_tradingview_ideas_parser.py
│   ├── test_typed_ai.py
│   ├── test_ui_dashboard_actions.py
│   ├── test_ui_dashboard_routes.py
│   ├── test_ui_server.py
│   ├── test_ui_server_audit_wiring.py
│   ├── test_uniswapx_adapter.py
│   ├── test_uniswapx_quote.py
│   ├── test_uniswapx_signer.py
│   ├── test_update_validator.py
│   ├── test_uplift_causalml.py
│   ├── test_vpin_imbalance_plugin.py
│   ├── test_weaviate_store.py
│   ├── test_weight_adjuster.py
│   ├── test_windows_launcher.py
│   └── unit
│       ├── __init__.py
│       ├── test_governance.py
│       ├── test_kernel.py
│       ├── test_ledger.py
│       └── test_mind.py
├── tools
│   ├── __init__.py
│   ├── authority_lint.py
│   ├── authority_matrix_lint.py
│   ├── build_status_generator.py
│   ├── cli.py
│   ├── cli_dashboard.py
│   ├── codebase_intelligence.py
│   ├── codegen
│   │   ├── __init__.py
│   │   └── pydantic_to_ts.py
│   ├── codeql_analyzer.py
│   ├── config_validator.py
│   ├── constraint_lint.py
│   ├── contract_diff.py
│   ├── enforce.py
│   ├── enforcement_matrix.py
│   ├── gen_protos.sh
│   ├── graph_visualizer.py
│   ├── hydra_config.py
│   ├── invariant_prover.py
│   ├── jaeger_tracer.py
│   ├── operator_terminal.py
│   ├── replay_validator.py
│   ├── runtime_activation.py
│   ├── runtime_capability.py
│   ├── runtime_topology.py
│   ├── rust_bridge
│   │   ├── Cargo.toml
│   │   ├── README.md
│   │   └── src
│   │       ├── bin
│   │       │   └── fast_risk_cache_bench.rs
│   │       └── lib.rs
│   ├── rust_revival_reminder.py
│   ├── sandbox_runner.py
│   ├── scvs_lint.py
│   ├── semgrep_scanner.py
│   └── total_validation.py
├── trader_modeling
│   ├── __init__.py
│   ├── archetype_publisher.py
│   ├── behavioral_classifier.py
│   ├── profile_extractor.py
│   └── trader_modeling_runtime.py
├── trading.py
├── translation
│   ├── __init__.py
│   ├── audit_log.py
│   ├── audit_writer.py
│   ├── intent_models.py
│   ├── intent_to_patch.py
│   ├── mappings.yaml
│   ├── round_trip.py
│   ├── round_trip_validator.py
│   ├── translator.py
│   └── validator.py
├── ui
│   ├── __init__.py
│   ├── _ledger_boot.py
│   ├── authority_routes.py
│   ├── cockpit_routes.py
│   ├── cockpit_routes_integration_guide.py
│   ├── cockpit_routes_phase11_1.py
│   ├── cognitive_chat_runtime.py
│   ├── cognitive_governance_routes.py
│   ├── cognitive_report_routes.py
│   ├── cognitive_research_routes.py
│   ├── cognitive_routes.py
│   ├── cognitive_runtime_routes.py
│   ├── cognitive_stream_routes.py
│   ├── dashboard_projection_routes.py
│   ├── dashboard_routes.py
│   ├── evolution_routes.py
│   ├── execution_routes.py
│   ├── fabric_routes.py
│   ├── feeds
│   │   ├── __init__.py
│   │   ├── binance_public_ws.py
│   │   ├── bls_http.py
│   │   ├── coindesk_rss.py
│   │   ├── consumes.yaml
│   │   ├── fred_http.py
│   │   ├── news_fanout.py
│   │   ├── news_runner.py
│   │   ├── pumpfun_runner.py
│   │   ├── pumpfun_ws.py
│   │   ├── raydium_pools.py
│   │   ├── raydium_runner.py
│   │   ├── runner.py
│   │   ├── solana_launch_ws.py
│   │   ├── tradingview_alert.py
│   │   └── tradingview_ideas.py
│   ├── feeds_routes.py
│   ├── governance_hardening_routes.py
│   ├── governance_routes.py
│   ├── harness
│   │   ├── __init__.py
│   │   ├── background_task_manager.py
│   │   ├── boot_manager.py
│   │   ├── route_registrar.py
│   │   ├── runtime_registrar.py
│   │   └── source_trust_replay.py
│   ├── memory_routes.py
│   ├── mock_feed_replacement.py
│   ├── operator_controls.py
│   ├── operator_routes.py
│   ├── paper_trading_routes.py
│   ├── plugin_routes.py
│   ├── portfolio_sync.py
│   ├── runtime_routes.py
│   ├── server.py
│   ├── simulation_routes.py
│   ├── state_projection.py
│   ├── static
│   │   ├── app.js
│   │   ├── index.html
│   │   └── styles.css
│   └── websocket_gateway.py
└── windows
    ├── DIX-VISION.spec
    ├── installer
    │   ├── env_setup.ps1
    │   ├── registry.ps1
    │   ├── setup.ps1
    │   └── uninstall.ps1
    ├── launcher_entry.py
    ├── service
    │   ├── nssm_config.xml
    │   ├── recovery.ps1
    │   ├── service_wrapper.py
    │   ├── watchdog.ps1
    │   └── winsw_config.xml
    ├── tray
    │   ├── tray_actions.py
    │   ├── tray_app.py
    │   └── tray_ui.py
    └── updater
        ├── rollback_update.py
        ├── update_engine.py
        └── version_check.py
```

## Build phasing (Build Compiler Spec §2 — locked sequence)

The phase-by-phase delivery is in `build_plan.md`. Updated to integrate
v3 (Tier 1 follow-ons + Phase 10):

| Phase / Step | Scope | Status |
|---|---|---|
| Phase 0 | Bootstrap core (contracts, ledger, registry, time, event bus) | DONE (PR #14, #15, #23) |
| Phase 1 | Governance core (GOV-CP-01..07, Mode FSM, OperatorBridge) | DONE (PR #28) |
| Phase 2 | Execution core (adapters, lifecycle FSM, hot path, runtime monitor) | DONE (PR #29) |
| Phase 3 | Indira (signal_pipeline, microstructure, strategy_runtime, learning_interface) | DONE (PR #30, #31) |
| Phase 4 | Dyon (HAZ-01..12, health monitors, system state, patch pipeline) | DONE (PR #32, #33) |
| Phase 5 | Learning + Evolution closed loop | DONE (PR #34) |
| **Phase 6** | **Dashboard OS Control Plane** — 5 IMMUTABLE WIDGETS per spec §6 | **DONE (PR #37)** |
| Phase 6.T1a | Tier 1 follow-on: Belief State + Pressure Vector (`core/coherence/`) — entropy-aware uncertainty (INV-50) [v3.2] | **NEXT** |
| Phase 6.T1b | Tier 1 follow-on: Meta-Controller + Confidence Engine (`intelligence_engine/meta_controller/`) — INV-48 fallback lane in `policy/execution_policy.py` [v3.2] + INV-52 shadow lane in `policy/shadow_policy.py` [v3.3] | after 6.T1a |
| Phase 6.T1c | Tier 1 follow-on: Reward shaping (`learning_engine/performance_analysis/reward_shaping.py`) + per-component RewardBreakdown ledger row (B18) [v3.3] + `learning_engine/calibration/coherence_calibrator.py` (INV-53) + `sim_realism_tracker.py` (INV-55) wiring | after 6.T1b |
| Phase 6.T1d | v3.1 fold-in: System Intent Engine (`core/coherence/system_intent.py`, GOV-CP-07 setter) | after 6.T1c |
| Phase 6.T1e | v3.2 fold-in: regime hysteresis activation (`regime_detector.py` + `registry/regime_hysteresis.yaml`, INV-49) | after 6.T1d |
| Phase 7 | Asset systems (forex, stocks, crypto, memecoin isolated process) + PolicyEngine constant-time decision table (I7 reframed) [v3.2] | locked spec |
| Phase 8 | Neuromorphic + AutoLearn (sensors, web autolearn, anomaly adapters) | locked spec |
| Phase 9 | Optimization layer (Rust ports if measured) | locked spec |
| **Phase 10** | **Intelligence Depth Layer** — Simulation vPro + Trader Intelligence (full F1) + Macro Regime + Cross-Asset + Strategic Execution + `agents/` | **NEW (per E1)** |
| Phase 10.1 | Simulation vPro — adds richer `SimulationOutcome` (failure_modes + regime_performance_map + adversarial_breakdowns) [v3.2] + upstream feed for `learning_engine/calibration/sim_realism_tracker.py` (INV-55) [v3.3] | within Phase 10 |
| Phase 10.2–10.4 | Trader Intelligence ingest/offline/consumer + archetype lifecycle (`archetype_lifecycle.py`, INV-51) [v3.2] | within Phase 10 |
| Phase 10.8 | `agents/` namespace activation + typed `SignalEvent.agent_context` schema + B15 lint (`registry/agent_context_keys.yaml`) [v3.2] + AgentIntrospection contract (`_base.py` ABC, INV-54, B19) [v3.3] | within Phase 10 |
| Phase 10.10 | v3.1 fold-in: Opponent Model (`intelligence_engine/opponent_model/`) | within Phase 10 |
| Phase 10.11 | v3.1 fold-in: Reflexive Simulation Layer (`simulation/reflexive_layer/`) | within Phase 10 |
| Phase 10.12 | v3.1 fold-in: Strategy Genetics (`evolution_engine/genetic/`) | within Phase 10 |
| Phase 10.13 | v3.1 fold-in: Regret / Counterfactual Memory (`state/memory_tensor/regret/`) | within Phase 10 |
| Phase 10.14 | v3.1 fold-in: Internal Debate Round (`meta_controller/evaluation/debate_round.py`) | within Phase 10 |

Legacy v2 13-step build remains a sub-decomposition reference in
`build_plan.md` for non-engine items (drift killers, registry split,
operator audit).

Every phase lands as its own PR. Each PR ends with a green CI gate.
Build Compiler Spec §1.1 freeze rules apply to every phase: no engine
renames, no domain collapses, no module removals, additive only.

## Architectural invariants reinforced by this tree

1. **Engines are sealed boxes.** No engine imports another engine; only
   `core/contracts/` is shared. Lint rules `T1`, `B1`, `L1`, `L2`, `L3`
   enforce.
2. **Coherence is a layer, not an engine.** `core/coherence/` *binds*
   engines via event interception; it never modifies engine code. New
   lint rule `B2` (Step 4) reserves cross-engine import privilege to
   `core/coherence/`.
3. **Governance is the only authority.** Every state mutation
   (mode, plugin lifecycle, risk amend, patch deploy, learning update)
   traverses GOV-CP-01..07 and lands as a ledger row.
4. **Hard 3-domain isolation.** NORMAL / COPY-TRADING / MEMECOIN are
   separated under `execution_engine/domains/`; memecoin runs in its own
   process with a burner wallet (INV-20, SAFE-13).
5. **Replay determinism.** All offline engines (Learning, Evolution)
   read the ledger via `state/ledger/reader.py` only; never reach into
   runtime engine state. Data versioning (v2-H) guarantees that
   replay sees the same market data as live ran on.
6. **Coordinated portfolio.** v2-A + v2-B turn "many independent
   strategy outputs" into "one coordinated portfolio decision".
7. **Real broker realism.** v2-C + v2-D + v2-F provide the order
   lifecycle, normalised market state, and real-time risk evaluation
   needed for non-paper execution.
8. **Belief State + Pressure Vector are derived projections.** v3-T1
   `core/coherence/belief_state.py` and `performance_pressure.py` read
   existing engine state via L3 protocols; they never write engine
   state. Governance remains the only authority.
9. **Meta-Controller composes with Strategy Orchestrator (per B1).**
   Pipeline: `signal_pipeline → orchestrator (lifecycle gate) →
   meta_controller (regime route + selector + confidence + sizer +
   policy) → conflict_resolver (vote)`. Both modules retained, distinct
   responsibilities.
10. **Trader Intelligence is governed sensory data.** v3-P10 ingestion
    (`sensory/web_autolearn/trader_intelligence/`) emits
    `WEB_SIGNAL_EVENT` through HITL gate; learning side
    (`learning_engine/trader_abstraction/`) builds embeddings offline
    with fixed seed + ledgered checkpoint; consumer side
    (`intelligence_engine/meta/`) reads `registry/trader_archetypes.yaml`.
    Engines never reach into raw web data.
11. **Simulation runs on slower cadence than hot path.** v3-P10
    `simulation/strategy_arena/` publishes a `StrategyRanking` snapshot
    that the meta-controller reads cached. T1 ≤1ms hot-path budget
    preserved.
12. **Determinism preserved across all v3 additions.** Scenario
    generation uses caller-supplied PRNG seeds; embeddings produced
    offline with fixed seed + checkpoint hash ledgered; agents are
    pure-function-of-state with no clocks; no pure RL (INV-15).
13. **Intent is operator-written, system-read (v3.1).**
    `core/coherence/system_intent.py` is a frozen read-only projection.
    The operator writes `IntentTransition` events through GOV-CP-07
    (HITL gate); meta-controller reads intent via L3 Protocol. The
    system never auto-mutates its own mission. Governance remains the
    only authority.
14. **Internal debate is deterministic, not meta-RL (v3.1).**
    `meta_controller/evaluation/debate_round.py` runs a deterministic stance +
    confidence scoring round across stateful `agents/`. No learned
    coordinator, no policy-gradient meta-controller. Output feeds
    `confidence_engine`. INV-15 replay determinism preserved.
15. **Time hierarchy is layered, not new (v3.1).** Existing FSMs
    already span ms (hot_path) → sec/min (strategy_runtime) →
    hour/day (portfolio + arena cadence) → day/week
    (evolution_engine) → week/month (System Intent + GOV-G18 patch
    cadence). v3.1 documents this, no new modules.
16. **Dynamic identity is emergent (v3.1).** "From trend follower
    → mean reversion" is the active subset of LIVE strategies under
    the current regime + intent — produced by Strategy Lifecycle FSM
    + Strategy Arena + meta-controller `regime_router` reading
    `system_intent`. No new identity engine.
