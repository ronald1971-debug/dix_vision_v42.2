"""
State Deterministic Verifier - Deterministic Verification Module
Provides deterministic verification capabilities for state operations
NO LAZY LOADING - All components load directly
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class DeterminismStatus(Enum):
    """Determinism status enumeration"""
    DETERMINISTIC = "deterministic"
    NON_DETERMINISTIC = "non_deterministic"
    UNKNOWN = "unknown"
    ERROR = "error"

@dataclass
class DeterminismCheckResult:
    """Result of determinism check"""
    status: DeterminismStatus
    confidence: float
    details: Dict[str, Any] = None
    timestamp_ns: int = 0
    
    def __post_init__(self):
        if self.details is None:
            self.details = {}
        if self.timestamp_ns == 0:
            self.timestamp_ns = int(__import__('datetime').datetime.now().timestamp() * 1_000_000_000)

class DeterministicVerifier:
    """Base deterministic verifier for state operations"""
    
    def __init__(self):
        self._verification_history = []
        self._determinism_rules = {}
        
    def add_determinism_rule(self, rule_id: str, rule_function):
        """Add determinism verification rule"""
        self._determinism_rules[rule_id] = rule_function
        
    def verify_determinism(self, operation_data: Dict[str, Any]) -> DeterminismCheckResult:
        """Verify determinism of an operation"""
        # Apply all determinism rules
        rule_results = []
        for rule_id, rule_function in self._determinism_rules.items():
            try:
                result = rule_function(operation_data)
                rule_results.append(result)
            except Exception as e:
                logger.warning(f"Rule {rule_id} failed: {e}")
                rule_results.append(False)
        
        # Determine overall status
        if all(rule_results):
            status = DeterminismStatus.DETERMINISTIC
            confidence = 1.0
        elif any(rule_results):
            status = DeterminismStatus.NON_DETERMINISTIC
            confidence = sum(rule_results) / len(rule_results)
        else:
            status = DeterminismStatus.UNKNOWN
            confidence = 0.0
        
        result = DeterminismCheckResult(
            status=status,
            confidence=confidence,
            details={"rule_results": rule_results}
        )
        
        self._verification_history.append(result)
        return result
    
    def get_verification_history(self) -> List[DeterminismCheckResult]:
        """Get verification history"""
        return self._verification_history

# Global instance
_deterministic_verifier = None

def get_deterministic_verifier() -> DeterministicVerifier:
    """Get deterministic verifier instance"""
    global _deterministic_verifier
    if _deterministic_verifier is None:
        _deterministic_verifier = DeterministicVerifier()
    return _deterministic_verifier

# Alias for compatibility with state/__init__.py
DeterminismReport = DeterminismCheckResult

__all__ = ['DeterminismStatus', 'DeterminismCheckResult', 'DeterminismReport', 'DeterministicVerifier', 'get_deterministic_verifier']