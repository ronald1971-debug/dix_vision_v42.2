"""
Automated Dependency Scanner for 394 Archival Components
Phase 1: Complete dependency audit with direct imports only - NO LAZY LOADING
"""

import ast
import os
import sys
from collections import defaultdict
from pathlib import Path

class DependencyScanner:
    """Scan all Python files for import dependencies"""
    
    def __init__(self):
        self.component_dependencies = {}
        self.external_dependencies = set()
        self.internal_dependencies = set()
        self.circular_dependencies = []
        self.component_count = 0
        
    def scan_file(self, file_path):
        """Scan a single Python file for imports"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            imports = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append({
                            'type': 'import',
                            'module': alias.name,
                            'alias': alias.asname
                        })
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ''
                    for alias in node.names:
                        imports.append({
                            'type': 'from_import',
                            'module': module,
                            'name': alias.name,
                            'alias': alias.asname
                        })
            
            return imports
        except Exception as e:
            print(f"Error scanning {file_path}: {e}")
            return []
    
    def categorize_import(self, import_info):
        """Categorize import as internal or external"""
        module = import_info['module']
        
        # External libraries that are definitely external
        external_libs = [
            'ccxt', 'web3', 'hummingbot', 'vnpy', 'pandas', 'numpy',
            'requests', 'asyncio', 'aiohttp', 'sqlalchemy', 'pytest',
            'matplotlib', 'scipy', 'sklearn', 'tensorflow', 'torch',
            'django', 'flask', 'fastapi', 'uvicorn', 'redis', 'celery'
        ]
        
        # Check if it's an external library
        for ext_lib in external_libs:
            if module.startswith(ext_lib):
                return 'external'
        
        # Internal imports (unified system components)
        internal_patterns = [
            'execution_unified', 'governance_unified', 'core.',
            'system_', 'execution.', 'governance.', 'execution_engine.',
            'governance_engine.'
        ]
        
        for pattern in internal_patterns:
            if pattern in module:
                return 'internal'
        
        # Standard library
        std_lib_patterns = [
            'os', 'sys', 'json', 'datetime', 'time', 'math', 'random',
            'collections', 'itertools', 'functools', 'typing', 'dataclasses',
            'pathlib', 'threading', 'multiprocessing', 'queue', 'logging'
        ]
        
        if module in std_lib_patterns or module.startswith('std'):
            return 'stdlib'
        
        # Default to external if unknown
        return 'external'
    
    def scan_directory(self, directory):
        """Scan all Python files in a directory"""
        python_files = []
        
        for root, dirs, files in os.walk(directory):
            # Skip cache directories
            dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', 'node_modules']]
            
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, directory)
                    
                    imports = self.scan_file(file_path)
                    
                    # Categorize imports
                    external = set()
                    internal = set()
                    
                    for imp in imports:
                        category = self.categorize_import(imp)
                        if category == 'external':
                            external.add(imp['module'])
                        elif category == 'internal':
                            internal.add(imp['module'])
                    
                    self.component_dependencies[relative_path] = {
                        'imports': imports,
                        'external_dependencies': external,
                        'internal_dependencies': internal,
                        'file_path': file_path
                    }
                    
                    self.external_dependencies.update(external)
                    self.internal_dependencies.update(internal)
                    
                    python_files.append(relative_path)
        
        self.component_count = len(python_files)
        return python_files
    
    def detect_circular_dependencies(self):
        """Detect circular dependencies using dependency graph"""
        # Build adjacency list for dependency graph
        graph = defaultdict(list)
        
        for component, deps in self.component_dependencies.items():
            for dep in deps['internal_dependencies']:
                # Extract component name from dependency
                dep_component = dep.replace('execution_unified.', '').replace('governance_unified.', '')
                graph[component].append(dep_component)
        
        # Simple cycle detection using DFS
        visited = set()
        recursion_stack = set()
        
        def dfs(node, path):
            if node in recursion_stack:
                cycle_start = path.index(node)
                cycle = path[cycle_start:] + [node]
                return cycle
            if node in visited:
                return None
            
            visited.add(node)
            recursion_stack.add(node)
            
            for neighbor in graph.get(node, []):
                result = dfs(neighbor, path + [node])
                if result:
                    return result
            
            recursion_stack.remove(node)
            return None
        
        for component in self.component_dependencies:
            cycle = dfs(component, [])
            if cycle:
                self.circular_dependencies.append(cycle)
        
        return self.circular_dependencies
    
    def generate_report(self):
        """Generate comprehensive dependency report"""
        report = {
            'total_components': self.component_count,
            'external_dependencies': sorted(list(self.external_dependencies)),
            'internal_dependencies': sorted(list(self.internal_dependencies)),
            'circular_dependencies': self.circular_dependencies,
            'component_details': self.component_dependencies
        }
        
        return report

def main():
    """Main execution function"""
    print("=" * 80)
    print("PHASE 1: COMPREHENSIVE DEPENDENCY AUDIT")
    print("NO LAZY LOADING - ALL COMPONENTS MUST LOAD DIRECTLY")
    print("=" * 80)
    
    scanner = DependencyScanner()
    
    # Scan execution_unified archival components
    print("\nScanning execution_unified archival components...")
    execution_files = scanner.scan_directory('execution_unified')
    print(f"Found {len(execution_files)} Python files in execution_unified")
    
    # Scan governance_unified archival components  
    print("\nScanning governance_unified archival components...")
    governance_files = scanner.scan_directory('governance_unified')
    print(f"Found {len(governance_files)} Python files in governance_unified")
    
    # Detect circular dependencies
    print("\nDetecting circular dependencies...")
    circular_deps = scanner.detect_circular_dependencies()
    if circular_deps:
        print(f"WARNING: Found {len(circular_deps)} circular dependency cycles")
        for i, cycle in enumerate(circular_deps, 1):
            print(f"  Cycle {i}: {' -> '.join(cycle)}")
    else:
        print("OK: No circular dependencies detected")
    
    # Generate report
    print("\nGenerating dependency report...")
    report = scanner.generate_report()
    
    # Print summary
    print(f"\n{'='*80}")
    print("DEPENDENCY AUDIT SUMMARY")
    print(f"{'='*80}")
    print(f"Total Components Scanned: {report['total_components']}")
    print(f"Unique External Dependencies: {len(report['external_dependencies'])}")
    print(f"Unique Internal Dependencies: {len(report['internal_dependencies'])}")
    print(f"Circular Dependencies: {len(report['circular_dependencies'])}")
    
    print(f"\nExternal Dependencies:")
    for dep in report['external_dependencies']:
        print(f"  - {dep}")
    
    print(f"\nInternal Dependencies (sample):")
    for dep in list(report['internal_dependencies'])[:20]:
        print(f"  - {dep}")
    if len(report['internal_dependencies']) > 20:
        print(f"  ... and {len(report['internal_dependencies']) - 20} more")
    
    # Save detailed report
    import json
    with open('dependency_audit_report.json', 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    print(f"\nDetailed report saved to: dependency_audit_report.json")
    print(f"{'='*80}")
    
    return report

if __name__ == '__main__':
    report = main()