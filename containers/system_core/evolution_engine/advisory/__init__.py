"""evolution_engine.advisory — DYON's system engineering advisory capabilities.

DYON now has advisory capabilities to recommend:
- Architecture improvements
- Performance optimizations
- Security enhancements
- Scalability solutions
- Observability upgrades
- DevOps practices
- Database optimizations
- Distributed system patterns

This makes DYON a true System Engineer with advisory capabilities.
"""

from evolution_engine.advisory.dyon_suggestor import (
    AdvisoryCategory,
    AdvisoryPattern,
    AdvisoryPriority,
    AdvisoryRecommendation,
    DYONSuggestor,
    get_dyon_suggestor,
)

__all__ = [
    "AdvisoryCategory",
    "AdvisoryPattern",
    "AdvisoryPriority",
    "AdvisoryRecommendation",
    "DYONSuggestor",
    "get_dyon_suggestor",
]
