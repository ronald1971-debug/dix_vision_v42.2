"""Top-level pytest fixtures.

Hardening-S1 item 1 — the harness approval shim
(``governance_engine.harness_approver``) is opt-in only. Production
processes must explicitly set
:data:`governance_engine.harness_approver.HARNESS_APPROVER_ENV_VAR`
to a truthy value before any caller may invoke
:func:`approve_signal_for_execution`. The pytest session is, by
definition, harness territory: replay tests, plugin tests, and the
dashboard backend smoke tests all construct synthetic intents through
the shim. Setting the env var here at session start is the single
canonical opt-in for the whole tree.
"""

from __future__ import annotations

import os

os.environ.setdefault("DIX_HARNESS_APPROVER_ENABLED", "1")
os.environ.setdefault("DIXVISION_PERMIT_EPHEMERAL_LEDGER", "1")
os.environ.setdefault("DIXVISION_BOOT_MODE", "SAFE")
