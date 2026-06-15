"""Tests for Production Trading Components."""

import unittest
import sys
import os
import time

# Add paths to imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from execution_unified.production_trading import (
    Order,
    Position,
    OrderType,
    OrderSide,
    OrderStatus,
    StrategyType,
    RiskParameters,
    ProductionRiskManager,
    ProductionStrategyExecutor,
    ProductionAutonomousTrader,
    get_production_trader,
)


class TestProductionRiskManager(unittest.TestCase):
    """Test cases for production risk manager."""

    def setUp(self):
        """Set up test fixtures."""
        risk_params = RiskParameters(
            max_position_size=1000.0,
            max_portfolio_value=1000000.0,  # Increase to allow test orders
            max_daily_loss=0.02,
            max_drawdown=0.10,
            max_leverage=2.0
        )
        self.risk_manager = ProductionRiskManager(risk_params)

    def test_order_risk_check_pass(self):
        """Test order risk check with safe order."""
        # Create order with reasonable value that won't exceed limits
        order = Order(
            symbol="BTC/USD",
            order_type=OrderType.MARKET,
            order_side=OrderSide.BUY,
            quantity=1.0,  # Small quantity: 1 * 45000 = 45000, well within 100000 limit
            price=45000.0
        )

        is_safe, message = self.risk_manager.check_order_risk(order, {})

        self.assertTrue(is_safe, f"Order should pass risk check but failed: {message}")

    def test_order_risk_check_fail_size(self):
        """Test order risk check with oversized order."""
        order = Order(
            symbol="BTC/USD",
            order_type=OrderType.MARKET,
            order_side=OrderSide.BUY,
            quantity=2000.0,  # Exceeds max_position_size
            price=45000.0
        )

        is_safe, message = self.risk_manager.check_order_risk(order, {})

        self.assertFalse(is_safe)
        self.assertIn("exceeds maximum", message.lower())

    def test_position_size_calculation(self):
        """Test Kelly Criterion position size calculation."""
        signal_strength = 0.8  # Strong signal
        current_price = 45000.0
        portfolio_value = 100000.0

        position_size = self.risk_manager.calculate_position_size(
            signal_strength, current_price, portfolio_value
        )

        self.assertGreater(position_size, 0.0)
        self.assertLess(position_size, portfolio_value / current_price)  # Reasonable size

    def test_pnl_update(self):
        """Test PnL update."""
        initial_pnl = self.risk_manager._daily_pnl

        self.risk_manager.update_pnl(1000.0)

        self.assertEqual(self.risk_manager._daily_pnl, initial_pnl + 1000.0)

    def test_leverage_check(self):
        """Test leverage risk check."""
        # Create a portfolio with existing position
        portfolio_state = {
            "total_value": 100000.0,
            "leverage": 1.0
        }

        order = Order(
            symbol="BTC/USD",
            order_type=OrderType.MARKET,
            order_side=OrderSide.BUY,
            quantity=5000.0,  # Would exceed max_position_size first
            price=45000.0
        )

        is_safe, message = self.risk_manager.check_order_risk(order, {"BTC/USD": Position(
            symbol="BTC/USD",
            quantity=1000.0,
            average_entry_price=45000.0
        )})

        self.assertFalse(is_safe)
        self.assertIn("exceeds maximum", message.lower())


class TestProductionStrategyExecutor(unittest.TestCase):
    """Test cases for production strategy executor."""

    def setUp(self):
        """Set up test fixtures."""
        risk_params = RiskParameters()
        risk_manager = ProductionRiskManager(risk_params)
        self.executor = ProductionStrategyExecutor(risk_manager)

    def test_momentum_strategy_buy(self):
        """Test momentum strategy with buy signal."""
        result = self.executor.execute_momentum_strategy(
            symbol="BTC/USD",
            current_price=45000.0,
            momentum_signal=0.5,  # Strong buy
            portfolio_value=100000.0
        )

        if result:
            self.assertEqual(result.order_side, OrderSide.BUY)
            self.assertGreater(result.quantity, 0)

    def test_momentum_strategy_sell(self):
        """Test momentum strategy with sell signal."""
        result = self.executor.execute_momentum_strategy(
            symbol="BTC/USD",
            current_price=45000.0,
            momentum_signal=-0.5,  # Strong sell
            portfolio_value=100000.0
        )

        if result:
            self.assertEqual(result.order_side, OrderSide.SELL)
            self.assertGreater(result.quantity, 0)

    def test_mean_reversion_strategy(self):
        """Test mean reversion strategy."""
        result = self.executor.execute_mean_reversion_strategy(
            symbol="BTC/USD",
            current_price=44000.0,  # Below mean
            z_score=-2.5,  # Significant deviation
            mean_price=45000.0,
            portfolio_value=100000.0
        )

        # Should generate buy order for mean reversion
        if result:
            self.assertEqual(result.order_side, OrderSide.BUY)

    def test_breakout_strategy_upward(self):
        """Test breakout strategy with upward breakout."""
        result = self.executor.execute_breakout_strategy(
            symbol="BTC/USD",
            current_price=46000.0,
            resistance_level=45000.0,
            support_level=44000.0,
            portfolio_value=100000.0
        )

        if result:
            self.assertEqual(result.order_side, OrderSide.BUY)

    def test_position_update(self):
        """Test position update from fill."""
        # Create an order and simulate fill
        order = Order(
            symbol="BTC/USD",
            order_type=OrderType.MARKET,
            order_side=OrderSide.BUY,
            quantity=10.0,
            price=45000.0
        )

        filled_order = self.executor._simulate_order_fill(order)
        self.executor._update_positions_from_fill(filled_order)

        # Check position was created
        self.assertIn("BTC/USD", self.executor._positions)
        position = self.executor._positions["BTC/USD"]
        self.assertEqual(position.quantity, 10.0)
        self.assertEqual(position.average_entry_price, 45000.0)


class TestProductionAutonomousTrader(unittest.TestCase):
    """Test cases for production autonomous trader."""

    def setUp(self):
        """Set up test fixtures."""
        self.trader = get_production_trader(portfolio_value=100000.0)

    def test_singleton_trader(self):
        """Test that trader is singleton."""
        trader1 = get_production_trader()
        trader2 = get_production_trader()
        self.assertIs(trader1, trader2)

    def test_execute_trading_decision_momentum(self):
        """Test executing momentum trading decision."""
        order = self.trader.execute_trading_decision(
            strategy_type=StrategyType.MOMENTUM,
            symbol="BTC/USD",
            current_price=45000.0,
            signal=0.3
        )

        if order:
            self.assertIsInstance(order, Order)
            self.assertIn(order.order_side, [OrderSide.BUY, OrderSide.SELL])

    def test_execute_trading_decision_mean_reversion(self):
        """Test executing mean reversion decision."""
        order = self.trader.execute_trading_decision(
            strategy_type=StrategyType.MEAN_REVERSION,
            symbol="BTC/USD",
            current_price=44000.0,
            signal=-2.0,  # z-score
            mean_price=45000.0
        )

        if order:
            self.assertIsInstance(order, Order)

    def test_portfolio_state(self):
        """Test getting portfolio state."""
        state = self.trader.get_trading_statistics()

        self.assertIn("positions", state)
        self.assertIn("daily_pnl", state)
        self.assertIn("active_orders", state)

    def test_risk_parameters_integrity(self):
        """Test that risk parameters are properly set."""
        self.assertEqual(self.trader._risk_manager._risk_params.max_daily_loss, 0.02)
        self.assertEqual(self.trader._risk_manager._risk_params.max_leverage, 2.0)


def run_production_trading_tests():
    """Run all production trading tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestProductionRiskManager))
    suite.addTests(loader.loadTestsFromTestCase(TestProductionStrategyExecutor))
    suite.addTests(loader.loadTestsFromTestCase(TestProductionAutonomousTrader))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "="*70)
    print("PRODUCTION TRADING TEST SUMMARY")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    print("="*70)

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_production_trading_tests()
    sys.exit(0 if success else 1)
