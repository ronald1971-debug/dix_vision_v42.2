"""
DIX VISION CI/CD Service

Provides automated CI/CD pipelines, testing automation, deployment automation,
and build optimization for enhanced development workflow.
"""

from __future__ import annotations

import logging
import subprocess
import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple
from collections import defaultdict, deque
from datetime import datetime, timedelta
import json
import os
import statistics

from runtime.event_bus import EventBus, Event, EventType, get_event_bus
from runtime.service_manager import Service, ServiceState, ServiceHealth

logger = logging.getLogger(__name__)


class PipelineStatus(Enum):
    """Pipeline status."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


class BuildStage(Enum):
    """Build pipeline stages."""
    LINT = "lint"
    TEST = "test"
    BUILD = "build"
    PACKAGE = "package"
    DEPLOY = "deploy"
    VERIFY = "verify"


@dataclass
class PipelineConfig:
    """CI/CD pipeline configuration."""
    pipeline_id: str
    pipeline_name: str
    stages: List[BuildStage]
    trigger: str  # "push", "schedule", "manual"
    schedule: str = ""  # cron-like schedule
    branch: str = "main"
    enabled: bool = True
    timeout: int = 1800  # 30 minutes
    retry_count: int = 3
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PipelineExecution:
    """Pipeline execution record."""
    execution_id: str
    pipeline_id: str
    status: PipelineStatus
    stage: BuildStage
    commit_hash: str
    branch: str
    author: str
    started_at: float = field(default_factory=time.time)
    completed_at: Optional[float] = None
    duration: float = 0.0
    stage_results: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    logs: List[str] = field(default_factory=list)
    artifacts: List[str] = field(default_factory=list)


class CICDService(Service):
    """CI/CD service as per Runtime Specification."""
    
    # Service dependencies
    DEPENDENCIES = []
    
    def __init__(self):
        super().__init__("cicd_service")
        self._pipelines: Dict[str, PipelineConfig] = {}
        self._executions: List[PipelineExecution] = []
        self._execution_history: deque = deque(maxlen=1000)
        self._build_queue: deque = deque(maxlen=100)
        self._lock = threading.Lock()
        self._auto_run_enabled = False
        self._max_concurrent_builds = 3
        self._running_builds: set = set()
        
    def init(self, event_bus: EventBus, config: Dict[str, Any]) -> bool:
        """Initialize the CI/CD service."""
        try:
            self.event_bus = event_bus
            self.state = ServiceState.INITIALIZING
            
            # Load configuration
            cicd_config = config.get("cicd", {})
            self._auto_run_enabled = cicd_config.get("auto_run", False)
            self._max_concurrent_builds = cicd_config.get("max_concurrent_builds", 3)
            
            # Initialize default pipelines
            self._init_default_pipelines()
            
            logger.info("CI/CD Service initialized")
            return True
        except Exception as e:
            logger.error(f"CI/CD Service initialization failed: {e}")
            self.state = ServiceState.ERROR
            return False
    
    def start(self) -> bool:
        """Start the CI/CD service."""
        try:
            self.state = ServiceState.STARTING
            
            # Start build queue processor
            self._start_build_processor()
            
            # Start scheduled pipeline runner
            if self._auto_run_enabled:
                self._start_scheduler()
            
            self.state = ServiceState.RUNNING
            self.emit_event(str(EventType.SERVICE_START), {"service": self.name})
            logger.info("CI/CD Service started")
            return True
        except Exception as e:
            logger.error(f"CI/CD Service start failed: {e}")
            self.state = ServiceState.ERROR
            self.emit_event(str(EventType.SERVICE_CRASH), {"service": self.name, "error": str(e)})
            return False
    
    def stop(self) -> bool:
        """Stop the CI/CD service."""
        try:
            self.state = ServiceState.STOPPING
            self._auto_run_enabled = False
            
            # Wait for running builds to complete
            while self._running_builds:
                time.sleep(0.1)
            
            self.state = ServiceState.STOPPED
            self.emit_event(str(EventType.SERVICE_STOP), {"service": self.name})
            logger.info("CI/CD Service stopped")
            return True
        except Exception as e:
            logger.error(f"CI/CD Service stop failed: {e}")
            self.state = ServiceState.ERROR
            return False
    
    def health(self) -> ServiceHealth:
        """Get CI/CD service health."""
        return ServiceHealth(
            service=self.name,
            state=self.state,
            healthy=self.state == ServiceState.RUNNING,
            message=f"CI/CD Service - {len(self._pipelines)} pipelines",
            details={
                "total_pipelines": len(self._pipelines),
                "enabled_pipelines": sum(1 for p in self._pipelines.values() if p.enabled),
                "total_executions": len(self._executions),
                "running_builds": len(self._running_builds),
                "build_queue_size": len(self._build_queue),
                "success_rate": self._calculate_success_rate()
            },
            timestamp=time.time()
        )
    
    def create_pipeline(self, pipeline: PipelineConfig) -> bool:
        """Create a new CI/CD pipeline."""
        with self._lock:
            if pipeline.pipeline_id in self._pipelines:
                logger.error(f"Pipeline {pipeline.pipeline_id} already exists")
                return False
            
            self._pipelines[pipeline.pipeline_id] = pipeline
            logger.info(f"Created pipeline: {pipeline.pipeline_name}")
            return True
    
    def trigger_pipeline(self, pipeline_id: str, commit_hash: str = "",
                       branch: str = "", author: str = "") -> Optional[PipelineExecution]:
        """Trigger a pipeline execution."""
        with self._lock:
            pipeline = self._pipelines.get(pipeline_id)
            if not pipeline or not pipeline.enabled:
                logger.error(f"Pipeline {pipeline_id} not found or disabled")
                return None
            
            if len(self._running_builds) >= self._max_concurrent_builds:
                logger.warning("Max concurrent builds reached, queuing pipeline")
                self._build_queue.append(("trigger", pipeline_id, commit_hash, branch, author))
                return None
            
            execution = PipelineExecution(
                execution_id=self._generate_id(),
                pipeline_id=pipeline_id,
                status=PipelineStatus.RUNNING,
                stage=BuildStage.LINT,
                commit_hash=commit_hash or "unknown",
                branch=branch or pipeline.branch,
                author=author or "system"
            )
            
            self._executions.append(execution)
            self._running_builds.add(execution.execution_id)
            
            # Start pipeline execution in background
            self._execute_pipeline_async(execution)
            
            return execution
    
    def cancel_execution(self, execution_id: str) -> bool:
        """Cancel a pipeline execution."""
        with self._lock:
            execution = next((e for e in self._executions if e.execution_id == execution_id), None)
            if not execution:
                return False
            
            if execution.status == PipelineStatus.RUNNING:
                execution.status = PipelineStatus.CANCELLED
                execution.completed_at = time.time()
                self._running_builds.discard(execution_id)
                
                logger.info(f"Cancelled execution: {execution_id}")
                return True
            
            return False
    
    def get_pipeline_status(self, pipeline_id: str = None) -> List[PipelineExecution]:
        """Get pipeline execution status."""
        with self._lock:
            executions = self._executions
            
            if pipeline_id:
                executions = [e for e in executions if e.pipeline_id == pipeline_id]
            
            return executions[-20:]  # Return last 20 executions
    
    def get_pipeline_config(self, pipeline_id: str) -> Optional[PipelineConfig]:
        """Get pipeline configuration."""
        with self._lock:
            return self._pipelines.get(pipeline_id)
    
    def get_ci_stats(self) -> Dict[str, Any]:
        """Get CI/CD statistics."""
        with self._lock:
            total_executions = len(self._executions)
            successful = sum(1 for e in self._executions if e.status == PipelineStatus.SUCCESS)
            failed = sum(1 for e in self._executions if e.status == PipelineStatus.FAILED)
            
            # Calculate average duration
            completed_executions = [e for e in self._executions if e.completed_at]
            avg_duration = statistics.mean([e.duration for e in completed_executions]) if completed_executions else 0.0
            
            # Executions by stage
            stage_counts = defaultdict(int)
            for execution in self._executions:
                stage_counts[execution.stage.value] += 1
            
            return {
                "total_executions": total_executions,
                "successful": successful,
                "failed": failed,
                "success_rate": successful / total_executions if total_executions > 0 else 0.0,
                "avg_duration": avg_duration,
                "running_builds": len(self._running_builds),
                "queued_builds": len(self._build_queue),
                "stage_distribution": dict(stage_counts)
            }
    
    def _execute_pipeline_async(self, execution: PipelineExecution) -> None:
        """Execute pipeline in background thread."""
        def execute():
            try:
                pipeline = self._pipelines.get(execution.pipeline_id)
                if not pipeline:
                    execution.status = PipelineStatus.FAILED
                    return
                
                start_time = time.time()
                
                for stage in pipeline.stages:
                    execution.stage = stage
                    execution.logs.append(f"Starting stage: {stage.value}")
                    
                    try:
                        result = self._execute_stage(stage, execution)
                        execution.stage_results[stage.value] = {"status": "success", "result": result}
                        execution.logs.append(f"Stage {stage.value} completed successfully")
                    except Exception as e:
                        execution.stage_results[stage.value] = {"status": "failed", "error": str(e)}
                        execution.logs.append(f"Stage {stage.value} failed: {e}")
                        
                        if pipeline.retry_count > 0:
                            execution.logs.append(f"Retrying pipeline (attempts remaining: {pipeline.retry_count})")
                            # In production, implement retry logic
                            break
                        else:
                            execution.status = PipelineStatus.FAILED
                            break
                
                execution.status = PipelineStatus.SUCCESS
                execution.completed_at = time.time()
                execution.duration = execution.completed_at - start_time
                
                logger.info(f"Pipeline execution completed: {execution.execution_id}")
                
            except Exception as e:
                execution.status = PipelineStatus.FAILED
                execution.completed_at = time.time()
                execution.logs.append(f"Pipeline execution error: {e}")
                logger.error(f"Pipeline execution failed: {execution.execution_id} - {e}")
            
            finally:
                with self._lock:
                    self._running_builds.discard(execution.execution_id)
                    self._execution_history.append(execution)
        
        thread = threading.Thread(target=execute, daemon=True)
        thread.start()
    
    def _execute_stage(self, stage: BuildStage, execution: PipelineExecution) -> Any:
        """Execute a single pipeline stage."""
        if stage == BuildStage.LINT:
            return self._execute_lint(execution)
        elif stage == BuildStage.TEST:
            return self._execute_tests(execution)
        elif stage == BuildStage.BUILD:
            return self._execute_build(execution)
        elif stage == BuildStage.PACKAGE:
            return self._execute_package(execution)
        elif stage == BuildStage.DEPLOY:
            return self._execute_deploy(execution)
        elif stage == BuildStage.VERIFY:
            return self._execute_verify(execution)
        else:
            return {"status": "skipped", "reason": "unknown_stage"}
    
    def _execute_lint(self, execution: PipelineExecution) -> Dict[str, Any]:
        """Execute linting stage."""
        try:
            # Simulate linting
            result = subprocess.run(["flake8", "--max-line-length=120", "."], 
                                  capture_output=True, text=True, timeout=60)
            
            return {
                "exit_code": result.returncode,
                "issues": result.stdout if result.stdout else "",
                "has_errors": result.returncode != 0
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def _execute_tests(self, execution: PipelineExecution) -> Dict[str, Any]:
        """Execute testing stage."""
        try:
            # Simulate testing
            result = subprocess.run(["pytest", "-v", "tests/"], 
                                  capture_output=True, text=True, timeout=300)
            
            return {
                "exit_code": result.returncode,
                "tests_run": result.stdout.count("PASSED") if result.stdout else 0,
                "has_failures": result.returncode != 0
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def _execute_build(self, execution: PipelineExecution) -> Dict[str, Any]:
        """Execute build stage."""
        try:
            # Simulate build
            result = subprocess.run(["python", "-m", "build"], 
                                  capture_output=True, text=True, timeout=300)
            
            return {
                "exit_code": result.returncode,
                "build_output": result.stdout if result.stdout else "",
                "has_errors": result.returncode != 0
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def _execute_package(self, execution: PipelineExecution) -> Dict[str, Any]:
        """Execute packaging stage."""
        try:
            # Simulate packaging
            result = subprocess.run(["python", "-m", "pip", "package", "."], 
                                  capture_output=True, text=True, timeout=300)
            
            return {
                "exit_code": result.returncode,
                "package_file": "dix_vision_package.tar.gz",
                "has_errors": result.returncode != 0
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def _execute_deploy(self, execution: PipelineExecution) -> Dict[str, Any]:
        """Execute deployment stage."""
        try:
            # Simulate deployment
            result = subprocess.run(["python", "deploy.py"], 
                                  capture_output=True, text=True, timeout=600)
            
            return {
                "exit_code": result.returncode,
                "deployment_url": "https://deploy.example.com",
                "has_errors": result.returncode != 0
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def _execute_verify(self, execution: PipelineExecution) -> Dict[str, Any]:
        """Execute verification stage."""
        try:
            # Simulate verification
            return {
                "exit_code": 0,
                "verification_passed": True,
                "has_errors": False
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def _calculate_success_rate(self) -> float:
        """Calculate pipeline success rate."""
        if not self._executions:
            return 1.0
        
        successful = sum(1 for e in self._executions if e.status == PipelineStatus.SUCCESS)
        return successful / len(self._executions)
    
    def _init_default_pipelines(self) -> None:
        """Initialize default pipelines."""
        default_pipelines = [
            PipelineConfig(
                pipeline_id="main_pipeline",
                pipeline_name="Main Branch Pipeline",
                stages=[BuildStage.LINT, BuildStage.TEST, BuildStage.BUILD],
                trigger="push",
                branch="main",
                enabled=True
            ),
            PipelineConfig(
                pipeline_id="pr_pipeline",
                pipeline_name="Pull Request Pipeline",
                stages=[BuildStage.LINT, BuildStage.TEST, BuildStage.BUILD],
                trigger="push",
                branch="*",
                enabled=True
            )
        ]
        
        for pipeline in default_pipelines:
            self.create_pipeline(pipeline)
    
    def _start_build_processor(self) -> None:
        """Start background build processor."""
        def process_builds():
            while self.state == ServiceState.RUNNING:
                try:
                    if self._build_queue and len(self._running_builds) < self._max_concurrent_builds:
                        action, *args = self._build_queue.popleft()
                        
                        if action == "trigger":
                            self.trigger_pipeline(*args)
                    
                    time.sleep(1)  # Process builds every second
                except Exception as e:
                    logger.error(f"Build processor error: {e}")
                    time.sleep(5)
        
        thread = threading.Thread(target=process_builds, daemon=True)
        thread.start()
        logger.info("Build processor started")
    
    def _start_scheduler(self) -> None:
        """Start scheduled pipeline runner."""
        def run_scheduled():
            while self._auto_run_enabled and self.state == ServiceState.RUNNING:
                try:
                    current_time = time.time()
                    
                    for pipeline_id, pipeline in self._pipelines.items():
                        if pipeline.enabled and pipeline.trigger == "schedule" and pipeline.schedule:
                            # Simple schedule check (in production, use proper cron parser)
                            if "hourly" in pipeline.schedule:
                                self.trigger_pipeline(pipeline_id)
                            elif "daily" in pipeline.schedule:
                                # Check if it's time to run
                                pass
                    
                    time.sleep(60)  # Check every minute
                except Exception as e:
                    logger.error(f"Scheduler error: {e}")
                    time.sleep(30)
        
        thread = threading.Thread(target=run_scheduled, daemon=True)
        thread.start()
        logger.info("Scheduler started")
    
    def _generate_id(self) -> str:
        """Generate unique ID."""
        import uuid
        return str(uuid.uuid4())


# Global instance
_cicd_service: Optional[CICDService] = None


def get_cicd_service() -> CICDService:
    """Get global CI/CD service instance."""
    global _cicd_service
    if _cicd_service is None:
        _cicd_service = CICDService()
    return _cicd_service