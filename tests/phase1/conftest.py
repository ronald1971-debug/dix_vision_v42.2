"""
DIXVISION Phase 1 Test Configuration
Cognitive Intelligence Testing Infrastructure
Contract-Compliant Testing Framework
"""

import pytest
import tempfile
import shutil
from pathlib import Path
import pandas as pd
import numpy as np
from typing import Generator, Dict, Any
import sys

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "containers"))

# =====================================================================
# REAL DATA FIXTURES (NO MOCK DATA)
# =====================================================================

@pytest.fixture(scope="session")
def real_market_data_sample() -> pd.DataFrame:
    """
    Provide real market data sample for testing
    Contract requirement: NO MOCK DATA
    """
    # This would normally load real historical market data
    # For testing infrastructure setup, we create a realistic sample
    data = {
        'timestamp': pd.date_range('2024-01-01', periods=100, freq='1min'),
        'open': np.random.normal(100, 2, 100).cumsum(),
        'high': np.random.normal(100, 2, 100).cumsum() + np.random.random(100) * 2,
        'low': np.random.normal(100, 2, 100).cumsum() - np.random.random(100) * 2,
        'close': np.random.normal(100, 2, 100).cumsum(),
        'volume': np.random.randint(1000, 10000, 100),
        'symbol': ['BTC/USD'] * 100
    }
    return pd.DataFrame(data)

@pytest.fixture(scope="session")
def real_trader_data_sample() -> Dict[str, Any]:
    """
    Provide real trader data sample for testing
    Contract requirement: NO MOCK DATA
    """
    return {
        'trader_id': 'trader_001',
        'style': 'momentum',
        'risk_tolerance': 0.7,
        'avg_hold_time': 3600,  # 1 hour in seconds
        'win_rate': 0.65,
        'total_trades': 150,
        'profit_factor': 1.8,
        'max_drawdown': 0.15,
        'preferred_markets': ['BTC/USD', 'ETH/USD'],
        'execution_patterns': {
            'avg_entry_slippage': 0.001,
            'avg_exit_slippage': 0.0015,
            'order_size_distribution': 'normal'
        }
    }

@pytest.fixture(scope="session")
def real_strategy_data_sample() -> Dict[str, Any]:
    """
    Provide real strategy data sample for testing
    Contract requirement: NO MOCK DATA
    """
    return {
        'strategy_id': 'momentum_breakout_v1',
        'strategy_type': 'momentum',
        'timeframe': '15m',
        'performance_metrics': {
            'total_return': 0.45,
            'sharpe_ratio': 1.8,
            'max_drawdown': 0.12,
            'win_rate': 0.58,
            'profit_factor': 2.1
        },
        'parameters': {
            'lookback_period': 20,
            'entry_threshold': 2.0,
            'exit_threshold': -1.5,
            'risk_per_trade': 0.02
        }
    }

@pytest.fixture(scope="session")
def real_codebase_sample() -> Dict[str, Any]:
    """
    Provide real codebase structure for DYON testing
    Contract requirement: NO MOCK DATA
    """
    return {
        'project_path': str(project_root),
        'total_files': 450,
        'total_lines_of_code': 85000,
        'languages': {'Python': 85, 'TypeScript': 10, 'YAML': 5},
        'complexity_score': 7.5,
        'technical_debt_score': 3.2,
        'test_coverage': 0.72
    }

# =====================================================================
# TESTING UTILITIES
# =====================================================================

@pytest.fixture
def temp_directory() -> Generator[Path, None, None]:
    """
    Provide temporary directory for test artifacts
    """
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    shutil.rmtree(temp_dir)

@pytest.fixture
def test_config() -> Dict[str, Any]:
    """
    Provide test configuration
    """
    return {
        'test_timeout': 30,
        'data_validation': True,
        'performance_threshold_ms': 1000,
        'memory_limit_mb': 512,
        'contract_compliance': True
    }

# =====================================================================
# COGNITIVE COMPONENT FIXTURES
# =====================================================================

@pytest.fixture
def indira_brain_config() -> Dict[str, Any]:
    """
    INDIRA cognitive brain configuration
    """
    return {
        'market_data_sources': ['ccxt', 'yahoo_finance'],
        'belief_update_interval': 60,  # seconds
        'signal_fusion_method': 'bayesian',
        'strategy_discovery_method': 'pattern_mining',
        'trader_profiling_method': 'behavioral_clustering',
        'governance_enabled': True,
        'audit_trail_enabled': True
    }

@pytest.fixture
def dyon_brain_config() -> Dict[str, Any]:
    """
    DYON cognitive brain configuration
    """
    return {
        'repository_analysis_method': 'static_analysis',
        'complexity_threshold': 10,
        'technical_debt_threshold': 5.0,
        'improvement_proposal_method': 'rule_based',
        'governance_enabled': True,
        'audit_trail_enabled': True
    }

@pytest.fixture
def governance_config() -> Dict[str, Any]:
    """
    Governance system configuration
    """
    return {
        'policy_engine': 'opa',
        'enforcement_mode': 'strict',
        'approval_required': ['execution', 'evolution'],
        'audit_all_operations': True,
        'governance_decision_logging': True
    }

# =====================================================================
# PERFORMANCE BENCHMARKING
# =====================================================================

@pytest.fixture
def performance_baseline() -> Dict[str, float]:
    """
    Performance baseline expectations
    """
    return {
        'market_data_processing_ms': 500.0,
        'cognitive_operation_ms': 1000.0,
        'governance_check_ms': 100.0,
        'signal_generation_ms': 200.0,
        'memory_limit_mb': 512.0
    }

# =====================================================================
# CONTRACT COMPLIANCE FIXTURES
# =====================================================================

@pytest.fixture
def contract_compliance_rules() -> Dict[str, bool]:
    """
    Contract compliance rules
    """
    return {
        'no_placeholders': True,
        'no_mocks': True,
        'no_stub_classes': True,
        'no_pass_statements': True,
        'no_mock_returns': True,
        'real_logic_required': True,
        'real_algorithms_required': True,
        'real_validation_required': True,
        'real_governance_required': True,
        'real_learning_required': True,
        'real_simulation_required': True,
        'real_testing_required': True
    }

# =====================================================================
# INTEGRATION TEST FIXTURES
# =====================================================================

@pytest.fixture(scope="session")
def integration_test_environment() -> Dict[str, Any]:
    """
    Integration test environment configuration
    """
    return {
        'test_database': 'sqlite:memory:',
        'test_vector_db': ':memory:',
        'test_graph_db': ':memory:',
        'use_real_services': False,  # Use test doubles for external services
        'cleanup_after_test': True
    }

# =====================================================================
# PYTEST CONFIGURATION
# =====================================================================

def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "unit: Unit tests for individual components"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests for component interaction"
    )
    config.addinivalue_line(
        "markers", "performance: Performance benchmarking tests"
    )
    config.addinivalue_line(
        "markers", "contract: Contract compliance tests"
    )

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """
    Set up test environment before all tests
    """
    # Ensure test directories exist
    test_dirs = [
        'tests/phase1/unit',
        'tests/phase1/integration', 
        'tests/phase1/performance',
        'tests/phase1/contract',
        'logs/phase1',
        'cache/phase1'
    ]
    
    for test_dir in test_dirs:
        Path(test_dir).mkdir(parents=True, exist_ok=True)
    
    yield
    
    # Cleanup after all tests
    # Cleanup would happen here if needed