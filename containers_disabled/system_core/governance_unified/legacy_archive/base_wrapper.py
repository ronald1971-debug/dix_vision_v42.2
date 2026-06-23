"""
Base Governance Wrapper for External Container Services
All external services must use this wrapper for governance compliance
"""

import logging
import os
from typing import Any, Dict, Optional

import httpx
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class GovernanceDecision(BaseModel):
    approved: bool
    reason: Optional[str] = None
    conditions: Optional[Dict[str, Any]] = None


class BaseContainerGovernanceWrapper:
    """Base wrapper for all external container services

    Ensures governance compliance for all operations
    """

    def __init__(self):
        self.governance_url = os.getenv("GOVERNANCE_URL", "http://governance:8000")
        self.timeout = httpx.Timeout(10.0)
        self.client = httpx.AsyncClient(timeout=self.timeout)

    async def validate_operation(self, operation_data: Dict[str, Any]) -> GovernanceDecision:
        """Validate operation with governance before execution"""
        try:
            response = await self.client.post(
                f"{self.governance_url}/api/validate", json=operation_data
            )
            response.raise_for_status()
            return GovernanceDecision(**response.json())
        except httpx.HTTPError as e:
            logger.error(f"Governance validation failed: {e}")
            return GovernanceDecision(approved=False, reason="Governance service unavailable")

    async def execute_with_governance(self, operation: str, params: Dict[str, Any]):
        """Execute operation with governance oversight"""
        decision = await self.validate_operation({"operation": operation, "params": params})

        if not decision.approved:
            raise PermissionError(f"Operation rejected: {decision.reason}")

        result = await self._execute_operation(operation, params, decision.conditions)
        return result

    async def _execute_operation(
        self, operation: str, params: Dict[str, Any], conditions: Optional[Dict]
    ) -> Any:
        """Override this method in subclasses"""
        raise NotImplementedError("Subclasses must implement _execute_operation")
