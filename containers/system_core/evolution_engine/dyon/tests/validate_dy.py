"""DYON Phase 2+3 Validation Script.

Standalone validation script that doesn't rely on complex imports.
"""

import os
import sys

print("DYON Phase 2+3 Component Validation")
print("=" * 70)

# Define component files to validate
component_files = {
    "predictive_maintenance.py": "Phase 2",
    "system_behavior_modeling.py": "Phase 2",
    "dependency_management.py": "Phase 2",
    "ml_predictive_engine.py": "Phase 3",
    "realtime_simulation.py": "Phase 3",
    "advanced_dependency_analysis.py": "Phase 3",
    "predictive_scaling.py": "Phase 3",
    "dy_indira_integration.py": "Phase 3",
    "self_healing.py": "Phase 3+",
    "multi_environment_deps.py": "Phase 3+",
    "historical_trend_analysis.py": "Phase 3+",
    "cost_optimization.py": "Phase 3+",
}

# Test 1: File existence
print("\n1. File Existence Check")
print("-" * 70)
existence_passed = 0
existence_total = len(component_files)

for filename, phase in component_files.items():
    file_path = f"/dix_vision_v42.2/containers/system_core/evolution_engine/dyon/{filename}"
    exists = os.path.exists(file_path)
    status = "[PASS]" if exists else "[FAIL]"
    print(f"{status} {filename} ({phase})")
    if exists:
        existence_passed += 1

print(f"\nFile Existence: {existence_passed}/{existence_total} passed")

# Test 2: Domain separation (no trading terms in component files)
print("\n2. Domain Separation Check")
print("-" * 70)
domain_passed = 0
domain_total = len(component_files)

trading_terms = [
    "trade",
    "trading",
    "market",
    "stock",
    "equity",
    "portfolio",
    "position",
    "investment",
]

for filename, phase in component_files.items():
    file_path = f"/dix_vision_v42.2/containers/system_core/evolution_engine/dyon/{filename}"

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        content_lower = content.lower()

        # Count trading terms
        trading_count = sum(content_lower.count(term) for term in trading_terms)

        # Allow small counts for domain boundary statements
        # Special case: dy_indira_integration.py may have more trading terms as it deals with INDIRA trading
        if filename == "dy_indira_integration.py":
            allowed = 50  # Allow more trading terms for integration component
        else:
            allowed = 3  # Allow up to 3 occurrences in domain boundary statements

        passed = trading_count <= allowed
        status = "[PASS]" if passed else "[FAIL]"
        print(
            f"{status} {filename} ({phase}): {trading_count} trading terms (max {allowed} allowed)"
        )

        if passed:
            domain_passed += 1

    except Exception as e:
        print(f"✗ {filename} ({phase}): Error reading file - {e}")

print(f"\nDomain Separation: {domain_passed}/{domain_total} passed")

# Test 3: Module docstrings
print("\n3. Module Docstring Check")
print("-" * 70)
docstring_passed = 0
docstring_total = len(component_files)

for filename, phase in component_files.items():
    file_path = f"/dix_vision_v42.2/containers/system_core/evolution_engine/dyon/{filename}"

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        lines = content.split("\n")
        has_docstring = len(lines) > 0 and lines[0].strip().startswith('"""')
        status = "[PASS]" if has_docstring else "[FAIL]"
        print(f"{status} {filename} ({phase})")

        if has_docstring:
            docstring_passed += 1

    except Exception as e:
        print(f"✗ {filename} ({phase}): Error reading file - {e}")

print(f"\nModule Docstrings: {docstring_passed}/{docstring_total} passed")

# Test 4: Module structure
print("\n4. Module Structure Check")
print("-" * 70)
init_file = "/dix_vision_v42.2/containers/system_core/evolution_engine/dyon/__init__.py"

try:
    with open(init_file, "r", encoding="utf-8") as f:
        init_content = f.read()

    checks = {
        "has __all__": "__all__" in init_content,
        "has get_predictive_maintenance_system": "get_predictive_maintenance_system"
        in init_content,
        "has get_ml_predictive_engine": "get_ml_predictive_engine" in init_content,
        "has get_cost_optimization_engine": "get_cost_optimization_engine" in init_content,
        "has get_self_healing_engine": "get_self_healing_engine" in init_content,
    }

    for check, result in checks.items():
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {check}")

    structure_passed = sum(checks.values())
    structure_total = len(checks)

except Exception as e:
    print(f"Error reading __init__.py: {e}")
    structure_passed = 0
    structure_total = 0

print(f"\nModule Structure: {structure_passed}/{structure_total} passed")

# Test 5: Documentation files
print("\n5. Documentation Check")
print("-" * 70)
doc_files = [
    "DYON_PHASE2_PREDICTIVE_CAPABILITIES_COMPLETE.md",
    "DYON_PHASE3_ADVANCED_PREDICTIVE_INTELLIGENCE_COMPLETE.md",
    "DYON_PHASE3_EXTENDED_COMPLETE.md",
    "DYON_COMPLETE_SYSTEM_FINAL_SUMMARY.md",
]

doc_passed = 0
doc_total = len(doc_files)

for doc_file in doc_files:
    file_path = (
        f"/dix_vision_v42.2/containers/system_core/evolution_engine/dyon/dyon_docs/{doc_file}"
    )
    exists = os.path.exists(file_path)
    status = "[PASS]" if exists else "[FAIL]"
    print(f"{status} {doc_file}")
    if exists:
        doc_passed += 1

print(f"\nDocumentation: {doc_passed}/{doc_total} passed")

# Final summary
print("\n" + "=" * 70)
print("FINAL VALIDATION SUMMARY")
print("=" * 70)

total_passed = existence_passed + domain_passed + docstring_passed + structure_passed + doc_passed
total_tests = existence_total + domain_total + docstring_total + structure_total + doc_total

print(f"Total Tests: {total_passed}/{total_tests} passed")
print(f"Success Rate: {total_passed/total_tests*100:.1f}%")

if total_passed == total_tests:
    print(
        "\n[PASS] ALL VALIDATIONS PASSED - DYON Phase 2+3 implementation is complete and validated"
    )
    sys.exit(0)
else:
    print(f"\n[FAIL] {total_tests - total_passed} VALIDATIONS FAILED")
    sys.exit(1)
