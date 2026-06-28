"""
Execution Unified Core Adapters Retry Mixin
Provides retry functionality for adapters
NO LAZY LOADING - All components load directly
"""

import logging
import time
from typing import Optional

logger = logging.getLogger(__name__)


class RetryMixin:
    """Retry mixin for adapter operations"""

    def __init__(self):
        self._max_retries = 3
        self._retry_delay = 1.0

    def with_retry(self, func, *args, max_retries: Optional[int] = None, **kwargs):
        """Execute function with retry logic"""
        max_retries = max_retries or self._max_retries
        last_error = None

        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_error = e
                if attempt < max_retries - 1:
                    time.sleep(self._retry_delay)
                logger.warning(f"Retry attempt {attempt + 1}/{max_retries} failed: {e}")

        raise last_error

    def set_max_retries(self, max_retries: int):
        """Set maximum retry attempts"""
        self._max_retries = max_retries

    def set_retry_delay(self, delay: float):
        """Set retry delay in seconds"""
        self._retry_delay = delay


__all__ = ["RetryMixin"]
