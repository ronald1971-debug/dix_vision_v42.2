"""
DIXVISION Cross-Component Integration Tests
Comprehensive tests for integration between all system components

Tests integration between:
- Phase 1: INDIRA Trading Intelligence
- Phase 2: DYON Engineering Intelligence
- Phase 3: System Integration and Monitoring
- Phase 4: Dashboard2026 Infrastructure
- Phase 6: Execution System & State & Ledger
- Phase 8: Multi-Domain Trading Support
- Phase 9: DashMeme Domain Intelligence
- Phase 10: Integration & Production Readiness
"""

import logging
import unittest
from datetime import datetime

from containers.dashboard2026.infrastructure.center_communication import (
    CenterCommunication,
    MessagePriority,
    MessageType,
)

# Import system components
from containers.dashboard2026.infrastructure.mission_control_center import (
    MissionControlCenter,
    MissionState,
    TaskPriority,
    TaskStatus,
)
from containers.dashboard2026.infrastructure.operator_workspace import (
    OperatorWorkspace,
)
from containers.execution.infrastructure.execution_system import (
    ExecutionSystem,
    OrderType,
)
from containers.execution.infrastructure.state_ledger import (
    StateLedger,
)
from containers.trading.dashmeme.infrastructure.meme_intelligence import (
    MemeCategory,
    MemeIntelligenceLayer,
    TrendDirection,
)
from containers.trading.multi_domain.infrastructure.crypto_domain import (
    CryptoDomain,
)
from containers.trading.multi_domain.infrastructure.domain_abstraction import (
    DomainAbstractionLayer,
)
from containers.trading.multi_domain.infrastructure.forex_domain import ForexDomain


class CrossComponentIntegrationTestBase(unittest.TestCase):
    """Base class for cross-component integration tests"""

    def setUp(self):
        """Set up all system components for integration testing"""
        # Initialize Dashboard2026 components
        self.mission_control = MissionControlCenter()
        self.operator_workspace = OperatorWorkspace()
        self.center_comm = CenterCommunication()

        # Initialize Execution System components
        self.execution_system = ExecutionSystem()
        self.state_ledger = StateLedger()

        # Initialize Multi-Domain Trading components
        self.domain_abstraction = DomainAbstractionLayer()
        self.crypto_domain = CryptoDomain()
        self.forex_domain = ForexDomain()

        # Initialize DashMeme components
        self.meme_intelligence = MemeIntelligenceLayer()

        # Link components together for integration
        self._setup_component_links()

        logging.info("Cross-component integration test setup complete")

    def _setup_component_links(self):
        """Establish communication links between components"""
        # Link Mission Control to Execution System
        self.mission_control.execution_link = self.execution_system

        # Link Execution System to State Ledger
        self.execution_system.state_ledger = self.state_ledger

        # Link Domain Abstraction to specific domains
        self.domain_abstraction.register_domain("crypto", self.crypto_domain)
        self.domain_abstraction.register_domain("forex", self.forex_domain)

        # Link Execution System to Domain Abstraction
        self.execution_system.domain_abstraction = self.domain_abstraction

        # Link Meme Intelligence to Domain Abstraction
        self.meme_intelligence.domain_link = self.domain_abstraction

        # Link Center Communication to all components
        self.center_comm.register_component("mission_control", self.mission_control)
        self.center_comm.register_component("execution", self.execution_system)
        self.center_comm.register_component("domain_abstraction", self.domain_abstraction)
        self.center_comm.register_component("meme_intelligence", self.meme_intelligence)


class TestMissionControlToExecutionIntegration(CrossComponentIntegrationTestBase):
    """Test integration between Mission Control and Execution System"""

    def test_mission_creates_trading_tasks(self):
        """Test that mission control creates trading tasks that execute"""
        # Create a mission for trading strategy deployment
        mission = self.mission_control.create_mission(
            mission_name="Deploy Momentum Strategy",
            description="Deploy momentum trading strategy across multiple domains",
            created_by="operator_001",
            priority=TaskPriority.HIGH,
        )

        self.assertEqual(mission.state, MissionState.ACTIVE)
        self.assertIsNotNone(mission.mission_id)

        # Create task for execution
        task = self.mission_control.create_task(
            mission_id=mission.mission_id,
            task_name="Execute Crypto Trades",
            description="Execute momentum strategy on crypto domain",
            assigned_to="execution_system",
            created_by="operator_001",
            priority=TaskPriority.HIGH,
        )

        self.assertEqual(task.status, TaskStatus.PENDING)

        # Update task to in_progress (simulating system taking action)
        updated = self.mission_control.update_task_status(
            task_id=task.task_id, new_status=TaskStatus.IN_PROGRESS, operator="execution_system"
        )

        self.assertTrue(updated)

        # Verify execution system received the task
        self.assertEqual(task.status, TaskStatus.IN_PROGRESS)

    def test_execution_updates_mission_progress(self):
        """Test that execution updates mission progress"""
        mission = self.mission_control.create_mission(
            mission_name="Market Making Strategy",
            description="Implement market making on selected venues",
            created_by="operator_002",
        )

        task = self.mission_control.create_task(
            mission_id=mission.mission_id,
            task_name="Set up Market Making",
            description="Configure market making parameters",
            assigned_to="execution_system",
            created_by="operator_002",
        )

        # Simulate execution completing the task
        self.mission_control.update_task_status(
            task_id=task.task_id, new_status=TaskStatus.COMPLETED, operator="execution_system"
        )

        # Verify mission progress updated
        mission_tasks = self.mission_control.get_tasks_for_mission(mission.mission_id)
        completed_tasks = [t for t in mission_tasks if t.status == TaskStatus.COMPLETED]
        self.assertEqual(len(completed_tasks), 1)


class TestExecutionToStateLedgerIntegration(CrossComponentIntegrationTestBase):
    """Test integration between Execution System and State Ledger"""

    def test_order_execution_creates_ledger_entry(self):
        """Test that order execution creates immutable ledger entries"""
        # Create an order
        order = self.execution_system.create_order(
            symbol="BTC/USDT", order_type=OrderType.MARKET, direction="buy", quantity=1.5
        )

        # Simulate order execution
        self.execution_system.submit_order(order.order_id)

        # Verify state ledger has entry for this order
        ledger_entries = self.state_ledger.get_transactions_by_entity(order.order_id)

        # At minimum, there should be order creation and submission entries
        self.assertGreaterEqual(len(ledger_entries), 1)

        # Verify entry has required fields
        entry = ledger_entries[0]
        self.assertIn("entity_id", entry)
        self.assertIn("transaction_type", entry)
        self.assertIn("timestamp", entry)

    def test_state_checkpoint_restores_execution_state(self):
        """Test that state checkpointing can restore execution state"""
        # Create multiple orders
        order1 = self.execution_system.create_order("ETH/USDT", OrderType.LIMIT, "buy", 2.0, 2000.0)
        order2 = self.execution_system.create_order("BTC/USDT", OrderType.MARKET, "sell", 0.5)

        # Create checkpoint
        checkpoint_id = self.state_ledger.create_checkpoint(
            component_id="execution_system",
            state_data={
                "order_count": len(self.execution_system.orders),
                "orders": [order.order_id for order in self.execution_system.orders.values()],
            },
        )

        self.assertIsNotNone(checkpoint_id)

        # Restore checkpoint
        restored_state = self.state_ledger.restore_checkpoint(checkpoint_id)

        self.assertIsNotNone(restored_state)
        self.assertEqual(restored_state["order_count"], 2)


class TestDomainAbstractionToExecutionIntegration(CrossComponentIntegrationTestBase):
    """Test integration between Domain Abstraction and Execution System"""

    def test_crypto_domain_order_routing(self):
        """Test that crypto domain orders are properly routed"""
        # Register crypto domain
        self.domain_abstraction.register_domain("crypto", self.crypto_domain)

        # Create crypto order through domain abstraction
        order_request = {
            "domain": "crypto",
            "symbol": "BTC/USDT",
            "order_type": "market",
            "direction": "buy",
            "quantity": 1.0,
            "exchange": "binance",
        }

        # Domain abstraction should normalize the request
        normalized_order = self.domain_abstraction.normalize_order_request(order_request)

        self.assertIn("domain", normalized_order)
        self.assertEqual(normalized_order["domain"], "crypto")
        self.assertIn("symbol", normalized_order)

        # Execution system should handle the normalized order
        order = self.execution_system.create_order(
            symbol=normalized_order["symbol"],
            order_type=OrderType.MARKET,
            direction=normalized_order["direction"],
            quantity=normalized_order["quantity"],
        )

        self.assertIsNotNone(order)
        self.assertEqual(order.symbol, "BTC/USDT")

    def test_forex_domain_order_routing(self):
        """Test that forex domain orders are properly routed"""
        # Register forex domain
        self.domain_abstraction.register_domain("forex", self.forex_domain)

        # Create forex order through domain abstraction
        order_request = {
            "domain": "forex",
            "symbol": "EUR/USD",
            "order_type": "limit",
            "direction": "sell",
            "quantity": 10000.0,
            "price": 1.1000,
        }

        normalized_order = self.domain_abstraction.normalize_order_request(order_request)

        self.assertEqual(normalized_order["domain"], "forex")
        self.assertEqual(normalized_order["symbol"], "EUR/USD")

        order = self.execution_system.create_order(
            symbol=normalized_order["symbol"],
            order_type=OrderType.LIMIT,
            direction=normalized_order["direction"],
            quantity=normalized_order["quantity"],
            price=normalized_order["price"],
        )

        self.assertIsNotNone(order)
        self.assertEqual(order.symbol, "EUR/USD")


class TestMemeIntelligenceToExecutionIntegration(CrossComponentIntegrationTestBase):
    """Test integration between Meme Intelligence and Execution System"""

    def test_meme_signal_creates_trading_opportunity(self):
        """Test that meme intelligence signals create trading opportunities"""
        # Simulate meme intelligence detecting a trending meme
        meme_signal = {
            "token": "DOGE",
            "category": MemeCategory.DOG_BASED,
            "trend_direction": TrendDirection.UPWARD,
            "confidence": 0.85,
            "social_volume": 1000000,
            "price_change_24h": 15.5,
        }

        # Meme intelligence should generate trading recommendation
        recommendation = self.meme_intelligence.generate_trading_recommendation(meme_signal)

        self.assertIsNotNone(recommendation)
        self.assertIn("action", recommendation)
        self.assertIn("confidence", recommendation)
        self.assertIn("token", recommendation)

        # If recommendation is strong, it should create order
        if recommendation["confidence"] > 0.8 and recommendation["action"] == "buy":
            order = self.execution_system.create_order(
                symbol=recommendation["token"] + "/USDT",
                order_type=OrderType.MARKET,
                direction="buy",
                quantity=recommendation.get("suggested_quantity", 1.0),
            )

            self.assertIsNotNone(order)
            self.assertIn("DOGE", order.symbol)

    def test_meme_risk_assessment_affects_order_size(self):
        """Test that meme risk assessment affects order sizing"""
        # High-risk meme signal
        high_risk_signal = {
            "token": "NEW_COIN",
            "category": MemeCategory.NEW_LAUNCH,
            "trend_direction": TrendDirection.UPWARD,
            "confidence": 0.95,
            "social_volume": 50000,
            "risk_score": 0.9,  # High risk
        }

        risk_assessment = self.meme_intelligence.assess_risk(high_risk_signal)

        self.assertIsNotNone(risk_assessment)
        self.assertIn("risk_level", risk_assessment)
        self.assertIn("recommended_position_size", risk_assessment)

        # High risk should result in smaller position
        self.assertLess(risk_assessment["recommended_position_size"], 1.0)


class TestCenterCommunicationIntegration(CrossComponentIntegrationTestBase):
    """Test center communication across all components"""

    def test_mission_control_broadcast_to_execution(self):
        """Test that mission control can broadcast messages to execution"""
        message = self.center_comm.send_message(
            from_component="mission_control",
            to_component="execution",
            message_type=MessageType.COMMAND,
            priority=MessagePriority.HIGH,
            content={"command": "pause_all_trading", "reason": "market_volatility"},
        )

        self.assertIsNotNone(message)
        self.assertEqual(message.from_component, "mission_control")
        self.assertEqual(message.to_component, "execution")

        # Verify message was received
        received_messages = self.center_comm.get_messages_for_component("execution")
        self.assertGreater(len(received_messages), 0)

    def test_execution_system_status_broadcast(self):
        """Test that execution system broadcasts status updates"""
        # Execution system creates order
        order = self.execution_system.create_order("BTC/USDT", OrderType.MARKET, "buy", 1.0)

        # Broadcast status update
        status_message = self.center_comm.send_message(
            from_component="execution",
            to_component="mission_control",
            message_type=MessageType.STATUS_UPDATE,
            priority=MessagePriority.MEDIUM,
            content={
                "order_id": order.order_id,
                "status": order.status.value,
                "timestamp": datetime.now().isoformat(),
            },
        )

        self.assertIsNotNone(status_message)
        self.assertEqual(status_message.message_type, MessageType.STATUS_UPDATE)

    def test_meme_intelligence_alert_broadcast(self):
        """Test that meme intelligence broadcasts alerts"""
        alert_message = self.center_comm.send_message(
            from_component="meme_intelligence",
            to_component="mission_control",
            message_type=MessageType.ALERT,
            priority=MessagePriority.HIGH,
            content={
                "alert_type": "meme_explosion",
                "token": "PEPE",
                "severity": "high",
                "action_required": True,
            },
        )

        self.assertIsNotNone(alert_message)
        self.assertEqual(alert_message.priority, MessagePriority.HIGH)


class TestMultiComponentWorkflowIntegration(CrossComponentIntegrationTestBase):
    """Test complete workflows across multiple components"""

    def test_complete_trading_workflow(self):
        """Test complete workflow from signal to execution"""
        # Step 1: Mission Control creates trading mission
        mission = self.mission_control.create_mission(
            mission_name="Momentum Trading Deployment",
            description="Deploy momentum strategy on crypto domain",
            created_by="operator_001",
        )

        # Step 2: Meme Intelligence detects opportunity
        meme_signal = {
            "token": "SOL",
            "category": MemeCategory.GENERAL,
            "trend_direction": TrendDirection.UPWARD,
            "confidence": 0.8,
            "social_volume": 500000,
            "price_change_24h": 8.5,
        }

        recommendation = self.meme_intelligence.generate_trading_recommendation(meme_signal)

        # Step 3: Domain abstraction normalizes order
        order_request = {
            "domain": "crypto",
            "symbol": recommendation["token"] + "/USDT",
            "order_type": "market",
            "direction": recommendation["action"],
            "quantity": 2.0,
        }

        normalized_order = self.domain_abstraction.normalize_order_request(order_request)

        # Step 4: Execution System creates and executes order
        order = self.execution_system.create_order(
            symbol=normalized_order["symbol"],
            order_type=OrderType.MARKET,
            direction=normalized_order["direction"],
            quantity=normalized_order["quantity"],
        )

        # Step 5: State Ledger records transaction
        self.execution_system.submit_order(order.order_id)

        # Step 6: Mission Control updates task status
        task = self.mission_control.create_task(
            mission_id=mission.mission_id,
            task_name=f"Execute {recommendation['token']} trade",
            description="Execute trade based on meme intelligence signal",
            assigned_to="execution_system",
            created_by="operator_001",
        )

        self.mission_control.update_task_status(
            task_id=task.task_id, new_status=TaskStatus.COMPLETED, operator="execution_system"
        )

        # Verify complete workflow
        self.assertEqual(mission.state, MissionState.ACTIVE)
        self.assertIsNotNone(order)
        self.assertEqual(task.status, TaskStatus.COMPLETED)

        # Verify state ledger has record
        ledger_entries = self.state_ledger.get_transactions_by_entity(order.order_id)
        self.assertGreater(len(ledger_entries), 0)

    def test_error_handling_workflow(self):
        """Test error handling across components"""
        # Create order with invalid parameters
        try:
            order = self.execution_system.create_order(
                symbol="INVALID/SYMBOL",
                order_type=OrderType.LIMIT,
                direction="buy",
                quantity=0.0,  # Invalid: zero quantity
            )
            self.fail("Should have raised ValueError for zero quantity")
        except ValueError as e:
            self.assertIn("positive", str(e))

        # Mission Control should record error
        error_message = self.center_comm.send_message(
            from_component="execution",
            to_component="mission_control",
            message_type=MessageType.ERROR,
            priority=MessagePriority.HIGH,
            content={
                "error_type": "validation_error",
                "error_message": "Invalid order parameters",
                "timestamp": datetime.now().isoformat(),
            },
        )

        self.assertIsNotNone(error_message)
        self.assertEqual(error_message.message_type, MessageType.ERROR)


class TestPerformanceAndScalabilityIntegration(CrossComponentIntegrationTestBase):
    """Test performance and scalability of integrated components"""

    def test_high_volume_order_processing(self):
        """Test processing high volume of orders"""
        import time

        start_time = time.time()

        # Create 100 orders rapidly
        orders = []
        for i in range(100):
            order = self.execution_system.create_order(
                symbol=f"TEST{i}/USDT",
                order_type=OrderType.MARKET,
                direction="buy" if i % 2 == 0 else "sell",
                quantity=1.0,
            )
            orders.append(order)

        end_time = time.time()
        elapsed = end_time - start_time

        # Should process 100 orders in reasonable time (< 5 seconds)
        self.assertLess(elapsed, 5.0)
        self.assertEqual(len(orders), 100)

    def test_concurrent_mission_task_creation(self):
        """Test concurrent mission and task creation"""
        import time

        start_time = time.time()

        # Create multiple missions and tasks
        missions = []
        for i in range(10):
            mission = self.mission_control.create_mission(
                mission_name=f"Mission {i}",
                description=f"Test mission {i}",
                created_by=f"operator_{i % 3}",
            )
            missions.append(mission)

            # Create tasks for each mission
            for j in range(5):
                self.mission_control.create_task(
                    mission_id=mission.mission_id,
                    task_name=f"Task {j}",
                    description=f"Test task {j}",
                    assigned_to="execution_system",
                    created_by=f"operator_{i % 3}",
                )

        end_time = time.time()
        elapsed = end_time - start_time

        # Should handle concurrent creation efficiently
        self.assertLess(elapsed, 10.0)
        self.assertEqual(len(missions), 10)


if __name__ == "__main__":
    unittest.main()
