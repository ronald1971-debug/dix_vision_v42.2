"""
Execution Unified Core Paper Trading Ledger Integration - Ledger Integration
Provides ledger integration for paper trading
NO LAZY LOADING - All components load directly
"""

from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class LedgerIntegration:
    """Ledger integration for paper trading"""
    
    def __init__(self):
        self._ledger_entries = []
        
    def record_transaction(self, transaction_data: Dict[str, Any]) -> str:
        """Record transaction in ledger"""
        transaction_id = f"txn_{len(self._ledger_entries)}"
        self._ledger_entries.append({"id": transaction_id, **transaction_data})
        return transaction_id
    
    def get_ledger(self) -> List[Dict[str, Any]]:
        """Get ledger entries"""
        return self._ledger_entries.copy()

__all__ = ['LedgerIntegration']