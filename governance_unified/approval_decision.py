"""
Governance Unified Approval Decision - Approval Decision Support
Provides approval decision capabilities for governance operations
NO LAZY LOADING - All components load directly
"""

from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class ApprovalDecision:
    """Approval decision for governance operations"""
    
    def __init__(self, approved: bool, reason: str = ""):
        self.approved = approved
        self.reason = reason
        self.timestamp = __import__('datetime').datetime.now().timestamp_ns()

__all__ = ['ApprovalDecision']