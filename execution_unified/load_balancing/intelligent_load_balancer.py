"""
execution_unified.load_balancing.intelligent_load_balancer
DIX VISION v42.2 — Intelligent Load Balancer (Priority 2)

Provides AI-powered load balancing for optimal performance.
This is a Priority 2 enhancement for performance optimization.
"""

from __future__ import annotations

import logging
import threading
import random
from datetime import datetime
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class LoadBalancingAlgorithm(Enum):
    """Load balancing algorithms."""
    ROUND_ROBIN = "ROUND_ROBIN"
    LEAST_CONNECTIONS = "LEAST_CONNECTIONS"
    WEIGHTED_ROUND_ROBIN = "WEIGHTED_ROUND_ROBIN"
    PREDICTIVE = "PREDICTIVE"
    GEOGRAPHIC = "GEOGRAPHIC"


@dataclass
class ExecutionNode:
    """Node for load balancing."""
    
    node_id: str
    node_type: str  # PRIMARY, BACKUP, GEOGRAPHIC
    address: str
    current_connections: int = 0
    max_connections: int = 1000
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    latency_ms: float = 0.0
    is_healthy: bool = True
    region: str = "US_EAST"
    cost_factor: float = 1.0  # Cost multiplier
    last_updated: datetime = field(default_factory=datetime.utcnow)


@dataclass
class LoadBalancingDecision:
    """Load balancing decision."""
    
    decision_id: str
    selected_node: ExecutionNode
    algorithm_used: LoadBalancingAlgorithm
    confidence: float = 0.0
    reasoning: str = ""
    alternative_nodes: List[ExecutionNode] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class TrafficAnalysis:
    """Analysis of traffic patterns."""
    
    total_requests: int = 0
    average_latency: float = 0.0
    peak_requests_per_second: float = 0.0
    geographic_distribution: Dict[str, float] = field(default_factory=dict)
    request_pattern: str = "UNIFORM"  # UNIFORM, SPIKY, BURST


@dataclass
class LoadBalancingResult:
    """Result of load balancing operation."""
    
    success: bool
    decision: Optional[LoadBalancingDecision] = None
    load_distribution: Dict[str, float] = field(default_factory=dict)
    expected_latency_ms: float = 0.0
    total_requests_routed: int = 0
    error_message: str = ""


class TrafficAnalyzer:
    """Analyzes traffic patterns for load balancing."""
    
    def __init__(self):
        self._lock = threading.Lock()
        self._request_history: List[datetime] = []
        self._history_size = 1000
        
        logger.info("[TRAFFIC_ANALYZER] Initialized")
    
    def analyze(self, execution_requests: List[Any]) -> TrafficAnalysis:
        """
        Analyze traffic patterns.
        
        Args:
            execution_requests: List of execution requests
            
        Returns:
            Traffic analysis
        """
        with self._lock:
            current_time = datetime.utcnow()
            
            # Update request history
            for _ in execution_requests:
                self._request_history.append(current_time)
            
            # Keep only recent history
            if len(self._request_history) > self._history_size:
                self._request_history = self._request_history[-self._history_size:]
            
            # Calculate metrics
            total_requests = len(self._request_history)
            
            # Calculate peak requests per second
            if len(self._request_history) >= 60:
                # Calculate requests in last minute
                minute_ago = current_time - datetime.timedelta(minutes=1)
                requests_last_minute = sum(1 for t in self._request_history if t >= minute_ago)
                peak_rps = requests_last_minute / 60.0
            else:
                peak_rps = total_requests / 60.0 if total_requests > 0 else 0.0
            
            # Determine request pattern
            if peak_rps > 100:
                request_pattern = "BURST"
            elif peak_rps > 50:
                request_pattern = "SPIKY"
            else:
                request_pattern = "UNIFORM"
            
            return TrafficAnalysis(
                total_requests=total_requests,
                average_latency=0.0,  # Would be calculated from actual metrics
                peak_requests_per_second=peak_rps,
                request_pattern=request_pattern
            )


class PredictiveScaler:
    """Predicts scaling needs for load balancing."""
    
    def __init__(self):
        self._lock = threading.Lock()
        
        logger.info("[PREDICTIVE_SCALER] Initialized")
    
    def predict(self, traffic_analysis: TrafficAnalysis) -> List[float]:
        """
        Predict future load based on traffic analysis.
        
        Args:
            traffic_analysis: Traffic analysis
            
        Returns:
            Predicted load factors for next time intervals
        """
        with self._lock:
            # Simple prediction based on pattern
            pattern = traffic_analysis.request_pattern
            current_rps = traffic_analysis.peak_requests_per_second
            
            predictions = []
            
            if pattern == "BURST":
                # Bursts may continue or increase
                predictions = [current_rps * 1.2, current_rps * 1.1, current_rps * 1.0]
            elif pattern == "SPIKY":
                # Spiky - conservative prediction
                predictions = [current_rps * 1.1, current_rps * 1.0, current_rps * 0.9]
            else:  # UNIFORM
                # Stable - predict continuation
                predictions = [current_rps * 1.05, current_rps * 1.0, current_rps * 0.95]
            
            return predictions


class LatencyPredictor:
    """Predicts latency for different routing options."""
    
    def __init__(self):
        self._lock = threading.Lock()
        
        logger.info("[LATENCY_PREDICTOR] Initialized")
    
    def predict(self, node: ExecutionNode, current_load: float) -> float:
        """
        Predict latency for a node given current load.
        
        Args:
            node: Execution node
            current_load: Current load percentage
            
        Returns:
            Predicted latency in milliseconds
        """
        with self._lock:
            base_latency = node.latency_ms
            
            # Adjust based on load
            if node.cpu_usage > 80.0 or current_load > 80.0:
                predicted = base_latency * 2.0
            elif node.cpu_usage > 60.0 or current_load > 60.0:
                predicted = base_latency * 1.5
            else:
                predicted = base_latency
            
            return max(predicted, node.latency_ms)


class IntelligentLoadBalancer:
    """
    AI-powered load balancing for optimal performance.
    
    Features:
    - Traffic pattern analysis
    - Predictive scaling
    - Latency prediction
    - Intelligent routing
    - Geographic optimization
    - Cost optimization
    """
    
    def __init__(self):
        self._lock = threading.Lock()
        
        # Components
        self._traffic_analyzer = TrafficAnalyzer()
        self._predictive_scaler = PredictiveScaler()
        self._latency_predictor = LatencyPredictor()
        
        # Nodes
        self._nodes: Dict[str, ExecutionNode] = {}
        self._current_algorithm = LoadBalancingAlgorithm.PREDICTIVE
        
        # Routing statistics
        self._routing_stats: Dict[str, int] = {}
        
        logger.info("[INTELLIGENT_LOAD_BALANCER] Initialized")
    
    def register_node(self, node: ExecutionNode) -> None:
        """Register an execution node."""
        with self._lock:
            self._nodes[node.node_id] = node
            logger.info(f"[INTELLIGENT_LOAD_BALANCER] Registered node: {node.node_id}")
    
    def balance_load(
        self,
        execution_requests: List[Any],
        algorithm: Optional[LoadBalancingAlgorithm] = None
    ) -> LoadBalancingResult:
        """
        Intelligently distribute load across execution nodes.
        
        Args:
            execution_requests: List of execution requests to distribute
            algorithm: Load balancing algorithm to use
            
        Returns:
            Load balancing result
        """
        with self._lock:
            if not self._nodes:
                return LoadBalancingResult(
                    success=False,
                    error_message="No registered nodes"
                )
            
            algorithm = algorithm or self._current_algorithm
            
            # Analyze traffic
            traffic_analysis = self._traffic_analyzer.analyze(execution_requests)
            
            # Predict load
            predicted_loads = self._predictive_scaler.predict(traffic_analysis)
            
            # Balance load using selected algorithm
            if algorithm == LoadBalancingAlgorithm.ROUND_ROBIN:
                result = self._round_robin_balance(execution_requests)
            elif algorithm == LoadBalancingAlgorithm.LEAST_CONNECTIONS:
                result = self._least_connections_balance(execution_requests)
            elif algorithm == LoadBalancingAlgorithm.PREDICTIVE:
                result = self._predictive_balance(execution_requests, predicted_loads)
            elif algorithm == LoadBalancingAlgorithm.GEOGRAPHIC:
                result = self._geographic_balance(execution_requests)
            else:
                result = self._predictive_balance(execution_requests, predicted_loads)
            
            # Calculate expected latency
            if result.decision:
                result.expected_latency_ms = self._latency_predictor.predict(
                    result.decision.selected_node,
                    traffic_analysis.peak_requests_per_second
                )
            
            return result
    
    def _round_robin_balance(self, requests: List[Any]) -> LoadBalancingResult:
        """Round-robin load balancing."""
        node_list = list(self._nodes.values())
        
        if not node_list:
            return LoadBalancingResult(success=False, error_message="No nodes available")
        
        # Select next node in round-robin fashion
        selected_index = self._routing_stats.get("round_robin_index", 0) % len(node_list)
        selected_node = node_list[selected_index]
        
        self._routing_stats["round_robin_index"] = selected_index + 1
        
        decision = LoadBalancingDecision(
            decision_id=f"decision_{int(datetime.utcnow().timestamp() * 1000)}",
            selected_node=selected_node,
            algorithm_used=LoadBalancingAlgorithm.ROUND_ROBIN,
            confidence=0.7,
            reasoning="Round-robin selection"
        )
        
        return LoadBalancingResult(
            success=True,
            decision=decision,
            total_requests_routed=len(requests)
        )
    
    def _least_connections_balance(self, requests: List[Any]) -> LoadBalancingResult:
        """Load balancing based on least connections."""
        healthy_nodes = [n for n in self._nodes.values() if n.is_healthy]
        
        if not healthy_nodes:
            return LoadBalancingResult(success=False, error_message="No healthy nodes")
        
        # Select node with least connections
        selected_node = min(healthy_nodes, key=lambda n: n.current_connections)
        
        decision = LoadBalancingDecision(
            decision_id=f"decision_{int(datetime.utcnow().timestamp() * 1000)}",
            selected_node=selected_node,
            algorithm_used=LoadBalancingAlgorithm.LEAST_CONNECTIONS,
            confidence=0.8,
            reasoning=f"Node with least connections: {selected_node.current_connections}"
        )
        
        return LoadBalancingResult(
            success=True,
            decision=decision,
            total_requests_routed=len(requests)
        )
    
    def _predictive_balance(self, requests: List[Any], predicted_loads: List[float]) -> LoadBalancingResult:
        """Predictive load balancing."""
        healthy_nodes = [n for n in self._nodes.values() if n.is_healthy]
        
        if not healthy_nodes:
            return LoadBaliningResult(success=False, error_message="No healthy nodes")
        
        # Score nodes based on predicted load and current state
        predicted_load = predicted_loads[0] if predicted_loads else 0.0
        
        scored_nodes = []
        for node in healthy_nodes:
            score = 0.0
            reasoning_parts = []
            
            # Lower current connections = higher score
            if node.current_connections < node.max_connections:
                availability_score = (node.max_connections - node.current_connections) / node.max_connections
                score += availability_score * 50
                reasoning_parts.append(f"Availability: {availability_score:.2f}")
            
            # Lower CPU usage = higher score
            cpu_score = (100.0 - node.cpu_usage) / 100.0
            score += cpu_score * 30
            reasoning_parts.append(f"CPU score: {cpu_score:.2f}")
            
            # Lower latency = higher score
            if node.latency_ms > 0:
                latency_score = min(100.0 / node.latency_ms, 1.0)
                score += latency_score * 20
                reasoning_parts.append(f"Latency score: {latency_score:.2f}")
            
            scored_nodes.append((score, node, "; ".join(reasoning_parts)))
        
        # Select best node
        if scored_nodes:
            best_score, best_node, best_reasoning = max(scored_nodes, key=lambda x: x[0])
            confidence = min(best_score / 100.0, 1.0)
        else:
            best_node = healthy_nodes[0]
            best_reasoning = "Default selection"
            confidence = 0.5
        
        # Get alternatives
        alternatives = [s[1] for s in sorted(scored_nodes, key=lambda x: x[0], reverse=True)[1:3]]
        
        decision = LoadBalancingDecision(
            decision_id=f"decision_{int(datetime.utcnow().timestamp() * 1000)}",
            selected_node=best_node,
            algorithm_used=LoadBalancingAlgorithm.PREDICTIVE,
            confidence=confidence,
            reasoning=best_reasoning,
            alternative_nodes=alternatives
        )
        
        return LoadBalancingResult(
            success=True,
            decision=decision,
            total_requests_routed=len(requests)
        )
    
    def _geographic_balance(self, requests: List[Any]) -> LoadBalancingResult:
        """Geographic load balancing."""
        healthy_nodes = [n for n in self._nodes.values() if n.is_healthy]
        
        if not healthy_nodes:
            return LoadBalancingResult(success=False, error_message="No healthy nodes")
        
        # Group nodes by region
        regions: Dict[str, List[ExecutionNode]] = {}
        for node in healthy_nodes:
            if node.region not in regions:
                regions[node.region] = []
            regions[node.region].append(node)
        
        # Select region with most available nodes
        best_region = max(regions.keys(), key=lambda r: len(regions[r]))
        region_nodes = regions[best_region]
        
        # Select node within region with least connections
        selected_node = min(region_nodes, key=lambda n: n.current_connections)
        
        decision = LoadBalancingDecision(
            decision_id=f"decision_{int(datetime.utcnow().timestamp() * 1000)}",
            selected_node=selected_node,
            algorithm_used=LoadBalancingAlgorithm.GEOGRAPHIC,
            confidence=0.75,
            reasoning=f"Geographic selection for region {best_region}"
        )
        
        return LoadBalancingResult(
            success=True,
            decision=decision,
            total_requests_routed=len(requests)
        )
    
    def get_load_distribution(self) -> Dict[str, float]:
        """Get current load distribution across nodes."""
        with self._lock:
            total_connections = sum(node.current_connections for node in self._nodes.values())
            
            distribution = {}
            for node_id, node in self._nodes.items():
                if total_connections > 0:
                    distribution[node_id] = node.current_connections / total_connections
                else:
                    distribution[node_id] = 0.0
            
            return distribution
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get load balancer statistics."""
        with self._lock:
            return {
                "registered_nodes": len(self._nodes),
                "current_algorithm": self._current_algorithm.value,
                "routing_stats": self._routing_stats,
                "load_distribution": self.get_load_distribution(),
                "healthy_nodes": sum(1 for n in self._nodes.values() if n.is_healthy),
                "total_connections": sum(n.current_connections for n in self._nodes.values())
            }


# Singleton instance
_intelligent_load_balancer: Optional[IntelligentLoadBalancer] = None
_intelligent_load_balancer_lock = threading.Lock()

def get_intelligent_load_balancer() -> IntelligentLoadBalancer:
    """Get the singleton intelligent load balancer instance."""
    global _intelligent_load_balancer
    if _intelligent_load_balancer is None:
        with _intelligent_load_balancer_lock:
            if _intelligent_load_balancer is None:
                _intelligent_load_balancer = IntelligentLoadBalancer()
    return _intelligent_load_balancer


__all__ = [
    "LoadBalancingAlgorithm",
    "ExecutionNode",
    "LoadBalancingDecision",
    "TrafficAnalysis",
    "LoadBalancingResult",
    "TrafficAnalyzer",
    "PredictiveScaler",
    "LatencyPredictor",
    "IntelligentLoadBalancer",
    "get_intelligent_load_balancer",
]