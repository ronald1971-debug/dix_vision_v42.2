"""
Core Contracts External Signal Trust
Real implementation for external signal trust registry
"""

from typing import Dict


class ExternalSignalTrustRegistry:
    """Registry for external signal trust levels"""

    def __init__(self):
        self._signals: Dict[str, float] = {}
        self._default_trust = 0.5

    def register_signal(self, signal_id: str, trust_level: float) -> None:
        """Register a signal with its trust level"""
        self._signals[signal_id] = max(0.0, min(1.0, trust_level))

    def get_trust(self, signal_id: str) -> float:
        """Get the trust level for a signal"""
        return self._signals.get(signal_id, self._default_trust)

    def set_default_trust(self, level: float) -> None:
        """Set the default trust level"""
        self._default_trust = max(0.0, min(1.0, level))

    def list_signals(self) -> list:
        """List all registered signals"""
        return list(self._signals.keys())


def load_external_signal_trust(path=None) -> ExternalSignalTrustRegistry:
    """Load and return the external signal trust registry"""
    # Path argument accepted for compatibility but not used in current implementation
    return ExternalSignalTrustRegistry()


__all__ = ["ExternalSignalTrustRegistry", "load_external_signal_trust"]
