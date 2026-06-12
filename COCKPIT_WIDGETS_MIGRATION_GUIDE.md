# Cockpit Widgets Migration Guide

**Purpose:** Document the migration path for cockpit widgets to the cognitive control center, ensuring zero feature loss.

**Status:** Widgets preserved in cockpit/ for backward compatibility during migration.

---

## Cockpit Widgets Overview

The cockpit directory contains 9 widgets that provide specialized UI functionality:

1. **alert_center.py** - Alert management and notification center
2. **decision_trace.py** - Decision trace and audit logging
3. **governance_panel.py** - Governance controls and policy management
4. **kill_switch.py** - Emergency kill switch
5. **master_sliders.py** - Master control sliders
6. **plugin_manager.py** - Plugin lifecycle management
7. **portfolio_view.py** - Portfolio visualization and management
8. **risk_view.py** - Risk visualization and monitoring
9. **system_health.py** - System health monitoring

---

## Migration Strategy

### Phase 1: Widget Feature Audit (COMPLETED ✅)

All 9 widgets have been audited in `ZERO_FEATURE_LOSS_AUDIT.md`:
- ✅ Features documented
- ✅ Dependencies identified
- ✅ Integration points mapped
- ✅ Migration paths defined

### Phase 2: Migration Approach

Given that:
1. The cockpit static frontend (`cockpit/static/`) is being replaced by the cognitive operating environment UI
2. Dashboard2026 provides more advanced React components
3. Widgets will be transformed into cognitive environment workspace components

**Strategy: Defer widget migration to Phase 3 (Dashboard Transformation)**

Rationale:
- Backend services (auth, chat, llm, qr, pairing) are critical and must be migrated first ✅ COMPLETED
- Widget functionality will be reimplemented as part of the cognitive operating environment UI
- This prevents duplicate work and ensures widget features are enhanced with cognitive environment capabilities
- Cockpit widgets remain functional during transition through compatibility layer

### Phase 3: Widget Transformation (FUTURE)

When transforming Dashboard2026 to cognitive operating environment:

1. **Alert Center** → Cognitive Operations Center → Real-time alert feeds with cognitive context
2. **Decision Trace** → Agent Operations Center → Enhanced with agent timeline integration
3. **Governance Panel** → Mission Control → Enhanced with mode manager integration
4. **Kill Switch** → Mission Control → Integrated with cognitive environment
5. **Master Sliders** → Mission Control → Integrated with workspace controls
6. **Plugin Manager** → Shared Services → Enhanced with cognitive environment awareness
7. **Portfolio View** → INDIRA Workspace → Integrated with trading cognitive processes
8. **Risk View** → Mission Control → Enhanced with real-time cognitive feeds
9. **System Health** → Agent Operations Center → Integrated with agent observability

---

## Widget Migration Matrix

| Cockpit Widget | Target Location | Enhancement | Priority |
|---|---|---|---|
| alert_center.py | mission_control/alert_center.py | Real-time cognitive context | P2 |
| decision_trace.py | agent_operations_center/decision_trace.py | Agent timeline integration | P2 |
| governance_panel.py | mission_control/governance_panel.py | Mode manager integration | P2 |
| kill_switch.py | mission_control/kill_switch.py | Cognitive environment integration | P2 |
| master_sliders.py | mission_control/master_controls.py | Workspace controls | P2 |
| plugin_manager.py | shared_services/plugin_manager.py | Cognitive environment awareness | P3 |
| portfolio_view.py | unified_workspaces/portfolio_view.py | INDIRA workspace integration | P2 |
| risk_view.py | mission_control/risk_monitor.py | Real-time cognitive feeds | P2 |
| system_health.py | mission_control/system_health.py | Agent operations center integration | P2 |

---

## Zero Feature Loss Guarantees

### During Migration Period
- **cockpit/widgets/** remains functional and accessible
- All widget features continue to work through existing cockpit backend
- No functionality is removed until replacements are available
- Compatibility layer ensures smooth transition

### After Migration
- Every widget feature will be preserved in cognitive environment
- Features will be enhanced with cognitive capabilities
- Integration with agent operations center for real-time observability
- Workspace-based model for better user experience

### Migration Validation
- ✅ Feature parity checklist for each widget
- ⏳ UI component comparison tests
- ⏳ Widget functionality validation
- ⏳ User acceptance testing
- ⏳ Performance validation

---

## Implementation Steps (When Ready)

### Step 1: Widget Feature Documentation
For each widget:
- Document all features and behaviors
- Document API dependencies
- Document state management
- Document user interactions

### Step 2: Cognitive Environment Integration
For each widget:
- Design cognitive environment integration points
- Add agent operations center connections
- Add real-time activity feed integration
- Add workspace context awareness

### Step 3: React Component Implementation
For each widget:
- Implement as React component in cognitive environment
- Preserve all widget functionality
- Add cognitive enhancements
- Test thoroughly

### Step 4: Validation
For each widget:
- Feature parity validation
- Integration testing
- User acceptance testing
- Performance validation

### Step 5: Removal
After validation:
- Remove from cockpit/widgets/
- Update documentation
- Archive old code

---

## Current Status

### ✅ COMPLETED
- Backend service migration (auth, chat, llm, qr, pairing)
- ui/cockpit_routes.py updated to use cognitive control center
- Feature audit completed
- Migration guide created

### ⏳ DEFERRED (To Phase 3)
- Widget component migration (deferred to Dashboard2026 transformation)
- Widget UI enhancements (deferred to cognitive environment UI)

### ✅ PRESERVED
- All widgets remain functional in cockpit/
- Zero feature loss during migration period
- Compatibility layer ensures smooth transition

---

## Notes

**Why defer widget migration?**

1. **Strategic Priority**: Backend services are more critical for the cognitive operating environment foundation
2. **Avoid Duplication**: Widget functionality will be reimplemented as part of Dashboard2026 → Cognitive Environment transformation
3. **Enhanced Integration**: Widgets will be enhanced with cognitive environment capabilities, not just copied
4. **Efficiency**: Prevents duplicate work and ensures better final architecture
5. **Zero Risk**: Cockpit widgets remain functional during transition

**Zero Feature Loss Maintained:**
- All widget features are documented and preserved
- Migration path is clearly defined
- No functionality is removed until enhanced replacements are available
- Transition period ensures smooth user experience