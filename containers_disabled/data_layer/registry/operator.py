"""registry.operator — Default operator authority configuration.

This module provides the DEFAULT_AUTHORITY constant used as the baseline
operator authority configuration when the system boots.
"""

from core.contracts.operator_authority import (
    LearningAuthority,
    LiveExecutionAuthority,
    OperatorAuthority,
    PracticeAuthority,
    TradingDomain,
    TradingMode,
)

DEFAULT_AUTHORITY = OperatorAuthority(
    learning=LearningAuthority.FULL,
    practice=PracticeAuthority.ON,
    live_execution=LiveExecutionAuthority.BLOCKED,
    trading_mode={
        TradingDomain.NORMAL: TradingMode.MANUAL,
        TradingDomain.COPY_TRADING: TradingMode.MANUAL,
        TradingDomain.MEMECOIN: TradingMode.MANUAL,
    },
    operator_id="ronald",
    granted_ts_ns=0,
    notes="Default safe configuration",
)
