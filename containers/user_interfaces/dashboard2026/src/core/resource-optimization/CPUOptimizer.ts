/**
 * CPU Optimization System
 * DIX VISION v42.2 - Phase 2: Resource Optimization
 * 
 * Production-grade CPU optimization with Web Worker pools,
 * task scheduling, throttling, and load balancing.
 */

interface WorkerTask {
  id: string;
  type: string;
  data: any;
  priority: 'high' | 'normal' | 'low';
  timestamp: number;
  timeout: number;
}

interface WorkerInstance {
  id: number;
  worker: Worker;
  busy: boolean;
  currentTask: WorkerTask | null;
  performance: {
    tasksCompleted: number;
    averageExecutionTime: number;
    errors: number;
  };
}

interface TaskResult {
  taskId: string;
  result: any;
  executionTime: number;
  success: boolean;
  error?: Error;
}

class CPUOptimizer {
  private workers: Map<number, WorkerInstance> = new Map();
  private taskQueue: WorkerTask[] = [];
  private maxWorkers: number = navigator.hardwareConcurrency || 4;
  private taskResults: Map<string, TaskResult> = new Map();
  private taskTimeouts: Map<string, number> = new Map();
  private isInitialized = false;

  constructor() {
    this.maxWorkers = Math.min(this.maxWorkers, 8); // Cap at 8 workers
  }

  /**
   * Initialize worker pool
   */
  async initialize(): Promise<void> {
    if (this.isInitialized) {
      console.warn('CPU optimizer already initialized');
      return;
    }

    console.log(`Initializing CPU optimizer with ${this.maxWorkers} workers`);

    // Create workers
    for (let i = 0; i < this.maxWorkers; i++) {
      await this.createWorker(i);
    }

    this.isInitialized = true;
    console.log('CPU optimizer initialization complete');
  }

  /**
   * Create a new worker
   */
  private async createWorker(id: number): Promise<void> {
    try {
      // Create a blob URL for the worker code
      const workerCode = this.getWorkerCode();
      const blob = new Blob([workerCode], { type: 'application/javascript' });
      const workerUrl = URL.createObjectURL(blob);
      
      const worker = new Worker(workerUrl);
      
      const workerInstance: WorkerInstance = {
        id,
        worker,
        busy: false,
        currentTask: null,
        performance: {
          tasksCompleted: 0,
          averageExecutionTime: 0,
          errors: 0
        }
      };
      
      // Set up message handler
      worker.onmessage = (event) => {
        this.handleWorkerMessage(id, event.data);
      };
      
      // Set up error handler
      worker.onerror = (error) => {
        this.handleWorkerError(id, error);
      };
      
      this.workers.set(id, workerInstance);
      
      console.log(`Worker ${id} created successfully`);
    } catch (error) {
      console.error(`Failed to create worker ${id}:`, error);
    }
  }

  /**
   * Get worker code as a string
   */
  private getWorkerCode(): string {
    return `
      self.onmessage = function(event) {
        const { taskId, taskType, taskData } = event.data;
        
        try {
          const result = processTask(taskType, taskData);
          self.postMessage({
            taskId,
            success: true,
            result
          });
        } catch (error) {
          self.postMessage({
            taskId,
            success: false,
            error: error.message
          });
        }
      };
      
      function processTask(type, data) {
        switch (type) {
          case 'heavy-computation':
            return heavyComputation(data);
          case 'data-processing':
            return dataProcessing(data);
          case 'calculation':
            return calculation(data);
          default:
            throw new Error('Unknown task type: ' + type);
        }
      }
      
      function heavyComputation(data) {
        // Simulate heavy computation
        const result = {};
        for (let i = 0; i < data.iterations; i++) {
          result[i] = Math.sqrt(i) * Math.sin(i);
        }
        return result;
      }
      
      function dataProcessing(data) {
        // Simulate data processing
        if (Array.isArray(data)) {
          return data.map(item => ({
            original: item,
            processed: item * 2,
            timestamp: Date.now()
          }));
        }
        return data;
      }
      
      function calculation(data) {
        // Simulate mathematical calculation
        const { operation, operands } = data;
        switch (operation) {
          case 'add':
            return operands.reduce((sum: number, val: number) => sum + val, 0);
          case 'multiply':
            return operands.reduce((product: number, val: number) => product * val, 1);
          case 'mean':
            const sum = operands.reduce((s: number, v: number) => s + v, 0);
            return sum / operands.length;
          default:
            throw new Error('Unknown operation: ' + operation);
        }
      }
    `;
  }

  /**
   * Handle worker message
   */
  private handleWorkerMessage(workerId: number, message: any): void {
    const worker = this.workers.get(workerId);
    if (!worker) return;

    const { taskId, success, result, error } = message;
    const task = worker.currentTask;

    if (task) {
      const executionTime = Date.now() - task.timestamp;

      const taskResult: TaskResult = {
        taskId,
        result: success ? result : null,
        executionTime,
        success,
        error: error ? new Error(error) : undefined
      };

      this.taskResults.set(taskId, taskResult);
      
      // Update worker performance
      worker.performance.tasksCompleted++;
      worker.performance.averageExecutionTime = 
        (worker.performance.averageExecutionTime * (worker.performance.tasksCompleted - 1) + executionTime) / 
        worker.performance.tasksCompleted;

      if (!success) {
        worker.performance.errors++;
      }

      // Mark worker as available
      worker.busy = false;
      worker.currentTask = null;

      // Clear timeout
      const timeoutId = this.taskTimeouts.get(taskId);
      if (timeoutId) {
        clearTimeout(timeoutId);
        this.taskTimeouts.delete(taskId);
      }

      // Process next task in queue
      this.processNextTask();

      console.log(`Worker ${workerId} completed task ${taskId} in ${executionTime}ms`);
    }
  }

  /**
   * Handle worker error
   */
  private handleWorkerError(workerId: number, error: ErrorEvent): void {
    const worker = this.workers.get(workerId);
    if (!worker) return;

    console.error(`Worker ${workerId} error:`, error);
    worker.performance.errors++;

    // Reset worker state
    worker.busy = false;
    worker.currentTask = null;

    // Recreate worker if it crashed
    this.recreateWorker(workerId);
  }

  /**
   * Recreate a crashed worker
   */
  private async recreateWorker(workerId: number): Promise<void> {
    const worker = this.workers.get(workerId);
    if (worker) {
      try {
        worker.worker.terminate();
      } catch (error) {
        console.warn('Failed to terminate worker:', error);
      }
    }

    await this.createWorker(workerId);
  }

  /**
   * Execute a task
   */
  async executeTask(
    taskType: string,
    taskData: any,
    options: {
      priority?: 'high' | 'normal' | 'low';
      timeout?: number;
    } = {}
  ): Promise<any> {
    const taskId = this.generateTaskId();
    
    const task: WorkerTask = {
      id: taskId,
      type: taskType,
      data: taskData,
      priority: options.priority || 'normal',
      timestamp: Date.now(),
      timeout: options.timeout || 30000 // 30 second default timeout
    };

    // Add task to queue
    this.taskQueue.push(task);
    
    // Sort queue by priority
    this.taskQueue.sort((a, b) => {
      const priorityOrder = { high: 3, normal: 2, low: 1 };
      return priorityOrder[b.priority] - priorityOrder[a.priority];
    });

    // Process queue
    this.processNextTask();

    // Wait for result
    return new Promise((resolve, reject) => {
      const timeoutId = setTimeout(() => {
        this.taskTimeouts.delete(taskId);
        reject(new Error(`Task ${taskId} timed out after ${task.timeout}ms`));
      }, task.timeout);

      this.taskTimeouts.set(taskId, timeoutId);

      const checkInterval = setInterval(() => {
        const result = this.taskResults.get(taskId);
        if (result) {
          clearInterval(checkInterval);
          if (result.success) {
            resolve(result.result);
          } else {
            reject(result.error);
          }
        }
      }, 100);
    });
  }

  /**
   * Process next task in queue
   */
  private processNextTask(): void {
    if (this.taskQueue.length === 0) return;

    // Find available worker
    const availableWorker = this.findAvailableWorker();
    if (!availableWorker) {
      // No workers available, wait for next cycle
      return;
    }

    // Get next task
    const task = this.taskQueue.shift();
    if (!task) return;

    // Assign task to worker
    this.assignTaskToWorker(availableWorker, task);
  }

  /**
   * Find available worker
   */
  private findAvailableWorker(): WorkerInstance | null {
    for (const worker of this.workers.values()) {
      if (!worker.busy) {
        return worker;
      }
    }
    return null;
  }

  /**
   * Assign task to worker
   */
  private assignTaskToWorker(worker: WorkerInstance, task: WorkerTask): void {
    worker.busy = true;
    worker.currentTask = task;

    worker.worker.postMessage({
      taskId: task.id,
      taskType: task.type,
      taskData: task.data
    });

    console.log(`Worker ${worker.id} assigned task ${task.id} (${task.type})`);
  }

  /**
   * Throttle function execution
   */
  throttle<T extends (...args: any[]) => any>(
    func: T,
    delay: number
  ): (...args: Parameters<T>) => void {
    let lastCall = 0;
    let timeoutId: number | null = null;

    return (...args: Parameters<T>) => {
      const now = Date.now();
      const timeSinceLastCall = now - lastCall;

      if (timeSinceLastCall >= delay) {
        func(...args);
        lastCall = now;
      } else {
        if (timeoutId) {
          clearTimeout(timeoutId);
        }
        timeoutId = window.setTimeout(() => {
          func(...args);
          lastCall = Date.now();
        }, delay - timeSinceLastCall);
      }
    };
  }

  /**
   * Debounce function execution
   */
  debounce<T extends (...args: any[]) => any>(
    func: T,
    delay: number
  ): (...args: Parameters<T>) => void {
    let timeoutId: number | null = null;

    return (...args: Parameters<T>) => {
      if (timeoutId) {
        clearTimeout(timeoutId);
      }
      timeoutId = window.setTimeout(() => {
        func(...args);
      }, delay);
    };
  }

  /**
   * Schedule periodic task
   */
  schedulePeriodicTask(
    taskType: string,
    taskData: any,
    intervalMs: number,
    options: { priority?: 'high' | 'normal' | 'low' } = {}
  ): () => void {
    const intervalId = setInterval(() => {
      this.executeTask(taskType, taskData, options).catch(error => {
        console.error(`Periodic task failed:`, error);
      });
    }, intervalMs);

    // Return cleanup function
    return () => {
      clearInterval(intervalId);
    };
  }

  /**
   * Get CPU statistics
   */
  getCPUStats(): {
    totalWorkers: number;
    busyWorkers: number;
    queueLength: number;
    tasksCompleted: number;
    averageExecutionTime: number;
    totalErrors: number;
  } {
    const workers = Array.from(this.workers.values());
    const busyWorkers = workers.filter(w => w.busy).length;
    const totalTasksCompleted = workers.reduce((sum, w) => sum + w.performance.tasksCompleted, 0);
    const totalErrors = workers.reduce((sum, w) => sum + w.performance.errors, 0);
    const avgExecutionTime = totalTasksCompleted > 0 ?
      workers.reduce((sum, w) => sum + w.performance.averageExecutionTime * w.performance.tasksCompleted, 0) / 
      totalTasksCompleted : 0;

    return {
      totalWorkers: this.workers.size,
      busyWorkers,
      queueLength: this.taskQueue.length,
      tasksCompleted: totalTasksCompleted,
      averageExecutionTime: avgExecutionTime,
      totalErrors
    };
  }

  /**
   * Shutdown CPU optimizer
   */
  async shutdown(): Promise<void> {
    console.log('Shutting down CPU optimizer');

    // Clear timeouts
    this.taskTimeouts.forEach((timeoutId) => {
      clearTimeout(timeoutId);
    });
    this.taskTimeouts.clear();

    // Terminate all workers
    const shutdownPromises = Array.from(this.workers.values()).map(worker => {
      return new Promise<void>((resolve) => {
        try {
          worker.worker.terminate();
          resolve();
        } catch (error) {
          console.warn('Failed to terminate worker:', error);
          resolve();
        }
      });
    });

    await Promise.all(shutdownPromises);

    this.workers.clear();
    this.taskQueue = [];
    this.taskResults.clear();
    this.isInitialized = false;

    console.log('CPU optimizer shutdown complete');
  }

  /**
   * Generate unique task ID
   */
  private generateTaskId(): string {
    return `task_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Check if initialized
   */
  isInitialized(): boolean {
    return this.isInitialized;
  }
}

// Singleton instance
export const cpuOptimizer = new CPUOptimizer();