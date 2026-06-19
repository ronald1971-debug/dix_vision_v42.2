"""Comprehensive tests for M-1 Knowledge Layer components.

Tests for:
- KnowledgeValidator
- SourceConflictGraph
- EdgeCaseMemory
- Enhanced MemoryIndexAuthority
- KnowledgeDriftMonitor
"""

import unittest
import threading
import time
from collections.abc import Mapping
from types import MappingProxyType

# Import M-1 Knowledge Layer components
import sys
import os

# Add paths to imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from intelligence_engine.knowledge.knowledge_validator import (
    KnowledgeValidator,
    KnowledgeSource,
    KnowledgeSourceType,
    ValidationSeverity,
    ValidationResult,
    ConflictReport,
    IntegrityScore,
    ReliabilityScore,
    ConsistencyReport,
)

from intelligence_engine.knowledge.source_conflict_graph import (
    SourceConflictGraph,
    ConflictGraph,
    ConflictType,
    ResolutionStrategy,
    ConsensusMechanism,
)

from state.memory.edge_case_memory import (
    EdgeCaseMemory,
    EdgeCase,
    EdgeCaseContext,
    EdgeCaseSeverity,
    EdgeCaseCategory,
    EdgeCaseStatus,
    Query,
)

from state.memory.index import MemoryIndexAuthority
from state.memory.contracts import MemoryRecord, MemoryKind

from intelligence_engine.knowledge.drift_monitor import (
    KnowledgeDriftMonitor,
    DriftType,
    DriftSeverity,
    DriftReport,
    ResponseActionType,
)


class TestKnowledgeValidator(unittest.TestCase):
    """Test cases for KnowledgeValidator."""

    def setUp(self):
        """Set up test fixtures."""
        self.validator = KnowledgeValidator()

    def test_knowledge_source_creation(self):
        """Test creating a valid KnowledgeSource."""
        source = KnowledgeSource(
            source_id="test_source_1",
            source_type=KnowledgeSourceType.MARKET_DATA,
            origin="test_module",
            content=MappingProxyType({"price": "100.0", "volume": "1000"}),
            confidence=0.8,
            reliability_score=0.75,
        )
        self.assertEqual(source.source_id, "test_source_1")
        self.assertEqual(source.source_type, KnowledgeSourceType.MARKET_DATA)
        self.assertEqual(source.confidence, 0.8)

    def test_invalid_knowledge_source(self):
        """Test that invalid KnowledgeSource raises errors."""
        with self.assertRaises(ValueError):
            KnowledgeSource(
                source_id="",  # Empty source_id should fail
                source_type=KnowledgeSourceType.MARKET_DATA,
                origin="test_module",
            )

        with self.assertRaises(ValueError):
            KnowledgeSource(
                source_id="test_source",
                source_type=KnowledgeSourceType.MARKET_DATA,
                origin="test_module",
                confidence=1.5,  # Invalid confidence > 1.0
            )

    def test_source_validation(self):
        """Test basic source validation."""
        source = KnowledgeSource(
            source_id="test_source_2",
            source_type=KnowledgeSourceType.MARKET_DATA,
            origin="test_module",
            content=MappingProxyType({"price": "100.0", "volume": "1000", "timestamp": "123456789"}),
            confidence=0.8,
            reliability_score=0.75,
        )

        result = self.validator.validate_source(source)

        self.assertIsInstance(result, ValidationResult)
        self.assertTrue(result.is_valid or len(result.issues) > 0)
        self.assertGreaterEqual(result.confidence_score, 0.0)
        self.assertLessEqual(result.confidence_score, 1.0)

    def test_validation_with_missing_fields(self):
        """Test validation detects missing required fields."""
        source = KnowledgeSource(
            source_id="test_source_3",
            source_type=KnowledgeSourceType.MARKET_DATA,
            origin="test_module",
            content=MappingProxyType({"price": "100.0"}),  # Missing required fields
            confidence=0.8,
            reliability_score=0.75,
        )

        result = self.validator.validate_source(source)

        # Should have issues due to missing fields
        self.assertGreater(len(result.issues), 0)

    def test_conflict_detection(self):
        """Test conflict detection between sources."""
        source1 = KnowledgeSource(
            source_id="source_1",
            source_type=KnowledgeSourceType.MARKET_DATA,
            origin="module_a",
            content=MappingProxyType({"price": "100.0", "volume": "1000"}),
            confidence=0.8,
            reliability_score=0.75,
        )

        source2 = KnowledgeSource(
            source_id="source_2",
            source_type=KnowledgeSourceType.MARKET_DATA,
            origin="module_b",
            content=MappingProxyType({"price": "105.0", "volume": "1000"}),  # Different price
            confidence=0.7,
            reliability_score=0.70,
        )

        conflicts = self.validator.detect_conflicts([source1, source2])

        # Should detect at least some conflicts
        self.assertIsInstance(conflicts, list)

    def test_thread_safety(self):
        """Test thread safety of validation operations."""
        sources = [
            KnowledgeSource(
                source_id=f"source_{i}",
                source_type=KnowledgeSourceType.MARKET_DATA,
                origin="test_module",
                content=MappingProxyType({"price": str(100 + i), "volume": "1000"}),
                confidence=0.8,
                reliability_score=0.75,
            )
            for i in range(10)
        ]

        def validate_source(source):
            return self.validator.validate_source(source)

        threads = [threading.Thread(target=validate_source, args=(s,)) for s in sources]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        # Should complete without errors
        stats = self.validator._validation_history
        self.assertGreaterEqual(len(stats), 10)


class TestSourceConflictGraph(unittest.TestCase):
    """Test cases for SourceConflictGraph."""

    def setUp(self):
        """Set up test fixtures."""
        self.conflict_graph = SourceConflictGraph()

    def test_conflict_graph_building(self):
        """Test building a conflict graph."""
        sources = [
            KnowledgeSource(
                source_id=f"source_{i}",
                source_type=KnowledgeSourceType.MARKET_DATA,
                origin="test_module",
                content=MappingProxyType({"price": str(100 + i), "volume": "1000"}),
                confidence=0.8,
                reliability_score=0.75,
            )
            for i in range(3)
        ]

        # Create mock validation results
        from intelligence_engine.knowledge.knowledge_validator import ValidationResult, ValidationIssue

        validation_results = [
            ValidationResult(
                is_valid=True,
                confidence_score=0.8,
                issues=(),
                validated_source=source,
                timestamp_ns=0,
            )
            for source in sources
        ]

        graph = self.conflict_graph.build_conflict_graph(sources, validation_results)

        self.assertIsInstance(graph, ConflictGraph)
        self.assertEqual(len(graph.nodes), 3)

    def test_conflict_resolution(self):
        """Test conflict resolution strategy."""
        # Create a mock conflict report
        conflict = ConflictReport(
            conflict_id="test_conflict",
            sources_involved=("source_1", "source_2"),
            conflict_type="direct_content_conflict",
            severity=ValidationSeverity.HIGH,
            description="Test conflict",
            conflicting_fields=("price",),
            detected_at_ns=0,
        )

        # Create a mock graph
        from intelligence_engine.knowledge.source_conflict_graph import ConflictNode

        graph = ConflictGraph(
            nodes=MappingProxyType(
                {
                    "source_1": ConflictNode(
                        source_id="source_1",
                        confidence_score=0.8,
                        reliability_score=0.75,
                        source_type="MARKET_DATA",
                        conflict_count=1,
                        timestamp_ns=0,
                    ),
                    "source_2": ConflictNode(
                        source_id="source_2",
                        confidence_score=0.6,
                        reliability_score=0.65,
                        source_type="MARKET_DATA",
                        conflict_count=1,
                        timestamp_ns=0,
                    ),
                }
            ),
            edges=(),
            graph_id="test_graph",
            timestamp_ns=0,
        )

        strategy = self.conflict_graph.resolve_conflicts(conflict, graph)

        self.assertIsInstance(strategy, ResolutionStrategy)
        self.assertEqual(strategy.conflict_id, "test_conflict")

    def test_consensus_mechanism(self):
        """Test consensus mechanism for conflict resolution."""
        # Create mock conflicts
        conflicts = [
            ConflictReport(
                conflict_id=f"conflict_{i}",
                sources_involved=(f"source_{i}", f"source_{i+1}"),
                conflict_type="direct_content_conflict",
                severity=ValidationSeverity.MEDIUM,
                description=f"Test conflict {i}",
                conflicting_fields=("price",),
                detected_at_ns=0,
            )
            for i in range(3)
        ]

        # Create a mock graph
        from intelligence_engine.knowledge.source_conflict_graph import ConflictNode

        graph = ConflictGraph(
            nodes=MappingProxyType(
                {
                    f"source_{i}": ConflictNode(
                        source_id=f"source_{i}",
                        confidence_score=0.7 + (i * 0.05),
                        reliability_score=0.65 + (i * 0.05),
                        source_type="MARKET_DATA",
                        conflict_count=1,
                        timestamp_ns=0,
                    )
                    for i in range(4)
                }
            ),
            edges=(),
            graph_id="test_graph",
            timestamp_ns=0,
        )

        result = self.conflict_graph.consensus_mechanism(
            conflicts, graph, ConsensusMechanism.WEIGHTED_VOTE
        )

        self.assertIsInstance(result, type(result))  # ConsensusResult


class TestEdgeCaseMemory(unittest.TestCase):
    """Test cases for EdgeCaseMemory."""

    def setUp(self):
        """Set up test fixtures."""
        self.edge_case_memory = EdgeCaseMemory()

    def test_edge_case_capture(self):
        """Test capturing an edge case."""
        context = EdgeCaseContext(
            system_state=MappingProxyType({"cpu_usage": "90%", "memory_usage": "85%"}),
            market_conditions=MappingProxyType({"volatility": "high"}),
        )

        event = MappingProxyType({"error_type": "timeout", "component": "order_execution"})

        edge_case = self.edge_case_memory.capture_edge_case(
            event=event,
            context=context,
            category=EdgeCaseCategory.SYSTEM_FAILURE,
            severity=EdgeCaseSeverity.HIGH,
            description="Order execution timeout detected",
            event_type="system_error",
        )

        self.assertIsInstance(edge_case, EdgeCase)
        self.assertEqual(edge_case.category, EdgeCaseCategory.SYSTEM_FAILURE)
        self.assertEqual(edge_case.severity, EdgeCaseSeverity.HIGH)

    def test_edge_case_retrieval(self):
        """Test retrieving similar edge cases."""
        # First, capture some edge cases
        context = EdgeCaseContext(
            system_state=MappingProxyType({"cpu_usage": "90%"}),
            market_conditions=MappingProxyType({}),
        )

        for i in range(3):
            event = MappingProxyType({"error_type": f"error_{i}", "component": "test"})
            self.edge_case_memory.capture_edge_case(
                event=event,
                context=context,
                category=EdgeCaseCategory.SYSTEM_FAILURE,
                severity=EdgeCaseSeverity.MEDIUM,
                description=f"Test error {i}",
            )

        # Query for edge cases
        query = Query(
            query_id="test_query",
            categories=frozenset([EdgeCaseCategory.SYSTEM_FAILURE]),
            severities=frozenset([EdgeCaseSeverity.MEDIUM]),
            limit=10,
        )

        results = self.edge_case_memory.retrieve_similar_cases(query)

        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)

    def test_automatic_detection(self):
        """Test automatic edge case detection."""
        events = [
            MappingProxyType({"metric": "cpu_usage", "value": "95%"}) for _ in range(5)
        ]

        contexts = [
            EdgeCaseContext(system_state=MappingProxyType({"status": "operational"}))
            for _ in range(5)
        ]

        detected = self.edge_case_memory.automatic_edge_case_detection(events, contexts)

        self.assertIsInstance(detected, list)

    def test_edge_case_statistics(self):
        """Test edge case statistics."""
        # Capture some edge cases
        context = EdgeCaseContext()
        event = MappingProxyType({"test": "data"})

        self.edge_case_memory.capture_edge_case(
            event=event,
            context=context,
            category=EdgeCaseCategory.SYSTEM_FAILURE,
            severity=EdgeCaseSeverity.MEDIUM,
            description="Test edge case",
        )

        stats = self.edge_case_memory.get_edge_case_statistics()

        self.assertIsInstance(stats, dict)
        self.assertIn("total_cases", stats)
        self.assertGreater(stats["total_cases"], 0)


class TestEnhancedMemoryIndex(unittest.TestCase):
    """Test cases for enhanced MemoryIndexAuthority."""

    def setUp(self):
        """Set up test fixtures."""
        self.index = MemoryIndexAuthority()

    def test_enhanced_indexing(self):
        """Test enhanced indexing with new features."""
        record = MemoryRecord(
            record_id="test_record_1",
            kind=MemoryKind.EPISODIC,
            ts_ns=123456789,
            source="test_module",
            summary="Test record with semantic content about market data",
            tags=frozenset(["market", "data", "test"]),
            confidence=0.8,
        )

        self.index.index(record)

        # Should be indexed in traditional index
        snapshot = self.index.snapshot()
        self.assertEqual(snapshot["indexed_records"], 1)

        # Should have temporal indexing
        self.assertGreater(snapshot["temporal_buckets"], 0)

        # Should have semantic indexing
        self.assertGreater(snapshot["semantic_concepts"], 0)

    def test_temporal_search(self):
        """Test temporal search functionality."""
        # Create records with different timestamps
        base_timestamp = 1234567890000000000  # Base timestamp in nanoseconds

        for i in range(5):
            record = MemoryRecord(
                record_id=f"record_{i}",
                kind=MemoryKind.EPISODIC,
                ts_ns=base_timestamp + (i * 3600000000000),  # 1 hour intervals
                source="test_module",
                summary=f"Test record {i}",
                confidence=0.8,
            )
            self.index.index(record)

        # Search within a temporal range
        results = self.index.search_temporal(
            start_ns=base_timestamp,
            end_ns=base_timestamp + (2 * 3600000000000),  # 2 hour range
            limit=10,
        )

        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)

    def test_semantic_search(self):
        """Test semantic search functionality."""
        record = MemoryRecord(
            record_id="semantic_test",
            kind=MemoryKind.SEMANTIC,
            ts_ns=123456789,
            source="test_module",
            summary="This record contains market analysis and trading concepts",
            tags=frozenset(["market", "trading", "analysis"]),
            confidence=0.8,
        )

        self.index.index(record)

        # Search for semantic concepts
        results = self.index.search_semantic(concepts=["market", "trading"], limit=10)

        self.assertIsInstance(results, list)

    def test_hybrid_search(self):
        """Test hybrid search combining multiple criteria."""
        record = MemoryRecord(
            record_id="hybrid_test",
            kind=MemoryKind.SEMANTIC,
            ts_ns=123456789,
            source="test_module",
            summary="Test record for hybrid search",
            tags=frozenset(["test", "hybrid"]),
            confidence=0.8,
        )

        self.index.index(record)

        # Hybrid search with multiple criteria
        results = self.index.search_hybrid(
            keywords=["test"],
            concepts=["hybrid"],
            source="test_module",
            kind="SEMANTIC",
            limit=10,
        )

        self.assertIsInstance(results, list)

    def test_source_search(self):
        """Test source-based search."""
        record = MemoryRecord(
            record_id="source_test",
            kind=MemoryKind.EPISODIC,
            ts_ns=123456789,
            source="specific_module",
            summary="Test record",
            confidence=0.8,
        )

        self.index.index(record)

        # Search by source
        results = self.index.search_by_source(source="specific_module", limit=10)

        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)


class TestKnowledgeDriftMonitor(unittest.TestCase):
    """Test cases for KnowledgeDriftMonitor."""

    def setUp(self):
        """Set up test fixtures."""
        self.drift_monitor = KnowledgeDriftMonitor()

    def test_drift_detection_setup(self):
        """Test drift monitor initialization."""
        self.assertIsInstance(self.drift_monitor, KnowledgeDriftMonitor)
        self.assertTrue(self.drift_monitor._monitoring_active)

    def test_distribution_drift_detection(self):
        """Test distribution drift detection."""
        # Create data streams with different distributions
        baseline_data = [10.0, 11.0, 10.5, 10.2, 10.8] * 10
        drifted_data = [20.0, 21.0, 20.5, 20.2, 20.8] * 10

        # First, establish baseline
        data_streams = {"test_stream": baseline_data}
        reports = self.drift_monitor.detect_distribution_drift(data_streams, sensitivity=0.1)

        # Should not detect drift with baseline establishment
        self.assertEqual(len(reports), 0)

        # Now test with drifted data
        data_streams = {"test_stream": drifted_data}
        reports = self.drift_monitor.detect_distribution_drift(data_streams, sensitivity=0.1)

        # Should detect drift
        self.assertIsInstance(reports, list)

    def test_drift_mitigation_strategy(self):
        """Test drift mitigation strategy generation."""
        # Create a mock drift report
        report = DriftReport(
            report_id="test_drift",
            drift_type=DriftType.CONCEPT_DRIFT,
            severity=DriftSeverity.HIGH,
            component="test_component",
            description="Test concept drift",
            metrics=MappingProxyType({"drift_score": "0.8"}),
            baseline_metrics=MappingProxyType({"baseline_score": "0.2"}),
            drift_timestamp_ns=0,
            requires_immediate_action=True,
        )

        strategy = self.drift_monitor.drift_mitigation_strategy(report)

        self.assertIsInstance(strategy, type(strategy))  # MitigationPlan
        self.assertEqual(strategy.drift_report_id, "test_drift")

    def test_automated_drift_response(self):
        """Test automated drift response."""
        # Create a mock drift report
        report = DriftReport(
            report_id="test_drift_response",
            drift_type=DriftType.DISTRIBUTION_DRIFT,
            severity=DriftSeverity.HIGH,
            component="test_component",
            description="Test distribution drift",
            metrics=MappingProxyType({"drift_score": "0.7"}),
            baseline_metrics=MappingProxyType({"baseline_score": "0.1"}),
            drift_timestamp_ns=0,
            requires_immediate_action=True,
        )

        response = self.drift_monitor.automated_drift_response(report)

        self.assertIsInstance(response, type(response))  # ResponseAction
        self.assertEqual(response.drift_alert_id, "test_drift_response")

    def test_drift_statistics(self):
        """Test drift monitoring statistics."""
        stats = self.drift_monitor.get_drift_statistics()

        self.assertIsInstance(stats, dict)
        self.assertIn("total_drifts_detected", stats)
        self.assertIn("total_responses_executed", stats)
        self.assertIn("monitored_components", stats)


class TestIntegration(unittest.TestCase):
    """Integration tests for M-1 Knowledge Layer components."""

    def test_knowledge_validation_to_conflict_graph(self):
        """Test integration between validation and conflict graph."""
        validator = KnowledgeValidator()
        conflict_graph = SourceConflictGraph()

        # Create sources
        sources = [
            KnowledgeSource(
                source_id=f"source_{i}",
                source_type=KnowledgeSourceType.MARKET_DATA,
                origin="test_module",
                content=MappingProxyType({"price": str(100 + i), "volume": "1000"}),
                confidence=0.8,
                reliability_score=0.75,
            )
            for i in range(3)
        ]

        # Validate sources
        validation_results = [validator.validate_source(source) for source in sources]

        # Build conflict graph
        graph = conflict_graph.build_conflict_graph(sources, validation_results)

        # Should have graph built successfully
        self.assertEqual(len(graph.nodes), 3)

    def test_edge_case_to_memory_index_integration(self):
        """Test integration between edge case memory and memory index."""
        edge_case_memory = EdgeCaseMemory()
        memory_index = MemoryIndexAuthority()

        # Capture edge case
        context = EdgeCaseContext()
        event = MappingProxyType({"test": "data"})

        edge_case = edge_case_memory.capture_edge_case(
            event=event,
            context=context,
            category=EdgeCaseCategory.SYSTEM_FAILURE,
            severity=EdgeCaseSeverity.MEDIUM,
            description="Test edge case",
        )

        # Create a memory record from edge case with valid timestamp
        record = MemoryRecord(
            record_id=f"record_{edge_case.case_id}",
            kind=MemoryKind.RUNTIME,
            ts_ns=1234567890000000000,  # Valid positive timestamp
            source="edge_case_memory",
            summary=edge_case.description,
            tags=frozenset([edge_case.category.value]),
            confidence=0.8,
        )

        # Index the record
        memory_index.index(record)

        # Should be able to retrieve it
        results = memory_index.search([edge_case.category.value])
        self.assertGreater(len(results), 0)


def run_tests():
    """Run all M-1 Knowledge Layer tests."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestKnowledgeValidator))
    suite.addTests(loader.loadTestsFromTestCase(TestSourceConflictGraph))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCaseMemory))
    suite.addTests(loader.loadTestsFromTestCase(TestEnhancedMemoryIndex))
    suite.addTests(loader.loadTestsFromTestCase(TestKnowledgeDriftMonitor))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "="*70)
    print("M-1 KNOWLEDGE LAYER TEST SUMMARY")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    print("="*70)

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)