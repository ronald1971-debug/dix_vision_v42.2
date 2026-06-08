# DIXVISION Architectural Invariants (Constitution)

> **Phase:** EPIC-001 ARCHITECTURAL CONSTITUTION  
> **Status:** Authoritative  
> **Enforcement:** CI (tools/authority_lint.py), Governance Engine, Runtime

This document is the **Constitution of DIXVISION**. Nothing gets merged if it violates it.

## INV-DIX-01: Cognitive System First

DIXVISION is a cognitive intelligence system, not a trading bot. All system behavior flows from cognition.

**Enforced by:** B-TRADING, B-COGNITIVE-ONLY

## INV-DIX-02: BeliefState as Single Source of Truth

BeliefState is the single source of truth for all reality domains. No subsystem may maintain a competing version of reality.

Reality Domains:
- `MarketBeliefs` — market state, prices, volatility, regime
- `TraderBeliefs` — trader profiles, preferences, behavior patterns  
- `StrategyBeliefs` — strategy performance, hypotheses, rankings
- `PortfolioBeliefs` — allocation, exposure, correlation, capital
- `ExecutionBeliefs` — fill data, slippage, latency, reconciliation
- `SystemBeliefs` — health, latency, resource utilization

**Enforced by:** B-BELIEF-STATE, runtime_guard

## INV-DIX-03: INDIRA Domain Ownership

INDIRA owns market, trader, strategy, portfolio, allocation, position, and execution-feedback cognition.

Domains:
- `market_intelligence`
- `trader_intelligence`
- `strategy_intelligence`
- `portfolio_intelligence`
- `allocation_intelligence`
- `position_intelligence`
- `execution_feedback_intelligence`

**Enforced by:** B-INDIRA-DOMAIN

## INV-DIX-04: DYON Domain Ownership

DYON owns system cognition only.

Domains:
- `repository_intelligence`
- `architecture_intelligence`
- `runtime_intelligence`
- `infrastructure_intelligence`

**Enforced by:** B-DYON-DOMAIN

## INV-DIX-05: Strategy Cognition Exclusivity

Strategy cognition belongs exclusively to INDIRA. No other module may generate trading strategies.

**Enforced by:** Authority Linter, Runtime Graph Validator

```python
# Example violation:
# evolution_engine/dyon/topology_scanner.py
# imports strategy_engine → FAIL INV-DIX-05
```

## INV-DIX-06: Execution Engine Purity

Execution Engine owns market interaction, not decision creation.

**Enforced by:** T1, B1, B20

## INV-DIX-07: Learning Engine Authority

Learning Engine owns experience transformation.

**Enforced by:** L1, INV-15

## INV-DIX-08: Governance Accountability

Governance Engine owns accountability, not cognition.

**Enforced by:** CONF-01, CONF-08, CONF-09

## INV-DIX-09: System Awareness

System Engine owns operational awareness.

**Enforced by:** CONF-02, CONF-03

## INV-DIX-010: Operator Supremacy

Operator is the highest authority. All governance changes require operator action.

**Enforced by:** GOV-CP-07

## INV-DIX-011: Cognitive Development Priority

Cognitive development is a primary objective. The system evolves through observation, reasoning, and learning.

**Enforced by:** Development Mode Policy

## INV-DIX-012: Capital Separation

Capital deployment is separate from cognitive development. No cognitive process may directly move capital.

**Enforced by:** Triad Lock (B20, B21, B22)

## INV-DIX-013: Domain Separation

Architectural domain separation is mandatory. Cross-domain imports require explicit governance approval.

**Enforced by:** Authority Linter (all rules)

## INV-DIX-014: Continuous Evolution

DIXVISION continuously evolves through observation, reasoning, learning. Static configurations are prohibited.

**Enforced by:** DYON mutation pipeline

---

## Enforcement Matrix

| Invariant | CI Enforcement | Runtime Enforcement | Governance Check |
|-----------|----------------|-------------------|-----------------|
| INV-DIX-01 | B-COGNITIVE-ONLY | - | Operator Mode |
| INV-DIX-02 | B-BELIEF-STATE | Invariant Monitor | - |
| INV-DIX-03 | B-INDIRA-DOMAIN | Domain Guard | - |
| INV-DIX-04 | B-DYON-DOMAIN | Domain Guard | - |
| INV-DIX-05 | Authority Linter | Runtime Graph | - |
| INV-DIX-06 | T1, B1 | AuthorityGuard | - |
| INV-DIX-07 | L1 | - | - |
| INV-DIX-08 | CONF-01 | - | Validation |
| INV-DIX-09 | CONF-02,03 | - | - |
| INV-DIX-010 | - | - | GOV-CP-07 |
| INV-DIX-011 | - | Development Mode | - |
| INV-DIX-012 | B20,B21,B22 | Triad Guard | - |
| INV-DIX-013 | All Lint Rules | Domain Guard | - |
| INV-DIX-014 | Mutation Pipeline | DYON Constraints | - |

---

## Violation Consequences

| Severity | Action | Replay Required |
|----------|--------|-----------------|
| BLOCKING | Merge denied | Yes |
| WARNING | Operator alert | No |
| CRITICAL | Immediate halt | Yes |

---

## Related Documents

- `contracts/ownership_registry.yaml` — Domain ownership definitions
- `contracts/belief_state.proto` — BeliefState contract
- `tools/authority_lint.py` — CI enforcement implementation
- `governance_engine/policy_compiler.py` — Governance rules
- `governance_engine/dyon_constraints.py` — DYON limitations