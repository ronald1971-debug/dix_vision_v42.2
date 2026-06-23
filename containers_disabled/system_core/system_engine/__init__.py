"""RUNTIME-ENGINE-03 System (Phase E0 shell).

Dyon domain. Hazard sensors, health monitors, state plugins. Emits
``HAZARD_EVENT`` and ``SYSTEM_EVENT``. Subject to lint rules B1 and L3.

Canonical System Engine - System Infrastructure Only

This is the canonical system_engine that contains ONLY system infrastructure
components as specified in the DIX VISION architectural vision.

System Architecture (Canonical):
- INDIRA: Market cognition (separate domain: indira_cognitive/)
- DYON: System cognition (separate domain: dyon_cognitive/)
- GOVERNANCE: Control authority (separate domain: governance_unified/)
- EXECUTION: Market interaction (separate domain: execution_unified/)
- LEARNING: Experience transformation (separate domain: learning_engine/)
- EVOLUTION: System adaptation (separate domain: evolution_engine/)
- SYSTEM_ENGINE: System infrastructure (this directory)
"""

from system_engine.engine import SystemEngine

__all__ = ["SystemEngine"]
