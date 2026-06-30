"""
DIX VISION ML Training Service

Provides distributed training, hyperparameter optimization, model selection,
and training automation for enhanced ML capabilities.
"""

from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple
from collections import defaultdict, deque
from datetime import datetime, timedelta
import statistics
import random

from runtime.event_bus import EventBus, Event, EventType, get_event_bus
from runtime.service_manager import Service, ServiceState, ServiceHealth

logger = logging.getLogger(__name__)


class TrainingStatus(Enum):
    """Training job status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class OptimizationStrategy(Enum):
    """Hyperparameter optimization strategies."""
    GRID_SEARCH = "grid_search"
    RANDOM_SEARCH = "random_search"
    BAYESIAN = "bayesian"
    GENETIC = "genetic"


@dataclass
class TrainingJob:
    """Training job configuration."""
    job_id: str
    model_name: str
    dataset: str
    hyperparameters: Dict[str, Any]
    epochs: int = 100
    batch_size: int = 32
    distributed: bool = False
    workers: int = 1
    status: TrainingStatus = TrainingStatus.PENDING
    started_at: float = 0.0
    completed_at: Optional[float] = None
    metrics: Dict[str, float] = field(default_factory=dict)
    artifacts: List[str] = field(default_factory=list)
    error_message: str = ""


@dataclass
class HyperparameterOptimization:
    """Hyperparameter optimization configuration."""
    optimization_id: str
    model_name: str
    parameter_space: Dict[str, Tuple[Any, Any]]  # parameter: (min, max)
    strategy: OptimizationStrategy
    max_iterations: int = 100
    objective: str = "accuracy"  # metric to optimize
    status: TrainingStatus = TrainingStatus.PENDING
    best_parameters: Dict[str, Any] = field(default_factory=dict)
    best_score: float = 0.0
    history: List[Dict[str, Any]] = field(default_factory=list)


class MLTrainingService(Service):
    """ML training service as per Runtime Specification."""
    
    # Service dependencies
    DEPENDENCIES = []
    
    def __init__(self):
        super().__init__("ml_training_service")
        self._training_jobs: Dict[str, TrainingJob] = {}
        self._optimizations: Dict[str, HyperparameterOptimization] = {}
        self._job_queue: deque = deque(maxlen=100)
        self._training_history: deque = deque(maxlen=1000)
        self._lock = threading.Lock()
        self._max_concurrent_jobs = 4
        self._running_jobs: set = set()
        self._auto_train_enabled = False
        
    def init(self, event_bus: EventBus, config: Dict[str, Any]) -> bool:
        """Initialize the ML training service."""
        try:
            self.event_bus = event_bus
            self.state = ServiceState.INITIALIZING
            
            # Load configuration
            training_config = config.get("ml_training", {})
            self._max_concurrent_jobs = training_config.get("max_concurrent_jobs", 4)
            self._auto_train_enabled = training_config.get("auto_train", False)
            
            logger.info("ML Training Service initialized")
            return True
        except Exception as e:
            logger.error(f"ML Training Service initialization failed: {e}")
            self.state = ServiceState.ERROR
            return False
    
    def start(self) -> bool:
        """Start the ML training service."""
        try:
            self.state = ServiceState.STARTING
            
            # Start job processor
            self._start_job_processor()
            
            # Start optimization processor
            self._start_optimization_processor()
            
            self.state = ServiceState.RUNNING
            self.emit_event(str(EventType.SERVICE_START), {"service": self.name})
            logger.info("ML Training Service started")
            return True
        except Exception as e:
            logger.error(f"ML Training Service start failed: {e}")
            self.state = ServiceState.ERROR
            self.emit_event(str(EventType.SERVICE_CRASH), {"service": self.name, "error": str(e)})
            return False
    
    def stop(self) -> bool:
        """Stop the ML training service."""
        try:
            self.state = ServiceState.STOPPING
            self._auto_train_enabled = False
            
            # Wait for running jobs to complete
            while self._running_jobs:
                time.sleep(0.1)
            
            self.state = ServiceState.STOPPED
            self.emit_event(str(EventType.SERVICE_STOP), {"service": self.name})
            logger.info("ML Training Service stopped")
            return True
        except Exception as e:
            logger.error(f"ML Training Service stop failed: {e}")
            self.state = ServiceState.ERROR
            return False
    
    def health(self) -> ServiceHealth:
        """Get ML training service health."""
        return ServiceHealth(
            service=self.name,
            state=self.state,
            healthy=self.state == ServiceState.RUNNING,
            message=f"ML Training Service - {len(self._training_jobs)} training jobs",
            details={
                "total_jobs": len(self._training_jobs),
                "running_jobs": len(self._running_jobs),
                "queued_jobs": len(self._job_queue),
                "completed_jobs": sum(1 for j in self._training_jobs.values() if j.status == TrainingStatus.COMPLETED),
                "failed_jobs": sum(1 for j in self._training_jobs.values() if j.status == TrainingStatus.FAILED),
                "optimizations": len(self._optimizations)
            },
            timestamp=time.time()
        )
    
    def create_training_job(self, job: TrainingJob) -> bool:
        """Create a new training job."""
        with self._lock:
            if job.job_id in self._training_jobs:
                logger.error(f"Training job {job.job_id} already exists")
                return False
            
            self._training_jobs[job.job_id] = job
            self._job_queue.append(job.job_id)
            
            logger.info(f"Created training job: {job.job_id}")
            return True
    
    def cancel_training_job(self, job_id: str) -> bool:
        """Cancel a training job."""
        with self._lock:
            job = self._training_jobs.get(job_id)
            if not job:
                return False
            
            if job.status == TrainingStatus.RUNNING:
                job.status = TrainingStatus.CANCELLED
                job.completed_at = time.time()
                self._running_jobs.discard(job_id)
                
                logger.info(f"Cancelled training job: {job_id}")
                return True
            
            return False
    
    def start_hyperparameter_optimization(self, optimization: HyperparameterOptimization) -> bool:
        """Start hyperparameter optimization."""
        with self._lock:
            if optimization.optimization_id in self._optimizations:
                logger.error(f"Optimization {optimization.optimization_id} already exists")
                return False
            
            self._optimizations[optimization.optimization_id] = optimization
            optimization.status = TrainingStatus.RUNNING
            
            # Start optimization in background
            self._run_optimization_async(optimization)
            
            logger.info(f"Started hyperparameter optimization: {optimization.optimization_id}")
            return True
    
    def get_training_job(self, job_id: str) -> Optional[TrainingJob]:
        """Get training job details."""
        with self._lock:
            return self._training_jobs.get(job_id)
    
    def get_training_jobs(self, status: TrainingStatus = None) -> List[TrainingJob]:
        """Get training jobs, optionally filtered by status."""
        with self._lock:
            jobs = list(self._training_jobs.values())
            
            if status:
                jobs = [j for j in jobs if j.status == status]
            
            return jobs
    
    def get_optimization(self, optimization_id: str) -> Optional[HyperparameterOptimization]:
        """Get optimization details."""
        with self._lock:
            return self._optimizations.get(optimization_id)
    
    def get_training_stats(self) -> Dict[str, Any]:
        """Get training statistics."""
        with self._lock:
            total_jobs = len(self._training_jobs)
            completed = sum(1 for j in self._training_jobs.values() if j.status == TrainingStatus.COMPLETED)
            failed = sum(1 for j in self._training_jobs.values() if j.status == TrainingStatus.FAILED)
            
            # Calculate average training time
            completed_jobs = [j for j in self._training_jobs.values() if j.completed_at and j.started_at]
            avg_duration = statistics.mean([j.completed_at - j.started_at for j in completed_jobs]) if completed_jobs else 0.0
            
            # Calculate average metrics
            if completed_jobs:
                avg_accuracy = statistics.mean([j.metrics.get("accuracy", 0.0) for j in completed_jobs])
                avg_loss = statistics.mean([j.metrics.get("loss", 0.0) for j in completed_jobs])
            else:
                avg_accuracy = 0.0
                avg_loss = 0.0
            
            return {
                "total_jobs": total_jobs,
                "completed": completed,
                "failed": failed,
                "success_rate": completed / total_jobs if total_jobs > 0 else 0.0,
                "avg_duration": avg_duration,
                "avg_accuracy": avg_accuracy,
                "avg_loss": avg_loss,
                "running_jobs": len(self._running_jobs),
                "queued_jobs": len(self._job_queue)
            }
    
    def _run_training_job_async(self, job: TrainingJob) -> None:
        """Run training job in background."""
        def train():
            try:
                job.status = TrainingStatus.RUNNING
                job.started_at = time.time()
                
                # Simulate training (in production, this would call actual ML framework)
                for epoch in range(job.epochs):
                    if job.status == TrainingStatus.CANCELLED:
                        break
                    
                    # Simulate training step
                    time.sleep(0.1)  # Simulate training time
                    
                    # Update metrics
                    job.metrics["loss"] = max(0.1, job.metrics.get("loss", 1.0) * 0.95)
                    job.metrics["accuracy"] = min(0.99, job.metrics.get("accuracy", 0.0) + 0.01)
                    
                    if epoch % 10 == 0:
                        logger.info(f"Job {job.job_id} epoch {epoch}: loss={job.metrics['loss']:.4f}, accuracy={job.metrics['accuracy']:.4f}")
                
                job.status = TrainingStatus.COMPLETED
                job.completed_at = time.time()
                job.artifacts.append(f"model_{job.job_id}.pkl")
                
                logger.info(f"Training job completed: {job.job_id}")
                
            except Exception as e:
                job.status = TrainingStatus.FAILED
                job.completed_at = time.time()
                job.error_message = str(e)
                logger.error(f"Training job failed: {job.job_id} - {e}")
            
            finally:
                with self._lock:
                    self._running_jobs.discard(job.job_id)
                    self._training_history.append(job)
        
        thread = threading.Thread(target=train, daemon=True)
        thread.start()
    
    def _run_optimization_async(self, optimization: HyperparameterOptimization) -> None:
        """Run hyperparameter optimization in background."""
        def optimize():
            try:
                optimization.status = TrainingStatus.RUNNING
                
                for iteration in range(optimization.max_iterations):
                    if optimization.status == TrainingStatus.CANCELLED:
                        break
                    
                    # Generate hyperparameters based on strategy
                    if optimization.strategy == OptimizationStrategy.RANDOM_SEARCH:
                        params = {
                            key: random.uniform(min_val, max_val) if isinstance(min_val, (int, float))
                            else random.choice([min_val, max_val])
                            for key, (min_val, max_val) in optimization.parameter_space.items()
                        }
                    elif optimization.strategy == OptimizationStrategy.GRID_SEARCH:
                        # Simplified grid search
                        params = {
                            key: min_val + (max_val - min_val) * (iteration / optimization.max_iterations)
                            for key, (min_val, max_val) in optimization.parameter_space.items()
                        }
                    else:
                        params = {
                            key: random.uniform(min_val, max_val) if isinstance(min_val, (int, float))
                            else random.choice([min_val, max_val])
                            for key, (min_val, max_val) in optimization.parameter_space.items()
                        }
                    
                    # Simulate training with these parameters
                    score = random.uniform(0.7, 0.95)  # Simulated accuracy
                    
                    optimization.history.append({
                        "iteration": iteration,
                        "parameters": params,
                        "score": score
                    })
                    
                    # Update best parameters
                    if score > optimization.best_score:
                        optimization.best_score = score
                        optimization.best_parameters = params
                    
                    logger.info(f"Optimization {optimization.optimization_id} iteration {iteration}: score={score:.4f}")
                
                optimization.status = TrainingStatus.COMPLETED
                logger.info(f"Hyperparameter optimization completed: {optimization.optimization_id}")
                
            except Exception as e:
                optimization.status = TrainingStatus.FAILED
                logger.error(f"Optimization failed: {optimization.optimization_id} - {e}")
        
        thread = threading.Thread(target=optimize, daemon=True)
        thread.start()
    
    def _start_job_processor(self) -> None:
        """Start background job processor."""
        def process_jobs():
            while self.state == ServiceState.RUNNING:
                try:
                    if self._job_queue and len(self._running_jobs) < self._max_concurrent_jobs:
                        job_id = self._job_queue.popleft()
                        
                        with self._lock:
                            job = self._training_jobs.get(job_id)
                            if job and job.status == TrainingStatus.PENDING:
                                self._running_jobs.add(job_id)
                                self._run_training_job_async(job)
                    
                    time.sleep(1)  # Process jobs every second
                except Exception as e:
                    logger.error(f"Job processor error: {e}")
                    time.sleep(5)
        
        thread = threading.Thread(target=process_jobs, daemon=True)
        thread.start()
        logger.info("Job processor started")
    
    def _start_optimization_processor(self) -> None:
        """Start background optimization processor."""
        def process_optimizations():
            while self.state == ServiceState.RUNNING:
                try:
                    # Check for completed optimizations
                    with self._lock:
                        for opt_id, opt in self._optimizations.items():
                            if opt.status == TrainingStatus.COMPLETED:
                                # Create training job with best parameters
                                best_job = TrainingJob(
                                    job_id=f"{opt_id}_best",
                                    model_name=opt.model_name,
                                    dataset="default",
                                    hyperparameters=opt.best_parameters,
                                    epochs=100
                                )
                                self.create_training_job(best_job)
                                del self._optimizations[opt_id]
                    
                    time.sleep(60)  # Check every minute
                except Exception as e:
                    logger.error(f"Optimization processor error: {e}")
                    time.sleep(30)
        
        thread = threading.Thread(target=process_optimizations, daemon=True)
        thread.start()
        logger.info("Optimization processor started")


# Global instance
_ml_training_service: Optional[MLTrainingService] = None


def get_ml_training_service() -> MLTrainingService:
    """Get global ML training service instance."""
    global _ml_training_service
    if _ml_training_service is None:
        _ml_training_service = MLTrainingService()
    return _ml_training_service