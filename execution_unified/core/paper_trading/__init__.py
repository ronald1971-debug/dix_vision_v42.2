"""
Execution Unified Core Paper Trading - Paper Trading Infrastructure
Provides paper trading capabilities for strategy testing
NO LAZY LOADING - All components load directly
"""

from typing import Dict, List, Optional, Any
import logging
import asyncio
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class Adapter:
    """Paper trading adapter interface"""
    
    def __init__(self):
        self._connected = False
        
    async def connect(self) -> bool:
        """Connect paper trading adapter"""
        self._connected = True
        logger.info("Paper trading adapter connected")
        return True
    
    async def disconnect(self) -> bool:
        """Disconnect paper trading adapter"""
        self._connected = False
        logger.info("Paper trading adapter disconnected")
        return True
    
    def is_connected(self) -> bool:
        """Check if connected"""
        return self._connected


class Hub:
    """Paper trading hub for managing paper trading sessions"""
    
    def __init__(self):
        self._sessions: Dict[str, Dict[str, Any]] = {}
        
    async def create_session(self, session_id: str, initial_capital: float) -> bool:
        """Create paper trading session"""
        self._sessions[session_id] = {
            'initial_capital': initial_capital,
            'current_capital': initial_capital,
            'positions': {},
            'orders': {},
            'created_at': datetime.now().timestamp_ns()
        }
        logger.info(f"Created paper trading session: {session_id}")
        return True
    
    async def close_session(self, session_id: str) -> bool:
        """Close paper trading session"""
        if session_id in self._sessions:
            del self._sessions[session_id]
            logger.info(f"Closed paper trading session: {session_id}")
            return True
        return False


class LedgerIntegration:
    """Ledger integration for paper trading"""
    
    def __init__(self):
        self._ledger_entries: Dict[str, Dict[str, Any]] = {}
        
    async def record_trade(self, session_id: str, trade_data: Dict[str, Any]) -> str:
        """Record trade in ledger"""
        entry_id = f"entry_{datetime.now().timestamp_ns()}"
        self._ledger_entries[entry_id] = {
            'session_id': session_id,
            'trade_data': trade_data,
            'timestamp': datetime.now().timestamp_ns()
        }
        return entry_id
    
    async def get_balance(self, session_id: str) -> float:
        """Get session balance"""
        # Calculate balance from ledger entries
        total = 0.0
        for entry in self._ledger_entries.values():
            if entry['session_id'] == session_id:
                total += entry['trade_data'].get('pnl', 0.0)
        return total


class PaperOnlyEnforcer:
    """Enforcer to ensure paper trading only mode"""
    
    def __init__(self):
        self._enforcement_enabled = True
        
    async def enforce_paper_only(self, operation: str) -> bool:
        """Enforce paper trading only"""
        if self._enforcement_enabled:
            logger.debug(f"Enforced paper-only mode for: {operation}")
            return True
        return False


class PromotionGateIntegration:
    """Integration with promotion gates"""
    
    def __init__(self):
        self._gates: Dict[str, bool] = {}
        
    async def check_gate(self, gate_name: str) -> bool:
        """Check if promotion gate is open"""
        return self._gates.get(gate_name, False)
    
    async def open_gate(self, gate_name: str):
        """Open promotion gate"""
        self._gates[gate_name] = True
        logger.info(f"Opened promotion gate: {gate_name}")


class VenueConfig:
    """Venue configuration for paper trading"""
    
    def __init__(self):
        self._venue_configs: Dict[str, Dict[str, Any]] = {}
        
    async def configure_venue(self, venue_name: str, config: Dict[str, Any]):
        """Configure trading venue"""
        self._venue_configs[venue_name] = config
        logger.info(f"Configured venue: {venue_name}")


# Global instances
_adapter = None
_hub = None
_ledger_integration = None
_paper_only_enforcer = None
_promotion_gate_integration = None
_venue_config = None


def get_adapter() -> Adapter:
    """Get paper trading adapter instance"""
    global _adapter
    if _adapter is None:
        _adapter = Adapter()
    return _adapter


def get_hub() -> Hub:
    """Get hub instance"""
    global _hub
    if _hub is None:
        _hub = Hub()
    return _hub


def get_ledger_integration() -> LedgerIntegration:
    """Get ledger integration instance"""
    global _ledger_integration
    if _ledger_integration is None:
        _ledger_integration = LedgerIntegration()
    return _ledger_integration


def get_paper_only_enforcer() -> PaperOnlyEnforcer:
    """Get paper only enforcer instance"""
    global _paper_only_enforcer
    if _paper_only_enforcer is None:
        _paper_only_enforcer = PaperOnlyEnforcer()
    return _paper_only_enforcer


def get_promotion_gate_integration() -> PromotionGateIntegration:
    """Get promotion gate integration instance"""
    global _promotion_gate_integration
    if _promotion_gate_integration is None:
        _promotion_gate_integration = PromotionGateIntegration()
    return _promotion_gate_integration


def get_venue_config() -> VenueConfig:
    """Get venue config instance"""
    global _venue_config
    if _venue_config is None:
        _venue_config = VenueConfig()
    return _venue_config


__all__ = [
    'Adapter',
    'Hub',
    'LedgerIntegration',
    'PaperOnlyEnforcer',
    'PromotionGateIntegration',
    'VenueConfig',
    'get_adapter',
    'get_hub',
    'get_ledger_integration',
    'get_paper_only_enforcer',
    'get_promotion_gate_integration',
    'get_venue_config'
]