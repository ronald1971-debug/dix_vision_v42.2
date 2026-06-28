"""
Core Contracts News
Real implementation for news data contracts
"""

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class NewsKind(Enum):
    """News kind enumeration"""

    MARKET = "market"
    ECONOMIC = "economic"
    COMPANY = "company"
    REGULATORY = "regulatory"
    GEOPOLITICAL = "geopolitical"
    TECHNOLOGY = "technology"
    WEATHER = "weather"
    OTHER = "other"


class NewsSentiment(Enum):
    """News sentiment enumeration"""

    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    MIXED = "mixed"
    UNKNOWN = "unknown"


class NewsSource(Enum):
    """News source enumeration"""

    REUTERS = "reuters"
    BLOOMBERG = "bloomberg"
    AP = "ap"
    AFP = "afp"
    XINHUA = "xinhua"
    INTERNAL = "internal"
    CUSTOM = "custom"
    UNKNOWN = "unknown"


@dataclass
class NewsItem:
    """News item information"""

    item_id: str
    title: str
    content: str
    news_kind: NewsKind
    source: NewsSource
    sentiment: NewsSentiment
    timestamp: float = field(default_factory=time.time)
    symbols: List[str] = field(default_factory=list)
    relevance_score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def is_positive(self) -> bool:
        """Check if sentiment is positive"""
        return self.sentiment == NewsSentiment.POSITIVE

    def is_negative(self) -> bool:
        """Check if sentiment is negative"""
        return self.sentiment == NewsSentiment.NEGATIVE

    def is_relevant(self, threshold: float = 0.5) -> bool:
        """Check if news is relevant based on score"""
        return self.relevance_score >= threshold

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "item_id": self.item_id,
            "title": self.title,
            "content": self.content,
            "news_kind": self.news_kind.value,
            "source": self.source.value,
            "sentiment": self.sentiment.value,
            "timestamp": self.timestamp,
            "symbols": self.symbols,
            "relevance_score": self.relevance_score,
            "metadata": self.metadata,
        }


class NewsFilter:
    """Filter for news items"""

    def __init__(self):
        self.allowed_kinds: List[NewsKind] = []
        self.allowed_sources: List[NewsSource] = []
        self.min_relevance: float = 0.0
        self.max_age_seconds: float = 86400.0  # 24 hours default

    def add_kind(self, kind: NewsKind) -> None:
        """Add a kind to the allowed kinds"""
        if kind not in self.allowed_kinds:
            self.allowed_kinds.append(kind)

    def add_source(self, source: NewsSource) -> None:
        """Add a source to the allowed sources"""
        if source not in self.allowed_sources:
            self.allowed_sources.append(source)

    def matches(self, item: NewsItem) -> bool:
        """Check if a news item matches the filter"""
        current_time = time.time()

        # Check age
        if item.timestamp < current_time - self.max_age_seconds:
            return False

        # Check kind
        if self.allowed_kinds and item.news_kind not in self.allowed_kinds:
            return False

        # Check source
        if self.allowed_sources and item.source not in self.allowed_sources:
            return False

        # Check relevance
        if item.relevance_score < self.min_relevance:
            return False

        return True


class NewsFeed:
    """Feed of news items"""

    def __init__(self):
        self._items: Dict[str, NewsItem] = {}
        self._items_by_kind: Dict[NewsKind, List[str]] = {kind: [] for kind in NewsKind}
        self._max_items = 1000

    def add_item(self, item: NewsItem) -> bool:
        """Add a news item to the feed"""
        if len(self._items) >= self._max_items:
            return False

        self._items[item.item_id] = item
        self._items_by_kind[item.news_kind].append(item.item_id)
        return True

    def get_item(self, item_id: str) -> Optional[NewsItem]:
        """Get a specific news item"""
        return self._items.get(item_id)

    def get_items_by_kind(self, kind: NewsKind) -> List[NewsItem]:
        """Get all items of a specific kind"""
        item_ids = self._items_by_kind.get(kind, [])
        return [self._items[iid] for iid in item_ids if iid in self._items]

    def get_recent_items(self, limit: int = 10) -> List[NewsItem]:
        """Get the most recent items"""
        sorted_items = sorted(self._items.values(), key=lambda x: x.timestamp, reverse=True)
        return sorted_items[:limit]

    def filter_items(self, filter: NewsFilter) -> List[NewsItem]:
        """Filter items based on a filter"""
        return [item for item in self._items.values() if filter.matches(item)]

    def remove_item(self, item_id: str) -> bool:
        """Remove a news item"""
        item = self._items.get(item_id)
        if item:
            del self._items[item_id]
            if item_id in self._items_by_kind[item.news_kind]:
                self._items_by_kind[item.news_kind].remove(item_id)
            return True
        return False


# Global news feed
_news_feed: Optional[NewsFeed] = None


def get_news_feed() -> NewsFeed:
    """Get the global news feed"""
    global _news_feed
    if _news_feed is None:
        _news_feed = NewsFeed()
    return _news_feed


def create_news_item(
    item_id: str,
    title: str,
    content: str,
    news_kind: NewsKind,
    source: NewsSource,
    sentiment: NewsSentiment,
) -> NewsItem:
    """Create a new news item"""
    return NewsItem(
        item_id=item_id,
        title=title,
        content=content,
        news_kind=news_kind,
        source=source,
        sentiment=sentiment,
    )


__all__ = [
    "NewsKind",
    "NewsSentiment",
    "NewsSource",
    "NewsItem",
    "NewsFilter",
    "NewsFeed",
    "get_news_feed",
    "create_news_item",
]
