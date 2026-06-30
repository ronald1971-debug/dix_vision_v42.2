"""
DIX VISION Extended Multi-Domain Trading Service

Extends multi-domain trading to new asset classes including commodities,
forex, futures, options, and derivatives for broader market coverage.
"""

from __future__ import annotations

import logging
import threading
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
import numpy as np

# Import existing multi-domain trading
import sys
sys.path.insert(0, "c:/dix_vision_v42.2/containers/trading")
from multi_domain_trading import MultiDomainTradingSystem

logger = logging.getLogger(__name__)


@dataclass
class ExtendedAssetClass:
    """Extended asset class configuration."""
    asset_class: str
    market_type: str
    tick_size: float
    contract_size: float
    trading_hours: str
    margin_requirements: Dict[str, float]
    specific_features: List[str]
    supported_strategies: List[str]


@dataclass
class CrossDomainStrategy:
    """Strategy that works across multiple asset classes."""
    strategy_id: str
    strategy_name: str
    applicable_domains: List[str]
    domain_specific_params: Dict[str, Dict[str, float]]
    performance_by_domain: Dict[str, float]
    risk_by_domain: Dict[str, float]


class ExtendedMultiDomainTrading:
    """
    Extended multi-domain trading system with new asset classes.
    
    Supports:
    - Commodities (gold, oil, agricultural products)
    - Forex (currency pairs)
    - Futures (index futures, commodity futures)
    - Options (equity options, futures options)
    - Derivatives (swaps, forwards)
    """
    
    def __init__(self):
        # Initialize existing multi-domain system
        self._multi_domain_system = MultiDomainTradingSystem()
        
        # Extended asset classes
        self._extended_asset_classes: Dict[str, ExtendedAssetClass] = {}
        
        # Cross-domain strategies
        self._cross_domain_strategies: List[CrossDomainStrategy] = []
        
        # Domain-specific adapters
        self._domain_adapters: Dict[str, Any] = {}
        
        self._lock = threading.Lock()
        
        # Initialize extended asset classes
        self._initialize_extended_asset_classes()
        
        logger.info("Extended Multi-Domain Trading initialized")
    
    def _initialize_extended_asset_classes(self):
        """Initialize extended asset classes."""
        # Commodities
        gold = ExtendedAssetClass(
            asset_class="commodities",
            market_type="gold",
            tick_size=0.01,
            contract_size=100.0,
            trading_hours="24/5",
            margin_requirements={"initial": 0.10, "maintenance": 0.05},
            specific_features=["inflation_hedge", "safe_haven", "seasonal_patterns"],
            supported_strategies=["momentum", "mean_reversion", "carry_trade"]
        )
        
        oil = ExtendedAssetClass(
            asset_class="commodities",
            market_type="crude_oil",
            tick_size=0.01,
            contract_size=1000.0,
            trading_hours="24/5",
            margin_requirements={"initial": 0.15, "maintenance": 0.10},
            specific_features=["geopolitical_sensitivity", "storage_costs", "seasonal_demand"],
            supported_strategies=["momentum", "volatility", "seasonal"]
        )
        
        # Forex
        eurusd = ExtendedAssetClass(
            asset_class="forex",
            market_type="eur_usd",
            tick_size=0.0001,
            contract_size=100000.0,
            trading_hours="24/5",
            margin_requirements={"initial": 0.02, "maintenance": 0.01},
            specific_features=["interest_rate_parity", "central_bank_policy", "economic_indicators"],
            supported_strategies=["carry_trade", "momentum", "mean_reversion"]
        )
        
        # Futures
        es_futures = ExtendedAssetClass(
            asset_class="futures",
            market_type="es_futures",
            tick_size=0.25,
            contract_size=50.0,
            trading_hours="extended_hours",
            margin_requirements={"initial": 0.20, "maintenance": 0.15},
            specific_features=["index_tracking", "fair_value_premium", "roll_yield"],
            supported_strategies=["index_arbitrage", "momentum", "volatility"]
        )
        
        # Options
        spy_options = ExtendedAssetClass(
            asset_class="options",
            market_type="spy_options",
            tick_size=0.01,
            contract_size=100.0,
            trading_hours="extended_hours",
            margin_requirements={"initial": 0.20, "maintenance": 0.15},
            specific_features=["implied_volatility", "greeks", "time_decay"],
            supported_strategies=["volatility", "directional", "delta_neutral"]
        )
        
        self._extended_asset_classes = {
            "gold": gold,
            "oil": oil,
            "eurusd": eurusd,
            "es_futures": es_futures,
            "spy_options": spy_options
        }
        
        logger.info(f"Initialized {len(self._extended_asset_classes)} extended asset classes")
    
    def add_cross_domain_strategy(self, strategy_name: str, applicable_domains: List[str],
                               domain_params: Dict[str, Dict[str, float]]) -> CrossDomainStrategy:
        """Add a cross-domain strategy."""
        strategy = CrossDomainStrategy(
            strategy_id=f"cross_{strategy_name}_{int(datetime.now().timestamp())}",
            strategy_name=strategy_name,
            applicable_domains=applicable_domains,
            domain_specific_params=domain_params,
            performance_by_domain={domain: 0.0 for domain in applicable_domains},
            risk_by_domain={domain: 0.0 for domain in applicable_domains}
        )
        
        with self._lock:
            self._cross_domain_strategies.append(strategy)
        
        logger.info(f"Added cross-domain strategy: {strategy_name} for domains: {applicable_domains}")
        
        return strategy
    
    def execute_cross_domain_trade(self, strategy_id: str, domain: str,
                              trade_params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute trade across multiple domains."""
        # Find strategy
        strategy = next((s for s in self._cross_domain_strategies if s.strategy_id == strategy_id), None)
        if not strategy:
            return {"error": "Strategy not found"}
        
        # Check if domain is applicable
        if domain not in strategy.applicable_domains:
            return {"error": f"Strategy not applicable to {domain}"}
        
        # Get domain-specific parameters
        domain_params = strategy.domain_specific_params.get(domain, {})
        
        # Execute trade with domain-specific adaptations
        execution_result = {
            "strategy_id": strategy_id,
            "domain": domain,
            "domain_params": domain_params,
            "execution_status": "simulated",
            "expected_performance": strategy.performance_by_domain.get(domain, 0.0),
            "estimated_risk": strategy.risk_by_domain.get(domain, 0.0),
            "timestamp": datetime.now().isoformat()
        }
        
        return execution_result
    
    def get_extended_domain_status(self) -> Dict[str, Any]:
        """Get status of extended domain trading."""
        with self._lock:
            return {
                "extended_asset_classes": len(self._extended_asset_classes),
                "asset_classes": list(self._extended_asset_classes.keys()),
                "cross_domain_strategies": len(self._cross_domain_strategies),
                "strategies": [s.strategy_name for s in self._cross_domain_strategies],
                "domains_covered": list(set([d for s in self._cross_domain_strategies for d in s.applicable_domains]))
            }


# Global instance
_extended_multi_domain_trading: Optional[ExtendedMultiDomainTrading] = None


def get_extended_multi_domain_trading() -> ExtendedMultiDomainTrading:
    """Get global extended multi-domain trading instance."""
    global _extended_multi_domain_trading
    if _extended_multi_domain_trading is None:
        _extended_multi_domain_trading = ExtendedMultiDomainTrading()
    return _extended_multi_domain_trading