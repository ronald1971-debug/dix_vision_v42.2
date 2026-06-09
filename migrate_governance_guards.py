#!/usr/bin/env python3
"""
Governance Guard Migration Script

Automated migration of governance guards from separate systems into the unified
governance_engine/domains/ structure while preserving exact functionality.
"""

import re
from pathlib import Path

# Migration mapping: (source, destination, domain)
MIGRATION_MAP = [
    # Cognitive domain guards
    ("cognitive_governance/causal_consistency.py", "governance_engine/domains/cognitive/", "cognitive"),
    ("cognitive_governance/epistemic_drift.py", "governance_engine/domains/cognitive/", "cognitive"),
    ("cognitive_governance/hallucination_guard.py", "governance_engine/domains/cognitive/", "cognitive"),
    ("cognitive_governance/identity_stability.py", "governance_engine/domains/cognitive/", "cognitive"),
    ("cognitive_governance/learning_truthfulness.py", "governance_engine/domains/cognitive/", "cognitive"),
    ("cognitive_governance/memory_contamination.py", "governance_engine/domains/cognitive/", "cognitive"),
    ("cognitive_governance/mutation_validator.py", "governance_engine/domains/cognitive/", "cognitive"),
    ("cognitive_governance/reward_hacking_detector.py", "governance_engine/domains/cognitive/", "cognitive"),
    ("cognitive_governance/strategy_lineage_guard.py", "governance_engine/domains/cognitive/", "cognitive"),
    ("cognitive_governance/synthetic_feedback_detection.py", "governance_engine/domains/cognitive/", "cognitive"),
    ("cognitive_governance/cognitive_constitution.py", "governance_engine/domains/cognitive/", "cognitive"),
    ("cognitive_governance/learning_coherence.py", "governance_engine/domains/cognitive/", "cognitive"),
    ("cognitive_governance/cognitive_physics.py", "governance_engine/domains/cognitive/", "cognitive"),
    ("cognitive_governance/knowledge_lifecycle.py", "governance_engine/domains/cognitive/", "cognitive"),
    
    # Financial domain guards
    ("financial_governance/capital_throttle.py", "governance_engine/domains/financial/", "financial"),
    ("financial_governance/execution_hazard.py", "governance_engine/domains/financial/", "financial"),
    ("financial_governance/exposure_guard.py", "governance_engine/domains/financial/", "financial"),
    ("financial_governance/leverage_monitor.py", "governance_engine/domains/financial/", "financial"),
    ("financial_governance/liquidation_sentinel.py", "governance_engine/domains/financial/", "financial"),
    
    # Operator domain guards
    ("operator_governance/authority_escalation.py", "governance_engine/domains/operator/", "operator"),
    ("operator_governance/consent_router.py", "governance_engine/domains/operator/", "operator"),
    ("operator_governance/governance_visibility.py", "governance_engine/domains/operator/", "operator"),
    ("operator_governance/manual_lockout.py", "governance_engine/domains/operator/", "operator"),
    ("operator_governance/override_priority.py", "governance_engine/domains/operator/", "operator"),
    
    # System domain guards
    ("system_governance/contract_integrity.py", "governance_engine/domains/system/", "system"),
    ("system_governance/convergence_monitor.py", "governance_engine/domains/system/", "system"),
    ("system_governance/dependency_validator.py", "governance_engine/domains/system/", "system"),
    ("system_governance/replay_integrity.py", "governance_engine/domains/system/", "system"),
    ("system_governance/runtime_consistency.py", "governance_engine/domains/system/", "system"),
    ("system_governance/topology_guard.py", "governance_engine/domains/system/", "system"),
]

# Module reference updates
MODULE_UPDATES = {
    "cognitive_governance": "governance_engine.domains.cognitive",
    "financial_governance": "governance_engine.domains.financial", 
    "operator_governance": "governance_engine.domains.operator",
    "system_governance": "governance_engine.domains.system",
}


def update_module_references(content: str, old_module: str, new_module: str) -> str:
    """Update module references in file content."""
    # Update docstrings
    content = re.sub(
        r'cognitive_governance/([\w_]+)',
        'governance_engine/domains/cognitive/\\1',
        content
    )
    content = re.sub(
        r'financial_governance/([\w_]+)',
        'governance_engine/domains/financial/\\1',
        content
    )
    content = re.sub(
        r'operator_governance/([\w_]+)',
        'governance_engine/domains/operator/\\1',
        content
    )
    content = re.sub(
        r'system_governance/([\w_]+)',
        'governance_engine/domains/system/\\1',
        content
    )
    
    # Update event source references
    content = re.sub(
        r'"cognitive_governance\.([\w_]+)"',
        '"governance_engine.domains.cognitive.\\1"',
        content
    )
    content = re.sub(
        r'"financial_governance\.([\w_]+)"',
        '"governance_engine.domains.financial.\\1"',
        content
    )
    content = re.sub(
        r'"operator_governance\.([\w_]+)"',
        '"governance_engine.domains.operator.\\1"',
        content
    )
    content = re.sub(
        r'"system_governance\.([\w_]+)"',
        '"governance_engine.domains.system.\\1"',
        content
    )
    
    return content


def migrate_guard(source_path: str, dest_dir: str, domain: str) -> bool:
    """Migrate a single guard file."""
    try:
        source_file = Path(source_path)
        if not source_file.exists():
            print(f"  ⚠️  Source file not found: {source_path}")
            return False
        
        dest_path = Path(dest_dir) / source_file.name
        dest_file = Path(dest_path)
        
        # Read source content
        with open(source_file, encoding='utf-8') as f:
            content = f.read()
        
        # Update module references
        old_module = source_path.split('/')[0]
        new_module = f"governance_engine.domains.{domain}"
        content = update_module_references(content, old_module, new_module)
        
        # Update docstring to indicate migration
        lines = content.split('\n')
        if lines and '"""' in lines[0]:
            # Add migration note after first docstring line
            lines.insert(1, f'Migrated from {source_path}')
            content = '\n'.join(lines)
        
        # Write to destination
        dest_file.parent.mkdir(parents=True, exist_ok=True)
        with open(dest_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"  ✅ Migrated: {source_file.name} → {dest_path}")
        return True
        
    except Exception as e:
        print(f"  ❌ Failed to migrate {source_path}: {e}")
        return False


def update_domain_init(domain: str, guards: list[str]) -> None:
    """Update __init__.py file for a domain."""
    init_path = Path(f"governance_engine/domains/{domain}/__init__.py")
    
    try:
        with open(init_path, encoding='utf-8') as f:
            content = f.read()
        
        # Extract class names from guard filenames
        imports = []
        for guard in guards:
            # Convert filename to class name (e.g., belief_integrity.py → BeliefIntegrity)
            class_name = ''.join(word.capitalize() for word in guard.replace('.py', '').split('_'))
            # Handle special cases
            if 'kill_switch' in guard:
                class_name = 'KillSwitch'
            elif 'operator_constitution' in guard:
                class_name = 'OperatorConstitution'
            
            module_name = guard.replace('.py', '')
            factory_name = f"get_{module_name}"
            
            imports.append(f"from .{module_name} import {class_name}, {factory_name}")
        
        # Replace the comment block with actual imports
        import_block = '\n'.join(imports)
        content = re.sub(
            r'# Guard imports will be added during migration.*?(?=\n__all__)',
            import_block + '\n',
            content,
            flags=re.DOTALL
        )
        
        # Update __all__
        all_exports = []
        for guard in guards:
            module_name = guard.replace('.py', '')
            class_name = ''.join(word.capitalize() for word in module_name.split('_'))
            if 'kill_switch' in guard:
                class_name = 'KillSwitch'
            elif 'operator_constitution' in guard:
                class_name = 'OperatorConstitution'
            
            factory_name = f"get_{module_name}"
            all_exports.extend([class_name, factory_name])
        
        content = re.sub(
            r'__all__ = \[\]',
            f'__all__ = {all_exports}',
            content
        )
        
        with open(init_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        print(f"  ✅ Updated {domain}/__init__.py")
        
    except Exception as e:
        print(f"  ❌ Failed to update {domain}/__init__.py: {e}")


def main():
    """Execute the migration."""
    print("🚀 Starting Governance Guard Migration...")
    print(f"📋 Total guards to migrate: {len(MIGRATION_MAP)}")
    
    # Group by domain
    by_domain: dict[str, list[str]] = {
        "cognitive": [],
        "financial": [],
        "operator": [],
        "system": []
    }
    
    success_count = 0
    fail_count = 0
    
    for source, dest, domain in MIGRATION_MAP:
        print(f"\n📦 Migrating {source}")
        if migrate_guard(source, dest, domain):
            success_count += 1
            by_domain[domain].append(Path(source).name)
        else:
            fail_count += 1
    
    # Update domain __init__.py files
    print("\n📝 Updating domain __init__.py files...")
    for domain, guards in by_domain.items():
        if guards:
            update_domain_init(domain, guards)
    
    # Summary
    print(f"\n{'='*60}")
    print("✅ Migration Complete!")
    print(f"   Success: {success_count}")
    print(f"   Failed: {fail_count}")
    print(f"   Total: {len(MIGRATION_MAP)}")
    print(f"{'='*60}")
    
    print("\n📊 Domain Breakdown:")
    for domain, guards in by_domain.items():
        print(f"   {domain}: {len(guards)} guards")


if __name__ == "__main__":
    main()