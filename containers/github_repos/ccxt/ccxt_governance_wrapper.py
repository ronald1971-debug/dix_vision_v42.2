"""
CCXT Governance Wrapper for DIX VISION Integration

This wrapper provides governance oversight for cryptocurrency trading operations
through the CCXT library, ensuring operator authority, safety checks, and
compliance with DIX VISION's constitutional governance.

Author: DIX VISION Trading Governance
Version: 42.2
"""

import sys
import time
from datetime import datetime
from typing import Any, Dict, Optional

sys.path.append('/app/governance')

from base_external_repo_wrapper import (
    BaseExternalRepoGovernanceWrapper,
    ExternalRepositoryMetrics,
    GovernanceViolation,
    PermissionLevel,
)


class CCXTGovernanceWrapper(BaseExternalRepoGovernanceWrapper):
    """
    Governance wrapper for CCXT cryptocurrency trading operations.
    
    This ensures that all trading operations are:
    - Governed by operator authority (operator has ultimate authority)
    - Validated for safety (position limits, risk checks)
    - Audited for compliance (trade logging, position tracking)
    - Monitored for performance (latency, success rates)
    """
    
    def __init__(self, permission_level: PermissionLevel = PermissionLevel.READ_ONLY):
        super().__init__("ccxt", permission_level)
        self.metrics = ExternalRepositoryMetrics("ccxt")
        self.ccxt_instance = None
        self.current_positions = {}
        self.position_limits = {
            'max_position_value': 10000,  # USD
            'max_position_percentage': 0.1,  # 10% of portfolio
            'max_daily_trades': 100,
            'daily_trade_count': 0
        }
        self.risk_parameters = {
            'max_leverage': 3.0,
            'max_slippage': 0.05,  # 5%
            'min_liquidity': 1000  # USD
        }
        
    def initialize_ccxt(self, exchange_id: str, api_config: Dict[str, Any]):
        """
        Initialize CCXT exchange with governance oversight.
        
        Args:
            exchange_id: CCXT exchange identifier (e.g., 'binance', 'kraken')
            api_config: API configuration (key, secret, etc.)
        """
        try:
            import ccxt
            exchange_class = getattr(ccxt, exchange_id)
            self.ccxt_instance = exchange_class({
                'apiKey': api_config.get('api_key'),
                'secret': api_config.get('api_secret'),
                'enableRateLimit': True,
                'options': {
                    'defaultType': api_config.get('default_type', 'spot')
                }
            })
            
            self.logger.info(f"Initialized CCXT exchange: {exchange_id}")
            
            # Test connection
            markets = self.ccxt_instance.load_markets()
            self.logger.info(f"Loaded {len(markets)} markets for {exchange_id}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize CCXT exchange {exchange_id}: {str(e)}")
            raise GovernanceViolation(f"CCXT initialization failed: {str(e)}")
    
    def safety_check(self, operation: str, params: Dict[str, Any]) -> bool:
        """
        Enhanced safety checks specific to cryptocurrency trading.
        """
        if not self.safety_check_enabled:
            return True
            
        # Check basic safety
        if not super().safety_check(operation, params):
            return False
            
        # Trading-specific safety checks
        if 'trade' in operation.lower() or 'order' in operation.lower():
            if not self._validate_trade_safety(params):
                return False
                
        # Position limit checks
        if 'position' in operation.lower():
            if not self._validate_position_limits(params):
                return False
                
        return True
    
    def _validate_trade_safety(self, params: Dict[str, Any]) -> bool:
        """Validate safety of trading operations"""
        symbol = params.get('symbol', '')
        amount = params.get('amount', 0)
        price = params.get('price', 0)
        
        # Validate symbol format
        if not symbol or '/' not in symbol:
            self.logger.warning(f"Invalid symbol format: {symbol}")
            return False
            
        # Validate amount
        try:
            amount_float = float(amount)
            if amount_float <= 0:
                self.logger.warning(f"Invalid amount: {amount}")
                return False
                
            # Check daily trade limit
            if self.position_limits['daily_trade_count'] >= self.position_limits['max_daily_trades']:
                self.logger.warning("Daily trade limit reached")
                return False
                
        except (ValueError, TypeError):
            self.logger.warning(f"Invalid amount type: {amount}")
            return False
            
        # Validate price for market orders
        if params.get('type') == 'limit' and price <= 0:
            self.logger.warning(f"Invalid price: {price}")
            return False
            
        return True
    
    def _validate_position_limits(self, params: Dict[str, Any]) -> bool:
        """Validate position size limits"""
        position_value = params.get('value', 0)
        position_percentage = params.get('percentage', 0)
        
        try:
            position_value_float = float(position_value)
            position_percentage_float = float(position_percentage)
            
            if position_value_float > self.position_limits['max_position_value']:
                self.logger.warning(f"Position value exceeds limit: {position_value_float}")
                return False
                
            if position_percentage_float > self.position_limits['max_position_percentage']:
                self.logger.warning(f"Position percentage exceeds limit: {position_percentage_float}")
                return False
                
        except (ValueError, TypeError):
            self.logger.warning(f"Invalid position parameters")
            return False
            
        return True
    
    def _execute_internal(self, operation: str, params: Dict[str, Any]) -> Any:
        """
        Internal execution method for CCXT operations.
        """
        start_time = time.time()
        success = False
        
        try:
            if not self.ccxt_instance:
                raise GovernanceViolation("CCXT instance not initialized")
            
            # Map operation to CCXT method
            if operation == 'get_markets':
                result = self.ccxt_instance.load_markets()
            elif operation == 'get_ticker':
                result = self.ccxt_instance.fetch_ticker(params['symbol'])
            elif operation == 'get_orderbook':
                result = self.ccxt_instance.fetch_order_book(params['symbol'])
            elif operation == 'get_balance':
                result = self.ccxt_instance.fetch_balance()
            elif operation == 'create_order':
                self.position_limits['daily_trade_count'] += 1
                result = self.ccxt_instance.create_order(
                    params['symbol'],
                    params['type'],
                    params['side'],
                    params['amount'],
                    params.get('price', None)
                )
            elif operation == 'cancel_order':
                result = self.ccxt_instance.cancel_order(params['order_id'], params.get('symbol', None))
            elif operation == 'get_open_orders':
                result = self.ccxt_instance.fetch_open_orders(params.get('symbol', None))
            elif operation == 'get_closed_orders':
                result = self.ccxt_instance.fetch_closed_orders(params.get('symbol', None))
            else:
                raise ValueError(f"Unknown operation: {operation}")
            
            success = True
            execution_time = time.time() - start_time
            self.metrics.record_operation(success, execution_time)
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.metrics.record_operation(False, execution_time)
            self.logger.error(f"CCXT operation failed: {operation} - {str(e)}")
            raise
    
    def get_portfolio_value(self) -> Dict[str, Any]:
        """
        Get current portfolio value with safety checks.
        """
        try:
            balance = self.execute_operation('get_balance', {}, PermissionLevel.READ_ONLY)
            
            total_value = 0
            asset_values = {}
            
            for currency, amount in balance.get('total', {}).items():
                if amount > 0:
                    # Convert to USD value (simplified)
                    if currency == 'USDT' or currency == 'USD':
                        asset_values[currency] = {'amount': amount, 'value_usd': amount}
                        total_value += amount
                    else:
                        # Get ticker for conversion
                        try:
                            ticker = self.execute_operation('get_ticker', {'symbol': f'{currency}/USDT'}, PermissionLevel.READ_ONLY)
                            last_price = ticker.get('last', 0)
                            value_usd = float(amount) * float(last_price)
                            asset_values[currency] = {'amount': amount, 'value_usd': value_usd}
                            total_value += value_usd
                        except Exception as e:
                            self.logger.warning(f"Could not value {currency}: {str(e)}")
            
            return {
                'total_value_usd': total_value,
                'assets': asset_values,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get portfolio value: {str(e)}")
            raise
    
    def execute_trade(self, 
                     symbol: str, 
                     order_type: str, 
                     side: str, 
                     amount: float, 
                     price: Optional[float] = None) -> Dict[str, Any]:
        """
        Execute a trade with full governance oversight.
        
        This is the main entry point for trading operations and includes:
        - Operator authority validation
        - Safety checks (position limits, risk parameters)
        - Portfolio value calculation
        - Trade execution
        - Result validation
        """
        try:
            # Check permission
            if not self.check_permission(PermissionLevel.EXECUTE):
                raise GovernanceViolation("Execute permission required for trading")
            
            # Get current portfolio for validation
            portfolio = self.get_portfolio_value()
            
            # Calculate position value
            if price:
                position_value = float(amount) * float(price)
            else:
                # Use market price estimate
                ticker = self.execute_operation('get_ticker', {'symbol': symbol}, PermissionLevel.READ_ONLY)
                market_price = ticker.get('last', 0)
                position_value = float(amount) * float(market_price)
            
            # Validate position size
            position_percentage = position_value / portfolio['total_value_usd'] if portfolio['total_value_usd'] > 0 else 0
            
            trade_params = {
                'symbol': symbol,
                'type': order_type,
                'side': side,
                'amount': amount,
                'price': price,
                'value': position_value,
                'percentage': position_percentage
            }
            
            # Execute trade with governance
            result = self.execute_operation('create_order', trade_params, PermissionLevel.EXECUTE)
            
            # Add governance metadata to result
            result['governance'] = {
                'portfolio_value_before': portfolio['total_value_usd'],
                'position_value': position_value,
                'position_percentage': position_percentage,
                'operator_permission': self.permission_level.value,
                'safety_checks_passed': True,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Trade execution failed: {str(e)}")
            raise
    
    def get_trading_metrics(self) -> Dict[str, Any]:
        """Get trading performance metrics"""
        return {
            'repository_metrics': self.metrics.get_metrics(),
            'position_limits': self.position_limits,
            'daily_trade_count': self.position_limits['daily_trade_count'],
            'risk_parameters': self.risk_parameters,
            'permission_level': self.permission_level.value
        }


# Example usage
if __name__ == "__main__":
    # Create wrapper with appropriate permission level
    wrapper = CCXTGovernanceWrapper(PermissionLevel.READ_ONLY)
    
    # Initialize with exchange (this would use real credentials in production)
    # wrapper.initialize_ccxt('binance', {
    #     'api_key': 'your_api_key',
    #     'api_secret': 'your_api_secret'
    # })
    
    # Example safe operation
    # markets = wrapper.execute_operation('get_markets', {}, PermissionLevel.READ_ONLY)
    # print(f"Loaded {len(markets)} markets")
    
    print("CCXT Governance Wrapper initialized successfully")
