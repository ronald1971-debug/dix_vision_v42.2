"""
CCXT Domain Adapter for DIX VISION Integration

This adapter translates CCXT cryptocurrency trading concepts into DIX VISION's
cognitive architecture, ensuring proper domain mapping and data transformation.

Author: DIX VISION Trading Domain Adapter
Version: 42.2
"""

import sys
from datetime import datetime
from typing import Any, Dict, List

sys.path.append('/app/adapters')

from base_domain_adapter import DataFormat, MarketDomainAdapter


class CCXTDomainAdapter(MarketDomainAdapter):
    """
    Domain adapter for CCXT cryptocurrency trading data.
    
    This adapter handles:
    - Exchange-specific concept mapping
    - Order book data transformation
    - Market data standardization
    - Portfolio data integration
    - Trade data cognitive enhancement
    """
    
    def __init__(self):
        super().__init__("ccxt")
        
        # CCXT-specific concept mappings
        self.register_concept_mapping('bid', 'buy_price')
        self.register_concept_mapping('ask', 'sell_price')
        self.register_concept_mapping('base', 'base_currency')
        self.register_concept_mapping('quote', 'quote_currency')
        self.register_concept_mapping('maker', 'liquidity_provider')
        self.register_concept_mapping('taker', 'liquidity_consumer')
        
        # Exchange-specific mappings
        self.exchange_mappings = {
            'binance': 'centralized_exchange_1',
            'kraken': 'centralized_exchange_2',
            'coinbase': 'regulated_exchange_1',
            'poloniex': 'altcoin_exchange_1'
        }
        
    def adapt_orderbook_data(self, orderbook: Dict[str, List], symbol: str) -> Dict[str, Any]:
        """
        Adapt orderbook data to DIX VISION format.
        
        Args:
            orderbook: CCXT orderbook data {bids: [[price, amount]], asks: [[price, amount]]}
            symbol: Trading symbol (e.g., 'BTC/USDT')
        
        Returns:
            Adapted orderbook with DIX VISION cognitive enhancements
        """
        try:
            adapted = {
                'symbol': symbol,
                'timestamp': datetime.utcnow().isoformat(),
                'buy_orders': [],
                'sell_orders': [],
                'market_depth': 0,
                'spread': 0,
                'mid_price': 0,
                'liquidity_score': 0
            }
            
            # Process buy orders (bids)
            for bid in orderbook.get('bids', [])[:20]:  # Top 20 levels
                price, amount = bid
                adapted['buy_orders'].append({
                    'price': float(price),
                    'amount': float(amount),
                    'value': float(price) * float(amount),
                    'type': 'limit_order',
                    'side': 'buy'
                })
            
            # Process sell orders (asks)
            for ask in orderbook.get('asks', [])[:20]:  # Top 20 levels
                price, amount = ask
                adapted['sell_orders'].append({
                    'price': float(price),
                    'amount': float(amount),
                    'value': float(price) * float(amount),
                    'type': 'limit_order',
                    'side': 'sell'
                })
            
            # Calculate market metrics
            if adapted['buy_orders'] and adapted['sell_orders']:
                best_bid = adapted['buy_orders'][0]['price']
                best_ask = adapted['sell_orders'][0]['price']
                adapted['spread'] = best_ask - best_bid
                adapted['mid_price'] = (best_bid + best_ask) / 2
                adapted['spread_percentage'] = (adapted['spread'] / adapted['mid_price']) * 100
                
            # Calculate market depth
            buy_depth = sum(order['value'] for order in adapted['buy_orders'])
            sell_depth = sum(order['value'] for order in adapted['sell_orders'])
            adapted['market_depth'] = buy_depth + sell_depth
            adapted['liquidity_score'] = min(buy_depth, sell_depth) / max(buy_depth, sell_depth) if max(buy_depth, sell_depth) > 0 else 0
            
            return self.enhance_data(adapted, {
                'data_type': 'orderbook',
                'source': 'ccxt',
                'symbol': symbol,
                'cognitive_layer': 'market_intelligence'
            })
            
        except Exception as e:
            self.logger.error(f"Failed to adapt orderbook data: {str(e)}")
            raise
    
    def adapt_ticker_data(self, ticker: Dict[str, Any], symbol: str) -> Dict[str, Any]:
        """
        Adapt ticker data to DIX VISION format.
        
        Args:
            ticker: CCXT ticker data
            symbol: Trading symbol
        
        Returns:
            Adapted ticker with DIX VISION cognitive enhancements
        """
        try:
            adapted = {
                'symbol': symbol,
                'timestamp': datetime.utcnow().isoformat(),
                'current_price': 0,
                'price_change': 0,
                'price_change_percentage': 0,
                'volume': 0,
                'volume_value': 0,
                'high_24h': 0,
                'low_24h': 0,
                'open_24h': 0
            }
            
            # Map CCXT ticker fields to DIX VISION format
            adapted['current_price'] = float(ticker.get('last', ticker.get('close', 0)))
            adapted['price_change'] = float(ticker.get('change', 0))
            adapted['price_change_percentage'] = float(ticker.get('percentage', 0))
            adapted['volume'] = float(ticker.get('baseVolume', ticker.get('volume', 0)))
            adapted['volume_value'] = float(ticker.get('quoteVolume', 0))
            adapted['high_24h'] = float(ticker.get('high', 0))
            adapted['low_24h'] = float(ticker.get('low', 0))
            adapted['open_24h'] = float(ticker.get('open', 0))
            
            # Calculate additional metrics
            if adapted['open_24h'] > 0:
                adapted['price_range_percentage'] = ((adapted['high_24h'] - adapted['low_24h']) / adapted['open_24h']) * 100
            
            # Add market sentiment indicator
            adapted['market_sentiment'] = self._calculate_market_sentiment(adapted)
            
            return self.enhance_data(adapted, {
                'data_type': 'ticker',
                'source': 'ccxt',
                'symbol': symbol,
                'cognitive_layer': 'market_sentiment'
            })
            
        except Exception as e:
            self.logger.error(f"Failed to adapt ticker data: {str(e)}")
            raise
    
    def _calculate_market_sentiment(self, ticker_data: Dict[str, Any]) -> str:
        """Calculate market sentiment based on ticker data"""
        if ticker_data['price_change_percentage'] > 2:
            return 'strong_bullish'
        elif ticker_data['price_change_percentage'] > 0:
            return 'bullish'
        elif ticker_data['price_change_percentage'] > -2:
            return 'bearish'
        else:
            return 'strong_bearish'
    
    def adapt_trade_data(self, trade: Dict[str, Any], symbol: str) -> Dict[str, Any]:
        """
        Adapt trade data to DIX VISION format.
        
        Args:
            trade: CCXT trade data
            symbol: Trading symbol
        
        Returns:
            Adapted trade with DIX VISION cognitive enhancements
        """
        try:
            adapted = {
                'symbol': symbol,
                'trade_id': trade.get('id', ''),
                'timestamp': trade.get('timestamp', datetime.utcnow().timestamp()),
                'datetime': trade.get('datetime', datetime.utcnow().isoformat()),
                'side': trade.get('side', ''),
                'order_type': trade.get('type', ''),
                'price': float(trade.get('price', 0)),
                'amount': float(trade.get('amount', 0)),
                'value': float(trade.get('cost', 0)),
                'fee': float(trade.get('fee', {}).get('cost', 0)) if trade.get('fee') else 0,
                'fee_currency': trade.get('fee', {}).get('currency', '') if trade.get('fee') else ''
            }
            
            # Calculate net trade value
            adapted['net_value'] = adapted['value'] - adapted['fee']
            
            # Add trade classification
            adapted['trade_classification'] = self._classify_trade(adapted)
            
            return self.enhance_data(adapted, {
                'data_type': 'trade',
                'source': 'ccxt',
                'symbol': symbol,
                'cognitive_layer': 'execution_intelligence'
            })
            
        except Exception as e:
            self.logger.error(f"Failed to adapt trade data: {str(e)}")
            raise
    
    def _classify_trade(self, trade: Dict[str, Any]) -> str:
        """Classify trade based on characteristics"""
        if trade['order_type'] == 'market':
            return 'immediate_execution'
        elif trade['order_type'] == 'limit':
            return 'price_optimization'
        elif trade['order_type'] == 'stop':
            return 'risk_management'
        else:
            return 'standard_trade'
    
    def adapt_balance_data(self, balance: Dict[str, Any]) -> Dict[str, Any]:
        """
        Adapt balance data to DIX VISION format.
        
        Args:
            balance: CCXT balance data
        
        Returns:
            Adapted balance with DIX VISION cognitive enhancements
        """
        try:
            adapted = {
                'timestamp': datetime.utcnow().isoformat(),
                'assets': {},
                'total_value_usd': 0,
                'asset_count': 0
            }
            
            for currency, amounts in balance.items():
                if currency == 'info' or currency == 'timestamp':
                    continue
                    
                total = float(amounts.get('total', 0))
                free = float(amounts.get('free', 0))
                used = float(amounts.get('used', 0))
                
                if total > 0:
                    adapted['assets'][currency] = {
                        'total': total,
                        'free': free,
                        'used': used,
                        'utilization_percentage': (used / total * 100) if total > 0 else 0
                    }
                    adapted['asset_count'] += 1
            
            # Calculate portfolio diversity
            adapted['portfolio_diversity'] = adapted['asset_count']
            adapted['asset_utilization'] = sum(asset['utilization_percentage'] for asset in adapted['assets'].values()) / adapted['asset_count'] if adapted['asset_count'] > 0 else 0
            
            return self.enhance_data(adapted, {
                'data_type': 'balance',
                'source': 'ccxt',
                'cognitive_layer': 'portfolio_intelligence'
            })
            
        except Exception as e:
            self.logger.error(f"Failed to adapt balance data: {str(e)}")
            raise
    
    def adapt_data(self, data: Any, source_format: DataFormat) -> Any:
        """
        Main adaptation method for CCXT data.
        """
        # Determine data type and route to appropriate adapter
        if isinstance(data, dict):
            if 'bids' in data and 'asks' in data:
                # Orderbook data
                symbol = data.get('symbol', 'UNKNOWN')
                return self.adapt_orderbook_data(data, symbol)
            elif 'last' in data or 'close' in data:
                # Ticker data
                symbol = data.get('symbol', 'UNKNOWN')
                return self.adapt_ticker_data(data, symbol)
            elif 'side' in data and 'price' in data:
                # Trade data
                symbol = data.get('symbol', 'UNKNOWN')
                return self.adapt_trade_data(data, symbol)
            elif 'total' in data or 'free' in data:
                # Balance data
                return self.adapt_balance_data(data)
        
        # Default adaptation
        return self.enhance_data(data)
    
    def reverse_adapt_data(self, internal_data: Any, target_format: DataFormat) -> Any:
        """
        Reverse adaptation for sending data back to CCXT.
        """
        # Remove DIX VISION enhancements
        if isinstance(internal_data, dict) and 'data' in internal_data:
            data = internal_data['data']
        else:
            data = internal_data
        
        # Reverse concept mappings for order parameters
        if target_format == DataFormat.JSON:
            return self._reverse_json_ccxt_data(data)
        
        return data
    
    def _reverse_json_ccxt_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Reverse JSON CCXT data adaptation"""
        reverse_mappings = {v: k for k, v in self.concept_mappings.items()}
        adapted = {}
        
        for key, value in data.items():
            external_key = reverse_mappings.get(key, key)
            
            # Handle nested structures
            if isinstance(value, dict):
                adapted[external_key] = {reverse_mappings.get(k, k): v for k, v in value.items()}
            elif isinstance(value, list):
                adapted[external_key] = [
                    {reverse_mappings.get(k, k): v for k, v in item.items()} if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                adapted[external_key] = value
        
        return adapted


# Example usage
if __name__ == "__main__":
    adapter = CCXTDomainAdapter()
    
    # Example orderbook adaptation
    sample_orderbook = {
        'bids': [[50000.0, 0.5], [49999.0, 0.3]],
        'asks': [[50001.0, 0.4], [50002.0, 0.2]],
        'symbol': 'BTC/USDT'
    }
    
    adapted_orderbook = adapter.adapt_orderbook_data(sample_orderbook, 'BTC/USDT')
    print("Adapted orderbook:", adapted_orderbook)
    
    print("CCXT Domain Adapter initialized successfully")
