"""
performance_validation.py
DIX VISION v42.2 — Performance Validation and Tuning

Comprehensive performance validation for cognitive architecture integration.
Includes latency measurement, resource utilization, throughput analysis,
and performance comparison with legacy system.
"""

from __future__ import annotations

import logging
import time
import threading
import psutil
from datetime import datetime
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
import statistics

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetric:
    """A single performance metric."""
    metric_name: str
    metric_value: float
    unit: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PerformanceTestResult:
    """Result of a performance test."""
    test_name: str
    success: bool
    duration_seconds: float
    metrics: List[PerformanceMetric] = field(default_factory=list)
    error_message: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)


class PerformanceValidator:
    """
    Performance validator for cognitive architecture integration.
    
    Features:
    - Latency measurement for cognitive operations
    - Resource utilization monitoring
    - Throughput analysis
    - Memory usage tracking
    - Performance comparison with legacy
    - Performance tuning recommendations
    """
    
    def __init__(self):
        self._lock = threading.Lock()
        self._metrics_history: List[PerformanceMetric] = []
        self._test_results: List[PerformanceTestResult] = []
        
        # Performance thresholds
        self._thresholds = {
            "max_indira_latency_ms": 10.0,  # INDIRA decision < 10ms
            "max_dyon_latency_ms": 50.0,    # DYON analysis < 50ms
            "max_memory_mb": 12000.0,       # Total memory < 12GB (more realistic)
            "max_cpu_percent": 80.0,        # CPU usage < 80%
            "min_throughput_ops_per_sec": 100.0  # Throughput > 100 ops/sec
        }
        
        logger.info("[PERFORMANCE_VALIDATOR] Performance validator initialized")
    
    def run_all_performance_tests(self) -> Dict[str, Any]:
        """Run all performance tests and return summary."""
        results = {
            "test_start": datetime.utcnow().isoformat(),
            "tests_completed": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "test_results": [],
            "performance_summary": {},
            "recommendations": []
        }
        
        try:
            # Test 1: INDIRA Brain Latency
            indira_result = self._test_indira_latency()
            results["test_results"].append(indira_result)
            results["tests_completed"] += 1
            if indira_result.success:
                results["tests_passed"] += 1
            else:
                results["tests_failed"] += 1
            
            # Test 2: DYON Brain Latency
            dyon_result = self._test_dyon_latency()
            results["test_results"].append(dyon_result)
            results["tests_completed"] += 1
            if dyon_result.success:
                results["tests_passed"] += 1
            else:
                results["tests_failed"] += 1
            
            # Test 3: Resource Utilization
            resource_result = self._test_resource_utilization()
            results["test_results"].append(resource_result)
            results["tests_completed"] += 1
            if resource_result.success:
                results["tests_passed"] += 1
            else:
                results["tests_failed"] += 1
            
            # Test 4: Throughput Analysis
            throughput_result = self._test_throughput()
            results["test_results"].append(throughput_result)
            results["tests_completed"] += 1
            if throughput_result.success:
                results["tests_passed"] += 1
            else:
                results["tests_failed"] += 1
            
            # Test 5: Memory Efficiency
            memory_result = self._test_memory_efficiency()
            results["test_results"].append(memory_result)
            results["tests_completed"] += 1
            if memory_result.success:
                results["tests_passed"] += 1
            else:
                results["tests_failed"] += 1
            
            # Test 6: Legacy Comparison
            comparison_result = self._test_legacy_comparison()
            results["test_results"].append(comparison_result)
            results["tests_completed"] += 1
            if comparison_result.success:
                results["tests_passed"] += 1
            else:
                results["tests_failed"] += 1
            
            # Generate summary
            results["performance_summary"] = self._generate_performance_summary()
            results["recommendations"] = self._generate_recommendations()
            results["test_end"] = datetime.utcnow().isoformat()
            
            logger.info(f"[PERFORMANCE_VALIDATOR] Performance tests completed: "
                       f"{results['tests_passed']}/{results['tests_completed']} passed")
            
            return results
            
        except Exception as e:
            logger.error(f"[PERFORMANCE_VALIDATOR] Performance tests failed: {e}")
            results["error"] = str(e)
            return results
    
    def _test_indira_latency(self) -> PerformanceTestResult:
        """Test INDIRA brain decision latency."""
        test_name = "INDIRA Brain Latency Test"
        latencies = []
        
        try:
            from indira_cognitive.indira_brain.concrete import ConcreteINDIRABrain
            
            brain = ConcreteINDIRABrain()
            
            # Run 10 iterations
            for i in range(10):
                start_time = time.time()
                
                # Simulate trading decision
                market_state = {"signal": 0.5, "regime": "TRENDING", "price": 50000.0}
                asset = "BTC_USDT"
                decision = brain.execute_fast_trading_decision(market_state, asset)
                
                end_time = time.time()
                latency_ms = (end_time - start_time) * 1000
                latencies.append(latency_ms)
            
            # Calculate statistics
            avg_latency = statistics.mean(latencies)
            max_latency = max(latencies)
            min_latency = min(latencies)
            std_latency = statistics.stdev(latencies) if len(latencies) > 1 else 0.0
            
            # Check against threshold
            success = avg_latency < self._thresholds["max_indira_latency_ms"]
            
            metrics = [
                PerformanceMetric("avg_latency_ms", avg_latency, "ms"),
                PerformanceMetric("max_latency_ms", max_latency, "ms"),
                PerformanceMetric("min_latency_ms", min_latency, "ms"),
                PerformanceMetric("std_latency_ms", std_latency, "ms"),
                PerformanceMetric("iterations", len(latencies), "count")
            ]
            
            result = PerformanceTestResult(
                test_name=test_name,
                success=success,
                duration_seconds=sum(latencies) / 1000.0,
                metrics=metrics,
                error_message=f"Avg latency {avg_latency:.2f}ms exceeds threshold "
                              f"{self._thresholds['max_indira_latency_ms']}ms" if not success else ""
            )
            
            logger.info(f"[PERFORMANCE_VALIDATOR] {test_name}: avg={avg_latency:.2f}ms, success={success}")
            
            return result
            
        except Exception as e:
            logger.error(f"[PERFORMANCE_VALIDATOR] {test_name} failed: {e}")
            return PerformanceTestResult(
                test_name=test_name,
                success=False,
                duration_seconds=0.0,
                error_message=str(e)
            )
    
    def _test_dyon_latency(self) -> PerformanceTestResult:
        """Test DYON brain analysis latency."""
        test_name = "DYON Brain Latency Test"
        latencies = []
        
        try:
            from dyon_cognitive.dyon_brain.concrete import ConcreteDYONBrain
            
            brain = ConcreteDYONBrain()
            
            # Run 10 iterations
            for i in range(10):
                start_time = time.time()
                
                # Simulate system analysis
                from dyon_cognitive.dyon_brain import SystemAnalysis
                analysis = SystemAnalysis(
                    analysis_id=f"test_issue_{i}",
                    target=f"Test issue {i}",
                    analysis_type="CODE",
                    findings=["Test finding"],
                    recommendations=["Test recommendation"]
                )
                analysis_result = brain.analyze_system(analysis)
                
                end_time = time.time()
                latency_ms = (end_time - start_time) * 1000
                latencies.append(latency_ms)
            
            # Calculate statistics
            avg_latency = statistics.mean(latencies)
            max_latency = max(latencies)
            min_latency = min(latencies)
            std_latency = statistics.stdev(latencies) if len(latencies) > 1 else 0.0
            
            # Check against threshold
            success = avg_latency < self._thresholds["max_dyon_latency_ms"]
            
            metrics = [
                PerformanceMetric("avg_latency_ms", avg_latency, "ms"),
                PerformanceMetric("max_latency_ms", max_latency, "ms"),
                PerformanceMetric("min_latency_ms", min_latency, "ms"),
                PerformanceMetric("std_latency_ms", std_latency, "ms"),
                PerformanceMetric("iterations", len(latencies), "count")
            ]
            
            result = PerformanceTestResult(
                test_name=test_name,
                success=success,
                duration_seconds=sum(latencies) / 1000.0,
                metrics=metrics,
                error_message=f"Avg latency {avg_latency:.2f}ms exceeds threshold "
                              f"{self._thresholds['max_dyon_latency_ms']}ms" if not success else ""
            )
            
            logger.info(f"[PERFORMANCE_VALIDATOR] {test_name}: avg={avg_latency:.2f}ms, success={success}")
            
            return result
            
        except Exception as e:
            logger.error(f"[PERFORMANCE_VALIDATOR] {test_name} failed: {e}")
            return PerformanceTestResult(
                test_name=test_name,
                success=False,
                duration_seconds=0.0,
                error_message=str(e)
            )
    
    def _test_resource_utilization(self) -> PerformanceTestResult:
        """Test resource utilization."""
        test_name = "Resource Utilization Test"
        
        try:
            # Get current resource utilization
            cpu_percent = psutil.cpu_percent(interval=1)
            memory_info = psutil.virtual_memory()
            memory_mb = memory_info.used / (1024 * 1024)
            
            # Check against thresholds
            cpu_ok = cpu_percent < self._thresholds["max_cpu_percent"]
            memory_ok = memory_mb < self._thresholds["max_memory_mb"]
            success = cpu_ok and memory_ok
            
            metrics = [
                PerformanceMetric("cpu_percent", cpu_percent, "%"),
                PerformanceMetric("memory_mb", memory_mb, "MB"),
                PerformanceMetric("memory_percent", memory_info.percent, "%")
            ]
            
            result = PerformanceTestResult(
                test_name=test_name,
                success=success,
                duration_seconds=1.0,
                metrics=metrics,
                error_message=f"CPU {cpu_percent}% or memory {memory_mb:.0f}MB exceeds thresholds" if not success else ""
            )
            
            logger.info(f"[PERFORMANCE_VALIDATOR] {test_name}: CPU={cpu_percent}%, Memory={memory_mb:.0f}MB, success={success}")
            
            return result
            
        except Exception as e:
            logger.error(f"[PERFORMANCE_VALIDATOR] {test_name} failed: {e}")
            return PerformanceTestResult(
                test_name=test_name,
                success=False,
                duration_seconds=0.0,
                error_message=str(e)
            )
    
    def _test_throughput(self) -> PerformanceTestResult:
        """Test throughput for cognitive operations."""
        test_name = "Throughput Test"
        
        try:
            from indira_cognitive.indira_brain.concrete import ConcreteINDIRABrain
            from indira_cognitive.indira_brain import MarketAnalysis
            
            brain = ConcreteINDIRABrain()
            
            # Run operations for 10 seconds
            duration = 10.0
            start_time = time.time()
            operations_count = 0
            
            while time.time() - start_time < duration:
                # Simulate trading decision
                market_state = {"signal": 0.5, "regime": "TRENDING", "price": 50000.0}
                asset = "BTC_USDT"
                decision = brain.execute_fast_trading_decision(market_state, asset)
                operations_count += 1
            
            actual_duration = time.time() - start_time
            throughput = operations_count / actual_duration
            
            # Check against threshold
            success = throughput >= self._thresholds["min_throughput_ops_per_sec"]
            
            metrics = [
                PerformanceMetric("operations_count", operations_count, "count"),
                PerformanceMetric("throughput_ops_per_sec", throughput, "ops/sec"),
                PerformanceMetric("actual_duration_seconds", actual_duration, "sec")
            ]
            
            result = PerformanceTestResult(
                test_name=test_name,
                success=success,
                duration_seconds=actual_duration,
                metrics=metrics,
                error_message=f"Throughput {throughput:.1f} ops/sec below threshold "
                              f"{self._thresholds['min_throughput_ops_per_sec']} ops/sec" if not success else ""
            )
            
            logger.info(f"[PERFORMANCE_VALIDATOR] {test_name}: {throughput:.1f} ops/sec, success={success}")
            
            return result
            
        except Exception as e:
            logger.error(f"[PERFORMANCE_VALIDATOR] {test_name} failed: {e}")
            return PerformanceTestResult(
                test_name=test_name,
                success=False,
                duration_seconds=0.0,
                error_message=str(e)
            )
    
    def _test_memory_efficiency(self) -> PerformanceTestResult:
        """Test memory efficiency."""
        test_name = "Memory Efficiency Test"
        
        try:
            # Get process memory info
            process = psutil.Process()
            memory_info = process.memory_info()
            
            rss_mb = memory_info.rss / (1024 * 1024)  # Resident Set Size
            vms_mb = memory_info.vms / (1024 * 1024)  # Virtual Memory Size
            
            # Memory growth over time
            initial_memory = rss_mb
            time.sleep(2)
            final_memory = process.memory_info().rss / (1024 * 1024)
            memory_growth = final_memory - initial_memory
            
            # Check memory efficiency
            memory_ok = final_memory < self._thresholds["max_memory_mb"]
            growth_ok = abs(memory_growth) < 10.0  # Less than 10MB growth in 2 seconds
            success = memory_ok and growth_ok
            
            metrics = [
                PerformanceMetric("rss_mb", rss_mb, "MB"),
                PerformanceMetric("vms_mb", vms_mb, "MB"),
                PerformanceMetric("memory_growth_mb", memory_growth, "MB")
            ]
            
            result = PerformanceTestResult(
                test_name=test_name,
                success=success,
                duration_seconds=2.0,
                metrics=metrics,
                error_message=f"Memory {final_memory:.0f}MB or growth {memory_growth:.1f}MB exceeds limits" if not success else ""
            )
            
            logger.info(f"[PERFORMANCE_VALIDATOR] {test_name}: RSS={rss_mb:.0f}MB, growth={memory_growth:.1f}MB, success={success}")
            
            return result
            
        except Exception as e:
            logger.error(f"[PERFORMANCE_VALIDATOR] {test_name} failed: {e}")
            return PerformanceTestResult(
                test_name=test_name,
                success=False,
                duration_seconds=0.0,
                error_message=str(e)
            )
    
    def _test_legacy_comparison(self) -> PerformanceTestResult:
        """Test performance comparison with legacy system."""
        test_name = "Legacy Performance Comparison Test"
        
        try:
            from mind.engine import IndiraEngine
            from indira_cognitive.indira_brain.concrete import ConcreteINDIRABrain
            from indira_cognitive.indira_brain import MarketAnalysis
            
            # Test legacy engine
            legacy_engine = IndiraEngine()
            legacy_latencies = []
            
            for i in range(5):
                start_time = time.time()
                # Use basic legacy functionality
                try:
                    legacy_engine.process_tick({"timestamp": time.time()})
                except:
                    pass
                end_time = time.time()
                legacy_latencies.append((end_time - start_time) * 1000)
            
            # Test new architecture
            new_brain = ConcreteINDIRABrain()
            new_latencies = []
            
            for i in range(5):
                start_time = time.time()
                market_state = {"signal": 0.5, "regime": "TRENDING", "price": 50000.0}
                asset = "BTC_USDT"
                decision = new_brain.execute_fast_trading_decision(market_state, asset)
                end_time = time.time()
                new_latencies.append((end_time - start_time) * 1000)
            
            # Compare
            avg_legacy = statistics.mean(legacy_latencies)
            avg_new = statistics.mean(new_latencies)
            ratio = avg_new / avg_legacy if avg_legacy > 0 else 1.0
            
            # New architecture should be within 2x of legacy
            success = ratio < 2.0
            
            metrics = [
                PerformanceMetric("avg_legacy_latency_ms", avg_legacy, "ms"),
                PerformanceMetric("avg_new_latency_ms", avg_new, "ms"),
                PerformanceMetric("performance_ratio", ratio, "x")
            ]
            
            result = PerformanceTestResult(
                test_name=test_name,
                success=success,
                duration_seconds=sum(legacy_latencies + new_latencies) / 1000.0,
                metrics=metrics,
                error_message=f"New architecture {ratio:.1f}x slower than legacy" if not success else ""
            )
            
            logger.info(f"[PERFORMANCE_VALIDATOR] {test_name}: new={avg_new:.2f}ms, legacy={avg_legacy:.2f}ms, ratio={ratio:.1f}x, success={success}")
            
            return result
            
        except Exception as e:
            logger.error(f"[PERFORMANCE_VALIDATOR] {test_name} failed: {e}")
            return PerformanceTestResult(
                test_name=test_name,
                success=False,
                duration_seconds=0.0,
                error_message=str(e)
            )
    
    def _generate_performance_summary(self) -> Dict[str, Any]:
        """Generate performance summary from all tests."""
        summary = {
            "overall_performance": "GOOD",
            "key_metrics": {},
            "bottlenecks": [],
            "strengths": []
        }
        
        for test_result in self._test_results:
            for metric in test_result.metrics:
                summary["key_metrics"][metric.metric_name] = {
                    "value": metric.metric_value,
                    "unit": metric.unit
                }
        
        # Analyze performance
        if summary["key_metrics"].get("avg_latency_ms", 0) > 20:
            summary["bottlenecks"].append("High latency detected")
            summary["overall_performance"] = "NEEDS_IMPROVEMENT"
        
        if summary["key_metrics"].get("memory_mb", 0) > 400:
            summary["bottlenecks"].append("High memory usage")
            summary["overall_performance"] = "NEEDS_IMPROVEMENT"
        
        if summary["key_metrics"].get("throughput_ops_per_sec", 0) < 50:
            summary["bottlenecks"].append("Low throughput")
            summary["overall_performance"] = "NEEDS_IMPROVEMENT"
        
        if summary["key_metrics"].get("performance_ratio", 1.0) < 1.5:
            summary["strengths"].append("Performance comparable to legacy")
        
        return summary
    
    def _generate_recommendations(self) -> List[str]:
        """Generate performance tuning recommendations."""
        recommendations = []
        
        for test_result in self._test_results:
            if not test_result.success:
                if "latency" in test_result.test_name.lower():
                    recommendations.append(
                        "Consider optimizing cognitive computation paths or "
                        "caching frequent operations to reduce latency"
                    )
                elif "memory" in test_result.test_name.lower():
                    recommendations.append(
                        "Implement memory pooling or optimize data structures "
                        "to reduce memory footprint"
                    )
                elif "throughput" in test_result.test_name.lower():
                    recommendations.append(
                        "Consider parallel processing or batching operations "
                        "to improve throughput"
                    )
        
        if not recommendations:
            recommendations.append("Performance is within acceptable thresholds - no immediate tuning needed")
        
        return recommendations


def main():
    """Main function to run performance validation."""
    logging.basicConfig(level=logging.INFO)
    
    print("=== DIX VISION v42.2 Performance Validation ===\n")
    
    validator = PerformanceValidator()
    results = validator.run_all_performance_tests()
    
    print(f"\n=== Performance Test Results ===")
    print(f"Tests Completed: {results['tests_completed']}")
    print(f"Tests Passed: {results['tests_passed']}")
    print(f"Tests Failed: {results['tests_failed']}")
    print(f"Success Rate: {results['tests_passed']/results['tests_completed']*100 if results['tests_completed'] > 0 else 0:.1f}%")
    
    print(f"\n=== Individual Test Results ===")
    for test_result in results['test_results']:
        status = "PASS" if test_result.success else "FAIL"
        print(f"{status} - {test_result.test_name}")
        if test_result.error_message:
            print(f"  Error: {test_result.error_message}")
    
    print(f"\n=== Performance Summary ===")
    summary = results['performance_summary']
    print(f"Overall Performance: {summary['overall_performance']}")
    print(f"Key Metrics: {len(summary['key_metrics'])} metrics collected")
    
    if summary['bottlenecks']:
        print(f"Bottlenecks: {', '.join(summary['bottlenecks'])}")
    
    if summary['strengths']:
        print(f"Strengths: {', '.join(summary['strengths'])}")
    
    print(f"\n=== Recommendations ===")
    for i, recommendation in enumerate(results['recommendations'], 1):
        print(f"{i}. {recommendation}")
    
    return results['tests_passed'] == results['tests_completed']


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
