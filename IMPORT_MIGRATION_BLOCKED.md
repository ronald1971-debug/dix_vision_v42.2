# ⚠️ CRITICAL FINDING - Import Migration Blocked

**Date:** 2026-06-08
**Status:** ⛔ IMPORT MIGRATION CANNOT PROCEED SAFELY

---

## 🔴 PROBLEM

**execution_engine is NOT a complete drop-in replacement for execution/**

After analyzing 27 files with `from execution.` imports, I discovered that critical components are still MISSING from execution_engine:

### Missing Critical Components

1. **adapter_router** (CRITICAL - used by 3 core files)
   - `runtime/paper_trading.py` uses `execution.adapter_router`
   - `runtime/live_trading.py` uses `execution.adapter_router`
   - `mind/fast_execute.py` uses `execution.adapter_router`
   - **execution_engine/adapters/ exists but has NO router**

2. **hazard detection system** (CRITICAL - used by governance)
   - `governance/kernel.py` uses `execution.hazard.async_bus`
   - `governance/kernel.py` uses `execution.hazard.severity_classifier`
   - **execution_engine/protections/ has circuit_breaker but NOT hazard bus**

### Impact

- **3 core runtime files** would break if we update imports blindly
- **governance kernel** would break (loss of hazard detection)
- **Trading hot path** would break (loss of adapter routing)

---

## 📊 Import Analysis Summary

### External Files with execution imports (9 total):

**BLOCKED - Missing equivalents in execution_engine:**
1. `runtime/paper_trading.py` - needs adapter_router ❌
2. `runtime/live_trading.py` - needs adapter_router ❌
3. `mind/fast_execute.py` - needs adapter_router ❌
4. `governance/kernel.py` - needs hazard/async_bus, hazard/severity_classifier ❌

**POTENTIALLY SAFE - Need analysis:**
5. `system_monitor/telemetry_ingest.py` - needs analysis
6. `system_monitor/heartbeat_monitor.py` - needs analysis
7. `system_monitor/hazard_bus.py` - needs analysis
8. `tests/test_neuromorphic_triad.py` - needs analysis
9. `execution_engine/mcos_orchestrator.py` - needs analysis

### Internal execution/ files (18 total)
These are legacy files in execution/ and can be left as-is.

---

## 🎯 RECOMMENDED ACTION

### Option A: Complete Missing Components First (Recommended)
Migrate the missing critical components to execution_engine before updating imports:
1. Migrate `execution/adapter_router.py` → `execution_engine/adapters/router.py`
2. Migrate `execution/hazard/` → `execution_engine/hazard/` or integrate into protections/
3. Verify all functionality works
4. Then proceed with import updates

**Estimated effort:** 2-4 hours
**Risk:** Low (methodical migration)

### Option B: Keep execution/ as Dependency (Alternative)
Accept that execution_engine is not yet complete and keep execution/ as a dependency for:
- adapter_router
- hazard detection
- other missing components

Update the migration plan to reflect this partial consolidation.

**Estimated effort:** 30 minutes
**Risk:** None (no breaking changes)

### Option C: Blind Import Update (NOT RECOMMENDED)
Update all imports anyway and accept that the system will break until missing components are migrated.

**Estimated effort:** 1-2 hours
**Risk:** CRITICAL (system will break)

---

## 📋 Missing Components Inventory

### execution/ components NOT in execution_engine:

1. **adapter_router.py** - CRITICAL
2. **hazard/** directory - CRITICAL
   - async_bus.py
   - severity_classifier.py
   - detector.py
   - event_emitter.py
3. **confirmations/** directory
   - reconciliation.py
4. **algos/** directory
5. **Other adapters** (execution has 5 adapters, execution_engine has 40+ but may have different APIs)

---

## ✅ CURRENT STATUS

**Phase 1 (Governance):** 100% COMPLETE ✅
**Phase 2.1 (Execution Critical):** 100% COMPLETE ✅
**Phase 2.4 (Import Updates):** ❌ BLOCKED - Missing components

**Recommendation:** Proceed with Option A to complete missing component migration before import updates.

---

**Last Updated:** 2026-06-08
**Action Required:** Decision on Option A, B, or C