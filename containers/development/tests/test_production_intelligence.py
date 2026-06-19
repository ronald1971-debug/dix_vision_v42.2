"""Tests for Production Intelligence Components."""

import unittest
import sys
import os
import time
import numpy as np

# Add paths to imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from intelligence_engine.cognitive.production_intelligence import (
    ProductionPatternRecognition,
    ProductionRiskAssessment,
    ProductionDecisionEngine,
    get_production_decision_engine,
    DecisionType,
    ConfidenceLevel,
    MarketDataPoint,
    DecisionContext,
    CognitiveDecision,
)


class TestProductionPatternRecognition(unittest.TestCase):
    """Test cases for production pattern recognition."""

    def setUp(self):
        """Set up test fixtures."""
        self.pattern_recognition = ProductionPatternRecognition(window_size=100)

    def test_price_pattern_analysis(self):
        """Test real price pattern analysis."""
        current_price = 100.0
        volume = 1000.0

        patterns = self.pattern_recognition.analyze_price_patterns(current_price, volume)

        self.assertIn("momentum", patterns)
        self.assertIn("volatility", patterns)
        self.assertIn("trend", patterns)
        self.assertIn("rsi", patterns)

    def test_pattern_strength_calculation(self):
        """Test pattern strength calculation."""
        # Add some data points
        for i in range(20):
            price = 100.0 + i * 0.5 + (i % 3) * 0.1
            volume = 1000 + i * 10
            self.pattern_recognition.analyze_price_patterns(price, volume)

        patterns = self.pattern_recognition.analyze_price_patterns(105.0, 1200)

        self.assertGreater(patterns["pattern_confidence"], 0.0)
        self.assertLessEqual(patterns["pattern_confidence"], 1.0)

    def test_rsi_calculation(self):
        """Test RSI calculation."""
        # Add enough data points for RSI
        for i in range(30):
            price = 100.0 + i * 0.2 + (i % 5) * 0.5
            self.pattern_recognition.analyze_price_patterns(price, 1000)

        rsi = self.pattern_recognition._calculate_rsi(
            np.array(list(self.pattern_recognition.price_history))
        )

        self.assertGreaterEqual(rsi, 0.0)
        self.assertLessEqual(rsi, 100.0)


class TestProductionRiskAssessment(unittest.TestCase):
    """Test cases for production risk assessment."""

    def setUp(self):
        """Set up test fixtures."""
        self.risk_assessment = ProductionRiskAssessment()

    def test_portfolio_risk_assessment(self):
        """Test portfolio risk assessment."""
        portfolio_state = {
            "total_value": 100000.0,
            "positions": [
                {"value": 30000.0},
                {"value": 20000.0},
                {"value": 10000.0}
            ],
            "volatility": 0.2
        }

        market_data = MarketDataPoint(
            timestamp=time.time(),
            price=100.0,
            volume=1000.0,
            bid=99.5,
            ask=100.5,
            spread=1.0,
            volatility=0.2,
            momentum=0.01,
            trend=0.5,
            support_level=95.0,
            resistance_level=105.0
        )

        risk_metrics = self.risk_assessment.assess_portfolio_risk(portfolio_state, market_data)

        self.assertIn("var_95", risk_metrics)
        self.assertIn("beta", risk_metrics)
        self.assertIn("sharpe_ratio", risk_metrics)
        self.assertIn("max_drawdown", risk_metrics)

    def test_var_calculation(self):
        """Test VaR calculation."""
        portfolio_state = {
            "total_value": 100000.0,
            "volatility": 0.2
        }

        market_data = MarketDataPoint(
            timestamp=time.time(),
            price=100.0,
            volume=1000.0,
            bid=99.5,
            ask=100.5,
            spread=1.0,
            volatility=0.2,
            momentum=0.01,
            trend=0.5,
            support_level=95.0,
            resistance_level=105.0
        )

        var_95 = self.risk_assessment._calculate_var(portfolio_state, market_data, confidence=0.95)
        var_99 = self.risk_assessment._calculate_var(portfolio_state, market_data, confidence=0.99)

        self.assertGreater(var_95, 0.0)
        self.assertGreater(var_99, var_95)  # 99% VaR should be higher

    def test_concentration_risk(self):
        """Test concentration risk calculation."""
        positions = [
            {"value": 80000.0},  # 80% in one position - high concentration
            {"value": 10000.0},
            {"value": 10000.0}
        ]

        concentration = self.risk_assessment._calculate_concentration_risk(positions)

        self.assertGreaterEqual(concentration, 0.0)
        self.assertLessEqual(concentration, 1.0)
        self.assertGreater(concentration, 0.5)  # Should be high due to concentration


class TestProductionDecisionEngine(unittest.TestCase):
    """Test cases for production decision engine."""

    def setUp(self):
        """Set up test fixtures."""
        self.decision_engine = get_production_decision_engine()

    def test_trading_decision(self):
        """Test real trading decision."""
        context = DecisionContext(
            current_time=time.time(),
            market_data=MarketDataPoint(
                timestamp=time.time(),
                price=100.0,
                volume=1000.0,
                bid=99.5,
                ask=100.5,
                spread=1.0,
                volatility=0.2,
                momentum=0.05,  # Positive momentum
                trend=2.0,
                support_level=95.0,
                resistance_level=105.0
            ),
            portfolio_state={"total_value": 100000.0, "positions": [], "volatility": 0.2},
            risk_metrics={"overall_risk_score": 0.4},
            market_conditions={"trend": "upward"},
            historical_performance=[0.01, 0.02, 0.015, 0.03, 0.025],
            available_capital=100000.0
        )

        decision = self.decision_engine.make_production_decision(
            context=context,
            decision_type=DecisionType.TRADING
        )

        self.assertIsInstance(decision, CognitiveDecision)
        self.assertEqual(decision.decision_type, DecisionType.TRADING)
        self.assertIn(decision.action, ["BUY", "SELL", "HOLD"])
        self.assertGreater(decision.confidence, 0.0)
        self.assertLessEqual(decision.confidence, 1.0)

    def test_risk_management_decision(self):
        """Test risk management decision."""
        context = DecisionContext(
            current_time=time.time(),
            market_data=MarketDataPoint(
                timestamp=time.time(),
                price=100.0,
                volume=1000.0,
                bid=99.5,
                ask=100.5,
                spread=1.0,
                volatility=0.15,
                momentum=0.0,
                trend=0.0,
                support_level=95.0,
                resistance_level=105.0
            ),
            portfolio_state={"total_value": 100000.0, "positions": [], "volatility": 0.15},
            risk_metrics={"overall_risk_score": 0.85},  # High risk
            market_conditions={"volatility": "high"},
            historical_performance=[0.01, 0.02, 0.015],
            available_capital=100000.0
        )

        decision = self.decision_engine.make_production_decision(
            context=context,
            decision_type=DecisionType.RISK_MANAGEMENT
        )

        self.assertIsInstance(decision, CognitiveDecision)
        self.assertEqual(decision.decision_type, DecisionType.RISK_MANAGEMENT)
        self.assertIn("REDUCE", decision.action)  # Should recommend reduction

    def test_confidence_level_mapping(self):
        """Test confidence level mapping."""
        test_cases = [
            (0.1, ConfidenceLevel.VERY_LOW),
            (0.3, ConfidenceLevel.LOW),
            (0.5, ConfidenceLevel.MEDIUM),
            (0.7, ConfidenceLevel.HIGH),
            (0.9, ConfidenceLevel.VERY_HIGH)
        ]

        for confidence, expected_level in test_cases:
            result = self.decision_engine._get_confidence_level(confidence)
            self.assertEqual(result, expected_level)

    def test_decision_statistics(self):
        """Test decision statistics."""
        # Generate some decisions
        for i in range(5):
            context = DecisionContext(
                current_time=time.time(),
                market_data=MarketDataPoint(
                    timestamp=time.time(),
                    price=100.0 + i * 10,
                    volume=1000.0,
                    bid=99.5,
                    ask=100.5,
                    spread=1.0,
                    volatility=0.2,
                    momentum=0.01,
                    trend=0.5,
                    support_level=95.0,
                    resistance_level=105.0
                ),
                portfolio_state={"total_value": 100000.0, "positions": [], "volatility": 0.2},
                risk_metrics={"overall_risk_score": 0.4},
                market_conditions={"trend": "upward"},
                historical_performance=[0.01, 0.02, 0.015, 0.03, 0.025],
                available_capital=100000.0
            )

            self.decision_engine.make_production_decision(
                context=context,
                decision_type=DecisionType.TRADING
            )

        stats = self.decision_engine.get_decision_statistics()

        self.assertGreater(stats["total_decisions"], 0)
        self.assertIn("action_distribution", stats)
        self.assertIn("average_confidence", stats)


def run_production_intelligence_tests():
    """Run all production intelligence tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestProductionPatternRecognition))
    suite.addTests(loader.loadTestsFromTestCase(TestProductionRiskAssessment))
    suite.addTests(loader.loadTestsFromTestCase(TestProductionDecisionEngine))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "="*70)
    print("PRODUCTION INTELLIGENCE TEST SUMMARY")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    print("="*70)

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_production_intelligence_tests()
    sys.exit(0 if success else 1)
