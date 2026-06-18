"""
Automated Import Path Fixer for 394 Archival Components
Phase 3: Systematic Import Path Fixing - DIRECT IMPORTS ONLY, NO LAZY LOADING
"""

import os
import re
import sys
from pathlib import Path

class ImportPathFixer:
    """Fix import paths in archival components to work in unified system"""
    
    def __init__(self):
        self.files_processed = 0
        self.files_with_errors = 0
        self.import_fixes_applied = 0
        
    def fix_import_paths(self, file_path):
        """Fix import paths in a single file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            fixes_applied = 0
            
            # Import path replacements (NO LAZY LOADING - DIRECT IMPORTS)
            
            # Replace execution.* with execution_unified.*
            if 'from execution.' in content or 'import execution.' in content:
                content = re.sub(r'from execution\.', 'from execution_unified.', content)
                content = re.sub(r'import execution\.', 'import execution_unified.', content)
                fixes_applied += 1
            
            # Replace execution_engine.* with execution_unified.core.*
            if 'from execution_engine.' in content or 'import execution_engine.' in content:
                content = re.sub(r'from execution_engine\.', 'from execution_unified.core.', content)
                content = re.sub(r'import execution_engine\.', 'import execution_unified.core.', content)
                fixes_applied += 1
            
            # Replace governance_engine.* with governance_unified.*
            if 'from governance_engine.' in content or 'import governance_engine.' in content:
                content = re.sub(r'from governance_engine\.', 'from governance_unified.', content)
                content = re.sub(r'import governance_engine\.', 'import governance_unified.', content)
                fixes_applied += 1
            
            # Replace governance.* with governance_unified.* (where appropriate)
            # Be careful not to replace governance_unified.* -> governance_unified.governance_unified.*
            if 'from governance.' in content and 'from governance_unified.' not in content:
                # Only replace if it's not already governance_unified
                if 'from governance.' in content and 'governance_unified' not in content:
                    content = re.sub(r'from governance\.', 'from governance_unified.', content)
                    fixes_applied += 1
            
            # Fix common internal paths
            content = re.sub(r'from execution\.adapters\.', 'from execution_unified.adapters.', content)
            content = re.sub(r'from execution\.core\.', 'from execution_unified.core.', content)
            content = re.sub(r'from governance\.domains\.', 'from governance_unified.domains.', content)
            
            # Fix system.* to system_unified.* if needed
            if 'from system.' in content and 'system_unified' not in content:
                content = re.sub(r'from system\.', 'from system_unified.', content)
                fixes_applied += 1
            
            # Only write back if changes were made
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.import_fixes_applied += fixes_applied
                return fixes_applied
            
            return 0
            
        except Exception as e:
            print(f"Error fixing {file_path}: {e}")
            self.files_with_errors += 1
            return -1
    
    def fix_directory(self, directory):
        """Fix import paths in all Python files in a directory"""
        fixed_files = []
        
        for root, dirs, files in os.walk(directory):
            # Skip cache directories
            dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', 'node_modules']]
            
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, directory)
                    
                    # Skip if not an archival component
                    if 'archive' not in root.lower() and '_archive' not in file:
                        continue
                    
                    fixes = self.fix_import_paths(file_path)
                    if fixes >= 0:
                        fixed_files.append((relative_path, fixes))
                    self.files_processed += 1
        
        return fixed_files

def main():
    """Main execution function"""
    print("=" * 80)
    print("PHASE 3: SYSTEMATIC IMPORT PATH FIXING")
    print("DIRECT IMPORTS ONLY - NO LAZY LOADING")
    print("=" * 80)
    
    fixer = ImportPathFixer()
    
    # Fix execution_unified archival components
    print("\nFixing execution_unified archival components...")
    execution_files = fixer.fix_directory('execution_unified')
    print(f"Processed {fixer.files_processed} execution files")
    print(f"Applied {fixer.import_fixes_applied} import fixes")
    
    # Fix governance_unified archival components
    print("\nFixing governance_unified archival components...")
    governance_files = fixer.fix_directory('governance_unified')
    print(f"Processed {fixer.files_processed} total files")
    print(f"Applied {fixer.import_fixes_applied} total import fixes")
    
    print(f"\nFiles with errors: {fixer.files_with_errors}")
    
    # Print sample of fixes
    print("\nSample import path fixes:")
    for file_path, fixes in execution_files[:10]:
        if fixes > 0:
            print(f"  {file_path}: {fixes} fixes")
    
    print("\n" + "=" * 80)
    print("IMPORT PATH FIXING COMPLETE")
    print("ALL COMPONENTS NOW USE DIRECT UNIFIED SYSTEM IMPORTS")
    print("=" * 80)
    
    return {
        'files_processed': fixer.files_processed,
        'import_fixes_applied': fixer.import_fixes_applied,
        'files_with_errors': fixer.files_with_errors
    }

if __name__ == '__main__':
    result = main()