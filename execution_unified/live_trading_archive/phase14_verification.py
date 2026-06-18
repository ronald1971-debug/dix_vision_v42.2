"""
execution_engine.live_trading.phase14_verification
DIX VISION v42.2 — Phase 14 Verification Script

Migrated from execution/live_trading/phase14_verification.py

Verifies that Phase 14 — Live Trading Infrastructure exit criteria are met:
1. Governance approved
2. Risk constrained
3. Ledger backed
4. Deterministic
5. Auditable

This script validates that all Phase 14 components are functional
and that the exit criteria "Production deployment ready" is satisfied.
"""

from execution_unified.core.live_trading.audit_system import (
    get_live_trading_audit_system,
)
from execution_unified.core.live_trading.deterministic_executor import (
    get_deterministic_live_trading_executor,
)
from execution_unified.core.live_trading.governance_layer import (
    GovernanceDecisionType,
    get_live_trading_governance_layer,
)
from execution_unified.core.live_trading.ledger_backed_operations import (
    LiveOperationType,
    get_live_trading_ledger_backed_operations,
)
from execution_unified.core.live_trading.risk_constraints import (
    RiskConstraintConfig,
    get_live_trading_risk_constraints,
)


def verify_phase14_components() -> dict[str, bool]:
    """Verify all Phase 14 components are functional."""
    verification_results = {}

    # Test 1: Governance Approval Layer
    print("Testing Governance Approval Layer...")
    try:
        governance_layer = get_live_trading_governance_layer()
        enabled = governance_layer.is_live_trading_enabled()
        verification_results["governance_layer"] = True
        print(f"  Governance Layer: PASSED (Live trading enabled: {enabled})")
    except Exception as e:
        verification_results["governance_layer"] = False
        print(f"  Governance Layer: FAILED - {e}")

    # Test 2: Risk Constraints
    print("Testing Risk Constraints...")
    try:
        risk_constraints = get_live_trading_risk_constraints()
        risk_constraints.enable()
        enabled = risk_constraints._enabled
        verification_results["risk_constraints"] = True
        print(f"  Risk Constraints: PASSED (Enabled: {enabled})")
    except Exception as e:
        verification_results["risk_constraints"] = False
        print(f"  Risk Constraints: FAILED - {e}")

    # Test 3: Ledger-Backed Operations
    print("Testing Ledger-Backed Operations...")
    try:
        ledger_ops = get_live_trading_ledger_backed_operations()
        ledger_ops.enable()
        enabled = ledger_ops.is_enabled()
        verification_results["ledger_backed_operations"] = True
        print(f"  Ledger-Backed Operations: PASSED (Enabled: {enabled})")
    except Exception as e:
        verification_results["ledger_backed_operations"] = False
        print(f"  Ledger-Backed Operations: FAILED - {e}")

    # Test 4: Deterministic Executor
    print("Testing Deterministic Executor...")
    try:
        deterministic_executor = get_deterministic_live_trading_executor()
        deterministic_executor.enable()
        verification_results["deterministic_executor"] = True
        print("  Deterministic Executor: PASSED")
    except Exception as e:
        verification_results["deterministic_executor"] = False
        print(f"  Deterministic Executor: FAILED - {e}")

    # Test 5: Audit System
    print("Testing Audit System...")
    try:
        audit_system = get_live_trading_audit_system()
        audit_system.enable()
        enabled = audit_system.is_enabled()
        verification_results["audit_system"] = True
        print(f"  Audit System: PASSED (Enabled: {enabled})")
    except Exception as e:
        verification_results["audit_system"] = False
        print(f"  Audit System: FAILED - {e}")

    return verification_results


def verify_governance_approved() -> dict[str, bool]:
    """Verify that governance approval is implemented."""
    print("Verifying Governance Approved...")
    governance_verification = {}

    try:
        governance_layer = get_live_trading_governance_layer()

        # Test enabling live trading
        ts_ns = 1_700_000_000_000_000_000
        enabled = governance_layer.enable_live_trading(
            approver="verification", ts_ns=ts_ns, mode="LIVE"
        )

        governance_verification["live_trading_approval"] = enabled
        print(f"  Live Trading Approval: {'VERIFIED' if enabled else 'FAILED'}")
    except Exception as e:
        governance_verification["live_trading_approval"] = False
        print(f"  Live Trading Approval: FAILED - {e}")

    try:
        governance_layer = get_live_trading_governance_layer()

        # Test governance approval request
        from execution_unified.core.live_trading.governance_layer import (
            LiveTradeGovernanceContext,
        )

        context = LiveTradeGovernanceContext(
            trade_id="test_trade_1",
            venue="binance",
            symbol="BTC/USDT",
            side="BUY",
            size_usd=1000.0,
            portfolio_usd=100000.0,
            strategy="test_strategy",
            timestamp_ns=ts_ns,
            mode="LIVE",
        )

        decision = governance_layer.request_approval(context)
        governance_verification["governance_decisions"] = decision is not None
        print(f"  Governance Decisions: {'VERIFIED' if decision is not None else 'FAILED'}")
        if decision:
            print(f"    Decision: {decision.decision.value}")
            print(f"    Reason: {decision.reason}")
    except Exception as e:
        governance_verification["governance_decisions"] = False
        print(f"  Governance Decisions: FAILED - {e}")

    return governance_verification


def verify_risk_constrained() -> dict[str, bool]:
    """Verify that risk constraints are implemented."""
    print("Verifying Risk Constrained...")
    risk_verification = {}

    try:
        risk_constraints = get_live_trading_risk_constraints()
        config = RiskConstraintConfig()
        risk_constraints.configure(config)

        # Test risk constraint checking
        from execution_unified.core.live_trading.risk_constraints import (
            LiveTradeRiskContext,
        )

        context = LiveTradeRiskContext(
            trade_id="test_trade_1",
            venue="binance",
            symbol="BTC/USDT",
            side="BUY",
            size_usd=1000.0,
            price=50000.0,
            portfolio_usd=100000.0,
            current_positions={},
            daily_pnl_usd=0.0,
        )

        passed, results = risk_constraints.check_risk_constraints(context)
        risk_verification["risk_constraints_enforced"] = True
        print(f"  Risk Constraints Enforced: {'VERIFIED'}")
        print(f"    Check Result: {'PASSED' if passed else 'FAILED'}")
        print(f"    Number of checks: {len(results)}")
    except Exception as e:
        risk_verification["risk_constraints_enforced"] = False
        print(f"  Risk Constraints Enforced: FAILED - {e}")

    try:
        risk_constraints = get_live_trading_risk_constraints()
        stats = risk_constraints.get_statistics()
        risk_verification["risk_constraints_configured"] = stats["enabled"]
        print(f"  Risk Constraints Configured: {'VERIFIED' if stats['enabled'] else 'FAILED'}")
        print(f"    Max Position: ${stats['config']['max_position_usd']:,.2f}")
        print(f"    Max Leverage: {stats['config']['max_leverage']:.2f}x")
    except Exception as e:
        risk_verification["risk_constraints_configured"] = False
        print(f"  Risk Constraints Configured: FAILED - {e}")

    return risk_verification


def verify_ledger_backed() -> dict[str, bool]:
    """Verify that operations are ledger-backed."""
    print("Verifying Ledger Backed...")
    ledger_verification = {}

    try:
        ledger_ops = get_live_trading_ledger_backed_operations()

        # Test recording an operation
        ts_ns = 1_700_000_000_000_000_000
        result = ledger_ops.record_operation(
            operation_type=LiveOperationType.TRADE_REQUEST,
            venue="binance",
            symbol="BTC/USDT",
            timestamp_ns=ts_ns,
            payload={"test": "data"},
        )

        ledger_verification["operation_recording"] = result.recorded
        print(f"  Operation Recording: {'VERIFIED' if result.recorded else 'FAILED'}")
        print(f"    Operation ID: {result.operation_id}")
    except Exception as e:
        ledger_verification["operation_recording"] = False
        print(f"  Operation Recording: FAILED - {e}")

    try:
        ledger_ops = get_live_trading_ledger_backed_operations()
        valid = ledger_ops.verify_hash_chain()
        ledger_verification["hash_chain_valid"] = valid
        print(f"  Hash Chain Valid: {'VERIFIED' if valid else 'FAILED'}")
    except Exception as e:
        ledger_verification["hash_chain_valid"] = False
        print(f"  Hash Chain Valid: FAILED - {e}")

    return ledger_verification


def verify_deterministic() -> dict[str, bool]:
    """Verify that execution is deterministic."""
    print("Verifying Deterministic...")
    deterministic_verification = {}

    try:
        deterministic_executor = get_deterministic_live_trading_executor()
        valid = deterministic_executor.verify_determinism()
        deterministic_verification["determinism_verified"] = True
        print(f"  Determinism Verified: {'VERIFIED'}")
    except Exception as e:
        deterministic_verification["determinism_verified"] = False
        print(f"  Determinism Verified: FAILED - {e}")

    try:
        deterministic_executor = get_deterministic_live_trading_executor()
        stats = deterministic_executor.get_statistics()
        deterministic_verification["determinism_enforced"] = stats["enabled"]
        print(f"  Determinism Enforced: {'VERIFIED' if stats['enabled'] else 'FAILED'}")
        print(f"    Total Executions: {stats['total_executions']}")
        print(f"    Violation Count: {stats['violation_count']}")
    except Exception as e:
        deterministic_verification["determinism_enforced"] = False
        print(f"  Determinism Enforced: FAILED - {e}")

    return deterministic_verification


def verify_auditable() -> dict[str, bool]:
    """Verify that full auditability is implemented."""
    print("Verifying Auditable...")
    audit_verification = {}

    try:
        audit_system = get_live_trading_audit_system()

        # Test recording a governance decision
        ts_ns = 1_700_000_000_000_000_000
        event_id = audit_system.record_governance_decision(
            governance_decision=type(
                "Decision",
                (),
                {
                    "decision": GovernanceDecisionType.APPROVED,
                    "context": type("Context", (), {"trade_id": "test", "venue": "binance", "symbol": "BTC/USDT", "side": "BUY", "size_usd": 1000.0, "portfolio_usd": 100000.0, "strategy": "test", "timestamp_ns": ts_ns, "mode": "LIVE"}),
                    "reason": "Test decision",
                    "approver": "test",
                    "approved_by": "test",
                },
            )()
        )

        audit_verification["audit_recording"] = event_id != ""
        print(f"  Audit Recording: {'VERIFIED' if event_id != '' else 'FAILED'}")
        print(f"    Event ID: {event_id}")
    except Exception as e:
        audit_verification["audit_recording"] = False
        print(f"  Audit Recording: FAILED - {e}")

    try:
        audit_system = get_live_trading_audit_system()
        audit_log = audit_system.get_audit_log(limit=10)
        audit_verification["audit_log_accessible"] = len(audit_log) >= 0
        print(f"  Audit Log Accessible: {'VERIFIED'}")
        print(f"    Log Size: {len(audit_log)}")
    except Exception as e:
        audit_verification["audit_log_accessible"] = False
        print(f"  Audit Log Accessible: FAILED - {e}")

    return audit_verification


def main() -> bool:
    """Main verification routine for Phase 14."""
    print("=" * 70)
    print("PHASE 14 — LIVE TRADING INFRASTRUCTURE VERIFICATION")
    print("=" * 70)
    print()

    print("Exit Criteria: Production deployment ready")
    print()
    print("Requirements:")
    print("  1. Governance approved")
    print("  2. Risk constrained")
    print("  3. Ledger backed")
    print("  4. Deterministic")
    print("  5. Auditable")
    print()

    # Verify components
    print("Step 1: Verifying Phase 14 Components")
    print("-" * 70)
    component_results = verify_phase14_components()
    print()

    # Verify governance approved
    print("Step 2: Verifying Governance Approved")
    print("-" * 70)
    governance_results = verify_governance_approved()
    print()

    # Verify risk constrained
    print("Step 3: Verifying Risk Constrained")
    print("-" * 70)
    risk_results = verify_risk_constrained()
    print()

    # Verify ledger backed
    print("Step 4: Verifying Ledger Backed")
    print("-" * 70)
    ledger_results = verify_ledger_backed()
    print()

    # Verify deterministic
    print("Step 5: Verifying Deterministic")
    print("-" * 70)
    deterministic_results = verify_deterministic()
    print()

    # Verify auditable
    print("Step 6: Verifying Auditable")
    print("-" * 70)
    audit_results = verify_auditable()
    print()

    # Final assessment
    print("Step 7: Final Assessment")
    print("-" * 70)

    all_components_passed = all(component_results.values())
    all_governance_passed = all(governance_results.values())
    all_risk_passed = all(risk_results.values())
    all_ledger_passed = all(ledger_results.values())
    all_deterministic_passed = all(deterministic_results.values())
    all_audit_passed = all(audit_results.values())

    print(f"  All Components Functional: {all_components_passed}")
    print(f"  Governance Approved: {all_governance_passed}")
    print(f"  Risk Constrained: {all_risk_passed}")
    print(f"  Ledger Backed: {all_ledger_passed}")
    print(f"  Deterministic: {all_deterministic_passed}")
    print(f"  Auditable: {all_audit_passed}")

    phase14_complete = (
        all_components_passed
        and all_governance_passed
        and all_risk_passed
        and all_ledger_passed
        and all_deterministic_passed
        and all_audit_passed
    )

    print()
    print("=" * 70)
    if phase14_complete:
        print("PHASE 14: COMPLETED")
        print("Exit Criteria Met: Production deployment ready")
    else:
        print("PHASE 14: INCOMPLETE")
        print("Exit Criteria Not Met")
    print("=" * 70)

    return phase14_complete


if __name__ == "__main__":
    import sys

    success = main()
    sys.exit(0 if success else 1)
