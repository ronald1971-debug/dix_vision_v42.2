"""
Execution Unified Core Adapters - Adapter Error Classes
Provides adapter error handling
NO LAZY LOADING - All components load directly
"""

from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class NonRecoverableError(Exception):
    """Non-recoverable error for adapter operations"""

    def __init__(self, message: str, error_code: Optional[str] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code

    def __str__(self) -> str:
        code_str = f" (code {self.error_code})" if self.error_code else ""
        return f"NonRecoverableError: {self.message}{code_str}"

class RecoverableExceptionPredicate:
    """Predicate to determine if an exception is recoverable"""

    def __init__(self, recoverable_error_types: List[type] = None):
        self._recoverable_types = recoverable_error_types or []

    def is_recoverable(self, exception: Exception) -> bool:
        """Check if exception is recoverable"""
        return any(isinstance(exception, t) for t in self._recoverable_types) or \
               isinstance(exception, (ConnectionError, TimeoutError))

@dataclass
class RetryAttempt:
    """Data structure for retry attempts"""
    attempt_number: int
    exception: Optional[Exception] = None
    will_retry: bool = True

class RetryOutcome(Enum):
    """Outcome of a retry attempt"""
    SUCCESS = "success"
    EXHAUSTED = "exhausted"
    NON_RECOVERABLE = "non_recoverable"

@dataclass
class RetryRecord:
    """Record of a retry operation"""
    attempts: List[RetryAttempt] = field(default_factory=list)
    final_outcome: RetryOutcome = RetryOutcome.EXHAUSTED
    total_delay_seconds: float = 0.0

def default_is_recoverable(exception: Exception) -> bool:
    """Default predicate for recoverable exceptions"""
    return isinstance(exception, (ConnectionError, TimeoutError))

__all__ = ['NonRecoverableError', 'RecoverableExceptionPredicate', 'RetryAttempt',
           'RetryOutcome', 'RetryRecord', 'default_is_recoverable']