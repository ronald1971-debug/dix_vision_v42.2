"""
Multi-Domain Trading Support Infrastructure
Contract-Compliant Real Implementation

Real multi-domain trading infrastructure for unified trading across financial domains
"""

from .domain_abstraction import DomainAbstractionLayer, Instrument, UnifiedOrder, UnifiedPosition, UnifiedMarketData, DomainAdapter, TradingDomain, InstrumentType, OrderSide, PositionSide
from .stocks_domain import StocksDomainAdapter, StockMarketHours, OrderCondition, StockMarketHours, StockOrderConfig
from .futures_domain import FuturesDomainAdapter, FuturesContract, FuturesContractType, ContractMonth, FuturesOrderConfig
from .forex_domain import ForexDomainAdapter, CurrencyPair, ForexSession, ForexPricing, ForexOrderConfig
from .crypto_domain import CryptoDomainAdapter, CryptoToken, BlockchainType, CryptoInstrument, CryptoOrderConfig

__all__ = [
    # Domain Abstraction Layer
    'DomainAbstractionLayer',
    'Instrument',
    'UnifiedOrder',
    'UnifiedPosition',
    'UnifiedMarketData',
    'DomainAdapter',
    'TradingDomain',
    'InstrumentType',
    'OrderSide',
    'PositionSide',
    
    # Stocks Domain
    'StocksDomainAdapter',
    'StockMarketHours',
    'OrderCondition',
    'StockOrderConfig',
    
    # Futures Domain
    'FuturesDomainAdapter',
    'FuturesContract',
    'FuturesContractType',
    'ContractMonth',
    'FuturesOrderConfig',
    
    # Forex Domain
    'ForexDomainAdapter',
    'CurrencyPair',
    'ForexSession',
    'ForexPricing',
    'ForexOrderConfig',
    
    # Crypto Domain
    'CryptoDomainAdapter',
    'CryptoToken',
    'BlockchainType',
    'CryptoInstrument',
    'CryptoOrderConfig'
]