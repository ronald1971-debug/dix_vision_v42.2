"""Curiosity Engine - generates investigative questions.

Most systems react. Cognitive systems investigate.

Example questions:
- Why is Trader #381 suddenly outperforming?
- Why is this strategy working now?
- Why did volatility structure change?
"""

from cognitive_engine.curiosity_engine.curiosity_scorer import CuriosityScore, CuriosityScorer
from cognitive_engine.curiosity_engine.investigation import Investigation, InvestigationManager
from cognitive_engine.curiosity_engine.question_generator import Question, QuestionGenerator

__all__ = [
    "CuriosityScorer",
    "CuriosityScore",
    "Investigation",
    "InvestigationManager",
    "Question",
    "QuestionGenerator",
]