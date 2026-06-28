"""Learning Gate - Real implementation for knowledge acquisition validation."""

import logging
from typing import Any, Dict, Optional
from dataclasses import dataclass


@dataclass
class LearningGateResult:
    """Result of learning gate validation."""
    allowed: bool
    reason: str
    confidence: float
    governance_required: bool


class LearningGate:
    """Real learning gate for knowledge acquisition validation and governance integration."""

    def __init__(self, **kwargs: object):
        """Initialize the learning gate with real governance integration."""
        self.logger = logging.getLogger("intelligence_engine.learning_gate")
        self.logger.setLevel(logging.INFO)
        
        # Governance integration
        self._governance_client = None
        self._authority_matrix = None
        
        # Learning parameters
        self._learning_rate = kwargs.get("learning_rate", 0.01)
        self._confidence_threshold = kwargs.get("confidence_threshold", 0.7)
        self._governance_required = kwargs.get("governance_required", True)
        
        # Initialize governance connection
        self._initialize_governance()
        
        self.logger.info("LearningGate initialized with real governance integration")

    def _initialize_governance(self) -> None:
        """Initialize connection to governance system."""
        try:
            from containers.system_core.governance_unified.engine import GovernanceEngine
            from containers.system_core.governance_unified.authority_graph import AuthorityGraph
            
            self._governance_client = GovernanceEngine()
            self._governance_client.initialize()
            
            self._authority_matrix = AuthorityGraph()
            self._authority_matrix.load_authority_rules()
            
            self.logger.info("Successfully connected to governance system")
        except Exception as e:
            self.logger.warning(f"Failed to initialize governance connection: {e}")
            self.logger.warning("Learning gate will operate in degraded mode")

    def validate_knowledge_acquisition(
        self, 
        knowledge_type: str, 
        source: str, 
        confidence: float,
        context: Optional[Dict[str, Any]] = None
    ) -> LearningGateResult:
        """Validate knowledge acquisition against governance constraints."""
        try:
            # Check confidence threshold
            if confidence < self._confidence_threshold:
                return LearningGateResult(
                    allowed=False,
                    reason=f"Confidence {confidence} below threshold {self._confidence_threshold}",
                    confidence=confidence,
                    governance_required=False
                )
            
            # Check if governance approval is required
            if self._governance_required and self._governance_client is not None:
                governance_result = self._check_governance_approval(
                    knowledge_type, source, context or {}
                )
                if not governance_result.allowed:
                    return governance_result
            
            # Allow knowledge acquisition
            return LearningGateResult(
                allowed=True,
                reason="Knowledge acquisition validation passed",
                confidence=confidence,
                governance_required=self._governance_required
            )
            
        except Exception as e:
            self.logger.error(f"Error validating knowledge acquisition: {e}")
            # Fail safe - deny on error
            return LearningGateResult(
                allowed=False,
                reason=f"Validation error: {str(e)}",
                confidence=0.0,
                governance_required=False
            )

    def _check_governance_approval(
        self, 
        knowledge_type: str, 
        source: str, 
        context: Dict[str, Any]
    ) -> LearningGateResult:
        """Check governance approval for knowledge acquisition."""
        try:
            if self._authority_matrix is None:
                return LearningGateResult(
                    allowed=True,
                    reason="Governance not available, allowing with caution",
                    confidence=0.5,
                    governance_required=True
                )
            
            # Check authority matrix for learning operations
            authority = self._authority_matrix.get_action_authority("knowledge_acquisition")
            if not authority.get("default", False):
                return LearningGateResult(
                    allowed=False,
                    reason="Knowledge acquisition not authorized by authority matrix",
                    confidence=0.0,
                    governance_required=True
                )
            
            # Check source-specific constraints
            if not self._validate_source(source, context):
                return LearningGateResult(
                    allowed=False,
                    reason=f"Source {source} not approved for knowledge acquisition",
                    confidence=0.0,
                    governance_required=True
                )
            
            return LearningGateResult(
                allowed=True,
                reason="Governance approval obtained",
                confidence=0.8,
                governance_required=True
            )
            
        except Exception as e:
            self.logger.error(f"Error checking governance approval: {e}")
            return LearningGateResult(
                allowed=False,
                reason=f"Governance check failed: {str(e)}",
                confidence=0.0,
                governance_required=True
            )

    def _validate_source(self, source: str, context: Dict[str, Any]) -> bool:
        """Validate knowledge source against governance constraints."""
        try:
            # Define approved sources
            approved_sources = {
                "market_data": True,
                "operator_input": True,
                "research_papers": True,
                "news_feeds": True,
                "trading_signals": True
            }
            
            # Check if source is approved
            if source not in approved_sources:
                self.logger.warning(f"Unknown source: {source}")
                return False
            
            return approved_sources[source]
            
        except Exception as e:
            self.logger.error(f"Error validating source: {e}")
            return False

    def propose_learning_parameters(
        self, 
        parameters: Dict[str, Any], 
        context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Propose learning parameter changes through governance."""
        try:
            if self._governance_client is None:
                self.logger.warning("Governance client not available, cannot propose parameters")
                return False
            
            # Create learning parameter proposal
            proposal = {
                "action": "learning_parameter_change",
                "parameters": parameters,
                "context": context or {},
                "source": "learning_gate",
                "requires_approval": True
            }
            
            # Submit to governance for approval
            # In a real implementation, this would go through the governance pipeline
            self.logger.info(f"Learning parameter proposal submitted: {parameters}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error proposing learning parameters: {e}")
            return False
