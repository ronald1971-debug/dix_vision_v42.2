#!/usr/bin/env python3
"""
Simplified Governance Guard Migration Script
"""

import re
from pathlib import Path


def migrate_file(source: str, dest: str, domain: str) -> bool:
    """Migrate a single file with module reference updates."""
    try:
        source_path = Path(source)
        dest_path = Path(dest)
        
        if not source_path.exists():
            print(f"❌ Source not found: {source}")
            return False
            
        # Read source
        with open(source_path, encoding='utf-8') as f:
            content = f.read()
        
        # Update module references
        old_domain = source.split('/')[0]
        new_domain = f"governance_engine.domains.{domain}"
        
        # Update file paths in docstrings
        content = re.sub(
            f'{old_domain}/([\\w_]+)',
            f'governance_engine/domains/{domain}/\\1',
            content
        )
        
        # Update event source references
        content = re.sub(
            f'"{old_domain}\\.([\\w_]+)"',
            f'"governance_engine.domains.{domain}.\\1"',
            content
        )
        
        # Add migration note to docstring
        lines = content.split('\n')
        if lines and '"""' in lines[0]:
            lines.insert(1, f'Migrated from {source}')
            content = '\n'.join(lines)
        
        # Write destination
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        with open(dest_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        print(f"✅ {source_path.name} → {dest_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error migrating {source}: {e}")
        return False

def main():
    """Execute migration focusing on financial domain first."""
    print("🚀 Starting Guard Migration...")
    
    # Financial domain priority (most critical)
    financial_guards = [
        "capital_throttle.py",
        "execution_hazard.py", 
        "leverage_monitor.py",
        "liquidation_sentinel.py"
    ]
    
    print("\n📊 PRIORITY: Financial Domain")
    success_count = 0
    for guard in financial_guards:
        source = f"financial_governance/{guard}"
        dest = f"governance_engine/domains/financial/{guard}"
        if migrate_file(source, dest, "financial"):
            success_count += 1
    
    # Operator domain (second priority)
    operator_guards = [
        "authority_escalation.py",
        "consent_router.py",
        "governance_visibility.py", 
        "manual_lockout.py",
        "override_priority.py"
    ]
    
    print("\n📊 PRIORITY: Operator Domain")
    for guard in operator_guards:
        source = f"operator_governance/{guard}"
        dest = f"governance_engine/domains/operator/{guard}"
        if migrate_file(source, dest, "operator"):
            success_count += 1
    
    # System domain (third priority)
    system_guards = [
        "contract_integrity.py",
        "convergence_monitor.py",
        "dependency_validator.py",
        "replay_integrity.py",
        "runtime_consistency.py",
        "topology_guard.py"
    ]
    
    print("\n📊 PRIORITY: System Domain")
    for guard in system_guards:
        source = f"system_governance/{guard}"
        dest = f"governance_engine/domains/system/{guard}"
        if migrate_file(source, dest, "system"):
            success_count += 1
    
    # Cognitive domain (most files, do last)
    cognitive_guards = [
        "causal_consistency.py",
        "epistemic_drift.py",
        "hallucination_guard.py",
        "identity_stability.py",
        "learning_truthfulness.py",
        "memory_contamination.py",
        "mutation_validator.py",
        "reward_hacking_detector.py",
        "strategy_lineage_guard.py",
        "synthetic_feedback_detection.py",
        "cognitive_constitution.py",
        "learning_coherence.py",
        "cognitive_physics.py",
        "knowledge_lifecycle.py"
    ]
    
    print("\n📊 PRIORITY: Cognitive Domain")
    for guard in cognitive_guards:
        source = f"cognitive_governance/{guard}"
        dest = f"governance_engine/domains/cognitive/{guard}"
        if migrate_file(source, dest, "cognitive"):
            success_count += 1
    
    total = len(financial_guards) + len(operator_guards) + len(system_guards) + len(cognitive_guards)
    print(f"\n{'='*50}")
    print(f"✅ Migration Complete: {success_count}/{total}")
    print(f"{'='*50}")

if __name__ == "__main__":
    main()