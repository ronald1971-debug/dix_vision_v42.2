"""registry.operator — loads default OperatorAuthority from YAML."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from core.contracts.operator_authority import (
    LearningAuthority,
    LiveExecutionAuthority,
    OperatorAuthority,
    PracticeAuthority,
    SemiAutoPolicy,
    TradingDomain,
    TradingMode,
)

_DEFAULT_PATH = Path(__file__).resolve().parent / "operator.yaml"


def _dict_to_semi_auto_policy(d: dict[str, Any]) -> SemiAutoPolicy:
    return SemiAutoPolicy(
        entry_requires_approval=bool(d.get("entry_requires_approval", True)),
        exit_auto=bool(d.get("exit_auto", True)),
        risk_reduce_auto=bool(d.get("risk_reduce_auto", True)),
        notional_threshold_usd=float(d.get("notional_threshold_usd", 5000.0)),
        position_fraction_cap=float(d.get("position_fraction_cap", 0.05)),
        volatility_cap_zscore=float(d.get("volatility_cap_zscore", 3.0)),
    )


def _dict_to_operator_authority(d: dict[str, Any]) -> OperatorAuthority:
    raw_learning = d.get("learning", "FULL")
    raw_practice = d.get("practice", "ON")
    raw_live = d.get("live_execution", "BLOCKED")
    try:
        learning = LearningAuthority(raw_learning)
    except ValueError:
        learning = LearningAuthority.FULL
    try:
        practice = PracticeAuthority(raw_practice)
    except ValueError:
        practice = PracticeAuthority.ON
    try:
        live = LiveExecutionAuthority(raw_live)
    except ValueError:
        live = LiveExecutionAuthority.BLOCKED
    raw_tm = d.get("trading_mode", {})
    trading_mode: dict[TradingDomain, TradingMode] = {}
    for domain_str, mode_str in raw_tm.items():
        try:
            domain = TradingDomain(domain_str)
            mode = TradingMode(mode_str)
            trading_mode[domain] = mode
        except ValueError:
            pass
    raw_policy = d.get("semi_auto_policy", {})
    semi_auto_policy: dict[TradingDomain, SemiAutoPolicy] = {}
    for domain_str, policy_dict in raw_policy.items():
        try:
            domain = TradingDomain(domain_str)
            semi_auto_policy[domain] = _dict_to_semi_auto_policy(policy_dict)
        except ValueError:
            pass
    return OperatorAuthority(
        learning=learning,
        practice=practice,
        live_execution=live,
        trading_mode=trading_mode,
        semi_auto_policy=semi_auto_policy,
        operator_id=d.get("operator_id", "ronald"),
        granted_ts_ns=int(d.get("granted_ts_ns", 0)),
        notes=d.get("notes", ""),
    )


def load_default_authority(path: Path | None = None) -> OperatorAuthority:
    """Load default OperatorAuthority from YAML registry."""
    p = path or _DEFAULT_PATH
    try:
        raw = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
        return _dict_to_operator_authority(raw.get("operator_authority", {}))
    except FileNotFoundError:
        return OperatorAuthority()


DEFAULT_AUTHORITY: OperatorAuthority = load_default_authority()
