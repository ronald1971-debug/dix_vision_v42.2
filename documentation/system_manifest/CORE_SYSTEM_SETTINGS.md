# DIX VISION v42.2+ - Core System Settings

**Status:** ✅ CANONICAL (June 21, 2026)
**Purpose:** Define core system settings that must not deviate across development phases
**Enforcement:** All future development must adhere to these core settings

---

## 🎯 CANONICAL CORE SETTINGS

### **1. Signal-First Decision Architecture (UNIVERSAL BASELINE)**

**Setting Name:** SIGNAL_WORLD_RATIO_UNIVERSAL_BASELINE
**Value:** 85/15 (85% Signals, 15% World)
**Status:** ✅ CANONICAL (DO NOT DEVIATE)
**Date Established:** June 21, 2026
**Rationale:** Trading is fundamentally signal-driven; world understanding provides essential risk enhancement

**Implementation:**
- Universal baseline for all trading forms
- Dashboard control provides operator adjustment (50-95% range)
- Auto-adjustment to optimal ratios per trading form
- Trading form optimization database provides specific optimal ratios

**Constraints:**
- Signals must remain primary (minimum 50% signals in any scenario)
- World context is enhancement, not replacement
- Operator sovereignty maintained via dashboard control
- All future phases must maintain signal-first architecture

**Reference Implementation:**
- File: `containers/system_core/world_model/signal_first_decision_engine.py`
- File: `containers/system_core/world_model/signal_world_ratio_analyzer.py`
- Documentation: `documentation/phase_reports/DASHBOARD_SIGNAL_WORLD_CONTROL_IMPLEMENTATION.md`

---

### **2. Domain Separation (MANDATORY)**

**Setting Name:** CANONICAL_DOMAIN_SEPARATION
**Value:** Six cognitive domains must remain separate
**Status:** ✅ CANONICAL (DO NOT DEVIATE)
**Date Established:** From vision documents (maintained)

**Domains:**
1. **INDIRA** (Market Intelligence) - `indira_cognitive/`
2. **DYON** (System Engineering Intelligence) - `dyon_cognitive/`
3. **GOVERNANCE** (Control Authority) - `governance_unified/`
4. **EXECUTION** (Market Interaction) - `execution_unified/`
5. **LEARNING** (Experience Transformation) - `learning_engine/`
6. **EVOLUTION** (System Adaptation) - `evolution_engine/`

**Infrastructure Domain (Non-Cognitive):**
- **SYSTEM ENGINE** (Infrastructure Only) - `system_engine/` (health, monitoring, fault management)

**Constraints:**
- No consolidation across cognitive domains
- Each cognitive domain has its own directory
- System Engine contains only infrastructure components
- No cognitive components in system_engine/

---

### **3. Zero Placeholder Policy (MANDATORY)**

**Setting Name:** ZERO_PLACEHOLDER_POLICY
**Value:** All code must be real implementations, no placeholders
**Status:** ✅ CANONICAL (DO NOT DEVIATE)
**Date Established:** From Tier-0 Build Contract

**Prohibited:**
- No TODO comments (use features/bucket lists instead)
- No FIXME comments (use features/bucket lists instead)
- No NotImplemented exceptions
- No pass statements in function bodies
- No fake data or stub implementations

**Required:**
- All code must have real runtime behavior
- Complete capability chains: INPUT → PROCESSING → DECISION → OUTPUT → VALIDATION → OBSERVABILITY → AUDITABILITY
- Real metrics and monitoring
- Production-grade error handling

---

### **4. Operator Sovereignty (MANDATORY)**

**Setting Name:** OPERATOR_SOVEREIGNTY_ABSOLUTE
**Value:** Operator control is absolute and never bypassed
**Status:** ✅ CANONICAL (DO NOT DEVIATE)
**Date Established:** From vision documents

**Requirements:**
- All governance decisions require operator authority
- Dashboard control requires operator ID for audit trail
- No system can self-authorize critical actions
- Kill switch requires operator activation
- All ratio changes logged with operator ID

---

### **5. INDIRA Constraints (MANDATORY)**

**Setting Name:** INDIRA_CONSTRAINTS_MANDATORY
**Value:** INDIRA must never execute trades directly
**Status:** ✅ CANONICAL (DO NOT DEVIATE)
**Date Established:** From vision documents

**Constraints:**
- Never executes trades directly (delegated to execution via governance-gated intents)
- Never modifies learning parameters (proposal-only, requires COGNITIVE GOVERNANCE approval)
- Never imports execution_engine or governance_engine internals (contracts only)
- Never operates in the fast path or blocks synchronously

---

### **6. DYON Constraints (MANDATORY)**

**Setting Name:** DYON_CONSTRAINTS_MANDATORY
**Value:** DYON must never deploy patches directly
**Status:** ✅ CANONICAL (DO NOT DEVIATE)
**Date Established:** From vision documents

**Constraints:**
- NEVER deploys patches directly (all patches flow through PatchProposal FSM)
- NEVER modifies live trading parameters or capital accounts
- NEVER suppresses operator visibility
- NEVER self-authorises system restart or kill switch activation
- NEVER modifies event ledger or hash chain
- NEVER introduces non-determinism into replay paths

---

### **7. Governance Constraints (MANDATORY)**

**Setting Name:** GOVERNANCE_CONSTRAINTS_MANDATORY
**Value:** Governance must never execute trades
**Status:** ✅ CANONICAL (DO NOT DEVIATE)
**Date Established:** From vision documents

**Constraints:**
- NEVER executes trades
- NEVER runs in the fast path or blocks INDIRA synchronously
- NEVER amends charter without SYSTEM/CHARTER_AMENDED event + human approval
- NEVER promotes strategy without shadow window completion

---

## 🎯 DASHBOARD CONTROL SETTINGS

### **Signal-World Ratio Control (UNIVERSAL)**

**Setting Name:** DASHBOARD_SIGNAL_WORLD_CONTROL_ENABLED
**Value:** True (dashboard control is canonical interface)
**Status:** ✅ CANONICAL (DO NOT DEVIATE)
**Date Established:** June 21, 2026

**Dashboard Components:**
- Trading form selection (4 dropdowns: category, domain, timeframe, execution mode)
- Signal-world ratio slider (50-95% signals range)
- Current vs optimal ratio display
- 6 preset configurations (95/5 to 65/35)
- Auto-adjustment toggles (trading form, regime)
- Reset to optimal button
- Performance tracking by ratio

**Auto-Adjustment Settings:**
- **Auto-adjust when trading form changes:** Enabled (default)
- **Auto-adjust for market regimes:** Enabled (default)
- **Auto-adjust based on performance:** Disabled (manual for now)

---

## 🎯 CORE SETTING ENFORCEMENT

### **How to Ensure No Deviation:**

**1. Documentation Review:**
- All vision documents updated with signal-first architecture
- System manifest updated with signal-first principle
- Core settings documented in this file
- Phase reports reference canonical architecture

**2. Implementation Review:**
- All new code must reference signal-first architecture
- Dashboard control must be used for ratio adjustments
- Trading form selection must use optimal ratio database
- No hardcoded signal-world ratios (use database)

**3. Contract Compliance:**
- All phases must verify contract compliance
- Zero placeholder policy must be maintained
- Domain separation must be preserved
- Operator sovereignty must be absolute

**4. Audit Trail:**
- All dashboard changes logged with operator ID
- All ratio adjustments documented
- All deviations from optimal logged
- All canonical setting changes documented

---

## 🎯 CORE SETTING MODIFICATION PROCESS

**To Modify a Core Setting:**

1. **Document Rationale:**
   - Why is the change necessary?
   - What problem does it solve?
   - What is the impact?

2. **Update All References:**
   - System manifest
   - Vision documents
   - This core settings file
   - Phase reports
   - Implementation files

3. **Verify Contract Compliance:**
   - Does the change violate any constraint?
   - Is operator sovereignty maintained?
   - Is domain separation preserved?
   - Is zero placeholder policy maintained?

4. **Test Implementation:**
   - Update implementation to use new setting
   - Verify all components use new setting
   - Test dashboard control with new setting
   - Verify optimal ratio database updated

5. **Document Change:**
   - Update all documentation
   - Add change log entry
   - Update canonical status
   - Notify all developers

---

## 🎯 CURRENT CANONICAL SETTINGS SUMMARY

| Setting Name | Value | Status | Date |
|-------------|-------|--------|------|
| SIGNAL_WORLD_RATIO_UNIVERSAL_BASELINE | 85/15 | ✅ CANONICAL | June 21, 2026 |
| CANONICAL_DOMAIN_SEPARATION | Six separate domains | ✅ CANONICAL | From vision |
| ZERO_PLACEHOLDER_POLICY | No placeholders allowed | ✅ CANONICAL | From contract |
| OPERATOR_SOVEREIGNTY_ABSOLUTE | Operator control absolute | ✅ CANONICAL | From vision |
| INDIRA_CONSTRAINTS_MANDATORY | Never execute directly | ✅ CANONICAL | From vision |
| DYON_CONSTRAINTS_MANDATORY | Never deploy directly | ✅ CANONICAL | From vision |
| GOVERNANCE_CONSTRAINTS_MANDATORY | Never execute trades | ✅ CANONICAL | From vision |
| DASHBOARD_SIGNAL_WORLD_CONTROL_ENABLED | True (canonical interface) | ✅ CANONICAL | June 21, 2026 |

---

## 🎯 NEXT PHASE REQUIREMENTS

**Phase 2 (Learning System Organization) Must:**
- ✅ Maintain signal-first architecture (85/15 baseline)
- ✅ Use dashboard control for any ratio adjustments
- ✅ Reference optimal ratio database for trading forms
- ✅ Maintain domain separation
- ✅ Maintain zero placeholder policy
- ✅ Maintain operator sovereignty
- ✅ Maintain all cognitive system constraints

**Do Not Deviate From:**
- Signal-first decision architecture
- Dashboard control interface
- Universal baseline 85/15
- Trading form optimization
- Core constraint settings

---

**This document defines the canonical core settings for DIX VISION v42.2+. All future development must adhere to these settings without deviation.**