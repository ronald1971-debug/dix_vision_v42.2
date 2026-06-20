"""
Core Contracts Source Trust Promotions
Real implementation for source trust promotion store
"""

from typing import Dict, Optional

class SourceTrustPromotionStore:
    """Store for source trust promotions"""
    
    def __init__(self):
        self._promotions: Dict[str, str] = {}
    
    def add_promotion(self, source: str, promotion: str) -> None:
        """Add a promotion for a source"""
        self._promotions[source] = promotion
    
    def get_promotion(self, source: str) -> Optional[str]:
        """Get the promotion for a source"""
        return self._promotions.get(source)
    
    def list_sources(self) -> list:
        """List all sources with promotions"""
        return list(self._promotions.keys())
    
    def remove_promotion(self, source: str) -> bool:
        """Remove a promotion for a source"""
        if source in self._promotions:
            del self._promotions[source]
            return True
        return False

__all__ = ["SourceTrustPromotionStore"]