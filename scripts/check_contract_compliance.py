#!/usr/bin/env python3
"""
DIXVISION Contract Compliance Checker
Enforces non-negotiable engineering directives from BUILDBASH.txt

NO PLACEHOLDERS
NO MOCK IMPLEMENTATIONS  
NO STUB CLASSES
NO PASS STATEMENTS
NO return {"mock": true}
"""

import ast
import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Set, Tuple
import argparse

class ContractViolation:
    """Represents a contract compliance violation"""
    
    def __init__(self, file_path: str, line_number: int, violation_type: str, 
                 description: str, severity: str = "ERROR"):
        self.file_path = file_path
        self.line_number = line_number
        self.violation_type = violation_type
        self.description = description
        self.severity = severity
    
    def __str__(self):
        return f"{self.severity}: {self.file_path}:{self.line_number} - {self.violation_type}: {self.description}"

class ContractComplianceChecker:
    """Checks code for compliance with non-negotiable engineering directives"""
    
    # Non-negotiable patterns to detect
    PLACEHOLDER_PATTERNS = [
        r"# TODO:.*placeholder",
        r"# FIXME:.*placeholder", 
        r"# PLACEHOLDER",
        r"raise NotImplementedError\(",
        r"pass\s*#\s*placeholder",
        r"NotImplementedError",
    ]
    
    MOCK_PATTERNS = [
        r"mock\(",
        r"@patch",
        r"@mock",
        r"Mock\(",
        r"MagicMock\(",
        r"return.*mock.*:",
        r"mock_data",
        r"mock_response",
        r'"mock":\s*true',
        r"'mock':\s*true",
    ]
    
    STUB_PATTERNS = [
        r"class.*Stub",
        r"def.*stub",
        r"# STUB",
        r"# FIXME:.*stub",
        r"# TODO:.*stub",
    ]
    
    EMPTY_IMPLEMENTATION_PATTERNS = [
        r"^\s*pass\s*$",
        r"^\s*return\s*$",
        r"^\s*return\s+None\s*$",
        r"^\s*return\s+\{\}\s*$",
        r"^\s*return\s+""\s*$",
        r"^\s*return\s+''\s*$",
    ]
    
    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
        self.violations: List[ContractViolation] = []
        self.checked_files: Set[str] = set()
        
    def check_file(self, file_path: Path) -> List[ContractViolation]:
        """Check a single file for contract compliance"""
        violations = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            # Parse AST
            try:
                tree = ast.parse(content, filename=str(file_path))
            except SyntaxError:
                violations.append(ContractViolation(
                    str(file_path), 0, "SYNTAX_ERROR",
                    "File contains syntax errors", "ERROR"
                ))
                return violations
            
            # Check for various violations
            violations.extend(self._check_placeholders(file_path, lines))
            violations.extend(self._check_mocks(file_path, lines))
            violations.extend(self._check_stubs(file_path, lines))
            violations.extend(self._check_empty_implementations(file_path, lines, tree))
            violations.extend(self._check_ast_placeholders(file_path, tree))
            
        except Exception as e:
            violations.append(ContractViolation(
                str(file_path), 0, "CHECK_ERROR",
                f"Error checking file: {str(e)}", "ERROR"
            ))
        
        return violations
    
    def _check_placeholders(self, file_path: Path, lines: List[str]) -> List[ContractViolation]:
        """Check for placeholder code"""
        violations = []
        
        for line_num, line in enumerate(lines, 1):
            for pattern in self.PLACEHOLDER_PATTERNS:
                if re.search(pattern, line, re.IGNORECASE):
                    violations.append(ContractViolation(
                        str(file_path), line_num, "PLACEHOLDER",
                        f"Placeholder code detected: {line.strip()}", "ERROR"
                    ))
        
        return violations
    
    def _check_mocks(self, file_path: Path, lines: List[str]) -> List[ContractViolation]:
        """Check for mock implementations (except in test files)"""
        violations = []
        
        # Skip test files - mocks are allowed in tests
        if 'test' in file_path.name.lower():
            return violations
        
        for line_num, line in enumerate(lines, 1):
            for pattern in self.MOCK_PATTERNS:
                if re.search(pattern, line, re.IGNORECASE):
                    # Allow mock imports if they're for testing frameworks
                    if 'import mock' not in line.lower() and 'from unittest' not in line.lower():
                        violations.append(ContractViolation(
                            str(file_path), line_num, "MOCK_IMPLEMENTATION",
                            f"Mock implementation detected: {line.strip()}", "ERROR"
                        ))
        
        return violations
    
    def _check_stubs(self, file_path: Path, lines: List[str]) -> List[ContractViolation]:
        """Check for stub classes"""
        violations = []
        
        for line_num, line in enumerate(lines, 1):
            for pattern in self.STUB_PATTERNS:
                if re.search(pattern, line, re.IGNORECASE):
                    violations.append(ContractViolation(
                        str(file_path), line_num, "STUB_CLASS",
                        f"Stub class detected: {line.strip()}", "ERROR"
                    ))
        
        return violations
    
    def _check_empty_implementations(self, file_path: Path, lines: List[str], 
                                    tree: ast.AST) -> List[ContractViolation]:
        """Check for empty implementations"""
        violations = []
        
        # Check for standalone pass statements (not in interfaces/abstract classes)
        for node in ast.walk(tree):
            if isinstance(node, ast.Pass):
                # Check if this pass is in an interface/abstract class
                parent = self._find_parent_class(tree, node)
                if parent and not self._is_abstract_class(parent):
                    violations.append(ContractViolation(
                        str(file_path), node.lineno, "EMPTY_IMPLEMENTATION",
                        "Empty implementation with pass statement", "ERROR"
                    ))
        
        return violations
    
    def _check_ast_placeholders(self, file_path: Path, tree: ast.AST) -> List[ContractViolation]:
        """Check AST for placeholder patterns"""
        violations = []
        
        for node in ast.walk(tree):
            # Check for NotImplementedError in functions
            if isinstance(node, ast.Raise):
                if isinstance(node.exc, ast.Call):
                    if isinstance(node.exc.func, ast.Name):
                        if node.exc.func.id == "NotImplementedError":
                            # Check if this is in an abstract class
                            parent = self._find_parent_class(tree, node)
                            if parent and not self._is_abstract_class(parent):
                                violations.append(ContractViolation(
                                    str(file_path), node.lineno, "PLACEHOLDER",
                                    "NotImplementedError in non-abstract class", "ERROR"
                                ))
        
        return violations
    
    def _find_parent_class(self, tree: ast.AST, node: ast.AST) -> ast.ClassDef:
        """Find the parent class of a node"""
        for parent in ast.walk(tree):
            if isinstance(parent, ast.ClassDef):
                for child in ast.walk(parent):
                    if child is node:
                        return parent
        return None
    
    def _is_abstract_class(self, class_node: ast.ClassDef) -> bool:
        """Check if a class is abstract"""
        # Check for ABC inheritance
        for base in class_node.bases:
            if isinstance(base, ast.Name):
                if base.id in ['ABC', 'ABCMeta', 'abstractmethod']:
                    return True
            elif isinstance(base, ast.Attribute):
                if base.attr in ['ABC', 'ABCMeta']:
                    return True
        
        # Check for abstract methods
        for node in class_node.body:
            if isinstance(node, ast.FunctionDef):
                for decorator in node.decorator_list:
                    if isinstance(decorator, ast.Name):
                        if decorator.id == 'abstractmethod':
                            return True
        
        return False
    
    def check_directory(self, directory: Path) -> None:
        """Check all Python files in a directory recursively"""
        python_files = directory.rglob("*.py")
        
        for file_path in python_files:
            # Skip __pycache__ and test files for main compliance check
            if '__pycache__' in str(file_path):
                continue
            
            # Check test files separately with different rules
            is_test_file = 'test' in file_path.name.lower()
            
            violations = self.check_file(file_path)
            self.violations.extend(violations)
            self.checked_files.add(str(file_path))
    
    def generate_report(self) -> Dict:
        """Generate compliance report"""
        error_count = sum(1 for v in self.violations if v.severity == "ERROR")
        warning_count = sum(1 for v in self.violations if v.severity == "WARNING")
        
        # Group violations by type
        violations_by_type: Dict[str, List[ContractViolation]] = {}
        for violation in self.violations:
            if violation.violation_type not in violations_by_type:
                violations_by_type[violation.violation_type] = []
            violations_by_type[violation.violation_type].append(violation)
        
        return {
            "total_files_checked": len(self.checked_files),
            "total_violations": len(self.violations),
            "error_count": error_count,
            "warning_count": warning_count,
            "violations_by_type": violations_by_type,
            "violations": [str(v) for v in self.violations],
            "compliant": error_count == 0
        }

def main():
    parser = argparse.ArgumentParser(description="Check DIXVISION contract compliance")
    parser.add_argument("path", help="Path to check (file or directory)")
    parser.add_argument("--strict", action="store_true", help="Fail on warnings as well")
    parser.add_argument("--output", help="Output file for report")
    
    args = parser.parse_args()
    
    checker = ContractComplianceChecker(args.path)
    path = Path(args.path)
    
    if path.is_file():
        checker.violations = checker.check_file(path)
        checker.checked_files.add(str(path))
    elif path.is_directory():
        checker.check_directory(path)
    else:
        print(f"Error: {args.path} is not a valid file or directory")
        sys.exit(1)
    
    report = checker.generate_report()
    
    # Print report
    print("=" * 80)
    print("DIXVISION CONTRACT COMPLIANCE REPORT")
    print("=" * 80)
    print(f"Files checked: {report['total_files_checked']}")
    print(f"Total violations: {report['total_violations']}")
    print(f"Errors: {report['error_count']}")
    print(f"Warnings: {report['warning_count']}")
    print(f"Compliant: {report['compliant']}")
    print("=" * 80)
    
    # Print violations by type
    for violation_type, violations in report['violations_by_type'].items():
        print(f"\n{violation_type} ({len(violations)}):")
        for violation in violations:
            print(f"  {violation}")
    
    # Write to file if requested
    if args.output:
        import json
        with open(args.output, 'w') as f:
            json.dump(report, f, indent=2)
    
    # Exit with appropriate code
    if report['compliant']:
        print("\n✅ CONTRACT COMPLIANT")
        sys.exit(0)
    else:
        print(f"\n❌ CONTRACT VIOLATIONS DETECTED ({report['error_count']} errors)")
        sys.exit(1)

if __name__ == "__main__":
    main()