"""Dynamic Risk Management with Adaptive Controls - Advanced Risk Intelligence.

This module provides dynamic risk management with adaptive controls, enabling real-time
risk assessment, mitigation, and continuous adaptation to changing market conditions.
"""

from __future__ import annotations

import logging
import threading
import time
from collections import defaultdict, deque
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

import numpy as np

logger = logging.getLogger(__name__)


class RiskType(str, Enum):
    """Types of risks."""

    MARKET = "MARKET"
    CREDIT = "CREDIT"
    LIQUIDITY = "LIQUIDITY"
    OPERATIONAL = "OPERATIONAL"
    SYSTEMIC = "SYSTEMIC"
    CONCENTRATION = "CONCENTRATION"
    EXPOSURE = "EXPOSURE"


class RiskSeverity(str, Enum):
    """Risk severity levels."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class RiskAction(str, Enum):
    """Risk mitigation actions."""

    REDUCE_POSITION = "REDUCE_POSITION"
    INCREASE_POSITION = "INCREASE_POSITION"
    HEDGE = "HEDGE"
    DIVERSIFY = "DIVERSIFY"
    MONITOR = "MONITOR"
    HALT_TRADING = "HALT_TRADING"
    ADAPT_PARAMETERS = "ADAPT_PARAMETERS"


@dataclass
class RiskFactor:
    """Individual risk factor."""

    factor_id: str
    risk_type: RiskType
    severity: RiskSeverity
    value: float
    threshold: float
    trend: str  # "increasing", "decreasing", "stable"
    volatility: float
    confidence: float
    timestamp: float


@dataclass
class RiskAssessment:
    """Comprehensive risk assessment."""

    assessment_id: str
    overall_risk_score: float
    risk_factors: List[RiskFactor]
    risk_distribution: Dict[str, float]
    recommended_actions: List[RiskAction]
    confidence: float
    time_horizon: float
    timestamp: float


@dataclass
class AdaptiveControl:
    """Adaptive control for risk management."""

    control_id: str
    control_type: str
    current_value: float
    target_value: float
    adjustment_rate: float
    triggered_by_risk_factors: List[str]
    action_required: bool
    timestamp: float


@dataclass
class RiskMitigation:
    """Risk mitigation action."""

    mitigation_id: str
    risk_assessment_id: str
    action: RiskAction
    parameters: Dict[str, Any]
    expected_reduction: float
    actual_reduction: Optional[float]
    effectiveness: Optional[float]
    timestamp: float


class DynamicRiskManager:
    """Dynamic risk management system with adaptive controls."""

    def __init__(self):
        self._lock = threading.Lock()
        self._risk_factors: Dict[str, RiskFactor] = {}
        self._risk_assessments: deque = deque(maxlen=1000)
        self._adaptive_controls: Dict[str, AdaptiveControl] = {}
        self._mitigations: List[RiskMitigation] = []
        self._risk_thresholds = self._initialize_default_thresholds()
        self._risk_analyzer = RiskAnalyzer()
        self._control_adaptator = ControlAdaptator()
        self._mitigation_optimizer = MitigationOptimizer()
        self._risk_monitor = RiskMonitor()
        self._initialized = False

    def start(self) -> bool:
        """Start dynamic risk manager."""
        logger.info("[RISK_MANAGER] Starting dynamic risk manager...")
        self._initialized = True
        logger.info("[RISK_MANAGER] Dynamic risk manager started")
        return True

    def stop(self) -> bool:
        """Stop dynamic risk manager."""
        logger.info("[RISK_MANAGER] Stopping dynamic risk manager...")
        self._initialized = False
        logger.info("[RISK_MANAGER] Dynamic risk manager stopped")
        return True

    def assess_risk(
        self,
        market_state: Dict[str, float],
        portfolio_state: Dict[str, float],
        time_horizon: float = 3600.0,
    ) -> RiskAssessment:
        """Perform comprehensive risk assessment."""
        logger.info("[RISK_MANAGER] Performing risk assessment")

        assessment_id = f"risk_assessment_{int(time.time())}"

        # Analyze risk factors
        risk_factors = self._risk_analyzer.analyze_risk_factors(market_state, portfolio_state)

        # Calculate overall risk score
        overall_risk_score = self._calculate_overall_risk(risk_factors)

        # Calculate risk distribution
        risk_distribution = self._calculate_risk_distribution(risk_factors)

        # Generate recommended actions
        recommended_actions = self._generate_recommended_actions(risk_factors, overall_risk_score)

        # Calculate confidence
        confidence = self._calculate_assessment_confidence(risk_factors)

        assessment = RiskAssessment(
            assessment_id=assessment_id,
            overall_risk_score=overall_risk_score,
            risk_factors=risk_factors,
            risk_distribution=risk_distribution,
            recommended_actions=recommended_actions,
            confidence=confidence,
            time_horizon=time_horizon,
            timestamp=time.time(),
        )

        # Store assessment
        with self._lock:
            self._risk_assessments.append(assessment)
            # Update current risk factors
            for factor in risk_factors:
                self._risk_factors[factor.factor_id] = factor

        return assessment

    def apply_adaptive_controls(self, risk_assessment: RiskAssessment) -> List[AdaptiveControl]:
        """Apply adaptive controls based on risk assessment."""
        logger.info("[RISK_MANAGER] Applying adaptive controls")

        controls = []

        # Check each adaptive control
        for control_id, control in self._adaptive_controls.items():
            # Update control based on risk assessment
            updated_control = self._control_adaptator.update_control(
                control, risk_assessment, self._risk_thresholds
            )

            self._adaptive_controls[control_id] = updated_control
            controls.append(updated_control)

        return controls

    def execute_mitigation(
        self, risk_assessment: RiskAssessment, selected_actions: List[RiskAction]
    ) -> List[RiskMitigation]:
        """Execute risk mitigation actions."""
        logger.info(f"[RISK_MANAGER] Executing {len(selected_actions)} mitigation actions")

        mitigations = []

        for action in selected_actions:
            mitigation = self._mitigation_optimizer.execute_mitigation(risk_assessment, action)
            mitigations.append(mitigation)

        # Store mitigations
        with self._lock:
            self._mitigations.extend(mitigations)

        return mitigations

    def monitor_risk(self, risk_assessment: RiskAssessment) -> Dict[str, Any]:
        """Monitor risk in real-time."""
        monitoring_result = self._risk_monitor.monitor(risk_assessment, self._risk_factors)

        return monitoring_result

    def set_risk_threshold(self, risk_type: str, threshold: float) -> None:
        """Set risk threshold for specific risk type."""
        with self._lock:
            self._risk_thresholds[risk_type] = threshold
            logger.info(f"[RISK_MANAGER] Set {risk_type} threshold to {threshold}")

    def get_risk_statistics(self) -> Dict[str, Any]:
        """Get risk management statistics."""
        with self._lock:
            recent_assessments = list(self._risk_assessments)[-10:]

            if recent_assessments:
                avg_risk_score = np.mean([a.overall_risk_score for a in recent_assessments])
                risk_trend = (
                    "increasing"
                    if recent_assessments[-1].overall_risk_score
                    > recent_assessments[0].overall_risk_score
                    else "decreasing"
                )
            else:
                avg_risk_score = 0.0
                risk_trend = "stable"

            return {
                "total_risk_factors": len(self._risk_factors),
                "total_assessments": len(self._risk_assessments),
                "active_controls": len(self._adaptive_controls),
                "total_mitigations": len(self._mitigations),
                "average_risk_score": avg_risk_score,
                "risk_trend": risk_trend,
                "risk_thresholds": self._risk_thresholds.copy(),
            }

    def _initialize_default_thresholds(self) -> Dict[str, float]:
        """Initialize default risk thresholds."""
        return {
            "market": 0.7,
            "credit": 0.8,
            "liquidity": 0.6,
            "operational": 0.5,
            "systemic": 0.9,
            "concentration": 0.7,
            "exposure": 0.8,
        }

    def _calculate_overall_risk(self, risk_factors: List[RiskFactor]) -> float:
        """Calculate overall risk score from individual factors."""
        if not risk_factors:
            return 0.0

        # Weighted average based on severity
        severity_weights = {
            RiskSeverity.LOW: 0.25,
            RiskSeverity.MEDIUM: 0.5,
            RiskSeverity.HIGH: 0.75,
            RiskSeverity.CRITICAL: 1.0,
        }

        total_weight = 0.0
        weighted_risk = 0.0

        for factor in risk_factors:
            weight = severity_weights.get(factor.severity, 0.5)
            weighted_risk += factor.value * weight
            total_weight += weight

        overall_risk = weighted_risk / total_weight if total_weight > 0 else 0.0
        return overall_risk

    def _calculate_risk_distribution(self, risk_factors: List[RiskFactor]) -> Dict[str, float]:
        """Calculate distribution of risk types."""
        distribution = defaultdict(float)

        for factor in risk_factors:
            distribution[factor.risk_type.value] += factor.value

        # Normalize
        total = sum(distribution.values())
        if total > 0:
            distribution = {k: v / total for k, v in distribution.items()}

        return dict(distribution)

    def _generate_recommended_actions(
        self, risk_factors: List[RiskFactor], overall_risk_score: float
    ) -> List[RiskAction]:
        """Generate recommended actions based on risk assessment."""
        actions = []

        # High overall risk requires immediate action
        if overall_risk_score > 0.8:
            actions.extend([RiskAction.HALT_TRADING, RiskAction.REDUCE_POSITION])
        elif overall_risk_score > 0.6:
            actions.extend([RiskAction.REDUCE_POSITION, RiskAction.MONITOR])
        elif overall_risk_score > 0.4:
            actions.extend([RiskAction.HEDGE, RiskAction.MONITOR])

        # Specific risk factors require specific actions
        for factor in risk_factors:
            if factor.severity == RiskSeverity.CRITICAL:
                if factor.risk_type == RiskType.MARKET:
                    actions.append(RiskAction.HEDGE)
                elif factor.risk_type == RiskType.CONCENTRATION:
                    actions.append(RiskAction.DIVERSIFY)
                elif factor.risk_type == RiskType.EXPOSURE:
                    actions.append(RiskAction.REDUCE_POSITION)

        # Remove duplicates while preserving order
        seen = set()
        unique_actions = []
        for action in actions:
            if action not in seen:
                seen.add(action)
                unique_actions.append(action)

        return unique_actions

    def _calculate_assessment_confidence(self, risk_factors: List[RiskFactor]) -> float:
        """Calculate confidence in risk assessment."""
        if not risk_factors:
            return 0.5

        # Confidence based on factor confidence and recency
        factor_confidences = [f.confidence for f in risk_factors]

        # Recency weighting (more recent = higher confidence)
        current_time = time.time()
        time_weights = []
        for factor in risk_factors:
            time_diff = current_time - factor.timestamp
            time_weight = max(0.1, 1.0 - (time_diff / 3600.0))  # 1-hour half-life
            time_weights.append(time_weight)

        # Combine confidences with time weights
        weighted_confidences = [fc * tw for fc, tw in zip(factor_confidences, time_weights)]
        avg_confidence = np.mean(weighted_confidences)

        return avg_confidence


class RiskAnalyzer:
    """Analyze risk factors from market and portfolio states."""

    def analyze_risk_factors(
        self, market_state: Dict[str, float], portfolio_state: Dict[str, float]
    ) -> List[RiskFactor]:
        """Analyze risk factors from current states."""
        risk_factors = []

        # Market risk
        market_volatility = market_state.get("volatility", 0.2)
        market_trend = market_state.get("trend", 0.0)
        market_risk = self._analyze_market_risk(market_volatility, market_trend)
        risk_factors.append(market_risk)

        # Liquidity risk
        liquidity = market_state.get("liquidity", 1.0)
        liquidity_risk = self._analyze_liquidity_risk(liquidity)
        risk_factors.append(liquidity_risk)

        # Exposure risk
        total_exposure = portfolio_state.get("total_exposure", 1.0)
        exposure_risk = self._analyze_exposure_risk(total_exposure)
        risk_factors.append(exposure_risk)

        # Concentration risk
        concentration = portfolio_state.get("concentration", 0.5)
        concentration_risk = self._analyze_concentration_risk(concentration)
        risk_factors.append(concentration_risk)

        return risk_factors

    def _analyze_market_risk(self, volatility: float, trend: float) -> RiskFactor:
        """Analyze market risk."""
        # Market risk based on volatility and trend strength
        market_risk_value = volatility + abs(trend)

        # Determine severity
        if market_risk_value > 0.6:
            severity = RiskSeverity.CRITICAL
        elif market_risk_value > 0.4:
            severity = RiskSeverity.HIGH
        elif market_risk_value > 0.2:
            severity = RiskSeverity.MEDIUM
        else:
            severity = RiskSeverity.LOW

        # Determine trend
        if volatility > 0.3:
            trend_direction = "increasing"
        else:
            trend_direction = "stable"

        return RiskFactor(
            factor_id=f"market_risk_{int(time.time())}",
            risk_type=RiskType.MARKET,
            severity=severity,
            value=market_risk_value,
            threshold=0.5,
            trend=trend_direction,
            volatility=volatility,
            confidence=0.85,
            timestamp=time.time(),
        )

    def _analyze_liquidity_risk(self, liquidity: float) -> RiskFactor:
        """Analyze liquidity risk."""
        # Liquidity risk inversely related to liquidity
        liquidity_risk_value = 1.0 - min(1.0, liquidity)

        if liquidity_risk_value > 0.6:
            severity = RiskSeverity.CRITICAL
        elif liquidity_risk_value > 0.4:
            severity = RiskSeverity.HIGH
        elif liquidity_risk_value > 0.2:
            severity = RiskSeverity.MEDIUM
        else:
            severity = RiskSeverity.LOW

        return RiskFactor(
            factor_id=f"liquidity_risk_{int(time.time())}",
            risk_type=RiskType.LIQUIDITY,
            severity=severity,
            value=liquidity_risk_value,
            threshold=0.4,
            trend="stable",
            volatility=0.1,
            confidence=0.9,
            timestamp=time.time(),
        )

    def _analyze_exposure_risk(self, total_exposure: float) -> RiskFactor:
        """Analyze exposure risk."""
        # Exposure risk based on total exposure
        exposure_risk_value = min(1.0, total_exposure)

        if exposure_risk_value > 0.8:
            severity = RiskSeverity.CRITICAL
        elif exposure_risk_value > 0.6:
            severity = RiskSeverity.HIGH
        elif exposure_risk_value > 0.4:
            severity = RiskSeverity.MEDIUM
        else:
            severity = RiskSeverity.LOW

        return RiskFactor(
            factor_id=f"exposure_risk_{int(time.time())}",
            risk_type=RiskType.EXPOSURE,
            severity=severity,
            value=exposure_risk_value,
            threshold=0.7,
            trend="stable",
            volatility=0.05,
            confidence=0.8,
            timestamp=time.time(),
        )

    def _analyze_concentration_risk(self, concentration: float) -> RiskFactor:
        """Analyze concentration risk."""
        # Concentration risk based on portfolio concentration
        concentration_risk_value = concentration

        if concentration_risk_value > 0.7:
            severity = RiskSeverity.CRITICAL
        elif concentration_risk_value > 0.5:
            severity = RiskSeverity.HIGH
        elif concentration_risk_value > 0.3:
            severity = RiskSeverity.MEDIUM
        else:
            severity = RiskSeverity.LOW

        return RiskFactor(
            factor_id=f"concentration_risk_{int(time.time())}",
            risk_type=RiskType.CONCENTRATION,
            severity=severity,
            value=concentration_risk_value,
            threshold=0.5,
            trend="stable",
            volatility=0.1,
            confidence=0.85,
            timestamp=time.time(),
        )


class ControlAdaptator:
    """Adapt controls based on risk assessment."""

    def update_control(
        self,
        control: AdaptiveControl,
        risk_assessment: RiskAssessment,
        risk_thresholds: Dict[str, float],
    ) -> AdaptiveControl:
        """Update control based on risk assessment."""
        # Check if any risk factors exceed thresholds
        exceeded_thresholds = []
        for risk_factor in risk_assessment.risk_factors:
            threshold = risk_thresholds.get(risk_factor.risk_type.value, 0.5)
            if risk_factor.value > threshold:
                exceeded_thresholds.append(risk_factor.factor_id)

        # Determine if action is required
        action_required = len(exceeded_thresholds) > 0

        # Calculate new target value
        if action_required:
            # More aggressive control when thresholds exceeded
            adjustment_rate = min(1.0, control.adjustment_rate * 1.5)
            target_value = control.target_value * 0.8  # Reduce exposure
        else:
            # Normal adjustment
            adjustment_rate = control.adjustment_rate
            target_value = control.target_value

        # Gradually move towards target
        if action_required:
            current_value = (
                control.current_value - (control.current_value - target_value) * adjustment_rate
            )
        else:
            current_value = control.current_value  # Maintain current value

        updated_control = AdaptiveControl(
            control_id=control.control_id,
            control_type=control.control_type,
            current_value=current_value,
            target_value=target_value,
            adjustment_rate=adjustment_rate,
            triggered_by_risk_factors=exceeded_thresholds,
            action_required=action_required,
            timestamp=time.time(),
        )

        return updated_control


class MitigationOptimizer:
    """Optimize and execute risk mitigation."""

    def execute_mitigation(
        self, risk_assessment: RiskAssessment, action: RiskAction
    ) -> RiskMitigation:
        """Execute specific mitigation action."""
        mitigation_id = f"mitigation_{int(time.time())}_{action.value}"

        # Calculate expected reduction based on action type and risk
        expected_reduction = self._calculate_expected_reduction(action, risk_assessment)

        # Generate action parameters
        parameters = self._generate_action_parameters(action, risk_assessment)

        mitigation = RiskMitigation(
            mitigation_id=mitigation_id,
            risk_assessment_id=risk_assessment.assessment_id,
            action=action,
            parameters=parameters,
            expected_reduction=expected_reduction,
            actual_reduction=None,
            effectiveness=None,
            timestamp=time.time(),
        )

        return mitigation

    def _calculate_expected_reduction(
        self, action: RiskAction, risk_assessment: RiskAssessment
    ) -> float:
        """Calculate expected risk reduction from action."""
        # Simplified reduction calculation
        action_effectiveness = {
            RiskAction.REDUCE_POSITION: 0.6,
            RiskAction.INCREASE_POSITION: -0.3,  # Actually increases risk
            RiskAction.HEDGE: 0.4,
            RiskAction.DIVERSIFY: 0.5,
            RiskAction.MONITOR: 0.1,
            RiskAction.HALT_TRADING: 0.9,
            RiskAction.ADAPT_PARAMETERS: 0.3,
        }

        effectiveness = action_effectiveness.get(action, 0.0)
        expected_reduction = risk_assessment.overall_risk_score * effectiveness

        return max(0.0, expected_reduction)  # Reduction should be positive

    def _generate_action_parameters(
        self, action: RiskAction, risk_assessment: RiskAssessment
    ) -> Dict[str, Any]:
        """Generate parameters for mitigation action."""
        parameters = {
            "action_type": action.value,
            "target_risk_level": max(0.1, risk_assessment.overall_risk_score * 0.8),
            "priority": "high" if risk_assessment.overall_risk_score > 0.7 else "medium",
        }

        if action == RiskAction.REDUCE_POSITION:
            parameters["reduction_percentage"] = 0.2  # Reduce by 20%
        elif action == RiskAction.HEDGE:
            parameters["hedge_ratio"] = 0.5  # 50% hedge
        elif action == RiskAction.DIVERSIFY:
            parameters["diversification_targets"] = ["new_asset_class", "geographic"]

        return parameters


class RiskMonitor:
    """Monitor risk in real-time."""

    def monitor(
        self, risk_assessment: RiskAssessment, current_risk_factors: Dict[str, RiskFactor]
    ) -> Dict[str, Any]:
        """Monitor risk assessment."""
        monitoring_result = {"overall_status": "normal", "alerts": [], "recommendations": []}

        # Check for critical risk factors
        critical_factors = [
            f for f in risk_assessment.risk_factors if f.severity == RiskSeverity.CRITICAL
        ]

        if critical_factors:
            monitoring_result["overall_status"] = "critical"
            monitoring_result["alerts"].extend([f.factor_id for f in critical_factors])
            monitoring_result["recommendations"].append("Immediate action required")

        # Check for high risk factors
        high_factors = [f for f in risk_assessment.risk_factors if f.severity == RiskSeverity.HIGH]

        if high_factors and not critical_factors:
            monitoring_result["overall_status"] = "high"
            monitoring_result["alerts"].extend([f.factor_id for f in high_factors])
            monitoring_result["recommendations"].append("Close monitoring required")

        # Check for increasing risk trends
        increasing_risks = [f for f in risk_assessment.risk_factors if f.trend == "increasing"]

        if increasing_risks:
            monitoring_result["recommendations"].append(
                f"{len(increasing_risks)} risk factors increasing"
            )

        return monitoring_result


# Singleton instance
_risk_manager: Optional[DynamicRiskManager] = None
_risk_manager_lock = threading.Lock()


def get_risk_manager() -> DynamicRiskManager:
    """Get the singleton risk manager instance."""
    global _risk_manager
    if _risk_manager is None:
        with _risk_manager_lock:
            if _risk_manager is None:
                _risk_manager = DynamicRiskManager()
    return _risk_manager


__all__ = [
    "DynamicRiskManager",
    "get_risk_manager",
    "RiskType",
    "RiskSeverity",
    "RiskAction",
    "RiskFactor",
    "RiskAssessment",
    "AdaptiveControl",
    "RiskMitigation",
]
