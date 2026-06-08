"""Tests: core.contracts.operator_authority (BUILD-DIRECTIVE §1).

Covers:
  1.  OperatorAuthority value-object validation (all fields, __post_init__ guards)
  2.  SemiAutoPolicy validation (all threshold fields)
  3.  FreezePolicy defers to OperatorAuthority when present
"""

from __future__ import annotations

import pytest

from core.contracts.learning_evolution_freeze import LearningEvolutionFreezePolicy
from core.contracts.operator_authority import (
    LearningAuthority,
    LiveExecutionAuthority,
    OperatorAuthority,
    PracticeAuthority,
    SemiAutoPolicy,
    TradingDomain,
    TradingMode,
)

# ---- 1. OperatorAuthority value-object validation ------------------------


class TestOperatorAuthorityDefaults:
    def test_default_learning_full(self):
        a = OperatorAuthority(operator_id="ronald", granted_ts_ns=0)
        assert a.learning is LearningAuthority.FULL

    def test_default_practice_on(self):
        a = OperatorAuthority(operator_id="ronald", granted_ts_ns=0)
        assert a.practice is PracticeAuthority.ON

    def test_default_live_blocked(self):
        a = OperatorAuthority(operator_id="ronald", granted_ts_ns=0)
        assert a.live_execution is LiveExecutionAuthority.BLOCKED

    def test_default_trading_mode(self):
        a = OperatorAuthority(operator_id="ronald", granted_ts_ns=0)
        assert a.trading_mode[TradingDomain.NORMAL] is TradingMode.FULL_AUTO
        assert a.trading_mode[TradingDomain.COPY_TRADING] is TradingMode.SEMI_AUTO
        assert a.trading_mode[TradingDomain.MEMECOIN] is TradingMode.MANUAL

    def test_default_semi_auto_policy(self):
        a = OperatorAuthority(operator_id="ronald", granted_ts_ns=0)
        p = a.semi_auto_policy[TradingDomain.NORMAL]
        assert p.notional_threshold_usd == 5000.0
        assert p.position_fraction_cap == 0.05
        assert p.volatility_cap_zscore == 3.0

    def test_operator_id_non_empty(self):
        with pytest.raises(ValueError, match="operator_id must be non-empty"):
            OperatorAuthority(operator_id="", granted_ts_ns=0)

    def test_operator_id_empty_raises(self):
        with pytest.raises(ValueError):
            OperatorAuthority(operator_id="", granted_ts_ns=0)

    def test_ts_ns_positive(self):
        with pytest.raises(ValueError, match="granted_ts_ns must be >= 0"):
            OperatorAuthority(operator_id="ronald", granted_ts_ns=-1)

    def test_ts_ns_zero_valid(self):
        a = OperatorAuthority(operator_id="ronald", granted_ts_ns=0)
        assert a.granted_ts_ns == 0

    def test_frozen_slotted(self):
        import dataclasses

        a = OperatorAuthority(operator_id="ronald", granted_ts_ns=0)
        assert dataclasses.is_dataclass(a)
        assert getattr(type(a), "__slots__", None) is not None

    def test_notes_defaults_empty(self):
        a = OperatorAuthority(operator_id="ronald", granted_ts_ns=0)
        assert a.notes == ""

    def test_notes_set(self):
        a = OperatorAuthority(operator_id="ronald", granted_ts_ns=0, notes="test")
        assert a.notes == "test"


class TestOperatorAuthorityExplicit:
    def test_explicit_learning_off(self):
        a = OperatorAuthority(
            learning=LearningAuthority.OFF,
            practice=PracticeAuthority.OFF,
            live_execution=LiveExecutionAuthority.BLOCKED,
            operator_id="ronald",
            granted_ts_ns=1000,
        )
        assert a.learning is LearningAuthority.OFF
        assert a.practice is PracticeAuthority.OFF
        assert a.live_execution is LiveExecutionAuthority.BLOCKED

    def test_all_learning_values(self):
        for lv in LearningAuthority:
            a = OperatorAuthority(
                learning=lv,
                practice=PracticeAuthority.ON,
                live_execution=LiveExecutionAuthority.BLOCKED,
                operator_id="ronald",
                granted_ts_ns=0,
            )
            assert a.learning is lv

    def test_all_practice_values(self):
        for pv in PracticeAuthority:
            a = OperatorAuthority(
                learning=LearningAuthority.FULL,
                practice=pv,
                live_execution=LiveExecutionAuthority.BLOCKED,
                operator_id="ronald",
                granted_ts_ns=0,
            )
            assert a.practice is pv

    def test_all_live_execution_values(self):
        for lv in LiveExecutionAuthority:
            a = OperatorAuthority(
                learning=LearningAuthority.FULL,
                practice=PracticeAuthority.ON,
                live_execution=lv,
                operator_id="ronald",
                granted_ts_ns=0,
            )
            assert a.live_execution is lv


# ---- 2. SemiAutoPolicy validation -----------------------------------------


class TestSemiAutoPolicyDefaults:
    def test_defaults(self):
        p = SemiAutoPolicy()
        assert p.entry_requires_approval is True
        assert p.exit_auto is True
        assert p.risk_reduce_auto is True
        assert p.notional_threshold_usd == 5000.0
        assert p.position_fraction_cap == 0.05
        assert p.volatility_cap_zscore == 3.0

    def test_entry_by_default(self):
        p = SemiAutoPolicy()
        assert p.entry_requires_approval is True

    def test_exit_auto_by_default(self):
        p = SemiAutoPolicy()
        assert p.exit_auto is True

    def test_risk_reduce_auto_by_default(self):
        p = SemiAutoPolicy()
        assert p.risk_reduce_auto is True


class TestSemiAutoPolicyValidation:
    def test_negative_notional_rejected(self):
        with pytest.raises(ValueError, match="notional_threshold_usd must be >= 0"):
            SemiAutoPolicy(notional_threshold_usd=-1.0)

    def test_zero_notional_allowed(self):
        p = SemiAutoPolicy(notional_threshold_usd=0.0)
        assert p.notional_threshold_usd == 0.0

    def test_position_fraction_zero_rejected(self):
        with pytest.raises(ValueError, match="position_fraction_cap must be in"):
            SemiAutoPolicy(position_fraction_cap=0.0)

    def test_position_fraction_negative_rejected(self):
        with pytest.raises(ValueError):
            SemiAutoPolicy(position_fraction_cap=-0.1)

    def test_position_fraction_one_allowed(self):
        p = SemiAutoPolicy(position_fraction_cap=1.0)
        assert p.position_fraction_cap == 1.0

    def test_position_fraction_half(self):
        p = SemiAutoPolicy(position_fraction_cap=0.5)
        assert p.position_fraction_cap == 0.5

    def test_volatility_zero_rejected(self):
        with pytest.raises(ValueError, match="volatility_cap_zscore must be > 0"):
            SemiAutoPolicy(volatility_cap_zscore=0.0)

    def test_volatility_negative_rejected(self):
        with pytest.raises(ValueError):
            SemiAutoPolicy(volatility_cap_zscore=-1.0)

    def test_volatility_small_positive(self):
        p = SemiAutoPolicy(volatility_cap_zscore=0.01)
        assert p.volatility_cap_zscore == 0.01


# ---- 3. FreezePolicy defers to OperatorAuthority --------------------------


class TestFreezePolicyOperatorAuthority:
    def test_full_learning_unfrozen(self):
        from core.contracts.operator_authority import OperatorAuthority

        auth = OperatorAuthority(
            learning=LearningAuthority.FULL,
            practice=PracticeAuthority.ON,
            live_execution=LiveExecutionAuthority.BLOCKED,
            operator_id="ronald",
            granted_ts_ns=0,
        )
        freeze = LearningEvolutionFreezePolicy(
            mode=None,  # type: ignore[arg-type]
            operator_authority=auth,
        )
        assert freeze.is_unfrozen() is True
        assert freeze.is_frozen() is False

    def test_off_learning_frozen(self):
        from core.contracts.operator_authority import OperatorAuthority

        auth = OperatorAuthority(
            learning=LearningAuthority.OFF,
            practice=PracticeAuthority.ON,
            live_execution=LiveExecutionAuthority.BLOCKED,
            operator_id="ronald",
            granted_ts_ns=0,
        )
        freeze = LearningEvolutionFreezePolicy(
            mode=None,  # type: ignore[arg-type]
            operator_authority=auth,
        )
        assert freeze.is_frozen() is True
        assert freeze.is_unfrozen() is False

    def test_shadow_learning_frozen_for_apply(self):
        from core.contracts.operator_authority import OperatorAuthority

        auth = OperatorAuthority(
            learning=LearningAuthority.SHADOW,
            practice=PracticeAuthority.ON,
            live_execution=LiveExecutionAuthority.BLOCKED,
            operator_id="ronald",
            granted_ts_ns=0,
        )
        freeze = LearningEvolutionFreezePolicy(
            mode=None,  # type: ignore[arg-type]
            operator_authority=auth,
        )
        assert freeze.is_frozen() is True
        assert freeze.is_shadow_eligible() is True

    def test_no_authority_falls_back_operator_override(self):
        freeze = LearningEvolutionFreezePolicy(
            mode=None,  # type: ignore[arg-type]
            operator_override=True,
        )
        assert freeze.is_unfrozen() is True

    def test_no_authority_override_false_frozen(self):
        freeze = LearningEvolutionFreezePolicy(
            mode=None,  # type: ignore[arg-type]
            operator_override=False,
        )
        assert freeze.is_frozen() is True
