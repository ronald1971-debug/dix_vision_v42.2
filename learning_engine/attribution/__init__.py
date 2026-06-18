"""Attribution Engine — "Why did we win/lose?"

PnL decomposition, decision attribution, mistake classifier, and
edge decay tracker. Answers the most important question in trading:
what actually caused each outcome?

Components:
- PnLDecomposer: breaks down PnL into alpha, beta, execution, timing
- DecisionAttributor: links outcomes to specific decisions/signals
- MistakeClassifier: categorizes errors for learning
- EdgeDecayTracker: detects when an edge is dying
"""

from learning_engine.attribution.decision_attributor import (
    Attribution,
    DecisionAttributor,
)
from learning_engine.attribution.edge_decay_tracker import EdgeDecayTracker, EdgeHealth
from learning_engine.attribution.mistake_classifier import (
    MistakeCategory,
    MistakeClassifier,
)
from learning_engine.attribution.outcome_linker import OutcomeLinker, PatternAttribution
from learning_engine.attribution.pnl_decomposer import PnLComponents, PnLDecomposer

class AttributionEngine:
    """Main attribution engine that combines all attribution components"""
    
    def __init__(self):
        self._decision_attributor = DecisionAttributor()
        self._mistake_classifier = MistakeClassifier()
        self._edge_decay_tracker = EdgeDecayTracker()
        self._outcome_linker = OutcomeLinker()
        self._pnl_decomposer = PnLDecomposer()
    
    def analyze_outcome(self, trade_data: dict) -> dict:
        """Complete attribution analysis of a trade outcome"""
        return {
            "decision_attribution": self._decision_attributor.attribution(trade_data),
            "mistake_classification": self._mistake_classifier.classify(trade_data),
            "edge_health": self._edge_decay_tracker.get_health(trade_data),
            "pattern_attribution": self._outcome_linker.link_to_patterns(trade_data),
            "pnl_decomposition": self._pnl_decomposer.decompose(trade_data)
        }

__all__ = [
    "PnLDecomposer",
    "PnLComponents", 
    "DecisionAttributor",
    "Attribution",
    "MistakeClassifier",
    "MistakeCategory",
    "EdgeDecayTracker",
    "EdgeHealth",
    "OutcomeLinker",
    "PatternAttribution",
    "AttributionEngine"
]
