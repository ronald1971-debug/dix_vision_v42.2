"""Cognitive Maturity Model - measures understanding levels.

Most important missing piece.

Today maturity measured by PnL.

Future maturity measures:
- Market Understanding
- Trader Understanding
- Strategy Understanding
- Execution Understanding
- System Understanding
- Self Understanding

Each with explicit levels (1-10).
"""

from cognitive_engine.maturity_model.levels import DomainMaturity, MaturityDomain, MaturityLevel
from cognitive_engine.maturity_model.model import CognitiveMaturityModel
from cognitive_engine.maturity_model.report import MaturityReport

__all__ = [
    "CognitiveMaturityModel",
    "DomainMaturity",
    "MaturityDomain",
    "MaturityLevel",
    "MaturityReport",
]