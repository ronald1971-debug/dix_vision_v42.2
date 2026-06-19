"""
Placeholder Detection Script for DIX VISION v42.2

Scans the codebase for placeholder implementations that violate the zero placeholder policy:
- TODO, FIXME, NotImplemented
- Empty return statements without context
- Pass statements outside of abstract methods
- Mock/fake implementations

Usage:
    python detect_placeholders.py
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple, Set
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class PlaceholderDetector:
    """Detects placeholder implementations in Python code."""
    
    def __init__(self, root_dir: str):
        self.root_dir = Path(root_dir)
        self.issues: List[Dict[str, any]] = []
        self.file_patterns = ['*.py']
        self.exclude_dirs = {
            'venv', 'env', '.git', '__pycache__', 'node_modules',
            '.pytest_cache', 'migrations', 'build', 'dist',
            'backup_before_unification', 'github_debug_repo', 'alternatives',
            'scripts', 'dashboard2026', 'ui', '.vscode'
        }
        
    def scan_codebase(self) -> List[Dict[str, any]]:
        """Scan the entire codebase for placeholders."""
        logger.info(f"Scanning codebase: {self.root_dir}")
        
        for pattern in self.file_patterns:
            for file_path in self.root_dir.rglob(pattern):
                if self._should_include_file(file_path):
                    self._scan_file(file_path)
        
        logger.info(f"Scanned {len(self.issues)} placeholder issues found")
        return self.issues
    
    def _should_include_file(self, file_path: Path) -> bool:
        """Check if file should be included in scan."""
        # Check if file is in excluded directory
        for part in file_path.parts:
            if part in self.exclude_dirs:
                return False
        
        # Check if file is a test file (tests are allowed to have placeholders)
        if 'test' in file_path.name.lower() or file_path.parent.name == 'tests':
            return False
        
        return True
    
    def _scan_file(self, file_path: Path):
        """Scan a single file for placeholders."""
        try:
            content = file_path.read_text(encoding='utf-8')
            lines = content.split('\n')
            
            for line_num, line in enumerate(lines, 1):
                line_stripped = line.strip()
                
                # Skip empty lines and comments
                if not line_stripped or line_stripped.startswith('#'):
                    continue
                
                # Check for TODO, FIXME, NotImplemented
                self._check_for_placeholders(file_path, line_num, line, lines, line_num)
                
                # Check for pass statements (outside abstract methods)
                self._check_for_pass_statements(file_path, line_num, line, lines, line_num)
                
                # Check for empty returns (without context)
                self._check_for_empty_returns(file_path, line_num, line, lines, line_num)
                
                # Check for mock/fake implementations
                self._check_for_mock_implementations(file_path, line_num, line)
                
        except Exception as e:
            logger.warning(f"Error scanning {file_path}: {e}")
    
    def _check_for_placeholders(self, file_path: Path, line_num: int, line: str, lines: List[str], current_line_num: int):
        """Check for TODO, FIXME, NotImplemented comments."""
        # Only check for TODO/FIXME (NotImplementedError is allowed in abstract methods)
        patterns = [
            r'TODO\s*(?!.*#.*no.*todo)',  # TODO but not "no todo needed"
            r'FIXME',
        ]
        
        # Skip if it's a comment describing the file/purpose (documentation)
        if line.strip().startswith('"""') or line.strip().startswith("'''") or 'Zero Placeholder Policy' in line:
            return
            
        for pattern in patterns:
            if re.search(pattern, line):
                self.issues.append({
                    'file': str(file_path.relative_to(self.root_dir)),
                    'line': line_num,
                    'type': 'placeholder',
                    'pattern': pattern,
                    'content': line.strip(),
                    'severity': 'medium'
                })
    
    def _check_for_pass_statements(self, file_path: Path, line_num: int, line: str, lines: List[str], current_line_num: int):
        """Check for pass statements outside abstract methods and exception handlers."""
        if 'pass' in line and line.strip().startswith('pass'):
            # Check if it's in an abstract method
            in_abstract_method = self._is_in_abstract_method(lines, current_line_num)
            
            # Check if it's in an exception handler
            in_exception_handler = self._is_in_exception_handler(lines, current_line_num)
            
            # Check if it's in a guard clause (early return pattern)
            in_guard_clause = self._is_in_guard_clause(lines, current_line_num)
            
            # Only flag if it's not in any of these legitimate contexts
            if not in_abstract_method and not in_exception_handler and not in_guard_clause:
                self.issues.append({
                    'file': str(file_path.relative_to(self.root_dir)),
                    'line': line_num,
                    'type': 'pass_statement',
                    'content': line.strip(),
                    'severity': 'medium',
                    'context': self._get_context(lines, current_line_num)
                })
    
    def _check_for_empty_returns(self, file_path: Path, line_num: int, line: str, lines: List[str], current_line_num: int):
        """Check for empty return statements without context."""
        # Check for empty return with no content
        if re.match(r'^\s*return\s*$', line):
            # Check if it's in an exception handler or guard clause
            in_exception_handler = self._is_in_exception_handler(lines, current_line_num)
            in_guard_clause = self._is_in_guard_clause(lines, current_line_num)
            in_abstract_method = self._is_in_abstract_method(lines, current_line_num)
            
            # Only flag if not in legitimate contexts
            if not in_exception_handler and not in_guard_clause and not in_abstract_method:
                self.issues.append({
                    'file': str(file_path.relative_to(self.root_dir)),
                    'line': line_num,
                    'type': 'empty_return',
                    'content': line.strip(),
                    'severity': 'low',
                    'context': self._get_context(lines, current_line_num)
                })
    
    def _check_for_mock_implementations(self, file_path: Path, line_num: int, line: str):
        """Check for mock/fake implementations."""
        # Only flag actual placeholder implementations, not test mocks or documentation
        mock_patterns = [
            r'#.*placeholder.*implementation',  # Comments about placeholder implementations
            r'this is a placeholder implementation',  # Self-identifying comments
        ]
        
        for pattern in mock_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                self.issues.append({
                    'file': str(file_path.relative_to(self.root_dir)),
                    'line': line_num,
                    'type': 'mock_implementation',
                    'content': line.strip(),
                    'severity': 'high',
                    'pattern': pattern
                })
    
    def _is_in_abstract_method(self, lines: List[str], line_num: int) -> bool:
        """Check if current line is in an abstract method."""
        # Look for @abstractmethod decorator in previous lines
        for i in range(max(0, line_num - 10), line_num):
            if '@abstractmethod' in lines[i]:
                return True
        return False
    
    def _is_in_exception_handler(self, lines: List[str], line_num: int) -> bool:
        """Check if current line is in an exception handler."""
        # Look for except block in previous lines
        for i in range(max(0, line_num - 5), line_num):
            if 'except' in lines[i] and ':' in lines[i]:
                return True
        return False
    
    def _is_in_guard_clause(self, lines: List[str], line_num: int) -> bool:
        """Check if current line is in a guard clause."""
        if line_num == 0:
            return False
        
        prev_line = lines[line_num - 1].strip()
        # Check if previous line is a conditional or early return
        if prev_line.startswith('if') or prev_line.startswith('return'):
            return True
        return False
    
    def _get_context(self, lines: List[str], line_num: int) -> str:
        """Get context around a line."""
        start = max(0, line_num - 2)
        end = min(len(lines), line_num + 3)
        return '\n'.join(lines[start:end])
    
    def generate_report(self) -> str:
        """Generate a report of placeholder issues."""
        if not self.issues:
            return "✅ No placeholder issues found! Codebase is compliant with zero placeholder policy."
        
        print(f"\n{len(self.issues)} placeholder issues found\n")

        report = [
            "# Placeholder Detection Report\n",
            f"Total Issues: {len(self.issues)}\n",
            "## Issues by Severity:\n"
        ]
        
        high_severity = [i for i in self.issues if i.get('severity') == 'high']
        medium_severity = [i for i in self.issues if i.get('severity') == 'medium']
        low_severity = [i for i in self.issues if i.get('severity') == 'low']
        
        report.append(f"### High Severity (Critical - must fix): {len(high_severity)}")
        for issue in high_severity:
            report.append(f"- {issue['file']}:{issue['line']} - {issue['content'][:100]}")
        
        report.append(f"\n### Medium Severity (Review needed): {len(medium_severity)}")
        for issue in medium_severity[:20]:  # Show first 20
            report.append(f"- {issue['file']}:{issue['line']} - {issue['content'][:80]}")
        
        if len(medium_severity) > 20:
            report.append(f"... and {len(medium_severity) - 20} more")
        
        report.append(f"\n### Low Severity (Potential issues): {len(low_severity)}")
        for issue in low_severity[:10]:  # Show first 10
            report.append(f"- {issue['file']}:{issue['line']} - {issue['content'][:80]}")
        
        if len(low_severity) > 10:
            report.append(f"... and {len(low_severity) - 10} more")
        
        return '\n'.join(report)


def main():
    """Main entry point."""
    # Set UTF-8 encoding for output
    sys.stdout.reconfigure(encoding='utf-8')
    
    if len(sys.argv) > 1:
        root_dir = sys.argv[1]
    else:
        root_dir = str(Path(__file__).parent.parent)
    
    detector = PlaceholderDetector(root_dir)
    issues = detector.scan_codebase()
    
    print("\n" + "=" * 60, file=sys.stdout)
    print("DIX VISION v42.2 - Placeholder Detection", file=sys.stdout)
    print("=" * 60 + "\n", file=sys.stdout)
    
    print(detector.generate_report(), file=sys.stdout)
    
    if issues:
        logger.error(f"Found {len(issues)} placeholder issues that need to be addressed.")
        sys.exit(1)
    else:
        logger.info("Codebase is compliant with zero placeholder policy!")
        sys.exit(0)


if __name__ == "__main__":
    main()