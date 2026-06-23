"""
Execution Unified Algos Archive - Trading Algorithm Components
Provides production-ready trading algorithms and execution strategies
NO LAZY LOADING - All components load directly
"""

import logging

logger = logging.getLogger(__name__)

__all__ = [
    "almgren_chriss",
    "adversarial_executor",
    "optimal_execution",
    "depth_estimator",
    "model",
    "slippage_curve",
]
