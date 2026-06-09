"""
Task Scheduler - Async task scheduling and execution
"""

import asyncio
import logging
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field


@dataclass
class Task:
    """Represents a scheduled task."""
    id: str
    name: str
    func: Callable
    args: tuple = field(default_factory=tuple)
    kwargs: dict = field(default_factory=dict)
    interval: Optional[float] = None
    delay: Optional[float] = None
    priority: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    next_run: Optional[datetime] = None
    running: bool = False
    completed: bool = False
    error_count: int = 0


class TaskScheduler:
    """
    Async task scheduler for agent runtime.
    
    Manages periodic tasks, delayed execution, and priority-based
    task scheduling with comprehensive error handling and retry logic.
    """
    
    def __init__(self, event_bus):
        """
        Initialize the task scheduler.
        
        Args:
            event_bus: Event bus for task notifications
        """
        self.event_bus = event_bus
        self.tasks: Dict[str, Task] = {}
        self.task_queue: asyncio.PriorityQueue = asyncio.PriorityQueue()
        self.is_running = False
        self.worker_task: Optional[asyncio.Task] = None
        
        self.logger = logging.getLogger(__name__)
        
    async def initialize(self) -> None:
        """Initialize the scheduler."""
        self.logger.info("Task Scheduler initialized")
        
    async def start(self) -> None:
        """Start the scheduler worker."""
        self.is_running = True
        self.worker_task = asyncio.create_task(self._worker())
        self.logger.info("Task Scheduler started")
        
    async def stop(self) -> None:
        """Stop the scheduler worker."""
        self.is_running = False
        if self.worker_task:
            self.worker_task.cancel()
            try:
                await self.worker_task
            except asyncio.CancelledError:
                pass
        self.logger.info("Task Scheduler stopped")
        
    async def schedule(
        self,
        task_id: str,
        name: str,
        func: Callable,
        args: tuple = (),
        kwargs: dict = None,
        interval: Optional[float] = None,
        delay: Optional[float] = None,
        priority: int = 0,
        metadata: Dict[str, Any] = None,
    ) -> None:
        """
        Schedule a task for execution.
        
        Args:
            task_id: Unique task identifier
            name: Task name
            func: Function to execute
            args: Positional arguments
            kwargs: Keyword arguments
            interval: Interval in seconds for periodic tasks
            delay: Delay in seconds before first execution
            priority: Task priority (higher = more important)
            metadata: Additional task metadata
        """
        if kwargs is None:
            kwargs = {}
        if metadata is None:
            metadata = {}
            
        task = Task(
            id=task_id,
            name=name,
            func=func,
            args=args,
            kwargs=kwargs,
            interval=interval,
            delay=delay,
            priority=priority,
            metadata=metadata,
        )
        
        # Calculate next run time
        if delay:
            task.next_run = datetime.utcnow() + timedelta(seconds=delay)
        else:
            task.next_run = datetime.utcnow()
            
        self.tasks[task_id] = task
        
        # Emit task scheduled event
        await self.event_bus.emit("task.scheduled", {
            "task_id": task_id,
            "name": name,
            "next_run": task.next_run.isoformat(),
        })
        
        self.logger.info(f"Scheduled task: {name} (id: {task_id})")
        
    async def cancel(self, task_id: str) -> None:
        """
        Cancel a scheduled task.
        
        Args:
            task_id: Task identifier
        """
        if task_id in self.tasks:
            del self.tasks[task_id]
            await self.event_bus.emit("task.cancelled", {"task_id": task_id})
            self.logger.info(f"Cancelled task: {task_id}")
            
    async def get_task(self, task_id: str) -> Optional[Task]:
        """
        Get a task by ID.
        
        Args:
            task_id: Task identifier
            
        Returns:
            Task instance or None
        """
        return self.tasks.get(task_id)
        
    async def get_all_tasks(self) -> List[Task]:
        """
        Get all tasks.
        
        Returns:
            List of all tasks
        """
        return list(self.tasks.values())
        
    async def _worker(self) -> None:
        """Main worker loop for task execution."""
        while self.is_running:
            try:
                # Check for ready tasks
                now = datetime.utcnow()
                ready_tasks = [
                    task for task in self.tasks.values()
                    if not task.completed and task.next_run and task.next_run <= now
                ]
                
                # Sort by priority
                ready_tasks.sort(key=lambda t: t.priority, reverse=True)
                
                for task in ready_tasks:
                    if not task.running:
                        await self._execute_task(task)
                        
                await asyncio.sleep(0.1)  # Small sleep to prevent busy loop
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Worker error: {e}")
                await asyncio.sleep(1)
                
    async def _execute_task(self, task: Task) -> None:
        """
        Execute a single task.
        
        Args:
            task: Task to execute
        """
        task.running = True
        
        try:
            await self.event_bus.emit("task.started", {
                "task_id": task.id,
                "name": task.name,
            })
            
            # Execute the task
            if asyncio.iscoroutinefunction(task.func):
                result = await task.func(*task.args, **task.kwargs)
            else:
                result = task.func(*task.args, **task.kwargs)
                
            await self.event_bus.emit("task.completed", {
                "task_id": task.id,
                "name": task.name,
                "result": str(result),
            })
            
            # Handle periodic tasks
            if task.interval:
                task.next_run = datetime.utcnow() + timedelta(seconds=task.interval)
                task.running = False
            else:
                task.completed = True
                if task.id in self.tasks:
                    del self.tasks[task.id]
                    
        except Exception as e:
            task.error_count += 1
            self.logger.error(f"Task execution error: {task.name} - {e}")
            
            await self.event_bus.emit("task.failed", {
                "task_id": task.id,
                "name": task.name,
                "error": str(e),
                "error_count": task.error_count,
            })
            
            # Reschedule periodic tasks
            if task.interval:
                task.next_run = datetime.utcnow() + timedelta(seconds=task.interval)
                task.running = False
            else:
                task.completed = True
                if task.id in self.tasks:
                    del self.tasks[task.id]
                    
        finally:
            task.running = False
