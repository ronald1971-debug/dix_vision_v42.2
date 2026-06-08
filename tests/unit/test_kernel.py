"""Tests for core kernel – BeliefState and primitives."""

from core.mcos_kernel import (
    BeliefState,
    ConfidenceLevel,
    MarketRegime,
    MarketView,
    SystemPhase,
)


def test_belief_state_defaults():
    bs = BeliefState()
    assert bs.phase == SystemPhase.INITIALIZING
    assert bs.market_view.regime == MarketRegime.UNKNOWN
    assert bs.kill_switch_active is False
    assert not bs.is_halted()


def test_belief_state_snapshot():
    bs = BeliefState()
    snap = bs.snapshot()
    assert snap.state_id != bs.state_id
    assert snap.phase == bs.phase


def test_belief_state_with_market_view():
    bs = BeliefState()
    view = MarketView(regime=MarketRegime.TRENDING_UP, confidence=ConfidenceLevel.HIGH)
    updated = bs.with_market_view(view)
    assert updated.market_view.regime == MarketRegime.TRENDING_UP
    assert bs.market_view.regime == MarketRegime.UNKNOWN  # original unchanged


def test_kill_switch():
    bs = BeliefState()
    halted = bs.activate_kill_switch()
    assert halted.kill_switch_active is True
    assert halted.is_halted()
    assert halted.phase == SystemPhase.HALTED


def test_with_phase():
    bs = BeliefState()
    obs = bs.with_phase(SystemPhase.OBSERVING)
    assert obs.phase == SystemPhase.OBSERVING
