"""
mind/sources/news_streams.py
Registry of structured news feeds. Each registered source returns a list of
(headline, polarity, confidence) tuples — never raw text.
"""

from __future__ import annotations

import threading
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any


@dataclass
class NewsItem:
    source: str
    headline: str
    polarity: float = 0.0
    confidence: float = 0.0
    timestamp_utc: str = ""
    narratives: list[Any] = None  # Cognitive narrative detection

    def __post_init__(self):
        if self.narratives is None:
            self.narratives = []


NewsFn = Callable[[], list[NewsItem]]


class NewsStreamRegistry:
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._sources: dict[str, NewsFn] = {}
        self._narrative_engine = None
        
        # Initialize cognitive integration
        self._init_cognitive_integration()

    def _init_cognitive_integration(self) -> None:
        """Initialize cognitive narrative engine integration."""
        try:
            from cognitive_engine.cognitive_orchestrator import get_cognitive_orchestrator
            from system.feature_flags import CognitiveFeatureFlags, FeatureFlagManager
            
            if FeatureFlagManager.is_enabled(CognitiveFeatureFlags.NARRATIVE_DETECTION):
                self._narrative_engine = get_cognitive_orchestrator()
        except Exception:
            # Narrative detection optional - fail gracefully
            pass

    def register(self, name: str, fn: NewsFn) -> None:
        with self._lock:
            self._sources[name] = fn

    def pull_all(self) -> list[NewsItem]:
        out: list[NewsItem] = []
        with self._lock:
            srcs = list(self._sources.items())
        for _, fn in srcs:
            try:
                items = fn()
                # Apply narrative detection if enabled
                if self._narrative_engine:
                    items = self._apply_narrative_detection(items)
                out.extend(items)
            except Exception:
                continue
        return out

    def _apply_narrative_detection(self, items: list[NewsItem]) -> list[NewsItem]:
        """Apply cognitive narrative detection to news items."""
        enriched_items = []
        
        for item in items:
            try:
                # Convert news item to narrative data format
                narrative_data = {
                    "headline": item.headline,
                    "sentiment": item.polarity,
                    "source": item.source,
                    "timestamp": item.timestamp_utc
                }
                
                # Detect narratives using cognitive engine
                narratives = self._detect_narratives(narrative_data)
                
                # Create enriched news item
                enriched_item = NewsItem(
                    source=item.source,
                    headline=item.headline,
                    polarity=item.polarity,
                    confidence=item.confidence,
                    timestamp_utc=item.timestamp_utc,
                    narratives=narratives
                )
                
                enriched_items.append(enriched_item)
                
            except Exception:
                # If narrative detection fails, return original item
                enriched_items.append(item)
        
        return enriched_items

    def _detect_narratives(self, news_data: dict[str, Any]) -> list[Any]:
        """Detect narratives from news data using cognitive engine."""
        if not self._narrative_engine:
            return []
        
        try:
            # Get cognitive enrichment
            enrichment = self._narrative_engine.enrich_market_data({
                "news_item": news_data,
                "source": "news_stream"
            })
            
            return enrichment.narratives or []
            
        except Exception:
            return []


_registry: NewsStreamRegistry | None = None
_lock = threading.Lock()


def get_news_streams() -> NewsStreamRegistry:
    global _registry
    if _registry is None:
        with _lock:
            if _registry is None:
                _registry = NewsStreamRegistry()
    return _registry
