"""evolution_engine.dyon.system_behavior_modeling — System Behavior Modeling for DYON.

System behavior modeling and simulation capabilities for advanced system cognition.

This implementation provides system behavior modeling capabilities:
- System behavior simulation under different conditions
- Load modeling and performance prediction
- Failure scenario analysis and resilience testing
- Capacity planning and resource prediction
- Stress testing and bottleneck identification
- Behavior pattern analysis
- Configuration simulation and optimization
- System evolution modeling

Authority (L2/B1): evolution_engine.* only at module level.
DYON provides system behavior modeling for optimization, never for trading purposes.
"""

from __future__ import annotations

import logging
import threading
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

_logger = logging.getLogger(__name__)


class SimulationScenario(Enum):
    """Types of simulation scenarios."""

    LOAD_TEST = "load_test"
    STRESS_TEST = "stress_test"
    FAILURE_SCENARIO = "failure_scenario"
    CAPACITY_PLANNING = "capacity_planning"
    CONFIGURATION_OPTIMIZATION = "configuration_optimization"
    BEHAVIOR_ANALYSIS = "behavior_analysis"
    EVOLUTION_MODELING = "evolution_modeling"


class SystemState(Enum):
    """Possible system states in simulation."""

    NORMAL = "NORMAL"
    DEGRADED = "DEGRADED"
    OVERLOADED = "OVERLOADED"
    FAILED = "FAILED"
    RECOVERING = "RECOVERING"


class ResourceType(Enum):
    """Types of system resources."""

    CPU = "cpu"
    MEMORY = "memory"
    DISK = "disk"
    NETWORK = "network"
    DATABASE_CONNECTIONS = "database_connections"
    THREADS = "threads"


@dataclass
class ResourceConfiguration:
    """System resource configuration for simulation."""

    resource_type: ResourceType
    capacity: float
    available: float
    utilization: float = 0.0
    cost_per_unit: float = 0.0


@dataclass
class SimulationParameter:
    """Parameter for simulation."""

    parameter_name: str
    parameter_value: float
    parameter_type: str  # "continuous", "discrete", "boolean"
    valid_range: Tuple[float, float] = (0.0, 1.0)
    description: str = ""


@dataclass
class SimulationResult:
    """Result of a simulation run."""

    simulation_id: str
    scenario_type: SimulationScenario
    simulation_timestamp: float
    parameters: Dict[str, SimulationParameter] = field(default_factory=dict)
    system_states: List[Dict[str, Any]] = field(default_factory=list)
    final_state: SystemState = SystemState.NORMAL
    resource_utilization: Dict[ResourceType, float] = field(default_factory=dict)
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    bottlenecks: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    confidence: float = 0.0


@dataclass
class BehaviorModel:
    """Abstracted model of system behavior."""

    model_id: str
    model_type: str
    created_timestamp: float
    training_data_points: int
    accuracy_score: float
    parameters: Dict[str, Any] = field(default_factory=dict)
    valid_conditions: List[str] = field(default_factory=list)


class SystemBehaviorModeling:
    """System behavior modeling and simulation engine.

    DYON uses this for system behavior understanding and prediction
    without performing any trading operations.
    """

    def __init__(self, repo_root: str | Path = "."):
        """Initialize system behavior modeling.

        Args:
            repo_root: Path to repository root
        """
        self.repo_root = Path(repo_root)
        self._lock = threading.Lock()
        self._behavior_models: Dict[str, BehaviorModel] = {}
        self._simulation_history: List[SimulationResult] = []
        self._current_configurations: Dict[str, ResourceConfiguration] = {}

        # Initialize default resource configurations
        self._initialize_default_configurations()

        _logger.info(f"[SystemBehaviorModeling] Initialized with repo_root={repo_root}")

    def _initialize_default_configurations(self) -> None:
        """Initialize default resource configurations."""
        self._current_configurations = {
            ResourceType.CPU: ResourceConfiguration(
                resource_type=ResourceType.CPU, capacity=100.0, available=100.0, cost_per_unit=10.0
            ),
            ResourceType.MEMORY: ResourceConfiguration(
                resource_type=ResourceType.MEMORY,
                capacity=16384.0,  # 16GB
                available=16384.0,
                cost_per_unit=0.05,
            ),
            ResourceType.DISK: ResourceConfiguration(
                resource_type=ResourceType.DISK,
                capacity=500000.0,  # 500GB
                available=500000.0,
                cost_per_unit=0.01,
            ),
            ResourceType.NETWORK: ResourceConfiguration(
                resource_type=ResourceType.NETWORK,
                capacity=1000.0,  # 1000 Mbps
                available=1000.0,
                cost_per_unit=0.02,
            ),
            ResourceType.DATABASE_CONNECTIONS: ResourceConfiguration(
                resource_type=ResourceType.DATABASE_CONNECTIONS,
                capacity=100.0,
                available=100.0,
                cost_per_unit=5.0,
            ),
            ResourceType.THREADS: ResourceConfiguration(
                resource_type=ResourceType.THREADS,
                capacity=500.0,
                available=500.0,
                cost_per_unit=0.01,
            ),
        }

    def run_simulation(
        self, scenario_type: SimulationScenario, parameters: Dict[str, Any] = None
    ) -> SimulationResult:
        """Run a simulation scenario.

        Args:
            scenario_type: Type of simulation to run
            parameters: Simulation parameters

        Returns:
            Simulation result
        """
        import time

        simulation_id = f"sim_{int(time.time())}_{scenario_type.value}"
        simulation_timestamp = time.time()

        _logger.info(f"[SystemBehaviorModeling] Running simulation: {scenario_type.value}")

        with self._lock:
            if parameters is None:
                parameters = self._get_default_parameters(scenario_type)

            # Convert parameters to SimulationParameter objects
            sim_parameters = {
                k: SimulationParameter(k, v, self._infer_parameter_type(v))
                for k, v in parameters.items()
            }

            # Run simulation based on scenario type
            if scenario_type == SimulationScenario.LOAD_TEST:
                result = self._simulate_load_test(sim_parameters)
            elif scenario_type == SimulationScenario.STRESS_TEST:
                result = self._simulate_stress_test(sim_parameters)
            elif scenario_type == SimulationScenario.FAILURE_SCENARIO:
                result = self._simulate_failure_scenario(sim_parameters)
            elif scenario_type == SimulationScenario.CAPACITY_PLANNING:
                result = self._simulate_capacity_planning(sim_parameters)
            elif scenario_type == SimulationScenario.CONFIGURATION_OPTIMIZATION:
                result = self._simulate_configuration_optimization(sim_parameters)
            else:
                result = self._simulate_general_behavior(sim_parameters)

            # Add metadata
            result.simulation_id = simulation_id
            result.scenario_type = scenario_type
            result.simulation_timestamp = simulation_timestamp
            result.parameters = sim_parameters

            # Store in history
            self._simulation_history.append(result)

            _logger.info(
                f"[SystemBehaviorModeling] Simulation complete: {result.final_state.value}, "
                f"bottlenecks: {len(result.bottlenecks)}"
            )

            return result

    def _get_default_parameters(self, scenario_type: SimulationScenario) -> Dict[str, Any]:
        """Get default parameters for a scenario type.

        Args:
            scenario_type: Scenario type

        Returns:
            Default parameters
        """
        defaults = {
            SimulationScenario.LOAD_TEST: {
                "concurrent_users": 100,
                "request_rate": 1000,
                "duration_seconds": 300,
                "ramp_up_time": 60,
            },
            SimulationScenario.STRESS_TEST: {
                "max_load_multiplier": 3.0,
                "duration_seconds": 600,
                "failure_threshold": 0.5,
            },
            SimulationScenario.FAILURE_SCENARIO: {
                "component_to_fail": "database",
                "failure_duration_seconds": 120,
                "recovery_time_seconds": 300,
            },
            SimulationScenario.CAPACITY_PLANNING: {
                "growth_rate": 1.2,
                "time_horizon_days": 90,
                "service_level_agreement": 0.99,
            },
            SimulationScenario.CONFIGURATION_OPTIMIZATION: {
                "optimization_target": "cost",
                "performance_requirement": 0.9,
                "configurations_to_test": 10,
            },
        }

        return defaults.get(scenario_type, {})

    def _infer_parameter_type(self, value: Any) -> str:
        """Infer parameter type from value.

        Args:
            value: Parameter value

        Returns:
            Parameter type string
        """
        if isinstance(value, bool):
            return "boolean"
        elif isinstance(value, int):
            return "discrete"
        else:
            return "continuous"

    def _simulate_load_test(self, parameters: Dict[str, SimulationParameter]) -> SimulationResult:
        """Simulate load test scenario.

        Args:
            parameters: Simulation parameters

        Returns:
            Simulation result
        """
        system_states = []
        bottlenecks = []

        # Extract key parameters
        concurrent_users = self._get_param_value(parameters, "concurrent_users", 100)
        request_rate = self._get_param_value(parameters, "request_rate", 1000)
        duration = self._get_param_value(parameters, "duration_seconds", 300)

        # Simulate load test
        current_time = 0
        time_step = 10  # 10 second steps
        request_backlog = 0

        while current_time < duration:
            # Calculate load
            load_factor = (request_rate * concurrent_users) / 10000.0  # Normalized

            # Calculate resource utilization
            cpu_util = min(load_factor * 0.7 + 0.2, 1.0)
            memory_util = min(load_factor * 0.5 + 0.15, 1.0)

            # Calculate request backlog
            arrival_rate = request_rate / time_step
            processing_rate = min(200, request_rate * 0.8)  # Max 200 requests per step
            request_backlog = max(0, request_backlog + (arrival_rate - processing_rate) * time_step)

            # Determine system state
            if cpu_util > 0.9 or request_backlog > 1000:
                state = SystemState.OVERLOADED
            elif cpu_util > 0.7 or request_backlog > 500:
                state = SystemState.DEGRADED
            else:
                state = SystemState.NORMAL

            # Record state
            system_states.append(
                {
                    "time": current_time,
                    "state": state.value,
                    "cpu_util": cpu_util,
                    "memory_util": memory_util,
                    "request_backlog": request_backlog,
                    "throughput": min(request_rate * 0.8, 200),
                }
            )

            # Identify bottlenecks
            if cpu_util > 0.8:
                bottlenecks.append(f"CPU bottleneck at t={current_time}s")
            if request_backlog > 500:
                bottlenecks.append(f"Request queue backlog at t={current_time}s")

            current_time += time_step

        # Calculate final results
        final_state = self._determine_final_state(system_states)

        return SimulationResult(
            system_states=system_states,
            final_state=final_state,
            resource_utilization={ResourceType.CPU: cpu_util, ResourceType.MEMORY: memory_util},
            performance_metrics={
                "avg_throughput": sum(s.get("throughput", 0) for s in system_states)
                / len(system_states),
                "max_backlog": max(s.get("request_backlog", 0) for s in system_states),
                "availability": sum(
                    1 for s in system_states if s["state"] == SystemState.NORMAL.value
                )
                / len(system_states),
            },
            bottlenecks=list(set(bottlenecks)),
            recommendations=self._generate_load_test_recommendations(system_states, bottlenecks),
            confidence=0.85,
        )

    def _simulate_stress_test(self, parameters: Dict[str, SimulationParameter]) -> SimulationResult:
        """Simulate stress test scenario.

        Args:
            parameters: Simulation parameters

        Returns:
            Simulation result
        """
        system_states = []
        bottlenecks = []

        # Extract key parameters
        max_load_multiplier = self._get_param_value(parameters, "max_load_multiplier", 3.0)
        duration = self._get_param_value(parameters, "duration_seconds", 600)

        current_time = 0
        time_step = 10
        load_multiplier = 1.0

        while current_time < duration:
            # Gradually increase load
            if current_time < 120:
                load_multiplier = 1.0 + (max_load_multiplier - 1.0) * (current_time / 120.0)

            # Calculate extreme resource utilization
            cpu_util = min(load_multiplier * 0.95, 1.0)
            memory_util = min(load_multiplier * 0.85, 1.0)

            # Simulate stress effects
            error_rate = max(0.0, (load_multiplier - 1.0) * 0.1)

            # Determine system state
            if cpu_util >= 0.95 or error_rate > 0.5:
                state = SystemState.FAILED
            elif cpu_util > 0.85 or error_rate > 0.1:
                state = SystemState.OVERLOADED
            else:
                state = SystemState.DEGRADED

            system_states.append(
                {
                    "time": current_time,
                    "state": state.value,
                    "cpu_util": cpu_util,
                    "memory_util": memory_util,
                    "error_rate": error_rate,
                    "load_multiplier": load_multiplier,
                }
            )

            # Identify breaking point
            if state == SystemState.FAILED:
                bottlenecks.append(f"System failure at load multiplier: {load_multiplier:.2f}x")

            current_time += time_step

        # Find breaking point
        breaking_point = 1.0
        for state in system_states:
            if state["state"] == SystemState.FAILED.value:
                breaking_point = state["load_multiplier"]
                break

        final_state = self._determine_final_state(system_states)

        return SimulationResult(
            system_states=system_states,
            final_state=final_state,
            resource_utilization={ResourceType.CPU: cpu_util, ResourceType.MEMORY: memory_util},
            performance_metrics={
                "max_stable_load": breaking_point,
                "breaking_point": breaking_point,
                "stress_tolerance": breaking_point,
            },
            bottlenecks=list(set(bottlenecks)),
            recommendations=self._generate_stress_test_recommendations(breaking_point),
            confidence=0.80,
        )

    def _simulate_failure_scenario(
        self, parameters: Dict[str, SimulationParameter]
    ) -> SimulationResult:
        """Simulate failure scenario and system resilience.

        Args:
            parameters: Simulation parameters

        Returns:
            Simulation result
        """
        system_states = []

        # Extract key parameters
        component_to_fail = self._get_param_value(parameters, "component_to_fail", "database")
        failure_duration = self._get_param_value(parameters, "failure_duration_seconds", 120)
        recovery_time = self._get_param_value(parameters, "recovery_time_seconds", 300)

        current_time = 0
        total_duration = failure_duration + recovery_time
        time_step = 10

        while current_time < total_duration:
            # Determine system state based on phase
            if current_time < failure_duration:
                # Failure phase
                state = SystemState.DEGRADED
                performance_impact = 0.5
            else:
                # Recovery phase
                recovery_progress = (current_time - failure_duration) / recovery_time
                if recovery_progress >= 1.0:
                    state = SystemState.NORMAL
                    performance_impact = 1.0
                else:
                    state = SystemState.RECOVERING
                    performance_impact = 0.5 + 0.5 * recovery_progress

            system_states.append(
                {
                    "time": current_time,
                    "state": state.value,
                    "failed_component": component_to_fail,
                    "performance_impact": performance_impact,
                    "phase": "failure" if current_time < failure_duration else "recovery",
                }
            )

            current_time += time_step

        final_state = (
            SystemState.NORMAL
            if (current_time >= failure_duration + recovery_time)
            else SystemState.DEGRADED
        )

        return SimulationResult(
            system_states=system_states,
            final_state=final_state,
            resource_utilization={ResourceType.CPU: 0.3, ResourceType.MEMORY: 0.4},
            performance_metrics={
                "recovery_time": recovery_time,
                "resilience_score": 0.8 if final_state == SystemState.NORMAL else 0.4,
                "mttr": 300.0,
            },
            bottlenecks=[f"{component_to_fail} failure simulation"],
            recommendations=self._generate_failure_scenario_recommendations(component_to_fail),
            confidence=0.75,
        )

    def _simulate_capacity_planning(
        self, parameters: Dict[str, SimulationParameter]
    ) -> SimulationResult:
        """Simulate capacity planning scenarios.

        Args:
            parameters: Simulation parameters

        Returns:
            Simulation result
        """
        system_states = []

        # Extract key parameters
        growth_rate = self._get_param_value(parameters, "growth_rate", 1.2)
        time_horizon_days = self._get_param_value(parameters, "time_horizon_days", 90)
        sla_requirement = self._get_param_value(parameters, "service_level_agreement", 0.99)

        # Simulate capacity over time
        day = 0
        while day < time_horizon_days:
            # Calculate load growth
            current_load = 1.0 * (growth_rate**day)

            # Calculate resource requirements
            required_cpu = current_load * 30.0  # Base 30% CPU
            required_memory = current_load * 4.0  # Base 4GB memory

            # Check if current capacity meets requirement
            cpu_sufficient = required_cpu <= self._current_configurations[ResourceType.CPU].capacity
            memory_sufficient = (
                required_memory <= self._current_configurations[ResourceType.MEMORY].capacity
            )

            # Calculate SLA compliance
            sla_met = cpu_sufficient and memory_sufficient
            sla_score = 1.0 if sla_met else max(0.0, 1.0 - (current_load / sla_requirement))

            system_states.append(
                {
                    "day": day,
                    "load_factor": current_load,
                    "required_cpu": required_cpu,
                    "required_memory": required_memory,
                    "cpu_sufficient": cpu_sufficient,
                    "memory_sufficient": memory_sufficient,
                    "sla_met": sla_met,
                    "sla_score": sla_score,
                }
            )

            day += 1

        # Calculate final requirements
        final_load = 1.0 * (growth_rate ** (time_horizon_days - 1))
        recommended_cpu = final_load * 30.0 * 1.2  # 20% headroom
        recommended_memory = final_load * 4.0 * 1.2

        return SimulationResult(
            system_states=system_states,
            final_state=SystemState.NORMAL,
            resource_utilization={
                ResourceType.CPU: recommended_cpu
                / self._current_configurations[ResourceType.CPU].capacity,
                ResourceType.MEMORY: recommended_memory
                / self._current_configurations[ResourceType.MEMORY].capacity,
            },
            performance_metrics={
                "final_load_factor": final_load,
                "recommended_cpu": recommended_cpu,
                "recommended_memory": recommended_memory,
                "sla_compliance": sum(1 for s in system_states if s["sla_met"])
                / len(system_states),
            },
            bottlenecks=[],
            recommendations=self._generate_capacity_recommendations(
                recommended_cpu,
                recommended_memory,
                self._current_configurations[ResourceType.CPU].capacity,
            ),
            confidence=0.80,
        )

    def _simulate_configuration_optimization(
        self, parameters: Dict[str, SimulationParameter]
    ) -> SimulationResult:
        """Simulate configuration optimization scenarios.

        Args:
            parameters: Simulation parameters

        Returns:
            Simulation result
        """
        system_states = []
        configurations_tested = []

        # Extract key parameters
        optimization_target = self._get_param_value(parameters, "optimization_target", "cost")
        perf_requirement = self._get_param_value(parameters, "performance_requirement", 0.9)
        configs_to_test = self._get_param_value(parameters, "configurations_to_test", 10)

        # Test different configurations
        for i in range(configs_to_test):
            config = self._generate_test_configuration(i, optimization_target)
            config_cost = self._calculate_configuration_cost(config)
            config_performance = self._estimate_configuration_performance(config)

            configurations_tested.append(
                {
                    "config_id": i,
                    "cost": config_cost,
                    "performance": config_performance,
                    "meets_requirements": config_performance >= perf_requirement,
                }
            )

            system_states.append(
                {
                    "config_id": i,
                    "cost": config_cost,
                    "performance": config_performance,
                    "passes_requirements": config_performance >= perf_requirement,
                }
            )

        # Find optimal configuration
        if optimization_target == "cost":
            optimal = min(
                configurations_tested,
                key=lambda x: x["cost"] if x["meets_requirements"] else float("inf"),
            )
        else:
            optimal = max(
                configurations_tested,
                key=lambda x: x["performance"] if x["meets_requirements"] else 0,
            )

        return SimulationResult(
            system_states=system_states,
            final_state=SystemState.NORMAL,
            resource_utilization={
                ResourceType.CPU: optimal["performance"],
                ResourceType.MEMORY: optimal["performance"],
            },
            performance_metrics={
                "optimal_config_id": optimal["config_id"],
                "optimal_cost": optimal["cost"],
                "optimal_performance": optimal["performance"],
                "cost_reduction": 0.0,  # Would calculate relative to baseline
            },
            bottlenecks=[],
            recommendations=[f"Use configuration {optimal['config_id']}"],
            confidence=0.70,
        )

    def _simulate_general_behavior(
        self, parameters: Dict[str, SimulationParameter]
    ) -> SimulationResult:
        """Simulate general system behavior.

        Args:
            parameters: Simulation parameters

        Returns:
            Simulation result
        """
        return SimulationResult(
            system_states=[],
            final_state=SystemState.NORMAL,
            resource_utilization={},
            performance_metrics={},
            bottlenecks=[],
            recommendations=[],
            confidence=0.5,
        )

    def _get_param_value(
        self, parameters: Dict[str, SimulationParameter], key: str, default: Any = None
    ) -> Any:
        """Get parameter value from simulation parameters.

        Args:
            parameters: Simulation parameters
            key: Parameter key
            default: Default value

        Returns:
            Parameter value
        """
        param = parameters.get(key)
        return param.parameter_value if param else default

    def _determine_final_state(self, system_states: List[Dict[str, Any]]) -> SystemState:
        """Determine final system state from simulation.

        Args:
            system_states: System state history

        Returns:
            Final system state
        """
        if not system_states:
            return SystemState.NORMAL

        # Use last state
        return SystemState(system_states[-1]["state"])

    def _generate_load_test_recommendations(
        self, system_states: List[Dict[str, Any]], bottlenecks: List[str]
    ) -> List[str]:
        """Generate recommendations from load test results.

        Args:
            system_states: System state history
            bottlenecks: Identified bottlenecks

        Returns:
            List of recommendations
        """
        recommendations = []

        avg_throughput = sum(s.get("throughput", 0) for s in system_states) / len(system_states)
        max_backlog = max(s.get("request_backlog", 0) for s in system_states)

        if avg_throughput < 150:
            recommendations.append(
                "Consider scaling up processing capacity to handle increased load"
            )

        if max_backlog > 500:
            recommendations.append("Implement request queue management and prioritization")

        if "CPU bottleneck" in str(bottlenecks):
            recommendations.append("Scale CPU resources or optimize processing algorithms")

        return recommendations

    def _generate_stress_test_recommendations(self, breaking_point: float) -> List[str]:
        """Generate recommendations from stress test results.

        Args:
            breaking_point: Breaking point load multiplier

        Returns:
            List of recommendations
        """
        recommendations = []

        if breaking_point < 1.5:
            recommendations.append(
                "System has low stress tolerance - implement graceful degradation"
            )
        elif breaking_point < 2.0:
            recommendations.append("Moderate stress tolerance - add autoscaling capabilities")
        else:
            recommendations.append("Good stress tolerance - ensure scaling automation")

        recommendations.append(
            f"Plan for loads up to {breaking_point * 0.8:.1f}x normal load with confidence"
        )

        return recommendations

    def _generate_failure_scenario_recommendations(self, failed_component: str) -> List[str]:
        """Generate recommendations from failure scenario simulation.

        Args:
            failed_component: Component that failed

        Returns:
            List of recommendations
        """
        recommendations = [
            f"Implement redundant {failed_component} to improve resilience",
            f"Add circuit breaker pattern for {failed_component} interactions",
            f"Implement health checks and automated recovery for {failed_component}",
            "Create runbook for handling {failed_component} failures",
        ]

        return recommendations

    def _generate_capacity_recommendations(
        self, required_cpu: float, required_memory: float, current_capacity: float
    ) -> List[str]:
        """Generate capacity planning recommendations.

        Args:
            required_cpu: Required CPU
            required_memory: Required memory
            current_capacity: Current CPU capacity

        Returns:
            List of recommendations
        """
        recommendations = []

        if required_cpu > current_capacity:
            recommendations.append(
                f"Scale CPU capacity from {current_capacity} to {required_cpu:.1f}"
            )
        else:
            recommendations.append(
                f"Current CPU capacity ({current_capacity}) is sufficient for predicted load"
            )

        if required_memory > current_capacity:
            recommendations.append(
                f"Scale memory capacity from {current_capacity} to {required_memory:.1f}"
            )
        else:
            recommendations.append(
                f"Current memory capacity ({current_capacity}) is sufficient for predicted load"
            )

        return recommendations

    def _generate_test_configuration(self, config_id: int, target: str) -> ResourceConfiguration:
        """Generate a test configuration.

        Args:
            config_id: Configuration ID
            target: Optimization target

        Returns:
            Resource configuration
        """
        if target == "cost":
            # Lower performance, lower cost
            return ResourceConfiguration(
                resource_type=ResourceType.CPU,
                capacity=50.0 + config_id * 10,
                available=50.0 + config_id * 10,
                cost_per_unit=5.0,
            )
        else:
            # Higher performance, higher cost
            return ResourceConfiguration(
                resource_type=ResourceType.CPU,
                capacity=100.0 + config_id * 20,
                available=100.0 + config_id * 20,
                cost_per_unit=15.0,
            )

    def _calculate_configuration_cost(self, config: ResourceConfiguration) -> float:
        """Calculate total cost of configuration.

        Args:
            config: Resource configuration

        Returns:
            Total cost
        """
        return config.capacity * config.cost_per_unit

    def _estimate_configuration_performance(self, config: ResourceConfiguration) -> float:
        """Estimate configuration performance.

        Args:
            config: Resource configuration

        Returns:
            Performance score (0.0 to 1.0)
        """
        # Simple model: more capacity = higher performance
        return min(config.capacity / 100.0, 1.0)

    def get_simulation_history(self, limit: int = 10) -> List[SimulationResult]:
        """Get simulation history.

        Args:
            limit: Maximum number of results to return

        Returns:
            List of simulation results
        """
        with self._lock:
            return list(self._simulation_history[-limit:])

    def analyze_behavior_patterns(self) -> Dict[str, Any]:
        """Analyze behavior patterns from simulation history.

        Returns:
            Behavior pattern analysis
        """
        with self._lock:
            if not self._simulation_history:
                return {"status": "no_history"}

            # Analyze scenario types
            scenario_counts = Counter([s.scenario_type.value for s in self._simulation_history])

            # Analyze success rates
            success_counts = Counter(
                [
                    s.final_state.value
                    for s in self._simulation_history
                    if s.final_state in [SystemState.NORMAL, SystemState.DEGRADED]
                ]
            )

            # Analyze common bottlenecks
            all_bottlenecks = []
            for sim in self._simulation_history:
                all_bottlenecks.extend(sim.bottlenecks)
            bottleneck_counts = Counter(all_bottlenecks)

            return {
                "status": "analyzed",
                "simulations_run": len(self._simulation_history),
                "scenario_distribution": dict(scenario_counts),
                "success_rates": dict(success_counts),
                "common_bottlenecks": dict(bottleneck_counts.most_common(5)),
            }


# Singleton instance
_behavior_modeling: Optional[SystemBehaviorModeling] = None
_modeling_lock = threading.Lock()


def get_system_behavior_modeling(repo_root: str | Path = ".") -> SystemBehaviorModeling:
    """Get singleton instance of system behavior modeling.

    Args:
        repo_root: Path to repository root

    Returns:
        System behavior modeling instance
    """
    global _behavior_modeling

    with _modeling_lock:
        if _behavior_modeling is None:
            _behavior_modeling = SystemBehaviorModeling(repo_root)
        return _behavior_modeling
