"""
state.knowledge_validator
DIX VISION v42.2 — Knowledge Validation System

Priority 2 Implementation: Knowledge Layer Completion

Validates knowledge entries for consistency, accuracy, and reliability.
Ensures knowledge stored in the system meets quality standards and is consistent
with the shared world model reality.
"""

from __future__ import annotations

import logging
import threading
from datetime import datetime
from typing import Any, Dict, List, Optional, Set
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class ValidationSeverity(Enum):
    """Severity levels for validation issues."""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


class ValidationStatus(Enum):
    """Status of knowledge validation."""
    VALID = "VALID"
    VALID_WITH_WARNINGS = "VALID_WITH_WARNINGS"
    INVALID = "INVALID"
    PENDING = "PENDING"


@dataclass
class ValidationIssue:
    """A validation issue found in knowledge."""
    severity: ValidationSeverity
    category: str  # consistency, accuracy, reliability, completeness
    description: str
    field: Optional[str] = None
    value: Optional[Any] = None
    expected: Optional[Any] = None
    timestamp: str = ""


@dataclass
class ValidationResult:
    """Result of knowledge validation."""
    status: ValidationStatus
    issues: List[ValidationIssue]
    confidence: float  # 0.0 to 1.0
    validated_at: str = ""
    validator_version: str = "1.0.0"


@dataclass
class KnowledgeEntry:
    """A knowledge entry to be validated."""
    id: str
    content: str
    source: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = ""
    tags: List[str] = field(default_factory=list)


class KnowledgeValidator:
    """
    Knowledge validation system for ensuring knowledge quality.
    
    Responsibilities:
    - Validate knowledge entries for consistency
    - Check accuracy against world model
    - Assess reliability of sources
    - Detect incomplete or inconsistent knowledge
    - Provide confidence scores
    - Maintain validation history
    """
    
    def __init__(self):
        self._lock = threading.Lock()
        
        # Validation rules and thresholds
        self._validation_rules = {
            "consistency": self._check_consistency,
            "accuracy": self._check_accuracy,
            "reliability": self._check_reliability,
            "completeness": self._check_completeness
        }
        
        # Validation thresholds
        self._thresholds = {
            "min_confidence": 0.7,
            "max_warnings": 3,
            "critical_issue_limit": 0
        }
        
        # Source reliability scores
        self._source_reliability: Dict[str, float] = {}
        
        # Validation history
        self._validation_history: Dict[str, ValidationResult] = {}
        
        logger.info("[KNOWLEDGE_VALIDATOR] Knowledge Validator initialized")
    
    def validate_knowledge(
        self,
        knowledge_entry: KnowledgeEntry,
        world_model_state: Optional[Dict[str, Any]] = None
    ) -> ValidationResult:
        """
        Validate a knowledge entry against validation rules.
        
        Args:
            knowledge_entry: Knowledge entry to validate
            world_model_state: Current world model state for consistency checking
            
        Returns:
            ValidationResult with status, issues, and confidence
        """
        with self._lock:
            issues = []
            
            # Run all validation rules
            for category, validator in self._validation_rules.items():
                category_issues = validator(knowledge_entry, world_model_state)
                issues.extend(category_issues)
            
            # Calculate confidence score
            confidence = self._calculate_confidence(issues)
            
            # Determine status
            status = self._determine_status(issues, confidence)
            
            # Create result
            result = ValidationResult(
                status=status,
                issues=issues,
                confidence=confidence,
                validated_at=str(datetime.utcnow())
            )
            
            # Store in history
            self._validation_history[knowledge_entry.id] = result
            
            logger.info(f"[KNOWLEDGE_VALIDATOR] Validated {knowledge_entry.id}: {status.value} (confidence: {confidence:.2f})")
            
            return result
    
    def _check_consistency(
        self,
        knowledge_entry: KnowledgeEntry,
        world_model_state: Optional[Dict[str, Any]] = None
    ) -> List[ValidationIssue]:
        """Check consistency with world model and other knowledge."""
        issues = []
        
        # Check consistency with world model if available
        if world_model_state:
            issues.extend(self._check_world_model_consistency(knowledge_entry, world_model_state))
        
        # Check internal consistency
        issues.extend(self._check_internal_consistency(knowledge_entry))
        
        return issues
    
    def _check_world_model_consistency(
        self,
        knowledge_entry: KnowledgeEntry,
        world_model_state: Dict[str, Any]
    ) -> List[ValidationIssue]:
        """Check consistency with world model state."""
        issues = []
        
        # Check for contradictions with market state
        if "market_state" in world_model_state:
            market_state = world_model_state["market_state"]
            
            # Example: Check if knowledge contradicts known market conditions
            if "bullish" in knowledge_entry.tags and market_state.get("trend") == "bearish":
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.HIGH,
                    category="consistency",
                    description="Knowledge contradicts current market trend",
                    field="tags",
                    value=knowledge_entry.tags,
                    expected=f"tags consistent with {market_state.get('trend')} trend"
                ))
        
        # Check for contradictions with causal structure
        if "causal_structure" in world_model_state:
            causal_structure = world_model_state["causal_structure"]
            
            # Example: Check if knowledge contradicts known causal relationships
            if "causal" in knowledge_entry.tags:
                # Would implement detailed causal consistency checking
                pass
        
        return issues
    
    def _check_internal_consistency(
        self,
        knowledge_entry: KnowledgeEntry
    ) -> List[ValidationIssue]:
        """Check internal consistency of knowledge entry."""
        issues = []
        
        # Check if content is empty
        if not knowledge_entry.content or len(knowledge_entry.content.strip()) < 10:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.HIGH,
                category="completeness",
                description="Knowledge content is too short or empty",
                field="content",
                value=len(knowledge_entry.content) if knowledge_entry.content else 0,
                expected="content with meaningful information"
            ))
        
        # Check timestamp consistency
        try:
            entry_time = datetime.fromisoformat(knowledge_entry.timestamp)
            if entry_time > datetime.utcnow():
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.MEDIUM,
                    category="consistency",
                    description="Knowledge timestamp is in the future",
                    field="timestamp",
                    value=knowledge_entry.timestamp,
                    expected="timestamp not in the future"
                ))
        except ValueError:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.HIGH,
                category="consistency",
                description="Invalid timestamp format",
                field="timestamp",
                value=knowledge_entry.timestamp,
                expected="valid ISO format timestamp"
            ))
        
        return issues
    
    def _check_accuracy(
        self,
        knowledge_entry: KnowledgeEntry,
        world_model_state: Optional[Dict[str, Any]] = None
    ) -> List[ValidationIssue]:
        """Check accuracy of knowledge against reality."""
        issues = []
        
        # Check source credibility
        source_reliability = self._source_reliability.get(knowledge_entry.source, 0.5)
        if source_reliability < self._thresholds["min_confidence"]:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.MEDIUM,
                category="reliability",
                description="Knowledge source has low reliability score",
                field="source",
                value=knowledge_entry.source,
                expected=f"source with reliability >= {self._thresholds['min_confidence']}"
            ))
        
        # Check for factual accuracy markers
        # This would be enhanced with external fact-checking services
        
        return issues
    
    def _check_reliability(
        self,
        knowledge_entry: KnowledgeEntry,
        world_model_state: Optional[Dict[str, Any]] = None
    ) -> List[ValidationIssue]:
        """Check reliability of knowledge source and content."""
        issues = []
        
        # Check if source is specified
        if not knowledge_entry.source or knowledge_entry.source == "unknown":
            issues.append(ValidationIssue(
                severity=ValidationSeverity.LOW,
                category="reliability",
                description="Knowledge source is unknown",
                field="source",
                value=knowledge_entry.source,
                expected="known and credible source"
            ))
        
        # Check for evidence in metadata
        if "evidence" not in knowledge_entry.metadata:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.LOW,
                category="reliability",
                description="No evidence provided in metadata",
                field="metadata",
                expected="evidence field in metadata"
            ))
        
        return issues
    
    def _check_completeness(
        self,
        knowledge_entry: KnowledgeEntry,
        world_model_state: Optional[Dict[str, Any]] = None
    ) -> List[ValidationIssue]:
        """Check completeness of knowledge entry."""
        issues = []
        
        # Check required fields
        required_fields = ["id", "content", "source"]
        for field in required_fields:
            if not getattr(knowledge_entry, field, None):
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.CRITICAL,
                    category="completeness",
                    description=f"Required field is missing",
                    field=field,
                    value=getattr(knowledge_entry, field, None),
                    expected="non-empty value"
                ))
        
        # Check metadata completeness
        if "context" not in knowledge_entry.metadata:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.LOW,
                category="completeness",
                description="Context metadata missing",
                field="metadata",
                expected="context in metadata"
            ))
        
        return issues
    
    def _calculate_confidence(self, issues: List[ValidationIssue]) -> float:
        """Calculate confidence score based on validation issues."""
        if not issues:
            return 1.0
        
        # Penalize confidence based on issue severity
        severity_weights = {
            ValidationSeverity.CRITICAL: 0.5,
            ValidationSeverity.HIGH: 0.3,
            ValidationSeverity.MEDIUM: 0.15,
            ValidationSeverity.LOW: 0.05,
            ValidationSeverity.INFO: 0.0
        }
        
        total_penalty = sum(severity_weights.get(issue.severity, 0.1) for issue in issues)
        confidence = max(0.0, 1.0 - min(total_penalty, 1.0))
        
        return round(confidence, 2)
    
    def _determine_status(self, issues: List[ValidationIssue], confidence: float) -> ValidationStatus:
        """Determine validation status based on issues and confidence."""
        # Check for critical issues
        critical_issues = [issue for issue in issues if issue.severity == ValidationSeverity.CRITICAL]
        if critical_issues:
            return ValidationStatus.INVALID
        
        # Check confidence threshold
        if confidence < self._thresholds["min_confidence"]:
            return ValidationStatus.INVALID
        
        # Check warning limit
        high_issues = [issue for issue in issues if issue.severity in [ValidationSeverity.HIGH, ValidationSeverity.MEDIUM]]
        if len(high_issues) > self._thresholds["max_warnings"]:
            return ValidationStatus.INVALID
        
        # Determine if valid with warnings
        if issues:
            return ValidationStatus.VALID_WITH_WARNINGS
        
        return ValidationStatus.VALID
    
    def update_source_reliability(self, source: str, reliability_score: float) -> None:
        """Update reliability score for a knowledge source."""
        with self._lock:
            self._source_reliability[source] = max(0.0, min(1.0, reliability_score))
            logger.info(f"[KNOWLEDGE_VALIDATOR] Updated source reliability: {source} -> {reliability_score}")
    
    def get_validation_history(self, knowledge_id: str) -> Optional[ValidationResult]:
        """Get validation history for a specific knowledge entry."""
        with self._lock:
            return self._validation_history.get(knowledge_id)
    
    def get_source_reliability(self, source: str) -> float:
        """Get reliability score for a source."""
        with self._lock:
            return self._source_reliability.get(source, 0.5)


# Singleton instance
_knowledge_validator: Optional[KnowledgeValidator] = None
_knowledge_validator_lock = threading.Lock()

def get_knowledge_validator() -> KnowledgeValidator:
    """Get the singleton knowledge validator instance."""
    global _knowledge_validator
    if _knowledge_validator is None:
        with _knowledge_validator_lock:
            if _knowledge_validator is None:
                _knowledge_validator = KnowledgeValidator()
    return _knowledge_validator


__all__ = [
    "ValidationSeverity",
    "ValidationStatus",
    "ValidationIssue",
    "ValidationResult",
    "KnowledgeEntry",
    "KnowledgeValidator",
    "get_knowledge_validator",
]