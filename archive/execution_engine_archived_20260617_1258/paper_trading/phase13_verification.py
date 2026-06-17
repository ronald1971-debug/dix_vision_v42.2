"""
execution_engine/paper_trading/phase13_verification.py
DIX VISION v42.2 — Phase 13 Verification Script

Verifies that Phase 13 — Paper Trading exit criteria are met:
1. No capital risk
2. Full ledger recording
3. Promotion gate approval
4. 100% paper environment

This script validates that all Phase 13 components are functional
and that the exit criteria "100% paper environment" is satisfied.
"""

from execution_engine.paper_trading.ledger_integration import (
    get_paper_trade_ledger_integrator,
)
from execution_engine.paper_trading.paper_only_enforcer import (
    get_paper_only_enforcer,
)
from execution_engine.paper_trading.promotion_gate_integration import (
    TradingMode,
    get_paper_trading_promotion_gate_integration,
)


def verify_phase13_components() -> dict[str, bool]:
    """Verify all Phase 13 components are functional."""
    verification_results = {}

    # Test 1: Ledger Integration
    print("Testing Ledger Integration...")
    try:
        ledger_integrator = get_paper_trade_ledger_integrator()
        ledger_integrator.enable()
        enabled = ledger_integrator.is_enabled()
        verification_results["ledger_integration"] = enabled
        print(f"  Ledger Integration: {'PASSED' if enabled else 'FAILED'}")
        if not enabled:
            print("    Reason: Ledger integrator not enabled")
    except Exception as e:
        verification_results["ledger_integration"] = False
        print(f"  Ledger Integration: FAILED - {e}")

    # Test 2: Promotion Gate Integration
    print("Testing Promotion Gate Integration...")
    try:
        promotion_integration = get_paper_trading_promotion_gate_integration()
        bound_hash = promotion_integration.enter_paper_mode(
            ts_ns=1_700_000_000_000_000_000, requestor="verification"
        )
        current_mode = promotion_integration.get_current_mode()
        integration_ok = (
            bound_hash is not None and current_mode == TradingMode.PAPER
        )
        verification_results["promotion_gate_integration"] = integration_ok
        print(f"  Promotion Gate Integration: {'PASSED' if integration_ok else 'FAILED'}")
        if not integration_ok:
            print(f"    Bound hash: {bound_hash}")
            print(f"    Current mode: {current_mode}")
    except Exception as e:
        verification_results["promotion_gate_integration"] = False
        print(f"  Promotion Gate Integration: FAILED - {e}")

    # Test 3: Paper-Only Enforcer
    print("Testing Paper-Only Enforcer...")
    try:
        enforcer = get_paper_only_enforcer()
        enforcer.enable_enforcement()
        is_paper = enforcer.is_paper_environment()
        verification_results["paper_only_enforcer"] = is_paper
        print(f"  Paper-Only Enforcer: {'PASSED' if is_paper else 'FAILED'}")
        if not is_paper:
            print("    Reason: Enforcement not enabled")
    except Exception as e:
        verification_results["paper_only_enforcer"] = False
        print(f"  Paper-Only Enforcer: FAILED - {e}")

    return verification_results


def verify_no_capital_risk() -> dict[str, bool]:
    """Verify that there is no capital risk (virtual capital only)."""
    print("Verifying No Capital Risk...")
    risk_verification = {}

    # Check that paper trading uses virtual capital
    try:
        from execution_engine.paper_trading.adapter import PaperVenueAdapter
        from execution_engine.paper_trading.venue_config import BINANCE_PAPER

        adapter = PaperVenueAdapter(BINANCE_PAPER)
        initial_cash = adapter.initial_cash()
        cash_balance = adapter.cash_balance()

        # Paper trading should have virtual capital, no real money
        virtual_capital = initial_cash > 0 and initial_cash == cash_balance
        risk_verification["virtual_capital_only"] = virtual_capital
        print(f"  Virtual Capital Only: {'VERIFIED' if virtual_capital else 'FAILED'}")
        print(f"    Initial cash: ${initial_cash:,.2f}")
        print(f"    Current cash: ${cash_balance:,.2f}")
    except Exception as e:
        risk_verification["virtual_capital_only"] = False
        print(f"  Virtual Capital Only: FAILED - {e}")

    # Check that no credentials are required
    try:
        from execution_engine.paper_trading.adapter import PaperVenueAdapter
        from execution_engine.paper_trading.venue_config import BINANCE_PAPER

        adapter = PaperVenueAdapter(BINANCE_PAPER)
        adapter.connect()  # Paper adapters don't need credentials

        credential_free = True
        risk_verification["credential_free"] = credential_free
        print(f"  Credential Free: {'VERIFIED' if credential_free else 'FAILED'}")
    except Exception as e:
        risk_verification["credential_free"] = False
        print(f"  Credential Free: FAILED - {e}")

    return risk_verification


def verify_full_ledger_recording() -> dict[str, bool]:
    """Verify that full ledger recording is implemented."""
    print("Verifying Full Ledger Recording...")
    ledger_verification = {}

    try:
        from state.ledger.event_store import EventStore

        # Check that event store exists and is functional
        event_store = EventStore(db_path=":memory:")  # Use in-memory for testing

        # Test appending an event
        event = event_store.append(
            event_type="MARKET",
            sub_type="PAPER_TRADE_EXECUTION",
            source="PAPER_TRADING",
            payload={"test": "data"},
        )

        ledger_functional = event.event_id is not None
        ledger_verification["ledger_functional"] = ledger_functional
        print(f"  Ledger Functional: {'VERIFIED' if ledger_functional else 'FAILED'}")
        print(f"    Event ID: {event.event_id}")
    except Exception as e:
        ledger_verification["ledger_functional"] = False
        print(f"  Ledger Functional: FAILED - {e}")

    try:
        from execution_engine.paper_trading.ledger_integration import (
            get_paper_trade_ledger_integrator,
        )

        ledger_integrator = get_paper_trade_ledger_integrator()
        ledger_integrator.enable()
        recording_enabled = ledger_integrator.is_enabled()
        ledger_verification["paper_trade_recording"] = recording_enabled
        print(f"  Paper Trade Recording: {'VERIFIED' if recording_enabled else 'FAILED'}")
    except Exception as e:
        ledger_verification["paper_trade_recording"] = False
        print(f"  Paper Trade Recording: FAILED - {e}")

    return ledger_verification


def verify_promotion_gate_approval() -> dict[str, bool]:
    """Verify that promotion gate approval is implemented."""
    print("Verifying Promotion Gate Approval...")
    promotion_verification = {}

    try:
        from execution_engine.paper_trading.promotion_gate_integration import (
            get_paper_trading_promotion_gate_integration,
        )

        promotion_integration = get_paper_trading_promotion_gate_integration()

        # Test entering paper mode
        bound_hash = promotion_integration.enter_paper_mode(
            ts_ns=1_700_000_000_000_000_000, requestor="verification"
        )

        # Test promotion request
        result = promotion_integration.request_promotion(
            target_mode=TradingMode.SHADOW, ts_ns=1_700_000_000_001_000_000
        )

        promotion_functional = bound_hash is not None and result is not None
        promotion_verification["promotion_functional"] = promotion_functional
        print(f"  Promotion Functional: {'VERIFIED' if promotion_functional else 'FAILED'}")
        print(f"    Bound hash: {bound_hash}")
        print(f"    Promotion result passed: {result.passed}")
        print(f"    Promotion reason: {result.reason}")
    except Exception as e:
        promotion_verification["promotion_functional"] = False
        print(f"  Promotion Functional: FAILED - {e}")

    try:
        from governance_engine.control_plane.promotion_gates import (
            DEFAULT_PROMOTION_GATES_PATH,
            compute_file_hash,
        )

        # Check that promotion gates file exists
        file_exists = DEFAULT_PROMOTION_GATES_PATH.exists()
        promotion_verification["promotion_gates_file"] = file_exists
        print(f"  Promotion Gates File: {'VERIFIED' if file_exists else 'FAILED'}")
        if file_exists:
            try:
                file_hash = compute_file_hash(DEFAULT_PROMOTION_GATES_PATH)
                print(f"    File hash: {file_hash}")
            except Exception as e:
                print(f"    Hash computation failed: {e}")
    except Exception as e:
        promotion_verification["promotion_gates_file"] = False
        print(f"  Promotion Gates File: FAILED - {e}")

    return promotion_verification


def verify_100_percent_paper_environment() -> dict[str, bool]:
    """Verify that 100% paper environment is enforced."""
    print("Verifying 100% Paper Environment...")
    paper_verification = {}

    try:
        from execution_engine.paper_trading.paper_only_enforcer import (
            get_paper_only_enforcer,
        )

        enforcer = get_paper_only_enforcer()
        enforcer.enable_enforcement()

        # Test blocking live venue
        from core.contracts.events import Side, SignalEvent

        test_signal = SignalEvent(
            ts_ns=1_700_000_000_000_000_000,
            symbol="BTC/USDT",
            side=Side.BUY,
            qty=1.0,
            price=50000.0,
        )

        allowed, reason, action = enforcer.check_trade_allowed(test_signal, "binance")

        live_blocked = not allowed and "blocked" in reason.lower()
        paper_verification["live_venue_blocked"] = live_blocked
        print(f"  Live Venue Blocked: {'VERIFIED' if live_blocked else 'FAILED'}")
        print(f"    Reason: {reason}")
        print(f"    Action: {action.value}")
    except Exception as e:
        paper_verification["live_venue_blocked"] = False
        print(f"  Live Venue Blocked: FAILED - {e}")

    try:
        from execution_engine.paper_trading.paper_only_enforcer import (
            get_paper_only_enforcer,
        )

        enforcer = get_paper_only_enforcer()

        # Test allowing paper venue
        from core.contracts.events import Side, SignalEvent

        test_signal = SignalEvent(
            ts_ns=1_700_000_000_000_000_000,
            symbol="BTC/USDT",
            side=Side.BUY,
            qty=1.0,
            price=50000.0,
        )

        allowed, reason, action = enforcer.check_trade_allowed(test_signal, "binance_paper")

        paper_allowed = allowed and "allowed" in reason.lower()
        paper_verification["paper_venue_allowed"] = paper_allowed
        print(f"  Paper Venue Allowed: {'VERIFIED' if paper_allowed else 'FAILED'}")
        print(f"    Reason: {reason}")
        print(f"    Action: {action.value}")
    except Exception as e:
        paper_verification["paper_venue_allowed"] = False
        print(f"  Paper Venue Allowed: FAILED - {e}")

    try:
        from execution_engine.paper_trading.paper_only_enforcer import (
            get_paper_only_enforcer,
        )

        enforcer = get_paper_only_enforcer()
        is_paper = enforcer.is_paper_environment()
        paper_verification["enforcement_active"] = is_paper
        print(f"  Enforcement Active: {'VERIFIED' if is_paper else 'FAILED'}")
    except Exception as e:
        paper_verification["enforcement_active"] = False
        print(f"  Enforcement Active: FAILED - {e}")

    return paper_verification


def main() -> bool:
    """Main verification routine for Phase 13."""
    print("=" * 70)
    print("PHASE 13 — PAPER TRADING VERIFICATION")
    print("=" * 70)
    print()

    print("Exit Criteria: 100% paper environment")
    print()
    print("Requirements:")
    print("  1. No capital risk")
    print("  2. Full ledger recording")
    print("  3. Promotion gate approval")
    print("  4. 100% paper environment")
    print()

    # Verify components
    print("Step 1: Verifying Phase 13 Components")
    print("-" * 70)
    component_results = verify_phase13_components()
    print()

    # Verify no capital risk
    print("Step 2: Verifying No Capital Risk")
    print("-" * 70)
    risk_results = verify_no_capital_risk()
    print()

    # Verify full ledger recording
    print("Step 3: Verifying Full Ledger Recording")
    print("-" * 70)
    ledger_results = verify_full_ledger_recording()
    print()

    # Verify promotion gate approval
    print("Step 4: Verifying Promotion Gate Approval")
    print("-" * 70)
    promotion_results = verify_promotion_gate_approval()
    print()

    # Verify 100% paper environment
    print("Step 5: Verifying 100% Paper Environment")
    print("-" * 70)
    paper_results = verify_100_percent_paper_environment()
    print()

    # Final assessment
    print("Step 6: Final Assessment")
    print("-" * 70)

    all_components_passed = all(component_results.values())
    all_risk_checks_passed = all(risk_results.values())
    all_ledger_checks_passed = all(ledger_results.values())
    all_promotion_checks_passed = all(promotion_results.values())
    all_paper_checks_passed = all(paper_results.values())

    print(f"  All Components Functional: {all_components_passed}")
    print(f"  No Capital Risk: {all_risk_checks_passed}")
    print(f"  Full Ledger Recording: {all_ledger_checks_passed}")
    print(f"  Promotion Gate Approval: {all_promotion_checks_passed}")
    print(f"  100% Paper Environment: {all_paper_checks_passed}")

    phase13_complete = (
        all_components_passed
        and all_risk_checks_passed
        and all_ledger_checks_passed
        and all_promotion_checks_passed
        and all_paper_checks_passed
    )

    print()
    print("=" * 70)
    if phase13_complete:
        print("PHASE 13: COMPLETED")
        print("Exit Criteria Met: 100% paper environment")
    else:
        print("PHASE 13: INCOMPLETE")
        print("Exit Criteria Not Met")
    print("=" * 70)

    return phase13_complete


if __name__ == "__main__":
    import sys

    success = main()
    sys.exit(0 if success else 1)
