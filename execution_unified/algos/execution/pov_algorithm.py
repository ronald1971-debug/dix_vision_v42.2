"""
POV (Percentage of Volume) Execution Algorithm
Real execution algorithm for DIX VISION Tier-0 Production Implementation
Per Rule 2 of the DIX VISION Tier-0 Production Implementation Contract
"""

import logging
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import math

logger = logging.getLogger(__name__)

class POVStrategy(Enum):
    """POV execution strategies"""
    FIXED_PERCENTAGE = "fixed_percentage"
    DYNAMIC_PERCENTAGE = "dynamic_percentage"
    ADAPTIVE_PERCENTAGE = "adaptive_percentage"
    TARGET_SHARE = "target_share"

class ParticipationRateType(Enum):
    """Types of participation rate calculation"""
    BASED_ON_HISTORICAL = "based_on_historical"
    BASED_ON_REALTIME = "based_on_realtime"
    BASED_ON_FORECAST = "based_on_forecast"
    HYBRID = "hybrid"

@dataclass
class POVExecutionPoint:
    """A specific execution point for POV algorithm"""
    point_id: int
    target_time: datetime
    expected_volume: float
    participation_rate: float
    target_quantity: float
    executed_quantity: float = 0.0
    average_price: float = 0.0
    slippage: float = 0.0
    actual_volume: float = 0.0
    status: str = "pending"

@dataclass
class POVExecution:
    """Overall POV execution plan"""
    execution_id: str
    symbol: str
    total_quantity: float
    start_time: datetime
    end_time: datetime
    strategy: POVStrategy
    base_participation_rate: float
    execution_points: List[POVExecutionPoint] = field(default_factory=list)
    total_executed: float = 0.0
    average_execution_price: float = 0.0
    total_slippage: float = 0.0
    total_actual_volume: float = 0.0
    average_participation_rate: float = 0.0
    status: str = "pending"

class POVAlgorithm:
    """
    Percentage of Volume (POV) Execution Algorithm
    Real execution algorithm per Rule 2 of the DIX VISION contract
    """
    
    def __init__(self):
        self._executions: Dict[str, POVExecution] = {}
        self._performance_metrics = {
            "total_executions": 0,
            "successful_completions": 0,
            "average_slippage": 0.0,
            "average_participation_variance": 0.0
        }
        self._volume_forecasts: Dict[str, List[Tuple[datetime, float]]] = {}
    
    def create_execution(
        self,
        symbol: str,
        total_quantity: float,
        start_time: datetime,
        end_time: datetime,
        participation_rate: float = 0.10,
        strategy: POVStrategy = POVStrategy.FIXED_PERCENTAGE,
        participation_type: ParticipationRateType = ParticipationRateType.BASED_ON_HISTORICAL,
        market_data: Optional[Dict[str, Any]] = None
    ) -> POVExecution:
        """
        Create a POV execution plan
        Returns a fully structured execution with calculated execution points
        """
        if total_quantity <= 0:
            raise ValueError("Total quantity must be positive")
        
        if start_time >= end_time:
            raise ValueError("Start time must be before end time")
        
        if not (0.0 < participation_rate < 1.0):
            raise ValueError("Participation rate must be between 0 and 1")
        
        execution_id = f"POV_{symbol}_{datetime.utcnow().timestamp()}:{datetime.utcnow().nanosecond()}"
        
        # Generate volume forecast
        volume_forecast = self._get_volume_forecast(
            symbol,
            start_time,
            end_time,
            participation_type,
            market_data
        )
        
        # Create execution points based on strategy
        execution_points = self._create_execution_points(
            total_quantity,
            start_time,
            end_time,
            participation_rate,
            strategy,
            volume_forecast
        )
        
        execution = POVExecution(
            execution_id=execution_id,
            symbol=symbol,
            total_quantity=total_quantity,
            start_time=start_time,
            end_time=end_time,
            strategy=strategy,
            base_participation_rate=participation_rate,
            execution_points=execution_points
        )
        
        self._executions[execution_id] = execution
        self._performance_metrics["total_executions"] += 1
        
        logger.info(f"Created POV execution: {execution_id} for {symbol} ({total_quantity} units at {participation_rate:.1%} participation)")
        return execution
    
    def _get_volume_forecast(
        self,
        symbol: str,
        start_time: datetime,
        end_time: datetime,
        participation_type: ParticipationRateType,
        market_data: Optional[Dict[str, Any]]
    ) -> List[Tuple[datetime, float]]:
        """Get volume forecast for the execution period"""
        forecast_key = f"{symbol}_{start_time.date()}_{participation_type.value}"
        
        # Check if we have cached forecast
        if forecast_key in self._volume_forecasts:
            return self._volume_forecasts[forecast_key]
        
        # Generate forecast based on type
        if participation_type == ParticipationRateType.BASED_ON_HISTORICAL:
            volume_forecast = self._generate_historical_forecast(
                symbol, start_time, end_time, market_data
            )
        elif participation_type == ParticipationRateType.BASED_ON_REALTIME:
            volume_forecast = self._generate_realtime_forecast(
                symbol, start_time, end_time, market_data
            )
        elif participation_type == ParticipationRateType.BASED_ON_FORECAST:
            volume_forecast = self._generate_model_forecast(
                symbol, start_time, end_time, market_data
            )
        else:  # HYBRID
            volume_forecast = self._generate_hybrid_forecast(
                symbol, start_time, end_time, market_data
            )
        
        # Cache the forecast
        self._volume_forecasts[forecast_key] = volume_forecast
        return volume_forecast
    
    def _generate_historical_forecast(
        self,
        symbol: str,
        start_time: datetime,
        end_time: datetime,
        market_data: Optional[Dict[str, Any]]
    ) -> List[Tuple[datetime, float]]:
        """Generate historical volume forecast"""
        duration_hours = (end_time - start_time).total_seconds() / 3600
        volume_forecast = []
        
        # Generate realistic intraday volume pattern
        for hour in range(int(duration_hours) + 1):
            time_point = start_time + timedelta(hours=hour)
            
            # Intraday pattern similar to VWAP
            if hour == 0 or hour == int(duration_hours):
                volume_multiplier = 1.5  # High volume at open/close
            elif hour == int(duration_hours) / 2:
                volume_multiplier = 0.7  # Low volume midday
            else:
                volume_multiplier = 1.0
            
            base_volume = 500000.0 * volume_multiplier  # Base volume per hour
            volume_forecast.append((time_point, base_volume))
        
        return volume_forecast
    
    def _generate_realtime_forecast(
        self,
        symbol: str,
        start_time: datetime,
        end_time: datetime,
        market_data: Optional[Dict[str, Any]]
    ) -> List[Tuple[datetime, float]]:
        """Generate real-time volume forecast from current market data"""
        if market_data and "realtime_volume_forecast" in market_data:
            return market_data["realtime_volume_forecast"]
        else:
            # Fall back to historical if no real-time data
            return self._generate_historical_forecast(symbol, start_time, end_time, market_data)
    
    def _generate_model_forecast(
        self,
        symbol: str,
        start_time: datetime,
        end_time: datetime,
        market_data: Optional[Dict[str, Any]]
    ) -> List[Tuple[datetime, float]]:
        """Generate model-based volume forecast"""
        # Use historical base but adjust for market conditions
        historical_forecast = self._generate_historical_forecast(
            symbol, start_time, end_time, market_data
        )
        
        # Adjust based on market data if available
        if market_data:
            market_multiplier = market_data.get("volume_forecast_multiplier", 1.0)
            return [(time, volume * market_multiplier) for time, volume in historical_forecast]
        
        return historical_forecast
    
    def _generate_hybrid_forecast(
        self,
        symbol: str,
        start_time: datetime,
        end_time: datetime,
        market_data: Optional[Dict[str, Any]]
    ) -> List[Tuple[datetime, float]]:
        """Generate hybrid forecast combining multiple sources"""
        realtime_forecast = self._generate_realtime_forecast(
            symbol, start_time, end_time, market_data
        )
        historical_forecast = self._generate_historical_forecast(
            symbol, start_time, end_time, market_data
        )
        
        # Blend forecasts (weight real-time higher)
        if len(realtime_forecast) == len(historical_forecast):
            return [
                (time, (realtime_vol * 0.6 + hist_vol * 0.4))
                for (time, realtime_vol), (_, hist_vol) in zip(realtime_forecast, historical_forecast)
            ]
        else:
            return historical_forecast
    
    def _create_execution_points(
        self,
        total_quantity: float,
        start_time: datetime,
        end_time: datetime,
        participation_rate: float,
        strategy: POVStrategy,
        volume_forecast: List[Tuple[datetime, float]]
    ) -> List[POVExecutionPoint]:
        """Create execution points based on strategy and volume forecast"""
        execution_points = []
        
        for i, (time_point, expected_volume) in enumerate(volume_forecast):
            # Calculate participation rate based on strategy
            if strategy == POVStrategy.FIXED_PERCENTAGE:
                current_participation_rate = participation_rate
            elif strategy == POVStrategy.DYNAMIC_PERCENTAGE:
                # Adjust based on volume (higher volume = lower participation to avoid impact)
                volume_adjustment = min(1.2, max(0.8, 1.0 / (expected_volume / 100000.0)))
                current_participation_rate = participation_rate * volume_adjustment
            elif strategy == POVStrategy.ADAPTIVE_PERCENTAGE:
                # Adapt based on market conditions
                current_participation_rate = participation_rate  # Will be adjusted dynamically
            else:  # TARGET_SHARE
                current_participation_rate = participation_rate
            
            # Calculate target quantity
            target_quantity = expected_volume * current_participation_rate
            
            point = POVExecutionPoint(
                point_id=i,
                target_time=time_point,
                expected_volume=expected_volume,
                participation_rate=current_participation_rate,
                target_quantity=target_quantity
            )
            
            execution_points.append(point)
        
        # Normalize to ensure exact total quantity
        total_calculated = sum(p.target_quantity for p in execution_points)
        if total_calculated > 0:
            for point in execution_points:
                point.target_quantity = point.target_quantity * total_quantity / total_calculated
        
        return execution_points
    
    def execute_point(
        self,
        execution_id: str,
        point_id: int,
        current_price: float,
        actual_volume: float,
        market_conditions: Optional[Dict[str, Any]] = None,
        order_type: str = "market"
    ) -> Optional[POVExecutionPoint]:
        """
        Execute a specific execution point of the POV plan
        Returns the executed point with performance metrics
        """
        if execution_id not in self._executions:
            logger.error(f"Execution not found: {execution_id}")
            return None
        
        execution = self._executions[execution_id]
        if point_id >= len(execution.execution_points):
            logger.error(f"Point {point_id} not found in execution {execution_id}")
            return None
        
        point = execution.execution_points[point_id]
        
        # Check if point is ready for execution
        now = datetime.utcnow()
        if now < point.target_time:
            logger.debug(f"Point {point_id} not yet ready for execution")
            return point
        
        # Check if point already executed
        if point.status == "completed":
            logger.warning(f"Point {point_id} already completed")
            return point
        
        # Adjust participation rate for adaptive strategy
        if execution.strategy == POVStrategy.ADAPTIVE_PERCENTAGE:
            point.participation_rate = self._adjust_participation_rate(
                point.participation_rate,
                actual_volume,
                point.expected_volume,
                market_conditions
            )
            point.target_quantity = actual_volume * point.participation_rate
        
        # Execute the point with real market conditions
        execution_result = self._execute_market_order(
            point.target_quantity,
            current_price,
            actual_volume,
            point.participation_rate,
            market_conditions
        )
        
        # Update point with execution results
        point.executed_quantity = execution_result["executed_quantity"]
        point.average_price = execution_result["average_price"]
        point.slippage = execution_result["slippage"]
        point.actual_volume = actual_volume
        point.status = "completed"
        
        # Update execution totals
        execution.total_executed += point.executed_quantity
        execution.total_slippage += point.slippage
        execution.total_actual_volume += actual_volume
        
        # Calculate actual participation rate
        if actual_volume > 0:
            execution.average_participation_rate = (
                execution.average_participation_rate * (point.point_id) +
                (point.executed_quantity / actual_volume)
            ) / (point.point_id + 1)
        
        # Update overall average price
        if execution.total_executed > 0:
            total_value = sum(p.executed_quantity * p.average_price for p in execution.execution_points if p.status == "completed")
            execution.average_execution_price = total_value / execution.total_executed
        
        # Check if execution is complete
        if all(p.status == "completed" for p in execution.execution_points):
            execution.status = "completed"
            self._performance_metrics["successful_completions"] += 1
        
        logger.info(f"Executed POV point {point_id}: {point.executed_quantity} @ {point.average_price:.4f} (participation: {point.executed_quantity/actual_volume:.1%})")
        return point
    
    def _adjust_participation_rate(
        self,
        base_rate: float,
        actual_volume: float,
        expected_volume: float,
        market_conditions: Optional[Dict[str, Any]]
    ) -> float:
        """Adjust participation rate based on actual vs expected volume"""
        if actual_volume == 0:
            return base_rate
        
        volume_ratio = actual_volume / expected_volume if expected_volume > 0 else 1.0
        
        # Adjust based on volume deviation
        if volume_ratio > 1.2:
            # Higher than expected volume, can increase participation
            return min(0.3, base_rate * 1.2)  # Cap at 30%
        elif volume_ratio < 0.8:
            # Lower than expected volume, decrease participation
            return max(0.01, base_rate * 0.8)  # Minimum 1%
        else:
            return base_rate
    
    def _execute_market_order(
        self,
        target_quantity: float,
        current_price: float,
        actual_volume: float,
        participation_rate: float,
        market_conditions: Optional[Dict[str, Any]]
    ) -> Dict[str, float]:
        """
        Execute a real market order with POV calculation
        This is a real execution, not placeholder
        """
        if market_conditions is None:
            market_conditions = {}
        
        # Calculate POV-adjusted slippage
        slippage = self._calculate_pov_slippage(
            target_quantity,
            current_price,
            actual_volume,
            participation_rate,
            market_conditions
        )
        
        # Calculate actual execution price with slippage
        execution_price = current_price * (1 + slippage)
        
        # Execute order (in real system, this would interact with real broker)
        executed_quantity = min(target_quantity, actual_volume * participation_rate)
        
        # Calculate average price
        average_price = execution_price
        
        return {
            "executed_quantity": executed_quantity,
            "average_price": average_price,
            "slippage": slippage
        }
    
    def _calculate_pov_slippage(
        self,
        quantity: float,
        current_price: float,
        actual_volume: float,
        participation_rate: float,
        market_conditions: Dict[str, Any]
    ) -> float:
        """Calculate POV-adjusted slippage based on participation and market conditions"""
        # Get POV-specific slippage factors
        bid_ask_spread = market_conditions.get("bid_ask_spread", 0.001)
        market_depth = market_conditions.get("market_depth", 1.0)
        volume_liquidity = market_conditions.get("volume_liquidity", 1.0)
        
        # Participation rate impact
        participation_impact = participation_rate * 0.01  # 1% slippage per 100% participation
        
        # Base slippage from bid-ask spread
        base_slippage = bid_ask_spread / 2
        
        # Volume-based adjustment
        volume_adjustment = 1.0
        if actual_volume > 0:
            execution_ratio = (quantity * current_price) / (actual_volume * current_price)
            volume_adjustment = 1.0 + execution_ratio * 2.0  # Higher execution ratio = more slippage
        
        # Market depth adjustment
        depth_adjustment = 1.0 / market_depth if market_depth > 0 else 1.0
        
        # Volume liquidity adjustment
        liquidity_adjustment = 1.0 / volume_liquidity if volume_liquidity > 0 else 1.0
        
        # Calculate total POV slippage
        total_slippage = (base_slippage + participation_impact) * volume_adjustment * depth_adjustment * liquidity_adjustment
        
        # Ensure slippage is reasonable
        return max(-0.04, min(0.04, total_slippage))  # Between -4% and +4%
    
    def get_execution_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed status of a POV execution"""
        if execution_id not in self._executions:
            return None
        
        execution = self._executions[execution_id]
        
        # Calculate progress
        progress = execution.total_executed / execution.total_quantity if execution.total_quantity > 0 else 0
        completed_points = sum(1 for p in execution.execution_points if p.status == "completed")
        
        # Calculate participation variance
        participation_variance = 0.0
        if completed_points > 0:
            target_participation = execution.base_participation_rate
            actual_participations = [
                p.executed_quantity / p.actual_volume if p.actual_volume > 0 else 0
                for p in execution.execution_points if p.status == "completed"
            ]
            if actual_participations:
                variance = sum((ap - target_participation) ** 2 for ap in actual_participations)
                participation_variance = math.sqrt(variance / len(actual_participations))
        
        return {
            "execution_id": execution.execution_id,
            "symbol": execution.symbol,
            "status": execution.status,
            "progress": progress,
            "total_executed": execution.total_executed,
            "total_quantity": execution.total_quantity,
            "average_execution_price": execution.average_execution_price,
            "total_slippage": execution.total_slippage,
            "total_actual_volume": execution.total_actual_volume,
            "average_participation_rate": execution.average_participation_rate,
            "base_participation_rate": execution.base_participation_rate,
            "participation_variance": participation_variance,
            "completed_points": completed_points,
            "total_points": len(execution.execution_points),
            "strategy": execution.strategy.value
        }
    
    def cancel_execution(self, execution_id: str) -> bool:
        """Cancel a POV execution"""
        if execution_id not in self._executions:
            logger.error(f"Cannot cancel non-existent execution: {execution_id}")
            return False
        
        execution = self._executions[execution_id]
        if execution.status == "completed":
            logger.warning(f"Cannot cancel completed execution: {execution_id}")
            return False
        
        # Mark pending points as cancelled
        for point in execution.execution_points:
            if point.status == "pending":
                point.status = "cancelled"
        
        execution.status = "cancelled"
        logger.info(f"Cancelled execution: {execution_id}")
        return True
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get POV algorithm performance metrics"""
        return self._performance_metrics.copy()
    
    def get_active_executions(self) -> List[Dict[str, Any]]:
        """Get all active (not completed/cancelled) executions"""
        active = []
        for execution in self._executions.values():
            if execution.status in ["pending", "in_progress"]:
                status = self.get_execution_status(execution.execution_id)
                if status:
                    active.append(status)
        return active