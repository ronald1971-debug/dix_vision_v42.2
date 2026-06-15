
"""Local cache adapter for dockerless caching."""

import json
import time
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class LocalCacheAdapter:
    """Local file-based cache adapter."""

    def __init__(self, cache_path: str):
        self.cache_path = cache_path
        self._cache = self._load_cache()

    def _load_cache(self) -> Dict:
        """Load cache from file."""
        try:
            with open(self.cache_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"cache": {}, "config": {}, "monitoring": {}}

    def _save_cache(self):
        """Save cache to file."""
        with open(self.cache_path, 'w') as f:
            json.dump(self._cache, f, indent=2)

    def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache."""
        return self._cache.get(key, default)

    def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        """Set value in cache with TTL."""
        self._cache[key] = {
            "value": value,
            "expiry": time.time() + ttl
        }
        self._save_cache()
        return True

    def delete(self, key: str) -> bool:
        """Delete value from cache."""
        if key in self._cache:
            del self._cache[key]
            self._save_cache()
            return True
        return False

    def clear(self) -> bool:
        """Clear all cache entries."""
        self._cache = {"cache": {}, "config": {}, "monitoring": {}}
        self._save_cache()
        return True
