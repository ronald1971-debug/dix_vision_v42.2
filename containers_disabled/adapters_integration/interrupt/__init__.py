"""
Interrupt - Signal Interrupt Handler
Provides signal interrupt capabilities
NO LAZY LOADING - All components load directly
"""

import logging
import signal
from typing import Callable, Optional

logger = logging.getLogger(__name__)


class InterruptHandler:
    """Signal interrupt handler"""

    def __init__(self):
        self._interrupted = False
        self._callback: Optional[Callable] = None

    def setup_interrupt(self, callback: Optional[Callable] = None):
        """Setup interrupt handler"""
        self._callback = callback

        def handler(signum, frame):
            self._interrupted = True
            logger.info(f"Interrupt signal received: {signum}")
            if self._callback:
                self._callback()

        signal.signal(signal.SIGINT, handler)
        signal.signal(signal.SIGTERM, handler)

    def is_interrupted(self) -> bool:
        """Check if interrupted"""
        return self._interrupted

    def reset(self):
        """Reset interrupt status"""
        self._interrupted = False


__all__ = ["InterruptHandler"]
