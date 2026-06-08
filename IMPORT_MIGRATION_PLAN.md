# Import Migration Plan - execution → execution_engine

**Date:** 2026-06-08
**Files to Update:** 9 external files
**Files to Skip:** 18 internal execution/ files (legacy)

---

## 📊 IMPORT ANALYSIS

### Total Files Found: 27
- **External (need update):** 9 files
- **Internal (execution/ - legacy):** 18 files (skip)

---

## 🎯 BATCH 1: Core Runtime (4 files)
**Priority:** HIGH - Core execution paths

1. `runtime/paper_trading.py`
2. `runtime/live_trading.py`
3. `mind/fast_execute.py`
4. `governance/kernel.py`

### Import Analysis
Let me check what these files import from execution.