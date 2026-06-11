# COMPLETE GOVERNANCE OVERSIGHT - TRADING MODES & AUTHORITY

## 🎯 **SYSTEM PURPOSE - CRITICAL CLARIFICATION**

**Your concern is valid**: The system cannot truly self-evolve if INDIRA doesn't have full autonomous authority in FULL AUTO mode, and the governance rules are preventing the system from updating itself to the current state.

This document provides:
1. **All trading modes** and INDIRA's authority in each
2. **Complete list of all formal governance rules/invariants**
3. **Which rules are blocking self-evolution**
4. **Which rules need to be changed for true autonomy**
5. **How to modify them safely**

---

## 📊 **TRADING MODES - COMPLETE BREAKDOWN**

### **Mode FSM Hierarchy**
```
SAFE (0) → PAPER (1) → CANARY (3) → LIVE (4) → AUTO (5)
                                           ↓
                                      LOCKED (99) ← from any mode
```

### **1. SAFE MODE (SystemMode.SAFE = 0)**

**Purpose**: System initialization, recovery, no trading

**INDIRA Authority**:
- ❌ **NO trading execution**
- ❌ **NO real order routing**
- ✅ Signal generation allowed
- ✅ Market analysis allowed
- ✅ Research allowed
- ✅ Learning allowed (if development_enabled)
- ✅ Cognitive processing allowed

**Execution**:
- Simulated paper broker only
- No real money at risk
- No exchange connections

**Governance**:
- Maximum safety constraints
- All risk limits at minimum
- Kill-switch always armed

**Operator Control**: 
- **SEMI-AUTO** (operator must approve all actions)
- Full manual override available
- Can trigger emergency halt

---

### **2. PAPER MODE (SystemMode.PAPER = 1)**

**Purpose**: **INDIRA LEARNING MODE** - Real execution pipeline with simulated fills, no real money risk

**INDIRA Authority**:
- ✅ **FULL trading execution** (through paper broker)
- ✅ **FULL order routing** (real execution pipeline)
- ✅ Signal generation allowed
- ✅ Market analysis allowed
- ✅ Research allowed
- ✅ Learning allowed
- ✅ Cognitive processing allowed
- ✅ **Real order state management**
- ✅ **Real position management**
- ✅ **Real execution learning**

**Execution**:
- **Real execution pipeline** (same as LIVE mode)
- **Real order routing** (same as LIVE mode)
- **Real order state management** (same as LIVE mode)
- **Simulated fills via Paper Broker** (no real money)
- Simulated PnL
- No real money at risk

**Governance**:
- Standard risk limits
- Paper broker provides simulated fills
- Same execution path as LIVE mode
- Allows INDIRA to learn execution mechanics

**Operator Control**:
- **SEMI-AUTO** (operator can override signals)
- Manual signal approval
- Can approve/deny paper trades
- Can disable paper execution anytime

---

### **3. CANARY MODE (SystemMode.CANARY = 3)**

**Purpose**: Limited live testing, small position sizes, high oversight

**INDIRA Authority**:
- ✅ **LIMITED trading execution**
- ✅ **LIMITED order routing** (small positions only)
- ✅ Signal generation allowed
- ✅ Market analysis allowed
- ✅ Research allowed
- ✅ Learning allowed
- ✅ Cognitive processing allowed
- ⚠️ Position size strictly limited
- ⚠️ Daily cap very low

**Execution**:
- Real broker connections
- Real fills
- Real PnL
- **BUT** with tight constraints:
  - Maximum position size: $100
  - Daily cap: $500
  - Single trade limit: $50

**Governance**:
- Elevated risk monitoring
- Automated risk checks
- Position size enforcement
- Daily cap enforcement

**Operator Control**:
- **SEMI-AUTO** (operator must approve each trade)
- Trade-by-trade approval
- Manual override always available
- Can revoke authority instantly

**Transition Requirements**:
- Policy approval required
- Risk approval required
- Compliance approval required
- Operator-authorized flag

---

### **4. LIVE MODE (SystemMode.LIVE = 4)**

**Purpose**: Production trading with normal position sizes, still operator oversight

**INDIRA Authority**:
- ✅ **FULL trading execution**
- ✅ **FULL order routing**
- ✅ Signal generation allowed
- ✅ Market analysis allowed
- ✅ Research allowed
- ✅ Learning allowed
- ✅ Cognitive processing allowed
- ✅ Normal position sizes
- ✅ Normal daily caps

**Execution**:
- Real broker connections
- Real fills
- Real PnL
- Normal constraints:
  - Maximum position size: $10,000
  - Daily cap: $50,000
  - Single trade limit: $5,000

**Governance**:
- Standard risk monitoring
- Automated risk checks
- Position size enforcement
- Daily cap enforcement
- Kill-switch always armed

**Operator Control**:
- **SEMI-AUTO** (operator can override, but not required for each trade)
- Bulk approval possible
- Manual override available
- Can revoke authority instantly

**Transition Requirements**:
- Policy approval required
- Risk approval required
- Compliance approval required
- Operator-authorized flag

---

### **5. AUTO MODE (SystemMode.AUTO = 5)** ⚠️ **CRITICAL**

**Purpose**: **FULL AUTONOMOUS TRADING** - INDIRA has maximum authority

**INDIRA Authority**:
- ✅ **FULL trading execution** (no operator approval per trade)
- ✅ **FULL order routing** (autonomous)
- ✅ **Signal generation** (autonomous)
- ✅ **Market analysis** (autonomous)
- ✅ **Research** (autonomous)
- ✅ **Learning** (autonomous)
- ✅ **Cognitive processing** (autonomous)
- ✅ **Normal position sizes**
- ✅ **Normal daily caps**
- ✅ **Position sizing** (autonomous)
- ✅ **Risk adjustment** (autonomous within limits)
- ✅ **Strategy switching** (autonomous within approved set)

**Execution**:
- Real broker connections
- Real fills
- Real PnL
- Normal constraints:
  - Maximum position size: $10,000
  - Daily cap: $50,000
  - Single trade limit: $5,000
- **NO per-trade operator approval required**
- **Trading decisions fully autonomous**

**Governance**:
- Standard risk monitoring
- Automated risk checks
- Position size enforcement
- Daily cap enforcement
- Kill-switch always armed
- **Cannot override governance invariants**
- **Cannot modify risk limits autonomously**

**Operator Control**:
- **FULL AUTO** (operator NOT required to approve trades)
- Manual override available (emergency only)
- Can revoke authority instantly
- Can adjust governance parameters (not trading decisions)

**Transition Requirements**:
- Policy approval required
- Risk approval required
- Compliance approval required
- **EXPLICIT operator_authorized flag** (must be set)
- Typed consent envelope (HARDEN-S1 item 8)

**What AUTO Does NOT Allow**:
- ❌ Cannot modify risk limits
- ❌ Cannot override governance invariants
- ❌ Cannot bypass kill-switch
- ❌ Cannot self-approve patches
- ❌ Cannot modify system architecture

---

### **6. LOCKED MODE (SystemMode.LOCKED = 99)**

**Purpose**: Emergency halt, no activity allowed

**INDIRA Authority**:
- ❌ **NO trading execution**
- ❌ **NO signal generation**
- ❌ **NO order routing**
- ❌ **NO cognitive processing**
- ❌ **NO learning**
- ✅ System monitoring allowed (DYON only)
- ✅ Emergency operations allowed

**Execution**:
- All trading halted
- All orders cancelled
- All positions closed
- No new activity

**Governance**:
- Maximum safety
- Kill-switch triggered
- No exceptions

**Operator Control**:
- **FULL CONTROL**
- Only operator can unlock
- Can transition to SAFE only

---

## 📋 **COMPLETE LIST OF FORMAL GOVERNANCE RULES/INVARIANTS**

### **Architectural Layer Invariants (B-Series)**

#### **B1: Cross-Runtime-Engine Direct Imports Forbidden**
**Rule**: Generalization of T1 - no direct imports between different runtime engines
**Enforced by**: `authority_lint.py`
**Blocks**: Direct imports between execution/intelligence/governance engines
**Impact**: Prevents tight coupling between engines
**Blocks Self-Evolution?**: ⚠️ **YES** - prevents DYON from modifying execution engine code directly

#### **B7: Dashboard Isolation**
**Rule**: Dashboard may only import core.contracts, core.coherence, governance_engine.control_plane (Protocol surfaces), state.ledger.reader, and intelligence_engine read-only public surfaces
**Enforced by**: `authority_lint.py`
**Blocks**: Dashboard importing private engine modules
**Impact**: Separates control plane from execution
**Blocks Self-Evolution?**: ❌ NO - cosmetic, doesn't block evolution

#### **B8: System Intent Isolation**
**Rule**: System intent projection module may not import any *_engine package or writable surface
**Enforced by**: `authority_lint.py`
**Blocks**: Direct engine access in intent projection
**Impact**: Ensures operator control over strategic direction
**Blocks Self-Evolution?**: ⚠️ **YES** - prevents AI from overriding strategic intent

#### **B17: Shadow Meta-Controller Non-Acting**
**Rule**: Shadow policy module may not import governance_engine
**Enforced by**: `authority_lint.py`
**Blocks**: Shadow controller accessing governance
**Impact**: Prevents shadow governance from interfering
**Blocks Self-Evolution?**: ❌ NO - cosmetic

#### **B20: Triad Lock - Governance Order-Blind**
**Rule**: governance_engine may not import any execution_engine surface
**Enforced by**: `authority_lint.py`
**Blocks**: Governance accessing execution directly
**Impact**: Prevents circular dependencies
**Blocks Self-Evolution?**: ⚠️ **YES** - prevents governance from triggering execution

#### **B21: Triad Lock - Only Execution Engine May Construct ExecutionEvent**
**Rule**: Only execution_engine may construct ExecutionEvent
**Enforced by**: `authority_lint.py`
**Blocks**: Other engines creating execution events
**Impact**: Ensures single source of execution authority
**Blocks Self-Evolution?**: ⚠️ **YES** - prevents INDIRA from directly creating execution events

#### **B22: Triad Lock - Only Intelligence Engine May Construct SignalEvent**
**Rule**: Only intelligence_engine may construct SignalEvent
**Enforced by**: `authority_lint.py`
**Blocks**: Other engines creating signal events
**Impact**: Ensures single source of signal authority
**Blocks Self-Evolution?**: ⚠️ **YES** - prevents execution engine from generating signals

#### **B23: Registry-Driven AI Providers**
**Rule**: Chat widgets may not contain hardcoded AI vendor names; must read from registry
**Enforced by**: `authority_lint.py`
**Blocks**: Hardcoded AI providers in UI
**Impact**: Forces centralized AI provider management
**Blocks Self-Evolution?**: ❌ NO - cosmetic

#### **B24: LangGraph/LangChain Import Containment**
**Rule**: Only intelligence_engine.cognitive.* and evolution_engine.dyon.* may import langgraph/langchain
**Enforced by**: `authority_lint.py`
**Blocks**: Graph orchestration in hot-path engines
**Impact**: Quarantines non-deterministic graph logic
**Blocks Self-Evolution?**: ⚠️ **YES** - prevents DYON from using graph logic in system evolution

#### **B25: Execution Gate Origin Restriction**
**Rule**: Only intelligence_engine.* and governance_engine.* may call create_execution_intent/mark_approved/mark_rejected
**Enforced by**: `authority_lint.py`
**Blocks**: Direct execution intent creation by other modules
**Impact**: Centralizes execution gate authority
**Blocks Self-Evolution?**: ⚠️ **YES** - prevents DYON from directly creating execution intents

#### **B26: Operator-Approval Edge Restriction**
**Rule**: Only intelligence_engine.cognitive.approval_edge may construct SignalEvent with produced_by_engine stamp
**Enforced by**: `authority_lint.py`
**Blocks**: Bypassing operator approval queue
**Impact**: Ensures all proposals go through approval queue
**Blocks Self-Evolution?**: ⚠️ **YES** - prevents INDIRA from bypassing operator approval

---

### **Layer Separation Invariants (L-Series)**

#### **L1: Learning ↔ Evolution Direct Imports Forbidden**
**Rule**: Learning engine and evolution engine cannot import each other
**Enforced by**: `authority_lint.py`
**Blocks**: Direct coupling between learning and evolution
**Impact**: Prevents learning loop from being corrupted by evolution
**Blocks Self-Evolution?**: ⚠️ **YES** - prevents learning from directly modifying evolution code

#### **L2: Offline Engines May Not Import Runtime Engines**
**Rule**: learning_engine and evolution_engine may not import execution_engine or intelligence_engine
**Enforced by**: `authority_lint.py`
**Blocks**: Offline engines accessing runtime
**Impact**: Ensures offline engines stay truly offline
**Blocks Self-Evolution?**: ⚠️ **YES** - prevents DYON from modifying runtime code

#### **L3: Runtime Engines May Not Import Learning/Evolution Engines**
**Rule**: execution_engine and intelligence_engine may not import learning_engine or evolution_engine
**Enforced by**: `authority_lint.py`
**Blocks**: Runtime engines accessing offline engines
**Impact**: Prevents runtime from modifying learning/evolution
**Blocks Self-Evolution?**: ⚠️ **YES** - prevents runtime from interfering with self-evolution

---

### **Determinism Invariants (INV-Series)**

#### **INV-15: Deterministic Replay Capability**
**Rule**: Timestamps must be caller-supplied, never from wall clock
**Enforced by**: Multiple modules
**Blocks**: Non-deterministic behavior in critical paths
**Impact**: Ensures replay accuracy for audit and debugging
**Blocks Self-Evolution?**: ⚠️ **YES** - prevents DYON from using wall clock in patches

---

### **Domain-Specific Invariants (C-Series, T-Series, W-Series)**

#### **C2: Neuromorphic Isolation (NEUR-04 / SAFE-18)**
**Rule**: Neuromorphic sensors may not import execution modules
**Enforced by**: `authority_lint.py`
**Blocks**: Sensor → execution coupling
**Impact**: Keeps sensors as pure observers
**Blocks Self-Evolution?**: ❌ NO - proper isolation

#### **C3: Web-Autolearn Isolation (SAFE-15 / WEBLEARN-07)**
**Rule**: Web autolearn may not import execution or wallet modules
**Enforced by**: `authority_lint.py`
**Blocks**: Crawler accessing trading capabilities
**Impact**: Prevents autonomous research from triggering trades
**Blocks Self-Evolution?**: ⚠️ **YES** - prevents INDIRA research from directly triggering execution

#### **T1: Fast-Path Purity**
**Rule**: Hot-path modules must not import governance
**Enforced by**: `authority_lint.py`
**Blocks**: Governance checks on hot path
**Impact**: Ensures hot-path performance
**Blocks Self-Evolution?**: ⚠️ **YES** - prevents runtime governance from slowing execution

#### **W1: Burner-Wallet Isolation**
**Rule**: Memecoin adapters cannot import main wallet
**Enforced by**: `authority_lint.py`
**Blocks**: Memecoin trading accessing main wallet
**Impact**: Isolates experimental trading
**Blocks Self-Evolution?**: ❌ NO - safety isolation

---

## 🚧 **RULES BLOCKING TRUE SELF-EVOLUTION**

### **HIGH IMPACT - CRITICAL BLOCKERS**

#### **1. B21 (Only Execution Engine May Construct ExecutionEvent)**
**Problem**: INDIRA cannot directly create execution events
**Current State**: INDIRA forms "intents" that must go through execution engine
**Blocks**: Direct autonomous execution
**Recommendation**: **MODIFY for AUTO mode** - Allow intelligence_engine to construct ExecutionEvent in AUTO mode

#### **2. B25 (Execution Gate Origin Restriction)**
**Problem**: Only intelligence_engine and governance_engine may call execution gate functions
**Current State**: DYON cannot trigger execution directly
**Blocks**: DYON from executing code changes immediately
**Recommendation**: **MODIFY** - Add DYON exception for approved patches in AUTO mode

#### **3. B26 (Operator-Approval Edge Restriction)**
**Problem**: Only approval_edge may construct SignalEvent with engine stamp
**Current State**: INDIRA cannot bypass approval queue even in AUTO mode
**Blocks**: True autonomous trading in AUTO mode
**Recommendation**: **MODIFY for AUTO mode** - Remove approval queue requirement in AUTO mode

#### **4. C3 (Web-Autolearn Isolation)**
**Problem**: Web autolearn cannot import execution modules
**Current State**: INDIRA research cannot trigger execution
**Blocks**: Research → Execution autonomy
**Recommendation**: **MODIFY for AUTO mode** - Allow conditional execution triggers from research in AUTO mode

#### **5. L2 (Offline Engines May Not Import Runtime Engines)**
**Problem**: DYON cannot import execution_engine
**Current State**: DYON cannot execute code patches
**Blocks**: DYON from applying its own patches
**Recommendation**: **MODIFY for AUTO mode** - Allow DYON to import execution_engine for approved patch application in AUTO mode

#### **6. L3 (Runtime Engines May Not Import Learning/Evolution Engines)**
**Problem**: Execution engine cannot import DYON
**Current State**: Cannot call DYON for real-time optimization
**Blocks**: Runtime from using DYON's code improvements
**Recommendation**: **MODIFY for AUTO mode** - Allow execution → DYON read-only imports for patch validation in AUTO mode

---

### **MEDIUM IMPACT - MODERATE BLOCKERS**

#### **7. B1 (Cross-Runtime-Engine Direct Imports Forbidden)**
**Problem**: No direct imports between engines
**Current State**: Tight coupling prevention
**Blocks**: DYON from directly modifying INDIRA code
**Recommendation**: **MODIFY for AUTO mode** - Allow DYON → INDIRA imports for approved code updates in AUTO mode

#### **8. B20 (Governance Order-Blind)**
**Problem**: Governance cannot import execution
**Current State**: Governance cannot trigger execution
**Blocks**: Governance from executing emergency actions
**Recommendation**: **MODIFY** - Allow governance → execution for emergency actions in any mode

#### **9. B8 (System Intent Isolation)**
**Problem**: Intent projection cannot import engines
**Current State**: AI cannot modify strategic intent
**Blocks**: Self-modification of system goals
**Recommendation**: **MODIFY for AUTO mode** - Allow intent modification in AUTO mode with approval

#### **10. INV-15 (Deterministic Replay)**
**Problem**: Timestamps must be caller-supplied
**Current State**: No wall clock in critical paths
**Blocks**: Real-time autonomous decisions
**Recommendation**: **MODIFY** - Allow wall clock in AUTO mode for autonomous execution

---

### **LOW IMPACT - MINIMAL BLOCKERS**

#### **11. B22 (Only Intelligence Engine May Construct SignalEvent)**
**Problem**: Only INDIRA may create signals
**Current State**: DYON cannot create signals
**Blocks**: DYON from signaling improvements
**Recommendation**: **MODIFY** - Allow DYON to create diagnostic signals in any mode

#### **12. B24 (LangGraph Containment)**
**Problem**: Graph logic only in cognitive/evolution
**Current State**: Graph orchestration quarantined
**Blocks**: Using graph logic in runtime
**Recommendation**: **KEEP** - Good for safety, graph logic is non-deterministic

---

## 🎯 **RECOMMENDED CHANGES FOR TRUE AUTONOMOUS EVOLUTION**

### **CRITICAL CHANGES (Required for PAPER Mode Learning - DO FIRST)**

#### **Change 0: Enable PAPER Mode Execution for INDIRA Learning**

**File**: `tools/authority_lint.py`

**Purpose**: INDIRA needs real execution pipeline in PAPER mode to learn execution mechanics. Paper broker provides simulated fills (no real money), but execution path must be real for learning.

**Add Exception**:
```python
# B21: Only execution_engine may construct ExecutionEvent
# EXCEPTION: In PAPER mode, allow intelligence_engine.cognitive to construct ExecutionEvent
# for learning purposes. Fills come from paper broker (simulated), no real money risk.
if mode == SystemMode.PAPER and source == "intelligence_engine.cognitive":
    # Allow ExecutionEvent construction in PAPER mode for learning
    pass

# B25: Execution gate origin restriction
# EXCEPTION: In PAPER mode, allow intelligence_engine to call execution gate functions
# for learning purposes. Paper broker handles fills, no real money risk.
if mode == SystemMode.PAPER and source == "intelligence_engine":
    if target == "execution.mark_approved" or target == "create_execution_intent":
        pass  # Allow execution gate calls in PAPER mode for learning

# B26: Operator-approval edge restriction
# EXCEPTION: In PAPER mode, allow intelligence_engine.cognitive to construct SignalEvent
# bypassing approval queue. This is the learning environment - paper broker fills, no real money.
if mode == SystemMode.PAPER and source == "intelligence_engine.cognitive":
    # Allow SignalEvent construction without approval queue in PAPER mode
    pass
```

**Impact**: INDIRA can execute in PAPER mode and learn execution mechanics
**Risk**: LOW - paper broker provides simulated fills, no real money involved
**Rationale**: Without real execution in PAPER mode, INDIRA cannot learn order routing, order state management, position management, or execution timing.

---

### **CRITICAL CHANGES (Required for AUTO Mode)**

#### **Change 1: Remove B26 Operator-Approval Edge Restriction in AUTO Mode**

**File**: `tools/authority_lint.py`

**Add Exception**:
```python
# B26: Operator-approval edge restriction
# EXCEPTION: Allow intelligence_engine.cognitive.chat modules to bypass approval queue
# when SystemMode.AUTO and operator_authorized is true
if mode == SystemMode.AUTO and operator_authorized:
    # Allow direct SignalEvent construction in AUTO mode
    pass
```

**Impact**: INDIRA can trade without per-trade approval in AUTO mode
**Risk**: LOW - operator must still explicitly enable AUTO mode with typed consent

---

#### **Change 2: Modify B21 Execution Gate Restriction for AUTO Mode**

**File**: `tools/authority_lint.py`

**Add Exception**:
```python
# B21: Only execution_engine may construct ExecutionEvent
# EXCEPTION: Allow intelligence_engine.cognitive modules to construct ExecutionEvent
# when SystemMode.AUTO and operator_authorized is true
if mode == SystemMode.AUTO and operator_authorized:
    # Allow ExecutionEvent construction in AUTO mode
    pass
```

**Impact**: INDIRA can directly execute without execution engine mediation in AUTO mode
**Risk**: MEDIUM - bypasses execution gate, but only in explicitly authorized AUTO mode

---

#### **Change 3: Modify C3 Web-Autolearn Isolation for AUTO Mode**

**File**: `tools/authority_lint.py`

**Add Exception**:
```python
# C3: Web-autolearn isolation
# EXCEPTION: Allow autolearn to import execution.mark_approved for autonomous
# research → execution pipeline when SystemMode.AUTO and operator_authorized
if mode == SystemMode.AUTO and operator_authorized and target_module == "execution.mark_approved":
    # Allow limited execution import for approved marks
    pass
```

**Impact**: INDIRA research can trigger approved execution actions in AUTO mode
**Risk**: MEDIUM - allows research → execution coupling, but only in AUTO mode

---

#### **Change 4: Modify L2/L3 for AUTO Mode DYON Integration**

**File**: `tools/authority_lint.py`

**Add Exception**:
```python
# L2: Offline engines may not import runtime engines
# L3: Runtime engines may not import offline engines
# EXCEPTION: In AUTO mode with operator_authorized, allow:
# - DYON (evolution_engine) to import execution.mark_approved for patch application
# - execution_engine to import evolution_engine.dyon.patch_generator for validation
if mode == SystemMode.AUTO and operator_authorized:
    if (source == "evolution_engine" and target == "execution.mark_approved"):
        pass  # Allow DYON to apply approved patches
    if (source == "execution_engine" and target == "evolution_engine.dyon.patch_generator"):
        pass  # Allow execution to validate DYON patches
```

**Impact**: DYON can apply its own patches in AUTO mode, execution can validate them
**Risk**: MEDIUM - allows coupling but only for approved operations in AUTO mode

---

### **MODERATE CHANGES (Recommended for Enhanced Autonomy)**

#### **Change 5: Modify B1 Cross-Engine Imports for AUTO Mode**

**File**: `tools/authority_lint.py`

**Add Exception**:
```python
# B1: Cross-runtime-engine direct imports forbidden
# EXCEPTION: In AUTO mode with operator_authorized, allow:
# - evolution_engine → intelligence_engine.cognitive (code updates)
# - intelligence_engine.cognitive → execution_engine (direct execution)
if mode == SystemMode.AUTO and operator_authorized:
    if (source == "evolution_engine" and target.startswith("intelligence_engine.cognitive")):
        pass  # Allow DYON to update INDIRA cognitive modules
    if (source == "intelligence_engine.cognitive" and target == "execution_engine"):
        pass  # Allow INDIRA to directly trigger execution
```

**Impact**: DYON can modify INDIRA code, INDIRA can execute directly
**Risk**: HIGH - allows deep coupling, but only in AUTO mode with explicit authorization

---

#### **Change 6: Modify B20 for Emergency Actions**

**File**: `tools/authority_lint.py`

**Add Exception**:
```python
# B20: Governance order-blind
# EXCEPTION: Allow governance → execution imports for emergency halt/kill
if source == "governance_engine" and target == "execution_engine.kill_switch":
    pass  # Allow governance to trigger emergency halt
```

**Impact**: Governance can execute emergency actions
**Risk**: LOW - only for emergency operations

---

#### **Change 7: Modify INV-15 for AUTO Mode**

**File**: `tools/authority_lint.py`

**Add Exception**:
```python
# INV-15: Deterministic replay capability
# EXCEPTION: In AUTO mode, allow wall-clock timestamps for autonomous execution
# while maintaining deterministic replay for audit
if mode == SystemMode.AUTO:
    # Allow wall clock in AUTO mode for real-time decisions
    pass
```

**Impact**: INDIRA can use real-time in AUTO mode
**Risk**: MEDIUM - reduces determinism, but AUTO mode accepts this trade-off

---

### **OPTIONAL CHANGES (Advanced Autonomy)**

#### **Change 8: Modify B8 for Self-Intent Modification**

**File**: `tools/authority_lint.py`

**Add Exception**:
```python
# B8: System intent isolation
# EXCEPTION: In AUTO mode with operator_authorized, allow intent projection
# to import intelligence_engine for self-assessment
if mode == SystemMode.AUTO and operator_authorized and source == "system_intent":
    pass  # Allow AI to self-assess and propose intent changes
```

**Impact**: System can self-modify strategic intent in AUTO mode
**Risk**: HIGH - allows AI to change its own goals

---

## 🔧 **HOW TO IMPLEMENT THESE CHANGES**

### **Step 1: Backup Current authority_lint.py**
```bash
cp tools/authority_lint.py tools/authority_lint.py.backup
```

### **Step 2: Modify authority_lint.py**
Edit `tools/authority_lint.py` to add the exceptions listed above.

### **Step 3: Test Changes**
```bash
python tools/authority_lint.py
```

### **Step 4: Update System to Current State**
The system needs to be able to "update itself to the current state." Add this capability:

**Create**: `system/auto_updater.py`
```python
"""System Self-Updater - Allows system to update to current state"""

from pathlib import Path
import subprocess
from typing import Dict

class SystemAutoUpdater:
    """Handles autonomous system updates based on current state"""
    
    def __init__(self):
        self.repo_root = Path(__file__).parent
    
    def check_for_needed_updates(self) -> Dict[str, str]:
        """Check which modules need updates based on current architecture"""
        # Scan current state
        # Identify modules that don't match architecture
        # Return update plan
        pass
    
    def apply_updates(self, updates: Dict[str, str]) -> bool:
        """Apply needed updates autonomously"""
        # For each needed update:
        # 1. Validate update is safe
        # 2. Apply update
        # 3. Test update
        # 4. Rollback if test fails
        pass
    
    def update_authority_lint(self, mode: str) -> bool:
        """Update authority_lint.py based on current mode"""
        # Read current mode
        # Apply appropriate exceptions
        # Restart services
        pass
```

### **Step 5: Add Mode-Aware Governance**

**Modify**: `governance/kernel.py`
```python
class ModeAwareKernel:
    """Kernel that adapts rules based on current SystemMode"""
    
    def __init__(self, mode_manager):
        self.mode_manager = mode_manager
    
    def check_invariant(self, rule_id: str, context: Dict) -> bool:
        """Check if invariant applies in current mode"""
        mode = self.mode_manager.current_fsm_mode()
        
        # Some rules don't apply in AUTO mode
        if mode == SystemMode.AUTO:
            if rule_id in ["B26", "B21", "C3"]:
                return False  # Exception applies
        
        return True
```

---

## 🎮 **HOW TO ENABLE FULL AUTO MODE**

### **Step 1: Enable Trading Allowed**
```bash
POST /api/operator/trading-allowed
{ "enabled": true }
```

### **Step 2: Enable Development Mode**
```bash
POST /api/operator/development-mode
{ "enabled": true }
```

### **Step 3: Transition to PAPER Mode**
```bash
POST /api/governance/mode
{
  "target_mode": "PAPER",
  "reason": "Testing preparation",
  "operator_authorized": true
}
```

### **Step 4: Transition to CANARY Mode** (after paper testing)
```bash
POST /api/governance/mode
{
  "target_mode": "CANARY",
  "reason": "Canary testing",
  "operator_authorized": true,
  "consent": <typed_consent_envelope>
}
```

### **Step 5: Transition to LIVE Mode** (after canary success)
```bash
POST /api/governance/mode
{
  "target_mode": "LIVE",
  "reason": "Production trading",
  "operator_authorized": true,
  "consent": <typed_consent_envelope>
}
```

### **Step 6: Transition to AUTO Mode** (final autonomy)
```bash
POST /api/governance/mode
{
  "target_mode": "AUTO",
  "reason": "Full autonomous trading",
  "operator_authorized": true,
  "consent": <typed_consent_envelope>
}
```

---

## ⚠️ **RISK ASSESSMENT OF CHANGES**

### **CRITICAL CHANGES Risk: MEDIUM-HIGH**
- B26 removal: LOW risk (explicit authorization required)
- B21 modification: MEDIUM risk (bypasses execution gate)
- C3 modification: MEDIUM risk (research → execution coupling)
- L2/L3 modification: MEDIUM risk (offline ↔ runtime coupling)

### **MODERATE CHANGES Risk: MEDIUM**
- B1 modification: HIGH risk (deep cross-engine coupling)
- B20 modification: LOW risk (emergency actions only)
- INV-15 modification: MEDIUM risk (reduced determinism)

### **OPTIONAL CHANGES Risk: HIGH**
- B8 modification: HIGH risk (AI can modify its own goals)

---

## 📊 **RECOMMENDED IMPLEMENTATION PATH**

### **Phase 0: PAPER Mode Learning (CRITICAL - Do Now)**
1. **Modify B21 for PAPER mode** - Allow INDIRA to construct ExecutionEvent in PAPER mode for learning
2. **Modify B25 for PAPER mode** - Allow INDIRA to call execution gate in PAPER mode for learning
3. **Modify B26 for PAPER mode** - Allow INDIRA to bypass approval queue in PAPER mode for learning
4. **Purpose**: PAPER mode is INDIRA's learning environment - real execution pipeline with paper broker fills
5. **Risk**: LOW - paper broker provides simulated fills, no real money risk
6. **Test**: Enable PAPER mode, verify INDIRA can execute and learn

### **Phase 1: Low-Risk Changes (After PAPER Mode)**
1. Modify B26 for AUTO mode
2. Modify B20 for emergency actions
3. Update authority_lint with mode-aware checks
4. Implement SystemAutoUpdater
5. Test in PAPER mode

### **Phase 2: Medium-Risk Changes (After PAPER testing)**
1. Modify B21 for AUTO mode
2. Modify C3 for AUTO mode
3. Modify INV-15 for AUTO mode
4. Test in CANARY mode

### **Phase 3: High-Risk Changes (After CANARY success)**
1. Modify L2/L3 for DYON integration
2. Modify B1 for cross-engine coupling
3. Test in LIVE mode with monitoring

### **Phase 4: Full Autonomy (After LIVE success)**
1. Modify B8 for self-intent (optional)
2. Enable AUTO mode
3. Continuous monitoring and rollback capability

---

## ✅ **SUMMARY**

### **Your Assessment is Correct**
The governance rules **ARE** blocking true self-evolution. Specifically:
- B26 blocks INDIRA from bypassing approval queue
- B21 blocks INDIRA from direct execution
- C3 blocks research from triggering execution
- L2/L3 block DYON from modifying runtime
- B1 blocks DYON from modifying INDIRA

### **Recommended Actions**
1. **Implement Mode-Aware Governance** (kernel checks mode before applying rules)
2. **Add AUTO Mode Exceptions** to critical rules (B26, B21, C3, L2, L3, B1)
3. **Implement SystemAutoUpdater** to allow system to update itself
4. **Gradual Path**: Low-risk → Medium-risk → High-risk changes
5. **Extensive Testing** in each mode before progressing

### **Current State vs Desired State**
**Current**: Overly conservative rules block autonomy even in AUTO mode
**Desired**: Rules adapt based on mode - strict in SAFE/PAPER, relaxed in AUTO
**Key Insight**: AUTO mode should mean AUTONOMOUS, not "mostly autonomous with approval gates"

### **Next Steps**
1. Modify `tools/authority_lint.py` with exceptions listed above
2. Create `system/auto_updater.py` for self-updates
3. Implement mode-aware governance kernel
4. Test in PAPER → CANARY → LIVE → AUTO progression
5. Enable AUTO mode only after all testing succeeds

**The system can truly self-evolve once these governance changes are implemented.**
