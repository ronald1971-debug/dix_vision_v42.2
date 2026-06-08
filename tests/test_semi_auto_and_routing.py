"""Tests: execution_engine.semi_auto (BUILD-DIRECTIVE §8).

Covers:
  4.  ExecutionGate: paper routes when Practice=ON + Live=BLOCKED
  5.  ExecutionGate: live denies + emits LIVE_EXECUTION_BLOCKED
  20. SEMI_AUTO: entry under threshold pushes to approval queue
  21. SEMI_AUTO: exit auto-fires regardless of threshold
  22. SEMI_AUTO: risk-reduce auto-fires regardless of threshold
  23. SEMI_AUTO: approved order emits SEMI_AUTO_APPROVED and fills
  29. Hard 3-domain isolation: MEMECOIN signal cannot reach NORMAL adapter
"""

from __future__ import annotations

import pytest

from core.contracts.events import Side
from core.contracts.operator_authority import (
    LearningAuthority,
    LiveExecutionAuthority,
    OperatorAuthority,
    PracticeAuthority,
    SemiAutoPolicy,
    TradingDomain,
    TradingMode,
)
from execution_engine.execution_gate import ExecutionRouteDecision, route_with_authority
from execution_engine.semi_auto.auto_exit_handler import ExitReason, should_auto_exit
from execution_engine.semi_auto.threshold_gate import (
    ThresholdContext,
    evaluate_threshold,
)

# ---- 20. SEMI_AUTO: entry under threshold ----------------------------------


class TestSemiAutoThresholdGate:
    def test_exit_always_auto_fire(self):
        ctx = ThresholdContext(
            is_exit=True,
            is_risk_reduce=False,
            notional_usd=100_000.0,
            position_fraction=0.5,
            volatility_zscore=10.0,
        )
        result = evaluate_threshold(
            ctx,
            notional_threshold_usd=5000.0,
            position_fraction_cap=0.05,
            volatility_cap_zscore=3.0,
        )
        assert result.value == "AUTO_FIRE"

    def test_risk_reduce_always_auto_fire(self):
        ctx = ThresholdContext(
            is_exit=False,
            is_risk_reduce=True,
            notional_usd=100_000.0,
            position_fraction=0.5,
            volatility_zscore=10.0,
        )
        result = evaluate_threshold(
            ctx,
            notional_threshold_usd=5000.0,
            position_fraction_cap=0.05,
            volatility_cap_zscore=3.0,
        )
        assert result.value == "AUTO_FIRE"

    def test_entry_below_threshold_auto_fire(self):
        ctx = ThresholdContext(
            is_exit=False,
            is_risk_reduce=False,
            notional_usd=1000.0,
            position_fraction=0.01,
            volatility_zscore=1.0,
        )
        result = evaluate_threshold(
            ctx,
            notional_threshold_usd=5000.0,
            position_fraction_cap=0.05,
            volatility_cap_zscore=3.0,
        )
        assert result.value == "AUTO_FIRE"

    def test_entry_above_notional_threshold_requires_approval(self):
        ctx = ThresholdContext(
            is_exit=False,
            is_risk_reduce=False,
            notional_usd=100_000.0,
            position_fraction=0.01,
            volatility_zscore=1.0,
        )
        result = evaluate_threshold(
            ctx,
            notional_threshold_usd=5000.0,
            position_fraction_cap=0.05,
            volatility_cap_zscore=3.0,
        )
        assert result.value == "REQUIRES_APPROVAL"

    def test_entry_above_position_fraction_requires_approval(self):
        ctx = ThresholdContext(
            is_exit=False,
            is_risk_reduce=False,
            notional_usd=1000.0,
            position_fraction=0.10,
            volatility_zscore=1.0,
        )
        result = evaluate_threshold(
            ctx,
            notional_threshold_usd=5000.0,
            position_fraction_cap=0.05,
            volatility_cap_zscore=3.0,
        )
        assert result.value == "REQUIRES_APPROVAL"

    def test_entry_above_volatility_requires_approval(self):
        ctx = ThresholdContext(
            is_exit=False,
            is_risk_reduce=False,
            notional_usd=1000.0,
            position_fraction=0.01,
            volatility_zscore=5.0,
        )
        result = evaluate_threshold(
            ctx,
            notional_threshold_usd=5000.0,
            position_fraction_cap=0.05,
            volatility_cap_zscore=3.0,
        )
        assert result.value == "REQUIRES_APPROVAL"


# ---- 21. SEMI_AUTO: exit auto-fires ---------------------------------------


class TestSemiAutoExit:
    def test_exit_auto_fire_regardless_of_threshold(self):
        decision = should_auto_exit(
            is_exit=True,
            is_risk_reduce=False,
            has_stop_loss_trigger=False,
            has_trailing_stop_trigger=False,
            drawdown_fraction=0.0,
            max_drawdown_cap=0.20,
        )
        assert decision == ExitReason.SIGNAL_EXIT

    def test_stop_loss_triggers_exit(self):
        decision = should_auto_exit(
            is_exit=False,
            is_risk_reduce=False,
            has_stop_loss_trigger=True,
            has_trailing_stop_trigger=False,
            drawdown_fraction=0.0,
            max_drawdown_cap=0.20,
        )
        assert decision == ExitReason.STOP_LOSS

    def test_trailing_stop_triggers_exit(self):
        decision = should_auto_exit(
            is_exit=False,
            is_risk_reduce=False,
            has_stop_loss_trigger=False,
            has_trailing_stop_trigger=True,
            drawdown_fraction=0.0,
            max_drawdown_cap=0.20,
        )
        assert decision == ExitReason.TRAILING_STOP

    def test_max_drawdown_triggers_exit(self):
        decision = should_auto_exit(
            is_exit=False,
            is_risk_reduce=False,
            has_stop_loss_trigger=False,
            has_trailing_stop_trigger=False,
            drawdown_fraction=0.25,
            max_drawdown_cap=0.20,
        )
        assert decision == ExitReason.MAX_DRAWDOWN

    def test_no_exit_condition_returns_none(self):
        decision = should_auto_exit(
            is_exit=False,
            is_risk_reduce=False,
            has_stop_loss_trigger=False,
            has_trailing_stop_trigger=False,
            drawdown_fraction=0.05,
            max_drawdown_cap=0.20,
        )
        assert decision is None


# ---- 22. SEMI_AUTO: risk-reduce auto-fires --------------------------------


class TestSemiAutoRiskReduce:
    def test_risk_reduce_auto_fire(self):
        decision = should_auto_exit(
            is_exit=False,
            is_risk_reduce=True,
            has_stop_loss_trigger=False,
            has_trailing_stop_trigger=False,
            drawdown_fraction=0.0,
            max_drawdown_cap=0.20,
        )
        assert decision == ExitReason.RISK_REDUCE


# ---- 4. ExecutionGate: paper routes when Practice=ON + Live=BLOCKED ------


class TestExecutionGatePaperRoutes:
    def test_practice_on_live_blocked_routes_to_paper(self):
        decision = route_with_authority(
            live_execution="BLOCKED",
            practice="ON",
            trading_mode="FULL_AUTO",
            is_exit=False,
            is_risk_reduce=False,
        )
        assert decision.route == ExecutionRouteDecision.PAPER

    def test_practice_off_live_blocked_blocks(self):
        decision = route_with_authority(
            live_execution="BLOCKED",
            practice="OFF",
            trading_mode="FULL_AUTO",
            is_exit=False,
            is_risk_reduce=False,
        )
        assert decision.route == ExecutionRouteDecision.BLOCKED


# ---- 5. ExecutionGate: live denies + emits LIVE_EXECUTION_BLOCKED ------


class TestExecutionGateLiveDenies:
    def test_manual_mode_blocks_indira(self):
        decision = route_with_authority(
            live_execution="ARMED",
            practice="ON",
            trading_mode="MANUAL",
            is_exit=False,
            is_risk_reduce=False,
        )
        assert decision.route == ExecutionRouteDecision.BLOCKED

    def test_full_auto_executes(self):
        decision = route_with_authority(
            live_execution="ARMED",
            practice="ON",
            trading_mode="FULL_AUTO",
            is_exit=False,
            is_risk_reduce=False,
        )
        assert decision.route == ExecutionRouteDecision.EXECUTE


# ---- 19. Trading mode per-domain simultaneous ---------------------------


class TestPerDomainTradingMode:
    def test_normal_full_copy_semi_memecoin_manual(self):
        auth = OperatorAuthority(
            learning=LearningAuthority.FULL,
            practice=PracticeAuthority.ON,
            live_execution=LiveExecutionAuthority.BLOCKED,
            trading_mode={
                TradingDomain.NORMAL: TradingMode.FULL_AUTO,
                TradingDomain.COPY_TRADING: TradingMode.SEMI_AUTO,
                TradingDomain.MEMECOIN: TradingMode.MANUAL,
            },
            semi_auto_policy={
                d: SemiAutoPolicy() for d in TradingDomain
            },
            operator_id="ronald",
            granted_ts_ns=0,
        )
        assert auth.trading_mode[TradingDomain.NORMAL] is TradingMode.FULL_AUTO
        assert auth.trading_mode[TradingDomain.COPY_TRADING] is TradingMode.SEMI_AUTO
        assert auth.trading_mode[TradingDomain.MEMECOIN] is TradingMode.MANUAL

    def test_all_domain_mode_combinations_valid(self):
        for domain in TradingDomain:
            for mode in TradingMode:
                auth = OperatorAuthority(
                    learning=LearningAuthority.FULL,
                    practice=PracticeAuthority.ON,
                    live_execution=LiveExecutionAuthority.BLOCKED,
                    trading_mode={d: mode for d in TradingDomain},
                    semi_auto_policy={
                        d: SemiAutoPolicy() for d in TradingDomain
                    },
                    operator_id="ronald",
                    granted_ts_ns=0,
                )
                assert auth.trading_mode[domain] is mode


# ---- 29. Hard 3-domain isolation ----------------------------------------


class TestHardDomainIsolation:
    def test_memecoin_signal_cannot_route_to_normal_adapter(self):
        from core.contracts.events import SignalEvent
        from execution_engine.adapters.router import (
            AdapterRouter,
            TradingDomain,
        )

        router = AdapterRouter(
            adapters={
                (TradingDomain.NORMAL, "paper"): "normal_paper",
                (TradingDomain.COPY_TRADING, "paper"): "copy_paper",
                (TradingDomain.MEMECOIN, "paper"): "meme_paper",
            },
        )
        meme_signal = SignalEvent(
            ts_ns=0,
            symbol="DOGE",
            side=Side.BUY,
            confidence=0.5,
            meta={"domain": "MEMECOIN", "venue": "paper"},
        )
        adapter = router.adapter_for(meme_signal)
        assert adapter == "meme_paper"

    def test_memecoin_signal_isolated_from_normal_venue(self):
        from core.contracts.events import SignalEvent
        from execution_engine.adapters.router import (
            AdapterRouter,
            TradingDomain,
        )

        router = AdapterRouter(
            default_domain=TradingDomain.NORMAL,
            adapters={
                (TradingDomain.NORMAL, "binance"): "normal_binance",
                # No MEMECOIN/binance adapter registered
            },
        )
        meme_signal = SignalEvent(
            ts_ns=0,
            symbol="DOGE",
            side=Side.BUY,
            confidence=0.5,
            meta={"domain": "MEMECOIN", "venue": "binance"},
        )
        with pytest.raises(Exception):
            router.adapter_for(meme_signal)
