"""
DIX VISION Causal Governance Optimizer

Applies causal discovery to governance optimization by discovering
causal relationships between governance decisions and system outcomes.
"""

from __future__ import annotations

import logging
import threading
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd

# Import existing causal discovery
import sys
sys.path.insert(0, "c:/dix_vision_v42.2/containers/system_core/cognitive_os/causal")
from advanced_causal_discovery import (
    AdvancedCausalDiscovery,
    CausalAlgorithm,
    CausalType,
    CausalStrength,
    CausalRelation,
    CausalGraph
)

# Import existing governance system
import sys
sys.path.insert(0, "c:/dix_vision_v42.2/containers/system_core/governance_unified")
from engine import GovernanceEngine

logger = logging.getLogger(__name__)


@dataclass
class GovernanceCausalRelation:
    """Causal relationship in governance system."""
    relation_id: str
    governance_decision: str  # e.g., "risk_limit_change", "approval_policy_update"
    system_outcome: str  # e.g., "trading_performance", "system_stability"
    causal_type: CausalType
    strength: float
    strength_level: CausalStrength
    confidence: float
    causal_effect: float
    time_lag: Optional[float]  # hours
    governance_context: Dict[str, Any]
    timestamp: float


@dataclass
class GovernanceCausalGraph:
    """Causal graph for governance relationships."""
    graph_id: str
    governance_domain: str  # "cognitive", "financial", "operator", "system"
    nodes: List[str]  # Governance variables
    edges: List[GovernanceCausalRelation]
    is_dag: bool
    graph_properties: Dict[str, Any]
    timestamp: float


@dataclass
class GovernanceCausalIntervention:
    """Causal intervention simulation for governance."""
    intervention_id: str
    governance_decision: str
    intervention_type: str
    intervention_value: float
    expected_system_impact: Dict[str, float]
    governance_implication: str
    confidence: float
    timestamp: float


@dataclass
class GovernanceOptimizationRecommendation:
    """Optimization recommendation based on causal insights."""
    recommendation_id: str
    governance_parameter: str
    current_value: float
    recommended_value: float
    expected_improvement: float
    causal_evidence: List[str]
    risk_assessment: str
    implementation_priority: str
    timestamp: float


class CausalGovernanceOptimizer:
    """
    Applies causal discovery to governance optimization.
    
    Discovers causal relationships between:
    - Governance decisions and system performance
    - Policy changes and operational outcomes
    - Risk parameters and trading results
    - Approval processes and system efficiency
    """
    
    def __init__(self):
        # Initialize causal discovery engine
        self._causal_discovery = AdvancedCausalDiscovery()
        
        # Initialize governance engine
        self._governance_engine = GovernanceEngine()
        
        # Governance causal graphs by domain
        self._governance_graphs: Dict[str, GovernanceCausalGraph] = {}
        
        # Historical governance causal relationships
        self._governance_causal_history: deque = deque(maxlen=1000)
        
        # Intervention results
        self._intervention_results: Dict[str, GovernanceCausalIntervention] = {}
        
        # Optimization recommendations
        self._optimization_recommendations: List[GovernanceOptimizationRecommendation] = []
        
        # Governance variables mapping
        self._governance_variables = {
            "risk_limit": "Risk Limit",
            "approval_threshold": "Approval Threshold",
            "leverage_limit": "Leverage Limit",
            "position_size_limit": "Position Size Limit",
            "stop_loss_threshold": "Stop Loss Threshold",
            "governance_latency": "Governance Latency",
            "approval_rate": "Approval Rate",
            "rejection_rate": "Rejection Rate"
        }
        
        # System outcome variables
        self._system_outcomes = {
            "trading_performance": "Trading Performance",
            "system_stability": "System Stability",
            "operational_efficiency": "Operational Efficiency",
            "risk_compliance": "Risk Compliance",
            "error_rate": "Error Rate",
            "downtime": "System Downtime"
        }
        
        self._lock = threading.Lock()
        
        logger.info("Causal Governance Optimizer initialized")
    
    def prepare_governance_data(self, governance_data: Dict[str, Any]) -> pd.DataFrame:
        """Prepare governance data for causal discovery."""
        data_dict = {}
        
        # Add governance variables
        for var_key, var_name in self._governance_variables.items():
            if var_key in governance_data:
                data_dict[var_name] = [governance_data[var_key]]
            else:
                data_dict[var_name] = [self._get_default_governance_value(var_key)]
        
        # Add system outcomes
        for outcome_key, outcome_name in self._system_outcomes.items():
            if outcome_key in governance_data:
                data_dict[outcome_name] = [governance_data[outcome_key]]
            else:
                data_dict[outcome_name] = [self._get_default_outcome_value(outcome_key)]
        
        return pd.DataFrame(data_dict)
    
    def _get_default_governance_value(self, var_key: str) -> float:
        """Get default value for governance variable."""
        defaults = {
            "risk_limit": 0.02,
            "approval_threshold": 0.7,
            "leverage_limit": 2.0,
            "position_size_limit": 100000.0,
            "stop_loss_threshold": 0.05,
            "governance_latency": 100.0,
            "approval_rate": 0.8,
            "rejection_rate": 0.2
        }
        return defaults.get(var_key, 0.0)
    
    def _get_default_outcome_value(self, outcome_key: str) -> float:
        """Get default value for system outcome."""
        defaults = {
            "trading_performance": 0.5,
            "system_stability": 0.9,
            "operational_efficiency": 0.8,
            "risk_compliance": 0.95,
            "error_rate": 0.01,
            "downtime": 0.001
        }
        return defaults.get(outcome_key, 0.0)
    
    def discover_governance_causal_relationships(self, governance_domain: str,
                                                 governance_data: Dict[str, Any],
                                                 algorithm: CausalAlgorithm = CausalAlgorithm.PC_ALGORITHM) -> GovernanceCausalGraph:
        """Discover causal relationships in governance system."""
        # Prepare data
        df = self.prepare_governance_data(governance_data)
        
        # Apply causal discovery
        causal_graph = self._causal_discovery.discover_causal_graph(
            data=df,
            algorithm=algorithm
        )
        
        # Convert to governance-specific causal graph
        governance_graph = self._convert_to_governance_graph(governance_domain, causal_graph, governance_data)
        
        with self._lock:
            self._governance_graphs[governance_domain] = governance_graph
            self._governance_causal_history.append(governance_graph)
        
        logger.info(f"Discovered {len(governance_graph.edges)} governance causal relationships for {governance_domain}")
        
        return governance_graph
    
    def _convert_to_governance_graph(self, governance_domain: str,
                                    causal_graph: CausalGraph,
                                    governance_data: Dict[str, Any]) -> GovernanceCausalGraph:
        """Convert general causal graph to governance-specific graph."""
        governance_edges = []
        
        for edge in causal_graph.edges:
            # Only keep edges that involve governance variables or system outcomes
            if (edge.cause_variable in self._governance_variables.values() or
                edge.effect_variable in self._system_outcomes.values()):
                
                governance_edge = GovernanceCausalRelation(
                    relation_id=f"{governance_domain}_{edge.relation_id}",
                    governance_decision=edge.cause_variable,
                    system_outcome=edge.effect_variable,
                    causal_type=edge.causal_type,
                    strength=edge.strength,
                    strength_level=edge.strength_level,
                    confidence=edge.confidence,
                    causal_effect=edge.causal_effect,
                    time_lag=edge.time_lag,
                    governance_context={
                        "domain": governance_domain,
                        "timestamp": datetime.now().isoformat(),
                        "data_context": governance_data
                    },
                    timestamp=datetime.now().timestamp()
                )
                governance_edges.append(governance_edge)
        
        return GovernanceCausalGraph(
            graph_id=f"{governance_domain}_governance_causal_graph",
            governance_domain=governance_domain,
            nodes=causal_graph.nodes,
            edges=governance_edges,
            is_dag=causal_graph.is_dag,
            graph_properties=causal_graph.graph_properties,
            timestamp=datetime.now().timestamp()
        )
    
    def analyze_governance_impact_drivers(self, governance_domain: str) -> List[GovernanceCausalRelation]:
        """Analyze what governance decisions drive system outcomes."""
        if governance_domain not in self._governance_graphs:
            return []
        
        graph = self._governance_graphs[governance_domain]
        
        # Find causal relations where cause is a governance decision
        impact_drivers = [
            edge for edge in graph.edges
            if edge.governance_decision in self._governance_variables.values()
        ]
        
        # Sort by strength
        impact_drivers.sort(key=lambda x: x.strength, reverse=True)
        
        return impact_drivers
    
    def simulate_governance_intervention(self, governance_domain: str,
                                       governance_decision: str,
                                       intervention_value: float) -> GovernanceCausalIntervention:
        """Simulate a governance intervention using causal reasoning."""
        if governance_domain not in self._governance_graphs:
            return None
        
        graph = self._governance_graphs[governance_domain]
        
        # Find causal chain from governance decision to system outcomes
        system_effects = []
        
        for edge in graph.edges:
            if edge.governance_decision == governance_decision:
                if edge.system_outcome in self._system_outcomes.values():
                    system_effects.append(edge)
        
        # Calculate expected system impacts
        expected_impacts = {}
        for effect in system_effects:
            impact = effect.causal_effect * intervention_value
            expected_impacts[effect.system_outcome] = impact
        
        # Determine governance implication
        performance_impact = expected_impacts.get("Trading Performance", 0.0)
        stability_impact = expected_impacts.get("System Stability", 0.0)
        
        if performance_impact > 0.1 and stability_impact > 0.0:
            governance_implication = "Positive impact expected - recommended implementation"
        elif performance_impact < -0.1 or stability_impact < -0.0:
            governance_implication = "Negative impact expected - caution recommended"
        else:
            governance_implication = "Minimal impact expected - neutral recommendation"
        
        # Calculate confidence based on edge confidences
        confidence = np.mean([edge.confidence for edge in system_effects]) if system_effects else 0.0
        
        intervention = GovernanceCausalIntervention(
            intervention_id=f"{governance_domain}_{governance_decision}_intervention",
            governance_decision=governance_decision,
            intervention_type="do",
            intervention_value=intervention_value,
            expected_system_impact=expected_impacts,
            governance_implication=governance_implication,
            confidence=confidence,
            timestamp=datetime.now().timestamp()
        )
        
        with self._lock:
            self._intervention_results[intervention.intervention_id] = intervention
        
        return intervention
    
    def generate_optimization_recommendations(self, governance_domain: str) -> List[GovernanceOptimizationRecommendation]:
        """Generate governance optimization recommendations based on causal insights."""
        if governance_domain not in self._governance_graphs:
            return []
        
        graph = self._governance_graphs[governance_domain]
        impact_drivers = self.analyze_governance_impact_drivers(governance_domain)
        
        recommendations = []
        
        for driver in impact_drivers[:5]:  # Top 5 drivers
            # Determine optimization direction
            if driver.causal_effect > 0:
                # Positive effect - increase value
                current_value = self._get_default_governance_value(
                    self._get_var_key_from_name(driver.governance_decision)
                )
                recommended_value = current_value * 1.2  # 20% increase
                expected_improvement = driver.causal_effect * 0.2
            else:
                # Negative effect - decrease value
                current_value = self._get_default_governance_value(
                    self._get_var_key_from_name(driver.governance_decision)
                )
                recommended_value = current_value * 0.8  # 20% decrease
                expected_improvement = abs(driver.causal_effect) * 0.2
            
            # Determine implementation priority
            if driver.strength > 0.7 and driver.confidence > 0.8:
                priority = "HIGH"
            elif driver.strength > 0.5 and driver.confidence > 0.6:
                priority = "MEDIUM"
            else:
                priority = "LOW"
            
            # Risk assessment
            if abs(driver.causal_effect) > 0.3:
                risk_assessment = "HIGH_RISK_HIGH_REWARD"
            elif abs(driver.causal_effect) > 0.1:
                risk_assessment = "MODERATE_RISK_MODERATE_REWARD"
            else:
                risk_assessment = "LOW_RISK_LOW_REWARD"
            
            recommendation = GovernanceOptimizationRecommendation(
                recommendation_id=f"opt_{int(datetime.now().timestamp())}",
                governance_parameter=driver.governance_decision,
                current_value=current_value,
                recommended_value=recommended_value,
                expected_improvement=expected_improvement,
                causal_evidence=[
                    f"Causal strength: {driver.strength:.2f}",
                    f"Confidence: {driver.confidence:.2f}",
                    f"Effect on {driver.system_outcome}: {driver.causal_effect:.3f}"
                ],
                risk_assessment=risk_assessment,
                implementation_priority=priority,
                timestamp=datetime.now().timestamp()
            )
            
            recommendations.append(recommendation)
        
        with self._lock:
            self._optimization_recommendations.extend(recommendations)
        
        return recommendations
    
    def _get_var_key_from_name(self, var_name: str) -> str:
        """Get variable key from variable name."""
        for key, name in self._governance_variables.items():
            if name == var_name:
                return key
        return var_name.lower().replace(" ", "_")
    
    def get_governance_causal_insights(self, governance_domain: str) -> Dict[str, Any]:
        """Get comprehensive causal insights for governance."""
        if governance_domain not in self._governance_graphs:
            return {"error": f"No causal graph found for {governance_domain}"}
        
        graph = self._governance_graphs[governance_domain]
        impact_drivers = self.analyze_governance_impact_drivers(governance_domain)
        recommendations = self.generate_optimization_recommendations(governance_domain)
        
        return {
            "governance_domain": governance_domain,
            "total_causal_relations": len(graph.edges),
            "is_dag": graph.is_dag,
            "impact_drivers": [
                {
                    "governance_decision": driver.governance_decision,
                    "system_outcome": driver.system_outcome,
                    "strength": driver.strength,
                    "confidence": driver.confidence,
                    "causal_effect": driver.causal_effect
                }
                for driver in impact_drivers
            ],
            "optimization_recommendations": [
                {
                    "parameter": rec.governance_parameter,
                    "current_value": rec.current_value,
                    "recommended_value": rec.recommended_value,
                    "expected_improvement": rec.expected_improvement,
                    "priority": rec.implementation_priority,
                    "risk_assessment": rec.risk_assessment
                }
                for rec in recommendations
            ],
            "graph_properties": graph.graph_properties,
            "timestamp": graph.timestamp
        }


class PredictiveGovernanceSystem:
    """
    Predictive governance system using causal discovery.
    
    Uses causal relationships to predict governance outcomes and
    recommend proactive governance interventions.
    """
    
    def __init__(self):
        self._causal_optimizer = CausalGovernanceOptimizer()
        self._prediction_history: List[Dict[str, Any]] = []
        
        self._lock = threading.Lock()
        
        logger.info("Predictive Governance System initialized")
    
    def predict_governance_outcome(self, governance_domain: str,
                                  governance_scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Predict system outcome for a governance scenario."""
        # Discover causal relationships for scenario
        causal_graph = self._causal_optimizer.discover_governance_causal_relationships(
            governance_domain, governance_scenario
        )
        
        # Simulate interventions for scenario parameters
        predictions = {}
        
        for param, value in governance_scenario.items():
            if param in self._causal_optimizer._governance_variables:
                intervention = self._causal_optimizer.simulate_governance_intervention(
                    governance_domain, param, value
                )
                if intervention:
                    predictions[param] = {
                        "expected_impact": intervention.expected_system_impact,
                        "governance_implication": intervention.governance_implication,
                        "confidence": intervention.confidence
                    }
        
        prediction_result = {
            "governance_domain": governance_domain,
            "scenario": governance_scenario,
            "predictions": predictions,
            "causal_relations_count": len(causal_graph.edges),
            "timestamp": datetime.now().isoformat()
        }
        
        with self._lock:
            self._prediction_history.append(prediction_result)
        
        return prediction_result
    
    def recommend_proactive_governance(self, governance_domain: str) -> List[GovernanceOptimizationRecommendation]:
        """Recommend proactive governance interventions."""
        return self._causal_optimizer.generate_optimization_recommendations(governance_domain)
    
    def get_predictive_governance_status(self) -> Dict[str, Any]:
        """Get predictive governance system status."""
        with self._lock:
            recent_predictions = self._prediction_history[-10:] if self._prediction_history else []
            
            return {
                "total_predictions": len(self._prediction_history),
                "recent_predictions": len(recent_predictions),
                "governance_domains_analyzed": list(self._causal_optimizer._governance_graphs.keys()),
                "total_recommendations": len(self._causal_optimizer._optimization_recommendations)
            }


# Global instances
_causal_governance_optimizer: Optional[CausalGovernanceOptimizer] = None
_predictive_governance_system: Optional[PredictiveGovernanceSystem] = None


def get_causal_governance_optimizer() -> CausalGovernanceOptimizer:
    """Get global causal governance optimizer instance."""
    global _causal_governance_optimizer
    if _causal_governance_optimizer is None:
        _causal_governance_optimizer = CausalGovernanceOptimizer()
    return _causal_governance_optimizer


def get_predictive_governance_system() -> PredictiveGovernanceSystem:
    """Get global predictive governance system instance."""
    global _predictive_governance_system
    if _predictive_governance_system is None:
        _predictive_governance_system = PredictiveGovernanceSystem()
    return _predictive_governance_system