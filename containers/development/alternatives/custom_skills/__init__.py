"""
DIX VISION Custom Skills

Custom skills for DIX VISION Desktop AgentOS including:
- Research Coin: Cryptocurrency research
- Analyze Wallet: Wallet behavior analysis
- Analyze Repository: Code repository analysis
"""

from .analyze_repository import AnalyzeRepositorySkill
from .analyze_wallet import AnalyzeWalletSkill
from .research_coin import ResearchCoinSkill

__all__ = [
    "ResearchCoinSkill",
    "AnalyzeWalletSkill",
    "AnalyzeRepositorySkill",
]
