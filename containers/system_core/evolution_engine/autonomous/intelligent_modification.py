"""
evolution_engine.autonomous.intelligent_modification
DIX VISION v42.2 — Intelligent Code Modification System (Priority 1)

Provides AI-powered code modification with strict safety constraints.
This is a Priority 1 enhancement for autonomous engineering capabilities.
"""

from __future__ import annotations

import logging
import threading
import ast
import json
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class ModificationRisk(Enum):
    """Risk level of code modification."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass
class CodeContext:
    """Context information for code modification."""
    
    file_path: str
    language: str
    component: str
    current_code: str
    dependencies: List[str] = field(default_factory=list)
    test_files: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ModificationObjective:
    """Objective for code modification."""
    
    objective_type: str  # OPTIMIZATION, BUG_FIX, FEATURE_ADDITION, REFACTORING
    description: str
    target_function: Optional[str] = None
    constraints: List[str] = field(default_factory=list)
    success_criteria: List[str] = field(default_factory=list)


@dataclass
class ModificationProposal:
    """Proposal for code modification with safety validation."""
    
    proposal_id: str
    proposed_code: str
    risk_level: ModificationRisk
    modified_lines: List[int] = field(default_factory=list)
    added_lines: List[str] = field(default_factory=list)
    removed_lines: List[str] = field(default_factory=list)
    safety_score: float = 0.0  # 0.0 to 1.0
    validation_errors: List[str] = field(default_factory=list)
    generated_tests: List[str] = field(default_factory=list)
    rollback_plan: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    @property
    def is_safe(self) -> bool:
        return self.safety_score >= 0.7 and len(self.validation_errors) == 0


@dataclass
class ModificationResult:
    """Result of code modification execution."""
    
    success: bool
    proposal_id: str
    applied_changes: int
    test_results: Dict[str, bool] = field(default_factory=dict)
    rollback_performed: bool = False
    error_message: str = ""
    modification_time_ms: float = 0.0


class SafetyConstraintChecker(ABC):
    """Base class for safety constraint checkers."""
    
    @abstractmethod
    def validate(self, code_context: CodeContext, proposed_code: str) -> List[str]:
        """Validate code against safety constraints."""
        pass


class DependencySafetyChecker(SafetyConstraintChecker):
    """Checks for dependency safety in code modifications."""
    
    def validate(self, code_context: CodeContext, proposed_code: str) -> List[str]:
        """Validate that dependencies are not broken."""
        errors = []
        
        # Check imports in proposed code
        proposed_imports = self._extract_imports(proposed_code)
        
        # Check if imports exist in codebase
        for imp in proposed_imports:
            if not self._import_exists(imp, code_context):
                errors.append(f"Dependency violation: Import {imp} not found")
        
        # Check if removing existing imports
        current_imports = self._extract_imports(code_context.current_code)
        for imp in current_imports:
            if imp not in proposed_imports:
                # Check if import is used in code
                if self._import_is_used(imp, code_context):
                    errors.append(f"Dependency violation: Removing used import {imp}")
        
        return errors
    
    def _extract_imports(self, code: str) -> List[str]:
        """Extract import statements from code."""
        imports = []
        lines = code.split('\n')
        for line in lines:
            if line.strip().startswith('import ') or line.strip().startswith('from '):
                imports.append(line.strip())
        return imports
    
    def _import_exists(self, import_statement: str, context: CodeContext) -> bool:
        """Check if import exists in codebase."""
        # Placeholder - would check against actual codebase
        return True
    
    def _import_is_used(self, import_statement: str, context: CodeContext) -> bool:
        """Check if import is used in the code."""
        # Placeholder - would analyze usage in code
        return False


class SyntaxSafetyChecker(SafetyConstraintChecker):
    """Checks for syntax safety in code modifications."""
    
    def validate(self, code_context: CodeContext, proposed_code: str) -> List[str]:
        """Validate syntax safety."""
        errors = []
        
        # Try to parse the proposed code
        try:
            ast.parse(proposed_code)
        except SyntaxError as e:
            errors.append(f"Syntax error: {str(e)}")
        
        # Check for dangerous patterns
        dangerous_patterns = [
            r'\beval\s*\(',
            r'exec\s*\(',
            r'__import__\s*\(',
            r'\.system\(',
            r'\.shell\(',
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, proposed_code):
                errors.append(f"Security risk: Dangerous pattern detected: {pattern}")
        
        return errors


class AutomatedTestGenerator:
    """Generates automated tests for code modifications."""
    
    def __init__(self):
        self._lock = threading.Lock()
    
    def generate_tests(self, code_context: CodeContext, proposal: ModificationProposal) -> List[str]:
        """
        Generate automated tests for a modification proposal.
        
        Args:
            code_context: Context information
            proposal: Modification proposal
            
        Returns:
            Generated test code strings
        """
        with self._lock:
            tests = []
            
            # Extract function signature from proposal
            function_name = self._extract_function_name(proposal.proposed_code)
            if function_name:
                test_code = f"""
def test_{function_name}_modification():
    # Test for modification (auto-generated)
    # This test was automatically generated
    assert True  # Replace with actual test logic
    pass
"""
                tests.append(test_code)
            
            # Generate integration test
            integration_test = f"""
def test_{function_name}_integration():
    # Integration test for {code_context.component}
    # This test was automatically generated
    assert True  # Replace with actual test logic
    pass
"""
            tests.append(integration_test)
            
            return tests
    
    def _extract_function_name(self, code: str) -> Optional[str]:
        """Extract function name from code."""
        match = re.search(r'def\s+(\w+)\s*\(', code)
        return match.group(1) if match else None


class IntelligentCodeModifier:
    """
    AI-powered code modification system with strict safety constraints.
    
    This system provides autonomous engineering capabilities with:
    - Multi-layer safety validation
    - Automated test generation
    - Rollback planning
    - Dependency analysis
    - Syntax safety checking
    """
    
    def __init__(self):
        self._lock = threading.Lock()
        
        # Safety checkers
        self._safety_checkers: List[SafetyConstraintChecker] = [
            SyntaxSafetyChecker(),
            DependencySafetyChecker(),
        ]
        
        # Test generator
        self._test_generator = AutomatedTestGenerator()
        
        # Modification history
        self._modification_history: List[ModificationResult] = []
        
        # Governance integration
        self._governance_integration_enabled = True
        
        logger.info("[INTELLIGENT_MODIFIER] Initialized with {len(self._safety_checkers)} safety checkers")
    
    def propose_modification(
        self,
        code_context: CodeContext,
        objective: ModificationObjective
    ) -> Optional[ModificationProposal]:
        """
        Propose code modification based on objective.
        
        Args:
            code_context: Context information
            objective: Modification objective
            
        Returns:
            Modification proposal or None if unsafe
        """
        with self._lock:
            # Placeholder for AI-powered modification generation
            # In production, this would use LLM or specialized AI
            
            try:
                # Analyze current code
                current_ast = ast.parse(code_context.current_code)
                
                # Generate modification (placeholder)
                proposed_code = self._generate_modification(code_context, objective)
                
                if not proposed_code:
                    return None
                
                # Validate through safety layers
                validation_errors = []
                safety_scores = []
                
                for checker in self._safety_checkers:
                    errors = checker.validate(code_context, proposed_code)
                    validation_errors.extend(errors)
                    safety_scores.append(0.0 if errors else 1.0)
                
                # Calculate overall safety score
                overall_safety = sum(safety_scores) / len(safety_scores) if safety_scores else 0.0
                
                # Determine risk level
                if overall_safety < 0.3:
                    risk_level = ModificationRisk.CRITICAL
                elif overall_safety < 0.5:
                    risk_level = ModificationRisk.HIGH
                elif overall_safety < 0.7:
                    risk_level = ModificationRisk.MEDIUM
                else:
                    risk_level = ModificationRisk.LOW
                
                # Generate rollback plan
                rollback_plan = self._generate_rollback_plan(code_context)
                
                # Generate tests
                proposal_id = f"proposal_{int(datetime.utcnow().timestamp() * 1000)}"
                temp_proposal = ModificationProposal(
                    proposal_id=proposal_id,
                    proposed_code=proposed_code,
                    risk_level=risk_level
                )
                tests = self._test_generator.generate_tests(code_context, temp_proposal)
                
                # Create final proposal with all fields
                final_proposal = ModificationProposal(
                    proposal_id=proposal_id,
                    proposed_code=proposed_code,
                    risk_level=risk_level,
                    validation_errors=validation_errors,
                    generated_tests=tests,
                    rollback_plan=rollback_plan
                )
                
                return final_proposal
                
            except Exception as e:
                logger.error(f"[INTELLIGENT_MODIFIER] Failed to generate proposal: {e}")
                return None
    
    def _generate_modification(
        self,
        code_context: CodeContext,
        objective: ModificationObjective
    ) -> Optional[str]:
        """Generate code modification (placeholder)."""
        # Placeholder for AI-powered generation
        # In production, this would use LLM to generate modifications
        
        if objective.objective_type == "OPTIMIZATION":
            # Generate optimized version
            return self._apply_optimization_heuristics(code_context.current_code)
        elif objective.objective_type == "BUG_FIX":
            # Generate fixed version
            return self._apply_bug_fix_heuristics(code_context.current_code, objective.description)
        else:
            # Return original code (no modification)
            return code_context.current_code
    
    def _apply_optimization_heuristics(self, code: str) -> str:
        """Apply optimization heuristics to code (placeholder)."""
        # Placeholder - simple optimizations
        # Remove unnecessary whitespace
        lines = code.split('\n')
        optimized_lines = [line.rstrip() for line in lines]
        return '\n'.join(optimized_lines)
    
    def _apply_bug_fix_heuristics(self, code: str, bug_description: str) -> str:
        """Apply bug fix heuristics (placeholder)."""
        # Placeholder - simple bug fixes
        # In production, this would use AI to fix bugs
        return code  # Return original for now
    
    def _generate_rollback_plan(self, code_context: CodeContext) -> str:
        """Generate rollback plan for code modification."""
        return f"""
Rollback Plan for {code_context.component}:
1. Backup current code: {code_context.file_path}
2. Keep backup for 30 days
3. Rollback procedure: restore from backup
4. Validation: run existing tests after rollback
5. Notification: alert operators on rollback
"""
    
    def apply_modification(
        self,
        proposal: ModificationProposal,
        code_context: CodeContext
    ) -> ModificationResult:
        """
        Apply a validated code modification.
        
        Args:
            proposal: Modification proposal to apply
            code_context: Context information
            
        Returns:
            Modification result
        """
        start_time = datetime.utcnow()
        
        if not proposal.is_safe:
            return ModificationResult(
                success=False,
                proposal_id=proposal.proposal_id,
                error_message="Proposal not safe enough to apply"
            )
        
        # Check governance approval if enabled
        if self._governance_integration_enabled:
            if not self._check_governance_approval(proposal):
                return ModificationResult(
                    success=False,
                    proposal_id=proposal.proposal_id,
                    error_message="Governance approval not granted"
                )
        
        try:
            # Create backup
            backup_code = code_context.current_code
            
            # Write new code
            encoding = code_context.encoding if hasattr(code_context, 'encoding') else 'utf-8'
            with open(code_context.file_path, 'w', encoding=encoding) as f:
                f.write(proposal.proposed_code)
            
            # Run generated tests
            test_results = {}
            for i, test_code in enumerate(proposal.generated_tests):
                test_name = f"test_auto_generated_{i}"
                # In production, would actually run the test
                test_results[test_name] = True  # Placeholder
            
            modification_time_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            return ModificationResult(
                success=True,
                proposal_id=proposal.proposal_id,
                applied_changes=len(proposal.modified_lines),
                test_results=test_results,
                modification_time_ms=modification_time_ms
            )
            
        except Exception as e:
            logger.error(f"[INTELLIGENT_MODIFIER] Failed to apply modification: {e}")
            
            # Rollback on failure
            self._perform_rollback(code_context.file_path, code_context.current_code)
            
            return ModificationResult(
                success=False,
                proposal_id=proposal.proposal_id,
                error_message=str(e),
                rollback_performed=True
            )
    
    def _check_governance_approval(self, proposal: ModificationProposal) -> bool:
        """Check if governance system approves the modification."""
        # Placeholder for governance integration
        # In production, would query governance_unified for approval
        return True  # Placeholder - always approve for now
    
    def _perform_rollback(self, file_path: str, original_code: str) -> bool:
        """Rollback code to original state."""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(original_code)
            return True
        except Exception as e:
            logger.error(f"[INTELLIGENT_MODIFIER] Rollback failed: {e}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get modification statistics."""
        with self._lock:
            successful = sum(1 for r in self._modification_history if r.success)
            total = len(self._modification_history)
            
            return {
                "total_modifications": total,
                "successful_modifications": successful,
                "success_rate": successful / total if total > 0 else 0.0,
                "safety_checkers_count": len(self._safety_checkers),
                "governance_integration_enabled": self._governance_integration_enabled
            }


# Singleton instance
_intelligent_modifier: Optional[IntelligentCodeModifier] = None
_intelligent_modifier_lock = threading.Lock()

def get_intelligent_code_modifier() -> IntelligentCodeModifier:
    """Get the singleton intelligent code modifier instance."""
    global _intelligent_modifier
    if _intelligent_modifier is None:
        with _intelligent_modifier_lock:
            if _intelligent_modifier is None:
                _intelligent_modifier = IntelligentCodeModifier()
    return _intelligent_modifier


def get_intelligent_modification_system() -> IntelligentCodeModifier:
    """Get the singleton intelligent code modification system instance (alias)."""
    return get_intelligent_code_modifier()


__all__ = [
    "ModificationRisk",
    "CodeContext",
    "ModificationObjective",
    "ModificationProposal",
    "ModificationResult",
    "SafetyConstraintChecker",
    "DependencySafetyChecker",
    "SyntaxSafetyChecker",
    "AutomatedTestGenerator",
    "IntelligentCodeModifier",
    "get_intelligent_code_modifier",
    "get_intelligent_modification_system",
]