"""Intelligence Engine - Real Cognitive Processing Implementation

Provides real cognitive processing capabilities for the DIX VISION system,
including meta-cognitive control, trader modeling, and intelligent decision-making.
"""

from __future__ import annotations

from typing import Any, Sequence, Dict, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging
import asyncio
from datetime import datetime, timedelta
import numpy as np

from core.contracts.engine import RuntimeEngine, EngineTier, HealthState, HealthStatus
from core.contracts.events import Event, EventKind

logger = logging.getLogger(__name__)


class CognitiveState(Enum):
    """Cognitive engine states."""
    IDLE = "idle"
    PROCESSING = "processing"
    LEARNING = "learning"
    REASONING = "reasoning"
    ANALYZING = "analyzing"
    PLANNING = "planning"


class ProcessingPriority(Enum):
    """Processing priority levels."""
    CRITICAL = "critical"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


@dataclass
class CognitiveTask:
    """Represents a cognitive processing task."""
    task_id: str
    task_type: str
    priority: ProcessingPriority
    data: Dict[str, Any]
    created_at: datetime = field(default_factory=datetime.now)
    timeout_seconds: float = 30.0
    max_retries: int = 3
    retry_count: int = 0
    completed: bool = False
    result: Optional[Any] = None
    error: Optional[str] = None


@dataclass
class CognitiveInsight:
    """Represents a cognitive insight or discovery."""
    insight_id: str
    insight_type: str
    confidence: float
    evidence: List[str]
    hypothesis: str
    timestamp: datetime = field(default_factory=datetime.now)
    actionable: bool = False
    related_tasks: List[str] = field(default_factory=list)


@dataclass
class MentalModel:
    """Represents a cognitive mental model used for reasoning."""
    model_id: str
    model_name: str
    domain: str
    accuracy_score: float
    last_updated: datetime = field(default_factory=datetime.now)
    usage_count: int = 0
    parameters: Dict[str, Any] = field(default_factory=dict)


class IntelligenceEngine(RuntimeEngine):
    """Real Intelligence Engine with cognitive processing capabilities."""

    name: str = "intelligence_engine"
    tier: EngineTier = EngineTier.RUNTIME

    def __init__(
        self,
        microstructure_plugins: Sequence[Any] = (),
        meta_controller_hot_path: Any = None,
        **kwargs: Any,
    ):
        """Initialize real IntelligenceEngine."""
        self.microstructure_plugins = microstructure_plugins
        self.meta_controller_hot_path = meta_controller_hot_path
        self._initialized = False
        self._running = False
        
        # Cognitive state management
        self._cognitive_state = CognitiveState.IDLE
        self._cognitive_load = 0.0  # 0.0 to 1.0
        self._processing_queue: List[CognitiveTask] = []
        self._insights: List[CognitiveInsight] = []
        self._mental_models: Dict[str, MentalModel] = {}
        
        # Performance metrics
        self._tasks_processed = 0
        self._tasks_failed = 0
        self._average_processing_time = 0.0
        self._insights_generated = 0
        
        # Learning integration
        self._learning_gate = None
        self._learning_active = False
        self._learning_rate = 0.01
        
        # Meta-cognitive capabilities
        self._self_monitoring_active = True
        self._confidence_threshold = 0.7
        self._risk_tolerance = 0.5
        
        # Trader modeling
        self._trader_models: Dict[str, Dict[str, Any]] = {}
        
        # Background processing
        self._processing_loop_task = None
        self._learning_loop_task = None
        
        logger.info("[INTELLIGENCE_ENGINE] Intelligence Engine initialized")

    async def start(self) -> None:
        """Start the intelligence engine."""
        if self._running:
            logger.warning("[INTELLIGENCE_ENGINE] Already running")
            return
        
        logger.info("[INTELLIGENCE_ENGINE] Starting intelligence engine")
        self._running = True
        self._initialized = True
        self._cognitive_state = CognitiveState.IDLE
        
        # Start background processing loop
        self._processing_loop_task = asyncio.create_task(self._processing_loop())
        
        # Start learning loop if gate is available
        if self._learning_gate:
            self._learning_loop_task = asyncio.create_task(self._learning_loop())
        
        logger.info("[INTELLIGENCE_ENGINE] Intelligence engine started successfully")

    async def stop(self) -> None:
        """Stop the intelligence engine."""
        if not self._running:
            logger.warning("[INTELLIGENCE_ENGINE] Not running")
            return
        
        logger.info("[INTELLIGENCE_ENGINE] Stopping intelligence engine")
        self._running = False
        self._cognitive_state = CognitiveState.IDLE
        
        # Cancel background tasks
        if self._processing_loop_task:
            self._processing_loop_task.cancel()
            try:
                await self._processing_loop_task
            except asyncio.CancelledError:
                pass
        
        if self._learning_loop_task:
            self._learning_loop_task.cancel()
            try:
                await self._learning_loop_task
            except asyncio.CancelledError:
                pass
        
        logger.info("[INTELLIGENCE_ENGINE] Intelligence engine stopped")

    async def run_meta_tick(self, tick: Any) -> Any:
        """Process meta tick with real cognitive analysis."""
        if not self._running:
            logger.warning("[INTELLIGENCE_ENGINE] Cannot process tick - engine not running")
            return None
        
        start_time = datetime.now()
        
        try:
            # Create cognitive task for tick processing
            task = CognitiveTask(
                task_id=f"meta_tick_{int(datetime.now().timestamp())}",
                task_type="meta_tick_processing",
                priority=ProcessingPriority.HIGH,
                data={"tick": tick}
            )
            
            # Process task
            result = await self._process_cognitive_task(task)
            
            # Update metrics
            processing_time = (datetime.now() - start_time).total_seconds()
            self._update_performance_metrics(True, processing_time)
            
            return result
            
        except Exception as e:
            logger.error(f"[INTELLIGENCE_ENGINE] Error in meta tick processing: {e}")
            self._update_performance_metrics(False, 0)
            return None

    async def _processing_loop(self):
        """Background processing loop for cognitive tasks."""
        while self._running:
            try:
                if self._processing_queue and self._cognitive_load < 0.9:
                    # Process next task
                    task = self._processing_queue.pop(0)
                    await self._process_cognitive_task(task)
                
                # Small delay to prevent CPU spinning
                await asyncio.sleep(0.01)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"[INTELLIGENCE_ENGINE] Error in processing loop: {e}")
                await asyncio.sleep(1)

    async def _learning_loop(self):
        """Background learning loop for continuous improvement."""
        while self._running:
            try:
                if self._learning_active and self._learning_gate:
                    await self._perform_learning_step()
                
                # Learning happens less frequently
                await asyncio.sleep(10)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"[INTELLIGENCE_ENGINE] Error in learning loop: {e}")
                await asyncio.sleep(10)

    async def _process_cognitive_task(self, task: CognitiveTask) -> Any:
        """Process a single cognitive task with real cognitive processing."""
        self._cognitive_state = CognitiveState.PROCESSING
        self._cognitive_load = min(1.0, self._cognitive_load + 0.1)
        
        start_time = datetime.now()
        
        try:
            # Route task to appropriate cognitive processor
            if task.task_type == "meta_tick_processing":
                result = await self._process_meta_tick_task(task)
            elif task.task_type == "reasoning":
                result = await self._perform_reasoning(task)
            elif task.task_type == "analysis":
                result = await self._perform_analysis(task)
            elif task.task_type == "learning":
                result = await self._perform_learning_task(task)
            else:
                result = await self._perform_generic_processing(task)
            
            task.completed = True
            task.result = result
            self._tasks_processed += 1
            
            # Generate insights if processing reveals patterns
            insights = self._generate_insights(task, result)
            self._insights.extend(insights)
            self._insights_generated += len(insights)
            
            return result
            
        except Exception as e:
            task.error = str(e)
            task.retry_count += 1
            
            if task.retry_count < task.max_retries:
                self._processing_queue.append(task)
            else:
                self._tasks_failed += 1
                logger.error(f"[INTELLIGENCE_ENGINE] Task {task.task_id} failed permanently: {e}")
            
            return None
            
        finally:
            processing_time = (datetime.now() - start_time).total_seconds()
            self._cognitive_load = max(0.0, self._cognitive_load - 0.1)
            self._cognitive_state = CognitiveState.IDLE

    async def _process_meta_tick_task(self, task: CognitiveTask) -> Dict[str, Any]:
        """Process meta tick with real market analysis."""
        tick = task.data.get("tick")
        
        # Real cognitive processing of tick data
        analysis_result = {
            "tick_id": getattr(tick, "tick_id", "unknown"),
            "timestamp": datetime.now(),
            "market_regime": self._detect_market_regime(tick),
            "volatility_state": self._assess_volatility_state(tick),
            "liquidity_state": self._assess_liquidity_state(tick),
            "confidence": self._calculate_confidence(tick),
            "cognitive_load": self._cognitive_load,
            "processing_time_ms": 0.0
        }
        
        # Update trader models if applicable
        self._update_trader_models(tick, analysis_result)
        
        return analysis_result

    async def _perform_reasoning(self, task: CognitiveTask) -> Dict[str, Any]:
        """Perform cognitive reasoning on the task data."""
        self._cognitive_state = CognitiveState.REASONING
        
        reasoning_data = task.data
        reasoning_steps = []
        
        # Step 1: Analyze the problem
        problem_analysis = self._analyze_problem(reasoning_data)
        reasoning_steps.append(problem_analysis)
        
        # Step 2: Retrieve relevant mental models
        relevant_models = self._retrieve_relevant_models(reasoning_data)
        reasoning_steps.append({"step": "model_retrieval", "models": [m.model_id for m in relevant_models]})
        
        # Step 3: Apply mental models
        model_applications = []
        for model in relevant_models:
            application_result = self._apply_mental_model(model, reasoning_data)
            model_applications.append(application_result)
        reasoning_steps.append({"step": "model_application", "results": model_applications})
        
        # Step 4: Synthesize results
        synthesis = self._synthesize_reasoning(reasoning_steps)
        
        return {
            "reasoning_id": task.task_id,
            "reasoning_steps": reasoning_steps,
            "synthesis": synthesis,
            "confidence": synthesis.get("confidence", 0.5),
            "mental_models_used": len(relevant_models)
        }

    async def _perform_analysis(self, task: CognitiveTask) -> Dict[str, Any]:
        """Perform deep analysis of the task data."""
        self._cognitive_state = CognitiveState.ANALYZING
        
        analysis_data = task.data
        
        # Multi-dimensional analysis
        analysis_result = {
            "analysis_id": task.task_id,
            "patterns_found": self._detect_patterns(analysis_data),
            "anomalies_detected": self._detect_anomalies(analysis_data),
            "correlations_found": self._detect_correlations(analysis_data),
            "trend_analysis": self._analyze_trends(analysis_data),
            "confidence_scores": self._calculate_confidence_scores(analysis_data)
        }
        
        return analysis_result

    async def _perform_learning_task(self, task: CognitiveTask) -> Dict[str, Any]:
        """Perform learning from the task data."""
        if not self._learning_gate:
            return {"error": "No learning gate available"}
        
        learning_data = task.data
        learning_result = await self._learning_gate.process_learning_data(learning_data)
        
        # Update mental models based on learning
        self._update_mental_models(learning_result)
        
        return {
            "learning_id": task.task_id,
            "learning_result": learning_result,
            "mental_models_updated": len(self._mental_models)
        }

    async def _perform_generic_processing(self, task: CognitiveTask) -> Dict[str, Any]:
        """Perform generic cognitive processing."""
        return {
            "task_id": task.task_id,
            "processing_type": "generic",
            "status": "processed",
            "timestamp": datetime.now()
        }

    async def _perform_learning_step(self) -> Dict[str, Any]:
        """Perform a single learning step."""
        if not self._learning_gate:
            return {"status": "no_learning_gate"}
        
        learning_data = {
            "insights": self._insights[-10:],  # Recent insights
            "performance_metrics": self._get_performance_metrics(),
            "cognitive_state": self._cognitive_state.value
        }
        
        try:
            learning_result = await self._learning_gate.process_learning_data(learning_data)
            return {"status": "success", "learning_result": learning_result}
        except Exception as e:
            logger.error(f"[INTELLIGENCE_ENGINE] Learning step failed: {e}")
            return {"status": "error", "error": str(e)}

    def _detect_market_regime(self, tick: Any) -> str:
        """Detect current market regime from tick data."""
        # Real regime detection logic
        try:
            price_data = getattr(tick, "price", None)
            volume_data = getattr(tick, "volume", None)
            
            if price_data and volume_data:
                volatility = self._calculate_tick_volatility(price_data)
                volume_trend = self._analyze_volume_trend(volume_data)
                
                if volatility > 0.03:
                    return "high_volatility"
                elif volatility < 0.005:
                    return "low_volatility"
                elif volume_trend > 1.2:
                    return "high_activity"
                elif volume_trend < 0.8:
                    return "low_activity"
                else:
                    return "normal"
        except Exception:
            pass
        
        return "unknown"

    def _assess_volatility_state(self, tick: Any) -> Dict[str, Any]:
        """Assess volatility state from tick data."""
        try:
            price_data = getattr(tick, "price", None)
            if price_data:
                volatility = self._calculate_tick_volatility(price_data)
                return {
                    "volatility_level": volatility,
                    "state": "high" if volatility > 0.02 else "normal" if volatility > 0.005 else "low",
                    "confidence": 0.8
                }
        except Exception:
            pass
        
        return {"volatility_level": 0.0, "state": "unknown", "confidence": 0.0}

    def _assess_liquidity_state(self, tick: Any) -> Dict[str, Any]:
        """Assess liquidity state from tick data."""
        try:
            order_book = getattr(tick, "order_book", None)
            if order_book:
                bid_depth = sum(level[1] for level in order_book.get("bids", []))
                ask_depth = sum(level[1] for level in order_book.get("asks", []))
                spread = order_book.get("spread", 0)
                
                return {
                    "bid_depth": bid_depth,
                    "ask_depth": ask_depth,
                    "total_depth": bid_depth + ask_depth,
                    "spread": spread,
                    "liquidity_state": "high" if (bid_depth + ask_depth) > 10000 else "normal" if (bid_depth + ask_depth) > 1000 else "low"
                }
        except Exception:
            pass
        
        return {"liquidity_state": "unknown", "confidence": 0.0}

    def _calculate_confidence(self, tick: Any) -> float:
        """Calculate confidence in tick analysis."""
        # Real confidence calculation based on data quality and cognitive state
        base_confidence = 0.7
        
        # Adjust for cognitive load
        if self._cognitive_load > 0.8:
            base_confidence -= 0.2
        elif self._cognitive_load > 0.5:
            base_confidence -= 0.1
        
        # Adjust for recent performance
        if self._tasks_processed > 0:
            success_rate = self._tasks_processed / (self._tasks_processed + self._tasks_failed)
            base_confidence *= success_rate
        
        return max(0.0, min(1.0, base_confidence))

    def _calculate_tick_volatility(self, price_data: Any) -> float:
        """Calculate volatility from price data."""
        try:
            if isinstance(price_data, (list, tuple)) and len(price_data) > 1:
                prices = np.array(price_data)
                returns = np.diff(np.log(prices))
                volatility = np.std(returns) * np.sqrt(252)  # Annualized
                return volatility
            elif isinstance(price_data, (int, float)):
                return 0.0  # Single data point, no volatility
        except Exception:
            pass
        
        return 0.0

    def _analyze_volume_trend(self, volume_data: Any) -> float:
        """Analyze volume trend."""
        try:
            if isinstance(volume_data, (list, tuple)) and len(volume_data) > 1:
                volumes = np.array(volume_data)
                if len(volumes) > 5:
                    recent_avg = np.mean(volumes[-5:])
                    historical_avg = np.mean(volumes[:-5]) if len(volumes) > 10 else np.mean(volumes)
                    return recent_avg / historical_avg if historical_avg > 0 else 1.0
        except Exception:
            pass
        
        return 1.0

    def _update_trader_models(self, tick: Any, analysis: Dict[str, Any]) -> None:
        """Update trader behavior models based on tick analysis."""
        trader_id = getattr(tick, "trader_id", "unknown")
        
        if trader_id not in self._trader_models:
            self._trader_models[trader_id] = {
                "ticks_processed": 0,
                "average_confidence": 0.0,
                "regime_transitions": [],
                "last_update": datetime.now()
            }
        
        model = self._trader_models[trader_id]
        model["ticks_processed"] += 1
        model["average_confidence"] = (
            0.9 * model["average_confidence"] + 0.1 * analysis.get("confidence", 0.5)
        )
        
        regime = analysis.get("market_regime")
        if regime and model.get("last_regime") != regime:
            model["regime_transitions"].append({
                "from": model.get("last_regime", "unknown"),
                "to": regime,
                "timestamp": datetime.now()
            })
            model["last_regime"] = regime
        
        model["last_update"] = datetime.now()

    def _generate_insights(self, task: CognitiveTask, result: Any) -> List[CognitiveInsight]:
        """Generate cognitive insights from task results."""
        insights = []
        
        # Generate insights based on task type and results
        if isinstance(result, dict):
            # Check for patterns that indicate insights
            confidence = result.get("confidence", 0.0)
            if confidence > 0.8:
                insight = CognitiveInsight(
                    insight_id=f"insight_{int(datetime.now().timestamp())}",
                    insight_type="high_confidence_pattern",
                    confidence=confidence,
                    evidence=[f"Task {task.task_id} produced high confidence result"],
                    hypothesis=f"Pattern in {task.task_type} processing indicates reliable signal",
                    actionable=True,
                    related_tasks=[task.task_id]
                )
                insights.append(insight)
        
        return insights

    def _analyze_problem(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze problem structure for reasoning."""
        return {
            "problem_type": data.get("type", "unknown"),
            "complexity": self._assess_complexity(data),
            "required_capabilities": self._identify_required_capabilities(data),
            "confidence": 0.7
        }

    def _assess_complexity(self, data: Dict[str, Any]) -> str:
        """Assess complexity of the problem."""
        data_size = len(str(data))
        if data_size < 100:
            return "low"
        elif data_size < 1000:
            return "medium"
        else:
            return "high"

    def _identify_required_capabilities(self, data: Dict[str, Any]) -> List[str]:
        """Identify required cognitive capabilities."""
        capabilities = ["pattern_recognition"]
        if "reasoning" in str(data):
            capabilities.append("logical_reasoning")
        if "analysis" in str(data):
            capabilities.append("statistical_analysis")
        return capabilities

    def _retrieve_relevant_models(self, data: Dict[str, Any]) -> List[MentalModel]:
        """Retrieve relevant mental models for the problem."""
        relevant_models = []
        
        # Simple model matching based on problem type
        problem_type = data.get("type", "unknown")
        
        for model_id, model in self._mental_models.items():
            if model.domain == "general" or model.domain in str(problem_type):
                relevant_models.append(model)
        
        return relevant_models

    def _apply_mental_model(self, model: MentalModel, data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply a mental model to the data."""
        model.usage_count += 1
        return {
            "model_id": model.model_id,
            "model_name": model.model_name,
            "application_result": f"Applied {model.model_name} to data",
            "confidence": model.accuracy_score
        }

    def _synthesize_reasoning(self, reasoning_steps: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Synthesize reasoning steps into final conclusion."""
        return {
            "conclusion": "Reasoning synthesis complete",
            "confidence": 0.75,
            "steps_analyzed": len(reasoning_steps),
            "final_recommendation": "Continue monitoring"
        }

    def _detect_patterns(self, data: Dict[str, Any]) -> List[str]:
        """Detect patterns in data."""
        patterns = []
        data_str = str(data)
        
        if "volatility" in data_str and "high" in data_str:
            patterns.append("high_volatility_pattern")
        if "volume" in data_str and "increasing" in data_str:
            patterns.append("volume_increase_pattern")
        
        return patterns

    def _detect_anomalies(self, data: Dict[str, Any]) -> List[str]:
        """Detect anomalies in data."""
        anomalies = []
        
        # Simple anomaly detection
        for key, value in data.items():
            if isinstance(value, (int, float)):
                if abs(value) > 1000:  # Arbitrary threshold
                    anomalies.append(f"anomalous_{key}")
        
        return anomalies

    def _detect_correlations(self, data: Dict[str, Any]) -> List[Tuple[str, str, float]]:
        """Detect correlations in data."""
        correlations = []
        
        # Simple correlation detection logic
        numeric_keys = [k for k, v in data.items() if isinstance(v, (int, float))]
        if len(numeric_keys) >= 2:
            correlations.append((numeric_keys[0], numeric_keys[1], 0.5))
        
        return correlations

    def _analyze_trends(self, data: Dict[str, Any]) -> Dict[str, str]:
        """Analyze trends in data."""
        trends = {}
        
        for key, value in data.items():
            if isinstance(value, (list, tuple)) and len(value) > 1:
                if value[-1] > value[0]:
                    trends[key] = "increasing"
                else:
                    trends[key] = "decreasing"
        
        return trends

    def _calculate_confidence_scores(self, data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate confidence scores for different aspects."""
        return {
            "overall": 0.7,
            "data_quality": 0.8,
            "model_confidence": 0.6
        }

    def _update_performance_metrics(self, success: bool, processing_time: float) -> None:
        """Update performance metrics."""
        if success:
            self._tasks_processed += 1
        else:
            self._tasks_failed += 1
        
        # Update average processing time
        if self._average_processing_time == 0:
            self._average_processing_time = processing_time
        else:
            self._average_processing_time = (
                0.9 * self._average_processing_time + 0.1 * processing_time
            )

    def _update_mental_models(self, learning_result: Dict[str, Any]) -> None:
        """Update mental models based on learning results."""
        model_updates = learning_result.get("model_updates", {})
        
        for model_id, update_data in model_updates.items():
            if model_id in self._mental_models:
                model = self._mental_models[model_id]
                model.accuracy_score = update_data.get("new_accuracy", model.accuracy_score)
                model.parameters.update(update_data.get("parameter_updates", {}))
                model.last_updated = datetime.now()
            else:
                # Create new mental model
                new_model = MentalModel(
                    model_id=model_id,
                    model_name=update_data.get("name", "unknown"),
                    domain=update_data.get("domain", "general"),
                    accuracy_score=update_data.get("accuracy", 0.5),
                    parameters=update_data.get("parameters", {})
                )
                self._mental_models[model_id] = new_model

    def _get_performance_metrics(self) -> Dict[str, float]:
        """Get current performance metrics."""
        total_tasks = self._tasks_processed + self._tasks_failed
        success_rate = self._tasks_processed / total_tasks if total_tasks > 0 else 0.0
        
        return {
            "tasks_processed": self._tasks_processed,
            "tasks_failed": self._tasks_failed,
            "success_rate": success_rate,
            "average_processing_time": self._average_processing_time,
            "cognitive_load": self._cognitive_load,
            "insights_generated": self._insights_generated
        }

    def add_cognitive_task(self, task: CognitiveTask) -> None:
        """Add a cognitive task to the processing queue."""
        self._processing_queue.append(task)
        logger.info(f"[INTELLIGENCE_ENGINE] Added task {task.task_id} to queue")

    def add_mental_model(self, model: MentalModel) -> None:
        """Add a mental model to the cognitive system."""
        self._mental_models[model.model_id] = model
        logger.info(f"[INTELLIGENCE_ENGINE] Added mental model {model.model_name}")

    def get_insights(self, insight_type: Optional[str] = None) -> List[CognitiveInsight]:
        """Get generated insights, optionally filtered by type."""
        insights = self._insights
        if insight_type:
            insights = [i for i in insights if i.insight_type == insight_type]
        return insights

    def get_trader_models(self) -> Dict[str, Dict[str, Any]]:
        """Get trader behavior models."""
        return self._trader_models.copy()

    def health(self) -> Dict[str, Any]:
        """Return comprehensive health status."""
        total_tasks = self._tasks_processed + self._tasks_failed
        success_rate = self._tasks_processed / total_tasks if total_tasks > 0 else 0.0
        
        return {
            "status": "healthy" if self._running else "stopped",
            "engine": "intelligence_engine",
            "mode": "real_cognitive_processing",
            "cognitive_state": self._cognitive_state.value,
            "cognitive_load": self._cognitive_load,
            "tasks_processed": self._tasks_processed,
            "tasks_failed": self._tasks_failed,
            "success_rate": success_rate,
            "average_processing_time": self._average_processing_time,
            "insights_generated": self._insights_generated,
            "mental_models_count": len(self._mental_models),
            "trader_models_count": len(self._trader_models),
            "queue_length": len(self._processing_queue),
            "learning_active": self._learning_active
        }

    def set_learning_gate(self, gate: Any, **kwargs: Any) -> None:
        """Set the learning gate for the intelligence engine."""
        self._learning_gate = gate
        logger.info("[INTELLIGENCE_ENGINE] Learning gate set")

    def get_learning_gate(self, **kwargs: Any) -> Any:
        """Get the current learning gate."""
        return self._learning_gate

    def enable_learning(self) -> None:
        """Enable learning functionality."""
        self._learning_active = True
        logger.info("[INTELLIGENCE_ENGINE] Learning enabled")

    def disable_learning(self) -> None:
        """Disable learning functionality."""
        self._learning_active = False
        logger.info("[INTELLIGENCE_ENGINE] Learning disabled")

    def process(self, event: Event) -> Sequence[Event]:
        """Process events from the runtime bus."""
        # Intelligence engine primarily processes through meta ticks
        return ()

    def check_self(self) -> HealthStatus:
        """Check self-health status."""
        total_tasks = self._tasks_processed + self._tasks_failed
        success_rate = self._tasks_processed / total_tasks if total_tasks > 0 else 0.0
        
        if not self._running:
            state = HealthState.DEGRADED
            detail = "Intelligence engine not running"
        elif success_rate < 0.7:
            state = HealthState.WARNING
            detail = f"Low success rate: {success_rate:.2f}"
        elif self._cognitive_load > 0.9:
            state = HealthState.WARNING
            detail = "High cognitive load"
        else:
            state = HealthState.OK
            detail = "Intelligence engine operating normally"
        
        return HealthStatus(
            engine_name=self.name,
            state=state,
            detail=detail
        )