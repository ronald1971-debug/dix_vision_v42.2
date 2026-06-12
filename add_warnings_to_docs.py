"""
Script to add verification warnings to all misleading "COMPLETE" documentation files.
"""

import os
from pathlib import Path

WARNING_HEADER = """⚠️ **DOCUMENTATION ACCURACY WARNING** ⚠️

This document claims components are "COMPLETE" or "production-ready".
**ACTUAL SYSTEM STATE (as of 2026-06-11):**
- System can bootstrap 100% (excellent core infrastructure)
- System CANNOT reach operational state (API mismatches in Tier 4)
- Many "complete" components have API mismatches preventing initialization
- System health is 50/100 (not 68-72/100 as claimed in docs)

**This documentation is NOT ACCURATE about current system state.**
See BOOT_TEST_EXECUTIVE_SUMMARY.md for actual boot test results.
See TRUE_SYSTEM_STATE_ASSESSMENT.md for code-based analysis.

---

"""

def add_warning_to_file(filepath):
    """Add warning header to a markdown file if not already present."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check if warning already present
        if "DOCUMENTATION ACCURACY WARNING" in content:
            return False  # Already has warning

        # Add warning at the beginning
        new_content = WARNING_HEADER + content

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)

        print(f"[OK] Added warning to: {filepath}")
        return True
    except Exception as e:
        print(f"[ERROR] Error processing {filepath}: {e}")
        return False

# List of files to update
FILES_TO_UPDATE = [
    "TIER2_INTELLIGENCE_COMPLETE.md",
    "TIER2_ADVANCED_INTELLIGENCE_COMPLETE.md",
    "TIER3_MODELING_SIMULATION_COMPLETE.md",
    "TIER4_MISSION_OPTIMIZATION_COMPLETE.md",
    "ALL_FEATURES_COMPLETE_REPORT.md",
    "ALL_REMAINING_COMPONENTS_IMPLEMENTED_COMPLETE.md",
    "ALL_PHASES_COMPLETE.md",
    "ALL_OPTIONS_COMPLETE.md",
    "FULL_INTEGRATION_MISSION_COMPLETE.md",
    "FULL_SYSTEM_ANALYSIS_COMPLETE.md",
    "FULL_COGNITIVE_INTEGRATION_COMPLETE.md",
    "FIVE_MAJOR_ORCHESTRATORS_INTEGRATION_COMPLETE.md",
    "CORE_ORCHESTRATORS_INTEGRATION_COMPLETE.md",
    "DYNAMIC_CAPABILITY_FOUNDATION_COMPLETE.md",
    "FEATURE_FLAGS_ACTIVATION_COMPLETE.md",
    "CONSOLIDATION_COMPLETE.md",
    "FULL_CONSOLIDATION_COMPLETE.md",
    "DOCUMENTATION_CONSOLIDATION_COMPLETE.md",
    "DOCUMENTATION_FIX_COMPLETE.md",
    "IMPORT_MIGRATION_COMPLETE.md",
    "INDIRA_DYON_ENHANCEMENTS_IMPLEMENTATION_COMPLETE.md",
    "INDIRA_TRADING_INTELLIGENCE_COMPLETE.md",
    "INDIRA_TRADING_INTELLIGENCE_ENHANCEMENT_COMPLETE.md",
    "DYON_ARCHITECTURAL_CORRECTION_COMPLETE.md",
    "DYON_INTELLIGENCE_ENGINE_INTEGRATION_COMPLETE.md",
    "DYON_LEARNING_ENGINE_INTEGRATION_COMPLETE.md",
    "DYON_MODELING_INTEGRATION_COMPLETE.md",
    "DYON_SIMULATION_ENGINE_INTEGRATION_COMPLETE.md",
    "DYON_SYSTEM_ENGINE_INTEGRATION_COMPLETE.md",
    "MODULAR_ARCHITECTURE_COMPLETE.md",
    "COMPLETE_SYSTEM_INTEGRATION.md",
    "VALIDATION_COMPLETE.md",
    "FINAL_SESSION_COMPLETE.md",
    "SESSION_COMPLETE.md",
    "ULTIMATE_SESSION_COMPLETE.md",
    "PHASE2_COMPLETE_FINAL.md",
    "PHASE2.1_COMPLETE_REPORT.md",
    "PHASE3_COMPLETE.md",
    "AI_PROVIDERS_IMPLEMENTATION_COMPLETE.md",
    "DIX_VISION_DESKTOP_INTEGRATION_COMPLETE.md",
]

# Process each file
base_dir = Path("C:/dix_vision_v42.2")
updated_count = 0
skipped_count = 0

for filename in FILES_TO_UPDATE:
    filepath = base_dir / filename
    if filepath.exists():
        if add_warning_to_file(filepath):
            updated_count += 1
        else:
            skipped_count += 1
    else:
        print(f"[WARN] File not found: {filename}")

print(f"\n[SUMMARY]")
print(f"  Updated: {updated_count}")
print(f"  Skipped (already has warning): {skipped_count}")
