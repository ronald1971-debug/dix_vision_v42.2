"""
enforcement/policy_enforcer.py
Canonical attribute-level policy enforcement surface (P1 consolidation).

This module is the SINGLE enforcement entry point. It owns the deny-rule
registry and delegates evaluation to ``governance.policy_engine`` so all
policy decisions flow through one authority surface.

``governance/policy_engine.py`` is the canonical rule owner; this module
wraps it for attribute-level (call-site) enforcement.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from governance.policy_engine import get_policy_engine as _get_canonical_engine
from system.fast_risk_cache import get_risk_cache


@dataclass(frozen=True)
class EnforceResult:
    allowed: bool
    reason: str
    reasons: tuple[str, ...] = ()


class PolicyEnforcer:
    def __init__(self) -> None:
        self._engine = _get_canonical_engine()

    def allow(self, ctx: dict[str, Any]) -> EnforceResult:
        rc = get_risk_cache().get()
        if not rc.trading_allowed:
            return EnforceResult(False, "trading_disallowed")
        size_usd = float(ctx.get("size_usd", 0.0))
        portfolio_usd = float(ctx.get("portfolio_usd", 100_000.0))
        ok, reason = rc.allows_trade(size_usd=size_usd, portfolio_usd=portfolio_usd)
        if not ok:
            return EnforceResult(False, reason)
        result = self._engine.evaluate(ctx)
        if not result.allowed:
            return EnforceResult(False, result.reasons[-1] if result.reasons else "policy_denied", tuple(result.reasons))
        return EnforceResult(True, "ok")

    def enforce(self, fn: Callable[..., Any], ctx: dict[str, Any]) -> Any:
        verdict = self.allow(ctx)
        if not verdict.allowed:
            raise PermissionError(f"policy_denied: {verdict.reason}")
        return fn()


_pe: PolicyEnforcer | None = None


def get_policy_enforcer() -> PolicyEnforcer:
    global _pe
    if _pe is None:
        _pe = PolicyEnforcer()
    return _pe


__all__ = ["EnforceResult", "PolicyEnforcer", "get_policy_enforcer"]
