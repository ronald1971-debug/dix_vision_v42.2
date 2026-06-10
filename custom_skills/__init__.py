"""
DIX VISION Custom Skills

Custom skills for DIX VISION Desktop AgentOS including:
- Research Coin: Cryptocurrency research
- Analyze Wallet: Wallet behavior analysis  
- Analyze Repository: Code repository analysis
"""

from .research_coin import ResearchCoinSkill
from .analyze_wallet import AnalyzeWalletSkill
from .analyze_repository import AnalyzeRepositorySkill

__all__ = [
    "ResearchCoinSkill",
    "AnalyzeWalletSkill",
    "AnalyzeRepositorySkill",
]
