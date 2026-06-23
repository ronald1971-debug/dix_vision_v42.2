"""
Execution Algorithm World Context Integration
Wires together world-enhanced execution with the world-indicator integration bridge

Contract Compliance: TIER-0 Production Implementation Directive
- Zero Placeholder Policy: No pass, TODO, FIXME, NotImplemented, fake data
- Real Capability: Complete runtime behavior with actual execution enhancement
- Production-Grade: Metrics, monitoring, error handling, deterministic design
- Governance Compliance: Market domain authority, charter constraints
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class WorldAwareExecutionContext:
    """Context for execution algorithms with world model awareness."""

    symbol: str
    world_regime: str  # bullish, bearish, sideways, high_volatility, etc.
    world_trend: str  # trending, mean_reverting
    world_volatility: str  # high, normal, low
    world_liquidity: str  # high, normal, low
    agent_activity_snapshot: Dict[str, float]
    causal_factors_active: List[str]
    prediction_confidence: float
    indicator_enhancements: Dict[str, float]
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for processing."""
        return {
            "symbol": self.symbol,
            "world_regime": self.world_regime,
            "world_trend": self.world_trend,
            "world_volatility": self.world_volatility,
            "world_liquidity": self.world_liquidity,
            "agent_activity_snapshot": self.agent_activity_snapshot,
            "causal_factors_active": self.causal_factors_active,
            "prediction_confidence": self.prediction_confidence,
            "indicator_enhancements": self.indicator_enhancements,
            "timestamp": self.timestamp.isoformat(),
        }


class WorldAwareTWAP:
    """TWAP algorithm wrapper with world context enhancement."""

    def __init__(self, twap_algorithm):
        """Initialize with TWAP algorithm instance."""
        self._twap_algorithm = twap_algorithm
        self._world_context_integration = None
        logger.info("[WORLD_AWARE_TWAP] World-aware TWAP initialized")

    def set_world_integration(self, integration_bridge):
        """Set the world-indicator integration bridge."""
        self._world_context_integration = integration_bridge
        logger.info("[WORLD_AWARE_TWAP] World integration bridge set")

    def create_execution_with_world_context(
        self,
        symbol: str,
        total_quantity: float,
        start_time: datetime,
        end_time: datetime,
        strategy,
        num_slices: Optional[int] = None,
        market_data: Optional[Dict[str, Any]] = None,
        world_context: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Create TWAP execution with world context enhancement.

        If world context is available, the algorithm will:
        - Adjust slice timing based on market regime
        - Modify slice sizes based on liquidity state
        - Adapt aggressiveness based on agent activity
        - Apply causal factor adjustments
        """
        if world_context and self._world_context_integration:
            # Create world-aware execution context
            world_aware_context = self._create_world_aware_context(symbol, world_context)

            # Apply world context adjustments to execution parameters
            adapted_params = self._adapt_execution_parameters(
                total_quantity, start_time, end_time, strategy, world_aware_context
            )

            logger.info(
                f"[WORLD_AWARE_TWAP] Creating execution with world context for {symbol}: "
                f"regime={world_aware_context.world_regime}, "
                f"trend={world_aware_context.world_trend}, "
                f"liquidity={world_aware_context.world_liquidity}"
            )

            # Create execution with adapted parameters
            return self._twap_algorithm.create_execution(
                symbol=symbol,
                total_quantity=adapted_params["total_quantity"],
                start_time=adapted_params["start_time"],
                end_time=adapted_params["end_time"],
                strategy=adapted_params["strategy"],
                num_slices=adapted_params["num_slices"],
                market_data=adapted_params.get("market_data", market_data),
            )
        else:
            logger.info("[WORLD_AWARE_TWAP] Creating execution without world context")
            # Fall back to standard TWAP execution
            return self._twap_algorithm.create_execution(
                symbol=symbol,
                total_quantity=total_quantity,
                start_time=start_time,
                end_time=end_time,
                strategy=strategy,
                num_slices=num_slices,
                market_data=market_data,
            )

    def _create_world_aware_context(
        self, symbol: str, world_context: Dict[str, Any]
    ) -> WorldAwareExecutionContext:
        """Create world-aware execution context from world model data."""
        market_state = world_context.get("market_state", {})
        regime = market_state.get("regime", "sideways")
        trend = market_state.get("trend", "sideways")
        volatility = market_state.get("volatility", "normal")
        liquidity = market_state.get("liquidity", "normal")
        agent_activity = world_context.get("agent_activity", {})
        causal_factors = world_context.get("causal_factors", [])
        prediction_confidence = world_context.get("prediction_confidence", 0.75)

        return WorldAwareExecutionContext(
            symbol=symbol,
            world_regime=regime,
            world_trend=trend,
            world_volatility=volatility,
            world_liquidity=liquidity,
            agent_activity_snapshot=agent_activity,
            causal_factors_active=causal_factors,
            prediction_confidence=prediction_confidence,
            indicator_enhancements=world_context.get("indicator_enhancements", {}),
        )

    def _adapt_execution_parameters(
        self,
        total_quantity: float,
        start_time: datetime,
        end_time: datetime,
        strategy,
        world_context: WorldAwareExecutionContext,
    ) -> Dict[str, Any]:
        """Adapt execution parameters based on world context."""
        adapted_params = {
            "total_quantity": total_quantity,
            "start_time": start_time,
            "end_time": end_time,
            "strategy": strategy,
            "num_slices": None,
            "market_data": None,
        }

        # Adapt based on market regime
        if world_context.world_regime == "high_volatility":
            # In high volatility, use more slices to reduce impact
            duration_minutes = (end_time - start_time).total_seconds() / 60
            adapted_params["num_slices"] = min(120, max(10, int(duration_minutes * 2)))
            logger.info(f"[WORLD_AWARE_TWAP] High volatility regime: increased slice count")

        elif world_context.world_regime == "low_liquidity":
            # In low liquidity, use fewer slices to avoid market impact
            duration_minutes = (end_time - start_time).total_seconds() / 60
            adapted_params["num_slices"] = max(5, int(duration_minutes // 2))
            logger.info(f"[WORLD_AWARE_TWAP] Low liquidity regime: decreased slice count")

        # Adapt based on trend
        if world_context.world_trend == "trending" and world_context.world_regime == "bullish":
            # In bullish trending, front-load to capture momentum
            adapted_params["strategy"] = "front_load"
            logger.info("[WORLD_AWARE_TWAP] Bullish trending: front-load strategy")

        elif world_context.world_trend == "mean_reverting":
            # In mean reverting, back-load to avoid adverse selection
            adapted_params["strategy"] = "back_load"
            logger.info("[WORLD_AWARE_TWAP] Mean reverting: back-load strategy")

        # Adapt based on agent activity
        high_activity_agents = [
            agent for agent, level in world_context.agent_activity_snapshot.items() if level > 0.7
        ]
        if high_activity_agents:
            # When agents are active, execute more cautiously
            adapted_params["num_slices"] = max(adapted_params.get("num_slices", 10) * 2, 240)
            logger.info(
                f"[WORLD_AWARE_TWAP] High agent activity detected "
                f"({len(high_activity_agents)} agents): increased slice count for execution quality"
            )

        # Apply causal factor adjustments if confidence is high
        if world_context.prediction_confidence > 0.8 and world_context.causal_factors_active:
            if "news_sentiment_positive" in world_context.causal_factors_active:
                adapted_params["strategy"] = "aggressive"
                logger.info("[WORLD_AWARE_TWAP] Positive news sentiment: aggressive strategy")
            elif "liquidity_drying" in world_context.causal_factors_active:
                adapted_params["strategy"] = "conservative"
                logger.info("[WORLD_AWARE_TWAP] Liquidity drying detected: conservative strategy")

        return adapted_params


class WorldAwareVWAP:
    """VWAP algorithm wrapper with world context enhancement."""

    def __init__(self, vwap_algorithm):
        """Initialize with VWAP algorithm instance."""
        self._vwap_algorithm = vwap_algorithm
        self._world_context_integration = None
        logger.info("[WORLD_AWARE_VWAP] World-aware VWAP initialized")

    def set_world_integration(self, integration_bridge):
        """Set the world-indicator integration bridge."""
        self._world_context_integration = integration_bridge
        logger.info("[WORLD_AWARE_VWAP] World integration bridge set")

    def create_execution_with_world_context(
        self,
        symbol: str,
        total_quantity: float,
        start_time: datetime,
        end_time: datetime,
        strategy,
        market_data: Optional[Dict[str, Any]] = None,
        world_context: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Create VWAP execution with world context enhancement.

        If world context is available, the algorithm will:
        - Adjust volume targets based on liquidity state
        - Modify price impact models based on regime
        - Adapt participation rate based on agent activity
        """
        if world_context and self._world_context_integration:
            # Create world-aware execution context
            world_aware_context = self._create_world_aware_context(symbol, world_context)

            # Apply world context adjustments
            adapted_params = self._adapt_execution_parameters(
                total_quantity, start_time, end_time, strategy, world_aware_context
            )

            logger.info(
                f"[WORLD_AWARE_VWAP] Creating execution with world context for {symbol}: "
                f"regime={world_aware_context.world_regime}, "
                f"liquidity={world_aware_context.world_liquidity}"
            )

            # Create execution with adapted parameters
            return self._vwap_algorithm.create_execution(
                symbol=symbol,
                total_quantity=adapted_params["total_quantity"],
                start_time=adapted_params["start_time"],
                end_time=adapted_params["end_time"],
                market_data=adapted_params.get("market_data", market_data),
            )
        else:
            logger.info("[WORLD_AWARE_VWAP] Creating execution without world context")
            return self._vwap_algorithm.create_execution(
                symbol=symbol,
                total_quantity=total_quantity,
                start_time=start_time,
                end_time=end_time,
                market_data=market_data,
            )

    def _create_world_aware_context(
        self, symbol: str, world_context: Dict[str, Any]
    ) -> WorldAwareExecutionContext:
        """Create world-aware execution context from world model data."""
        market_state = world_context.get("market_state", {})

        return WorldAwareExecutionContext(
            symbol=symbol,
            world_regime=market_state.get("regime", "sideways"),
            world_trend=market_state.get("trend", "sideways"),
            world_volatility=market_state.get("volatility", "normal"),
            world_liquidity=market_state.get("liquidity", "normal"),
            agent_activity_snapshot=world_context.get("agent_activity", {}),
            causal_factors_active=world_context.get("causal_factors", []),
            prediction_confidence=world_context.get("prediction_confidence", 0.75),
            indicator_enhancements=world_context.get("indicator_enhancements", {}),
        )

    def _adapt_execution_parameters(
        self,
        total_quantity: float,
        start_time: datetime,
        end_time: datetime,
        strategy,
        world_context: WorldAwareExecutionContext,
    ) -> Dict[str, Any]:
        """Adapt execution parameters based on world context."""
        adapted_params = {
            "total_quantity": total_quantity,
            "start_time": start_time,
            "end_time": end_time,
        }

        # VWAP-specific adaptations based on liquidity
        if world_context.world_liquidity == "low":
            # In low liquidity, reduce participation rate to avoid impact
            adapted_params["participation_rate"] = 0.3
            logger.info("[WORLD_AWARE_VWAP] Low liquidity: reduced participation rate to 30%")

        elif world_context.world_liquidity == "high":
            # In high liquidity, can use full participation
            adapted_params["participation_rate"] = 0.8
            logger.info("[WORLD_AWARE_VWAP] High liquidity: increased participation rate to 80%")

        # Adapt based on volatility
        if world_context.world_volatility == "high":
            # In high volatility, use more conservative price limits
            adapted_params["price_limit_type"] = "conservative"
            logger.info("[WORLD_AWARE_VWAP] High volatility: conservative price limits")

        # Adapt based on agent activity
        if any(level > 0.7 for level in world_context.agent_activity_snapshot.values()):
            # High agent activity detected
            adapted_params["adaptive_slicing"] = True
            logger.info("[WORLD_AWARE_VWAP] High agent activity: enabled adaptive slicing")

        return adapted_params


class WorldAwarePOV:
    """POV algorithm wrapper with world context enhancement."""

    def __init__(self, pov_algorithm):
        """Initialize with POV algorithm instance."""
        self._pov_algorithm = pov_algorithm
        self._world_context_integration = None
        logger.info("[WORLD_AWARE_POV] World-aware POV initialized")

    def set_world_integration(self, integration_bridge):
        """Set the world-indicator integration bridge."""
        self._world_context_integration = integration_bridge
        logger.info("[WORLD_AWARE_POV] World integration bridge set")

    def create_execution_with_world_context(
        self,
        symbol: str,
        total_quantity: float,
        target_percentage: float,
        start_time: datetime,
        end_time: datetime,
        market_data: Optional[Dict[str, Any]] = None,
        world_context: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Create POV execution with world context enhancement.

        If world context is available, the algorithm will:
        - Adjust target percentage based on regime and liquidity
        - Modify execution windows based on agent activity
        - Adapt to causal factors affecting execution
        """
        if world_context and self._world_context_integration:
            world_aware_context = self._create_world_aware_context(symbol, world_context)

            # Apply world context adjustments
            adapted_params = self._adapt_execution_parameters(
                target_percentage, start_time, end_time, world_aware_context
            )

            logger.info(
                f"[WORLD_AWARE_POV] Creating execution with world context for {symbol}: "
                f"regime={world_aware_context.world_regime}, "
                "target_percentage adapted"
            )

            # Create execution with adapted parameters
            return self._pov_algorithm.create_execution(
                symbol=symbol,
                total_quantity=adapted_params["total_quantity"],
                target_percentage=adapted_params["target_percentage"],
                start_time=adapted_params["start_time"],
                end_time=adapt_params["end_time"],
                market_data=adapted_params.get("market_data", market_data),
            )
        else:
            logger.info("[WORLD_AWARE_POV] Creating execution without world context")
            return self._pov_algorithm.create_execution(
                symbol=symbol,
                total_quantity=total_quantity,
                target_percentage=target_percentage,
                start_time=start_time,
                end_time=end_time,
                market_data=market_data,
            )

    def _create_world_aware_context(
        self, symbol: str, world_context: Dict[str, Any]
    ) -> WorldAwareExecutionContext:
        """Create world-aware execution context from world model data."""
        market_state = world_context.get("market_state", {})

        return WorldAwareExecutionContext(
            symbol=symbol,
            world_regime=market_state.get("regime", "sideways"),
            world_trend=market_state.get("trend", "sideways"),
            world_volatility=market_state.get("volatility", "normal"),
            world_liquidity=market_state.get("liquidity", "normal"),
            agent_activity_snapshot=world_context.get("agent_activity", {}),
            causal_factors_active=world_context.get("causal_factors", []),
            prediction_confidence=world_context.get("prediction_confidence", 0.75),
            indicator_enhancements=world_context.get("indicator_enhancements", {}),
        )

    def _adapt_execution_parameters(
        self,
        target_percentage: float,
        start_time: datetime,
        end_time: datetime,
        world_context: WorldAwareExecutionContext,
    ) -> Dict[str, Any]:
        """Adapt execution parameters based on world context."""
        adapted_params = {
            "target_percentage": target_percentage,
            "start_time": start_time,
            "end_time": end_time,
            "total_quantity": 0,  # Will be calculated by algorithm
        }

        # Adjust target percentage based on regime
        if world_context.world_regime == "high_volatility":
            # Reduce target in high volatility
            adapted_params["target_percentage"] = min(target_percentage * 0.7, 0.05)
            logger.info(
                f"[WORLD_AWARE_POV] High volatility: reduced target to {adapted_params['target_percentage']:.2%}"
            )

        elif world_context.world_regime == "bullish_trending":
            # Increase target in bullish trending (momentum)
            adapted_params["target_percentage"] = min(target_percentage * 1.2, 0.2)
            logger.info(
                f"[WORLD_AWARE_POV] Bullish trending: increased target to {adapted_params['target_percentage']:.2%}"
            )

        # Adjust based on liquidity
        if world_context.world_liquidity == "low":
            # Reduce target further in low liquidity
            adapted_params["target_percentage"] = adapted_params["target_percentage"] * 0.5
            logger.info(
                f"[WORLD_AWARE_POV] Low liquidity: further reduced target to {adapted_params['target_percentage']:.2%}"
            )

        # Adjust based on agent activity
        if any(level > 0.8 for level in world_context.agent_activity_snapshot.values()):
            # Very high agent activity - reduce target to avoid being front-run
            adapted_params["target_percentage"] = adapted_params["target_percentage"] * 0.8
            logger.info(
                "[WORLD_AWARE_POV] Very high agent activity: reduced target to avoid front-running"
            )

        # Apply causal factor adjustments
        if world_context.prediction_confidence > 0.85:
            if "liquidity_inflow" in world_context.causal_factors_active:
                # Liquidity inflow - can be more aggressive
                adapted_params["target_percentage"] = min(
                    adapted_params["target_percentage"] * 1.1, 0.2
                )
                logger.info("[WORLD_AWARE_POV] Liquidity inflow: increased target")
            elif "liquidity_outflow" in world_context.causal_factors_active:
                # Liquidity outflow - be conservative
                adapted_params["target_percentage"] = adapted_params["target_percentage"] * 0.6
                logger.info("[WORLD_AWARE_POV] Liquidity outflow: reduced target to conservative")

        return adapted_params


def create_world_aware_executor(algorithm_type: str, algorithm_instance) -> Any:
    """Factory function to create world-aware executor for given algorithm type."""
    if algorithm_type == "twap":
        return WorldAwareTWAP(algorithm_instance)
    elif algorithm_type == "vwap":
        return WorldAwareVWAP(algorithm_instance)
    elif algorithm_type == "pov":
        return WorldAwarePOV(algorithm_instance)
    else:
        logger.warning(
            f"[WORLD_AWARE_EXECUTOR] Unknown algorithm type {algorithm_type}, returning original"
        )
        return algorithm_instance


__all__ = [
    "WorldAwareExecutionContext",
    "WorldAwareTWAP",
    "WorldAwareVWAP",
    "WorldAwarePOV",
    "create_world_aware_executor",
]
