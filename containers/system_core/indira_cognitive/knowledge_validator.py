"""
INDIRA Knowledge Validator - Knowledge Layer Component
Validates incoming knowledge sources for reliability, accuracy, and consistency
Per Rule 6 of the DIX VISION Tier-0 Production Implementation Contract
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class KnowledgeSource(Enum):
    """Types of knowledge sources"""

    MARKET_DATA = "market_data"
    NEWS_SENTIMENT = "news_sentiment"
    ONCHAIN_ANALYSIS = "onchain_analysis"
    SOCIAL_SIGNAL = "social_signal"
    FUNDAMENTAL_DATA = "fundamental_data"
    TECHNICAL_ANALYSIS = "technical_analysis"
    OPERATOR_INPUT = "operator_input"
    INTERNAL_MODEL = "internal_model"


class ValidationLevel(Enum):
    """Knowledge validation confidence levels"""

    VERIFIED = "verified"
    PROBABLE = "probable"
    UNCERTAIN = "uncertain"
    REJECTED = "rejected"


@dataclass
class ValidationResult:
    """Result of knowledge validation"""

    source: KnowledgeSource
    confidence: float  # 0.0 to 1.0
    level: ValidationLevel
    evidence: List[str]
    warnings: List[str]
    timestamp: datetime
    metadata: Dict[str, Any]


class KnowledgeValidator:
    """
    Validates incoming knowledge for INDIRA cognitive system
    Ensures every belief is traceable to validated evidence
    """

    def __init__(self):
        self._source_reliability = {
            KnowledgeSource.MARKET_DATA: 0.95,
            KnowledgeSource.ONCHAIN_ANALYSIS: 0.98,
            KnowledgeSource.FUNDAMENTAL_DATA: 0.85,
            KnowledgeSource.TECHNICAL_ANALYSIS: 0.80,
            KnowledgeSource.NEWS_SENTIMENT: 0.60,
            KnowledgeSource.SOCIAL_SIGNAL: 0.50,
            KnowledgeSource.OPERATOR_INPUT: 0.90,
            KnowledgeSource.INTERNAL_MODEL: 0.75,
        }

        self._validation_history: List[ValidationResult] = []
        self._confidence_decay = 0.95  # decay factor for old knowledge

    def validate_knowledge(
        self,
        knowledge: Dict[str, Any],
        source: KnowledgeSource,
        context: Optional[Dict[str, Any]] = None,
    ) -> ValidationResult:
        """
        Validate incoming knowledge piece
        Returns validation result with confidence level
        """
        evidence = []
        warnings = []
        base_confidence = self._source_reliability[source]

        # Rule 6 Acceptance: Every belief traceable to evidence
        if "evidence" not in knowledge:
            warnings.append("No evidence provided for knowledge")
            base_confidence *= 0.5

        if "timestamp" not in knowledge:
            warnings.append("No timestamp provided")
            base_confidence *= 0.7

        # Check for required fields based on source type
        required_fields = self._get_required_fields(source)
        for field in required_fields:
            if field not in knowledge:
                warnings.append(f"Missing required field: {field}")
                base_confidence *= 0.8

        # Validate data consistency
        if self._check_data_consistency(knowledge):
            evidence.append("Data consistency validated")
        else:
            warnings.append("Data inconsistency detected")
            base_confidence *= 0.6

        # Check for conflicts with existing knowledge
        if context:
            conflicts = self._detect_conflicts(knowledge, context)
            if conflicts:
                warnings.append(f"Conflicts detected: {conflicts}")
                base_confidence *= 0.5
            else:
                evidence.append("No conflicts with existing knowledge")

        # Determine validation level
        if base_confidence >= 0.90:
            level = ValidationLevel.VERIFIED
        elif base_confidence >= 0.70:
            level = ValidationLevel.PROBABLE
        elif base_confidence >= 0.50:
            level = ValidationLevel.UNCERTAIN
        else:
            level = ValidationLevel.REJECTED

        # Create validation result
        result = ValidationResult(
            source=source,
            confidence=base_confidence,
            level=level,
            evidence=evidence,
            warnings=warnings,
            timestamp=datetime.utcnow(),
            metadata={"context": context, "raw_confidence": base_confidence},
        )

        self._validation_history.append(result)
        logger.info(
            f"Validated knowledge from {source}: {level.value} (confidence: {base_confidence:.2f})"
        )

        return result

    def _get_required_fields(self, source: KnowledgeSource) -> List[str]:
        """Get required fields for each knowledge source type"""
        required_fields = {
            KnowledgeSource.MARKET_DATA: ["symbol", "price", "volume", "timestamp"],
            KnowledgeSource.ONCHAIN_ANALYSIS: ["address", "contract_type", "timestamp"],
            KnowledgeSource.NEWS_SENTIMENT: ["content", "sentiment", "timestamp"],
            KnowledgeSource.SOCIAL_SIGNAL: ["source", "signal_type", "timestamp"],
            KnowledgeSource.OPERATOR_INPUT: ["operator_id", "command", "timestamp"],
            KnowledgeSource.INTERNAL_MODEL: ["model_id", "prediction", "confidence", "timestamp"],
        }
        return required_fields.get(source, [])

    def _check_data_consistency(self, knowledge: Dict[str, Any]) -> bool:
        """Check internal consistency of knowledge data"""
        try:
            # Check numeric ranges
            if "price" in knowledge:
                price = float(knowledge["price"])
                if price <= 0 or price > 1e9:  # reasonable range
                    return False

            if "volume" in knowledge:
                volume = float(knowledge["volume"])
                if volume < 0:
                    return False

            if "confidence" in knowledge:
                conf = float(knowledge["confidence"])
                if conf < 0 or conf > 1:
                    return False

            return True
        except (TypeError, ValueError):
            return False

    def _detect_conflicts(self, knowledge: Dict[str, Any], context: Dict[str, Any]) -> List[str]:
        """Detect conflicts with existing knowledge"""
        conflicts = []

        # Check for timestamp conflicts
        if "timestamp" in knowledge and "recent_timestamps" in context:
            new_timestamp = knowledge["timestamp"]
            for existing_ts in context["recent_timestamps"]:
                if abs(new_timestamp - existing_ts) < 1:  # 1 second tolerance
                    conflicts.append(f"Timestamp conflict with {existing_ts}")

        # Check for value conflicts in numeric data
        if "price" in knowledge and "current_prices" in context:
            new_price = float(knowledge["price"])
            symbol = knowledge.get("symbol", "")
            if symbol in context["current_prices"]:
                existing_price = context["current_prices"][symbol]
                if abs(new_price - existing_price) / existing_price > 0.10:  # 10% deviation
                    conflicts.append(
                        f"Price conflict for {symbol}: {new_price} vs {existing_price}"
                    )

        return conflicts

    def get_validation_history(
        self, source: Optional[KnowledgeSource] = None, limit: int = 100
    ) -> List[ValidationResult]:
        """Get validation history, optionally filtered by source"""
        history = self._validation_history
        if source:
            history = [r for r in history if r.source == source]
        return history[-limit:]

    def get_source_reliability(self, source: KnowledgeSource) -> float:
        """Get the current reliability score for a knowledge source"""
        return self._source_reliability.get(source, 0.5)

    def update_source_reliability(self, source: KnowledgeSource, delta: float) -> None:
        """
        Update reliability score for a knowledge source
        Delta should be between -1.0 and 1.0
        """
        current = self._source_reliability[source]
        self._source_reliability[source] = max(0.0, min(1.0, current + delta))
        logger.info(
            f"Updated {source} reliability: {current:.2f} -> {self._source_reliability[source]:.2f}"
        )

    def purge_old_validations(self, older_than_hours: int = 24) -> int:
        """Remove validation results older than specified hours"""
        cutoff = datetime.utcnow().timestamp() - (older_than_hours * 3600)
        old_count = len(self._validation_history)
        self._validation_history = [
            r for r in self._validation_history if r.timestamp.timestamp() > cutoff
        ]
        removed = old_count - len(self._validation_history)
        logger.info(f"Purged {removed} old validation results")
        return removed
