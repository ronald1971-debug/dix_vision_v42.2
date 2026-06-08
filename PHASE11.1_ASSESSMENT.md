# PHASE 11.1 - DASHBOARD UPDATE IMPLEMENTATION ASSESSMENT

**Date:** 2026-06-02
**Repository:** DIX VISION v42.2
**Status:** Phase 11.1 Assessment - In Progress

---

## EXECUTIVE SUMMARY

Phase 11.1 - Dashboard Update Implementation addresses the specific dashboard modernization requirements outlined in the Desktop specification. The specification defines missing dashboard features organized by domain (INDIRA, DYON, GOVERNANCE) and provides a detailed implementation plan.

**Gap Analysis from Specification:**

**HIGH Priority Missing:**
- Four Golden Signals (p50/p95/p99 latency, traffic, errors, saturation) - DYON
- SLO burn-rate panel (1h/6h/24h error budget) - DYON
- Per-trading-form tiles (SPOT/MARGIN/PERP/FUTURES/OPTIONS/DEX_SWAP/DEX_LP) - INDIRA
- Per-adapter health + last-tick age - DYON
- Kill-switch state indicator (top-bar) - GOVERNANCE
- Authority-violation counter - GOVERNANCE

**MEDIUM Priority Missing:**
- Mode-transition timeline (NORMAL/SAFE/DEGRADED/HALTED) - GOVERNANCE
- Ledger tail with filters + export - EVENT-SOURCED LEDGER
- SYSTEM_HAZARD event feed - DYON → GOVERNANCE
- Open orders + fills feed - INDIRA
- Candlestick chart with trade markers - INDIRA

**LOW Priority Missing:**
- Replay-from-N panel (deterministic replay) - LEDGER
- Chaos/fault-injection panel (shadow only) - DYON

**Required Work:**
Implement missing dashboard features per the Desktop specification.

**Exit Criteria:**
All HIGH and MEDIUM priority dashboard features implemented.

---

## DELIVERABLES

### 1. Phase 1: Core Infrastructure & API Layer

**Goal:** Add new API endpoints to support dashboard features.

**New API Endpoints (to add to ui/cockpit_routes.py):**

**DYON Domain (System Observation):**
- GET /api/signals → Four Golden Signals (latency, traffic, errors, saturation)
- GET /api/adapters → Per-adapter meta + connection state + last-tick age
- GET /api/hazards → SYSTEM_HAZARD_EVENT feed

**INDIRA Domain (Market Execution):**
- GET /api/forms → Per-trading-form rollup (7 forms)
- GET /api/orders/open → Open orders
- GET /api/fills → Recent fills
- POST /api/orders/submit → Submit new order (INDIRA execution)
- POST /api/orders/cancel → Cancel order (INDIRA execution)
- POST /api/orders/cancel-all → Cancel all orders (INDIRA execution)
- POST /api/strategies/activate → Activate strategy (INDIRA execution)
- POST /api/strategies/pause → Pause strategy (INDIRA execution)
- POST /api/positions/close → Close position (INDIRA execution)

**GOVERNANCE Domain (Authority Observation):**
- GET /api/mode/timeline → Mode transitions (NORMAL → SAFE → DEGRADED → HALTED)
- GET /api/security/events → Authority violations + kill switch events
- POST /api/kill-switch → Arm/disarm/trigger (CONTROL-domain only)

**EVENT-SOURCED LEDGER:**
- GET /api/ledger/tail → Last 100 events per stream (MARKET/SYSTEM/GOVERNANCE/HAZARD/SECURITY)
- GET /api/ledger/verify → Hash chain verification (ok + break row if any)
- GET /api/ledger/export → JSONL download
- POST /api/ledger/replay → Deterministic replay preview (read-only, rebuilds projector hash)

**New API Client Functions (dashboard2026/src/api/signals.ts):**
- fetchGoldenSignals()
- fetchSLOBurnRate()
- fetchAdapterHealth()
- fetchSystemHazards()
- fetchTradingForms()
- fetchOpenOrders()
- fetchRecentFills()
- submitOrder()
- cancelOrder()
- cancelAllOrders()
- activateStrategy()
- pauseStrategy()
- closePosition()
- fetchModeTimeline()
- fetchSecurityEvents()
- triggerKillSwitch()
- fetchLedgerTail()
- verifyLedgerChain()
- exportLedger()

### 2. Phase 2: New Dashboard Pages

**Goal:** Create new dashboard pages as specified.

**Signals Page — DYON Observation (SignalsPage.tsx):**
- Route: #/signals
- Four Golden Signals visualization
- SLO Burn Rate panel (1h/6h/24h)
- Per-adapter health + last-tick age

**Ledger Page — EVENT-SOURCED LEDGER (LedgerPage.tsx - update existing):**
- Route: #/ledger (update existing)
- Ledger tail with filters (MARKET/SYSTEM/GOVERNANCE/HAZARD/SECURITY)
- Hash chain verification
- JSONL export
- Replay-from-N panel (deterministic replay)

**Hazard Feed Page — DYON → GOVERNANCE (HazardsPage.tsx - update existing):**
- Route: #/hazards (update existing)
- SYSTEM_HAZARD event feed
- Real-time hazard monitoring

**Top-Bar Updates:**
- Kill-switch state indicator (red/green/amber)
- Authority-violation counter
- Mode-transition timeline ribbon

---

## ASSESSMENT METHODOLOGY

### Step 1: Gap Validation

**Approach:** Validate the gaps identified in the specification against current dashboard state.

### Step 2: Implementation Feasibility

**Approach:** Assess implementation feasibility for each feature.

### Step 3: Implementation Plan

**Approach:** Create implementation plan with priorities.

---

## EXIT CRITERIA

Phase 11.1 is complete when:

1. ✅ Gap validation is complete
2. ✅ API endpoints are implemented
3. ✅ API client functions are implemented
4. ✅ HIGH priority dashboard features are implemented
5. ✅ MEDIUM priority dashboard features are implemented
6. ✅ Phase 11.1 Final Report is generated

---

## NEXT STEPS

1. Validate gaps against current dashboard state
2. Implement Phase 1 API endpoints
3. Implement API client functions
4. Implement Phase 2 dashboard pages
5. Implement top-bar updates
6. Test all new features
7. Generate Phase 11.1 Final Report
