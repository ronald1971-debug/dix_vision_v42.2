"""
Execution Unified Core Package
Core execution infrastructure for the unified system
NO LAZY LOADING - All components load directly
"""

from execution_unified.core.engine import (
    ExecutionMode,
    OrderPriority,
    OrderRouting,
    ExecutionConfig,
    ExecutionMetrics,
    ExecutionEngine,
    get_execution_engine
)

__all__ = [
    'ExecutionMode',
    'OrderPriority',
    'OrderRouting',
    'ExecutionConfig',
    'ExecutionMetrics',
    'ExecutionEngine',
    'get_execution_engine'
]