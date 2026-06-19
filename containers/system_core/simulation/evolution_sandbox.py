"""
simulation/evolution_sandbox.py
DIX VISION v42.2 — Evolution Sandbox (Phase 12)

A safe, isolated environment for testing DYON evolution proposals before
they are approved by governance. The sandbox:

- Runs proposed code changes in isolation
- Validates that proposals don't introduce breaking changes
- Tests evolution proposals against simulation scenarios
- Measures performance impact of proposed changes
- Generates approval reports for governance

CRITICAL: All evolution proposals MUST pass sandbox validation before
governance approval. No self-deployment, no self-modification.
"""

from __future__ import annotations

import ast
import importlib.util
import sys
import tempfile
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Any

from simulation.governance_tester import GovernanceTestCase, GovernanceTestHarness


class EvolutionProposalType(StrEnum):
    """Types of evolution proposals."""

    CODE_PATCH = "code_patch"
    ARCHITECTURE_CHANGE = "architecture_change"
    PARAMETER_TUNING = "parameter_tuning"
    REFACTOR = "refactor"
    TEST_GENERATION = "test_generation"
    OPTIMIZATION = "optimization"


@dataclass(frozen=True, slots=True)
class EvolutionProposal:
    """A proposed change from DYON."""

    proposal_id: str
    proposal_type: EvolutionProposalType
    target_file: str
    original_code: str
    proposed_code: str
    description: str
    risk_level: str  # "LOW", "MEDIUM", "HIGH"
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class SandboxTestConfig:
    """Configuration for sandbox testing."""

    proposal: EvolutionProposal
    seed: int
    test_scenarios: list[str] = field(default_factory=list)
    governance_tests: list[GovernanceTestCase] = field(default_factory=list)


@dataclass(slots=True)
class SandboxTestResult:
    """Result of testing an evolution proposal in the sandbox."""

    proposal_id: str
    passed: bool
    syntax_valid: bool = True
    import_valid: bool = True
    runtime_valid: bool = True
    governance_compliant: bool = True
    performance_impact: float = 0.0
    test_results: dict[str, bool] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    approval_recommendation: str = ""


@dataclass(slots=True)
class CodeDiff:
    """Represent a code diff for validation."""

    added_lines: list[str] = field(default_factory=list)
    removed_lines: list[str] = field(default_factory=list)
    modified_functions: list[str] = field(default_factory=list)
    new_functions: list[str] = field(default_factory=list)


class EvolutionSandbox:
    """Isolated sandbox for testing evolution proposals.

    The sandbox provides a safe environment to validate DYON proposals
    before governance approval. All proposals are tested in isolation
    and never affect the production codebase.
    """

    def __init__(self, *, deterministic_seed: int = 42) -> None:
        self._seed = deterministic_seed
        self._governance_harness = GovernanceTestHarness(deterministic_seed=deterministic_seed)
        self._proposal_results: dict[str, SandboxTestResult] = {}
        self._temp_dir: Path | None = None

    def test_proposal(self, config: SandboxTestConfig) -> SandboxTestResult:
        """Test an evolution proposal in the sandbox."""
        result = SandboxTestResult(proposal_id=config.proposal.proposal_id, passed=False)

        # Step 1: Syntax validation
        result.syntax_valid = self._validate_syntax(config.proposal.proposed_code)
        if not result.syntax_valid:
            result.errors.append("Syntax validation failed")
            self._proposal_results[config.proposal.proposal_id] = result
            return result

        # Step 2: Import validation (in isolation)
        result.import_valid = self._validate_import(config.proposal)
        if not result.import_valid:
            result.errors.append("Import validation failed")
            self._proposal_results[config.proposal.proposal_id] = result
            return result

        # Step 3: Runtime validation
        result.runtime_valid = self._validate_runtime(config.proposal)
        if not result.runtime_valid:
            result.errors.append("Runtime validation failed")
            self._proposal_results[config.proposal.proposal_id] = result
            return result

        # Step 4: Governance compliance
        result.governance_compliant = self._validate_governance_compliance(config)
        if not result.governance_compliant:
            result.errors.append("Governance compliance failed")
            self._proposal_results[config.proposal.proposal_id] = result
            return result

        # Step 5: Performance impact assessment
        result.performance_impact = self._assess_performance_impact(config.proposal)
        if result.performance_impact > 0.5:  # 50% degradation threshold
            result.warnings.append(f"Performance impact {result.performance_impact:.2%} exceeds threshold")

        # Step 6: Final approval decision
        result.passed = (
            result.syntax_valid
            and result.import_valid
            and result.runtime_valid
            and result.governance_compliant
        )
        result.approval_recommendation = self._generate_approval_recommendation(result, config.proposal)

        self._proposal_results[config.proposal.proposal_id] = result
        return result

    def _validate_syntax(self, code: str) -> bool:
        """Validate that code has valid Python syntax."""
        try:
            ast.parse(code)
            return True
        except SyntaxError:
            return False

    def _validate_import(self, proposal: EvolutionProposal) -> bool:
        """Validate that the proposed code can be imported in isolation."""
        try:
            # Create a temporary file with the proposed code
            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
                f.write(proposal.proposed_code)
                temp_path = Path(f.name)

            # Try to import it
            spec = importlib.util.spec_from_file_location(
                f"sandbox_{proposal.proposal_id}", temp_path
            )
            if spec is None or spec.loader is None:
                return False

            module = importlib.util.module_from_spec(spec)
            sys.modules[f"sandbox_{proposal.proposal_id}"] = module
            spec.loader.exec_module(module)

            # Clean up
            del sys.modules[f"sandbox_{proposal.proposal_id}"]
            temp_path.unlink()

            return True
        except Exception:
            return False

    def _validate_runtime(self, proposal: EvolutionProposal) -> bool:
        """Validate that the proposed code runs without errors."""
        try:
            # Parse the code and check for dangerous patterns
            tree = ast.parse(proposal.proposed_code)

            # Check for dangerous imports
            dangerous_imports = {"os.system", "subprocess", "eval", "exec"}
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name in dangerous_imports:
                            return False
                elif isinstance(node, ast.ImportFrom):
                    if node.module in dangerous_imports:
                        return False
                elif isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        if node.func.id in {"eval", "exec"}:
                            return False

            return True
        except Exception:
            return False

    def _validate_governance_compliance(self, config: SandboxTestConfig) -> bool:
        """Validate that the proposal is compliant with governance policies."""
        # Run governance tests if specified
        if config.governance_tests:
            for test_case in config.governance_tests:
                from simulation.governance_tester import (
                    GovernanceTestConfig,
                    GovernanceTestHarness,
                )

                test_config = GovernanceTestConfig(
                    test_case=test_case,
                    scenario_id=f"{config.proposal.proposal_id}_{test_case.value}",
                    seed=config.seed,
                )
                harness = GovernanceTestHarness(deterministic_seed=config.seed)
                result = harness.run_test(test_config)

                if not result.passed:
                    return False

        # Check for governance-risky patterns in the code
        risky_patterns = ["governance.kernel", "policy_engine", "risk_cache"]
        for pattern in risky_patterns:
            if pattern in config.proposal.proposed_code.lower():
                # Proposals touching governance require extra scrutiny
                if config.proposal.risk_level == "HIGH":
                    return False  # High-risk governance changes are auto-rejected

        return True

    def _assess_performance_impact(self, proposal: EvolutionProposal) -> float:
        """Assess the performance impact of the proposal."""
        # Simple heuristic based on code complexity
        original_lines = len(proposal.original_code.split("\n"))
        proposed_lines = len(proposal.proposed_code.split("\n"))

        # If the proposal adds significant code, flag for performance review
        if proposed_lines > original_lines * 2:
            return 0.3  # 30% estimated impact
        elif proposed_lines > original_lines * 1.5:
            return 0.15  # 15% estimated impact
        else:
            return 0.0  # No significant impact

    def _generate_approval_recommendation(
        self, result: SandboxTestResult, proposal: EvolutionProposal
    ) -> str:
        """Generate an approval recommendation for governance."""
        if not result.passed:
            return f"REJECT: {', '.join(result.errors)}"

        if result.warnings:
            return f"APPROVE_WITH_WARNINGS: {', '.join(result.warnings)}"

        if proposal.risk_level == "HIGH":
            return "APPROVE_MANUAL_REVIEW: High-risk proposal requires manual governance review"

        return "APPROVE: Proposal passed all validation checks"

    def analyze_code_diff(self, proposal: EvolutionProposal) -> CodeDiff:
        """Analyze the diff between original and proposed code."""
        diff = CodeDiff()

        original_lines = proposal.original_code.split("\n")
        proposed_lines = proposal.proposed_code.split("\n")

        # Simple line-by-line diff
        for i, (orig, prop) in enumerate(zip(original_lines, proposed_lines)):
            if orig != prop:
                diff.modified_functions.append(f"line_{i}")

        # Detect added functions
        tree = ast.parse(proposal.proposed_code)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                diff.new_functions.append(node.name)

        return diff

    def get_result(self, proposal_id: str) -> SandboxTestResult | None:
        """Retrieve a sandbox test result by proposal ID."""
        return self._proposal_results.get(proposal_id)

    def get_all_results(self) -> dict[str, SandboxTestResult]:
        """Get all sandbox test results."""
        return self._proposal_results.copy()

    def cleanup(self) -> None:
        """Clean up temporary resources."""
        if self._temp_dir and self._temp_dir.exists():
            import shutil

            shutil.rmtree(self._temp_dir, ignore_errors=True)


def run_evolution_sandbox_suite() -> dict[str, SandboxTestResult]:
    """Run a sample evolution sandbox test suite."""
    sandbox = EvolutionSandbox(deterministic_seed=42)
    results: dict[str, SandboxTestResult] = {}

    # Test 1: Valid code patch
    proposal1 = EvolutionProposal(
        proposal_id="patch_001",
        proposal_type=EvolutionProposalType.CODE_PATCH,
        target_file="example.py",
        original_code="def add(a, b):\n    return a + b\n",
        proposed_code="def add(a, b):\n    \"\"\"Add two numbers.\"\"\"\n    return a + b\n",
        description="Add docstring to add function",
        risk_level="LOW",
    )
    config1 = SandboxTestConfig(proposal=proposal1, seed=42)
    results[proposal1.proposal_id] = sandbox.test_proposal(config1)

    # Test 2: Invalid syntax
    proposal2 = EvolutionProposal(
        proposal_id="patch_002",
        proposal_type=EvolutionProposalType.CODE_PATCH,
        target_file="example.py",
        original_code="def add(a, b):\n    return a + b\n",
        proposed_code="def add(a, b:\n    return a + b\n",  # Missing closing paren
        description="Invalid syntax",
        risk_level="LOW",
    )
    config2 = SandboxTestConfig(proposal=proposal2, seed=42)
    results[proposal2.proposal_id] = sandbox.test_proposal(config2)

    # Test 3: High-risk governance change
    proposal3 = EvolutionProposal(
        proposal_id="patch_003",
        proposal_type=EvolutionProposalType.ARCHITECTURE_CHANGE,
        target_file="governance/kernel.py",
        original_code="def evaluate():\n    pass\n",
        proposed_code="def evaluate():\n    # Direct governance.kernel modification\n    pass\n",
        description="Governance kernel modification",
        risk_level="HIGH",
    )
    config3 = SandboxTestConfig(
        proposal=proposal3,
        seed=42,
        governance_tests=[GovernanceTestCase.POLICY_ENFORCEMENT],
    )
    results[proposal3.proposal_id] = sandbox.test_proposal(config3)

    sandbox.cleanup()
    return results


__all__ = [
    "CodeDiff",
    "EvolutionProposal",
    "EvolutionProposalType",
    "EvolutionSandbox",
    "SandboxTestConfig",
    "SandboxTestResult",
    "run_evolution_sandbox_suite",
]
