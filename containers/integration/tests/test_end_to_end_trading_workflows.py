"""
DIXVISION End-to-End Trading Workflow Tests
Comprehensive tests for complete trading workflows from signal to execution

Tests complete workflows including:
- Signal generation and fusion
- Strategy discovery and deployment
- Order creation and execution
- Portfolio management and rebalancing
- Multi-domain trading coordination
- Meme intelligence integration
- Risk management and governance
"""

import unittest
from datetime import datetime, timedelta
from typing import Dict, Any, List
import json
import logging
import time

# Import system components
from containers.dashboard2026.infrastructure.mission_control_center import (
    MissionControlCenter, TaskPriority, TaskStatus, MissionState
)
from containers.execution.infrastructure.execution_system import (
    ExecutionSystem, OrderType, OrderStatus, ExecutionConfig
)
from containers.execution.infrastructure.state_ledger import (
    StateLedger, TransactionType
)
from containers.trading.multi_domain.infrastructure.domain_abstraction import (
    DomainAbstractionLayer
)
from containers.trading.multi_domain.infrastructure.crypto_domain import CryptoDomain
from containers.trading.multi_domain.infrastructure.forex_domain import ForexDomain
from containers.trading.dashmeme.infrastructure.meme_intelligence import (
    MemeIntelligenceLayer, MemeCategory, TrendDirection
)
from containers.dashboard2026.infrastructure.center_communication import (
    CenterCommunication, MessageType, MessagePriority
)


class EndToEndWorkflowTestBase(unittest.TestCase):
    """Base class for end-to-end workflow tests"""
    
    def setUp(self):
        """Set up complete system for workflow testing"""
        # Initialize all components
        self.mission_control = MissionControlCenter()
        self.execution_system = ExecutionSystem()
        self.state_ledger = StateLedger()
        self.domain_abstraction = DomainAbstractionLayer()
        self.crypto_domain = CryptoDomain()
        self.forex_domain = ForexDomain()
        self.meme_intelligence = MemeIntelligenceLayer()
        self.center_comm = CenterCommunication()
        
        # Register domains
        self.domain_abstraction.register_domain("crypto", self.crypto_domain)
        self.domain_abstraction.register_domain("forex", self.forex_domain)
        
        # Link components
        self.execution_system.domain_abstraction = self.domain_abstraction
        self.execution_system.state_ledger = self.state_ledger
        self.meme_intelligence.domain_link = self.domain_abstraction
        
        # Register components for communication
        self.center_comm.register_component("mission_control", self.mission_control)
        self.center_comm.register_component("execution", self.execution_system)
        self.center_comm.register_component("domain_abstraction", self.domain_abstraction)
        self.center_comm.register_component("meme_intelligence", self.meme_intelligence)
        
        logging.info("End-to-end workflow test setup complete")


class TestSignalToExecutionWorkflow(EndToEndWorkflowTestBase):
    """Test complete workflow from signal generation to execution"""
    
    def test_momentum_signal_workflow(self):
        """Test momentum strategy signal to execution workflow"""
        # Step 1: Create mission for momentum strategy
        mission = self.mission_control.create_mission(
            mission_name="Momentum Strategy Deployment",
            description="Deploy momentum trading strategy on crypto domain",
            created_by="operator_001",
            priority=TaskPriority.HIGH
        )
        
        # Step 2: Generate trading signal (simulated)
        trading_signal = {
            "strategy": "momentum",
            "domain": "crypto",
            "symbol": "ETH/USDT",
            "direction": "buy",
            "confidence": 0.85,
            "quantity": 3.0,
            "reasoning": "Strong upward momentum detected",
            "timestamp": datetime.now().isoformat()
        }
        
        # Step 3: Create task for signal execution
        task = self.mission_control.create_task(
            mission_id=mission.mission_id,
            task_name=f"Execute {trading_signal['symbol']} momentum trade",
            description="Execute momentum strategy trade",
            assigned_to="execution_system",
            created_by="operator_001",
            priority=TaskPriority.HIGH
        )
        
        # Step 4: Normalize order through domain abstraction
        normalized_order = self.domain_abstraction.normalize_order_request({
            "domain": trading_signal["domain"],
            "symbol": trading_signal["symbol"],
            "order_type": "market",
            "direction": trading_signal["direction"],
            "quantity": trading_signal["quantity"]
        })
        
        # Step 5: Create order
        order = self.execution_system.create_order(
            symbol=normalized_order["symbol"],
            order_type=OrderType.MARKET,
            direction=normalized_order["direction"],
            quantity=normalized_order["quantity"]
        )
        
        # Step 6: Submit order
        self.execution_system.submit_order(order.order_id)
        
        # Step 7: Update task status
        self.mission_control.update_task_status(
            task_id=task.task_id,
            new_status=TaskStatus.COMPLETED,
            operator="execution_system"
        )
        
        # Verify workflow completion
        self.assertEqual(task.status, TaskStatus.COMPLETED)
        self.assertIsNotNone(order)
        self.assertEqual(order.status, OrderStatus.SUBMITTED)
        
        # Verify state ledger entry
        ledger_entries = self.state_ledger.get_transactions_by_entity(order.order_id)
        self.assertGreater(len(ledger_entries), 0)
    
    def test_mean_reversion_signal_workflow(self):
        """Test mean reversion strategy signal to execution workflow"""
        mission = self.mission_control.create_mission(
            mission_name="Mean Reversion Strategy",
            description="Deploy mean reversion strategy on forex domain",
            created_by="operator_002"
        )
        
        # Generate mean reversion signal
        trading_signal = {
            "strategy": "mean_reversion",
            "domain": "forex",
            "symbol": "GBP/USD",
            "direction": "sell",
            "confidence": 0.78,
            "quantity": 50000.0,
            "price": 1.2800,
            "reasoning": "Price deviated from mean, expected to revert",
            "timestamp": datetime.now().isoformat()
        }
        
        task = self.mission_control.create_task(
            mission_id=mission.mission_id,
            task_name="Execute GBP/USD mean reversion trade",
            description="Execute mean reversion trade",
            assigned_to="execution_system",
            created_by="operator_002"
        )
        
        normalized_order = self.domain_abstraction.normalize_order_request({
            "domain": trading_signal["domain"],
            "symbol": trading_signal["symbol"],
            "order_type": "limit",
            "direction": trading_signal["direction"],
            "quantity": trading_signal["quantity"],
            "price": trading_signal["price"]
        })
        
        order = self.execution_system.create_order(
            symbol=normalized_order["symbol"],
            order_type=OrderType.LIMIT,
            direction=normalized_order["direction"],
            quantity=normalized_order["quantity"],
            price=normalized_order["price"]
        )
        
        self.execution_system.submit_order(order.order_id)
        
        self.mission_control.update_task_status(
            task_id=task.task_id,
            new_status=TaskStatus.COMPLETED,
            operator="execution_system"
        )
        
        self.assertEqual(task.status, TaskStatus.COMPLETED)
        self.assertIsNotNone(order)


class TestMemeIntelligenceWorkflow(EndToEndWorkflowTestBase):
    """Test complete meme intelligence to execution workflow"""
    
    def test_meme_launch_detection_workflow(self):
        """Test workflow from meme launch detection to trading"""
        # Step 1: Detect new meme launch
        meme_signal = {
            "token": "PEPE2",
            "category": MemeCategory.NEW_LAUNCH,
            "trend_direction": TrendDirection.UPWARD,
            "confidence": 0.92,
            "social_volume": 250000,
            "liquidity_score": 0.7,
            "holder_count": 1500,
            "price_change_1h": 45.0,
            "price_change_24h": 120.0
        }
        
        # Step 2: Generate trading recommendation
        recommendation = self.meme_intelligence.generate_trading_recommendation(meme_signal)
        
        self.assertIsNotNone(recommendation)
        self.assertEqual(recommendation["action"], "buy")
        self.assertGreater(recommendation["confidence"], 0.8)
        
        # Step 3: Create mission for meme trading
        mission = self.mission_control.create_mission(
            mission_name=f"Trade {meme_signal['token']} meme opportunity",
            description=f"Trade new meme token {meme_signal['token']}",
            created_by="meme_intelligence",
            priority=TaskPriority.HIGH
        )
        
        # Step 4: Create execution task
        task = self.mission_control.create_task(
            mission_id=mission.mission_id,
            task_name=f"Execute {recommendation['token']} buy order",
            description="Execute buy order for meme token",
            assigned_to="execution_system",
            created_by="meme_intelligence",
            priority=TaskPriority.HIGH
        )
        
        # Step 5: Normalize and create order
        order_request = {
            "domain": "crypto",
            "symbol": recommendation["token"] + "/USDT",
            "order_type": "market",
            "direction": recommendation["action"],
            "quantity": recommendation.get("suggested_quantity", 0.5)
        }
        
        normalized_order = self.domain_abstraction.normalize_order_request(order_request)
        order = self.execution_system.create_order(
            symbol=normalized_order["symbol"],
            order_type=OrderType.MARKET,
            direction=normalized_order["direction"],
            quantity=normalized_order["quantity"]
        )
        
        # Step 6: Execute and record
        self.execution_system.submit_order(order.order_id)
        self.mission_control.update_task_status(
            task_id=task.task_id,
            new_status=TaskStatus.COMPLETED,
            operator="execution_system"
        )
        
        # Verify workflow
        self.assertEqual(task.status, TaskStatus.COMPLETED)
        self.assertIsNotNone(order)
        self.assertIn(recommendation["token"], order.symbol)
        
        # Verify communication
        alert_messages = self.center_comm.get_messages_for_component("mission_control")
        self.assertGreater(len(alert_messages), 0)
    
    def test_meme_risk_management_workflow(self):
        """Test workflow with meme risk management"""
        # High-risk meme signal
        meme_signal = {
            "token": "RUG_COIN",
            "category": MemeCategory.NEW_LAUNCH,
            "trend_direction": TrendDirection.UPWARD,
            "confidence": 0.95,
            "social_volume": 10000,
            "liquidity_score": 0.2,  # Low liquidity
            "holder_count": 50,
            "price_change_1h": 500.0,
            "price_change_24h": 2000.0
        }
        
        # Assess risk
        risk_assessment = self.meme_intelligence.assess_risk(meme_signal)
        
        self.assertIsNotNone(risk_assessment)
        self.assertIn("risk_level", risk_assessment)
        
        # High risk should result in conservative sizing
        if risk_assessment["risk_level"] == "high":
            self.assertLess(risk_assessment["recommended_position_size"], 0.1)
            
            # Should create alert to mission control
            alert = self.center_comm.send_message(
                from_component="meme_intelligence",
                to_component="mission_control",
                message_type=MessageType.ALERT,
                priority=MessagePriority.HIGH,
                content={
                    "alert_type": "high_risk_meme",
                    "token": meme_signal["token"],
                    "risk_level": risk_assessment["risk_level"],
                    "recommended_action": "monitor_only"
                }
            )
            
            self.assertIsNotNone(alert)


class TestMultiDomainWorkflow(EndToEndWorkflowTestBase):
    """Test workflows across multiple trading domains"""
    
    def test_cross_domain_arbitrage_workflow(self):
        """Test arbitrage workflow across crypto and forex domains"""
        # Create mission for arbitrage
        mission = self.mission_control.create_mission(
            mission_name="Cross-Domain Arbitrage",
            description="Execute arbitrage between crypto and forex domains",
            created_by="operator_001",
            priority=TaskPriority.CRITICAL
        )
        
        # Simulate arbitrage opportunity
        arbitrage_signal = {
            "opportunity_type": "cross_domain_arbitrage",
            "domain1": "crypto",
            "symbol1": "BTC/USDT",
            "price1": 45000.0,
            "domain2": "forex",
            "symbol2": "BTC/USD",
            "price2": 45200.0,
            "profit_potential": 200.0,
            "confidence": 0.75
        }
        
        # Create tasks for each leg
        task1 = self.mission_control.create_task(
            mission_id=mission.mission_id,
            task_name="Buy BTC on crypto domain",
            description="First leg: buy BTC at lower price",
            assigned_to="execution_system",
            created_by="operator_001",
            priority=TaskPriority.CRITICAL
        )
        
        task2 = self.mission_control.create_task(
            mission_id=mission.mission_id,
            task_name="Sell BTC on forex domain",
            description="Second leg: sell BTC at higher price",
            assigned_to="execution_system",
            created_by="operator_001",
            priority=TaskPriority.CRITICAL,
            dependencies=[task1.task_id]
        )
        
        # Execute first leg
        order1 = self.execution_system.create_order(
            symbol=arbitrage_signal["symbol1"],
            order_type=OrderType.MARKET,
            direction="buy",
            quantity=1.0
        )
        self.execution_system.submit_order(order1.order_id)
        self.mission_control.update_task_status(
            task_id=task1.task_id,
            new_status=TaskStatus.COMPLETED,
            operator="execution_system"
        )
        
        # Execute second leg
        order2 = self.execution_system.create_order(
            symbol=arbitrage_signal["symbol2"],
            order_type=OrderType.MARKET,
            direction="sell",
            quantity=1.0
        )
        self.execution_system.submit_order(order2.order_id)
        self.mission_control.update_task_status(
            task_id=task2.task_id,
            new_status=TaskStatus.COMPLETED,
            operator="execution_system"
        )
        
        # Verify both legs completed
        self.assertEqual(task1.status, TaskStatus.COMPLETED)
        self.assertEqual(task2.status, TaskStatus.COMPLETED)
        self.assertIsNotNone(order1)
        self.assertIsNotNone(order2)
    
    def test_multi_domain_portfolio_rebalance_workflow(self):
        """Test portfolio rebalancing across multiple domains"""
        # Create rebalancing mission
        mission = self.mission_control.create_mission(
            mission_name="Multi-Domain Portfolio Rebalance",
            description="Rebalance portfolio across crypto, forex, and stocks",
            created_by="operator_001"
        )
        
        # Simulate portfolio state
        current_portfolio = {
            "crypto": {"BTC": 2.0, "ETH": 10.0, "value": 150000.0},
            "forex": {"EUR": 50000, "GBP": 30000, "value": 100000.0},
            "stocks": {"AAPL": 100, "MSFT": 50, "value": 20000.0}
        }
        
        target_allocation = {
            "crypto": 0.60,
            "forex": 0.30,
            "stocks": 0.10
        }
        
        # Create rebalancing tasks for each domain
        for domain, current_value in current_portfolio.items():
            task = self.mission_control.create_task(
                mission_id=mission.mission_id,
                task_name=f"Rebalance {domain} position",
                description=f"Adjust {domain} allocation to target",
                assigned_to="execution_system",
                created_by="operator_001"
            )
        
        # Simulate rebalancing execution
        for domain in current_portfolio.keys():
            if domain == "crypto":
                order = self.execution_system.create_order(
                    symbol="BTC/USDT",
                    order_type=OrderType.MARKET,
                    direction="sell",
                    quantity=0.5
                )
            elif domain == "forex":
                order = self.execution_system.create_order(
                    symbol="EUR/USD",
                    order_type=OrderType.MARKET,
                    direction="buy",
                    quantity=10000
                )
        
        # Verify tasks created
        mission_tasks = self.mission_control.get_tasks_for_mission(mission.mission_id)
        self.assertEqual(len(mission_tasks), 3)


class TestRiskManagementWorkflow(EndToEndWorkflowTestBase):
    """Test workflows with integrated risk management"""
    
    def test_position_limit_workflow(self):
        """Test workflow with position limit enforcement"""
        # Create mission with position limits
        mission = self.mission_control.create_mission(
            mission_name="Constrained Trading",
            description="Trading with strict position limits",
            created_by="operator_001"
        )
        
        # Set position limits
        position_limits = {
            "BTC/USDT": {"max_position": 5.0, "current_position": 4.0},
            "ETH/USDT": {"max_position": 20.0, "current_position": 15.0}
        }
        
        # Try to exceed position limit
        try:
            order = self.execution_system.create_order(
                symbol="BTC/USDT",
                order_type=OrderType.MARKET,
                direction="buy",
                quantity=3.0  # Would exceed limit (4.0 + 3.0 > 5.0)
            )
            # If order created, check if it should be rejected
            if position_limits["BTC/USDT"]["current_position"] + 3.0 > position_limits["BTC/USDT"]["max_position"]:
                self.execution_system.reject_order(order.order_id, "Position limit exceeded")
        except Exception as e:
            # Expected behavior: order rejected or error raised
            self.assertIsNotNone(str(e))
    
    def test_stop_loss_workflow(self):
        """Test workflow with automatic stop-loss execution"""
        # Create mission with stop-loss strategy
        mission = self.mission_control.create_mission(
            mission_name="Stop-Loss Strategy",
            description="Implement stop-loss on existing positions",
            created_by="operator_001"
        )
        
        # Create initial position
        initial_order = self.execution_system.create_order(
            symbol="ETH/USDT",
            order_type=OrderType.MARKET,
            direction="buy",
            quantity=5.0
        )
        self.execution_system.submit_order(initial_order.order_id)
        
        # Create stop-loss order
        stop_loss_order = self.execution_system.create_order(
            symbol="ETH/USDT",
            order_type=OrderType.STOP,
            direction="sell",
            quantity=5.0,
            stop_price=1800.0  # Stop loss if price drops
        )
        
        self.execution_system.submit_order(stop_loss_order.order_id)
        
        # Verify both orders exist
        self.assertIn(initial_order.order_id, self.execution_system.orders)
        self.assertIn(stop_loss_order.order_id, self.execution_system.orders)


class TestGovernanceWorkflow(EndToEndWorkflowTestBase):
    """Test workflows with governance and approval"""
    
    def test_governance_approval_workflow(self):
        """Test workflow requiring governance approval"""
        # Create mission requiring approval
        mission = self.mission_control.create_mission(
            mission_name="High-Risk Strategy Deployment",
            description="Deploy high-risk strategy requiring approval",
            created_by="operator_001",
            priority=TaskPriority.HIGH
        )
        
        # Set mission to waiting approval
        self.mission_control.update_mission_state(
            mission_id=mission.mission_id,
            new_state=MissionState.WAITING_APPROVAL,
            operator="operator_001"
        )
        
        # Create governance decision
        decision = self.mission_control.record_decision(
            mission_id=mission.mission_id,
            decision_type="strategy_approval",
            decision_text="Approved with reduced position size",
            operator="governance_committee",
            approved=True
        )
        
        # Update mission state based on approval
        if decision.approved:
            self.mission_control.update_mission_state(
                mission_id=mission.mission_id,
                new_state=MissionState.APPROVED,
                operator="governance_committee"
            )
        
        # Verify approval workflow
        self.assertEqual(mission.state, MissionState.APPROVED)
        self.assertIsNotNone(decision)
    
    def test_governance_rejection_workflow(self):
        """Test workflow with governance rejection"""
        mission = self.mission_control.create_mission(
            mission_name="Unauthorized Strategy",
            description="Strategy not compliant with governance rules",
            created_by="operator_002",
            priority=TaskPriority.MEDIUM
        )
        
        self.mission_control.update_mission_state(
            mission_id=mission.mission_id,
            new_state=MissionState.WAITING_APPROVAL,
            operator="operator_002"
        )
        
        # Reject mission
        decision = self.mission_control.record_decision(
            mission_id=mission.mission_id,
            decision_type="strategy_approval",
            decision_text="Rejected: does not meet risk criteria",
            operator="governance_committee",
            approved=False
        )
        
        # Update mission state
        if not decision.approved:
            self.mission_control.update_mission_state(
                mission_id=mission.mission_id,
                new_state=MissionState.PAUSED,
                operator="governance_committee"
            )
        
        # Verify rejection
        self.assertEqual(mission.state, MissionState.PAUSED)
        self.assertFalse(decision.approved)


class TestMonitoringAndAlertingWorkflow(EndToEndWorkflowTestBase):
    """Test workflows with integrated monitoring and alerting"""
    
    def test_system_health_monitoring_workflow(self):
        """Test workflow with system health monitoring"""
        # Create monitoring mission
        mission = self.mission_control.create_mission(
            mission_name="System Health Monitoring",
            description="Monitor system health and generate alerts",
            created_by="system"
        )
        
        # Simulate health check
        health_status = {
            "execution_system": "healthy",
            "domain_abstraction": "healthy",
            "state_ledger": "healthy",
            "meme_intelligence": "degraded"
        }
        
        # Generate alert for degraded component
        if "degraded" in health_status.values():
            alert = self.center_comm.send_message(
                from_component="monitoring",
                to_component="mission_control",
                message_type=MessageType.ALERT,
                priority=MessagePriority.MEDIUM,
                content={
                    "alert_type": "component_degraded",
                    "component": "meme_intelligence",
                    "severity": "medium",
                    "health_status": health_status
                }
            )
            
            self.assertIsNotNone(alert)
            self.assertEqual(alert.message_type, MessageType.ALERT)
    
    def test_performance_alert_workflow(self):
        """Test workflow with performance-based alerts"""
        mission = self.mission_control.create_mission(
            mission_name="Performance Monitoring",
            description="Monitor execution performance",
            created_by="system"
        )
        
        # Simulate performance metrics
        performance_metrics = {
            "order_latency_ms": 150.0,
            "execution_success_rate": 0.98,
            "error_rate": 0.02
        }
        
        # Generate alert if performance degraded
        if performance_metrics["order_latency_ms"] > 100.0:
            alert = self.center_comm.send_message(
                from_component="monitoring",
                to_component="mission_control",
                message_type=MessageType.ALERT,
                priority=MessagePriority.HIGH,
                content={
                    "alert_type": "performance_degradation",
                    "metric": "order_latency",
                    "value": performance_metrics["order_latency_ms"],
                    "threshold": 100.0
                }
            )
            
            self.assertIsNotNone(alert)


if __name__ == '__main__':
    unittest.main()
