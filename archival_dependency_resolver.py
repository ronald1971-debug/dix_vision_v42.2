"""
Archival Dependency Resolver - Systematic Resolution of Archival-to-Archival Dependencies
Phase 1: Resolve 214 internal archival dependencies
NO LAZY LOADING - Direct imports only
"""

import os
import re
from typing import Dict, List, Set
from pathlib import Path

class ArchivalDependencyResolver:
    """Resolve archival component dependencies by updating import paths"""
    
    def __init__(self):
        self.archival_files: List[str] = []
        self.dependency_graph: Dict[str, Set[str]] = {}
        self.dependency_replacements: Dict[str, str] = {
            # Map archival internal dependencies to new infrastructure modules
            'execution.order_manager': 'mind.order_manager',
            'execution.portfolio_manager': 'mind.portfolio_manager',
            'operator_governance': 'operator_governance',
            'system': 'system_unified',
            'execution.core': 'execution_unified.core',
            'execution.live_trading': 'execution_unified.live_trading',
            'execution.slippage': 'execution_unified.slippage',
            'execution.adapters': 'execution_unified.core.adapters',
            'execution.hot_path': 'execution_unified.core.hot_path',
            'execution.intelligence': 'execution_unified.core.intelligence',
            'execution.lifecycle': 'execution_unified.core.lifecycle',
            'execution.market_data': 'execution_unified.core.market_data',
            'execution.offline': 'execution_unified.core.offline',
            'execution.paper_trading': 'execution_unified.core.paper_trading',
        }
        
    def scan_archival_components(self):
        """Scan all archival components for dependencies"""
        for root, dirs, files in os.walk('execution_unified'):
            if 'archive' in root.lower():
                for file in files:
                    if file.endswith('.py') and file != '__init__.py':
                        file_path = os.path.join(root, file)
                        relative_path = os.path.relpath(file_path, 'execution_unified')
                        self.archival_files.append(relative_path)
        
        for root, dirs, files in os.walk('governance_unified'):
            if 'archive' in root.lower() or 'legacy' in root.lower():
                for file in files:
                    if file.endswith('.py') and file != '__init__.py':
                        file_path = os.path.join(root, file)
                        relative_path = os.path.relpath(file_path, 'governance_unified')
                        self.archival_files.append(relative_path)
        
        print(f"Found {len(self.archival_files)} archival components")
        
    def resolve_archival_imports(self, file_path: str) -> int:
        """Resolve archival imports in a single file"""
        # Determine the correct base directory based on actual file location
        is_execution = (
            'execution_archived' in file_path or 
            'engine_archive' in file_path or 
            'adapters_archive' in file_path or 
            'hazard_archive' in file_path or 
            'live_trading_archive' in file_path or 
            'monitoring_archive' in file_path or 
            'confirmations_archive' in file_path or 
            'algos_archive' in file_path or 
            file_path.endswith('_archive.py')
        )
        
        if is_execution:
            full_path = os.path.join('execution_unified', file_path)
        else:
            # Default to governance_unified for legacy_archive and governance_engine
            full_path = os.path.join('governance_unified', file_path)
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            replacements_made = 0
            
            # Apply dependency replacements
            for old_import, new_import in self.dependency_replacements.items():
                # Replace from imports
                if f'from {old_import}' in content:
                    content = content.replace(f'from {old_import}', f'from {new_import}')
                    replacements_made += 1
                # Replace direct imports
                if f'import {old_import}' in content:
                    content = content.replace(f'import {old_import}', f'import {new_import}')
                    replacements_made += 1
            
            # Only write back if changes were made
            if content != original_content:
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            
            return replacements_made
            
        except Exception as e:
            print(f"Error resolving {file_path}: {e}")
            return 0
    
    def resolve_all_archival_dependencies(self):
        """Resolve all archival dependencies systematically"""
        print("Resolving archival-to-archival dependencies...")
        
        total_replacements = 0
        files_modified = 0
        
        for file_path in self.archival_files:
            replacements = self.resolve_archival_imports(file_path)
            if replacements > 0:
                total_replacements += replacements
                files_modified += 1
                print(f"Modified {file_path}: {replacements} replacements")
        
        print(f"\nDependency resolution complete:")
        print(f"Files modified: {files_modified}/{len(self.archival_files)}")
        print(f"Total replacements: {total_replacements}")
        
        return total_replacements, files_modified

def main():
    """Main execution function"""
    print("=" * 80)
    print("PHASE 1: ARCHIVAL DEPENDENCY RESOLUTION")
    print("Resolving 214 archival-to-archival dependencies")
    print("=" * 80)
    
    resolver = ArchivalDependencyResolver()
    
    # Scan archival components
    print("\nScanning archival components...")
    resolver.scan_archival_components()
    
    # Resolve dependencies
    print("\nResolving dependencies...")
    total_replacements, files_modified = resolver.resolve_all_archival_dependencies()
    
    print("\n" + "=" * 80)
    print("ARCHIVAL DEPENDENCY RESOLUTION COMPLETE")
    print("=" * 80)
    
    return total_replacements, files_modified

if __name__ == '__main__':
    result = main()