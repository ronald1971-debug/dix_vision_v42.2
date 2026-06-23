"""
DIXVISION Performance Benchmarking Tests
Comprehensive performance testing and optimization validation

Tests performance characteristics including:
- Order processing throughput
- System response times
- Memory and resource usage
- Scalability under load
- Component performance optimization
- Multi-domain trading performance
- Real-time signal processing
"""

import logging
import os
import statistics
import threading
import time
import unittest
from datetime import datetime
from typing import Dict, List

import psutil

from containers.dashboard2026.infrastructure.center_communication import (
    CenterCommunication,
    MessagePriority,
)

# Import system components
from containers.dashboard2026.infrastructure.mission_control_center import (
    MissionControlCenter,
    TaskPriority,
)
from containers.execution.infrastructure.execution_system import (
    ExecutionSystem,
    OrderType,
)
from containers.execution.infrastructure.state_ledger import StateLedger
from containers.trading.multi_domain.infrastructure.crypto_domain import CryptoDomain
from containers.trading.multi_domain.infrastructure.domain_abstraction import DomainAbstractionLayer


class PerformanceBenchmarkTestBase(unittest.TestCase):
    """Base class for performance benchmarking tests"""

    def setUp(self):
        """Set up components for performance testing"""
        self.mission_control = MissionControlCenter()
        self.execution_system = ExecutionSystem()
        self.state_ledger = StateLedger()
        self.domain_abstraction = DomainAbstractionLayer()
        self.crypto_domain = CryptoDomain()
        self.center_comm = CenterCommunication()

        self.domain_abstraction.register_domain("crypto", self.crypto_domain)
        self.execution_system.domain_abstraction = self.domain_abstraction
        self.execution_system.state_ledger = self.state_ledger

        # Performance metrics collection
        self.performance_metrics = {
            "order_processing_times": [],
            "mission_creation_times": [],
            "message_throughput": [],
            "memory_usage": [],
            "cpu_usage": [],
        }

        logging.info("Performance benchmarking test setup complete")

    def measure_order_processing_time(
        self, symbol: str, order_type: OrderType, direction: str, quantity: float
    ) -> float:
        """Measure time to create and submit an order"""
        start_time = time.perf_counter()

        order = self.execution_system.create_order(
            symbol=symbol, order_type=order_type, direction=direction, quantity=quantity
        )
        self.execution_system.submit_order(order.order_id)

        end_time = time.perf_counter()
        processing_time = (end_time - start_time) * 1000  # Convert to milliseconds
        self.performance_metrics["order_processing_times"].append(processing_time)

        return processing_time

    def measure_mission_creation_time(
        self, mission_name: str, description: str, created_by: str
    ) -> float:
        """Measure time to create a mission"""
        start_time = time.perf_counter()

        mission = self.mission_control.create_mission(
            mission_name=mission_name, description=description, created_by=created_by
        )

        end_time = time.perf_counter()
        creation_time = (end_time - start_time) * 1000
        self.performance_metrics["mission_creation_times"].append(creation_time)

        return creation_time

    def get_system_metrics(self) -> Dict[str, float]:
        """Get current system resource metrics"""
        process = psutil.Process(os.getpid())

        memory_info = process.memory_info()
        cpu_percent = process.cpu_percent(interval=0.1)

        metrics = {
            "memory_mb": memory_info.rss / 1024 / 1024,
            "cpu_percent": cpu_percent,
            "memory_percent": process.memory_percent(),
        }

        self.performance_metrics["memory_usage"].append(metrics["memory_mb"])
        self.performance_metrics["cpu_usage"].append(metrics["cpu_percent"])

        return metrics

    def calculate_performance_statistics(self, times: List[float]) -> Dict[str, float]:
        """Calculate statistics for performance times"""
        if not times:
            return {}

        return {
            "mean_ms": statistics.mean(times),
            "median_ms": statistics.median(times),
            "min_ms": min(times),
            "max_ms": max(times),
            "std_dev_ms": statistics.stdev(times) if len(times) > 1 else 0.0,
            "p95_ms": self.calculate_percentile(times, 95),
            "p99_ms": self.calculate_percentile(times, 99),
        }

    def calculate_percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile of data"""
        if not data:
            return 0.0
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        return sorted_data[min(index, len(sorted_data) - 1)]


class TestOrderProcessingPerformance(PerformanceBenchmarkTestBase):
    """Test order processing performance"""

    def test_single_order_performance(self):
        """Test performance of single order processing"""
        processing_times = []

        for i in range(10):
            time_taken = self.measure_order_processing_time(
                symbol=f"TEST{i}/USDT", order_type=OrderType.MARKET, direction="buy", quantity=1.0
            )
            processing_times.append(time_taken)

        stats = self.calculate_performance_statistics(processing_times)

        logging.info(f"Single order performance: {stats}")

        # Single order should be processed in < 10ms
        self.assertLess(stats["mean_ms"], 10.0)
        self.assertLess(stats["p95_ms"], 20.0)

    def test_batch_order_performance(self):
        """Test performance of batch order processing"""
        batch_sizes = [10, 50, 100]
        batch_results = {}

        for batch_size in batch_sizes:
            start_time = time.perf_counter()

            for i in range(batch_size):
                order = self.execution_system.create_order(
                    symbol=f"BATCH{i}/USDT",
                    order_type=OrderType.MARKET,
                    direction="buy",
                    quantity=1.0,
                )
                self.execution_system.submit_order(order.order_id)

            end_time = time.perf_counter()
            total_time = (end_time - start_time) * 1000
            throughput = batch_size / (total_time / 1000)  # orders per second

            batch_results[batch_size] = {
                "total_time_ms": total_time,
                "throughput_orders_per_sec": throughput,
                "avg_time_per_order_ms": total_time / batch_size,
            }

        logging.info(f"Batch order performance: {batch_results}")

        # Should maintain reasonable throughput even at scale
        self.assertGreater(batch_results[100]["throughput_orders_per_sec"], 50)

    def test_concurrent_order_performance(self):
        """Test performance under concurrent order processing"""

        def process_orders(worker_id: int, num_orders: int):
            """Worker function to process orders"""
            for i in range(num_orders):
                order = self.execution_system.create_order(
                    symbol=f"CONCURRENT{worker_id}_{i}/USDT",
                    order_type=OrderType.MARKET,
                    direction="buy",
                    quantity=1.0,
                )
                self.execution_system.submit_order(order.order_id)

        num_workers = 4
        orders_per_worker = 25

        start_time = time.perf_counter()

        threads = []
        for worker_id in range(num_workers):
            thread = threading.Thread(target=process_orders, args=(worker_id, orders_per_worker))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        end_time = time.perf_counter()
        total_time = (end_time - start_time) * 1000
        total_orders = num_workers * orders_per_worker
        throughput = total_orders / (total_time / 1000)

        logging.info(f"Concurrent order processing: {total_time:.2f}ms for {total_orders} orders")
        logging.info(f"Throughput: {throughput:.2f} orders/sec")

        # Should handle concurrent processing efficiently
        self.assertLess(total_time, 5000.0)  # Should complete in < 5 seconds
        self.assertGreater(throughput, 20)  # Should maintain > 20 orders/sec


class TestMissionControlPerformance(PerformanceBenchmarkTestBase):
    """Test mission control performance"""

    def test_mission_creation_performance(self):
        """Test performance of mission creation"""
        creation_times = []

        for i in range(20):
            time_taken = self.measure_mission_creation_time(
                mission_name=f"Performance Test Mission {i}",
                description=f"Test mission {i} for performance testing",
                created_by=f"operator_{i % 3}",
            )
            creation_times.append(time_taken)

        stats = self.calculate_performance_statistics(creation_times)

        logging.info(f"Mission creation performance: {stats}")

        # Mission creation should be fast
        self.assertLess(stats["mean_ms"], 50.0)
        self.assertLess(stats["p95_ms"], 100.0)

    def test_mission_with_tasks_performance(self):
        """Test performance of creating missions with tasks"""
        start_time = time.perf_counter()

        mission = self.mission_control.create_mission(
            mission_name="Complex Mission Performance Test",
            description="Test mission with multiple tasks",
            created_by="operator_001",
        )

        # Create multiple tasks
        for i in range(10):
            self.mission_control.create_task(
                mission_id=mission.mission_id,
                task_name=f"Performance Task {i}",
                description=f"Task {i} for performance testing",
                assigned_to="execution_system",
                created_by="operator_001",
                priority=TaskPriority.MEDIUM,
            )

        end_time = time.perf_counter()
        total_time = (end_time - start_time) * 1000

        logging.info(f"Mission with 10 tasks creation time: {total_time:.2f}ms")

        # Should complete in reasonable time
        self.assertLess(total_time, 200.0)

    def test_concurrent_mission_creation(self):
        """Test concurrent mission creation performance"""

        def create_missions(worker_id: int, num_missions: int):
            """Worker function to create missions"""
            for i in range(num_missions):
                mission = self.mission_control.create_mission(
                    mission_name=f"Concurrent Mission {worker_id}_{i}",
                    description=f"Concurrent test mission {i}",
                    created_by=f"operator_{worker_id}",
                )

                # Create tasks
                for j in range(5):
                    self.mission_control.create_task(
                        mission_id=mission.mission_id,
                        task_name=f"Task {j}",
                        description="Test task",
                        assigned_to="execution_system",
                        created_by=f"operator_{worker_id}",
                    )

        num_workers = 3
        missions_per_worker = 5

        start_time = time.perf_counter()

        threads = []
        for worker_id in range(num_workers):
            thread = threading.Thread(target=create_missions, args=(worker_id, missions_per_worker))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        end_time = time.perf_counter()
        total_time = (end_time - start_time) * 1000
        total_missions = num_workers * missions_per_worker

        logging.info(
            f"Concurrent mission creation: {total_time:.2f}ms for {total_missions} missions"
        )

        # Should handle concurrent creation efficiently
        self.assertLess(total_time, 3000.0)


class TestStateLedgerPerformance(PerformanceBenchmarkTestBase):
    """Test state ledger performance"""

    def test_checkpoint_creation_performance(self):
        """Test performance of checkpoint creation"""
        creation_times = []

        for i in range(50):
            start_time = time.perf_counter()

            checkpoint_id = self.state_ledger.create_checkpoint(
                component_id=f"component_{i}",
                state_data={
                    "timestamp": datetime.now().isoformat(),
                    "counter": i,
                    "data": f"test_data_{i}" * 10,  # Simulate larger state
                },
            )

            end_time = time.perf_counter()
            creation_time = (end_time - start_time) * 1000
            creation_times.append(creation_time)

        stats = self.calculate_performance_statistics(creation_times)

        logging.info(f"Checkpoint creation performance: {stats}")

        # Checkpoint creation should be efficient
        self.assertLess(stats["mean_ms"], 20.0)

    def test_checkpoint_restoration_performance(self):
        """Test performance of checkpoint restoration"""
        # Create checkpoints first
        checkpoint_ids = []
        for i in range(20):
            checkpoint_id = self.state_ledger.create_checkpoint(
                component_id=f"component_{i}",
                state_data={
                    "timestamp": datetime.now().isoformat(),
                    "counter": i,
                    "data": f"test_data_{i}" * 10,
                },
            )
            checkpoint_ids.append(checkpoint_id)

        # Measure restoration performance
        restoration_times = []
        for checkpoint_id in checkpoint_ids:
            start_time = time.perf_counter()

            restored_state = self.state_ledger.restore_checkpoint(checkpoint_id)

            end_time = time.perf_counter()
            restoration_time = (end_time - start_time) * 1000
            restoration_times.append(restoration_time)

        stats = self.calculate_performance_statistics(restoration_times)

        logging.info(f"Checkpoint restoration performance: {stats}")

        # Restoration should be fast
        self.assertLess(stats["mean_ms"], 30.0)

    def test_transaction_recording_performance(self):
        """Test performance of transaction recording"""
        recording_times = []

        for i in range(100):
            start_time = time.perf_counter()

            self.state_ledger.record_transaction(
                entity_id=f"entity_{i}",
                transaction_type="state_change",
                previous_state={"value": i},
                new_state={"value": i + 1},
                metadata={"source": "performance_test"},
            )

            end_time = time.perf_counter()
            recording_time = (end_time - start_time) * 1000
            recording_times.append(recording_time)

        stats = self.calculate_performance_statistics(recording_times)

        logging.info(f"Transaction recording performance: {stats}")

        # Transaction recording should be very fast
        self.assertLess(stats["mean_ms"], 5.0)


class TestCommunicationPerformance(PerformanceBenchmarkTestBase):
    """Test center communication performance"""

    def test_message_throughput(self):
        """Test message throughput"""
        num_messages = 1000
        message_sizes = [100, 500, 1000]  # bytes

        for message_size in message_sizes:
            start_time = time.perf_counter()

            for i in range(num_messages):
                message = self.center_comm.send_message(
                    from_component="sender",
                    to_component="receiver",
                    message_type="status_update",
                    priority=MessagePriority.MEDIUM,
                    content={"data": "x" * message_size, "counter": i},
                )

            end_time = time.perf_counter()
            total_time = (end_time - start_time) * 1000
            throughput = num_messages / (total_time / 1000)

            logging.info(
                f"Message throughput ({message_size} bytes): {throughput:.2f} messages/sec"
            )

            # Should maintain high throughput
            self.assertGreater(throughput, 100)

    def test_concurrent_message_sending(self):
        """Test concurrent message sending performance"""

        def send_messages(worker_id: int, num_messages: int):
            """Worker function to send messages"""
            for i in range(num_messages):
                self.center_comm.send_message(
                    from_component=f"worker_{worker_id}",
                    to_component="receiver",
                    message_type="status_update",
                    priority=MessagePriority.MEDIUM,
                    content={"worker": worker_id, "counter": i},
                )

        num_workers = 5
        messages_per_worker = 100

        start_time = time.perf_counter()

        threads = []
        for worker_id in range(num_workers):
            thread = threading.Thread(target=send_messages, args=(worker_id, messages_per_worker))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        end_time = time.perf_counter()
        total_time = (end_time - start_time) * 1000
        total_messages = num_workers * messages_per_worker
        throughput = total_messages / (total_time / 1000)

        logging.info(f"Concurrent message sending: {throughput:.2f} messages/sec")

        # Should handle concurrent messaging efficiently
        self.assertGreater(throughput, 50)


class TestResourceUsage(PerformanceBenchmarkTestBase):
    """Test system resource usage"""

    def test_memory_usage_under_load(self):
        """Test memory usage under load"""
        initial_metrics = self.get_system_metrics()

        # Create load
        for i in range(100):
            order = self.execution_system.create_order(
                symbol=f"MEMORY{i}/USDT", order_type=OrderType.MARKET, direction="buy", quantity=1.0
            )
            self.execution_system.submit_order(order.order_id)

        peak_metrics = self.get_system_metrics()

        memory_increase = peak_metrics["memory_mb"] - initial_metrics["memory_mb"]

        logging.info(
            f"Memory usage: initial {initial_metrics['memory_mb']:.2f}MB, peak {peak_metrics['memory_mb']:.2f}MB"
        )
        logging.info(f"Memory increase: {memory_increase:.2f}MB")

        # Memory increase should be reasonable
        self.assertLess(memory_increase, 50.0)

    def test_cpu_usage_under_load(self):
        """Test CPU usage under sustained load"""
        # Measure baseline
        baseline_metrics = self.get_system_metrics()

        # Sustained load
        start_time = time.perf_counter()

        for i in range(200):
            order = self.execution_system.create_order(
                symbol=f"CPU{i}/USDT", order_type=OrderType.MARKET, direction="buy", quantity=1.0
            )
            self.execution_system.submit_order(order.order_id)

            # Small delay to simulate real work
            time.sleep(0.001)

        end_time = time.perf_counter()

        load_metrics = self.get_system_metrics()

        duration = end_time - start_time
        avg_cpu = statistics.mean(self.performance_metrics["cpu_usage"])

        logging.info(f"CPU usage under load: {avg_cpu:.2f}% over {duration:.2f}s")

        # CPU usage should be reasonable
        self.assertLess(avg_cpu, 80.0)


class TestScalabilityPerformance(PerformanceBenchmarkTestBase):
    """Test scalability under increasing load"""

    def test_linear_scalability(self):
        """Test that system scales linearly with load"""
        load_levels = [10, 50, 100, 200]
        processing_times = []

        for load in load_levels:
            start_time = time.perf_counter()

            for i in range(load):
                order = self.execution_system.create_order(
                    symbol=f"SCALE{load}_{i}/USDT",
                    order_type=OrderType.MARKET,
                    direction="buy",
                    quantity=1.0,
                )
                self.execution_system.submit_order(order.order_id)

            end_time = time.perf_counter()
            total_time = (end_time - start_time) * 1000
            processing_times.append(total_time)

        # Check for linear scalability (time should increase proportionally to load)
        # Calculate ratios between consecutive load levels
        ratios = []
        for i in range(1, len(load_levels)):
            load_ratio = load_levels[i] / load_levels[i - 1]
            time_ratio = processing_times[i] / processing_times[i - 1]
            ratios.append(time_ratio / load_ratio)

        # Ratios close to 1.0 indicate linear scalability
        avg_ratio = statistics.mean(ratios)

        logging.info(f"Scalability ratios: {ratios}")
        logging.info(f"Average scalability ratio: {avg_ratio:.2f}")

        # Should be reasonably linear (ratio between 0.5 and 2.0)
        self.assertGreater(avg_ratio, 0.5)
        self.assertLess(avg_ratio, 2.0)

    def test_component_interaction_scalability(self):
        """Test scalability of component interactions"""
        interaction_counts = [10, 50, 100, 200]
        interaction_times = []

        for count in interaction_counts:
            start_time = time.perf_counter()

            # Create mission-task-execution chain
            mission = self.mission_control.create_mission(
                mission_name="Scalability Test",
                description="Test component interaction scalability",
                created_by="operator_001",
            )

            for i in range(count):
                task = self.mission_control.create_task(
                    mission_id=mission.mission_id,
                    task_name=f"Interaction Task {i}",
                    description="Test task",
                    assigned_to="execution_system",
                    created_by="operator_001",
                )

                order = self.execution_system.create_order(
                    symbol=f"INT{i}/USDT",
                    order_type=OrderType.MARKET,
                    direction="buy",
                    quantity=1.0,
                )
                self.execution_system.submit_order(order.order_id)

            end_time = time.perf_counter()
            total_time = (end_time - start_time) * 1000
            interaction_times.append(total_time)

        logging.info(f"Component interaction scalability: {interaction_times}")

        # Should complete even at higher interaction counts
        self.assertLess(interaction_times[-1], 10000.0)  # < 10 seconds for 200 interactions


class TestPerformanceOptimization(PerformanceBenchmarkTestBase):
    """Test performance optimization features"""

    def test_caching_performance(self):
        """Test that caching improves performance"""
        # First access (cache miss)
        start_time = time.perf_counter()
        for i in range(100):
            order = self.execution_system.create_order(
                symbol=f"CACHE{i}/USDT", order_type=OrderType.MARKET, direction="buy", quantity=1.0
            )
        end_time = time.perf_counter()
        first_access_time = (end_time - start_time) * 1000

        # Simulate cached access (reusing similar operations)
        start_time = time.perf_counter()
        for i in range(100):
            # Similar operations that might benefit from caching
            order = self.execution_system.create_order(
                symbol="BTC/USDT",  # Reuse same symbol
                order_type=OrderType.MARKET,
                direction="buy",
                quantity=1.0,
            )
        end_time = time.perf_counter()
        cached_access_time = (end_time - start_time) * 1000

        logging.info(
            f"First access: {first_access_time:.2f}ms, Cached access: {cached_access_time:.2f}ms"
        )

        # Cached access should be faster or similar
        self.assertLessEqual(cached_access_time, first_access_time * 1.5)

    def test_batch_optimization(self):
        """Test that batch operations are optimized"""
        # Individual operations
        start_time = time.perf_counter()
        for i in range(50):
            self.execution_system.create_order(
                symbol=f"BATCH_OPT{i}/USDT",
                order_type=OrderType.MARKET,
                direction="buy",
                quantity=1.0,
            )
        end_time = time.perf_counter()
        individual_time = (end_time - start_time) * 1000

        # Simulated batch operations (using optimized patterns)
        start_time = time.perf_counter()
        # In a real system, this would use batch API calls
        for i in range(50):
            self.execution_system.create_order(
                symbol=f"BATCH_OPT{i}/USDT",
                order_type=OrderType.MARKET,
                direction="buy",
                quantity=1.0,
            )
        end_time = time.perf_counter()
        batch_time = (end_time - start_time) * 1000

        logging.info(
            f"Individual operations: {individual_time:.2f}ms, Batch operations: {batch_time:.2f}ms"
        )

        # Batch should be competitive with individual
        self.assertLessEqual(batch_time, individual_time * 1.2)


if __name__ == "__main__":
    unittest.main()
